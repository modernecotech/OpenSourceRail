"""Small constructed API responses test contracts, not actual distributor prices."""
from copy import deepcopy
import json
import hashlib
import pytest
from engineering.sourcing.model import record, validate_record
from engineering.sourcing.adapters import DigiKeyClient, parse_digikey_response


LOCALE = dict(Site="UK", Language="en", Currency="GBP")


def source(environment="production"):
    return record("source", publisher="Synthetic DigiKey fixture",
        url="https://api.digikey.com/products/v4/search/TEST/pricing",
        retrieved_at="2026-10-29", access="test-only-no-live-price",
        source_kind="distributor_catalogue", document_sha256=None, licence=None,
        environment=environment)


def payload():
    return {"SettingsUsed":{"SearchLocale":dict(LOCALE)},"ProductPricings":[{
        "Manufacturer":{"Name":"Fixture manufacturer"},"ManufacturerProductNumber":"TEST-ONLY-001",
        "Description":{"ProductDescription":"Synthetic test component"},
        "ProductVariations":[{"DigiKeyProductNumber":"TEST-CT-ND","PackageType":{"Id":2,"Name":"Cut Tape"},
            "MinimumOrderQuantity":1,"MarketPlace":False,"QuantityAvailableforPackageType":500,
            "StandardPricing":[{"BreakQuantity":1,"UnitPrice":"2.00"},{"BreakQuantity":100,"UnitPrice":"1.50"}]}]}]}


def constraints(src):return {"TEST-CT-ND":{"order_multiple":"1","source_id":src["record_id"]}}


def test_missing_order_multiple_preserves_price_facts_but_holds_purchase_cost():
    result = parse_digikey_response(payload(), source(), expected_locale=LOCALE)
    assert len(result) == 2 and result[0]["kind"] == "product"
    assert "order-multiple-evidence-unreported" in result[0]["specifications"]["sourcing_holds"]
    assert result[1]["order_multiple"] is None and result[1]["purchase_cost_admission"] == "held"


def test_actual_tiers_are_half_open_and_flags_not_approved():
    src = source();result = parse_digikey_response(payload(), src, expected_locale=LOCALE, quantity_constraints=constraints(src))
    product, offer = result
    assert offer["product_id"] == product["record_id"]
    assert offer["tiers"] == [{"minimum_quantity":"1","maximum_quantity":"100","unit_price":"2"},{"minimum_quantity":"100","maximum_quantity":None,"unit_price":"1.5"}]
    assert offer["tax_basis"] == "unknown" and offer["freight_cost"] is None
    assert not offer["procurement_approved"] and validate_record(offer)


def test_returned_locale_fallback_is_rejected():
    data = payload();data["SettingsUsed"]["SearchLocale"]["Currency"] = "USD"
    with pytest.raises(ValueError, match="differs"):parse_digikey_response(data, source(), expected_locale=LOCALE)


def test_details_uses_its_distinct_locale_container():
    data = payload();data = dict(SearchLocaleUsed=LOCALE, Product=data["ProductPricings"][0])
    assert parse_digikey_response(data, source(), expected_locale=LOCALE)[0]["part_number"] == "TEST-ONLY-001"


@pytest.mark.parametrize("field", ["MinimumOrderQuantity", "StandardPricing"])
def test_unreported_quantities_or_price_are_not_zero(field):
    data = payload();del data["ProductPricings"][0]["ProductVariations"][0][field]
    result = parse_digikey_response(data, source(), expected_locale=LOCALE)
    if field == "StandardPricing":assert all(r["kind"] != "offer" for r in result)
    else:assert result[1]["minimum_order_quantity"] is None and result[1]["purchase_cost_admission"] == "held"


def test_sandbox_payload_cannot_create_commercial_offer():
    src = source("sandbox")
    result = parse_digikey_response(payload(), src, expected_locale=LOCALE, quantity_constraints=constraints(src))
    assert len(result) == 1 and "sandbox-data-not-live-price-evidence" in result[0]["specifications"]["sourcing_holds"]


def test_duplicate_package_and_break_quantities_rejected():
    data = payload();data["ProductPricings"][0]["ProductVariations"] *= 2
    with pytest.raises(ValueError, match="Duplicate"):parse_digikey_response(data, source(), expected_locale=LOCALE)
    data = payload();data["ProductPricings"][0]["ProductVariations"][0]["StandardPricing"] *= 2
    src=source()
    with pytest.raises(ValueError, match="Duplicate"):parse_digikey_response(data, src, expected_locale=LOCALE, quantity_constraints=constraints(src))


def quantity_payload(mixed=False):
    row={"DigiKeyProductNumber":"TEST-CT-ND","QuantityPriced":100,"MinimumOrderQuantity":1,"UnitPrice":"1.5","ExtendedPrice":"150","PackageType":{"Name":"Cut Tape","Id":2},"Marketplace":False}
    return dict(RequestedQuantity=100,ManufacturerPartNumber="TEST-ONLY-001",Manufacturer={"Name":"Fixture manufacturer"},Description={"ProductDescription":"Synthetic"},SettingsUsed={"SearchLocaleUsed":LOCALE},StandardPricingOptions=[dict(PricingOption="Exact",TotalQuantityPriced=200 if mixed else 100,Products=[row,row] if mixed else [row])])


def test_quantity_option_is_only_priced_at_its_actual_quantity():
    src=source();result=parse_digikey_response(quantity_payload(),src,expected_locale=LOCALE,quantity_constraints=constraints(src))
    assert result[1]["tiers"] == [{"minimum_quantity":"100","maximum_quantity":"101","unit_price":"1.5"}]


def test_mixed_package_quantity_option_is_held_as_bundle():
    result=parse_digikey_response(quantity_payload(True),source(),expected_locale=LOCALE)
    assert result[0]["kind"] == "run" and result[0]["status"] == "held"


def test_no_credentials_does_not_call_network():
    def forbidden(*args,**kwargs):raise AssertionError("network must not run")
    result=DigiKeyClient(environ={},transport=forbidden).get_pricing("TEST")
    assert result[0]["reason"] == "authentication-required" and not result[0]["network_executed"]


def test_oauth_expiry_fixed_endpoint_and_secret_boundary():
    calls=[];now=[0]
    def transport(method,url,**kwargs):
        calls.append((method,url,kwargs))
        if url.endswith('/token'):return 200,{},json.dumps(dict(access_token="PRIVATE-TOKEN",expires_in=60,token_type="Bearer")).encode()
        return 200,{},json.dumps(payload()).encode()
    env=dict(DIGIKEY_CLIENT_ID="PRIVATE-ID",DIGIKEY_CLIENT_SECRET="PRIVATE-SECRET",DIGIKEY_ACCOUNT_ID="PRIVATE-ACCOUNT")
    client=DigiKeyClient(environ=env,transport=transport,clock=lambda:now[0])
    result=client.get_pricing("TEST-CT-ND",expected_locale=LOCALE)
    client.get_pricing("TEST-CT-ND",expected_locale=LOCALE)
    assert len([x for x in calls if x[0]=='POST']) == 1
    now[0]=61;client.get_pricing("TEST-CT-ND",expected_locale=LOCALE)
    assert len([x for x in calls if x[0]=='POST']) == 2
    assert all(x[1].startswith('https://api.digikey.com/') for x in calls)
    serialized=json.dumps(result)+repr(client)
    assert all(secret not in serialized for secret in ('PRIVATE-TOKEN','PRIVATE-SECRET','PRIVATE-ID','PRIVATE-ACCOUNT'))


def test_oauth_redirect_is_held_without_forwarding_credentials():
    def transport(*args,**kwargs):return 302,{"Location":"https://evil.example"},b""
    client=DigiKeyClient(environ=dict(DIGIKEY_CLIENT_ID="a",DIGIKEY_CLIENT_SECRET="b",DIGIKEY_ACCOUNT_ID="c"),transport=transport)
    result=client.get_pricing("TEST")
    assert result[0]["status"] == "held" and result[0]["http_status"] == 302


def test_hash_bound_distributor_source_requires_matching_original_bytes():
    raw=json.dumps(payload()).encode();fields={k:v for k,v in source().items() if k not in ('record_id','schema','kind')}
    fields['document_sha256']=hashlib.sha256(raw).hexdigest();src=record('source',**fields)
    assert parse_digikey_response(raw,src,expected_locale=LOCALE)
    with pytest.raises(ValueError,match='hash differs'):parse_digikey_response(raw+b' ',src,expected_locale=LOCALE)
    with pytest.raises(ValueError,match='Original document bytes'):parse_digikey_response(payload(),src,expected_locale=LOCALE)


def test_client_quantity_endpoint_parses_official_quantity_schema():
    calls=[]
    def transport(method,url,**kwargs):
        calls.append(url)
        if url.endswith('/token'):return 200,{},b'{"access_token":"SECRET","expires_in":60,"token_type":"Bearer"}'
        return 200,{},json.dumps(quantity_payload()).encode()
    client=DigiKeyClient(environ=dict(DIGIKEY_CLIENT_ID='a',DIGIKEY_CLIENT_SECRET='b',DIGIKEY_ACCOUNT_ID='c'),transport=transport)
    result=client.get_pricing('TEST',requested_quantity=100,expected_locale=LOCALE)
    assert calls[-1].endswith('/products/v4/search/TEST/pricingbyquantity/100')
    assert result[-1]['kind']=='offer' and result[-1]['order_multiple'] is None


def test_quantity_option_preserves_account_specific_price_scope():
    data=quantity_payload();data['MyPricingOptions']=data.pop('StandardPricingOptions')
    result=parse_digikey_response(data,source(),expected_locale=LOCALE)
    assert result[-1]['price_kind']=='account-specific'

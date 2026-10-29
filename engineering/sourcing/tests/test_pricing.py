from decimal import Decimal
import pytest
from engineering.sourcing.model import record
from engineering.sourcing.pricing import evaluate_offers, convert_quantity, fx_factor


def sample(quantity="1", unit="m"):
    req=record("requirement",candidate_id="a"*64,input_id="b"*64,namespace="manufacturing-study",requirement_key="glass",
               quantity=quantity,quantity_unit=unit,occurrence_ids=[],procurement_scope="raw-material")
    product=record("product",product_key="fixture-glass",manufacturer="Schema fixture",part_number="440-127",category="raw-glass-fabric",
                   description="synthetic parser contract, not a live listing",source_ids=["c"*64],
                   specifications={"width_m":{"value":"1.27","unit":"m","scope":"fabric-roll"}},supply_scope="raw-material")
    offer=record("offer",product_id=product["record_id"],source_id="c"*64,price_date="2026-10-29",currency="GBP",quantity_unit="m",
                 source_class="B",tax_basis="excluded",tax_rate=None,minimum_order_quantity="1",order_multiple="1",valid_until=None,
                 tiers=[{"minimum_quantity":"0","maximum_quantity":"5","unit_price":"4.05"},
                        {"minimum_quantity":"5","maximum_quantity":"10","unit_price":"3.75"},
                        {"minimum_quantity":"10","maximum_quantity":"101","unit_price":"3.50"},
                        {"minimum_quantity":"101","maximum_quantity":None,"unit_price":"3.10"}])
    return req,product,offer


@pytest.mark.parametrize("quantity,total",[("1","4.05"),("5","18.75"),("100","350"),("101","313.1")])
def test_actual_order_break_is_not_lowest_headline_price(quantity,total):
    req,p,o=sample(quantity)
    r=evaluate_offers(req,p,[o],[],as_of="2026-10-29",target_currency="GBP")[0]
    assert r["status"]=="priced" and r["comparable_order_subtotal"]==total
    assert r["complete_installed_cost"] is None


def test_roll_width_and_purchase_rounding():
    req,p,o=sample("1","m2")
    r=evaluate_offers(req,p,[o],[],as_of="2026-10-29",target_currency="GBP")[0]
    assert r["purchased_quantity"]=="1" and r["comparable_order_subtotal"]=="4.05"
    assert Decimal(r["demanded_quantity"])==Decimal(1)/Decimal("1.27")
    assert convert_quantity("1","t","kg")==1000
    assert convert_quantity("1","CY","m3")==Decimal(".764554857984")
    with pytest.raises(ValueError):convert_quantity("1","kg","m2",p)


def test_moq_changes_applicable_tier():
    req,p,o=sample("2")
    body={k:v for k,v in o.items() if k not in ("schema","kind","record_id")}
    body.update(minimum_order_quantity="101",order_multiple="5")
    o=record("offer",**body)
    r=evaluate_offers(req,p,[o],[],as_of="2026-10-29",target_currency="GBP")[0]
    assert r["purchased_quantity"]=="105" and r["comparable_order_subtotal"]=="325.5"


def test_missing_stale_and_future_fx_never_falls_back_one_to_one():
    req,p,o=sample()
    for rates in ([],[record("fx",source_id="d"*64,rate_date="2026-09-01",base_currency="GBP",quote_currency="USD",rate="1.3")],
                  [record("fx",source_id="d"*64,rate_date="2026-10-30",base_currency="GBP",quote_currency="USD",rate="1.3")]):
        result=evaluate_offers(req,p,[o],rates,as_of="2026-10-29")[0]
        assert result["status"]=="held" and result["comparable_order_subtotal"] is None
        assert "missing-dated-compatible-FX" in result["holds"]


def test_fx_uses_single_observation_day():
    rates=[record("fx",source_id="d"*64,rate_date="2026-10-28",base_currency="EUR",quote_currency="GBP",rate=".8"),
           record("fx",source_id="d"*64,rate_date="2026-10-28",base_currency="EUR",quote_currency="USD",rate="1.2")]
    factor,ids,date=fx_factor(rates,"GBP","USD",as_of="2026-10-29")
    assert factor==Decimal("1.5") and len(ids)==2 and date=="2026-10-28"
    assert fx_factor(rates,"GBP","IQD",as_of="2026-10-29")[0] is None


def test_tax_and_unverified_actual_quote_holds():
    req,p,o=sample()
    body={k:v for k,v in o.items() if k not in ("schema","kind","record_id")}
    body.update(tax_basis="included",tax_rate=None,source_class="A",authenticated=True)
    o=record("offer",**body)
    r=evaluate_offers(req,p,[o],[],as_of="2026-10-29",target_currency="GBP")[0]
    assert r["comparable_order_subtotal"] is None
    assert "tax-conversion-needs-explicit-rate" in r["holds"]
    assert "actual-quote-needs-external-authentication" in r["holds"]


def test_unknown_order_constraints_keep_requested_quantity_extension_separate():
    req,p,o=sample("101")
    body={k:v for k,v in o.items() if k not in ("schema","kind","record_id")}
    body.update(minimum_order_quantity=None,order_multiple=None)
    o=record("offer",**body)
    r=evaluate_offers(req,p,[o],[],as_of="2026-10-29",target_currency="GBP")[0]
    assert r["status"]=="held" and "held-order-constraints" in r["holds"]
    assert r["purchased_quantity"] is None and r["comparable_order_subtotal"] is None
    assert r["comparable_listed_extension"]=="313.1"
    assert r["listed_extension_is_order_cost"] is False and r["listed_extension_is_cost_bound"] is False


@pytest.mark.parametrize("other_source,other_kind",[("e"*64,"reference"),("d"*64,"cash")])
def test_fx_does_not_mix_providers_or_rate_regimes(other_source,other_kind):
    rates=[record("fx",source_id="d"*64,rate_date="2026-10-28",base_currency="EUR",quote_currency="GBP",rate=".8",rate_kind="reference"),
           record("fx",source_id=other_source,rate_date="2026-10-28",base_currency="EUR",quote_currency="USD",rate="1.2",rate_kind=other_kind)]
    assert fx_factor(rates,"GBP","USD",as_of="2026-10-29")[0] is None

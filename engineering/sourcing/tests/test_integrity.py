"""Independent-review regressions against real catalogue shapes and corruption."""
from copy import deepcopy
from decimal import localcontext
from pathlib import Path
import json
import pytest
from engineering.sourcing.model import record, decimal_text, identity, encoded
from engineering.sourcing.database import Store
from engineering.sourcing.catalogue import seed, load_catalogue
from engineering.sourcing.requirements import validate_requirements
from engineering.sourcing.matching import match_products
from engineering.sourcing.pricing import evaluate_offers
from engineering.sourcing.publication import execute, publish, verify


def requirement(product, quantity="1.27", unit="m2", **extra):
    fields=dict(candidate_id="a"*64,input_id="b"*64,namespace="manufacturing-study",
        requirement_key="cloth",description="Explicit research procurement requirement",
        category="body-materials",priority=3,quantity=quantity,quantity_unit=unit,
        occurrence_ids=[],physical_scopes=["plan/cloth"],procurement_scope=product["supply_scope"],
        identifiers=dict(manufacturer=product["manufacturer"],part_number=product["part_number"]),constraints=[])
    fields.update(extra)
    return record("requirement",**fields)


def test_observation_decimals_never_round_under_callers_context():
    value="12345678901234567890123456789.0500"
    with localcontext() as context:
        context.prec=2
        assert decimal_text("4.05")=="4.05"
        assert decimal_text(value)=="12345678901234567890123456789.05"
        assert decimal_text("-0.000",nonnegative=False)=="0"
    assert decimal_text(value)=="12345678901234567890123456789.05"


@pytest.mark.parametrize("paths",[["panel//glass"],["panel/./glass"],["panel/x/../glass"],
    ["/panel/glass"],["panel/"],["panel","panel/glass"],["panel/glass","panel/glass"]])
def test_scope_aliases_and_within_line_double_charges_rejected(paths):
    p=next(v for v in load_catalogue() if v["kind"]=="product" and v["product_key"]=="EC-GF-BA-440-127")
    req=requirement(p,physical_scopes=paths)
    with pytest.raises(ValueError):validate_requirements([req])


def test_actual_combined_catalogue_retains_provenance_and_exact_area_tiers():
    values=load_catalogue();assert len(values)==277
    assert len([v for v in values if v["kind"]=="source"])==55
    assert len([v for v in values if v["kind"]=="product"])==16
    p=next(v for v in values if v["kind"]=="product" and v["product_key"]=="EC-GF-BA-440-127")
    rates=[v for v in values if v["kind"]=="fx"]
    cbi_rate=next(v for v in rates if v["base_currency"]=="GBP" and v["quote_currency"]=="IQD")
    assert cbi_rate["rate"]=="1692.216" and cbi_rate["rate_date"]=="2026-10-29"
    assert cbi_rate["executable_transaction_rate"] is False
    sources={v["source_key"]:v for v in values if v["kind"]=="source"}
    assert sources["iraq-nubin-grp-facade"]["source_kind"]=="manufacturer_catalogue"
    assert sources["iraq-abralqamar-composites-chemicals"]["source_kind"]=="distributor_catalogue"
    assert sources["iraq-almniee-polymer-raw-materials"]["source_kind"]=="distributor_catalogue"
    domestic_aluminium={"iraq.asia-aluminium","iraq.alko-aluminium",
                        "iraq.baxi-siwail-aluminium","iraq.ii-alco-aluminium"}
    assert domestic_aluminium <= sources.keys()
    domestic_aluminium_ids={sources[key]["record_id"] for key in domestic_aluminium}
    assert not [v for v in values if v["kind"]=="offer" and
                (v.get("source_id") in domestic_aluminium_ids or
                 set(v.get("source_ids", [])) & domestic_aluminium_ids)]
    assert not [v for v in values if v["kind"]=="product" and
                set(v.get("source_ids", [])) & domestic_aluminium_ids]
    offers=[v for v in values if v["kind"]=="offer"]
    for area,quantity,total in (("1.27","1","4.05"),("128.27","101","313.1")):
        req=requirement(p,area)
        assert match_products([req],[p])[0]["status"]=="compatible"
        price=evaluate_offers(req,p,offers,rates,as_of="2026-10-29",target_currency="GBP")[0]
        assert price["demanded_quantity"]==quantity
        assert price["comparable_listed_extension"]==total
        assert price["purchased_quantity"] is None and price["comparable_order_subtotal"] is None
        assert "held-order-constraints" in price["holds"]
    assert any(v.get("seed_provenance",{}).get("research_package_id") for v in values if v["kind"]=="source")


def test_iraqi_gfrp_supplier_leads_do_not_create_prices_or_rail_qualification():
    values=load_catalogue()
    lead_ids={v["record_id"] for v in values if v.get("source_key") in {
        "iraq-nubin-grp-facade", "iraq-abralqamar-composites-chemicals",
        "iraq-almniee-polymer-raw-materials"}}
    assert len(lead_ids)==3
    assert not [v for v in values if v["kind"]=="offer" and
                (v.get("source_id") in lead_ids or set(v.get("source_ids", [])) & lead_ids)]


def test_abb_inverter_family_is_a_specification_lead_without_price_or_lim_approval():
    values=load_catalogue()
    drive=next(v for v in values if v.get("product_key")=="ABB-ACS880-SINGLE-FAMILY")
    assert drive["supply_scope"]=="industrial-drive-family"
    assert drive["specifications"]["published_observations"]["power_range_kW"]==["0.55","6000"]
    assert drive["specifications"]["compatibility"]=="pending"
    assert not [v for v in values if v["kind"]=="offer" and v["product_id"]==drive["record_id"]]


def test_gurit_corecell_is_a_typed_unpriced_material_lead_not_rail_qualification():
    values=load_catalogue()
    foam=next(v for v in values if v.get("product_key")=="GURIT-CORECELL-M80")
    assert foam["specifications"]["density_range_kg_m3"]["values"]==["81","89"]
    assert foam["specifications"]["installed_assembly_complete"] is False
    assert foam["specifications"]["compatibility"]=="pending for rail vehicle use"
    assert not [v for v in values if v["kind"]=="offer" and v["product_id"]==foam["record_id"]]


def test_actual_mechanism_conflict_cannot_become_complete_door():
    p=next(v for v in load_catalogue() if v["kind"]=="product" and v["product_key"]=="WABTEC-ESP4C-1300")
    req=requirement(p,"12","each",category="doors-glazing")
    result=match_products([req],[p])[0]
    assert result["status"]=="pending" and "unresolved-publisher-specification-conflict" in result["holds"]
    req=requirement(p,"12","each",category="doors-glazing",procurement_scope="complete-installed-door")
    assert "product-and-required-assembly-scope-differ" in match_products([req],[p])[0]["holds"]


def test_real_catalogue_packet_replays_and_rejects_resealed_completion_claim(tmp_path):
    with Store(tmp_path/"source.sqlite") as store:
        seed(store)
        p=next(v for v in store.all("product") if v["product_key"]=="EC-GF-BA-440-127")
        req=requirement(p)
        payload=dict(schema="osr-sourcing-declared-requirements/1",candidate_id=req["candidate_id"],requirements=[req])
        twin=dict(schema="osr-sourcing-twin-input/1",payload=payload,payload_id=identity(payload),origin=dict(software_fixture=True))
        request=dict(as_of="2026-10-29",target_currency="GBP")
        result=execute(store,twin,request)
        assert result["summary"]["known_listed_extension_subtotal"]=="4.05"
        publish(store,result,twin,request,tmp_path/"packet")
    assert verify(tmp_path/"packet")["semantic_replay_executed"] is True
    path=tmp_path/"packet/manifest.json";manifest=json.loads(path.read_bytes())
    manifest["complete_installed_cost"]="0";manifest.pop("publication_id");manifest["publication_id"]=identity(manifest)
    path.write_bytes(encoded(manifest)+b"\n")
    with pytest.raises(ValueError,match="completion claim"):verify(tmp_path/"packet")


def test_source_record_never_persists_embedded_credentials():
    with pytest.raises(ValueError):
        record("source",publisher="Schema fixture",url="https://vendor.test/catalogue?client_secret=never-store",
            retrieved_at="2026-10-29",access="public",source_kind="manufacturer_catalogue")

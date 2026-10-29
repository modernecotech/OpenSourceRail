import pytest
from engineering.sourcing.model import record
from engineering.sourcing.matching import match_products


def inputs():
    req=record("requirement",candidate_id="a"*64,input_id="b"*64,namespace="component_registry",registry_id="e"*64,
        requirement_key="door",part_definition_id="f"*64,part_revision_id="1"*64,description="complete installed door",
        category="doors-glazing",quantity="12",quantity_unit="each",occurrence_ids=["car/door"],
        procurement_scope="installed-door-assembly",identifiers={},constraints=[])
    p=record("product",product_key="fixture-ESP4C",manufacturer="Schema fixture",part_number="ESP4C",category="door-mechanism",
        description="mechanism without leaves",source_ids=["c"*64],supply_scope="door-mechanism",
        specifications={"mass_kg":{"value":"46","unit":"kg","scope":"mechanism-and-hanger"}})
    return req,p


def test_mechanism_cannot_replace_full_installed_door_even_with_mapping():
    req,p=inputs()
    binding={"candidate_id":req["candidate_id"],"requirement_id":req["record_id"],"product_id":p["record_id"],
             "registry_id":req["registry_id"],"part_definition_id":req["part_definition_id"],"part_revision_id":req["part_revision_id"]}
    result=match_products([req],[p],bindings=[binding])[0]
    assert result["status"]=="pending" and "product-and-required-assembly-scope-differ" in result["holds"]


def test_forged_mapping_revision_rejected():
    req,p=inputs()
    binding={"candidate_id":"0"*64,"requirement_id":req["record_id"],"product_id":p["record_id"]}
    with pytest.raises(ValueError,match="candidate"):match_products([req],[p],bindings=[binding])
    binding["candidate_id"]=req["candidate_id"]
    with pytest.raises(ValueError,match="registry_id"):match_products([req],[p],bindings=[binding])


def test_required_hot_rated_point_is_not_inferred_from_35_degree_table():
    req=record("requirement",candidate_id="a"*64,input_id="b"*64,namespace="manufacturing-study",requirement_key="HVAC",
        description="hot HVAC",category="HVAC",quantity="1",quantity_unit="each",occurrence_ids=[],
        procurement_scope="HVAC-unit",identifiers={},constraints=[{"field":"rated_ambient_C","minimum":"55","unit":"degC"}])
    p=record("product",product_key="fixture-HVAC",manufacturer="Schema fixture",part_number="LRV",category="HVAC",
        description="35C rated point",source_ids=["c"*64],supply_scope="HVAC-unit",
        specifications={"rated_ambient_C":{"value":"35","unit":"degC"}})
    result=match_products([req],[p])[0]
    assert result["status"]=="unsuitable" and result["checks"][0]["status"]=="fail"

from copy import deepcopy
import pytest
from engineering.component_registry import make_part,make_occurrence,make_registry,validate_registry
from engineering.sourcing.model import record
from engineering.sourcing.requirements import extract_requirements
from engineering.sourcing.twin import propose_revision


def inputs():
    p=make_part("TEST-HVAC","A",["HVAC"],dict(kind="envelope",dimensions_m=[1.,.5,.4],net_volume_m3=None),None,
        dict(calculated_kg=None,lower_bound_kg=50.,upper_bound_kg=70.,evidence_state="bounded-estimate"),dict(method="purchase"),
        procurement=dict(scope="HVAC-unit",manufacturer="synthetic",manufacturer_part_number="HVAC1",supplier=None))
    r=make_registry("test",[p],[make_occurrence("car/HVAC",p)],["HVAC"])
    product=record("product",product_key="test-HVAC",manufacturer="synthetic",part_number="HVAC1",category="HVAC",
        description="synthetic source, not live supplier data",source_ids=["c"*64],supply_scope="HVAC-unit",
        specifications={"mass_kg":{"value":"60","unit":"kg","scope":"HVAC-unit"}})
    return r,extract_requirements(r)[0],product


def test_property_evidence_keeps_physical_identity_and_invalidates_evaluations():
    reg,req,p=inputs();saved=deepcopy(reg)
    result=propose_revision(reg,req,p,changes={"mass_per_unit_kg":"60"},reason="explicit catalogue observation",mode="property-evidence")
    assert reg==saved and result["registry"]["candidate_id"]==reg["candidate_id"]
    assert result["registry"]["registry_id"]!=reg["registry_id"]
    assert result["registry"]["parts"][0]["mass"]["lower_bound_kg"] is None
    assert result["proposal"]["mass_coverage"]["installed_CG_m"] is None
    assert all(r["accepted"] is False for r in result["proposal"]["dependent_evaluations"])
    validate_registry(result["registry"])


def test_actual_substitution_gets_new_identity_but_no_release():
    reg,req,p=inputs()
    result=propose_revision(reg,req,p,changes={"mass_per_unit_kg":"60"},reason="new supplier candidate")
    assert result["registry"]["candidate_id"]!=reg["candidate_id"]
    assert result["proposal"]["physical_qualification"] is None
    assert result["registry"]["operating_release"] is False
    assert result["registry"]["parts"][0]["electrical_thermal"]["power_W"] is None
    assert result["registry"]["parts"][0]["manufacturing"]["cycle_hours"] is None


def test_invented_mass_geometry_and_price_revision_rejected():
    reg,req,p=inputs()
    with pytest.raises(ValueError,match="source observation"):propose_revision(reg,req,p,changes={"mass_per_unit_kg":"1"},reason="bad")
    with pytest.raises(ValueError,match="supplier envelope"):propose_revision(reg,req,p,changes={"geometry":dict(kind="envelope",dimensions_m=[2.,3.,4.])},reason="bad")
    with pytest.raises(ValueError,match="commercial"):propose_revision(reg,req,p,changes={"cost":1},reason="bad")


def test_new_geometry_never_inherits_old_supplier_mass_or_mm_as_metres():
    reg,req,p=inputs()
    body={k:v for k,v in p.items() if k not in ("schema","kind","record_id")}
    body["specifications"]={"dimensions_m":{"value":["2",".5",".4"],"unit":"m"}}
    p=record("product",**body)
    revised=propose_revision(reg,req,p,changes={"geometry":dict(kind="envelope",dimensions_m=[2.,.5,.4])},reason="configured envelope")
    assert revised["registry"]["parts"][0]["mass"]["evidence_state"]=="unresolved"
    assert revised["proposal"]["mass_coverage"]["known_calculated_mass_kg"]==0
    assert revised["proposal"]["mass_coverage"]["mass_upper_bound_kg"] is None
    body["specifications"]["dimensions_m"]["unit"]="mm";p=record("product",**body)
    with pytest.raises(ValueError,match="metres"):
        propose_revision(reg,req,p,changes={"geometry":dict(kind="envelope",dimensions_m=[2.,.5,.4])},reason="bad unit")

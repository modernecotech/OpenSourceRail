import gzip,json
from pathlib import Path
import pytest
from engineering.component_registry import make_part,make_occurrence,make_registry
from engineering.sourcing.requirements import extract_requirements,validate_requirements,classify


def registry():
    p=make_part("TEST-DOOR","A",["doors"],dict(kind="envelope",dimensions_m=[1.,.1,2.],net_volume_m3=None),None,
        dict(calculated_kg=None,lower_bound_kg=40.,upper_bound_kg=60.,evidence_state="bounded-estimate"),dict(method="purchase"))
    return make_registry("synthetic registry contract",[p],[make_occurrence("car/door/1",p),make_occurrence("car/door/2",p)],["doors"])


def test_actual_occurrences_group_by_exact_revision():
    r=registry();requirements=extract_requirements(r)
    assert len(requirements)==1 and requirements[0]["quantity"]=="2"
    assert requirements[0]["part_revision_id"]==r["parts"][0]["revision_id"]
    with pytest.raises(ValueError,match="binding"):extract_requirements(r,candidate_id="a"*64)
    wrapper=dict(candidate_id="a"*64,body_candidate_id=r["candidate_id"],vehicle=dict(candidate_id=r["candidate_id"],registry=r))
    assert extract_requirements(wrapper)[0]["candidate_id"]=="a"*64
    with pytest.raises(ValueError,match="duplicate"):validate_requirements(requirements+requirements)


def test_published_selected_export_remains_twelve_accounts():
    root=Path(__file__).resolve().parents[3]
    p=root/"docs/design-engine/current/exports/engineering-bom.json.gz"
    result=extract_requirements(json.loads(gzip.decompress(p.read_bytes())))
    assert len(result)==12 and all(r["quantity"] is None and not r["occurrence_ids"] for r in result)
    hvac=next(r for r in result if r["requirement_key"]=="retained-comfort/HVAC")
    assert hvac["accounted_mass_kg_per_car"]==960 and hvac["quantity_unit"] is None


def test_wrong_scene_namespace_and_forged_registry_reject():
    r=registry()
    with pytest.raises(ValueError,match="namespaces"):extract_requirements(r,namespace="twin-scene")
    r["occurrences"][0]["candidate_id"]="0"*64
    with pytest.raises(ValueError):extract_requirements(r)


def test_explicit_running_gear_function_precedes_frame_keyword_and_lim_is_token():
    assert classify(["running-gear","bogie-frame"])[0]=="running-gear"
    assert classify(["climate system"])[0]=="HVAC"
    assert classify(["station-LIM-winding"])[0]=="propulsion"


def test_disjoint_groups_cannot_mix_registry_revisions_of_same_physical_candidate():
    a=make_part("P1","A",["doors"],dict(kind="envelope",dimensions_m=[1.,.1,2.],net_volume_m3=None),None,
        dict(calculated_kg=None,lower_bound_kg=40.,upper_bound_kg=60.,evidence_state="bounded-estimate"),dict(method="purchase"))
    def other(revision,upper):
        return make_part("P2",revision,["doors"],dict(kind="envelope",dimensions_m=[1.,.1,2.],net_volume_m3=None),None,
            dict(calculated_kg=None,lower_bound_kg=40.,upper_bound_kg=upper,evidence_state="bounded-estimate"),dict(method="purchase"))
    old,new=other("A",60.),other("B",80.)
    def version(p):return make_registry("test",[a,p],[make_occurrence("car/p1",a),make_occurrence("car/p2",p)],["doors"])
    before,after=version(old),version(new)
    assert before["candidate_id"]==after["candidate_id"] and before["registry_id"]!=after["registry_id"]
    left=next(r for r in extract_requirements(before) if r["requirement_key"]=="P1")
    right=next(r for r in extract_requirements(after) if r["requirement_key"]=="P2")
    with pytest.raises(ValueError,match="source revision"):validate_requirements([left,right])


@pytest.mark.parametrize("field,value",[("input_id","e"*64),("namespace","twin-scene")])
def test_mixed_input_or_namespace_rejected(field,value):
    from engineering.sourcing.model import record
    first=extract_requirements(registry())[0]
    second={k:v for k,v in first.items() if k not in ("schema","kind","record_id")}
    second.update(requirement_key="other",occurrence_ids=["other/door"])
    second[field]=value;second=record("requirement",**second)
    with pytest.raises(ValueError,match="source revision"):validate_requirements([first,second])

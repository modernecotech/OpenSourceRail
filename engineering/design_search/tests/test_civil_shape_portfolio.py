"""Civil quantities, cost arithmetic, evidence boundaries and immutable replay."""
from copy import deepcopy
import json
import pytest

from engineering.design_search import civil_shape_portfolio as p
from engineering.design_search import multifidelity
from engineering.station_rail.common import identity


def test_cost_adds_each_scope_once_and_keeps_unsized_reserves_explicit():
    candidate=p.geometry.generate("reference_box")
    quantities=p.geometry.quantities(candidate)
    spec=p.specification(); assumptions=p.model_cost.assumptions()
    cost=p.estimate(candidate,quantities,spec,assumptions)
    for case in cost["cases"]:
        name=case["case"]; lines={k:v[name] for k,v in cost["line_items_iqd"].items()}
        assert case["scoped_installed_iqd"]==pytest.approx(sum(lines.values()),rel=0,abs=.1)
        assert case["delivered_iqd"]==pytest.approx(case["factory_gate_iqd"]
            +lines["rails_and_fastenings"]+lines["transport"],rel=0,abs=.03)
        assert case["scoped_installed_iqd"]==pytest.approx(case["delivered_iqd"]
            +lines["erection"]+lines["site_labour"]+lines["supports_foundations_and_bearings_reserve"]
            +lines["site_services_reserve"],rel=0,abs=.03)
        assert case["scoped_lifecycle_npv_iqd"]>case["scoped_installed_iqd"]
        assert case["unsized_prestress_reserve_kg"]>0
    assert cost["complete_installed_mass_kg"] is cost["complete_installed_cost_iqd"] is None
    assert cost["production_shifts_per_day"]==cost["civil_shifts_per_day"]==2
    assert all(cost[key] is False for key in p.FLAGS)
    assert [c["scoped_installed_iqd"] for c in cost["cases"]]==sorted(c["scoped_installed_iqd"] for c in cost["cases"])
    changed=deepcopy(quantities);changed["candidate_id"]="0"*64
    with pytest.raises(ValueError,match="candidate identities differ"):
        p.estimate(candidate,changed,spec,assumptions)
    missing=deepcopy(quantities);del missing["by_material"]["research_concrete"]
    missing["evaluation_id"]=identity({k:v for k,v in missing.items() if k!="evaluation_id"})
    with pytest.raises(ValueError,match="does not reproduce"):
        p.estimate(candidate,missing,spec,assumptions)
    short=deepcopy(assumptions);short["design_life_years"]=10
    with pytest.raises(ValueError,match="30-year life"):
        p.estimate(candidate,quantities,spec,short)


def test_geometry_and_process_assumptions_change_evaluation_without_changing_hardware():
    candidate=p.geometry.generate("variable_depth_box"); q=p.geometry.quantities(candidate)
    spec=p.specification(); a=p.model_cost.assumptions(); before=identity(candidate)
    first=p.estimate(candidate,q,spec,a)
    different=deepcopy(spec);different["rates"]["form_labour_h_per_m2"]=[v*2 for v in spec["rates"]["form_labour_h_per_m2"]]
    second=p.estimate(candidate,q,different,a)
    assert first["competition_assumption_id"]!=second["competition_assumption_id"]
    assert first["factory_person_hours"]["base"]<second["factory_person_hours"]["base"]
    assert first["candidate_id"]==second["candidate_id"] and identity(candidate)==before
    lean=p.geometry.generate("variable_depth_box","lean"); lean_q=p.geometry.quantities(lean)
    assert lean["candidate_id"]!=candidate["candidate_id"]
    assert lean_q["total_nominal_stock_mass_kg"]<q["total_nominal_stock_mass_kg"]


def test_frontier_is_breadth_first_with_persisted_deferred_families():
    value,_=p._calculate()
    assert value["candidate_count"]==18 and value["family_count"]==6
    frontier=value["frontier"]
    assert len(frontier["requests"])==6 and len({r["family"] for r in frontier["requests"]})==6
    assert frontier["executed_stages"]==[0] and frontier["numerical_jobs_dispatched"]==0
    partial=multifidelity.plan(value["evaluations"],value["archive"]["retained_candidate_ids"],
        maximum_tasks=2,runtime_s=150,memory_bytes=1024,source_sha256=value["source_sha256"])
    assert len(partial["requests"])==2 and len(partial["deferred_requests"])==4
    assert {r["candidate_id"] for r in partial["requests"]+partial["deferred_requests"]}=={r["candidate_id"] for r in frontier["requests"]}
    for row in value["evaluations"]:
        assert row["structural_analysis"]=="not-run" and row["engineering_screen"]=="unknown"
        assert row["complete_installed_mass_kg"] is None
    for row in frontier["requests"]:
        assert row["execution"]=="queued" and row["admission"]=="definition-and-domain-review-required"
    incomplete=deepcopy(value["evaluations"]);incomplete[0]["execution"]="interrupted"
    with pytest.raises(ValueError,match="completed stage-zero"):
        multifidelity.plan(incomplete,value["archive"]["retained_candidate_ids"],
            maximum_tasks=6,runtime_s=150,memory_bytes=1024,source_sha256=value["source_sha256"])


def test_publication_replays_and_tampering_does_not_become_current(tmp_path):
    out=tmp_path/"publication"; result=p.build(output=out)
    assert result["verified"] and result["candidate_count"]==18
    assert p.verify(output=out)==result
    m=json.loads((out/"manifest.json").read_bytes())
    assert "engineering/design_search/search_backends.py" in m["source_sha256"]
    (out/"result.json").write_text("{}")
    with pytest.raises(ValueError,match="payload differs"):p.verify(output=out)
    with pytest.raises(ValueError,match="payload differs"):p.build(output=out)

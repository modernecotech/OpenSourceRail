"""Controller failures cannot turn a research example into accepted railway detail."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.twin_workflow import core as c
from engineering.twin_workflow.adapters import evaluate


def proposal(kind="mechanical-cleat", params=None):
    return dict(schema="osr-twin-proposal/1", id="candidate", baseline_sha256=c.digest({}),
        kind=kind, parameters=params or {}, rationale="Compare geometry and response", sources=[],
        expected_tests=["actual native model"])


@pytest.fixture
def workspace(tmp_path):
    orders = dict(packages=[{}], items=[{}], requests=[{}])
    c.write(tmp_path / "work-orders.json", orders)
    c.write(tmp_path / "state.json", dict(schema="osr-twin-completion-controller/1",
        source_sha256={}, baseline_sha256=c.digest({}), work_orders_sha256=c.sha(tmp_path / "work-orders.json"),
        proposals=[], receipts=[], provider_calls=[], stop_reason="ready", **c.FLAGS))
    return tmp_path


@pytest.mark.parametrize("change", [dict(baseline_sha256="old"), dict(approved=True),
    dict(parameters={"thickness_m": True}), dict(parameters={"force_n": 0}), dict(kind="unknown"),
    dict(expected_tests=[]), dict(parameters={"thickness_m": float("nan")})])
def test_rejects_stale_or_untrusted_commands_and_changed_functions(change):
    p = proposal(); p.update(change)
    with pytest.raises(ValueError):
        c.validate(p, c.digest({}))


def test_deduplicates_design_regardless_of_names_and_rationale(workspace):
    p = proposal()
    assert c.submit(workspace, [p])["added"] == 1
    p.update(id="new-name", rationale="A differently worded claim")
    assert c.submit(workspace, [p])["added"] == 0
    assert c.status(workspace)["queued_candidates"] == 1


def test_submission_is_atomic_on_invalid_second_proposal(workspace):
    before = (workspace / "state.json").read_bytes()
    bad = proposal(); bad["approved"] = True
    with pytest.raises(ValueError):
        c.submit(workspace, [proposal(), bad])
    assert (workspace / "state.json").read_bytes() == before


def test_no_progress_stops_without_calling_native_solver(workspace):
    result = c.run(workspace, wall_seconds=10, reserve_gib=.1)
    assert result["stop_reason"] == "needs-new-proposals-or-evidence"
    assert result["completed_specifications"] == 0
    assert all(result[k] is False for k in c.FLAGS)


def test_work_order_tampering_and_stale_sources_rejected(workspace, tmp_path):
    c.write(workspace / "work-orders.json", {})
    with pytest.raises(ValueError, match="work orders"):
        c.status(workspace)
    path = tmp_path / "source.py"; path.write_text("old")
    state = dict(source_sha256={str(path): c.sha(path)})
    state["baseline_sha256"] = c.digest(state["source_sha256"])
    path.write_text("new")
    with pytest.raises(ValueError, match="stale"):
        c.current(state)


def test_provider_protocol_reads_feedback_and_stops_on_identical_designs(workspace, tmp_path):
    # Protocol fixture, deliberately not described as a real LLM.
    script = tmp_path / "fixture.py"
    script.write_text("import json,sys\nr=json.load(sys.stdin)\np=r['prototype']\n"
                      "p.update(id='guarded',kind='software-precharge',parameters={'policy':'guarded'})\n"
                      "print(json.dumps({'proposals':[p]}))\n")
    result = c.run(workspace, steps=6, wall_seconds=20, reserve_gib=.1,
                   provider_argv=[sys.executable, str(script)])
    assert result["provider_calls"] == 2
    assert result["evaluated_candidates"] == 1
    assert result["study_pass_candidates"] == 1
    assert result["stop_reason"] == "provider-no-progress"
    assert c.verify(workspace)["integrity_verified"]
    replay = next((workspace / "runs").glob("*/artifacts/fault-replay.json"))
    replay.write_text("[]")
    with pytest.raises(ValueError, match="artifact"):
        c.verify(workspace)


def test_provider_timeout_is_retained_as_failure(workspace, tmp_path):
    script = tmp_path / "sleep.py"
    script.write_text("import time\ntime.sleep(20)\n")
    result = c.run(workspace, steps=2, wall_seconds=.0 + 1, reserve_gib=.1,
                   provider_argv=[sys.executable, str(script)])
    assert result["stop_reason"] == "provider-error"
    assert result["evaluated_candidates"] == 0
    assert c.verify(workspace)["integrity_verified"]


def test_open_specification_tree_is_not_completed_by_good_example():
    item = dict(id="part", catalogue_id="bolt", title="Bolt", source="source.json", source_sha256="a" * 64,
                source_records=[dict(pointer="/parts/0")], package_ids=["pkg"], required_detail_sections=["threads"])
    graph = dict(items=[item], packages=[{}], relationships=[])
    orders = c.work_orders(graph, [dict(id="thread-qualification")])
    assert all(s == "open" for s in orders["items"][0]["stages"].values())
    assert len(orders["requests"]) == 1


@pytest.mark.parametrize("policy,passed", [("ratio-only", False), ("interlocks-only", False), ("guarded", True)])
def test_actual_fault_simulator_distinguishes_designs(tmp_path, policy, passed):
    result = evaluate(proposal("software-precharge", dict(policy=policy)), tmp_path / policy)
    assert result["study_pass"] is passed
    assert result["metrics"]["cases"] == 19
    assert all(result[k] is False for k in c.FLAGS)


def test_assembly_recipe_is_data_and_cannot_attach_external_evidence():
    from engineering.design_consistency.demonstrators import interface
    contract = interface()
    p = proposal("controlled-assembly", dict(contract=contract))
    assert c.validate(p, c.digest({}))
    contract["parts"][0]["evidence"] = [dict(path="/etc/passwd")]
    with pytest.raises(ValueError, match="evidence"):
        c.validate(p, c.digest({}))


def test_read_rejects_duplicate_keys_nonfinite_and_oversized_json(tmp_path):
    path = tmp_path / "input.json"
    for text in ('{"x":1,"x":2}', '{"x":NaN}'):
        path.write_text(text)
        with pytest.raises(ValueError):
            c.read(path)
    path.write_text(" " * 20)
    with pytest.raises(ValueError):
        c.read(path, maximum=10)


def test_real_ifc_schema_feedback_repairs_analytical_records_without_changing_physical_parts(tmp_path):
    import ifcopenshell
    from engineering.design_consistency.demonstrators import viaduct
    from engineering.design_consistency.ifc import export
    from engineering.twin_workflow.ifc_checks import correct_analytical_representation
    path = tmp_path / "civil.ifc"
    receipt = export(viaduct(), path)
    before = ifcopenshell.open(str(path))
    parts_before = {p.GlobalId: (p.Name, str(p.ObjectPlacement), str(p.Representation))
                    for p in before.by_type("IfcElement")}
    report = correct_analytical_representation(path)
    assert len(report["before"]) == 4
    assert len(report["repairs"]) == 4
    assert report["after"] == []
    after = ifcopenshell.open(str(path))
    assert {p.GlobalId: (p.Name, str(p.ObjectPlacement), str(p.Representation))
            for p in after.by_type("IfcElement")} == parts_before
    assert receipt["physical_part_count"] == 77
    assert receipt["maximum_tessellation_volume_relative_error"] <= 5e-4
    assert len(after.by_type("IfcStructuralCurveMember")) == 1
    assert all(p.ObjectPlacement for p in after.by_type("IfcStructuralItem"))
    assert after.by_type("IfcStructuralCurveMember")[0].Representation.Representations[0].Items[0].is_a("IfcEdgeCurve")


def test_historical_integrity_does_not_claim_current_sources(workspace):
    state = c.read(workspace / "state.json")
    state["source_sha256"] = {"missing-old-source.py": "a" * 64}
    state["baseline_sha256"] = c.digest(state["source_sha256"])
    c.write(workspace / "state.json", state)
    with pytest.raises(ValueError, match="stale"):
        c.verify(workspace)
    result = c.verify(workspace, historical=True)
    assert result["integrity_verified"] and not result["current_sources_required"]
    assert not result["physical_validation"]

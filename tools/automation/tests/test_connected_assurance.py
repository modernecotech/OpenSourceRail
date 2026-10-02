import copy
import json
from pathlib import Path
import shutil

import pytest

from tools.automation import connected_assurance as thread


@pytest.fixture
def baseline(tmp_path):
    config = json.loads((thread.ROOT / thread.CONFIG).read_text())
    paths = [thread.CONFIG, thread.MANIFEST, "tools/automation/connected_assurance.py",
             *config["models"][0]["source_paths"]]
    paths.extend(value for item in thread.import_items(thread.ROOT) for value in item["source_paths"])
    for value in paths:
        path = tmp_path / value
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(thread.ROOT / value, path)
    return tmp_path, config


def compile_baseline(baseline):
    root, config = baseline
    return thread.compile_thread(root, copy.deepcopy(config))


def test_pump_substitution_reaches_entire_vertical_example(baseline):
    before = compile_baseline(baseline)
    root, config = baseline
    config["design_items"][0]["revision"] = "B"
    config["design_items"][0]["interfaces"]["power_supply_v"] = 48
    after = thread.compile_thread(root, config)
    impact = thread.change_impact(before, after)
    assert "OSR-COOL-PUMP" in impact["changed_records"]
    expected = {
        "requirements": "REQ-COOL-PUMP", "failure_modes": "FM-COOL-RAILWAY",
        "scenarios": "SCN-COOL-PUMP", "evidence": "EVD-COOL-BENCH",
        "production_records": "DEMO-PROD-CONNECTION-01", "occurrences": "DEMO-PUMP-02",
        "decisions": "DEC-LM3-TRAINSET-A000-G4", "interfaces": "IF-COOL-MOUNT",
        "incidents": "DEMO-FRACAS-01", "obligations": "OBL-COOL-APPLICABILITY",
    }
    for kind, identifier in expected.items():
        assert identifier in impact["impacted"][kind]
        assert impact["trace_paths"][identifier]
    assert "stale design revision: OSR-COOL-PUMP" in after["gaps"]["CFG-DEMO-COOL-A"]
    assert "failure analysis binds an earlier design revision" in after["gaps"]["FM-COOL-PUMP"]
    assert impact["release_ready"] is False


def test_defective_batch_is_narrower_than_design_change(baseline):
    report = compile_baseline(baseline)
    impact = thread.batch_impact(report, "DEMO-BATCH-A")
    assert impact["impacted"]["occurrences"] == ["DEMO-CAR-01", "DEMO-CONNECTOR-01", "DEMO-PUMP-01"]
    assert "DEMO-PROD-CONNECTION-01" in impact["impacted"]["production_records"]
    assert "design_items" not in impact["impacted"]
    assert "DEMO-PUMP-02" not in impact["trace_paths"]
    with pytest.raises(ValueError, match="unknown supplier batch"):
        thread.batch_impact(report, "missing")


@pytest.mark.parametrize("mutation,match", [
    (lambda d: d["failure_modes"][0].update(item_id="missing"), "orphan"),
    (lambda d: d["failure_modes"][0].pop("next_higher_effect"), "missing required"),
    (lambda d: d["design_items"].append(copy.deepcopy(d["design_items"][0])), "duplicate"),
    (lambda d: d["design_items"][3].update(part_of=["OSR-COOL-PUMP"]), "cycle in part_of"),
    (lambda d: d["failure_modes"][-2].update(propagates_to=["FM-COOL-PUMP"]), "cycle in propagates_to"),
    (lambda d: d["scenarios"][0].update(acceptance_criteria={"battery_isolation_request":False}), "derive from requirements"),
    (lambda d: d["interfaces"][0].update(endpoints=["REQ-COOL-PUMP","OSR-COOL-PUMP"]), "wrong-kind"),
    (lambda d: d["decisions"][0].update(state="accepted"), "cannot manufacture"),
    (lambda d: d["models"][0].update(source_paths=["../outside"]), "repository-relative"),
])
def test_invalid_relationships_and_claims_fail_closed(baseline, mutation, match):
    root, config = baseline
    mutation(config)
    with pytest.raises(ValueError, match=match):
        thread.compile_thread(root, config)


def test_unknown_occurrence_and_unverified_mitigation_remain_visible(baseline):
    report = compile_baseline(baseline)
    failures = [row for row in report["nodes"] if row["kind"] == "failure_modes"]
    assert all(row["priority"] == "mandatory-safety-review" for row in failures)
    assert all(row["risk"]["occurrence"] == "unknown" for row in failures)
    assert "mitigation lacks a verification scenario: REQ-COOL-TORQUE" in report["gaps"]["FM-COOL-TORQUE"]
    assert "engineering handback and effectiveness review open" in report["gaps"]["DEMO-FRACAS-01"]


def reviewed_evidence(root, config):
    result = root / "bench-result.json"
    result.write_text('{"measured": true}')
    row = config["evidence"][1]
    row.update(state="reviewed", author="test-author", reviewer="test-reviewer", review_reference="TEST-review",
               valid_until="2027-01-01", input_hashes={thread.MANIFEST:thread.digest(root,thread.MANIFEST)},
               result_path="bench-result.json", result_sha256=thread.digest(root,"bench-result.json"),
               configuration_fingerprint=thread.fingerprint({**config["configurations"][0],"kind":"configurations"}))
    return row


def test_review_independence_expiry_and_stale_bytes(baseline):
    root, config = baseline
    row = reviewed_evidence(root, config)
    row["reviewer"] = row["author"]
    with pytest.raises(ValueError, match="reviewer must be independent"):
        thread.compile_thread(root, config)
    row["reviewer"] = "test-reviewer"
    row["input_hashes"][thread.MANIFEST] = "0" * 64
    (root / "bench-result.json").write_text('{"changed":true}')
    report = thread.compile_thread(root, config, today=thread.date(2027, 1, 2))
    gaps = report["gaps"][row["id"]]
    assert "evidence expired" in gaps
    assert "stale result bytes" in gaps
    assert any(gap.startswith("stale evidence input:") for gap in gaps)


def test_parent_requires_children_dependencies_and_integration(baseline):
    report = compile_baseline(baseline)
    gate = next(row for row in report["nodes"] if row["id"] == "DEC-OSR-COOL-LOOP-G3")
    assert "child/dependency decision open: OSR-COOL-PUMP/G3" in gate["blockers"]
    assert "child/dependency decision open: LM3-AUX-P010/G3" in gate["blockers"]
    assert "reviewed physical integration evidence missing" in gate["blockers"]
    assert "prior gate decision open: G2" in gate["blockers"]
    assert gate["evaluated_state"] == "blocked"


def test_model_source_change_reopens_scenarios_and_gates(baseline):
    root, config = baseline
    before = compile_baseline(baseline)
    path = root / config["models"][0]["source_paths"][0]
    path.write_text(path.read_text() + "\n// changed model\n")
    after = thread.compile_thread(root, config)
    impact = thread.change_impact(before, after)
    assert "MODEL-COOL-CONTROLLER" in impact["changed_records"]
    assert "SCN-COOL-PUMP" in impact["impacted"]["scenarios"]
    assert "DEC-LM3-TRAINSET-A000-G4" in impact["impacted"]["decisions"]


def test_cad_source_change_invalidates_configuration_and_execution(baseline):
    root, config = baseline
    execution = json.loads((thread.ROOT / thread.EXECUTION).read_text())
    for value in [*execution["input_hashes"], thread.EXECUTION]:
        path = root / value
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(thread.ROOT / value, path)
    before = thread.compile_thread(root)
    source_path = root / "design/component-catalogue/src/osr_mech/rolling_stock/systems.py"
    source_path.write_text(source_path.read_text() + "\n# CAD design changed\n")
    after = thread.compile_thread(root)
    assert after["gaps"]["CFG-DEMO-COOL-A"]
    assert "LM3-TRC-P040" in thread.change_impact(before, after)["changed_records"]
    assert all(row["controller_execution"] == "stale" for row in after["nodes"]
               if row["kind"] == "scenarios" and row["status"] == "controller-executable")
    with pytest.raises(ValueError, match="stale configuration"):
        thread.run_scenarios(root, root / "unused-execution.json")


def test_old_relationships_survive_removal_in_impact_review(baseline):
    before = compile_baseline(baseline)
    after = copy.deepcopy(before)
    after["edges"] = [row for row in after["edges"] if row["from"] != "OSR-COOL-PUMP"]
    after["node_hashes"]["OSR-COOL-PUMP"] = "changed"
    impact = thread.change_impact(before, after)
    assert "LM3-TRAINSET-A000" in impact["impacted"]["design_items"]
    assert "DEMO-PUMP-01" in impact["impacted"]["occurrences"]


@pytest.mark.parametrize('operation', ['add', 'remove', 'change'])
def test_relationship_only_changes_seed_both_endpoints(baseline, operation):
    before = compile_baseline(baseline)
    after = copy.deepcopy(before)
    edge = next(row for row in after['edges'] if row['to']=='OSR-COOL-PUMP' and row['relation']=='depends_on')
    if operation=='add':
        after['edges'].append(dict(edge, relation='extra-dependency'))
    elif operation=='remove':
        after['edges'].remove(edge)
    else:
        edge['relation']='changed-dependency'
    impact=thread.change_impact(before,after)
    assert impact['changed_records']==[]
    assert {edge['from'],edge['to']} <= set(impact['seeds'])
    assert 'EVD-COOL-BENCH' in impact['impacted']['evidence']
    assert 'DEC-LM3-TRAINSET-A000-G4' in impact['impacted']['decisions']
    assert impact['decision']=='reassess-affected-evidence-assets-and-gates'


def test_source_only_changes_reopen_evidence_without_node_changes(baseline):
    before=compile_baseline(baseline)
    after=copy.deepcopy(before)
    after['source_hashes']['unmapped-controller-build-source']='changed'
    impact=thread.change_impact(before,after)
    assert impact['changed_records']==[]
    assert impact['changed_sources']==['unmapped-controller-build-source']
    assert 'EVD-COOL-BENCH' in impact['seeds']
    assert thread.change_impact(before,before)['decision']=='no-record-change'


def test_manifest_is_source_of_physical_hierarchy_and_report_is_deterministic(baseline):
    first = compile_baseline(baseline)
    second = compile_baseline(baseline)
    assert first == second
    assert {"from":"LM3-HV-SA510", "to":"LM3-CAR-A900", "relation":"part_of"} in first["edges"]
    assert all(row["evaluated_state"] == "blocked" for row in first["nodes"] if row["kind"] == "decisions")


def test_current_controller_execution_is_real_and_remains_unreviewed():
    execution = json.loads((thread.ROOT / thread.EXECUTION).read_text())
    assert execution["state"] == "generated-unreviewed"
    assert len(execution["results"]) == 4
    assert all(row["passed"] for row in execution["results"])
    report = thread.compile_thread()
    executable = [row for row in report["nodes"] if row["kind"] == "scenarios" and row["status"] == "controller-executable"]
    assert all(row["controller_execution"] == "passed-unreviewed" for row in executable)
    assert report["release_ready"] is False

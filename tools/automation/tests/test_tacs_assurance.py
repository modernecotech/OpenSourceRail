"""Exercise evidence invalidation and shared change-impact, not generated formatting."""
import json
from pathlib import Path
import shutil

import pytest

from tools.automation import tacs_assurance as tacs
from tools.automation import connected_assurance as thread


@pytest.fixture
def package(tmp_path):
    paths = set(tacs.compile_package()["source_hashes"])
    paths.update(tacs.compile_graph(tacs.ROOT)["source_hashes"])
    for path in paths:
        destination = tmp_path/path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(tacs.ROOT/path, destination)
    return tmp_path


def test_real_recorded_execution_has_no_physical_release_and_shared_hierarchy():
    report = tacs.compile_package()
    assert report["software_milestone_passed"], report["evidence_issues"]
    assert not report["physical_readiness"] and not report["operational_release_ready"]
    assert len(report["twin_case_summary"]) == len(tacs.CASES)
    for id in ("None", "RadioReconnection", "ControllerRestart"):
        case = next(c for c in report["twin_case_summary"] if c["id"] == id)
        assert case["station_arrivals"] == [101, 102]
    propagation = {(e["from"], e["to"]) for e in report["graph"]["edges"] if e["relation"] == "propagates_to"}
    # The shared compiler stores propagation in dependency-traversal direction.
    for child, parent in zip(["SPEED", "LOCALISATION", "PROTECTION", "TRAIN"], ["LOCALISATION", "PROTECTION", "TRAIN", "SEPARATION"]):
        assert ("TACS-FM-" + child, "TACS-FM-" + parent) in propagation
    decisions = [n for n in report["graph"]["nodes"] if n["kind"] == "decisions"]
    assert len(decisions) == 4 and all(d["evaluated_state"] == "blocked" for d in decisions)


def test_geometry_braking_or_firmware_changes_reopen_bound_evidence_and_decisions(package):
    old = tacs.compile_package(package)
    path = package/tacs.MODEL
    data = json.loads(path.read_text())
    data["trains"][0]["config"]["length_mm"] += 1
    data["trains"][0]["config"]["minimum_deceleration_mmps2"] -= 1
    path.write_text(tacs.encoded(data))
    new = tacs.compile_package(package)
    assert not new["software_milestone_passed"]
    assert any("stale execution inputs" in s for s in new["evidence_issues"])
    assert any("baseline stale" in s for s in new["evidence_issues"])
    impact = thread.change_impact(old["graph"], new["graph"])
    reached = {id for values in impact["impacted"].values() for id in values}
    assert {"TACS-MODEL-TWIN", "TACS-EV-TWIN", "TACS-EV-PROCEDURES", "TACS-DECISION-G4"} <= reached
    path = package/"crates/osr-runtime/src/train.rs"
    path.write_text(path.read_text() + "\n// Changed firmware baseline\n")
    assert any("stale execution inputs" in s for s in tacs.compile_package(package)["evidence_issues"])


def test_result_bytes_and_edited_startup_parameters_cannot_preserve_milestone(package):
    output = package/(tacs.BASE + "twin-results.json")
    output.write_bytes(output.read_bytes() + b" ")
    assert any("stale/missing execution result" in s for s in tacs.compile_package(package)["evidence_issues"])
    deployment = package/tacs.DEPLOYMENT
    data = json.loads(deployment.read_text())
    data["train_startup"][0]["config"]["length_mm"] += 1000
    deployment.write_text(tacs.encoded(data))
    assert "generated deployment differs from controlled railway model" in tacs.compile_package(package)["evidence_issues"]


def test_formal_tool_identity_is_checked_before_running_java(package):
    jar = package/"wrong.jar"
    jar.write_bytes(b"not the pinned TLC tool")
    with pytest.raises(ValueError, match="checksum"):
        tacs.record_formal(package, jar)


def test_fmea_revision_alone_invalidates_software_milestone(package):
    path = package/tacs.ASSURANCE
    data = json.loads(path.read_text())
    data['failure_modes'][0]['item_revision'] = 'sha256:' + '0'*64
    path.write_text(tacs.encoded(data))
    report = tacs.compile_package(package)
    assert not report['software_milestone_passed']
    assert any('FMEA applicability stale' in issue for issue in report['evidence_issues'])
    assert not report['physical_readiness'] and not report['operational_release_ready']


def test_paired_fault_must_activate_and_trip_for_the_right_reason(package):
    path = package/(tacs.BASE + 'twin-results.json')
    result = json.loads(path.read_text())
    case = next(c for c in result['cases'] if c['id'] == 'ChannelReplay')
    case['dual_fault_injected'] = False
    path.write_text(tacs.encoded(result))
    record_path = package/(tacs.BASE + 'twin-execution.json')
    record = json.loads(record_path.read_text())
    record['result_sha256'] = tacs.digest(path)
    record_path.write_text(tacs.encoded(record))
    assert any('paired fault activation/response' in i for i in tacs.compile_package(package)['evidence_issues'])

"""Actual evidence inventory, byte provenance and no inferred release authority."""

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from engineering.generative_design import manufacturing as m


def claim(name, payload):
    return dict(
        artifact_ref=name,
        artifact_sha256=hashlib.sha256(payload).hexdigest(),
        revision="research-fixture-A",
        checked_by="recorded-reviewer-not-authenticated",
        approved_by="recorded-approver-not-authenticated",
        issued_at="2026-10-16T12:00:00Z",
        status="issued",
    )


@pytest.fixture(scope="module")
def audit():
    return m.run()


def test_actual_source_registers_partition_all_products_and_retain_open_work(audit):
    counts = audit["counts"]
    assert counts["vehicle_products"] == 120
    assert counts["local_production_products"] == 62
    assert counts["supplier_configuration_products"] == 58
    assert counts["required_production_artifacts"] == 472
    assert counts["missing_or_unissued_production_artifacts"] == 472
    assert counts["inspection_characteristics"] == 416
    assert counts["actual_inspection_result_records"] == 0
    assert counts["issued_drawing_references"] == 0
    make = {p["product_id"] for p in audit["products"]}
    buy = {p["product_id"] for p in audit["supplier_configuration_requests"]}
    assert not make & buy
    assert len(make | buy) == 120
    assert all(not i["accepted"] for i in audit["inspection_characteristics"])
    assert all(not p["manufacturing_release"] for p in audit["products"])
    assert not audit["manufacturing_release"] and not audit["physical_release"]


def test_missing_metadata_and_bad_or_missing_bytes_cannot_become_issued_evidence(
    tmp_path,
):
    missing = m.artifact_record(dict(status="issued"), root=tmp_path)
    assert missing["state"] == "missing"
    assert "approved_by" in missing["missing_fields"]
    assert not missing["bytes_verified"]
    data = b"preliminary test artifact\n"
    record = claim("definition.txt", data)
    absent = m.artifact_record(record, root=tmp_path)
    assert absent["state"] == "invalid-artifact-bytes"
    (tmp_path / "definition.txt").write_bytes(data + b"changed")
    altered = m.artifact_record(record, root=tmp_path)
    assert altered["state"] == "invalid-artifact-bytes"
    assert not altered["bytes_verified"]
    assert not altered["manufacturing_release"]


def test_complete_record_claim_checks_bytes_but_authenticates_no_approver(tmp_path):
    data = b"unit-test-only unissued research definition\n"
    (tmp_path / "definition.txt").write_bytes(data)
    result = m.artifact_record(claim("definition.txt", data), root=tmp_path)
    assert result["state"] == "complete-record-claim"
    assert result["bytes_verified"]
    assert not result["authority_independently_verified"]
    assert not result["manufacturing_release"]
    unissued = claim("definition.txt", data)
    unissued["status"] = "draft"
    assert m.artifact_record(unissued, root=tmp_path)["state"] == "unissued-record"


def test_unsafe_and_symlinked_evidence_references_are_rejected(tmp_path):
    data = b"outside\n"
    with pytest.raises(ValueError, match="repository-relative"):
        m.artifact_record(claim("../outside.txt", data), root=tmp_path)
    external = tmp_path.parent / (tmp_path.name + "-outside.txt")
    external.write_bytes(data)
    (tmp_path / "linked.txt").symlink_to(external)
    with pytest.raises(ValueError, match="repository-relative"):
        m.artifact_record(claim("linked.txt", data), root=tmp_path)


def test_every_drawing_definition_read_is_source_bound(audit):
    expected = set()
    for family in ("buildable-trainset", "buildable-stations"):
        folder = (
            m.ROOT / "design/component-catalogue/catalog" / family / "factory-drawings"
        )
        expected.update(p.relative_to(m.ROOT).as_posix() for p in folder.glob("*.json"))
    assert expected
    assert expected <= set(audit["sources_sha256"])
    for name in expected:
        assert (
            audit["sources_sha256"][name]
            == hashlib.sha256((m.ROOT / name).read_bytes()).hexdigest()
        )


def fake_repository(tmp_path, monkeypatch):
    original = m.ROOT
    for name in (m.PDR, m.FAI, m.DEFAULTS, m.TRAIN, m.QUALIFICATION):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original / name, target)
    monkeypatch.setattr(m, "ROOT", tmp_path)
    return tmp_path


def test_present_artifact_bytes_and_drawing_issue_reference_are_both_source_bound(
    tmp_path, monkeypatch
):
    root = fake_repository(tmp_path, monkeypatch)
    payload = b"preliminary production definition - no release\n"
    name = "evidence/preliminary-definition.txt"
    path = root / name
    path.parent.mkdir()
    path.write_bytes(payload)
    pdr = json.loads((root / m.PDR).read_text())
    first = pdr["products"][0]["required_artifacts"][0]
    first.update(claim(name, payload))
    (root / m.PDR).write_text(json.dumps(pdr))
    drawing = (
        root
        / "design/component-catalogue/catalog/buildable-trainset/factory-drawings/test.json"
    )
    drawing.parent.mkdir(parents=True)
    drawing.write_text(
        json.dumps(
            dict(
                drawing_id="unit-test-drawing",
                issue_status="unissued",
                issue_record=dict(published_drawing_ref=name),
            )
        )
    )
    before = m.run()
    assert before["sources_sha256"][name] == hashlib.sha256(payload).hexdigest()
    assert drawing.relative_to(root).as_posix() in before["sources_sha256"]
    assert (
        before["products"][0]["artifacts"][0]["observed"]["state"]
        == "complete-record-claim"
    )
    assert not before["products"][0]["manufacturing_release"]
    path.write_bytes(payload + b"changed\n")
    after = m.run()
    assert before["sources_sha256"][name] != after["sources_sha256"][name]
    assert (
        after["products"][0]["artifacts"][0]["observed"]["state"]
        == "invalid-artifact-bytes"
    )


def test_missing_reference_appearance_changes_provenance_membership(
    tmp_path, monkeypatch
):
    root = fake_repository(tmp_path, monkeypatch)
    pdr = json.loads((root / m.PDR).read_text())
    # The recorded metadata remains open; even unapproved input bytes must not
    # change invisibly after they have become available to the audit.
    name = "not-issued-yet.txt"
    pdr["products"][0]["required_artifacts"][0]["artifact_ref"] = name
    (root / m.PDR).write_text(json.dumps(pdr))
    before = m.run()
    assert name in before["missing_referenced_artifacts"]
    assert name not in before["sources_sha256"]
    (root / name).write_text("unissued research input\n")
    after = m.run()
    assert name not in after["missing_referenced_artifacts"]
    assert name in after["sources_sha256"]
    assert after["products"][0]["artifacts"][0]["observed"]["state"] == "missing"
    assert not after["manufacturing_release"]

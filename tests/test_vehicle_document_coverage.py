import hashlib
import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/vehicle_document_coverage.py"
SPEC = importlib.util.spec_from_file_location("vehicle_document_coverage", SCRIPT)
COVERAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COVERAGE)


def test_inventory_binds_frozen_candidate_and_real_payloads():
    report = COVERAGE.build_report(ROOT)
    assert report["identity"]["vehicle_candidate_id"] == "9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba"
    assert report["identity"]["vehicle_evaluation_id"] == "dfb48ca3fac6ee9b702ae13b2e5e4e0c112d734263750deefb25ad5718fdb272"
    assert report["identity"]["pilot_publication_manifest_id"] == "b16892f0ffed69174223b73e2555e8fe4a31a905e9534a1a51328618675f51fe"
    assert report["identity"]["delivery_manifest_id"] == "e35411fcbd64304bf770d395149d66de55b863399a0b6ca6e3b0a5f486ed0e59"
    assert report["identity"]["delivery_proposal_id"] == "7b88d05f9e0a16ada127d60e51d8ebfdc23b0dcb90ba0c906b2050d4e65a5775"
    assert report["identity"]["engineering_revision"] == report["identity"]["vehicle_evaluation_id"]
    assert report["identity"]["service_evaluation_id"] == "830ee18500b3c4c192f74fb61a9f8079adc1ef7eb3e3f3a9db96cdee8bf4a4c2"
    assert report["generator"]["path"] == "tools/vehicle_document_coverage.py"
    assert report["generator"]["sha256"] == hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
    assert COVERAGE.DEFAULT_OUTPUT == Path("docs/design-engine/v06-design-closure/vehicle-document-coverage.json")
    assert report["counts"]["parts"] == report["counts"]["delivery_mapping_items"] == 668
    assert report["counts"]["assemblies"] == 41
    for source in report["source_payloads"].values():
        path = ROOT / source["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]
        assert source["pin_sources"]
    assert "not a repository-wide search" in report["missing_document_rationale"]["scope"]


def test_missing_documents_remain_explicit_and_never_close_manufacturing(tmp_path):
    report = COVERAGE.build_report(ROOT)
    assert all(
        all(doc["status"] == "missing" and doc["reference"] is None for doc in row["controlled_documents"].values())
        for row in report["parts"]
    )
    assert all(
        all(doc["status"] == "missing" and doc["reference"] is None for doc in row["controlled_documents"].values())
        for row in report["assemblies"]
    )
    assert report["counts"]["null_delivery_reference_counts"] == {
        "drawing_reference": 668,
        "inspection_reference": 668,
        "production_bom": 668,
        "conversion_rule": 668,
    }
    assert report["closure"]["manufacturing_documentation_complete"] is False
    assert report["closure"]["manufacturing_release"] is False
    assert report["closure"]["erp_ready"] is False
    COVERAGE.write_report(report, tmp_path / "coverage.json")
    written = (tmp_path / "coverage.json").read_bytes()
    COVERAGE.write_report(report, tmp_path / "coverage.json")
    assert (tmp_path / "coverage.json").read_bytes() == written
    assert json.loads(written)["closure"]["status"].startswith("held")


def _copy_minimal_packet(destination):
    source = ROOT / COVERAGE.PACKET
    for relative in (
        "manifest.json",
        "bundle.json",
        "vehicle/manifest.json",
        "vehicle/bom.csv",
        "vehicle/installation.json.gz",
        "vehicle/assembly.glb",
        "delivery/manifest.json",
        "delivery/execution-mapping-draft.json",
        "delivery/proposal.json.gz",
        "delivery/inputs/body.json.gz",
        "delivery/inputs/study.json.gz",
    ):
        target = destination / COVERAGE.PACKET / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target)


def test_missing_manifest_pin_is_rejected(tmp_path):
    _copy_minimal_packet(tmp_path)
    manifest_path = tmp_path / COVERAGE.PACKET / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    del manifest["files_sha256"]["delivery/proposal.json.gz"]
    manifest_path.write_text(json.dumps(manifest))
    try:
        COVERAGE.build_report(tmp_path)
    except ValueError as error:
        assert "missing required manifest pin" in str(error)
    else:
        raise AssertionError("expected missing publication pin to be rejected")


def test_delivery_identity_mismatch_is_rejected_even_with_updated_manifest_pin(tmp_path):
    _copy_minimal_packet(tmp_path)
    folder = tmp_path / COVERAGE.PACKET
    delivery_manifest_path = folder / "delivery/manifest.json"
    delivery_manifest = json.loads(delivery_manifest_path.read_text())
    delivery_manifest["identities"]["service_evaluation_id"] = "0" * 64
    delivery_manifest_path.write_text(json.dumps(delivery_manifest))

    top_manifest_path = folder / "manifest.json"
    top_manifest = json.loads(top_manifest_path.read_text())
    top_manifest["files_sha256"]["delivery/manifest.json"] = hashlib.sha256(
        delivery_manifest_path.read_bytes()
    ).hexdigest()
    top_manifest_path.write_text(json.dumps(top_manifest))

    try:
        COVERAGE.build_report(tmp_path)
    except ValueError as error:
        assert "delivery manifest identity service_evaluation_id" in str(error)
    else:
        raise AssertionError("expected delivery service identity mismatch to be rejected")

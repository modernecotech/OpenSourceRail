import hashlib
import importlib.util
import json
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
    assert report["counts"]["parts"] == report["counts"]["delivery_mapping_items"] == 668
    assert report["counts"]["assemblies"] == 41
    for source in report["source_payloads"].values():
        path = ROOT / source["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]


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
    first = COVERAGE.write_report(report, tmp_path / "coverage.json")
    assert first is None
    written = (tmp_path / "coverage.json").read_bytes()
    COVERAGE.write_report(report, tmp_path / "coverage.json")
    assert (tmp_path / "coverage.json").read_bytes() == written
    assert json.loads(written)["closure"]["status"].startswith("held")

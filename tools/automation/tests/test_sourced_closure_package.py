import gzip
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tools/automation/sourced-closure-package.py"
SPEC = importlib.util.spec_from_file_location("osr_sourced_closure_package", SCRIPT)
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


def test_checked_in_closure_display_matches_its_source_report():
    folder = ROOT / "docs/design-engine/sourced-case"
    report_path = folder / "closure.json.gz"
    with gzip.open(report_path, "rt", encoding="utf-8") as stream:
        report = json.load(stream)
    summary = json.loads((folder / "closure-summary.json").read_text(encoding="utf-8"))
    expected = PACKAGE.projection(report, hashlib.sha256(report_path.read_bytes()).hexdigest())
    assert summary == expected


def test_retained_native_archives_reopen_as_seven_closed_packages(tmp_path):
    descriptors = PACKAGE.descriptors(ROOT, tmp_path)
    assert len(descriptors) == 7
    assert sum(item["kind"] == "distributed-contact-whole" for item in descriptors) == 3
    assert all((Path(item["path"]) / "manifest.json").is_file() for item in descriptors)


def test_closure_report_gzip_is_deterministic_and_decodable():
    report = {"schema": "test", "value": 3.5}
    first = PACKAGE.report_bytes(report)
    second = PACKAGE.report_bytes(report)
    assert first == second
    assert json.loads(gzip.decompress(first)) == report


def test_seals_match_the_shared_railway_identity_encoding():
    from engineering.station_rail.common import identity

    value = {"source": "Iraq — بغداد", "amount": 3.5}
    assert PACKAGE.identity(value) == identity(value)

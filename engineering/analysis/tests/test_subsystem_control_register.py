import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "subsystem_control_register", ROOT / "engineering/subsystem_control_register.py"
)
REGISTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REGISTER)


def test_register_covers_every_controlled_subsystem_without_claiming_release():
    report = REGISTER.build_register()
    assert report["summary"]["domains"] == {
        "civil": 19,
        "mechanical": 146,
        "rust": 58,
        "station": 7,
    }
    assert report["summary"]["records"] == 230
    assert report["summary"]["physical_identity_templates"] == 172
    assert report["summary"]["printable_qr_labels"] == 0
    assert report["validation"] == {
        "passed": True,
        "unique_identity": True,
        "complete_source_coverage": True,
        "all_release_evidence_open": True,
        "qr_fail_closed": True,
    }
    assert all(row["release_state"] == "evidence-open-not-released" for row in report["records"])


def test_generated_registers_match_the_compiler():
    report = REGISTER.build_register()
    assert REGISTER.OUTPUT_JSON.read_text() == REGISTER.serialise(report)
    assert REGISTER.OUTPUT_MARKDOWN.read_text() == REGISTER.markdown(report)

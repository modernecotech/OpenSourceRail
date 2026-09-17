import importlib.util
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('safety_summary', ROOT / 'tools/automation/safety-case-summary.py')
SUMMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUMMARY)


def test_counts_follow_case_edits_without_claiming_proof_acceptance(tmp_path):
    directory = tmp_path / 'docs/safety-case/gsn'
    directory.mkdir(parents=True)
    case = directory / 'case.toml'
    case.write_text('[[goal]]\nid="G1"\n[[solution]]\nid="E1"\n')
    assert '**1 goals, 0 strategies, 1 solutions**' in SUMMARY.render(tmp_path)
    case.write_text(case.read_text() + '[[goal]]\nid="G2"\n')
    assert '**2 goals, 0 strategies, 1 solutions**' in SUMMARY.render(tmp_path)
    assert 'not successful or accepted proofs' in SUMMARY.render(tmp_path)


def test_documented_counts_are_current():
    subprocess.run(['python3', str(ROOT / 'tools/automation/safety-case-summary.py'), '--check'], check=True)


def test_reviewed_documentation_boundaries_do_not_regress():
    shift = (ROOT / 'docs/operations/dispatcher/s6-shift-end.md').read_text()
    assert 'at least 150 kW' not in shift
    assert 'charging-duty and morning-readiness' in shift
    operations = (ROOT / 'docs/operations/README.md').read_text()
    assert 'recorded in [ERPNext]' in operations and 'read-only' in operations
    architecture = (ROOT / 'docs/ARCHITECTURE.md').read_text()
    assert 'is proven to refine the model' not in architecture
    evidence = (ROOT / 'docs/certification/evidence-register.md').read_text()
    assert 'Zero open\nsafety-case gaps' not in evidence
    assert '45 named-property proofs' not in evidence

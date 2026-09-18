"""Release evidence must retain every declared execution, including its exact log."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('kani_release', ROOT / 'tools/automation/kani_release.py')
KANI = importlib.util.module_from_spec(spec); spec.loader.exec_module(KANI)


@pytest.fixture
def artifacts(tmp_path, monkeypatch):
    declaration = dict(solution='E1', kind='kani', path='crates/example/src/kani_proofs.rs', anchor='property')
    monkeypatch.setattr(KANI.ASSURANCE, 'declared', lambda: [declaration])
    monkeypatch.setattr(KANI.ASSURANCE, 'scope', lambda: {'input.rs': 'current'})
    folder = tmp_path / 'safety-execution-example'; folder.mkdir()
    header = dict(command=['cargo', 'kani', '-p', 'example', '--harness', 'kani_proofs::property', '--exact'],
                  tool_version='cargo-kani 0.67.0', source_commit='commit', timeout_seconds=300)
    log = folder / 'E1.log'; log.write_text(json.dumps(header) + '\nVERIFICATION:- SUCCESSFUL\n')
    row = dict(**declaration, inputs={'input.rs': 'current'}, status='passed', exit_code=0,
        tool='cargo-kani', tool_version='cargo-kani 0.67.0', bounds='fixture input bounds',
        executed_by='github:modernecotech/OpenSourceRail/actions/runs/7',
        report='build/assurance/example/E1.log', report_sha256=KANI.digest(log))
    results = folder / 'results.toml'; results.write_text(KANI.ASSURANCE.toml([row]))
    manifest = dict(schema='osr-controlled-execution/1', commit='commit', runner=row['executed_by'],
                    passed=True, inputs=row['inputs'], results_sha256=KANI.digest(results), solutions=['E1'])
    (folder / 'execution.json').write_text(json.dumps(manifest))
    return tmp_path, folder, row, manifest


def test_exports_original_manifest_results_and_log(artifacts):
    root, folder, row, manifest = artifacts
    output = root / 'export'; output.mkdir()
    result = KANI.export(root, output, 'commit', 7)
    assert len(result['harnesses']) == 1
    assert result['independently_accepted'] is False
    for name in ('execution.json', 'results.toml', 'E1.log'):
        assert (folder / name).read_bytes() == (output / 'build/assurance/example' / name).read_bytes()


@pytest.mark.parametrize('fault', ['missing', 'duplicate', 'failed', 'stale-input', 'wrong-anchor',
    'changed-log', 'changed-results', 'wrong-commit', 'wrong-run', 'report-path', 'extra-file', 'no-success'])
def test_incomplete_stale_failed_or_tampered_proofs_cannot_be_exported(artifacts, fault):
    root, folder, row, manifest = artifacts
    rows = [row]
    if fault == 'missing': rows = []
    elif fault == 'duplicate': rows = [row, copy.deepcopy(row)]
    elif fault == 'failed': row.update(status='failed', exit_code=124)
    elif fault == 'stale-input': row['inputs'] = {'input.rs': 'old'}
    elif fault == 'wrong-anchor': row['anchor'] = 'another_property'
    elif fault == 'wrong-commit': manifest['commit'] = 'old-commit'
    elif fault == 'wrong-run': manifest['runner'] = 'local-unattested'
    elif fault == 'report-path': row['report'] = '/etc/passwd'
    elif fault == 'extra-file': (folder / 'unlisted.txt').write_text('not evidence')
    elif fault in ('changed-log', 'no-success'):
        log = folder / 'E1.log'
        log.write_text(log.read_text().replace('SUCCESSFUL', 'FAILED'))
        if fault == 'no-success': row['report_sha256'] = KANI.digest(log)
    results = folder / 'results.toml'; results.write_text(KANI.ASSURANCE.toml(rows))
    if fault != 'changed-results': manifest['results_sha256'] = KANI.digest(results)
    else: results.write_text(results.read_text() + '\n# altered\n')
    (folder / 'execution.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError): KANI.validate(root, 'commit', 7)

"""Baghdad target provenance and missing-input execution boundaries."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

import pytest

from engineering.civil_exploration.contracts import ROOT, HERE, encoded, load, sha
from engineering.civil_exploration import qualification

CLI = ROOT/'tools/automation/civil-study.py'


@pytest.fixture
def supplier_record():
    """Synthetic contract input only; never installed as a deployment input."""
    scratch = ROOT/'build/engineering/qualification-contract-tests'
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as name:
        folder = Path(name)
        source = folder/'synthetic-source.txt'
        source.write_text('Synthetic test data, not a supplier drawing or engineering evidence.\n')
        weights = list(range(15, 39))
        record = dict(schema='osr-civil-supplier-train/1', deployment='baghdad',
                      family='metro-6car', cars=6, axle_count=24, length_m=111.,
                      loaded_mass_kg=258000., load_case='AW2',
                      basis='Synthetic contract fixture only; no deployment acceptance',
                      source=source.relative_to(ROOT).as_posix(), source_sha256=sha(source),
                      axle_positions_m=[1.+4*i for i in range(24)],
                      axle_loads_kn=[258000.*9.81/1000*w/sum(weights) for w in weights])
        path = folder/'synthetic-record.json'
        path.write_bytes(encoded(record))
        yield path, record, source


def cli_module():
    spec = importlib.util.spec_from_file_location('civil_study_qualification_test', CLI)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_baghdad_retained_envelopes_and_open_inputs():
    report = qualification.build()
    assert report['deployment'] == 'baghdad'
    assert report['planning_train'] == dict(
        family='metro-6car', cars=6, axles=24, length_m=111., tare_mass_t=204.,
        aw2_mass_t=258., aw3_mass_t=276., infrastructure_full_train_allowance_t=384.,
        basis='planning envelopes; infrastructure allowance and averages do not define loaded axle forces')
    assert report['catalogue_context']['lines'] == 54
    assert report['catalogue_context']['missing_ground_profiles'] == 30
    assert report['supplier_pattern'] is None
    assert not report['moving_force_execution_ready']
    assert not report['coupled_programme_execution_ready']
    assert not report['engineering_qualification_ready'] and not report['physical_release']
    assert all(row['status'] == 'open' for row in report['missing_inputs'])
    assert {r['id'] for r in report['missing_inputs'] if r['blocks_moving_load']} == {
        'TRAIN-AXLE-POSITIONS', 'TRAIN-LOADED-DISTRIBUTION'}
    for relative, digest in report['source_hashes'].items():
        assert sha(ROOT/relative) == digest
    with pytest.raises(ValueError, match='blocked'):
        qualification.moving_force_study(report)


@pytest.mark.parametrize('command', ['run', 'programme'])
def test_default_cli_retains_gaps_and_runs_no_solver(command, tmp_path):
    output = tmp_path/command
    result = subprocess.run([sys.executable, str(CLI), command, '--output', str(output)],
                            cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 2, result.stderr
    assert 'blocked-missing-supplier-axle-inputs' in result.stderr
    assert {p.name for p in output.iterdir()} == {'qualification.json', 'qualification.md'}
    assert load(output/'qualification.json')['supplier_pattern'] is None
    assert 'LM3 axle spacing is never repeated' in (output/'qualification.md').read_text()


def test_supplied_pattern_preserves_forces_and_other_gaps(supplier_record):
    path, record, source = supplier_record
    report = qualification.build(path)
    study = qualification.moving_force_study(report)
    assert report['moving_force_execution_ready']
    assert not report['coupled_programme_execution_ready']
    assert not report['engineering_qualification_ready'] and not report['physical_release']
    assert study['train']['axle_offsets_m'] == [4.*i for i in range(24)]
    assert study['train']['axle_loads_kn'] == record['axle_loads_kn']
    assert study['train']['supplier_verified']
    assert report['supplier_pattern']['leading_axle_offset_m'] == 1.
    assert study['evidence_refs']['train']['sha256'] == sha(path)
    assert study['sources_sha256'][source.relative_to(ROOT).as_posix()] == sha(source)
    assert not study['material']['measured'] and not study['foundation']['site_verified']
    assert all(not g['calibrated'] for g in study['ground_scenarios'])
    assert all(r['status'] == 'open' for r in report['missing_inputs'][2:])


@pytest.mark.parametrize('mutation', [
    lambda r: r.update(axle_positions_m=r['axle_positions_m'][:12], axle_count=12),
    lambda r: r['axle_loads_kn'].__setitem__(0, r['axle_loads_kn'][0]*2),
    lambda r: r['axle_positions_m'].__setitem__(1, r['axle_positions_m'][0]),
    lambda r: r['axle_positions_m'].__setitem__(23, 112.),
    lambda r: r['axle_positions_m'].__setitem__(0, True),
    lambda r: r.update(source_sha256='0'*64),
    lambda r: r.update(source='../uncontrolled-source.txt'),
    lambda r: r.update(source=str(ROOT/'docs/civil/viaduct-load-model.toml')),
    lambda r: r.update(axle_force_average_kn=120.),
])
def test_incomplete_unbalanced_or_uncontrolled_supplier_data_rejected(supplier_record, mutation):
    path, record, _ = supplier_record
    mutation(record)
    path.write_bytes(encoded(record))
    with pytest.raises(ValueError):
        qualification.build(path)


def test_source_mutation_rejected(supplier_record):
    path, _, source = supplier_record
    source.write_text('Changed source after record was signed by its checksum.\n')
    with pytest.raises(ValueError, match='stale'):
        qualification.build(path)


def test_study_overrides_retained_and_resume_requires_same_inputs(supplier_record, tmp_path):
    path, _, _ = supplier_record
    report = qualification.build(path)
    selected = load(HERE/'config/reference.json')
    selected['material']['youngs_modulus_pa'] *= .9
    config = tmp_path/'study.json'
    config.write_bytes(encoded(selected))
    output = tmp_path/'qualification'
    qualification.write(report, output, config=config)
    profile = load(output/'solver-profile.json')
    assert profile['material'] == selected['material']
    assert len(profile['train']['axle_offsets_m']) == 24
    qualification.write(report, output, config=config, resume=True)
    changed = deepcopy(report)
    changed['planning_train']['length_m'] += 1
    with pytest.raises(ValueError, match='resume inputs changed'):
        qualification.write(changed, output, config=config, resume=True)
    selected['material']['youngs_modulus_pa'] *= .9
    config.write_bytes(encoded(selected))
    with pytest.raises(ValueError, match='resume solver profile changed'):
        qualification.write(report, output, config=config, resume=True)


def test_coupled_programme_stays_blocked_with_moving_force_data(supplier_record, tmp_path, monkeypatch):
    path, _, _ = supplier_record
    module = cli_module()
    from engineering.civil_exploration import programme
    monkeypatch.setattr(programme, 'run', lambda *a, **k: pytest.fail('coupled solver must not run'))
    output = tmp_path/'coupled'
    monkeypatch.setattr(sys, 'argv', [str(CLI), 'programme', '--train-record', str(path), '--output', str(output)])
    assert module.main() == 2
    report = load(output/'qualification.json')
    assert report['moving_force_execution_ready']
    assert not report['coupled_programme_execution_ready']
    assert not (output/'reference-campaign').exists()


def test_baghdad_cli_returns_failed_numerical_status_and_forwards_retry(supplier_record, tmp_path, monkeypatch):
    path, _, _ = supplier_record
    module = cli_module()
    output = tmp_path/'moving-force'
    calls = []

    def run(config, evaluation, **kwargs):
        calls.append(kwargs)
        assert len(load(config)['train']['axle_offsets_m']) == 24
        evaluation.mkdir(exist_ok=True)
        (evaluation/'comparison.json').write_bytes(encoded(dict(rows=[dict(execution='completed', numerical_screen='failed')])))

    monkeypatch.setattr(module, 'run_campaign', run)
    argv = [str(CLI), 'run', '--train-record', str(path), '--output', str(output)]
    monkeypatch.setattr(sys, 'argv', argv)
    assert module.main() == 1
    monkeypatch.setattr(sys, 'argv', argv+['--resume', '--retry-failed'])
    assert module.main() == 1
    assert calls == [dict(resume=False, retry_failed=False), dict(resume=True, retry_failed=True)]


def test_reference_replay_requires_explicit_selection(tmp_path, monkeypatch):
    module = cli_module()
    from engineering.civil_exploration import programme
    calls = []
    monkeypatch.setattr(programme, 'run', lambda output, **kwargs: calls.append((output, kwargs)))
    output = tmp_path/'reference'
    monkeypatch.setattr(sys, 'argv', [str(CLI), 'programme', '--deployment', 'reference', '--quick', '--output', str(output)])
    assert module.main() == 0
    assert calls == [(output, dict(full=False, search_evaluations=32))]


def test_retained_baghdad_readiness_matches_generator(tmp_path):
    report = load(HERE/'examples/baghdad-qualification/qualification.json')
    assert report == qualification.build()
    assert not report['physical_release'] and report['supplier_pattern'] is None
    output = qualification.write(report, tmp_path/'readiness')
    assert (output/'qualification.md').read_bytes() == (HERE/'examples/baghdad-qualification/qualification.md').read_bytes()

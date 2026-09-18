import copy
import importlib.util
import json
from pathlib import Path
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('design_options', ROOT / 'engineering/design-options/workflow.py')
option = importlib.util.module_from_spec(spec)
spec.loader.exec_module(option)


def profile(city='samawah', **settings):
    return dict(schema='osr-design-option/1', city=city, id='test-option', lines={'line-1': settings})


def resolved(p):
    return option.resolve(p, option.read(option.GENERIC))


@pytest.mark.parametrize('settings', [dict(additional_trainsets=True), dict(additional_trainsets=1.5),
    dict(additional_storage_modules=-1), dict(additional_pv_kw=float('nan')),
    dict(additional_pv_kw=float('inf')), dict(charging_dwell_seconds=601),
    dict(charging_dwell_seconds=None), dict(unknown=2)])
def test_invalid_or_unknown_settings_are_rejected(settings):
    with pytest.raises(ValueError):
        resolved(profile(**settings))


def test_unknown_profile_keys_and_paths_are_rejected():
    for p in [dict(profile(), release=True), dict(profile(), city='../mosul')]:
        with pytest.raises(ValueError):
            resolved(p)


def source(city='Samawah'):
    path = ROOT / 'cities/catalogue/west-asia/Iraq' / city / 'design.toml'
    design = tomllib.loads(path.read_text())
    baseline = tomllib.loads(option.generate_scenario(design, path, ROOT / 'lib/templates'))
    return path, design, baseline


def test_energy_dwell_and_fleet_changes_reach_the_scenario_without_changing_service_contract():
    path, design, baseline = source()
    settings = resolved(profile(charging_dwell_seconds=330, additional_trainsets=4,
                               additional_storage_modules=2, additional_pv_kw=200))
    original = copy.deepcopy(design)
    candidate, ledger = option.apply_option(design, baseline, settings)
    scenario = tomllib.loads(option.generate_scenario(candidate, path, ROOT / 'lib/templates'))
    option.check_effects(baseline, scenario, settings, design)
    assert original == design
    assert tomllib.loads(option.toml_snapshot(candidate)) == candidate
    assert ledger['resource_delta']['additional_trainsets'] == 4
    assert ledger['resource_delta']['additional_storage_modules'] > 2
    assert ledger['resource_delta']['additional_storage_kwh'] > 0
    assert not ledger['costs_recomputed']
    selected = {s['id'] for s in design['stations'] if s['line'] == 'line-1'}
    for a, b in zip(baseline['sites'], scenario['sites']):
        if a['station'] not in selected:
            assert a == b
        else:
            assert b['storage_capacity_kwh'] == a['storage_capacity_kwh'] + 2 * a['storage_module_kwh']
            assert b['storage_max_discharge_kw'] == a['storage_max_discharge_kw']
    scenario['fleets'][0]['schedule'][0]['headway_min'] += 1
    with pytest.raises(ValueError, match='timetable'):
        option.check_effects(baseline, scenario, settings, design)


def test_ignored_settings_and_unknown_lines_fail():
    _, design, baseline = source()
    p = resolved(profile(charging_dwell_seconds=330))
    with pytest.raises(ValueError, match='not effective'):
        option.check_effects(baseline, baseline, p, design)
    p['lines']['unknown'] = p['lines'].pop('line-1')
    with pytest.raises(ValueError, match='unknown city line'):
        option.apply_option(design, baseline, p)


def test_empty_city_overlay_is_a_no_op():
    _, design, baseline = source()
    p = profile();p['lines'] = {}
    candidate, ledger = option.apply_option(design, baseline, resolved(p))
    assert candidate == design and not ledger['changes']


def test_changed_bundle_and_results_cannot_reuse_pass(tmp_path):
    (tmp_path / 'design.toml').write_text('x=1\n')
    option.write(tmp_path / 'manifest.json', dict(schema='osr-design-option-bundle/1', city='samawah',
        files={'design.toml': option.sha(tmp_path / 'design.toml')}, inputs={}))
    option.verify(tmp_path)
    (tmp_path / 'design.toml').write_text('x=2\n')
    with pytest.raises(ValueError, match='Changed bundle'):
        option.verify(tmp_path)
    (tmp_path / 'design.toml').write_text('x=1\n')
    option.write(tmp_path / 'result.json', dict(manifest_sha256='old', qualification_sha256='old'))
    with pytest.raises(ValueError, match='does not match'):
        option.verify(tmp_path)


@pytest.mark.parametrize('name', ['samawah-fleet12', 'samawah-fleet20', 'mosul-energy'])
def test_retained_options_bind_actual_full_qualification(name):
    folder = ROOT / 'engineering/design-options/examples' / name
    manifest = option.verify(folder, current=False)
    report = option.read(folder / 'qualification.json')
    result = option.read(folder / 'result.json')
    assert manifest['canonical_scenario_matches_generator']
    assert report['resilience_required'] and len(report['resilience_cases']) == 8
    assert report['full_window_passed'] and report['qualification_inputs_unchanged']
    assert result['passed'] is (name != 'samawah-fleet12')
    assert result['operating_release'] is False


def test_current_source_check_is_distinct_from_historical_integrity(tmp_path, monkeypatch):
    monkeypatch.setattr(option, 'ROOT', tmp_path)
    source = tmp_path / 'source.py';source.write_text('original')
    folder = tmp_path / 'bundle';folder.mkdir()
    option.write(folder / 'manifest.json', dict(schema='osr-design-option-bundle/1',
        files={}, inputs={'source.py': option.sha(source)}))
    option.verify(folder)
    source.write_text('changed')
    with pytest.raises(ValueError, match='Changed source'):
        option.verify(folder)
    option.verify(folder, current=False)


@pytest.mark.parametrize('field,value', [('passed', True), ('operating_release', True)])
def test_failed_option_cannot_be_relabelled_as_passed_or_released(tmp_path, field, value):
    import shutil
    folder = tmp_path / 'option'
    shutil.copytree(ROOT / 'engineering/design-options/examples/samawah-fleet12', folder)
    result = option.read(folder / 'result.json');result[field] = value
    option.write(folder / 'result.json', result)
    with pytest.raises(ValueError):
        option.verify(folder, current=False)

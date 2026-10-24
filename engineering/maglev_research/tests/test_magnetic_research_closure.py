"""Research reporting must preserve joint load, winding and thermal failures."""
from copy import deepcopy
from hashlib import sha256
import itertools
import json

import pytest

from engineering.maglev_research import magnetic_research_closure as closure


@pytest.fixture(scope='module')
def archive():
    _, _, records, inputs, summary = closure._load(closure.ROOT)
    return records, inputs, summary


def test_archive_counts_and_independent_winding_lower_bounds(archive):
    records, inputs, summary = archive
    result = closure.assess(records, inputs, summary)
    assert result['executed_case_records'] == 225
    assert result['original_static_passes'] == 4
    assert result['original_1_3_aw3_passes'] == 0
    assert result['conditional_topology_1_3_aw3_passes'] == 15
    assert result['guidance_combined_passes'] == 0
    assert result['baseline_failure_invariant']
    best = result['best_fitting_guidance']
    assert best['id'] == 'guide-w22.5-s2.40-n200-a13.4-wide'
    assert best['fixed_load_required_conductor_area_mm2'][1] == pytest.approx(16.7435652682)
    assert best['fixed_load_required_guide_fill'] == pytest.approx(.682101596)
    assert best['fixed_load_required_guide_fill'] > inputs['coil_fill_limit']
    assert best['fixed_load_required_cooling_at120c_w_k'][1] == pytest.approx(49.8823258335)
    assert not result['configuration_adopted']
    assert not result['complete_system_feasible']


@pytest.mark.parametrize('field,value', [
    ('original_cases_with_static_screen', 15),
    ('topological_sensitivities_with1_3screen', 14),
    ('guidance_combined_screen_passes', 1),
])
def test_misleading_summary_counts_are_refused(archive, field, value):
    records, inputs, summary = archive
    changed = deepcopy(summary)
    changed[field] = value
    with pytest.raises(ValueError, match='differs from raw research'):
        closure.assess(records, inputs, changed)


@pytest.mark.parametrize('mutation,error', [
    ('mass', 'AW3 mass feedback'),
    ('density', 'current density'),
    ('thermal', 'thermal equilibrium'),
    ('force', 'achieved joint force'),
    ('combined', 'combined joint screen'),
])
def test_raw_joint_gate_drift_is_refused(archive, mutation, error):
    records, inputs, summary = archive
    changed = deepcopy(records)
    row = changed['guidance-results.json']['cases'][0]
    point = closure._joint_point(row)
    if mutation == 'mass':
        row['controlled_aw3_kg'] -= 100
    elif mutation == 'density':
        point['current_density_a_mm2'][1] = 0.
    elif mutation == 'thermal':
        point['constant_current_thermal_equilibrium_c'][1] = 80.
    elif mutation == 'force':
        point['actual_force_n'][1] -= 100.
    else:
        row['conditional_nominal_aw3_lateral_screen'] = True
    with pytest.raises(ValueError, match=error):
        closure.assess(changed, inputs, summary)


def test_audit_does_not_modify_sealed_archive(archive):
    path = closure.ROOT / closure.ARCHIVE
    before = sorted(str(p.relative_to(path)) for p in path.rglob('*'))
    result = closure.audit()
    assert sorted(str(p.relative_to(path)) for p in path.rglob('*')) == before
    assert len(result['source_sha256']) == 2
    json.dumps(result, allow_nan=False)


def test_existing_optimisation_output_is_never_overwritten(tmp_path):
    output = tmp_path / 'receipt.json'
    output.write_text('retained execution')
    with pytest.raises(ValueError, match='retain prior optimisation evidence'):
        closure.optimise(output)
    assert output.read_text() == 'retained execution'


def test_executed_optimisation_is_source_bound_complete_and_preserves_failures(archive):
    records, inputs, _ = archive
    output = closure.ROOT / 'docs/design-engine/ferrite-maglev/research-closure/magnetic-optimisation.json'
    result = json.loads(output.read_text())
    assert result['schema'] == 'osr-bounded-magnetic-winding-optimisation/1'
    for name, expected in result['source_sha256'].items():
        assert sha256((closure.ROOT / name).read_bytes()).hexdigest() == expected
    expected_plans = list(itertools.product((.020, .0225, .025, .0275, .030, .035),
                                           (1.5, 1.75, 2., 2.2, 2.4),
                                           (140., 200.), (False, True), (False, True)))
    assert result['executed_cases'] == len(result['cases']) == len(expected_plans) == 240
    parent = records['results.json']
    for row, (width, scale, turns, large, sensitive) in zip(result['cases'], expected_plans):
        hypothesis = row['hypothesis']
        assert hypothesis['width_m'] == width
        assert hypothesis['core_scale'] == scale
        assert hypothesis['guide_turns'] == turns
        assert hypothesis['wide_pack'] is large
        assert hypothesis['topology'] == ('useful-only-poles-sensitivity' if sensitive else 'original-branch-flux')
        assert row['module_mass_kg'] == pytest.approx(row['counted_stock_mass_kg'])
        assert row['controlled_aw3_kg'] == pytest.approx(parent['parent_aw3_kg'] + 24 * (row['module_mass_kg'] - parent['parent_module_mass_kg']))
        point = row['nominal_joint']
        assert point['actual_force_n'] == pytest.approx(point['target_n'])
        assert row['normalised_constraint_ratios']['density'] == pytest.approx(max(point['current_density_a_mm2']) / inputs['continuous_current_density_a_mm2'])
        assert row['normalised_constraint_ratios']['thermal'] == pytest.approx(max(required / available for required, available in zip(row['fixed_current_required_cooling_at120c_w_k'], [24., 18.])))
        passed = bool(row['nominal_aabb_clear'] and max(row['copper_fill_fractions']) <= inputs['coil_fill_limit']
                      and point['map_valid'] and point['continuous_current_density_screen'] and point['constant_current_thermal_screen'])
        assert row['joint_screen_pass'] is passed
        assert not row['topology_independently_validated']
        assert not row['configuration_adopted']
    assert result['joint_screen_passes'] == sum(row['joint_screen_pass'] for row in result['cases']) == 0
    assert not result['complete_system_feasible']
    assert not result['configuration_adopted']


@pytest.mark.parametrize('mutation', ['sources', 'cases', 'hypothesis', 'mass', 'joint', 'rank', 'best', 'model'])
def test_optimisation_cannot_drop_bindings_cases_or_misreport_screens(archive, monkeypatch, mutation):
    records, inputs, summary = archive
    monkeypatch.setattr(closure, '_load', lambda root: (closure.ROOT / closure.ARCHIVE, {}, records, inputs, summary))
    receipt = closure.ROOT / 'docs/design-engine/ferrite-maglev/research-closure/magnetic-optimisation.json'
    value = json.loads(receipt.read_text())
    if mutation == 'sources':
        value['source_sha256'] = {}
    elif mutation == 'cases':
        value['cases'] = []
        value['executed_cases'] = 0
        value['joint_screen_passes'] = 0
    elif mutation == 'hypothesis':
        value['cases'][0]['hypothesis']['width_m'] = .03
    elif mutation == 'mass':
        value['cases'][0]['controlled_aw3_kg'] = 30000.
    elif mutation == 'joint':
        value['cases'][0]['nominal_joint']['constant_current_thermal_screen'] = True
    elif mutation == 'rank':
        value['cases'][0]['maximum_constraint_ratio'] = .5
    elif mutation == 'best':
        value['best_by_topology']['original-branch-flux'] = value['best_by_topology']['useful-only-poles-sensitivity']
    else:
        value['source_model_sha256'] = {}
    with pytest.raises(ValueError):
        closure.validate_optimisation(value)


def test_optimisation_rejects_source_mutation_during_execution(tmp_path, monkeypatch):
    archive = tmp_path / closure.ARCHIVE
    (archive / 'evidence').mkdir(parents=True)
    frozen = b'pass\n'
    names = ('run.py', 'run_topology.py', 'run_controls.py', 'run_guidance.py')
    for name in names:
        (archive / 'evidence' / name).write_bytes(frozen)
    manifest = {'files_sha256': {'evidence/' + name: sha256(frozen).hexdigest() for name in names}}
    for name in closure.SOURCE_NAMES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(json.dumps(manifest).encode() if name.endswith('manifest.json') else b'original-source')
    monkeypatch.setattr(closure, '_load', lambda root: (archive, [], {}, {}, {}))

    def changed_during_run(command, **kwargs):
        work = closure.Path(command[1]).parent
        assert (work / 'closure_sweep.py').read_bytes() == b'original-source'
        (work / 'closure-sweep.json').write_text('{}')
        (tmp_path / closure.SOURCE_NAMES[2]).write_text('concurrent edit')

    monkeypatch.setattr(closure.subprocess, 'run', changed_during_run)
    output = tmp_path / 'result.json'
    with pytest.raises(ValueError, match='sources changed during execution'):
        closure.optimise(output, root=tmp_path)
    assert not output.exists()

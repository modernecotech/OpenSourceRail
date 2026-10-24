"""Cross-workstream identity, complete qualification coverage and stale evidence."""
from copy import deepcopy
import json
import tomllib

import pytest

from engineering.maglev_research import research_closure as closure


@pytest.fixture(scope='module')
def inputs():
    return (closure.magnetic_research_closure.audit(), closure.propulsion_research.study(),
            closure.dynamics_readiness.study(),
            closure.check_optimisation(json.loads(closure.OPTIMISATION.read_bytes())),
            closure.qualification.study())


def test_complete_original_worklist_is_preserved_without_physical_credit(inputs):
    result = closure.assemble(*deepcopy(inputs))
    original = inputs[-1]
    assert len(result['tasks']) == original['coverage']['tasks'] == 576
    assert {task['id'] for task in result['tasks']} == {task['id'] for task in original['tasks']}
    assert all(task['state'] == 'hold' and task['accepted'] is False for task in result['tasks'])
    assert all(result[key] is False for key in closure.FLAGS)
    assert result['full_line_rerun_ready'] is False
    positions = {identity: index for index, identity in enumerate(result['topological_task_order'])}
    for task in result['tasks']:
        assert all(positions[dependency] < positions[task['id']] for dependency in task['prerequisites'])
    assert len(result['workstreams']) == 8
    admission = {row['id']: row['evidence'] for row in result['admission_requirements']}
    assert 'selected formation' in admission['maps-and-initial-equilibrium']
    assert 'separate preserved reference' in admission['maps-and-initial-equilibrium']
    assert 'no inherited six-car credit' in admission['continued-fault-motion']
    experiments = {row['id']: row for row in result['next_magnetic_experiments']}
    assert len(experiments) == 4
    for row in experiments.values():
        assert row['executed'] is False
        pair = [experiments[key] for key in row['comparison_pair_ids']]
        assert len(pair) == 2
        geometries = [{k: v for k, v in case['hypothesis'].items() if k != 'topology'} for case in pair]
        assert geometries[0] == geometries[1]


@pytest.mark.parametrize('change,error', [
    (lambda values: values[1].update(parent_configuration_sha256='b'*64), 'mixed research'),
    (lambda values: values[2].update(eligible_for_adoption=True), 'cannot adopt'),
    (lambda values: values[4]['tasks'][0].update(accepted=True), 'cannot close'),
    (lambda values: values[4]['tasks'].pop(), 'coverage differs'),
    (lambda values: values[4]['groups'].pop(), 'workstream owner'),
])
def test_mixed_identity_and_earned_credit_are_not_silently_imported(inputs, change, error):
    values = deepcopy(inputs)
    change(values)
    with pytest.raises(ValueError, match=error):
        closure.assemble(*values)


@pytest.mark.parametrize('rows,error', [
    ([dict(id='a', prerequisites=['missing'])], 'unknown task'),
    ([dict(id='a', prerequisites=['b']), dict(id='b', prerequisites=['a'])], 'cyclic'),
    ([dict(id='a', prerequisites=[]), dict(id='a', prerequisites=[])], 'unique'),
])
def test_invalid_dependency_graph_is_held(rows, error):
    with pytest.raises(ValueError, match=error):
        closure.task_order(rows)


def test_optimisation_drift_cannot_invent_a_surviving_design(inputs):
    receipt = deepcopy(inputs[3])
    receipt['joint_screen_passes'] = 1
    with pytest.raises(ValueError, match='survivor count'):
        closure.check_optimisation(receipt)
    receipt = deepcopy(inputs[3])
    receipt['cases'][0]['joint_screen_pass'] = True
    with pytest.raises(ValueError, match='joint screen differs'):
        closure.check_optimisation(receipt)
    receipt = deepcopy(inputs[3])
    receipt['cases'][0]['topology_independently_validated'] = True
    with pytest.raises(ValueError, match='topology validation'):
        closure.check_optimisation(receipt)


def test_stale_optimisation_source_is_held(inputs):
    receipt = deepcopy(inputs[3])
    name = next(iter(receipt['source_sha256']))
    receipt['source_sha256'][name] = '0'*64
    with pytest.raises(ValueError, match='stale optimisation source'):
        closure.check_optimisation(receipt)


def test_publication_recomputes_payload_and_rejects_modified_plan(inputs, tmp_path, monkeypatch):
    monkeypatch.setattr(closure, 'study', lambda _: closure.assemble(*deepcopy(inputs)))
    closure.publish(tmp_path)
    closure.publish(tmp_path, check=True)
    path = tmp_path/'execution-plan.json.gz'
    path.write_bytes(path.read_bytes()[:-1])
    with pytest.raises(ValueError, match='stale research publication'):
        closure.publish(tmp_path, check=True)


@pytest.fixture(scope='module')
def design_inputs():
    return [*(json.loads((closure.OUTPUT/name).read_bytes()) for name in (
        'support-architecture.json', 'service-envelope.json',
        'service-envelope-proposed-mass.json', 'carrier-geometry.json')),
        tomllib.loads(closure.Path(closure.__file__).with_name('design-intent.toml').read_text())]


def test_service_and_support_share_the_same_lower_bound_mass_without_installation_credit(design_inputs):
    result = closure.validate_design_round(*deepcopy(design_inputs))
    mass = result['support']['recommended_next_design_contract']['controlled_aw3_material_lower_bound_kg_per_car']
    assert result['service_at_support_material_mass']['assumptions']['aw3_mass_kg_per_car'] == mass
    assert mass > result['service_at_canonical_comparison_mass']['assumptions']['aw3_mass_kg_per_car']
    assert result['specification_decision']['common_accepted_configuration'] is False
    assert result['specification_decision']['carrier_and_remaining_installed_mass_reconciled'] is False
    assert result['specification_decision']['existing_defaults_changed'] is False
    assert result['design_intent']['service_comparison']['reference_normal_capacity_passengers_hour_direction'] == 14400


@pytest.mark.parametrize('change,error', [
    (lambda values: values[2]['assumptions'].update(aw3_mass_kg_per_car=37618.), 'masses differ'),
    (lambda values: values[2]['comparison_mass_support_binding'].update(proposed_case_id='other'), 'identities differ'),
    (lambda values: values[3].update(parent_configuration_sha256='b'*64), 'mixed second-round'),
    (lambda values: values[3].update(configuration_adopted=True), 'cannot adopt'),
    (lambda values: values[1].update(physical_validation=True), 'physical validation'),
    (lambda values: values[3].update(complete_installed_carrier_fit=True), 'installed acceptance'),
    (lambda values: values[4]['service_comparison'].update(reference_normal_capacity_passengers_hour_direction=10000), 'capacity floor changed'),
    (lambda values: values[3].update(dynamics_rerun_ready=True), 'dynamics readiness'),
    (lambda values: values[4]['unchanged_magnetic_screens'].update(current_limit_a=999.), 'magnetic screen differs'),
    (lambda values: values[4]['unchanged_magnetic_screens'].update(support_peak_load_factor=1.), 'magnetic screen differs'),
    (lambda values: values[4]['unchanged_magnetic_screens'].update(limits_are_independently_qualified=True), 'independently qualified'),
])
def test_research_round_cannot_mix_mass_reduce_capacity_or_promote_stock_geometry(design_inputs, change, error):
    values = deepcopy(design_inputs)
    change(values)
    with pytest.raises(ValueError, match=error):
        closure.validate_design_round(*values)

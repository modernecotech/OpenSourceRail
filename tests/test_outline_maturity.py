from copy import deepcopy

import pytest

from engineering.outline import maturity
from engineering.station_rail.common import identity, encoded


def outline():
    return dict(outline_id='railway-outline-1', requirements_id='service-requirements-1',
        envelopes=[dict(id='carbody', dimensions_m=[17., 2.65, 3.])],
        bounded_mass_kg=dict(low=18000., base=22000., high=28000.),
        costs=dict(low=100., base=200., high=400., currency='IQD', source_class='C'),
        manufacturing_routes=[dict(part='body', process='cut; assemble; inspect', provisional=True)],
        service_constraints=[dict(key='normal-capacity', status='pass', required_at='outline',
            known_physical_contradiction=False, explanation='Declared formation and headway provide the target arithmetic capacity.')],
        assumptions=[dict(id='thrust-study', bounds=dict(low=100000., base=150000., high=200000.),
            source='Class C engineering scenario', purpose='Conditional launch sizing before a motor map is validated.')])


def constraint(key, status, phase, **extra):
    return dict(key=key, status=status, required_at=phase,
        known_physical_contradiction=False, explanation=key+' needs the appropriate evaluator/evidence.', **extra)


def test_bounded_class_c_outline_is_positively_accepted_without_physical_promotion():
    record = outline(); original = deepcopy(record); result = maturity.assess(record)
    assert result['outline_acceptance'] == 'accepted'
    assert result['outline_accepted'] and result['comparison_admitted'] and result['detailing_admitted']
    assert result['execution'] == 'completed'
    assert result['concept_screen'] == result['detailed_design'] == result['prototype_validation'] == 'not-assessed'
    assert all(result[key] is False for key in maturity.FLAGS)
    assert result['qualification_authority']['workflow'] == 'engineering.railway_completion.evidence'
    assert record == original
    assert result['evaluation_id'] == identity({k:v for k,v in result.items() if k != 'evaluation_id'})
    assert encoded(maturity.assess(record)) == encoded(result)


def test_missing_quotes_and_prototype_tests_are_later_tasks_not_outline_failures():
    record = outline()
    record['service_constraints'] += [constraint('supplier-quotation', 'unknown', 'release'),
        constraint('prototype-braking', 'unknown', 'prototype'), constraint('detailed-joint', 'unknown', 'detail')]
    result = maturity.assess(record)
    assert result['outline_acceptance'] == 'accepted' and result['reasons'] == []
    assert {x['phase'] for x in result['next_tasks']} == {'release', 'prototype', 'detail'}
    assert not any(x['blocks_outline'] for x in result['next_tasks'])


def test_known_physical_contradiction_requires_revision_even_when_its_test_is_later():
    record = outline(); row = constraint('door-clearance', 'fail', 'detail')
    row['known_physical_contradiction'] = True
    record['service_constraints'].append(row)
    result = maturity.assess(record)
    assert result['outline_acceptance'] == 'needs-revision'
    assert result['comparison_admitted'] is False
    assert next(x for x in result['findings'] if x['key'] == 'door-clearance')['physical_failure_inferred'] is True
    assert any(x['kind'] == 'revise-outline' and x['blocks_outline'] for x in result['next_tasks'])


def test_unlocated_mass_and_envelope_can_be_sufficient_without_installed_geometry():
    record = outline(); record['installed_mass_complete'] = False
    record['service_constraints'].append(constraint('installed-connections', 'unknown', 'detail'))
    assert maturity.assess(record)['outline_acceptance'] == 'accepted'


def test_unknown_current_requirement_needs_explicit_bounded_assumption():
    record = outline(); record['service_constraints'].append(constraint('launch-target', 'unknown', 'outline'))
    unresolved = maturity.assess(record)
    assert unresolved['outline_acceptance'] == 'needs-definition'
    assert not any(x['physical_failure_inferred'] for x in unresolved['findings'])
    record['service_constraints'][-1]['assumption_id'] = 'thrust-study'
    result = maturity.assess(record)
    assert result['outline_acceptance'] == 'accepted'
    assert result['findings'][-1]['disposition'] == 'conditionally-satisfied'
    assert any(x['phase'] == 'concept' and x['kind'] == 'evaluate-assumption' for x in result['next_tasks'])


def test_out_of_domain_or_axial_pin_failure_is_not_a_full_shell_physical_failure():
    record = outline(); record['service_constraints'] += [constraint('coarse-shell', 'out-of-domain', 'concept'),
        constraint('axial-pin-mechanism', 'fail', 'detail')]
    result = maturity.assess(record)
    assert result['outline_acceptance'] == 'accepted'
    assert not any(x['physical_failure_inferred'] for x in result['findings'])
    assert any(x['kind'] == 'extend-evaluator' for x in result['next_tasks'])


def test_synthetic_force_map_never_becomes_an_available_force_map():
    record = outline(); record['service_constraints'].append(constraint('force-map', 'pass', 'outline',
        synthetic=True, assumption_id='thrust-study'))
    record['available_force_map_admitted'] = True
    result = maturity.assess(record)
    assert result['outline_acceptance'] == 'accepted'
    assert result['available_force_map_admitted'] is False
    assert result['native_evaluator_admission'] is False
    assert 'available_force_map_admitted' in result['blocked_release_claims']
    del record['service_constraints'][-1]['assumption_id']
    assert maturity.assess(record)['outline_acceptance'] == 'needs-definition'


def test_claimed_physical_or_operation_approval_cannot_promote_any_gate():
    record = outline(); record.update(physical_accepted=True, engineering_accepted=True,
        manufacturing_release=True, operating_release=True, selected_reference_changed=True)
    result = maturity.assess(record)
    assert result['outline_acceptance'] == 'accepted'
    assert all(result[key] is False for key in maturity.FLAGS)
    assert set(('physical_accepted','manufacturing_release','operating_release')).issubset(result['blocked_release_claims'])
    assert any(x['kind'] == 'existing-qualification-review' for x in result['next_tasks'])


def test_missing_cost_is_needs_definition_and_remains_none_instead_of_zero():
    record = outline(); record['costs'] = None
    result = maturity.assess(record)
    assert result['outline_acceptance'] == 'needs-definition'
    assert result['resolved_cost_bounds'] is None
    assert any(x['key'] == 'costs' for x in result['reasons'])


def test_named_bounded_quantity_can_complete_mass_without_inventing_values():
    record = outline(); record['assumptions'].append(dict(id='mass-study',
        bounds=dict(low=17000., base=23000., high=29000.), source='Counted components plus reserve', purpose='Outline mass envelope'))
    record['bounded_mass_kg'] = dict(assumption_id='mass-study')
    result = maturity.assess(record)
    assert result['outline_acceptance'] == 'accepted'
    assert result['resolved_mass_bounds_kg'] == dict(low=17000., base=23000., high=29000.)


def test_later_missing_assumption_link_is_a_later_definition_task():
    record = outline(); record['service_constraints'].append(constraint('fatigue-map', 'unknown', 'detail', assumption_id='future-model'))
    result = maturity.assess(record)
    assert result['outline_acceptance'] == 'accepted'
    assert not any(task['blocks_outline'] for task in result['next_tasks'])


@pytest.mark.parametrize('field', ['envelopes', 'bounded_mass_kg', 'manufacturing_routes', 'service_constraints'])
def test_missing_outline_input_requires_definition(field):
    record = outline(); record.pop(field)
    assert maturity.assess(record)['outline_acceptance'] == 'needs-definition'


@pytest.mark.parametrize('field,key,value', [
    ('costs','base',float('nan')), ('costs','low',-1.), ('costs','high',150.),
    ('bounded_mass_kg','low',0.), ('bounded_mass_kg','base',40000.), ('costs','base',True)])
def test_nonfinite_negative_zero_or_inverted_bounds_are_rejected(field, key, value):
    record = outline(); record[field][key] = value
    with pytest.raises(ValueError): maturity.assess(record)


@pytest.mark.parametrize('sizes', [[17., -2., 3.], [17., 0., 3.], [17., float('inf'), 3.], [17., 2.]])
def test_invalid_envelope_bounds_are_rejected(sizes):
    record = outline(); record['envelopes'][0]['dimensions_m'] = sizes
    with pytest.raises(ValueError): maturity.assess(record)


def test_unsupported_model_cannot_declare_known_physical_contradiction():
    record = outline(); row = constraint('shell-domain', 'out-of-domain', 'concept')
    row['known_physical_contradiction'] = True; record['service_constraints'].append(row)
    with pytest.raises(ValueError): maturity.assess(record)


@pytest.mark.parametrize('field', ['outline_id', 'requirements_id'])
def test_constraint_cannot_borrow_another_outlines_result(field):
    record = outline(); record['service_constraints'][0][field] = 'different-outline-or-requirements'
    with pytest.raises(ValueError, match='Mixed'): maturity.assess(record)


def test_negative_grade_can_be_an_explicit_bounded_assumption_not_negative_mass_or_cost():
    record = outline(); record['assumptions'].append(dict(id='grade',
        bounds=dict(low=-.02, base=0., high=.02), source='Synthetic alignment range', purpose='Explore gradients'))
    assert maturity.assess(record)['outline_acceptance'] == 'accepted'


def test_unexecuted_physics_is_not_relabelled_as_completed_by_policy_execution():
    record = outline(); record.update(execution='not-run', numerical_validity='outside-domain')
    result = maturity.assess(record)
    assert result['execution'] == 'completed'
    assert result['execution_scope'] == 'outline-policy-assessment-only'
    assert result['reported_execution'] == 'not-run'
    assert result['reported_numerical_validity'] == 'outside-domain'
    assert result['numerical_validity'] == 'not-required-for-outline-acceptance'

"""Independent architecture identity, interface and redesign checks."""
from copy import deepcopy
import pytest
from engineering.reference_cell import architecture as a

REQ=dict(cars=6,normal_places_per_car=46,speed_cap_m_s=20.,headway_s=120.)
CHOICES=dict(body='V1',**{'running-gear':'passive'},propulsion='five-20m',guideway='box',station='accessible-two-station',manufacturing='local-modular')


def test_registry_composes_full_typed_candidate_and_keeps_unsupported_architecture_open():
    r=a.defaults();v=r.bundle(CHOICES,REQ)
    assert set(v['components'])==set(a.KINDS) and not v['physical_accepted']
    choices=dict(CHOICES,propulsion='station-cable');other=r.bundle(choices,REQ)
    assert other['candidate_id']!=v['candidate_id'] and 'propulsion' in other['unsupported_evaluators']
    assert all(k in r.records for k in [('body','V5'),('guideway','u'),('propulsion','six-20m'),('propulsion','continuous-500m')])


def test_registration_rejects_duplicate_wrong_interface_imported_executable_and_nan():
    r=a.Registry();r.register('body','new',{'shape':'test'},a.PORTS['body'])
    with pytest.raises(ValueError):r.register('body','new',{},a.PORTS['body'])
    with pytest.raises(ValueError):r.register('body','other',{},a.PORTS['propulsion'])
    with pytest.raises(ValueError):r.register('body','other',{},a.PORTS['body'],evaluator=lambda:True)
    with pytest.raises(ValueError):r.register('body','other',{'thickness':float('nan')},a.PORTS['body'])


def test_evaluator_only_change_is_evaluation_revision_not_new_hardware():
    a1=a.Registry();a2=a.Registry()
    r1=a1.register('propulsion','same',{'length_m':20.},a.PORTS['propulsion'],evaluator='solver-A')
    r2=a2.register('propulsion','same',{'length_m':20.},a.PORTS['propulsion'],evaluator='solver-B')
    assert r1['definition_id']==r2['definition_id']
    assert r1!=r2
    r3=a.Registry().register('propulsion','same',{'length_m':25.},a.PORTS['propulsion'],evaluator='solver-A')
    assert r3['definition_id']!=r1['definition_id']


def test_grade_to_geometry_to_axles_cost_control_selection_dependencies_are_transitive():
    v=set(a.invalidated(['materials']))
    assert {'materials','geometry','mass','propulsion','brakes','journey','civil','construction','energy','cost','selection','controls'}<=v
    assert len(a.invalidated(['mass','mass']))==len(a.invalidated(['mass']))
    with pytest.raises(ValueError):a.invalidated(['imaginary-stage'])


@pytest.mark.parametrize('failure',['physical','numerical','missing-evidence','cost'])
def test_failure_diagnosis_keeps_experiment_selection_separate_from_integrated_baseline(failure):
    v=a.revision('a'*64,failure,[{'result':'bounded-observation'}])
    assert v['parent_candidate_id']=='a'*64 and v['selection_purpose']=='next-experiment-only'
    assert v['integrated_winner'] is None and not v['selected_reference_changed']
    assert bool(v['permitted_actions']) and bool(v['invalidated_stages'])


def test_invalid_failure_identity_or_empty_observation_rejected():
    with pytest.raises(ValueError):a.revision('not-a-hash','physical',[{'reason':'test'}])
    with pytest.raises(ValueError):a.revision('a'*64,'physical',[])
    with pytest.raises(ValueError):a.revision('a'*64,'ambiguous',[{'reason':'test'}])

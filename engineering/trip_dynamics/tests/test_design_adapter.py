from copy import deepcopy
import pytest
from engineering.design_search.contracts import make_candidate
from engineering.design_search.registry import ImmutableRegistry
from engineering.trip_dynamics.design_adapter import evaluate_preflight
from engineering.trip_dynamics.scenario import scenario


def candidate():
    return make_candidate(requirement_revision='trip-test-r1', architecture={'cars':6},
        frames=[dict(id='world', parent_id=None, origin_m=[0.,0.,0.], rotation_matrix=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])],
        materials=[dict(id='GFRP', density_kg_m3=1800., basis='fixture only')],
        geometry=[dict(id='shell', kind='unresolved-equipment', frame_id='world', material_id='GFRP')],
        interfaces=[], installed_inventory=[dict(id='equipped-car', geometry_id='shell', frame_id='world',
            quantity=1, status='unknown', scope='vehicle-per-car', basis='missing installed stock', unit_mass_kg=None)])


def test_registry_records_real_preflight_without_feasibility(tmp_path):
    c = candidate(); s = scenario('candidate-AW3', 2000, 'AW3')
    r = evaluate_preflight(c, s, registry=tmp_path)
    assert r['execution_status'] == 'executed' and r['screen_status'] == 'unknown'
    assert r['metrics']['installed_mass_properties']['total_mass_kg'] is None
    assert not r['physical_accepted'] and r['metrics']['dynamic_execution'] == 'not-run'
    assert ImmutableRegistry(tmp_path).cached(r['request']) == r
    r2 = evaluate_preflight(c, scenario('candidate-hot', 2000, 'AW3', temperature_C=50.), registry=tmp_path)
    assert r2['evaluation_id'] != r['evaluation_id']


def test_ideal_benchmark_cannot_be_registered_as_candidate_evidence():
    with pytest.raises(ValueError, match='evidence mode'):
        evaluate_preflight(candidate(), scenario('ideal', 2000, 'AW3', mode='benchmark'))


def test_foreign_modal_model_refused():
    with pytest.raises(ValueError, match='different physical candidate'):
        evaluate_preflight(candidate(), scenario('id', 2000, 'AW3'), modal_model={'candidate_id':'f'*64})

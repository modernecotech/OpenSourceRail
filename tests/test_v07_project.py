from copy import deepcopy
import pytest
from engineering.v07_project import DEPENDENCIES, affected, stage_record, compose


def records():
    result = {}
    for stage, dependencies in DEPENDENCIES.items():
        result[stage] = stage_record(stage, 'a'*64, 'b'*64,
            source_sha256={'solver.py': 'c'*64},
            dependencies={key: result[key]['stage_id'] for key in dependencies})
    return result


def test_station_edit_reuses_vehicle_and_manufacturing():
    stages = affected(['geometry'])
    assert 'service' in stages and 'civil' in stages and 'dossier' in stages
    assert 'vehicle' not in stages and 'manufacturing' not in stages and 'maintenance' not in stages
    assert affected(['cost']) == ['cost', 'delivery', 'dossier']
    assert affected(['vehicle']) == [x for x in DEPENDENCIES if x != 'geometry']
    with pytest.raises(ValueError): affected(['unknown-stage'])


def test_complete_composition_does_not_grant_physical_acceptance():
    result = compose('a'*64, records())
    assert result['composition_complete']
    assert result['engineering_accepted'] is False and result['manufacturing_release'] is False
    assert compose('a'*64, {})['missing_stages'] == list(DEPENDENCIES)


def test_rejects_mixed_candidate_and_stale_upstream():
    value = records()
    value['vehicle'] = stage_record('vehicle', 'd'*64, 'b'*64,
        source_sha256={'solver.py': 'c'*64}, dependencies={})
    with pytest.raises(ValueError, match='Mixed'): compose('a'*64, value)
    value = records()
    value['vehicle'] = stage_record('vehicle', 'a'*64, 'e'*64,
        source_sha256={'solver.py': 'c'*64}, dependencies={})
    with pytest.raises(ValueError, match='stale'): compose('a'*64, value)


def test_mutation_and_unknown_inputs_are_rejected():
    value = deepcopy(records()); value['cost']['artifact_id'] = 'f'*64
    with pytest.raises(ValueError, match='seal'): compose('a'*64, value)
    with pytest.raises(ValueError): stage_record('cost', 'a'*64, 'b'*64,
        source_sha256={}, dependencies={})


def test_corridor_projection_preserves_missing_manufacturing_boundary():
    from engineering.station_rail.common import identity
    from engineering.v07_project import from_comparison
    refs={'candidate_id':'a'*64,'body_candidate_id':'b'*64}
    ids=dict(reference_candidate_ids=refs,city_input_id='c'*64,
             service_evaluation_id='d'*64,civil_quantity_id='e'*64)
    report=dict(schema='osr-corridor-revision-comparison/1',reference_candidate_ids=refs,
                source_sha256={'solver.py':'f'*64},identities={'before':ids,'after':ids})
    report['comparison_id']=identity(report)
    projection=from_comparison(report)
    assert projection['cases']['after']['missing_stages']==['manufacturing','cost','delivery','maintenance','dossier']
    assert projection['cases']['after']['composition_complete'] is False
    report['identities']['after']['city_input_id']='0'*64
    with pytest.raises(ValueError,match='Sealed'):from_comparison(report)

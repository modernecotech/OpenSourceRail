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

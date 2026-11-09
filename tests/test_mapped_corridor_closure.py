from copy import deepcopy

import pytest

from engineering.railway_project import mapped_corridor_closure as closure


def test_closure_audit_preserves_candidate_ancestry_and_open_unknowns():
    source = {'seed/study.json': 'a' * 64, 'geometry/01/result.json': 'b' * 64}
    packet = closure.audit(source_sha256=source)
    assert closure.verify(packet)
    assert packet['candidate_identity']['body_candidate_id'] == closure.BODY
    assert packet['candidate_identity']['whole_candidate_seed_id'] == closure.SEED
    assert packet['candidate_identity']['recovery_equipped_alternative_id'] == closure.RECOVERY_ALTERNATIVE
    assert packet['corridors'][0]['source_stop_ids'] == [
        'line-1-2500-0775-s000000', 'line-1-2343-0771-s003515', 'line-1-2180-0774-s007014']
    assert len(packet['corridors'][1]['source_stop_ids']) == 6
    assert packet['service_context']['corridor_capacity_pphpd'] is None
    assert packet['service_context']['corridor_full_tail_clearance_m'] is None
    assert packet['service_context']['corridor_grade_profile'] is None
    assert packet['coverage']['fourteen_cost_scopes'] == list(closure.SCOPES)
    assert packet['coverage']['scalar_cost_per_km_used'] is False
    assert packet['source_sha256'] == source
    assert all(packet[key] is False for key in (
        'engineering_accepted', 'physical_accepted', 'selected_reference_changed',
        'manufacturing_release', 'operating_release', 'movement_authority'))


def test_audit_rejects_candidate_substitution_and_prior_geometry_rewrite():
    with pytest.raises(ValueError, match='assigned whole-candidate'):
        closure.audit(seed_candidate_id='0' * 64)
    changed = deepcopy(closure.PRIOR_GEOMETRY)
    changed['geometry-preflight-01'] = '0' * 64
    with pytest.raises(ValueError, match='preserved exactly'):
        closure.audit(prior_geometry=changed)


def test_geometry_revision_is_an_explicit_screen_only_ancestry():
    revision = dict(evaluation_id='a' * 64, alignment_evaluation_id='b' * 64,
        alignment_candidate_id='c' * 64, maximum_deviation_m=205.0,
        screen_passed=True, route_m=6405.581584798581, result_sha256='d' * 64)
    packet = closure.audit(geometry_revision=revision)
    assert closure.verify(packet)
    assert packet['revised_geometry_parameter']['evaluated'] is True
    assert packet['geometry_revision'] == revision
    assert packet['physical_accepted'] is False
    revision['screen_passed'] = False
    with pytest.raises(ValueError, match='Exact passing 205 m'):
        closure.audit(geometry_revision=revision)


def test_integrity_check_rejects_false_release_or_mutation():
    packet = closure.audit()
    packet['operating_release'] = True
    with pytest.raises(ValueError, match='identity mismatch'):
        closure.verify(packet)
    packet = closure.audit()
    packet['manufacturing_release'] = True
    packet['evaluation_id'] = closure.identity({k: v for k, v in packet.items() if k != 'evaluation_id'})
    with pytest.raises(ValueError, match='cannot confer acceptance'):
        closure.verify(packet)

"""One-opening route intake refuses proxy geometry and mixed candidates."""
from copy import deepcopy
import json

import pytest

from engineering.station_rail.common import identity
from tools.automation import v07_door_route as route


@pytest.fixture(scope='module')
def route_request():
    raw = route.HANDOFF.read_bytes()
    return route.compile_request(json.loads(raw), raw)


def proposal(request):
    return dict(schema='osr-v07-one-opening-route-proposal/1',
                request_id=request['request_id'],
                physical_candidate_id=request['physical_candidate_id'],
                installed_candidate_id=request['installed_candidate_id'],
                installed_evaluation_id=request['installed_evaluation_id'],
                opening=request['opening'], guide={}, belt={},
                ready_for_native_assembly=False, installed_geometry_verified=False,
                manufacturing_release=False,
                engineering_accepted=False, physical_accepted=False)


def test_request_keeps_counted_child_and_missing_datums(route_request):
    request = route_request
    assert request['request_id'] == identity({k: v for k, v in request.items() if k != 'request_id'})
    assert (request['part_count'], request['piece_count']) == (74, 694)
    assert len(request['component_definitions']) == 74
    assert request['guide']['stock_cut_length_m'] == 2.9
    assert request['belt']['stock_cut_length_m'] == 5.8
    assert request['nominal_motion_control']['opening_plus_two_slides_m'] == pytest.approx(2.84)
    assert request['nominal_motion_control']['guide_stock_minus_nominal_span_m'] == pytest.approx(.06)
    assert request['guide']['installed_start_m'] is None
    assert request['belt']['closed_pitch_path_m'] is None
    assert request['ready_for_native_assembly'] is False
    assert route.assess_proposal(request, proposal(request))


def test_committed_request_matches_handoff(route_request):
    request = route_request
    assert route.OUTPUT.read_bytes() == route.encoded(request)


def test_well_formed_synthetic_route_still_requires_review(route_request):
    draft = proposal(route_request)
    draft['guide'] = dict(geometry='straight-full-guide', extent_m=2.9,
                          installed_start_m=[0, 0, 0], installed_end_m=[2.9, 0, 0])
    draft['belt'] = dict(geometry='closed-loop',
                         closed_pitch_path_m=[[0, 0, 0], [1.45, 0, 0],
                                              [1.45, 1.45, 0], [0, 1.45, 0], [0, 0, 0]])
    holds = route.assess_proposal(route_request, draft)
    assert 'independent motion, clearance, electrical and physical review' in holds
    assert all(draft[k] is False for k in ('installed_geometry_verified',
                                          'ready_for_native_assembly',
                                          'manufacturing_release', 'engineering_accepted',
                                          'physical_accepted'))


@pytest.mark.parametrize('fault', ['guide_proxy', 'straight_belt', 'belt_extent',
                                   'candidate', 'evaluation', 'claimed_acceptance',
                                   'claimed_native_ready',
                                   'open_belt_path', 'short_endpoints', 'request_seal'])
def test_false_route_or_authority_rejected(route_request, fault):
    request = route_request
    original = request
    draft = proposal(request)
    if fault == 'guide_proxy':
        draft['guide'] = dict(geometry='straight-full-guide', extent_m=2.0)
    elif fault == 'straight_belt':
        draft['belt'] = dict(geometry='straight', straight_extent_m=5.8)
    elif fault == 'belt_extent':
        draft['belt'] = dict(geometry='closed-loop', straight_extent_m=5.8)
    elif fault == 'candidate':
        draft['physical_candidate_id'] = '0' * 64
    elif fault == 'evaluation':
        draft['installed_evaluation_id'] = '0' * 64
    elif fault == 'claimed_acceptance':
        draft['installed_geometry_verified'] = True
    elif fault == 'claimed_native_ready':
        draft['ready_for_native_assembly'] = True
    elif fault == 'open_belt_path':
        draft['belt'] = dict(geometry='closed-loop',
                             closed_pitch_path_m=[[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
    elif fault == 'short_endpoints':
        draft['guide'] = dict(geometry='straight-full-guide', extent_m=2.9,
                              installed_start_m=[0, 0, 0], installed_end_m=[2, 0, 0])
    else:
        original = deepcopy(request)
        original['piece_count'] = 693
    with pytest.raises(ValueError):
        route.assess_proposal(original, draft)


def test_changed_handoff_bytes_rejected(route_request):
    raw = route.HANDOFF.read_bytes()
    with pytest.raises(ValueError, match='bytes differ'):
        route.compile_request(json.loads(raw), raw + b' ')


def test_forged_object_rejected_even_with_genuine_handoff_bytes():
    raw = route.HANDOFF.read_bytes()
    forged = deepcopy(json.loads(raw))
    forged['parts'][0]['component_definition_id'] = 'f' * 64
    forged['handoff_id'] = identity({k: v for k, v in forged.items() if k != 'handoff_id'})
    with pytest.raises(ValueError, match='differs from pinned bytes'):
        route.compile_request(forged, raw)


def test_resealed_short_guide_request_rejected(route_request):
    forged = deepcopy(route_request)
    forged['guide']['stock_cut_length_m'] = 2.0
    forged['request_id'] = identity({k: v for k, v in forged.items() if k != 'request_id'})
    draft = proposal(forged)
    draft['guide'] = dict(geometry='straight-full-guide', extent_m=2.0,
                          installed_start_m=[0, 0, 0], installed_end_m=[2, 0, 0])
    with pytest.raises(ValueError, match='pinned child handoff'):
        route.assess_proposal(forged, draft)

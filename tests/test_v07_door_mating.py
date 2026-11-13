"""One opening remains held until counted parts acquire controlled datums."""
import json

import pytest

from engineering.station_rail.common import identity
from engineering.vehicle_parts import door_mating as mating
from tools.automation import v07_door_route as route


@pytest.fixture(scope='module')
def route_request():
    raw=route.HANDOFF.read_bytes()
    return route.compile_request(json.loads(raw),raw)


def draft(route_request):
    return dict(schema='osr-v07-one-opening-route-proposal/1',
        request_id=route_request['request_id'],physical_candidate_id=route_request['physical_candidate_id'],
        installed_candidate_id=route_request['installed_candidate_id'],
        installed_evaluation_id=route_request['installed_evaluation_id'],opening=route_request['opening'],
        guide={},belt={},ready_for_native_assembly=False,installed_geometry_verified=False,
        manufacturing_release=False,engineering_accepted=False,physical_accepted=False)


def axes():
    return [dict(part_id=name,origin_car_m=[x,.05,0.],axis_unit_car=[0.,0.,1.],
                 pitch_radius_m=.03) for name,x in
            (('body/door-drive-pulley',.05),('body/door-idler-pulley',2.75))]


def test_current_child_is_counted_source_bound_and_unlocated():
    result=mating.evaluate()
    assert result['assessment_id']==identity({k:v for k,v in result.items() if k!='assessment_id'})
    assert result['physical_candidate_id']==route.PHYSICAL_CHILD
    assert result['installed_candidate_id']==route.INSTALLED_CHILD
    assert len(result['all_parts_per_opening'])==74 and result['pieces_per_opening']==694
    assert result['checked_hardware_per_opening']['body/door-carriage-roller']==8
    assert result['checked_hardware_per_opening']['body/door-pulley-bearing']==2
    assert result['checked_hardware_per_opening']['body/door-guide-bolt']==24
    assert result['checked_hardware_per_opening']['services/door-trailing-loom']==2
    assert result['motor_cooling_hardware_count'] is None
    assert result['stock']['guide_cut_length_m']==2.9
    assert result['stock']['belt_cut_length_m']==5.8
    assert result['nominal_control']['opening_plus_slides_m']==pytest.approx(2.84)
    assert result['nominal_control']['guide_stock_minus_nominal_span_m']==pytest.approx(.06)
    assert result['frames']['header']['transform_from_parent'] is None
    assert result['accepted_header_to_body_transform'] is None
    assert result['ready_for_native_assembly'] is False
    assert result['manufacturing_release'] is False


def test_proposed_loop_and_full_guide_are_only_screened(route_request):
    value=draft(route_request)
    value['guide']=dict(geometry='straight-full-guide',extent_m=2.9,
                        installed_start_m=[0.,0.,0.],installed_end_m=[2.9,0.,0.])
    value['belt']=dict(geometry='closed-loop',
        closed_pitch_path_m=[[0.,0.,0.],[2.8,0.,0.],[2.8,.1,0.],[0.,.1,0.],[0.,0.,0.]],
        pulley_axis_datums=axes())
    result=mating.evaluate(proposal=value)
    assert result['proposed_guide']['straight_extent_m']==pytest.approx(2.9)
    assert result['proposed_belt_pitch_polyline_m']==pytest.approx(5.8)
    assert result['belt_stock_minus_polyline_m']==pytest.approx(0.)
    assert result['proposed_pulley_axes']==value['belt']['pulley_axis_datums']
    assert result['stock']['belt_pitch_length_m'] is None
    assert result['new_physical_child_required_before_adopting_proposal'] is True
    assert result['proposed_geometry_installed_in_child'] is False
    assert result['route_intake_holds'] and result['ready_for_native_assembly'] is False


@pytest.mark.parametrize('fault,error',[
    ('sideways-guide','longitudinal x'),
    ('nonparallel-axes','parallel'),
    ('off-plane-belt','pitch plane'),
    ('off-route-pulley','inside'),
    ('oversized-pulley','stock envelope'),
    ('degenerate-belt','degenerate segment'),
])
def test_proposed_geometry_errors_fail_before_native_work(route_request,fault,error):
    value=draft(route_request)
    value['guide']=dict(geometry='straight-full-guide',extent_m=2.9,
                        installed_start_m=[0.,0.,0.],installed_end_m=[2.9,0.,0.])
    value['belt']=dict(geometry='closed-loop',
        closed_pitch_path_m=[[0.,0.,0.],[2.8,0.,0.],[2.8,.1,0.],[0.,.1,0.],[0.,0.,0.]],
        pulley_axis_datums=axes())
    if fault=='sideways-guide':value['guide']['installed_end_m']=[0.,2.9,0.]
    if fault=='nonparallel-axes':value['belt']['pulley_axis_datums'][1]['axis_unit_car']=[1.,0.,0.]
    if fault=='off-plane-belt':value['belt']['closed_pitch_path_m'][2][2]=.01
    if fault=='off-route-pulley':value['belt']['pulley_axis_datums'][1]['origin_car_m']=[3.75,.05,0.]
    if fault=='oversized-pulley':value['belt']['pulley_axis_datums'][0]['pitch_radius_m']=.04
    if fault=='degenerate-belt':value['belt']['closed_pitch_path_m'][1]=[0.,0.,0.]
    with pytest.raises(ValueError,match=error):mating.evaluate(proposal=value)


def test_mixed_child_proposal_rejected(route_request):
    value=draft(route_request);value['physical_candidate_id']='0'*64
    with pytest.raises(ValueError,match='physical_candidate_id differs'):
        mating.evaluate(proposal=value)


def test_stale_upstream_source_is_held(monkeypatch):
    actual=mating.digest
    def changed(path):
        if str(path).endswith('engineering/vehicle_parts/policy.json'):
            return '0'*64
        return actual(path)
    monkeypatch.setattr(mating,'digest',changed)
    with pytest.raises(ValueError,match='child source changed'):
        mating.evaluate()

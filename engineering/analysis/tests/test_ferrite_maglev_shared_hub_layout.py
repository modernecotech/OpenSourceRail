"""Independent curve, stop, door, obstruction and publication controls."""
from copy import deepcopy
import gzip
from hashlib import sha256
import json
import math
import shutil

import pytest

from engineering.ferrite_maglev import shared_hub_layout as hub


def test_bernstein_bound_controls_known_parabola_and_rejects_smaller_radius():
    points=[[0.,0.],[.5,0.],[1.,1.]] # x=t, y=t²: max curvature2 at t=0.
    assert hub.curvature(points,0.)==2.
    assert hub.curvature(points,1.)==pytest.approx(2/5**1.5)
    assert hub.curvature_bound(points)>=max(hub.curvature(points,i/100) for i in range(101))
    assert hub.certify_curvature(points,.5)['passed']
    assert not hub.certify_curvature(points,.6)['passed']


def test_straight_curve_length_and_split_recover_independent_control():
    points=[[x,0.] for x in [0.,15.,30.,70.,85.,100.]]
    length,error=hub.curve_length(points);assert length==pytest.approx(100.) and error<1e-8
    first,last=hub.split(points)
    for t in [0.,.1,.5,.9,1.]:
        assert hub.bezier(first,t)==pytest.approx(hub.bezier(points,t/2))
        assert hub.bezier(last,t)==pytest.approx(hub.bezier(points,.5+t/2))
    assert hub.certify_curvature(points,10000.)['passed']


def test_quintic_transition_has_matching_tangents_and_zero_endpoint_curvature():
    result=hub.transition([-2000.,0.],[-200.,100.],[1.,0.],[1.,0.],250.,hub.load())
    assert result['passed'];value=result['selected'];points=value['control_points_xy_m']
    assert points[0]==[-2000.,0.] and points[-1]==[-200.,100.]
    for t in [0.,1.]:
        tangent=hub.unit(hub.bezier(hub.derivative(points),t));assert tangent==pytest.approx([1.,0.])
        assert hub.curvature(points,t)<1e-12
    assert value['length_m']>=math.dist(points[0],points[-1])
    assert value['curvature']['certified_minimum_radius_m']>=250.
    assert max(hub.curvature(points,i/1000) for i in range(1001))<=1/value['curvature']['certified_minimum_radius_m']+1e-10


def test_reversed_short_or_insufficient_radius_transitions_are_rejected():
    a=hub.load()
    assert not hub.transition([0.,0.],[20.,0.],[1.,0.],[1.,0.],250.,a)['passed']
    assert not hub.transition([0.,0.],[1000.,0.],[-1.,0.],[1.,0.],250.,a)['passed']
    assert not hub.transition([0.,0.],[100.,100.],[1.,0.],[0.,1.],10000.,a)['passed']


def line(identity='test',heading=(1.,0.),level=8.):
    return dict(line=identity,heading_xy=list(heading),station_centre_xy_m=[0.,0.],beam_top_level_m=level,
        platform_floor_level_m=level+.35,station_tangent_bounds_m=[-200.,200.],station_tangent_length_m=400.)


def test_front_stop_uses_exact_six_bodies_gaps_and_twentyfour_doors():
    r=hub.body_and_doors(line(),18.,hub.load())
    assert r['formation_length_m']==104.5 and r['platform_bounds_along_m']==[-109.5,109.5]
    assert r['platform_length_m']==219. and len(r['body_intervals'])==12 and len(r['doors'])==24
    assert min(p['along_m'] for p in r['doors'])==-100.5 and max(p['along_m'] for p in r['doors'])==100.5
    assert {p['body_local_door_m'] for p in r['doors']}=={-4.5,4.5}
    forward=[p for p in r['body_intervals'] if p['direction']==1]
    assert min(p['body_extent_along_m'][0] for p in forward)==-104.5
    assert max(p['body_extent_along_m'][1] for p in forward)==0.
    lengths=sum(p['body_extent_along_m'][1]-p['body_extent_along_m'][0] for p in forward)
    assert lengths==102. and r['formation_length_m']-lengths==5*.5


def test_visibility_solver_routes_around_real_obstacle_and_rejects_blocked_floor():
    rectangle=[[-1.,-1.],[1.,1.]]
    path=hub.visibility_path([-5.,0.],[5.,0.],[rectangle],lambda p:all(abs(x)<=10 for x in p))
    assert path['length_m']==pytest.approx(2*math.sqrt(17)+2)
    assert all(hub.rect_segment_clear(p,q,rectangle) for p,q in zip(path['points_xy_m'],path['points_xy_m'][1:]))
    assert not hub.rect_segment_clear([-5.,0.],[5.,0.],rectangle)
    assert hub.visibility_path([-5.,0.],[5.,0.],[rectangle],lambda p:abs(p[0])<=10 and abs(p[1])<=.5) is None


def test_rotated_platform_void_overlap_recovers_full_partial_and_outside_areas():
    rect=[[-1.,-1.],[1.,1.]]
    assert hub.rectangle_platform_overlap_area(rect,[0.,0.],[1.,0.],10.,10.)==4.
    assert hub.rectangle_platform_overlap_area(rect,[1.,0.],[1.,0.],2.,10.)==2.
    assert hub.rectangle_platform_overlap_area(rect,[10.,0.],[1.,0.],2.,2.)==0.
    assert hub.rectangle_platform_overlap_area(rect,[0.,0.],hub.unit([1.,1.]),10.,10.)==pytest.approx(4.)


def test_all_exact_door_pairs_route_wide_platform_with_vertical_distance_separate():
    lines=[line('a'),line('b',(0.,1.),16.)];r=hub.circulation(lines,18.,hub.load(),door_details=True)
    assert r['all_boarding_door_pairs_routed'] and r['platform_bypass_screen_pass']
    p=r['platform_pair_walks'][0];assert p['required_door_pairs']==p['routed_door_pairs']==576
    assert len(p['door_pair_routes'])==576
    assert p['maximum_horizontal_walk_m']>190. and p['maximum_horizontal_walk_m']>p['minimum_horizontal_walk_m']
    assert p['lift_time_at_assumed_1m_s']==pytest.approx(8.)
    assert p['via_ground_hall_vertical_lift_travel_m']==pytest.approx(20.7)
    assert p['lift_queues_door_opening_and_service_wait_s'] is None
    assert all(row['vertical_lift_travel_m']==pytest.approx(8.) for row in p['door_pair_routes'])
    assert not r['common_lift_capacity_outage_fire_power_and_platform_interfaces_accepted']


def supported_horizontal_paths(plan):
    for flight in plan['flights']:
        for first,last in zip(flight['walking_path_xyz_m'],flight['walking_path_xyz_m'][1:]):
            if abs(first[2]-last[2])>1e-9:continue
            for fraction in (.125,.375,.625,.875):
                p=[x+(y-x)*fraction for x,y in zip(first,last)]
                supported=any(abs(p[2]-u['top_m'])<1e-8 and all(abs(p[j]-u['xy_m'][j])<=u['size_m'][j]/2+1e-8 for j in (0,1)) for u in plan['units'])
                if not supported:return False
    return True


def test_every_short_stair_flight_reaches_landing_and_next_flight_without_gap():
    access=hub.circulation([line('a'),line('b',(0.,1.),16.)],18.,hub.load());plan=access['stair_geometry']
    assert plan['all_flights_have_connected_landings'] and supported_horizontal_paths(plan)
    for first,last in zip(plan['flights'],plan['flights'][1:]):
        assert first['walking_path_xyz_m'][-1]==pytest.approx(last['walking_path_xyz_m'][0])
    for path in plan['flights']:
        landing=next(u for u in plan['units'] if u['id']==path['landing_id'])
        final_tread=next(u for u in plan['units'] if u['id']==path['tread_ids'][-1])
        assert abs(landing['top_m']-final_tread['top_m'])<=.1500001
        assert landing['size_m'][0]>=hub.load()['stair_landing_length_m']
    assert any(p['landing_extra_length_m']>.29 for p in plan['flights'])
    # Recreate the former fixed-length landing placement on one short flight.
    bad=deepcopy(plan);short=next(p for p in bad['flights'] if p['landing_extra_length_m']>.29);landing=next(u for u in bad['units'] if u['id']==short['landing_id'])
    sign=1 if short['flight']%2 else -1
    landing['size_m'][0]=2.4;landing['xy_m'][0]=sign*(bad['maximum_run_m']/2+1.2)
    assert not supported_horizontal_paths(bad)


def test_mesh_placement_is_derived_from_source_stock_instead_of_cad_bounds():
    stock=dict(size_m=[2.,1.,3.],xy_m=[10.,20.],bottom_m=5.,angle_deg=90.)
    vertices=[[x,y,z] for x in (9.5,10.5) for y in (19.,21.) for z in (5.,8.)]
    assert hub.verify_stock_placement(dict(vertices_m=vertices),stock)==pytest.approx([-1.,-.5,0.,1.,.5,3.])
    translated=dict(vertices_m=[[x+10.,y,z] for x,y,z in vertices])
    with pytest.raises(ValueError,match='source xy/angle/z'):hub.verify_stock_placement(translated,stock)


def test_compact_six_metre_island_is_not_credited_as_core_bypass():
    r=hub.circulation([line('a'),line('b',(0.,1.),16.)],6.,hub.load())
    assert not r['platform_bypass_screen_pass']
    assert not r['all_boarding_door_pairs_routed']


def test_terminal_source_condition_is_not_misrepresented_as_through_connection():
    a=hub.load();a['_variant_platform_width_m']=18.
    proposal=dict(line='terminal',local_chord_coordinates=[[0.,0.],[.01,0.],[0.,0.]],previous_retained_anchor_id='end',next_retained_anchor_id='end')
    result=hub.fit_line(proposal,[dict(heading=[1.,0.],projection_offset_m=0.)]*2,[.01,0.],[0.,0.],0.,250.,8.,a)
    assert not result['passed'] and 'coincident before/after anchors' in result['reason']


def test_projected_anchor_repairs_are_separate_and_preserve_source_controls():
    a=hub.load();concept=dict(id='source',pair_id='pair-test',line_proposals=[dict(line='a',local_chord_coordinates=[[.0001,0.],[.005,0.],[.01,0.]])])
    context={'a':[dict(coordinate=[.0001,0.],projected_coordinate=[0.,0.],projected_chainage_m=0.,heading=[1.,0.],projection_offset_m=11.1195),
        dict(coordinate=[.01,0.],projected_coordinate=[.01,0.],projected_chainage_m=1111.95,heading=[1.,0.],projection_offset_m=0.)]}
    original=deepcopy((concept,context));fixed,anchors=hub.projected_anchor_repair(concept,context,a)
    assert (concept,context)==original
    assert fixed['id']=='source/projected-anchors' and fixed['anchor_mode']=='projected-repair'
    assert fixed['line_proposals'][0]['local_chord_coordinates'][0]==[0.,0.]
    assert anchors['a'][0]['projection_offset_m']==0.
    provenance=fixed['anchor_repair_provenance'];assert provenance['rejected_original_retained']
    assert not provenance['projection_limit_relaxed'] and not provenance['old_civil_cost_reused']
    record=provenance['records'][0];assert record['original_coordinate']==[.0001,0.] and record['projected_coordinate']==[0.,0.]
    assert record['exact_retained_polyline_chainage_m']==0. and record['displacement_m']==pytest.approx(11.1195,abs=.001)
    assert record['source_control_exceeded_5m_limit'] and not record['connection_and_access_site_accepted']


def test_independent_closed_mesh_volume_and_missing_or_reversed_faces():
    p=dict(vertices_m=[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]],triangles=[[0,2,1],[0,1,3],[0,3,2],[1,2,3]])
    assert hub.mesh_volume(p)==pytest.approx(1/6)
    translated=deepcopy(p);translated['vertices_m']=[[x+100.,y-20.,z+5.] for x,y,z in p['vertices_m']]
    assert hub.mesh_volume(translated)==pytest.approx(1/6)
    missing=deepcopy(p);missing['triangles'].pop()
    with pytest.raises(ValueError,match='bounded closed|closed consistently'):hub.mesh_volume(missing)
    reversed_face=deepcopy(p);reversed_face['triangles'][0].reverse()
    with pytest.raises(ValueError,match='closed consistently'):hub.mesh_volume(reversed_face)


@pytest.mark.parametrize('key,value',[('minimum_station_tangent_m',349.),('hub_selected',True),('stop_coordinate_convention','consist-centre'),('vehicle_envelope_half_width_m',1.)])
def test_unbounded_or_inconsistent_policy_rejected(tmp_path,monkeypatch,key,value):
    import re
    text=hub.INPUT.read_text();text=re.sub(r'^'+key+r'\s*=.*$',key+' = '+json.dumps(value),text,flags=re.M)
    path=tmp_path/'invalid.toml';path.write_text(text);monkeypatch.setattr(hub,'INPUT',path)
    with pytest.raises(ValueError):hub.load()


@pytest.fixture(scope='module')
def packet(tmp_path_factory):
    folder=tmp_path_factory.mktemp('shared-hub');hub.publish(folder,native=False);return folder


def test_bounded_packet_retains_rejections_source_convention_and_all_accepted_flags_open(packet):
    hub.verify(packet);value=hub.study();assert value['source_concepts']==7 and value['variant_count']==528
    assert value['projected_anchor_repair_concepts']==4
    assert value['stop_convention']['required_common_straight_m']==400.
    assert value['stop_convention']['common_platform_length_m']==219.
    assert value['source_terminal_condition']['implies_entire_hub_impossible'] is False
    assert value['geometric_fit_count']>0 and value['representatives']
    assert not value['hub_selected'] and not value['city_geometry_or_price_replaced']
    assert all(value[key] is False for key in hub.FLAGS)
    assert all(not row['selected'] for row in value['alternatives'])
    assert any('coincident' in line['reason'] for row in value['alternatives'] for line in row['line_screens'])
    assert any('projection offset' in line['reason'] for row in value['alternatives'] for line in row['line_screens'])
    repaired=[r for r in value['alternatives'] if r['anchor_mode']=='projected-repair'];assert len(repaired)==192
    assert all(not r['anchor_repair_provenance']['projection_limit_relaxed'] and r['anchor_repair_provenance']['rejected_original_retained'] for r in repaired)
    for row in repaired:
        for record in row['anchor_repair_provenance']['records']:
            assert record['displacement_m']==pytest.approx(hub.hubs.op.distance(record['original_coordinate'],record['projected_coordinate']))
    for row in value['representatives']:
        assert row['geometric_research_screen_pass'] and row['circulation']['all_boarding_door_pairs_routed']
        for physical_line in row['lines']:
            assert physical_line['station_tangent_length_m']==400.
            assert physical_line['ordinary_beam_centres_m']==3.8
            assert physical_line['station_beam_centres_m']==pytest.approx(row['platform_island_width_m']+2.65+.15)
            for beam in physical_line['directional_beams']:
                assert beam['flared_transition_geometry_fitted']
                for side in ('incoming','outgoing'):
                    assert beam[side]['curvature']['passed'] and beam[side]['curvature']['certified_minimum_radius_m']>=row['minimum_directional_beam_radius_m']
        for pair in row['circulation']['platform_pair_walks']:
            assert pair['required_door_pairs']==pair['routed_door_pairs']==len(pair['door_pair_routes'])==576
        assert row['quantities']['complete_installed_cost_usd'] is None and row['quantities']['old_civil_price_or_foundation_credit_usd']==0.
        for physical_line in row['lines']:
            marks=sorted(p['s_m'] for p in row['portal_layout']['portals'] if p['line']==physical_line['line'])
            assert marks[0]==-200. and marks[-1]==200.
            assert max(q-p for p,q in zip(marks,marks[1:]))<=25.000001
        assert row['quantities']['platform_net_slab_concrete_m3']<row['quantities']['platform_concrete_m3']


def test_native_definition_counts_exact_station_bays_cutouts_and_distinct_envelopes(packet):
    value=hub.study();definition=hub.native_definition(value);assert definition is not None
    assert len({p['id'] for p in definition['parts']})==len(definition['parts'])
    beams=[p for p in definition['parts'] if p['kind']=='hollow-guidebeam'];row=value['representatives'][0]
    assert len(beams)==row['quantities']['station_guideway_bays']
    assert sum(p['size_m'][0] for p in beams)==pytest.approx(row['quantities']['station_straight_directional_beam_m'])
    assert max(p['size_m'][0] for p in beams)<=25.000001
    platforms=[p for p in definition['parts'] if p['id'].endswith('-platform')]
    assert len(platforms)==len(row['lines']) and all(p['cutout_rectangles_xy_m'] for p in platforms)
    assert sum(p['volume_m3'] for p in platforms)==pytest.approx(row['quantities']['platform_net_slab_concrete_m3'])
    assert len([p for p in definition['parts'] if p['role']=='clearance-envelope'])==2
    assert all(not p['production_released'] and p['volume_m3']>0 for p in definition['parts'])


def test_rehashed_geometry_or_result_tampering_is_rejected(packet,tmp_path):
    folder=tmp_path/'packet';shutil.copytree(packet,folder);value=json.loads(gzip.decompress((folder/'study.json.gz').read_bytes()))
    value['stop_convention']['common_platform_length_m']=104.5
    value.pop('content_sha256');value['content_sha256']=sha256(hub.encoded(value)).hexdigest()
    raw=hub.encoded(value);(folder/'study.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    manifest=json.loads((folder/'manifest.json').read_text());manifest.update(content_sha256=value['content_sha256'],raw_bytes=len(raw))
    manifest['files_sha256']['study.json.gz']=hub.digest(folder/'study.json.gz');(folder/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='recalculated content'):hub.verify(folder)


def test_packet_rejects_rehashed_false_presentation_and_unowned_files(packet,tmp_path):
    folder=tmp_path/'packet';shutil.copytree(packet,folder);(folder/'station-plan.svg').write_text('<svg>compact100m certified</svg>')
    manifest=json.loads((folder/'manifest.json').read_text());manifest['files_sha256']['station-plan.svg']=hub.digest(folder/'station-plan.svg')
    (folder/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='presentation differs'):hub.verify(folder)
    (folder/'unowned.txt').write_text('unowned')
    with pytest.raises(ValueError,match='inventory differs'):hub.verify(folder)


def test_rehashed_native_translation_cannot_change_source_placement(tmp_path):
    if not (hub.OUTPUT/'manifest.json').is_file() or not json.loads((hub.OUTPUT/'manifest.json').read_text()).get('native_present'):
        pytest.skip('current canonical reopened native packet required; generated by the publication qualification')
    hub.verify();folder=tmp_path/'native-packet';shutil.copytree(hub.OUTPUT,folder)
    mesh=json.loads(gzip.decompress((folder/'native-mesh.json.gz').read_bytes()))
    for part in mesh['parts']:
        for point in part['vertices_m']:point[0]+=10.
    (folder/'native-mesh.json.gz').write_bytes(gzip.compress(hub.encoded(mesh),mtime=0))
    receipt=json.loads((folder/'native-cad.json').read_text())
    for part in receipt['parts']:
        for index in (0,3):part['bounds_m'][index]+=10.
    receipt['files_sha256']['native-mesh.json.gz']=hub.digest(folder/'native-mesh.json.gz');(folder/'native-cad.json').write_text(json.dumps(receipt))
    visual=json.loads((folder/'native-visual.json').read_text());visual['mesh_sha256']=hub.digest(folder/'native-mesh.json.gz');(folder/'native-visual.json').write_text(json.dumps(visual))
    manifest=json.loads((folder/'manifest.json').read_text())
    for name in ('native-mesh.json.gz','native-cad.json','native-visual.json'):manifest['files_sha256'][name]=hub.digest(folder/name)
    (folder/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='source xy/angle/z'):hub.verify(folder)

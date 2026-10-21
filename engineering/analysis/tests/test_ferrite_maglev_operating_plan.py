"""Independent route interpolation, motion, terminal geometry and cost controls."""
from copy import deepcopy
import json
import math
from pathlib import Path
import tomllib

import pytest
from engineering.ferrite_maglev import operating_plan as op,cities,model,manufacturing,station


@pytest.fixture(scope='module')
def context():return model.load()


def fixture(context,*,length=3000.):
    c=context[1];capacity=dict(passenger_capacity=720,crush_capacity=960)
    f=cities.formation(c,capacity,[])
    line=dict(name='fixture',shape='radial',length_m=length,capacity=capacity,
        service=dict(schedule=[dict(headway_min=3.)]))
    stops=[dict(id=f's{i}',line='fixture',s_m=s,lon=44.+s/100000,lat=33.,platform_length_m=121.)
        for i,s in enumerate((0.,104.8,length))]
    feature=dict(properties=dict(name='fixture'),geometry=dict(type='LineString',
        coordinates=[[44.,33.],[44.015,33.],[44.015,33.015]]))
    return c,f,line,stops,[feature]


def test_intermediate_stations_follow_retained_bend_not_endpoint_chord(context):
    c,f,line,stops,features=fixture(context)
    before=json.dumps(stops,sort_keys=True);r=op.plan_line(c,f,line,stops,features)
    assert json.dumps(stops,sort_keys=True)==before
    assert r['operating_station_count']<math.ceil(r['measured_polyline_length_m']/1000)+1
    for stop in r['stations']:
        assert stop['lat']==pytest.approx(33.) or stop['lon']==pytest.approx(44.015)
        p,q=features[0]['geometry']['coordinates'][stop['source_segment_index']:stop['source_segment_index']+2]
        k=stop['source_segment_fraction']
        assert stop['lat']==pytest.approx(p[1]+k*(q[1]-p[1]))
        assert stop['lon']==pytest.approx(p[0]+k*(q[0]-p[0]))
    assert not r['route_site_approval']


def test_close_access_points_are_preserved_as_explicit_catchment_proposals(context):
    c,f,line,stops,features=fixture(context);r=op.plan_line(c,f,line,stops,features)
    assignments=r['retained_station_assignments']
    assert {a['retained_station_id'] for a in assignments}=={s['id'] for s in stops}
    assert {a['retained_station_id']:a['retained_station'] for a in assignments}=={s['id']:s for s in stops}
    assert any(a['along_route_access_offset_m']>1 for a in assignments)
    assert all(not a['catchment_connection_designed'] for a in assignments)
    assert r['flat_mainline_screen_pass']


def test_bounded_runtime_search_keeps_empty_normal_and_full_load_force_checks(context):
    c,f,*_=fixture(context);r=op.trip(c,f,1000.)
    assert r['study_pass']
    assert r['resource_headway_lower_bound_s']<=180
    assert {v['load'] for v in r['profiles']}=={'tare_kg','aw2_kg','aw3_kg'}
    assert r['clearance_front_distance_m']==254.5
    assert r['minimum_assumed_force_reserve_fraction']>=.15
    for row in r['profiles']:
        t=row['trajectory'];assert t['energy_balance']['passed']
        assert row['zone']['study_pass']
        assert t['inputs']['acceleration_m_s2']==r['acceleration_m_s2']
        assert row['tail_clearance_s']==pytest.approx(station._time_at_position(t,254.5))
    assert r['acceleration_m_s2']==1.
    assert all(r[key] is False for key in model.FLAGS)


def test_terminal_arcs_are_tangent_and_connect_opposite_parallel_beams():
    curve=op.terminal_geometry(dict(lon=44.,lat=33.),(1.,0.))
    points=curve['local_coordinates_m'];r=curve['radius_m'];theta=math.acos((r+3.8/2)/(2*r))
    assert curve['length_m']==pytest.approx(r*(math.pi+4*theta))
    assert points[0]==pytest.approx([0.,-1.9])
    assert points[-1]==pytest.approx([0.,1.9])
    assert min(p[0] for p in points)>-1e-8
    first=[points[1][i]-points[0][i] for i in (0,1)]
    last=[points[-1][i]-points[-2][i] for i in (0,1)]
    assert first[0]>0 and last[0]<0
    for left,right in zip(curve['arcs'],curve['arcs'][1:]):
        a=left['start_angle_rad']+left['turn_angle_rad'];b=right['start_angle_rad']
        left_point=[left['centre_m'][0]+r*math.cos(a),left['centre_m'][1]+r*math.sin(a)]
        right_point=[right['centre_m'][0]+r*math.cos(b),right['centre_m'][1]+r*math.sin(b)]
        assert left_point==pytest.approx(right_point)
        ta=a+(math.pi/2 if left['turn_angle_rad']>0 else -math.pi/2)
        tb=b+(math.pi/2 if right['turn_angle_rad']>0 else -math.pi/2)
        assert math.cos(ta-tb)==pytest.approx(1.)
    assert curve['lateral_screen_pass'] and not curve['curve_phase_and_guidance_validated']


def test_terminal_station_only_sections_and_energy_events_close(context):
    c,f,line,stops,features=fixture(context);plan=op.plan_line(c,f,line,stops,features)
    a=tomllib.loads(cities.ASSUMPTIONS.read_text())
    result=cities.operating_line_plan(c,a,f,line,line['service'],plan)
    assert result['terminal_numerical_motion_screen_pass']
    assert len(plan['terminal_loops'])==2
    for loop in plan['terminal_loops']:
        assert loop['sections']==3 and len(loop['service_zones'])==2
        motion=loop['motion'];assert motion['study_pass']
        assert motion['winding_start_m']==-100 and motion['winding_end_m']==50
        assert motion['clearance_front_distance_m']==229.5<loop['section_length_m']
        for profile in motion['profiles']:
            assert profile['trajectory']['inputs']['speed_limit_kmh']==25.
    events=result['duty']['arrival_events_per_circuit'];dwell=result['charging']['dwell_seconds']
    expected_mainline_events=2*(len(plan['stations'])-1)
    assert len(events)==expected_mainline_events+2*3
    assert result['duty']['cycle_distance_m']==pytest.approx(2*plan['measured_polyline_length_m']+sum(l['geometry']['length_m'] for l in plan['terminal_loops']))
    assert result['duty']['conservative_cycle_seconds']==pytest.approx(sum(e['moving_seconds']+dwell for e in events))
    assert result['duty']['hot_aw3_no_regen_cycle_kwh']==pytest.approx(sum(e['hot_no_regen_motion_kwh']+360*dwell/3600 for e in events))
    assert not result['retained_capacity_target_met']
    assert result['selected_peak_headway_seconds']>result['retained_peak_headway_seconds']
    assert result['selected_eligible_operating_design'] is None


def test_every_added_station_and_loop_unit_enters_costs_without_free_foundations(context):
    c,f,line,stops,features=fixture(context);plan=op.plan_line(c,f,line,stops,features)
    a=tomllib.loads(cities.ASSUMPTIONS.read_text());r=cities.operating_line_plan(c,a,f,line,line['service'],plan)
    programme=manufacturing.city_programme(c,context[2],[r],3.)
    base=next(row for row in programme['scenarios'] if row['scenario']=='base')
    terminal=base['terminal_civil_bill'];loop_length=sum(l['geometry']['length_m'] for l in plan['terminal_loops'])
    count=sum(math.ceil(l['geometry']['length_m']/25) for l in plan['terminal_loops'])
    assert terminal['beam_units']==count
    assert terminal['support_positions']==count+2
    box=c['civil']['narrow_box_screen']
    void=(box['outer_width_m']-2*box['web_thickness_m'])*(box['outer_depth_m']-2*box['flange_thickness_m'])
    area=box['outer_width_m']*box['outer_depth_m']-void
    assert terminal['concrete_m3']==pytest.approx((area+.12)*loop_length+2*.4*void*count)
    assert base['mainline_station_electrical_packages']==len(plan['stations'])
    assert base['terminal_service_electrical_packages']==4
    upgrade=240000.*(r['charging']['candidate_kw_per_car']/200.-1)
    assert base['terminal_service_electrical_allowance_usd']==pytest.approx(4*(2335000.+upgrade))
    assert programme['quantities']['station_charger_connections']==(2*len(plan['stations'])+4)*6
    assert base['priced_scope_subtotal_usd']==pytest.approx(base['repeat_fleet_allowance_usd']+
        base['ordinary_elevated_allowance_usd']+base['terminal_civil_allowance_usd']+base['station_electrical_allowance_usd']+base['conditional_foundation_increment_usd']+base['booster_electrical_allowance_usd']+base['booster_mount_allowance_usd']+base['rescue_kit_allowance_usd'])
    foundation=programme['conditional_foundation_proposal']
    expected=(40*3+terminal['support_positions'])*foundation['incremental_support_allowance_usd']
    assert base['conditional_foundation_increment_usd']==pytest.approx(expected)
    assert base['complete_city_programme_usd'] is None


def test_too_short_line_remains_held_instead_of_overlapping_power_zones(context):
    c,f,line,stops,features=fixture(context,length=150.)
    features[0]['geometry']['coordinates']=[[44.,33.],[44.001,33.]]
    r=op.plan_line(c,f,line,stops,features)
    assert not r['flat_mainline_screen_pass']
    assert any('too short' in t['reason'] for t in r['trips'] if not t['study_pass'])


def test_baghdad_sparse_transfers_preserve_source_records_and_expose_conflicts(context):
    root=model.ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
    before=(root/'city.json').read_bytes();design=json.loads(before)
    features=json.loads((root/'baghdad.corridor.geojson').read_text())['features']
    a=tomllib.loads(cities.ASSUMPTIONS.read_text());count=0;lines=[];conflicts=[];benchmark=0
    for line in design['lines']:
        f=cities.formation(context[1],line['capacity'],[])
        retained=[s for s in design['stations'] if s['line']==line['name']]
        plan=op.plan_line(context[1],f,line,retained,features,interchanges=design['interchanges'])
        result=cities.operating_line_plan(context[1],a,f,line,line['service'],plan)
        assert plan['terminal_longitudinal_screen_pass'],line['name']
        assert result['selected_eligible_operating_design'] is None
        assert result['system_design_holds']
        assert {row['retained_station_id'] for row in plan['retained_station_assignments']}=={row['id'] for row in retained}
        assert plan['straight_alignment_alternative']['selected'] is False
        assert plan['straight_alignment_alternative']['existing_civil_classification_reused'] is False
        assert all(not t.get('selected_eligible_alternative') for t in plan['trips'])
        assert not any(t.get('research_comparison_candidate',{}).get('battery_kwh_per_car',30)!=30 for t in plan['trips'])
        conflicts.extend(plan['spacing_conflicts']);count+=len(plan['stations']);benchmark+=plan['retained_dense_benchmark']['passenger_stops'];lines.append(result)
    assert count==273 and benchmark==599
    assert len(conflicts)==10 and all(c['distance_m']>=350 for c in conflicts)
    assert not any(l['kinematic_holds'] for l in lines)
    urban_topups=[z for l in lines for z in l['operating_plan']['powered_top_up_zones']]
    assert len(urban_topups)==2 and all(z['length_m_per_direction']==275 for z in urban_topups)
    connectors=[v for l in lines for v in l['operating_plan']['terminal_transfer_access_proposals']]
    assert len(connectors)==1 and connectors[0]['retained_route_separation_m']==pytest.approx(49.4679668)
    assert any(not l['retained_capacity_target_met'] for l in lines)
    assert all(l['formation']['cars']==6 for l in lines)
    assert (root/'city.json').read_bytes()==before

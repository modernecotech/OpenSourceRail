"""Sparse fixed-line passenger transfers, powered zones and independent quantities."""
from copy import deepcopy
import math
import pytest
from engineering.ferrite_maglev import operating_plan as op,model,cities,manufacturing


def fixture(length=8000.):
    lon=math.degrees(length/op.EARTH_M)
    path=dict(points=[[0.,0.],[lon,0.]],cumulative_m=[0.,length],length_m=length,retained_length_m=length)
    line=dict(name='x',shape='radial',length_m=length,capacity=dict(passenger_capacity=720,crush_capacity=960),service=dict(schedule=[dict(headway_min=3)]))
    stops=[dict(id=f's{i}',line='x',s_m=i*200.,lon=math.degrees(i*200/op.EARTH_M),lat=0.,platform_length_m=121.) for i in range(int(length/200)+1)]
    return path,line,stops


def hub(identity,s):
    return dict(id=identity,lon=math.degrees(s/op.EARTH_M),lat=0.,lines=['x','y'],platforms=[])


def test_dense_access_records_do_not_force_dense_operating_stops():
    path,line,stops=fixture();before=deepcopy(stops)
    layout=op.passenger_layout(path,line,stops)
    assert [s['s_m'] for s in layout['stations']]==[0.,2000.,4000.,6000.,8000.]
    assert not layout['spacing_conflicts']
    assert len(layout['retained_station_assignments'])==len(stops)
    assert stops==before
    assert layout['physical_switches_proposed']==0


def test_fixed_transfer_crossings_are_retained_and_short_gap_is_not_hidden():
    path,line,stops=fixture();crossings=[hub('j1',2000),hub('j2',2800)]
    layout=op.passenger_layout(path,line,stops,crossings)
    ids={s['id'] for s in layout['stations'] if s['mandatory_junction_ids']}
    assert len(ids)==2
    assert {h['id'] for h in layout['transfer_hubs']}=={'j1','j2'}
    for h in layout['transfer_hubs']:
        source=next(j for j in crossings if j['id']==h['id'])
        assert h['exact_crossing_coordinate']==[source['lon'],source['lat']]
        assert not h['train_routing'] and not h['access_qualified']
    assert len(layout['spacing_conflicts'])==1
    conflict=layout['spacing_conflicts'][0]
    assert conflict['distance_m']==pytest.approx(800)
    assert conflict['minimum_m']==1500
    assert conflict['alternatives'][0]['actual_accessible_path_m'] is None
    assert conflict['alternatives'][0]['capex_usd'] is None


def test_suburban_spacing_is_an_explicit_scenario_not_population_inference():
    path,line,stops=fixture(10000.)
    layout=op.passenger_layout(path,line,stops,service_class='suburban')
    assert [s['s_m'] for s in layout['stations']]==[0.,5000.,10000.]
    assert layout['classification']=='explicit suburban scenario'
    assert op.load()['default_service_class']=='urban'


def test_compact_terminal_transfer_keeps_loop_datum_and_original_crossing():
    path,line,stops=fixture();crossing=hub('near-terminal',7950.)
    layout=op.passenger_layout(path,line,stops,[crossing])
    assert layout['stations'][-1]['s_m']==8000.
    assert len(layout['stations'])==5 and not layout['spacing_conflicts']
    assert layout['stations'][-1]['mandatory_junction_ids']==['near-terminal']
    source=layout['transfer_hubs'][0]
    assert source['s_m']==pytest.approx(7950.) and source['exact_crossing_coordinate']==[crossing['lon'],crossing['lat']]
    connector=layout['terminal_transfer_access_proposals'][0]
    assert connector['retained_route_separation_m']==pytest.approx(50.)
    assert not connector['terminal_loop_datum_changed'] and not connector['train_routing']
    assert connector['capex_usd'] is None and connector['accessible_path_length_m'] is None
    assert len(layout['retained_station_assignments'])==len(stops)


def test_midpoint_topup_resolves_urban_coast_reach_without_reclassifying_land_use():
    _,c,_=model.load();f=cities.formation(c,dict(passenger_capacity=720,crush_capacity=960),[])
    trip=op.wide_trip(c,f,2786.398733)
    assert trip['service_class']=='urban' and not trip['land_use_classification_inferred_from_propulsion']
    assert trip['kinematic_screen_pass'] and trip['rating_screen_pass']
    assert trip['propulsion_topology']=='one-located-midpoint-top-up'
    assert not trip['topology_comparisons'][0]['all_load_motion_rating_pass']
    assert trip['topology_comparisons'][1]['all_load_motion_rating_pass']
    booster=next(z for z in trip['installed_zones'] if z['kind']=='top-up')
    assert booster['length_m']==275. and not booster['passenger']
    assert all(p['corridor']['motion_screen_pass'] and p['corridor']['rating_screen_pass'] for p in trip['profiles'])
    assert trip['selected_eligible_alternative'] is None and not trip['study_pass']


def test_suburban_reserve_hold_is_not_removed_by_larger_pack_comparison():
    _,c,k=model.load();f=cities.formation(c,dict(passenger_capacity=720,crush_capacity=960),[])
    trip=op.wide_trip(c,f,5000.,service_class='suburban')
    assert trip['selected_eligible_alternative'] is None
    assert trip['research_comparison_candidate']['battery_kwh_per_car']==30.
    assert not trip['research_comparison_candidate']['service_energy_screen_pass']
    assert any(a['battery_kwh_per_car']>30 and a['service_energy_screen_pass'] for a in trip['alternatives'])
    assert all(not a['eligible'] for a in trip['alternatives'])
    assert {r['option'] for r in trip['equivalent_motor_alternatives']}=={'higher-voltage','lower-force-constant'}
    assert not trip['motor_price_comparison_proved']
    assert any(not z['passenger'] for z in trip['installed_zones'])


def test_topup_and_independent_rescue_quantities_reach_the_bill():
    _,c,k=model.load();path,line,stops=fixture(5000.);features=[dict(properties=dict(name='x'),geometry=dict(type='LineString',coordinates=path['points']))]
    f=cities.formation(c,line['capacity'],[]);plan=op.plan_line(c,f,line,stops,features,service_class='suburban')
    assert len(plan['powered_top_up_zones'])==1
    assert plan['powered_top_up_zones'][0]['services_charger'] is False
    assert plan['powered_top_up_zones'][0]['mechanical_takeoff']['mount_bolts']>0
    assert len(plan['rescue_nodes'])==6 and plan['rescue_kit_count']==12
    assert not any(n['station_booster_colocation_credit'] for n in plan['rescue_nodes'])
    a=cities.tomllib.loads(cities.ASSUMPTIONS.read_text());compiled=cities.operating_line_plan(c,a,f,line,line['service'],plan)
    programme=manufacturing.city_programme(c,k,[compiled],5.)
    base=next(r for r in programme['scenarios'] if r['scenario']=='base')
    for key in ('booster_electrical_allowance_usd','booster_mount_allowance_usd','rescue_kit_allowance_usd'):assert base[key]>0
    assert base['rescue_kit_allowance_usd']==pytest.approx(12*plan['rescue_kit_reference']['listed_kit_target_usd'])
    keys=('repeat_fleet_allowance_usd','ordinary_elevated_allowance_usd','terminal_civil_allowance_usd','station_electrical_allowance_usd','conditional_foundation_increment_usd','booster_electrical_allowance_usd','booster_mount_allowance_usd','rescue_kit_allowance_usd')
    assert base['priced_scope_subtotal_usd']==pytest.approx(sum(base[key] for key in keys))
    assert programme['configured_motor_voltage_current_rating_premium_usd'] is None
    assert base['complete_city_programme_usd'] is None

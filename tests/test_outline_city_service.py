from copy import deepcopy
from math import ceil,fsum

import pytest

from engineering.development_baseline import selection
from engineering.design_search import line_benchmark as budget
from engineering.design_search import line_benchmark_service as helper
from engineering.outline import city_inputs,city_service
from engineering.station_rail.common import identity


@pytest.fixture(scope='module')
def inputs():
    context=city_inputs.prepare();city=city_inputs.load('samawah',context=context)
    return city,budget.specification(),selection.load()['vehicle'],context


def synthetic(city,distances,ring=False):
    c=deepcopy(city);line=deepcopy(c['lines'][0]);line['shape']='ring' if ring else 'radial'
    line['route_m']=line['operational_route_m']=sum(distances)
    line.pop('coordinates',None);line.pop('coordinate_chainages_m',None)
    n=len(distances) if ring else len(distances)+1
    line['stops']=[dict(id='stop-'+str(i),chainage_m=sum(distances[:i]),dwell_s=35,lon=0,lat=0) for i in range(n)]
    line['legs']=[dict(from_stop='stop-'+str(i),to_stop='stop-'+str((i+1)%n),distance_m=d,closing_leg=ring and i==len(distances)-1) for i,d in enumerate(distances)]
    c['lines']=[line];c['test_hypothesis']='Synthetic independently declared evaluator fixture'
    c['input_id']=identity({k:v for k,v in c.items() if k!='input_id'})
    return c


def run(inputs,distances,ring=False,requirements=None):
    city,spec,vehicle,_=inputs
    return city_service.evaluate(synthetic(city,distances,ring),requirements or {},spec['design'],vehicle)


def test_catalogue_has_all_cities_and_no_surveyed_demand_is_inherited(inputs):
    city,_,_,context=inputs
    assert len(context['rows'])==266
    assert city['od']==[] and city['input_id']==identity({k:v for k,v in city.items() if k!='input_id'})
    assert all(not x['retained_service_and_capacity_are_current_demand'] for x in city['lines'])
    assert city_inputs.load(context['by_slug']['samawah'],context=context)==city
    assert all(city[k] is False for k in city_inputs.FLAGS)
    for line in city['lines']:
        assert len(line['coordinates'])==len(line['coordinate_chainages_m'])
        assert line['coordinate_chainages_m'][-1]==pytest.approx(line['route_m'])


def test_actual_ring_closing_distance_is_included(inputs):
    context=inputs[3];city=city_inputs.load('agra',context=context)
    ring=next(x for x in city['lines'] if x['shape']=='ring')
    assert len(ring['legs'])==len(ring['stops'])
    assert ring['legs'][-1]['closing_leg']
    assert fsum(x['distance_m'] for x in ring['legs'])==pytest.approx(ring['route_m'])


def test_unequal_legs_are_evaluated_separately_and_demand_derives_headway(inputs):
    result=run(inputs,[600,2000]);line=result['line_services'][0];service=line['service']
    assert [x['distance_m'] for x in line['legs']]==[600,2000]
    assert service['requirements']['headway_s']==200
    assert service['planning_usable_capacity_pphpd']==pytest.approx(276*18*.85*.99)
    assert service['one_way_s']==pytest.approx(fsum(x['scheduled_runtime_s'] for x in line['legs'])+service['stop_dwell_s'][1])
    assert line['propulsion_hypothesis']['kind']=='station-launch-reference'
    assert result['assumptions']['survey_demand_available'] is False
    assert service['actual_available_force_map'] is None
    assert all(x['braking_necessary_distance_fits_after_launch'] for x in line['legs'])
    assert line['requirements']['operating_days_per_year']==365
    assert line['requirements']['design_life_years']==30
    assert line['requirements']['real_discount_rate']==.04
    assert 'alignment_id' in line['requirements']


def test_short_leg_uses_exact_smaller_scurve_and_retains_platform_hold(inputs):
    spec=inputs[1];v=inputs[2];rotor=city_service.braking.rotating_stock(v)['equivalent_inertial_mass_kg_per_car']
    leg=city_service._leg(39.95021266757067,v['mass']['accounted_cap_loaded_kg_per_car']+250,rotor,spec['design'])
    assert leg['adaptive_speed_cap_m_s']<20
    assert leg['launch_distance_m']+leg['braking_distance_m']+leg['coast_distance_m']==pytest.approx(leg['distance_m'],abs=1e-7)
    assert leg['jerk_bound']['distance_m']==leg['launch_distance_m']
    assert leg['braking_necessary_distance_fits_after_launch'] is True
    line=run(inputs,[39.95021266757067,2000])['line_services'][0]
    assert line['station_repair']['applied'] and not line['physical_accepted']
    assert line['station_repair']['original_stop_count']==3
    assert len(line['operational_stops'])==line['requirements']['stations']==2
    assert line['station_repair']['additional_access_walkway_m']==pytest.approx(39.95021266757067)
    assert line['station_repair']['additional_shared_platform_length_m']==pytest.approx(2*39.95021266757067)
    assert line['station_repair']['original_marker_spacing_failures']


def test_ring_complex_repair_wraps_without_losing_original_access_markers(inputs):
    line=run(inputs,[1000,2000,40],True)['line_services'][0]
    repair=line['station_repair']
    assert repair['original_stop_count']==3 and repair['operational_stop_count']==2
    assert len(line['legs'])==2
    assert fsum(x['distance_m'] for x in line['legs'])==pytest.approx(3040)
    assert sum(len(x['original_stop_ids']) for x in repair['complexes'])==3
    assert all(x['distance_m']>=120 for x in line['legs'])


def test_single_overlapping_complex_does_not_claim_a_working_rail_line(inputs):
    with pytest.raises(ValueError,match='one overlapping complex'):run(inputs,[39])


def test_explicit_line_geometry_speed_cap_is_respected(inputs):
    city,spec,vehicle,_=inputs;c=synthetic(city,[2000,2000],True)
    c['lines'][0].update(design_speed_cap_m_s=8.,curve_speed_basis='Declared rounded-corner research bound')
    c['input_id']=identity({k:v for k,v in c.items() if k!='input_id'})
    line=city_service.evaluate(c,{},spec['design'],vehicle)['line_services'][0]
    assert line['design']['speed_m_s']==8
    assert all(x['adaptive_speed_cap_m_s']<=8 for x in line['legs'])
    assert line['line_geometry_hypothesis']['curve_speed_basis']=='Declared rounded-corner research bound'


def test_long_coast_failure_generates_new_mass_energy_and_feed_hypothesis(inputs):
    result=run(inputs,[7003.100240351595]);line=result['line_services'][0];service=line['service'];h=line['propulsion_hypothesis']
    assert line['known_reference_failures'][0]['reference_profile']['reason']=='coast_stops_before_receiving_zone'
    assert h['kind']=='powered-axle-continuous-research' and h['added_traction_mass_kg_per_car']==1000
    assert h['continuous_feed_route_m']==pytest.approx(7003.100240351595)
    assert h['traction_motors_per_car']==4 and h['traction_rated_kw_per_car']>0
    assert line['legs'][0]['powered_cruise_distance_m']>0
    assert service['provisional_normal_mass_kg_per_car']==pytest.approx(inputs[2]['mass']['accounted_cap_loaded_kg_per_car']+250+1000)
    assert service['mechanical_work_kwh_per_departure']>0 and service['actual_available_force_map'] is None
    assert h['research_configuration_id']==identity({k:v for k,v in h.items() if k!='research_configuration_id'})


def test_ring_fleet_counts_both_directions_without_terminal_turnback(inputs):
    result=run(inputs,[1800,2000,1900],True);line=result['line_services'][0];s=line['service']
    cycle=fsum(x['scheduled_runtime_s'] for x in line['legs'])+fsum(s['stop_dwell_s'])
    assert s['round_trip_s']==pytest.approx(cycle)
    assert s['active_trainsets']==2*ceil(cycle/200)
    assert s['spare_trainsets']==ceil(s['active_trainsets']*.15)
    assert s['departure_sites']==6 and s['boarding_edges']==6
    assert line['design']['terminal_turnback_s']==0
    assert s['auxiliary']['energy_balance_screen']=='pass'
    assert s['train_km_per_day']==pytest.approx(2*3600/200*18*5.7)


def test_radial_fleet_independently_includes_two_terminal_resources(inputs):
    result=run(inputs,[1500,1800,2000]);line=result['line_services'][0];s=line['service']
    assert s['round_trip_s']==pytest.approx(2*(s['one_way_s']+line['design']['terminal_turnback_s']))
    assert s['active_trainsets']==ceil(s['round_trip_s']/200)
    assert s['auxiliary']['energy_balance_screen']=='pass'
    assert s['departure_sites']==6 and s['boarding_edges']==8
    assert s['departures_per_day']==pytest.approx(2*18*18*3)


def test_extended_operations_uses_three_shifts_without_changing_factory_shifts(inputs):
    s=run(inputs,[2000],requirements={'operating_hours_per_day':24})['line_services'][0]['service']
    assert s['shift_info']['operations_shifts_per_day']==3
    assert s['shift_info']['operations_hours_per_shift']==8
    assert s['shift_info']['production_shifts_per_day']==s['shift_info']['construction_shifts_per_day']==2


def test_reporting_schedule_fraction_is_not_auxiliary_kwh_surplus(inputs):
    _,spec,vehicle,_=inputs
    r=helper.evaluate(spec['requirements'],spec['design'],vehicle)
    assert r['schedule_running_time_margin_fraction']==.05
    assert r['auxiliary']['energy_margin_kwh_per_car_per_half_cycle']!=.05
    assert r['scheduled_segment_runtime_s']==pytest.approx(r['unpadded_segment_runtime_s']*1.05)


def test_wrong_candidate_or_bad_numeric_inputs_do_not_silently_complete(inputs):
    city,spec,vehicle,_=inputs
    c=deepcopy(city);c['city']['slug']='tampered'
    with pytest.raises(ValueError,match='identity'):city_service.evaluate(c,{},spec['design'],vehicle)
    with pytest.raises(ValueError,match='Finite'):city_service.evaluate(city,{'peak_demand_pphpd':float('nan')},spec['design'],vehicle)

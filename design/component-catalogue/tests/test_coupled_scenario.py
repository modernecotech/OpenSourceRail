import pytest
from osr_mech.coupled_scenario import allocate_od,line_opening,OPENING_PACKAGES,operating_cost
from osr_mech.station.circulation import continuous_path
from osr_mech.station_capacity import footprint_screen,station_capacity_screen,passenger_pulses
from osr_mech.vehicle_mass_properties import mass_properties
from osr_mech.workload_staffing import workload_staffing,recruitment_backplan
from osr_mech.depot_dispatch import yard_dispatch
from osr_mech.pack_thermal import thermal_step,thermal_duty
from osr_mech.service_trace import encode_sections,decode_sections


def event(journey,train,line,a,b,depart,arrive):
    return dict(journey=journey,train=train,line=line,heading='forward',from_station=a,to_station=b,
        depart_minute=depart,arrival_minute=arrive,distance_m=1000)


def leg(line,a,b,walk=0):
    return dict(line=line,heading='forward',from_station=a,to_station=b,transfer_walk_minutes=walk)


def test_shared_section_capacity_limits_od_cohorts_and_transfers_charge_once():
    events=[event('one','t1','L1','a','b',5,10),event('one','t1','L1','b','c',11,16),
        event('two','t2','L2','x','y',15,20)]
    requests=[dict(id='first',arrival_minute=0,passengers=8,fare_iqd=100,legs=[leg('L1','a','b'),leg('L2','x','y',4)]),
        dict(id='second',arrival_minute=0,passengers=6,fare_iqd=100,legs=[leg('L1','a','c')])]
    result=allocate_od(events,requests,{'t1':10,'t2':10},[('b','x')])
    assert result['totals']['completed_paid_journeys']==10
    assert result['totals']['train_boardings']==18
    assert result['totals']['recognised_fare_iqd']==1000
    assert result['cohorts'][1]['unserved_passengers']==4
    assert result['actual_collected_receipts_iqd'] is None
    requests[0]['legs'][1]['transfer_walk_minutes']=6
    assert allocate_od(events,requests,{'t1':10,'t2':10},[('b','x')])['cohorts'][0]['completed_paid_journeys']==0


def test_dictionary_encoded_section_events_are_lossless_and_reproducible():
    events=[event('one','train','line','a','b',0,1),event('one','train','line','b','c',2,3)]
    raw=encode_sections(events)
    assert encode_sections(events)==raw and decode_sections(raw)==events


def test_a_partial_train_journey_can_deliver_a_short_od_but_not_an_unserved_destination():
    events=[event('partial','t1','line','a','b',5,10)]
    r=dict(id='short',arrival_minute=0,passengers=5,fare_iqd=100,legs=[leg('line','a','b')])
    assert allocate_od(events,[r],{'t1':10})['totals']['completed_paid_journeys']==5
    r['legs']=[leg('line','a','c')]
    assert allocate_od(events,[r],{'t1':10})['totals']['completed_paid_journeys']==0


def test_line_opening_waits_for_all_packages_and_keeps_unknown_cash_open():
    packages={k:dict(completion_date='2028-01-01',installed_cash_usd=1,accepted=True,acceptance_record=k) for k in OPENING_PACKAGES}
    packages['approvals']['completion_date']='2028-02-01'
    row=line_opening('line',packages)
    assert row['full_line_opening_date']=='2028-02-01' and row['known_bottleneck_packages']==['approvals']
    packages['stations']['completion_date']=None;packages['stations']['installed_cash_usd']=None
    row=line_opening('line',packages)
    assert row['full_line_opening_date'] is None and row['complete_scope_cash_usd'] is None
    assert not row['opening_accepted'] and not row['revenue_opening_adopted']


def test_energy_and_distance_are_costed_once_in_the_same_operating_scope():
    cost=operating_cost(100,20,.1,2,50)
    assert cost['total_modelled_opex_usd']==100


def test_alternating_cross_section_lanes_do_not_establish_a_connected_path():
    bounds=(-20,20,-4,4)
    obstacles=[(-15,0,-4,1),(0,15,-1,4)]
    assert not continuous_path(bounds,obstacles,1.5)
    assert continuous_path(bounds,[(-10,10,-1,1)],1.5)


def test_capacity_screen_does_not_clip_a_protruding_lift_to_hide_its_envelope():
    platform=dict(level='platform',y_mm=0,width_mm=8000)
    lift=dict(served_levels=['platform'],x_mm=0,y_mm=3000,width_mm=3500,length_mm=3500)
    with pytest.raises(ValueError,match='outside platform'):footprint_screen(platform,60,[lift])


def test_serial_lift_levels_limit_outage_capacity_instead_of_summing_all_cabs():
    lifts=[dict(id=name,kind='lift',served_levels=levels,x_mm=x,y_mm=0,width_mm=1000,length_mm=1000)
        for name,levels,x in [('low-a',['street','middle'],-5000),('low-b',['street','middle'],5000),
            ('high-a',['middle','upper'],-5000),('high-b',['middle','upper'],5000)]]
    station=dict(id='station',passenger_demand={},layout=dict(equipment=lifts,platforms=[dict(id='upper-platform',level='upper',y_mm=0,width_mm=8000)]))
    result=station_capacity_screen(station,60,dict(lift_capacity_pax_hour={'low-a':10,'low-b':10,'high-a':100,'high-b':100},source_record='synthetic-lift-duty'))
    case=next(r for r in result['one_lift_out_cases'] if r['unavailable_lift']=='low-a')
    assert case['street_to_platform_capacity_pax_hour']['upper-platform']==10
    assert case['remaining_station_lift_capacity_pax_hour']==210
    assert not case['capacity_acceptance']


def test_arrivals_transfers_and_train_load_pulses_keep_their_station_and_time():
    events=[dict(request='one',station='a',destination='b',arrival_minute=0,minute=10,alight_minute=20,passengers=30),
        dict(request='two',station='a',destination='b',arrival_minute=5,minute=15,alight_minute=25,passengers=20)]
    rows={r['station']:r for r in passenger_pulses(events)}
    assert rows['a']['peak_reserved_waiting_passengers']==50
    assert rows['b']['alighting_train_load_pulses'][0]==dict(minute=20,passengers=30)


def test_component_locations_drive_cg_and_unequal_axle_loads_without_closing_mass_evidence():
    bodies=[dict(id='body',supports=['left','right'])]
    bogies=[dict(id='left',pivot_x_m=2.,axle_x_m=[1.,3.]),dict(id='right',pivot_x_m=8.,axle_x_m=[7.,9.])]
    rows=[dict(id='one',included_items=['one'],mass_kg=1000.,uncertainty_kg=10.,x_m=3.,y_m=0.,z_m=1.,
        position_uncertainty_m=.1,body='body',evidence_record='bench-component-weigh')]
    result=mass_properties(rows,['one'],bodies,bogies)
    assert result['cg_m']['x']==3 and result['cg_interval_m']['x'][0]<3<result['cg_interval_m']['x'][1]
    assert result['axle_pattern'][0]['static_load_kn']>result['axle_pattern'][-1]['static_load_kn']
    assert result['load_balance_passed'] and not result['simulator_startup_replaced']
    assert mass_properties(rows,['one','unweighed'],bodies,bogies)['total_mass_kg'] is None
    with pytest.raises(ValueError,match='overlaps'):mass_properties(rows+[dict(rows[0],id='parent')],['one'],bodies,bogies)


def test_workload_and_peak_posts_replace_weighted_headcount_and_missing_measurements_stay_unknown():
    row=dict(id='inspection',role='inspector',qualified_people_per_task=2,simultaneous_tasks=3,simultaneous_group='peak',
        annual_tasks=1000,worker_minutes_per_task=60,measurement_record='bench-stopwatch')
    calendar=dict(paid_hours_year=2080,leave_hours=160,training_hours=80,sickness_hours=40,holiday_hours=80,handover_hours=40)
    result=workload_staffing([row],calendar)
    assert result['roles'][0]['complete_person_hours']==2000 and result['roles'][0]['required_establishment_fte']==6
    row['measurement_record']=None
    assert workload_staffing([row],calendar)['roles'][0]['required_establishment_fte'] is None


def test_recruitment_dates_include_training_batches_and_assessment_capacity():
    training=dict(recruitment_days=30,induction_days=5,course_days=10,learners_per_cohort=2,parallel_cohorts=1,
        supervised_practice_days=20,assessment_days=1,assessor_people_per_day=1)
    row=recruitment_backplan('2027-06-01',10,training)
    assert row['cohorts']==5 and row['recruitment_open_on']=='2027-02-06'
    assert not row['attendance_equals_equipment_authority'] and not row['work_authority_granted']


def test_two_trains_queue_for_the_same_switch_and_cannot_teleport_on_the_next_day():
    routes=[dict(id='exit-a',from_berth='a',to_berth='line',to_is_network=True,resources=['switch','lead'],travel_minutes=5,clearance_minutes=2),
        dict(id='exit-b',from_berth='b',to_berth='line',to_is_network=True,resources=['switch','lead'],travel_minutes=5,clearance_minutes=2),
        dict(id='return-a',from_berth='line',to_berth='a',resources=['switch','lead'],travel_minutes=5)]
    trains=[dict(id='a',berth='a',ready_minute=0,charge_ready_minute=10),dict(id='b',berth='b',ready_minute=0)]
    requests=[dict(id='one',train='a',route='exit-a',requested_minute=0),dict(id='two',train='b',route='exit-b',requested_minute=10),
        dict(id='return',train='a',route='return-a',requested_minute=1440)]
    result=yard_dispatch(routes,trains,requests,horizon_minutes=2880)
    assert result['departures'][0]['departure_minute']==10
    assert result['departures'][1]['departure_minute']==17
    assert result['final_train_states']['a']['berth']=='a'
    requests[-1]['route']='exit-a'
    with pytest.raises(ValueError,match='origin'):yard_dispatch(routes,trains,requests,horizon_minutes=2880)


def test_heat_generation_and_cooling_update_pack_temperature_without_fake_calibration():
    parameters=dict(heat_capacity_kj_k=100,loss_fraction=.1,conductance_kw_k=0,
        maximum_cooling_thermal_kw=0,cooling_target_c=30,source_record='synthetic-thermal-bench')
    result=thermal_step(30,30,100,60,parameters)
    assert result['temperature_c']==36 and not result['calibration_accepted']
    parameters['maximum_cooling_thermal_kw']=20
    assert thermal_step(30,30,100,60,parameters)['temperature_c']==30
    assert thermal_step(30,30,100,60,None)['temperature_c'] is None


def test_hot_and_aged_pack_limits_feed_back_into_delivered_power():
    import json
    from pathlib import Path
    profile=json.loads((Path(__file__).resolve().parents[3]/'lib/templates/battery-profiles.json').read_text())['profiles']['lfp-onboard-study']
    parameters=dict(heat_capacity_kj_k=100,loss_fraction=.1,conductance_kw_k=0,
        maximum_cooling_thermal_kw=0,cooling_target_c=30,source_record='synthetic-thermal-bench')
    steps=[dict(seconds=60,power_kw=500,ambient_c=45)]*2
    hot=thermal_duty(profile,parameters,steps,initial_soc=.8,initial_temperature_c=profile['temperature_max_c']-1,soh=.8)
    assert hot['steps'][1]['delivered_terminal_power_kw']<hot['steps'][0]['delivered_terminal_power_kw']<500
    parameters['maximum_cooling_thermal_kw']=20
    recovered=thermal_duty(profile,parameters,steps,initial_soc=.8,initial_temperature_c=profile['temperature_max_c']-1,soh=.8)
    assert recovered['steps'][1]['delivered_terminal_power_kw']>hot['steps'][1]['delivered_terminal_power_kw']

"""Independent controls for the offline station/system evidence boundary.

The moving interface fixture is explicitly synthetic; station/interlocking
observations are emitted by the actual built Rust example. Physical acceptance
and executable input/output authority remain false throughout.
"""
from copy import deepcopy
from dataclasses import asdict
import gzip
from hashlib import sha256
import json
import math
from pathlib import Path

import pytest

from engineering.ferrite_maglev import configuration,model,moving_train,station
from engineering.ferrite_maglev import system_campaign as campaign


@pytest.fixture(scope='module')
def context():
    return model.load()[1]


def replace_input(monkeypatch,tmp_path,old,new):
    text=campaign.INPUT.read_text()
    assert old in text
    path=tmp_path/'campaign.toml';path.write_text(text.replace(old,new))
    monkeypatch.setattr(campaign,'INPUT',path)


def test_motor_voltage_bound_comes_from_declared_dc_bus(monkeypatch,tmp_path):
    a=campaign.load();m=a['motor']
    limit=m['dc_bus_v']*m['modulation_ceiling_fraction']/math.sqrt(3)
    assert m['maximum_voltage_v']<=limit
    replace_input(monkeypatch,tmp_path,f'maximum_voltage_v = {m["maximum_voltage_v"]}',
                  f'maximum_voltage_v = {limit+1}')
    with pytest.raises(ValueError,match='voltage|modulation|bus'):
        campaign.load()


@pytest.mark.parametrize('fraction',[0.,1.01])
def test_invalid_modulation_fraction_is_not_an_unbounded_voltage_allowance(monkeypatch,tmp_path,fraction):
    replace_input(monkeypatch,tmp_path,'modulation_ceiling_fraction = 0.90',
                  f'modulation_ceiling_fraction = {fraction}')
    with pytest.raises(ValueError):campaign.load()


@pytest.mark.parametrize('bad',[-1,True,12,13])
def test_failed_unit_count_is_bounded_and_cannot_invent_braking_capacity(context,bad):
    with pytest.raises(ValueError):campaign.emergency_brake(context,failed_units=bad)


def test_brake_kinetic_and_gradient_energy_close_independently(context):
    a=campaign.load()['brake'];r=campaign.emergency_brake(context,speed_kmh=80.,grade=.05,mu=.25)
    count=context['vehicle']['cars_per_train']
    mass=model.mass(context,context['mass']['ferrite_base'],context['power']['services_battery_kwh_per_car'])['aw3_kg']*count
    v=80/3.6;g=9.81*.05/math.sqrt(1+.05**2)
    distance=v*a['response_s']+.5*g*a['response_s']**2+(v+g*a['response_s'])**2/(2*a['net_deceleration_m_s2'])
    energy=.5*mass*v*v+mass*g*distance
    assert r['train_mass_kg']==mass
    assert r['stopping_distance_m']==pytest.approx(distance)
    assert r['brake_energy_j']==pytest.approx(energy)
    assert r['thermal_mass_kg']==pytest.approx(energy*a['thermal_mass_factor']/(a['heat_capacity_j_kg_k']*a['temperature_rise_k']))
    assert r['added_mass_kg_per_car']==pytest.approx(r['thermal_mass_kg']/count+a['hardware_allowance_kg_per_car'])
    assert r['remaining_growth_reserve_kg_per_car']+r['consumed_growth_reserve_kg_per_car']==pytest.approx(context['mass']['growth_reserve'])
    assert r['reserve_is_not_additional_verified_mass']
    assert not r['engineering_accepted'] and all(r[k] is False for k in model.FLAGS)


def test_speed_grade_and_failed_caliper_have_monotonic_physical_demands(context):
    slow=campaign.emergency_brake(context,speed_kmh=40.,grade=0.)
    fast=campaign.emergency_brake(context,speed_kmh=80.,grade=0.)
    grade=campaign.emergency_brake(context,speed_kmh=80.,grade=.05)
    for key in ('brake_energy_j','stopping_distance_m','thermal_mass_kg'):
        assert slow[key]<fast[key]<grade[key]
    weak=campaign.emergency_brake(context,mu=.15)
    strong=campaign.emergency_brake(context,mu=.35)
    assert weak['braking_force_n']==strong['braking_force_n']
    assert weak['available_friction_force_n']<strong['available_friction_force_n']
    assert weak['interface_loads']['pad_pressure_pa']>strong['interface_loads']['pad_pressure_pa']
    failed=campaign.emergency_brake(context,failed_units=1)
    nominal=campaign.emergency_brake(context)
    for key in ('brake_energy_j','thermal_mass_kg','braking_force_n','added_mass_kg_per_car','installed_clamp_force_n'):
        assert failed[key]==nominal[key]
    assert failed['available_units']==nominal['installed_units']-1
    assert failed['available_friction_force_n']/nominal['available_friction_force_n']==pytest.approx(failed['available_units']/nominal['available_units'])
    pressure=failed['braking_force_n']/(failed['friction_coefficient_assumption']*2*failed['available_units']*campaign.load()['brake']['pad_area_m2'])
    assert failed['interface_loads']['pad_pressure_pa']==pytest.approx(pressure)
    assert failed['interface_loads']['pad_pressure_pa']>nominal['interface_loads']['pad_pressure_pa']


def test_frame_positions_are_measured_at_observed_time_and_force_is_current(context):
    a=campaign.load();request,t,_=campaign.frames(a,context)
    dwell=context['power']['station_dwell_seconds'];age=a['motor']['observation_age_ns']
    assert age>0
    selected=request['frames'][::137]+[request['frames'][-1]]
    for f in selected:
        elapsed=(f['now_ns']-campaign.BASE-10000)/1e9
        measured=(f['observed_ns']-campaign.BASE-10000)/1e9
        assert f['now_ns']-f['observed_ns']==age
        local=measured-(a['runtime_s']+dwell) if f['outgoing'] else measured
        if not f['outgoing'] and elapsed>=a['runtime_s']:
            position=speed=0.
        else:
            p=moving_train.trajectory_at(t,max(0.,min(a['runtime_s'],local)))
            position=p['position_m']-(a['distance_m'] if f['zone']==2 and not f['outgoing'] else 0.)
            speed=p['speed_m_s']
        assert f['position_mm']==round(position*1000)
        assert f['velocity_mmps']==round(speed*1000)
        if f['mode'] in (1,3):assert f['force_n']==0.
        else:
            current_local=elapsed-(a['runtime_s']+dwell) if f['outgoing'] else elapsed
            current=moving_train.trajectory_at(t,max(0.,min(a['runtime_s'],current_local)))
            assert f['force_n']==pytest.approx(current['motor_force_n'])
    assert request['frames'][-1]['full_tail_clear']
    final=request['frames'][-1]
    cfg=configuration.selected(context)
    local=(final['now_ns']-campaign.BASE-10000)/1e9-a['runtime_s']-dwell
    actual=moving_train.trajectory_at(t,local)['position_m']
    assert actual-cfg.formation.assumed_overall_length_m>station.load()['station']['winding_end_m']+a['downstream_overlap_m']


def moving_fixture(c):
    """Exact-input synthetic interface; no claim to execute the moving twin here."""
    a=campaign.load();cfg=configuration.selected(c);motion=moving_train.load()
    t=station.trajectory(distance_m=a['distance_m'],runtime_s=a['runtime_s'],acceleration=a['acceleration_m_s2'],
        car_mass_kg=model.mass(c,c['mass']['ferrite_base'],c['power']['services_battery_kwh_per_car'])['aw3_kg'],cars=cfg.formation.cars)
    spread=.002
    return dict(schema='osr-selected-moving-twin/1',candidate_sha256='a'*64,
        configuration_revision=cfg.revision,source_sha256=moving_train.sources(),study_pass=True,
        formation=asdict(cfg.formation),profile=t['inputs'],beam_section_m=motion['beam_section_m'],
        guideway_span_m=motion['guideway_span_m'],beam_modulus_pa=motion['beam_modulus_pa'],
        gross_train_mass_kg=t['inputs']['train_mass_kg'],coupler_stiffness_n_m=motion['coupler_stiffness_n_m'],
        coupler_damping_n_s_m=motion['coupler_damping_n_s_m'],maximum_cumulative_indexing_spread_m=spread,
        maximum_magnetic_phase_spread_degrees=spread/(2*station.load()['vehicle']['pole_pitch_m'])*360,
        maximum_individual_coupler_extension_m=.0004,peak_coupler_force_n=40000.,
        minimum_gap_m=.003,maximum_gap_m=.011,sensor_bias_screen_m=.0005,
        beam_modulus_adverse_factor=.85,mandatory_confirmation_candidate_sha256=['b'*64,'c'*64,'d'*64],
        physical_output_authorised=False,shared_field_phase_registration_accepted=False,**model.FLAGS)


def test_exact_moving_spread_is_charged_to_phase_error_budget(context):
    moving=moving_fixture(context);a=campaign.load()
    request,_,_=campaign.frames(a,context,moving=moving)
    expected=a['motor']['position_uncertainty_um']+math.ceil(moving['maximum_cumulative_indexing_spread_m']*1e6)
    assert {f['position_uncertainty_um'] for f in request['frames']}=={expected}
    assert all(f['receiver_healthy'] for f in request['frames'])
    bad=deepcopy(moving);bad['configuration_revision']='other-revision'
    with pytest.raises(ValueError,match='moving|revision|configuration'):campaign.frames(a,context,moving=bad)
    bad=deepcopy(moving);bad['profile']['runtime_s']+=1
    with pytest.raises(ValueError,match='moving|profile|runtime'):campaign.frames(a,context,moving=bad)
    bad=deepcopy(moving);bad['beam_section_m']['depth']+=.01
    with pytest.raises(ValueError,match='moving|beam|section'):campaign.frames(a,context,moving=bad)


@pytest.fixture(scope='module')
def actual_campaign(context):
    # This executes Rust interlocking and station control. The separate moving
    # solver interface remains a synthetic exact-input fixture in this test.
    moving=moving_fixture(context)
    patch=pytest.MonkeyPatch()
    patch.setattr(moving_train,'read_selected',lambda *args,**kwargs:deepcopy(moving))
    try:
        result,execution=campaign.study()
        yield result,execution,moving
    finally:patch.undo()


def test_actual_rust_nominal_and_fault_cases_retain_protected_resources(actual_campaign):
    result,execution,moving=actual_campaign
    assert [r['case'] for r in result['cases']]==['nominal',*campaign.FAULTS]
    assert result['numerical_study_pass']
    nominal=json.loads(execution['nominal']['stdout'])
    request=json.loads(execution['nominal']['stdin'])
    assert nominal['incoming_cleared'] and nominal['outgoing_committed']
    assert all(row['incoming_protected'] for row in nominal['observations'][:-1])
    final=nominal['observations'][-1]
    assert final['outgoing_protected'] and not final['incoming_protected']
    first_clear=next(i for i,f in enumerate(request['frames']) if f['full_tail_clear'])
    assert first_clear==len(request['frames'])-1
    assert result['resource_headway']['planning_minimum_s']==pytest.approx(
        (final['now_ns']-campaign.BASE-10000)/1e9+station.load()['station']['release_allowance_s'])
    assert result['resource_headway']['planning_minimum_s']<=180
    for name in campaign.FAULTS:
        value=json.loads(execution[name]['stdout']);last=value['observations'][-1]
        assert not value['incoming_cleared'] and not last['feasible']
        assert last['incoming_protected'] is (name!='uncommitted')
        if name!='uncommitted':assert value['fault_held'] and last['recovery_required']
        assert not last['physical_output_authorised'] and not last['support_shutdown_requested']
    assert result['phase_position_uncertainty_um']==campaign.load()['motor']['position_uncertainty_um']+2000
    assert result['selected_moving_evidence']==moving
    assert all(result[k] is False for k in model.FLAGS)


def test_rust_motor_outputs_follow_independent_si_work_equations(actual_campaign):
    _,execution,_=actual_campaign
    request=json.loads(execution['nominal']['stdin']);observed=json.loads(execution['nominal']['stdout'])
    m=request['motor'];previous={}
    for f,r in zip(request['frames'],observed['observations']):
        force=f['force_n'] if f['mode'] not in (1,3) else 0.
        current=force/m['force_constant_n_a']
        velocity=f['velocity_mmps']/1000
        old_time,old_current=previous.get(f['zone'],(None,0.))
        dt=(m['maximum_tick_ns'] if old_time is None else f['now_ns']-old_time)/1e9
        voltage=0. if f['mode'] in (1,3) else abs(m['resistance_ohm']*current)+m['inductance_h']*abs((current-old_current)/dt)+abs(m['force_constant_n_a']*velocity)
        assert r['force_n']==pytest.approx(force)
        assert r['current_a']==pytest.approx(current)
        assert r['mechanical_power_w']==pytest.approx(force*velocity)
        assert r['airgap_electrical_power_w']==pytest.approx(force*velocity)
        assert r['copper_loss_w']==pytest.approx(current**2*m['resistance_ohm'])
        assert r['voltage_bound_v']==pytest.approx(voltage)
        assert abs(current)<=m['maximum_current_a']
        assert voltage<=m['maximum_voltage_v']
        previous[f['zone']]=(f['now_ns'],current)


@pytest.mark.parametrize('field,value',[
    ('current_a',0.),('voltage_bound_v',0.),('copper_loss_w',0.),
    ('physical_output_authorised',True),('incoming_protected',False),
])
def test_replay_verifier_rejects_plausible_but_unexecuted_outputs(actual_campaign,field,value):
    _,execution,_=actual_campaign
    request=json.loads(execution['nominal']['stdin']);observed=json.loads(execution['nominal']['stdout'])
    index=next(i for i,row in enumerate(observed['observations']) if abs(row['force_n'])>10000)
    assert observed['observations'][index][field]!=value
    observed['observations'][index][field]=value
    with pytest.raises(ValueError):campaign.validate_replay(observed,request,'nominal')


def write_packet(output,result,execution):
    output.mkdir()
    payload={'result.json.gz':gzip.compress(campaign.encoded(result),mtime=0,compresslevel=1),
        'executed.json.gz':gzip.compress(campaign.encoded(execution),mtime=0,compresslevel=1),
        'overview.svg':b'<svg xmlns="http://www.w3.org/2000/svg"/>','README.md':b'Offline test fixture\n'}
    for name,data in payload.items():(output/name).write_bytes(data)
    manifest=dict(schema='osr-system-campaign-publication/1',source_sha256=result['source_sha256'],
        files_sha256={name:sha256(data).hexdigest() for name,data in payload.items()},**model.FLAGS)
    (output/'manifest.json').write_bytes(campaign.encoded(manifest))
    return output


def rehash(output,name,value):
    data=gzip.compress(campaign.encoded(value),mtime=0,compresslevel=1);(output/name).write_bytes(data)
    path=output/'manifest.json';manifest=json.loads(path.read_text())
    manifest['files_sha256'][name]=sha256(data).hexdigest();path.write_bytes(campaign.encoded(manifest))


def test_actual_campaign_packet_checksums_and_independent_verification(actual_campaign,tmp_path):
    result,execution,_=actual_campaign
    output=write_packet(tmp_path/'valid',result,execution)
    manifest=campaign.verify(output)
    assert manifest['source_sha256']==campaign.sources()
    assert set(manifest['files_sha256'])==campaign.FILES


@pytest.mark.parametrize('field',[
    'resource_headway','numerical_study_pass','binary_sha256','full_bundle_tail_clearance_front_distance_m',
    'phase_position_uncertainty_um','emergency_brake_cases','selected_moving_evidence','physical_release',
])
def test_rehashed_result_tampering_cannot_promote_or_change_the_study(actual_campaign,tmp_path,field):
    original,execution,_=actual_campaign;result=deepcopy(original)
    output=write_packet(tmp_path/'tampered',original,execution)
    if field=='resource_headway':result[field]['planning_minimum_s']-=10
    elif field=='numerical_study_pass':result[field]=not result[field]
    elif field=='binary_sha256':result[field]='0'*64
    elif field=='full_bundle_tail_clearance_front_distance_m':result[field]-=75
    elif field=='phase_position_uncertainty_um':result[field]-=1
    elif field=='emergency_brake_cases':result[field][0]['brake_energy_j']*=.5
    elif field=='selected_moving_evidence':result[field]['candidate_sha256']='f'*64
    else:result[field]=True
    rehash(output,'result.json.gz',result)
    with pytest.raises(ValueError):campaign.verify(output)


def test_rehashed_input_and_output_tampering_are_rejected(actual_campaign,tmp_path):
    result,original,_=actual_campaign
    execution=deepcopy(original);request=json.loads(execution['nominal']['stdin'])
    request['frames'][1]['observed_ns']+=1
    execution['nominal']['stdin']=campaign.encoded(request).decode()
    output=write_packet(tmp_path/'input',result,execution)
    with pytest.raises(ValueError):campaign.verify(output)
    execution=deepcopy(original);value=json.loads(execution['nominal']['stdout'])
    value['observations'][3]['current_a']+=1
    execution['nominal']['stdout']=json.dumps(value)
    output=write_packet(tmp_path/'output',result,execution)
    with pytest.raises(ValueError):campaign.verify(output)


def test_wrong_manifest_schema_and_symlinked_receipt_are_rejected(actual_campaign,tmp_path):
    result,execution,_=actual_campaign
    output=write_packet(tmp_path/'schema',result,execution)
    manifest=json.loads((output/'manifest.json').read_text());manifest['schema']='unrelated/1'
    (output/'manifest.json').write_bytes(campaign.encoded(manifest))
    with pytest.raises(ValueError):campaign.verify(output)
    output=write_packet(tmp_path/'symlink',result,execution)
    target=tmp_path/'external-manifest.json';(output/'manifest.json').rename(target)
    (output/'manifest.json').symlink_to(target)
    with pytest.raises(ValueError):campaign.verify(output)


@pytest.mark.parametrize('change',[
    'missing-confirmation','duplicate-confirmation','bad-candidate','wrong-phase-spread',
    'release-authority','unbounded-indexing',
])
def test_moving_evidence_budget_is_exact_and_cannot_omit_controls(context,change):
    moving=moving_fixture(context);a=campaign.load()
    t=station.trajectory(distance_m=a['distance_m'],runtime_s=a['runtime_s'],acceleration=a['acceleration_m_s2'],
        car_mass_kg=model.mass(context,context['mass']['ferrite_base'],context['power']['services_battery_kwh_per_car'])['aw3_kg'])
    if change=='missing-confirmation':moving['mandatory_confirmation_candidate_sha256'].pop()
    elif change=='duplicate-confirmation':moving['mandatory_confirmation_candidate_sha256'][1]=moving['mandatory_confirmation_candidate_sha256'][0]
    elif change=='bad-candidate':moving['candidate_sha256']='not-a-revision'
    elif change=='wrong-phase-spread':moving['maximum_magnetic_phase_spread_degrees']/=2
    elif change=='release-authority':moving['physical_release']=True
    else:moving['maximum_cumulative_indexing_spread_m']=.01
    with pytest.raises(ValueError):campaign.validate_moving(moving,a,context,t)


@pytest.mark.parametrize('fault',['future-observation','repeated-observation'])
def test_actual_rust_rejects_impossible_observation_timestamps(actual_campaign,fault):
    _,execution,_=actual_campaign
    request=json.loads(execution['nominal']['stdin']);request['frames']=request['frames'][:3]
    f=request['frames'][-1]
    f['observed_ns']=f['now_ns']+1 if fault=='future-observation' else request['frames'][-2]['observed_ns']
    binary=execution['nominal']['command']
    observed=json.loads(campaign._run(binary,campaign.encoded(request).decode())['stdout'])
    last=observed['observations'][-1]
    assert not last['feasible'] and last['fault']=='Some(ClockOrReplay)'
    assert last['recovery_required'] and last['incoming_protected']
    assert not observed['incoming_cleared'] and not last['physical_output_authorised']


@pytest.mark.parametrize('field,value',[
    ('schema','unrelated/1'),('fault_held',True),('outgoing_committed',False),
    ('detector_evidence','physical authenticated detectors'),
])
def test_rehashed_nominal_metadata_cannot_add_fault_or_acceptance_claims(actual_campaign,field,value):
    _,execution,_=actual_campaign
    request=json.loads(execution['nominal']['stdin']);observed=json.loads(execution['nominal']['stdout'])
    observed[field]=value
    with pytest.raises(ValueError):campaign.validate_replay(observed,request,'nominal')


@pytest.mark.parametrize('field,value',[('fault','Some(Voltage)'),('recovery_required',True)])
def test_nominal_trace_cannot_claim_inconsistent_latched_fault(actual_campaign,field,value):
    _,execution,_=actual_campaign
    request=json.loads(execution['nominal']['stdin']);observed=json.loads(execution['nominal']['stdout'])
    observed['observations'][1][field]=value
    with pytest.raises(ValueError):campaign.validate_replay(observed,request,'nominal')


def test_primary_traffic_uses_complete_bundle_and_matches_discrete_clearance(context):
    primary=station.evaluate(context);traffic=primary['traffic'];a=campaign.load()
    cfg=configuration.selected(context)
    end=station.load()['station']['winding_end_m']
    assert traffic['downstream_overlap_beyond_winding_m']==a['downstream_overlap_m']==75.
    assert traffic['clearance_front_distance_m']==cfg.formation.assumed_overall_length_m+end+75==254.5
    assert traffic['time_until_tail_clears_resource_s']>traffic['time_until_tail_clears_winding_s']
    request,_,_=campaign.frames(a,context)
    discrete=(request['frames'][-1]['now_ns']-campaign.BASE-10000)/1e9+station.load()['station']['release_allowance_s']
    assert traffic['planning_minimum_headway_s']==pytest.approx(178.08816072,abs=1e-7)
    assert 0<=discrete-traffic['planning_minimum_headway_s']<=a['step_s']+1e-9
    assert discrete==pytest.approx(178.09,abs=1e-8)
    authored=station.evaluate()
    assert authored['trajectory']['inputs']['runtime_s']==90.
    assert authored['traffic']['downstream_overlap_beyond_winding_m']==0.
    assert authored['traffic']['clearance_front_distance_m']==179.5


def test_primary_supply_peaks_do_not_mix_converted_services_with_source_input(context):
    result=station.evaluate(context);p=context['power'];t=result['trajectory'];power=result['station_power']
    cars=context['vehicle']['cars_per_train'];hotel=p['hot_hotel_kw_per_car']*cars
    runtime=t['inputs']['runtime_s'];dwell=p['station_dwell_seconds'];connected=p['charger_effective_seconds']
    converted=hotel*(runtime+dwell)/connected
    source=converted/p['station_charger_efficiency_assumption']
    assert result['charging']['connected_interface_kw_per_train']==pytest.approx(converted)
    assert result['charging']['connected_input_kw_per_train']==pytest.approx(source)
    assert power['one_launch_plus_opposite_connected_services_kw']==pytest.approx(t['peak_traction_input_kw']+source)
    assert power['one_launch_plus_opposite_connected_services_kw']==pytest.approx(4179.6,abs=.01)
    assert power['two_coincident_connected_services_kw']==pytest.approx(2*source)
    assert power['two_coincident_connected_services_kw']==pytest.approx(2631.111111)
    assert power['two_coincident_converted_services_kw']==pytest.approx(2*converted)
    assert power['one_launch_plus_opposite_converted_services_kw']==pytest.approx(t['peak_traction_input_kw']+converted)
    hotel_source_kwh=hotel*(runtime+dwell)/3600/p['station_charger_efficiency_assumption']
    expected_average=(t['station_positive_input_kwh']+hotel_source_kwh)*2*3600/result['traffic']['scheduled_headway_s']
    assert power['average_two_direction_input_kw_before_station_loads']==pytest.approx(expected_average)
    assert power['average_two_direction_input_kw_before_station_loads']>power['average_two_direction_input_kw_before_station_loads_and_losses']


@pytest.mark.parametrize('eta',[0.,1.01,float('nan'),True])
def test_primary_charging_efficiency_cannot_create_energy(context,eta):
    changed=deepcopy(context);changed['power']['station_charger_efficiency_assumption']=eta
    with pytest.raises(ValueError):model.validate(changed)
    with pytest.raises(ValueError):station.evaluate(changed)

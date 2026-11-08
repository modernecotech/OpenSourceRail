"""Independent necessary-bound, identity and fail-closed adapter controls."""
from copy import deepcopy
from math import pi, sqrt

import pytest

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity, digest
from engineering.compact_drive.common import seal, policy
from engineering.compact_drive.gears import train
from engineering.railway_project import drive


def body_fixture():
    """Small explicit counted fixture; not a generated/qualified railway body."""
    hardware=dict(manufacturer='EMRAX',model='268',winding='MV',phase_system='1UVW',cooling='LC')
    physical=dict(schema='osr-compact-drive-body-physical/1',hardware=dict(motor=hardware),
                  config=policy()['configs'][0],geometry='unit-test-only; no installation claim')
    cid=identity(physical)
    names=(('vendor-motor',24,22.3),('inverter',24,30.),('integration-reserve',6,400.),
           ('stage1-pinion',24,3.),('stage1-wheel',24,10.),('stage2-pinion',24,6.),('stage2-wheel',24,14.))
    parts=[dict(id='compact-drive/'+name,quantity_per_train=count,mass_each_kg={k:mass for k in ('low','base','high')}) for name,count,mass in names]
    ownership=dict(all_new_drive_components_in_body_BOM=True,additional_external_drive_mass_kg=0.,
                   zero_is_exact_no_external_addition_not_unknown_equipment=True,remaining_unknown_mass_positive=True)
    contract=dict(schema='osr-compact-drive-interface-contract/1',candidate_id=cid,
                  geartrain=train(policy()['configs'][0]),mass_ownership=ownership)
    contract['contract_id']=identity(contract)
    return seal(dict(schema='osr-vehicle-installation/1',physical_definition=physical,candidate_id=cid,
        parts=parts,patterns=[dict(part_id=r['id'],count=r['quantity_per_train']) for r in parts],
        compact_drive_contract=contract,
        source_sha256={n:digest(ROOT/n) for n in ('engineering/compact_drive/design.py','engineering/compact_drive/data/vendor.json')},
        **{k:False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','selected_reference_changed','movement_authority')}))


def reseal_body(b):
    b['candidate_id']=identity(b['physical_definition'])
    c=b['compact_drive_contract'];c['candidate_id']=b['candidate_id'];c.pop('contract_id',None);c['contract_id']=identity(c)
    return seal(b)


def declared():
    """Explicit synthetic sizing hypotheses, NOT selected commercial hardware."""
    return dict(wheel_radius_m=.34,motor_torque_limit_nm=205.,motor_power_limit_w=91000.,
        inverter_current_limit_arms=220.,inverter_input_power_limit_w_each=120000.,
        dc_bus_min_v=650.,gear_input_torque_limit_nm=205.,gear_output_torque_limit_nm=1800.,
        gear_output_power_limit_w=90000.,gear_efficiency=.9,motor_efficiency_floor=.9,
        inverter_efficiency_floor=.97,grid_input_power_limit_w=3e6,contact_force_limit_n=120000.,
        coolant_inlet_c=45.,coolant_flow_l_min_each=6.,rotor_airflow_m3_min_each=37.,
        cooling_parasitic_power_w=12000.,copper_resistance_hot_multiplier=1.3,
        voltage_model='catalogue-nominal-kv-sizing-hypothesis',assumption_reference='test-positive-bound-only')


def test_continuous_envelope_uses_real_ratio_current_and_power_caps():
    b=body_fixture(); r=drive.evaluate(b,declared());m=r['model']
    assert r['candidate_id']==b['candidate_id'] and r['body_evaluation_id']==b['evaluation_id']
    assert m['gear_ratio']==pytest.approx(7.37)
    assert m['motor_torque_cap_nm']==205.
    assert m['motor_rms_current_cap_a']==pytest.approx(205./1.2)
    assert m['maximum_speed_m_s']==pytest.approx(4500*2*pi/60/7.37*.34)
    assert m['torque_output_cap_nm_each']==pytest.approx(205*7.37*.9)
    assert m['mechanical_power_w']<=24*91000*.9
    assert m['rotor_reflected_equivalent_mass_kg']==pytest.approx(24*.0949*7.37**2/.34**2)
    assert r['installed_operating_map_admission']=='held'
    assert all(r[k] is False for k in drive.FLAGS)
    assert r['source_catalogue']['peak_torque_nm']==500.
    assert r['source_catalogue']['peak_not_used'] is True


@pytest.mark.parametrize('name',['/etc/passwd','../outside.json'])
def test_external_source_paths_are_refused_before_reading(name):
    b=body_fixture();b['source_sha256'][name]='0'*64
    with pytest.raises(ValueError,match='in-root'):
        drive.evaluate(seal(b),declared())


def test_native_shape_has_exact_counted_mass_and_acknowledgement_required():
    r=drive.evaluate(body_fixture(),declared())
    with pytest.raises(ValueError,match='acknowledgement'):
        drive.native_drive(r,1500.)
    n=drive.native_drive(r,1500.,acknowledge_domain=drive.CONDITIONAL_DOMAIN)
    assert set(n)=={'points','windows_m','maximum_speed_m_s','mechanical_power_w','electrical_efficiency','grid_power_w','contact_force_cap_n','external_mass_kg','external_resistance_n'}
    assert n['windows_m']==[[0.,1500.]] and n['external_mass_kg']==0.
    assert r['mass_ownership']['motor_mass_kg']['base']==pytest.approx(535.2)
    assert r['mass_ownership']['integration_reserve_mass_kg']['base']==2400.
    assert drive.mandatory_auxiliary_power_w(r)>12000.
    # Native point interpolation must additionally cap F*v by output power.
    for point in n['points']:
        assert point['force_n']*point['speed_m_s']<=n['mechanical_power_w']+1e-8


@pytest.mark.parametrize('field',[k for k in drive.INPUT_UNITS if k not in ('voltage_model','assumption_reference')])
def test_null_capacity_or_efficiency_never_becomes_zero_or_native_drive(field):
    q=declared();q[field]=None;r=drive.evaluate(body_fixture(),q)
    assert r['declared'][field] is None and r['model'] is None
    assert any(h.get('field')==field for h in r['definition_holds'])
    with pytest.raises(ValueError,match='held'):
        drive.native_drive(r,1000.,acknowledge_domain=drive.CONDITIONAL_DOMAIN)


def test_hypothesis_changes_change_evaluation_but_do_not_mutate_geometry():
    b=body_fixture();old=deepcopy(b);q=declared();r=drive.evaluate(b,q)
    q['motor_torque_limit_nm']=180.;r2=drive.evaluate(b,q)
    assert b==old
    assert r['candidate_id']==r2['candidate_id']==identity(b['physical_definition'])
    assert r['evaluation_id']!=r2['evaluation_id']
    assert r2['model']['motor_torque_cap_nm']==180.
    assert r2['model']['points'][0]['force_n']<r['model']['points'][0]['force_n']


def test_gear_output_current_and_dc_caps_reduce_available_performance():
    q=declared();q.update(gear_output_torque_limit_nm=900.,inverter_current_limit_arms=100.,dc_bus_min_v=400.)
    r=drive.evaluate(body_fixture(),q);m=r['model']
    assert m['motor_torque_cap_nm']==120.
    assert m['torque_output_cap_nm_each']<=900.
    assert m['maximum_speed_m_s']==pytest.approx(400*7.59*2*pi/60/7.37*.34)
    q['gear_output_power_limit_w']=20000.
    assert drive.evaluate(body_fixture(),q)['model']['mechanical_power_w']==pytest.approx(24*20000)


@pytest.mark.parametrize('change',[{'motor_torque_limit_nm':500.},{'motor_power_limit_w':117000.},
    {'inverter_current_limit_arms':500.},{'wheel_radius_m':.30},{'dc_bus_min_v':900.},
    {'gear_efficiency':1.1},{'motor_efficiency_floor':.98},{'copper_resistance_hot_multiplier':.5},
    {'grid_input_power_limit_w':float('nan')},{'gear_output_torque_limit_nm':True}])
def test_peak_stale_source_or_invalid_physical_domains_rejected(change):
    q=declared();q.update(change)
    with pytest.raises(ValueError):drive.evaluate(body_fixture(),q)


@pytest.mark.parametrize('change',[{'coolant_inlet_c':51.},{'coolant_flow_l_min_each':5.9},
    {'rotor_airflow_m3_min_each':30.},{'grid_input_power_limit_w':1000.},
    {'inverter_input_power_limit_w_each':100.}])
def test_failed_source_cooling_or_power_condition_holds_simulation(change):
    q=declared();q.update(change);r=drive.evaluate(body_fixture(),q)
    assert r['model'] is None and r['definition_holds']


def test_body_quantity_winding_source_and_ownership_mismatch_rejected():
    b=body_fixture();b['parts'][0]['quantity_per_train']=12
    with pytest.raises(ValueError,match='24 motor'):drive.evaluate(seal(b),declared())
    b=body_fixture();b['patterns'][0]['count']=12
    with pytest.raises(ValueError,match='occurrence'):drive.evaluate(seal(b),declared())
    b=body_fixture();b['parts'][-1]['quantity_per_train']=12
    with pytest.raises(ValueError,match='gear trains'):drive.evaluate(seal(b),declared())
    b=body_fixture();b['physical_definition']['hardware']['motor']['winding']='HV'
    with pytest.raises(ValueError,match='MV1UVW'):drive.evaluate(reseal_body(b),declared())
    b=body_fixture();b['source_sha256']['engineering/compact_drive/design.py']='0'*64
    with pytest.raises(ValueError,match='source epoch'):drive.evaluate(seal(b),declared())
    b=body_fixture();b['compact_drive_contract']['mass_ownership']['additional_external_drive_mass_kg']=9552.
    with pytest.raises(ValueError,match='mass ownership'):drive.evaluate(reseal_body(b),declared())


def test_phase1_missing_hardware_is_retained_as_held_without_identity_rewrite():
    b=body_fixture();b['physical_definition'].pop('hardware');reseal_body(b)
    r=drive.evaluate(b,declared())
    assert r['candidate_id']==b['candidate_id'] and r['model'] is None
    assert any(h['kind']=='missing-physical-hardware-projection' for h in r['definition_holds'])


def test_trace_rms_copper_heat_and_identity_diagnostics_are_explicit():
    r=drive.evaluate(body_fixture(),declared());m=r['model']
    force=24*120.*7.37*.9/.34
    trace=[dict(time_s=0.,speed_m_s=0.,traction_n=force),dict(time_s=10.,speed_m_s=5.,traction_n=force)]
    a=drive.audit_trace(r,trace,candidate_id=r['candidate_id'])
    assert a['motor_current_rms_a']==pytest.approx(100.)
    assert a['copper_loss_estimate_j']==pytest.approx(24*3*100**2*.00967*1.3*10.)
    assert a['wheel_work_estimate_j']==pytest.approx(force*25.)
    assert a['current_dynamics_resolved'] is False and a['repeated_duty_thermal_admission'] is False
    with pytest.raises(ValueError,match='different physical'):drive.audit_trace(r,trace,candidate_id='a'*64)
    trace[-1]['time_s']=0.
    with pytest.raises(ValueError,match='ordering'):drive.audit_trace(r,trace,candidate_id=r['candidate_id'])


def test_tampered_duty_cannot_be_exported_and_no_free_power_reservation():
    r=drive.evaluate(body_fixture(),declared());r['model']['mechanical_power_w']*=2
    with pytest.raises(ValueError,match='Sealed'):drive.native_drive(r,1000.,acknowledge_domain=drive.CONDITIONAL_DOMAIN)
    r=drive.evaluate(body_fixture(),declared());r['source_sha256']['engineering/compact_drive/design.py']='0'*64
    r.pop('evaluation_id');r['evaluation_id']=identity(r)
    with pytest.raises(ValueError,match='source epoch'):drive.native_drive(r,1000.,acknowledge_domain=drive.CONDITIONAL_DOMAIN)
    r=drive.evaluate(body_fixture(),declared());m=r['model'];q=r['declared']
    assert m['grid_power_w']+m['mandatory_auxiliary_addition_w']==pytest.approx(q['grid_input_power_limit_w'])
    assert m['motor_rms_current_cap_a']<=q['inverter_current_limit_arms']
    assert m['mandatory_auxiliary_addition_w']>=24*3*m['motor_rms_current_cap_a']**2*.00967
    assert r['current_dynamics']['thermal_rc'] is None

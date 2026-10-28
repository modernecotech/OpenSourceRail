"""Source-conditioned drive calculations never constitute operating qualification."""
from copy import deepcopy
from math import sqrt,pi
import pytest
from engineering.sourced_case import drive as d,identity,FLAGS
from engineering.reference_cell import vehicles


def cold(variant='emrax348-lv43-h300',**kwargs):
    return d.configure(variant,motor_air_C=25.,ambient_C=55.,**kwargs)


def test_current_emrax_exact_versions_do_not_mix_cover_peak_or_old_ratings():
    a=cold();b=cold('emrax268-mv-h300')
    assert a['motor']['version']=='V1.7 page3'
    assert a['motor']['continuous_torque_Nm']==360 and a['motor']['continuous_power_W']==160000
    assert a['motor']['limiting_rpm']==4500 and a['motor']['mass_kg']==43.9
    assert a['motor']['phase_R25_ohm']==.00462
    assert b['motor']['continuous_power_W']==91000 and b['motor']['mass_kg']==22.3
    assert all(a[k] is False for k in FLAGS)


def test_gear_and_voltage_caps_limit_compatible_pairs_without_using_peak_current():
    for variant in d.PAIRS:
        c=cold(variant)
        assert c['continuous_current_cap_Arms']<=c['inverter']['continuous_current_Arms']
        assert c['continuous_motor_torque_cap_Nm']*5*.97<=1200+1e-9
        assert c['motor_rpm_at20m_s']<=3000
        assert c['continuous_shaft_power_cap_W']<=c['motor']['continuous_power_W']
        assert c['continuous_shaft_power_cap_W']<=135000


def test_hot_ambient_does_not_become_valid_just_because_coolant_is_cold():
    c=d.configure(ambient_C=55.,motor_coolant_C=30.)
    assert c['source_domain_checks']['motor_coolant']
    assert not c['source_domain_checks']['motor_air'] and not c['source_domain_supported']
    controlled=cold();assert controlled['source_domain_supported']
    assert controlled['physical_definition']['conditioned_motor_plenum_required']
    assert controlled['installed_cooling_verified'] is False


def test_hot_parker_resolver_case_retains_old_source_and_missing_R_L_flow():
    c=d.configure('parker400-dpw-h300',ambient_C=55.)
    assert c['source_domain_supported'] and c['motor']['coolant_in_max_C']==65
    assert c['motor']['motor_air_max_C']==120 and c['motor']['mass_kg']==99.5
    assert c['motor']['minimum_flow_l_min'] is None
    assert d.electrical_step(c,0,100,100,0.01)['execution'].startswith('held')


@pytest.mark.parametrize('changes',[{'dc_voltage_V':120},{'roller_radius_m':.25},{'inverter_coolant_C':60},{'motor_air_C':55}])
def test_voltage_speed_and_thermal_domain_failures_are_explicit(changes):
    kwargs=dict(motor_air_C=25.);kwargs.update(changes)
    c=d.configure(**kwargs)
    assert not c['source_domain_supported']


@pytest.fixture(scope='module')
def vehicle():return vehicles.evaluate('V1')


def test_new_physical_inventory_replaces_heavy_motors_and_counts_actual_power_plant(vehicle):
    a=d.materialize(vehicle,configuration=cold())
    names={r['part_id'] for r in a['inventory']}
    assert 'ABB-M3BP355MLB6-K' not in names and 'VFD-protection-cooling-cabling' not in names
    assert a['installed_physical_motor_count']==60
    assert a['published_catalogue_mass_subtotal_kg']==pytest.approx(60*(43.9+7.5+29))
    assert 'conditioned-rotor-air-plenum-chiller-fan-filter-condensate' in names
    assert 'bank-rectifier-DC-bus-feeder-transformer-earthing-protection' in names
    assert a['complete_installed_mass_kg'] is None and a['installed_CAPEX_usd'] is None
    assert a['candidate_id']!=a['parent_prototype_candidate_id']
    assert a['evaluation_id']==identity({k:v for k,v in a.items() if k!='evaluation_id'})
    assert all(r['candidate_id']==a['candidate_id'] for r in a['inventory'])


def test_shared_motor_does_not_duplicate_opposing_face_power(vehicle):
    a=d.materialize(vehicle,configuration=cold());b=d.materialize(vehicle,configuration=cold(shared_motor=True))
    assert b['installed_physical_motor_count']*2==a['installed_physical_motor_count']
    fa=d.force_model(a)(0.,20.);fb=d.force_model(b)(0.,20.)
    assert fa['active_motor_count']==fb['active_motor_count']
    assert fb['physical_motor_count']*2==fa['physical_motor_count']
    assert fb['shaft_power_upper_W']*2==pytest.approx(fa['shaft_power_upper_W'])
    assert fb['torque_force_cap_N']*2==pytest.approx(fa['torque_force_cap_N'])
    assert b['parameters']['motor_count']==6


def test_more_banks_pairs_or_coast_banks_are_real_hardware_revisions(vehicle):
    a=d.materialize(vehicle,configuration=cold())
    b=d.materialize(vehicle,configuration=cold(),parameters={'roller_pairs_per_bank':8,'bank_starts_m':[-12.,91.,194.,297.,400.,850.]})
    assert b['installed_physical_motor_count']==96 and b['candidate_id']!=a['candidate_id']
    assert b['parameters']['bank_starts_m'][-1]==850.
    assert all(r['count']>0 for r in b['inventory'])


def test_actual_failure_indices_and_hot_domain_hold_are_not_silent_force_scaling(vehicle):
    a=d.materialize(vehicle,configuration=cold());f=d.force_model(a)
    assert f(0.,0.)['force_N'][0]>0
    assert f(0.,0.,failed_banks=[0])['force_N']==[0.,0.]
    with pytest.raises(ValueError):f(0.,0.,failed_banks=[5])
    hot=d.materialize(vehicle,ambient_C=55.)
    assert d.force_model(hot)(0.,0.)['force_N'] is None


def test_owned_model_identity_cannot_be_changed_after_configuration(vehicle):
    a=d.materialize(vehicle,configuration=cold());a['conditional_force_model']['power_per_motor_W']*=10
    with pytest.raises(ValueError):d.force_model(a)


def test_RL_current_is_dynamic_limited_and_hot_copper_loss_is_counted():
    c=cold();a=d.electrical_step(c,0,100,0,.000001);b=d.electrical_step(c,0,100,0,.1)
    assert 0<a['current_Arms']<b['current_Arms']<=c['continuous_current_cap_Arms']
    assert b['copper_loss_W']==pytest.approx(3*b['phase_R_ohm']*b['current_Arms']**2)
    assert not b['current_dynamics_validated']


def test_repeated120s_loss_account_never_calls_copper_the_entire_cooling_load():
    c=cold();s=dict(dt_s=20.,current_Arms=100.,shaft_power_W=30000.,rpm=1000.,winding_C=80.)
    r=d.duty(c,[s]);assert r['RMS_current_Arms']==pytest.approx(100/sqrt(6))
    assert r['counted_copper_heat_W']>0 and r['mean_shaft_power_W']==5000
    assert r['inverter_heat_W'] is None and r['motor_heat_upper_bound_W'] is None
    assert r['full_thermal_or_cooling_screen_passed'] is False
    with pytest.raises(ValueError):d.duty(c,[dict(s,dt_s=121.)])


def test_failed_primary_retrievals_and_parsed_representation_remain_distinguishable():
    c=d.catalogue();rows={r['id']:r for r in c['retrievals']}
    assert rows['emrax-348-v1.7']['sha256']=='9ae90016b6b1068e12497bce128d4c8aa4c1196032f8ebadcd6a5de1ff64c7f5'
    assert rows['cascadia-PM150']['retrieval']=='failed' and '404' in rows['cascadia-PM150']['reason']
    for r in c['parsed_primary_sources'].values():
        assert r['original_document_sha256'] is None and len(r['parsed_facts_sha256'])==64
    assert c['prices'] is None


def test_resealed_configuration_cannot_invent_rating_current_or_source_epoch():
    c=cold();c['continuous_motor_torque_cap_Nm']*=10
    c['evaluation_id']=identity({k:v for k,v in c.items() if k!='evaluation_id'})
    with pytest.raises(ValueError):d.electrical_step(c,0,100,0,.1)


def test_low_RMS_cannot_hide_illegal_instantaneous_peak_current():
    c=cold();s=dict(dt_s=1.,current_Arms=500.,shaft_power_W=30000.,rpm=1000.,winding_C=80.)
    r=d.duty(c,[s]);assert r['RMS_current_Arms']<c['continuous_current_cap_Arms']
    assert not r['instantaneous_continuous_current_screen_passed'] and not r['current_necessary_screen_passed']

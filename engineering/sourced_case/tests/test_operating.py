"""Real conditional V1 trajectories; no supplier sheet qualifies railway service."""
from copy import deepcopy
from functools import lru_cache
from math import fsum
import pytest
from engineering.reference_cell import vehicles
from engineering.sourced_case import equipment,coordinator as c,operating as o,drive,identity,FLAGS


@lru_cache(maxsize=1)
def prepared():
    # Scoped existing-body fixture avoids repeating unfinished structural/power
    # revisions; source substitutions and all geometry/masses are real generators.
    v=vehicles.evaluate('V1');return equipment.substitute(v,battery_parallel_strings=4)


@pytest.fixture(scope='session')
def cell():
    e=prepared();b,a,civil,limits=c.compose(e,2000.)
    return e,b,a,civil,limits


@pytest.fixture(scope='module')
def nominal(cell):return o.evaluate(cell[1],cell[2],context={'ambient_C':55.})


def energy(r):
    w=r['energy_J'];net=w['traction']-fsum(w[k] for k in ('aerodynamic','rolling','gravity','brake'))
    assert net==pytest.approx(r['kinetic_energy_J'],abs=2e-5)
    assert abs(r['discrete_work_kinetic_residual_J'])<2e-5


def first_brake(r):return next(row['front_m'] for row in r['trajectory'] if row['brake_N']>0)


def test_actual_2km_nominal_uses_source_capacity_and_reconciles_work(nominal,cell):
    assert nominal['execution']=='stopped' and nominal['conditional_numerical_arrival']
    assert nominal['final_speed_m_s']==0 and abs(nominal['stopping_error_m'])<=.5
    assert nominal['bundle_definition_id']==cell[1]['definition_id']
    assert all(row['traction_N']<=row['available_conditional_force_N']+1e-8 for row in nominal['trajectory'])
    assert all(nominal[k] is False for k in FLAGS) and not nominal['qualified_numerical_arrival']
    assert nominal['protected_occupancy_s'] is None;energy(nominal)


def test_sourced_caliper_command_is_normalized_not_old_physical_pressure(nominal):
    assert nominal['sourced_brake_model']['nominal_friction_is_guaranteed_minimum'] is False
    for row in nominal['trajectory']:
        assert 'brake_pressure_Pa' not in row
        assert 0<=row['normalized_brake_command_fraction']<=1
        assert row['actual_hydraulic_release_pressure_Pa'] is None
    hold=nominal['static_brake_hold_hypothesis']
    assert 'pressure_Pa' not in hold and hold['actual_hydraulic_release_pressure_Pa'] is None
    assert 0<=hold['normalized_brake_command_fraction']<=1


def test_downhill_governor_prevents_overspeed_without_resetting_trajectory(cell):
    _,b,a,_,_=cell
    regulated=o.evaluate(b,a,context={'ambient_C':55.,'grade_fraction':-.02})
    unregulated=o.evaluate(b,a,context={'ambient_C':55.,'grade_fraction':-.02,'speed_governor':False})
    assert regulated['maximums']['speed_m_s']<=20+1e-7
    assert any(row['governor_active'] for row in regulated['trajectory'])
    assert unregulated['maximums']['speed_m_s']>20 and unregulated['speed_cap_exceeded']
    assert not unregulated['requested_service_screen_passed']
    assert regulated['energy_J']['brake']>0
    energy(regulated);energy(unregulated)


def test_known_low_adhesion_starts_braking_earlier_than_fixed_nominal_envelope(cell,nominal):
    _,b,a,_,_=cell
    adapted=o.evaluate(b,a,context={'ambient_C':55.,'adhesion_coefficient':.025,'condition':'low-friction'})
    fixed=o.evaluate(b,a,context={'ambient_C':55.,'adhesion_coefficient':.025,'condition':'low-friction','brake_envelope_control':False})
    assert first_brake(adapted)<first_brake(nominal)
    assert adapted['conditional_numerical_arrival'] and not fixed['conditional_numerical_arrival']
    assert adapted['maximums']['brake_N']<=adapted['translating_train_mass_kg']*9.80665*.025+1e-8
    energy(adapted);energy(fixed)


def test_extra_coast_banks_are_new_hardware_and_supply_actual_grade_work(cell):
    e,b,a,_,_=cell;extra,plant,_,_=c.compose(e,2000.,distributed=True)
    failed=o.evaluate(b,a,context={'ambient_C':55.,'grade_fraction':.02})
    supplied=o.evaluate(extra,plant,context={'ambient_C':55.,'grade_fraction':.02})
    assert extra['candidate_id']!=b['candidate_id'] and plant['candidate_id']!=a['candidate_id']
    assert len(plant['parameters']['bank_starts_m'])>len(a['parameters']['bank_starts_m'])
    assert supplied['energy_J']['traction']>failed['energy_J']['traction']
    assert not failed['conditional_numerical_arrival']
    assert any(row['front_m']>600 and row['traction_N']>0 for row in supplied['trajectory'])
    energy(supplied);energy(failed)


def test_required_current_samples_obey_hardware_caps_without_becoming_actual_thermal_proof(nominal,cell):
    rating=cell[2]['drive_configuration'];duty=nominal['electrical_duty']
    assert duty['samples']
    assert all('current_Arms' not in x for x in duty['samples'])
    assert all(x['required_quasi_static_current_Arms']<=rating['continuous_current_cap_Arms']+1e-8 for x in duty['samples'])
    assert duty['full_grid_input_energy_J'] is None and not duty['actual_repeated_temperature_envelope_validated']
    assert duty['known_copper_energy_J'] is None  # Parker R/L not supplied.
    assert nominal['motor_current_A'] is None and nominal['motor_temperature_C'] is None


def test_unavailable_hot_emrax_domain_is_held_not_replaced_by_desired_force(cell):
    e,_,_,_,_=cell;b,a,_,_=c.compose(e,2000.,variant='emrax348-lv43-h300',ambient_C=55.)
    r=o.evaluate(b,a,context={'ambient_C':55.})
    assert r['execution'].startswith('held') and not r['conditional_numerical_arrival']
    assert r['trajectory']==[] and not r['admitted_operating_map']


@pytest.mark.parametrize('change',[{'definition_id':'f'*64},{'body_candidate_id':'f'*64}])
def test_mixed_or_modified_bundle_rejected(cell,change):
    _,b,a,_,_=cell;b=deepcopy(b);b.update(change)
    with pytest.raises(ValueError):o.evaluate(b,a)


def test_faulted_first_bank_has_no_initial_force_or_launch_energy(cell):
    _,b,a,_,_=cell;r=o.evaluate(b,a,context={'ambient_C':55.,'failed_banks':[0]})
    assert r['execution']=='stalled' and r['final_front_m']==0 and r['energy_J']['traction']==0
    energy(r)


def test_cold_drive_configuration_cannot_supply_unconditioned_hot_route(cell):
    e,_,_,_,_=cell;b,a,_,_=c.compose(e,2000.,variant='emrax348-lv43-h300',ambient_C=25.)
    with pytest.raises(ValueError):o.evaluate(b,a,context={'ambient_C':55.})


def test_source_R_motor_copper_is_integrated_but_total_grid_and_cooling_stay_unknown(cell):
    e,_,_,_,_=cell;b,a,_,_=c.compose(e,2000.,variant='emrax348-lv43-h300',ambient_C=25.)
    r=o.evaluate(b,a,context={'ambient_C':25.});duty=r['electrical_duty']
    copper=fsum(x['copper_loss_per_motor_W']*x['active_motors']*x['dt_s'] for x in duty['samples'])
    assert duty['known_copper_energy_J']==pytest.approx(copper,abs=1e-6) and copper>0
    assert duty['mechanical_plus_copper_input_energy_J']==pytest.approx(r['energy_J']['traction']+copper,abs=2e-5)
    assert duty['full_grid_input_energy_J'] is None and duty['rotor_iron_inverter_gear_cooling_standby_losses_unknown']
    assert not duty['actual_repeated_temperature_envelope_validated'];energy(r)


def test_placeholder_pressure_scale_does_not_change_source_nominal_caliper_force(cell,nominal):
    _,b,a,_,_=cell;b=deepcopy(b)
    b['brake_definition']['maximum_pressure_Pa_hypothesis']*=10
    b['brake_definition']['brake_definition_id']=identity({k:v for k,v in b['brake_definition'].items() if k!='brake_definition_id'})
    b['definition_id']=identity({k:v for k,v in b.items() if k!='definition_id'})
    r=o.evaluate(b,a,context={'ambient_C':55.})
    assert r['final_front_m']==pytest.approx(nominal['final_front_m'],abs=1e-6)
    assert r['journey_time_s']==pytest.approx(nominal['journey_time_s'],abs=1e-6)
    assert r['energy_J']['brake']==pytest.approx(nominal['energy_J']['brake'],abs=1e-5)
    assert r['sourced_brake_model']['nominal_train_force_N']==nominal['sourced_brake_model']['nominal_train_force_N']
    energy(r)

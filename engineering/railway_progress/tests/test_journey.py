"""Conditional station-launch mechanics; fixtures never become operating evidence."""
from copy import deepcopy
from math import fsum
import pytest
from engineering.reference_cell import vehicles,bundle as binding
from engineering.railway_progress import alternatives,journey,identity,FLAGS


@pytest.fixture(scope='module')
def cell():
    vehicle=vehicles.evaluate('V1');bundle=binding.materialize(vehicle,2000.)
    alternative=alternatives.evaluate(vehicle,bundle,kind='station-pinch-rollers',distance_m=2000.)
    bundle['progress_architecture']={'alternative_candidate_id':alternative['candidate_id']}
    bundle['definition_id']=identity({k:v for k,v in bundle.items() if k!='definition_id'})
    return vehicle,bundle,alternative


@pytest.fixture(scope='module')
def nominal(cell):
    _,bundle,alternative=cell
    return journey.evaluate(bundle,alternative)


def assert_energy(result):
    work=result['energy_J']
    expected=work['traction']-fsum(work[k] for k in ('aerodynamic','rolling','gravity','brake'))
    assert expected==pytest.approx(result['kinetic_energy_J'],abs=2e-5)
    assert abs(result['discrete_work_kinetic_residual_J'])<2e-5
    assert work['auxiliary']==pytest.approx(6*6200*result['journey_time_s'],abs=1e-5)


def test_real_discrete_work_closes_against_effective_kinetic_energy(nominal):
    assert_energy(nominal)
    assert nominal['energy_J']['traction']>nominal['energy_J']['brake']>0
    assert nominal['energy_J']['auxiliary']>0
    assert nominal['adiabatic_counted_disc_temperature_C']>50


def test_nominal_stop_reports_actual_endpoint_error_without_clamping(nominal):
    assert nominal['execution']=='stopped'
    assert nominal['conditional_numerical_arrival'] is True
    assert nominal['final_speed_m_s']==0
    assert 0<abs(nominal['stopping_error_m'])<.5
    assert nominal['final_front_m']==2000+nominal['stopping_error_m']
    assert nominal['trajectory'][-1]['front_m']==nominal['final_front_m']
    assert nominal['maximums']['acceleration_m_s2']<=.4+1e-12


def test_conditional_trajectory_never_becomes_available_map_or_safe_headway(nominal):
    assert all(nominal[k] is False for k in FLAGS)
    assert not nominal['qualified_numerical_arrival'] and not nominal['admitted_operating_map']
    assert nominal['protected_occupancy_s'] is None and not nominal['protected_headway_qualified']
    assert nominal['motor_current_A'] is None and nominal['motor_temperature_C'] is None
    assert nominal['brake_fade_or_temperature_limit_C'] is None


def test_every_sample_respects_finite_contact_and_conditional_hardware_caps(nominal,cell):
    _,b,a=cell
    for row in nominal['trajectory']:
        assert 0<=row['traction_N']<=row['available_conditional_force_N']+1e-8
        if row['front_m']>503:assert row['traction_N']==0
    for x in (0,100,200,450,700):
        for speed in (0.,5.,20.):
            caps=alternatives.force_bounds(a,x,speed)
            assert caps['force_N'][0]>=0
            assert caps['force_N'][1]<=caps['torque_force_cap_N']+1e-9
            if speed:assert caps['force_N'][1]*speed<=caps['shaft_power_upper_W']+1e-7
    assert alternatives.force_bounds(a,700.,20.)['force_N']==[0.,0.]


def test_bank_failure_removes_contact_instead_of_rescaling_whole_force(cell):
    _,b,a=cell
    live=alternatives.force_bounds(a,0.,0.)
    dead=alternatives.force_bounds(a,0.,0.,failed_banks=[0])
    assert live['active_motor_count']>0 and dead['active_motor_count']==0
    assert dead['force_N']==[0.,0.]
    r=journey.evaluate(b,a,context={'failed_banks':[0]})
    assert r['execution']=='stalled' and r['final_front_m']==0
    assert r['energy_J']['traction']==0 and not r['conditional_numerical_arrival']
    assert_energy(r)


@pytest.mark.parametrize('faults',[[5],[-1],[0,0],[True]])
def test_bank_failure_requires_exact_registered_distinct_indices(cell,faults):
    _,b,a=cell
    with pytest.raises(ValueError):journey.evaluate(b,a,context={'failed_banks':faults})


def test_power_interruption_removes_supply_without_invented_recovery(cell):
    _,b,a=cell;r=journey.evaluate(b,a,context={'power_interrupt_at_s':5.})
    assert r['execution']=='stalled' and 0<r['final_front_m']<200
    assert not r['conditional_numerical_arrival']
    assert all(row['traction_N']==0 for row in r['trajectory'] if row['time_s']>5.2)
    assert_energy(r)


def test_unpowered_gradient_necessary_energy_bound_is_not_hidden_by_speed_command(cell):
    _,b,a=cell;r=journey.evaluate(b,a,context={'grade_fraction':.04})
    # Even the full20m/s cap at500m cannot fund1500m of4%uphill potential.
    assert .5*r['effective_mass_kg']*20**2<r['translating_train_mass_kg']*9.80665*.04*1500
    assert r['execution']=='stalled' and 500<r['final_front_m']<2000
    assert not r['conditional_numerical_arrival'] and r['energy_J']['brake']==0
    assert_energy(r)


def test_emergency_stop_is_reported_as_fault_stop_not_arrival(cell):
    _,b,a=cell;r=journey.evaluate(b,a,context={'emergency_at_m':150.})
    assert r['execution']=='stopped' and 150<r['final_front_m']<500
    assert not r['conditional_numerical_arrival'] and r['energy_J']['brake']>0
    assert_energy(r)


def test_low_adhesion_overrun_is_retained_without_terminal_state_reset(cell):
    _,b,a=cell;r=journey.evaluate(b,a,context={'adhesion_coefficient':.005})
    assert r['execution']=='overrun' and r['final_front_m']>2100 and r['final_speed_m_s']>0
    assert r['maximums']['brake_N']<=r['translating_train_mass_kg']*9.80665*.005+1e-8
    assert not r['conditional_numerical_arrival']
    assert_energy(r)


def test_rotating_inertia_is_not_added_to_static_axle_weight(cell,nominal):
    _,b,a=cell
    assert nominal['counted_rotor_equivalent_mass_kg']>0
    assert nominal['effective_mass_kg']==nominal['translating_train_mass_kg']+6*b['rotating_equivalent_kg_per_car']
    assert nominal['axle_static_weight_hypothesis_N']==pytest.approx(nominal['translating_train_mass_kg']*9.80665/24)
    assert nominal['axle_route_offsets_from_leading_nose_m']==b['route_axle_offsets_from_leading_nose_m']
    assert all(0<row['offset_behind_leading_nose_m']<104.5 for row in nominal['axle_route_offsets_from_leading_nose_m'])


def test_empty_normal_crowd_share_physical_candidate_and_count_passenger_mass(cell):
    _,b,a=cell
    cases={load:journey.evaluate(b,a,context={'load':load,'maximum_s':.1}) for load in ('empty','normal','crowd-control')}
    assert len({r['candidate_id'] for r in cases.values()})==1
    assert cases['normal']['translating_train_mass_kg']-cases['empty']['translating_train_mass_kg']==pytest.approx(75*276)
    assert cases['crowd-control']['translating_train_mass_kg']-cases['empty']['translating_train_mass_kg']==pytest.approx(75*960)
    for r in cases.values():assert_energy(r)


@pytest.mark.parametrize('kind',['five-20m-LIM','onboard-rescue-research'])
def test_unavailable_force_model_is_held_instead_of_becoming_required_force(cell,kind):
    v,b,_=cell;b=deepcopy(b);a=alternatives.evaluate(v,b,kind=kind)
    b['progress_architecture']={'alternative_candidate_id':a['candidate_id']};b['definition_id']=identity({k:v for k,v in b.items() if k!='definition_id'})
    r=journey.evaluate(b,a)
    assert r['execution']=='held-no-conditional-mechanical-model'
    assert r['trajectory']==[] and not r['conditional_numerical_arrival']
    assert not r['admitted_operating_map'] and all(r[k] is False for k in FLAGS)


@pytest.mark.parametrize('changes',[{'qualified_numerical_arrival':True},{'admitted_operating_map':True},{'physical_accepted':True},{'speed_cap_m_s':21},{'grade_fraction':float('nan')}])
def test_scenario_cannot_claim_qualification_or_leave_declared_domains(cell,changes):
    _,b,a=cell
    with pytest.raises(ValueError):journey.evaluate(b,a,context=changes)


def test_scenario_identity_is_recomputed_from_owned_fields(cell):
    _,b,a=cell;r=journey.evaluate(b,a,context={'maximum_s':.1,'scenario_id':'f'*64})
    assert r['scenario']['scenario_id']!='f'*64
    assert r['evaluation_id']==identity({k:v for k,v in r.items() if k!='evaluation_id'})


def test_changed_alternative_evaluation_and_wrong_cell_are_refused(cell):
    _,b,a=cell;bad=deepcopy(a);bad['conditional_force_model']['power_per_motor_W']*=100
    with pytest.raises(ValueError):journey.evaluate(b,bad)
    bad=deepcopy(b);bad['progress_architecture']['alternative_candidate_id']='f'*64
    with pytest.raises(ValueError):journey.evaluate(bad,a)


def test_bundle_definition_is_checked_and_exact_input_provenance_retained(cell,nominal):
    _,b,a=cell;bad=deepcopy(b);bad['mass_interval_kg_per_car'][1]*=.1
    with pytest.raises(ValueError):journey.evaluate(bad,a)
    assert nominal['bundle_definition_id']==b['definition_id']
    assert nominal['source_sha256'].items()>=b['source_sha256'].items()


def test_1500m_has_separate_same_vehicle_cell_and_force_driven_endpoint(cell):
    v,old,_=cell;b=binding.materialize(v,1500.)
    a=alternatives.evaluate(v,b,kind='station-pinch-rollers',distance_m=1500.)
    b['progress_architecture']={'alternative_candidate_id':a['candidate_id']};b['definition_id']=identity({k:v for k,v in b.items() if k!='definition_id'})
    r=journey.evaluate(b,a,context={'distance_m':1500.})
    assert b['body_candidate_id']==old['body_candidate_id'] and b['candidate_id']!=old['candidate_id']
    assert r['conditional_numerical_arrival'] and abs(r['final_front_m']-1500)<.5
    assert r['qualified_numerical_arrival'] is False
    assert_energy(r)
    with pytest.raises(ValueError):journey.evaluate(b,a,context={'distance_m':2000.})


def bound_alternative(cell,parameters):
    v,b,_=cell;b=deepcopy(b)
    a=alternatives.evaluate(v,b,parameters=parameters)
    b['progress_architecture']={'alternative_candidate_id':a['candidate_id']}
    b['definition_id']=identity({k:v for k,v in b.items() if k!='definition_id'})
    return b,a


def test_mass_bound_never_selects_optimistic_contact_force_bound(cell):
    b,a=bound_alternative(cell,{'clamp_design_pressure_Pa':.5e6})
    lo=journey.evaluate(b,a,context={'mass_bound':'lower','maximum_s':.1})
    hi=journey.evaluate(b,a,context={'mass_bound':'upper','maximum_s':.1})
    optimistic=journey.evaluate(b,a,context={'mass_bound':'upper','force_bound':'upper','maximum_s':.1})
    assert lo['scenario']['force_bound']==hi['scenario']['force_bound']=='lower'
    assert lo['trajectory'][0]['available_conditional_force_N']==hi['trajectory'][0]['available_conditional_force_N']
    assert optimistic['trajectory'][0]['available_conditional_force_N']>hi['trajectory'][0]['available_conditional_force_N']
    assert lo['translating_train_mass_kg']<hi['translating_train_mass_kg']


def test_finite_contact_exit_cannot_create_work_in_next_unpowered_gap(cell):
    # One actual point-roller pair starts at the centre of a50mm leading-car
    # strip; forward contact ends after25mm, far before any followingcar strip.
    b,a=bound_alternative(cell,{'drive_strip_length_m':.05,'bank_starts_m':[-9.],
        'bank_length_m':1.,'roller_pairs_per_bank':1,'motor_count':2})
    capacity=alternatives.force_bounds(a,0.,.04)['force_N'][0]
    r=journey.evaluate(b,a,context={'dt_s':.1})
    assert r['execution']=='stalled' and .025<r['final_front_m']<1.
    assert r['energy_J']['traction']==pytest.approx(capacity*.025,abs=1e-6)
    assert r['energy_J']['brake']==0 and not r['conditional_numerical_arrival']
    assert_energy(r)


def test_substep_power_interruption_and_emergency_position_have_exact_event_boundaries(cell):
    _,b,a=cell;r=journey.evaluate(b,a,context={'power_interrupt_at_s':.05})
    force=r['effective_mass_kg']*.4+r['translating_train_mass_kg']*9.80665*.003
    # Powered motion lasts exactly50ms at0.4m/s2, not one whole100ms step.
    assert r['trajectory'][0]['time_s']==pytest.approx(.05,abs=1e-12)
    assert r['energy_J']['traction']==pytest.approx(force*.5*.4*.05**2,abs=1e-6)
    assert r['execution']=='stalled';assert_energy(r)
    emergency=journey.evaluate(b,a,context={'emergency_at_m':.001,'maximum_s':.1})
    assert emergency['trajectory'][0]['front_m']==pytest.approx(.001,abs=1e-12)
    assert_energy(emergency)


def test_stopping_endpoint_does_not_clear_unpowered_downhill_overspeed(cell):
    _,b,a=cell;r=journey.evaluate(b,a,context={'grade_fraction':-.02})
    assert r['maximums']['speed_m_s']>20.
    assert r['speed_cap_exceeded'] is True
    assert r['requested_service_screen_passed'] is False
    assert not r['qualified_numerical_arrival'] and not r['operating_release']
    assert_energy(r)

"""Independent conservation controls and adverse coupled system inputs."""
from copy import deepcopy
import math
import pytest
from engineering.assembly_design import system_design as design


def short():
    value=design.defaults();value['duration_s']=60.
    return value


def test_hierarchical_circuits_do_not_invent_equipment_or_chassis_return():
    value=design.electrical_architecture()
    assert len(value['nodes'])==6*18 and len(value['nets'])==6*16
    assert all(n['supplier_part'] is None for n in value['nodes'])
    assert all(n['cable_length_m'] is None for n in value['nets'])
    assert all(n['separate_from_signal_return'] for n in value['interfaces'] if n['type']=='protective-bond')
    broken=deepcopy(value);broken['nets'][0]['endpoints'][0]='missing'
    with pytest.raises(ValueError):design.validate_architecture(broken)
    broken=deepcopy(value);broken['nodes'].append(dict(broken['nodes'][0]))
    with pytest.raises(ValueError):design.validate_architecture(broken)


def test_complete_rc_numeric_solution_agrees_with_closed_form():
    result=design.circuit_benchmark()
    assert result['passed'] and result['maximum_voltage_error_v']<1e-7
    assert not result['ngspice_executed']


def test_coupled_energy_and_water_close_and_unknown_acceptance_stays_open():
    result=design.simulate(short())
    assert not result['failed_checks'] and result['checks']['completed_horizon']
    assert result['held_checks'] and not result['physical_release']
    assert result['representative_car_totals']['chemical_j']==pytest.approx(
        result['representative_car_totals']['terminal_j']+result['representative_car_totals']['joule_j'],abs=1e-5)
    assert result['six_identical_car_totals']['terminal_j']==pytest.approx(6*result['representative_car_totals']['terminal_j'])


def test_heat_and_moisture_independent_closed_form_unconditioned_zero_flow():
    c=short();c.update(passengers_per_car=0.,solar_w=0.,equipment_w=0.,fresh_air_kg_s=0.,door_air_kg_s=0.,
        fan_power_w=0.,cooling_capacity_w=0.)
    r=design.simulate(c)
    expected=c['ambient_c']+(c['initial_c']-c['ambient_c'])*math.exp(-c['envelope_ua_w_k']*c['duration_s']/c['thermal_capacity_j_k'])
    assert r['final']['cabin_c']==pytest.approx(expected,abs=1e-10)
    assert r['final']['humidity_kg_kg']==pytest.approx(c['initial_humidity_kg_kg'])
    assert not r['failed_checks']


def test_cooling_failure_increases_temperature_and_reduces_auxiliary_energy():
    good=design.simulate(short());failed=design.simulate(short(),fault='cooling-loss')
    assert failed['final']['cabin_c']>good['final']['cabin_c']
    assert failed['representative_car_totals']['hvac_electric_j']<good['representative_car_totals']['hvac_electric_j']


def test_battery_cooling_is_an_electrical_load_and_fault_is_separate():
    c=short();nominal=design.simulate(c);failed=design.simulate(c,fault='battery-cooling-loss')
    expected=c['battery_cooling_w']/c['battery_cooling_cop']*c['duration_s']
    assert nominal['representative_car_totals']['battery_cooling_electric_j']==pytest.approx(expected)
    assert failed['representative_car_totals']['battery_cooling_electric_j']==0.
    assert failed['final']['battery_c']>nominal['final']['battery_c']


def test_ambient_heat_control_detects_perturbed_temperature():
    step=dict(joule_heat_j=10.,active_heat_removed_j=2.,temperature_c=30.)
    args=dict(thermal_capacity_j_k=1000.,conductance_w_k=10.,ambient_c=25.)
    base=design.independent_battery_heat_residual(step,30.,1.,**args)
    changed=design.independent_battery_heat_residual(dict(step,temperature_c=31.),30.,1.,**args)
    assert changed-base==pytest.approx(-1000.)


def test_condensation_bound_preserves_nonnegative_moisture_with_simultaneous_exhaust():
    c=short();c.update(duration_s=1.,initial_humidity_kg_kg=1e-6,ambient_humidity_kg_kg=0.,passenger_latent_w=0.)
    r=design.simulate(c)
    assert r['final']['humidity_kg_kg']>=0 and not r['failed_checks']


def test_negative_sensor_bias_changes_the_cycling_response():
    c=short();c['duration_s']=1200.
    a=design.simulate(c);b=design.simulate(c,fault='sensor-bias')
    assert b['final']['cabin_c']>a['final']['cabin_c']+1.


@pytest.mark.parametrize('fault',['unlock','open-bond','communication-loss'])
def test_fault_permission_removes_traction_and_latches(fault):
    c=short();c['duration_s']=360. if fault=='communication-loss' else 60.
    r=design.simulate(c,fault=fault)
    samples=[row for row in r['trace'] if row['time_s']>300 or fault!='communication-loss']
    assert samples and all(not row['enabled'] and row['traction_w']==0 for row in samples)
    assert not r['failed_checks']


@pytest.mark.parametrize('key,value',[('car_count',3),('cop',0.),('converter_efficiency',1.1),('solar_w',float('nan')),
    ('fresh_air_kg_s',-1.),('duration_s',1e9),('battery_soc',1.1),('battery_soh',.1)])
def test_invalid_domains_fail_closed(key,value):
    c=short();c[key]=value
    with pytest.raises(ValueError):design.simulate(c)

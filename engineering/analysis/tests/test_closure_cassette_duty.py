"""Independent dynamic energy/water/CO2 and ideal protection adverse controls."""
import math

import pytest

from engineering.assembly_design import cassette_duty as d,cassette_detail,baseline,models
from engineering.twin_workflow import core


def test_electrothermal_energy_and_short_clearing_i2t():
    normal=d.electrothermal();short=d.electrothermal(fault='short')
    assert not normal['tripped'] and normal['final_temperature_c']>50.
    assert short['tripped'] and .1<short['clearing_time_s']<.101
    assert short['peak_current_a']>200.
    assert short['accumulated_overcurrent_i2t_a2s']==pytest.approx(20.)
    for report in (normal,short,d.electrothermal(fault='open'),d.electrothermal(fault='reversed')):
        assert abs(report['electrical_balance_residual_j'])<1e-8
        assert abs(report['thermal_balance_residual_j'])<1e-8
        assert not report['protection_qualified']
        assert core.encoded(report)


def test_protection_time_and_gauge_length_sensitivity_not_headline_rating():
    normal=d.electrothermal();longer=d.electrothermal(female_length_m=1.6)
    assert longer['peak_current_a']<normal['peak_current_a']
    assert longer['ledger']['loop_heat_j']>normal['ledger']['loop_heat_j']
    fast=d.electrothermal(fault='short',clearing_i2t_a2s=10.)
    slow=d.electrothermal(fault='short',clearing_i2t_a2s=40.)
    assert fast['clearing_time_s']<slow['clearing_time_s']
    assert fast['ledger']['loop_heat_j']<slow['ledger']['loop_heat_j']
    fine=d.electrothermal(fault='short',step_s=.001)
    assert fine['clearing_time_s']==pytest.approx(d.electrothermal(fault='short')['clearing_time_s'],abs=1e-8)


def test_synthetic_map_domain_and_degrading_hot_low_supply_capacity():
    cool=d.cooling_map(26.);hot=d.cooling_map(60.);low=d.cooling_map(50.,18.)
    assert cool['per_module_capacity_w']==40000.
    assert hot['per_module_capacity_w']==22000. and hot['cop']==1.8
    assert low['per_module_capacity_w']<d.cooling_map(50.)['per_module_capacity_w']
    assert cool['capacity_map_hypothesis'] and cool['supplier_source'] is None
    with pytest.raises(ValueError):d.cooling_map(65.)
    with pytest.raises(ValueError):d.cooling_map(50.,16.)


def test_empty_car_cooling_loss_matches_independent_first_order_heat_solution():
    r=d.car_transient(passengers=0,module_count=0,duration_s=10.,step_s=.1)
    q=.5+.3+1.;conductance=1.1*q*1005+250.;capacity=8e6
    equilibrium=50.+10000./conductance
    exact=equilibrium+(26.-equilibrium)*math.exp(-conductance*10/capacity)
    assert r['final_temperature_c']==pytest.approx(exact,abs=2e-6)
    assert r['final_co2_ppm']==pytest.approx(400.,abs=1e-9)
    assert abs(r['water_residual_kg'])<1e-8


def test_co2_mixing_against_independent_constant_flow_analytic_solution():
    r=d.car_transient(duration_s=10.,step_s=.1)
    q=1.8;volume=18.5*2.65*2.8;source=100*5e-6
    equilibrium=400e-6+source/q
    exact=(equilibrium+(400e-6-equilibrium)*math.exp(-q*10/volume))*1e6
    assert r['final_co2_ppm']==pytest.approx(exact,abs=.03)
    assert not r['air_quality_criterion_adopted']


def test_adverse_fan_cooling_sensor_and_hot_start_propagate_without_losing_conservation():
    base=d.car_transient()
    cases=[d.car_transient(fault='failed-fan'),d.car_transient(fault='loss-of-cooling'),d.car_transient(sensor_bias_c=-3.),d.car_transient(initial_c=50.)]
    assert cases[0]['fresh_air_m3_s']==0 and cases[0]['maximum_co2_ppm']>base['maximum_co2_ppm']
    assert cases[1]['final_temperature_c']>base['final_temperature_c']
    assert cases[2]['final_temperature_c']>base['final_temperature_c']
    assert cases[3]['final_temperature_c']>base['final_temperature_c']
    for r in cases+[base]:
        assert abs(r['sensible_energy_residual_j'])<1e-4
        assert abs(r['water_residual_kg'])<1e-8
        assert abs(r['condenser_balance_residual_j'])<1e-4
        assert not r['comfort_qualified'] and not r['refrigerant_circuit_designed']


def test_refinement_and_full_campaign_remain_held_and_bind_route_lengths():
    p=core.read(baseline.DATA);base=models.build(p,'service-cassette',{k:v[0]for k,v in p['pilots']['service-cassette']['domains'].items()})
    c=cassette_detail.build(p,base);r=d.campaign(candidate=c)
    assert r['candidate_revision']==c['revision']
    assert r['electrical'][0]['female_length_m']==pytest.approx(.9635)
    assert len(r['thermal'])==11 and len(r['electrical'])==4 and not r['failed_checks']
    assert r['held_checks']==['actual_supplier_map','physical_climate_and_fault_correlation']
    assert r['checks']['zone_time_refinement']
    assert not r['digital_specification_complete'] and core.encoded(r)
    with pytest.raises(ValueError):d.car_transient(step_s=100.)

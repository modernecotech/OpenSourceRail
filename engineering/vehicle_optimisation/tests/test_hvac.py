"""Independent HVAC heat/air units, source limits and exclusive mass accounting."""
from copy import deepcopy
from hashlib import sha256
import math

import pytest

from engineering.vehicle_optimisation import hvac


def option(key):
    return next(row for row in hvac.candidates() if row['id'] == key)


def test_ventilation_and_door_units_are_independent_of_headway():
    result = hvac.heat_load({})
    assert result['fresh_air_cabin_m3_s'] == pytest.approx(.720)
    assert result['fresh_air_cabin_m3_h'] == pytest.approx(2592.)
    assert result['door_average_outside_air_m3_s'] == pytest.approx(2*1.4*2.1*.2*30/180)
    faster = hvac.heat_load(dict(door_cycle_s=120.))
    assert faster['door_average_outside_air_m3_s'] == pytest.approx(1.5*result['door_average_outside_air_m3_s'])
    assert faster['total_kWthermal'] > result['total_kWthermal']
    assert hvac.CONTEXT['headway_s'] == 180
    assert hvac.CONTEXT['door_cycle_inferred_from_headway'] is False


def test_psychrometric_enthalpy_balance_includes_latent_fresh_air():
    result = hvac.heat_load(dict(outdoor_RH=.30))
    outside = hvac.moist_air(50., .30)
    inside = hvac.moist_air(26., .50)
    expected = result['dry_fresh_air_kg_s']*(outside['enthalpy_J_per_kg_dry']-inside['enthalpy_J_per_kg_dry'])
    actual = result['unrecovered_ventilation_sensible_W']+result['unrecovered_ventilation_latent_W']
    assert actual == pytest.approx(expected)
    assert result['unrecovered_ventilation_latent_W'] > 0
    assert result['latent_components_W']['occupants'] == 120*55
    assert result['latent_kWthermal'] > hvac.heat_load(dict(outdoor_RH=.05))['latent_kWthermal']


def test_signed_heat_conservation_survives_dry_outside_air():
    result = hvac.heat_load(dict(outdoor_RH=0., passengers=0))
    assert result['unrecovered_ventilation_latent_W'] == 0.
    reconstructed = (1000*result['total_kWthermal']-result['heating_required_W']-result['humidification_required_W'])
    assert reconstructed == pytest.approx(result['signed_net_heat_W'])
    occupied = hvac.heat_load(dict(outdoor_RH=0.))
    assert occupied['latent_components_W']['occupants'] > 0


def test_thermal_capacity_is_not_electrical_power_or_apparent_power():
    result = hvac.heat_load(dict(system_COP_scenario=2.))
    assert result['HVAC_electric_scenario_kWe'] == pytest.approx(result['total_kWthermal']/2)
    river = option('rail-river-two')
    assert river['package_capacity_kWthermal'] == [49.2, 49.2]
    assert river['package_apparent_power_kVA'] == 33.
    assert river['package_electrical_input_kWe'] is None
    assert result['complete_services_kWe'] is None


def test_people_heat_is_preserved_at_AW2_and_AW3():
    aw2 = hvac.heat_load(dict(passengers=120))
    aw3 = hvac.heat_load(dict(passengers=160))
    assert aw3['sensible_components_W']['occupants'] == 160*75
    assert aw3['latent_components_W']['occupants'] == 160*55
    assert aw3['fresh_air_cabin_m3_h'] == pytest.approx(3456.)
    assert aw3['total_kWthermal'] > aw2['total_kWthermal']
    assert aw3['comfort_qualified'] is False


def test_solar_control_changes_only_its_declared_gain_not_passenger_or_ventilation_heat():
    clear = hvac.heat_load(dict(solar_factor=.82))
    controlled = hvac.heat_load(dict(solar_factor=.55))
    assert clear['total_kWthermal']-controlled['total_kWthermal'] == pytest.approx(28*600*(.82-.55)/1000.)
    assert clear['latent_components_W'] == controlled['latent_components_W']
    assert clear['sensible_components_W']['occupants'] == controlled['sensible_components_W']['occupants']
    assert controlled['scenario']['glazing_U_W_m2K'] == 5.7


def test_recovery_cannot_recover_open_door_heat_and_hardware_is_not_free():
    ordinary = hvac.heat_load(dict(solar_factor=.55))
    recovery = hvac.heat_load(dict(solar_factor=.55, sensible_recovery_effectiveness=.6,
                                  latent_recovery_effectiveness=.4, recovery_total_pressure_Pa=200.))
    assert recovery['sensible_components_W']['doors_and_leakage'] == ordinary['sensible_components_W']['doors_and_leakage']
    assert recovery['sensible_components_W']['mechanical_fresh_air'] == pytest.approx(.4*ordinary['sensible_components_W']['mechanical_fresh_air'])
    assert recovery['recovery_fan_extra_kWe'] > 0
    assert recovery['recovery_hardware_mass_kg'] is None
    assert recovery['HVAC_electric_scenario_kWe'] == pytest.approx(recovery['total_kWthermal']/2.5+recovery['recovery_fan_extra_kWe'])


def test_demand_ventilation_sensitivity_retains_CO2_and_does_not_invent_a_legal_limit():
    full = hvac.heat_load(dict(fresh_air_L_s_per_person=6.))
    low = hvac.heat_load(dict(fresh_air_L_s_per_person=3.))
    assert low['co2_steady_mechanical_only_ppm']-420 == pytest.approx(2*(full['co2_steady_mechanical_only_ppm']-420))
    assert low['co2_after_stationary_period_ppm'] > full['co2_after_stationary_period_ppm']
    assert low['co2_legal_limit_ppm'] is None
    assert low['ventilation_compliance_established'] is False
    zero = hvac.heat_load(dict(fresh_air_L_s_per_person=0.))
    assert zero['co2_steady_mechanical_only_ppm'] is None
    assert zero['co2_after_stationary_period_ppm'] > low['co2_after_stationary_period_ppm']


def test_current_manufacturer_ranges_multiply_units_not_only_the_lightest_module():
    lrc = option('rail-lrc-two');msu = option('rail-msu-two')
    assert lrc['package_hardware_mass_range_kg_per_car'] == [830., 960.]
    assert lrc['package_capacity_kWthermal'] == [52., 70.]
    assert msu['package_hardware_mass_range_kg_per_car'] == [640., 660.]
    assert msu['package_capacity_kWthermal'] == [30., 36.]
    assert msu['published_operating_or_reduced_limit_C'] == 49.
    assert lrc['break_even_all_additional_hardware_mass_kg'][1] < 0


def test_complete_bus_compressor_package_has_real_mass_headroom_but_no_rail_or_50C_credit():
    bus = option('bus-ul700-electric-two')
    assert bus['package_hardware_mass_range_kg_per_car'] == [384., 384.]
    assert bus['break_even_all_additional_hardware_mass_kg'] == [416., 416.]
    assert bus['provisional_installed_mass_scenario_kg'] == [469., 624.]
    assert bus['complete_installed_mass_kg'] is None
    assert bus['bus_only_not_rail_qualified'] is True
    result = hvac.assess(bus, hvac.heat_load({}))
    assert result['ambient_rating_disposition'] == 'unknown-rating-domain'
    assert result['thermal_screen'] == 'unknown'
    assert result['available_capacity_band_kWthermal'] is None
    three = option('bus-ul500-electric-three')
    assert three['package_hardware_mass_range_kg_per_car'] == [486., 486.]
    assert three['package_capacity_kWthermal'] == [72., 72.]
    assert three['break_even_all_additional_hardware_mass_kg'] == [314., 314.]
    assert three['nominal_evaporator_air_m3_h'] == 3*4720.
    assert three['roof_projected_package_area_m2'] < 17.*2.65
    assert result['required_kWthermal_per_unit'] == pytest.approx(result['needed_kWthermal']/2)


def test_hot_case_refuses_outside_ambient_and_missing_derating():
    hot = hvac.heat_load(dict(outdoor_C=50., passengers=160, outdoor_RH=.30, doors_open=0))
    assert hot['total_kWthermal'] > 100
    msu = hvac.assess(option('rail-msu-two'), hot)
    assert msu['thermal_screen'] == 'fail-ambient-domain'
    lrc = hvac.assess(option('rail-lrc-one'), hot)
    assert lrc['ambient_rating_disposition'] == 'reduced-output-curve-unknown'
    assert lrc['available_capacity_band_kWthermal'][0] == 0
    assert lrc['thermal_screen'] == 'necessary-capacity-fail'
    outside = hvac.assess(option('bus-ul700-electric-two'), hvac.heat_load(dict(outdoor_C=55.)))
    assert outside['thermal_screen'] == 'fail-ambient-domain'


def test_fresh_air_and_unknown_underfloor_hardware_cannot_disappear():
    result = hvac.assess(option('rail-lrc-one'), hvac.heat_load({}))
    assert result['additional_fresh_air_treatment_needed_m3_h'] == pytest.approx(2592-1150)
    unknown = option('rail-underfloor-custom')
    assert unknown['package_hardware_mass_range_kg_per_car'] is None
    assert unknown['provisional_installed_mass_scenario_kg'] is None
    assert hvac.allocation_replacement(unknown)['mass_change_scenario_kg'] is None


def test_extra_insulation_is_counted_instead_of_becoming_free_HVAC_lightening():
    old = hvac.heat_load({});new = hvac.heat_load(dict(upper_core_m=.06))
    assert new['total_kWthermal'] < old['total_kWthermal']
    assert new['additional_upper_core_mass_scenario_kg'] > 190.
    assert new['additional_insulation_interfaces_mass_kg'] is None


def test_exact_ancestor_allocation_replacement_preserves_known_stock_and_services():
    trace = hvac.allocation_trace()
    assert trace['mass_kg'] == 800.
    assert trace['retained_residual_before_kg'] == pytest.approx(7378.253763406856)
    assert trace['retained_residual_after_single_removal_kg'] == pytest.approx(trace['retained_residual_before_kg']-800)
    assert trace['normal_total_services_kWe'] == 40.
    assert trace['normal_hvac_allocation_kWe']+trace['normal_other_services_allocation_kWe'] == 40.
    assert trace['hot_total_services_kWe'] == 60.
    assert trace['hot_hvac_split_kWe'] is None
    change = hvac.allocation_replacement(option('bus-ul700-electric-two'))
    assert change['remove_component_id'] == 'hvac'
    assert change['known_geometry_mass_removed_kg'] == 0.
    assert change['mass_change_scenario_kg'] == [-331., -176.]
    for total, delta in zip(change['combined_residual_and_replacement_scenario_kg'], change['mass_change_scenario_kg']):
        assert total == pytest.approx(trace['retained_residual_before_kg']+delta)
    assert change['other_services_battery_body_glazing_door_allocations_removed'] is False


@pytest.mark.parametrize('already', [('hvac',), ('FM-HVAC',), ('cabin_hvac_ducting',), ('doors', 'doors')])
def test_duplicate_or_aliased_hvac_removal_is_refused(already):
    with pytest.raises(ValueError, match='already removed|duplicate'):
        hvac.allocation_replacement(option('bus-ul700-electric-two'), already_removed_ids=already)


@pytest.mark.parametrize('updates', [dict(door_open_s=181.), dict(doors_open=5), dict(passengers=161),
    dict(fresh_air_L_s_per_person=-1.), dict(outdoor_RH=2.), dict(solar_factor=1.1),
    dict(door_width_m=-1.), dict(stationary_duration_s=-1.), dict(co2_generation_L_s_per_person_at_cabin=-1.),
    dict(sensible_recovery_effectiveness=.6), dict(car_mass_kg=10000.)])
def test_invalid_thermal_and_air_inputs_fail_closed(updates):
    with pytest.raises(ValueError):hvac.heat_load(updates)


def test_invalid_replacement_mass_does_not_create_negative_equipment():
    bad = deepcopy(option('bus-ul700-electric-two'))
    bad['provisional_installed_mass_scenario_kg'] = [-1., 0.]
    with pytest.raises(ValueError):hvac.allocation_replacement(bad)


def test_study_sources_and_all_acceptance_states_are_explicit():
    result = hvac.study()
    for name, expected in result['source_inputs']['local_sha256'].items():
        assert sha256((hvac.ROOT/name).read_bytes()).hexdigest() == expected
    assert len(result['comparisons']) == len(result['loads'])*len(result['candidates'])
    assert result['lighter_complete_HVAC_proven'] is False
    assert all(row['comfort_qualified'] is False for row in result['comparisons'])
    assert result['context']['normal_passengers_per_car'] == 120
    assert result['context']['maximum_passengers_per_car'] == 160
    assert result['physical_accepted'] is False

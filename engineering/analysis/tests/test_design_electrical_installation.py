"""Independent demand balances and adverse public-component incompatibilities."""

import pytest

from engineering.design_engine.electrical_installation import (
    auxiliary_power_screen,
    cooling_loss_duty,
    installation_report,
    mount_demand,
    pv_screen,
)


def test_auxiliary_converter_never_qualifies_mac_voltage_or_unknown_losses():
    report = auxiliary_power_screen(dict(nominal_voltage_v=772.8), 4)
    assert report["checks"]["direct_dc_to_ac_load"] == "failed"
    assert report["checks"]["output_voltage_tolerance"] == "unknown"
    assert report["checks"]["continuous_apparent_capacity"] == "unknown"
    assert report["voltage_difference_v"] == 15
    assert report["conditional_conversion_heat_w"] is None
    assert report["additional_equipment_mass_lower_bound_kg_per_car"] == 350
    assert report["candidate_installed"] is False
    assert report["engineering_constraints_passed"] is None


def test_five_hvac_modules_exceed_converter_even_at_unity_power_factor():
    report = auxiliary_power_screen(dict(nominal_voltage_v=772.8), 5, efficiency=.95)
    assert report["checks"]["continuous_apparent_capacity"] == "failed"
    assert report["ac_component_input_lower_bound_w"] == 27500
    assert report["conditional_conversion_heat_w"] == pytest.approx(27500*(1/.95-1))
    assert report["conditional_dc_bus_current_a"]*772.8 == pytest.approx(report["conditional_dc_input_lower_bound_w"])
    out = auxiliary_power_screen(dict(nominal_voltage_v=950), 4, ambient_c=51)
    assert out["checks"]["nominal_converter_input_voltage"] == "failed"
    assert out["checks"]["ambient_rating"] == "failed"


def test_pv_stc_independent_energy_and_mass_ledger_no_credit():
    report = pv_screen(4, 2, irradiance_w_m2=1000, cell_temperature_c=25,
                       cold_cell_temperature_c=25, duration_s=3600,
                       mppt_efficiency=.9, additional_hardware_mass_kg=12)
    assert report["conditional_module_power_w"] == 1600
    assert report["conditional_delivered_energy_j"] == 1440*3600
    assert report["conditional_installed_mass_kg"] == pytest.approx(8*4.9+12)
    assert report["vehicle_energy_credit_j"] == 0
    assert report["checks"]["battery_bus_and_mppt_compatibility"] == "unknown"
    assert report["engineering_constraints_passed"] is None


def test_pv_cold_voltage_and_area_reject_without_geometry_or_weather_credit():
    report = pv_screen(24, 1, irradiance_w_m2=1000, cell_temperature_c=85,
                       cold_cell_temperature_c=-40, duration_s=3600, exposed_area_m2=1)
    assert report["cold_open_circuit_voltage_v"] > 600
    assert report["checks"]["cold_string_insulation_voltage"] == "failed"
    assert report["checks"]["roof_area_lower_bound"] == "failed"
    assert report["checks"]["complete_roof_stack_fire"] == "unknown"
    assert report["conditional_delivered_energy_j"] is None
    shaded = pv_screen(4, 1, irradiance_w_m2=1000, cell_temperature_c=25,
                        cold_cell_temperature_c=25, duration_s=3600, shaded_fraction=1.)
    assert shaded["conditional_module_power_w"] == 0


def test_rigid_mount_independent_closed_form_weight_eccentricity_and_torsion():
    report = mount_demand(100, [(-1,-1),(-1,1),(1,-1),(1,1)],
                          cg_m=(.2,.3,.5), acceleration_m_s2=(2,3,10))
    # Force = (200,300,1000), CG cross force = (150,-100,0).
    assert report["load_moment_nm"] == pytest.approx([150,-100,0])
    assert report["mounts"][0]["reaction_n"] == pytest.approx([50,75,187.5])
    assert report["mounts"][-1]["reaction_n"] == pytest.approx([50,75,312.5])
    assert max(map(abs,report["force_balance_residual_n"])) < 1e-10
    assert max(map(abs,report["moment_balance_residual_nm"])) < 1e-10
    torsion = mount_demand(100, [(-1,-1),(-1,1),(1,-1),(1,1)],
                           cg_m=(.2,.3,.5), acceleration_m_s2=(0,3,10))
    assert torsion["load_moment_nm"][2] == pytest.approx(60)
    assert max(map(abs,torsion["moment_balance_residual_nm"])) < 1e-10
    uplift = mount_demand(100,[(-1,-1),(-1,1),(1,-1),(1,1)],cg_m=(2,0,0))
    assert any(row["retention_required"] for row in uplift["mounts"])
    assert uplift["resistance_state"] == "unknown"


@pytest.mark.parametrize("call", [
    lambda: auxiliary_power_screen(dict(nominal_voltage_v=772.8),True),
    lambda: auxiliary_power_screen(dict(nominal_voltage_v=772.8),4,efficiency=1.1),
    lambda: pv_screen(4,1,irradiance_w_m2=float("nan"),cell_temperature_c=25,cold_cell_temperature_c=0,duration_s=1),
    lambda: mount_demand(100,[(0,0),(1,1),(2,2)]),
    lambda: mount_demand(100,[(0,0),(0,0),(0,0)]),
])
def test_invalid_inputs_never_turn_into_success(call):
    with pytest.raises(ValueError):
        call()


def test_actual_subsystem_mass_and_hole_patterns_are_used_without_extra_hardware_credit():
    from engineering.design_engine.subsystems import hvac
    data = hvac(dict(hvac_modules=5,carrier_thickness_m=.005))
    report = data["installation"]
    assert report["battery_mount_demand"]["mass_kg"] == data["battery"]["properties"]["mass_kg"]
    assert len(report["battery_mount_demand"]["mounts"]) == len(data["battery"]["hole_pattern_m"])
    assert report["battery_mount_demand"]["cg_m"][2] == pytest.approx(data["battery"]["properties"]["cg_m"][2]-data["battery"]["hole_pattern_m"][0][2])
    assert len(report["hvac_mount_demands"]) == 6*5
    assert report["auxiliary_power"]["checks"]["continuous_apparent_capacity"] == "failed"
    assert report["candidate_converter_train_mass_lower_bound_kg"] == 6*350
    assert data["review"]["residual_free_hardware_prevented"] is True
    assert report["pv"]["energy_credit_j"] == 0
    battery = installation_report(data,kind="battery")
    assert "auxiliary_power" not in battery
    assert battery["battery_cooling"]["coolant_mass_kg"] is None
    assert battery["fire_interfaces"]["state"] == "unknown"


def test_adiabatic_duty_against_hand_solved_current_and_heat_balance():
    # I=10A is an exact root for P=V I-R I²=990W. With no cooling,
    # 10W resistive heat for 100s raises a 500J/K lump by exactly 2K.
    pack = dict(nominal_voltage_v=100.,resistance_ohm=.1,thermal_capacity_j_k=500.,
                capacity_ah=10.,soc_min=.1,soc_max=.9,temperature_limit_c=46.,
                discharge_current_limit_a=20.,charge_current_limit_a=20.)
    out = cooling_loss_duty(pack,[dict(duration_s=100.,terminal_power_w=900.)],
                            auxiliary_power_w=90.)
    assert out["history"][0]["current_a"] == pytest.approx(10.)
    assert out["history"][0]["temperature_c"] == pytest.approx(47.)
    assert out["history"][0]["soc"] == pytest.approx(.8-1000/36000)
    assert out["research_constraints_passed"] is False
    assert out["auxiliary_energy_j"] == 9000
    assert out["heat_removed_j"] == 0
    assert abs(out["electrical_balance_residual_j"]) < 1e-8
    assert abs(out["thermal_balance_residual_j"]) < 1e-8
    regen = cooling_loss_duty(pack,[dict(duration_s=100.,terminal_power_w=-900.)],
                              auxiliary_power_w=90.)
    assert regen["history"][0]["combined_terminal_power_w"] == -810
    assert regen["heat_generated_j"] > 0
    assert regen["history"][0]["soc"] > .8
    invalid = cooling_loss_duty(pack,[dict(duration_s=100.,terminal_power_w=25001.)])
    assert invalid["state"] == "outside-domain"
    assert invalid["engineering_constraints_passed"] is None


def test_independent_electrical_duty_matches_legacy_on_identical_finite_segments():
    from engineering.civil_exploration.automated_battery import duty_cycle, operating_budget
    pack = dict(nominal_voltage_v=100.,resistance_ohm=.1,thermal_capacity_j_k=500.,
                capacity_ah=10.,soc_min=.1,soc_max=.9,temperature_limit_c=90.,
                cooling_conductance_w_k=10.,parallel_strings=2,
                usable_energy_kwh=.8,discharge_current_limit_a=20.,charge_current_limit_a=20.)
    segments = [dict(duration_s=5.,terminal_power_w=990.),
                dict(duration_s=2.,terminal_power_w=-1010.)]
    legacy = duty_cycle(pack,segments,initial_temperature_c=45.,ambient_temperature_c=45.)
    independent = cooling_loss_duty(pack,segments)
    # The electrical branch is identical; cooled and adiabatic thermal models
    # are deliberately distinct and never treated as calibrated equivalents.
    assert independent['terminal_energy_j'] == pytest.approx(legacy['terminal_energy_j'])
    assert independent['chemical_energy_j'] == pytest.approx(legacy['chemical_energy_change_j'])
    assert independent['heat_generated_j'] == pytest.approx(legacy['heat_generated_j'])
    assert independent['history'][-1]['soc'] == pytest.approx(legacy['history'][-1]['soc'])
    assert independent['history'][-1]['temperature_c'] > legacy['history'][-1]['temperature_c']
    budget = operating_budget(pack,6,train_energy_kwh_km=3.,average_pack_power_w=990.,train_charger_power_w=6060.)
    assert budget['discharge_current_a_per_pack'] == pytest.approx(10.)
    assert budget['charge_current_a_per_pack'] == pytest.approx(-10.)
    assert budget['usable_terminal_energy_kwh'] == pytest.approx(6*.8*.99)
    assert budget['range_km'] == pytest.approx(6*.8*.99/3.)
    assert budget['full_usable_window_recharge_time_s'] == pytest.approx(6*.8*3.6e6/6000.)


def test_potential_catalogue_exact_variants_preserve_unknown_qualification():
    import json
    from pathlib import Path
    from engineering.design_engine.electrical_installation import SOURCES
    path = Path(__file__).resolve().parents[2]/'design_engine/data/potential-parts.json'
    catalogue = json.loads(path.read_text())
    indexed = {r['id']:r for r in catalogue['parts']}
    for identifier in ('abb-m40-b','renogy-rsp200db-72-g1'):
        row = indexed[identifier]
        assert row['physical_release'] is row['project_qualified'] is row['selected_supplier'] is False
        assert row['price'] is row['quotation'] is row['regional_availability'] is None
        assert catalogue['sources'][row['source_id']]['url'] == SOURCES[identifier]['url']
        for field in row['properties']:
            assert row['properties'][field] == SOURCES[identifier][field]

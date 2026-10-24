"""Independent finite-group electrical and cost invariants."""
import math
import pytest
from engineering.ferrite_maglev import launch_optimisation as l

@pytest.fixture(scope='module')
def profile():return l.reference_profile()

def test_current_profile_uses_component_reconciled_mass(profile):
    assert profile['inputs']['car_mass_kg']>28000
    assert profile['inputs']['train_mass_kg']==6*profile['inputs']['car_mass_kg']

def test_segmentation_preserves_all_copper_and_counts_converters(profile):
    a=l.loss_model(profile);b=l.loss_model(profile,groups_per_direction=14)
    expected=8400*1.5*350e-6*8960
    assert a['station_winding_copper_kg']==pytest.approx(expected)
    assert b['station_winding_copper_kg']==pytest.approx(expected)
    assert a['station_converter_count']==4 and b['station_converter_count']==28
    assert a['force_balance_residual_n']<1e-6 and b['force_balance_residual_n']<1e-6
    assert b['converter_allowance_usd']>0

def test_conductor_and_turn_scaling_not_free_current_reduction(profile):
    a=l.loss_model(profile);b=l.loss_model(profile,conductor_area_mm2=500.);c=l.loss_model(profile,turns=2)
    assert b['station_winding_copper_kg']/a['station_winding_copper_kg']==pytest.approx(500/350)
    assert b['copper_heat_kwh_per_trip']/a['copper_heat_kwh_per_trip']==pytest.approx(350/500)
    assert c['peak_current_a']/a['peak_current_a']==pytest.approx(.5)
    assert c['station_winding_copper_kg']/a['station_winding_copper_kg']==pytest.approx(2.)
    assert c['peak_phase_voltage_v']>a['peak_phase_voltage_v']

def test_voltage_limit_rejects_trajectory_instead_of_clipping(profile):
    r=l.loss_model(profile,turns=2,dc_bus_v=1800.)
    assert not r['limits']['voltage'] and not r['feasible']
    assert r['force_balance_residual_n']<1e-6
    assert r['automatic_adoption'] is False

def test_suburban_booster_has_actual_stock_and_losses():
    p=l.reference_profile('suburban');r=l.loss_model(p,groups_per_direction=7)
    assert r['booster_converter_count']>0 and r['booster_copper_kg']>0
    assert r['winding_copper_kg']==pytest.approx(r['station_winding_copper_kg']+r['booster_copper_kg'])
    assert r['copper_heat_kwh_per_trip']>r['terminal_copper_heat_kwh_per_trip']
    assert r['station_installed_allowance_usd'] is None

def test_lifecycle_does_not_omit_maintenance_renewal_idle(profile):
    r=l.loss_model(profile);s=r['lifecycle']
    assert s['annual_maintenance_allowance_usd']>0 and s['converter_renewal_present_usd']>0
    idle=s['idle_accounting']
    assert idle['full_year_station_idle_kwh']>0
    assert idle['idle_already_inside_trip_dc_kwh']+idle['annual_idle_reconciliation_kwh']==pytest.approx(idle['full_year_station_idle_kwh'])
    assert s['installed_lifetime_cost_usd']>r['all_profile_assets_allowance_usd']
    assert not r['cost_is_quote'] and not r['qualified']

def test_actual_duty_idle_accounting_subtracts_trip_component_once():
    r=l.idle_control_energy(physical_station_groups=14,annual_mainline_legs=10000,runtime_s=140,stations=4)
    assert r['full_year_station_idle_kwh']==pytest.approx(4*14*35*8760/1000)
    assert r['idle_already_inside_trip_dc_kwh']==pytest.approx(10000*140*14*35/3.6e6)
    assert r['additional_idle_kwh']+r['idle_already_inside_trip_dc_kwh']==pytest.approx(r['full_year_station_idle_kwh'])

def test_overlapping_trip_allocations_are_replaced_by_one_calendar_load(profile):
    r=l.idle_control_energy(physical_station_groups=14,annual_mainline_legs=100000,runtime_s=400)
    assert r['included_idle_exceeds_calendar_budget']
    assert r['additional_idle_kwh']==0
    assert r['duplicated_trip_idle_credit_kwh']>0
    assert r['idle_already_inside_trip_dc_kwh']+r['annual_idle_reconciliation_kwh']==pytest.approx(14*35*8760/1000)
    value=l.loss_model(profile,groups_per_direction=7);account=value['lifecycle']['idle_accounting']
    assert account['installed_groups']==14
    assert account['idle_already_inside_trip_dc_kwh']+account['annual_idle_reconciliation_kwh']==pytest.approx(account['full_year_station_idle_kwh'])
    annual=value['lifecycle']['reference_annual_train_passages']
    expected=(annual*value['net_grid_kwh_at_assumed_reuse']+account['annual_idle_reconciliation_kwh'])*l.load()['electricity_usd_per_kwh']
    assert value['lifecycle']['annual_energy_allowance_usd']==pytest.approx(expected)

def test_booster_installed_stock_and_trip_allocation_have_distinct_counts():
    value=l.loss_model(l.reference_profile('suburban'),groups_per_direction=7)
    r=value['lifecycle']['idle_accounting']
    assert r['installed_groups']==value['station_converter_count']+2*value['booster_converter_count']
    assert r['groups_inside_each_trip']==value['powered_groups']

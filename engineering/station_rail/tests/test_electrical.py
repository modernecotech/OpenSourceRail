import pytest
from engineering.station_rail import electrical as e
from engineering.station_rail import operations as op


def test_module_mass_contains_cells_once_and_current_is_voltage_bound():
    b=e.battery_definition()
    assert b['module_count']==75
    assert b['gross_energy_kWh']==pytest.approx(82.8)
    assert b['mass_kg']==1345
    assert b['cell_mass_kg']<b['supplier_module_mass_kg']
    assert b['conservative_voltage_current_power_kW']==216
    assert b['catalogue_voltage_range_V']==[450,810]
    assert b['supplier_railway_approval'] is False


def test_battery_power_limiting_is_not_nominal_voltage_shortcut():
    low=e.charge_leg(140,parallel_strings=2)
    default=e.charge_leg(140,parallel_strings=3)
    assert low['catalogue_low_voltage_current_capped_charge_kW_per_car']==144
    assert low['energy_balance_screen']=='fail'
    assert default['energy_balance_screen']=='pass'
    assert default['actual_charge_power_available'] is None


def test_hot_hotel_and_catalogue_ambient_failures_not_hidden():
    result=e.charge_leg(180,hotel_kW=50,module_environment_C=50)
    assert result['energy_deficit_kWh_per_car']>0
    assert result['minimum_extra_terminal_charge_s_per_leg']>0
    assert result['ambient_catalogue_screen']=='fail'


def test_route_soc_does_not_recharge_above_maximum_or_ignore_floor():
    okay=e.state_of_charge([120]*40)
    assert okay['final_SOC']<=.9
    deficit=e.state_of_charge([500]*20,hotel_kW=50)
    assert deficit['reserve_screen']=='fail'
    assert deficit['minimum_terminal_extra_charge_s']>0


def test_lim_secondary_slip_heat_is_positive_and_increases():
    p=op.profile(2000,23000)
    small=e.secondary_heat(p,58.536,slip=.02)
    large=e.secondary_heat(p,58.536,slip=.25)
    assert large['adiabatic_temperature_rise_K']>small['adiabatic_temperature_rise_K']>0
    assert large['actual_secondary_temperature_C'] is None
    assert large['thermal_screen']=='unknown'


def test_spreader_does_not_establish_instantaneous_active_plate_temperature():
    p=op.profile(2000,23000)
    all_stock=e.secondary_heat(p,207.067,slip=.25)
    plate=e.secondary_heat(p,58.536,slip=.25)
    assert plate['adiabatic_temperature_rise_K']>3*all_stock['adiabatic_temperature_rise_K']
    assert all_stock['contact_conductance_W_K'] is None


def test_failed_charger_can_violate_reserve_during_dwell():
    from engineering.station_rail.electrical import state_of_charge
    result=state_of_charge([0.],initial_SOC=.21,hotel_kW=50.,charging_power_kW=0.,dwell_s=100.)
    assert result['reserve_screen']=='fail'
    assert result['legs'][0]['dwell_floor_violated']
    assert not result['legs'][0]['arrival_floor_violated']
    assert result['lowest_SOC']==result['final_SOC']

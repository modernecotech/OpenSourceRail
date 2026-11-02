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


def test_charge_acceptance_and_independent_dwell_supply_are_explicit():
    reference=e.charge_leg(147.361774,hotel_kW=50.,charging_power_kW=200.,
        parallel_strings=3,charge_acceptance_fraction=1.)
    restricted=e.charge_leg(147.361774,hotel_kW=50.,charging_power_kW=200.,
        parallel_strings=3,charge_acceptance_fraction=.5)
    direct=e.charge_leg(147.361774,hotel_kW=50.,charging_power_kW=200.,
        parallel_strings=3,independent_dwell_supply_kW_per_car=50.)
    assert reference['catalogue_low_voltage_current_limit_kW_per_car']==216.
    assert restricted['catalogue_low_voltage_current_capped_charge_kW_per_car']==108.
    assert restricted['energy_deficit_kWh_per_car']>reference['energy_deficit_kWh_per_car']
    assert direct['dwell_hotel_energy_from_independent_supply_kWh_per_car']==pytest.approx(50*35/3600)
    assert direct['energy_deficit_kWh_per_car']==pytest.approx(
        reference['energy_deficit_kWh_per_car']-50*35/3600)
    assert direct['energy_balance_screen']=='fail'
    assert direct['actual_charge_power_available'] is None
    with pytest.raises(ValueError,match='acceptance'):
        e.charge_leg(100,charge_acceptance_fraction=1.1)


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


def test_route_soc_can_compare_charge_acceptance_and_direct_dwell_source():
    baseline=e.state_of_charge([147.361774]*10,hotel_kW=50.,charging_power_kW=200.)
    accepted=e.state_of_charge([147.361774]*10,hotel_kW=50.,charging_power_kW=200.,
        charge_acceptance_fraction=.5)
    fed=e.state_of_charge([147.361774]*10,hotel_kW=50.,charging_power_kW=200.,
        independent_dwell_supply_kW_per_car=50.)
    assert accepted['final_SOC']<baseline['final_SOC']
    assert fed['final_SOC']>baseline['final_SOC']


@pytest.mark.parametrize(
    'strings,charger,acceptance,hotel,feed,expected_charge,expected_seconds',
    [
        # 144 kW catalogue limit, acceptance-limited to 72 kW.
        (2, 200., .5, 50., 0., 72., 18000. / (68.4 - 50.)),
        # 144 kW catalogue limit, charger-limited to 40 kW.
        (2, 40., .5, 50., 50., 40., 18000. / 38.),
        # 216 kW catalogue limit, acceptance-limited to 108 kW.
        (3, 200., .5, 50., 0., 108., 18000. / (102.6 - 50.)),
        # 216 kW catalogue limit, charger-limited to 100 kW.
        (3, 100., .5, 50., 0., 100., 18000. / 45.),
        # An independent dwell feed supplies hotel load during replenishment.
        (3, 200., .5, 50., 50., 108., 18000. / 102.6),
    ],
)
def test_terminal_charge_uses_same_independent_power_limits(
        strings, charger, acceptance, hotel, feed, expected_charge, expected_seconds):
    # The 360-second trip consumes exactly 5 kWh at 50 kW; zero dwell
    # isolates terminal replenishment from charging during the trip.
    result=e.state_of_charge([360.], parallel_strings=strings, hotel_kW=hotel,
        charging_power_kW=charger, charge_acceptance_fraction=acceptance,
        independent_dwell_supply_kW_per_car=feed, dwell_s=0.)
    assert result['terminal_replenishment_energy_kWh_per_car']==pytest.approx(5.)
    assert result['legs'][0]['balance']['catalogue_low_voltage_current_capped_charge_kW_per_car']==expected_charge
    assert result['minimum_terminal_extra_charge_s']==pytest.approx(expected_seconds)


@pytest.mark.parametrize('charger,acceptance,hotel,efficiency', [
    (0., 1., 50., .95),
    (100., 0., 50., .95),
    (100., 1., 100., 1.),
])
def test_terminal_charge_reports_no_positive_net_rate(charger, acceptance, hotel, efficiency):
    result=e.state_of_charge([360.], hotel_kW=hotel, charging_power_kW=charger,
        charge_acceptance_fraction=acceptance, efficiency=efficiency, dwell_s=0.)
    assert result['terminal_replenishment_energy_kWh_per_car']>0
    assert result['minimum_terminal_extra_charge_s'] is None


def test_terminal_charge_needs_no_extra_time_without_shortfall():
    result=e.state_of_charge([], charging_power_kW=0.)
    assert result['terminal_replenishment_energy_kWh_per_car']==0.
    assert result['minimum_terminal_extra_charge_s']==0.


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

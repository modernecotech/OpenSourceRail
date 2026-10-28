from copy import deepcopy
from pathlib import Path
import pytest
from engineering.reference_cell import vehicles
from engineering.sourced_case import equipment,commerce as c
ROOT=Path(__file__).resolve().parents[3]
@pytest.fixture(scope='module')
def equipped():return equipment.substitute(vehicles.evaluate('V1',root=ROOT),root=ROOT)


def test_source_has_real_converter_and_public_B_prices():
    x=c.catalogue(ROOT);ep=next(p for p in x['products'] if p['key']=='epc5k5648i')
    assert ep['mass_kg']==8.95 and ep['facts']['ambient_range_C']==[-10,40]
    assert ep['dimensions_m']==[.211,.159,.5009]
    for p in x['prices']:assert p['source_class']=='B' and not p['actual_quote']
    assert all(len(s['sha256'])==64 for s in x['sources'].values())


def test_boost_voltage_current_and_mass_are_counted(equipped):
    p=c.power_case(equipped,root=ROOT)
    assert p['voltage_within_published_domain']
    assert p['EPC_catalogue_mass_per_car_kg']==pytest.approx(26.85)
    assert len(p['removed_occurrence_ids'])==6
    assert len(p['occurrences'])==6*(3+7)
    assert p['HV_available_bounds_per_car_W'][0]>=10800
    assert p['LV_available_per_car_W']==7*266
    assert p['converter_electrical_necessary_screen']=='conditional-pass'
    assert p['conditioned_enclosure_mass_kg'] is None
    assert p['complete_installed_mass_kg'] is None
    assert all(p[k] is False for k in c.FLAGS)


def test_two_units_do_not_supply_peak_across_low_voltage(equipped):
    p=c.power_case(equipped,converter_units=2,root=ROOT)
    assert p['HV_available_bounds_per_car_W'][0]<p['HV_required_per_car_W']
    assert p['converter_electrical_necessary_screen']=='fail-or-held'


def test_hot_ambient_cannot_use_40C_factory_rating(equipped):
    p=c.power_case(equipped,converter_air_C=50.,root=ROOT)
    assert not p['air_temperature_within_published_domain']
    assert p['HV_available_bounds_per_car_W']==[None,None]
    assert p['converter_electrical_necessary_screen']=='fail-or-held'


def test_efficiency_revision_evaluation_only_and_inventory_physical(equipped):
    a=c.power_case(equipped,root=ROOT)
    b=c.power_case(equipped,efficiency_bounds=(.92,.97),root=ROOT)
    d=c.power_case(equipped,converter_units=4,root=ROOT)
    assert a['physical_definition_id']==b['physical_definition_id']
    assert a['evaluation_id']!=b['evaluation_id']
    assert a['physical_definition_id']!=d['physical_definition_id']
    with pytest.raises(ValueError):c.power_case(equipped,efficiency_bounds=(.90,.99),root=ROOT)


def test_price_scope_and_unknowns_not_quote(equipped):
    cid=equipped['candidate_id'];records=[dict(candidate_id=cid,SKU='BAT524120620',occurrence_ids=['pack1','pack2','pack3','pack4']),dict(candidate_id=cid,SKU='EPC5k5648i',occurrence_ids=['boost1'])]
    p=c.price_subtotal(cid,records,ROOT)
    assert p['known_list_price_subtotal_USD']==4*2038
    assert p['listed_scope_total_USD'] is None
    assert p['complete_installed_total_USD'] is None
    assert p['actual_quotation_coverage']==0
    assert p['rows'][1]['unit_price_USD'] is None


def test_price_overlap_and_mixed_candidate_rejected(equipped):
    cid=equipped['candidate_id'];a=dict(candidate_id=cid,SKU='ORI482441110',occurrence_ids=['same'])
    with pytest.raises(ValueError):c.price_subtotal(cid,[a,a],ROOT)
    bad=deepcopy(a);bad['candidate_id']='0'*64
    with pytest.raises(ValueError):c.price_subtotal(cid,[bad],ROOT)


def test_directLV_HVAC_cannot_claim_desert_capacity():
    p=c.citysphere_case(33000,root=ROOT)
    assert p['units_per_car']==9 and p['catalogue_mass_kg']==405
    assert p['available_at_selected_ambient_W'] is None
    assert p['hot_climate_screen']=='held-no-rated-hot-capacity'


def test_station_charge_conservation_and_failure(equipped):
    p=c.charge_budget(equipped,13000.,120.,35.)
    assert p['required_battery_replenishment_Wh']==pytest.approx(13000*155/3600)
    assert p['required_mean_battery_charge_W']==pytest.approx(13000*155/35)
    assert p['required_mean_battery_charge_W']>p['nominal_upper_battery_charge_power_W']
    assert p['necessary_charge_screen']=='fail-power-bound'
    assert p['charger_installed_mass_kg'] is None


def test_tampered_equipment_rejected(equipped):
    bad=deepcopy(equipped);bad['candidate_id']='0'*64
    with pytest.raises(ValueError):c.power_case(bad,root=ROOT)
    with pytest.raises(ValueError):c.power_case(equipped,converter_units=0,root=ROOT)


def test_recommended_charge_and_BMS_limit_are_separate(equipped):
    p=c.charge_budget(equipped,2000.,120.,35.,bms_current_A=200.)
    assert p['source_max_charge_current_A']==400
    assert p['manufacturer_recommended_charge_current_A']==200
    assert p['current_limit_after_BMS_hypothesis_A']==200
    assert p['nominal_upper_battery_charge_power_W']==pytest.approx(56.8*200)
    assert not p['installed_BMS_current_validated']
    with pytest.raises(ValueError):c.charge_budget(equipped,2000.,120.,bms_current_A=-1)

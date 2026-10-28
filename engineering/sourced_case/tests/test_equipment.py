"""Catalogue/quantity/physical-domain checks; these do not qualify hardware."""
from copy import deepcopy
from pathlib import Path
import pytest
from engineering.reference_cell import vehicles
from engineering.component_registry import validate_registry
from engineering.sourced_case import equipment as e

ROOT=Path(__file__).resolve().parents[3]
@pytest.fixture(scope='module')
def vehicle():return vehicles.evaluate('V1',root=ROOT)
@pytest.fixture(scope='module')
def one(vehicle):return e.substitute(vehicle,root=ROOT)
@pytest.fixture(scope='module')
def two(vehicle):return e.substitute(vehicle,root=ROOT,hvac_units_per_car=2)


def reseal(v):
    v.pop('evaluation_id',None);v['evaluation_id']=e.identity(v);return v


def test_five_actual_configurations_and_exact_source_hashes():
    c=e.catalogue(ROOT);assert len(c['products'])>=5
    for p in c['products']:
        source=c['sources'][p['source']]
        assert len(source['sha256'])==64 and source['bytes']>1000
        assert source['source_class']=='B' and source['actual_supplier_quote'] is False
    assert all(c[k] is False for k in e.FLAGS)


def test_actual_substitutions_new_physical_identity_and_count(vehicle,one):
    assert one['candidate_id']!=vehicle['candidate_id']
    assert one['vehicle']['registry']['parent_candidate_id']==vehicle['candidate_id']
    assert one['counts']=={'independent-brake-caliper':48,'HVAC-roof-unit':6,'auxiliary-battery-with-BMS':24,'auxiliary-DC-converter':6}
    validate_registry(one['vehicle']['registry'])
    assert len(one['replacements'])==48+6+6+6
    assert one['dependency_invalidation']['physical_revision']
    assert one['summary']['price_upper_bound_usd'] is None
    assert one['vehicle']['per_car_mass_properties']['installed_CG_m'] is None
    assert one['vehicle']['per_car_mass_properties']['mass_upper_bound_kg']<vehicle['per_car_mass_properties']['mass_upper_bound_kg']


def test_mass_sum_and_cg_bounds_reconciled(one):
    r=one['vehicle']['registry'];parts={p['physical_definition_id']:p for p in r['parts']}
    lo=sum(parts[o['part_definition_id']]['mass']['lower_bound_kg'] for o in r['occurrences'])
    hi=sum(parts[o['part_definition_id']]['mass']['upper_bound_kg'] for o in r['occurrences'])
    assert one['summary']['mass_lower_bound_kg']==pytest.approx(lo)
    assert one['summary']['mass_upper_bound_kg']==pytest.approx(hi)
    for axis in one['vehicle']['train_mass_properties']['all_item_CG_bounds_m']:assert axis[0]<axis[1]


def test_no_pad_double_charge_and_bracket_package_count(one):
    assert one['pad_accounting']['removed_old_pad_occurrences']==48
    assert not any('-BRAKE-PAD-PAIR-' in p['part_id'] for p in one['vehicle']['registry']['parts'])
    assert sum('CALIPER-BRACKET-RETENTION' in p['part_id'] for p in one['vehicle']['registry']['parts'])==1
    assert one['known_installation_scope']['bracket_allowances']==48
    assert 'pending' in one['pad_accounting']['treatment']


def test_brake_torque_uses_published_lever_rule_not_wheelradius(one):
    c=e.constraints(one)
    assert c['brake']['nominal_torque_per_disc_Nm']==pytest.approx(1120)
    assert c['brake']['nominal_train_force_before_adhesion_N']==pytest.approx(168000)
    assert c['brake']['conditional_force_upper_N']<168000
    assert c['brake']['hot_wet_mu_map'] is None
    assert c['brake']['adiabatic_all_energy_to_disc_rise_K'] is None
    assert c['brake']['operating_map_admitted'] is False


def test_published_force_ambiguity_stays_unknown(vehicle):
    s=e.substitute(vehicle,{'independent-brake-caliper':'knorr-hsc1p10n'},root=ROOT)
    c=e.constraints(s);assert c['brake']['nominal_train_force_before_adhesion_N'] is None
    assert c['brake']['nominal_torque_per_disc_Nm'] is None


def test_single_vs_double_HVAC_hardware_and_electrical_held(one,two):
    a=e.constraints(one);b=e.constraints(two)
    assert one['candidate_id']!=two['candidate_id']
    assert a['HVAC']['per_car_peak_electrical_W']==12620
    assert b['HVAC']['per_car_peak_electrical_W']==25240
    assert a['HVAC']['cooling_available_at_selected_ambient_W'] is None
    assert a['HVAC']['cooling_capacity_unit_conflict']
    assert b['electrical']['peak_HVAC_only_deficit_W']==7320
    assert b['electrical']['LV_fan_only_deficit_W']==3374
    assert a['electrical']['LV_converter_per_car_capacity_W']==266
    assert not a['electrical']['HVAC600V_converter_available']
    assert not a['electrical']['fan_voltage_compatibility_qualified']


def test_module_count_and_mass_propagate(vehicle,one):
    s=e.substitute(vehicle,root=ROOT,battery_parallel_strings=4)
    assert s['candidate_id']!=one['candidate_id']
    assert s['counts']['auxiliary-battery-with-BMS']==48
    assert e.constraints(s)['electrical']['nominal_per_car_energy_Wh']==40960
    assert s['vehicle']['per_car_mass_properties']['mass_lower_bound_kg']>one['vehicle']['per_car_mass_properties']['mass_lower_bound_kg']
    assert s['architecture']['battery_new_cradle_required']


def test_property_correction_invalidates_evaluation_not_physical(vehicle,one):
    c=e.catalogue(ROOT)
    p=next(p for p in c['products'] if p['key']=='victron-ng256-200')
    p['mass_typical_kg']=38
    p.pop('product_evaluation_id');p['product_evaluation_id']=e.identity(p);reseal(c)
    changed=e.substitute(vehicle,root=ROOT,catalogue_override=c)
    assert changed['candidate_id']==one['candidate_id']
    assert changed['evaluation_id']!=one['evaluation_id']
    assert changed['summary']['mass_upper_bound_kg']>one['summary']['mass_upper_bound_kg']


def test_no_temperature_or_adhesion_extrapolation(one):
    c=e.constraints(one,ambient_C=56)
    assert c['electrical']['LV_converter_per_car_capacity_W'] is None
    assert not c['electrical']['discharge_temperature_in_range']
    assert not c['HVAC']['application_ambient_in_published_range']
    with pytest.raises(ValueError):e.constraints(one,adhesion=1.1)
    with pytest.raises(ValueError):e.constraints(one,speed_m_s=-1)


def test_tamper_and_wrong_function_rejected(vehicle,one):
    bad=deepcopy(one);bad['candidate_id']='0'*64
    with pytest.raises(ValueError):e.constraints(bad)
    with pytest.raises(ValueError):e.substitute(vehicle,{'HVAC-roof-unit':'svendborg-bsfi208'},root=ROOT)
    with pytest.raises(ValueError):e.substitute(vehicle,root=ROOT,hvac_units_per_car=0)
    bad=deepcopy(vehicle);bad['candidate_id']='0'*64;reseal(bad)
    with pytest.raises(ValueError):e.substitute(bad,root=ROOT)


def test_thermal_bound_is_conditional_and_not_120s_per_vehicle_duty(one):
    c=e.constraints(one,disc_specific_heat_J_kgK=500)
    assert c['brake']['adiabatic_all_energy_to_disc_rise_K']>0
    assert c['brake']['each_train_brake_repetition_period_s'] is None
    assert c['brake']['rotational_and_gradient_energy_J'] is None
    assert all(c[k] is False for k in e.FLAGS)


def test_method_probe_keeps_experimental_configuration_separate():
    p=e.friction_method_probe(ROOT)
    assert .38<p['fitted_equation_mu']<.48
    assert p['explicit_prose_corrected_mu']==pytest.approx(.98*p['fitted_equation_mu'])
    assert p['independently_reproduced_raw_measurement_error'] is None
    assert p['can_supply_OSR_operating_brake_map'] is False


def test_revised_service_paths_sized_and_held(one):
    paths=one['vehicle']['assembly_access'];assert paths
    for p in paths:
        assert len(p['start_transform'])==4 and len(p['end_transform'])==4
        assert p['envelope_dimensions_m'] and p['lifting_capacity_required_kg_lower']>0
        assert not p['continuous_clearance_proved'] and not p['installation_accepted']


def test_friction_case_convention_and_extrapolation_are_explicit():
    a=e.friction_case(9.6,50.,'paper-Td-temperature-rise',root=ROOT)
    b=e.friction_case(9.6,50.,'figure-surface-temperature',apply_prose_c=True,root=ROOT)
    assert b['evaluated_mu']==pytest.approx(.98*a['evaluated_mu'])
    assert a['actual_complete_empirical_domain'] is None
    assert a['evaluation_id']!=b['evaluation_id']
    c=e.friction_case(15.,100.,'paper-Td-temperature-rise',root=ROOT)
    assert c['extrapolation_beyond_documented_slice']
    with pytest.raises(ValueError):e.friction_case(9.6,50.,'automatically-inferred',root=ROOT)

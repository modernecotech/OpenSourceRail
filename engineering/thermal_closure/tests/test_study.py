"""Independent heat/circuit balances and evidence-admission regression cases."""
from copy import deepcopy
import json
import math

import pytest
from scipy.integrate import solve_ivp

from engineering.vehicle_optimisation import hvac
from engineering.thermal_closure import study as s


def test_linear_RL_step_matches_independent_ODE_and_signed_energy_conservation():
    p=dict(initial_A=-15.,voltage_V=48.,resistance_ohm=1.55,inductance_H=.012,duration_s=.010)
    result=s.linear_rl_step(**p)
    integrated=solve_ivp(lambda t,y:[(48.-1.55*y[0])/.012,48.*y[0],1.55*y[0]**2],
        [0.,.010],[-15.,0.,0.],rtol=1e-10,atol=1e-11)
    assert result['final_A']==pytest.approx(integrated.y[0,-1],rel=1e-9)
    assert result['net_electrical_input_J']==pytest.approx(integrated.y[1,-1],rel=1e-9)
    assert result['copper_heat_J']==pytest.approx(integrated.y[2,-1],rel=1e-9)
    assert abs(result['energy_residual_J'])<1e-11
    assert result['actual_current_control_or_voltage_qualified'] is False
    assert result['exits_retained_field_current_domain'] is True
    assert result['current_limiting_modelled'] is False
    assert result['force_credit_from_RL_diagnostic'] is False
    # Initially opposing I/V returns electrical energy rather than consuming it.
    short=s.linear_rl_step(**(p|dict(duration_s=.0001)))
    assert short['net_electrical_input_J']<0<short['copper_heat_J']


def test_adiabatic_temperature_matches_independent_temperature_dependent_resistance_ODE():
    p=dict(initial_C=50.,current_A=15.,R20_ohm=1.2543,alpha_per_K=.00393,capacity_J_K=4015.,duration_s=300.)
    r=s.adiabatic_copper(**p)
    result=solve_ivp(lambda t,y:[15**2*1.2543*(1+.00393*(y[0]-20))/4015.],
        [0.,300.],[50.],rtol=1e-11,atol=1e-11)
    assert r['final_C']==pytest.approx(result.y[0,-1],rel=1e-10)
    assert r['copper_heat_and_stored_J']==pytest.approx(4015.*(r['final_C']-50.))
    assert r['rejected_heat_J']==0.
    assert r['installed_temperature_prediction'] is False
    zero=s.adiabatic_copper(**(p|dict(current_A=0.)))
    assert zero['final_C']==pytest.approx(50.)


def test_initially_empty_inductor_tiny_step_retains_positive_cubic_heat():
    R,L,V,dt=1.55,.012,48.,1e-12
    result=s.linear_rl_step(initial_A=0.,voltage_V=V,resistance_ohm=R,inductance_H=L,duration_s=dt)
    assert result['final_A']==pytest.approx(V*dt/L,rel=1e-9)
    assert result['copper_heat_J']==pytest.approx(R*(V/L)**2*dt**3/3,rel=1e-9,abs=0.)


@pytest.mark.parametrize('changes',[dict(inductance_H=0.),dict(resistance_ohm=True),dict(duration_s=-1.),dict(voltage_V=float('nan'))])
def test_invalid_circuit_parameters_are_refused(changes):
    with pytest.raises(ValueError):s.linear_rl_step(**(dict(initial_A=0.,voltage_V=48.,resistance_ohm=1.,inductance_H=.01,duration_s=.01)|changes))


def test_reflective_roof_changes_hot_core_screen_and_more_insulation_is_not_core_cooling():
    dark=hvac.heat_load(hvac.default_scenario(outdoor_C=50.,roof_absorptivity=.5))
    light=hvac.heat_load(hvac.default_scenario(outdoor_C=50.,roof_absorptivity=.2))
    black=s.roof_core_screen(dark);white=s.roof_core_screen(light)
    assert black['necessary_temperature_screen']=='fail' and black['outer_core_face_C']>70
    assert white['necessary_temperature_screen']=='pass' and white['outer_core_face_C']<70
    # Independent resistance network: sol-air -> outer film ->2mm skin ->core.
    U=1/(.17+.004/.3+.04/.031)
    expected=80.-U*(80.-26.)*(1/15.+.002/.3)
    assert black['outer_core_face_C']==pytest.approx(expected)
    thicker=s.roof_core_screen(hvac.heat_load(hvac.default_scenario(upper_core_m=.06)))
    assert thicker['outer_core_face_C']>black['outer_core_face_C']
    assert black['heat_distortion_temperature_used_as_continuous_allowable'] is False


def test_extra_core_density_interval_closes_to_thermal_envelope_without_free_interfaces():
    features=s.passive_options()
    assert len(features)==16 and len({f['thermal_feature_id'] for f in features})==16
    added=next(f for f in features if f['upper_core_m']==.06 and f['glazing_solar_factor']==.82 and f['roof_absorptivity']==.5 and not f['recovery'])
    material=added['stock_additions'][0]
    expected_volume=.02*(17*2.65+2*17*2.8+2*2.65*2.8-4*1.4*2.1-24.)
    assert material['volume_m3']==pytest.approx(expected_volume)
    assert material['material_mass_range_kg']==pytest.approx([expected_volume*67,expected_volume*87])
    assert material['bonds_edges_fire_layers_cut_waste_and_interfaces_mass_kg'] is None
    assert added['complete_additional_installed_mass_kg'] is None


def test_package_auxiliary_input_is_not_compressor_real_power_and_N_minus_one_keeps_hardware():
    package=next(p for p in s.packages() if p['units_per_car']==5)
    assert package['catalogue_hardware_kg']==960.
    assert package['catalogue_regular_low_voltage_kWe']==pytest.approx(2.6)
    assert package['catalogue_maximum_low_voltage_kWe']==pytest.approx(11.7)
    assert package['compressor_real_kWe'] is None
    assert package['actual_50C_COP'] is None
    load=dict(total_kWthermal=140.,load_id='fixture',fresh_air_cabin_m3_h=3456.,
              specified_low_voltage_scenario_kWe=2.6,recovery_fan_extra_kWe=0.)
    normal=s.capacity_screen(package,load);failed=s.capacity_screen(package,load,failed_cooling_units=1)
    assert normal['nominal_capacity_comparison']=='pass'
    assert failed['nominal_capacity_comparison']=='fail'
    assert failed['required_capacity_fraction_of_nominal']==pytest.approx(140/132)
    assert normal['actual_50C_capacity_screen']==failed['actual_50C_capacity_screen']=='unknown'
    assert failed['package_candidate_id']==normal['package_candidate_id']
    assert failed['complete_HVAC_electric_kWe'] is None
    assert package['catalogue_hardware_kg']==960.


def test_package_binding_refuses_different_quantity_or_envelope_and_does_not_create_complete_mass():
    package=next(p for p in s.packages() if p['units_per_car']==5)
    parent=dict(units_per_car=5,source_id='konvekta',package_unit_envelope_m=[2.655,2.083,.357],
        package_unit_mass_range_kg=[192.,192.],package_hardware_mass_range_kg_per_car=[960.,960.],
        package_capacity_kWthermal=[165.,165.])
    assert s.matches_parent_package(package,parent)
    assert not s.matches_parent_package(next(p for p in s.packages() if p['units_per_car']==3),parent)
    parent['package_unit_envelope_m'][0]=2.0
    assert not s.matches_parent_package(package,parent)
    assert package['installed_HVAC_mass_kg'] is None


def test_passenger_and_fresh_air_loads_are_preserved_and_fan_heat_is_not_free_power():
    campaign=s.hvac_campaign()
    assert len(campaign['loads'])==768 and len(campaign['comparisons'])==1536
    assert len(campaign['component_candidates'])==48
    assert campaign['vehicle_structural_mass_is_an_HVAC_load_input'] is False
    for row in campaign['loads']:
        passengers=row['scenario']['passengers']
        assert row['fresh_air_cabin_m3_h']==pytest.approx(passengers*6*3.6)
        assert row['sensible_components_W']['occupants']==passengers*75
        assert row['latent_components_W']['occupants']==passengers*55
        assert row['specified_low_voltage_scenario_kWe']>0
        assert row['actual_HVAC_electric_kWe'] is None
        assert row['sensible_components_W']['unit_blower']==pytest.approx(row['specified_low_voltage_scenario_kWe']*1000*row['low_voltage_heat_fraction_into_cabin'])


def test_recovery_leaves_door_infiltration_untreated_and_adds_electric_load_and_unknown_hardware():
    campaign=s.hvac_campaign()
    def chosen(recovery):
        feature=next(f for f in campaign['thermal_features'] if f['glazing_solar_factor']==.55 and f['roof_absorptivity']==.2 and f['upper_core_m']==.04 and f['recovery']==recovery)
        return next(l for l in campaign['loads'] if l['thermal_feature_id']==feature['thermal_feature_id'] and l['scenario']['name']=='AW3-humid-door60' and l['low_voltage_draw_mode']=='catalogue-regular' and l['low_voltage_heat_fraction_into_cabin']==1.)
    old,new=chosen(False),chosen(True)
    assert old['sensible_components_W']['doors_and_leakage']==new['sensible_components_W']['doors_and_leakage']
    assert old['latent_components_W']['doors_and_leakage']==new['latent_components_W']['doors_and_leakage']
    assert new['recovery_fan_extra_kWe']>0
    assert new['recovery_hardware_mass_kg'] is None


def test_resealed_fabricated_payload_and_extra_artifact_are_rejected(tmp_path,monkeypatch):
    value=dict(schema=s.SCHEMA,source_sha256={'fixture':'source'},counts={},readiness={'HVAC_50C_capacity':'unknown'},**s.FLAGS)
    value['evaluation_id']=s.identity(value)
    monkeypatch.setattr(s,'evaluate',lambda root:deepcopy(value))
    out=tmp_path/'run';s.run(out,tmp_path);assert s.verify(out,tmp_path)['current']
    bad=deepcopy(value);bad['readiness']['HVAC_50C_capacity']='pass';bad['evaluation_id']=s.identity({k:v for k,v in bad.items() if k!='evaluation_id'})
    (out/'result.json').write_bytes(s.encoded(bad));manifest=json.loads((out/'manifest.json').read_text())
    manifest['evaluation_id']=bad['evaluation_id'];manifest['files_sha256']['result.json']=s.sha256(s.encoded(bad)).hexdigest()
    manifest['manifest_id']=s.identity({k:v for k,v in manifest.items() if k!='manifest_id'});(out/'manifest.json').write_bytes(s.encoded(manifest))
    with pytest.raises(ValueError,match='derived result'):s.verify(out,tmp_path)
    (out/'extra.txt').write_text('unexpected')
    with pytest.raises(ValueError,match='inventory'):s.verify(out,tmp_path)


def test_research_acceptance_cannot_be_asserted_even_if_resealed():
    for key in s.FLAGS:
        with pytest.raises(ValueError,match='acceptance'):s._unaccepted({'nested':{key:True}})

"""Failure-led checks for declared landing and hot-roof proposal equations."""
from copy import deepcopy
import math
from pathlib import Path
import os

import pytest

from engineering.thermal_closure import comfort_fixes as m

MAIN=Path(os.environ.get('OSR_EVIDENCE_ROOT','/home/hayder/Documents/OpenSourceRail'))


@pytest.fixture(scope='module')
def car():
    from engineering.development_baseline import selection
    return selection.load(MAIN)['vehicle']


def test_retained_spring_reproduces_energy_and_fails_loaded_drop():
    c=m.capture_candidates()[0];mass=20806.683728076856
    r=m.capture_response(c,mass)
    K=8e7;W=mass*m.G
    unconstrained=(W+math.sqrt(W*W+2*K*W*.005))/K
    assert unconstrained>.008
    assert not r['arrested_before_bottoming']
    assert r['necessary_energy_force_stroke_screen']=='fail'
    assert r['required_compression_m']==pytest.approx(.008,abs=1e-9)
    assert abs(r['energy_balance_residual_J'])<.001


def test_no_catalogue_energy_rating_becomes_a_slow_impact_force_map():
    assert math.sqrt(2*m.G*.005)<m.REFERENCES['ace']['dynamic_curve_minimum_impact_speed_m_s']
    assert 'static/low-speed' in m.REFERENCES['ace']['scope']


def test_crush_counted_stock_replaces_exact_scope_and_has_retention():
    options=m.capture_candidates()[2:]
    assert {c['physical_definition']['count'] for c in options}=={12,16,24,32}
    for c in options:
        assert math.fsum(p['mass_kg'] for p in c['stock'])==pytest.approx(c['counted_or_allocated_stock_kg'])
        assert c['net_accounted_stock_change_kg']==pytest.approx(c['counted_or_allocated_stock_kg']-145.76)
        assert len(c['physical_definition']['positions_m'])==c['physical_definition']['count']
        assert any('retaining-collars' in p['id'] for p in c['stock'])
        assert c['geometry']['stack_with_spreaders_m']<.12
        assert c['physical_accepted'] is False


def test_honeycomb_energy_and_timestep_confirmation():
    c=next(c for c in m.capture_candidates() if c['physical_definition']['count']==16)
    mass=17356.683728076856+75*46+c['net_accounted_stock_change_kg']
    a=m.capture_response(c,mass,precrushed=True,max_step_s=.0002)
    b=m.capture_response(c,mass,precrushed=True,max_step_s=.00005)
    assert a['arrested_before_bottoming']
    assert a['necessary_energy_force_stroke_screen']=='pass'
    assert a['required_compression_m']==pytest.approx(b['required_compression_m'],rel=2e-5)
    assert abs(a['energy_balance_residual_J'])<.01
    assert a['rebound_height_m_upper_bound']>0
    assert a['rebound_energy_J_upper_bound']==pytest.approx(a['absorbed_loading_work_J'])
    assert a['rebound_energy_J_conditional_on_fraction']==pytest.approx(.1*a['rebound_energy_J_upper_bound'])
    assert a['occupant_acceleration_pulse_acceptance']=='unknown'


def test_precrush_uncertainty_and_missing_contacts_are_not_free():
    c=next(c for c in m.capture_candidates() if c['physical_definition']['count']==16)
    mass=17356.683728076856+75*160+2000+c['net_accounted_stock_change_kg']
    nominal=m.capture_response(c,mass,precrushed=True)
    low=m.capture_response(c,mass,precrushed=True,strength_factor=.75)
    missing=m.capture_response(c,mass,precrushed=True,active_count=12)
    uncrushed=m.capture_response(c,mass,precrushed=False,strength_factor=1.25)
    assert nominal['necessary_energy_force_stroke_screen']=='pass'
    assert low['necessary_energy_force_stroke_screen']=='fail'
    assert missing['necessary_energy_force_stroke_screen']=='fail'
    assert uncrushed['peak_force_N_each']>50000
    with pytest.raises(ValueError,match='active count'):m.capture_response(c,mass,active_count=17)


def test_finish_mass_comes_from_actual_two_coat_coverage():
    r=m.coating_stock(100*.09290304)
    assert r['wet_USgal']==pytest.approx(3.)
    assert r['nominal_dry_finish_kg']==pytest.approx(3*11.5*.45359237*.63)
    assert r['primer_and_repairs_mass_kg'] is None
    assert r['nominal_dry_finish_kg']>0


def test_radiation_convection_heat_balance_and_aged_finish(car):
    roofs=m.roof_candidates(car)
    control=next(c for c in roofs if c['physical_definition']['name']=='retained-H60')
    white=next(c for c in roofs if c['physical_definition']['name']=='white-aged-H60')
    a=m.roof_equilibrium(control);b=m.roof_equilibrium(white)
    assert a['core_hot_C']>70
    assert b['core_hot_C']<70
    assert b['core_hot_C']<a['core_hot_C']
    assert abs(b['heat_balance_residual_W_m2'])<1e-6
    assert white['net_counted_material_change_kg']>40
    assert b['whole_car_HVAC_demand_kW'] is None


def test_stagnant_warm_longwave_stress_and_blocked_vent_are_retained(car):
    roofs=m.roof_candidates(car)
    white=next(c for c in roofs if c['physical_definition']['name']=='white-aged-H60')
    hot=m.roof_equilibrium(white,outside_h_W_m2K=5,longwave_environment_C=60)
    assert hot['necessary_core_temperature_screen']=='fail'
    canopy=next(c for c in roofs if c['physical_definition']['canopy'])
    vent=m.roof_equilibrium(canopy,outside_h_W_m2K=5,longwave_environment_C=60)
    blocked=m.roof_equilibrium(canopy,outside_h_W_m2K=5,longwave_environment_C=60,canopy_air_h_W_m2K=0)
    assert blocked['core_hot_C']>vent['core_hot_C']
    assert canopy['physical_definition']['roof_HVAC_recirculation_access_wind_and_bridges_qualified'] is False
    assert canopy['net_counted_material_change_kg']>white['net_counted_material_change_kg']


def test_hp_processing_temperature_is_not_a_continuous_limit(car):
    hp=next(c for c in m.roof_candidates(car) if c['physical_definition']['core_grade']=='HP60')
    assert hp['physical_definition']['core_continuous_limit_C']==80
    assert hp['source_materiality']=='manufacturer-indexed-HP-data-native-document-unavailable'
    assert hp['complete_added_installed_mass_kg'] is None
    bad=deepcopy(hp);bad['physical_definition']['absorptivity']=2
    with pytest.raises(ValueError,match='optical'):m.roof_equilibrium(bad)

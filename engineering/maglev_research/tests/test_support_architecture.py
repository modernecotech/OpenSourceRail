"""Counted architecture changes preserve support, packaging and research gates."""
from copy import deepcopy
import json
import math

import pytest

from engineering.maglev_research import support_architecture as support


@pytest.fixture(scope='module')
def result():
    return support.study()


def test_extra_canonical_modules_cannot_support_their_own_mass(result):
    canonical=result['canonical']
    assert canonical['fulltrain_modules']==144
    assert canonical['net_support_per_added_canonical_module_n']==pytest.approx(-1211.42555472)
    for count in (24,30,32,48,1000):
        assert count*canonical['module_max_sampled_force_n']<count*canonical['module_weight_n']
    assert canonical['speed_cannot_resolve_static_support']


def test_complete_joint_grid_and_unchanged_constraints(result):
    assert result['executed_joint_model_cases']==len(result['cases'])==256
    assert len(result['separate_guidance_bound_cases'])==18
    constraints=result['fixed_constraints']
    assert constraints['passenger_payload_kg_per_car']==12000
    assert constraints['adverse_lift_aw3_factor']==1.3
    assert constraints['current_limit_a']==120
    assert constraints['current_density_limit_a_mm2']==3.75
    assert constraints['maximum_copper_c']==120
    assert constraints['coil_fill_limit']==.55
    assert constraints['field_limit_t']==2.2
    assert result['nominal_joint_passes']==32
    assert result['simultaneous_survivor_count']==0
    assert not result['configuration_adopted']
    assert not result['complete_system_feasible']


def test_new_cooler_adds_stock_power_and_series_resistance(result):
    cooler=result['cooler_design']
    assert cooler['mass_kg']==pytest.approx(20.9228955168)
    assert cooler['auxiliary_power_target_w']==pytest.approx(74.2148186708)
    assert cooler['qualified'] is False
    assert cooler['mass_kg']==pytest.approx(sum(row['volume_m3']*row['density_kg_m3'] for row in cooler['parts']))
    for row in result['cases']:
        if row['hypothesis']['cooling']=='counted-fin-tank-fan-targets':
            assert row['added_cooler_mass_kg_per_module']==cooler['mass_kg']
            assert row['guide_cooling_w_k']<cooler['air_conductance_w_k']
            assert row['cooler_auxiliary_power_target_w_per_car']==pytest.approx(row['hypothesis']['modules_per_car']*cooler['auxiliary_power_target_w'])
        else:
            assert row['guide_cooling_w_k']==18.
            assert row['added_cooler_mass_kg_per_module']==0.


def test_packaging_and_full_train_counts_are_not_erased_by_a_nominal_pass(result):
    for row in result['cases']:
        count=row['hypothesis']['modules_per_car']
        assert row['fulltrain_module_count']==6*count
        assert row['controlled_aw3_kg']-row['controlled_tare_kg']==pytest.approx(12000.)
        assert row['six_car_aw3_kg']==pytest.approx(6*row['controlled_aw3_kg'])
        if count==32:
            assert row['array_row_length_m']==pytest.approx(16.11)
            assert not row['array_nominal_fit']
            assert not row['conditional_joint_support_coupon_pass']
        if row['conditional_nominal_joint_pass']:
            assert row['hypothesis']['topology']=='useful-only-poles-sensitivity'
            assert not row['conditional_1_3_peak_pass']
            assert not row['topology_independently_validated']


def test_separate_guide_winding_is_counted_and_never_becomes_a_joint_result(result):
    for row in result['separate_guidance_bound_cases']:
        guide=row['guide_material_bound']
        assert guide['turns']==222
        assert guide['current_a']<=120.
        assert guide['current_a']/guide['conductor_area_mm2']==pytest.approx(3.75)
        assert guide['copper_fill']==pytest.approx(.549)
        assert guide['gap_field_t']==pytest.approx(.95*guide['field_t'])
        assert guide['gap_field_t']*guide['area_per_face_m2']/guide['effective_iron_section_m2']==pytest.approx(2.2)
        assert guide['force_per_energised_unit_n']==pytest.approx(guide['gap_field_t']**2*guide['area_per_face_m2']/(4e-7*math.pi))
        inner=math.prod(guide['coil_inner_m']);outer=math.prod(guide['coil_outer_m'])
        copper_volume=guide['copper_kg_per_unit']/8960.
        assert copper_volume/((outer-inner)*guide['coil_height_m'])==pytest.approx(.549)
        assert guide['nominal_turn_envelope_fits']
        assert guide['mass_kg_per_unit']==pytest.approx(sum(guide[name] for name in (
            'steel_kg_per_unit','copper_kg_per_unit','enclosure_kg_per_unit','enamel_kg_per_unit','fluid_kg_per_unit','bobbin_kg_per_unit')))
        assert row['guide_cooler_mass_kg_per_unit']==result['cooler_design']['mass_kg']
        assert not row['joint_guidance_model_executed']
        assert not row['complete_system_feasible']
        assert not row['configuration_adopted']
    original=[row for row in result['separate_guidance_bound_cases'] if row['support_topology']=='original-branch-flux' and row['support_modules_per_car']==30]
    assert any(row['conditional_symmetric_support_screen'] for row in original)


def test_nominal_and_static_peak_power_consume_the_existing_suspension_budget(result):
    row=next(row for row in result['separate_guidance_bound_cases'] if row['id']=='separate-guidance-03')
    power=row['suspension_power_budget']
    nominal=sum(power[name] for name in ('nominal_support_dc_copper_w_per_car','guide_hot_copper_w_per_car',
        'new_guide_cooler_auxiliary_target_w_per_car','retained_support_pump_target_w_per_car'))
    assert power['nominal_accounted_lower_bound_w_per_car']==pytest.approx(nominal)
    assert nominal==pytest.approx(5956.98585009)
    assert power['nominal_allocation_headroom_w_per_car']==pytest.approx(10000.-nominal)
    peak=power['static_1_3_support_copper_at40c_w_per_car']+nominal-power['nominal_support_dc_copper_w_per_car']
    assert power['static_1_3_accounted_lower_bound_w_per_car']==pytest.approx(peak)
    assert peak==pytest.approx(21971.8967519)
    assert peak>power['existing_suspension_allocation_w_per_car']
    assert power['extra_stock_for_uniform_new_coolers_kg_per_car']==pytest.approx(30*result['cooler_design']['mass_kg'])
    assert not power['uniform_new_coolers_mass_feedback_executed']


@pytest.mark.parametrize('mutation', ['sources','grid','payload','mass','cooler','density','survivor','bound'])
def test_optimistic_reporting_drift_is_refused(result,monkeypatch,mutation):
    loaded=support.retained._load(support.ROOT)
    monkeypatch.setattr(support.retained,'_load',lambda root:loaded)
    changed=deepcopy(result)
    if mutation=='sources':changed['source_sha256']={}
    elif mutation=='grid':changed['cases'][0]['hypothesis']['modules_per_car']=30
    elif mutation=='payload':changed['fixed_constraints']['passenger_payload_kg_per_car']=0.
    elif mutation=='mass':changed['cases'][0]['controlled_aw3_kg']-=100.
    elif mutation=='cooler':changed['cases'][0]['guide_cooling_w_k']=999.
    elif mutation=='density':changed['cases'][0]['nominal_joint']['continuous_current_density_screen']=True
    elif mutation=='survivor':changed['simultaneous_survivor_count']=1
    else:changed['separate_guidance_bound_cases'][0]['joint_guidance_model_executed']=True
    with pytest.raises(ValueError):support.validate(changed)

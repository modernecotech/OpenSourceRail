"""Physical stock, replacement boundaries and support-load feedback checks."""
from copy import deepcopy
import math
import sys
from types import ModuleType

import pytest

from engineering.halbach_scaling import vehicles as v
from engineering.vehicle_optimisation import equipment, hvac, magnets

ROOT = v.ROOT


@pytest.mark.parametrize('b,h,t',[(.14,.22,.004),(.10,.25,.0025),(.08,.06,.0015)])
def test_disjoint_prisms_recover_independent_hollow_rectangle_integrals(b,h,t):
    q = v.extrusion_section(b,h,t)
    area = b*h-(b-2*t)*(h-2*t)
    iy = (b*h**3-(b-2*t)*(h-2*t)**3)/12
    iz = (h*b**3-(h-2*t)*(b-2*t)**3)/12
    assert q['area_m2'] == pytest.approx(area,rel=1e-12)
    assert q['I_strong_m4'] == pytest.approx(iy,rel=1e-12)
    assert q['I_weak_m4'] == pytest.approx(iz,rel=1e-12)
    assert q['centroid_yz_m'] == pytest.approx([b/2,h/2])
    for a in q['rectangles']:
        for other in q['rectangles']:
            if a is other:continue
            dy=min(a['y']+a['width'],other['y']+other['width'])-max(a['y'],other['y'])
            dz=min(a['z']+a['height'],other['z']+other['height'])-max(a['z'],other['z'])
            assert not (dy>1e-12 and dz>1e-12)


def test_six_cell_intersections_are_not_counted_twice_and_support_local_plate_bound():
    b,h,t,w=.22,.36,.003,.002
    q=v.extrusion_section(b,h,t,web_m=w)
    expected=b*h-(b-2*t)*(h-2*t)+w*(h-2*t)+2*w*(b-2*t-w)
    assert q['cell_count']==6 and len(q['rectangles'])==9
    assert q['area_m2']==pytest.approx(expected,rel=1e-12)
    empty=v.extrusion_section(b,h,t)
    assert q['I_strong_m4']>empty['I_strong_m4'] and q['I_weak_m4']>empty['I_weak_m4']
    assert q['elastic_local_plate_critical_Pa']>empty['elastic_local_plate_critical_Pa']
    for a in q['rectangles']:
        for other in q['rectangles']:
            if a is other:continue
            dy=min(a['y']+a['width'],other['y']+other['width'])-max(a['y'],other['y'])
            dz=min(a['z']+a['height'],other['z']+other['height'])-max(a['z'],other['z'])
            assert not (dy>1e-12 and dz>1e-12)


@pytest.mark.parametrize('args,kw',[((0.,.2,.002),{}),((.1,.2,.1),{}),((.1,.2,.002),{'web_m':.1}),((True,.2,.002),{})])
def test_invalid_extrusion_dimensions_are_refused(args,kw):
    with pytest.raises(ValueError):v.extrusion_section(*args,**kw)


def test_fourteen_variants_preserve_fixed_passenger_and_door_service():
    rows=v.variants(ROOT)
    assert len(rows)==14 and len({q['candidate_id'] for q in rows})==14
    for q in rows:
        v.validate(q,ROOT)
        assert q['service']['cars']==6 and q['service']['body_length_m']==17
        assert q['service']['passengers_normal_per_car']==120
        assert q['service']['passengers_aw3_per_car']*q['service']['passenger_mass_kg']==12000
        assert q['service']['doors_per_car']==4 and q['service']['door_opening_m']==[1.4,2.1]
        assert q['installed_empty_kg_per_car'] is None and q['cg_m'] is None
        assert all(q[k] is False for k in v.FLAGS)
        removed_stock=[];removed_allocations=[]
        for row in q['replacement_changes']:
            removed_stock+=row.get('removed_part_ids',[])
            removed_allocations+=row.get('removed_allocation_ids',[])
        assert len(removed_stock)==len(set(removed_stock))
        assert len(removed_allocations)==len(set(removed_allocations))
        assert not any('equipped-body-total' in name for name in removed_allocations)


def test_new_frame_stock_closes_but_failed_compact_stiffness_is_retained():
    rows=v.variants(ROOT)
    deep=next(q['frame'] for q in rows if q['name']=='6082-six-cell-deep/retained-equipment')
    compact=next(q['frame'] for q in rows if q['name']=='6082-six-cell-compact/retained-equipment')
    for frame in (deep,compact):
        assert frame['counted_material_mass_kg']==pytest.approx(math.fsum(p['total_mass_kg'] for p in frame['stock_parts']))
        assert frame['counted_material_mass_kg']<frame['removed_counted_frame_kg']
        assert frame['engineering_member_count']==65 and frame['joint_bolt_count']==520
        assert len(frame['removed_stock_ids'])==260
    a=v.structure_screen(compact,35000)
    b=v.structure_screen(deep,35000)
    assert not a['matched_both_axis_section_stiffness'] and not a['member_level_necessary_pass']
    assert b['matched_both_axis_section_stiffness'] and b['member_level_necessary_pass']
    assert not b['full_length_unbraced_Euler_screen_pass']
    assert b['hypothetical_2m_braced_Euler_screen_pass']
    assert not b['actual_bracing_qualified'] and not b['global_body_qualified']
    higher=v.structure_screen(deep,45000)
    assert higher['roof_force_N_per_module']>b['roof_force_N_per_module']
    assert higher['spreader_stress_Pa']>higher['spreader_allowable_Pa']


@pytest.mark.parametrize('name,target,roof,plate',[
    ('6082-six-cell-deep-40kn',40000.,(.10,.25,.0045),.024),
    ('6082-six-cell-deep-70kn',70000.,(.14,.30,.005),.032),
])
def test_counted_reinforcement_closes_exact_profile_and_spreader_mass(name,target,roof,plate):
    rows=v.variants(ROOT)
    original=next(q['frame'] for q in rows if q['name']=='6082-six-cell-deep/retained-equipment')
    proposed=next(q['frame'] for q in rows if q['name']==name+'/bus-ul700-electric-five-proposal')
    assert proposed['design_force_N_per_module']==target
    assert proposed['design_force_bound_qualified'] is False
    length=sum(q['length_m'] for q in original['members'] if 'roof-longitudinal' in q['id'])
    area=lambda b,h,t:b*h-(b-2*t)*(h-2*t)
    delta_roof=length*(area(*roof)-area(.10,.25,.0025))*2710
    delta_plate=24*.30*.22*(plate-.018)*2700
    assert proposed['counted_material_mass_kg']-original['counted_material_mass_kg']==pytest.approx(delta_roof+delta_plate)
    assert proposed['counted_material_mass_kg']==pytest.approx(sum(q['total_mass_kg'] for q in proposed['stock_parts']))
    spreader=next(q for q in proposed['stock_parts'] if q['id']=='hardpoints/roof-spreader')
    assert spreader['quantity']==24 and spreader['size_m']==[.30,.22,plate]
    assert spreader['total_mass_kg']==pytest.approx(24*.30*.22*plate*2700)
    assert max(q['section']['wall_m'] for q in proposed['members'])<=.005
    assert [q for q in proposed['members'] if 'lower-stringer' in q['id']]==[
        q for q in original['members'] if 'lower-stringer' in q['id']]
    checked=v.structure_screen(proposed,35000,magnetic_force_N_per_module=target)
    assert checked['member_level_necessary_pass']
    assert checked['roof_stress_Pa']<=checked['roof_HAZ_allowable_Pa']
    assert checked['roof_deflection_m']<=.002
    assert checked['spreader_stress_Pa']<=checked['spreader_allowable_Pa']
    assert not checked['global_body_qualified'] and not checked['full_length_unbraced_Euler_screen_pass']


def test_peak_magnetic_force_cannot_be_hidden_by_mean_weight_screen():
    rows=v.variants(ROOT)
    old=next(q['frame'] for q in rows if q['name']=='6082-six-cell-deep/retained-equipment')
    medium=next(q['frame'] for q in rows if q['name']=='6082-six-cell-deep-40kn/bus-ul700-electric-five-proposal')
    strong=next(q['frame'] for q in rows if q['name']=='6082-six-cell-deep-70kn/bus-ul700-electric-five-proposal')
    assert v.structure_screen(old,35000)['member_level_necessary_pass']
    assert not v.structure_screen(old,35000,magnetic_force_N_per_module=40000)['member_level_necessary_pass']
    assert not v.structure_screen(old,35000,magnetic_force_N_per_module=70000)['member_level_necessary_pass']
    assert not v.structure_screen(medium,35000,magnetic_force_N_per_module=70000)['member_level_necessary_pass']
    checked=v.structure_screen(strong,35000,magnetic_force_N_per_module=70000)
    assert checked['member_level_necessary_pass'] and checked['applied_force_N_per_module']==70000
    for low in (0.,1.,1000.):
        below=v.structure_screen(strong,35000,magnetic_force_N_per_module=low)
        assert below['applied_force_N_per_module']==below['mean_weight_requirement_N_per_module']
    for bad in (-1.,True,float('nan'),float('inf')):
        with pytest.raises(ValueError):v.structure_screen(strong,35000,magnetic_force_N_per_module=bad)
    assert v.structure_screen(None,35000,magnetic_force_N_per_module=70000)['member_level_necessary_pass'] is None


def test_same_equipment_has_same_hot_load_across_body_mass_options():
    rows=[q for q in v.variants(ROOT) if q['name'].endswith('/bus-ul700-electric-two')]
    assert len(rows)==3
    assert rows[0]['thermal']==rows[1]['thermal']==rows[2]['thermal']
    thermal=rows[0]['thermal']
    assert thermal['passenger_ventilation_reduced'] is False
    assert thermal['thermal_load_depends_on_body_mass'] is False
    assert thermal['loads'][1]['total_kWthermal']>thermal['loads'][0]['total_kWthermal']
    assert all(not c['complete_mass_and_electric_input_known'] for c in thermal['comparisons'])


def test_five_package_quantity_scales_known_unit_properties_but_not_installation_or_hot_rating():
    before=hvac.candidates()
    base=next(q for q in before if q['id']=='bus-ul700-electric-two')
    rows=v.variants(ROOT)
    body=next(q for q in rows if q['name']=='6082-six-cell-deep/bus-ul700-electric-five-proposal')
    five=body['HVAC']
    assert len(rows)==14 and not any('ul500' in q['name'] for q in rows)
    assert five['units_per_car']==5
    assert five['package_unit_mass_range_kg']==base['package_unit_mass_range_kg']==[192,192]
    assert five['package_hardware_mass_range_kg_per_car']==[960,960]
    assert five['package_capacity_kWthermal']==[165,165]
    assert five['nominal_evaporator_air_m3_h']==pytest.approx(5*base['nominal_evaporator_air_m3_h']/2)
    assert five['roof_projected_package_area_m2']==pytest.approx(5*math.prod(base['package_unit_envelope_m'][:2]))
    assert five['package_unit_envelope_m']==base['package_unit_envelope_m']
    assert five['rated_fresh_air_m3_h'] is None  # evaporator air is not delivered fresh air
    assert five['provisional_installed_mass_scenario_kg'] is None
    assert five['external_installation_allowances'] is None
    assert five['break_even_all_additional_hardware_mass_kg']==[-160,-160]
    assert five['installed_HVAC_mass_saving_established'] is False
    assert five['package_electrical_input_kWe'] is None
    assert before==hvac.candidates()  # no mutation of the legacy catalogue
    hot=body['thermal']['comparisons'][1]
    assert hot['needed_kWthermal']==pytest.approx(132.1,abs=.1)
    assert hot['nominal_capacity_necessary_pass'] and hot['nominal_headroom_kWthermal']>0
    assert hot['actual_50C_capacity_verified'] is False and hot['thermal_screen']=='unknown'
    for mode in ('bus-ul700-electric-two','bus-ul700-electric-three'):
        control=next(q for q in rows if q['name']=='6082-six-cell-deep/'+mode)['thermal']['comparisons'][1]
        assert control['nominal_capacity_necessary_pass'] is False
        assert control['nominal_capacity_necessary_screen']=='nominal-nameplate-insufficient'


def test_five_package_hardware_is_heavier_than_removed_hvac_and_has_no_transferred_band(monkeypatch):
    small,_=_magnetic_adapter(monkeypatch)
    body=next(q for q in v.variants(ROOT) if q['name']=='6082-six-cell-deep/bus-ul700-electric-five-proposal')
    result=v.compose(body,small,root=ROOT)
    row=next(q for q in result['ledger']['changes'] if q['id']=='hvac')
    assert row['removed_kg_per_car']==800 and row['added_known_kg_per_car']==960
    assert row['delta_known_comparison_kg']==160
    assert result['HVAC_external_installation_scenario_band_kg'] is None
    assert result['installed_aw3_kg_per_car'] is None
    assert result['total_equipped_mass_bounded'] is False


def test_rehashed_vehicle_geometry_material_accounting_or_payload_change_is_refused():
    original=next(q for q in v.variants(ROOT) if q['frame'] is not None)
    for mutate in (lambda q:q['frame']['members'][0]['section'].__setitem__('wall_m',.0001),
                   lambda q:q['frame']['material'].__setitem__('density_kg_m3',1.),
                   lambda q:q.__setitem__('base_empty_kg_per_car',100.),
                   lambda q:q['service'].__setitem__('passengers_aw3_per_car',120)):
        changed=deepcopy(original);mutate(changed);changed.pop('bundle_sha256');changed['bundle_sha256']=v.identity(changed)
        with pytest.raises(ValueError,match='unsupported or modified'):v.validate(changed,ROOT)


def _magnetic_adapter(monkeypatch):
    """Use real legacy stock; stub only the sibling catalogue admission boundary.

    The coordinator runs integration with its new exact candidate catalogue.
    This fixture independently tests vehicle feedback before that package is
    available in this specialist worktree.
    """
    rows=[magnets._build(('N35-H8-half-no-yoke','planar-halbach','Arnold-N35UH',dict(segments=8,yoke_m=0.,magnet_volume_m3=x))) for x in (.006,.012)]
    module=ModuleType('engineering.halbach_scaling.candidates')
    def validate(value,root):
        if not any(value==q for q in rows):raise ValueError('unsupported magnetic fixture')
    module.validate=validate;monkeypatch.setitem(sys.modules,module.__name__,module)
    import engineering.halbach_scaling as package
    monkeypatch.setattr(package,'candidates',module,raising=False)
    return rows


def test_composition_uses_exact_magnetic_inventory_and_never_reduces_payload(monkeypatch):
    small,large=_magnetic_adapter(monkeypatch)
    body=next(q for q in v.variants(ROOT) if q['name']=='6082-six-cell-deep/bus-ul700-electric-two')
    a=v.compose(body,small,root=ROOT);b=v.compose(body,large,root=ROOT)
    expected=24*(large['stock']['train_known_mass_kg_per_module']-small['stock']['train_known_mass_kg_per_module'])
    assert b['comparison_aw3_kg_per_car']-a['comparison_aw3_kg_per_car']==pytest.approx(expected)
    assert a['ledger']['payload_kg']==b['ledger']['payload_kg']==12000
    assert a['candidate_id']!=b['candidate_id'] and a['body_candidate_id']==b['body_candidate_id']
    assert a['comparison_train_aw3_kg']==pytest.approx(6*a['comparison_aw3_kg_per_car'])
    assert a['integrated_candidate_eligible'] is False and a['overall_structure_qualified'] is False
    assert a['installed_aw3_kg_per_car'] is None and a['cg_m'] is None
    assert all(p.get('mass_kg') is None for p in a['unknown_installed_inventory'] if isinstance(p,dict))
    with pytest.raises(ValueError,match='24-module'):v.compose(body,small,modules=30,root=ROOT)


def test_unclosed_mass_is_separate_from_inventory_and_propagates_to_support_and_roof(monkeypatch):
    small,_=_magnetic_adapter(monkeypatch)
    body=next(q for q in v.variants(ROOT) if q['name']=='6082-six-cell-deep/bus-ul700-electric-two')
    composed=v.compose(body,small,root=ROOT);points=composed['support_requirements_by_unclosed_mass']
    assert [p['unclosed_additional_mass_kg_per_car'] for p in points]==[0,1000,2000,3000]
    for index,point in enumerate(points):
        assert point['comparison_aw3_kg_per_car']==pytest.approx(composed['comparison_aw3_kg_per_car']+index*1000)
        assert point['required_force_N_per_module']==pytest.approx(point['comparison_aw3_kg_per_car']*9.80665*1.3/24)
        assert not point['actual_installed_mass_known']
        if index:
            assert point['structure']['roof_stress_Pa']>points[index-1]['structure']['roof_stress_Pa']
    assert composed['HVAC_external_installation_scenario_band_kg']==[85,240]
    assert composed['ledger']['added_known_kg_per_car']==pytest.approx(sum(q['added_known_kg_per_car'] for q in composed['ledger']['changes']))


def test_real_new_magnetic_catalogue_composes_without_a_mocked_admission_boundary():
    from engineering.halbach_scaling import candidates
    magnetic=candidates.candidates(ROOT)
    assert len(magnetic)==36
    small=next(q for q in magnetic if q['physical_id']==candidates.PARENT_ID)
    large=max(magnetic,key=lambda q:q['stock']['train_known_mass_kg_per_module'])
    body=next(q for q in v.variants(ROOT) if q['name']=='6082-six-cell-deep/bus-ul700-electric-two')
    a=v.compose(body,small,root=ROOT);b=v.compose(body,large,root=ROOT)
    expected=24*(large['stock']['train_known_mass_kg_per_module']-small['stock']['train_known_mass_kg_per_module'])
    assert b['comparison_aw3_kg_per_car']-a['comparison_aw3_kg_per_car']==pytest.approx(expected)
    assert a['magnet_component_id']==small['physical_id'] and b['magnet_component_id']==large['physical_id']
    assert a['ledger']['payload_kg']==12000 and a['installed_aw3_kg_per_car'] is None


def test_reinforcement_mass_reenters_mean_support_and_peak_hypotheses_stay_separate():
    from engineering.halbach_scaling import candidates
    module=next(q for q in candidates.candidates(ROOT) if q['physical_id']==candidates.PARENT_ID)
    rows=v.variants(ROOT)
    old=next(q for q in rows if q['name']=='6082-six-cell-deep/bus-ul700-electric-five-proposal')
    new=next(q for q in rows if q['name']=='6082-six-cell-deep-70kn/bus-ul700-electric-five-proposal')
    before=v.compose(old,module,root=ROOT);after=v.compose(new,module,root=ROOT)
    added=new['frame']['counted_material_mass_kg']-old['frame']['counted_material_mass_kg']
    assert after['comparison_aw3_kg_per_car']-before['comparison_aw3_kg_per_car']==pytest.approx(added)
    for a,b in zip(before['support_requirements_by_unclosed_mass'],after['support_requirements_by_unclosed_mass']):
        assert b['required_force_N_per_module']-a['required_force_N_per_module']==pytest.approx(added*9.80665*1.3/24)
        assert b['structure']['provided_magnetic_force_N_per_module'] is None
        peak=b['declared_force_hypothesis_structure']
        assert peak['provided_magnetic_force_N_per_module']==70000
        assert peak['applied_force_N_per_module']>=b['required_force_N_per_module']
        assert not peak['magnetic_force_fault_bound_qualified'] and not after['overall_structure_qualified']

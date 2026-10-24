"""Independent equilibrium, stock, placement and adverse structural controls."""
from copy import deepcopy
import json
import math

import numpy as np
import pytest

from engineering.ferrite_maglev import candidate_magnetics as magnetics
from engineering.ferrite_maglev import candidate_structures as structures


@pytest.fixture(scope='module')
def candidate():return magnetics.definition()


@pytest.fixture(scope='module')
def mass(candidate):return structures.mass_properties(candidate)


@pytest.fixture(scope='module')
def loads(candidate,mass):return structures.load_cases(candidate,mass)


@pytest.fixture(scope='module')
def mechanical(candidate,mass,loads):return structures.mechanical(candidate,mass,loads)


def test_signed_hole_integral_matches_independent_concentric_cube():
    p=dict(kind='box',at_m=[-1,-1,-1],size_m=[2,2,2],holes=[dict(axis='z',x_m=1,y_m=1,diameter_m=1,length_m=2)])
    v,c,I=structures.primitive(p);hole=math.pi/2
    assert v==pytest.approx(8-hole)
    assert c==pytest.approx([0,0,0])
    assert I[2,2]==pytest.approx(16/3-hole*.5**2/2)
    assert I[0,0]==pytest.approx(16/3-hole*(3*.5**2+2**2)/12)


def test_offcentre_drilling_moves_mass_centroid():
    p=dict(kind='box',at_m=[0,0,0],size_m=[2,2,2],holes=[dict(axis='z',x_m=.5,y_m=1,diameter_m=.4,length_m=2)])
    v,c,I=structures.primitive(p);vh=math.pi*.2**2*2
    assert c[0]==pytest.approx((8-vh*.5)/(8-vh))
    assert c[1:]==pytest.approx([1,1])
    assert np.linalg.eigvalsh(I).min()>0


def test_mass_ledgers_close_without_reusing_old_inertias(candidate,mass):
    assert mass['known_stock_mass_kg']==pytest.approx(6113.666799604363,abs=1e-7)
    assert mass['laden']['mass_kg']==pytest.approx(candidate['controlled_aw3_kg'],abs=1e-7)
    assert mass['empty']['mass_kg']==pytest.approx(candidate['controlled_tare_kg'],abs=1e-7)
    assert mass['unlocated_retained_mass_kg']==pytest.approx(candidate['mass_accounting']['retained_unlocated_allocation_kg'],abs=1e-6)
    I=np.asarray(mass['laden']['inertia_kg_m2']);assert I[0,0]!=20000 and I[1,1]!=600000
    assert np.allclose(I,I.T) and np.linalg.eigvalsh(I).min()>0
    assert mass['complete_installed_distribution'] is False
    assert mass['retained_placement_height_sensitivity'][0]['cg_m'][2]<mass['retained_placement_height_sensitivity'][1]['cg_m'][2]


def test_common_exact_stock_cg_and_inertia_agree(candidate,mass):
    assert np.allclose(mass['laden']['cg_m'],candidate['mass_properties']['cg_m'],atol=1e-8)
    assert np.allclose(mass['laden']['inertia_kg_m2'],candidate['mass_properties']['inertia_kg_m2'],atol=1e-6)


def test_duplicate_module_placement_is_rejected(candidate):
    changed=deepcopy(candidate);changed['module_placements'][1]['centre_m']=changed['module_placements'][0]['centre_m']
    with pytest.raises(ValueError,match='duplicate'):structures.validate_candidate(changed)


def test_full_wrench_equilibrium_and_actual_failed_support(loads):
    for case in loads['cases']:
        points=np.array([p['at_m'] for p in case['modules']]);forces=np.array(case['forces_n'])
        recovered=np.r_[forces.sum(axis=0),np.cross(points,forces).sum(axis=0)]
        assert recovered==pytest.approx(case['target_wrench'],abs=1e-6)
        assert forces[:,2].min()>=-1e-7
    assert loads['controls']['double_load_reaction_ratio']==pytest.approx(2)
    assert loads['controls']['zero_load_peak_n']==pytest.approx(0,abs=1e-10)
    assert loads['controls']['failed_support_load_n']==0


def test_rank_deficient_supports_and_unbalanced_targets_reject():
    with pytest.raises(ValueError,match='rank'):structures.reactions([[0,0,0]]*4,[0,0,100],[1,2,3])
    with pytest.raises(ValueError):structures.reactions([[0,0,0],[1,0,0],[2,0,0]],[0,0,100],[100,0,0])


def test_force_not_clipped_to_twenty_kn(candidate,mass):
    heavy=deepcopy(mass);heavy['laden']['mass_kg']*=2
    results=structures.load_cases(candidate,heavy)
    peak=next(r for r in results['cases'] if r['id']=='AW3-vertical-dynamic')
    assert peak['peak_module_resultant_n']>20000
    assert peak['force_screen_pass'] is False
    assert sum(r[2] for r in peak['forces_n'])==pytest.approx(heavy['laden']['mass_kg']*9.81*1.3)


def test_angular_acceleration_uses_full_candidate_inertia(candidate,mass):
    changed=deepcopy(mass);changed['laden']['inertia_kg_m2']=(np.asarray(changed['laden']['inertia_kg_m2'])*2).tolist()
    first=structures.load_cases(candidate,mass)['cases'][-1];second=structures.load_cases(candidate,changed)['cases'][-1]
    delta=np.asarray(second['target_wrench'][3:])-first['target_wrench'][3:]
    expected=np.asarray(mass['laden']['inertia_kg_m2'])@np.asarray(first['angular_acceleration_rad_s2'])
    assert delta==pytest.approx(expected,abs=1e-6)


def test_bolt_group_recovers_force_and_all_three_moments():
    force=[1234,2345,3456];moment=[789,456,321]
    result=structures.bolt_group(force,moment,[-.15,-.05,.05,.15],[-.1,.1])
    assert result['recovered_wrench']==pytest.approx([*force,*moment])
    assert max(abs(x) for x in result['equilibrium_residual'])<1e-8
    assert any(b['signed_normal_n']<0 for b in result['bolts'])
    assert result['maximum_tension_n']>max(b['signed_normal_n'] for b in result['bolts'])


def test_hardpoint_uses_actual_vertical_and_transverse_arm(mechanical):
    worst=mechanical['hardpoint']['worst'];arm=np.asarray(worst['load_arm_m']);F=worst['force_n']
    assert abs(arm[2])>.1
    assert worst['joint_moment_nm']==pytest.approx(np.cross(arm,F))
    assert worst['joint_centre_m'][2]==pytest.approx(-.3155)


def test_retained_splice_failure_is_not_hidden_by_geometry_upgrade(mechanical):
    old=mechanical['collector_splice'];new=mechanical['alternatives'][0]
    assert old['per_cut_bolts']==8 and old['cut_count_per_car']==48
    assert old['utilisation']>1 and old['passed'] is False
    assert new['additional_stock_mass_kg_per_car']>0
    assert new['requires_candidate_revision'] is True
    assert new['packaging_and_service_path_fitted'] is False


def test_candidate_body_bending_end_equilibrium_and_fatigue_open(mechanical):
    body=mechanical['body_spine'];assert abs(body['end_moment_residual_nm'])<1e-5
    assert body['net_area_each_m2']>0 and body['net_I_each_m4']>0
    assert all(r['detail_category_qualified'] is False for r in body['fatigue'])


def test_strand_layout_has_real_cover_spacing_and_no_impossible_layers():
    a=structures.load();s=a['beam_sections'][0];p=structures.strand_coordinates(s,18,8,a)
    assert p is not None and len(p)==26
    for r in p:
        assert abs(r['y_m'])+.0152/2<=s['width_m']/2-a['concrete']['cover_m']+1e-10
    assert structures.strand_coordinates(s,38,12,a) is None


def test_hollow_box_inertia_and_uniform_beam_equilibrium():
    p=structures.section_properties(dict(width_m=.8,depth_m=2.5,web_m=.1,flange_m=.15))
    assert p['area_m2']==pytest.approx(.68)
    assert p['I_m4']==pytest.approx((.8*2.5**3-.6*2.2**3)/12)
    left,right,M,V=structures._simple_beam(([(12.5,100)],20),25,[0,12.5,25])
    assert left==right==300
    assert M==pytest.approx([0,100*25/4+20*25**2/8,0])
    assert p['torsion_J_m4']>0


def test_moving_load_matches_exact_midspan_control_and_adverse_scaling():
    c=dict(cars=1);case=dict(id='AW3-vertical-dynamic',modules=[dict(at_m=[0,0,0],force_n=[0,0,100])],target_wrench=[0,0,100,0,0,0])
    results=structures.moving_envelope(c,dict(cases=[case]),25,0,.5)
    assert results['max_moment_nm']==pytest.approx(625)
    assert results['max_live_deflection_times_EI_n_m3']==pytest.approx(100*25**3/48)
    doubled=deepcopy(case);doubled['modules'][0]['force_n'][2]=200;doubled['target_wrench'][2]=200
    adverse=structures.moving_envelope(c,dict(cases=[doubled]),25,0,.5)
    assert adverse['max_moment_nm']==pytest.approx(2*results['max_moment_nm'])


def test_l_returns_and_crossmembers_are_separately_counted(candidate):
    r=structures.return_rail_and_attachments(candidate)
    assert len([p for p in r['guideway']['parts'] if p['id'].startswith('return/')])==8
    assert r['rail_mass_kg']==pytest.approx(sum(p['mass_kg'] for p in r['guideway']['parts']))
    assert r['steel_mass_kg']==pytest.approx(r['rail_mass_kg']+r['crossmembers']['mass_kg']+r['baseplates']['mass_kg']+r['risers']['mass_kg']+r['riser_caps_mass_kg'])
    assert r['crossmembers']['count']==26 and r['anchors']['count']==208
    assert r['old_flat_rail_steel_reused'] is False
    assert r['vehicle_swept_clearance_fitted'] is False
    assert r['risers']['count']==104 and len(r['support_parts'])>100


def test_hole_cannot_make_positive_solid_intersection_disappear():
    a=dict(kind='box',at_m=[0,0,0],size_m=[2,2,2],holes=[dict(axis='z',diameter_m=.2,x_m=1,y_m=1)])
    through=dict(kind='box',at_m=[.99,.99,0],size_m=[.02,.02,2])
    assert structures.collision_witness(a,through) is None
    occupied=dict(kind='box',at_m=[.6,.6,0],size_m=[.2,.2,2])
    assert structures.collision_witness(a,occupied) is not None


def test_old_high_returnrail_proves_retained_stringer_material_collision(candidate):
    guideway=magnetics.guideway_definition(25,variant_id=candidate['variant_id']);high=deepcopy(candidate)
    # Recreate the original, explicitly rejected z−.55 layout in the same
    # viewport/material checks, regardless of selected repaired mount height.
    shift=-.55-high['module_placements'][0]['centre_m'][2]
    for p in high['module_placements']:p['centre_m'][2]+=shift
    for p in guideway['parts']:p['at_m'][2]+=shift
    result=structures.interface_clearance(high,guideway)
    assert result['counts']['rail_retained']>0
    assert any('lower-stringer' in r['second'] for r in result['findings'])


def test_attachment_material_quantities_are_signed_geometry_not_allowance():
    d=json.loads((structures.DATA/'candidate-attachment-equipment.json').read_text());mass=0
    for part in d['parts']:
        v,c,I=structures.primitive(part);mass+=v*part['density_kg_m3'];assert v==pytest.approx(part['volume_m3'])
    assert mass==pytest.approx(d['mass_kg_per_module'])
    assert d['quantity_per_car']==24
    assert len(d['retained_machining'])==48
    assert sum(len(r['world_centres_xy_m']) for r in d['retained_machining'])==384
    assert all(r['removed_mass_credit_kg']==0 for r in d['retained_machining'])


def test_preferred_support_stays_bounded_and_recovers_actual_wrench(candidate):
    result=structures.preferred_support_loads(candidate,18000)
    assert result['passed'] is True and result['adopted'] is False
    f=np.asarray(result['preferred_loads_n']);p=np.asarray(result['positions_m']);mass=result['reference_mass_kg'];g=result['gravity_m_s2']
    assert min(f)>=0 and max(f)<=18000+1e-7
    assert sum(f)==pytest.approx(mass*g)
    assert max(abs(x) for x in result['equilibrium_residual'])<1e-5
    assert result['peak_bending_nm']<=result['uniform_request_peak_bending_nm']+1e-5
    assert structures.preferred_support_loads(candidate,1000)['passed'] is False
    caps=[18000.]*24;caps[0]=16000.;bounded=structures.preferred_support_loads(candidate,caps)
    assert bounded['passed'] and bounded['preferred_loads_n'][0]<=16000+1e-7
    with pytest.raises(ValueError,match='24module'):structures.preferred_support_loads(candidate,[18000.]*23)
    caps[0]=float('nan')
    with pytest.raises(ValueError,match='24module'):structures.preferred_support_loads(candidate,caps)
    feasible=structures.preferred_support_loads(candidate,18000,[2000.]*24)
    assert feasible['passed'] and min(feasible['preferred_loads_n'])>=2000-1e-7
    assert feasible['force_vector_sha256']!=result['force_vector_sha256']
    with pytest.raises(ValueError,match='lower bounds'):structures.preferred_support_loads(candidate,18000,19000)


def test_larger_crane_uses_real_radius_row_and_all_suspended_mass():
    a=structures.load();r=structures.crane_alternative(61000,a)
    assert r['chart_load_kg']==61000+3000+2600
    assert r['capacity_kg']==74900 and r['used_chart_radius_m']==26
    assert r['required_radius_m']==25 and r['radius_capacity_screen_pass'] is True
    assert r['manufacturer_max_outrigger_reaction_n']==2093000
    for soil in r['mat_area_sensitivities']:
        assert soil['minimum_area_m2']*soil['assumed_allowable_pa']==pytest.approx(2093000)
    a['construction']['crane_radius_m']=27
    assert structures.crane_alternative(1000,a)['radius_capacity_screen_pass'] is False
    assert structures.crane_alternative(75000)['radius_capacity_screen_pass'] is False


def test_axial_series_spring_uses_drilled_steel_and_discloses_coupler(candidate):
    r=structures.axial_properties(candidate);area=.14*.22-.132*.212-4*.013*.004
    assert r['axial_EA_n']==pytest.approx(2*area*200e9)
    assert 1/r['body_and_coupler_series_stiffness_n_m']==pytest.approx(17/r['axial_EA_n']+1/100e6)
    assert r['coupler_measured'] is False and r['qualified'] is False


@pytest.fixture(scope='module')
def study():return structures.study()


def test_full_package_keeps_rejected_controls_and_counted_schedules(study):
    assert study['all_implemented_screens_pass'] is False
    assert all(study[k] is False for k in structures.FLAGS)
    assert study['mechanical']['collector_splice']['passed'] is False
    assert study['mechanical']['body_spine']['passed'] is False
    assert len(study['civil']['beam_variants'])==3
    b=study['civil']['beam_variants'][0]
    assert b['gross_mass_kg']==pytest.approx(b['concrete_mass_kg']+b['reaction_rail_and_attachment_steel_mass_kg']+b['reinforcement_mass_kg']+b['strand_mass_kg'])
    assert b['construction']['crane']['screen_pass'] is False
    assert b['construction']['larger_crane_alternative']['radius_capacity_screen_pass'] is True
    assert study['manufacturing_schedule']['stages'][3]['release_strength_pa']==35e6
    assert all(q['release'] is False for q in study['qa_schedule'])
    assert all(row['quantity']>=0 for row in study['bom'])
    assert all(row['manufacturing_release'] is False for row in study['bom'])
    fixture=study['vehicle_handling']
    assert len(fixture['pick_points_m'])==10
    assert fixture['fixture_mass_kg']==pytest.approx(sum(r['mass_kg'] for r in fixture['fixture_bom']))
    assert fixture['mass_added_to_vehicle_kg']==0
    assert fixture['suspended_vehicle_and_fixture_kg']==pytest.approx(study['controlled_tare_kg']+fixture['fixture_mass_kg'])
    assert fixture['end_only_rejected_control']['maximum_moment_nm']>fixture['body_lifting_moment_nm']
    protection=study['protection_structures']
    assert protection['capture']['count']==8 and protection['capture']['unsupported_drop_screen_pass'] is False
    assert protection['braking']['braking_work_including_downgrade_j']>.5*study['controlled_aw3_kg']*25**2
    assert protection['braking']['deceleration_screen_pass'] is False
    assert protection['cross_tie']['stress_pa']==pytest.approx(50000/protection['cross_tie']['area_m2'])


def test_pile_and_spread_footing_equilibrium_independent(study):
    beam=study['civil']['beam_variants'][0];p=study['civil']['substructure_variants'][beam['id']][0]
    for scenario in p['foundations']:
        soil=scenario['soil']
        for f in scenario['alternatives']:
            if f['type']=='piled':
                assert len(f['pile_centres_m'])==len(f['pile_axial_forces_n'])==f['pile_count']
                capweight=f['cap_concrete_m3']*soil['effective_concrete_unit_weight_n_m3']
                assert sum(f['pile_axial_forces_n'])==pytest.approx(p['vertical_n']+capweight)
                x=np.array(f['pile_centres_m']);forces=np.array(f['pile_axial_forces_n']);Mx,My=p['normal_moments_nm'];amp=p['second_order_factor']
                assert np.dot(x[:,1],forces)==pytest.approx(Mx*amp)
                assert np.dot(x[:,0],forces)==pytest.approx(My*amp)
            else:
                B=f['side_m'];weight=f['concrete_m3']*soil['effective_concrete_unit_weight_n_m3']
                assert (f['qmax_pa']+f['qmin_pa'])/2*B*B==pytest.approx(p['vertical_n']+weight)
            assert f['accepted'] is False and f['soil_values_measured'] is False


def test_drawn_girder_concrete_and_source_identity(study):
    geometry=study['geometry'];b=study['civil']['beam_variants'][0]
    assert geometry['configuration_sha256']==study['configuration_sha256']
    assert sum(p['volume_m3'] for p in geometry['parts'] if p['material']=='concrete')==pytest.approx(b['concrete_volume_m3'])
    assert study['configuration_sha256'][:12] in study['drawings']['beam-section.svg']
    assert geometry['net_manufactured_solids_complete'] is False
    assert all(len(x)==64 for x in study['source_sha256'].values())


def test_publication_rejects_rehashed_quantity_and_geometry_forgery(tmp_path,monkeypatch,study):
    from hashlib import sha256
    from PIL import Image
    calls=[]
    def current(candidate=None):calls.append(True);return deepcopy(study)
    monkeypatch.setattr(structures,'study',current);structures.publish(tmp_path);calls.clear();summary=structures.read_summary(tmp_path)
    assert len(calls)==1 and summary['configuration_sha256']==study['configuration_sha256']
    def rehash(name):
        p=tmp_path/'manifest.json';m=json.loads(p.read_text());m['files_sha256'][name]=sha256((tmp_path/name).read_bytes()).hexdigest();p.write_bytes(structures.encoded(m))
    rows=json.loads((tmp_path/'bom.json').read_text());rows[0]['quantity']+=1;(tmp_path/'bom.json').write_bytes(structures.encoded(rows));rehash('bom.json')
    with pytest.raises(ValueError,match='BOM'):structures.verify(tmp_path)
    structures.publish(tmp_path)
    with Image.open(tmp_path/'section.png') as image:
        im=image.copy();im.putpixel((400,200),(0,0,0));im.save(tmp_path/'section.png')
    rehash('section.png')
    with pytest.raises(ValueError,match='pixels'):structures.verify(tmp_path)
    structures.publish(tmp_path);m=json.loads((tmp_path/'manifest.json').read_text());m['configuration_sha256']='0'*64;(tmp_path/'manifest.json').write_bytes(structures.encoded(m))
    with pytest.raises(ValueError,match='stale'):structures.verify(tmp_path)

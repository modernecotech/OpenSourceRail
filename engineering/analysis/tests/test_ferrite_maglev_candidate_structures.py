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


def test_each_section_uses_its_own_governing_train_position():
    # A single load's largest whole-beam moment occurs atmidspan. Near theend,
    # however, that same load must sit at the section being checked, notmidspan.
    case=dict(id='AW3-vertical-dynamic',modules=[dict(at_m=[0,0,0],force_n=[0,0,150000.])],target_wrench=[0,0,150000.,0,0,0])
    envelope=structures.moving_envelope(dict(cars=1),dict(cases=[case]),10.,1000.,.1)
    section=.2
    local=structures.service_moment_bounds(envelope,[section],10.,1000.)
    expected=150000.*section*(10-section)/10+1000.*section*(10-section)/2
    assert local[0][1]['moment_nm']==pytest.approx(expected)
    assert local[0][1]['train_offset_m']==pytest.approx(section)
    global_points=[(r['x_m'],r['force_n']) for r in envelope['critical_points']]
    old=structures._simple_beam((global_points,1000.),10.,[section])[2][0]
    assert local[0][1]['moment_nm']>old*1.8
    assert local[0][0]['moment_nm']==pytest.approx(1000.*section*(10-section)/2)


def test_unloaded_end_transfer_stress_cannot_be_hidden_by_midspan_train():
    # Independent closed-form fixture. The threshold deliberately lies between
    # the former wrong-position stress and the actual unloaded prestress stress.
    a=deepcopy(structures.load());c=a['concrete']
    c.update(span_m=10.,prestress_bottom_counts=[4],prestress_top_counts=[0],prestress_debond_counts=[0],service_tension_screen_pa=500000.)
    section=dict(id='oracle',width_m=1.,depth_m=1.,web_m=.1,flange_m=.2)
    case=dict(id='AW3-vertical-dynamic',modules=[dict(at_m=[0,0,0],force_n=[0,0,150000.])],target_wrench=[0,0,150000.,0,0,0])
    envelope=structures.moving_envelope(dict(cars=1),dict(cases=[case]),10.,1000.,.1)
    result=structures.prestress_design(section,envelope,1000.,a)
    stage=result['selected']['stages'][-1]
    # Four fully transferred bottom strands atx1m; no live load governs.
    A=1.-.8*.6;I=(1.-.8*.6**3)/12;Z=I/.5
    strand_z=.05+.0152/2
    force=4*.00014*1860e6*.7*.8
    moment=1000.*1.*9./2
    expected=force/A-force*(.5-strand_z)/Z+moment/Z
    assert stage['governing_minimum']['x_m']==pytest.approx(1.)
    assert stage['governing_minimum']['face']=='top'
    assert stage['minimum_compression_pa']==pytest.approx(expected)
    assert not stage['passed']
    wrong=deepcopy(envelope)
    points=[(r['x_m'],r['force_n']) for r in envelope['critical_points']]
    pattern=structures._simple_beam((points,1000.),10.,envelope['x_samples_m'])[2].tolist()
    wrong['service_moment_min_nm']=pattern;wrong['service_moment_max_nm']=pattern
    for key in ('service_min_governing_offsets_m','service_max_governing_offsets_m'):
        wrong[key]=[envelope['critical_offset_m']]*len(pattern)
    old_stage=structures.prestress_design(section,wrong,1000.,a)['selected']['stages'][-1]
    assert old_stage['passed']
    assert old_stage['minimum_compression_pa']>-500000.


def test_prestress_envelope_rejects_mismatched_span_and_unsampled_section():
    case=dict(id='AW3-vertical-dynamic',modules=[dict(at_m=[0,0,0],force_n=[0,0,100])],target_wrench=[0,0,100,0,0,0])
    envelope=structures.moving_envelope(dict(cars=1),dict(cases=[case]),25.,10.,.5)
    with pytest.raises(ValueError,match='consistent'):structures.service_moment_bounds(envelope,[1.],24.,10.)
    with pytest.raises(ValueError,match='explicitly sample'):structures.service_moment_bounds(envelope,[.01],25.,10.)


def test_interface_clearance_accepts_rotated_modules_and_rejects_reflections(candidate):
    from engineering.design_search.geometry import rigid_transform
    angle=.03;c,s=math.cos(angle),math.sin(angle)
    changed=deepcopy(candidate)
    changed['module_placements'][0]['rotation_matrix']=[[c,-s,0],[s,c,0],[0,0,1]]
    guideway=magnetics.guideway_definition(25,variant_id=candidate['variant_id'])
    result=structures.interface_clearance(changed,guideway)
    assert result['sampled_pose_count']==1
    assert result['clearance_tolerance_approved'] is False
    changed['module_placements'][0]['rotation_matrix']=[[-1,0,0],[0,1,0],[0,0,1]]
    with pytest.raises(ValueError,match='proper orthonormal'):structures.interface_clearance(changed,guideway)


def test_selected_beam_explicit_span_propagates_to_geometry_and_end_infill(candidate):
    bundle=structures.selected_beam(candidate,section_id='wider-intermediate',span_m=20.)
    beam=bundle['beam'];rail=bundle['rail_and_attachments']
    assert beam['section_id']=='wider-intermediate' and beam['span_m']==20.
    assert rail['guideway']['span_m']==20.
    assert beam['moving_load']['span_m']==20.
    assert bundle['assumptions']['concrete']['span_m']==20.
    value=dict(configuration_sha256=candidate['configuration_sha256'],assumptions=bundle['assumptions'],civil=dict(beam_variants=[beam],rail_and_attachments=rail))
    geometry=structures.geometry_definition(value,selection=bundle['selection'])
    assert geometry['span_m']==20. and geometry['section_id']=='wider-intermediate'
    concrete=[p for p in geometry['parts'] if p['material']=='concrete']
    assert sum(p['volume_m3'] for p in concrete)==pytest.approx(beam['concrete_volume_m3'])
    assert len([p for p in concrete if p['id'].startswith('girder/end-infill')])==2
    value['civil']['rail_and_attachments']['guideway']['span_m']=25.
    with pytest.raises(ValueError,match='span and candidate'):structures.geometry_definition(value,selection=bundle['selection'])


def test_selected_beam_rejects_unknown_mixed_or_unsupported_selection(candidate):
    for choice in (dict(section_id='missing',span_m=25.),dict(section_id='narrow-deep-reference',span_m=50.)):
        with pytest.raises(ValueError):structures.selected_beam(candidate,selection=choice)
    changed=deepcopy(candidate);changed['architecture']=dict(guidebeam=dict(section_id='narrow-deep-reference',span_m=20.))
    with pytest.raises(ValueError,match='architecture'):structures.selected_beam(changed,selection=dict(section_id='wider-intermediate',span_m=20.))


def test_explicit_guideway_binding_cannot_relabel_a_different_module(candidate):
    from hashlib import sha256
    changed=deepcopy(candidate);old=changed['configuration_sha256'];changed['configuration_sha256']='a'*64
    changed['source_candidate_configuration_sha256']=old
    rail=magnetics.guideway_definition(20.,variant_id=candidate['variant_id'])
    rail.update(configuration_sha256=changed['configuration_sha256'],source_configuration_sha256=old,guideway_source_module_sha256=sha256(structures.encoded(changed['module'])).hexdigest())
    changed['guideway_definition']=rail
    bound=structures.return_rail_and_attachments(changed,20.)
    assert bound['guideway']['configuration_sha256']=='a'*64
    forged=deepcopy(changed);forged['module']['parts'][0]['size_m'][0]*=2
    forged['guideway_definition']['guideway_source_module_sha256']=sha256(structures.encoded(forged['module'])).hexdigest()
    with pytest.raises(ValueError,match='changed magnetic module'):structures.return_rail_and_attachments(forged,20.)
    forged=deepcopy(changed);forged['guideway_definition']['parts'][0]['mass_kg']+=1
    with pytest.raises(ValueError,match='source module/rail/span'):structures.return_rail_and_attachments(forged,20.)


def test_trial_span_retains_exact_strand_transfer_and_debond_boundaries():
    case=dict(id='AW3-vertical-dynamic',modules=[dict(at_m=[0,0,0],force_n=[0,0,100])],target_wrench=[0,0,100,0,0,0])
    envelope=structures.moving_envelope(dict(cars=1),dict(cases=[case]),17.,100.,.5)
    for x in (1.,1.5,2.5,14.5,15.5,16.):
        assert any(abs(sample-x)<1e-12 for sample in envelope['x_samples_m'])


def diagnostic_candidate(candidate):
    base=structures.mass_properties(candidate);changed=deepcopy(candidate)
    regions=[dict(deepcopy(region),id='native/'+region['id']) for region in base['regions']]
    regions.append(structures._uniform_region('carrier/new-known-stock',100.,[7.,0.,1.],[1.,1.,1.],'Synthetic explicit known stock'))
    empty=structures._combine([r for r in regions if r['id']!='native/AW3-passengers']);laden=structures._combine(regions)
    inventory=[dict(id='carrier/new-known-stock',mass_kg=100.),dict(id='joint/unknown',mass_kg=None)]
    inventory_hash=__import__('hashlib').sha256(structures.encoded(inventory)+b'\n').hexdigest()
    changed.update(controlled_tare_kg=empty['mass_kg'],controlled_aw3_kg=laden['mass_kg'],allow_incomplete_diagnostic=True,
        design_search_bundle=dict(candidate_id=changed['configuration_sha256'],installed_inventory=inventory),
        diagnostic_mass_state=dict(candidate_id=changed['configuration_sha256'],source_inventory_sha256=inventory_hash,
            empty=empty,laden=laden,regions=regions,diagnostic_known_stock_only=True,unknown_stock_ids=['joint/unknown'],
            complete_installed_distribution=False,physical_accepted=False))
    return changed,base


def test_diagnostic_carrier_stock_keeps_real_placement_and_requires_opt_in(candidate):
    changed,base=diagnostic_candidate(candidate)
    with pytest.raises(ValueError,match='explicit diagnostic permission'):structures.mass_properties(changed)
    mass=structures.mass_properties(changed,allow_incomplete=True)
    expected=(base['laden']['mass_kg']*base['laden']['cg_m'][0]+100.*7.)/(base['laden']['mass_kg']+100.)
    assert mass['laden']['cg_m'][0]==pytest.approx(expected)
    assert mass['unlocated_retained_mass_kg']==pytest.approx(base['unlocated_retained_mass_kg'])
    assert mass['unknown_stock_ids']==['joint/unknown']
    assert mass['complete_installed_distribution'] is False
    assert mass['diagnostic_known_stock_only'] is True
    changed['allow_incomplete_diagnostic']=False
    with pytest.raises(ValueError,match='explicit diagnostic permission'):structures.mass_properties(changed,allow_incomplete=True)


def test_diagnostic_mass_source_identity_and_recomputed_regions_are_checked(candidate):
    changed,_=diagnostic_candidate(candidate)
    changed['design_search_bundle']['installed_inventory'][0]['mass_kg']=0.
    with pytest.raises(ValueError,match='mass/inventory contract'):structures.mass_properties(changed,allow_incomplete=True)
    changed,_=diagnostic_candidate(candidate)
    changed['diagnostic_mass_state']['regions'][-1]['cg_m'][0]=0.
    with pytest.raises(ValueError,match='actual known regions'):structures.mass_properties(changed,allow_incomplete=True)

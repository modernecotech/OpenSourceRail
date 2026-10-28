"""Research identities, exact primitive accounting and adversarial registry checks."""
from copy import deepcopy
import math
import pytest
from engineering.component_registry import registry as c,materials


def part(name='P',kind='box',dimensions=None,grade='AL-6082-T651-SHEET',mass=None,**kw):
    material=materials.lookup(grade)
    geometry=dict(kind=kind,dimensions_m=dimensions or [1.,2.,.01])
    volume=c.geometry_properties(geometry)['volume_m3']
    calculated=None if volume is None else volume*material['density_kg_m3']['nominal']
    if mass is None:
        mass=dict(calculated_kg=calculated,lower_bound_kg=None if volume is None else volume*material['density_kg_m3']['lower'],
          upper_bound_kg=None if volume is None else volume*material['density_kg_m3']['upper'],evidence_state='unresolved' if volume is None else 'calculated')
    return c.make_part(name,'A',['body'],geometry,material['material_id'],mass,dict(method='cutting',scrap_fraction=.1),**kw)


def registry(parts=None,occurrences=None,**kw):
    parts=parts or [part()]
    return c.make_registry('test',parts,occurrences or [c.make_occurrence('first',parts[0])],['body','braking'],**kw)


def seal(r):
    r['candidate_id']=c.identity(c._physical(r))
    for o in r['occurrences']:o['candidate_id']=r['candidate_id']
    r['registry_id']=c.identity({k:v for k,v in r.items() if k!='registry_id'})
    return r


def reseal_part(p):
    p['physical_definition_id']=c.identity(c._part_physical(p));p['revision_id']=c.identity({k:v for k,v in p.items() if k!='revision_id'})
    return p


def test_separate_part_and_occurrences_count_full_installed_multiplicity():
    p=part();r=registry([p],[c.make_occurrence('window-1',p),c.make_occurrence('window-2',p)])
    s=c.summary(r)
    assert s['unique_part_definitions']==1 and s['physical_occurrences']==2
    assert s['known_calculated_mass_kg']==pytest.approx(108.)
    assert s['mass_lower_bound_kg']==pytest.approx(107.2)
    assert s['missing_functions']==['braking']
    assert s['validation_coverage']==0 and s['price_occurrence_coverage']==0
    assert s['price_lower_bound_usd'] is None
    assert s['installed_CG_m'] is None and not s['physical_accepted']


def test_rigid_rotated_offset_primitive_inertia_and_parallel_axis():
    p=part(dimensions=[2.,1.,.5]);m=p['mass']['calculated_kg']
    a=c.make_occurrence('left',p,transform=[[0.,-1.,0.,-2.],[1.,0.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])
    b=c.make_occurrence('right',p,transform=[[1.,0.,0.,2.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])
    s=c.summary(registry([p],[a,b]));I=s['primitive_uniform_mass_inertia_kg_m2']
    assert s['primitive_uniform_mass_CG_m']==[0.,0.,0.]
    assert I[0][0]==pytest.approx(m*((4+.25)+(1+.25))/12)
    assert I[1][1]==pytest.approx(m*((1+.25)+(4+.25))/12+2*m*4)
    assert I[2][2]==pytest.approx(2*m*(4+1)/12+2*m*4)


@pytest.mark.parametrize('g,volume',[({'kind':'tube','dimensions_m':{'length':2.,'outer_radius':.2,'inner_radius':.1}},math.pi*.03*2),
 ({'kind':'cylinder','dimensions_m':{'length':2.,'radius':.2}},math.pi*.04*2),
 ({'kind':'rhs','dimensions_m':{'length':2.,'width':.2,'height':.3,'wall':.01}},2*(.2*.3-.18*.28))])
def test_net_primitives_count_cavity_and_exact_uniform_inertia(g,volume):
    x=c.geometry_properties(g,20.)
    assert x['volume_m3']==pytest.approx(volume)
    assert all(x['inertia_kg_m2'][i][i]>0 for i in range(3))


def test_purchased_envelope_mass_bounds_never_become_dense_stock_mass_or_inertia():
    p=part(kind='envelope',mass=dict(calculated_kg=None,lower_bound_kg=100.,upper_bound_kg=180.,evidence_state='bounded-estimate'))
    s=c.summary(registry([p]))
    assert s['complete_nominal_mass_kg'] is None
    assert (s['mass_lower_bound_kg'],s['mass_upper_bound_kg'])==(100.,180.)
    assert s['primitive_uniform_mass_inertia_kg_m2'] is None
    assert s['mass_occurrence_coverage']==0 and s['mass_bound_occurrence_coverage']==1


def test_unknown_mass_stays_none_in_total_and_scope():
    p=part(kind='envelope');s=c.summary(registry([p]))
    assert s['mass_lower_bound_kg'] is None and s['scopes']['vehicle']['lower_mass_kg'] is None
    assert s['known_calculated_mass_kg']==0 and s['complete_nominal_mass_kg'] is None


@pytest.mark.parametrize('mutation',[
 lambda r:r['occurrences'].append(deepcopy(r['occurrences'][0])),
 lambda r:r['occurrences'][0].update(candidate_id='f'*64),
 lambda r:r['occurrences'][0].update(part_revision_id='f'*64),
 lambda r:r['occurrences'][0].update(part_definition_id='f'*64),
 lambda r:r['occurrences'][0].update(quantity=2),
 lambda r:r['occurrences'][0].update(accounted_mass_kg=10.),
 lambda r:r['occurrences'][0].update(parent_id='missing'),
 lambda r:r['occurrences'][0].update(parent_id='first'),
 lambda r:r['parts'][0].update(physical_accepted=True),
 lambda r:r.update(complete_installed_design=True),
])
def test_resealed_mixed_duplicate_cyclic_and_promoted_records_rejected(mutation):
    r=registry();mutation(r)
    if r['occurrences'][0].get('candidate_id')=='f'*64:
        r['registry_id']=c.identity({k:v for k,v in r.items() if k!='registry_id'})
    else:seal(r)
    with pytest.raises(ValueError):c.validate_registry(r)


@pytest.mark.parametrize('pose',[
 [[2.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]],
 [[-1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]],
 [[1.,0.,0.,float('nan')],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]],
 [[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,1.,1.]],
])
def test_nonrigid_reflected_nonfinite_and_bad_frame_poses_rejected(pose):
    with pytest.raises(ValueError):c.make_occurrence('bad',part(),transform=pose)


def test_assemblies_are_massless_ownership_nodes_not_duplicate_stock():
    p=part();r=registry([p],[c.make_occurrence('first',p,parent_id='car-1')],assemblies=[{'id':'train','parent_id':None},{'id':'car-1','parent_id':'train'}])
    assert c.summary(r)['known_calculated_mass_kg']==54.
    r['assemblies'][0]['parent_id']='car-1';seal(r)
    with pytest.raises(ValueError,match='cycle'):c.validate_registry(r)


def test_density_substitution_invalidates_geometry_and_all_dependent_evaluations():
    old=registry();p=part(grade='STEEL-S355-HYPOTHESIS');new=registry([p])
    changes=c.affected_dependencies(old,new)
    assert changes['physical_revision'] and old['candidate_id']!=new['candidate_id']
    assert set(('geometry','structure','mass','propulsion','braking','civil','manufacturing','cost'))<=set(changes['invalidated_stages'])


def test_changed_price_or_mass_estimate_is_new_record_not_new_geometry():
    r=registry();p=deepcopy(r['parts'][0]);p['cost']=dict(source_class='B',currency='USD',lower_usd=10.,upper_usd=20.,source_id='engineering-process-estimate',source_date='2026-10-28',location='research-cell',quantity_basis='one-part')
    p['manufacturing']['cycle_hours']=2.;p['mass']['upper_bound_kg']+=1.;reseal_part(p)
    new=registry([p]);assert new['candidate_id']==r['candidate_id'] and new['registry_id']!=r['registry_id']
    assert not c.affected_dependencies(r,new)['physical_revision']
    assert c.summary(new)['price_upper_bound_usd']==20.


def test_false_net_geometry_mass_and_unused_part_fail_before_evaluation():
    p=part();p['mass']['calculated_kg']+=.1;reseal_part(p)
    with pytest.raises(ValueError,match='mass disagree'):registry([p])
    with pytest.raises(ValueError,match='Unused'):registry([part(),part('UNUSED')])
    with pytest.raises(ValueError,match='volume'):c.geometry_properties({'kind':'box','dimensions_m':[1.,1.,1.],'net_volume_m3':.5})


@pytest.mark.parametrize('mass',[
 dict(calculated_kg=None,lower_bound_kg=10.,upper_bound_kg=None,evidence_state='bounded-estimate'),
 dict(calculated_kg=None,lower_bound_kg=20.,upper_bound_kg=10.,evidence_state='bounded-estimate'),
 dict(calculated_kg=None,lower_bound_kg=None,upper_bound_kg=None,evidence_state='bounded-estimate'),
 dict(calculated_kg=0.,lower_bound_kg=None,upper_bound_kg=None,evidence_state='unresolved'),
])
def test_malformed_or_fictional_mass_bounds_refused(mass):
    with pytest.raises(ValueError):part(kind='envelope',mass=mass)


def test_sources_and_material_facts_are_sealed_without_promoting_allowables():
    book=materials.catalogue();assert len(book['materials'])==12
    assert len({m['family'] for m in book['materials']})>=9
    for m in book['materials']:
        assert materials.validate_material(m)
        assert m['qualified_design_allowables'] is None and m['physical_lot_id'] is None
        assert m['unit_price_usd'] is None and m['automatic_substitution_eligible'] is False
    raw=deepcopy(book['materials'][0]);raw['density_kg_m3']['nominal']=1.
    with pytest.raises(ValueError,match='identity'):materials.validate_material(raw)


def test_source_hash_and_nominal_interval_forgery_rejected_even_if_material_resealed():
    raw=materials.lookup('AL-6082-T651-SHEET');raw['source_records'][0]['document_sha256']='x'
    s=raw['source_records'][0];s['source_id']=c.identity({k:v for k,v in s.items() if k!='source_id'});raw['density_kg_m3']['source_id']=s['source_id'];raw['material_evaluation_id']=c.identity({k:v for k,v in raw.items() if k!='material_evaluation_id'})
    with pytest.raises(ValueError,match='digest'):materials.validate_material(raw)


def test_final_clear_position_does_not_hide_intermediate_swept_collision():
    p=part(dimensions=[.2,.2,.2]);a=c.make_occurrence('moving',p)
    b=c.make_occurrence('obstacle',p,transform=[[1.,0.,0.,1.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])
    r=registry([p],[a,b]);end=[[1.,0.,0.,2.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
    s=c.screen_sweep(r,'moving',end)
    assert s['potential_interference_occurrence_ids']==['obstacle'] and not s['physical_accepted']
    after=c.screen_sweep(r,'moving',end,removed_before_motion=['obstacle'])
    assert not after['potential_interference_occurrence_ids'] and not after['lifting_retention_and_flexible_services_verified']


def test_rotating_removal_uses_bounding_sphere_not_sampled_pose_clearance():
    p=part(dimensions=[2.,.2,.2]);r=registry([p]);end=[[0.,-1.,0.,0.],[1.,0.,0.,0.],[0.,0.,1.,2.],[0.,0.,0.,1.]]
    s=c.screen_sweep(r,'first',end,tool_radius_m=.1)
    assert s['method']=='conservative-enclosing-sphere-translation-and-rotation'
    assert s['swept_AABB_m']['max'][0]>1.1 and s['finite_path_checked']


def test_renaming_registry_or_mass_estimate_does_not_invent_new_geometry():
    r=registry();copy=deepcopy(r);copy['label']='Renamed review';copy['registry_id']=c.identity({k:v for k,v in copy.items() if k!='registry_id'})
    assert c.validate_registry(copy) and copy['candidate_id']==r['candidate_id']


def test_resealed_unit_change_cannot_silently_scale_installed_geometry():
    r=registry();r['coordinate_frame']['length_unit']='mm';r['registry_id']=c.identity({k:v for k,v in r.items() if k!='registry_id'})
    with pytest.raises(ValueError,match='coordinate frame'):c.validate_registry(r)


def test_corrected_same_grade_density_changes_evaluation_not_physical_candidate():
    old=registry();r=deepcopy(old);p=r['parts'][0]
    index=next(i for i,m in enumerate(r['materials']) if m['material_id']==p['material_id']);m=deepcopy(r['materials'][index])
    before_id=m['material_id'];m['density_kg_m3']['nominal']=2710.;m=materials.reseal(m)
    assert m['material_id']==before_id and m['material_evaluation_id']!=r['materials'][index]['material_evaluation_id']
    r['materials'][index]=m;p['material_evaluation_id']=m['material_evaluation_id'];p['mass']['calculated_kg']=54.2;reseal_part(p)
    r['occurrences'][0]['part_revision_id']=p['revision_id'];seal(r)
    assert c.validate_registry(r) and r['candidate_id']==old['candidate_id'] and r['registry_id']!=old['registry_id']
    changes=c.affected_dependencies(old,r)
    assert changes['material_evaluation_revision'] and not changes['physical_revision']
    assert {'mass','structure','propulsion','manufacturing','cost'}<=set(changes['invalidated_stages'])


def test_stale_material_property_evaluation_cannot_be_mixed_into_current_registry():
    r=registry();p=r['parts'][0];p['material_evaluation_id']='f'*64;reseal_part(p);r['occurrences'][0]['part_revision_id']=p['revision_id'];seal(r)
    with pytest.raises(ValueError,match='material evaluation'):c.validate_registry(r)


def test_laminate_layup_substitution_is_physical_material_revision():
    a=materials.lookup('GFRP-EGLASS-HYPOTHESIS-1');b=deepcopy(a);b['directional_model']['stacking_sequence']=[0,45,-45,90]
    b=materials.reseal(b)
    assert a['material_id']!=b['material_id'] and a['material_evaluation_id']!=b['material_evaluation_id']

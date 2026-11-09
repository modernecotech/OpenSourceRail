"""Tiny invented material/ledger fixtures only, never retained run03 adapter."""
from copy import deepcopy
from hashlib import sha256
import gzip,json
import pytest
from engineering.railway_project import terminal_component as t

def enc(x):return(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def cases(x):return dict.fromkeys(t.CASES,x)
def fixture():
 R=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]];T=[.1,.2,.3]
 base=dict(kind='box',size_m=[.02,.03,.04],at_m=T,rotation=R)
 exact=dict(id='SYNTHETIC/plate',part_id='SYNTHETIC/plate',material='al5083',geometry=base,
  holes=[dict(kind='cylinder-cut',at_m=[.1,.205,.3],axis=[0.,1.,0.],diameter_m=.002,length_m=.02,purpose='SYNTHETIC')],additional_voids=[])
 def row(name,geometry,at,R):return dict(id=name,part_id=name,material_id='al5083',geometry=geometry,at_m=at,rotation=R,frame='terminal-local-UVW',scope='installed',functions=[name],mass_kg=cases(.001),centroid_local_m=[0.,0.,0.],shape_I_per_kg=[[.1,0,0],[0,.1,0],[0,0,.1]],uncertainty_m=[.001]*3,cost_share=1.,mass_basis='SYNTHETIC allowance',inertia_basis='SYNTHETIC proxy')
 plate=row('SYNTHETIC/plate',dict(kind='envelope',size_m=[.03,.02,.04]),T,R);plate['exact_CSG_entity']=exact
 ann=row('SYNTHETIC/bush',dict(kind='annulus',size_m=[.01,.006,.006],outer_radius_m=.003,inner_radius_m=.001),[0,0,0],t.I)
 unknown=row('SYNTHETIC/unknown',dict(kind='envelope',size_m=[.004,.004,.004]),[.2,0,0],t.I)
 unknown['exact_CSG_entity']=dict(id='SYNTHETIC/unknown',part_id='SYNTHETIC/unknown',geometry=None,holes=[],required_interface_uvw_m=[.2,0,0],geometry_hold='SYNTHETIC supplier unknown')
 es=[plate,ann,unknown];groups=[dict(id='stock/'+e['id'],entity_ids=[e['id']],net_mass_kg=cases(.001),gross_mass_kg=cases(.0012),scrap_mass_kg=cases(.0002),direct_cost_usd=cases(.1),basis='SYNTHETIC',cost_basis='SYNTHETIC') for e in es]
 bindings=[dict(id='SYNTHETIC/front',at_m=[0,0,0],rotation=t.I),dict(id='SYNTHETIC/rear',at_m=[1.,0,0],rotation=[[-1.,0,0],[0,-1.,0],[0,0,1.]])]
 c=dict(definition_id=t.identity(dict(SYNTHETIC='component')),entities=es,stock_groups=groups,actual_joint_contracts=[],required_bindings=bindings,composition_admitted=False)
 src=dict(schema='SYNTHETIC-tiny-terminal',parent=deepcopy(t.PARENT),source_sha256=deepcopy(t.SOURCE_FILES),component_proposal=c,component_bindings=bindings,
  physical_definition=dict(schema='SYNTHETIC-physical',local_definition_id=c['definition_id'],fixture=True),new_welds=[],source_machining=[],old_leaf_replacements=[],floor_wear_patch=dict(automatically_applied=False),
  local_account_coverage=dict(schema='SYNTHETIC-coverage'),person_hours=dict(schema='SYNTHETIC-hours'),consumables=dict(shared_fixture=dict(quantity=1,installed=False,mass_bounds_kg=[1,2,3]),shared_extractor=dict(quantity_per_train=1,installed=False)),holds=['SYNTHETIC physical testing pending'])
 src.update({k:False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','native_eligible','selected_reference_changed','movement_authority')})
 return src

def frozen(src,monkeypatch):
 src=deepcopy(src);src['component_proposal'].pop('evaluation_id',None);src['component_proposal']=t.seal(src['component_proposal']);src.pop('evaluation_id',None);src['candidate_id']=t.identity(src['physical_definition']);src=t.seal(src)
 raw=gzip.compress(enc(src),mtime=0);pin=dict(candidate_id=src['candidate_id'],evaluation_id=src['evaluation_id'],raw_sha256=sha256(raw).hexdigest());monkeypatch.setattr(t,'SOURCE',pin)
 return raw,pin
def run(src,monkeypatch):
 raw,pin=frozen(src,monkeypatch);return t.normalize(raw,pin=pin,request_id='b'*64)

def test_finite_csg_points_bores_frames_roundtrip_without_replacing_material_with_proxy(monkeypatch):
 out=run(fixture(),monkeypatch);d=out['canonical_draft'];e=d['entities'][0];s=e['finished_spec'];base=s['normalized_material_graph']['base'];void=s['normalized_material_graph']['voids'][0]
 assert base['at_m']==pytest.approx([0,0,0]) and base['rotation']==t.I
 assert void['centre_m']==pytest.approx([.015,0,0]) and void['axis']==pytest.approx([1,0,0])
 assert void['base_m']==pytest.approx([.005,0,0]) and void['source_cut_schema']==t.SOURCE_CUT_SCHEMA
 assert s['source_exact_CSG_entity']['holes'][0]['at_m']==[.1,.205,.3]
 assert s['normalized_material_graph']['base']['kind']=='box' and s['source_packaging_proxy']['kind']=='envelope'
 assert s['packaging_is_finished_material'] is False

def test_unknown_geometry_is_named_held_and_keeps_positive_stock_without_filled_solid(monkeypatch):
 out=run(fixture(),monkeypatch);e=out['canonical_draft']['entities'][2]
 assert e['finished_spec']['normalized_material_graph'] is None and e['finished_spec']['source_exact_CSG_entity']['geometry'] is None
 assert any(w.get('entity_id')==e['id'] for w in out['canonical_draft']['unsupported_work'])
 assert e['mass_kg']['base']>0 and not out['canonical_admitted']
 assert out['canonical_draft']['schema']!='osr-composition-component/1'

def test_known_void_change_survives_physical_projection_with_same_packaging(monkeypatch):
 src=fixture();a=run(src,monkeypatch);src['component_proposal']['entities'][0]['exact_CSG_entity']['holes'][0]['diameter_m']=.003;b=run(src,monkeypatch)
 assert a['canonical_draft']['definition_id']!=b['canonical_draft']['definition_id']
 assert a['canonical_draft']['entities'][0]['geometry']==b['canonical_draft']['entities'][0]['geometry']

def test_price_metadata_changes_evaluation_not_finished_geometry_identity(monkeypatch):
 src=fixture();a=run(src,monkeypatch);src['component_proposal']['stock_groups'][0]['direct_cost_usd']=cases(.2);b=run(src,monkeypatch)
 assert a['canonical_draft']['definition_id']==b['canonical_draft']['definition_id'] and a['evaluation_id']!=b['evaluation_id']

def test_source_mass_price_inertia_and_scopes_preserved_no_body_or_floor_patch(monkeypatch):
 src=fixture();out=run(src,monkeypatch);d=out['canonical_draft']
 assert d['stock_groups']==src['component_proposal']['stock_groups']
 for a,b in zip(d['entities'],src['component_proposal']['entities']):
  for k in ('mass_kg','centroid_local_m','shape_I_per_kg','uncertainty_m','at_m','rotation','frame'):assert a[k]==b[k]
 assert out['applied_body_operations']==[] and out['floor_wear_patch_unapplied']==src['floor_wear_patch']
 assert out['lifecycle_workshop']['shared_extractor']['quantity_per_train']==1

def test_two_explicit_seam_prisms_preserve_station_to_entity_transform_and_hold_qualification(monkeypatch):
 src=fixture();e=src['component_proposal']['entities'][1];e.update(id='SYNTHETIC/seam',geometry=dict(kind='envelope',size_m=[.04,.04,.04]),physical_drawing=dict(kind='two-explicit-extruded-triangular-weld-profiles',triangle_orientation_defined=True,profile_vertices_UV_from_station_m=[[[0,0],[.003,0],[0,.003]],[[.006,0],[.009,0],[.006,.003]]],W_from_station_m=[-.01,.01],exact_triangle_orientation_and_runout_resolved=False))
 src['component_proposal']['stock_groups'][1]['entity_ids']=[e['id']];src['new_welds']=[dict(id=e['id'],at_uvw_m=[0,0,0])]
 out=run(src,monkeypatch);spec=out['canonical_draft']['entities'][1]['finished_spec']
 assert len(spec['normalized_material_graph']['pieces'])==2
 assert len(spec['normalized_material_graph']['pieces'][0]['vertices_m'])==6
 assert 'weld-runout-WPS-contact-and-load-qualification' in spec['holds']
 assert spec['source_physical_drawing']==e['physical_drawing']

def test_unoriented_weld_never_becomes_filled_packaging(monkeypatch):
 src=fixture();e=src['component_proposal']['entities'][1];e['geometry']=dict(kind='envelope',size_m=[.01,.01,.01]);e['physical_drawing']=dict(kind='triangular-weld-seams',leg_m=.001,local_segments_m=[[[0,0,0],[0,.005,0]]],exact_triangle_orientation_and_runout_resolved=False)
 out=run(src,monkeypatch);s=out['canonical_draft']['entities'][1]['finished_spec']
 assert s['normalized_material_graph'] is None and any('orientation' in h for h in s['holds'])

def test_blind_joint_cannot_become_resolved_through_stack_or_drop_obligation(monkeypatch):
 src=fixture();j=dict(id='SYNTHETIC/blind',kind='blind-threaded-endplate',axis=0,direction=-1,origin_m=[0,0,0],stack=dict(layers=[dict(start_m=0.,end_m=.005)],pilot_depth_m=.009,thread_engagement_m=.007,remaining_pilot_bound_m=.001,liner_ID_m=.0045,liner_OD_m=.006))
 src['component_proposal']['actual_joint_contracts']=[j];out=run(src,monkeypatch);d=out['canonical_draft'];contract=d['required_counterpart_obligations'][0]
 assert d['required_counterpart_ids']==[contract['id']] and contract['source_contract']==j and contract['resolved'] is False
 assert contract['schema']!='osr-coaxial-through-stack/1' and d['joint_dispositions'][j['id']]['status']=='unresolved-normalization'

@pytest.mark.parametrize('change',[lambda s:s['component_proposal']['stock_groups'].append(deepcopy(s['component_proposal']['stock_groups'][0])),lambda s:s['component_proposal']['stock_groups'][0]['net_mass_kg'].update(base=0.),lambda s:s['component_proposal']['entities'][0].update(rotation=[[-1.,0,0],[0,1.,0],[0,0,1.]]),lambda s:s.update(physical_accepted=True),lambda s:s['component_proposal']['entities'][0]['uncertainty_m'].__setitem__(0,-.1)])
def test_duplicate_stock_unknown_zero_reflection_and_promotion_fail_closed(monkeypatch,change):
 src=fixture();change(src);raw,pin=frozen(src,monkeypatch)
 with pytest.raises(ValueError):t.normalize(raw,pin=pin,request_id='b'*64)

def test_raw_source_request_and_parent_mismatch_fail_closed(monkeypatch):
 raw,pin=frozen(fixture(),monkeypatch)
 with pytest.raises(ValueError):t.normalize(raw+b'bad',pin=pin,request_id='b'*64)
 with pytest.raises(ValueError):t.normalize(raw,pin=pin,request_id='not-an-identity')
 src=fixture();src['parent']['candidate_id']='0'*64;raw,pin=frozen(src,monkeypatch)
 with pytest.raises(ValueError,match='Mixed'):t.normalize(raw,pin=pin,request_id='b'*64)

def test_union_difference_and_additional_voids_preserved_in_same_source_frame(monkeypatch):
 src=fixture();old=src['component_proposal']['entities'][0]['exact_CSG_entity'];box=deepcopy(old['geometry']);small=deepcopy(box);small['size_m']=[.005,.005,.005]
 old['geometry']=dict(kind='difference',outer=dict(kind='union-material',pieces=[box]),void=small);old['additional_voids']=[small]
 out=run(src,monkeypatch);g=out['canonical_draft']['entities'][0]['finished_spec']['normalized_material_graph']
 assert g['base']['kind']=='difference' and g['base']['outer']['kind']=='union-material'
 assert len(g['additional_voids'])==1 and g['additional_voids'][0]['at_m']==pytest.approx([0,0,0])

def test_invalid_cut_axis_and_unknown_solid_are_named_holds_not_erased(monkeypatch):
 src=fixture();src['component_proposal']['entities'][0]['exact_CSG_entity']['geometry']['kind']='SYNTHETIC-unsupported'
 out=run(src,monkeypatch);s=out['canonical_draft']['entities'][0]['finished_spec']
 assert s['normalized_material_graph'] is None and s['source_exact_CSG_entity']['geometry']['kind']=='SYNTHETIC-unsupported'
 src=fixture();src['component_proposal']['entities'][0]['exact_CSG_entity']['holes'][0]['axis']=[1,1,0]
 out=run(src,monkeypatch);assert any('Unit source cut axis' in w['required_work'] for w in out['canonical_draft']['unsupported_work'])

def test_rhs_and_finite_profile_normalize_without_geometry_replacement(monkeypatch):
 src=fixture();g=src['component_proposal']['entities'][0]['exact_CSG_entity']['geometry'];g.update(kind='rhs',wall_m=.002)
 out=run(src,monkeypatch);assert out['canonical_draft']['entities'][0]['finished_spec']['normalized_material_graph']['base']['wall_m']==.002
 g.pop('wall_m');g.pop('size_m');g.update(kind='profile-prism',length_m=.01,points_yz_m=[[0.,0.],[.003,0.],[0.,.003]])
 out=run(src,monkeypatch);assert out['canonical_draft']['entities'][0]['finished_spec']['normalized_material_graph']['base']['points_yz_m']==g['points_yz_m']

def test_self_intersecting_profile_and_broken_ordered_stack_fail_truthfully(monkeypatch):
 src=fixture();g=src['component_proposal']['entities'][0]['exact_CSG_entity']['geometry'];g.pop('size_m');g.update(kind='profile-prism',length_m=.01,points_yz_m=[[0,0],[.004,.003],[0,.004],[.003,0]])
 out=run(src,monkeypatch);assert any('Selfintersecting' in w['required_work'] for w in out['canonical_draft']['unsupported_work'])
 src=fixture();src['component_proposal']['actual_joint_contracts']=[dict(id='SYNTHETIC/badstack',kind='ordered-through-stack',axis=0,direction=1,origin_m=[0,0,0],stack=dict(layers=[dict(start_m=.001,end_m=.003)]))]
 raw,pin=frozen(src,monkeypatch)
 with pytest.raises(ValueError,match='Ordered'):t.normalize(raw,pin=pin,request_id='b'*64)

def test_unsupported_drawing_parameters_survive_identity_even_while_held(monkeypatch):
 src=fixture();e=src['component_proposal']['entities'][1];e['physical_drawing']=dict(kind='revolved-frustum',height_m=.0024,small_radius_m=.002,large_radius_m=.004)
 a=run(src,monkeypatch);e['physical_drawing']['large_radius_m']=.0042;b=run(src,monkeypatch)
 assert a['canonical_draft']['definition_id']!=b['canonical_draft']['definition_id']
 assert b['canonical_draft']['entities'][1]['finished_spec']['normalized_material_graph'] is None
 assert any('frustum' in w['required_work'] for w in b['canonical_draft']['unsupported_work'])

def test_boolean_joint_direction_is_not_a_rigid_axis_value(monkeypatch):
 src=fixture();src['component_proposal']['actual_joint_contracts']=[dict(id='SYNTHETIC/bool',kind='ordered-through-stack',axis=0,direction=True,origin_m=[0,0,0])]
 raw,pin=frozen(src,monkeypatch)
 with pytest.raises(ValueError,match='axis'):t.normalize(raw,pin=pin,request_id='b'*64)

def test_hold_and_geometry_hold_notes_are_evaluation_only_with_complete_originals(monkeypatch):
 src=fixture();src['component_proposal']['entities'][0]['exact_CSG_entity']['geometry_hold']='SYNTHETIC assessment'
 a=run(src,monkeypatch);src['component_proposal']['entities'][0]['exact_CSG_entity']['geometry_hold']=None
 b=run(src,monkeypatch)
 assert a['canonical_draft']['definition_id']==b['canonical_draft']['definition_id']
 assert a['evaluation_id']!=b['evaluation_id']
 d=deepcopy(a['canonical_draft']);before=t.identity(t.physical_projection(d))
 d['entities'][0]['finished_spec']['holds']=[]
 assert t.identity(t.physical_projection(d))==before
 assert a['canonical_draft']['entities'][0]['finished_spec']['source_exact_CSG_entity']['geometry_hold']=='SYNTHETIC assessment'

def test_joint_status_and_strength_review_do_not_change_declared_physical_contract(monkeypatch):
 src=fixture();src['component_proposal']['actual_joint_contracts']=[dict(id='SYNTHETIC/blind',kind='blind-threaded-endplate',axis=0,direction=-1,origin_m=[0,0,0],stack=dict(layers=[dict(start_m=0.,end_m=.005)],pilot_depth_m=.009,thread_engagement_m=.007,remaining_pilot_bound_m=.001,liner_ID_m=.0045,liner_OD_m=.006,strength_qualified=False))]
 a=run(src,monkeypatch);src['component_proposal']['actual_joint_contracts'][0]['stack']['strength_qualified']=True;b=run(src,monkeypatch)
 assert a['canonical_draft']['definition_id']==b['canonical_draft']['definition_id'] and a['evaluation_id']!=b['evaluation_id']
 d=deepcopy(a['canonical_draft']);before=t.identity(t.physical_projection(d));j=d['required_counterpart_obligations'][0]
 j.update(status='SYNTHETIC reviewed',validation_scope='changed assessment',resolved=True,physical_accepted=True)
 assert t.identity(t.physical_projection(d))==before
 j['source_contract']['stack']['thread_engagement_m']-=.0001
 assert t.identity(t.physical_projection(d))!=before

def test_process_price_source_hash_changes_are_evaluation_only(monkeypatch):
 src=fixture();e=src['component_proposal']['entities'][0]['exact_CSG_entity'];e.update(old_entity_sha256='1'*64,process_h=.1,QA_h=.05,price_USD=2.)
 a=run(src,monkeypatch);e.update(old_entity_sha256='2'*64,process_h=.2,QA_h=.1,price_USD=3.);b=run(src,monkeypatch)
 assert a['canonical_draft']['definition_id']==b['canonical_draft']['definition_id'] and a['evaluation_id']!=b['evaluation_id']

@pytest.mark.parametrize('mutation',[
 lambda e:e['finished_spec']['source_exact_CSG_entity']['geometry']['size_m'].__setitem__(0,.021),
 lambda e:e['finished_spec']['source_exact_CSG_entity']['holes'][0].update(diameter_m=.003),
 lambda e:e.update(material_id='SYNTHETIC-steel'),
 lambda e:e['finished_spec']['source_exact_CSG_entity'].update(unknown_physical_port_geometry={'kind':'unsupported-but-required','size_m':None}),
 lambda e:e['finished_spec'].update(source_physical_drawing={'kind':'unsupported','root_faces_m':None,'nominal_edge_m':.007}),
])
def test_known_and_unknown_physical_facts_stay_in_projection(monkeypatch,mutation):
 d=run(fixture(),monkeypatch)['canonical_draft'];before=t.identity(t.physical_projection(d));mutation(d['entities'][0])
 assert t.identity(t.physical_projection(d))!=before

@pytest.mark.parametrize('axis',[[1.,0.,0.],[-1.,0.,0.],[0.,1.,0.],[0.,-1.,0.],[0.,0.,1.],[0.,0.,-1.]])
def test_cylinder_base_signed_axis_to_centre_and_proper_frame_endpoints(axis):
 base=[.11,.22,.33];T=[.1,.2,.3];R=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]];L=.012
 h=dict(kind='cylinder-cut',at_m=base,axis=axis,diameter_m=.006,length_m=L,purpose='SYNTHETIC through wall base')
 g=t.source_cuts([h],T,R,schema=t.SOURCE_CUT_SCHEMA)[0]
 assert g['base_m']==pytest.approx(t.local(base,T,R))
 assert g['centre_m']==pytest.approx(t.local([base[k]+axis[k]*L/2 for k in range(3)],T,R))
 far=t.local([base[k]+axis[k]*L for k in range(3)],T,R)
 assert [g['centre_m'][k]+g['axis'][k]*L/2 for k in range(3)]==pytest.approx(far)
 assert [g['centre_m'][k]-g['axis'][k]*L/2 for k in range(3)]==pytest.approx(g['base_m'])
 assert g['source_cut']==h

def test_ambiguous_source_cut_position_conventions_are_held_not_inferred():
 h=dict(kind='cylinder-cut',at_m=[0.,0.,0.],axis=[1.,0.,0.],diameter_m=.006,length_m=.012,purpose='SYNTHETIC')
 with pytest.raises(ValueError,match='BASE'):t.source_cuts([h],[0,0,0],t.I,schema='SYNTHETIC-centre')
 h['centre_m']=[.006,0,0]
 with pytest.raises(ValueError,match='schema'):t.source_cuts([h],[0,0,0],t.I)

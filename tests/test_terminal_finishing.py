"""Invented13→2 source records, no retained input/helper use."""
from copy import deepcopy
from hashlib import sha256
import math,unittest
from engineering.railway_project import terminal_finishing as m

def H(x):return sha256(x.encode()).hexdigest()
def srcseal(x):return dict(deepcopy(x),evaluation_id=m.noLF(x))
def C(a,b=None,c=None):return dict(low=a,base=a if b is None else b,high=a if c is None else c)
def cyl(L,r,T):return dict(axis=0,centre_m=list(T),length_m=L,radius_m=r)
PTS=[(y,z) for z in(-.555,.555) for y in(-.6,-.2,.2,.6)]+[(y,z) for y in(-.805,.805) for z in(-.25,.25)]

def fixture():
 es=[];ops=[];ps=[];hp=[];hg='INVENTED/hpstock';rg='INVENTED/ringstock'
 for i,(y,z) in enumerate(PTS):
  eid='INVENTED/hp/'+str(i);hp.append(eid);T=[.0395,y,z];box=dict(kind='box',at_m=T,rotation=deepcopy(m.I),size_m=[.012,.025,.025]);old=dict(kind='cylinder-cut',at_m=[.0335,y,z],axis=[1.,0.,0.],diameter_m=.006,length_m=.012,purpose='INVENTED through');g=dict(id=eid,material='al5083',geometry=box,holes=[old],geometry_hold=None);es.append(dict(id=eid,material_id='al5083',frame=m.FRAME,at_m=T,rotation=deepcopy(m.I),exact_CSG_entity=g,uncertainty_m=[.02]*3))
  th=dict(kind='thread-bounded-cut',at_m=[.0455,y,z],axis=[-1.,0.,0.],major_diameter_m=.008,pilot_diameter_m=.007,pitch_m=.001,depth_m=.0087,depth_tolerance_m=.0003,full_thread_depth_m=.0077,flat_bottom=True);u=dict(kind='union',pieces=[old,th]);op=dict(id='INVENTED/op/'+str(i),source_entity_id=eid,source_stock_owner_id=hg,frame=m.FRAME,units='m',paid_blank_retained_once=True,remaining_net_mass_and_CG=None,source_complete_void_union=u,minimum_circular_cut_union=[cyl(.0036,.003,[.0353,y,z]),cyl(.0084,.0035,[.0413,y,z])],maximum_circular_cut_union=[cyl(.003,.003,[.035,y,z]),cyl(.009,.004,[.041,y,z])],source_operation=dict(kind='hardpoint-thread-pocket',material='al5083',source_geometry=deepcopy(g),cost_USD=C(.1)));ops.append(op);ps.append(dict(id=op['id'],source_entity_id=eid,source_stock_owner_id=hg,complete_void_union=deepcopy(u)))
 T=[.0485,0.,0.];o=dict(kind='box',at_m=T,rotation=deepcopy(m.I),size_m=[.006,1.7,1.2]);ap=dict(kind='box',at_m=T,rotation=deepcopy(m.I),size_m=[.006,1.56,1.06]);holes=[dict(kind='cylinder-cut',at_m=[.0455,y,z],axis=[1.,0.,0.],diameter_m=.0055,length_m=.006,purpose='INVENTED oldport') for y,z in PTS];g=dict(id='INVENTED/ring',material='al5083',geometry=dict(kind='difference',outer=o,void=ap),holes=holes,geometry_hold=None);es.append(dict(id=g['id'],material_id='al5083',frame=m.FRAME,at_m=T,rotation=deepcopy(m.I),exact_CSG_entity=g,uncertainty_m=[.02]*3));u=dict(kind='union',pieces=[ap]+holes+[dict(h,diameter_m=.012,purpose='INVENTED newport') for h in holes]);op=dict(id='INVENTED/ringop',source_entity_id=g['id'],source_stock_owner_id=rg,frame=m.FRAME,units='m',paid_blank_retained_once=True,remaining_net_mass_and_CG=None,source_complete_void_union=u,minimum_circular_cut_union=[cyl(.006,.005975,[.0485,y,z]) for y,z in PTS],maximum_circular_cut_union=[cyl(.006,.006025,[.0485,y,z]) for y,z in PTS],source_operation=dict(kind='ring-access-port-enlargement',source_cylinder_position_convention='at_m is base; signed axis points into cut',material='al5083',source_geometry=deepcopy(g),cost_USD=C(.1),access_diameter_m=.012,diameter_tolerance_m=.00005,axis_position_tolerance_m=.0001,blank_owner_count=1,new_stock_purchase_count=0,cut_count=12));ops.append(op);ps.append(dict(id=op['id'],source_entity_id=g['id'],source_stock_owner_id=rg,complete_void_union=deepcopy(u),diameter_tolerance_m=.00005,axis_position_tolerance_m=.0001))
 V=.012*.025**2-math.pi*.003**2*.012;r=4.523893421169303e-7;R=.006*(1.7*1.2-1.56*1.06)-12*math.pi*.00275**2*.006
 gs=[dict(id=hg,entity_ids=hp,net_mass_kg=C((V-r)*2660*12,(V-r/2)*2660*12,V*2660*12),gross_mass_kg=C(.029**2*.012*2660*12),direct_cost_usd=C(1,2,3),original_source_account_person_h=None,source_account=dict(quantity=12,density_cases_kg_m3=[2660]*3,net_before_extra_machining_each_m3=V,additional_drill_removal_each_m3=dict(insert_pocket_extra_unknown_interval_m3=[0.,r]))),dict(id=rg,entity_ids=['INVENTED/ring'],net_mass_kg=C(R*2660),gross_mass_kg=C(6.6),direct_cost_usd=C(10,20,30),original_source_account_person_h=None,source_account=dict(quantity=1,density_cases_kg_m3=[2660]*3))]
 for entity in es:
  source=entity['exact_CSG_entity']['geometry'];outer=source['outer'] if source['kind']=='difference' else source;entity['geometry']=dict(kind='envelope',size_m=deepcopy(outer['size_m']))
 for operation,physical in zip(ops,ps):
  source=operation['source_operation'];source.update(id=operation['id'],source_entity_id=operation['source_entity_id'],source_stock_owner_id=operation['source_stock_owner_id'],complete_void_union=deepcopy(operation['source_complete_void_union']))
  physical.update(kind=source['kind'],source_material_geometry=dict(geometry=deepcopy(source['source_geometry']['geometry']),holes=deepcopy(source['source_geometry']['holes'])))
  if source['kind']=='hardpoint-thread-pocket':source.update(maximum_pocket_depth_m=.009,minimum_annular_rear_web_m=.003);physical.update(maximum_pocket_depth_m=.009,minimum_annular_rear_web_m=.003)
  else:physical.update(material='al5083',access_diameter_m=source['access_diameter_m'],diameter_tolerance_m=source['diameter_tolerance_m'],axis_position_tolerance_m=source['axis_position_tolerance_m'])
 phy=dict(INVENTED=True,entities=[e['exact_CSG_entity'] for e in es]);raw=m.seal(dict(candidate_id=m.identity(phy),physical_definition=deepcopy(phy)));common=dict(candidate_id=raw['candidate_id'],evaluation_id=raw['evaluation_id'],raw_sha256=H('INVENTEDraw'));t=dict(schema='osr-terminal-canonical-normalization-packet/1',source_pin=deepcopy(common),source_physical_definition=phy,canonical_draft=dict(entities=es,stock_groups=gs));w=dict(schema='osr-terminal-finite-full-revision-proposal/1',source_pin=deepcopy(common),source_proposal=raw,physical_definition=dict(INVENTED=True),final_changed_parent_entities={},accounting=dict(parent_stock_owner_revisions={},transaction_applied=False));orig=srcseal(dict(candidate_id=m.noLF({'INVENTED':True}),physical_definition={'INVENTED':True},parent=deepcopy(common),prototypes=dict(INVENTED=dict(materials={'al5083':[2580.2,2660.,2739.8]}))));h=dict(schema='osr-terminal-hardware-component-normalization/1',source_original_definition=orig,source_candidate_id=orig['candidate_id'],source_evaluation_id=orig['evaluation_id'],physical_definition=dict(source_finishing=ps),canonical_draft=dict(required_source_finishing=ops,source_finishing_owner_dispositions=[dict(source_owner_id=g['id'],source=deepcopy(g),operation_ids=[x['id'] for x in ops if x['source_stock_owner_id']==g['id']],paid_blank_count=1,stock_purchase_count=0,source_mass_and_moment_update_applied=False) for g in gs]),source_owner_transactions_applied=False,lifecycle_allocations=[dict(id='INVENTED/tools',count_per_train=1,piece_count=12)])
 return refresh(t,w,h)

def refresh(t,w,h):
 for x in [t,w,h]:x.pop('evaluation_id',None)
 w['physical_definition_id']=m.identity(w['physical_definition']);h['component_geometry_id']=m.identity(h['physical_definition']);o=h['source_original_definition'];o=srcseal({k:v for k,v in o.items() if k!='evaluation_id'});h['source_original_definition']=o;h['source_evaluation_id']=o['evaluation_id'];t,w,h=[m.seal(x) for x in [t,w,h]];pin=dict(schema='osr-terminal-finishing-input-pin/1',sources={k:dict(evaluation_id=x['evaluation_id'],raw_sha256=H(k+'file')) for k,x in [('terminal',t),('weld',w),('hardware',h)]});return t,w,h,pin

def run(f):return m.rebuild(*f[:3],input_pin=f[3],request_id=H('INVENTEDrequest'))
def change(f,fn):t,w,h,p=deepcopy(f);fn(t,w,h,p);return refresh(t,w,h)
def inside(x,b):return b[0]<=x<=b[1]

def revised_geometry(f,which,edit):
 t,w,h,p=deepcopy(f);edit(t['canonical_draft']['entities'][which]['exact_CSG_entity']);c=t['canonical_draft']['entities'][which]['exact_CSG_entity'];phy=deepcopy(t['source_physical_definition']);phy['entities'][which]=deepcopy(c);raw=m.seal(dict(candidate_id=m.identity(phy),physical_definition=deepcopy(phy)));common=dict(candidate_id=raw['candidate_id'],evaluation_id=raw['evaluation_id'],raw_sha256=H('INVENTED-revised-geometry'));t['source_physical_definition']=phy;t['source_pin']=deepcopy(common);w['source_pin']=deepcopy(common);w['source_proposal']=raw;h['source_original_definition']['parent']=deepcopy(common);h['canonical_draft']['required_source_finishing'][which]['source_operation']['source_geometry']=deepcopy(c);h['physical_definition']['source_finishing'][which]['source_material_geometry']=dict(geometry=deepcopy(c['geometry']),holes=deepcopy(c['holes']));return refresh(t,w,h)

class FinishingTests(unittest.TestCase):
 def bad(self,fn):
  f=change(fixture(),fn);before=deepcopy(f)
  with self.assertRaises((ValueError,KeyError)):run(f)
  self.assertEqual(f,before)
 def test13parents2owners(self):
  r=run(fixture());self.assertEqual(r['counts'],dict(finishing_operations=13,material_occurrences=13,hardpoints=12,backing_rings=1,paid_owner_groups=2,new_stock_purchases=0));self.assertTrue(all(o['paid_blank_group_count']==1 and o['new_stock_purchase_count']==0 for o in r['source_owner_conservation']))
 def test_complete_hp_volume_independent_formula(self):
  b=run(fixture())['pending_draft_replacements'][0]['complete_material_rebuild']['bounded_properties']['mass_interval_kg'];self.assertTrue(inside((.012*.025**2-math.pi*(.003**2*.003+.004**2*.009))*2660,b));self.assertTrue(inside((.012*.025**2-math.pi*(.003**2*.0036+.0035**2*.0084))*2660,b))
 def test_oldpocket_not_debited_again(self):
  o=run(fixture())['source_owner_conservation'][0];self.assertGreater(o['complete_rebuilt_net_mass_interval_kg'][0],o['source_owner_ancestry']['net_mass_kg']['base']);self.assertEqual(o['source_direct_price_retained_once'],C(1,2,3));self.assertFalse(o['source_price_credit'])
 def test_ring_tight_mass_matches_formula(self):
  b=run(fixture())['pending_draft_replacements'][-1]['complete_material_rebuild']['bounded_properties']['mass_interval_kg'];V=.006*(1.7*1.2-1.56*1.06);self.assertTrue(inside((V-12*math.pi*.006025**2*.006)*2660,b));self.assertTrue(inside((V-12*math.pi*.005975**2*.006)*2660,b));self.assertLess(b[1]-b[0],.000362)
 def test_independent_mixeddiameter_ring_CG(self):
  b=run(fixture())['pending_draft_replacements'][-1]['complete_material_rebuild']['bounded_properties']['nominal_datum'];vs=[math.pi*(.006025 if z>0 else .005975)**2*.006 for y,z in PTS];V=.006*(1.7*1.2-1.56*1.06)-sum(vs);Cz=-sum(v*z for v,(_,z) in zip(vs,PTS))/V;self.assertNotEqual(Cz,0.);self.assertTrue(inside(Cz,b['centroid_interval_m'][2]))
 def test_combined_radius_axis_position_extreme_is_enclosed(self):
  b=run(fixture())['pending_draft_replacements'][-1]['complete_material_rebuild']['bounded_properties']['nominal_datum'];base=.006*(1.7*1.2-1.56*1.06);lo=math.pi*.005975**2*.006;hi=math.pi*.006025**2*.006;vs=[lo if z>0 else hi for y,z in PTS];V=base-sum(vs);F=-sum(v*(z-.0001) for v,(_,z) in zip(vs,PTS));actual=F/V;radius_only_upper=-sum((lo if z>0 else hi)*z for y,z in PTS)/(base-12*hi);self.assertGreater(actual,radius_only_upper);self.assertTrue(inside(actual,b['centroid_interval_m'][2]))
 def test_parallel_translation_origin_inertia_witness(self):
  b=run(fixture())['pending_draft_replacements'][-1]['complete_material_rebuild']['bounded_properties']['with_source_position_uncertainty'];L=.006;r=.006;Vo=L*1.7*1.2;Va=L*1.56*1.06;v=math.pi*r*r*L;V=Vo-Va-12*v;F=[V*.0485,0.,0.];Q=[[0.]*3 for _ in range(3)];Q[0][0]=V*(.0485**2+L**2/12);Q[1][1]=Vo*1.7**2/12-Va*1.56**2/12-sum(v*(y*y+r*r/4) for y,z in PTS);Q[2][2]=Vo*1.2**2/12-Va*1.06**2/12-sum(v*(z*z+r*r/4) for y,z in PTS);D=[.019,-.017,.013];QQ=[[Q[i][j]+D[i]*F[j]+D[j]*F[i]+V*D[i]*D[j] for j in range(3)] for i in range(3)]
  for i in range(3):
   for j in range(3):value=2660*(sum(QQ[k][k] for k in range(3) if k!=i) if i==j else -QQ[i][j]);self.assertTrue(inside(value,b['inertia_about_terminal_origin_interval_kg_m2'][i][j]))
 def test_full_radial_axial_secondmoment_support(self):
  b=run(fixture())['pending_draft_replacements'][-1]['complete_material_rebuild']['bounded_properties']['nominal_datum'];Vo=.006*1.7*1.2;Va=.006*1.56*1.06;r=.006;Qy=Vo*1.7**2/12-Va*1.56**2/12-sum(math.pi*r*r*.006*(y*y+r*r/4) for y,z in PTS);Qz=Vo*1.2**2/12-Va*1.06**2/12-sum(math.pi*r*r*.006*(z*z+r*r/4) for y,z in PTS);self.assertTrue(inside((Qy+Qz)*2660,b['inertia_about_terminal_origin_interval_kg_m2'][0][0]))
 def test_uncertainties_are_separate_and_no_exactpoint(self):
  r=run(fixture());b=r['pending_draft_replacements'][-1]['complete_material_rebuild']['bounded_properties'];self.assertEqual(b['source_position_uncertainty_m'],[.02]*3);self.assertTrue(inside(.0485+.019,b['with_source_position_uncertainty']['centroid_interval_m'][0]));self.assertIsNone(b['nominal_datum']['exact_point_CG_m']);self.assertIsNone(b['nominal_datum']['centroidal_tensor_kg_m2']);self.assertTrue(r['pending_draft_replacements'][-1]['complete_material_rebuild']['axis_position_interpretation']['evaluation_hypothesis'])
 def test_threadphase_nonzero_radial_CG_support(self):
  b=run(fixture())['pending_draft_replacements'][0]['complete_material_rebuild']['bounded_properties']['nominal_datum']['centroid_interval_m'][1];self.assertLess(b[0],-.6);self.assertGreater(b[1],-.6)
 def test_derived_envelopes_not_physical_ID(self):
  r=run(fixture());self.assertNotIn('minimum_material_graph',r['physical_definition']['parents'][-1]);self.assertIn('source_declared_finishing',r['physical_definition']['parents'][-1])
 def test_Hdensity_ancestry_not_parent_debit(self):
  f=fixture();a=run(f);b=run(change(f,lambda t,w,h,p:h['source_original_definition']['prototypes']['INVENTED']['materials'].update(al5083=[1000,2000,5000])));self.assertEqual(a['component_geometry_id'],b['component_geometry_id']);self.assertEqual(a['source_owner_conservation'],b['source_owner_conservation']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])
 def test_price_evaluation_only(self):
  f=fixture();a=run(f);b=run(change(f,lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0]['source_operation'].update(cost_USD=C(3.))));self.assertEqual(a['component_geometry_id'],b['component_geometry_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])
 def test_pose_uncertainty_evaluation_only(self):
  f=fixture();a=run(f);b=run(change(f,lambda t,w,h,p:t['canonical_draft']['entities'][0].update(uncertainty_m=[.03]*3)));self.assertEqual(a['component_geometry_id'],b['component_geometry_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])
 def test_unknown_process_overlap_preserved(self):
  r=run(fixture());self.assertTrue(r['manufacturing_accounts']['process_overlap_hold']);self.assertFalse(r['manufacturing_accounts']['complete_installed_cost']);self.assertEqual(len(r['manufacturing_accounts']['H_finishing_allowance_records']),13);self.assertTrue(all(o['source_owner_ancestry']['original_source_account_person_h'] is None for o in r['source_owner_conservation']))
 def test_input_immutable_noadmission(self):
  f=fixture();old=deepcopy(f);r=run(f);self.assertEqual(old,f);self.assertIsNone(r['canonical_definition']);self.assertTrue(all(r[k] is False for k in m.FLAGS));self.assertEqual(r['manufacturing_accounts']['shared_tools_lifecycle_reference'][0]['count_per_train'],1)
 def test_parentdensity_disagreement_refuses(self):
  def edit(t,w,h,p):
   for g in [t['canonical_draft']['stock_groups'][0],h['canonical_draft']['source_finishing_owner_dispositions'][0]['source']]:g['source_account']['density_cases_kg_m3']=[2580.2,2660,2739.8]
  self.bad(edit)
 def test_doubledebit_oldledger_refuses(self):
  def edit(t,w,h,p):
   for g in [t['canonical_draft']['stock_groups'][0],h['canonical_draft']['source_finishing_owner_dispositions'][0]['source']]:g['net_mass_kg']={c:g['net_mass_kg'][c]-.004 for c in m.CASES}
  self.bad(edit)
 def test_duplicate_operation_refuses(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'].append(deepcopy(h['canonical_draft']['required_source_finishing'][0])))
 def test_duplicate_paidowner_refuses(self):self.bad(lambda t,w,h,p:h['canonical_draft']['source_finishing_owner_dispositions'].__setitem__(1,deepcopy(h['canonical_draft']['source_finishing_owner_dispositions'][0])))
 def test_weld_parent_overlap_refuses(self):self.bad(lambda t,w,h,p:w['final_changed_parent_entities'].update({'INVENTED/hp/0':{}}))
 def test_weld_owner_overlap_refuses(self):self.bad(lambda t,w,h,p:w['accounting']['parent_stock_owner_revisions'].update({'INVENTED/hpstock':{}}))
 def test_second_ring_purchase_refuses(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][-1]['source_operation'].update(new_stock_purchase_count=12))
 def test_oldvoid_missing_refuses(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0]['source_complete_void_union']['pieces'].pop(0))
 def test_wrong_circular_union_refuses(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0]['minimum_circular_cut_union'][0].update(radius_m=.004))
 def test_fake_point_properties_refuse(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0].update(remaining_net_mass_and_CG=[1,0,0]))
 def test_wrongframe_refuses(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0].update(frame='body'))
 def test_negative_knownprice_refuses(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0]['source_operation'].update(cost_USD=C(-1.)))
 def test_unknown_price_stays_unknown(self):
  r=run(change(fixture(),lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0]['source_operation'].update(cost_USD=None)));self.assertIsNone(r['manufacturing_accounts']['H_finishing_allowance_records'][0]['source_H_allowance'])
 def test_bad_terminal_physical_refuses(self):self.bad(lambda t,w,h,p:t['source_physical_definition'].update(lie=True))
 def test_bad_hardware_physical_refuses(self):self.bad(lambda t,w,h,p:h['source_original_definition']['physical_definition'].update(lie=True))
 def test_stale_pin_refuses(self):
  f=fixture();f[3]['sources']['weld']['evaluation_id']=H('wrong')
  with self.assertRaises(ValueError):run(f)
 def test_complete_minmax_graphs_retain_oldfullthrough(self):
  r=run(fixture())['pending_draft_replacements'][0]['complete_material_rebuild']
  for graph in [r['minimum_material_graph'],r['maximum_material_graph']]:self.assertEqual(graph['cuts'][0]['length_m'],.012);self.assertEqual(graph['cuts'][0]['radius_m'],.003);self.assertEqual(graph['cuts'][0]['kind'],'finite-cylinder-void')
 def test_bad_material_refuses(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0]['source_operation'].update(material='steel'))
 def test_nonboolean_paid_flag_refuses(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0].update(paid_blank_retained_once=1))
 def test_nonboolean_rotation_refuses(self):
  self.bad(lambda t,w,h,p:t['canonical_draft']['entities'][0]['rotation'][0].__setitem__(0,True))
 def test_complete_authenticated_ring_operation_field_roster_supported(self):
  # Invented identities/geometry/rates; key roster follows the read-only b42 schema.
  t,w,h,p=fixture();o=h['canonical_draft']['required_source_finishing'][-1]['source_operation']
  o.update(mode='INVENTED new-build ring',operations=['INVENTED fixture and enlarge'],person_QA_h=[.1,.2,.4],person_process_h=[.2,.4,.8],source_credit_USD=0.,original_paid_blank_retained=True,independent_cut_union_and_mass_update_required=True,stock_mass_application='INVENTED prospective once-only debit',incremental_removed_volume_bounds_m3=[0.,.001],incremental_removed_mass_bounds_kg=[0.,1.],incremental_removed_first_moment_bounds_kg_m=[[0.,1.]]*3,incremental_removed_centroid_box_m=[[-1.,-1.,-1.],[1.,1.,1.]],moment_basis='INVENTED bounded moments',nominal_removed_centroid_m=[.0485,0.,0.],process_time_basis={'INVENTED':True},unchanged_original_voids=True)
  expected={'access_diameter_m','axis_position_tolerance_m','blank_owner_count','complete_void_union','cost_USD','cut_count','diameter_tolerance_m','id','incremental_removed_centroid_box_m','incremental_removed_first_moment_bounds_kg_m','incremental_removed_mass_bounds_kg','incremental_removed_volume_bounds_m3','independent_cut_union_and_mass_update_required','kind','material','mode','moment_basis','new_stock_purchase_count','nominal_removed_centroid_m','operations','original_paid_blank_retained','person_QA_h','person_process_h','process_time_basis','source_credit_USD','source_cylinder_position_convention','source_entity_id','source_geometry','source_stock_owner_id','stock_mass_application','unchanged_original_voids'}
  self.assertEqual(set(o),expected);r=run(refresh(t,w,h));self.assertEqual(r['counts']['backing_rings'],1);self.assertIsNone(r['canonical_definition'])
 def test_signed_base_ring_convention_required_and_exact(self):
  for value in ('at_m is centre',None,True):
   f=change(fixture(),lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][-1]['source_operation'].update(source_cylinder_position_convention=value));before=deepcopy(f)
   with self.subTest(value=value),self.assertRaisesRegex(ValueError,'signed-BASE'):run(f)
   self.assertEqual(f,before)
 def test_physical_ring_diameter_tolerance_reviewer_witness_refused(self):
  f=change(fixture(),lambda t,w,h,p:h['physical_definition']['source_finishing'][-1].update(diameter_tolerance_m=.001));before=deepcopy(f)
  with self.assertRaisesRegex(ValueError,'bound-driving parameter'):run(f)
  self.assertEqual(f,before)
 def test_all_declared_physical_tolerances_bind_evaluated_domain(self):
  for index,field,value in [(-1,'access_diameter_m',.014),(-1,'axis_position_tolerance_m',.001),(0,'maximum_pocket_depth_m',.010),(0,'minimum_annular_rear_web_m',.002)]:
   f=change(fixture(),lambda t,w,h,p:h['physical_definition']['source_finishing'][index].update({field:value}))
   with self.subTest(field=field),self.assertRaisesRegex(ValueError,'bound-driving parameter'):run(f)
 def test_physical_counts_bind_source_counts(self):
  for field,value in [('cut_count',13),('blank_owner_count',2),('new_stock_purchase_count',1)]:
   f=change(fixture(),lambda t,w,h,p:h['physical_definition']['source_finishing'][-1].update({field:value}))
   with self.subTest(field=field),self.assertRaisesRegex(ValueError,'count differs'):run(f)
 def test_unhandled_physical_operation_field_refused(self):self.bad(lambda t,w,h,p:h['physical_definition']['source_finishing'][-1].update(extra_physical_feature={'kind':'slot'}))
 def test_evaluated_tolerance_with_unchangedphysical_refused(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][-1]['source_operation'].update(diameter_tolerance_m=.001))
 def test_consistent_but_unsupported_tolerance_domain_refused(self):
  def edit(t,w,h,p):h['physical_definition']['source_finishing'][-1]['diameter_tolerance_m']=.001;h['canonical_draft']['required_source_finishing'][-1]['source_operation']['diameter_tolerance_m']=.001
  self.bad(edit)
 def test_resealed_unknown_outer_void_reviewer_witness_refused(self):
  f=revised_geometry(fixture(),0,lambda c:c['geometry'].update(extra_physical_void=dict(kind='finite-cylinder-void',radius_m=.002,length_m=.012)));before=deepcopy(f)
  with self.assertRaisesRegex(ValueError,'Closed source box'):run(f)
  self.assertEqual(f,before)
 def test_unknown_source_geometry_fields_refused_at_alllevels(self):
  variants=[(0,lambda c:c.update(extra_physical_void={})),(-1,lambda c:c['geometry']['outer'].update(extra_physical_void={})),(-1,lambda c:c['geometry']['void'].update(features=[{'kind':'bore'}])),(-1,lambda c:c['geometry'].update(extra_physical_void={}))]
  for i,edit in variants:
   f=revised_geometry(fixture(),i,edit)
   with self.subTest(index=i),self.assertRaises(ValueError):run(f)
 def test_unknown_source_operation_geometry_declaration_refused(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0]['source_operation'].update(extra_physical_void={}))
 def test_physical_source_geometry_mismatch_refused(self):self.bad(lambda t,w,h,p:h['physical_definition']['source_finishing'][0]['source_material_geometry']['geometry']['size_m'].__setitem__(0,.02))
 def test_complete_nominal_source_geometry_binds_physicalID(self):
  f=fixture();r=run(f)
  for row in r['physical_definition']['parents']:
   e=next(e for e in f[0]['canonical_draft']['entities'] if e['id']==row['id']);self.assertEqual(row['nominal_source_geometry'],dict(material_id='al5083',geometry=e['exact_CSG_entity']['geometry'],holes=e['exact_CSG_entity']['holes']))
 def test_valid_relocated_material_changes_nominal_physical_identity(self):
  f=fixture();a=run(f)
  def edit(c):
   c['geometry']['at_m'][1]+=.01;c['holes'][0]['at_m'][1]+=.01
  # The source geometry is valid but operation/pose remains stale; refusal proves no silent relocation.
  g=revised_geometry(f,0,edit)
  with self.assertRaises(ValueError):run(g)
 def test_unknown_physical_feature_in_packaging_not_silently_used(self):self.bad(lambda t,w,h,p:t['canonical_draft']['entities'][0]['geometry'].update(extra_physical_void={}))
 def test_contradictory_packaging_size_refused(self):self.bad(lambda t,w,h,p:t['canonical_draft']['entities'][0]['geometry']['size_m'].__setitem__(0,.02))
 def test_outward_arithmetic(self):
  a=m.times([.1,.2],[-3.,4.]);self.assertLessEqual(a[0],-.6);self.assertGreaterEqual(a[1],.8)

if __name__=='__main__':unittest.main()

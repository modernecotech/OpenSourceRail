"""Tiny invented source-contract fixtures only; no retained candidate producer."""
from copy import deepcopy
from hashlib import sha256
import json
import unittest
from engineering.railway_project import terminal_revision as m

I = [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
def H(s):return sha256(s.encode()).hexdigest()
def cases(x):return dict(low=x,base=x,high=x)
def source_seal(x):return dict(deepcopy(x),evaluation_id=sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest())
def entity(eid,pid=None):
 csg=dict(id=eid.removeprefix('legacy/'),geometry=dict(kind='box',size_m=[.01,.01,.01],at_m=[0.,0.,0.],rotation=deepcopy(I)),holes=[])
 return dict(id=eid,part_id=pid or 'research/'+eid,material_id='al5083',at_m=[0.,0.,0.],rotation=deepcopy(I),frame=m.FRAME,scope='installed',geometry=dict(kind='box',size_m=[.01,.01,.01]),exact_CSG_entity=csg,mass_kg=cases(.00266),unknown_finished_geometry=False)
def group(oid,e,pid=None):
 return dict(id=oid,entity_ids=[e['id']],direct_cost_usd=cases(1.),net_m3=1e-6,net_mass_kg=cases(.00266),gross_mass_kg=cases(.003),source_account=dict(part_id=pid or e['part_id'],quantity=1,density_cases_kg_m3=[2660.,2660.,2660.]))
def physical(e):return {k:deepcopy(e[k]) for k in ('id','material_id','geometry','at_m','rotation')}


def fixture(conflict=False):
 parent='legacy/P' if conflict else 'B'
 es=[entity('legacy/P'),entity('legacy/Q'),entity('B'),entity('legacy/N','body/nut'),entity('legacy/G','research/guard'),entity('W1'),entity('W2')]
 E={e['id']:e for e in es};G={e['id']:group('g/'+e['id'],e) for e in es}
 raw=m.seal(dict(candidate_id=H('localphysical'),units='m',invented=True))
 common=dict(candidate_id=raw['candidate_id'],evaluation_id=raw['evaluation_id'],raw_sha256=H('tiny-raw'))
 source_physical=dict(exact_legacy_CSG=[deepcopy(e['exact_CSG_entity']) for e in es if e['id'].startswith('legacy/')],added_entities=[dict(physical(e),part_id=e['part_id']) for e in es if not e['id'].startswith('legacy/')])
 t=dict(schema=m.SCHEMAS['terminal'],source_pin=common,source_parent=dict(candidate_id=H('P1'),evaluation_id=H('P1-eval'),raw_sha256=H('P1-raw')),
  canonical_draft=dict(entities=es,stock_groups=list(G.values()),bindings=[dict(id='terminal/front',car=0,source_end='body/terminal-end/end-0',at_m=[0.,0.,2.25],rotation=[[-1.,0.,0.],[0.,-1.,0.],[0.,0.,1.]]),dict(id='terminal/rear',car=5,source_end='body/terminal-end/end-5',at_m=[105.25,0.,2.25],rotation=deepcopy(I))],source_account_coverage=dict(complete_account_retained_unchanged=True,residual_unknown=True)),
  source_physical_definition=source_physical,old_leaf_replacements_train_once=[dict(source_part_id='body/nut',source_ids=['source/'+H('P1frontnut'),'source/'+H('P1rearnut')],old_count=2,retained_original_price_once=False)],lifecycle_workshop=dict(fixture=dict(quantity=1,scope='project',unknown_machine_time=None)),source_holds=['tiny inherited terminal hold'],canonical_admitted=False)
 filler=dict(id='F1',material_id='al5083',vertices_terminal_m=[[0.,0.,0.],[.001,0.,0.],[0.,.001,0.],[0.,0.,.01],[.001,0.,.01],[0.,.001,.01]])
 revised=deepcopy(E[parent]);revised['geometry']['finite_void_prisms']=[dict(kind='triangle',vertices_m=[[0.,0.,0.],[.001,0.,0.],[0.,.001,0.]])]
 rg=deepcopy(G[parent]);rg['net_mass_kg']=cases(.00265)
 connector=entity('K');cg=group('g/K',connector);cg['quantity']=1
 fw=dict(id=G['W1']['id'],entity_ids=['F1'],quantity=1,direct_cost_usd=cases(.4),net_mass_kg=cases(.0001))
 w=dict(schema=m.SCHEMAS['weld'],source_pin=common,source_proposal=raw,
  physical_definition=dict(changed_parents=[physical(revised)],filler=[filler],new_parts=[physical(connector)]),
  source_routes={'W1':{},'W2':{}},defined_welds=['W1'],held=[dict(source_weld_id='W2',old_source_retained=True,phase='parent-preparation',reason='finite face held')],
  parent_preparation_receipts={'W1':dict(pieces=[dict(id='F1')])},final_changed_parent_entities={parent:revised},new_part_entities={'K':connector},
  parent_cut_unions={parent:dict(new_removed_volume_m3=1e-9,cases={c:dict(removed_mass_kg=2.66e-6) for c in m.CASES})},
  accounting=dict(transaction_applied=False,old_weld_dispositions=[dict(source_weld_id='W1',old_owner_id=G['W1']['id'],old_owner_sha256=m.identity(G['W1']),replacement_owner_id=G['W1']['id'],status='defined-one-for-one-replacement'),dict(source_weld_id='W2',old_owner_id=G['W2']['id'],old_owner_sha256=m.identity(G['W2']),replacement_owner_id=None,status='held-original')],
   filler_replacement_owners={'W1':fw},parent_stock_owner_revisions={G[parent]['id']:dict(source_owner=deepcopy(G[parent]),replacement_owner=rg,paid_gross_count=1,material_purchase_delta_USD=cases(0.),changed_parent_ids=[parent])},new_stock_owners={'g/K':cg}),
  source_policy=dict(materials={'al5083':dict(density_bounds_kg_m3=[2500.,2800.],density_kg_m3=2660.)}),holds=['tiny WPS hold'],canonical_definition=None,canonical_admitted=False)
 hparts=[];hgroups=[];mapping={};oldrows=[]
 for old,subparts in [('legacy/N',['nut','compound']),('legacy/G',['guard'])]:
  placement='hardware/'+old;ids=[]
  for sub in subparts:
   eid=placement+'/'+sub;p=dict(id=eid,material_id='al5083',frame=m.FRAME,at_m=[.1,0.,0.],rotation=deepcopy(I),part_definition=dict(geometry=dict(kind='box',size_m=[.001,.002,.003]),unknown_thread_phase=None))
   hparts.append(p);ids.append(eid)
  mapping[placement]=ids
  hgroups.append(dict(id='new/'+placement,entity_ids=ids,source_owner_group_id=G[old]['id'],old_occurrence_id=old,procurement_quantity=1,old_material_or_price_added=False,direct_cost_label_cases_USD=cases(.25),parts_are_subtotals_not_extra_payable_rows=True,source_key_map=None))
  oldrows.append(dict(source_owner_id=G[old]['id'],canonical_source_key_map=None,status='REQUIRED_NOT_APPLIED',source=dict(source_group=deepcopy(G[old]),source_group_id=G[old]['id'],old_entity_ids=[old],successor_ids=[placement],once_only=True,applied=False,source_price_not_added=True)))
 fin=[];pfin=[];fowners=[]
 for eid,kind in [('legacy/P','hardpoint-thread-pocket'),('legacy/Q','ring-access-port-enlargement')]:
  oid=G[eid]['id'];opid='finish/'+eid;void=dict(kind='union',pieces=[dict(kind='cylinder-cut',at_m=[0.,0.,0.],axis=[1.,0.,0.],diameter_m=.001,length_m=.003)])
  op=dict(id=opid,source_entity_id=eid,source_stock_owner_id=oid,frame=m.FRAME,units='m',paid_blank_retained_once=True,remaining_net_mass_and_CG=None,source_complete_void_union=void,incremental_removed_mass_bounds_kg=[1e-5,2e-5],incremental_removed_volume_bounds_m3=[1e-9,2e-9],source_operation=dict(kind=kind,material='al5083',source_geometry=deepcopy(E[eid]['exact_CSG_entity']),cost_USD=cases(.1)))
  fin.append(op);pfin.append(dict(id=opid,source_entity_id=eid,source_stock_owner_id=oid,complete_void_union=deepcopy(void),kind=kind))
  fowners.append(dict(source_owner_id=oid,source=deepcopy(G[eid]),operation_ids=[opid],paid_blank_count=1,stock_purchase_count=0,source_mass_and_moment_update_applied=False))
 original=source_seal(dict(candidate_id=H('hardwarephysical'),parent=common,prototypes={'fixture':dict(materials={'al5083':dict(density_kg_m3=[2580.2,2660.,2739.8])})}))
 h=dict(schema=m.SCHEMAS['hardware'],source_original_definition=original,source_candidate_id=original['candidate_id'],source_evaluation_id=original['evaluation_id'],source_owner_transactions_applied=False,
  canonical_draft=dict(entities=deepcopy(hparts),stock_groups=hgroups,old_stock_owner_dispositions=oldrows,required_source_finishing=fin,source_finishing_owner_dispositions=fowners),
  physical_definition=dict(entities=deepcopy(hparts),source_finishing=pfin,frame=m.FRAME,units='m',interfaces=[]),mapping=mapping,
  counts=dict(material_pieces=3,placements=2,new_stock_groups=2,old_owner_groups=2,finishing_paid_owner_groups=2,finishing_source_occurrences=2,source_finishing_operations=2,paid_backing_rings=1,shared_service_tool_pieces=12),
  original_source_contracts_and_holds=['tiny hardware thread held'],lifecycle_allocations=[dict(id='shared-kit',scope='train/workshop',count_per_train=1,charged_in_installed_stock=False,source=dict(piece_count=12,parts=[dict(id='tool/'+str(i)) for i in range(12)])),dict(id='repair',scope='event',charged_in_installed_stock=False,event_frequency=None,source=dict(mass=None))],canonical_definition=None,canonical_admitted=False)
 return refresh(t,w,h)


def refresh(t,w,h):
 for obj in [t,w,h]:obj.pop('evaluation_id',None)
 w['physical_definition_id']=m.identity(w['physical_definition']);h['component_geometry_id']=m.identity(h['physical_definition'])
 original=h['source_original_definition'];original=source_seal({k:v for k,v in original.items() if k!='evaluation_id'});h['source_original_definition']=original;h['source_evaluation_id']=original['evaluation_id']
 t,w,h=[m.seal(x) for x in [t,w,h]]
 counts=dict(terminal_entities=7,terminal_stock_groups=7,weld_routes=2,defined_welds=1,held_welds=1,filler_pieces=1,revised_parents=1,new_connectors=1,old_hardware_owners=2,hardware_placements=2,hardware_material_pieces=3,hardware_stock_groups=2,finishing_operations=2,finishing_paid_groups=2,finishing_source_occurrences=2,paid_backing_ring_groups=1,shared_service_tool_pieces=12,inherited_P1_owner_groups=1,local_research_hardware_owner_groups=1,local_material_occurrences=9,local_stock_groups=8)
 pin=dict(schema='osr-terminal-local-revision-input-pin/1',sources={k:dict(evaluation_id=x['evaluation_id'],raw_sha256=H(k+'-file'),source_commit='a'*40) for k,x in [('terminal',t),('weld',w),('hardware',h)]},expected_counts=counts)
 return t,w,h,pin


def run(f,**kwargs):return m.plan_revision(*f[:3],input_pin=f[3],request_id=H('new-request'),**kwargs)

def change(f,fn):
 t,w,h,pin=deepcopy(f);fn(t,w,h,pin);return refresh(t,w,h)


class TerminalRevisionTests(unittest.TestCase):
 def test_local_conservation_counts(self):
  r=run(fixture());self.assertEqual(r['counts']['local_material_occurrences'],9);self.assertEqual(r['counts']['local_stock_groups'],8);self.assertEqual(r['deployment_quantity_multiplier_applied'],1)
 def test_inputs_unmodified(self):
  f=fixture();before=deepcopy(f);run(f);self.assertEqual(f,before)
 def test_old_hardware_owner_ledger(self):
  r=run(fixture());ls=[x for x in r['replacement_ledger'] if x['kind']=='replace-local-hardware-owner'];self.assertEqual(len(ls),2);self.assertEqual({e for x in ls for e in x['old_entity_ids']},{'legacy/N','legacy/G'})
 def test_P1_retirement_inherited_once(self):
  r=run(fixture());self.assertEqual([x['new_P1_retirement_count'] for x in r['inherited_P1_retirements']],[0,0]);self.assertEqual(len(r['P1_old_leaf_retirement_ledger_owned_once_by_terminal']),1)
 def test_research_group_no_P1_predecessor(self):
  x=next(x for x in run(fixture())['inherited_P1_retirements'] if x['source_part_id']=='research/guard');self.assertEqual(x['source_keys'],[])
 def test_held_source_material_and_price_retained(self):
  r=run(fixture());es={x['id']:x for x in r['canonical_local_draft']['entities']};gs={x['id']:x for x in r['canonical_local_draft']['stock_groups']};self.assertIn('W2',es);self.assertEqual(gs['g/W2']['direct_cost_usd'],cases(1.));self.assertEqual(len(r['held_weld_records']),1)
 def test_weld_owner_replaced_once(self):
  r=run(fixture());es={x['id'] for x in r['canonical_local_draft']['entities']};self.assertNotIn('W1',es);self.assertIn('F1',es);self.assertEqual(sum(x['owner_id']=='g/W1' for x in r['pricing']['rows']),1)
 def test_finishing_two_paid_groups_no_new_blank(self):
  r=run(fixture());self.assertEqual(r['finishing_paid_owner_ids'],['g/legacy/P','g/legacy/Q']);self.assertEqual(len(r['source_finishing_records']),2);self.assertTrue(all(x['remaining_net_mass_and_CG'] is None for x in r['source_finishing_records']))
 def test_finished_parent_does_not_reuse_source_point_properties(self):
  r=run(fixture());e=next(x for x in r['canonical_local_draft']['entities'] if x['id']=='legacy/P');g=next(x for x in r['canonical_local_draft']['stock_groups'] if x['id']=='g/legacy/P');self.assertIsNone(e['mass_kg']);self.assertIsNone(e['center_of_gravity_m']);self.assertIsNone(e['inertia_kg_m2']);self.assertEqual(e['source_material_before_finishing']['mass_kg'],cases(.00266));self.assertIsNone(g['net_mass_kg']);self.assertEqual(g['source_paid_group_before_finishing']['net_mass_kg'],cases(.00266));self.assertEqual(g['direct_cost_usd'],cases(1.))
 def test_unknown_properties_stay_unknown(self):
  r=run(fixture());self.assertIsNone(r['mass_properties']['aggregate_mass_kg']);self.assertIsNone(r['mass_properties']['aggregate_CG_m']);self.assertIsNone(r['mass_properties']['aggregate_inertia_kg_m2']);self.assertIsNone(r['canonical_definition'])
 def test_all_approval_flags_false(self):
  r=run(fixture());self.assertTrue(all(r[k] is False for k in m.FLAGS));self.assertFalse(r['source_transactions_applied'])
 def test_reprice_changes_evaluation_not_physical(self):
  f=fixture();r=run(f);g=change(f,lambda t,w,h,p:h['canonical_draft']['stock_groups'][0].update(direct_cost_label_cases_USD=cases(2.)));rr=run(g);self.assertNotEqual(r['evaluation_id'],rr['evaluation_id']);self.assertEqual(r['local_component_geometry_id'],rr['local_component_geometry_id'])
 def test_price_raw_file_and_source_pin_not_geometry(self):
  f=fixture();r=run(f);f[3]['sources']['hardware']['raw_sha256']=H('new-file');f[3]['sources']['hardware']['source_commit']='b'*40;rr=run(f);self.assertEqual(r['local_component_geometry_id'],rr['local_component_geometry_id']);self.assertNotEqual(r['evaluation_id'],rr['evaluation_id'])
 def test_changed_hardware_physical_dimension_changes_geometry(self):
  f=fixture();r=run(f)
  def edit(t,w,h,p):
   for x in [h['physical_definition']['entities'][0],h['canonical_draft']['entities'][0]]:x['part_definition']['geometry']['size_m'][0]=.002
  rr=run(change(f,edit));self.assertNotEqual(r['local_component_geometry_id'],rr['local_component_geometry_id'])
 def test_opaque_physical_fields_retained(self):
  f=fixture();rr=run(change(f,lambda t,w,h,p:h['physical_definition']['entities'][0]['part_definition'].update(domain={'basis':'physical unknown port','holds':{'clearance_m':.002}})));p=next(x for x in rr['physical_definition']['material_occurrences'] if x['id']=='hardware/legacy/N/nut');self.assertEqual(p['physical_record']['part_definition']['domain']['holds']['clearance_m'],.002)
 def test_deployment_pose_not_local_geometry(self):
  f=fixture();a=run(f);b=run(change(f,lambda t,w,h,p:t['canonical_draft']['bindings'][1]['at_m'].__setitem__(0,110.)));self.assertEqual(a['local_component_geometry_id'],b['local_component_geometry_id']);self.assertEqual(a['counts'],b['counts']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])
 def test_overlay_is_held_without_overwrite(self):
  r=run(fixture(True));self.assertTrue(any(x['kind']=='combined-cut-union-required' for x in r['pending_contracts']));p=next(x for x in r['physical_definition']['material_occurrences'] if x['id']=='legacy/P');self.assertIn('finite_void_prisms',p['base_material']['physical_record']['geometry']);self.assertEqual(len(p['machining_union_operands']),1)
 def union(self,f):
  r=run(f);h=next(x for x in r['pending_contracts'] if x['kind']=='combined-cut-union-required');return dict(h['detail'],id=h['subject'],schema='osr-terminal-explicit-cut-union/1',set_operation='weld-revised-material minus union-of-complete-finishing-voids')
 def test_explicit_union_is_preserved_but_not_solved(self):
  f=fixture(True);u=self.union(f);r=run(f,combined_cut_unions=[u]);self.assertTrue(any(x['kind']=='combined-cut-union-evaluation-pending' for x in r['pending_contracts']));self.assertFalse(any(x['kind']=='combined-cut-union-required' for x in r['pending_contracts']));self.assertIsNone(r['canonical_definition'])
 def test_union_stale_or_missing_operand_refused(self):
  f=fixture(True)
  for key,value in [('weld_parent_physical_sha256',H('stale')),('source_parent_physical_sha256',H('wrong-source')),('finishing_operand_sha256s',[])]:
   u=self.union(f);u[key]=value;before=deepcopy(f)
   with self.subTest(key=key),self.assertRaises(ValueError):run(f,combined_cut_unions=[u])
   self.assertEqual(f,before)
 def test_extra_union_refused(self):
  f=fixture(True);u=self.union(f);u['id']='B'
  with self.assertRaises(ValueError):run(f,combined_cut_unions=[u])
 def bad(self,edit):
  f=change(fixture(),edit);before=deepcopy(f)
  with self.assertRaises((ValueError,KeyError)):run(f)
  self.assertEqual(f,before)
 def test_duplicate_finishing_operation_refused(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'].append(deepcopy(h['canonical_draft']['required_source_finishing'][0])))
 def test_duplicate_old_hardware_owner_refused(self):self.bad(lambda t,w,h,p:h['canonical_draft']['old_stock_owner_dispositions'].append(deepcopy(h['canonical_draft']['old_stock_owner_dispositions'][0])))
 def test_duplicate_new_stock_refused(self):self.bad(lambda t,w,h,p:h['canonical_draft']['stock_groups'].append(deepcopy(h['canonical_draft']['stock_groups'][0])))
 def test_missing_hardware_piece_refused(self):self.bad(lambda t,w,h,p:h['canonical_draft']['entities'].pop())
 def test_unowned_filler_refused(self):self.bad(lambda t,w,h,p:w['physical_definition']['filler'].append(dict(id='extra',material_id='al5083',vertices_terminal_m=[])))
 def test_missing_parent_owner_refused(self):self.bad(lambda t,w,h,p:w['accounting']['parent_stock_owner_revisions'].clear())
 def test_same_blank_bought_twice_refused(self):self.bad(lambda t,w,h,p:w['accounting']['parent_stock_owner_revisions']['g/B'].update(paid_gross_count=2))
 def test_new_parent_purchase_refused(self):self.bad(lambda t,w,h,p:w['accounting']['parent_stock_owner_revisions']['g/B'].update(material_purchase_delta_USD=cases(.2)))
 def test_changed_source_epoch_refused(self):self.bad(lambda t,w,h,p:h['source_original_definition']['parent'].update(raw_sha256=H('wrong')))
 def test_stale_input_pin_refused(self):
  f=fixture();f[3]['sources']['terminal']['evaluation_id']=H('wrong')
  with self.assertRaises(ValueError):run(f)
 def test_stale_evaluation_refused(self):
  f=fixture();f[0]['lifecycle_workshop']['new']=None
  with self.assertRaises(ValueError):run(f)
 def test_wrong_units_refused(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0].update(units='mm'))
 def test_boolean_counts_refused(self):
  f=fixture();f[3]['expected_counts']['weld_routes']=True
  with self.assertRaises(ValueError):run(f)
 def test_boolean_pose_refused(self):
  def edit(t,w,h,p):
   for x in [h['physical_definition']['entities'][0],h['canonical_draft']['entities'][0]]:x['at_m'][0]=True
  self.bad(edit)
 def test_reflection_refused(self):
  def edit(t,w,h,p):
   for x in [h['physical_definition']['entities'][0],h['canonical_draft']['entities'][0]]:x['rotation'][0][0]=-1.
  self.bad(edit)
 def test_density_mismatch_is_pending_not_zero(self):
  r=run(change(fixture(),lambda t,w,h,p:w['parent_cut_unions']['B']['cases']['low'].update(removed_mass_kg=2.5e-6)));self.assertTrue(any(x['kind']=='applied-cut-density-context-unresolved' for x in r['pending_contracts']));self.assertIsNone(r['mass_properties']['aggregate_mass_kg'])
 def test_dormant_global_density_is_not_applied_cut_failure(self):
  r=run(fixture());self.assertFalse(any(x['kind']=='applied-cut-density-context-unresolved' for x in r['pending_contracts']));self.assertTrue(any(x['kind']=='density-context-unresolved' for x in r['pending_contracts']))
 def test_nonfinite_density_refused(self):
  f=fixture();f[1]['parent_cut_unions']['B']['cases']['base']['removed_mass_kg']=float('nan')
  with self.assertRaises(ValueError):run(f)
 def test_lifecycle_shared_kit_not_doubled(self):self.bad(lambda t,w,h,p:h['lifecycle_allocations'][0].update(count_per_train=2))
 def test_lifecycle_cannot_be_installed(self):self.bad(lambda t,w,h,p:h['lifecycle_allocations'][0].update(charged_in_installed_stock=True))
 def test_unknown_lifecycle_frequency_preserved(self):self.assertIsNone(run(fixture())['lifecycle_allocations']['hardware'][1]['event_frequency'])
 def test_fake_finished_pointCG_refused(self):self.bad(lambda t,w,h,p:h['canonical_draft']['required_source_finishing'][0].update(remaining_net_mass_and_CG=[0.,0.,0.]))
 def test_unknown_price_not_zero(self):
  r=run(change(fixture(),lambda t,w,h,p:h['canonical_draft']['stock_groups'][0].update(direct_cost_label_cases_USD=None)));row=next(x for x in r['pricing']['rows'] if x['owner_id']=='new/hardware/legacy/N');self.assertIsNone(row['direct_cost_label_cases_USD']);self.assertFalse(r['complete_installed_cost'])
 def test_negative_price_refused(self):self.bad(lambda t,w,h,p:h['canonical_draft']['stock_groups'][0].update(direct_cost_label_cases_USD=cases(-1.)))
 def test_reused_hardware_piece_refused(self):self.bad(lambda t,w,h,p:h['mapping']['hardware/legacy/G'].append(h['mapping']['hardware/legacy/N'][0]))
 def test_hardware_applied_status_refused(self):self.bad(lambda t,w,h,p:h['canonical_draft']['old_stock_owner_dispositions'][0].update(status='APPLIED'))
 def test_hardware_transaction_already_applied_refused(self):self.bad(lambda t,w,h,p:h.update(source_owner_transactions_applied=True))
 def test_weld_transaction_already_applied_refused(self):self.bad(lambda t,w,h,p:w['accounting'].update(transaction_applied=True))
 def test_P1_retirement_missing_refused(self):self.bad(lambda t,w,h,p:t['old_leaf_replacements_train_once'].clear())
 def test_research_cannot_invent_P1_retirement(self):self.bad(lambda t,w,h,p:t['old_leaf_replacements_train_once'].append(dict(source_part_id='research/guard',source_ids=['source/'+H('fake')],old_count=1,retained_original_price_once=False)))
 def test_duplicate_source_physical_refused(self):self.bad(lambda t,w,h,p:t['source_physical_definition']['exact_legacy_CSG'].append(deepcopy(t['source_physical_definition']['exact_legacy_CSG'][0])))
 def test_approval_cannot_be_inherited(self):self.bad(lambda t,w,h,p:w.update(physical_accepted=True))
 def test_boolean_paid_quantity_refused(self):self.bad(lambda t,w,h,p:w['accounting']['filler_replacement_owners']['W1'].update(quantity=True))
 def test_boolean_hardware_declared_count_refused(self):self.bad(lambda t,w,h,p:h['counts'].update(paid_backing_rings=True))
 def test_boolean_shared_tool_pieces_refused(self):self.bad(lambda t,w,h,p:h['lifecycle_allocations'][0]['source'].update(piece_count=True))
 def test_duplicate_P1_source_key_refused(self):self.bad(lambda t,w,h,p:t['old_leaf_replacements_train_once'][0]['source_ids'].__setitem__(1,t['old_leaf_replacements_train_once'][0]['source_ids'][0]))
 def test_stale_P1_retirement_count_refused(self):self.bad(lambda t,w,h,p:t['old_leaf_replacements_train_once'][0].update(old_count=3))
 def test_extra_physical_finishing_refused(self):self.bad(lambda t,w,h,p:h['physical_definition']['source_finishing'].append(deepcopy(h['physical_definition']['source_finishing'][0])))
 def test_unknown_group_price_has_named_pending_contract(self):
  r=run(change(fixture(),lambda t,w,h,p:h['canonical_draft']['stock_groups'][0].update(direct_cost_label_cases_USD=None)));self.assertTrue(any(x['kind']=='unknown-price-component' for x in r['pending_contracts']))
 def test_request_identity_is_evaluation_only(self):
  f=fixture();a=run(f);b=m.plan_revision(*f[:3],input_pin=f[3],request_id=H('differentrequest'));self.assertEqual(a['local_component_geometry_id'],b['local_component_geometry_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])
 def test_whole_record_json_validity(self):
  f=fixture();f[3]['sources']['terminal']['raw_sha256']='wrong'
  with self.assertRaises(ValueError):run(f)

if __name__=='__main__':unittest.main()

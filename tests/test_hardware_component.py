"""Invented local records only; no retained source/producer imports."""
from copy import deepcopy
import math
import unittest
from unittest.mock import patch
from engineering.railway_project import hardware_component as h

def box(size,at=(0.,0.,0.)):return dict(kind='box',size_m=list(size),at_m=list(at),rotation=deepcopy(h.I))
def ann(L=.004,D=.012,d=.006,at=(0.,0.,0.)):return dict(kind='annulus',length_m=L,outer_diameter_m=D,inner_diameter_m=d,at_m=list(at),rotation=deepcopy(h.I))
def reseal(x):x.pop('evaluation_id',None);x['evaluation_id']=h.source_identity(x);return x
MATS={k:dict(density_kg_m3=[2.,3.,4.],USD_kg=[3.,5.,7.]) for k in ('al5083','invented-steel','EPDM-cellular-unqualified')}
RATES=dict(labour_USD_h=[1.,2.,3.],machine_USD_h=[2.,4.,6.],QA_USD_h=[3.,6.,9.],overhead_fraction=[.1,.2,.3])
def part(g=None,net=None,material='invented-steel'):
    g=deepcopy(g or ann());V=math.pi/4*(.012**2-.006**2)*.004 if net is None else net
    return dict(id='invented-washer',material=material,frame='part-X-insertion',geometry=g,gross_blank_volume_m3=V*2,net_volume_bounds_m3=[V,V],net_volume_base_m3=V,scrap_volume_bounds_m3=[V,V],paid_blank=dict(kind='invented blank',volume_m3=V*2),person_process_h=[.01,.02,.03],person_QA_h=[.01,.02,.03],machine_h=[.02,.04,.06],finish=dict(clean=True),source_quote=False)
def price(p,materials=MATS,rates=RATES):
    rho=materials[p['material']]['density_kg_m3'];r=materials[p['material']]['USD_kg'];lo,hi=p['net_volume_bounds_m3'];factor=p.get('mass_volume_factor',1.);p['mass_kg']={c:v*factor*rho[i] for i,(c,v) in enumerate(zip(h.CASES,[lo,p['net_volume_base_m3'],hi]))};p['paid_stock_kg']={c:p['gross_blank_volume_m3']*rho[i] for i,c in enumerate(h.CASES)};p['scrap_kg_bounds']=[0.,p['gross_blank_volume_m3']*rho[2]];breaks={}
    for i,c in enumerate(h.CASES):
        q=dict(material=p['gross_blank_volume_m3']*rho[i]*r[i],process=p['person_process_h'][i]*rates['labour_USD_h'][i],machine=p['machine_h'][i]*rates['machine_USD_h'][i],QA=p['person_QA_h'][i]*rates['QA_USD_h'][i]);q['overhead']=sum(q.values())*rates['overhead_fraction'][i];breaks[c]=q
    p['cost_breakdown_USD']=breaks;p['cost_USD']={c:sum(q.values()) for c,q in breaks.items()};return p

def prototype_seal(p):
    p['physical_definition']=dict(schema='osr-terminal-hardware-prototype-physical/1',family=p['family'],size=p['size'],parts=[{k:deepcopy(v) for k,v in x.items() if k not in h.SOURCE_PART_EVAL} for x in p['parts']],mating=[{k:deepcopy(v) for k,v in m.items() if k not in h.MATE_EVIDENCE|{'fork_driver'}} for m in p['mating']],quantity_per_source_end=1);p['candidate_id']=h.source_identity(p['physical_definition']);return reseal(p)
def prototype(p=None):
    p=price(deepcopy(p or part()));return prototype_seal(dict(schema='osr-terminal-hardware-prototype/1',family='M6-washer',size=None,parts=[p],mating=[dict(kind='annular bearing faces',axial_span_m=[-.002,.002],bore_m=.006)],manufactured_piece_count=1,basis='invented fixture',rates=deepcopy(RATES),materials=deepcopy(MATS),mass_kg=deepcopy(p['mass_kg']),cost_USD=deepcopy(p['cost_USD']),approvals={k:False for k in ('physical_accepted','engineering_accepted','native_eligible','manufacturing_release','operating_release')},holds=['invented hold'],nominal_material_AABB_m=[[-.002,-.006,-.006],[.002,.006,.006]],mass_property_bounds=dict(exact_CG_m=None,exact_inertia_kg_m2=None)))
def cut(at,axis,D,L):return dict(kind='cylinder-cut',at_m=list(at),axis=list(axis),diameter_m=D,length_m=L,purpose='invented source cut')
def source_ops():
    ops=[]
    def finish(op,v,cb):
        m=[v[0]*2.,v[1]*4.];op.update(incremental_removed_volume_bounds_m3=v,incremental_removed_mass_bounds_kg=m,incremental_removed_centroid_box_m=cb,incremental_removed_first_moment_bounds_kg_m=[[min(a*x for a in m for x in (cb[0][k],cb[1][k])),max(a*x for a in m for x in (cb[0][k],cb[1][k]))] for k in range(3)],source_cylinder_position_convention='at_m is base; signed axis points into cut',original_paid_blank_retained=True,source_credit_USD=0.,cost_USD=dict(low=.1,base=.2,high=.3),person_process_h=None,person_QA_h=None,independent_cut_union_and_mass_update_required=True);return op
    for n in range(12):
        y=n*.04;old=cut([.044,y,0.],[1.,0.,0.],.006,.012);g=dict(id='invented/hardpoint/'+str(n),part_id='invented/hp',material='al5083',geometry=box([.012,.025,.025],[.05,y,0.]),holes=[old],insert_pocket_max_depth_m=.009,insert_pocket_max_diameter_m=.01);pocket=dict(kind='thread-bounded-cut',at_m=[.056,y,0.],axis=[-1.,0.,0.],pilot_diameter_m=.007,major_diameter_m=.008,depth_m=.0087,pitch_m=.001,full_thread_depth_m=.0077,depth_tolerance_m=.0003,flat_bottom=True);v=[math.pi/4*(.007**2-.006**2)*.0084,math.pi/4*(.008**2-.006**2)*.009];ops.append(finish(dict(id='invented/receiver/'+str(n),kind='hardpoint-thread-pocket',source_entity_id='invented/hp/'+str(n),source_stock_owner_id='invented/hp-stock',source_geometry=g,complete_void_union=dict(kind='union',pieces=[old,pocket]),maximum_pocket_depth_m=.009,minimum_annular_rear_web_m=.003,material='al5083'),v,[[.047,y-.004,-.004],[.056,y+.004,.004]]))
    pts=[(y,z) for z in (-.08,.08) for y in (-.1,-.06,-.02,.02,.06,.1)];old=[cut([.077,y,z],[1.,0.,0.],.0055,.006) for y,z in pts];new=[cut([.077,y,z],[1.,0.,0.],.012,.006) for y,z in pts];void=box([.006,.1,.05],[.08,0.,0.]);g=dict(id='invented/ring',part_id='invented/ring',material='al5083',geometry=dict(kind='difference',outer=box([.006,.3,.2],[.08,0.,0.]),void=void),holes=old);v=[12*math.pi/4*(D**2-.0055**2)*.006 for D in (.01195,.01205)];ops.append(finish(dict(id='invented/ring-finish',kind='ring-access-port-enlargement',source_entity_id='invented/ring',source_stock_owner_id='invented/ring-stock',source_geometry=g,complete_void_union=dict(kind='union',pieces=[void]+old+new),blank_owner_count=1,new_stock_purchase_count=0,cut_count=12,access_diameter_m=.012,diameter_tolerance_m=.00005,axis_position_tolerance_m=.0001,material='al5083'),v,[[.08,-.107,-.087],[.08,.107,.087]]));return ops

def toolkit():
    ps=[]
    for n in range(12):p=price(part());p['id']='invented-tool/'+str(n);ps.append(p)
    q=dict(schema='osr-terminal-workshop-tool-physical/1',scope='One shared workshop kit, not installed railway material',parts=[dict(id=p['id'],material=p['material'],geometry=p['geometry'],paid_blank=p['paid_blank'],gross_volume_m3=p['gross_blank_volume_m3'],net_volume_bounds_m3=p['net_volume_bounds_m3']) for p in ps]);return dict(piece_count=12,parts=ps,count_per_train=1,qualified=False,lifecycle_definition_id=h.source_identity(q),physical_definition=q,mass_kg=None,calculated_cost_USD=None,scope='invented shared toolkit')
def reseal_all(r):
    for p in r['prototypes'].values():prototype_seal(p)
    r['physical_definition']=dict(schema='osr-terminal-hardware-local-physical/2',parent_candidate_id=h.PARENT['candidate_id'],fixed_source_interfaces=['invented fixed interface'],new_prototypes={k:p['physical_definition'] for k,p in r['prototypes'].items()},placements=[{k:deepcopy(o[k]) for k in ('id','prototype_key','placement','old_entity_id','source_part_id')} for o in r['occurrences']],source_machining=h._physical_source_ops(r['source_machining']),prospective_replacements=[dict(old=x['old_entity_id'],new=x['successor_occurrence_id']) for x in r['replacement_plan']]);r['candidate_id']=h.source_identity(r['physical_definition']);return reseal(r)
def fixture(p=None):
    proto=prototype(p);old=dict(id='invented/old0',part_id='invented/old-hardware',mass_kg=None,geometry=None);o=dict(id='hardware/'+old['id'],prototype_key='M6-washer',placement=dict(at_m=[1.,2.,3.],rotation=deepcopy(h.I),frame='terminal-local-UVW'),old_entity_id=old['id'],source_part_id=old['part_id'],source_entity_sha256=h.source_identity(old),finite_motion_poses_part_m=[[0.,0.,0.],[.02,0.,0.]],tool_envelope=dict(kind='invented envelope',radius_m=.02),continuous_sweep_verified=False);g=dict(id='invented/old-stock',entity_ids=[old['id']],direct_cost_usd=None,gross_mass_kg=None);repl=dict(old_entity_id=old['id'],old_part_id=old['part_id'],old_entity=old,old_stock_group_id=g['id'],successor_occurrence_id=o['id'],old_mass_or_price_added_to_new=False,canonical_applied=False);stock=dict(source_group=g,source_group_id=g['id'],old_entity_ids=[old['id']],successor_ids=[o['id']],once_only=True,applied=False,source_price_not_added=True);ops=source_ops();owners={k:dict(id=k,entity_ids=[x['source_entity_id'] for x in ops if x['source_stock_owner_id']==k],gross_mass_kg=None,direct_cost_usd=None) for k in ('invented/hp-stock','invented/ring-stock')}
    return reseal_all(dict(schema='osr-terminal-hardware-local-proposal/1',request_id='1'*64,parent=deepcopy(h.PARENT),prototypes={'M6-washer':proto},occurrences=[o],replacement_plan=[repl],source_stock_owner_replacements=[stock],source_machining=ops,source_machining_stock_owners=owners,shared_workshop_service_kit=toolkit(),workshop=dict(mass_kg=None,tooling_allowance_USD=None),repair_consumables_per_glazing_service=dict(annual_event_frequency=None,staffing_person_hours=None),new_parts_mass_kg=deepcopy(proto['mass_kg']),new_parts_cost_USD={c:proto['cost_USD'][c]+sum(x['cost_USD'][c] for x in ops) for c in h.CASES},physical_accepted=False,engineering_accepted=False,native_eligible=False,manufacturing_release=False,operating_release=False,composition_admitted=False,selected_reference_changed=False,selection_id=None,complete_installed_cost=False,cost_scope='invented subtotal',original_source_accounting={},original_source_coverage={},service_evaluation={},counted_joints={},wiring_cooling_and_bearings={},assembly_sequence=['invented sequence'],holds=['inherited unknown joint obligation']))
def run(r):
    pin=dict(candidate_id=r['candidate_id'],evaluation_id=r['evaluation_id'],raw_sha256='2'*64,source_request_id=r['request_id'],source_execution_id='3'*64,source_commit=h.SOURCE_COMMIT,source_module_sha256=h.SOURCE_SHA256)
    with patch.object(h,'FAMILIES',{'M6-washer':1}):return h.normalize(r,pin=pin,request_id='4'*64)

class HardwareTests(unittest.TestCase):
    def test_hash_conventions_distinct(self):self.assertNotEqual(h.source_identity({'x':1}),h.identity({'x':1}))
    def test_normalize_lossless_nonadmitted_and_owner_counts(self):
        r=fixture();before=deepcopy(r);p=run(r);self.assertEqual(r,before);self.assertEqual(p['source_original_definition'],r);self.assertIsNone(p['canonical_definition']);self.assertEqual(p['counts'],dict(placements=1,material_pieces=1,new_stock_groups=1,old_owner_groups=1,source_finishing_operations=13,finishing_source_occurrences=13,finishing_paid_owner_groups=2,paid_backing_rings=1,shared_service_tool_pieces=12));self.assertFalse(p['source_owner_transactions_applied']);self.assertTrue(all(p[k] is False for k in h.FLAGS));self.assertEqual(p['evaluation_id'],h.identity({k:v for k,v in p.items() if k!='evaluation_id'}))
    def test_price_or_density_changes_evaluation_not_installed_geometry(self):
        for mode in ('price','density'):
            r=fixture();a=run(r);p=r['prototypes']['M6-washer']
            if mode=='price':p['rates']['labour_USD_h']=[2.,3.,4.]
            else:p['materials']['invented-steel']['density_kg_m3']=[3.,4.,5.]
            price(p['parts'][0],p['materials'],p['rates']);p['mass_kg']=deepcopy(p['parts'][0]['mass_kg']);p['cost_USD']=deepcopy(p['parts'][0]['cost_USD']);r['new_parts_mass_kg']=deepcopy(p['mass_kg']);r['new_parts_cost_USD']={c:p['cost_USD'][c]+sum(x['cost_USD'][c] for x in r['source_machining']) for c in h.CASES};b=run(reseal_all(r));self.assertEqual(a['component_geometry_id'],b['component_geometry_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])
    def test_signed_pose_and_primitive_pose_apply_once(self):
        r=fixture(part(ann(at=(.3,0.,0.))));r['occurrences'][0]['placement']['rotation']=[[-1.,0.,0.],[0.,-1.,0.],[0.,0.,1.]];p=run(reseal_all(r));e=p['canonical_draft']['entities'][0];b=e['mass_properties_terminal_frame']['centroid_interval_m'];self.assertAlmostEqual(sum(b[0])/2,.7);self.assertAlmostEqual(sum(b[1])/2,2.);self.assertAlmostEqual(sum(b[2])/2,3.);self.assertEqual(e['geometry']['source_graph'],r['prototypes']['M6-washer']['parts'][0]['geometry'])
    def test_no_fabricated_point_CG_or_tensor(self):
        p=run(fixture());m=p['canonical_draft']['entities'][0]['mass_properties_terminal_frame'];self.assertIsNone(m['exact_point_CG_m']);self.assertIsNone(m['exact_inertia_kg_m2']);self.assertIsNone(m['centroidal_inertia']);self.assertGreater(m['inertia_about_frame_origin_interval_kg_m2'][0][0][1],0.);self.assertTrue(any(x['code']=='inherited-terminal-contracts' for x in p['held_facts']))
    def test_thread_minimum_maximum_graph_not_filled_box(self):
        outer=ann(.006,.012,0.);g=dict(kind='thread-bounded-material',outer=outer,minimum_material=dict(kind='difference',outer=outer,cuts=[ann(.006,.006,0.)]),maximum_material=dict(kind='difference',outer=outer,cuts=[ann(.006,.005,0.)]),thread=dict(major_diameter_m=.006,pilot_or_root_diameter_m=.005,pitch_m=.001,length_m=.006,at_m=[0.,0.,0.],axis=[1.,0.,0.],handedness='right',external=False,exact_helix_supported=False));p=run(fixture(part(g,net=1e-7)));e=p['canonical_draft']['entities'][0];self.assertEqual(e['geometry']['source_graph'],g);self.assertTrue(e['geometry']['not_filled_packaging']);self.assertFalse(p['native_eligible'])
    def test_unknown_geometry_preserved_with_named_unsupported_bound(self):
        g=dict(kind='invented-helical-surface',port=dict(size_m=[.1,.2,.3]));p=run(fixture(part(g,net=1e-7)));e=p['canonical_draft']['entities'][0];self.assertEqual(e['geometry']['source_graph'],g);self.assertIsNone(e['mass_properties_terminal_frame']['centroid_interval_m']);self.assertTrue(any(x['code']=='unsupported-material-graph-bound' for x in p['held_facts']))
    def test_cellular_free_compressed_constant_mass(self):
        g=dict(kind='difference',outer=box([.002,.1,.1]),cuts=[box([.002,.08,.08])]);p=part(g,net=.002*(.1*.1-.08*.08),material='EPDM-cellular-unqualified');p.update(mass_volume_factor=1.25,free_net_volume_m3=p['net_volume_base_m3']*1.25,installed_bulk_density_multiplier=1.25,free_shape=dict(kind='difference',outer=box([.0025,.1,.1]),cuts=[box([.0025,.08,.08])]),density_basis='invented free cellular density',deformation_model='invented cellular void compression');e=run(fixture(p))['canonical_draft']['entities'][0];self.assertEqual(e['material_state']['mass_volume_factor'],1.25);self.assertAlmostEqual(e['mass_label_cases_kg']['base'],p['net_volume_base_m3']*1.25*3.);self.assertEqual(e['geometry']['source_graph']['outer']['size_m'][0],.002)
    def test_free_seal_model_missing_refused(self):
        p=part();p['mass_volume_factor']=1.25
        with self.assertRaisesRegex(ValueError,'cellular'):run(fixture(p))
    def test_no_duplicate_oldprice_or_per_piece_new_account(self):
        p=run(fixture());d=p['canonical_draft'];self.assertEqual(len(d['old_stock_owner_dispositions']),1);self.assertEqual(d['old_stock_owner_dispositions'][0]['status'],'REQUIRED_NOT_APPLIED');s=d['stock_groups'][0];self.assertEqual(len(s['part_account_rows']),1);self.assertTrue(s['parts_are_subtotals_not_extra_payable_rows']);self.assertFalse(s['old_material_or_price_added']);self.assertIsNone(d['old_stock_owner_dispositions'][0]['source']['source_group']['direct_cost_usd'])
    def test_two_finishing_owner_groups_and_one_ring(self):
        p=run(fixture());d=p['canonical_draft'];self.assertEqual(sorted(len(x['operation_ids']) for x in d['source_finishing_owner_dispositions']),[1,12]);self.assertTrue(all(x['paid_blank_count']==1 and x['stock_purchase_count']==0 and not x['source_mass_and_moment_update_applied'] for x in d['source_finishing_owner_dispositions']));self.assertTrue(all(x['remaining_net_mass_and_CG'] is None for x in d['required_source_finishing']))
    def test_shared_tool_and_repair_not_installed(self):
        p=run(fixture());self.assertEqual(len(p['canonical_draft']['stock_groups']),1);self.assertTrue(all(not x['charged_in_installed_stock'] for x in p['lifecycle_allocations']));self.assertEqual(p['lifecycle_allocations'][0]['count_per_train'],1);self.assertIsNone(p['lifecycle_allocations'][2]['event_frequency'])
    def test_unknown_mass_price_hours_stayNone(self):
        r=fixture();p=r['prototypes']['M6-washer'];x=p['parts'][0];x.update(cost_USD=None,cost_breakdown_USD=None,person_process_h=None,person_QA_h=None,machine_h=None,mass_kg=None,paid_stock_kg=None);p.update(cost_USD=None,mass_kg=None);r.update(new_parts_mass_kg=None,new_parts_cost_USD=None);q=run(reseal_all(r));self.assertIsNone(q['known_new_parts_mass_label_cases_kg']);self.assertIsNone(q['known_new_hardware_direct_cost_label_cases_USD']);self.assertIsNone(q['canonical_draft']['entities'][0]['mass_properties_terminal_frame']['inertia_about_frame_origin_interval_kg_m2'])
    def test_duplicate_missing_reused_replacement_refusals(self):
        for mode in ('duplicate','successor','price','sourcehash','reuse'):
            r=fixture()
            if mode=='duplicate':r['replacement_plan']*=2
            elif mode=='successor':r['source_stock_owner_replacements'][0]['successor_ids']=['wrong']
            elif mode=='price':r['replacement_plan'][0]['old_mass_or_price_added_to_new']=True
            elif mode=='sourcehash':r['occurrences'][0]['source_entity_sha256']='a'*64
            else:r['source_stock_owner_replacements'][0]['old_entity_ids']*=2
            with self.subTest(mode=mode),self.assertRaises(ValueError):run(reseal_all(r))
    def test_incremental_union_old_hole_counted_once(self):
        op=source_ops()[0];q=h.finishing_plan(op,MATS);self.assertAlmostEqual(q['incremental_removed_volume_bounds_m3'][0],math.pi/4*(.007**2-.006**2)*.0084);self.assertEqual(len(q['retained_original_circular_union']),1);self.assertEqual(q['source_complete_void_union'],op['complete_void_union'])
    def test_signed_BASE_midpoint(self):
        c=h._cut(cut([.056,.1,.2],[-1.,0.,0.],.008,.009));self.assertAlmostEqual(c['centre_m'][0],.0515);self.assertEqual(c['axis'],0)
    def test_ring_union_not_summed_old_plus_new(self):
        q=h.finishing_plan(source_ops()[-1],MATS);self.assertAlmostEqual(q['incremental_removed_volume_bounds_m3'][1],12*math.pi/4*(.01205**2-.0055**2)*.006);self.assertEqual(len(q['maximum_circular_cut_union']),12)
    def test_wrong_increment_moment_mass_or_void_refused(self):
        for mode in ('volume','moment','mass','missing'):
            op=source_ops()[0]
            if mode=='volume':op['incremental_removed_volume_bounds_m3'][0]*=2
            elif mode=='moment':op['incremental_removed_first_moment_bounds_kg_m']=[[0.,0.]]*3
            elif mode=='mass':op['incremental_removed_mass_bounds_kg'][0]*=2
            else:op['complete_void_union']['pieces'].pop(0)
            with self.subTest(mode=mode),self.assertRaises(ValueError):h.finishing_plan(op,MATS)
    def test_cut_domain_rearweb_axis_and_boolean_refused(self):
        for mode in ('depth','axis','backweb','bool'):
            op=source_ops()[0]
            if mode=='depth':op['complete_void_union']['pieces'][1]['depth_m']=.02
            elif mode=='axis':op['complete_void_union']['pieces'][1]['axis']=[0.,1.,0.]
            elif mode=='backweb':op['minimum_annular_rear_web_m']=.004
            else:op['source_credit_USD']=False
            with self.subTest(mode=mode),self.assertRaises(ValueError):h.finishing_plan(op,MATS)
    def test_wrong_units_missing_pose_nan_bool_refused(self):
        for g in (box([True,.01,.01]),box([float('nan'),.01,.01]),dict(kind='box',size_m=[.01]*3),ann()|dict(units='mm')):
            with self.assertRaises(ValueError):h.material_bounds(g)
    def test_reflection_nonrigid_scale_and_datum_stale_refused(self):
        for R in ([[-1.,0.,0.],[0.,1.,0.],[0.,0.,1.]],[[2.,0.,0.],[0.,1.,0.],[0.,0.,1.]]):
            r=fixture();r['occurrences'][0]['placement']['rotation']=R
            with self.assertRaises(ValueError):run(reseal_all(r))
        for delta in (.15,1000.):
            r=fixture();r['occurrences'][0]['placement']['at_m'][0]+=delta;reseal(r)
            with self.assertRaises(ValueError):run(r)
    def test_corrupt_projection_unknown_wrapper_and_false_admission_refused(self):
        for mode in ('projection','unknown','approval'):
            r=fixture()
            if mode=='projection':r['physical_definition']['placements'][0]['placement']['at_m'][0]+=.1;r['candidate_id']=h.source_identity(r['physical_definition'])
            elif mode=='unknown':r['new_physical_port']={'size_m':[.1]*3}
            else:r['composition_admitted']=True
            reseal(r)
            with self.subTest(mode=mode),self.assertRaises(ValueError):run(r)
    def test_physical_ports_not_erased_by_annotation_collision(self):
        r=fixture();a=run(r);r['prototypes']['M6-washer']['parts'][0]['geometry']['strength_qualified']={'physical_port':dict(size_m=[.1,.2,.3])};b=run(reseal_all(r));self.assertNotEqual(a['component_geometry_id'],b['component_geometry_id']);self.assertIn('strength_qualified',b['canonical_draft']['entities'][0]['geometry']['source_graph'])
    def test_known_mate_evidence_vs_unknown_or_structured_physical(self):
        r=fixture();a=run(r);r['prototypes']['M6-washer']['mating'][0]['strength_qualified']=True;b=run(reseal_all(r));self.assertEqual(a['component_geometry_id'],b['component_geometry_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])
        for kind,v in (('invented-new-contact',True),('annular bearing faces',{'port_m':.01})):
            r=fixture();a=run(r);r['prototypes']['M6-washer']['mating'][0].update(kind=kind,strength_qualified=v);b=run(reseal_all(r));self.assertNotEqual(a['component_geometry_id'],b['component_geometry_id'])
    def test_tool_count_or_projection_refused_prices_eval_only(self):
        for mode in ('count','graph'):
            r=fixture();t=r['shared_workshop_service_kit']
            if mode=='count':t['piece_count']=11
            else:t['parts'][0]['geometry']['outer_diameter_m']+=.001
            with self.subTest(mode=mode),self.assertRaises(ValueError):run(reseal_all(r))
        r=fixture();a=run(r);r['shared_workshop_service_kit']['parts'][0]['cost_USD']['base']+=1;b=run(reseal_all(r));self.assertEqual(a['component_geometry_id'],b['component_geometry_id'])
    def test_refusal_does_not_mutate_inputs(self):
        r=fixture();r['source_stock_owner_replacements'][0]['applied']=True;reseal_all(r);before=deepcopy(r)
        with self.assertRaises(ValueError):run(r)
        self.assertEqual(r,before)
    def test_total_price_mass_and_breakdown_mismatch_refused(self):
        for mode in ('price','mass','breakdown'):
            r=fixture()
            if mode=='price':r['new_parts_cost_USD']['base']+=1
            elif mode=='mass':r['new_parts_mass_kg']['base']+=1
            else:r['prototypes']['M6-washer']['parts'][0]['cost_breakdown_USD']['base']['process']+=1
            with self.subTest(mode=mode),self.assertRaises(ValueError):run(reseal_all(r))
    def test_affine_mass_first_moment_and_inertia_enclose_independent_points(self):
        box=[[-.1,.2],[.3,.4],[-.6,-.5]];R=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]];T=[1.,-2.,3.];q=h.containment_moments(box,[2.,4.],T,R)
        for p in ([.05,.35,-.55],[-.1,.3,-.6],[.2,.4,-.5]):
            x=h.add(T,h.apply(R,p));m=3.
            for k in range(3):a,z=q['mass_first_moment_interval_kg_m'][k];self.assertLessEqual(a,m*x[k]);self.assertGreaterEqual(z,m*x[k])
            for i in range(3):
                for j in range(3):
                    v=m*sum(x[k]**2 for k in range(3) if k!=i) if i==j else -m*x[i]*x[j];a,z=q['inertia_about_frame_origin_interval_kg_m2'][i][j];self.assertLessEqual(a,v);self.assertGreaterEqual(z,v)

class AdditionalOwnershipTests(unittest.TestCase):
    def test_two_material_pieces_share_one_old_occurrence_owner(self):
        r=fixture();p=r['prototypes']['M6-washer'];second=price(part());second['id']='invented-second-material';second['geometry']['at_m']=[.04,0.,0.];p['parts'].append(second);p['manufactured_piece_count']=2;p['mass_kg']={c:sum(x['mass_kg'][c] for x in p['parts']) for c in h.CASES};p['cost_USD']={c:sum(x['cost_USD'][c] for x in p['parts']) for c in h.CASES};r['new_parts_mass_kg']=deepcopy(p['mass_kg']);r['new_parts_cost_USD']={c:p['cost_USD'][c]+sum(x['cost_USD'][c] for x in r['source_machining']) for c in h.CASES};q=run(reseal_all(r));self.assertEqual(q['counts']['material_pieces'],2);self.assertEqual(q['counts']['new_stock_groups'],1);self.assertEqual(len(q['canonical_draft']['stock_groups'][0]['entity_ids']),2)
    def test_simple_annulus_or_ring_net_lie_refused(self):
        r=fixture();p=r['prototypes']['M6-washer']['parts'][0];p['net_volume_bounds_m3']=[v*1.1 for v in p['net_volume_bounds_m3']];p['net_volume_base_m3']*=1.1;price(p)
        with self.assertRaisesRegex(ValueError,'material volume'):run(reseal_all(r))
    def test_structured_quote_flag_cannot_erase_port(self):
        r=fixture();r['prototypes']['M6-washer']['parts'][0]['source_quote']={'port':dict(size_m=[.1]*3)}
        with self.assertRaisesRegex(ValueError,'evidence flag'):run(reseal_all(r))
    def test_structured_density_basis_is_physical_not_erased(self):
        r=fixture();a=run(r);r['prototypes']['M6-washer']['parts'][0]['density_basis']={'port_m':.01};b=run(reseal_all(r));self.assertNotEqual(a['component_geometry_id'],b['component_geometry_id'])
    def test_all_three_round_axes_use_proper_frame(self):
        for R in (h.I,[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]],[[0.,0.,1.],[0.,1.,0.],[-1.,0.,0.]]):
            g=ann();g['rotation']=R;b=h.material_bounds(g);self.assertAlmostEqual(sorted(y-x for x,y in b)[0],.004);self.assertEqual(h.exact_simple_volume(g),h.exact_simple_volume(ann()))

class CostComponentGuardTests(unittest.TestCase):
    def test_HC_C1_negative_QA_equal_process_offset_refused(self):
        r=fixture();part=r['prototypes']['M6-washer']['parts'][0];q=part['cost_breakdown_USD']['base'];oldq=q['QA'];q['QA']=-1.;q['process']+=oldq+1.
        with self.assertRaisesRegex(ValueError,'nonnegative'):run(reseal_all(r))

    def test_HC_C2_positive_material_to_process_shift_refused(self):
        r=fixture();part=r['prototypes']['M6-washer']['parts'][0];q=part['cost_breakdown_USD']['base'];delta=q['material']/2;q['material']-=delta;q['process']+=delta
        with self.assertRaisesRegex(ValueError,'component differs'):run(reseal_all(r))

    def test_exact_five_keys_and_no_missing_or_extra_component(self):
        for mode in ('missing','extra','renamed'):
            r=fixture();q=r['prototypes']['M6-washer']['parts'][0]['cost_breakdown_USD']['base']
            if mode=='missing':q.pop('QA')
            elif mode=='extra':q['rebate']=0.
            else:q['qa']=q.pop('QA')
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'Exact five'):run(reseal_all(r))

    def test_each_known_component_finite_nonboolean_nonnegative(self):
        for key in ('material','process','machine','QA','overhead'):
            for value in (-.1,False,float('nan'),float('inf')):
                p=prototype();p['parts'][0]['cost_breakdown_USD']['base'][key]=value
                with self.subTest(key=key,value=value),self.assertRaises(ValueError):h._cost_components(p['parts'][0],p)

    def test_each_known_positive_component_reconciled_even_if_total_retained(self):
        for key in ('process','machine','QA','overhead'):
            r=fixture();q=r['prototypes']['M6-washer']['parts'][0]['cost_breakdown_USD']['base'];q[key]+=1e-6;q['material']-=1e-6
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'component differs'):run(reseal_all(r))

    def test_single_unknown_component_keptNone_and_named_partial_hold(self):
        r=fixture();before=run(r);r['prototypes']['M6-washer']['parts'][0]['cost_breakdown_USD']['base']['QA']=None;after=run(reseal_all(r));account=after['canonical_draft']['stock_groups'][0]['part_account_rows'][0];v=account['cost_component_verification'];self.assertIsNone(v['cases']['base']['reported']['QA']);self.assertGreater(v['cases']['base']['expected_from_known_inputs']['QA'],0.);self.assertFalse(v['unknown_reports_filled']);self.assertIn('base/QA',v['unknown_reported_components']);self.assertEqual(before['component_geometry_id'],after['component_geometry_id']);self.assertEqual(before['known_new_hardware_direct_cost_label_cases_USD'],after['known_new_hardware_direct_cost_label_cases_USD']);self.assertTrue(any(x['code']=='partial-cost-component-evidence' for x in after['held_facts']))

    def test_whole_missing_breakdown_and_partial_case_retained(self):
        for value in (None,{'low':None,'base':None,'high':None}):
            r=fixture();r['prototypes']['M6-washer']['parts'][0]['cost_breakdown_USD']=value;q=run(reseal_all(r));a=q['canonical_draft']['entities'][0]['cost_component_verification'];self.assertEqual(len(a['unknown_reported_components']),15);self.assertFalse(a['all_reported_components_reconciled']);self.assertIsNone(a['cases']['base']['reported']['material'])

    def test_unknown_QA_hours_retains_unverified_report_notzero(self):
        r=fixture();r['prototypes']['M6-washer']['parts'][0]['person_QA_h']=None;q=run(reseal_all(r));a=q['canonical_draft']['entities'][0]['cost_component_verification'];self.assertIn('base/QA',a['reported_components_with_unknown_inputs']);self.assertIsNone(a['cases']['base']['expected_from_known_inputs']['QA']);self.assertGreater(a['cases']['base']['reported']['QA'],0.);self.assertTrue(any(x['code']=='partial-cost-component-evidence' for x in q['held_facts']))

    def test_unknown_component_does_not_mask_another_known_wrong_component(self):
        r=fixture();part=r['prototypes']['M6-washer']['parts'][0];part['cost_breakdown_USD']['base']['QA']=None;part['cost_breakdown_USD']['base']['material']*=2
        with self.assertRaisesRegex(ValueError,'component differs'):run(reseal_all(r))

    def test_known_partial_components_cannot_exceed_declared_total(self):
        p=prototype();part=p['parts'][0];part['person_process_h']=None;part['cost_breakdown_USD']['base']={k:None for k in ('material','process','machine','QA','overhead')};part['cost_breakdown_USD']['base']['process']=part['cost_USD']['base']+1
        with self.assertRaisesRegex(ValueError,'exceed'):h._cost_components(part,p)

    def test_original_component_values_unchanged_and_refusal_nonmutating(self):
        r=fixture();p=run(r);row=p['canonical_draft']['stock_groups'][0]['part_account_rows'][0];self.assertEqual(row['source_account']['cost_breakdown_USD'],r['prototypes']['M6-washer']['parts'][0]['cost_breakdown_USD']);self.assertTrue(row['cost_component_verification']['all_reported_components_reconciled']);self.assertEqual(row['cost_component_verification']['cases']['base']['verified_components'],['material','process','machine','QA','overhead']);r['prototypes']['M6-washer']['parts'][0]['cost_breakdown_USD']['base']['material']=-1;reseal_all(r);old=deepcopy(r)
        with self.assertRaises(ValueError):run(r)
        self.assertEqual(old,r)

if __name__=='__main__':unittest.main()

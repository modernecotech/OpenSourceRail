"""Invented local member fixtures only; never load a retained candidate."""
from copy import deepcopy
import json
import math
import unittest
from unittest.mock import patch
from engineering import terminal_welds as w


def fixture(paths=None):
    paths=deepcopy(paths or [[[0.,-.010,0.],[0.,.010,0.]]])
    entity=dict(id='roof/standoff-weld/0',part_id='invented/weld',material_id='al5083',frame='terminal-local-UVW',scope='installed',at_m=[0.,0.,0.],rotation=deepcopy(w.I),geometry=dict(kind='envelope',size_m=[.006,.026,.006]),physical_drawing=dict(kind='triangular-weld-seams',leg_m=.003,local_segments_m=paths,in_prepared_grooves=False,exact_triangle_orientation_and_runout_resolved=False))
    parents=[dict(id='invented/base',material_id='al5083',frame='terminal-local-UVW',at_m=[.015,0.,-.005],rotation=deepcopy(w.I),geometry=dict(kind='box',size_m=[.030,.040,.010])),dict(id='invented/upright',material_id='al5083',frame='terminal-local-UVW',at_m=[-.005,0.,.015],rotation=deepcopy(w.I),geometry=dict(kind='box',size_m=[.010,.040,.030]))]
    policy=dict(materials=dict(al5083=dict(density_kg_m3=2660.,density_bounds_kg_m3=[2580.2,2739.8],rate_USD_kg=[3.5,5.,8.])),process=dict(labour_USD_h=[6.,10.,16.],weld_procurement_factor=1.2))
    L=sum(math.dist(*line) for line in paths);V=.5*.003**2*L;rho=[2580.2,2660.,2739.8]
    stock=dict(id='stock/'+entity['id'],entity_ids=[entity['id']],quantity=1,net_m3=V,gross_m3=V*1.2,process_h=.1,QA_h=.05,net_mass_kg={c:V*rho[j] for j,c in enumerate(w.CASES)},gross_mass_kg={c:V*1.2*rho[j] for j,c in enumerate(w.CASES)},scrap_mass_kg={c:V*.2*rho[j] for j,c in enumerate(w.CASES)},direct_cost_usd={c:V*1.2*rho[j]*policy['materials']['al5083']['rate_USD_kg'][j]+.15*policy['process']['labour_USD_h'][j] for j,c in enumerate(w.CASES)})
    contacts=[dict(parent_id=parents[0]['id'],source_parent_sha256=w.identity(parents[0]),cell_id='solid',axis=2,sign=1),dict(parent_id=parents[1]['id'],source_parent_sha256=w.identity(parents[1]),cell_id='solid',axis=0,sign=1)]
    assignment=dict(source_entity_id=entity['id'],source_entity_sha256=w.identity(entity),source_stock_sha256=w.identity(stock),parent_preparations=[],joint_domain='external-orthogonal-fillet',seams=[dict(source_segment_index=i,root_offset_m=[0.,0.,0.],contacts=deepcopy(contacts),end_treatment=dict(kind='flat-positive-runout',trim_start_m=.001,trim_end_m=.001)) for i in range(len(paths))])
    return [entity,stock,assignment,parents,policy]

def reseal(f):
    e,s,a,ps,p=f;a['source_entity_sha256']=w.identity(e);a['source_stock_sha256']=w.identity(s)
    for seam in a['seams']:
        for c in seam['contacts']:c['source_parent_sha256']=w.identity(next(x for x in ps if x['id']==c['parent_id']))
    return f

def run(f):return w.define_record(*f)


class WeldTests(unittest.TestCase):
    def test_external_volume_centroid_first_moment(self):
        f=fixture();before=deepcopy(f);r=run(f);self.assertEqual(f,before);self.assertAlmostEqual(r['net_volume_m3'],.5*.003**2*.018)
        for a,b in zip(r['centroid_m'],[.001,0.,.001]):self.assertAlmostEqual(a,b)
        for a,b in zip(r['first_volume_moment_m4'],[r['net_volume_m3']*.001,0.,r['net_volume_m3']*.001]):self.assertAlmostEqual(a,b)
        self.assertEqual(r['physical_definition_id'],w.identity(r['physical_definition']))
        self.assertFalse(r['canonical_admitted']);self.assertFalse(r['physical_accepted']);self.assertFalse(r['native_eligible'])

    def test_all_material_process_cases_once(self):
        r=run(fixture());a=r['accounting'];V=r['net_volume_m3'];self.assertEqual(a['quantity'],1);self.assertEqual(len(a['replacement_entity_ids']),1)
        for c,rho in zip(w.CASES,[2580.2,2660.,2739.8]):
            self.assertAlmostEqual(a['cases'][c]['net_mass_kg'],V*rho)
            self.assertAlmostEqual(a['cases'][c]['gross_procured_mass_kg']-a['cases'][c]['noninstalled_reserve_mass_kg'],V*rho)
            self.assertAlmostEqual(a['cases'][c]['direct_USD'],a['cases'][c]['material_USD']+a['cases'][c]['process_QA_USD'])
        self.assertEqual(a['process_h'],.1);self.assertEqual(a['QA_h'],.05);self.assertIsNone(a['extra_setup_rework_QA_h']);self.assertFalse(a['complete_installed_cost'])
        self.assertLess(a['net_volume_delta_vs_old_m3'],0.)

    def test_pattern_inventory(self):
        t=w.family_templates();self.assertEqual(sum(x['source_quantity'] for x in t['patterns']),183);self.assertEqual(len(t['patterns']),27);self.assertEqual(len({x['family'] for x in t['patterns']}),9)
        for p,q in w.PATTERNS:self.assertEqual(w.pattern_for(p.replace('*','0')),p)
        with self.assertRaises(w.DefinitionHold):w.pattern_for('roof/unreviewed-anything')

    def test_proper_pose_no_second_lift(self):
        f=fixture();R=[[-1.,0.,0.],[0.,-1.,0.],[0.,0.,1.]];T=[2.,3.,4.]
        for e in [f[0]]+f[3]:e['at_m']=w.world(e['at_m'],T,R);e['rotation']=deepcopy(R)
        r=run(reseal(f))
        for a,b in zip(r['centroid_m'],[1.999,3.,4.001]):self.assertLess(abs(a-b),1e-12)

    def test_price_changes_only_evaluation(self):
        f=fixture();a=run(f);f[4]['materials']['al5083']['rate_USD_kg']=[4.,6.,9.]
        for j,c in enumerate(w.CASES):f[1]['direct_cost_usd'][c]=f[1]['gross_mass_kg'][c]*f[4]['materials']['al5083']['rate_USD_kg'][j]+.15*f[4]['process']['labour_USD_h'][j]
        b=run(reseal(f));self.assertEqual(a['physical_definition_id'],b['physical_definition_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])

    def test_QA_changes_only_evaluation(self):
        f=fixture();a=run(f);f[1]['QA_h']=.15
        for j,c in enumerate(w.CASES):f[1]['direct_cost_usd'][c]+=.10*f[4]['process']['labour_USD_h'][j]
        b=run(reseal(f));self.assertEqual(a['physical_definition_id'],b['physical_definition_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])

    def test_trim_changes_physical(self):
        f=fixture();a=run(f);f[2]['seams'][0]['end_treatment']['trim_end_m']=.002;b=run(f);self.assertNotEqual(a['physical_definition_id'],b['physical_definition_id']);self.assertLess(b['net_volume_m3'],a['net_volume_m3'])

    def test_parent_material_changes_physical(self):
        f=fixture();a=run(f);f[3][0]['material_id']='al5754';b=run(reseal(f));self.assertNotEqual(a['physical_definition_id'],b['physical_definition_id']);self.assertTrue(b['holds'])

    def test_unknown_geometry_cannot_be_envelope(self):
        f=fixture();f[3][0]['geometry']['kind']='envelope'
        with self.assertRaisesRegex(w.DefinitionHold,'parent-material-domain'):run(reseal(f))

    def test_exact_source_parent_needs_own_adapter(self):
        f=fixture();f[3][0]['exact_CSG_entity']={'geometry':{'kind':'rhs'}}
        with self.assertRaisesRegex(w.DefinitionHold,'finished-CSG'):run(reseal(f))

    def test_unconsumed_parent_geometry_refused(self):
        f=fixture();f[3][0]['geometry']['hidden_cut']={'kind':'cylinder'}
        with self.assertRaisesRegex(w.DefinitionHold,'unconsumed-parent'):run(reseal(f))

    def test_steel_material_route_not_assumed(self):
        f=fixture();f[3][0]['material_id']='running/steel-s355'
        with self.assertRaisesRegex(w.DefinitionHold,'dissimilar'):run(reseal(f))

    def test_real_face_plane_gap_refused(self):
        f=fixture();f[3][0]['at_m'][2]-=.0005
        with self.assertRaisesRegex(w.DefinitionHold,'contact-plane'):run(reseal(f))

    def test_finite_contact_strip_edges_refused(self):
        f=fixture();f[3][0]['geometry']['size_m'][0]=.001;f[3][0]['at_m'][0]=.0005
        with self.assertRaisesRegex(w.DefinitionHold,'exceeds-real-parent-face'):run(reseal(f))

    def test_root_offset_is_explicit_and_checked(self):
        f=fixture();f[2]['seams'][0]['root_offset_m']=[0.,0.,.001]
        with self.assertRaisesRegex(w.DefinitionHold,'contact-plane'):run(f)

    def test_missing_face_and_segment_refused(self):
        f=fixture();f[2]['seams']=[]
        with self.assertRaisesRegex(w.DefinitionHold,'missing-segment'):run(f)

    def test_duplicate_segment_refused(self):
        f=fixture([[[0.,-.01,0.],[0.,0.,0.]],[[0.,0.,0.],[0.,.01,0.]]]);f[2]['seams'][1]['source_segment_index']=0
        with self.assertRaisesRegex(ValueError,'exactly once'):run(f)

    def test_distinct_members_required(self):
        f=fixture();f[2]['seams'][0]['contacts'][1]=deepcopy(f[2]['seams'][0]['contacts'][0]);f[3]=f[3][:1]
        with self.assertRaisesRegex(w.DefinitionHold,'distinct-member'):run(f)

    def test_parent_identity_mismatch(self):
        f=fixture();f[3][0]['geometry']['size_m'][0]+=.001
        with self.assertRaisesRegex(ValueError,'epoch'):run(f)

    def test_source_weld_identity_mismatch(self):
        f=fixture();f[0]['at_m'][1]=.001
        with self.assertRaisesRegex(ValueError,'identity mismatch'):run(f)

    def test_source_stock_identity_mismatch(self):
        f=fixture();f[1]['process_h']=.2
        with self.assertRaisesRegex(ValueError,'identity mismatch'):run(f)

    def test_original_volume_mismatch(self):
        f=fixture();f[1]['net_m3']*=2
        with self.assertRaisesRegex(ValueError,'volume/procurement'):run(reseal(f))

    def test_original_mass_mismatch(self):
        f=fixture();f[1]['net_mass_kg']['base']*=2
        with self.assertRaisesRegex(ValueError,'mass ownership'):run(reseal(f))

    def test_original_price_mismatch(self):
        f=fixture();f[1]['direct_cost_usd']['base']+=1
        with self.assertRaisesRegex(ValueError,'cost basis'):run(reseal(f))

    def test_no_reused_or_boolean_quantity(self):
        for quantity in [2,True]:
            f=fixture();f[1]['quantity']=quantity
            with self.assertRaisesRegex(ValueError,'once-only'):run(reseal(f))

    def test_positive_runout_required(self):
        for value in [0.,-.001,True,float('nan'),float('inf')]:
            f=fixture();f[2]['seams'][0]['end_treatment']['trim_start_m']=value
            with self.assertRaises(ValueError):run(f)

    def test_too_much_trim_refused(self):
        f=fixture();f[2]['seams'][0]['end_treatment']['trim_end_m']=.020
        with self.assertRaisesRegex(w.DefinitionHold,'remaining-seam'):run(f)

    def test_unmodelled_miter_refused(self):
        f=fixture();f[2]['seams'][0]['end_treatment']['kind']='arbitrary-miter'
        with self.assertRaisesRegex(w.DefinitionHold,'miter-not-supported'):run(f)

    def test_prepared_groove_is_held_not_imagined(self):
        f=fixture();f[0]['physical_drawing']['in_prepared_grooves']=True
        with self.assertRaisesRegex(w.DefinitionHold,'counted-parent-groove'):run(reseal(f))

    def test_new_bevel_cut_is_not_free(self):
        f=fixture();f[2]['parent_preparations']=[{'new_bevel':'not-counted'}]
        with self.assertRaisesRegex(w.DefinitionHold,'counted-parent-groove'):run(f)

    def test_bore_contact_cannot_be_filled(self):
        f=fixture();f[3][0]['geometry']['holes']=[dict(axis=2,centre_m=[-.014,0.,0.],radius_m=.001,length_m=.010)]
        with self.assertRaisesRegex(w.DefinitionHold,'source-bore'):run(reseal(f))

    def test_far_bore_conservative_domain(self):
        f=fixture();f[3][0]['geometry']['holes']=[dict(axis=2,centre_m=[.01,0.,0.],radius_m=.001,length_m=.010)]
        self.assertGreater(run(reseal(f))['net_volume_m3'],0.)

    def test_boolean_bore_axis_refused(self):
        f=fixture();f[3][0]['geometry']['holes']=[dict(axis=True,centre_m=[0.,0.,0.],radius_m=.001,length_m=.010)]
        with self.assertRaisesRegex(w.DefinitionHold,'bore-domain'):run(reseal(f))

    def test_rhs_real_material_cell(self):
        f=fixture();f[3][0]['geometry']=dict(kind='rhs',size_m=[.040,.040,.020],wall_m=.005);f[3][0]['at_m']=[.020,0.,-.010];f[2]['seams'][0]['contacts'][0]['cell_id']='z+'
        self.assertGreater(run(reseal(f))['net_volume_m3'],0.)

    def test_rhs_wall_interior_face_not_parent_free_space(self):
        f=fixture();f[3][0]['geometry']=dict(kind='rhs',size_m=[.040,.040,.020],wall_m=.005);f[3][0]['at_m']=[.020,0.,-.010];f[2]['seams'][0]['contacts'][0]['cell_id']='y+'
        with self.assertRaises(w.DefinitionHold):run(reseal(f))

    def test_overlapping_beads_refused(self):
        f=fixture([[[0.,-.010,0.],[0.,.010,0.]],[[0.,.010,0.],[0.,-.010,0.]]])
        with self.assertRaisesRegex(w.DefinitionHold,'interior-overlap'):run(f)

    def test_two_separated_beads_counted(self):
        f=fixture([[[0.,-.010,0.],[0.,0.,0.]],[[0.,0.,0.],[0.,.010,0.]]]);r=run(f);self.assertEqual(len(r['beads']),2);self.assertAlmostEqual(r['net_volume_m3'],.5*.003**2*.016)

    def test_reflection_refused(self):
        f=fixture();f[0]['rotation'][0][0]=-1.
        with self.assertRaisesRegex(ValueError,'Reflection'):run(reseal(f))

    def test_nonboolean_units_and_ids(self):
        f=fixture();f[2]['source_entity_sha256']='short'
        with self.assertRaisesRegex(ValueError,'SHA256'):run(f)
        f=fixture();f[0]['at_m'][0]=True
        with self.assertRaises(ValueError):run(reseal(f))

    def test_rate_and_density_unknowns_not_zero(self):
        for field,value in [('rate_USD_kg',[0.,1.,2.]),('density_bounds_kg_m3',[2600.]),('density_kg_m3',None),('rate_USD_kg',[True,5.,8.])]:
            f=fixture();f[4]['materials']['al5083'][field]=value
            with self.assertRaises((ValueError,TypeError)):run(f)

    def test_refusals_do_not_mutate_inputs(self):
        f=fixture();f[3][0]['geometry']['kind']='unknown';reseal(f);before=deepcopy(f)
        with self.assertRaises(w.DefinitionHold):run(f)
        self.assertEqual(f,before)

    def test_raw_source_pin_refusal_before_definition(self):
        with self.assertRaisesRegex(ValueError,'source raw/pin'):w.compile_definition(b'{}',pin=w.SOURCE,assignments={},request_id='a'*64)
        with self.assertRaisesRegex(ValueError,'SHA256'):w.compile_definition(b'{}',pin=w.SOURCE,assignments={},request_id='short')

    def synthetic_source(self, fs):
        entities=[];groups=[];parents={}
        for f in fs:
            entities.append(deepcopy(f[0]));groups.append(deepcopy(f[1]));parents.update({p['id']:deepcopy(p) for p in f[3]})
        entities.extend(parents.values())
        physical={'synthetic':True,'parts':[e['id'] for e in entities]}
        src=dict(candidate_id=w.identity(physical),physical_definition=physical,source_sha256={'engineering/terminal_installation.py':w.SOURCE_MODULE_SHA256},component_proposal=dict(units='m',local_axes=['u outward','v lateral','w up'],entities=entities,stock_groups=groups),materials=deepcopy(fs[0][4]['materials']),process_and_QA=deepcopy(fs[0][4]['process']))
        src=w.seal(src);raw=(json.dumps(src,sort_keys=True,separators=(',',':'))+'\n').encode();pin=dict(candidate_id=src['candidate_id'],evaluation_id=src['evaluation_id'],raw_sha256=w.sha256(raw).hexdigest());return src,raw,pin

    def test_tiny_source_orchestration_preserves_held_owner(self):
        f=fixture();src,raw,pin=self.synthetic_source([f]);before=deepcopy(src)
        with patch.object(w,'SOURCE',pin),patch.object(w,'PATTERNS',(('roof/standoff-weld/*',1),)):
            r=w.compile_definition(raw,pin=pin,assignments={},request_id='b'*64)
        self.assertEqual(r['source_proposal_unchanged'],before);self.assertEqual(r['defined_welds'],0);self.assertFalse(r['complete_finite_weld_definition']);self.assertTrue(r['held'][0]['old_source_retained']);self.assertEqual(r['held'][0]['old_stock_owner_id'],f[1]['id']);self.assertIsNone(r['canonical_definition'])

    def test_tiny_source_orchestration_single_definition(self):
        f=fixture();src,raw,pin=self.synthetic_source([f])
        with patch.object(w,'SOURCE',pin),patch.object(w,'PATTERNS',(('roof/standoff-weld/*',1),)):
            r=w.compile_definition(raw,pin=pin,assignments={f[0]['id']:f[2]},request_id='b'*64)
        self.assertEqual(r['defined_welds'],1);self.assertTrue(r['complete_finite_weld_definition']);self.assertFalse(r['physical_accepted']);self.assertFalse(r['canonical_admitted']);self.assertEqual(r['source_proposal_unchanged'],src)

    def test_cross_record_geometry_overlap_holds_definition(self):
        f=fixture();g=fixture();g[0]['id']='roof/standoff-weld/1';g[1]['id']='stock/'+g[0]['id'];g[1]['entity_ids']=[g[0]['id']];g[2]['source_entity_id']=g[0]['id'];reseal(g);src,raw,pin=self.synthetic_source([f,g])
        with patch.object(w,'SOURCE',pin),patch.object(w,'PATTERNS',(('roof/standoff-weld/*',2),)):
            r=w.compile_definition(raw,pin=pin,assignments={f[0]['id']:f[2],g[0]['id']:g[2]},request_id='b'*64)
        self.assertEqual(r['defined_welds'],2);self.assertEqual(len(r['cross_record_intersections']),1);self.assertFalse(r['complete_finite_weld_definition'])

    def test_tiny_source_duplicate_stock_owner_refused(self):
        f=fixture();src,raw,pin=self.synthetic_source([f]);src.pop('evaluation_id');src['component_proposal']['stock_groups'].append(deepcopy(f[1]));src=w.seal(src);raw=(json.dumps(src,sort_keys=True,separators=(',',':'))+'\n').encode();pin.update(evaluation_id=src['evaluation_id'],raw_sha256=w.sha256(raw).hexdigest())
        with patch.object(w,'SOURCE',pin),patch.object(w,'PATTERNS',(('roof/standoff-weld/*',1),)):
            with self.assertRaisesRegex(ValueError,'Duplicate source stock'):w.compile_definition(raw,pin=pin,assignments={},request_id='b'*64)

    def test_tiny_source_units_refused(self):
        f=fixture();src,raw,pin=self.synthetic_source([f]);src.pop('evaluation_id');src['component_proposal']['units']='mm';src=w.seal(src);raw=(json.dumps(src,sort_keys=True,separators=(',',':'))+'\n').encode();pin.update(evaluation_id=src['evaluation_id'],raw_sha256=w.sha256(raw).hexdigest())
        with patch.object(w,'SOURCE',pin),patch.object(w,'PATTERNS',(('roof/standoff-weld/*',1),)):
            with self.assertRaisesRegex(ValueError,'metre terminal axes'):w.compile_definition(raw,pin=pin,assignments={},request_id='b'*64)




def groove_fixture(with_bore=False):
    L,b,h,t=.090,.024,.040,.0032;T=[.2,.3,.4];g=dict(kind='rhs',size_m=[L,b,h],wall_m=t,corner_bevels=dict(count=4,leg_m=.002,length_m=L,separately_owned_filler=True));holesV=0.;holeM=[0.,0.,0.]
    if with_bore:
        c=[-.020,0.,h/2-t/2];g['holes']=[dict(axis=2,centre_m=c,radius_m=.001,length_m=t)];holesV=math.pi*.001**2*t;holeM=w.scale(c,holesV)
    fullV=L*(b*h-(b-2*t)*(h-2*t));oldRemoved=4*.5*.002**2*L
    p=dict(id='floor/support/invented',material_id='al5083',frame='terminal-local-UVW',scope='installed',at_m=T,rotation=deepcopy(w.I),geometry=g,centroid_local_m=w.scale(holeM,-1/(fullV-holesV)))
    policy=fixture()[4];rho=[2580.2,2660.,2739.8];rates=policy['materials']['al5083']['rate_USD_kg'];lab=policy['process']['labour_USD_h'];cuts=[[L,h,t],[L,h,t],[L,b-2*t,t],[L,b-2*t,t]];gross=sum((a+.011)*(bb+.004)*c for a,bb,c in cuts)
    def stock(eid,V,gv):
        return dict(id='stock/'+eid,entity_ids=[eid],quantity=1,net_m3=V,gross_m3=gv,process_h=.1,QA_h=.05,net_mass_kg={c:V*rho[j] for j,c in enumerate(w.CASES)},gross_mass_kg={c:gv*rho[j] for j,c in enumerate(w.CASES)},scrap_mass_kg={c:(gv-V)*rho[j] for j,c in enumerate(w.CASES)},direct_cost_usd={c:gv*rho[j]*rates[j]+.15*lab[j] for j,c in enumerate(w.CASES)})
    pg=stock(p['id'],fullV-holesV-oldRemoved,gross);pg.update(individual_plate_cuts_m=cuts,corner_bevel_removal_m3=oldRemoved)
    e=dict(id=p['id']+'/long-seams',material_id='al5083',frame='terminal-local-UVW',scope='installed',at_m=T,rotation=deepcopy(w.I),physical_drawing=dict(kind='triangular-weld-seams',leg_m=.002,in_prepared_grooves=True,local_segments_m=[[[-L/2,sy*b/2,sz*h/2],[L/2,sy*b/2,sz*h/2]] for sy in (-1,1) for sz in (-1,1)]))
    return [p,pg,e,stock(e['id'],oldRemoved,1.2*oldRemoved),policy]

def groove_run(f,**kw):return w.fabricated_butt_revision(*f,trim_start_m=.001,trim_end_m=.001,**kw)


class GrooveTests(unittest.TestCase):
    def test_joint_centred_grooves_replace_credit_once(self):
        f=groove_fixture();before=deepcopy(f);r=groove_run(f);a=r['accounting'];self.assertEqual(f,before);self.assertEqual(len(r['grooves']),4);self.assertEqual(a['source_paid_gross_count'],1);self.assertFalse(a['old_removal_charge_repeated']);self.assertEqual(a['parent_new_gross_m3'],f[1]['gross_m3']);self.assertEqual(a['new_parent_material_purchase_m3'],0.)
        self.assertAlmostEqual(a['net_parent_volume_delta_m3']+a['net_filler_volume_delta_m3'],0.,places=16);self.assertAlmostEqual(r['combined_volume_conservation_residual_m3'],0.,places=16)
        self.assertTrue(all(abs(x)<1e-16 for x in r['combined_first_moment_residual_m4']));self.assertIsNone(a['additional_groove_tool_setup_process_QA_h']);self.assertFalse(r['physical_accepted']);self.assertFalse(r['native_eligible'])

    def test_two_actual_plate_half_grooves_each(self):
        r=groove_run(groove_fixture());p=r['source_parent'];b,h=p['geometry']['size_m'][1:];t=p['geometry']['wall_m']
        for q in r['grooves']:
            self.assertEqual(len(q['source_cells']),2);self.assertAlmostEqual(sum(q['half_groove_volumes_m3']),q['volume_m3']);self.assertAlmostEqual(abs(q['centroid_local_m'][1]),b/2-t);self.assertAlmostEqual(abs(q['centroid_local_m'][2]),h/2-.002/3)
            self.assertEqual(len(q['vertices_m']),6)

    def test_existing_top_wall_bore_and_corrected_first_moment(self):
        f=groove_fixture(True);r=groove_run(f);self.assertGreater(max(abs(x) for x in r['source_parent_centroid_model_residual_m']),0.)
        self.assertTrue(all(abs(x)<1e-16 for x in r['combined_first_moment_residual_m4']));self.assertEqual(r['physical_definition']['source_bores'],f[0]['geometry']['holes'])

    def test_asymmetric_trim_mass_and_first_moment(self):
        f=groove_fixture(True);r=w.fabricated_butt_revision(*f,trim_start_m=.001,trim_end_m=.002);self.assertAlmostEqual(r['filler_new_centroid_local_m'][0],-.0005);self.assertAlmostEqual(r['combined_volume_conservation_residual_m3'],0.,places=16);self.assertTrue(all(abs(x)<1e-16 for x in r['combined_first_moment_residual_m4']))

    def test_all_three_mass_cases_cancel_parent_filler_delta(self):
        f=groove_fixture();r=groove_run(f)
        for c in w.CASES:
            expected=f[1]['net_mass_kg'][c]+f[3]['net_mass_kg'][c];actual=r['accounting']['cases'][c]['parent_net_kg']+r['accounting']['cases'][c]['filler_net_kg'];self.assertAlmostEqual(expected,actual,places=12)

    def test_cost_policy_changes_eval_only(self):
        f=groove_fixture();a=groove_run(f);f[4]['materials']['al5083']['rate_USD_kg']=[4.,6.,9.]
        for g in [f[1],f[3]]:
            for j,c in enumerate(w.CASES):g['direct_cost_usd'][c]=g['gross_mass_kg'][c]*f[4]['materials']['al5083']['rate_USD_kg'][j]+.15*f[4]['process']['labour_USD_h'][j]
        b=groove_run(f);self.assertEqual(a['physical_definition_id'],b['physical_definition_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])

    def test_changed_trim_changes_geometry_id(self):
        f=groove_fixture();a=groove_run(f);b=w.fabricated_butt_revision(*f,trim_start_m=.002,trim_end_m=.002);self.assertNotEqual(a['physical_definition_id'],b['physical_definition_id'])

    def test_changed_source_removed_budget_refused(self):
        f=groove_fixture();f[1]['corner_bevel_removal_m3']*=2
        with self.assertRaisesRegex(ValueError,'Prior corner'):groove_run(f)

    def test_changed_old_filler_paths_not_relabelled(self):
        f=groove_fixture();f[2]['physical_drawing']['local_segments_m'][0][0][1]+=.001
        with self.assertRaisesRegex(ValueError,'source seam'):groove_run(f)

    def test_parent_or_weld_material_mismatch_refused(self):
        f=groove_fixture();f[2]['material_id']='stainless'
        with self.assertRaisesRegex(ValueError,'Same-material'):groove_run(f)

    def test_unconsumed_source_cut_refused(self):
        f=groove_fixture();f[0]['geometry']['unresolved_cut']={'kind':'arbitrary'}
        with self.assertRaisesRegex(w.DefinitionHold,'complete-fabricated'):groove_run(f)

    def test_bad_prior_price_refused_without_zero(self):
        f=groove_fixture();f[1]['direct_cost_usd']['base']=0.
        with self.assertRaisesRegex(ValueError,'cost policy'):groove_run(f)

    def test_plate_cut_roster_and_reused_stock_refused(self):
        for mode in ['cuts','owner']:
            f=groove_fixture()
            if mode=='cuts':f[1]['individual_plate_cuts_m'][0][1]+=.001
            else:f[1]['entity_ids'].append('another-owner')
            with self.assertRaisesRegex(ValueError,'paid plate cuts'):groove_run(f)

    def test_wrong_bore_domain_refused(self):
        f=groove_fixture(True);f[0]['geometry']['holes'][0]['centre_m'][1]=f[0]['geometry']['size_m'][1]/2-f[0]['geometry']['wall_m']
        with self.assertRaisesRegex(w.DefinitionHold,'contained-in-one'):groove_run(f)

    def test_reflection_and_nan_trim_refused(self):
        f=groove_fixture();f[0]['rotation'][0][0]=-1.
        with self.assertRaisesRegex(ValueError,'Reflection'):groove_run(f)
        with self.assertRaises(ValueError):w.fabricated_butt_revision(*groove_fixture(),trim_start_m=float('nan'),trim_end_m=.001)




def cavity_fixture(end=0,revised=False):
    f=groove_fixture();tube=deepcopy(f[0]);tube['id']='side-stiffener/invented/0/front';L,b,h=tube['geometry']['size_m'];t=tube['geometry']['wall_m'];T=tube['at_m'];R=tube['rotation'];side=1 if end==0 else -1
    if revised:
        ff=deepcopy(f);ff[0]['id']=tube['id'];ff[1]['id']='stock/'+tube['id'];ff[1]['entity_ids']=[tube['id']];ff[2]['id']=tube['id']+'/long-seams';ff[3]['id']='stock/'+ff[2]['id'];ff[3]['entity_ids']=[ff[2]['id']];tube=groove_run(ff)['replacement_parent_entity']
    plate=dict(id=tube['id']+'/endplate'+str(end),material_id='al5083',frame='terminal-local-UVW',scope='installed',at_m=w.world([side*(L/2+.004),0.,0.],T,R),rotation=deepcopy(R),geometry=dict(kind='box',size_m=[.008,b,h]))
    corners=[[side*L/2,y,z] for y,z in [(-(b/2-t),-(h/2-t)),(b/2-t,-(h/2-t)),(b/2-t,h/2-t),(-(b/2-t),h/2-t)]];paths=[[corners[j],corners[(j+1)%4]] for j in range(4)]
    e=deepcopy(f[2]);e.update(id=tube['id']+'/weld'+str(end),geometry=dict(kind='envelope',size_m=[.004,b,h]));e['physical_drawing']['local_segments_m']=paths
    V=.5*.002**2*sum(math.dist(*line) for line in paths);rho=[2580.2,2660.,2739.8];policy=f[4];stock=deepcopy(f[3]);stock.update(id='stock/'+e['id'],entity_ids=[e['id']],net_m3=V,gross_m3=V*1.2)
    for j,c in enumerate(w.CASES):stock['net_mass_kg'][c]=V*rho[j];stock['gross_mass_kg'][c]=V*1.2*rho[j];stock['scrap_mass_kg'][c]=V*.2*rho[j];stock['direct_cost_usd'][c]=V*1.2*rho[j]*policy['materials']['al5083']['rate_USD_kg'][j]+.15*policy['process']['labour_USD_h'][j]
    a=w.endplate_cavity_binding(e,stock,tube,plate,trim_m=.002)
    return [e,stock,a,[tube,plate],policy]


class CavityTests(unittest.TestCase):
    def test_two_real_endplate_interfaces_both_ends(self):
        for end in (0,1):
            f=cavity_fixture(end);r=run(f);self.assertEqual(len(r['beads']),4);self.assertTrue(r['net_volume_m3']>0.);self.assertEqual(r['source_assignment']['joint_domain'],'existing-source-cavity-fillet');self.assertFalse(r['physical_accepted']);self.assertFalse(r['canonical_admitted'])

    def test_revision_hash_and_voids_propagate_to_endplate(self):
        a=run(cavity_fixture(0,False));f=cavity_fixture(0,True);b=run(f)
        self.assertNotEqual(a['physical_definition_id'],b['physical_definition_id']);p=b['physical_definition']['parent_material'][0];self.assertIn('finite_void_prisms',p['geometry']);self.assertNotIn('corner_bevels',p['geometry'])
        self.assertEqual(f[2]['seams'][0]['contacts'][0]['source_parent_sha256'],w.identity(f[3][0]));self.assertEqual(len(p['finite_source_void_prisms']),4)

    def test_revised_parent_keeps_paid_blank_once(self):
        f=groove_fixture();r=groove_run(f);p=r['replacement_parent_entity'];g=r['replacement_parent_stock'];self.assertEqual(g['gross_m3'],f[1]['gross_m3']);self.assertNotIn('corner_bevel_removal_m3',g);self.assertEqual(g['source_void_credit_m3'],f[1]['corner_bevel_removal_m3']);self.assertEqual(g['new_void_removal_m3'],r['filler_new_volume_m3']);self.assertAlmostEqual(g['net_m3'],r['parent_new_volume_m3']);self.assertFalse(p['physical_accepted']);self.assertFalse(g['new_complete_cost_known'])

    def test_original_corner_voids_expanded_not_omitted(self):
        f=cavity_fixture();r=run(f);p=next(p for p in r['physical_definition']['parent_material'] if p['id']==f[3][0]['id']);self.assertEqual(len(p['finite_source_void_prisms']),4)

    def test_stale_old_parent_hash_cannot_reuse_new_parent(self):
        a=cavity_fixture(0,False);b=cavity_fixture(0,True);b[2]=a[2]
        with self.assertRaisesRegex(ValueError,'parent epoch'):run(b)

    def test_cavity_flag_cannot_waive_actual_contact(self):
        f=fixture();f[0]['physical_drawing']['in_prepared_grooves']=True;f[2]['joint_domain']='existing-source-cavity-fillet';reseal(f)
        with self.assertRaisesRegex(w.DefinitionHold,'actual-source-inner-wall'):run(f)

    def test_wrong_endplate_mapping_or_gap_refused(self):
        f=cavity_fixture();f[3][1]['id']=f[3][1]['id'].replace('endplate0','endplate1')
        with self.assertRaisesRegex(ValueError,'mapping'):w.endplate_cavity_binding(f[0],f[1],*f[3],trim_m=.002)
        f=cavity_fixture();f[3][1]['at_m'][0]+=.001;f[2]=w.endplate_cavity_binding(f[0],f[1],*f[3],trim_m=.002)
        with self.assertRaisesRegex(w.DefinitionHold,'contact-plane'):run(f)

    def test_short_runout_exposes_overlap_not_waived(self):
        f=cavity_fixture();f[2]=w.endplate_cavity_binding(f[0],f[1],*f[3],trim_m=.001)
        with self.assertRaisesRegex(w.DefinitionHold,'interior-overlap'):run(f)

    def test_old_corner_and_new_rosters_cannot_both_subtract(self):
        f=cavity_fixture(0,True);f[3][0]['geometry']['corner_bevels']=dict(count=4,leg_m=.002,length_m=f[3][0]['geometry']['size_m'][0],separately_owned_filler=True)
        with self.assertRaisesRegex(w.DefinitionHold,'exact-source-corner'):w.endplate_cavity_binding(f[0],f[1],*f[3],trim_m=.002)

    def test_finite_void_outside_or_ambiguous_cavity_refused(self):
        for mode in ('outside','inner'):
            f=cavity_fixture(0,True);cut=f[3][0]['geometry']['finite_void_prisms'][0]
            for v in cut['vertices_m']:v[2]+=.1 if mode=='outside' else -.010
            with self.assertRaises(w.DefinitionHold):w.endplate_cavity_binding(f[0],f[1],*f[3],trim_m=.002)




def legacy_fixture():
    R=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]];T=[.2,.3,.4];base=w.world([0.,.020,0.],T,R);axis=w.direction([0.,-1.,0.],R)
    c=dict(id='header/0',part_id='invented/profile',material='al6005a',old_entity_sha256='c'*64,geometry_hold=None,geometry=dict(kind='rhs',size_m=[.20,.040,.030],wall_m=.004,at_m=T,rotation=R),holes=[dict(kind='cylinder-cut',at_m=base,axis=axis,diameter_m=.002,length_m=.004,purpose='invented wall bore')],source_machining_list=[dict(diameter_m=.002,length_m=.004,quantity=1)])
    return dict(id='legacy/header/0',material_id='al6005a',frame='terminal-local-UVW',scope='installed',at_m=[v+.001 for v in T],rotation=deepcopy(w.I),geometry=dict(kind='envelope',size_m=[.04,.20,.03]),exact_CSG_entity=c)


def unique_face_fixture():
    f=fixture();f[3][0]['geometry']['size_m'][0]=.040;f[3][0]['at_m'][0]=0.;return reseal(f)


class ParentBindingTests(unittest.TestCase):
    def test_exact_legacy_signed_base_to_true_material_frame(self):
        f=legacy_fixture();before=deepcopy(f);p=w.legacy_parent_view(f,cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256);self.assertEqual(f,before);self.assertEqual(p['at_m'],[.2,.3,.4]);self.assertEqual(p['rotation'],f['exact_CSG_entity']['geometry']['rotation']);self.assertEqual(p['geometry']['kind'],'rhs')
        h=p['geometry']['holes'][0];self.assertEqual(h['axis'],1)
        for a,b in zip(h['centre_m'],[0.,.018,0.]):self.assertAlmostEqual(a,b,places=13)
        self.assertEqual(p['legacy_source_view']['exact_CSG_entity'],f['exact_CSG_entity']);self.assertFalse(p['legacy_source_view']['body_placement_or_stock_changed']);self.assertFalse(p['physical_accepted'])

    def test_source_cut_authority_must_be_exact(self):
        with self.assertRaisesRegex(ValueError,'CAD authority'):w.legacy_parent_view(legacy_fixture(),cut_authority_sha256='a'*64)

    def test_legacy_unknown_material_or_extra_geometry_refused(self):
        for field in ['material','geometry']:
            f=legacy_fixture()
            if field=='material':f['exact_CSG_entity']['material']='steel'
            else:f['exact_CSG_entity']['geometry']['hidden_void']={'kind':'box'}
            with self.assertRaises(w.DefinitionHold):w.legacy_parent_view(f,cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256)

    def test_legacy_count_mismatch_or_bool_axis_refused(self):
        f=legacy_fixture();f['exact_CSG_entity']['source_machining_list'][0]['quantity']=2
        with self.assertRaisesRegex(w.DefinitionHold,'count-disagreement'):w.legacy_parent_view(f,cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256)
        f=legacy_fixture();f['exact_CSG_entity']['holes'][0]['axis'][0]=True
        with self.assertRaises(ValueError):w.legacy_parent_view(f,cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256)

    def test_legacy_physical_geometry_not_price_or_packaging_proxy(self):
        f=legacy_fixture();a=w.legacy_parent_view(f,cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256);f['new_price_annotation']=999.;f['geometry']['size_m']=[9.,9.,9.];b=w.legacy_parent_view(f,cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256);self.assertEqual(w._parent(a)['physical'],w._parent(b)['physical']);self.assertNotEqual(w.identity(a),w.identity(b))

    def test_unique_material_faces_proposed_then_finite_definition(self):
        f=unique_face_fixture();a=w.propose_bound_faces(f[0],f[1],f[3],root_offsets_m=[[0.,0.,0.]],trim_start_m=.001,trim_end_m=.001,joint_domain='external-orthogonal-fillet');f[2]=a;r=run(f);self.assertGreater(r['net_volume_m3'],0.);self.assertEqual(a['seams'][0]['contacts'][0]['axis'],2);self.assertEqual(a['seams'][0]['contacts'][1]['axis'],0)

    def test_ambiguous_free_quadrants_are_not_arbitrarily_chosen(self):
        f=fixture()
        with self.assertRaisesRegex(w.DefinitionHold,'candidates=2'):w.propose_bound_faces(f[0],f[1],f[3],root_offsets_m=[[0.,0.,0.]],trim_start_m=.001,trim_end_m=.001,joint_domain='external-orthogonal-fillet')

    def test_geometry_gap_cannot_become_a_contact(self):
        f=unique_face_fixture();f[3][1]['at_m'][0]+=.001
        with self.assertRaisesRegex(w.DefinitionHold,'contact-not-established'):w.propose_bound_faces(f[0],f[1],f[3],root_offsets_m=[[0.,0.,0.]],trim_start_m=.001,trim_end_m=.001,joint_domain='external-orthogonal-fillet')

    def test_explicit_revised_offset_can_follow_revised_member(self):
        f=unique_face_fixture();a=run(f);f[3][1]['at_m'][0]+=.001;f[2]=w.propose_bound_faces(f[0],f[1],f[3],root_offsets_m=[[.001,0.,0.]],trim_start_m=.001,trim_end_m=.001,joint_domain='external-orthogonal-fillet');b=run(f);self.assertNotEqual(a['physical_definition_id'],b['physical_definition_id'])

    def test_visible_uncut_parent_overlap_is_a_hold(self):
        f=unique_face_fixture();f[3][1]['at_m'][2]-=.001
        with self.assertRaisesRegex(w.DefinitionHold,'definite-interior-overlap'):w.propose_bound_faces(f[0],f[1],f[3],root_offsets_m=[[0.,0.,0.]],trim_start_m=.001,trim_end_m=.001,joint_domain='external-orthogonal-fillet')

    def test_cavity_picker_keeps_proper_inner_faces(self):
        f=cavity_fixture();f[2]=w.propose_bound_faces(f[0],f[1],f[3],root_offsets_m=[[0.,0.,0.]]*4,trim_start_m=.002,trim_end_m=.002,joint_domain='existing-source-cavity-fillet');self.assertEqual(len(run(f)['beads']),4)

    def test_no_parent_invention_and_refusal_immutability(self):
        f=unique_face_fixture();before=deepcopy(f)
        with self.assertRaisesRegex(ValueError,'two distinct'):w.propose_bound_faces(f[0],f[1],[f[3][0]],root_offsets_m=[[0.,0.,0.]],trim_start_m=.001,trim_end_m=.001,joint_domain='external-orthogonal-fillet')
        self.assertEqual(f,before)




class PathRevisionTests(unittest.TestCase):
    def test_original_owner_and_policy_retained_once(self):
        f=fixture();before=deepcopy(f);p=w.revise_source_paths(f[0],f[1],f[4],segments_terminal_m=[[[0.,-.008,0.],[0.,.008,0.]]],joint_domain='external-orthogonal-fillet',reason='invented shorter finite joint');self.assertEqual(f,before);self.assertEqual(p['old_source_stock'],f[1]);self.assertEqual(p['replacement_stock']['id'],f[1]['id']);self.assertTrue(p['replacement_entity']['path_revision']['old_owner_retired_once']);self.assertIsNone(p['replacement_entity']['shape_I_per_kg']);self.assertLess(p['nominal_filler_volume_delta_m3'],0.);self.assertFalse(p['physical_accepted'])
        for c in w.CASES:self.assertGreater(p['replacement_stock']['direct_cost_usd'][c],0.)

    def test_revised_path_gets_real_definition_with_same_source_lineage(self):
        f=unique_face_fixture();p=w.revise_source_paths(f[0],f[1],f[4],segments_terminal_m=[[[0.,-.008,0.],[0.,.008,0.]]],joint_domain='external-orthogonal-fillet',reason='invented path change');f[0]=p['replacement_entity'];f[1]=p['replacement_stock'];f[2]=w.propose_bound_faces(f[0],f[1],f[3],root_offsets_m=[[0.,0.,0.]],trim_start_m=.001,trim_end_m=.001,joint_domain='external-orthogonal-fillet');r=run(f);self.assertEqual(r['source_entity']['path_revision']['original_stock'],p['old_source_stock']);self.assertAlmostEqual(r['net_volume_m3'],.5*.003**2*.014)

    def test_revision_reason_is_eval_not_physical(self):
        f=fixture();kw=dict(segments_terminal_m=[[[0.,-.008,0.],[0.,.008,0.]]],joint_domain='external-orthogonal-fillet');a=w.revise_source_paths(f[0],f[1],f[4],reason='one rationale',**kw);b=w.revise_source_paths(f[0],f[1],f[4],reason='another rationale',**kw);self.assertEqual(a['physical_definition_id'],b['physical_definition_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])

    def test_revision_rejects_wrong_old_price_and_unknown_geometry(self):
        f=fixture();f[1]['direct_cost_usd']['base']+=1
        with self.assertRaisesRegex(ValueError,'ownership differs'):w.revise_source_paths(f[0],f[1],f[4],segments_terminal_m=[[[0.,-.008,0.],[0.,.008,0.]]],joint_domain='external-orthogonal-fillet',reason='bad original ownership')
        f=fixture()
        with self.assertRaises(ValueError):w.revise_source_paths(f[0],f[1],f[4],segments_terminal_m=[[[True,0.,0.],[0.,.008,0.]]],joint_domain='external-orthogonal-fillet',reason='boolean coordinate')

    def test_proper_rotated_revised_path_stays_in_actual_metres(self):
        f=fixture();R=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]];f[0]['rotation']=R;f[0]['at_m']=[1.,2.,3.];paths=[[[1.,2.,3.],[1.008,2.016,3.]]];p=w.revise_source_paths(f[0],f[1],f[4],segments_terminal_m=paths,joint_domain='external-orthogonal-fillet',reason='invented rotated diagonal');e=p['replacement_entity'];actual=[[w.world(q,e['at_m'],e['rotation']) for q in line] for line in e['physical_drawing']['local_segments_m']]
        for a,b in zip(actual[0],paths[0]):
            for x,y in zip(a,b):self.assertLess(abs(x-y),1e-12)




def butt_fixture():
    f=fixture();policy=f[4];rho=[2580.2,2660.,2739.8];ps=[];gs=[]
    for sign,label in [(-1,'bottom'),(1,'top')]:
        V=.05*.006*.025;p=dict(id='invented/'+label,material_id='al5083',frame='terminal-local-UVW',scope='installed',at_m=[0.,0.,sign*.0125],rotation=deepcopy(w.I),geometry=dict(kind='box',size_m=[.05,.006,.025]),mass_kg={c:V*rho[j] for j,c in enumerate(w.CASES)},centroid_local_m=[0.,0.,0.]);g=dict(id='stock/'+p['id'],entity_ids=[p['id']],quantity=1,gross_m3=1.2*V,net_m3=V);ps.append(p);gs.append(g)
    weld=deepcopy(f[0]);weld['physical_drawing']['leg_m']=.002;weld['physical_drawing']['local_segments_m']=[[[-.025,.003,0.],[.025,.003,0.]]];V=.5*.002**2*.05;g=deepcopy(f[1]);g.update(net_m3=V,gross_m3=V*1.2)
    for j,c in enumerate(w.CASES):g['net_mass_kg'][c]=V*rho[j];g['gross_mass_kg'][c]=V*1.2*rho[j];g['scrap_mass_kg'][c]=V*.2*rho[j];g['direct_cost_usd'][c]=V*1.2*rho[j]*policy['materials']['al5083']['rate_USD_kg'][j]+.15*policy['process']['labour_USD_h'][j]
    return [ps[0],ps[1],gs[0],gs[1],weld,g,policy]

def butt_run(f,**changes):
    kw=dict(root_segments_terminal_m=[[[-.025,.003,0.],[.025,.003,0.]]],joint_direction_m=[0.,0.,1.],surface_normals_m=[[0.,1.,0.]],half_width_m=.001,depth_m=.002,trim_start_m=.002,trim_end_m=.002,additional_process_h=.2,additional_QA_h=.1);kw.update(changes);return w.finite_surface_butt_revision(*f,**kw)


class ButtTests(unittest.TestCase):
    def test_two_half_voids_one_filler_and_mass_moment_conservation(self):
        f=butt_fixture();before=deepcopy(f);r=butt_run(f);self.assertEqual(f,before);self.assertEqual(len(r['replacement_parent_entities']),2);self.assertEqual(len(r['filler_pieces']),1);self.assertAlmostEqual(r['filler_net_volume_m3'],.001*.002*.046)
        for j,c in enumerate(w.CASES):
            rho=[2580.2,2660.,2739.8][j];old=sum(p['mass_kg'][c] for p in f[:2]);new=sum(p['mass_kg'][c] for p in r['replacement_parent_entities'])+r['accounting']['cases'][c]['new_filler_net_kg'];self.assertAlmostEqual(old,new,places=13)
            moments=[sum(p['mass_kg'][c]*p['centroid_terminal_cases_m'][c][k] for p in r['replacement_parent_entities'])+r['filler_first_volume_moment_m4'][k]*rho for k in range(3)];expected=[sum(p['mass_kg'][c]*p['at_m'][k] for p in f[:2]) for k in range(3)]
            for a,b in zip(moments,expected):self.assertAlmostEqual(a,b,places=14)
        self.assertFalse(r['physical_accepted']);self.assertFalse(r['canonical_admitted'])

    def test_new_cut_cost_not_free_or_charged_per_parent(self):
        r=butt_run(butt_fixture());a=r['accounting'];self.assertEqual(a['additional_preparation_process_h'],.2);self.assertEqual(a['additional_preparation_QA_h'],.1);self.assertIsNone(a['new_tool_machine_disposal_cost_USD']);self.assertFalse(a['complete_installed_cost'])
        for c,lab in zip(w.CASES,[6.,10.,16.]):self.assertAlmostEqual(a['cases'][c]['new_preparation_process_QA_USD'],.3*lab)
        self.assertTrue(a['retire_old_weld_owner_once'])

    def test_shared_parent_paid_owner_retained_once(self):
        f=butt_fixture();g=dict(id='stock/shared',entity_ids=[f[0]['id'],f[1]['id']],quantity=1,gross_m3=f[2]['gross_m3']+f[3]['gross_m3']);f[2]=deepcopy(g);f[3]=deepcopy(g);r=butt_run(f);self.assertEqual(len(r['accounting']['source_parent_owners']),1);self.assertEqual(len(r['accounting']['source_parent_owners'][0]['machined_parent_ids']),2)

    def test_wrong_parent_gap_refuses_air_groove(self):
        f=butt_fixture();f[1]['at_m'][2]+=.001
        with self.assertRaisesRegex(w.DefinitionHold,'real-parent-end'):butt_run(f)

    def test_wrong_surface_or_repeated_cut_refused(self):
        with self.assertRaises(w.DefinitionHold):butt_run(butt_fixture(),surface_normals_m=[[0.,-1.,0.]])
        line=[[-.025,.003,0.],[.025,.003,0.]]
        with self.assertRaisesRegex(w.DefinitionHold,'interiors-overlap'):butt_run(butt_fixture(),root_segments_terminal_m=[line,line],surface_normals_m=[[0.,1.,0.],[0.,1.,0.]])

    def test_too_deep_preparation_not_invented_material(self):
        with self.assertRaises(w.DefinitionHold):butt_run(butt_fixture(),depth_m=.007)

    def test_original_parent_gross_and_voids_not_charged_again(self):
        f=butt_fixture();r=butt_run(f)
        for p,op,g in zip(r['replacement_parent_entities'],r['parent_machining'],f[2:4]):self.assertEqual(op['paid_gross_m3'],g['gross_m3']);self.assertTrue(op['paid_gross_retained_once']);self.assertEqual(op['additional_parent_material_purchase_m3'],0.);self.assertEqual(len(p['geometry']['finite_void_prisms']),1)

    def test_cost_scope_changes_eval_only(self):
        f=butt_fixture();a=butt_run(f);b=butt_run(f,additional_QA_h=.2);self.assertEqual(a['physical_definition_id'],b['physical_definition_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])

    def test_changed_profile_changes_physical_identity(self):
        a=butt_run(butt_fixture());b=butt_run(butt_fixture(),depth_m=.0015);self.assertNotEqual(a['physical_definition_id'],b['physical_definition_id'])

    def test_unknown_mass_or_boolean_profile_refused(self):
        f=butt_fixture();f[0].pop('mass_kg')
        with self.assertRaisesRegex(w.DefinitionHold,'source-mass'):butt_run(f)
        f=butt_fixture();f[0]['centroid_local_m']=None
        with self.assertRaisesRegex(w.DefinitionHold,'centroid-proxy'):butt_run(f)
        with self.assertRaises(ValueError):butt_run(butt_fixture(),half_width_m=True)




class LegacyProxyFrameTests(unittest.TestCase):
    def test_declared_offcentre_proxy_preserved_in_world_frame(self):
        e=legacy_fixture();e.update(centroid_local_m=[.01,.02,.03],shape_I_per_kg=[[1.,0.,0.],[0.,2.,0.],[0.,0.,3.]],centroid_model_uncertainty_m=[.001,.002,.003]);before=deepcopy(e);p=w.legacy_parent_view(e,cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256)
        expected=w.world(e['centroid_local_m'],e['at_m'],e['rotation']);actual=w.world(p['centroid_local_m'],p['at_m'],p['rotation'])
        for a,b in zip(expected,actual):self.assertLess(abs(a-b),1e-13)
        self.assertEqual(p['shape_I_per_kg'],[[2.,0.,0.],[0.,1.,0.],[0.,0.,3.]]);self.assertEqual(p['centroid_model_uncertainty_m'],[.002,.001,.003]);self.assertEqual(e,before);self.assertTrue(p['legacy_source_view']['proxy_frame_reexpressed']);self.assertFalse(p['physical_accepted'])

    def test_missing_proxy_stays_unknown_not_zero(self):
        p=w.legacy_parent_view(legacy_fixture(),cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256);self.assertIsNone(p['centroid_local_m']);self.assertNotIn('shape_I_per_kg',p)




def connector_fixture(sign=1,z=3.):
    policy=fixture()[4];rho=[2580.2,2660.,2739.8];R=deepcopy(w.I);rootV=2.;rootlo=1.01;platefront=1.;parents=[];stocks=[]
    for label,size,T in [('root',[.1505,.07,.006],[rootlo+.1505/2,rootV,z]),('plate',[.012,.02,.12],[platefront-.006,rootV+sign*.025,z])]:
        V=size[0]*size[1]*size[2];p=dict(id='invented/'+label,part_id='invented/'+label,material_id='al5083',frame='terminal-local-UVW',scope='installed',at_m=T,rotation=deepcopy(R),geometry=dict(kind='box',size_m=size),mass_kg={c:V*rho[j] for j,c in enumerate(w.CASES)},centroid_local_m=[0.,0.,0.]);g=dict(id='stock/'+p['id'],entity_ids=[p['id']],quantity=1,net_m3=V,gross_m3=V*1.2);parents.append(p);stocks.append(g)
    old=deepcopy(fixture()[0]);old['at_m']=[rootlo,rootV+sign*.025,z];old['physical_drawing']['local_segments_m']=[[[0.,-.05,0.],[0.,.05,0.]]];old['physical_drawing']['leg_m']=.003;V=.5*.003**2*.1;wg=deepcopy(fixture()[1]);wg.update(net_m3=V,gross_m3=V*1.2)
    for j,c in enumerate(w.CASES):wg['net_mass_kg'][c]=V*rho[j];wg['gross_mass_kg'][c]=V*1.2*rho[j];wg['scrap_mass_kg'][c]=V*.2*rho[j];wg['direct_cost_usd'][c]=V*1.2*rho[j]*policy['materials']['al5083']['rate_USD_kg'][j]+.15*policy['process']['labour_USD_h'][j]
    root,plate=parents;rg,pg=stocks;bb=lambda p:[[p['at_m'][k]-p['geometry']['size_m'][k]/2,p['at_m'][k]+p['geometry']['size_m'][k]/2] for k in range(3)];rb=bb(root);eb=bb(plate);over=[max(rb[1][0],eb[1][0]),min(rb[1][1],eb[1][1])];cid='invented/connector';uncut=.01*.07*.006;cut=.001*.002*.066;leftV=2*.5*.003**2*.016;filler=2*cut+leftV;delta=uncut-2*cut+filler-V
    desc=lambda p,g:dict(id=p['id'],sha256=w.identity(p),stock_id=g['id'],stock_sha256=w.identity(g))
    row=dict(id=cid,source_root=desc(root,rg),source_endplate=desc(plate,pg),old_weld_to_replace_once=desc(old,wg),source_face_bounds=dict(root=rb,endplate=eb),new_connector_stock_proposal=dict(id=cid,geometry=dict(kind='box',size_m=[.01,.07,.006]),at_m=[(rootlo+platefront)/2,rootV,z],rotation=deepcopy(R),material_id='al5083',paid_blank_size_m=[.012,.072,.006],paid_blank_volume_m3=.012*.072*.006,finished_gross_volume_m3=uncut,net_volume_m3=uncut-cut,connector_new_cut_volume_m3=cut,existing_stock_credit_USD=0.,stock_owner_count=1,procurement_required=True),new_left_fillets=[dict(id=cid+'/left/'+str(s),contact_parent_ids=[plate['id'],cid],leg_m=.003,flat_runout_each_m=.002,outward_face_normals=[[1.,0.,0.],[0.,0.,float(s)]],root_line_m=[[platefront,over[0]+.002,z+s*.003],[platefront,over[1]-.002,z+s*.003]]) for s in (-1,1)],new_right_opposed_butt_grooves=[dict(id=cid+'/right/'+str(s),half_cut_parent_ids=[cid,root['id']],section_axes=[0,2],extrusion_axis=1,prior_void_credit=0.,nominal_root_between_opposed_grooves_m=.002,vertices_UW_m=[[rootlo-.001,z+s*.003],[rootlo+.001,z+s*.003],[rootlo,z+s*.001]],interval_m=[rb[1][0]+.002,rb[1][1]-.002]) for s in (-1,1)],new_filler_volume_m3=filler,retained_root_new_cut_volume_m3=cut,net_material_delta_vs_old_weld_kg={c:delta*rho[j] for j,c in enumerate(w.CASES)},manufacturing_estimate_inputs=dict(connector_cut_and_deburr_person_h=[.02,.04,.08],new_joint_setup_person_h=[.02,.04,.08],additional_QA_person_h=[.005,.01,.02],machine_rate_USD_h=None),known_source_tool_bounds=[dict(source_joint_id='invented/M4/'+str(j),source_joint_sha256=('a' if j==0 else 'b')*64,tool_radius_m=.01,insertion_m=.08,minimum_radial_projection_separation_m=.004) for j in (0,1)])
    return [row,root,rg,plate,pg,old,wg,policy]

def connector_run(f):return w.side_front_connector_revision(*f,binding_data_id=w.identity({'synthetic':True,'row':f[0]}))


class ConnectorTests(unittest.TestCase):
    def test_fixed_outline_geometry_four_beads_and_two_parent_debits(self):
        f=connector_fixture();before=deepcopy(f);r=connector_run(f);self.assertEqual(f,before);self.assertEqual(len(r['filler_pieces']),4);self.assertEqual(len(r['parent_machining']),2);self.assertAlmostEqual(r['filler_net_volume_m3'],4.08e-7);self.assertAlmostEqual(r['new_connector_stock']['net_m3'],4.068e-6);self.assertEqual(r['new_connector_stock']['paid_blank_size_m'],[.012,.072,.006]);self.assertFalse(r['physical_accepted']);self.assertFalse(r['native_eligible'])

    def test_exact_six_piece_mass_delta_no_percar_multiplier(self):
        sums={c:0. for c in w.CASES}
        for sign in (-1,1):
            for z in (3.,4.,5.):
                r=connector_run(connector_fixture(sign,z))
                for c in w.CASES:sums[c]+=r['net_mass_delta_kg'][c]
                self.assertIn('train multiplicity not applied',r['quantity_scope'])
        for c,expected in zip(w.CASES,[.0602837928,.06214824,.0640126872]):self.assertAlmostEqual(sums[c],expected,places=10)

    def test_filler_one_owner_and_paid_connector_once(self):
        r=connector_run(connector_fixture());a=r['accounting'];self.assertEqual(a['new_stock_owner_count'],1);self.assertTrue(a['retire_old_weld_once']);self.assertTrue(a['one_combined_filler_owner']);self.assertTrue(a['right_geometry_method_price_is_not_another_charge']);self.assertIsNone(a['machine_rate_USD_h']);self.assertFalse(a['complete_installed_cost']);self.assertIsNone(r['new_connector_stock']['QA_h']);self.assertEqual(r['new_connector_stock']['QA_owner_id'],a['old_weld_owner_id'])

    def test_physical_identity_excludes_QA_and_prices(self):
        f=connector_fixture();a=connector_run(f);f[0]['manufacturing_estimate_inputs']['additional_QA_person_h']=[.01,.02,.04];b=connector_run(f);self.assertEqual(a['physical_definition_id'],b['physical_definition_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])

    def test_bad_owner_hash_or_duplicate_quantity_refused(self):
        for field in ('hash','quantity'):
            f=connector_fixture()
            if field=='hash':f[0]['source_root']['sha256']='a'*64
            else:f[2]['quantity']=2;f[0]['source_root']['stock_sha256']=w.identity(f[2])
            with self.assertRaisesRegex(ValueError,'paid-owner'):connector_run(f)

    def test_changed_gap_or_blank_requires_drawing_revision(self):
        for field in ('gap','blank','width'):
            f=connector_fixture()
            if field=='gap':f[1]['at_m'][0]+=.001;f[0]['source_root']['sha256']=w.identity(f[1])
            elif field=='blank':f[0]['new_connector_stock_proposal']['paid_blank_size_m'][0]+=.001
            else:f[0]['new_connector_stock_proposal']['geometry']['size_m'][1]=.02
            with self.assertRaises(ValueError):connector_run(f)

    def test_left_contact_and_right_cut_vertices_must_be_exact(self):
        for field in ('left','right'):
            f=connector_fixture()
            if field=='left':f[0]['new_left_fillets'][0]['root_line_m'][0][1]+=.001
            else:f[0]['new_right_opposed_butt_grooves'][0]['vertices_UW_m'][0][0]+=.001
            with self.assertRaises(ValueError):connector_run(f)

    def test_existing_endplate_bores_stay_separate_from_new_filler(self):
        f=connector_fixture();p=f[3];V0=p['geometry']['size_m'][0]*p['geometry']['size_m'][1]*p['geometry']['size_m'][2];holes=[dict(axis=0,centre_m=[.00225,0.,z],radius_m=.002,length_m=.0075) for z in (-.020,.020)];p['geometry']['holes']=holes;p['centroid_local_m']=[-sum(math.pi*h['radius_m']**2*h['length_m']*h['centre_m'][k] for h in holes)/(V0-sum(math.pi*h['radius_m']**2*h['length_m'] for h in holes)) for k in range(3)];p['mass_kg']={c:(V0-sum(math.pi*h['radius_m']**2*h['length_m'] for h in holes))*rho for c,rho in zip(w.CASES,[2580.2,2660.,2739.8])};f[0]['source_endplate']['sha256']=w.identity(p);r=connector_run(f);self.assertEqual(r['source_endplate']['geometry']['holes'],holes);self.assertEqual(len(r['known_source_tool_projection_controls']),2)

    def test_tool_projection_bounds_not_silently_changed(self):
        f=connector_fixture();f[0]['known_source_tool_bounds'][0]['tool_radius_m']=.011
        with self.assertRaisesRegex(ValueError,'radial projection'):connector_run(f)

    def test_net_mass_or_paid_stock_budget_mismatch_refused(self):
        for field in ('net','stock'):
            f=connector_fixture()
            if field=='net':f[0]['net_material_delta_vs_old_weld_kg']['base']+=.001
            else:f[0]['new_connector_stock_proposal']['paid_blank_volume_m3']*=2
            with self.assertRaises(ValueError):connector_run(f)

    def test_boolean_count_or_unpriced_machine_is_explicit(self):
        f=connector_fixture();f[0]['new_connector_stock_proposal']['stock_owner_count']=True
        with self.assertRaises(ValueError):connector_run(f)
        f=connector_fixture();f[0]['manufacturing_estimate_inputs']['machine_rate_USD_h']=0.
        with self.assertRaisesRegex(ValueError,'unknown machine rate'):connector_run(f)




class ConnectorOwnerTests(unittest.TestCase):
    def test_derived_subtotal_is_two_payable_rows_not_an_extra_charge(self):
        r=connector_run(connector_fixture());a=r['accounting'];self.assertEqual(len(a['payable_rows']),2);self.assertEqual(len({x['owner_id'] for x in a['payable_rows']}),2);self.assertTrue(a['known_cases_are_derived_subtotals_not_extra_payable_rows']);self.assertEqual(len(r['replacement_weld_stock']['entity_ids']),4)
        for c in w.CASES:self.assertAlmostEqual(sum(x['direct_cost_usd'][c] for x in a['payable_rows']),a['known_cases'][c]['calculated_known_component_subtotal_USD'])

    def test_duplicate_filler_names_cannot_hide_occurrences(self):
        f=connector_fixture();f[0]['new_left_fillets'][1]['id']=f[0]['new_left_fillets'][0]['id']
        with self.assertRaisesRegex(ValueError,'Duplicate new finite filler'):connector_run(f)

if __name__=='__main__':unittest.main()

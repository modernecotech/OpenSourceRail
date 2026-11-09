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




def tie_fixture(sign=1):
    width=.003;depth=.0024;r=.0015;bottom=-.030;centre=.0015;A=width*(centre-bottom)+math.pi*r*r/2;cw=(width*(centre-bottom)*(bottom+centre)/2+(math.pi*r*r/2)*(centre+4*r/(3*math.pi)))/A
    slot=dict(width_m=width,depth_m=depth,bottom_W_m=bottom,round_end_centre_W_m=centre,closed_end_W_m=centre+r,end_radius_m=r,section_area_m2=A,removed_volume_m3=A*depth,removed_centroid_W_m=cw,tool='invented3mmflatendmill',remaining_tie_depth_m=.006-depth,source_bore_radial_ligament_m=.0004,local_wall_strength_qualified=False,slot_process_h_each=.10,slot_QA_h_each=.04,added_finish_surface_upper_reference_m2=A+(2*(centre-bottom)+math.pi*r+width)*depth)
    us=[a+b for a in (-.020,.020) for b in (-.006,.006)];holes=[dict(axis=1,centre_m=[u,0.,-.030],radius_m=.0041,length_m=.006) for u in (-.020,.020)];cs=[[u,sign*(.003-depth/2),-.030+cw] for u in us];V0=.070*.006*.120;cuts=[(math.pi*h['radius_m']**2*h['length_m'],h['centre_m']) for h in holes]+[(A*depth,c) for c in cs];V=V0-sum(x for x,c in cuts);C=[-sum(v*c[k] for v,c in cuts)/V for k in range(3)]
    d=dict(kind='tie-with-two-bores-and-four-open-roundended-extractor-slots',original_box_size_m=[.070,.006,.120],bores=deepcopy(holes),slot_spec=slot,slot_U_centres_local_m=us,bolt_W_local_m=-.030,opening='invented bottom opening',removed_centroids_local_m=cs,remaining_netsection_qualification=False)
    return dict(id='upper/'+str(sign)+'/frame-tie',part_id='invented/tie',material_id='al5083',frame='terminal-local-UVW',scope='installed',rotation=deepcopy(w.I),at_m=[.2,sign*2.,3.],geometry=dict(kind='envelope',size_m=[.070,.006,.120],holes=holes),physical_drawing=d,mass_kg={c:V*rho for c,rho in zip(w.CASES,[2580.2,2660.,2739.8])},centroid_local_m=C,shape_I_per_kg=None)


class MaterialUnionAndSlotTests(unittest.TestCase):
    def test_real_continuous_RHS_outerface_crosses_bookkeeping_cells(self):
        f=fixture([[[0.,-.0175,0.],[0.,.0175,0.]]]);f[0]['at_m']=[.01,0.,0.];f[0]['geometry']['size_m']=[.006,.041,.006]
        rhs=dict(id='invented/rhs',material_id='al5083',frame='terminal-local-UVW',scope='installed',at_m=[0.,0.,.015],rotation=deepcopy(w.I),geometry=dict(kind='rhs',size_m=[.100,.040,.030],wall_m=.003));block=dict(id='invented/block',material_id='al5083',frame='terminal-local-UVW',scope='installed',at_m=[0.,0.,-.005],rotation=deepcopy(w.I),geometry=dict(kind='box',size_m=[.020,.035,.010]));f[3]=[rhs,block];f[2]=w.propose_bound_faces(f[0],f[1],f[3],root_offsets_m=[[0.,0.,0.]],trim_start_m=.0001,trim_end_m=.0001,joint_domain='external-orthogonal-fillet');r=run(f);self.assertTrue(any(c['cell_id']=='outer-z-' for c in f[2]['seams'][0]['contacts']));self.assertGreater(r['net_volume_m3'],0.)

    def test_RHS_hollow_end_is_not_a_filled_contact_face(self):
        rhs=dict(id='invented/rhs',material_id='al5083',frame='terminal-local-UVW',at_m=[0.,0.,0.],rotation=deepcopy(w.I),geometry=dict(kind='rhs',size_m=[.100,.040,.030],wall_m=.003));p=w._parent(rhs)
        with self.assertRaises(w.DefinitionHold):w._face_normal_points(p,[1.,0.,0.],[[.050,-.010,0.],[.050,.010,0.]])

    def test_containment_in_real_RHS_union_not_only_one_plate(self):
        e=dict(id='invented/rhs',material_id='al5083',frame='terminal-local-UVW',at_m=[0.,0.,0.],rotation=deepcopy(w.I),geometry=dict(kind='rhs',size_m=[.100,.040,.030],wall_m=.003));p=w._parent(e);vs=[[x,y,z] for y in (-.019,.019) for x,z in [(-.001,.015),(.001,.015),(0.,.013)]];self.assertTrue(w._contained_in_RHS_material_union(vs,p));self.assertFalse(any(all(c['lo'][k]<=v[k]<=c['hi'][k] for v in vs for k in range(3)) for c in p['cells']))
        bad=deepcopy(vs)
        for v in bad:v[2]-=.003
        self.assertFalse(w._contained_in_RHS_material_union(bad,p))

    def test_round_slot_view_preserves_existing_voids_mass_and_provenance(self):
        for sign in (-1,1):
            e=tie_fixture(sign);before=deepcopy(e);p=w.upper_tie_parent_view(e);self.assertEqual(e,before);self.assertEqual(p['mass_kg'],e['mass_kg']);self.assertEqual(p['centroid_local_m'],e['centroid_local_m']);self.assertEqual(len(p['geometry']['open_round_slot_voids']),4);self.assertTrue(p['source_drawing_material_view']['already_counted_voids_preserved_once']);self.assertFalse(p['source_drawing_material_view']['new_removal_or_price_charge']);self.assertFalse(p['physical_accepted']);self.assertEqual(p['geometry']['open_round_slot_voids'][0]['face_sign'],sign)

    def test_slot_source_QA_notes_are_eval_only_geometry_lossless(self):
        e=tie_fixture();a=w.upper_tie_parent_view(e);e['physical_drawing']['slot_spec']['slot_QA_h_each']=.05;e['physical_drawing']['remaining_netsection_qualification']=True;b=w.upper_tie_parent_view(e);self.assertEqual(w._parent(a)['physical'],w._parent(b)['physical']);self.assertNotEqual(w.identity(a),w.identity(b));self.assertFalse(b['physical_accepted'])

    def test_slot_unknown_geometry_cannot_be_discarded(self):
        e=tie_fixture();e['physical_drawing']['slot_spec']['new_port']={'size_m':[1.,2.,3.]}
        with self.assertRaisesRegex(w.DefinitionHold,'unconsumed'):w.upper_tie_parent_view(e)

    def test_slot_sign_or_removed_centroid_mismatch_refused(self):
        e=tie_fixture(-1);e['physical_drawing']['removed_centroids_local_m'][0][1]*=-1
        with self.assertRaisesRegex(ValueError,'sign/frame'):w.upper_tie_parent_view(e)

    def test_slot_profile_or_bore_union_changes_refused(self):
        e=tie_fixture();e['physical_drawing']['slot_spec']['end_radius_m']=.002
        with self.assertRaises(w.DefinitionHold):w.upper_tie_parent_view(e)
        e=tie_fixture();e['physical_drawing']['bores'][0]['centre_m'][0]=-.026;e['geometry']['holes']=deepcopy(e['physical_drawing']['bores'])
        with self.assertRaises(ValueError):w.upper_tie_parent_view(e)

def routed_fixture(two_jobs=False,gap=False):
    f=butt_fixture();policy=f[6];rho=[2580.2,2660.,2739.8];ps=[deepcopy(f[0]),deepcopy(f[1]),deepcopy(f[1])];ps[2]['id']='invented/third';ps[2]['at_m'][2]=.0375
    gs=[]
    for p in ps:
        V=.050*.006*.025;gs.append(dict(id='stock/'+p['id'],entity_ids=[p['id']],quantity=1,net_m3=V,gross_m3=V*1.2,process_h=.1,QA_h=.05,net_mass_kg={c:V*rho[j] for j,c in enumerate(w.CASES)},gross_mass_kg={c:V*1.2*rho[j] for j,c in enumerate(w.CASES)},scrap_mass_kg={c:V*.2*rho[j] for j,c in enumerate(w.CASES)},direct_cost_usd={c:V*1.2*rho[j]*policy['materials']['al5083']['rate_USD_kg'][j]+.15*policy['process']['labour_USD_h'][j] for j,c in enumerate(w.CASES)}))
    welds=[];wg=[];routes={}
    for n in range(1 if two_jobs else 2):
        paths=[[[-.025,.003,z],[.025,.003,z]] for z in ([0.,.025] if two_jobs else [n*.025])];e=deepcopy(f[4]);e['id']='roof/standoff-weld/'+str(n);e['part_id']='invented/weld'+str(n);e['at_m']=[0.,0.,0.];e['physical_drawing']['local_segments_m']=paths;g=deepcopy(f[5]);g['id']='stock/'+e['id'];g['entity_ids']=[e['id']];V=.5*.002**2*.05*len(paths);g.update(net_m3=V,gross_m3=V*1.2)
        for j,c in enumerate(w.CASES):g['net_mass_kg'][c]=V*rho[j];g['gross_mass_kg'][c]=V*1.2*rho[j];g['scrap_mass_kg'][c]=V*.2*rho[j];g['direct_cost_usd'][c]=V*1.2*rho[j]*policy['materials']['al5083']['rate_USD_kg'][j]+.15*policy['process']['labour_USD_h'][j]
        welds.append(e);wg.append(g);ids=[p['id'] for p in (ps if two_jobs else ps[n:n+2])];r=dict(source_weld_id=e['id'],method='two-butt-jobs' if two_jobs else 'butt',parent_ids=ids,segments_terminal_m=paths,joint_direction_m=[0.,0.,1.],surface_normals_m=[[0.,1.,0.]]*len(paths),joint_domain='external-orthogonal-fillet',trim_start_m=.002,trim_end_m=.002,reason='Invented fixture joint')
        if two_jobs:r['pairs']=[[ps[0]['id'],ps[1]['id']],[ps[1]['id'],ps[2]['id']]]
        routes[e['id']]=r
    if gap:ps[2]['at_m'][2]+=.001
    entities=ps+welds;groups=gs+wg;byid={e['id']:e for e in entities};owners={eid:g for g in groups for eid in g['entity_ids']};src=dict(fixture='invented',materials=policy['materials'],process_and_QA=policy['process']);return src,byid,owners,{g['id']:g for g in groups},welds,routes


def routed_run(f):
    src,byid,owners,groups,welds,routes=f
    with patch.object(w,'route_record',side_effect=lambda e,p:deepcopy(routes[e['id']])):
        return w._compile_routed_source(src,byid,owners,groups,welds,pin=dict(candidate_id='a'*64),connector_binding=dict(rows=[]),cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256,request_id='b'*64,expected_records=len(welds))


class FullRoutingTests(unittest.TestCase):
    def test_shared_parent_two_cuts_debited_once_before_final_output(self):
        f=routed_fixture();before=deepcopy(f);r=routed_run(f);self.assertEqual(f,before);self.assertEqual(r['defined_weld_count'],2);self.assertEqual(r['held_weld_count'],0);self.assertTrue(r['complete_finite_weld_definition']);self.assertFalse(r['canonical_admitted']);self.assertFalse(r['physical_accepted']);mid='invented/top';u=r['parent_cut_unions'][mid];self.assertEqual(len(u['replacement_parent_entity']['geometry']['finite_void_prisms']),2);self.assertAlmostEqual(u['new_removed_volume_m3'],.001*.002*.046);row=r['accounting']['parent_stock_owner_revisions']['stock/'+mid];self.assertEqual(row['paid_gross_count'],1);self.assertEqual(row['replacement_owner']['gross_m3'],f[2][mid]['gross_m3']);self.assertEqual(row['replacement_owner']['direct_cost_usd'],f[2][mid]['direct_cost_usd']);self.assertIsNone(r['canonical_definition'])
        for c in w.CASES:self.assertAlmostEqual(row['replacement_owner']['net_mass_kg'][c],u['replacement_parent_entity']['mass_kg'][c])
        self.assertIsNone(u['replacement_parent_entity']['shape_I_per_kg'])

    def test_two_internal_jobs_keep_sealed_receipts_one_old_process_owner(self):
        r=routed_run(routed_fixture(two_jobs=True));eid=r['defined_welds'][0];p=r['parent_preparation_receipts'][eid];self.assertEqual(len(p['jobs']),2);self.assertEqual(len({x['id'] for x in p['pieces']}),2)
        for j in p['jobs']:self.assertEqual(j['evaluation_id'],w.identity({k:v for k,v in j.items() if k!='evaluation_id'}))
        g=r['accounting']['filler_replacement_owners'][eid];self.assertEqual(g['retained_original_process_h'],.1);self.assertEqual(g['retained_original_QA_h'],.05);self.assertEqual(g['additional_process_h'],.04);self.assertEqual(g['additional_QA_h'],.02);self.assertAlmostEqual(g['process_h'],.14);self.assertAlmostEqual(g['QA_h'],.07);self.assertEqual(len(r['accounting']['old_weld_dispositions']),1)

    def test_failed_shared_preparation_cannot_leave_orphan_cuts_or_filler(self):
        r=routed_run(routed_fixture(gap=True));self.assertEqual(r['defined_weld_count'],0);self.assertEqual(r['held_weld_count'],2);self.assertFalse(r['complete_finite_weld_definition']);self.assertEqual(r['final_changed_parent_entities'],{});self.assertEqual(r['accounting']['parent_stock_owner_revisions'],{});self.assertEqual(r['accounting']['filler_replacement_owners'],{});self.assertTrue(all(x['status']=='held-original-retained' for x in r['accounting']['old_weld_dispositions']));self.assertEqual(r['physical_definition']['filler'],[])

    def test_price_and_QA_changes_evaluation_not_full_physical_geometry(self):
        f=routed_fixture();a=routed_run(f);eid=f[4][0]['id'];g=f[2][eid];g['QA_h']+=.1
        for j,c in enumerate(w.CASES):g['direct_cost_usd'][c]+=.1*f[0]['process_and_QA']['labour_USD_h'][j]
        b=routed_run(f);self.assertEqual(a['physical_definition_id'],b['physical_definition_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])

    def test_public_full_entry_cannot_use_small_fixture_or_boolean_pin(self):
        with self.assertRaisesRegex(ValueError,'Exact full terminal source'):w.compile_full_definition(b'{}',pin=w.SOURCE,connector_binding={},cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256,request_id='c'*64)
        with self.assertRaisesRegex(ValueError,'Exact SHA256'):w.compile_full_definition(b'{}',pin=w.SOURCE,connector_binding={},cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256,request_id=True)

    def test_aggregate_duplicate_epoch_volume_and_overlap_refusals(self):
        f=butt_fixture();j=butt_run(f);p=f[0];g=f[2];cs=[dict(source_parent_sha256=w.identity(p),source_stock_sha256=w.identity(g),source_weld_id=f[4]['id'],cuts=w._extract_new_cuts(j,p))];a=w.aggregate_parent_cuts(p,g,cs,f[6]);self.assertAlmostEqual(a['new_removed_volume_m3'],j['parent_machining'][0]['new_removed_volume_m3'])
        for change in ('duplicate','epoch','volume','overlap'):
            q=deepcopy(cs)
            if change=='duplicate':q+=deepcopy(q)
            elif change=='epoch':q[0]['source_parent_sha256']='a'*64
            elif change=='volume':q[0]['cuts'][0]['volume_m3']*=2
            else:z=deepcopy(q[0]['cuts'][0]);z['id']+='/another';q[0]['cuts'].append(z)
            with self.assertRaises((ValueError,w.DefinitionHold)):w.aggregate_parent_cuts(p,g,q,f[6])

    def test_explicit_27_patterns_have_fixed_method_and_member_routes(self):
        class Roster(dict):
            def __contains__(self,k):return True
            def __getitem__(self,k):
                size=[.1,.04,.06];kind='rhs';g=dict(kind=kind,size_m=size,wall_m=.003)
                if k.startswith('floor/boss/'):g=dict(kind='box',size_m=[.020,.014,.006])
                return dict(id=k,material_id='al5083',frame='terminal-local-UVW',at_m=[0.,1.,0.],rotation=deepcopy(w.I),geometry=g)
        out=[]
        for p,q in w.PATTERNS:
            eid=p.replace('*','1');e=fixture()[0];e['id']=eid;e['physical_drawing']['local_segments_m']=[[[0.,0.,0.],[.05,0.,0.]]]*4;r=w.route_record(e,Roster());self.assertEqual(r['pattern'],p);self.assertTrue(r['parent_ids']);out.append(r['method'])
        self.assertEqual(len(out),27);self.assertEqual(set(out),{'fillet','butt','two-butt-jobs','fabricated-four-plate-butt','endplate-cavity','counted-gap-connector'})

    def test_aggregate_preserves_and_excludes_original_bore_domain(self):
        f=butt_fixture();j=butt_run(f);p=deepcopy(f[0]);g=f[2];p['geometry']['holes']=[dict(axis=1,centre_m=[0.,0.,.012],radius_m=.0004,length_m=.006)];cs=[dict(source_parent_sha256=w.identity(p),source_stock_sha256=w.identity(g),source_weld_id=f[4]['id'],cuts=w._extract_new_cuts(j,f[0]))]
        with self.assertRaisesRegex(w.DefinitionHold,'existing-source-void'):w.aggregate_parent_cuts(p,g,cs,f[6])

    def test_boss_retains14mm_stock_two_end_paths_and_heat_thread_hold(self):
        e=fixture()[0];e['id']='floor/boss/2/0.14/weld';e['physical_drawing']['local_segments_m']=[[[i,0.,0.],[i,.014,0.]] for i in range(4)];ps={k:dict(id=k,material_id='al5083',frame='terminal-local-UVW',at_m=[0.,0.,0.],rotation=deepcopy(w.I),geometry=dict(kind='box',size_m=[.020,.014,.006])) for k in ('floor/boss/2/0.14','floor/support/2')};r=w.route_record(e,ps);self.assertEqual(r['segments_terminal_m'],[e['physical_drawing']['local_segments_m'][1],e['physical_drawing']['local_segments_m'][3]]);self.assertEqual(r['nominal_thread_geometry']['lateral_major_ligament_m'],.005);self.assertIn('HAZ',r['reason']);ps['floor/boss/2/0.14']['geometry']['size_m'][1]=.010
        with self.assertRaises(w.DefinitionHold):w.route_record(e,ps)


if __name__=='__main__':unittest.main()


def invented_post_fixture(side=1):
    """Construct new tiny-account fixtures; never read a retained definition."""
    R=[[0.,1.,0.],[0.,0.,1.],[1.,0.,0.]];T=[-.050,side*1.165,.005];holes=[]
    for z in(-.85,-.51,-.17,.17,.51,.85):
        holes.extend([dict(kind='cylinder-cut',at_m=[-.004,side*1.2,z],axis=[1.,0.,0.],diameter_m=.0142,length_m=.004,purpose='invented sleeve-entry'),dict(kind='cylinder-cut',at_m=[-.100,side*1.2,z],axis=[1.,0.,0.],diameter_m=.0065,length_m=.004,purpose='invented opposite-wall')])
    for z in(-.95,.95):holes.append(dict(kind='cylinder-cut',at_m=[-.050,side*1.115,z],axis=[0.,float(side),0.],diameter_m=.003,length_m=.004,purpose='invented vent'))
    for u in(-.070,-.030):holes.append(dict(kind='cylinder-cut',at_m=[u,side*1.213,1.020],axis=[0.,float(side),0.],diameter_m=.0082,length_m=.004,purpose='owned detachable upper-frame bore,outer postwall only'))
    c=dict(id='invented/original-post',part_id='invented/post',material='al6005a',geometry=dict(kind='rhs',at_m=T,rotation=R,size_m=[2.190,.100,.100],wall_m=.004),geometry_hold=None,holes=holes,old_entity_sha256='a'*64,source_machining_list=[dict(diameter_m=.0142,length_m=.004,quantity=6),dict(diameter_m=.0065,length_m=.004,quantity=6),dict(diameter_m=.003,length_m=.004,quantity=2,purpose='invented prior vents')])
    V=2.190*(.1**2-.092**2)-sum(math.pi*(h['diameter_m']/2)**2*h['length_m'] for h in holes);rho=[2600.,2700.,2800.]
    e=dict(id='legacy/post/'+str(side),part_id='invented/post',material_id='al6005a',frame='terminal-local-UVW',scope='installed',at_m=T,rotation=deepcopy(w.I),geometry=dict(kind='envelope',size_m=[.1,.1,2.190]),mass_kg={k:V*rho[i] for i,k in enumerate(w.CASES)},centroid_local_m=[0.,0.,0.],shape_I_per_kg=None,uncertainty_m=[.02]*3,exact_CSG_entity=c)
    stock=dict(id='invented/shared-post-owner',entity_ids=['legacy/post/-1','legacy/post/1'],net_mass_kg={k:2*V*rho[i] for i,k in enumerate(w.CASES)},gross_mass_kg={k:2*2.35*(.1**2-.092**2)*rho[i] for i,k in enumerate(w.CASES)},scrap_mass_kg={k:2*(2.35*(.1**2-.092**2)-V)*rho[i] for i,k in enumerate(w.CASES)},direct_cost_usd={k:10.+i for i,k in enumerate(w.CASES)},additional_process_h=.4,additional_QA_h=None,source_account=dict(quantity=2,density_cases_kg_m3=rho))
    return e,stock


def invented_post_run(f):return w._post_bore_revision(*f,cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256)


class NewPostDrawingTests(unittest.TestCase):
    def test_signed_BASE_two_sides_fullwall_not_old_reinterpretation(self):
        for side in(-1,1):
            f=invented_post_fixture(side);old=deepcopy(f);r=invented_post_run(f);self.assertEqual(f,old)
            for q,u in zip(r['new_cut_drawing_records'],(-.070,-.030)):
                self.assertEqual(q['historical_signed_BASE']['at_m'],[u,side*1.213,1.020]);self.assertAlmostEqual(q['new_signed_BASE']['at_m'][1],side*1.211);self.assertAlmostEqual(q['BASE_translation_m'][1],-side*.002);self.assertAlmostEqual(q['actual_old_wall_overlap_m'],.002);self.assertAlmostEqual(q['new_actual_wall_removed_volume_m3'],2*q['old_actual_wall_removed_volume_m3'])
            p=r['replacement_parent_entity'];self.assertEqual(len(p['geometry']['holes']),16);self.assertEqual(len(r['inherited_cut_records']),14);self.assertEqual(len(r['inherited_machining_summary']),3);self.assertEqual(r['new_cut_drawing_records'][0]['new_signed_BASE']['axis'],[0.,float(side),0.]);self.assertFalse(r['physical_accepted']);self.assertIsNone(p['shape_I_per_kg'])
    def test_exact_nominal_integral_and_retained_uncertainty(self):
        f=invented_post_fixture();r=invented_post_run(f);m=r['nominal_material'];self.assertAlmostEqual(m['net_volume_m3'],m['gross_finished_rhs_volume_m3']-sum(x['volume_m3'] for x in m['cut_regions']))
        for k in range(3):self.assertAlmostEqual(m['centroid_intrinsic_m'][k],-sum(x['first_volume_moment_m4'][k] for x in m['cut_regions'])/m['net_volume_m3'])
        for c in w.CASES:
            self.assertAlmostEqual(r['accounting']['new_minus_previous_declared_mass_kg'][c],0.);self.assertGreater(r['accounting']['old_partial_wall_hypothesis_mass_kg'][c],r['accounting']['new_nominal_mass_kg'][c])
            for k in range(3):self.assertAlmostEqual(m['first_moment_bounds_kg_m'][c][k][0],r['accounting']['new_nominal_mass_kg'][c]*m['centroid_terminal_bounds_m'][k][0])
        self.assertEqual(m['source_spatial_uncertainty_m'],[.02]*3)
    def test_shared_paid_stock_allowance_and_originals_once(self):
        f=invented_post_fixture();r=invented_post_run(f);a=r['accounting'];self.assertEqual(a['source_owner'],f[1]);self.assertEqual(a['existing_shared_process_allowance_h'],.4);self.assertIsNone(a['per_hole_process_or_QA_split_h']);self.assertIsNone(a['new_BASE_location_fixture_tool_QA_USD']);self.assertEqual(a['additional_purchase_USD'],0.);self.assertTrue(a['new_mass_not_a_weight_saving_claim']);self.assertEqual(r['original_source_entity'],f[0])
    def test_exact_public_source_binding_refuses_invented_records(self):
        with self.assertRaisesRegex(ValueError,'Exact prospective'):w.prospective_post_revision(*invented_post_fixture(),cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256)
    def test_wrong_authority(self):
        with self.assertRaisesRegex(ValueError,'authority'):w._post_bore_revision(*invented_post_fixture(),cut_authority_sha256='f'*64)
    def test_extra_record_not_dropped(self):
        f=invented_post_fixture();f[0]['exact_CSG_entity']['holes'].append(deepcopy(f[0]['exact_CSG_entity']['holes'][-1]))
        with self.assertRaisesRegex(w.DefinitionHold,'14-plus2'):invented_post_run(f)
    def test_missing_extra_record_not_filled(self):
        f=invented_post_fixture();f[0]['exact_CSG_entity']['holes'].pop()
        with self.assertRaises(w.DefinitionHold):invented_post_run(f)
    def test_changed_addition_axis_radius_length_U_rejected(self):
        for key,value in [('axis',[0.,-1.,0.]),('diameter_m',.009),('length_m',.003),('at_m',[-.071,1.213,1.020])]:
            f=invented_post_fixture();f[0]['exact_CSG_entity']['holes'][14][key]=value
            with self.assertRaisesRegex(w.DefinitionHold,'exact-two'):invented_post_run(f)
    def test_missing_machining_summary_not_inferred(self):
        f=invented_post_fixture();f[0]['exact_CSG_entity']['source_machining_list'][0]['quantity']=5
        with self.assertRaisesRegex(w.DefinitionHold,'14-post'):invented_post_run(f)
    def test_duplicate_inherited_cylinder_refused(self):
        f=invented_post_fixture();f[0]['exact_CSG_entity']['holes'][2]=deepcopy(f[0]['exact_CSG_entity']['holes'][0])
        with self.assertRaises(w.DefinitionHold):invented_post_run(f)
    def test_wrong_datum_material_stock_dimensions(self):
        for mutate in (lambda e:e.update(material_id='steel'),lambda e:e['exact_CSG_entity']['geometry']['at_m'].__setitem__(1,1.166),lambda e:e['exact_CSG_entity']['geometry']['size_m'].__setitem__(1,.101)):
            f=invented_post_fixture();mutate(f[0])
            with self.assertRaises(w.DefinitionHold):invented_post_run(f)
    def test_allowance_not_doubled_or_zeroed(self):
        for v in(0.,.8):
            f=invented_post_fixture();f[1]['additional_process_h']=v
            with self.assertRaisesRegex(w.DefinitionHold,'already-priced'):invented_post_run(f)
    def test_unsupported_price_source_mass_or_uncertainty_refused(self):
        f=invented_post_fixture();f[0]['mass_kg']['base']*=1.001
        with self.assertRaisesRegex(w.DefinitionHold,'already-debited'):invented_post_run(f)
        f=invented_post_fixture();f[0].pop('uncertainty_m')
        with self.assertRaisesRegex(w.DefinitionHold,'uncertainty'):invented_post_run(f)
    def test_price_or_uncertainty_evaluation_only(self):
        f=invented_post_fixture();a=invented_post_run(f);f[1]['direct_cost_usd']['base']+=1.;b=invented_post_run(f);self.assertEqual(a['physical_definition_id'],b['physical_definition_id']);self.assertNotEqual(a['evaluation_id'],b['evaluation_id']);f[0]['uncertainty_m']=[.03]*3;c=invented_post_run(f);self.assertEqual(b['physical_definition_id'],c['physical_definition_id']);self.assertNotEqual(b['evaluation_id'],c['evaluation_id'])
    def test_historical_legacy_view_still_holds_14_vs16(self):
        with self.assertRaisesRegex(w.DefinitionHold,'machining-count'):w.legacy_parent_view(invented_post_fixture()[0],cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256)


def invented_post_wrapper_fixture():
    es=[];groups=[];posts=[]
    for side in(-1,1):
        p,g=invented_post_fixture(side);posts.append(p)
        e,stock,*_=fixture();e['id']='upper-frame/'+str(side)+'/0/boss-weld';e['part_id']='invented/weld';stock['id']='stock/'+e['id'];stock['entity_ids']=[e['id']];boss=dict(id='upper-frame/'+str(side)+'/0/boss',part_id='invented/boss',material_id='al5083',frame='terminal-local-UVW',at_m=[0.,0.,0.],rotation=deepcopy(w.I),geometry=dict(kind='box',size_m=[.02,.02,.02]));bg=dict(id='stock/'+boss['id'],entity_ids=[boss['id']],net_mass_kg={c:1. for c in w.CASES},gross_mass_kg={c:1. for c in w.CASES});es.extend([p,boss,e]);groups.extend([bg,stock])
    groups.append(g);by={e['id']:e for e in es};owners={eid:g for g in groups for eid in g['entity_ids']};welds=[e for e in es if e.get('physical_drawing')];policy=fixture()[4];return dict(src=dict(fixture='invented',materials=policy['materials'],process_and_QA=policy['process']),byid=by,owners=owners,groups={g['id']:g for g in groups},welds=welds,pin=dict(candidate_id='a'*64),connector_binding=dict(rows=[]),cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256,request_id='b'*64,expected_records=2)


class PostWrapperPropagationTests(unittest.TestCase):
    def test_two_corrected_post_entities_and_one_shared_owner_even_weldsheld(self):
        f=invented_post_wrapper_fixture()
        with patch.object(w,'prospective_post_revision',side_effect=lambda e,g,**kw:w._post_bore_revision(e,g,**kw)) as provider:r=w._compile_routed_source(**f)
        self.assertEqual(provider.call_count,2);self.assertEqual(len(r['source_post_revisions']),2);self.assertEqual(len(r['final_changed_parent_entities']),2);self.assertEqual(len(r['physical_definition']['changed_parents']),2);self.assertEqual(len(r['accounting']['source_post_owner_dispositions']),1);self.assertEqual(len(r['accounting']['parent_stock_owner_revisions']),1)
        owner=next(iter(r['accounting']['parent_stock_owner_revisions'].values()));self.assertEqual(owner['paid_gross_count'],1);self.assertEqual(owner['replacement_owner']['direct_cost_usd'],owner['source_owner']['direct_cost_usd']);self.assertEqual(r['held_weld_count'],2);self.assertFalse(r['installed_assembly_accepted']);self.assertEqual(len(r['accounting']['old_weld_dispositions']),2)
    def test_failed_material_view_memo_preserves_each_dependent_hold(self):
        f=invented_post_wrapper_fixture()
        for e in f['welds']:e['id']=e['id'].replace('/0/','/1/')
        # Use two records sharing one legacyheader, with distinct paid oldowners.
        es=[];gs=[]
        for i in(0,1):
            e,g,*_=fixture();e['id']='roof/standoff-weld/'+str(i);e['part_id']='invented/weld';g['id']='stock/'+e['id'];g['entity_ids']=[e['id']];p=dict(id='roof/standoff/'+str(i),part_id='invented/stand',material_id='al5083',frame='terminal-local-UVW',at_m=[0.,0.,0.],rotation=deepcopy(w.I),geometry=dict(kind='box',size_m=[.02,.02,.02]));es.extend([e,p]);gs.extend([g,dict(id='stock/'+p['id'],entity_ids=[p['id']])])
        h=dict(id='legacy/header/0',part_id='invented/header');es.append(h);gs.append(dict(id='invented/headerowner',entity_ids=[h['id']]));f.update(byid={e['id']:e for e in es},owners={eid:g for g in gs for eid in g['entity_ids']},groups={g['id']:g for g in gs},welds=[e for e in es if e.get('physical_drawing')])
        with patch.object(w,'legacy_parent_view',side_effect=w.DefinitionHold('invented deterministic held view')) as view:r=w._compile_routed_source(**f)
        self.assertEqual(view.call_count,1);self.assertEqual(len(r['held']),2);self.assertEqual({h['reason'] for h in r['held']},{'invented deterministic held view'});self.assertEqual(len(r['failed_parent_view_memo']),1);self.assertEqual(len(r['accounting']['old_weld_dispositions']),2);self.assertEqual(r['defined_weld_count'],0)


class PostRevisionInterfaceTests(unittest.TestCase):
    def test_public_binding_exact_both_entity_and_owner(self):
        f=invented_post_fixture();bindings={f[0]['id']:dict(entity_sha256=w.identity(f[0]),owner_sha256=w.identity(f[1]))}
        with patch.object(w,'POST_SOURCE_BINDINGS',bindings):
            r=w.prospective_post_revision(*f,cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256);self.assertEqual(len(r['new_cut_drawing_records']),2);f[1]['direct_cost_usd']['base']+=.01
            with self.assertRaisesRegex(ValueError,'shared-owner'):w.prospective_post_revision(*f,cut_authority_sha256=w.SOURCE_CUT_AUTHORITY_SHA256)
    def test_final_fillet_receives_revised_source_post(self):
        f=invented_post_wrapper_fixture();seen=[]
        def final_check(e,g,parents,**kw):
            post=next(p for p in parents if p['id'].startswith('legacy/post/'));seen.append(deepcopy(post));raise w.DefinitionHold('invented final geometry check')
        with patch.object(w,'prospective_post_revision',side_effect=lambda e,g,**kw:w._post_bore_revision(e,g,**kw)),patch.object(w,'propose_bound_faces',side_effect=final_check):r=w._compile_routed_source(**f)
        self.assertEqual(len(seen),2)
        for p in seen:
            self.assertEqual(len(p['geometry']['holes']),16);self.assertIn('prospective_post_revision',p);self.assertNotIn('exact_CSG_entity',p)
            for h in p['geometry']['holes'][14:]:self.assertAlmostEqual(abs(w.world(h['centre_m'],p['at_m'],p['rotation'])[1]),1.213)
        self.assertEqual(r['held_weld_count'],2)
    def test_failed_later_preparation_retains_base_post_no_orphan_cut(self):
        f=invented_post_wrapper_fixture();side=1;post=f['byid']['legacy/post/1'];sourceweld=f['welds'][1];sourceweld['id']='floor/post-bottom/1/post-closure-weld';oldstock=f['owners'].pop('upper-frame/1/0/boss-weld');oldstock['entity_ids']=[sourceweld['id']];oldstock['id']='invented/closure-weld-stock';closure=dict(id='floor/post-bottom/1/closure',part_id='invented/closure',material_id='al5083',frame='terminal-local-UVW',at_m=[0.,0.,0.],rotation=deepcopy(w.I),geometry=dict(kind='box',size_m=[.1,.1,.01]));cg=dict(id='invented/closure-stock',entity_ids=[closure['id']]);f.update(byid={sourceweld['id']:sourceweld,closure['id']:closure,post['id']:post},owners={sourceweld['id']:oldstock,closure['id']:cg,post['id']:f['owners'][post['id']]},groups={g['id']:g for g in(oldstock,cg,f['owners'][post['id']])},welds=[sourceweld],expected_records=1);seen=[]
        def prep(*args,**kw):seen.append(args[1]);raise w.DefinitionHold('invented later prep held')
        with patch.object(w,'prospective_post_revision',side_effect=lambda e,g,**kw:w._post_bore_revision(e,g,**kw)),patch.object(w,'finite_surface_butt_revision',side_effect=prep):r=w._compile_routed_source(**f)
        self.assertEqual(len(seen),1);self.assertIn('prospective_post_revision',seen[0]);self.assertIn(post['id'],r['final_changed_parent_entities']);self.assertFalse(r['accounting']['filler_replacement_owners']);self.assertFalse(r['parent_cut_unions']);self.assertEqual(r['held_weld_count'],1);self.assertEqual(len(r['accounting']['source_post_owner_dispositions']),1)


def independent_collision_pairs(pieces):
    """Scalar brute-force old predicate, no source bounds/SAT helper calls."""
    def sub(a,b):return[a[k]-b[k] for k in range(3)]
    def dot(a,b):return math.fsum(a[k]*b[k] for k in range(3))
    def cross(a,b):return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    def bbox(p):return[[min(v[k] for v in p['vertices']),max(v[k] for v in p['vertices'])] for k in range(3)]
    def edges(p):return[sub(p['vertices'][b],p['vertices'][a]) for f in p['faces'] for a,b in zip(f,f[1:]+f[:1])]
    def normals(p):return[cross(sub(p['vertices'][f[1]],p['vertices'][f[0]]),sub(p['vertices'][f[2]],p['vertices'][f[0]])) for f in p['faces']]
    def intersects(a,b):
        A=bbox(a);B=bbox(b)
        if not all(min(A[k][1],B[k][1])-max(A[k][0],B[k][0])>1e-10 for k in range(3)):return False
        for axis in normals(a)+normals(b)+[cross(e,f) for e in edges(a) for f in edges(b)]:
            L=math.sqrt(dot(axis,axis))
            if L<1e-18:continue
            q=[x/L for x in axis];pa=[dot(v,q) for v in a['vertices']];pb=[dot(v,q) for v in b['vertices']]
            if min(max(pa),max(pb))-max(min(pa),min(pb))<=1e-10:return False
        return True
    return[[a['id'],b['id']] for i,a in enumerate(pieces) for b in pieces[i+1:] if intersects(a['poly'],b['poly'])]


def collision_box(name,lo,hi,T=None,R=None):return dict(id='invented/'+name,poly=w._box(lo,hi,T or[0.,0.,0.],R or deepcopy(w.I)))


class FillerCollisionCacheTests(unittest.TestCase):
    def assertEquivalent(self,pieces):
        before=deepcopy(pieces);expected=independent_collision_pairs(pieces);actual=w._filler_intersections(pieces);self.assertEqual(actual,expected);self.assertEqual(pieces,before);return actual
    def test_empty_and_one(self):
        self.assertEqual(self.assertEquivalent([]),[]);self.assertEqual(self.assertEquivalent([collision_box('a',[-1.]*3,[1.]*3)]),[])
    def test_separated_and_exact_touching(self):
        for distance in(2.,3.):
            a=collision_box('a',[-1.]*3,[1.]*3);b=collision_box('b',[-1.]*3,[1.]*3,T=[distance,0.,0.]);self.assertEqual(self.assertEquivalent([a,b]),[])
    def test_EPS_threshold_and_nextafter_strict_screen(self):
        # Kernel numeric boundary fixture, not a subnanometre manufacturing claim.
        for overlap in(0.,.5e-10,1e-10,math.nextafter(1e-10,math.inf),2e-10):
            a=collision_box('a',[-1.,-1.,-1.],[0.,1.,1.]);b=collision_box('b',[-overlap,-1.,-1.],[1.,1.,1.]);r=self.assertEquivalent([a,b]);self.assertEqual(bool(r),overlap>1e-10)
    def test_rotated_AABB_overlap_can_still_be_SAT_separated(self):
        q=math.sqrt(.5);R=[[q,-q,0.],[q,q,0.],[0.,0.,1.]];a=collision_box('a',[-.5,-.05,-.05],[.5,.05,.05],R=R);b=collision_box('b',[-.5,-.05,-.05],[.5,.05,.05],T=[-.16,.16,0.],R=R);self.assertTrue(w.bounds_overlap(w.bounds(a['poly']['vertices']),w.bounds(b['poly']['vertices'])));self.assertEqual(self.assertEquivalent([a,b]),[])
    def test_rotated_actual_intersection(self):
        q=math.sqrt(.5);R=[[q,-q,0.],[q,q,0.],[0.,0.,1.]];a=collision_box('a',[-.5,-.05,-.05],[.5,.05,.05],R=R);b=collision_box('b',[-.5,-.05,-.05],[.5,.05,.05],T=[-.035,.035,0.],R=R);self.assertEqual(self.assertEquivalent([a,b]),[['invented/a','invented/b']])
    def test_triangular_filler_and_box_mixed(self):
        p=w._prism([0.,0.,0.],[0.,.02,0.],[1.,0.,0.],[0.,0.,1.],.003)['poly'];a=dict(id='invented/triangle',poly=p);b=collision_box('inside',[-.0001,.005,-.0001],[.0005,.015,.0005]);c=collision_box('far',[.1,.1,.1],[.2,.2,.2]);self.assertEqual(self.assertEquivalent([a,b,c]),[['invented/triangle','invented/inside']])
    def test_original_pair_order_even_when_sweep_order_reversed(self):
        pieces=[collision_box('z-last',[-1.]*3,[1.]*3,T=[.4,0.,0.]),collision_box('a-first',[-1.]*3,[1.]*3,T=[-.4,0.,0.]),collision_box('m-middle',[-1.]*3,[1.]*3)]
        self.assertEqual(self.assertEquivalent(pieces),[['invented/z-last','invented/a-first'],['invented/z-last','invented/m-middle'],['invented/a-first','invented/m-middle']])
    def test_equal_bounds_and_reused_poly_not_deduplicated(self):
        p=collision_box('unused',[-1.]*3,[1.]*3)['poly'];ps=[dict(id='invented/'+x,poly=p) for x in('c','a','b')];self.assertEqual(self.assertEquivalent(ps),[['invented/c','invented/a'],['invented/c','invented/b'],['invented/a','invented/b']])
    def test_single_cached_bounds_per_occurrence(self):
        ps=[collision_box(str(i),[-1.]*3,[1.]*3,T=[i*.2,0.,0.]) for i in range(8)];expected=independent_collision_pairs(ps)
        with patch.object(w,'bounds',wraps=w.bounds) as box:self.assertEqual(w._filler_intersections(ps),expected)
        self.assertEqual(box.call_count,len(ps))
    def test_separated_roster_skips_SAT_without_changing_pairs(self):
        ps=[collision_box(str(i),[-.01]*3,[.01]*3,T=[float(i),0.,0.]) for i in range(40)]
        with patch.object(w,'_interiors_overlap_sat',wraps=w._interiors_overlap_sat) as sat:self.assertEqual(w._filler_intersections(ps),independent_collision_pairs(ps))
        self.assertEqual(sat.call_count,0)
    def test_public_SAT_unchanged_against_independent_oracle(self):
        ps=[collision_box(str(i),[-.1,-.2,-.15],[.1,.2,.15],T=[x,y,z]) for i,(x,y,z) in enumerate(((0.,0.,0.),(.15,.1,.05),(.2,0.,0.),(.5,0.,0.)))];expected=independent_collision_pairs(ps);actual=[[a['id'],b['id']] for i,a in enumerate(ps) for b in ps[i+1:] if w.interiors_overlap(a['poly'],b['poly'])];self.assertEqual(actual,expected)
    def test_duplicate_occurrence_names_not_silently_collapsed_here(self):
        # Full wrapper retains its earlier unique-ID rejection before this helper.
        a=collision_box('same',[-1.]*3,[1.]*3);self.assertEqual(self.assertEquivalent([a,deepcopy(a)]),[['invented/same','invented/same']])

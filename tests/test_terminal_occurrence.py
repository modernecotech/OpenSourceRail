"""Invented miniature source records only; no retained candidate/evaluator calls."""
from copy import deepcopy
from fractions import Fraction
import unittest

from engineering.railway_project import terminal_occurrence as t


def sealed(v):
    v = deepcopy(v); v.pop('evaluation_id', None)
    return t.seal(v)


def fixture(retained_geometry=None):
    g = dict(kind='box', size_m=[.2,.3,.4], custom_machined_notch_m=.001)
    parts = [dict(id='old-end',material_id='al',quantity_per_train=2,stock=deepcopy(g)),
             dict(id='beam',material_id='al',quantity_per_train=1,stock=deepcopy(g))]
    patterns = [dict(id='old',part_id='old-end',count=2,positions_m=[[0.,0.,2.25],[105.25,0.,2.25]],
        rotation=t.I,geometry=deepcopy(g),direct_cost_usd=dict.fromkeys(t.CASES,100.)),
        dict(id='beam',part_id='beam',count=1,positions_m=[[1.,0.,1.]],rotation=t.I,
             geometry=deepcopy(g),direct_cost_usd=dict.fromkeys(t.CASES,20.))]
    if retained_geometry is not None:
        parts.append(dict(id='retained-stock',material_id='al',quantity_per_train=1,
                          stock=deepcopy(retained_geometry.get('source_stock'))))
        patterns.append(dict(id='retained-stock',part_id='retained-stock',count=1,
            positions_m=[[3.,0.,1.]],rotation=t.I,geometry=deepcopy(retained_geometry),
            direct_cost_usd=dict.fromkeys(t.CASES,11.)))
    layout = dict(cars=6,car_length_m=17.,car_width_m=2.65,intercar_gap_m=.65,floor_top_m=1.15,roof_z_m=3.55)
    physical = dict(layout=layout,config=dict(body_lift_m=.15),parts=parts,occurrence_patterns=patterns)
    parent = sealed(dict(schema='osr-vehicle-installation/1',candidate_id=t.identity(physical),
        physical_definition=physical,policy=dict(layout=deepcopy(layout)),parts=parts,patterns=patterns,**t.FLAGS))
    pp = dict(candidate_id=parent['candidate_id'],evaluation_id=parent['evaluation_id'],raw_sha256='a'*64)
    keys = ['source/'+t.identity([parent['candidate_id'],'old',j]) for j in range(2)]
    retire = [dict(operation='replace-or-relocate-once',old_count=2,source_ids=keys,
        source_occurrence_hashes=[dict(id=k,pattern_sha256=t.identity(patterns[0])) for k in keys],
        source_part_id='old-end',source_part_sha256=t.identity(parts[0]),retained_original_price_once=True)]
    mid = 'source/'+t.identity([parent['candidate_id'],'beam',0])
    machining = [dict(source_id=mid,source_part_sha256=t.identity(parts[1]),
        source_pattern_sha256=t.identity(patterns[1]),source_pattern_id='beam',source_position_index=0,
        kind='machine_in_place',source_part_id='beam',paid_source_cost_usd=dict.fromkeys(t.CASES,20.),
        gross_paid_source_retained=True,at_m=[1.,0.,1.],rotation=t.I,
        remaining_geometry=dict(kind='difference',outer=deepcopy(g),cuts=[dict(kind='cylinder-cut',diameter_m=.01)]),
        additional_process_USD=dict.fromkeys(t.CASES,7.))]
    bindings = [dict(id='terminal/front',car=0,source_end='body/terminal-end/end-0',at_m=[0.,0.,2.25],rotation=t.FRONT),
                dict(id='terminal/rear',car=5,source_end='body/terminal-end/end-5',at_m=[105.25,0.,2.25],rotation=t.I)]
    original_phys = dict(kind='box',size_m=[.1,.1,.1])
    epoch = dict(candidate_id=t.identity(original_phys),evaluation_id='b'*64,raw_sha256='c'*64)
    terminal = sealed(dict(schema='osr-terminal-canonical-normalization-packet/1',source_parent=pp,
        source_pin=epoch,source_physical_definition=original_phys,source_bindings=bindings,
        old_leaf_replacements_train_once=retire,source_machining_train_once=machining,
        floor_wear_patch_unapplied=dict(automatically_applied=False,precondition='later source only'),**t.FLAGS))
    terminal_pin = dict(evaluation_id=terminal['evaluation_id'],raw_sha256='d'*64,source_commit='e'*40)
    exact_J = [[26.,-4.,-6.],[-4.,20.,-12.],[-6.,-12.,10.]]
    es = [dict(id='point',frame='terminal-local-UVW',scope='installed',at_m=[1.,2.,3.],rotation=t.I,
               mass_kg=dict.fromkeys(t.CASES,1.),centroid_local_m=[0.,0.,0.],shape_I_per_kg=t.I,
               uncertainty_m=[.02]*3),
          dict(id='bounded',frame='terminal-local-UVW',scope='installed',at_m=[1.,2.,3.],rotation=t.I,
               mass_label_cases_kg=[2.,2.,2.],mass_properties_terminal_frame=dict(
                   mass_first_moment_interval_kg_m=[[2.,2.],[4.,4.],[6.,6.]],
                   inertia_about_frame_origin_interval_kg_m2=[[[v,v] for v in row] for row in exact_J])),
          dict(id='finish-a',frame='terminal-local-UVW',scope='prospective-local-installed-material',at_m=[0.,0.,0.],rotation=t.I,mass_kg=None),
          dict(id='finish-b',frame='terminal-local-UVW',scope='prospective-local-installed-material',at_m=[0.,0.,0.],rotation=t.I,mass_kg=None)]
    gs = [dict(id='paid-a',entity_ids=['point','finish-a'],direct_cost_usd=dict.fromkeys(t.CASES,10.)),
          dict(id='paid-b',entity_ids=['bounded','finish-b'],direct_cost_label_cases_USD=[15.,15.,15.],
               part_account_rows=[dict(cost=9999.,nonpayable=True)])]
    material = [dict(id=e['id'],domain='source-material-record',physical_record=dict(
        geometry=deepcopy(g),at_m=e['at_m'],rotation=e['rotation'])) for e in es]
    projection = dict(schema='osr-terminal-local-material-revision-physical/1',units='m',frame='terminal-local-UVW',
        material_occurrences=material,material_owner_graph=[dict(owner_id=x['id'],entity_ids=sorted(x['entity_ids'])) for x in gs])
    finishes = [dict(operation_id='cut-a',source_entity_id='finish-a',paid_owner_id='paid-a',source_record=dict(union='opaque a')),
                dict(operation_id='cut-b',source_entity_id='finish-b',paid_owner_id='paid-b',source_record=dict(union='opaque b'))]
    pricing = dict(rows=[dict(owner_id=x['id'],scope='one-local-terminal-group',direct_cost_label_cases_USD=x.get('direct_cost_usd',x.get('direct_cost_label_cases_USD'))) for x in gs]+
        [dict(owner_id='process/'+x['operation_id'],scope='one-local-machining-operation-no-new-blank',source_operation_id=x['operation_id'],direct_cost_label_cases_USD=[2.,2.,2.]) for x in finishes],
        common_source_residual_account=dict(each_row_used_once=True,unresolved_QA_split=None))
    counts = dict(local_material_occurrences=4,local_stock_groups=2,finishing_source_occurrences=2,finishing_paid_groups=2)
    plan = sealed(dict(schema='osr-terminal-local-revision-plan/1',physical_definition=projection,
        local_component_geometry_id=t.identity(projection),source_local_epoch=epoch,
        ancestry=dict(terminal_evaluation_id=terminal['evaluation_id']),source_input_pin=dict(sources=dict(terminal=terminal_pin)),
        canonical_definition=None,source_transactions_applied=False,deployment_quantity_multiplier_applied=1,
        deployment_data_unapplied=bindings,canonical_local_draft=dict(schema='osr-terminal-local-material-draft/1',
            entities=es,stock_groups=gs,material_projection=projection),
        P1_old_leaf_retirement_ledger_owned_once_by_terminal=retire,
        inherited_P1_retirements=[dict(new_P1_retirement_count=0,inherited_price_metadata_added_as_new_hardware_charge=False,source_keys=keys)],
        source_finishing_records=finishes,finishing_paid_owner_ids=['paid-a','paid-b'],counts=counts,
        pricing=pricing,lifecycle_allocations=dict(shared_tools=dict(piece_count=12,count_per_train=1),
            workshop=dict(quantity_scope='workshop'),events=dict(quantity_scope='per event',count=None)),
        pending_contracts=[dict(kind='finishing-material-properties-pending',resolved=False)],**t.FLAGS))
    pin = dict(schema='osr-terminal-occurrence-input-pin/1',sources=dict(parent=pp,terminal=terminal_pin,
        local_plan=dict(evaluation_id=plan['evaluation_id'],raw_sha256='f'*64,source_commit='1'*40,
                        local_component_geometry_id=plan['local_component_geometry_id'])),
        expected_counts=dict(counts,deployment_bindings=2,p1_retirement_groups=1,p1_retired_occurrences=2,source_machining_dispositions=1))
    return parent,terminal,plan,pin


def refresh_terminal(data):
    p,t0,plan,pin = data
    t0=sealed(t0); pin['sources']['terminal']['evaluation_id']=t0['evaluation_id']
    plan['ancestry']['terminal_evaluation_id']=t0['evaluation_id']
    plan['source_input_pin']['sources']['terminal']=deepcopy(pin['sources']['terminal'])
    return refresh_plan((p,t0,plan,pin))


def refresh_plan(data):
    p,t0,plan,pin=data
    plan['local_component_geometry_id']=t.identity(plan['physical_definition'])
    plan=sealed(plan);pin['sources']['local_plan']['evaluation_id']=plan['evaluation_id']
    pin['sources']['local_plan']['local_component_geometry_id']=plan['local_component_geometry_id']
    return p,t0,plan,pin


def run(data=None):
    p,t0,plan,pin=fixture() if data is None else data
    return t.compose(p,t0,plan,input_pin=pin,request_id='2'*64)


def retained_geometry(kind):
    if kind == 'cut-length':
        return dict(kind=kind,size_m=[1.2,.035,.035],exact_stock=False,
            finished_geometry_verified=False,definition_basis='proposed-route-zone',
            source_stock=dict(kind=kind,length_m=1.2,profile_description='Invented tube; wall and pressure rating unknown'))
    if kind == 'proposed-equipment-zone':
        return dict(kind=kind,size_m=[.2,.15,.12],exact_stock=False,
            finished_geometry_verified=False,definition_basis='proposed-bounded-component-zone',source_stock=None)
    return dict(kind='u_channel',size_m=[1.5,.035,.015],exact_stock=True,
        finished_geometry_verified=False,definition_basis='exact-gross-stock',
        source_stock=dict(kind='u_channel',length_m=1.5,width_m=.035,depth_m=.015,wall_m=.0015))


class RetainedParentDomainTests(unittest.TestCase):
    def test_parent_source_types_remain_complete_unadmitted_definitions(self):
        for kind in t.RETAINED_PARENT_KINDS:
            with self.subTest(kind=kind):
                g=retained_geometry(kind);d=fixture(g);before=deepcopy(d);r=run(d)
                self.assertEqual(d,before)
                self.assertEqual(r['physical_definition']['parent_physical_definition'],d[0]['physical_definition'])
                p=next(p for p in r['retained_parent_patterns'] if p['pattern_id']=='retained-stock')
                self.assertEqual(p['original_pattern_evaluation_record']['geometry'],g)
                self.assertEqual(p['retained_count'],1)
                self.assertIsNone(r['aggregate_mass_properties'])
                for flag in t.FLAGS:self.assertIs(r[flag],False)
                self.assertFalse(r['complete_installed_mass'])
                self.assertEqual(r['geometry_lift_to_apply_m'],0.)
                self.assertEqual(r['deployment_count'],2)

    def test_exact_source_node_paths_hashes_and_counts_do_not_become_material_quantities(self):
        for kind in t.RETAINED_PARENT_KINDS:
            with self.subTest(kind=kind):
                g=retained_geometry(kind);d=fixture(g);r=run(d)
                notes=r['retained_parent_source_domains'];self.assertEqual(len(notes),2 if kind!='proposed-equipment-zone' else 1)
                pat=next(p for p in d[0]['patterns'] if p['id']=='retained-stock')
                part=next(p for p in d[0]['parts'] if p['id']=='retained-stock')
                for note in notes:
                    self.assertEqual(note['pattern_id'],'retained-stock');self.assertEqual(note['part_id'],'retained-stock')
                    self.assertEqual(note['source_pattern_sha256'],t.identity(pat))
                    self.assertEqual(note['source_part_sha256'],t.identity(part))
                    self.assertEqual(note['source_geometry_sha256'],t.identity(g))
                    node=pat
                    for key in note['node_path']:node=node[key]
                    self.assertEqual(note['source_node_sha256'],t.identity(node))
                    self.assertEqual(note['original_pattern_count'],1);self.assertEqual(note['retained_pattern_count'],1)
                    self.assertIs(note['finished_geometry_supported'],False)
                    self.assertIs(note['geometry_operations_performed'],False)
                    self.assertIs(note['mass_properties_derived'],False)
                    self.assertIs(note['native_eligible'],False)
                    self.assertIn('node counts are not material',note['count_scope'])
                self.assertEqual(r['unresolved_obligations']['retained_parent_geometry_domains'],notes)
                self.assertEqual(r['counts']['parent_source_occurrences'],4)
                self.assertEqual(r['counts']['parent_retained_occurrences'],2)

    def test_parent_source_prices_and_train_once_accounts_are_not_recounted_per_node(self):
        baseline=run()
        for kind in t.RETAINED_PARENT_KINDS:
            with self.subTest(kind=kind):
                r=run(fixture(retained_geometry(kind)))
                self.assertEqual(r['pricing']['known_additive_subtotal_usd'],dict.fromkeys(t.CASES,81.))
                self.assertEqual(len(r['pricing']['payable_owner_rows']),6)
                # Parent-key hashes change with the source definition; their
                # once-only counts and shared lifecycle scope do not.
                self.assertEqual(r['lifecycle_allocations'],baseline['lifecycle_allocations'])
                self.assertEqual(len(r['p1_retirement_ledger']),2)
                self.assertEqual(len(r['source_machining_train_once']),1)
                self.assertEqual(r['additional_hardware_P1_retirements'],0)
                self.assertEqual(r['lifecycle_deployment_multiplier'],1)
                self.assertFalse(r['source_machining_geometry_applied'])
                self.assertEqual(r['pricing']['non_additive_process_allowances'][-1]['amount_usd'],dict.fromkeys(t.CASES,7.))

    def test_retained_source_graph_changes_are_identity_bound_without_new_geometry_claims(self):
        a=retained_geometry('cut-length');b=deepcopy(a)
        b['source_stock']['profile_description']='Different declared source tube; still unknown wall'
        ra,rb=run(fixture(a)),run(fixture(b))
        self.assertNotEqual(ra['candidate_id'],rb['candidate_id'])
        self.assertEqual(ra['pricing']['known_additive_subtotal_usd'],rb['pricing']['known_additive_subtotal_usd'])
        self.assertEqual(ra['terminal_material_occurrences'],rb['terminal_material_occurrences'])
        self.assertIsNone(ra['aggregate_mass_properties']);self.assertIsNone(rb['aggregate_mass_properties'])

    def test_retained_vocabulary_is_not_admitted_in_new_local_material_or_nested_unknowns(self):
        for kind in t.RETAINED_PARENT_KINDS:
            d=fixture();d[2]['physical_definition']['material_occurrences'][0]['physical_record']['geometry']=retained_geometry(kind)
            with self.subTest(new_local=kind),self.assertRaisesRegex(ValueError,'Unknown source geometry'):
                run(refresh_plan(d))
        g=retained_geometry('cut-length');g['new_feature']=dict(kind='unknown-milled-feature',depth_m=.001)
        with self.assertRaisesRegex(ValueError,'Unknown source geometry'):run(fixture(g))
        with self.assertRaisesRegex(ValueError,'Unknown source geometry'):run(fixture(dict(kind='unreviewed-equipment-zone',size_m=[1.,1.,1.])))

    def test_existing_supported_fixture_geometry_identity_is_unchanged(self):
        # Retained source-domain recognition changes evaluation coverage, not the
        # physical definition of this pre-existing independently reviewed control.
        r=run();self.assertEqual(r['candidate_id'],'203a96a3ccb2a86a3af31a2e075b063671b77cf986efbb0e63c39185de52f904')
        self.assertEqual(r['retained_parent_source_domains'],[])
        self.assertEqual(r['unresolved_obligations']['retained_parent_geometry_domains'],[])


def finished_fixture():
    """Two synthetic finished members/two paid owners, with separate other stock.

    This is a miniature consumption contract, not a substitute finisher or an
    actual hardpoint/ring geometry evaluation. Both moment reports are broad
    supplied bounds. No root apply_finishing/rebuild helper is called.
    """
    p,terminal,plan,pin=fixture()
    plan['ancestry'].update(weld_evaluation_id='3'*64,hardware_evaluation_id='4'*64)
    for name,ev in [('weld','3'*64),('hardware','4'*64)]:
        plan['source_input_pin']['sources'][name]=dict(evaluation_id=ev,raw_sha256='5'*64,source_commit='6'*40)
    es={e['id']:e for e in plan['canonical_local_draft']['entities']}
    gs={g['id']:g for g in plan['canonical_local_draft']['stock_groups']}
    gs['paid-a']['entity_ids']=['finish-a'];gs['paid-b']['entity_ids']=['finish-b']
    gs['other']=dict(id='other',entity_ids=['point','bounded'],direct_cost_usd=dict.fromkeys(t.CASES,5.))
    plan['canonical_local_draft']['stock_groups']=list(gs.values())
    plan['physical_definition']['material_owner_graph']=[dict(owner_id=k,entity_ids=sorted(g['entity_ids'])) for k,g in sorted(gs.items())]
    plan['counts'].update(local_stock_groups=3,finishing_operations=2)
    pin['expected_counts']['local_stock_groups']=3
    plan['pricing']['rows'].append(dict(owner_id='other',scope='one-local-terminal-group',direct_cost_label_cases_USD=[5.,5.,5.]))
    phys={x['id']:x for x in plan['physical_definition']['material_occurrences']}
    replacements=[];parents=[];owner_rows=[]
    outer=dict(kind='box',size_m=[2.,1.,1.]);cut=dict(kind='box',size_m=[1.,1.,1.],at_m=[-.5,0.,0.])
    union=dict(kind='union',pieces=[cut])
    report=dict(first_moment_interval_kg_m=[[-20.,20.]]*3,centroid_interval_m=[[-10.,10.]]*3,
        inertia_about_terminal_origin_interval_kg_m2=[[[0.,100.] if i==j else [-100.,100.] for j in range(3)] for i in range(3)],
        exact_point_CG_m=None,centroidal_tensor_kg_m2=None)
    broad=deepcopy(report);broad['first_moment_interval_kg_m']=[[-21.,21.]]*3
    broad['inertia_about_terminal_origin_interval_kg_m2']=[[[0.,200.] if i==j else [-200.,200.] for j in range(3)] for i in range(3)]
    props=dict(net_volume_interval_m3=[1.,1.],mass_interval_kg=[2.,2.],nominal_datum=report,
        with_source_position_uncertainty=broad,source_position_uncertainty_m=[.02]*3,
        method='Synthetic bounded consumer fixture; no geometry solver result',uniform_density_research_kg_m3=2.,physical_mass_CG_qualification=None)
    for i,req in enumerate(plan['source_finishing_records']):
        eid=req['source_entity_id'];oid=req['paid_owner_id'];g=gs[oid]
        g.update(direct_cost_usd=dict.fromkeys(t.CASES,10. if i==0 else 15.),gross_mass_kg=dict.fromkeys(t.CASES,10.))
        oldg=dict(id=oid,entity_ids=[eid],gross_mass_kg=deepcopy(g['gross_mass_kg']),direct_cost_usd=deepcopy(g['direct_cost_usd']),source_account=dict(density_cases_kg_m3=[2.,2.,2.]))
        old=dict(id=eid,at_m=[1.+i,2.,3.],rotation=t.I,material_id='al5083',uncertainty_m=[.02]*3,
            exact_CSG_entity=dict(geometry=deepcopy(outer),holes=[]))
        e=es[eid];e.update(at_m=old['at_m'],rotation=t.I,material_id='al5083',source_material_before_finishing=old)
        req['source_record']=dict(id=req['operation_id'],source_complete_void_union=deepcopy(union))
        req['physical_operation']=dict(kind='hardpoint-thread-pocket' if i==0 else 'ring-access-port-enlargement',complete_void_union=deepcopy(union))
        model=dict(kind='hardpoint-stopped-thread' if i==0 else 'ring-through-ports',
            minimum_material_graph=dict(kind='difference',outer=deepcopy(outer),cuts=[deepcopy(cut)]),
            maximum_material_graph=dict(kind='difference',outer=deepcopy(outer),cuts=[deepcopy(cut)]),
            complete_source_void_union=deepcopy(union),bounded_properties=deepcopy(props))
        nominal=dict(id=eid,material_id='al5083',source_pose=dict(at_m=old['at_m'],rotation=t.I),
            source_declared_finishing=deepcopy(req['physical_operation']),
            nominal_source_geometry=dict(material_id='al5083',geometry=deepcopy(outer),holes=[]))
        parents.append(nominal)
        replacements.append(dict(source_entity_id=eid,source_stock_owner_id=oid,
            source_entity_sha256=t.identity(old),source_owner_sha256=t.identity(oldg),
            source_entity_ancestry=deepcopy(old),source_finishing_operation=deepcopy(req['source_record']),
            material_id='al5083',frame='terminal-local-UVW',source_pose=deepcopy(nominal['source_pose']),
            old_incremental_H_removal_is_not_debited=True,transaction_applied=False,complete_material_rebuild=model))
        owner_rows.append(dict(source_owner_id=oid,source_owner_sha256=t.identity(oldg),source_owner_ancestry=deepcopy(oldg),
            source_occurrence_ids=[eid],paid_blank_group_count=1,new_stock_purchase_count=0,
            paid_gross_mass_kg=deepcopy(oldg['gross_mass_kg']),source_direct_price_retained_once=deepcopy(oldg['direct_cost_usd']),
            complete_rebuilt_net_mass_interval_kg=[2.,2.],rebuilt_scrap_mass_interval_kg=[8.,8.],
            new_material_charge=False,source_price_credit=False,transaction_applied=False))
        g.update(source_paid_group_before_finishing=oldg)
    # Authenticate an invented pre-application local epoch, before replacing its
    # material domain. This is provenance only, not a producer execution.
    terminal['canonical_draft']=dict(entities=[deepcopy(r['source_entity_ancestry']) for r in replacements],
        stock_groups=[deepcopy(r['source_owner_ancestry']) for r in owner_rows])
    p,terminal,plan,pin=refresh_terminal((p,terminal,plan,pin))
    before_eval,before_geometry=plan['evaluation_id'],plan['local_component_geometry_id']
    es={e['id']:e for e in plan['canonical_local_draft']['entities']}
    gs={g['id']:g for g in plan['canonical_local_draft']['stock_groups']}
    phys={x['id']:x for x in plan['physical_definition']['material_occurrences']}
    fp=dict(schema='osr-terminal-complete-finishing-material-physical/1',units='m',frame='terminal-local-UVW',parents=parents)
    fin=sealed(dict(schema='osr-terminal-finishing-material-rebuild/1',source_input_pin=dict(schema='osr-terminal-finishing-input-pin/1',
        sources={name:{k:row[k] for k in ('evaluation_id','raw_sha256')} for name,row in plan['source_input_pin']['sources'].items()}),
        source_local_epoch=deepcopy(plan['source_local_epoch']),source_terminal_evaluation_id=terminal['evaluation_id'],
        source_weld_evaluation_id=plan['ancestry']['weld_evaluation_id'],source_hardware_evaluation_id=plan['ancestry']['hardware_evaluation_id'],
        physical_definition=fp,component_geometry_id=t.identity(fp),pending_draft_replacements=replacements,
        source_owner_conservation=owner_rows,counts=dict(finishing_operations=2,material_occurrences=2,hardpoints=1,backing_rings=1,paid_owner_groups=2,new_stock_purchases=0),
        source_transactions_applied=False,canonical_definition=None,pending_contracts=['Process and physical evidence remain open'],**t.FLAGS))
    fpin=dict(evaluation_id=fin['evaluation_id'],raw_sha256='7'*64,component_geometry_id=fin['component_geometry_id'],source_commit='8'*40)
    for r,nominal in zip(replacements,parents):
        eid=r['source_entity_id'];e=es[eid];owner=gs[r['source_stock_owner_id']]
        phys[eid]=dict(id=eid,material_id='al5083',domain='bounded-complete-finished-source-material',physical_record=deepcopy(nominal))
        e.update(material_set_definition=deepcopy(phys[eid]),complete_material_rebuild=deepcopy(r['complete_material_rebuild']),
            bounded_properties=deepcopy(props),mass_kg=None,center_of_gravity_m=None,inertia_kg_m2=None,finishing_source_evaluation_id=fin['evaluation_id'])
        owner.update(complete_finished_owner_record=deepcopy(next(x for x in owner_rows if x['source_owner_id']==owner['id'])),
            net_mass_interval_kg=[2.,2.],scrap_mass_interval_kg=[8.,8.],net_mass_kg=None,scrap_mass_kg=None)
    plan['physical_definition']['material_occurrences']=[phys[k] for k in sorted(phys)]
    for req in plan['source_finishing_records']:req['complete_material_evaluation_id']=fin['evaluation_id']
    cleared=[dict(kind=kind,subject=req['operation_id'],resolved=False) for kind in ('finishing-material-properties-pending','density-context-unresolved') for req in plan['source_finishing_records']]
    plan['pending_contracts']=[dict(kind='bounded-finishing-source-and-process-evidence',resolved=False),dict(kind='other-source-obligation',resolved=False)]
    plan['finishing_application']=dict(schema='osr-terminal-local-finishing-application/1',
        input_pin=dict(schema='osr-terminal-local-finishing-input-pin/1',sources=dict(local_plan=dict(evaluation_id=before_eval,raw_sha256='9'*64),finishing={k:fpin[k] for k in ('evaluation_id','raw_sha256')})),
        parent_local_plan_evaluation_id=before_eval,parent_local_geometry_id=before_geometry,
        finishing_evaluation_id=fin['evaluation_id'],finishing_component_geometry_id=fin['component_geometry_id'],
        material_occurrences=2,paid_owners=2,cleared_calculation_holds=cleared,new_stock_purchases=0,new_P1_retirements=0,new_deployments=0,source_transactions_applied=False)
    data=refresh_plan((p,terminal,plan,pin))
    return data,fin,fpin


def refresh_finished(data,fin,fpin):
    fin['component_geometry_id']=t.identity(fin['physical_definition']);fin=sealed(fin)
    fpin['evaluation_id']=fin['evaluation_id'];fpin['component_geometry_id']=fin['component_geometry_id']
    plan=data[2];app=plan['finishing_application']
    app['finishing_evaluation_id']=fin['evaluation_id'];app['finishing_component_geometry_id']=fin['component_geometry_id']
    app['input_pin']['sources']['finishing']={k:fpin[k] for k in ('evaluation_id','raw_sha256')}
    for e in plan['canonical_local_draft']['entities']:
        if e['id'].startswith('finish-'):e['finishing_source_evaluation_id']=fin['evaluation_id']
    for req in plan['source_finishing_records']:req['complete_material_evaluation_id']=fin['evaluation_id']
    return refresh_plan(data),fin,fpin


def run_finished(data=None):
    data,fin,fpin=finished_fixture() if data is None else data
    parent,terminal,plan,pin=data
    return t.compose(parent,terminal,plan,input_pin=pin,request_id='2'*64,finishing=fin,finishing_pin=fpin)


class TerminalOccurrenceTests(unittest.TestCase):
    def test_two_exact_placements_unknown_and_bounded_properties(self):
        r=run(); poses={x['id']:x for x in r['terminal_evaluated_properties']}
        self.assertEqual(poses['terminal/front/point']['world_entity_pose']['at_m'],[-1.,-2.,5.25])
        self.assertEqual(poses['terminal/rear/point']['world_entity_pose']['at_m'],[106.25,2.,5.25])
        b=poses['terminal/front/bounded']['properties']
        self.assertEqual(b['kind'],'bounded')
        self.assertEqual(b['first_moment_about_body_origin_interval_kg_m'],[[-2.,-2.],[-4.,-4.],[10.5,10.5]])
        self.assertEqual(b['inertia_about_body_origin_interval_kg_m2'][0][0],[63.125,63.125])
        self.assertIsNone(b['exact_point_CG_m']);self.assertIsNone(b['centroidal_inertia'])
        u=poses['terminal/front/finish-a']['properties']
        self.assertEqual(u['kind'],'unknown');self.assertIsNone(u['mass_interval_kg'])
        self.assertEqual(poses['terminal/front/point']['properties']['kind'],'source-model-only')
        self.assertEqual(r['counts']['terminal_deployed_material_occurrences'],8)

    def test_source_refs_retirement_and_pending_machining_once(self):
        r=run()
        self.assertEqual(len(r['p1_retirement_ledger']),2)
        self.assertEqual(r['additional_hardware_P1_retirements'],0)
        for row in r['p1_retirement_ledger']:
            self.assertEqual(row['source_ref_sha256'],t.identity(row['source_ref']))
        self.assertEqual(r['counts']['parent_retained_occurrences'],1)
        m=r['source_machining_train_once'];self.assertEqual(len(m),1)
        self.assertFalse(m[0]['geometry_applied']);self.assertEqual(m[0]['additional_stock_purchase_count'],0)
        self.assertIn('custom_machined_notch_m',m[0]['original_geometry'])
        self.assertIn('remaining_geometry',m[0]['proposed'])

    def test_prices_owner_once_no_part_subtotals_or_process_overlap(self):
        r=run();cost=r['pricing']
        self.assertEqual(cost['known_additive_subtotal_usd'],dict.fromkeys(t.CASES,70.))
        self.assertEqual(len(cost['payable_owner_rows']),5)
        self.assertEqual(len(cost['non_additive_process_allowances']),5)
        self.assertFalse(cost['source_residual_applied'])
        self.assertEqual(r['lifecycle_allocations']['shared_tools']['piece_count'],12)
        self.assertEqual(r['lifecycle_deployment_multiplier'],1)
        self.assertEqual(r['geometry_lift_to_apply_m'],0.)
        self.assertEqual(r['deployment_count'],2)

    def test_finishing_contract_binds_exact_parents_owners_and_never_clears(self):
        r=run();c=r['finishing_supplement_contract']
        self.assertEqual(c['parent_entity_ids'],['finish-a','finish-b'])
        self.assertEqual(c['paid_owner_ids'],['paid-a','paid-b'])
        self.assertTrue(c['required']);self.assertFalse(c['resolved']);self.assertIsNone(c['accepted_supplement_schema'])
        for k in t.FLAGS:self.assertIs(r[k],False)
        self.assertIsNone(r['canonical_definition']);self.assertIsNone(r['aggregate_mass_properties'])

    def test_graph_fields_physical_price_and_properties_evaluation_only(self):
        a=fixture();r=run(a)
        b=fixture();b[2]['physical_definition']['material_occurrences'][0]['physical_record']['geometry']['custom_machined_notch_m']=.002
        b=refresh_plan(b);s=run(b)
        self.assertNotEqual(r['candidate_id'],s['candidate_id'])
        c=fixture();c[2]['canonical_local_draft']['stock_groups'][0]['direct_cost_usd']['base']=10.5
        c[2]['canonical_local_draft']['stock_groups'][0]['direct_cost_usd']['high']=11.
        c[2]['pricing']['rows'][0]['direct_cost_label_cases_USD']=dict(low=10.,base=10.5,high=11.)
        c=refresh_plan(c);priced=run(c)
        self.assertEqual(r['candidate_id'],priced['candidate_id']);self.assertNotEqual(r['evaluation_id'],priced['evaluation_id'])

    def test_deterministic_and_does_not_mutate_inputs_or_share_result(self):
        d=fixture();before=deepcopy(d);r=run(d)
        self.assertEqual(d,before);self.assertEqual(r,run(d))
        r['terminal_material_occurrences'][0]['material_definition']['physical_record']['geometry']['size_m'][0]=999.
        self.assertEqual(d,before)

    def test_refuses_unknown_geometry_or_domain(self):
        for field,value in [('domain','unreviewed-solid'),('kind','organic-magic')]:
            d=fixture();p=d[2]['physical_definition']['material_occurrences'][0]
            if field=='kind':p['physical_record']['geometry']['kind']=value
            else:p[field]=value
            with self.assertRaisesRegex(ValueError,'Unknown source'):
                run(refresh_plan(d))

    def test_refuses_stale_or_mixed_source_identity(self):
        for field in ('evaluation_id','local_component_geometry_id'):
            d=fixture();d[3]['sources']['local_plan'][field]='9'*64
            with self.assertRaises(ValueError):run(d)
        d=fixture();d[1]['source_parent']['candidate_id']='9'*64
        with self.assertRaisesRegex(ValueError,'Mixed parent'):
            run(refresh_terminal(d))

    def test_refuses_duplicate_retirement_and_hardware_retirement(self):
        d=fixture();d[2]['P1_old_leaf_retirement_ledger_owned_once_by_terminal'][0]['source_ids']*=2
        d[1]['old_leaf_replacements_train_once']=deepcopy(d[2]['P1_old_leaf_retirement_ledger_owned_once_by_terminal'])
        d[1]['old_leaf_replacements_train_once'][0]['old_count']=4
        d[2]['P1_old_leaf_retirement_ledger_owned_once_by_terminal'][0]['old_count']=4
        with self.assertRaisesRegex(ValueError,'Duplicate P1'):run(refresh_terminal(d))
        d=fixture();d[2]['inherited_P1_retirements'][0]['new_P1_retirement_count']=1
        with self.assertRaisesRegex(ValueError,'another P1'):run(refresh_plan(d))

    def test_refuses_duplicate_deployment_second_lift_or_12x(self):
        for update in ('duplicate','lift','multiplier'):
            d=fixture()
            if update=='duplicate':d[2]['deployment_data_unapplied'].append(deepcopy(d[2]['deployment_data_unapplied'][0]))
            elif update=='lift':d[2]['deployment_data_unapplied'][0]['at_m'][2]+=.15
            else:d[2]['deployment_quantity_multiplier_applied']=12
            with self.assertRaises(ValueError):run(refresh_plan(d))

    def test_refuses_stale_predecessor_or_reused_owner(self):
        d=fixture();d[2]['P1_old_leaf_retirement_ledger_owned_once_by_terminal'][0]['source_part_sha256']='9'*64
        d[1]['old_leaf_replacements_train_once']=deepcopy(d[2]['P1_old_leaf_retirement_ledger_owned_once_by_terminal'])
        with self.assertRaisesRegex(ValueError,'predecessor source hash'):run(refresh_terminal(d))
        d=fixture();d[2]['canonical_local_draft']['stock_groups'][1]['entity_ids'].append('point')
        with self.assertRaisesRegex(ValueError,'ownership'):run(refresh_plan(d))

    def test_refuses_price_double_count_unknown_fields_and_nan(self):
        d=fixture();d[2]['pricing']['rows'].append(deepcopy(d[2]['pricing']['rows'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate local payable'):run(refresh_plan(d))
        d=fixture();d[3]['pretend_finishing_resolved']=True
        with self.assertRaisesRegex(ValueError,'Closed input pin'):run(d)
        d=fixture();d[2]['physical_definition']['material_occurrences'][0]['physical_record']['geometry']['size_m'][0]=float('nan')
        with self.assertRaises(ValueError):run(d)

    def test_unknown_price_not_zero_and_not_outline_failure(self):
        d=fixture();d[2]['canonical_local_draft']['stock_groups'][0]['direct_cost_usd']=None
        d[2]['pricing']['rows'][0]['direct_cost_label_cases_USD']=None
        r=run(refresh_plan(d));cost=r['pricing']
        self.assertEqual(cost['known_additive_subtotal_usd'],dict.fromkeys(t.CASES,50.))
        self.assertEqual(cost['unknown_payable_owner_ids'],['terminal/front/paid-a','terminal/rear/paid-a'])
        self.assertIn('not outline failure',cost['scope'])

    def test_interval_transform_encloses_correlated_point_material_models(self):
        # Independent closed-form point-mass expectations, including negative
        # translation and off-diagonal signs. Marginal input correlations are
        # discarded conservatively, never promoted to a correlated scenario.
        b=dict(rotation=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]],at_m=[10.,-2.,3.])
        q=[1.,2.,3.];ms=[2.,3.]
        fm=[[min(m*x for m in ms),max(m*x for m in ms)] for x in q]
        Js=[[[m*((sum(x*x for x in q) if i==j else 0.)-q[i]*q[j]) for j in range(3)] for i in range(3)] for m in ms]
        J=[[[min(A[i][j] for A in Js),max(A[i][j] for A in Js)] for j in range(3)] for i in range(3)]
        f,origin=t._affine_moments(ms,fm,J,b)
        world=[8.,-1.,6.]
        for m in ms:
            for i in range(3):
                self.assertLessEqual(f[i][0],m*world[i]);self.assertGreaterEqual(f[i][1],m*world[i])
                for j in range(3):
                    exact=m*((sum(x*x for x in world) if i==j else 0.)-world[i]*world[j])
                    self.assertLessEqual(origin[i][j][0],exact);self.assertGreaterEqual(origin[i][j][1],exact)

    def test_unknown_mass_or_moments_preserved_without_inference(self):
        d=fixture();e=d[2]['canonical_local_draft']['entities'][1]
        e['mass_label_cases_kg']=None
        r=run(refresh_plan(d));b=r['terminal_evaluated_properties'][0]['properties']
        self.assertEqual(b['kind'],'unknown');self.assertIsNone(b['mass_interval_kg'])
        self.assertIsNone(b['first_moment_about_body_origin_interval_kg_m'])
        self.assertIsNotNone(b['source_property_record']['mass_properties_terminal_frame'])
        d=fixture();d[2]['canonical_local_draft']['entities'][1]['mass_properties_terminal_frame']['mass_first_moment_interval_kg_m']=None
        r=run(refresh_plan(d));b=r['terminal_evaluated_properties'][0]['properties']
        self.assertEqual(b['kind'],'bounded');self.assertEqual(b['mass_interval_kg'],[2.,2.])
        self.assertIsNone(b['first_moment_about_body_origin_interval_kg_m'])

    def test_refuses_false_zero_mass_and_boolean_deployment(self):
        d=fixture();d[2]['canonical_local_draft']['entities'][1]['mass_label_cases_kg']=[0.,0.,0.]
        with self.assertRaisesRegex(ValueError,'Positive source material'):run(refresh_plan(d))
        d=fixture();d[2]['deployment_quantity_multiplier_applied']=True
        with self.assertRaisesRegex(ValueError,'deployment refused'):run(refresh_plan(d))

    def test_refuses_unmapped_finishing_or_changed_paid_machining(self):
        d=fixture();d[2]['source_finishing_records'][0]['paid_owner_id']='paid-b'
        with self.assertRaisesRegex(ValueError,'finishing parent'):run(refresh_plan(d))
        d=fixture();d[1]['source_machining_train_once'][0]['paid_source_cost_usd']=dict.fromkeys(t.CASES,21.)
        with self.assertRaisesRegex(ValueError,'paid source owner price'):run(refresh_terminal(d))

    def test_refuses_unknown_pin_counts_and_false_acceptance(self):
        for target in ('source','counts'):
            d=fixture()
            if target=='source':d[3]['sources']['local_plan']['unknown']='not silently ignored'
            else:d[3]['expected_counts']['unknown']=0
            with self.assertRaisesRegex(ValueError,'Closed'):run(d)
        d=fixture();d[2]['native_eligible']=True
        with self.assertRaisesRegex(ValueError,'non-admitted'):run(refresh_plan(d))

    def test_outward_rounding_contains_binary_mass_translation_product(self):
        # Review witness: float(.1)*float(105.25) is not a singleton exact
        # rational endpoint. Compare with exact *binary-input* arithmetic.
        zero=[0.,0.];J=[[zero[:] for _ in range(3)] for _ in range(3)]
        fm,origin=t._affine_moments([.1,.1],[zero[:],zero[:],zero[:]],J,
            dict(rotation=t.I,at_m=[105.25,0.,0.]))
        exact=Fraction(.1)*Fraction(105.25)
        self.assertLessEqual(Fraction(fm[0][0]),exact)
        self.assertGreaterEqual(Fraction(fm[0][1]),exact)
        self.assertNotEqual(fm[0][0],fm[0][1])
        square=Fraction(.1)*Fraction(105.25)**2
        for k in (1,2):
            self.assertLessEqual(Fraction(origin[k][k][0]),square)
            self.assertGreaterEqual(Fraction(origin[k][k][1]),square)

    def test_outward_coefficients_and_cancellation_use_exact_binary_inputs(self):
        # Closed-form origin moments for decimal translation/first moments;
        # coefficients (.2**2+.3**2) and off-diagonals must not round early.
        mass=.1;T=[.1,.2,.3];p=[.4,.5,.6]
        z=[0.,0.];J=[[z[:] for _ in range(3)] for _ in range(3)]
        fm,origin=t._affine_moments([mass,mass],[[v,v] for v in p],J,
            dict(rotation=t.I,at_m=T))
        m=Fraction(mass);q=list(map(Fraction,p));a=list(map(Fraction,T))
        for i in range(3):
            exact=q[i]+m*a[i]
            self.assertLessEqual(Fraction(fm[i][0]),exact)
            self.assertGreaterEqual(Fraction(fm[i][1]),exact)
            for j in range(3):
                if i==j:
                    exact=m*sum(a[k]**2 for k in range(3) if k!=i)+2*sum(a[k]*q[k] for k in range(3) if k!=i)
                else:exact=-m*a[i]*a[j]-a[i]*q[j]-a[j]*q[i]
                self.assertLessEqual(Fraction(origin[i][j][0]),exact)
                self.assertGreaterEqual(Fraction(origin[i][j][1]),exact)

    def test_evaluated_pose_cannot_override_unchanged_physical_graph(self):
        d=fixture();before=d[2]['local_component_geometry_id']
        by={e['id']:e for e in d[2]['canonical_local_draft']['entities']}
        by['point']['at_m']=[20.,30.,40.]
        d=refresh_plan(d)
        self.assertEqual(before,d[2]['local_component_geometry_id'])
        with self.assertRaisesRegex(ValueError,'pose differs from physical'):
            run(d)

    def test_unbound_packaging_pose_is_not_reported_as_installed_pose(self):
        d=fixture();p=next(x for x in d[2]['physical_definition']['material_occurrences'] if x['id']=='point')
        p['physical_record'].pop('at_m');p['physical_record'].pop('rotation')
        r=run(refresh_plan(d))
        e=next(x for x in r['terminal_evaluated_properties'] if x['id']=='terminal/front/point')
        self.assertIsNone(e['world_entity_pose'])
        self.assertIn('packaging proxy is not an installed pose',e['world_entity_pose_status'])
        original=next(x for x in r['local_material_evaluation_records'] if x['id']=='point')
        self.assertEqual(original['at_m'],[1.,2.,3.])

    def test_present_flags_require_actual_boolean_false(self):
        for value in (0,1,None,'false',[],True):
            with self.subTest(value=value):
                d=fixture();d[2]['physical_accepted']=value
                with self.assertRaisesRegex(ValueError,'actual boolean False'):
                    run(refresh_plan(d))


class FinishedSupplementTests(unittest.TestCase):
    def test_explicit_complete_supplement_propagates_bounds_not_point_properties(self):
        r=run_finished();c=r['finishing_supplement_contract']
        self.assertTrue(c['resolved']);self.assertTrue(r['finishing_consumption']['calculation_supplement_resolved'])
        self.assertEqual(c['accepted_supplement_schema'],'osr-terminal-finishing-material-rebuild/1')
        rows={x['id']:x for x in r['terminal_evaluated_properties']}
        front=rows['terminal/front/finish-a']
        self.assertEqual(front['world_entity_pose']['at_m'],[-1.,-2.,5.25])
        props=front['properties'];self.assertEqual(props['kind'],'bounded')
        self.assertEqual(props['mass_interval_kg'],[2.,2.]);self.assertFalse(props['finishing_supplement_required'])
        self.assertEqual(props['source_position_uncertainty_terminal_axes_m'],[.02]*3)
        self.assertEqual(props['first_moment_about_body_origin_interval_kg_m'][2],[-16.5,25.5])
        self.assertEqual(props['body_frame_finishing_bounds']['nominal_datum']['first_moment_about_body_origin_interval_kg_m'][2],[-15.5,24.5])
        self.assertIsNone(props['exact_point_CG_m']);self.assertIsNone(props['centroidal_inertia'])
        self.assertIn('minimum_material_graph',props['source_property_record']['complete_material_rebuild'])
        self.assertEqual(r['pricing']['known_additive_subtotal_usd'],dict.fromkeys(t.CASES,80.))
        self.assertEqual(r['additional_hardware_P1_retirements'],0);self.assertEqual(len(r['p1_retirement_ledger']),2)
        self.assertEqual(r['lifecycle_deployment_multiplier'],1);self.assertEqual(r['geometry_lift_to_apply_m'],0.)
        self.assertTrue(r['accounting_coverage']['finishing_additivity_pending'])
        self.assertFalse(r['complete_installed_mass']);self.assertFalse(r['complete_installed_cost'])
        for key in t.FLAGS:self.assertIs(r[key],False)
        self.assertTrue(r['unresolved_obligations']['inherited_local_contracts'])

    def test_revised_plan_requires_packet_and_closed_pin_not_status_flag(self):
        data,fin,fpin=finished_fixture()
        with self.assertRaisesRegex(ValueError,'Explicit finishing packet'):
            run(data)
        fpin['unexpected']=True
        with self.assertRaisesRegex(ValueError,'Closed finishing pin'):
            run_finished((data,fin,fpin))
        data,fin,fpin=finished_fixture();data[2].pop('finishing_application')
        data=refresh_plan(data)
        with self.assertRaisesRegex(ValueError,'required together'):
            run_finished((data,fin,fpin))

    def test_mixed_finisher_source_epochs_or_raw_refs_refused(self):
        for mode in ('ancestry','raw','epoch'):
            data,fin,fpin=finished_fixture()
            if mode=='ancestry':fin['source_hardware_evaluation_id']='a'*64
            elif mode=='raw':fin['source_input_pin']['sources']['weld']['raw_sha256']='a'*64
            else:fin['source_local_epoch']['candidate_id']='a'*64
            with self.assertRaisesRegex(ValueError,'Mixed'):
                run_finished(refresh_finished(data,fin,fpin))

    def test_original_source_entities_bind_finishing_not_just_identity_labels(self):
        data,fin,fpin=finished_fixture()
        # Change the old member consistently inside new plan/finisher, retaining
        # the authenticated original terminal normalization. It must still fail.
        old=fin['pending_draft_replacements'][0]['source_entity_ancestry'];old['at_m']=[9.,9.,9.]
        row=fin['pending_draft_replacements'][0];row['source_entity_sha256']=t.identity(old)
        entity=next(e for e in data[2]['canonical_local_draft']['entities'] if e['id']=='finish-a')
        entity['source_material_before_finishing']=deepcopy(old)
        with self.assertRaisesRegex(ValueError,'original source record/hash'):
            run_finished(refresh_finished(data,fin,fpin))

    def test_mixed_owners_and_new_blank_dispositions_refused(self):
        data,fin,fpin=finished_fixture();fin['pending_draft_replacements'][0]['source_stock_owner_id']='paid-b'
        with self.assertRaisesRegex(ValueError,'source material/owner'):
            run_finished(refresh_finished(data,fin,fpin))
        data,fin,fpin=finished_fixture();fin['source_owner_conservation'][0]['new_stock_purchase_count']=1
        g=next(x for x in data[2]['canonical_local_draft']['stock_groups'] if x['id']=='paid-a')
        g['complete_finished_owner_record']=deepcopy(fin['source_owner_conservation'][0])
        with self.assertRaisesRegex(ValueError,'without purchase/credit'):
            run_finished(refresh_finished(data,fin,fpin))

    def test_material_model_and_nominal_physical_mismatches_refused(self):
        data,fin,fpin=finished_fixture()
        fin['pending_draft_replacements'][0]['complete_material_rebuild']['minimum_material_graph']['outer']['size_m'][0]=99.
        with self.assertRaisesRegex(ValueError,'graph/bounds differ'):
            run_finished(refresh_finished(data,fin,fpin))
        data,fin,fpin=finished_fixture();fin['physical_definition']['parents'][0]['nominal_source_geometry']['geometry']['size_m'][0]=99.
        with self.assertRaisesRegex(ValueError,'nominal material/pose'):
            run_finished(refresh_finished(data,fin,fpin))

    def test_invalid_or_false_point_material_bounds_refused(self):
        for mode in ('mass','point','uncertainty'):
            data,fin,fpin=finished_fixture();model=fin['pending_draft_replacements'][0]['complete_material_rebuild']
            if mode=='mass':model['bounded_properties']['mass_interval_kg']=[3.,3.]
            elif mode=='point':model['bounded_properties']['nominal_datum']['exact_point_CG_m']=[0.,0.,0.]
            else:model['bounded_properties']['source_position_uncertainty_m']=[.01]*3
            entity=next(e for e in data[2]['canonical_local_draft']['entities'] if e['id']=='finish-a')
            entity['complete_material_rebuild']=deepcopy(model);entity['bounded_properties']=deepcopy(model['bounded_properties'])
            with self.assertRaises(ValueError):
                run_finished(refresh_finished(data,fin,fpin))

    def test_owner_bound_conservation_is_required(self):
        data,fin,fpin=finished_fixture();owner=fin['source_owner_conservation'][0]
        owner['complete_rebuilt_net_mass_interval_kg']=[3.,3.]
        group=next(x for x in data[2]['canonical_local_draft']['stock_groups'] if x['id']=='paid-a')
        group['complete_finished_owner_record']=deepcopy(owner);group['net_mass_interval_kg']=[3.,3.]
        with self.assertRaisesRegex(ValueError,'constituent/gross conservation'):
            run_finished(refresh_finished(data,fin,fpin))

    def test_only_exact_calculation_holds_clear_and_other_evidence_stays_open(self):
        data,fin,fpin=finished_fixture();data[2]['finishing_application']['cleared_calculation_holds'].append(dict(kind='other-source-obligation',subject='local'))
        data=refresh_plan(data)
        with self.assertRaisesRegex(ValueError,'Only exact covered'):
            run_finished((data,fin,fpin))
        data,fin,fpin=finished_fixture();data[2]['pending_contracts'][0]['resolved']=True
        data=refresh_plan(data)
        with self.assertRaisesRegex(ValueError,'evidence must remain open'):
            run_finished((data,fin,fpin))

    def test_supplement_preserves_all_inputs(self):
        case=finished_fixture();before=deepcopy(case)
        r=run_finished(case);self.assertEqual(case,before)
        self.assertEqual(r,run_finished(case))

    def test_bounded_evaluation_revision_does_not_change_nominal_physical_identity(self):
        case=finished_fixture();original=run_finished(case)
        data,fin,pin=finished_fixture();model=fin['pending_draft_replacements'][0]['complete_material_rebuild']
        model['bounded_properties']['with_source_position_uncertainty']['first_moment_interval_kg_m']=[[-22.,22.]]*3
        e=next(e for e in data[2]['canonical_local_draft']['entities'] if e['id']=='finish-a')
        e['complete_material_rebuild']=deepcopy(model);e['bounded_properties']=deepcopy(model['bounded_properties'])
        revised=run_finished(refresh_finished(data,fin,pin))
        self.assertEqual(original['candidate_id'],revised['candidate_id'])
        self.assertNotEqual(original['evaluation_id'],revised['evaluation_id'])

    def test_unknown_material_grammar_and_conflicting_optional_source_commit_refused(self):
        data,fin,pin=finished_fixture();model=fin['pending_draft_replacements'][0]['complete_material_rebuild']
        model['minimum_material_graph']['kind']='unreviewed-filled-solid'
        e=next(e for e in data[2]['canonical_local_draft']['entities'] if e['id']=='finish-a')
        e['complete_material_rebuild']=deepcopy(model)
        with self.assertRaisesRegex(ValueError,'Unknown source geometry'):
            run_finished(refresh_finished(data,fin,pin))
        data,fin,pin=finished_fixture();fin['source_input_pin']['sources']['weld']['source_commit']='a'*40
        with self.assertRaisesRegex(ValueError,'source commits'):
            run_finished(refresh_finished(data,fin,pin))


if __name__ == '__main__':
    unittest.main()

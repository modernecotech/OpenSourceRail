"""Local transaction controls on invented material data; no retained producer."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

from engineering.railway_project import terminal_revision as m
_spec = importlib.util.spec_from_file_location('terminal_revision_invented_fixture', Path(__file__).with_name('test_terminal_revision.py'))
_fixture_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fixture_module)
fixture, refresh, run, H = (_fixture_module.fixture, _fixture_module.refresh,
                          _fixture_module.run, _fixture_module.H)


def seal(v):
    return m.seal({k:v for k,v in v.items() if k != 'evaluation_id'})


def properties():
    mass = [.0025, .00255]
    mode = dict(first_moment_interval_kg_m=[[-1e-5,1e-5]]*3,
                centroid_interval_m=[[-.005,.005]]*3,
                inertia_about_terminal_origin_interval_kg_m2=[[[1e-8,2e-8] if i==j else [-1e-9,1e-9] for j in range(3)] for i in range(3)],
                exact_point_CG_m=None, centroidal_tensor_kg_m2=None)
    return dict(mass_interval_kg=mass, net_volume_interval_m3=[x/2660. for x in mass],
                uniform_density_research_kg_m3=2660., source_position_uncertainty_m=[.001]*3,
                nominal_datum=deepcopy(mode), with_source_position_uncertainty=deepcopy(mode))


def inputs():
    t,w,h,p=fixture()
    for e in t['canonical_draft']['entities']:e['uncertainty_m']=[.001]*3
    local = run(refresh(t,w,h))
    E = {e['id']:e for e in local['canonical_local_draft']['entities']}
    G = {g['id']:g for g in local['canonical_local_draft']['stock_groups']}
    rows, owners, physical = [], [], []
    for k, req in enumerate(local['source_finishing_records']):
        eid, oid = req['source_entity_id'], req['paid_owner_id']
        old = E[eid]['source_material_before_finishing']; group = G[oid]['source_paid_group_before_finishing']
        model = dict(kind='hardpoint-stopped-thread' if k==0 else 'ring-through-ports',
                     complete_source_void_union=deepcopy(req['source_record']['source_complete_void_union']),
                     minimum_material_graph=dict(kind='invented-minimum-material',source_id=eid),
                     maximum_material_graph=dict(kind='invented-maximum-material',source_id=eid),
                     bounded_properties=properties())
        pose = dict(at_m=deepcopy(old['at_m']),rotation=deepcopy(old['rotation']))
        rows.append(dict(source_entity_id=eid,source_stock_owner_id=oid,frame=m.FRAME,material_id=old['material_id'],
                         source_entity_ancestry=deepcopy(old),source_entity_sha256=m.identity(old),
                         source_owner_sha256=m.identity(group),source_finishing_operation=deepcopy(req['source_record']),
                         source_pose=pose, complete_material_rebuild=model,transaction_applied=False,old_incremental_H_removal_is_not_debited=True))
        owners.append(dict(source_owner_id=oid,source_owner_ancestry=deepcopy(group),source_owner_sha256=m.identity(group),
                           source_occurrence_ids=[eid],paid_blank_group_count=1,new_stock_purchase_count=0,
                           paid_gross_mass_kg=deepcopy(group['gross_mass_kg']),source_direct_price_retained_once=deepcopy(group['direct_cost_usd']),
                           complete_rebuilt_net_mass_interval_kg=[.0025,.00255],rebuilt_scrap_mass_interval_kg=[.003-.00255,.003-.0025],
                           new_material_charge=False,source_price_credit=False,transaction_applied=False))
        physical.append(dict(id=eid,material_id=old['material_id'],source_pose=deepcopy(pose),
                             source_declared_finishing=deepcopy(req['physical_operation']),
                             nominal_source_geometry=dict(material_id=old['material_id'],geometry=deepcopy(old['exact_CSG_entity']['geometry']),holes=deepcopy(old['exact_CSG_entity']['holes']))))
    pd = dict(schema='osr-terminal-complete-finishing-material-physical/1',units='m',frame=m.FRAME,parents=physical)
    fin = dict(schema='osr-terminal-finishing-material-rebuild/1',source_local_epoch=deepcopy(local['source_local_epoch']),
               physical_definition=pd,component_geometry_id=m.identity(pd),pending_draft_replacements=rows,
               source_owner_conservation=owners,counts=dict(finishing_operations=2,material_occurrences=2,hardpoints=1,backing_rings=1,paid_owner_groups=2,new_stock_purchases=0),
               pending_contracts=['Invented bounded analysis; physical qualification open','Source finished price process split unknown'],
               source_transactions_applied=False,**m.FLAGS)
    for key in ('terminal','weld','hardware'):
        fin['source_'+key+'_evaluation_id']=local['ancestry'][key+'_evaluation_id']
    return local,seal(fin)


def apply(local,fin):
    pin=dict(schema='osr-terminal-local-finishing-input-pin/1',sources={k:dict(evaluation_id=v['evaluation_id'],raw_sha256=H('invented-'+k)) for k,v in [('local_plan',local),('finishing',fin)]})
    return m.apply_finishing(local,fin,input_pin=pin,request_id=H('apply-invented'))


class FinishingApplicationTests(unittest.TestCase):
    def test_complete_material_rebuild_replaces_unknown_properties_without_double_debit(self):
        l,f=inputs();before=deepcopy((l,f));r=apply(l,f)
        self.assertEqual((l,f),before)
        self.assertEqual(r['counts'],l['counts'])
        self.assertNotEqual(r['local_component_geometry_id'],l['local_component_geometry_id'])
        self.assertEqual(m.identity(r['physical_definition']),r['local_component_geometry_id'])
        self.assertEqual(r['physical_definition'],r['canonical_local_draft']['material_projection'])
        self.assertTrue(all(r[k] is False for k in m.FLAGS))
        self.assertFalse(r['source_transactions_applied'])
        self.assertIsNone(r['mass_properties']['aggregate_CG_m'])
        changed={x['source_entity_id'] for x in f['pending_draft_replacements']}
        old={e['id']:e for e in l['canonical_local_draft']['entities']}
        for e in r['canonical_local_draft']['entities']:
            if e['id'] in changed:
                self.assertEqual(e['bounded_properties']['mass_interval_kg'],[.0025,.00255])
                self.assertIsNone(e['mass_kg'])
                self.assertIsNone(e['center_of_gravity_m'])
            else:self.assertEqual(e,old[e['id']])

    def test_owners_prices_deployments_and_P1_retirements_are_once_only(self):
        l,f=inputs();r=apply(l,f)
        for key in ['P1_old_leaf_retirement_ledger_owned_once_by_terminal','inherited_P1_retirements','deployment_data_unapplied','lifecycle_allocations','replacement_ledger']:
            self.assertEqual(r[key],l[key])
        self.assertEqual(r['deployment_quantity_multiplier_applied'],1)
        groups={g['id']:g for g in r['canonical_local_draft']['stock_groups']}
        for x in f['source_owner_conservation']:
            g=groups[x['source_owner_id']]
            self.assertEqual(g['direct_cost_usd'],x['source_direct_price_retained_once'])
            self.assertEqual(g['gross_mass_kg'],x['paid_gross_mass_kg'])
            self.assertEqual(g['net_mass_interval_kg'],[.0025,.00255])
            self.assertIsNone(g['net_mass_kg'])
        for p in r['pricing']['rows']:
            if p['owner_id'].startswith('finishing-operation/'):
                self.assertFalse(p['additive_to_paid_source_owner'])
                self.assertEqual(p['possible_additional_cost_interval_USD'],[0.,.1])
                self.assertEqual(p['direct_cost_label_cases_USD'],dict(low=.1,base=.1,high=.1))
        self.assertEqual(r['finishing_application']['new_P1_retirements'],0)
        self.assertEqual(r['finishing_application']['new_stock_purchases'],0)

    def test_only_calculated_holds_cleared_source_and_physical_holds_preserved(self):
        l,f=inputs();r=apply(l,f)
        removed=r['finishing_application']['cleared_calculation_holds']
        self.assertEqual(len(removed),4)
        self.assertEqual({h['kind'] for h in removed},{'finishing-material-properties-pending','density-context-unresolved'})
        old=[h for h in l['pending_contracts'] if h['kind'] not in {'finishing-material-properties-pending','density-context-unresolved'}]
        self.assertEqual(r['pending_contracts'][:-1],old)
        self.assertFalse(r['pending_contracts'][-1]['resolved'])

    def test_twice_applied_material_bounds_refused(self):
        l,f=inputs();r=apply(l,f)
        with self.assertRaisesRegex(ValueError,'second application'):apply(r,f)

    def test_changed_evaluation_bounds_do_not_change_nominal_material_geometry(self):
        l,f=inputs();a=apply(l,f);f=deepcopy(f)
        f['pending_contracts'].append('Additional independent verification obligation')
        b=apply(l,seal(f));self.assertNotEqual(a['evaluation_id'],b['evaluation_id'])
        self.assertEqual(a['local_component_geometry_id'],b['local_component_geometry_id'])

    def test_outward_marginal_transpose_intervals_may_overlap_without_equal_endpoints(self):
        l,f=inputs();p=f['pending_draft_replacements'][0]['complete_material_rebuild']['bounded_properties']
        p['nominal_datum']['inertia_about_terminal_origin_interval_kg_m2'][0][1]=[-1.000000000000001e-9,1.000000000000001e-9]
        r=apply(l,seal(f));e=next(e for e in r['canonical_local_draft']['entities'] if e['id']=='legacy/P')
        self.assertEqual(e['bounded_properties'],p)

    def bad(self,mutate,which='finishing'):
        l,f=inputs();target=f if which=='finishing' else l;mutate(target)
        if which=='finishing':f=seal(target)
        else:l=seal(target)
        before=deepcopy((l,f))
        with self.assertRaises((ValueError,KeyError,TypeError)):apply(l,f)
        self.assertEqual((l,f),before)

    def test_invalid_and_mixed_material_contracts_refused(self):
        faults=[
            lambda f:f.update(source_terminal_evaluation_id=H('other-epoch')),
            lambda f:f.update(component_geometry_id=H('other-geometry')),
            lambda f:f['pending_draft_replacements'].append(deepcopy(f['pending_draft_replacements'][0])),
            lambda f:f['pending_draft_replacements'][0].update(source_stock_owner_id='wrong'),
            lambda f:f['pending_draft_replacements'][0].update(source_entity_sha256=H('wrong')),
            lambda f:f['pending_draft_replacements'][0].update(old_incremental_H_removal_is_not_debited=False),
            lambda f:f['pending_draft_replacements'][0]['source_finishing_operation'].update(unrecorded_void=True),
            lambda f:f['pending_draft_replacements'][0]['source_pose']['at_m'].__setitem__(0,10.),
            lambda f:f['pending_draft_replacements'][0]['complete_material_rebuild'].update(complete_source_void_union={}),
            lambda f:f['pending_draft_replacements'][0]['complete_material_rebuild']['bounded_properties'].update(mass_interval_kg=[.01,.02]),
            lambda f:f['pending_draft_replacements'][0]['complete_material_rebuild']['bounded_properties'].update(source_position_uncertainty_m=[0.,0.,0.]),
            lambda f:f['pending_draft_replacements'][0]['complete_material_rebuild']['bounded_properties']['nominal_datum'].update(exact_point_CG_m=[0.,0.,0.]),
            lambda f:f['pending_draft_replacements'][0]['complete_material_rebuild']['bounded_properties']['nominal_datum']['inertia_about_terminal_origin_interval_kg_m2'][0].__setitem__(1,[1.,2.]),
            lambda f:f['source_owner_conservation'][0].update(new_stock_purchase_count=True),
            lambda f:f['source_owner_conservation'][0].update(source_direct_price_retained_once=dict(low=0.,base=0.,high=0.)),
            lambda f:f['source_owner_conservation'][0].update(complete_rebuilt_net_mass_interval_kg=[.001,.002]),
            lambda f:f['source_owner_conservation'][0].update(source_occurrence_ids=[]),
            lambda f:f['source_owner_conservation'][0].update(source_price_credit=True),
            lambda f:f.update(physical_accepted=True),
            lambda f:f.update(counts=dict(f['counts'],new_stock_purchases=1)),
            lambda f:f.update(counts=dict(f['counts'],hardpoints=True)),
        ]
        for change in faults:
            with self.subTest(change=change):self.bad(change)

    def test_local_material_projection_or_unsupported_overlay_refused(self):
        for change in [lambda l:l.update(overlay_conflicts=[dict(source_entity_id='legacy/P')]),
                       lambda l:l['canonical_local_draft']['material_projection'].update(unbound_geometry=True),
                       lambda l:next(e for e in l['canonical_local_draft']['entities'] if e['id']=='legacy/P').update(at_m=[2.,0.,0.]),
                       lambda l:l.update(deployment_quantity_multiplier_applied=2)]:
            with self.subTest(change=change):self.bad(change,'local')


if __name__=='__main__':unittest.main()

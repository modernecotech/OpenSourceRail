import unittest
from copy import deepcopy
from math import prod
import importlib.util
from pathlib import Path
from engineering.design_search import design_grammar,system_body as b,grammar_shell as s


class SolidShellMethodTests(unittest.TestCase):
    def test_requires_full_positive_definite_orthotropic_law(self):
        with self.assertRaises(ValueError):s._law(dict(E_Pa=None,source_basis='density only'))
        law=dict(constitutive_kind='orthotropic',engineering_constants=[25e9,8e9,8e9,.25,.25,.25,4e9,3e9,3e9],source_basis='synthetic method fixture')
        self.assertIn('ENGINEERING CONSTANTS',s._law(law)[0])
        bad=deepcopy(law);bad['engineering_constants'][3]=4.
        with self.assertRaisesRegex(ValueError,'positive definite'):s._law(bad)

    def test_finite_face_connectivity_excludes_point_only_contact(self):
        def part(name,at):return dict(id=name,at_m=at,size_m=[1.,1.,1.],volume_m3=1.,material_id='a')
        _,_,face=s._mesh([part('a',[0,0,0]),part('b',[1,0,0])],2.)
        _,_,point=s._mesh([part('a',[0,0,0]),part('b',[1,1,1])],2.)
        self.assertEqual(face['finite_face_components'],1);self.assertEqual(point['finite_face_components'],2)
        with self.assertRaisesRegex(ValueError,'overlap'):s._mesh([part('a',[0,0,0]),part('b',[.5,0,0])],2.)

    def test_method_fixtures_have_analytical_targets_and_explicit_element_law(self):
        cases=s.benchmark_plan()['cases'];self.assertEqual(len(cases),4)
        for c in cases:
            self.assertIn('TYPE=C3D8I',c['raw']);self.assertNotIn('TYPE=C3D8R',c['raw'])
            self.assertEqual(c['definition']['finite_face_components'],1)
        bending=[c for c in cases if c['id'].startswith('bending')]
        self.assertAlmostEqual(bending[0]['definition']['expected_tip_m'],bending[1]['definition']['expected_tip_m'])
        for c in cases[2:]:self.assertGreater(c['definition']['expected_energy_J'],0)


class ConnectedBodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent=design_grammar.build(design_grammar.parameters());cls.frame=b.build(cls.parent);cls.skin=b.build(cls.parent,'aluminium_stressed_skin')

    def test_distinct_counted_children_validate_and_keep_equipment(self):
        for c in (self.frame,self.skin):
            design_grammar.validate(c);self.assertTrue(s.plan(c)['admitted']);self.assertIsNone(c['complete_installed_mass_kg']);self.assertFalse(c['physical_accepted'])
            self.assertEqual(c['physical']['apertures'],self.parent['physical']['apertures']);self.assertEqual(c['retained_equipment_accounts'],self.parent['retained_equipment_accounts'])
            self.assertAlmostEqual(c['known_structure_stock_kg'],sum(p['volume_m3']*c['materials'][p['material_id']]['density_kg_m3'] for p in c['parts']),places=7)
        self.assertNotEqual(self.frame['candidate_id'],self.skin['candidate_id'])
        self.assertTrue(any(p.get('structural_role')=='side-shear' for p in self.skin['parts']))
        self.assertFalse(any(p.get('structural_role')=='side-shear' for p in self.frame['parts']))

    def test_original_generated_body_is_held_not_given_isotropic_gfrp(self):
        p=s.plan(self.parent);self.assertFalse(p['admitted']);self.assertAlmostEqual(p['quantified_attachment_gaps']['upper_post_to_floor_m'],.05)
        self.assertIsNone(self.parent['materials']['gfrp_skin_research']['E_Pa'])

    def test_connected_frame_mesh_and_consistent_total_load(self):
        raw,d=s.deck(self.frame,mesh_m=1.7)
        self.assertEqual(d['finite_face_components'],1);self.assertEqual(len(d['support_patches']),4)
        total=sum(v[2] for v in d['loads_N'].values());self.assertAlmostEqual(total,-d['load_mass_kg']*9.80665,places=5)
        self.assertIn('TYPE=C3D8I',raw);self.assertNotIn('*EQUATION',raw)

    def test_actual_joint_stock_inventory_and_function_projection_integrate(self):
        # This sparse source worktree predates the coordinator-owned inventory
        # adapter; use its current read-only module if not present locally.
        import engineering.design_search as package
        main=Path('/home/hayder/Documents/OpenSourceRail')
        if importlib.util.find_spec('engineering.design_search.system_inventory') is None:package.__path__.append(str(main/'engineering/design_search'))
        from engineering.design_search import dfma,system_inventory,grammar_geometry,interface_graph
        for c in (self.frame,self.skin):
            ids={p['id'] for p in c['parts']};components={p['occurrence_id']:p for p in c['components']}
            self.assertTrue(c['joins'])
            for j in c['joins']:
                self.assertGreaterEqual(len(j['part_ids']),2);self.assertEqual(len(j['part_ids']),len(set(j['part_ids'])));self.assertFalse(set(j['part_ids'])-ids)
                self.assertIsNone(components[j['id']]['stock']['mass_kg'])
            manufacturing=dfma.evaluate(c,root=main);self.assertEqual(manufacturing['candidate_id'],c['candidate_id'])
            inventory=system_inventory.evaluate(c,bundle_id='1'*64,source_root=main,dfma_record=manufacturing)
            self.assertIsNone(inventory['complete_installed_mass_kg'])
            projection=interface_graph.assess(grammar_geometry.interface_projection(c));self.assertTrue(projection['declared_functions_preserved'])
            self.assertFalse(any(i['code']=='opening-keepout-intersection' for i in projection['issues']))
            self.assertNotEqual(projection['compatibility_status'],'fail')

    def test_ancillary_geometry_has_functions_and_does_not_enter_structural_mesh(self):
        c=self.frame;ancillary=[p for p in c['parts'] if p.get('structural_role')=='nonstructural-ancillary'];self.assertTrue(ancillary)
        self.assertTrue({'solar-mount','cable-route','drainage'}<={f for p in ancillary for f in p['functions']})
        primary=set(c['shell_model']['structural_part_ids']);self.assertFalse(primary&{p['id'] for p in ancillary})
        solids=[p for p in c['parts'] if p['id'] in primary]
        for a in ancillary:
            for p in solids:
                overlap=[min(a['at_m'][i]+a['size_m'][i],p['at_m'][i]+p['size_m'][i])-max(a['at_m'][i],p['at_m'][i]) for i in range(3)]
                self.assertFalse(all(v>1e-8 for v in overlap),(a['id'],p['id']))

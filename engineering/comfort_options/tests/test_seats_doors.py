"""Independent equation checks and strict source/mass accounting regressions."""
from copy import deepcopy
import math
from pathlib import Path
import tempfile
import unittest

from engineering.comfort_options import seats_doors as sd


class ComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[3]
        cls.records=sd.options(root=cls.root)
        cls.benches=[r for r in cls.records if r['component']=='bench']
        cls.doors=[r for r in cls.records if r['component']=='door']

    def test_fourteen_bounded_records_preserve_failures_and_add_passing_revisions(self):
        self.assertEqual((14,9,5),(len(self.records),len(self.benches),len(self.doors)))
        self.assertEqual(3,sum(r['necessary_screen']=='pass' for r in self.records))
        self.assertEqual(self.records,sd.options(root=self.root))
        self.assertEqual(14,len({r['component_id'] for r in self.records}))
        for record in self.records:
            self.assertTrue(sd.validate(record,root=self.root))

    def test_monolithic_pan_matches_closed_form_and_load_scaling(self):
        args=dict(width=.45,span=.48,face=.002,core=0.,load=1500.,young=20e9)
        r=sd.pan_fixture(**args)
        inertia=.45*.002**3/12
        self.assertAlmostEqual(inertia,r['face_I_m4'])
        self.assertAlmostEqual(5*1500*.48**3/(384*20e9*inertia),r['total_deflection_m'])
        twice=sd.pan_fixture(**dict(args,load=3000.))
        self.assertAlmostEqual(2*r['total_deflection_m'],twice['total_deflection_m'])
        self.assertAlmostEqual(2*r['face_stress_Pa'],twice['face_stress_Pa'])
        self.assertFalse(r['small_deflection_domain'])

    def test_rhs_and_two_rail_center_load_match_equilibrium_formula(self):
        r=sd.beam_fixture(width=.03,depth=.05,wall=.002,span=.94,total_load=3000.)
        inertia=(.03*.05**3-.026*.046**3)/12
        self.assertAlmostEqual(inertia,r['section']['I_m4'])
        self.assertAlmostEqual(1500*.94**3/(48*69e9*inertia),r['deflection_m'])
        self.assertAlmostEqual(1500*.94/(4*(inertia/.025)),r['stress_Pa'])
        with self.assertRaises(ValueError):
            sd.beam_fixture(width=.03,depth=.05,wall=.002,span=.94,total_load=-1.)

    def test_thin_panel_controls_fail_and_deeper_supports_gain_real_stiffness(self):
        thin=[r for r in self.benches if r['negative_control']]
        self.assertEqual(3,len(thin))
        self.assertTrue(all(r['necessary_screen']=='fail' for r in thin))
        self.assertTrue(all(r['numerical_validity']=='outside-linear-pan-domain' for r in thin))
        for i in (0,3,6):
            rows=self.benches[i:i+3]
            self.assertGreater(rows[0]['fixtures']['rails']['deflection_m'],rows[2]['fixtures']['rails']['deflection_m'])
            self.assertLess(rows[0]['counted_mass_kg'],rows[2]['counted_mass_kg'])
        passed=next(r for r in self.benches if r['necessary_screen']=='pass')
        self.assertEqual('GFRP0.8mm-H80-30mm',passed['physical_definition']['panel'])
        self.assertLessEqual(passed['fixtures']['total_vertical_deflection_m'],.005)
        self.assertTrue(all(passed['fixture_checks'].values()))

    def test_all_material_stock_sums_and_mass_basis_remain_explicit(self):
        for r in self.records:
            self.assertAlmostEqual(math.fsum(p['mass_kg'] for p in r['stock_parts']),r['counted_mass_kg'])
            self.assertTrue(r['mass_basis'])
            self.assertIsNone(r['installed_mass_kg'])
            self.assertFalse(r['applied_to_composed_vehicle'])
        sandwich=next(r for r in self.benches if 'H80-30mm' in r['name'])
        ids={p['id'] for p in sandwich['stock_parts']}
        self.assertTrue({'panel/GFRP-edge-closure','panel/bond','support/Al-RHS-legs',
                         'mount/M8-fastener-stock','mount/Al-footplates'}<=ids)

    def test_legacy_door_reference_reproduces_original_stock_before_common_fixings(self):
        from engineering.vehicle_optimisation.equipment import equipment_candidates
        old=next(r for r in equipment_candidates() if r['id'].startswith('aluminium-sandwich-ES2-reference/'))
        ref=self.doors[0]
        self.assertAlmostEqual(old['door']['physical_leaf_stock_mass_kg']/4,
                               ref['retained_reference_leaf_stock_per_door_kg'])
        extra=next(p['mass_kg'] for p in ref['stock_parts'] if p['id']=='door/M8-stock-fasteners')
        self.assertAlmostEqual(ref['retained_reference_leaf_stock_per_door_kg']+extra,ref['counted_mass_kg'])

    def test_lightened_door_stock_does_not_remove_operator_or_invent_qualified_stiffness(self):
        baseline=self.doors[0]
        for r in self.doors:
            self.assertEqual(41.,r['supplier_operator_reference_mass_kg'])
            self.assertAlmostEqual(r['counted_mass_kg']+41.,r['material_plus_operator_reference_kg'])
        for r in self.doors[:3]:
            self.assertEqual('fail',r['necessary_screen'])
            self.assertFalse(r['fixture_checks']['research_deflection'])
        for r in self.doors[1:3]:
            self.assertLess(r['counted_mass_kg'],baseline['counted_mass_kg'])
            self.assertGreater(r['physical_definition']['core_m'],baseline['physical_definition']['core_m'])
            self.assertLess(r['fixture']['total_deflection_m'],baseline['fixture']['total_deflection_m'])
            self.assertIn('track recess',' '.join(r['unknown']))

    def test_deeper_revisions_improve_same_load_fixture_with_counted_mass_penalty(self):
        parent=self.doors[2]
        for r,core in zip(self.doors[3:],(.060,.080)):
            self.assertEqual(2,r['design_iteration'])
            self.assertEqual(parent['component_id'],r['parent_component_id'])
            self.assertTrue(r['revision_rationale'])
            definition=r['physical_definition']; old=parent['physical_definition']
            for key in ('leaf_size_m','leaves','window_size_m','window_void_m2_each','skin_each_m',
                        'operator_reference_mass_kg','operator_reference_width_m','proposed_clear_width_m'):
                self.assertEqual(old[key],definition[key])
            self.assertEqual(core,definition['core_m'])
            self.assertEqual([.03,core,.0012],definition['edge_RHS_m'])
            self.assertEqual(1000.,r['fixture']['pressure_Pa'])
            self.assertEqual('pass',r['necessary_screen'])
            self.assertTrue(all(r['fixture_checks'].values()))
            self.assertLessEqual(r['fixture']['total_deflection_m'],.010)
            self.assertGreater(r['counted_mass_kg'],parent['counted_mass_kg'])
            self.assertGreater(r['leaf_depth_m'],r['retained_reference_leaf_depth_m'])
            self.assertIn('HVAC',' '.join(r['unknown']))
            self.assertFalse(r['applied_to_composed_vehicle'])
        self.assertLess(self.doors[4]['fixture']['total_deflection_m'],self.doors[3]['fixture']['total_deflection_m'])
        self.assertGreater(self.doors[4]['counted_mass_kg'],self.doors[3]['counted_mass_kg'])

    def test_room_temperature_properties_and_holds_are_not_vehicle_acceptance(self):
        for r in self.records:
            self.assertEqual(23.,r['fixture_temperature_C'])
            self.assertFalse(r['hot_weather_qualified'])
            self.assertEqual('hold',r['physical_acceptance'])
            self.assertTrue(all(r[key] is False for key in sd.FLAGS))
            self.assertTrue(r['unknown'])
            self.assertTrue(r['materials']['references'][0]['url'].startswith('https://diab-media.'))

    def test_forged_sources_masses_fixtures_and_acceptance_are_rejected(self):
        for key in ('counted_mass_kg','necessary_screen','physical_accepted','evaluation_id'):
            changed=deepcopy(self.records[0]);changed[key]='forged'
            with self.assertRaisesRegex(ValueError,'differs'):
                sd.validate(changed,root=self.root)
        changed=deepcopy(self.records[-1]);changed['fixture']['span_m']=.01
        with self.assertRaises(ValueError):
            sd.validate(changed,root=self.root)

    def test_changed_parent_sources_invalidate_previous_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in sd.SOURCE_FILES:
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes((self.root/name).read_bytes())
            path=root/sd.SOURCE_FILES[0];path.write_text(path.read_text()+'\n# changed source\n')
            with self.assertRaises(ValueError):
                sd.validate(self.records[0],root=root)


if __name__=='__main__':
    unittest.main()

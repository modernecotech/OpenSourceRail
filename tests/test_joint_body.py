import unittest
from pathlib import Path
from copy import deepcopy
import tempfile
from math import pi
from engineering.station_rail import vehicle
from engineering.station_rail.common import identity
from engineering.design_search import joint_body as j,wheel_body

ROOT=Path('/home/hayder/Documents/OpenSourceRail')


class FourBoltBodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=vehicle.build(ROOT);cls.p=j.default_parameters();cls.car=j.materialize_body(cls.base,cls.p,ROOT)

    def test_physical_four_bolt_identity_and_account(self):
        c=self.car
        self.assertNotEqual(c['body_candidate_id'],self.base['body_candidate_id'])
        self.assertEqual(c['body_candidate_id'],identity(c['body_physical_definition']))
        self.assertEqual(c['joint_body']['clamp_pads'],40)
        self.assertEqual(c['joint_body']['bolt_stacks'],160)
        self.assertEqual(c['joint_body']['transfer_rank_histogram'],{'6':40})
        delta=sum(q['mass_kg'] for q in c['geometry_parts'])-sum(q['mass_kg'] for q in self.base['geometry_parts'])
        self.assertAlmostEqual(delta,c['joint_body']['net_body_stock_delta_kg'])
        self.assertAlmostEqual(c['mass']['accounted_tare_kg_per_car']-self.base['mass']['accounted_tare_kg_per_car'],delta)
        self.assertIsNone(c['mass']['installed_tare_kg_per_car'])
        self.assertFalse(c['physical_accepted'])

    def test_hardware_participates_in_physical_definition(self):
        parts=self.car['body_physical_definition']['geometry_parts'];shanks=[p for p in parts if p['id'].startswith('wheel-shell-clamp/') and p['id'].endswith('/shank')]
        self.assertEqual(len(shanks),160)
        self.assertTrue(all(p['system']=='body-panel-connections' for p in shanks))
        self.assertTrue(all(len(p['bolt_axes'])==4 for p in self.car['wheel_body']['pads']))
        self.assertGreater(self.car['joint_body']['drilled_material_removed_kg'],0)

    def test_preserve_service_and_support_interfaces(self):
        c=self.car
        for group in ('vehicle','support','propulsion'):
            self.assertEqual(c['physical_definition'][group],self.base['physical_definition'][group])
        self.assertEqual(c['support_component_id'],self.base['support_component_id'])
        self.assertEqual(c['propulsion_component_id'],self.base['propulsion_component_id'])
        self.assertAlmostEqual(c['joint_body']['frame_floor_fit_stock_delta_kg'],77.15427156,places=6)

    def test_mutated_stock_rejected_before_mesh(self):
        c=deepcopy(self.car);c['geometry_parts'][0]['mass_kg']+=1
        with self.assertRaisesRegex(ValueError,'geometry differs'):j.body_deck(c,self.p)

    def test_four_bolt_native_input_contains_all_axes(self):
        raw,d=j.body_deck(self.car,self.p,dx=.6)
        self.assertEqual(d['ideal_fastener_equations'],40*4*3)
        self.assertIn('TYPE=C3D20,',raw)
        self.assertNotIn('TYPE=C3D20R',raw)
        self.assertIn('J_BODY_ALL',raw)
        self.assertEqual(d['body_candidate_id'],self.car['body_candidate_id'])

    def test_quality_requires_all_reactions_and_energy(self):
        good=dict(execution='completed',force_balance_relative_error=1e-8,force_balance_relative_error_all_axes=1e-8,moment_balance_relative_error_all_axes=1e-8,energy_relative_residual=1e-8)
        self.assertTrue(j._case_valid(good))
        for key in ('force_balance_relative_error_all_axes','moment_balance_relative_error_all_axes','energy_relative_residual'):
            self.assertFalse(j._case_valid({**good,key:.01}))
            self.assertFalse(j._case_valid({**good,key:None}))

    def test_provenance_guard_rejects_stale_helper(self):
        from engineering.station_rail.common import digest
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'helper.py';path.write_text('a=1\n');sources={'helper.py':digest(path)}
            j._verify_sources(sources,t)
            path.write_text('a=2\n')
            with self.assertRaisesRegex(ValueError,'Declared source differs'):j._verify_sources(sources,t)


class FiniteBackingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=vehicle.build(ROOT);cls.car=j.materialize_finite_body(cls.base,root=ROOT)

    def test_counted_insert_bond_cut_volume_and_mass(self):
        c=self.car;f=c['joint_body']['finite_backing'];patches=f['patches'];self.assertEqual(len(patches),40)
        added=[q for q in c['geometry_parts'] if q['id'].startswith(('wheel-shell-clamp/finite/','finite-body-bond/'))]
        expected=sum(k['contact_area_m2']*k['depth_m']-4*pi*.0045**2*k['depth_m'] for k in patches)
        self.assertAlmostEqual(sum(q['volume_m3'] for q in added),expected,places=10)
        point_delta=j.materialize_body(self.base,j.default_parameters(),ROOT)['joint_body']['net_body_stock_delta_kg']
        self.assertAlmostEqual(c['joint_body']['net_body_stock_delta_kg']-point_delta,f['added_stock_mass_kg']-f['removed_restored_panel_mass_kg']+f['restored_previous_panel_hole_mass_kg'],places=7)
        self.assertEqual(c['body_candidate_id'],identity(c['body_physical_definition']))
        self.assertNotEqual(c['body_candidate_id'],f['point_control_body_id'])

    def test_backing_material_does_not_overlap_retained_side_prisms(self):
        added=[q for q in self.car['geometry_parts'] if q['id'].startswith(('wheel-shell-clamp/finite/','finite-body-bond/'))]
        retained=[q for q in self.car['geometry_parts'] if q.get('role')=='panel-side' and q['id'].startswith('comfort-shell/')]
        for a in added:
            for b in retained:
                overlap=[min(a['at_m'][i]+a['size_m'][i],b['at_m'][i]+b['size_m'][i])-max(a['at_m'][i],b['at_m'][i]) for i in range(3)]
                self.assertFalse(all(x>1e-8 for x in overlap),(a['id'],b['id']))

    def test_finite_native_transfer_is_area_and_no_extra_global_support(self):
        raw,d=j.body_deck(self.car,j.finite_parameters(),dx=.6)
        self.assertTrue(d['no_additional_global_supports'])
        self.assertEqual(len(d['finite_area_transfer']),40)
        self.assertTrue(all(k['contact_nodes']>=8 and k['contact_area_m2']>0 for k in d['finite_area_transfer']))
        self.assertEqual(d['ideal_fastener_equations'],0)
        self.assertGreater(d['finite_area_equations'],40*4*3)
        self.assertIn('TYPE=C3D20,',raw)

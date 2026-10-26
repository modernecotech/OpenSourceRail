import unittest
from pathlib import Path
import tempfile
import numpy as np
from engineering.design_search import joint_models as j


class TransferFixtureTests(unittest.TestCase):
    def test_rank_and_virtual_work(self):
        for kind,rank in [('two_bolt_control',5),('four_bolt',6),('finite_area',6)]:
            r=j.rank_and_work_checks(j.joint_definition(kind))
            self.assertEqual(r['rank'],rank)
            self.assertLess(r['virtual_work_residual'],1e-14)

    def test_collinear_null_rotation_is_explicit(self):
        A=j._transfer_matrix(j.joint_definition('two_bolt_control')['transfer_points_m'])
        np.testing.assert_array_equal(A@np.array([0,0,0,1,0,0]),0)
        self.assertGreater(np.linalg.norm(j._transfer_matrix(j.joint_definition('four_bolt')['transfer_points_m'])[:,3]),0)

    def test_native_deck_six_loads_full_integration_dense_labels(self):
        raw,d=j.deck('four_bolt',2)
        self.assertEqual(raw.count('*CLOAD,OP=NEW'),6)
        self.assertEqual(raw.count('*FREQUENCY'),1)
        self.assertIn('TYPE=C3D20,',raw)
        self.assertNotIn('TYPE=C3D20R',raw)
        self.assertEqual(d['native_element_kind'],'C3D20')
        self.assertLess(d['solid_elements'],1000)
        self.assertEqual(d['rank_check']['rank'],6)

    def test_area_pads_count_stock_and_share_interface(self):
        raw,d=j.deck('finite_area',1)
        self.assertAlmostEqual(d['backing_stock_mass_kg'],4*.016*.002*.016*7850.)
        self.assertGreater(len(d['supported_nodes']),4)
        self.assertIn('ELSET=PAD',raw)
        self.assertFalse(d['physical_accepted'])

    def test_refinement_preserves_physical_identity(self):
        a=j.joint_definition('finite_area');b=j.joint_definition('finite_area')
        self.assertEqual(a,b)
        self.assertGreater(j.deck('finite_area',2)[1]['solid_elements'],j.deck('finite_area',1)[1]['solid_elements'])

    def test_modal_shapes_are_not_extra_static_cases(self):
        raw='displacements\n1 1.0 0.0 0.0\n E I G E N V A L U E   O U T P U T\n MODE NO EIGENVALUE FREQUENCY\n 1 4.0 2.0 .3183 0.0\n\ndisplacements\n1 99.0 0.0 0.0\n'
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'test.dat';p.write_text(raw);states,f=j._parse(p)
        self.assertEqual(len(states),1)
        self.assertEqual(f,[.3183])

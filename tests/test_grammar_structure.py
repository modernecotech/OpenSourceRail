from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
from engineering.design_search import grammar_structure as s


class AxialGraphTests(unittest.TestCase):
    def setUp(self):self.plan=s.benchmark_plan();self.axial=self.plan['native_jobs'][0]['graph'];self.tripod=self.plan['native_jobs'][2]['graph']

    def test_closed_form_axial_and_tripod(self):
        a=s.linear_reference(self.axial);t=s.linear_reference(self.tripod);checks=self.plan['analytical_checks']
        self.assertAlmostEqual(a['displacements_m']['tip'][0],checks['axial_tip_x_m'],places=12)
        self.assertAlmostEqual(a['reactions_N']['fixed'][0],-1200.,places=8)
        self.assertAlmostEqual(t['displacements_m']['3'][2],checks['tripod_tip_z_m'],places=12)
        self.assertAlmostEqual(t['strain_energy_J'],t['external_work_J'],places=12)

    def test_mechanism_detected_and_diagonal_restores_rank(self):
        g=deepcopy(self.plan['necessary_controls'][0]['graph']);d=s.diagnose_rigidity(g)
        self.assertEqual(d['mechanism_count'],1);self.assertGreater(d['load_projection_onto_mechanisms_N'],0)
        with self.assertRaisesRegex(ValueError,'mechanism'):s.deck(g)
        m=deepcopy(g['members'][0]);m.update(id='physical-diagonal',start_node='0',end_node='3');g['members'].append(m)
        self.assertEqual(s.diagnose_rigidity(g)['mechanism_count'],0)
        self.assertGreater(s.linear_reference(g)['displacements_m']['3'][0],0)

    def test_material_hypothesis_changes_evaluation_not_geometry_identity(self):
        g=deepcopy(self.axial);g['materials']['synthetic-al']['E_Pa']*=2
        a,b=s.diagnose_rigidity(self.axial),s.diagnose_rigidity(g)
        self.assertEqual(a['physical_graph_id'],b['physical_graph_id']);self.assertNotEqual(a['input_graph_id'],b['input_graph_id'])
        self.assertAlmostEqual(s.linear_reference(g)['displacements_m']['tip'][0]*2,s.linear_reference(self.axial)['displacements_m']['tip'][0])

    def test_counted_area_and_unknown_density_not_zero(self):
        g=deepcopy(self.axial);g['members'][0]['section']['area_m2']*=2
        with self.assertRaisesRegex(ValueError,'area differs'):s.deck(g)
        g=deepcopy(self.axial);g['materials']['synthetic-al']['density_kg_m3']=None;d=s.diagnose_rigidity(g)
        self.assertIsNone(d['counted_member_stock_mass_kg']);self.assertEqual(d['unknown_density_member_ids'],['bar'])
        self.assertIsNone(d['unknown_joint_hardware_mass_kg'])

    def test_native_axial_element_and_only_transverse_subdivision_constraints(self):
        raw,d=s.deck(self.tripod,subdivisions=2)
        self.assertEqual(d['elements'],6);self.assertEqual(d['transverse_interpolation_equations'],6)
        self.assertEqual(raw.count('TYPE=T3D2'),3);self.assertNotIn('TYPE=B31',raw)
        self.assertIn('axial displacement remains free',d['interpolation_scope'])
        self.assertEqual(d['graph_diagnostic']['member_count'],3)

    def test_subdivision_equations_leave_axial_motion_free(self):
        raw,d=s.deck(self.tripod,subdivisions=2);numbers=d['original_node_numbers'];U={n:np.arange(3,dtype=float)*.0001+n*.00003 for n in numbers.values()}
        for j,m in enumerate(self.tripod['members']):
            a,b=numbers[m['start_node']],numbers[m['end_node']];direction=np.array(d['nodes'][b])-d['nodes'][a];direction/=np.linalg.norm(direction)
            U[len(numbers)+j+1]=(U[a]+U[b])/2+direction*.0002
        lines=raw.splitlines()
        for i,line in enumerate(lines):
            if line!='*EQUATION':continue
            count=int(lines[i+1]);terms=[];j=i+2
            while len(terms)<3*count:
                values=lines[j].split(',');self.assertLessEqual(len(values),12);terms+=values;j+=1
            self.assertEqual(len(terms),3*count)
            residual=sum(float(terms[k+2])*U[int(terms[k])][int(terms[k+1])-1] for k in range(0,len(terms),3))
            self.assertAlmostEqual(residual,0.,places=13)

    def test_oblique_tripod_MPCs_wrap_all_six_terms(self):
        raw,_=s.deck(self.tripod,subdivisions=2);lines=raw.splitlines();oblique=0
        for i,line in enumerate(lines):
            if line=='*EQUATION' and lines[i+1]=='6':
                oblique+=1;self.assertEqual(len(lines[i+2].split(',')),12);self.assertEqual(len(lines[i+3].split(',')),6)
        self.assertGreater(oblique,0)

    def test_tool_error_packet_always_has_unknown_numerical_validity(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'failure'
            with patch.object(s.subprocess,'run',return_value=SimpleNamespace(returncode=201,stdout=b'input refused',stderr=b'')) as mocked:
                result=s.run(self.axial,out,root=s.ROOT)
            self.assertEqual(mocked.call_count,1);self.assertEqual(result['execution'],'tool_error');self.assertEqual(result['numerical_validity'],'unknown')
            self.assertTrue((out/'manifest.json').is_file());self.assertFalse(result['physical_accepted'])

    def test_loaded_support_RF_is_not_double_counted(self):
        _,d=s.deck(self.axial);r=s.linear_reference(self.axial);u=r['displacements_m']['tip'][0]
        raw=f'displacements\n1 0 0 0\n2 {u:.14g} 0 0\nforces\n1 -1000 0 0\n2 1000 0 0\ntotal internal energy\n{.5*1000*u:.14g}\n'
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'graph.dat';p.write_text(raw);result=s.analyse(self.axial,d,p)
        self.assertAlmostEqual(result['reactions_N']['fixed'][0],-1200.)
        np.testing.assert_allclose(result['force_residual_N'],0.,atol=1e-10)
        self.assertEqual(result['numerical_validity'],'verified_axial_method')

    def test_mixed_graph_or_unsupported_numeric_types_refused(self):
        g=deepcopy(self.axial);g['members'].append(deepcopy(g['members'][0]));g['members'][-1]['id']='duplicate'
        with self.assertRaisesRegex(ValueError,'Duplicate coincident'):s.diagnose_rigidity(g)
        for value in (True,1.,3):
            with self.assertRaises(ValueError):s.deck(self.axial,value)
        g=deepcopy(self.axial);g['supports'][0]['dofs']=[1.]
        with self.assertRaises(ValueError):s.diagnose_rigidity(g)

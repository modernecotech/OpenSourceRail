import copy
import unittest
from engineering.design_search.craft_backends import viaduct_fem as f

class ViaductFiniteElementTests(unittest.TestCase):
    def mesh(self):
        pts=[[0,0,0],[1,0,0],[0,1,0],[0,0,1]]
        pts += [[(pts[a][j]+pts[b][j])/2 for j in range(3)] for a,b in f.TET_EDGES]
        return dict(nodes={str(i+1):p for i,p in enumerate(pts)},elements={'1':list(range(1,11))})
    def test_independent_tetra_edge_mapping(self):
        m=self.mesh();self.assertTrue(f.validate_elements(m))
        shuffled=m['elements']['1'][:4]+list(reversed(m['elements']['1'][4:]))
        self.assertEqual(f.ccx_nodes(shuffled,m['nodes']),list(range(1,11)))
    def test_wrong_fieldcraft_edge_order_rejected(self):
        m=self.mesh();m['elements']['1'][-2:]=reversed(m['elements']['1'][-2:])
        with self.assertRaisesRegex(ValueError,'order'):f.validate_elements(m)
    def test_negative_jacobian_rejected(self):
        m=self.mesh();m['nodes']={n:[-p[0],p[1],p[2]] for n,p in m['nodes'].items()}
        with self.assertRaisesRegex(ValueError,'Jacobian'):f.validate_elements(m)
    def test_quadratic_patch_force_conserves_resultant_and_moment(self):
        m=dict(nodes={'1':[0,0,0],'2':[1,0,0],'3':[0,1,0],'4':[.5,0,0],'5':[.5,.5,0],'6':[0,.5,0]},top_faces=[[1,2,3,4,5,6]])
        forces=f.surface_forces(m,[0,.2,0,.2],80000)
        self.assertAlmostEqual(sum(forces.values()),-80000,places=7)
        self.assertAlmostEqual(sum(m['nodes'][str(n)][0]*v for n,v in forces.items()),-8000,places=7)
        self.assertAlmostEqual(sum(m['nodes'][str(n)][1]*v for n,v in forces.items()),-8000,places=7)
    def test_missing_cad_load_patch_rejected(self):
        m=dict(nodes={'1':[0,0,0],'2':[1,0,0],'3':[0,1,0],'4':[.5,0,0],'5':[.5,.5,0],'6':[0,.5,0]},top_faces=[[1,2,3,4,5,6]])
        with self.assertRaisesRegex(ValueError,'completely covered'):f.surface_forces(m,[0,1,0,1],1)
    def test_predeclared_numeric_screens_do_not_grant_strength(self):
        self.assertEqual(f.SCREENS['force_relative'],1e-5)
        self.assertNotIn('stress_allowable',f.SCREENS)
        self.assertTrue(all(v is False for v in f.FLAGS.values()))

if __name__=='__main__':unittest.main()

class ReactionsAndLoads(unittest.TestCase):
    def test_overlapping_bearing_anchor_nodes_are_deduplicated(self):
        self.assertEqual(f.constraint_nodes(dict(support_nodes=[[1,2],[3,4]],anchor_nodes=[1,3])),[1,2,3,4])
    def test_ccx_external_RF_subtracts_support_CLOAD(self):
        model=dict(nodes={'1':[0.,0.,0.]},support_nodes=[[1],[1]],anchor_nodes=[1,1],probe_nodes=[1],
          nodal_load_N={'1':[0.,0.,-2.]},applied_N=[0.,0.,-10.],applied_moment_Nm=[0.,0.,0.])
        text='displacements set TIP\n1 0 0 -1\nforces set ROOT\n1 0 0 8\nstresses\n1 1 1 0 0 0 0 0\n'
        r=f.parse_ccx(text,model)
        self.assertEqual(r['reaction_N'],[0.,0.,10.]);self.assertTrue(r['force_equilibrium_passed'])

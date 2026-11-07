import unittest
from engineering.design_search.craft_backends import viaduct_fem_resource as r

class ViaductResourceRevisionTests(unittest.TestCase):
    def test_resource_revision_does_not_change_physics(self):
        a=[dict(command='deck.read',params=dict(path='/old/mesh.inp',units='m-kg-s-N-Pa')),dict(command='file.save',params=dict(path='/old/checkpoint.fieldcraft')),dict(command='model.load.create',params=dict(vector=[0,0,-80]))]
        b=[dict(command='deck.read',params=dict(path='/new/mesh.inp',units='m-kg-s-N-Pa')),dict(command='file.open',params=dict(path='/new/checkpoint.fieldcraft')),dict(command='model.load.create',params=dict(vector=[0,0,-80]))]
        self.assertEqual(r.physics_commands(a),r.physics_commands(b))
        b[-1]['params']['vector']=[0,0,-81];self.assertNotEqual(r.physics_commands(a),r.physics_commands(b))
    def test_numerical_budget_does_not_relax_screens(self):
        v=lambda u:dict(displacement_m=[0,0,u])
        c=r.comparisons(v(-1),v(-1.1),v(-1.03))
        self.assertFalse(c['cross_solver_screen_passed']);self.assertFalse(c['displacement_refinement_screen_passed'])
    def test_other_resource_request_rejected_before_any_run(self):
        with self.assertRaisesRegex(ValueError,'3072'):r.revisionrun({},'/unused','/unused',memory_mb=4096)

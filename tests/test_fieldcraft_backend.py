"""Contract tests use synthetic readbacks; these fixtures are not native evidence."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    'osr_fieldcraft_backend',
    Path(__file__).resolve().parents[1] / 'engineering/design_search/craft_backends/fieldcraft.py')
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)


def readback(axial=False, nodes=None, displacement=None):
    step = 'Axial' if axial else 'Bend'
    point = [.3, 0, 0] if axial else [1., .05, .05]
    force = [1000., 0, 0] if axial else [0, 0, -1000.]
    reaction = [-v for v in force]
    moment = [0, 0, 0] if axial else [50., -1000., 0]
    root = 'Root' if axial else 'root'
    if displacement is None:
        displacement = [1000*.3/(70e9*1e-4), 0, 0] if axial else [0, 0, fc.cantilever_theory()]
    results = [
        dict(errors=0, ready=True),
        dict(step=step, units=dict(length='m', force='N', pressure='Pa'),
             reaction_total=reaction, warnings=[]),
        dict(step=step, units=dict(displacement='m', xyz='m'),
             nodes=[dict(xyz=point, displacement=displacement)]),
        dict(step=step, units=dict(force='N', length='m', moment='N·m'),
             stale=False, about=[0, 0, 0], applied=force,
             total=dict(force=reaction, moment=moment),
             sets=[dict(set=root, force=reaction, moment=moment)]),
        dict(display_units=fc.UNITS, own_units=True,
             nodes=nodes or (2 if axial else 261),
             elements={'rod2': 1} if axial else {'hex20': 32}, definitions=dict(sets=3))]
    return dict(ok=True, completed=len(results), results=results)


class FieldCraftRecipes(unittest.TestCase):
    def test_explicit_si_precedes_all_geometry(self):
        for commands in [fc.cantilever_commands(), fc.axial_commands()]:
            self.assertEqual(commands[0], dict(command='model.units', params=dict(system=fc.UNITS)))
            self.assertTrue(all(isinstance(c['params'], dict) for c in commands))
            self.assertEqual(commands[-5]['command'], 'model.check')
            self.assertEqual(commands[-1]['command'], 'model.info')
        self.assertEqual(len(fc.cantilever_commands()), 15)
        self.assertEqual(len(fc.axial_commands()), 19)

    def test_geometry_linked_support_and_load_preserved_during_remesh(self):
        commands = fc.cantilever_commands((8, 2, 2))
        mesh = commands[1]['params']
        self.assertEqual(mesh['kind'], 'hex20')
        self.assertEqual(mesh['divisions'], [8, 2, 2])
        self.assertEqual(mesh['corners'][-2], [1., .1, .1])
        self.assertEqual(mesh['faces'], {'6': 'root', '4': 'tip'})
        for row in commands[2:5]:
            self.assertIn('geometry', row['params'])
            self.assertNotIn('nodes', row['params'])
        remesh = fc.remesh_cantilever_commands((16, 4, 4))
        self.assertEqual(remesh[0], dict(command='mesh.clear', params=dict(bodies=['OSR-Elastic-Control'])))
        self.assertEqual(remesh[1]['params']['divisions'], [16, 4, 4])
        self.assertFalse(any('create' in row['command'] for row in remesh))

    def test_timoshenko_formula_and_predeclared_screen(self):
        self.assertAlmostEqual(fc.cantilever_theory(), -.0005748571428571429, places=16)
        self.assertEqual(fc.CANTILEVER['theory_relative_tolerance'], .02)
        self.assertEqual(fc.CANTILEVER['refinement_relative_tolerance'], .005)
        self.assertEqual(fc.cantilever_commands()[5]['params']['elastic']['poisson'], 0.)
        self.assertEqual(fc.cantilever_commands()[8]['params']['distribution'], 'total')
        self.assertEqual(fc.cantilever_commands()[8]['params']['vector'], [0, 0, -1000.])

    def test_mesh_resource_bounds(self):
        for value in [(0, 2, 2), (65, 2, 2), (16, 16, 16), (True, 2, 2), (8., 2, 2), (8, 2), '8,2,2']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                fc.cantilever_commands(value)

    def test_recipes_are_independent_mutable_results(self):
        first = fc.cantilever_commands()
        first[1]['params']['divisions'][0] = 60
        self.assertEqual(fc.cantilever_commands()[1]['params']['divisions'], [8, 2, 2])


class FieldCraftReadbacks(unittest.TestCase):
    def test_mcp_and_decoded_batch_parity(self):
        data = readback()
        raw = dict(jsonrpc='2.0', id=2, result=dict(content=[dict(type='text', text=json.dumps(data))]))
        expected = fc.parse_cantilever_result(data, 5)
        self.assertEqual(fc.parse_cantilever_result(json.dumps(raw), 5), expected)
        self.assertTrue(expected['numerical_screen_passed'])
        self.assertEqual(expected['reaction_moment_Nm'], [50., -1000., 0])
        self.assertTrue(all(expected[key] is False for key in fc.FLAGS))

    def test_axial_control(self):
        value = fc.parse_axial_result(readback(axial=True), 5)
        self.assertAlmostEqual(value['displacement_m'][0], 4.285714285714286e-5)
        self.assertEqual(value['reaction_N'], [-1000., 0, 0])
        self.assertTrue(value['numerical_screen_passed'])
        self.assertEqual(fc.axial_commands()[-3]['params']['at'], [[.3, 0, 0]])

    def test_partial_error_and_count_mismatch_are_rejected(self):
        for data in [dict(error='native failed'), dict(result=[]), dict(isError=True),
                     dict(ok=False, completed=0, results=[]),
                     dict(ok=True, completed=2, results=[]),
                     dict(ok=True, completed=0, results=[], failed=dict(index=0))]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                fc.batch_results(data)
        with self.assertRaises(ValueError):
            fc.parse_cantilever_result(readback(), 15)
        with self.assertRaises(ValueError):
            fc.parse_cantilever_result(dict(ok=True, completed=4, results=[{}]*4), 4)

    def test_units_stale_steps_geometry_loads_and_nonfinite_rejected(self):
        changes = [
            lambda r: r[4].update(display_units='mm-kg-s-N-MPa'),
            lambda r: r[4].update(own_units=False),
            lambda r: r[1]['units'].update(pressure='MPa'),
            lambda r: r[2]['units'].update(displacement='mm'),
            lambda r: r[3]['units'].update(moment='N·mm'),
            lambda r: r[3].update(stale=True),
            lambda r: r[2].update(step='OtherCandidate'),
            lambda r: r[2]['nodes'][0].update(xyz=[1000., 50., 50.]),
            lambda r: r[2]['nodes'][0].update(displacement=[0, 0, float('nan')]),
            lambda r: r[3].update(applied=[0, 0, -1e3+1]),
            lambda r: r[3].update(about=[1, 0, 0]),
            lambda r: r[3]['sets'][0].update(set='OtherRoot'),
            lambda r: r[4].update(elements={'hex8': 32}),
            lambda r: r[4].update(nodes=None),
        ]
        for change in changes:
            data = readback()
            change(data['results'])
            with self.subTest(change=change), self.assertRaises(ValueError):
                fc.parse_cantilever_result(data)

    def test_failed_engineering_screen_keeps_calculation_and_never_promotes(self):
        data = readback(displacement=[0, 0, 2*fc.cantilever_theory()])
        result = fc.parse_cantilever_result(data)
        self.assertFalse(result['numerical_screen_passed'])
        self.assertEqual(result['relative_theory_error'], 1.)
        self.assertTrue(all(result[key] is False for key in fc.FLAGS))

    def test_force_and_moment_unbalance_fail_screen(self):
        for field in ('force', 'moment'):
            data = readback()
            data['results'][3]['total'][field] = deepcopy(data['results'][3]['total'][field])
            data['results'][3]['total'][field][2] += 1
            data['results'][3]['sets'][0][field] = data['results'][3]['total'][field]
            if field == 'force':
                data['results'][1]['reaction_total'] = data['results'][3]['total'][field]
            self.assertFalse(fc.parse_cantilever_result(data)['numerical_screen_passed'])

    def test_independent_readback_disagreement_rejected(self):
        data = readback()
        data['results'][1]['reaction_total'] = [0, 0, 999.]
        with self.assertRaises(ValueError):
            fc.parse_cantilever_result(data)

    def test_refinement_requires_same_interfaces_and_more_nodes(self):
        coarse = fc.parse_cantilever_result(readback(displacement=[0, 0, -.0005744889092342115]))
        fine = fc.parse_cantilever_result(readback(nodes=1505, displacement=[0, 0, -.0005748094473424819]))
        result = fc.compare_refinement(coarse, fine)
        self.assertTrue(result['refinement_screen_passed'])
        self.assertFalse(result['mesh_independence_established'])
        self.assertAlmostEqual(result['relative_tip_change'], .0005576423800135621)
        for change in [dict(applied_N=[0, 0, -999.]), dict(nodes=200),
                       dict(probe_xyz_m=[1, 0, 0]), dict(physical_accepted=True)]:
            changed = dict(fine, **change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                fc.compare_refinement(coarse, changed)
        changed = dict(fine, displacement_m=[0, 0, -.001])
        self.assertFalse(fc.compare_refinement(coarse, changed)['refinement_screen_passed'])


if __name__ == '__main__':
    unittest.main()

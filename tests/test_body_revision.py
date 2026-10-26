import unittest
from pathlib import Path
from copy import deepcopy
from engineering.station_rail import vehicle
from engineering.station_rail.common import identity
from engineering.design_search import body_revision as b,joint_body,wheel_body

ROOT=Path('/home/hayder/Documents/OpenSourceRail')


class BodyRedistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=vehicle.build(ROOT);cls.rows=b.definitions(cls.base,ROOT);cls.cars=[b.materialize(cls.base,row,ROOT) for row in cls.rows]

    def test_three_physical_variants_and_continuous_model_domain(self):
        self.assertEqual([(r['parameters']['sill_depth_m'],r['parameters']['sill_wall_m']) for r in self.rows],[(.5,.006),(.6,.005),(.6,.008)])
        p={**self.rows[0]['parameters'],'sill_depth_m':.55,'sill_wall_m':.007}
        self.assertEqual(b._parameters(p),p)
        for key,value in [('sill_wall_m',.001),('sill_depth_m',2.),('material','honeycomb'),('sill_wall_m',True)]:
            with self.assertRaises(ValueError):b._parameters({**p,key:value})

    def test_exact_mass_ledger_actual_parameters_and_inertias(self):
        for row,car in zip(self.rows,self.cars):
            p=row['parameters'];ms=b._sills(car);self.assertEqual(len(ms),2)
            for m in ms:
                width,height,t=p['sill_width_m'],p['sill_depth_m'],p['sill_wall_m']
                area=width*height-(width-2*t)*(height-2*t);Iy=(width*height**3-(width-2*t)*(height-2*t)**3)/12
                self.assertAlmostEqual(m['area_m2'],area,places=10)
                self.assertAlmostEqual(m['I_about_local_1_m4'],Iy,places=10)
            delta=sum(q['mass_kg'] for q in car['geometry_parts'])-sum(q['mass_kg'] for q in self.base['geometry_parts'])
            self.assertAlmostEqual(delta,car['body_revision']['stock_mass_delta_kg'])
            self.assertAlmostEqual(delta,car['mass']['accounted_tare_kg_per_car']-self.base['mass']['accounted_tare_kg_per_car'])
            self.assertEqual(car['body_candidate_id'],identity(car['body_physical_definition']))
            self.assertEqual(car['joint_body']['parameters']['sill_wall_m'],p['sill_wall_m'])
            self.assertIsNone(car['mass']['installed_tare_kg_per_car']);self.assertFalse(car['physical_accepted'])

    def test_material_redistribution_is_lighter_and_geometrically_stiffer(self):
        for i in (0,1):
            metric=self.cars[i]['body_revision']['geometry_metrics'];self.assertLess(metric['sill_stock_delta_kg'],0);self.assertGreater(metric['vertical_I_ratio'],1);self.assertGreater(metric['vertical_I_per_mass_ratio'],1)
        self.assertGreater(self.cars[2]['body_revision']['sill_stock_delta_kg'],0)

    def test_unchanged_interfaces_payload_and_joint_geometry(self):
        for car in self.cars:
            for key in ('vehicle','support','propulsion'):self.assertEqual(car['physical_definition'][key],self.base['physical_definition'][key])
            self.assertEqual(len(car['joint_body']['finite_backing']['patches']),40)
            self.assertEqual(car['mass']['accounted_160_control_kg_per_car']-car['mass']['accounted_cap_loaded_kg_per_car'],8550.)
        self.assertEqual(len({c['body_candidate_id'] for c in self.cars}),3)

    def test_advisory_policy_is_not_physical_acceptance(self):
        for row in self.rows:
            self.assertEqual(row['advisory_policy']['status'],'advisory');self.assertEqual(row['selection_purpose'],'next_experiment');self.assertFalse(row['engineering_accepted'])
        p=b.plan(self.base,ROOT);self.assertEqual(p['maximum_native_jobs'],6);self.assertEqual(len(p['selected_definition_ids']),2)

    def test_reject_mixed_definition_or_revision_parent(self):
        altered=deepcopy(self.rows[0]);altered['parameters']['sill_wall_m']=.005
        with self.assertRaisesRegex(ValueError,'Mixed or mutated'):b.materialize(self.base,altered,ROOT)
        with self.assertRaisesRegex(ValueError,'unchanged'):b.definitions(self.cars[0],ROOT)

    def test_native_deck_uses_new_stock_and_finite_area_without_global_restraints(self):
        raw,m=b.deck(self.cars[1],self.rows[1],dx=.3)
        self.assertTrue(m['no_additional_global_supports']);self.assertEqual(len(m['finite_area_transfer']),40);self.assertGreater(m['finite_area_equations'],0)
        self.assertIn('TYPE=C3D20,',raw);self.assertNotIn('TYPE=C3D20R',raw)
        self.assertEqual(m['body_candidate_id'],self.cars[1]['body_candidate_id'])

    def test_geometry_mutation_rejected_before_native_mesh(self):
        car=deepcopy(self.cars[0]);car['geometry_parts'][0]['mass_kg']+=1
        with self.assertRaisesRegex(ValueError,'stock differs'):b.deck(car,self.rows[0])

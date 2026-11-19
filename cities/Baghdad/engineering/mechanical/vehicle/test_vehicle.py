"""Independent checks of the quotation geometry, load transfer and accounting."""
import csv
import io
import json
import unittest

from develop_vehicle import build, design, floor_tributaries


class VehicleStockTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        outputs = build()
        cls.result = json.loads(outputs["result.json"])
        cls.bom = list(csv.DictReader(io.StringIO(outputs["cut-list.csv"])))
        cls.mesh = outputs["braced-frame.obj"]

    def test_stock_and_mesh_component_counts(self):
        counts = sum(int(r["cuts_per_assembly"])*(2 if r["assembly"]=="bogie" else 1)
                     for r in self.bom)
        self.assertEqual(counts, self.mesh.count("\no "))
        self.assertEqual(counts, 128)
        mass = sum(float(r["mass_kg"])*(2 if r["assembly"]=="bogie" else 1) for r in self.bom)
        self.assertAlmostEqual(mass, self.result["braced_mesh_stock_mass_kg"], delta=0.01)

    def test_reaction_and_higher_case_linearity(self):
        r = self.result["cases"]
        for case in r.values():
            for variant in case["sidewall_cases"].values():
                supports = variant["sidewall_bolster_reactions_kn"]
                self.assertAlmostEqual(2*sum(supports.values()), case["applied_car_gravity_kn"],delta=0.002)
                self.assertLess(variant["load_residual_n"],0.0001)
        self.assertAlmostEqual(r["1.0"]["sidewall_cases"]["braced_revision"]["peak_nodal_vertical_mm"]*1.3,
                               r["1.3"]["sidewall_cases"]["braced_revision"]["peak_nodal_vertical_mm"],delta=0.001)

    def test_retains_unsuccessful_trials(self):
        case = self.result["cases"]["1.3"]
        self.assertTrue(case["sidewall_cases"]["unbraced_parent"]["nominal_yield_exceeded"])
        self.assertFalse(case["sidewall_cases"]["braced_revision"]["nominal_yield_exceeded"])
        self.assertTrue(case["local_members"]["superseded_floor_tie_trial"]["nominal_yield_exceeded"])
        self.assertFalse(case["local_members"]["floor_tie"]["nominal_yield_exceeded"])
        self.assertIsNone(self.result["complete_installed_mass_kg"])
        self.assertNotEqual(self.result["unbraced_parent_id"],self.result["braced_revision_id"])

    def test_independent_bolster_and_saddle_moments(self):
        case = self.result["cases"]["1.0"]
        force = case["applied_car_gravity_kn"]/4
        self.assertAlmostEqual(case["local_members"]["body_bolster"]["maximum_moment_knm"],force*(1.28-.85),delta=0.001)
        self.assertAlmostEqual(case["local_members"]["saddle"]["maximum_moment_knm"],force*.64/4,delta=0.001)

    def test_floor_strips_tile_body_and_clear_doors(self):
        stock, _, cfg, _, _, _, jambs, ends, _ = design()
        geom = cfg["vehicle_geometry"]
        trib = floor_tributaries(geom,jambs,ends)
        self.assertAlmostEqual(sum(trib.values()),geom["car_body_length_m"])
        self.assertEqual(len(jambs),8)
        for x1,x2 in zip(jambs[::2],jambs[1::2]):
            clear = x2-x1-stock["sections"]["jamb"][0]/1000
            self.assertAlmostEqual(clear,geom["door_clear_width_m"])

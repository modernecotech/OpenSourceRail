"""Physical stock, named-material and independent Halbach method controls."""
from copy import deepcopy
import math
import unittest

from engineering.vehicle_optimisation import magnets as m
from engineering.passive_suspension import fields


def select(name):
    return next(v for v in m.candidates() if v["sample_id"]==name)


class MagnetFamilies(unittest.TestCase):
    def test_named_primary_grades_minimum_typical_and_temperature(self):
        grades=m.material_sources()
        for key,br,hcj,beta in [("Arnold-N42SH",1.28,1592000.,-.0055),("Arnold-N35UH",1.17,1990000.,-.0051)]:
            g=grades[key]
            self.assertEqual(g["br_20c_t"],br)
            self.assertGreater(g["br_nominal_20c_t"],br)
            self.assertEqual(g["hcj_20c_a_m"],hcj)
            self.assertEqual(g["hcj_temperature_coefficient_per_k"],beta)
            self.assertEqual(g["density_kg_m3"],7600.)
            self.assertEqual(len(g["remote_pdf_sha256"]),64)
            self.assertIn("typical",g["density_basis"])
            self.assertIn("assumption",g["recoil_basis"])
            self.assertIsNone(g["supplier_quote"])
            self.assertIsNone(g["supplier_origin"])

    def test_twelve_bounded_geometries_and_32_checked_point_plan(self):
        values=m.candidates()
        self.assertEqual(len(values),12)
        self.assertEqual(len({v["physical_id"] for v in values}),12)
        self.assertEqual(len(m.reference_schedule(values)),32)
        self.assertEqual({x[1] for x in m.reference_schedule(values)},{.008,.012,.020})
        self.assertEqual({x[2] for x in m.reference_schedule(values)},{20.,80.})
        for v in values:
            m.validate(v)
            self.assertEqual(v["packing"]["modules_per_car"],24)
            self.assertGreater(v["packing"]["longitudinal_clearance_m"],0)

    def test_equal_volume_and_compact_variants_are_explicit(self):
        for v in m.candidates():
            expected=.006 if v["sample_id"] in ("N42-iron-compact","N42-H8-half-volume") else .012
            self.assertAlmostEqual(v["stock"]["magnet_volume_m3_per_module"],expected)
            grade=v["materials"][v["grade_id"]]
            self.assertAlmostEqual(v["stock"]["magnet_mass_kg_per_module"],expected*grade["density_kg_m3"])

    def test_ndfeb_stock_preserves_real_density_and_identity(self):
        v=select("N42-H8")
        native=m.native_definition(v)
        PM=[q for q in native["parts"] if q["material"]=="Arnold-N42SH"]
        self.assertEqual(len(PM),160)
        self.assertTrue(all(q["density_kg_m3"]==7600 for q in PM))
        self.assertTrue(all(q["size_m"][0]==.05 for q in PM))
        self.assertFalse(any(q["material"]=="ferrite" for q in native["parts"]))
        self.assertAlmostEqual(math.fsum(q["mass_kg"] for q in PM),91.2)
        for q in native["parts"]:
            self.assertAlmostEqual(q["volume_m3"],math.prod(q["size_m"]))
            self.assertAlmostEqual(q["mass_kg"],q["volume_m3"]*q["density_kg_m3"])

    def test_actual_complete_rotations_and_fourier_segmentation(self):
        for n in (4,8):
            directions=m.rotating_directions(n)
            self.assertEqual(len(directions),n)
            angles=[math.atan2(-q[0],q[1]) for q in directions]
            deltas=[(angles[(i+1)%n]-angles[i])%(2*math.pi) for i in range(n)]
            self.assertAlmostEqual(sum(deltas),2*math.pi)
            self.assertTrue(all(abs(d-2*math.pi/n)<1e-12 for d in deltas))
            self.assertTrue(all(abs(math.hypot(*q)-1)<1e-12 for q in directions))
        self.assertGreater(m.segmentation_factor(8),m.segmentation_factor(4))
        self.assertAlmostEqual(m.segmentation_factor(4),.9003163161571061)

    def test_generic_recoil_adapter_preserves_active_grade_and_no_extra_stock(self):
        v=select("N35-H8")
        g=m.field_geometry(v)
        self.assertEqual(g["recoil_adapter"]["active_chemistry"],"sintered-NdFeB")
        self.assertFalse(g["recoil_adapter"]["alias_creates_stock"])
        self.assertEqual(g["materials"]["ferrite"]["id"],"Arnold-N35UH")
        self.assertEqual(g["materials"]["Arnold-N35UH"]["hcj_20c_a_m"],1990000.)
        for r in g["regions"]:
            if r["group"]=="guideway":
                self.assertEqual(r["material"],"steel")
                self.assertEqual(r.get("J_x_A_m2",0),0)
                self.assertEqual(r.get("Br_z_T",0),0)
            if r["material"]=="Arnold-N35UH":
                self.assertAlmostEqual(math.hypot(r["Br_y_T"],r["Br_z_T"]),1.17)

    def test_exact_copper_and_steel_stock_is_counted(self):
        for v in m.candidates():
            train=[p for p in v["stock_parts"] if p["group"]=="train"]
            self.assertAlmostEqual(v["stock"]["train_known_mass_kg_per_car"],24*sum(p["mass_kg"] for p in train))
            self.assertGreater(v["stock"]["copper_mass_kg_per_module"],0)
            self.assertTrue(v["unknown_installed_inventory"])
            self.assertIsNone(v["installed_mass_kg_per_car"])
            self.assertFalse(v["physical_accepted"])
        self.assertGreater(select("N42-H8-yoke")["stock"]["steel_mass_kg_per_module"],select("N42-H8")["stock"]["steel_mass_kg_per_module"])

    def test_free_air_strong_side_and_independent_fundamental(self):
        v=select("N42-H8")
        g=m.field_geometry(v)
        g["regions"]=[r for r in g["regions"] if r["group"]=="train"]
        g["materials"][v["grade_id"]]["relative_permeability"]=1.
        t=v["parameters"]["pm_thickness_m"]
        points=[[0.,-.012+.025],[0.,-.012-t-.025]]
        samples=fields.sample_field(g,points,settings=dict(mesh_size_m=.006,outer_margin_m=.25))
        norms=[math.hypot(*b) for b in samples]
        self.assertGreater(norms[0]/norms[1],10.)
        exact=m.analytical_infinite_halbach_field_T(1.28,t,.32,.025,8)
        self.assertLess(abs(norms[0]/exact-1),.05)
        # Reversing rotation sends the strong side away from the facing.
        for r in g["regions"]:
            if r["material"]==v["grade_id"]:
                r["Br_y_T"]*=-1
        reverse=fields.sample_field(g,points,settings=dict(mesh_size_m=.006,outer_margin_m=.25))
        self.assertGreater(math.hypot(*reverse[1])/math.hypot(*reverse[0]),10.)

    def test_temperature_and_payload_digests_do_not_relabel_physical_grade(self):
        v=select("N42-H8")
        r=m.evaluate_reference(v,temperature_C=80.,settings=dict(mesh_size_m=.008,outer_margin_m=.15,check_convergence=False))
        self.assertEqual(r["physical_id"],v["physical_id"])
        raw=r["raw_result"]
        self.assertEqual(raw["declared_material_definitions"]["ferrite"]["id"],"Arnold-N42SH")
        self.assertAlmostEqual(raw["PM_recoil_knee_limit_A_per_m"],.8*1592000*(1-.0055*60))
        c=m.comparison(v,raw,aw3_mass_kg_per_car=30000.)
        self.assertAlmostEqual(c["required_1_3_aw3_N_per_module"],1.3*30000*9.80665/24)
        broken=deepcopy(raw);broken["F_z_N"]+=1
        with self.assertRaisesRegex(ValueError,"payload digest"):
            m.comparison(v,broken)
        with self.assertRaisesRegex(ValueError,"another physical geometry"):
            m.comparison(select("N35-H8"),raw)

    def test_replacement_mass_preserves_unknown_hardware(self):
        v=select("N42-H8")
        c=m.replacement_mass(v,base_empty_kg=25000.,removed_support_kg=10000.)
        self.assertAlmostEqual(c["material_subtotal_aw3_kg_per_car"],25000-10000+v["stock"]["train_known_mass_kg_per_car"]+12000)
        self.assertIsNone(c["installed_mass_kg_per_car"])
        self.assertEqual(c["unknown_installed_inventory"],v["unknown_installed_inventory"])

    def test_resigned_unsupported_changes_are_rejected_before_native_or_fields(self):
        for mutate in [lambda v:v["regions"][1]["bounds_yz_m"].__setitem__(0,-.2),
                       lambda v:v["stock_parts"][1].__setitem__("mass_kg",0.),
                       lambda v:v["materials"][v["grade_id"]].__setitem__("density_kg_m3",1.)]:
            v=select("N42-H8");mutate(v)
            v["physical_id"]=m.identity(m.physical_definition(v));v.pop("bundle_sha256")
            v["bundle_sha256"]=m.identity(v)
            with self.assertRaises(ValueError):m.field_geometry(v)
            with self.assertRaises(ValueError):m.native_definition(v)


if __name__=="__main__":
    unittest.main()

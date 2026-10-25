"""Independent analytical and numerical controls for the spatial field solve."""
from copy import deepcopy
import math
import unittest
from unittest.mock import patch

from engineering.passive_suspension import fields as f


def fixture():
    """Small actual PM/passive-facing plus closed-current copper-window unit."""
    return dict(length_x_m=.25, reference_gap_m=.03, regions=[
        dict(id="pm", material="ferrite", group="train", bounds_yz_m=[-.05,.05,-.09,-.03], Br_z_T=.45),
        dict(id="facing", material="steel", group="guideway", bounds_yz_m=[-.18,.18,0,.04]),
        dict(id="cw+", material="copper", group="train", bounds_yz_m=[-.08,-.06,-.08,-.04], turns_per_m2=100000., circuit_id="lift"),
        dict(id="cw-", material="copper", group="train", bounds_yz_m=[.06,.08,-.08,-.04], turns_per_m2=-100000., circuit_id="lift")],
        circuits={"lift": dict(resistance_20c_ohm=.2)})


SMALL = dict(mesh_size_m=.01, outer_margin_m=.15, check_convergence=True, max_solves=200)


class SpatialFields(unittest.TestCase):
    def test_exact_rectangular_pm_air_field_and_self_force(self):
        # Infinite-x, unit-recoil PM: exact field from two uniformly charged
        # horizontal surfaces, independent of this finite-element assembly.
        geometry = dict(length_x_m=1., materials={"ferrite": dict(relative_permeability=1., br_temperature_coefficient_per_k=0.)},
                        regions=[dict(id="pm", material="ferrite", group="train", bounds_yz_m=[-.1,.1,-.05,0.], Br_z_T=.45)])
        values = f.sample_field(geometry, [[0.,.05],[0.,.1]], settings=dict(mesh_size_m=.01, outer_margin_m=1.))
        for B, distance in zip(values, [.05,.1]):
            exact = .45/math.pi*(math.atan(.1/distance)-math.atan(.1/(distance+.05)))
            self.assertLess(abs(B[1]/exact-1), .025)
            self.assertLess(abs(B[0]), 1e-8)
        r = f.solve(geometry, settings=dict(mesh_size_m=.01, outer_margin_m=.3))
        self.assertLess(abs(r["F_z_N"]), 1e-6)
        self.assertLess(abs(r["F_y_N"]), 1e-6)
        self.assertFalse(r["physical_accepted"])
        self.assertIsNone(r["travel_drag_N"])

    def test_upward_attraction_symmetry_and_energy_force(self):
        geometry = fixture()
        cfg = dict(mesh_size_m=.004, outer_margin_m=.2)
        centre = f.solve(geometry, settings=cfg)
        minus = f.solve(geometry, gap_m=.029, settings=cfg)
        plus = f.solve(geometry, gap_m=.031, settings=cfg)
        force_energy = -(plus["coenergy_source_J"]-minus["coenergy_source_J"])/.002
        self.assertGreater(centre["F_z_N"], 0)
        self.assertLess(abs(centre["F_z_N"]/force_energy-1), .035)
        self.assertLess(abs(centre["F_y_N"]), 1e-6)
        self.assertLess(abs(centre["M_x_Nm"]), 1e-6)

    def test_mesh_boundary_and_air_contour_are_independent_holds(self):
        unchecked = f.solve(fixture(), settings=dict(mesh_size_m=.01, outer_margin_m=.15))
        self.assertEqual(unchecked["numerical_status"], "converged")
        self.assertFalse(unchecked["interpolation_usable"])
        checked = f.solve(fixture(), settings=SMALL)
        self.assertTrue(checked["interpolation_usable"])
        self.assertEqual(checked["diagnostics"]["validation_solves"], 3)
        self.assertTrue(checked["diagnostics"]["mesh_check"]["passed"])
        self.assertTrue(checked["diagnostics"]["boundary_check"]["passed"])
        self.assertTrue(checked["diagnostics"]["contour_check_pass"])

    def test_actual_map_reciprocity_inductance_and_temperature_resistance(self):
        result = f.field_map(fixture(), gaps_m=[.028,.032], laterals_m=[0.], currents_A=[-1.,1.], settings=SMALL)
        self.assertEqual(len(result["rows"]), 4)
        self.assertLessEqual(result["solves"], 200)
        self.assertEqual(result["unit_scope"], "per-module-extruded-length")
        self.assertEqual(result["control_circuit_id"], "lift")
        self.assertEqual(len(result["map_id"]), 64)
        for row in result["rows"]:
            self.assertGreater(row["L_H"], 0)
            self.assertLess(row["dF_z_dgap_N_per_m"], 0)
            self.assertLess(row["reciprocity_relative_residual"], .10)
            self.assertEqual(row["R_ohm"], .2)
            self.assertEqual(len(row["finite_difference_result_ids"]), 12)
            if not row["derivatives_validated"]:
                self.assertFalse(row["interpolation_usable"])
            self.assertFalse(result["physical_accepted"])
        warm = f.solve(fixture(), temperature_C=80., settings=dict(mesh_size_m=.01, outer_margin_m=.15))
        self.assertAlmostEqual(warm["coil_R_ohm"]["lift"], .2*(1+.00393*60))

    def test_explicit_series_connection_combines_flux_and_resistance(self):
        geometry = fixture()
        # Split each copper window into two stacked equal-area circuits; stock
        # geometry is disjoint, and each circuit still has its own return.
        original = geometry["regions"][2:]
        geometry["regions"] = geometry["regions"][:2]
        for row in original:
            for index, (lo, hi) in enumerate([(-.08,-.06),(-.06,-.04)]):
                item = deepcopy(row)
                item["id"] += str(index)
                item["circuit_id"] = "c"+str(index)
                item["bounds_yz_m"][2:] = [lo,hi]
                geometry["regions"].append(item)
        geometry["circuits"] = {"c0": dict(resistance_20c_ohm=.1), "c1": dict(resistance_20c_ohm=.15)}
        result = f.field_map(geometry, gaps_m=[.03], laterals_m=[0.], currents_A=[0.],
                             series_circuits={"c0":1,"c1":1}, circuit_id="series-lift",
                             settings=dict(mesh_size_m=.01, outer_margin_m=.15))
        row = result["rows"][0]
        point = next(r for r in result["solve_records"] if r["result_id"] == row["result_id"])
        self.assertAlmostEqual(row["flux_linkage_Wb_turn"], sum(point["flux_linkage_Wb_turn"].values()))
        self.assertAlmostEqual(row["R_ohm"], .25)
        self.assertEqual(result["series_circuits"], {"c0":1.,"c1":1.})
        self.assertFalse(result["interpolation_usable"])

    def test_length_scales_force_and_linkage_not_B(self):
        first = f.solve(fixture(), currents_A={"lift":2.}, settings=dict(mesh_size_m=.01, outer_margin_m=.15))
        geometry = fixture()
        geometry["length_x_m"] *= 2
        second = f.solve(geometry, currents_A={"lift":2.}, settings=dict(mesh_size_m=.01, outer_margin_m=.15))
        self.assertAlmostEqual(second["F_z_N"], 2*first["F_z_N"])
        self.assertAlmostEqual(second["flux_linkage_Wb_turn"]["lift"], 2*first["flux_linkage_Wb_turn"]["lift"])
        self.assertEqual(second["steel_B_peak_T"], first["steel_B_peak_T"])

    def test_known_failure_zero_remanence_and_zero_current_gives_zero_force(self):
        geometry = fixture()
        geometry["regions"][0]["Br_z_T"] = 0.
        result = f.solve(geometry, settings=dict(mesh_size_m=.01, outer_margin_m=.15))
        self.assertEqual(result["F_z_N"], 0.)
        self.assertEqual(result["F_y_N"], 0.)

    def test_no_pm_or_current_source_permitted_on_guideway(self):
        for key, value in (("J_x_A_m2", 1.), ("turns_per_m2", 1.)):
            geometry = fixture()
            geometry["regions"][1].update(material="copper", circuit_id="bad", **{key:value})
            with self.assertRaisesRegex(ValueError, "guideway must remain passive"):
                f.solve(geometry)
        geometry = fixture()
        geometry["regions"][1].update(material="ferrite", Br_z_T=.4)
        with self.assertRaisesRegex(ValueError, "guideway must remain passive"):
            f.solve(geometry)

    def test_unbalanced_current_return_is_refused(self):
        geometry = fixture()
        geometry["regions"].pop()
        with self.assertRaisesRegex(ValueError, "balanced forward/return"):
            f.solve(geometry)

    def test_contact_intersection_and_node_budget_are_refused(self):
        with self.assertRaisesRegex(ValueError, "bounding box|overlapping|air gap"):
            f.solve(fixture(), gap_m=0.)
        with self.assertRaisesRegex(ValueError, "node budget"):
            f.solve(fixture(), settings=dict(max_nodes=30))

    def test_nonlinear_nonconvergence_is_retained_not_passed(self):
        result = f.solve(fixture(), settings=dict(mesh_size_m=.01, outer_margin_m=.15,
                                                 steel_model="nonlinear_repo_proxy", nonlinear_max_iterations=1))
        self.assertEqual(result["numerical_status"], "nonconverged")
        self.assertFalse(result["interpolation_usable"])
        self.assertIsNone(result["coenergy_source_J"])
        self.assertIn("not a measured DC", result["material_proxy"]["steel"]["curve_basis"])

    def test_roll_transforms_geometry_but_retains_approximation_hold(self):
        result = f.solve(fixture(), roll_rad=.01, settings=dict(mesh_size_m=.006, outer_margin_m=.15))
        self.assertFalse(result["diagnostics"]["rectangle_conforming"])
        self.assertFalse(result["interpolation_usable"])

    def test_source_drift_during_solve_cannot_return_bound_result(self):
        original = f._single
        changed = False
        source = f.sources()
        def changing(*args, **kwargs):
            nonlocal changed
            result = original(*args, **kwargs)
            changed = True
            return result
        def snapshot():
            return source if not changed else {**source, "changed": "0"*64}
        with patch.object(f, "_single", changing), patch.object(f, "sources", snapshot):
            with self.assertRaisesRegex(ValueError, "sources changed"):
                f.solve(fixture(), settings=dict(mesh_size_m=.01, outer_margin_m=.15))

    def test_map_trial_budget_is_enforced_and_bad_connection_refused(self):
        with self.assertRaisesRegex(ValueError, "trial budget"):
            f.field_map(fixture(), gaps_m=[.03], laterals_m=[0.], currents_A=[0.], settings=dict(max_solves=2))
        with self.assertRaisesRegex(ValueError, "series_circuits"):
            f.field_map(fixture(), gaps_m=[.03], laterals_m=[0.], currents_A=[0.], series_circuits={"lift":2})

    def test_adjacent_segment_boundaries_do_not_create_sliver_overlaps(self):
        geometry = fixture()
        pm = geometry["regions"].pop(0)
        width = .1
        for i in range(3):
            a = -.05+i*width/3
            item = deepcopy(pm)
            item.update(id="segment"+str(i), bounds_yz_m=[a,a+width/3,-.09,-.03])
            geometry["regions"].append(item)
        result = f.solve(geometry, settings=dict(mesh_size_m=.005, outer_margin_m=.15))
        self.assertGreater(result["F_z_N"], 0.)
        self.assertLess(max(r["area_relative_error"] for r in result["region_diagnostics"].values()), 1e-8)

    def test_temperature_recoil_domain_and_unknown_material_law_are_holds(self):
        result = f.solve(fixture(), temperature_C=150., settings=dict(mesh_size_m=.01, outer_margin_m=.15))
        self.assertFalse(result["material_model_domain_pass"])
        self.assertFalse(result["interpolation_usable"])
        geometry = fixture()
        geometry["materials"] = {"steel": dict(h_a_m=[0,10], j_t=[0,2])}
        with self.assertRaisesRegex(ValueError, "unsupported alternate B-H"):
            f.solve(geometry, settings=dict(mesh_size_m=.01, outer_margin_m=.15))

    def test_point_convergence_cannot_override_unresolved_derivative(self):
        original = f.solve
        def point_with_unresolved_derivative(*args, **kwargs):
            result = original(*args, **kwargs)
            result["interpolation_usable"] = True
            if "validation_quantities" in result["diagnostics"]:
                # Artificially corrupt only coarse lateral-force derivative;
                # every individual point is still labelled converged.
                lateral = result["operating_point"]["lateral_m"]
                result["diagnostics"]["validation_quantities"]["coarse"]["F_y_N"] += lateral*1e8
            return result
        with patch.object(f, "solve", point_with_unresolved_derivative):
            result = f.field_map(fixture(), gaps_m=[.03], laterals_m=[0.], currents_A=[0.], settings=SMALL)
        row = result["rows"][0]
        self.assertEqual(row["numerical_status"], "converged")
        self.assertFalse(row["derivative_checks"]["dFy_dy_N_per_m"]["passed"])
        self.assertFalse(row["derivatives_validated"])
        self.assertFalse(result["interpolation_usable"])


if __name__ == "__main__":
    unittest.main()

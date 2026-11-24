import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from cities.Baghdad.engineering.simulation import airport_alignment, airport_demand, corridor, passengers, vehicle_audit as audit


class VehicleAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit.evaluate()

    def test_original_steel_bounds_and_axle_equilibrium(self):
        for state, loaded, axle in (("low", 165835.9582, 7018.55555),
                                    ("central", 198635.9582, 8707.487841666665),
                                    ("high", 246035.9582, 11213.737841666667)):
            case = self.result["mass_cases"][state]
            self.assertAlmostEqual(case["loaded_train_kg"], loaded)
            self.assertAlmostEqual(case["max_loaded_static_axle_kg"], axle)
            self.assertAlmostEqual(sum(a["loaded_kg"] for a in case["axles"].values()), loaded)
            self.assertAlmostEqual(sum(a["tare_kg"] for a in case["axles"].values()), case["tare_train_kg"])
            self.assertAlmostEqual(case["moment_balance_kg_m"], 0, places=8)
        self.assertTrue(all(row["installed_mass_kg"] is None for row in self.result["released_steel_bom"]))
        self.assertFalse(self.result["physical_accepted"])

    def test_independent_stop_high_load_exceeds_comparator(self):
        for state, expected_force, expected_stop in (("central", 14.3764, 379.9230),
                                                      ("high", 17.8070, 495.7459)):
            row = next(row for row in self.result["braking"][state] if row["downgrade_pct"] == 2
                       and row["coast_delay_s"] == 2 and row["wheel_adhesion_assumed"] == .08
                       and row["target_net_deceleration_m_s2"] == .6)
            rail = row["cases"]["none_wheel_brakes/1_rail_modules_out"]
            combined_fault = row["cases"]["one_out_wheel_brakes/1_rail_modules_out"]
            self.assertAlmostEqual(rail["required_force_per_available_module_kn"], expected_force, places=4)
            self.assertAlmostEqual(rail["stop_at_comparator"]["stop_distance_m"], expected_stop, places=4)
            self.assertAlmostEqual(rail["stop_at_target"]["stop_distance_m"], 386.9294, places=4)
            self.assertAlmostEqual(rail["stop_at_target"]["work_energy_residual_kwh"], 0, places=10)
            self.assertIsNone(rail["stop_wheel_only"]["stop_distance_m"])
            self.assertGreater(combined_fault["wheel_force_upper_bound_kn"], rail["wheel_force_upper_bound_kn"])
        self.assertIsNone(rail["target_stop_room_margin_m"])
        self.assertAlmostEqual(self.result["battery"]["end_of_life_margin_kwh"], -8.8)
        self.assertAlmostEqual(self.result["fit"]["doubled_loaded_distortion_margin_mm"], 2)
        self.assertLess(self.result["fit"]["passive_incremental_payload_cases"]["central"]["0.6"]
                        ["trial_40mm_stroke_margin_mm"], 0)
        high_traction = self.result["traction"]["high"]
        self.assertAlmostEqual(high_traction["min_driven_static_load_fraction"], .95705766)
        self.assertGreater(high_traction["layouts"][-2]["margin_kn"], 0)
        self.assertLess(high_traction["layouts"][-1]["margin_kn"], 0)
        self.assertEqual(high_traction["declared_physical_layout"], high_traction["layouts"][-2:])
        self.assertFalse(high_traction["declared_static_adhesion_necessary_screen_passes"])

    def test_route_grade_changes_duty_and_train_length_remains_centred(self):
        route = corridor.evaluate({"cars": 3, "grade_pct": -1})
        child = audit.evaluate(cars=3, route=route, available_stop_m=500, overlap_m=25)
        self.assertEqual(child["inputs"]["grade_pct"], 1)
        self.assertEqual(child["physical"]["car_centres_train_x_m"], [-17.5, 0.0, 17.5])
        self.assertEqual(child["physical"]["length_m"], 52)
        self.assertEqual(child["candidate_id"], audit.evaluate(cars=3)["candidate_id"])
        self.assertNotEqual(child["duty_id"], audit.evaluate(cars=3)["duty_id"])
        row = child["braking"]["central"][-1]["cases"]["none_wheel_brakes/1_rail_modules_out"]
        self.assertAlmostEqual(row["target_stop_room_margin_m"], 475 - row["stop_at_target"]["stop_distance_m"])
        with self.assertRaisesRegex(ValueError, "different candidates"):
            audit.evaluate(cars=6, route=route)
        with self.assertRaisesRegex(ValueError, "different candidates"):
            audit.evaluate(cars=3, route=route, grade_pct=2)

    def test_hot_end_of_life_battery_capacity_is_a_sensitivity_not_a_rating(self):
        battery = self.result["battery"]
        hot = battery["hot_end_of_life"]
        self.assertIsNone(hot["capacity_factor_measured"])
        self.assertIsNone(hot["deliverable_energy_kwh"])
        self.assertAlmostEqual(hot["minimum_capacity_factor_required"], 50.4 / 41.6)
        self.assertFalse(hot["energy_possible_with_capacity_factor_at_most_one"])
        for row in hot["sensitivity"]:
            factor = row["assumed_hot_capacity_factor"]
            self.assertAlmostEqual(row["usable_kwh"], 41.6 * factor)
            self.assertAlmostEqual(row["energy_margin_kwh"], 41.6 * factor - 50.4)
            self.assertAlmostEqual(row["minimum_nominal_kwh"], 50.4 / (.8 * .8 * factor))
        self.assertIsNone(battery["required_hot_discharge_peak_kw"])

    def test_corrective_envelopes_preserve_failed_obligations(self):
        battery = self.result["battery"]["corrective_procurement"]
        self.assertAlmostEqual(battery["minimum_hot_end_of_life_deliverable_kwh"], 50.4)
        self.assertAlmostEqual(battery["minimum_nominal_kwh_by_hot_capacity_factor"]["0.9"], 87.5)
        self.assertEqual(battery["baseline_installed_mass_allowance_kg"], 500)
        self.assertIsNone(battery["required_combined_hot_discharge_peak_kw"])
        self.assertIsNone(battery["changed_installed_mass_kg"])
        high = self.result["traction"]["high"]
        quote = high["corrective_procurement"]
        self.assertFalse(high["declared_static_adhesion_necessary_screen_passes"])
        self.assertAlmostEqual(quote["maximum_lost_driven_axle_static_kg"], 10565.35980535284)
        self.assertAlmostEqual(quote["minimum_reaction_transfer_from_each_heaviest_axle_kg"], 648.3780363138267)
        self.assertAlmostEqual(quote["minimum_reaction_transfer_per_car_kg"], 2 * quote["minimum_reaction_transfer_from_each_heaviest_axle_kg"])
        self.assertAlmostEqual(quote["required_adhesion_if_loads_unchanged"], .10027611443045059)
        self.assertAlmostEqual(quote["minimum_hot_wheel_force_after_one_axle_out_kn"], high["required_train_force_kn"])
        self.assertIsNone(quote["changed_installed_mass_kg"])

    def test_identified_battery_alternative_substitutes_mass_and_keeps_commercial_out_of_physical_id(self):
        alternative = dict(basis_kind="planning-estimate", supplier_reference="synthetic-study",
                           quote_source_sha256="a" * 64, nominal_kwh=100.0, usable_fraction=.8,
                           retained_capacity_fraction=.8, hot_capacity_factor=.8,
                           installed_mass_kg=800.0, installed_price_usd=180000.0,
                           car_x_m=0.0, car_z_m=.85, hot_continuous_discharge_kw=30.0,
                           hot_peak_discharge_kw=100.0, peak_duration_s=30.0)
        revised = audit.evaluate(battery_alternative=alternative)
        self.assertNotEqual(revised["candidate_id"], self.result["candidate_id"])
        self.assertAlmostEqual(revised["mass_cases"]["high"]["loaded_train_kg"],
                               self.result["mass_cases"]["high"]["loaded_train_kg"] + 300)
        self.assertAlmostEqual(revised["mass_cases"]["high"]["group_allocations"]["independent_service_pack"]["car_from_centroid_m"][0], 0)
        self.assertAlmostEqual(sum(a["loaded_kg"] for a in revised["mass_cases"]["high"]["axles"].values()),
                               revised["mass_cases"]["high"]["loaded_train_kg"])
        self.assertTrue(revised["battery"]["alternative"]["hot_energy_necessary_screen_passes"])
        self.assertIsNone(revised["battery"]["alternative"]["brake_and_egress_peak_power_screen_passes"])
        self.assertEqual(revised["battery"]["alternative"]["price_delta_usd"], 80000)
        shifted = audit.evaluate(battery_alternative={**alternative, "car_x_m": 1.0, "car_z_m": 1.85})
        for state, load in revised["mass_cases"].items():
            shifted_load = shifted["mass_cases"][state]
            expected_shift = alternative["installed_mass_kg"] / load["loaded_train_kg"]
            for axis in ("x", "z"):
                key = f"loaded_car_cg_{axis}_m"
                self.assertAlmostEqual(shifted_load[key] - load[key], expected_shift)
            self.assertGreater(shifted_load["axle_kg_per_car"][-1], load["axle_kg_per_car"][-1])
            self.assertAlmostEqual(sum(shifted_load["axle_kg_per_car"]), sum(load["axle_kg_per_car"]))
        repriced = audit.evaluate(battery_alternative={**alternative, "installed_price_usd": 200000})
        self.assertEqual(repriced["candidate_id"], revised["candidate_id"])
        self.assertNotEqual(repriced["evaluation_id"], revised["evaluation_id"])
        rehypothesized = audit.evaluate(battery_alternative={**alternative, "hot_capacity_factor": .7})
        self.assertEqual(rehypothesized["candidate_id"], revised["candidate_id"])
        self.assertFalse(rehypothesized["battery"]["alternative"]["hot_energy_necessary_screen_passes"])
        with self.assertRaisesRegex(ValueError, "source document"):
            audit.evaluate(battery_alternative={**alternative, "basis_kind": "supplier-quote"})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "quote.txt"
            path.write_text("synthetic quote fixture")
            documented = {**alternative, "basis_kind": "supplier-quote", "source_document": str(path),
                          "quote_source_sha256": audit.sha(path.read_bytes())}
            self.assertTrue(audit.evaluate(battery_alternative=documented)["battery"]["alternative"]["source_document_verified"])
            path.write_text("changed")
            with self.assertRaisesRegex(ValueError, "missing or changed"):
                audit.evaluate(battery_alternative=documented)

    def test_saloon_layout_counts_only_nonoverlapping_allocations_and_retains_high_crowd(self):
        folder = Path(audit.__file__).parent
        layout = json.loads((folder / "saloon-trial.json").read_text())
        trial = audit.evaluate(saloon_layout=layout, saloon_directory=folder)
        saloon = trial["saloon_layout"]
        self.assertEqual((saloon["seats_per_car"], saloon["wheelchair_places_per_car"],
                          saloon["standing_places_per_car"], saloon["places_per_train"]), (20, 2, 4, 156))
        self.assertGreaterEqual(saloon["unallocated_area_m2"], 0)
        self.assertEqual(trial["mass_cases"]["central"]["people"], 156)
        self.assertEqual(trial["mass_cases"]["high"]["people"], 700)
        self.assertEqual(trial["mass_cases"]["high"]["passenger_centroid_x_m"], 1.8)
        self.assertNotEqual(trial["candidate_id"], self.result["candidate_id"])
        lower_density = audit.evaluate(saloon_layout={**layout, "standing_density_person_m2": 2},
                                       saloon_directory=folder)
        self.assertEqual(lower_density["candidate_id"], trial["candidate_id"])
        self.assertNotEqual(lower_density["duty_id"], trial["duty_id"])
        overlap = deepcopy(layout)
        overlap["allocations"][-1]["y1_m"] = -.3
        with self.assertRaisesRegex(ValueError, "overlap"):
            audit.evaluate(saloon_layout=overlap, saloon_directory=folder)
        false_places = deepcopy(layout)
        false_places["allocations"][-1]["places"] = 700
        with self.assertRaisesRegex(ValueError, "Only seat and wheelchair"):
            audit.evaluate(saloon_layout=false_places, saloon_directory=folder)
        impossible_seats = deepcopy(layout)
        seat = next(row for row in impossible_seats["allocations"] if row["kind"] == "seat" and row["places"] == 4)
        seat["footprint_length_m"] = 3.0
        with self.assertRaisesRegex(ValueError, "whole footprint packing"):
            audit.evaluate(saloon_layout=impossible_seats, saloon_directory=folder)
        isolated = deepcopy(layout)
        isolated["allocations"] = [row for row in isolated["allocations"]
                                   if not (row["kind"] == "aisle" and row["x0_m"] == -5.65)]
        wheelchair = next(row for row in isolated["allocations"] if row["kind"] == "wheelchair" and row["x0_m"] == -5.65)
        wheelchair["x0_m"] = -5.5
        wheelchair["footprint_length_m"] = 1.8
        isolated["wheelchair_area_m2_per_place"] = 1.3
        with self.assertRaisesRegex(ValueError, "isolated"):
            audit.evaluate(saloon_layout=isolated, saloon_directory=folder)
        alignment = airport_alignment.evaluate()
        demand = airport_demand.evaluate(alignment, headway_min=30, normal_places_per_train=156)
        self.assertEqual(demand["service_offer"]["observation_context"]["normal_places_per_train"], 156)
        climate = passengers.evaluate(dict(cars=6, normal_places_per_train=156,
                                           busiest_departure_load=156, platform_queue=100))
        self.assertLessEqual(climate["door_exchange"]["arriving_load"], 156)
        with self.assertRaisesRegex(ValueError, "study domain"):
            passengers.evaluate(dict(cars=6, normal_places_per_train=156, busiest_departure_load=700))

    def test_claim_checks_identity_and_attachment_only(self):
        form = deepcopy(self.result["return_template"])
        form["kind"] = "synthetic-fixture"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.txt"
            path.write_text("synthetic test fixture")
            form["documents"][path.name] = dict(sha256=audit.sha(path.read_bytes()), issuer="Fixture", date="2026-11-24")
            form["returns"]["braking"] = dict(document=path.name, article_serial="FIXTURE", procedure_revision="TEST",
                                              witness="Synthetic fixture")
            result = audit.evaluate(evidence_return=form, evidence_directory=path.parent)["return_assessment"]
            self.assertEqual(result["claim"], "synthetic-fixture")
            self.assertFalse(result["physical_accepted"])
            with self.assertRaisesRegex(ValueError, "exact vehicle and duty"):
                audit.evaluate(cars=3, evidence_return=form, evidence_directory=path.parent)
            path.write_text("changed fixture")
            with self.assertRaisesRegex(ValueError, "Missing or changed"):
                audit.evaluate(evidence_return=form, evidence_directory=path.parent)
        json.dumps(self.result, allow_nan=False)

    def test_route_protection_return_checks_exact_alignment_record(self):
        alignment = airport_alignment.evaluate()
        aligned = audit.evaluate(alignment=alignment)
        self.assertEqual(aligned["candidate_id"], self.result["candidate_id"])
        self.assertNotEqual(aligned["duty_id"], self.result["duty_id"])
        self.assertEqual(aligned["inputs"]["alignment_id"], alignment["alignment_id"])
        form = deepcopy(aligned["return_template"])
        form["kind"] = "synthetic-fixture"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.txt"
            path.write_text("synthetic protection record")
            form["documents"][path.name] = dict(sha256=audit.sha(path.read_bytes()), issuer="Fixture", date="2026-11-24")
            form["returns"]["route_protection"] = dict(document=path.name, article_serial="FIXTURE",
                                                       procedure_revision="TEST", witness="Synthetic fixture")
            options = dict(evidence_return=form, evidence_directory=path.parent)
            attached = audit.evaluate(alignment=alignment, **options)
            self.assertEqual(attached["braking"], aligned["braking"])
            self.assertFalse(attached["return_assessment"]["physical_accepted"])
            revised = deepcopy(alignment)
            revised["review_gaps"].append("Synthetic later survey review")
            with self.assertRaisesRegex(ValueError, "alignment ID"):
                audit.evaluate(alignment=revised)
            revised["record_id"] = airport_alignment.identity({k: v for k, v in revised.items() if k != "record_id"})
            with self.assertRaisesRegex(ValueError, "exact vehicle and duty"):
                audit.evaluate(alignment=revised, **options)
            form["basis"] = self.result["basis"]
            with self.assertRaisesRegex(ValueError, "evaluated alignment"):
                audit.evaluate(**options)
        revised["parent_candidate_id"] = "unrelated"
        revised["alignment_id"] = airport_alignment.identity(airport_alignment.physical_record(revised))
        revised["record_id"] = airport_alignment.identity({k: v for k, v in revised.items() if k != "record_id"})
        with self.assertRaisesRegex(ValueError, "different Airport candidates"):
            audit.evaluate(alignment=revised)


if __name__ == "__main__":
    unittest.main()

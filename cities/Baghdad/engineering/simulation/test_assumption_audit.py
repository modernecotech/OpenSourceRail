"""Bounded integration checks for the corrected Airport decision and supplier intake."""

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from cities.Baghdad.engineering.mechanical.civil import family_comparison
from cities.Baghdad.engineering.simulation import (
    airport_alignment, airport_demand, assumption_audit as audit, audit_offers, audit_production, audit_register,
    motion_power, scenario, vehicle_audit,
)


class AssumptionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = airport_alignment.evaluate()
        cls.vehicle = vehicle_audit.evaluate()
        cls.demand, cls.climate = audit.service_inputs(cls.route, cls.vehicle, 30, 40, None, "service_sensitive")
        cls.civil = family_comparison.evaluate_high_load(cls.route["route_km"])

    @staticmethod
    def short_day(request):
        """Controlled evaluator result exercises binding and cash without rerunning the DC solve."""
        case = motion_power.normalize(request)
        route = request["alignment"]
        layout = case["topology"]
        km = route["route_km"]
        feeder = dict(name=layout, paths=2 if layout == "paired6" else 1, sites=case["chainages_m"],
                      droop=.01, outward=.03, return_path=.006, trunk_factor=1.)
        physical = dict(upstream_candidate_id=request["candidate_id"], alignment_id=route["alignment_id"], feeder=feeder)
        candidate = scenario._id(physical)
        year_days = 365
        return dict(
            physical=physical, candidate_id=candidate, evaluation_id=scenario._id({"physical": physical, "case": case}),
            source_publication_candidate_id=route["parent_candidate_id"], source_feeder_design_id=None,
            scenario={key: value for key, value in case.items() if key not in ("hourly_od", "od_matrix")},
            demand_basis={"od_id": scenario._id(case["hourly_od"])},
            booked_annual_train_km=(km+.5)*year_days, annual_train_km=(km+.5)*year_days,
            energy_kwh_per_train_km=120/(km+.5), electrical_enquiry={},
            failure=({"traction": {"mode": "heaviest_driven_axle_out",
                                   "vehicle_candidate_id": case["traction_fault"]["vehicle_candidate_id"],
                                   "vehicle_evaluation_id": case["traction_fault"]["vehicle_evaluation_id"],
                                   "load_state": case["traction_fault"]["load_state"],
                                   "low_adhesion_mu": case["traction_fault"]["low_adhesion_mu"],
                                   "adhesion_force_margin": case["traction_fault"]["adhesion_force_margin"],
                                   "controller": case.get("traction_fault_controller")}}
                     if "traction_fault" in case else {}),
            metrics=dict(booked_passenger_trips=1, completed_passenger_trips=1, booked_positioning_trips=0,
                         completed_positioning_trips=0, booked_yard_trips=2, completed_yard_trips=2,
                         booked_passenger_km=km, booked_positioning_km=0., booked_yard_km=.5,
                         fleet_sets_required=7, distance_km=km+.5, source_kwh=120.,
                         minimum_collector_v=1490., peak_site_current_ka=.7, bound_branch_rms_current_ka=.4,
                         max_site_rms_current_ka=.5, maximum_arrival_delay_s=20, boarded_passengers=10.,
                         **({"traction_fault_required_force_deficit_s": 0., "traction_fault_curtailed_s": 0.,
                             "traction_fault_limit_min_n": 100000.} if "traction_fault" in case else {})),
            gates=dict(all_workings_complete=True, dc_numerical_screen=True, motion_work_balance_screen=True,
                       utility_connection_approved=False, protection_approved=False, thermal_ratings_verified=False,
                       **({"traction_fault_force_envelope": True} if "traction_fault" in case else {})),
        )

    def working_day(self, cache=None, sources=None):
        return audit.working_day(self.route, self.demand, self.vehicle, self.climate, "paired6", "normal", 0,
                                 cache, sources or {"solver-test": "revision-a"}, phase=1306)

    def test_observed_od_uses_booked_dwell_and_cannot_rebook_a_short_sample(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "observed.json"
            for dwell in (35, 66):
                forecast = airport_demand.evaluate(self.route, headway_min=30, dwell_s=dwell)
                path.write_text(json.dumps(dict(
                    schema=airport_demand.OBSERVED_SCHEMA, alignment_id=self.route["alignment_id"],
                    stop_ids=forecast["stop_ids"], timezone="Asia/Baghdad", document="Test survey",
                    sample_date_from="2026-06-01", sample_date_to="2026-06-01", observed_days=1,
                    service_offer=forecast["service_offer"]["observation_context"], resolution="hourly",
                    od=[{"from": forecast["stop_ids"][0], "to": forecast["stop_ids"][-1],
                         "all": 1200, "paying": 1000, "hour": 9}],
                )))
                if dwell == 35:
                    with self.assertRaisesRegex(ValueError, "books 35 s dwell.*requires at least 66 s"):
                        audit.service_inputs(self.route, self.vehicle, 30, 40, path, "service_sensitive")
                else:
                    with self.assertRaisesRegex(ValueError, "must match the booked service"):
                        audit.service_inputs(self.route, self.vehicle, 30, 40, path, "service_sensitive")
                    demand, climate = audit.service_inputs(self.route, self.vehicle, 30, 40, path,
                                                           "service_sensitive", dwell_s=66)
                    self.assertEqual(demand["mode"], "observed")
                    self.assertEqual(demand["dwell_s"], 66)
                    self.assertEqual(demand["annual_all_journeys"], 1200 * 365)
                    self.assertEqual(climate["door_exchange"]["planned_dwell_s"], 66)

    def test_working_day_reuses_bound_cache_and_refuses_mixed_candidates(self):
        with TemporaryDirectory() as cache, patch.object(motion_power, "evaluate", side_effect=self.short_day) as solver:
            initial = self.working_day(cache)
            self.assertEqual(initial, self.working_day(cache))
            self.assertEqual(solver.call_count, 1)
            self.working_day(cache, {"solver-test": "revision-b"})
            self.assertEqual(solver.call_count, 2)
            self.assertEqual(initial["physical"]["upstream_candidate_id"], self.vehicle["candidate_id"])
            self.assertEqual(initial["scenario"]["demand_evaluation_id"], self.demand["evaluation_id"])
            self.assertEqual(initial["physical"]["feeder"]["sites"][-1], self.route["route_km"]*1000)
            self.assertIn(audit_production.MOTION_RECORD_ID, initial)
            stale = deepcopy(initial)
            stale["physical"]["alignment_id"] = "other"
            with patch.object(scenario, "stage", return_value=stale):
                with self.assertRaisesRegex(ValueError, "differ from the requested railway"):
                    self.working_day(cache)

    def test_register_preserves_unknowns_and_refuses_unclassified_inputs(self):
        with patch.object(motion_power, "evaluate", side_effect=self.short_day):
            config = self.working_day()["scenario"]
        args = self.route, self.demand, self.vehicle, self.civil, self.climate
        rows = {row["id"]: row for row in audit_register.register(*args, [config], {})}
        self.assertEqual(rows["route.posted_speed_limits"]["value_type"], "unknown")
        self.assertTrue(any(row["policy_class"] == "mandatory_obligation" for row in rows.values()))
        self.assertEqual(rows["route.vertical_profile"]["evidence_maturity"], "unknown")
        self.assertEqual(rows["civil.crane_limit_t"]["evidence_maturity"], "unknown")
        self.assertEqual(rows["motion.paired6.step_s"]["policy_class"], "numerical_validity_domain")
        self.assertEqual(rows["motion.paired6.positioning_slack_s"]["unit"], "s")
        with self.assertRaisesRegex(ValueError, "Unclassified normalized motion"):
            audit_register.register(*args, [dict(config, unexplained_solver_input=1)], {})
        demand = deepcopy(self.demand)
        demand["generalised_cost"]["unexplained_response"] = 1
        with self.assertRaisesRegex(ValueError, "Classify the changed generalised-cost"):
            audit_register.register(self.route, demand, self.vehicle, self.civil, self.climate, [config], {})

    def test_vehicle_screen_reports_known_failure_without_credit_for_missing_proof(self):
        stock = audit_register.vehicle_screens(self.vehicle)
        self.assertEqual(stock["aged_battery_energy"], "fail")
        self.assertEqual(stock["protected_stop_distance"], "unknown")
        constrained = vehicle_audit.evaluate(available_stop_m=350, overlap_m=30)
        screen = audit_register.vehicle_screens(constrained)
        self.assertEqual(screen["protected_stop_distance"], "fail")
        self.assertAlmostEqual(screen["protected_stop_margin_m"], 320 - screen["brake_trial_stop_m"])
        for trial in constrained["braking"]["high"]:
            case = trial["cases"]["none_wheel_brakes/1_rail_modules_out"]
            case["stop_at_comparator"]["stop_distance_m"] = None
            case["comparator_stop_room_margin_m"] = None
        self.assertEqual(audit_register.vehicle_screens(constrained)["protected_stop_distance"], "fail")

    def test_replacement_pack_displaces_fleet_allowance_and_moves_the_civil_axles(self):
        path = audit.HERE / "battery-trial.json"
        with patch.object(motion_power, "evaluate", side_effect=self.short_day):
            revised = audit.audit(battery_alternative=path, span=20, cache=None)
        train = revised["vehicle"]
        self.assertNotEqual(train["candidate_id"], self.vehicle["candidate_id"])
        self.assertEqual(revised["civil_quotation"]["installed_vehicle_candidate_id"], train["candidate_id"])
        for state, load in revised["civil"]["load_cases"].items():
            self.assertEqual(load["loaded_train_kg"], train["mass_cases"][state]["loaded_train_kg"])
            self.assertEqual(load["axle_kg_per_car"], train["mass_cases"][state]["axle_kg_per_car"])
            self.assertAlmostEqual(load["loaded_train_kg"] - self.vehicle["mass_cases"][state]["loaded_train_kg"], 300)
        price = revised["production"]["paired6"]
        rows = {row["lot_id"]: row for row in price["pricings"]}
        count = price["quantities"]["sets"]
        self.assertEqual(rows["essential-service-battery"]["usd"]["base"], count * 160000)
        self.assertAlmostEqual(rows["fleet"]["excluded_scope"]["archived_allowance_usd"]["base"], count * 100000)
        self.assertEqual(price["inputs"]["vehicle_candidate_id"], train["candidate_id"])
        screens = revised["decision"]["candidates"]["paired6"]["vehicle_screens"]
        self.assertEqual(screens["aged_battery_energy"], "pass")
        self.assertEqual(screens["battery_brake_and_egress_peak"], "unknown")
        self.assertIsNone(revised["decision"]["investment_selection"])

    def test_disposition_requires_all_duties_one_physical_candidate_and_prices(self):
        gates = dict(protection_approved=False, thermal_ratings_verified=False, utility_connection_approved=False,
                     all_workings_complete=True)
        days = [dict(condition=condition, topology=layout, candidate_id=layout, numerical_valid=True,
                     failed_screens=[key for key, value in gates.items() if not value], gates=gates.copy())
                for layout in audit.LAYOUTS for condition in motion_power.CONDITIONS]
        result = audit_register.disposition(self.route, self.demand, self.vehicle, days, None, {})
        self.assertEqual(result["passing_operational_days"], len(days))
        self.assertEqual(result["candidates"]["paired6"]["operating_screen"], "passed")
        self.assertEqual(result["candidates"]["paired6"]["scope_cost_status"], "partial or unpriced")
        self.assertEqual([row["task"] for row in result["completion_tests"]],
                         [f"A{index:02d}" for index in range(1, 11)])
        self.assertFalse(result["physical_acceptance"])
        self.assertIsNone(result["investment_selection"])
        with self.assertRaisesRegex(ValueError, "comparisons are incomplete"):
            audit_register.disposition(self.route, self.demand, self.vehicle, days[:-1], None, {})
        with self.assertRaisesRegex(ValueError, "duplicated duty"):
            audit_register.disposition(self.route, self.demand, self.vehicle, days + [days[0]], None, {})
        mismatched = deepcopy(days)
        mismatched[-1]["candidate_id"] = "revised physical feeder"
        half = len(days) // 2
        interleaved = [row for pair in zip(days[:half], days[half:], strict=True) for row in pair]
        self.assertEqual(result, audit_register.disposition(self.route, self.demand, self.vehicle, interleaved, None, {}))
        mixed_interleaved = [row for pair in zip(mismatched[:half], mismatched[half:], strict=True) for row in pair]
        with self.assertRaisesRegex(ValueError, "different physical candidates"):
            audit_register.disposition(self.route, self.demand, self.vehicle, mixed_interleaved, None, {})
        days[-1]["gates"]["all_workings_complete"] = False
        with self.assertRaisesRegex(ValueError, "failures differ from the case gates"):
            audit_register.disposition(self.route, self.demand, self.vehicle, interleaved, None, {})
        days[-1]["failed_screens"].append("all_workings_complete")
        failed = audit_register.disposition(self.route, self.demand, self.vehicle, interleaved, None, {})
        self.assertEqual(failed["candidates"][days[-1]["topology"]]["operating_screen"], "failed")

    def test_audit_offer_entry_point_retains_bids_and_high_load_holds(self):
        phase = dict(phase_s=300, conflicts=0, positioning_slack_s=0)
        with (patch.object(motion_power, "evaluate", side_effect=self.short_day),
              patch.object(audit, "phase_options", return_value=dict(as_booked=phase, best=phase)),
              patch.object(audit, "positioning_trial", return_value=phase),
              TemporaryDirectory() as directory):
            base = audit.audit(cache=Path(directory) / "cache")
            heavy = base["civil"]["load_cases"]["high"]["loaded_train_kg"]
            self.assertAlmostEqual(heavy, self.vehicle["mass_cases"]["high"]["loaded_train_kg"])
            self.assertGreater(heavy, base["civil"]["load_cases"]["central"]["loaded_train_kg"])
            self.assertTrue(base["civil_quotation"]["quotation_screen_passed"])
            combined = base["decision"]["candidates"]["paired6"]["functional_screen"]
            self.assertEqual(combined["status"], "failed")
            self.assertIn("aged battery", combined["failed"])
            self.assertIn("traction adhesion", combined["failed"])
            self.assertTrue(base["vehicle"]["traction"]["high"]["declared_static_adhesion_necessary_screen_passes"])
            self.assertIn("protected stopping distance", combined["unknown"])
            model = base["production"]["paired6"]
            self.assertIsNone(model["complete_installed_price_usd"])
            rows = {row["lot_id"]: row for row in model["pricings"]}
            self.assertIsNone(rows["revised-feeder-package"]["usd"])
            scope = rows["fleet"]["scope_id"]
            first = dict(offer_id="low-quote", supplier="Supplier A", scope_id=scope,
                         price_usd=rows["fleet"]["usd"]["base"]*.95, buyer_review_reference="evaluation A",
                         offer_sha256="a"*64, claimed_domestic_value_usd=None)
            second = dict(first, offer_id="selected-quote", supplier="Supplier B", buyer_review_reference="evaluation B",
                          offer_sha256="b"*64, price_usd=rows["fleet"]["usd"]["base"]*1.02)
            file = Path(directory) / "offers.json"
            file.write_text(json.dumps({"schema": audit_offers.SCHEMA, "layouts": {"paired6": {
                "offers": [first, second], "awards": [{
                    "scope_id": scope, "offer_id": second["offer_id"], "buyer_award_reference": "ERP purchase decision",
                }],
            }}}))
            awarded = audit.audit(offers=file, cache=Path(directory) / "cache")
            compared = awarded["supplier_comparisons"]["paired6"]
            self.assertEqual([row["status"] for row in compared], ["eligible", "awarded"])
            self.assertEqual(awarded["supplier_comparisons"]["radial30"], [])
            self.assertGreater(compared[1]["difference_vs_lowest_offer_usd"], 0)
            after = awarded["production"]["paired6"]
            paid = next(row for row in after["pricings"] if row["lot_id"] == "fleet")
            self.assertEqual(paid["usd"]["base"], second["price_usd"])
            self.assertEqual(after["feeder_scope"], model["feeder_scope"])
            self.assertIsNone(awarded["decision"]["investment_selection"])
            scope = after["inputs"]
            feeder_id = next(row["feeder_physical_id"] for row in awarded["power_days"] if row["topology"] == "paired6")
            risk_line = dict(risk_id="access-delay", description="Illustrative access delay",
                             evidence_basis="Test buyer estimate", cost_exclusions=["feeder supply"],
                             period="opening-direct", operating_year=None, range_usd=dict(low=10, base=20, high=30),
                             cash_treatment="exposure-only", substitutes_unpriced_lot_id=None,
                             historical_contingency_overlap_usd=None, overlap_basis=None)
            risk = dict(candidate_id=scope["vehicle_candidate_id"], alignment_id=scope["alignment_id"],
                        feeder_physical_id=feeder_id, civil_row_id=scope["civil_row_id"],
                        cash_basis_id=after["cash"]["owner_risk_sensitivity"]["cash_basis_id"],
                        currency="constant 2026 USD", basis_date="2026-11-24", calibration="uncalibrated",
                        lines=[risk_line])
            risk_file = Path(directory) / "owner-risk.json"
            risk_file.write_text(json.dumps(dict(schema="baghdad-airport-owner-risk/1", layouts={"paired6": risk})))
            review = audit.audit(offers=file, risk_return=risk_file, cache=Path(directory) / "cache")
            registered = [r for r in review["assumptions"] if r["id"] == "risk.paired6.access-delay"]
            self.assertEqual(len(registered), 1)
            self.assertEqual(review["production"]["paired6"]["cash"]["profiles"], after["cash"]["profiles"])
            self.assertFalse(review["production"]["radial30"]["cash"]["owner_risk_sensitivity"]["lines"])
            with self.assertRaisesRegex(ValueError, "cash basis|nominal cash"):
                audit.audit(risk_return=risk_file, cache=Path(directory) / "cache")

    def test_optional_fault_controller_is_separate_unapproved_comparison(self):
        phase = dict(phase_s=300, conflicts=0, positioning_slack_s=0)
        with (patch.object(motion_power, "evaluate", side_effect=self.short_day),
              patch.object(audit, "phase_options", return_value=dict(as_booked=phase, best=phase)),
              patch.object(audit, "positioning_trial", return_value=phase)):
            ordinary = audit.audit(cache=None)
            alternative = audit.audit(cache=None, fault_controller_sensitivity=True)
        self.assertNotIn("traction_fault_controller_sensitivity", ordinary)
        study = alternative["traction_fault_controller_sensitivity"]
        self.assertIsNone(study["degraded_service_requirement"])
        self.assertEqual(study["controller"], "reserve_limited")
        self.assertEqual(len(study["days"]), len(audit.LAYOUTS))
        default_fault = {row["topology"]: row for row in alternative["traction_fault_days"]}
        for row in study["days"]:
            self.assertEqual(row["candidate_id"], default_fault[row["topology"]]["candidate_id"])
            self.assertNotEqual(row["evaluation_id"], default_fault[row["topology"]]["evaluation_id"])
            self.assertEqual(row["failure"]["traction"]["controller"], "reserve_limited")


if __name__ == "__main__":
    unittest.main()

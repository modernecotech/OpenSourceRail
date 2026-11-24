"""Bounded integration checks for the corrected Airport decision and supplier intake."""

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from cities.Baghdad.engineering.mechanical.civil import family_comparison
from cities.Baghdad.engineering.simulation import (
    airport_alignment, assumption_audit as audit, audit_offers, audit_production, audit_register,
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
            energy_kwh_per_train_km=120/(km+.5), electrical_enquiry={}, failure={},
            metrics=dict(booked_passenger_trips=1, completed_passenger_trips=1, booked_positioning_trips=0,
                         completed_positioning_trips=0, booked_yard_trips=2, completed_yard_trips=2,
                         booked_passenger_km=km, booked_positioning_km=0., booked_yard_km=.5,
                         fleet_sets_required=7, distance_km=km+.5, source_kwh=120.,
                         minimum_collector_v=1490., peak_site_current_ka=.7, bound_branch_rms_current_ka=.4,
                         max_site_rms_current_ka=.5, maximum_arrival_delay_s=20, boarded_passengers=10.),
            gates=dict(all_workings_complete=True, dc_numerical_screen=True, motion_work_balance_screen=True,
                       utility_connection_approved=False, protection_approved=False, thermal_ratings_verified=False),
        )

    def working_day(self, cache=None, sources=None):
        return audit.working_day(self.route, self.demand, self.vehicle, self.climate, "paired6", "normal", 0,
                                 cache, sources or {"solver-test": "revision-a"}, phase=1306)

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
        self.assertFalse(result["physical_acceptance"])
        self.assertIsNone(result["investment_selection"])
        with self.assertRaisesRegex(ValueError, "comparisons are incomplete"):
            audit_register.disposition(self.route, self.demand, self.vehicle, days[:-1], None, {})
        with self.assertRaisesRegex(ValueError, "duplicated duty"):
            audit_register.disposition(self.route, self.demand, self.vehicle, days + [days[0]], None, {})
        mismatched = deepcopy(days)
        mismatched[-1]["candidate_id"] = "revised physical feeder"
        with self.assertRaisesRegex(ValueError, "different physical candidates"):
            audit_register.disposition(self.route, self.demand, self.vehicle, mismatched, None, {})
        days[-1]["failed_screens"].append("all_workings_complete")
        days[-1]["gates"]["all_workings_complete"] = False
        failed = audit_register.disposition(self.route, self.demand, self.vehicle, days, None, {})
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


if __name__ == "__main__":
    unittest.main()

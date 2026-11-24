"""Scope, service and production reconciliations for the Airport audit."""

from copy import deepcopy
import unittest

from cities.Baghdad.engineering.mechanical.civil import family_comparison
from cities.Baghdad.engineering.simulation import (
    airport_alignment, airport_demand, audit_power_return, audit_production, motion_power, vehicle_audit,
)


class AuditProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.alignment = airport_alignment.evaluate()
        cls.vehicle = vehicle_audit.evaluate()
        cls.demand = airport_demand.evaluate(cls.alignment, headway_min=30)
        civil = family_comparison.evaluate_high_load(cls.alignment["route_km"], selected_family="U", selected_span_m=20)
        cls.civil = next(row for row in civil["rows"] if row["physical_id"] == civil["quotation_leaders"]["base"]["physical_id"])
        central = cls.vehicle["mass_cases"]["central"]
        cls.motion = audit_production.seal_motion(motion_power.compact(motion_power.evaluate(dict(
            candidate_id=cls.vehicle["candidate_id"], alignment=cls.alignment,
            chainages_km=cls.alignment["chainages_km"], demand_record=cls.demand, dwell_s=cls.demand["dwell_s"],
            topology="paired6", headway_min=cls.demand["headway_min"],
            loaded_train_kg=central["loaded_train_kg"], tare_train_kg=central["tare_train_kg"],
        ))))
        cls.civil_evaluation_id = civil["evaluation_id"]
        cls.result = audit_production.evaluate(cls.alignment, cls.vehicle, cls.motion, cls.civil, demand=cls.demand,
                                               civil_evaluation_id=cls.civil_evaluation_id)

    def evaluate(self, *, vehicle=None, motion=None, civil=None, offers=(), risk_return=None):
        return audit_production.evaluate(
            self.alignment, vehicle or self.vehicle, motion or self.motion, civil or self.civil,
            demand=self.demand, civil_evaluation_id=self.civil_evaluation_id, supplier_offers=offers,
            risk_return=risk_return,
        )

    def risk_return(self):
        return dict(candidate_id=self.vehicle["candidate_id"], alignment_id=self.alignment["alignment_id"],
                    feeder_physical_id=audit_power_return.binding(self.motion)["feeder_physical_id"],
                    civil_row_id=self.civil["audit_row_id"],
                    cash_basis_id=self.result["cash"]["owner_risk_sensitivity"]["cash_basis_id"],
                    currency="constant 2026 USD", basis_date="2026-11-24", calibration="uncalibrated", lines=[
                        dict(risk_id="feeder-install", description="Illustrative unmatched feeder installation",
                             evidence_basis="Synthetic range for validation only; buyer rate return required",
                             cost_exclusions=["historical priced traction lots", "feeder upkeep", "renewals"],
                             period="opening-direct", operating_year=None,
                             range_usd={"low": 1_000_000, "base": 2_000_000, "high": 3_000_000},
                             cash_treatment="substitute-unpriced-lot",
                             substitutes_unpriced_lot_id="revised-feeder-package",
                             historical_contingency_overlap_usd={"low": 100_000, "base": 200_000, "high": 300_000},
                             overlap_basis="Illustrative declared allocation within inherited opening contingency"),
                        dict(risk_id="delay-claims", description="Illustrative owner delay claim exposure",
                             evidence_basis="Synthetic range for validation only; claims history required",
                             cost_exclusions=["feeder installation", "quoted lots"],
                             period="opening-direct", operating_year=None,
                             range_usd={"low": 0, "base": 500_000, "high": 1_000_000},
                             cash_treatment="exposure-only", substitutes_unpriced_lot_id=None,
                             historical_contingency_overlap_usd=None, overlap_basis=None),
                    ])

    def test_working_day_drives_partial_cash(self):
        receipt = self.result
        operation = receipt["operation_basis"]
        day = self.motion["metrics"]
        self.assertEqual(operation["operated_annual_train_km"], self.motion["annual_train_km"])
        self.assertEqual(operation["completed_working_day_passenger_trips"], day["completed_passenger_trips"])
        booked = operation["booked_annual_train_km_by_working"]
        self.assertAlmostEqual(operation["booked_annual_train_km"], sum(booked.values()))
        self.assertGreater(booked["yard"], 0)
        self.assertAlmostEqual(booked["passenger"], day["booked_passenger_trips"]*self.alignment["route_km"]*365)
        self.assertEqual(operation["working_day_nonrevenue_trips"]["yard"]["booked"], day["booked_yard_trips"])
        self.assertAlmostEqual(operation["annual_completed_journeys"], 365*day["boarded_passengers"])
        self.assertLessEqual(operation["annual_paid_journeys_proxy"], operation["annual_completed_journeys"])
        self.assertEqual(receipt["quantities"]["cars"], day["fleet_sets_required"]*6)
        lots = {row["lot_id"]: row for row in receipt["pricings"]}
        self.assertTrue(audit_production.CIVIL_DISPLACED.isdisjoint(lots))
        self.assertTrue(audit_production.FEEDER_LOTS.isdisjoint(lots))
        self.assertIsNone(lots["revised-feeder-package"]["usd"])
        self.assertEqual(lots["audited-standard-viaduct"]["usd"]["base"],
                         self.civil["standard_only_cost_cases"]["base"]["installed_usd"])
        self.assertLess(lots["audited-standard-viaduct"]["usd"]["base"], self.civil["priced_cases"]["base"]["installed_usd"])
        self.assertAlmostEqual(lots["opex-power"]["quantity"], operation["annual_estimated_utility_kwh"]/1e6)
        self.assertEqual(receipt["cash"]["profiles"]["base"]["annual_fares_usd"],
                         operation["annual_paid_journeys_proxy"]*operation["net_usd_per_paid_journey"])
        self.assertFalse(receipt["financial_selection_eligible"])
        self.assertIsNone(receipt["cash"]["sensitivity"]["confidence_interval"])
        self.assertIsNone(receipt["complete_installed_price_usd"])
        self.assertEqual(receipt["cash"]["scope"]["status"], "priced subtotal")
        self.assertIn("feeder-renewals", receipt["cash"]["scope"]["unpriced_lots_by_group"]["renewal-schedule"])
        self.assertIsNone(receipt["feeder_scope"]["renewals"]["operating_year"])

    def test_workshop_excludes_closure_and_keeps_disruptions(self):
        result = self.result
        self.assertGreater(result["civil_closure_bay_m"], 0)
        self.assertIsNone(result["closure_schedule_and_price"])
        self.assertEqual(set(result["scenarios"]), set(audit_production.production.SCENARIOS) | {"48h-mould-dwell"})
        for scenario in result["scenarios"].values():
            self.assertEqual(scenario["completed_units"]["installed_standard_placements"],
                             self.civil["quantities"]["standard_placements"])
            self.assertEqual(scenario["completed_units"]["pier_positions_assumed"], result["quantities"]["piers"])
        self.assertEqual(result["scenarios"]["rejected-first-article"]["completed_units"]["rejected_articles"], 1)
        self.assertEqual(result["scenarios"]["normal"]["mould_dwell_hours"], 24)
        self.assertEqual(result["scenarios"]["48h-mould-dwell"]["mould_dwell_hours"], 48)
        self.assertEqual(result["scenarios"]["48h-mould-dwell"]["mould_positions"],
                         result["scenarios"]["normal"]["mould_positions"])
        self.assertGreater(result["scenarios"]["48h-mould-dwell"]["last_completion_workday"],
                           result["scenarios"]["normal"]["last_completion_workday"])
        self.assertEqual(result["child_ids"]["motion_evaluation_id"], self.motion["evaluation_id"])

    def test_factory_disruption_rephases_full_purchaser_ledgers(self):
        cash = self.result["cash"]
        phasing = cash["disruption_phasing"]
        self.assertEqual(set(phasing), set(self.result["scenarios"]))
        for name, scheduled in self.result["scenarios"].items():
            row = phasing[name]
            self.assertEqual(row["last_completion_workday"], scheduled["last_completion_workday"])
            self.assertEqual(row["material_delay_workdays"], scheduled["material_delay_workdays"])
            self.assertEqual(row["availability_factor"], scheduled["availability_factor"])
            self.assertEqual(row["first_article_scrap_gate"], scheduled["first_article_scrap_gate"])
            self.assertEqual(row["civil_beam_position_occupied_workdays"],
                             scheduled["occupied_resource_workdays"].get("civil-beam-position", 0))
            self.assertEqual(row["civil_beam_position_peak"],
                             scheduled["peak_resource_occupation"].get("civil-beam-position", 0))
            self.assertEqual(row["mould_dwell_hours"], scheduled["mould_dwell_hours"])
            self.assertEqual(row["mould_positions"], scheduled["mould_positions"])
            self.assertEqual(row["opening_slip_years"], row["service_start_year"] - cash["service_start_year"])
            self.assertIsNone(row["disruption_increment_usd"])
            for case in audit_production.production.PRICES:
                profile = (cash["profiles"] if row["cash_profile_reference"] else row["price_profiles"])[case]
                ledger = profile["cash_by_year"]
                self.assertEqual(len(ledger), row["service_start_year"] + 29)
                self.assertEqual(sum(item["capital_usd"] for item in ledger), profile["capital_usd"])
                self.assertEqual(sum(item["opex_usd"] > 0 for item in ledger), 30)
                self.assertAlmostEqual(row["priced_30y_pv_timing_delta_usd"][case],
                                       profile["priced_30y_pv_usd"] - cash["profiles"][case]["priced_30y_pv_usd"])
        self.assertEqual(phasing["normal"]["cash_profile_reference"], "cash.profiles")
        self.assertIsNone(phasing["normal"]["price_profiles"])

        # Force a later opening without changing any priced lot or operating year.
        slipped = deepcopy(self.result["scenarios"]["delayed-material"])
        slipped["last_completion_workday"] = 250 * (cash["service_start_year"] + 1)
        rows = [row for row in self.result["pricings"] if row["usd"] is not None]
        paid = self.result["operation_basis"]["annual_paid_journeys_proxy"]
        fare = self.result["operation_basis"]["net_usd_per_paid_journey"]
        row = audit_production.factory_disruption_phasing(rows, {"slipped": slipped}, cash, paid, fare)["slipped"]
        self.assertEqual(row["opening_slip_years"], 2)
        for case in audit_production.production.PRICES:
            original = cash["profiles"][case]
            shifted = row["price_profiles"][case]
            self.assertEqual(shifted["capital_usd"], original["capital_usd"])
            self.assertEqual(shifted["annual_opex_usd"], original["annual_opex_usd"])
            self.assertEqual(shifted["annual_fares_usd"], original["annual_fares_usd"])
            self.assertEqual(sum(item["renewals_usd"] for item in shifted["cash_by_year"]),
                             sum(item["renewals_usd"] for item in original["cash_by_year"]))
            self.assertEqual(shifted["cash_by_year"][-1]["year"], row["service_start_year"] + 29)
            self.assertEqual(sum(item["opex_usd"] > 0 for item in shifted["cash_by_year"]), 30)

    def test_itemised_owner_risk_substitutes_only_explicit_unpriced_scope(self):
        source = self.risk_return()
        result = self.evaluate(risk_return=source)
        nominal = result["cash"]["profiles"]
        risk = result["cash"]["owner_risk_sensitivity"]
        self.assertEqual(risk["calibration"], "uncalibrated; no observed local loss data")
        self.assertEqual(risk["substituted_unpriced_lots"], ["revised-feeder-package"])
        self.assertIn("revised-feeder-package", result["unpriced_lots"])
        self.assertIsNone(risk["lines"][1]["net_increment_usd"])
        self.assertEqual(risk["lines"][0]["net_increment_usd"]["base"], 1_800_000)
        for case, increment in (("low", 900_000), ("base", 1_800_000), ("high", 2_700_000)):
            revised = risk["revised_profiles"][case]
            self.assertEqual(revised["capital_usd"] - nominal[case]["capital_usd"], increment)
            self.assertEqual(revised["annual_opex_usd"], nominal[case]["annual_opex_usd"])
            self.assertEqual(sum(row["capital_usd"] for row in revised["risk_increment_cash_by_year"]), increment)
            self.assertEqual(len(revised["cash_by_year"]), len(nominal[case]["cash_by_year"]))
            self.assertAlmostEqual(revised["priced_30y_pv_usd"] - nominal[case]["priced_30y_pv_usd"],
                                   increment / 1.04 ** (result["cash"]["service_start_year"] - 1))

        changed = self.risk_return()
        changed["candidate_id"] = "stale"
        with self.assertRaisesRegex(ValueError, "must match candidate"):
            self.evaluate(risk_return=changed)
        changed = self.risk_return()
        changed["feeder_physical_id"] = "stale"
        with self.assertRaisesRegex(ValueError, "must match candidate"):
            self.evaluate(risk_return=changed)
        changed = self.risk_return()
        changed["civil_row_id"] = "stale"
        with self.assertRaisesRegex(ValueError, "must match candidate"):
            self.evaluate(risk_return=changed)
        changed = self.risk_return()
        changed["cash_basis_id"] = "stale"
        with self.assertRaisesRegex(ValueError, "exact cash basis"):
            self.evaluate(risk_return=changed)
        changed = self.risk_return()
        changed["lines"][0]["historical_contingency_overlap_usd"]["base"] = 3_000_000
        with self.assertRaisesRegex(ValueError, "overlap exceeds gross"):
            self.evaluate(risk_return=changed)
        changed = self.risk_return()
        changed["lines"][0]["substitutes_unpriced_lot_id"] = "fleet"
        with self.assertRaisesRegex(ValueError, "matching unpriced lot"):
            self.evaluate(risk_return=changed)

    def test_risk_cash_basis_tracks_demand_and_simultaneous_offer(self):
        source = self.risk_return()
        baseline = self.result
        changed_context = deepcopy(baseline)
        changed_context["inputs"]["demand_evaluation_id"] = "different demand and timetable"
        self.assertNotEqual(audit_production.cash_basis(changed_context), source["cash_basis_id"])
        lot = next(row for row in baseline["pricings"] if row["lot_id"] == "fleet")
        offer = dict(offer_id="fixture offer", supplier="Synthetic supplier", scope_id=lot["scope_id"],
                     buyer_review_reference="Fixture review", offer_sha256="3" * 64,
                     price_usd=lot["usd"]["base"] + 1_000_000, claimed_domestic_value_usd=None)
        awarded_baseline = self.evaluate(offers=(offer,))
        self.assertNotEqual(awarded_baseline["cash"]["owner_risk_sensitivity"]["cash_basis_id"],
                            source["cash_basis_id"])
        other_offer = dict(offer, offer_id="other offer, same price", offer_sha256="4" * 64)
        other_baseline = self.evaluate(offers=(other_offer,))
        self.assertNotEqual(other_baseline["cash"]["owner_risk_sensitivity"]["cash_basis_id"],
                            awarded_baseline["cash"]["owner_risk_sensitivity"]["cash_basis_id"])
        with self.assertRaisesRegex(ValueError, "exact cash basis"):
            self.evaluate(offers=(offer,), risk_return=source)
        source["cash_basis_id"] = awarded_baseline["cash"]["owner_risk_sensitivity"]["cash_basis_id"]
        accepted = self.evaluate(offers=(offer,), risk_return=source)
        self.assertEqual(accepted["cash"]["owner_risk_sensitivity"]["return_id"], audit_production._id(source))

    def test_owner_risk_annual_and_renewal_periods_keep_thirty_operating_years(self):
        source = self.risk_return()
        annual = source["lines"][0]
        annual.update(risk_id="feeder-upkeep", period="first-full-year-operations",
                      substitutes_unpriced_lot_id="revised-feeder-upkeep",
                      historical_contingency_overlap_usd=dict.fromkeys(audit_production.production.PRICES, 0),
                      overlap_basis="Annual scope is outside the inherited opening contingency")
        renewal = deepcopy(annual)
        renewal.update(risk_id="feeder-renewal", period="renewal-schedule", operating_year=20,
                       substitutes_unpriced_lot_id="feeder-renewals",
                       overlap_basis="Renewal is outside the inherited opening contingency")
        source["lines"] = [annual, renewal]
        cash = self.evaluate(risk_return=source)["cash"]
        for case in audit_production.production.PRICES:
            additions = cash["owner_risk_sensitivity"]["revised_profiles"][case]["risk_increment_cash_by_year"]
            amount = annual["range_usd"][case]
            self.assertEqual(sum(row["opex_usd"] for row in additions), 30 * amount)
            self.assertEqual(sum(row["renewals_usd"] for row in additions), renewal["range_usd"][case])
            self.assertEqual(sum(row["renewals_usd"] > 0 for row in additions), 1)
            self.assertEqual(next(row["year"] for row in additions if row["renewals_usd"]),
                             cash["service_start_year"] + 19)

    def test_quotation_quantities_use_current_rate_units(self):
        result = self.result
        lots = {row["lot_id"]: row for row in result["pricings"]}
        length = self.alignment["route_km"]
        for key in ("signalling", "wayside-braking", "land-utilities"):
            row = lots[key]
            self.assertEqual(row["supplier_scope"]["unit"], "route-km")
            self.assertEqual(row["supplier_scope"]["quantity"], length)
            self.assertAlmostEqual(row["usd"]["base"], row["usd_per_current_unit"]["base"]*length)
            self.assertAlmostEqual(row["factor"]["base"], length/12)
        self.assertEqual(lots["track"]["supplier_scope"]["quantity"], 2*length)
        self.assertEqual(lots["track"]["supplier_scope"]["unit"], "track-km")
        self.assertEqual(lots["renewal-common-signalling-and-brake"]["supplier_scope"]["unit"], "track-km")
        self.assertEqual(lots["renewal-common-signalling-and-brake"]["supplier_scope"]["renewal_events"], 1)
        self.assertEqual(lots["renewal-fleet-major-renewal"]["supplier_scope"]["unit"], "trainsets")
        self.assertEqual(lots["renewal-fleet-major-renewal"]["supplier_scope"]["quantity"], result["quantities"]["sets"])

    def test_complete_scope_offer_replaces_existing_lot_and_origin_stays_unverified(self):
        lot = next(row for row in self.result["pricings"] if row["lot_id"] == "fleet")
        offer = dict(offer_id="test fleet offer", supplier="Synthetic supplier", scope_id=lot["scope_id"],
                     buyer_review_reference="Scope approval input", offer_sha256="1"*64,
                     price_usd=lot["usd"]["base"]+1_000_000, claimed_domestic_value_usd=20_000_000)
        new = self.evaluate(offers=(offer,))
        prior, changed = (receipt["cash"]["profiles"]["base"]["capital_usd"] for receipt in (self.result,new))
        self.assertAlmostEqual(changed-prior, 1_000_000 * 1.105 * 1.20)
        self.assertIsNone(new["localisation"]["verified_domestic_share"])
        self.assertEqual(new["localisation"]["buyer_referenced_offers"][0]["displaced_usd"], lot["usd"])
        with self.assertRaisesRegex(ValueError, "unique complete lot"):
            self.evaluate(offers=(dict(offer, scope_id="stale"),))
        motion = self.unsealed_motion()
        motion["evaluation_id"] = "3"*64
        with self.assertRaisesRegex(ValueError, "unique complete lot"):
            self.evaluate(motion=audit_production.seal_motion(motion), offers=(offer,))

    def unsealed_motion(self):
        result = deepcopy(self.motion)
        result.pop(audit_production.MOTION_RECORD_ID)
        return result

    def test_feeder_offer_prices_only_the_matching_cash_period(self):
        lot = next(row for row in self.result["pricings"] if row["lot_id"] == "revised-feeder-upkeep")
        offer = dict(offer_id="test feeder upkeep", supplier="Synthetic supplier", scope_id=lot["scope_id"],
                     buyer_review_reference="Scope approval input", offer_sha256="2"*64,
                     price_usd=500_000, claimed_domestic_value_usd=None)
        new = self.evaluate(offers=(offer,))
        prior, changed = (receipt["cash"]["profiles"]["base"] for receipt in (self.result, new))
        self.assertEqual(changed["capital_usd"], prior["capital_usd"])
        self.assertAlmostEqual(changed["annual_opex_usd"] - prior["annual_opex_usd"], offer["price_usd"])
        self.assertNotIn(lot["lot_id"], new["unpriced_lots"])
        self.assertIn("revised-feeder-package", new["unpriced_lots"])
        self.assertIn("feeder-renewals", new["unpriced_lots"])
        feeder = new["feeder_scope"]["audit_ledger"]
        self.assertEqual(feeder["annual_upkeep"]["usd"]["base"], offer["price_usd"])
        self.assertIsNone(feeder["opening"]["usd"])
        self.assertFalse(new["financial_selection_eligible"])

    def test_mixed_upstream_identity_refused(self):
        motion = self.unsealed_motion()
        motion["physical"]["upstream_candidate_id"] = "different"
        with self.assertRaisesRegex(ValueError, "share the ordinary working day"):
            self.evaluate(motion=audit_production.seal_motion(motion))
        motion = self.unsealed_motion()
        motion["scenario"]["demand_evaluation_id"] = "different"
        with self.assertRaisesRegex(ValueError, "different OD records"):
            self.evaluate(motion=audit_production.seal_motion(motion))

    def test_changed_receipt_payloads_and_missing_energy_are_refused(self):
        for key in ("source_kwh", "boarded_passengers", "completed_passenger_trips"):
            changed = deepcopy(self.motion)
            changed["metrics"].pop(key)
            with self.assertRaisesRegex(ValueError, "Moving working day record identity"):
                self.evaluate(motion=changed)
        changed = self.unsealed_motion()
        changed["metrics"].pop("source_kwh")
        with self.assertRaisesRegex(ValueError, "metered-side DC energy"):
            self.evaluate(motion=audit_production.seal_motion(changed))
        changed = deepcopy(self.motion)
        changed["annual_train_km"] += 100
        with self.assertRaisesRegex(ValueError, "Moving working day record identity"):
            self.evaluate(motion=changed)
        changed = self.unsealed_motion()
        changed["booked_annual_train_km"] -= changed["metrics"]["booked_yard_km"]*365
        with self.assertRaisesRegex(ValueError, "Booked train-km and working-day"):
            self.evaluate(motion=audit_production.seal_motion(changed))
        civil = deepcopy(self.civil)
        civil["standard_only_cost_cases"]["base"]["known_installed_subtotal_usd"] += 100
        with self.assertRaisesRegex(ValueError, "Civil audit row record identity"):
            self.evaluate(civil=civil)
        vehicle = deepcopy(self.vehicle)
        vehicle["mass_cases"]["high"]["loaded_train_kg"] += 100
        with self.assertRaisesRegex(ValueError, "Vehicle audit record identity"):
            self.evaluate(vehicle=vehicle)


if __name__ == "__main__":
    unittest.main()

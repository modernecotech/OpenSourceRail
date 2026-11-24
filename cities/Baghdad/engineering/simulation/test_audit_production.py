"""Scope, service and production reconciliations for the Airport audit."""

from copy import deepcopy
import unittest

from cities.Baghdad.engineering.mechanical.civil import family_comparison
from cities.Baghdad.engineering.simulation import (
    airport_alignment, airport_demand, audit_production, motion_power, vehicle_audit,
)


class AuditProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.alignment = airport_alignment.evaluate()
        cls.vehicle = vehicle_audit.evaluate()
        cls.demand = airport_demand.evaluate(cls.alignment)
        civil = family_comparison.evaluate_high_load(cls.alignment["route_km"], selected_family="U", selected_span_m=20)
        cls.civil = next(row for row in civil["rows"] if row["physical_id"] == civil["quotation_leaders"]["base"]["physical_id"])
        central = cls.vehicle["mass_cases"]["central"]
        cls.motion = audit_production.seal_motion(motion_power.compact(motion_power.evaluate(dict(
            candidate_id=cls.vehicle["candidate_id"], alignment=cls.alignment,
            chainages_km=cls.alignment["chainages_km"], demand_record=cls.demand, dwell_s=cls.demand["dwell_s"],
            topology="paired6", loaded_train_kg=central["loaded_train_kg"], tare_train_kg=central["tare_train_kg"],
        ))))
        cls.civil_evaluation_id = civil["evaluation_id"]
        cls.result = audit_production.evaluate(cls.alignment, cls.vehicle, cls.motion, cls.civil, demand=cls.demand,
                                               civil_evaluation_id=cls.civil_evaluation_id)

    def evaluate(self, *, vehicle=None, motion=None, civil=None, offers=()):
        return audit_production.evaluate(
            self.alignment, vehicle or self.vehicle, motion or self.motion, civil or self.civil,
            demand=self.demand, civil_evaluation_id=self.civil_evaluation_id, supplier_offers=offers,
        )

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

    def test_workshop_excludes_closure_and_keeps_disruptions(self):
        result = self.result
        self.assertGreater(result["civil_closure_bay_m"], 0)
        self.assertIsNone(result["closure_schedule_and_price"])
        self.assertEqual(set(result["scenarios"]), set(audit_production.production.SCENARIOS))
        for scenario in result["scenarios"].values():
            self.assertEqual(scenario["completed_units"]["installed_standard_placements"],
                             self.civil["quantities"]["standard_placements"])
            self.assertEqual(scenario["completed_units"]["pier_positions_assumed"], result["quantities"]["piers"])
        self.assertEqual(result["scenarios"]["rejected-first-article"]["completed_units"]["rejected_articles"], 1)
        self.assertEqual(result["child_ids"]["motion_evaluation_id"], self.motion["evaluation_id"])

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

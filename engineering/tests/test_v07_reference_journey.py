"""Joined v0.7 corridor edit, with no v0.6 selection or ERP transaction."""
import unittest

from engineering.v07_reference_journey import evaluate


JOINED = "osr-v07-joined-prototype-20261117"


class ReferenceJourneyTest(unittest.TestCase):
    def test_station_edit_recalculates_same_family(self):
        before = evaluate(expected_parent_candidate_id=JOINED)
        after = evaluate(stations=13, expected_parent_candidate_id=JOINED)
        self.assertEqual(before["physical_candidate_id"], JOINED)
        self.assertEqual(after["parent_physical_candidate_id"], JOINED)
        self.assertNotEqual(after["physical_candidate_id"], before["physical_candidate_id"])
        self.assertNotEqual(after["evaluation_id"], before["evaluation_id"])
        self.assertNotEqual(after["selection_id"], before["selection_id"])
        self.assertEqual(before["service"]["active_trainsets"], 44)
        self.assertEqual(before["service"]["reserve_trainsets"], 7)
        self.assertEqual(after["service"]["active_trainsets"], 46)
        self.assertEqual(after["service"]["reserve_trainsets"], 8)
        self.assertGreater(after["service"]["additional_round_trip_s"], 150)
        self.assertEqual(before["civil"]["beam_lifts"], after["civil"]["beam_lifts"])
        self.assertEqual(after["civil"]["support_positions"], 6002)
        self.assertEqual(after["civil"]["station_count"], 13)
        self.assertGreater(after["energy"]["annual_total_kwh"], before["energy"]["annual_total_kwh"])
        self.assertAlmostEqual(before["cost"]["installed_capital_usd_m"], 1023.4992)
        self.assertGreater(after["cost"]["installed_capital_usd_m"], before["cost"]["installed_capital_usd_m"])
        self.assertEqual(len(before["cost"]["scope_totals_usd_m"]), 14)
        self.assertEqual(len(after["cost"]["scope_totals_usd_m"]), 14)
        self.assertAlmostEqual(sum(after["cost"]["scope_totals_usd_m"].values()),
                               after["cost"]["installed_capital_usd_m"])
        self.assertEqual(after["manufacturing"]["quantity_schedule"]["powered_six_car_sets"], 54)
        self.assertEqual(after["manufacturing"]["quantity_schedule"]["ten_metre_beams"], 6000)
        for key in ("physical_accepted", "engineering_accepted", "manufacturing_release", "operating_release"):
            self.assertFalse(after[key])
        self.assertFalse(after["manufacturing"]["erpnext_posted"])
        self.assertEqual(after, evaluate(stations=13, expected_parent_candidate_id=JOINED))
        self.assertEqual(before, evaluate(route_km=30, expected_parent_candidate_id=JOINED))
        longer = evaluate(route_km=31, expected_parent_candidate_id=JOINED)
        self.assertEqual(longer["civil"]["beam_lifts"], 6200)
        self.assertEqual(longer["civil"]["support_positions"], 6202)
        self.assertGreater(longer["cost"]["installed_capital_usd_m"], before["cost"]["installed_capital_usd_m"])

    def test_mixed_candidate_and_invalid_geometry_rejected(self):
        with self.assertRaisesRegex(ValueError, "Mixed joined candidate"):
            evaluate(expected_parent_candidate_id="756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3")
        for kwargs in ({"stations": 1}, {"stations": 101}, {"route_km": float("nan")},
                       {"route_km": 0}, {"stations": True}):
            with self.assertRaises(ValueError):
                evaluate(expected_parent_candidate_id=JOINED, **kwargs)


if __name__ == "__main__":
    unittest.main()

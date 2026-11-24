"""Tests for the corrected Airport alignment and OD handoff."""

import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cities.Baghdad.engineering.simulation import airport_alignment, airport_demand, corridor


class AlignmentDemandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (airport_alignment.ROOT / "build").mkdir(exist_ok=True)
        cls.alignment = airport_alignment.evaluate()

    def test_mapped_geometry_and_historical_bound(self):
        alignment = self.alignment
        self.assertFalse(alignment["historical_route_order_screen"]["screen_passed"])
        self.assertAlmostEqual(alignment["historical_route_order_screen"]["mapped_centroid_bound_km"], 15.08858, 5)
        self.assertAlmostEqual(alignment["route_km"], 17.46091, 5)
        self.assertAlmostEqual(alignment["mapped_road_reference_km"] + alignment["review_connector_km"],
                               alignment["route_km"])
        self.assertIsNone(alignment["grade_profile"])
        stop = alignment["stops"][4]
        self.assertIsNone(stop["longitude_latitude"])
        self.assertEqual(airport_alignment.geojson(alignment)["features"][-2]["geometry"], None)
        tampered = {**alignment, "alignment_id": "x" * 64}
        with self.assertRaisesRegex(ValueError, "alignment ID"):
            airport_alignment.validate(tampered)
        tampered = copy.deepcopy(alignment)
        tampered["stops"][1]["id"] = "Airport-02"
        with self.assertRaisesRegex(ValueError, "stop order"):
            airport_alignment.validate(tampered)

    def test_supplied_centreline_stop_order_and_parent(self):
        alignment = self.alignment
        points = [stop["longitude_latitude"] for stop in alignment["stops"]]
        points[1] = [44.322, 33.298]
        points[4] = [44.351, 33.281]
        geometry = {"type": "LineString", "coordinates": points}
        stops = [{"id": stop_id, "vertex": index, "coordinates": point}
                 for index, (stop_id, point) in enumerate(zip(airport_alignment.STOP_IDS, points))]
        submission = {
            "schema": airport_alignment.SURVEY_SCHEMA, "parent_candidate_id": alignment["parent_candidate_id"],
            "crs": "EPSG:4326", "document": "Synthetic fixture", "revision": "1",
            "verification_reference": "Fixture only", "geometry": geometry, "stops": stops,
        }

        def write(path):
            submission["geometry_sha256"] = airport_alignment.identity({"geometry": geometry, "stops": stops})
            path.write_text(json.dumps(submission))

        with TemporaryDirectory(dir=airport_alignment.ROOT / "build") as directory:
            path = Path(directory) / "survey.json"
            write(path)
            candidate = airport_alignment.evaluate(path)
            self.assertNotEqual(candidate["alignment_id"], alignment["alignment_id"])
            self.assertEqual(candidate["geometry_mode"], "supplied_centreline")
            self.assertTrue(all(s["longitude_latitude"] for s in candidate["stops"]))
            self.assertIsNone(candidate["grade_profile"])
            offset = candidate["stops"][1]["offset_from_register_centroid_km"]
            self.assertGreater(offset["distance_km"], 2)
            self.assertGreater(offset["east_km"], 0)
            self.assertIsNone(candidate["stops"][4]["offset_from_register_centroid_km"])
            # Evidence revisions do not change the physical hypothesis.
            submission["revision"] = "2"
            write(path)
            rereleased = airport_alignment.evaluate(path)
            self.assertEqual(rereleased["alignment_id"], candidate["alignment_id"])
            self.assertNotEqual(rereleased["record_id"], candidate["record_id"])
            submission["parent_candidate_id"] = "wrong-parent"
            write(path)
            with self.assertRaisesRegex(ValueError, "matched parent"):
                airport_alignment.evaluate(path)
            submission["parent_candidate_id"] = alignment["parent_candidate_id"]
            stops[1]["vertex"], stops[2]["vertex"] = stops[2]["vertex"], stops[1]["vertex"]
            write(path)
            with self.assertRaisesRegex(ValueError, "increase strictly"):
                airport_alignment.evaluate(path)
            stops[1]["vertex"], stops[2]["vertex"] = stops[2]["vertex"], stops[1]["vertex"]
            points[1] = stops[1]["coordinates"] = [alignment["retained_map_bounds_wsen"][0] - .001, 33.298]
            write(path)
            with self.assertRaisesRegex(ValueError, "geometry-bound coverage decision"):
                airport_alignment.evaluate(path)
            submission["coverage_decision"] = {
                "document": "Synthetic survey extension", "review_reference": "Fixture only",
                "reason": "Exercise coverage handling", "geometry_sha256": submission["geometry_sha256"],
            }
            write(path)
            outside = airport_alignment.evaluate(path)
            self.assertEqual(outside["survey_source"]["vertices_outside_retained_coverage"], 1)
            self.assertLess(outside["stops"][1]["offset_from_register_centroid_km"]["east_km"], 0)

    def test_frequency_and_access_sensitivities(self):
        alignment = self.alignment
        historical = corridor.evaluate()
        fixed15 = airport_demand.evaluate(alignment, mode="fixed")
        fixed30 = airport_demand.evaluate(alignment, mode="fixed", headway_min=30, walk="long")
        self.assertEqual(fixed15["hourly_od"], historical["hourly_od"])
        self.assertEqual(fixed15["hourly_od"], fixed30["hourly_od"])
        self.assertAlmostEqual(fixed30["busiest_departure_load"], 2 * fixed15["busiest_departure_load"])
        self.assertNotAlmostEqual(fixed15["mean_trip_km"], historical["mean_trip_km"])
        central = airport_demand.evaluate(alignment)
        cases = ({"headway_min": 20}, {"walk": "long"}, {"fare_usd": 0.5})
        for args in cases:
            self.assertLess(airport_demand.evaluate(alignment, **args)["annual_all_journeys"],
                            central["annual_all_journeys"])
        cases = ({"walk": "short"}, {"transfer": False})
        for args in cases:
            self.assertGreater(airport_demand.evaluate(alignment, **args)["annual_all_journeys"],
                               central["annual_all_journeys"])
        self.assertEqual(airport_demand.validate(json.loads(json.dumps(central)), alignment), central)
        with self.assertRaisesRegex(ValueError, "Airport demand ID"):
            airport_demand.validate({**central, "alignment_id": "wrong"}, alignment)
        with self.assertRaisesRegex(ValueError, "stop order"):
            airport_demand.validate({**central, "stop_ids": central["stop_ids"][::-1]}, alignment)

    def test_observed_counts_and_mismatches(self):
        alignment = self.alignment
        submitted = {
            "schema": airport_demand.OBSERVED_SCHEMA, "alignment_id": alignment["alignment_id"],
            "stop_ids": list(airport_alignment.STOP_IDS), "timezone": "Asia/Baghdad",
            "document": "Synthetic survey fixture", "sample_date_from": "2026-11-20",
            "sample_date_to": "2026-11-21", "observed_days": 2, "resolution": "hourly",
            "od": [{"hour": 9, "from": "Airport-00", "to": "Airport-05", "all": 20, "paying": 16}],
        }
        with TemporaryDirectory(dir=airport_alignment.ROOT / "build") as directory:
            path = Path(directory) / "observed.json"
            path.write_text(json.dumps(submitted))
            result = airport_demand.evaluate(alignment, observed=path, headway_min=30)
            self.assertEqual(result["mode"], "observed")
            self.assertEqual(result["hourly_od"][9][0][-1], 10)
            self.assertEqual(result["annual_all_journeys"], 3650)
            self.assertEqual(result["annual_paid_journeys"], 2920)
            self.assertAlmostEqual(result["annual_passenger_km"], 3650 * alignment["route_km"])
            submitted["od"][0]["all"] = 2 * 10**9
            path.write_text(json.dumps(submitted))
            large = airport_demand.evaluate(alignment, observed=path)
            self.assertEqual(large["hourly_od"][9][0][-1], 10**9)
            submitted["od"][0]["all"] = 20
            submitted["resolution"] = "daily"
            del submitted["od"][0]["hour"]
            path.write_text(json.dumps(submitted))
            daily = airport_demand.evaluate(alignment, observed=path)
            self.assertAlmostEqual(daily["annual_all_journeys"], result["annual_all_journeys"])
            self.assertEqual(daily["observed_source"]["count_resolution"], "daily")
            submitted["alignment_id"] = "wrong"
            path.write_text(json.dumps(submitted))
            with self.assertRaisesRegex(ValueError, "matching alignment"):
                airport_demand.evaluate(alignment, observed=path)
            submitted["alignment_id"] = alignment["alignment_id"]
            submitted["od"][0]["to"] = "Airport-06"
            path.write_text(json.dumps(submitted))
            with self.assertRaisesRegex(ValueError, "route stops"):
                airport_demand.evaluate(alignment, observed=path)

    def test_corrected_motion_rejects_mismatched_handoffs(self):
        from cities.Baghdad.engineering.simulation import airport_audit_verify

        for label in airport_audit_verify.CASE_TIMINGS:
            with self.subTest(label=label):
                inputs, _, _ = airport_audit_verify.ordinary_inputs(label)
                rejected = airport_audit_verify.verify_inputs(inputs)
                self.assertIn("same timetable", rejected["dwell"])
                self.assertIn("candidate-bound demand", rejected["bound_demand_required"])
                self.assertIn("same timetable", rejected["demand_factor"])
                self.assertIn("positioning", rejected["unsupported_positioning_slack"].lower())


if __name__ == "__main__":
    unittest.main()

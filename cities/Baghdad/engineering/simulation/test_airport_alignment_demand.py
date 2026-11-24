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
            vertical = dict(geometry_sha256=submission["geometry_sha256"], datum="Synthetic rail datum",
                            elevations_m=[30, 31, 28, 28, 30, 29])
            submission["vertical_profile"] = vertical
            write(path)
            levelled = airport_alignment.evaluate(path)
            profile = levelled["grade_profile"]
            self.assertNotEqual(levelled["alignment_id"], candidate["alignment_id"])
            self.assertEqual(levelled["chainages_km"], candidate["chainages_km"])
            self.assertEqual(profile["datum"], vertical["datum"])
            for chainage_m, chainage_km in zip(profile["chainages_m"], levelled["chainages_km"], strict=True):
                self.assertAlmostEqual(chainage_m, 1000 * chainage_km)
            self.assertAlmostEqual(profile["grades_pct"][0], 100 / profile["chainages_m"][1])
            self.assertLess(profile["grades_pct"][1], 0)
            self.assertEqual(profile["grades_pct"][2], 0)
            self.assertEqual(levelled["survey_source"]["vertical_profile_sha256"], airport_alignment.identity(profile))
            self.assertEqual(airport_alignment.validate(json.loads(json.dumps(levelled))), levelled)
            for change, reason in (
                (lambda record: record["stops"][1].update(longitude_latitude=record["stops"][2]["longitude_latitude"]),
                 "surveyed stops"),
                (lambda record: record["segments"][1].update(start_km=record["segments"][1]["start_km"] + .01),
                 "segment chainages"),
                (lambda record: (record["stops"][1].update(chainage_km=record["stops"][1]["chainage_km"] + .01),
                                 record["chainages_km"].__setitem__(1, record["chainages_km"][1] + .01)),
                 "surveyed stops"),
            ):
                tampered = copy.deepcopy(levelled)
                change(tampered)
                tampered["alignment_id"] = airport_alignment.identity(airport_alignment.physical_record(tampered))
                tampered["record_id"] = airport_alignment.identity(
                    {key: value for key, value in tampered.items() if key != "record_id"})
                with self.assertRaisesRegex(ValueError, reason):
                    airport_alignment.validate(tampered)
            tampered = copy.deepcopy(levelled)
            tampered["grade_profile"]["grades_pct"][0] = 0
            tampered["alignment_id"] = airport_alignment.identity(airport_alignment.physical_record(tampered))
            tampered["record_id"] = airport_alignment.identity({k: v for k, v in tampered.items() if k != "record_id"})
            with self.assertRaisesRegex(ValueError, "grade profile differs"):
                airport_alignment.validate(tampered)
            for changes, reason in (
                ({"geometry_sha256": "wrong"}, "bind the supplied"),
                ({"datum": ""}, "vertical datum"),
                ({"elevations_m": [1]}, "per vertex"),
                ({"elevations_m": [0, 0, float("inf"), 0, 0, 0]}, "must be finite"),
                ({"elevations_m": [1.7e308, -1.7e308, 0, 0, 0, 0]}, "grades must be finite"),
            ):
                submission["vertical_profile"] = {**vertical, **changes}
                write(path)
                with self.assertRaisesRegex(ValueError, reason):
                    airport_alignment.evaluate(path)
            submission.pop("vertical_profile")
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
            "service_offer": airport_demand.evaluate(alignment, headway_min=30)["service_offer"]["observation_context"],
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
            self.assertEqual(result["observed_source"]["service_offer"], submitted["service_offer"])
            self.assertEqual(airport_demand.validate(json.loads(json.dumps(result)), alignment), result)
            tampered = copy.deepcopy(result)
            tampered["hourly_od"][9][0][5] += 1
            tampered["evaluation_id"] = airport_alignment.identity(
                {key: value for key, value in tampered.items() if key != "evaluation_id"})
            with self.assertRaisesRegex(ValueError, "conserve its annual count"):
                airport_demand.validate(tampered, alignment)
            tampered["annual_all_journeys"] += 365
            tampered["evaluation_id"] = airport_alignment.identity(
                {key: value for key, value in tampered.items() if key != "evaluation_id"})
            with self.assertRaisesRegex(ValueError, "loading and passenger-km"):
                airport_demand.validate(tampered, alignment)
            tampered = copy.deepcopy(result)
            tampered["observed_source"]["service_offer"]["headway_min"] = 15
            tampered.pop("evaluation_id")
            tampered["evaluation_id"] = airport_alignment.identity(tampered)
            with self.assertRaisesRegex(ValueError, "retain its matched service"):
                airport_demand.validate(tampered, alignment)
            for changes in (
                {"headway_min": 15}, {"dwell_s": 36}, {"fare_usd": .5}, {"transfer": False},
                {"formation_cars": 3}, {"connecting_headway_min": 20}, {"walk": "long"},
            ):
                with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, "service offer must match"):
                    airport_demand.evaluate(alignment, **{"headway_min": 30, "observed": path, **changes})
            service = submitted["service_offer"]
            for changed in ({**service, "start_hour_local": 7}, {**service, "fare_usd": False}, None):
                submitted["service_offer"] = changed
                path.write_text(json.dumps(submitted))
                with self.assertRaisesRegex(ValueError, "service offer must match"):
                    airport_demand.evaluate(alignment, observed=path, headway_min=30)
            submitted["service_offer"] = service
            alternative = {"headway_min": 30, "fare_usd": .5, "transfer": False}
            submitted["service_offer"] = airport_demand.evaluate(
                alignment, **alternative)["service_offer"]["observation_context"]
            path.write_text(json.dumps(submitted))
            paid_service = airport_demand.evaluate(alignment, observed=path, **alternative)
            self.assertEqual(paid_service["hourly_od"], result["hourly_od"])
            self.assertEqual(paid_service["annual_paid_journeys"], result["annual_paid_journeys"])
            submitted["service_offer"] = service
            submitted["schema"] = "osr-baghdad-airport-observed-od/1"
            path.write_text(json.dumps(submitted))
            with self.assertRaisesRegex(ValueError, "Observed OD v2"):
                airport_demand.evaluate(alignment, observed=path, headway_min=30)
            submitted["schema"] = airport_demand.OBSERVED_SCHEMA
            submitted["od"][0]["all"] = 2 * 10**9
            path.write_text(json.dumps(submitted))
            large = airport_demand.evaluate(alignment, observed=path, headway_min=30)
            self.assertEqual(large["hourly_od"][9][0][-1], 10**9)
            submitted["od"][0]["all"] = 20
            submitted["resolution"] = "daily"
            del submitted["od"][0]["hour"]
            path.write_text(json.dumps(submitted))
            daily = airport_demand.evaluate(alignment, observed=path, headway_min=30)
            self.assertAlmostEqual(daily["annual_all_journeys"], result["annual_all_journeys"])
            self.assertEqual(daily["observed_source"]["count_resolution"], "daily")
            submitted["alignment_id"] = "wrong"
            path.write_text(json.dumps(submitted))
            with self.assertRaisesRegex(ValueError, "matching alignment"):
                airport_demand.evaluate(alignment, observed=path, headway_min=30)
            submitted["alignment_id"] = alignment["alignment_id"]
            submitted["od"][0]["to"] = "Airport-06"
            path.write_text(json.dumps(submitted))
            with self.assertRaisesRegex(ValueError, "route stops"):
                airport_demand.evaluate(alignment, observed=path, headway_min=30)

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

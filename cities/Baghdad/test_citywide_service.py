import csv
from collections import defaultdict
from hashlib import sha256
import io
import sys
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

from cities.Baghdad import citywide_clockface as clock
from cities.Baghdad import citywide_service as city


class CitywideServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = city.build()

    def test_every_costed_section_and_train_km_has_one_scope(self):
        r = self.record
        active = {s for sections in r["scope"]["group_sections"].values() for s in sections}
        deferred, reserved = set(r["deferred"]), set(r["reserved_sections_km"])
        self.assertTrue(active.isdisjoint(deferred | reserved))
        self.assertTrue(deferred.isdisjoint(reserved))
        self.assertEqual(len(active), 15)  # 14 route IDs plus the airport extension
        self.assertEqual(len(deferred), 5)
        self.assertEqual(len(reserved), 6)
        self.assertAlmostEqual(
            r["costed_route_km"],
            r["in_service_route_km"]
            + sum(r["reserved_sections_km"].values())
            + sum(x["km"] for x in r["deferred"].values()),
        )
        self.assertAlmostEqual(
            r["published_peak_offer"]["train_km_year"] + r["deferred_train_km_year"],
            r["original_14_group_budget_train_km_year"],
        )
        self.assertFalse(r["published_peak_offer"]["one_block_per_station_pair_screen_passed"])
        self.assertNotEqual(r["timed_layout_candidate_id"], r["scope"]["infrastructure_candidate_id"])
        self.assertFalse(r["owner_adopted"])
        self.assertFalse(r["physical_accepted"])

    def test_full_day_events_exclude_cross_group_conflicts(self):
        cfg, _, _, _, groups = city.inputs()
        t = self.record["timetable"]
        movements = defaultdict(list)
        # Independently expand full occupied windows. Check adjacent movements
        # of different service groups by sweep instead of reusing the CSP masks.
        for group, base in sorted(groups.items()):
            line, windows, trips = clock.line_plan(
                group, base, cfg, t["headway_s"], self.record["vehicle"]["level_brake_m_s2"]
            )
            for hint, intervals in windows.items():
                for a, b in intervals:
                    for k in range(-7, 37):
                        start = a + t["origin_phases_s"][group] + k * t["headway_s"]
                        movements[hint].extend([(start, group, 1), (start + b - a, group, -1)])
            self.assertEqual(line["departures"], len(trips))
            self.assertEqual(sum(line["start_and_end_sets_by_origin"]), line["sets"])
            self.assertLessEqual(line["max_speed_kmh"], cfg["vehicle"]["speed_cap_kmh"])
        for hint, interval_events in movements.items():
            occupied = defaultdict(int)
            for _, delta, group in sorted((time, delta, group) for time, group, delta in interval_events):
                occupied[group] += delta
                self.assertLessEqual(sum(count > 0 for count in occupied.values()), 1, hint)
        self.assertEqual(
            [x["resource_screen_passed"] for x in self.record["attempted_schedules"]], [False, False, True]
        )
        self.assertTrue(all(v >= 0 for v in t["minimum_clearances_s"].values()))
        self.assertEqual(self.record["demand_and_resources"]["passenger_trips_day"], 1008)
        self.assertLess(
            self.record["market"]["central"]["priced_annual_operations_usd_m"],
            self.record["market"]["central"]["published_annual_operations_usd_m"],
        )

    def test_exported_ring_working_returns_to_origin_in_both_directions(self):
        output = io.StringIO()
        with patch.object(sys, "argv", ["citywide_service", "--events", "M09"]), patch.object(
            sys, "stdout", output
        ):
            city.main()
        rows = list(csv.DictReader(io.StringIO(output.getvalue())))
        self.assertEqual(len(rows), 72 * 27)
        sets = defaultdict(list)
        for row in rows:
            sets[row["train"]].append(row)
        for events in sets.values():
            self.assertEqual(len({r["direction"] for r in events}), 1)
            self.assertEqual(events[0]["stop"].removesuffix("-lap"), events[-1]["stop"].removesuffix("-lap"))
        self.assertEqual(len(sets), self.record["timetable"]["groups"]["M09"]["sets"])

    def test_incompatible_or_unverifiable_owner_returns_fail_closed(self):
        r = self.record
        f = city.return_template(r)
        with TemporaryDirectory() as directory:
            p = Path(directory) / "counts.txt"
            p.write_text("simulated example")
            f["line_peak_loads"]["M05"] = dict(
                passengers_hour_direction=1450,
                direction="A_to_B",
                period_local="test hour",
                load_section="M-075 vicinity",
                file=p.name,
                sha256=sha256(p.read_bytes()).hexdigest(),
            )
            result = city.assess(r, f, directory)
            self.assertEqual(result["seen_loads"]["M05"]["spare_places_hour"], -50)
            self.assertFalse(result["field_evidence_authenticated"])
            self.assertIsNone(result["complete_funded_cost"])
            p.write_text("substitution")
            with self.assertRaises(ValueError):
                city.assess(r, f, directory)
            f["selection_id"] = "wrong"
            with self.assertRaises(ValueError):
                city.assess(r, f, directory)

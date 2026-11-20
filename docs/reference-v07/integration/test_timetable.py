from collections import Counter, defaultdict
import unittest

from timetable import DIR, build, report


class CoreWorkingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build()

    def test_fleet_stop_calls_and_all_service_hours(self):
        trips = self.data["trips"]
        departures = Counter((t["origin"], t["departure_s"] // 3600) for t in trips)
        duties = defaultdict(list)
        for t in trips:
            duties[t["train"]].append(t)
            stops = t["calls"]
            self.assertEqual(len({call["station"] for call in stops}), 12)
            self.assertEqual(stops[0]["departure_s"], t["departure_s"])
            self.assertEqual(stops[-1]["arrival_s"], t["arrival_s"])
            for stop in stops[1:-1]:
                self.assertAlmostEqual(stop["departure_s"] - stop["arrival_s"], 35)
        for end in ("S01","S12"):
            for hour in range(6,24):
                self.assertEqual(departures[end,hour], 30 if hour in (7,8,16,17) else 12)
        self.assertEqual(len(duties), 44)
        for duty in duties.values():
            for prev, nxt in zip(duty, duty[1:]):
                self.assertEqual(prev["dest"], nxt["origin"])
                self.assertGreaterEqual(nxt["departure_s"] - prev["arrival_s"], 180)
        s = self.data["summary"]
        self.assertAlmostEqual(sum(t["arrival_s"]-t["departure_s"] for t in trips)/3600, s["passenger_train_hours_day"])
        self.assertAlmostEqual(180*len(trips)/3600, s["minimum_turnback_train_hours_day"])
        self.assertEqual(s["annual_train_km"], 6307200)
        self.assertEqual(len(s["single_face_rejected_arrivals"]), 60)

    def test_terminal_resources_and_disruptions(self):
        s = self.data["summary"]
        for end, records in self.data["terminal_occupation"].items():
            faces = defaultdict(list)
            for r in records:
                faces[r["face"]].append(r)
            self.assertEqual(len(faces), s["required_faces"][end])
            for intervals in faces.values():
                for left, right in zip(intervals, intervals[1:]):
                    self.assertLessEqual(left["end_s"], right["begin_s"])
        excluded = set(s["exposed_trips"])
        actual = {t["trip"] for t in self.data["trips"] if t["train"] == s["failed_set"] and t["departure_s"] >= 7*3600}
        self.assertEqual(excluded, actual)
        self.assertGreater(len(s["blocked_face_holds"]), 0)
        self.assertEqual(report(self.data), (DIR / "TIMETABLE.md").read_text())

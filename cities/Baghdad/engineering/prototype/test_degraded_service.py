import json
import unittest

from cities.Baghdad import airport_integration
from cities.Baghdad.engineering.commissioning import feeder
from cities.Baghdad.engineering.prototype import car, degraded_service


class DegradedServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = airport_integration.build()
        cls.service = parent["service"]
        cls.opening = car.build(parent)["opening"]
        cls.power = feeder.evaluate(cls.opening, service=cls.service)

    def test_limit_and_service(self):
        files = degraded_service.artifacts(self.opening, self.power, self.service)
        report = json.loads(files["degraded-service.json"])
        c = report["sensitivity_cases"]["combined sensitivity"]
        self.assertAlmostEqual(c["floor_current_bound_ka"] * self.power["floor_kv"], c["floor_load_bound_mw"])
        self.assertLess(c["loads"]["two_accelerating"]["collector_kv"], self.power["floor_kv"])
        self.assertGreater(c["loads"]["one_accelerating"]["collector_kv"], self.power["floor_kv"])
        self.assertEqual(c["maximum_concurrent_scheduled_pulses"], 1)
        for row in report["single_site_and_adjacent_path_pair_outages"]:
            self.assertEqual(
                row["within_voltage_limit_throughout"]
                + row["overlap_review_required"]
                + row["outside_source_area"],
                736,
            )
            self.assertEqual(abs(row["isolated_site"] - row["adjacent_source"]), 1)
        self.assertFalse(report["evacuation_authorised"])
        self.assertIn(b"accessible", files["degraded-service.md"])
        with self.assertRaises(ValueError):
            degraded_service.artifacts(self.opening, self.power, dict(self.service, trips=[]))

    def test_count_distinct_pulses_and_exclusive_end(self):
        pulses = [(0, 3, 1, 2), (2, 4, 1, 2), (4, 5, 2, 3), (0, 6, 5, 6)]
        self.assertEqual(
            degraded_service._counts(pulses, 0, 2, 1),
            {
                "within_voltage_limit_throughout": 1,
                "overlap_review_required": 2,
                "intersecting_pulses": 3,
                "outside_source_area": 1,
            },
        )

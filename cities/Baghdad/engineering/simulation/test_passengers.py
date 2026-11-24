"""Regression checks for Airport crowd, heat and doorway sensitivities."""

import json
import unittest
from pathlib import Path

from cities.Baghdad.engineering.simulation import passengers


class PassengerTest(unittest.TestCase):
    def test_hot_day_requires_more_energy_and_exposes_capacity_hold(self):
        result = passengers.evaluate()
        mild, hot = (result["summer_cases"][temp] for temp in ("40", "48"))
        self.assertAlmostEqual(result["auxiliary_kw"], hot["thermal_target_auxiliary_kw"])
        self.assertAlmostEqual(hot["required_cooling_kw_thermal"], sum(hot["thermal_components_kw"].values()))
        self.assertGreater(hot["thermal_target_auxiliary_kw"], mild["thermal_target_auxiliary_kw"])
        self.assertLess(hot["trial_thermal_margin_kw"], 0)
        self.assertGreater(hot["trial_bus_margin_kw"], 0)
        self.assertIsNone(hot["actual_installed_cooling_kw_thermal"])

    def test_queue_and_train_exchange_reconcile(self):
        result = passengers.evaluate({"platform_queue": 100, "busiest_departure_load": 500})
        doors = result["door_exchange"]
        platform = result["station_movement"]
        self.assertEqual(doors["arriving_load"] - doors["assumed_alighting"] + doors["assumed_boarding"], 500)
        self.assertEqual(platform["present_waiting_people"], 100)
        self.assertEqual(platform["two_exit_entries"]["population"], 100 + doors["arriving_load"])
        self.assertGreater(platform["one_exit_entry_unavailable"]["serial_travel_plus_flow_s"],
                           platform["two_exit_entries"]["serial_travel_plus_flow_s"])
        self.assertIsNone(platform["protected_accessible_vertical_route"])
        self.assertEqual(passengers.evaluate({"platform_queue": 0})["door_exchange"]["assumed_alighting"], 0)

    def test_shorter_formation_changes_boarding_layout(self):
        result = passengers.evaluate({"cars": 3, "busiest_departure_load": 235, "platform_queue": 80})
        standard = passengers.evaluate()
        self.assertEqual(result["door_exchange"]["doors_active"], 12)
        self.assertGreater(result["door_exchange"]["slow_walk_tail_s"], standard["door_exchange"]["slow_walk_tail_s"])
        self.assertLess(result["auxiliary_kw"], standard["auxiliary_kw"])
        with self.assertRaises(ValueError):
            passengers.evaluate({"cars": 3, "busiest_departure_load": 351})

    def test_booked_dwell_limits_door_open_cooling_duty(self):
        inputs = dict(platform_queue=600, busiest_departure_load=600)
        baseline = passengers.evaluate(inputs)
        longer = passengers.evaluate(dict(inputs, dwell_s=66))
        self.assertEqual(baseline["door_exchange"]["planned_dwell_s"], 35)
        self.assertEqual(longer["door_exchange"]["planned_dwell_s"], 66)
        self.assertLess(baseline["door_exchange"]["assisted_dwell_margin_s"], 0)
        self.assertGreater(longer["door_exchange"]["assisted_dwell_margin_s"], 0)
        self.assertGreater(longer["auxiliary_kw"], baseline["auxiliary_kw"])

    def test_archived_native_comparison_and_provenance(self):
        path = Path(passengers.__file__).with_name("passenger-benchmark.json")
        if not path.exists():
            self.skipTest("Native result not supplied in this checkout")
        data = json.loads(path.read_text())
        benchmark_id = data.pop("native_evaluation_id")
        self.assertEqual(benchmark_id, passengers.identity(data))
        self.assertEqual(data["evaluation_id"], passengers.evaluate()["evaluation_id"])
        cases = data["native"]["cases"]
        self.assertEqual(len(cases), 8)
        for i in range(0, len(cases), 2):
            both, one = cases[i:i+2]
            self.assertEqual(both["population"], one["population"])
            self.assertEqual(both["version"], "1.4.2")
            self.assertGreater(one["elapsed_s"], both["elapsed_s"])
            for row in (both, one):
                self.assertEqual(row["population"], row["cleared"] + sum(row["uncleared_by_mobility"].values()))
                self.assertGreater(row["groups"]["wheeled"], 0)


if __name__ == "__main__":
    unittest.main()

"""Check bridge geometry, passenger certificates and protected turnbacks."""

import unittest
from hashlib import sha256

import numpy as np
from scipy.spatial import cKDTree

from cities.Baghdad import central_access, holistic_network, holistic_through, ring_corridors, straight_network_study
from cities.Baghdad import straight_through_layout as layout
from cities.Baghdad.test_holistic_through import point


class ThroughLayoutTests(unittest.TestCase):
    def test_published_routes_beam_premium_and_holds_share_candidate(self):
        record = central_access.read(straight_network_study.RECORD)
        publication_id = record.pop("publication_id")
        self.assertEqual(publication_id, sha256(central_access.encode(record)).hexdigest())
        chosen = record["display_trial"]
        self.assertIn(chosen, record["selection"]["both_terminals_outside_outer_ring"])
        self.assertIn("Tigris", record["layouts"][chosen]["name"])
        for row in record["approved_through"][chosen]:
            self.assertEqual(row["terminals_outside_outer_ring"], 2)
            self.assertGreaterEqual(row["tigris_crossing_count"], 1)
            self.assertTrue(all(row["ring_interchanges"].values()))
        civil, cost, beam = (record[key] for key in ("civil", "cost", "beam_schedule"))
        self.assertEqual({data["candidate_id"] for data in (record["network"], civil, cost, beam)},
                         {record["network"]["candidate_id"]})
        for case, row in cost["cost_cases"].items():
            self.assertEqual(row["direct_scope_usd_m"]["special_beam_increment"],
                             beam["totals"]["incremental_allowance_usd"][case] / 1e6)
            self.assertAlmostEqual(sum(row["direct_scope_usd_m"].values()), row["direct_total_usd_m"])
        self.assertIsNone(beam["totals"]["held_cost_usd"])
        self.assertIsNone(beam["totals"]["integrated_completion_day"])

    def test_dry_landing_requires_tagged_bridge_approach(self):
        scale = holistic_network.LOCAL_METRES
        endpoints = np.asarray([point(-3000, 0), point(-450, 0), point(450, 0), point(3000, 0)]) * scale
        context = {"layers": {"water": [{"geometry": {
            "type": "Polygon", "coordinates": [[point(-100, -300), point(100, -300), point(100, 300),
                                               point(-100, 300), point(-100, -300)]],
        }}]}}
        water = holistic_through.WaterGeometry.from_context(context)
        bridges = holistic_through.DirectionalRoads.from_paths([[point(-400, 20), point(400, 20)]])
        no_crossing = holistic_through.DirectionalRoads.from_paths([])
        rail = cKDTree([point(0, 4000) * scale])
        result = layout._corridor(endpoints, context, bridges, bridges, water, rail)
        self.assertEqual(result[2][0]["mapped_wet_width_m"], 200)
        self.assertIsNone(layout._corridor(endpoints, context, bridges, no_crossing, water, rail))

    def test_only_actual_shared_stations_pass_both_ring_policy(self):
        def line(*stations):
            return {"station_ids": list(stations), "one_way_km": 20}

        network = {"lines": {"M09": line("x", "other"), "M15": line("y", "z"),
                             "ST": line("a", "x", "y", "b")}}
        axis = {"id": "ST", "terminal_ids": ["a", "b"], "detour_ratio": 1.03,
                "water_crossings": [{"mapped_wet_width_m": 120}], "tigris_crossing_count": 1,
                "mapped_bridge_approaches": [[44.1, 33.1], [44.2, 33.2]], "terminals_outside_outer_ring": 2,
                "major_road_share": .4, "near_existing_rail_share": .3}
        self.assertEqual(layout._through_certificate(network, axis)["ring_interchanges"], {"M09": ["x"], "M15": ["y"]})
        with self.assertRaisesRegex(ValueError, "corroborated crossing"):
            layout._through_certificate(network, axis | {"tigris_crossing_count": 0})
        network["lines"]["M15"]["station_ids"].remove("y")
        with self.assertRaisesRegex(ValueError, "shared interchange with M15"):
            layout._through_certificate(network, axis)

    def test_turnback_keeps_outer_arms_and_ring_station_access(self):
        coordinates = {"first": point(-3000, 0), "last": point(3000, 0),
                       "left": point(-1000, 0), "right": point(1000, 0), "north": point(0, 1000)}
        stations = {code: {"coordinates": xy, "lines": [], "name": code, "basis": "fixture"}
                    for code, xy in coordinates.items()}
        ring = [coordinates["left"], point(-1000, 1000), coordinates["north"], point(1000, 1000),
                coordinates["right"], point(1000, -1000), point(-1000, -1000), coordinates["left"]]
        path = [coordinates[code] for code in ("first", "left", "right", "last")]
        lines = {"M15": holistic_network._physical_line(ring, ["left", "north", "right"], stations, [], "fixture",
                                                       loop=True),
                 "L": holistic_network._physical_line(path, ["first", "left", "right", "last"], stations, [], "fixture")}
        for code, line in lines.items():
            for station in line["station_ids"]:
                stations[station]["lines"].append(code)
        network = {"lines": lines, "stations": stations, "transfers": []}
        ring_corridors._refresh_transfers(network)
        revised, actions, held = layout._core_turnbacks(network, [], set(stations))
        self.assertEqual(held, {})
        self.assertEqual(actions[0]["retained_branch_ids"], ["L", "L-outer"])
        self.assertEqual(set(revised["stations"]), set(stations))
        self.assertEqual(revised["lines"]["L"]["station_ids"], ["first", "left"])
        self.assertEqual(revised["lines"]["L-outer"]["station_ids"], ["right", "last"])


if __name__ == "__main__":
    unittest.main()

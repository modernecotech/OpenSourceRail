"""Check the mapped junction and close-station rules for the Baghdad alternatives."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import numpy as np

from . import holistic_network as hn, spaced_ring_layouts as layouts
from .spaced_ring_comparison import _without_inner
from .test_network_trunks import fixture as trunks_fixture


def fixture():
    points = {"start": (0, 0), "keeper": (1000, 0), "near": (1090, 0), "next": (1190, 0),
              "barrier": (1260, 0), "end": (2800, 0), "duplicate": (1000, 0), "north": (1600, 1000)}
    stations = {stop: {"name": stop, "basis": "Fixture", "lines": [],
                       "coordinates": (np.array([44.4, 33.3]) + point / hn.LOCAL_METRES).tolist()}
                for stop, point in points.items()}
    lines = {}
    for code, stops in {"A": ["start", "keeper", "near", "next", "barrier", "end"],
                        "B": ["start", "duplicate", "north"]}.items():
        lines[code] = hn._physical_line([stations[stop]["coordinates"] for stop in stops], stops,
                                        stations, [code], "Fixture") | {"name": code}
        for stop in stops:
            stations[stop]["lines"].append(code)
    network = {"lines": lines, "stations": stations, "station_site_links": [],
               "transfers": [{"id": "start", "station_ids": ["start"], "lines": ["A", "B"]}]}
    network["topology"] = hn.validate(network)
    return hn._identity(network)


class SpacedRingLayoutTests(unittest.TestCase):
    def test_each_absorbed_call_has_a_direct_walk_to_the_final_site(self):
        network = fixture()
        before = deepcopy(network)
        barrier = network["stations"]["barrier"]["coordinates"]

        def path(first, second):
            if first == barrier:
                return None
            return layouts.network_station_sites._metres(first, second), [first, second]

        context = {"layers": {"water": []}}
        with patch.object(layouts.network_station_sites, "_street_paths", return_value=(None, path)):
            candidate, audit = layouts._consolidate(network, None, context, {"keeper"})
        self.assertEqual(network, before)
        self.assertEqual(set(audit["clusters"]["keeper"]), {"near", "next", "duplicate"})
        self.assertIn("barrier", candidate["stations"])
        self.assertEqual(candidate["stations"]["keeper"]["lines"], ["A", "B"])
        self.assertEqual(candidate["topology"], hn.validate(candidate))
        self.assertEqual([row["geometry"] for row in candidate["lines"].values()],
                         [row["geometry"] for row in before["lines"].values()])
        for action in audit["actions"]:
            original = before["stations"][action["retired_station_id"]]["coordinates"]
            self.assertEqual(action["replacement_walk_geometry"][0][0], original)
            self.assertEqual(action["replacement_walk_geometry"][0][-1], before["stations"]["keeper"]["coordinates"])

    def test_eastern_junction_pairs_only_compatible_source_intervals(self):
        network = trunks_fixture()
        result, action = layouts._join(network, "M06", "M03", layouts.EAST_JUNCTION,
                                       first_endpoint=0, second_endpoint=1)
        self.assertEqual(result["station_ids"], ["Yusufiyah", "continuing", layouts.EAST_JUNCTION, "Shaoura"])
        self.assertEqual(action["source_directions"], {"M06": 1, "M03": 1})
        with self.assertRaisesRegex(ValueError, "30°"):
            layouts._join(trunks_fixture(north=(4_000, 2_000)), "M06", "M03", layouts.EAST_JUNCTION,
                          first_endpoint=0, second_endpoint=1)

    def test_withdrawal_rejects_protected_calls(self):
        network = fixture()
        with self.assertRaisesRegex(ValueError, "Protected stations would close"):
            layouts._apply(network, layouts.Layout("Withdraw one", withdrawn=("B",)), set(), {"north"})

    def test_paired_control_prunes_walks_to_withdrawn_ring_stops(self):
        network = fixture()
        inner = network["lines"]["M15"] = network["lines"].pop("B")
        inner["geometry"].append(inner["geometry"][0])
        inner.update(loop=True, one_way_km=hn.Track(inner["geometry"]).km)
        for stop in inner["station_ids"]:
            station = network["stations"][stop]
            station["lines"] = ["M15" if code == "B" else code for code in station["lines"]]
        network["transfers"][0]["lines"] = ["A", "M15"]
        coordinates = [network["stations"][stop]["coordinates"] for stop in ("near", "duplicate")]
        network["station_site_links"] = [{
            "id": "street", "station_ids": ["near", "duplicate"], "walks_m": [90, 90],
            "geometry": [coordinates, coordinates[::-1]],
        }]
        network["source_sha256"] = {}
        network["topology"] = hn.validate(network)
        hn._identity(network)
        control = _without_inner(network)
        self.assertEqual(control["lines"]["A"], network["lines"]["A"])
        self.assertNotIn("duplicate", control["stations"])
        self.assertEqual(control["station_site_links"], [])
        self.assertEqual(len(network["station_site_links"]), 1)
        self.assertEqual(control["paired_ring_control"]["source_evaluation_id"], network["evaluation_id"])


if __name__ == "__main__":
    unittest.main()

"""Check whole-line withdrawal and the mapped eastern junction experiment."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import numpy as np

from . import network_trunks as trunks
from .holistic_network import LOCAL_METRES, _identity, _physical_line, validate
from .residential_layouts import LineEdit


def fixture(north=(6_000, 2_000)):
    points = {
        "Airport-00": (0, -1000), "Tahrir": (0, 0), "Karkh": (1000, 0),
        "Mansour": (2000, 0), "University": (2000, -1500), "Shorja": (2000, 1500),
        "Yusufiyah": (0, 1000), "continuing": (3000, 1000), "Diyala": (6000, 1000),
        "west": (2000, -2100), "parallel": (3200, 550), "Shaoura": north,
        "G04-only": (1400, 1000), trunks.EAST_JUNCTION: (4000, 1000),
    }
    stations = {code: {"name": code, "coordinates": (np.array([44.4, 33.3]) + point / LOCAL_METRES).tolist(),
                       "lines": []}
                for code, point in points.items()}
    routes = {
        "C1": ["Airport-00", "Tahrir", "Karkh", "Mansour"],
        "C2": ["University", "Mansour", "Shorja"],
        "M06": ["Yusufiyah", "continuing", trunks.EAST_JUNCTION, "Diyala"],
        "M03": ["west", "University", "parallel", trunks.EAST_JUNCTION, "Shaoura"],
        "G04": ["Karkh", "G04-only", "continuing"],
        "M04": ["Yusufiyah", "Tahrir", "University"],
    }
    lines = {}
    for code, stop_ids in routes.items():
        path = [stations[stop]["coordinates"] for stop in stop_ids]
        lines[code] = _physical_line(path, stop_ids, stations, [code], "Fixture") | {"name": code}
        for stop in stop_ids:
            stations[stop]["lines"].append(code)
    transfers = [{"id": stop, "station_ids": [stop], "lines": sorted(station["lines"])}
                 for stop, station in stations.items() if len(station["lines"]) > 1]
    record = {"lines": lines, "stations": stations, "transfers": transfers}
    record["topology"] = validate(record)
    return _identity(record)


class TrunkSkeletonTests(unittest.TestCase):
    def test_withdrawal_rebuilds_membership_and_keeps_airport_and_central_anchors(self):
        prior = fixture()
        untouched = deepcopy(prior)
        packages = {"trial": trunks.Skeleton("Whole branch", "Use the two trunks.", withdrawn=("G04",))}
        with patch.object(trunks, "SKELETONS", packages):
            option = trunks.alternatives(prior)["trial"]
            prior_station = "G04-only"
            rejected = trunks.alternatives(prior, protected_stations=[prior_station])["trial"]

        network = option["network"]
        self.assertEqual(prior, untouched)
        self.assertEqual(network["lines"]["C1"], prior["lines"]["C1"])
        self.assertEqual(validate(network), network["topology"])
        self.assertNotIn("G04", network["lines"])
        self.assertNotIn(prior_station, network["stations"])
        self.assertEqual(option["actions"][0]["closed_stations"], [prior_station])
        self.assertEqual(network["stations"]["Karkh"]["lines"], ["C1"])
        self.assertEqual(network["layout_revision"]["parent_candidate_id"], prior["candidate_id"])
        self.assertFalse(network["physical_accepted"])
        self.assertIsNone(rejected["network"])
        self.assertIn(prior_station, rejected["rejection_reason"])

    def test_reassigned_east_branches_preserve_stops_and_withdraw_parallel_segment(self):
        prior = fixture()
        packages = {"trial": trunks.Skeleton(
            "One eastern junction", "Use the retained northeast and north branches.",
            branches=(LineEdit("M03", "End the western branch at M04.", end_station="University"),),
            eastern_splice=True,
        )}
        with patch.object(trunks, "SKELETONS", packages):
            option = trunks.alternatives(prior)["trial"]
            invalid = trunks.alternatives(fixture(north=(4000, 2000)))["trial"]

        network = option["network"]
        self.assertEqual(network["lines"]["M06"]["station_ids"],
                         ["Yusufiyah", "continuing", trunks.EAST_JUNCTION, "Shaoura"])
        self.assertEqual(network["lines"]["B06"]["station_ids"], [trunks.EAST_JUNCTION, "Diyala"])
        self.assertEqual(network["lines"]["M03"]["station_ids"], ["west", "University"])
        self.assertEqual(network["stations"][trunks.EAST_JUNCTION]["lines"], ["B06", "M06"])
        self.assertEqual(network["stations"]["Shaoura"]["coordinates"], prior["stations"]["Shaoura"]["coordinates"])
        self.assertNotIn("parallel", network["stations"])
        self.assertAlmostEqual(sum(row["removed_route_km"] for row in option["actions"]),
                               option["removed_route_km"], places=2)
        self.assertEqual(network["topology"], validate(network))
        self.assertIsNone(invalid["network"])
        self.assertIn("30°", invalid["rejection_reason"])


if __name__ == "__main__":
    unittest.main()

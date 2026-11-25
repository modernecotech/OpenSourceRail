"""Exercise retained-chainage trims and their walking-access accounting."""

import unittest

import numpy as np

from . import residential_layouts as layouts
from .holistic_access import Population
from .holistic_network import _identity, _physical_line, validate


def fixture():
    coordinates = {
        "first": [44.30, 33.30], "south": [44.32, 33.30], "east": [44.34, 33.30],
        "north": [44.34, 33.32], "west": [44.30, 33.32], "central": [44.33, 33.31],
        "tail": [44.33, 33.33],
    }
    stations = {stop: {"name": stop, "coordinates": point, "lines": []}
                for stop, point in coordinates.items()}
    lines = {}
    for code, order in (("ring", ["first", "south", "east", "north", "west"]),
                        ("inner", ["south", "central", "north", "tail"])):
        loop = code == "ring"
        path = [coordinates[stop] for stop in order + (order[:1] if loop else [])]
        lines[code] = _physical_line(path, order, stations, [code], "Fixture", loop)
        for stop in order:
            stations[stop]["lines"].append(code)
    transfers = [{"id": stop, "station_ids": [stop], "lines": sorted(station["lines"])}
                 for stop, station in stations.items() if len(station["lines"]) > 1]
    record = {"stations": stations, "lines": lines, "transfers": transfers}
    record["topology"] = validate(record)
    return _identity(record)


class ResidentialLayoutsTests(unittest.TestCase):
    def test_clip_ends_at_the_retained_chainage_and_revises_identity(self):
        prior = fixture()
        action = layouts.LineEdit("inner", "Use the shared northern stop.", end_station="north")
        network, changes = layouts.apply_edits(prior, [action])

        self.assertEqual(validate(network), network["topology"])
        self.assertEqual(network["lines"]["ring"], prior["lines"]["ring"])
        self.assertEqual(network["lines"]["inner"]["station_ids"], ["south", "central", "north"])
        self.assertEqual(network["lines"]["inner"]["geometry"][-1], prior["stations"]["north"]["coordinates"])
        self.assertEqual(network["lines"]["inner"]["station_chainage_km"]["north"],
                         network["lines"]["inner"]["one_way_km"])
        self.assertEqual(changes[0]["closed_stations"], ["tail"])
        self.assertIn("tail", prior["stations"])
        self.assertNotEqual(network["candidate_id"], prior["candidate_id"])
        self.assertEqual(layouts.apply_edits(prior, [action])[0]["evaluation_id"], network["evaluation_id"])

    def test_open_orbital_retains_the_wraparound_section(self):
        prior = fixture()
        network, changes = layouts.apply_edits(prior, [layouts.LineEdit("ring", "Keep the western arc.", "north", "south")])

        ring = network["lines"]["ring"]
        self.assertFalse(ring["loop"])
        self.assertEqual(ring["station_ids"], ["north", "west", "first", "south"])
        self.assertEqual(changes[0]["closed_stations"], ["east"])
        self.assertEqual(len(changes[0]["retained_source_chainage_km"]), 2)
        self.assertEqual(network["topology"]["transfer_stations"], 2)
        self.assertEqual(validate(network), network["topology"])

    def test_withdrawal_preserves_surviving_station_calls_and_rebuilds_transfers(self):
        prior = fixture()
        network, changes = layouts.apply_edits(prior, [layouts.LineEdit("ring", "Withdraw the loop.")])

        self.assertEqual(network["transfers"], [])
        self.assertEqual(network["stations"]["south"]["lines"], ["inner"])
        self.assertEqual(changes[0]["retained_station_calls_on_other_lines"], ["south", "north"])
        self.assertEqual(network["topology"]["connected_components"], 1)

    def test_withdrawal_rejects_a_bypassed_line_with_no_remaining_connection(self):
        prior = fixture()
        stations = prior["stations"]
        stations["spur"] = {"name": "spur", "coordinates": [44.35, 33.30], "lines": ["spur"]}
        stations["east"]["lines"].append("spur")
        prior["lines"]["spur"] = _physical_line([stations[stop]["coordinates"] for stop in ("east", "spur")],
                                                  ["east", "spur"], stations, ["spur"], "Fixture")
        prior["transfers"].append({"id": "east", "station_ids": ["east"], "lines": ["ring", "spur"]})
        prior["topology"] = validate(prior)
        _identity(prior)
        with self.assertRaisesRegex(ValueError, "Disconnected passenger lines"):
            layouts.apply_edits(prior, [layouts.LineEdit("ring", "Withdraw the loop.")])

    def test_trim_cannot_remove_a_protected_station_or_turn_back_at_a_solo_call(self):
        prior = fixture()
        with self.assertRaisesRegex(ValueError, "Protected stations removed"):
            layouts.apply_edits(prior, [layouts.LineEdit("inner", "Trim.", end_station="north")],
                                protected_stations=["tail"])
        with self.assertRaisesRegex(ValueError, "retained interchange"):
            layouts.apply_edits(prior, [layouts.LineEdit("inner", "Trim.", end_station="central")])

    def test_walk_losses_are_threshold_specific_and_count_each_native_pixel_once(self):
        population = Population({}, np.array([[44.3, 33.3], [44.3, 33.3], [44.4, 33.4], [44.4, 33.4]]),
                                np.array([5., 12., 30., 100.]), np.zeros(4), np.arange(4),
                                np.array([[0., 0.], [10., 10.], [3_000., 3_000.], [3_010., 3_010.]]))
        summary = layouts._housing_access(population, np.array([700., 700., 950., np.inf]),
                                         np.array([900., 1_250., 1_250., np.inf]))

        self.assertEqual(summary["800"]["estimated_residents_losing_walk_access"], 17)
        self.assertEqual(summary["1200"]["estimated_residents_losing_walk_access"], 42)
        self.assertEqual(summary["1200"]["estimated_residents_within_walk"], 5)
        self.assertEqual(summary["1200"]["largest_loss_cells_approx_1_km"][0]["estimated_residents"], 30)


if __name__ == "__main__":
    unittest.main()

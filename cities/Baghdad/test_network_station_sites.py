"""Check station-site consolidation against track and street topology."""

from copy import deepcopy
import unittest

import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree

from . import central_access, holistic_network, network_station_sites

EMPTY_WATER = {"layers": {"water": []}}
PROVISIONAL = "Population-ranked street-access infill on this alignment"


def point(x, y):
    return (np.asarray([44.4, 33.3]) + np.asarray([x, y]) / holistic_network.LOCAL_METRES).tolist()


def streets(points, edges):
    coordinates = [point(x, y) for x, y in points]
    longitude, latitude = np.asarray(coordinates).T
    raw = {"lon": longitude, "lat": latitude}
    starts, ends, metres = zip(*edges, strict=True)
    matrix = csr_matrix((metres, (starts, ends)), shape=(len(points), len(points)))
    return raw, matrix, np.arange(len(points)), cKDTree(central_access._points(coordinates)), {}


def crossing_fixture(a_call=(900, 0), b_call=(1000, 75)):
    positions = {"A0": (0, 0), "A1": a_call, "B0": (1000, -1000), "B1": b_call, "Hub": (2500, 0)}
    stops = {code: {"coordinates": point(*position), "name": code,
                    "basis": PROVISIONAL if code.endswith("1") else "named control",
                    "lines": ["A", "B"] if code == "Hub" else [code[0]]}
             for code, position in positions.items()}
    routes = {
        "A": ([(0, 0), (2500, 0)], ["A0", "A1", "Hub"]),
        "B": ([(1000, -1000), (1000, 1000), (2500, 1000), (2500, 0)], ["B0", "B1", "Hub"]),
    }
    lines = {code: holistic_network._physical_line([point(*coord) for coord in geometry], ids,
                                                    stops, [code], "fixture")
             for code, (geometry, ids) in routes.items()}
    return {"stations": stops, "lines": lines, "transfers": [
        {"id": "Hub", "station_ids": ["Hub"], "lines": ["A", "B"]}]}


class StationSitesTests(unittest.TestCase):
    def test_provisional_platforms_relocate_to_actual_crossing(self):
        base = crossing_fixture()
        original = deepcopy(base)
        graph = streets([(900, 0), (1000, 0), (1000, 75)], [(0, 1, 100), (1, 2, 75)])
        revised, audit = network_station_sites.consolidate(base, graph=graph, context=EMPTY_WATER)
        action, = audit["actions"]
        self.assertEqual(action["basis"], "eligible call moved to mapped track crossing")
        self.assertEqual(action["kept_station_id"], "A1")
        self.assertEqual(action["source_station_ids"], ["A1", "B1"])
        self.assertEqual(revised["stations"]["A1"]["lines"], ["A", "B"])
        self.assertEqual(revised["stations"]["A1"]["source_stations"], ["A1", "B1"])
        self.assertAlmostEqual(action["platforms"]["A"]["chainage_km"], 1)
        self.assertAlmostEqual(action["platforms"]["B"]["chainage_km"], 1)
        self.assertEqual({code: row["geometry"] for code, row in revised["lines"].items()},
                         {code: row["geometry"] for code, row in base["lines"].items()})
        self.assertEqual(base, original)
        self.assertEqual(revised["topology"]["connected_components"], 1)

    def test_directed_walking_links_preserve_calls_and_route_geometry(self):
        base = crossing_fixture()
        graph = streets([(900, 0), (1000, 0), (1000, 75)],
                        [(0, 1, 101), (1, 2, 76), (2, 0, 190)])
        revised, audit = network_station_sites.consolidate(
            base, graph=graph, context=EMPTY_WATER, protected_stations=("A1",))
        self.assertFalse(audit["actions"])
        link, = revised["station_site_links"]
        self.assertEqual(link["station_ids"], ["A1", "B1"])
        self.assertEqual(link["walks_m"], [177, 190])
        self.assertEqual(link["geometry"][0], [point(900, 0), point(1000, 0), point(1000, 75)])
        self.assertEqual(link["geometry"][1], [point(1000, 75), point(900, 0)])
        self.assertEqual(revised["lines"], base["lines"])

    def test_single_direction_path_leaves_separate_unlinked_calls(self):
        graph = streets([(900, 0), (1000, 0), (1000, 75)], [(0, 1, 101), (1, 2, 76)])
        revised, audit = network_station_sites.consolidate(
            crossing_fixture(), graph=graph, context=EMPTY_WATER, protected_stations=("A1",))
        self.assertFalse(revised["station_site_links"])
        self.assertFalse(audit["actions"])
        self.assertTrue(any(row["station_ids"] == ["A1", "B1"] for row in audit["held"]))

    def test_water_across_snap_connector_blocks_link(self):
        view = {"layers": {"water": [{"geometry": {"type": "Polygon", "coordinates": [
            [point(919, -5), point(921, -5), point(921, 5), point(919, 5), point(919, -5)]]}}]}}
        graph = streets([(940, 0), (1000, 75)], [(0, 1, 110), (1, 0, 110)])
        revised, audit = network_station_sites.consolidate(
            crossing_fixture(), graph=graph, context=view, protected_stations=("A1",))
        self.assertFalse(revised["station_site_links"])
        self.assertFalse(audit["actions"])

    def test_exact_co_location_keeps_line_chainages(self):
        base = crossing_fixture((1000, 0), (1000, 0))
        graph = streets([(1000, 0)], [(0, 0, 1)])
        revised, audit = network_station_sites.consolidate(base, graph=graph, context=EMPTY_WATER,
                                                           protected_stations=("B1",))
        action, = audit["actions"]
        self.assertEqual(action["basis"], "co-located mapped platforms")
        self.assertEqual(action["kept_station_id"], "B1")
        self.assertEqual(revised["lines"]["A"]["station_chainage_km"]["B1"],
                         base["lines"]["A"]["station_chainage_km"]["A1"])
        self.assertEqual(revised["lines"]["B"]["station_chainage_km"]["B1"],
                         base["lines"]["B"]["station_chainage_km"]["B1"])

    def test_same_line_pruning_keeps_protected_terminal_and_source_geometry(self):
        base = crossing_fixture((200, 0))
        graph = streets([(0, 0), (200, 0)], [(0, 1, 200), (1, 0, 200)])
        revised, audit = network_station_sites.consolidate(base, graph=graph, context=EMPTY_WATER)
        action, = audit["actions"]
        self.assertEqual(action["kind"], "retired_close_call")
        self.assertEqual(action["source_station_ids"], ["A0", "A1"])
        self.assertEqual(revised["lines"]["A"]["station_ids"], ["A0", "Hub"])
        self.assertEqual(revised["lines"]["A"]["geometry"], base["lines"]["A"]["geometry"])

    def test_consecutive_provisional_calls_have_deterministic_replacement(self):
        base = crossing_fixture((450, 0))
        base["stations"]["A2"] = {"coordinates": point(855, 0), "name": "Second infill",
                                   "basis": PROVISIONAL, "lines": ["A"]}
        holistic_network._add(base["lines"]["A"], "A2", .855)
        graph = streets([(450, 0), (855, 0)], [(0, 1, 407), (1, 0, 408)])
        revised, audit = network_station_sites.consolidate(base, graph=graph, context=EMPTY_WATER)
        action, = audit["actions"]
        self.assertEqual(action["source_station_ids"], ["A1", "A2"])
        self.assertEqual(action["replacement_walks_m"], [407, 408])
        self.assertEqual(revised["lines"]["A"]["station_ids"], ["A0", "A1", "Hub"])
        self.assertEqual(revised["lines"]["A"]["station_chainage_km"]["A1"],
                         base["lines"]["A"]["station_chainage_km"]["A1"])

        over_limit = streets([(450, 0), (855, 0)], [(0, 1, 407), (1, 0, 451)])
        revised, audit = network_station_sites.consolidate(base, graph=over_limit, context=EMPTY_WATER)
        self.assertFalse(audit["actions"])
        self.assertEqual(revised["lines"]["A"]["station_ids"], ["A0", "A1", "A2", "Hub"])

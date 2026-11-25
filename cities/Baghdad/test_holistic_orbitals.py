"""Check the inner orbital against retained stations, streets and water."""

import unittest

import numpy as np

from .holistic_network import INPUTS, Track, dry_points, evaluate, insert_stations, read, validate, walking_graph
from .holistic_orbitals import LINE_ID, _water_crossings, add_inner_orbit


class OrbitalTests(unittest.TestCase):
    def test_retained_inner_alignment_closes_and_transfers_on_both_banks(self):
        graph = walking_graph()
        context = read(INPUTS[-1])
        base = evaluate(graph)
        revised, evidence = add_inner_orbit(base, graph, context, southern_way=626727315)
        self.assertEqual(evidence["status"], "gis corridor and access screen passed")
        self.assertEqual(revised["lines"]["M09"], base["lines"]["M09"])
        self.assertNotIn(LINE_ID, base["lines"])
        self.assertEqual(validate(revised), revised["topology"])
        inner = revised["lines"][LINE_ID]
        self.assertTrue(inner["loop"])
        self.assertEqual(inner["geometry"][0], inner["geometry"][-1])
        self.assertAlmostEqual(inner["one_way_km"], 41.1288067)
        self.assertEqual(evidence["transfers_by_bank"], {"east": 3, "west": 2})
        self.assertEqual({row["line_id"] for row in evidence["transfer_sites"]},
                         {"M01", "C1", "M05", "M08", "M02"})
        self.assertEqual({row["name"] for row in evidence["mapped_water_crossings"]},
                         {"Al-A'imma Bridge", "Al-Jadriya Bridge"})
        self.assertTrue(dry_points([revised["stations"][stop]["coordinates"]
                                    for stop in inner["station_ids"]], context).all())
        self.assertGreaterEqual(np.diff([*(inner["station_chainage_km"][stop] for stop in inner["station_ids"]),
                                        inner["one_way_km"]]).min(), .65 - 1e-7)
        for transfer in evidence["transfer_sites"]:
            stop = transfer["station_id"]
            self.assertIn(stop, revised["lines"][transfer["line_id"]]["station_ids"])
            self.assertIn(stop, inner["station_ids"])
        self.assertFalse(revised["physical_accepted"])
        self.assertFalse(revised["operating_timetable_validated"])
        self.assertEqual(evidence["inner_length_share_within_350_m_of_outer"], 0.)

        populated = insert_stations(base, [{
            "line_id": "C1", "chainage_km": 31.2, "id": "C1-infill-31200",
            "name": "C1 infill · km 31.2", "basis": "Population-ranked street-access infill on this alignment",
        }])
        relocated, comparison = add_inner_orbit(populated, graph, context, southern_way=626727315)
        self.assertEqual(comparison["road_geometry_sha256"], evidence["road_geometry_sha256"])
        self.assertEqual(comparison["relocated_infill_stations"], 1)
        transfer = next(row for row in comparison["transfer_sites"] if row["line_id"] == "C1")
        self.assertEqual(transfer["station_id"], "C1-infill-31200")
        self.assertAlmostEqual(transfer["relocated_infill"]["shift_on_retained_line_m"], 282.4)
        self.assertEqual(relocated["stations"]["C1-infill-31200"]["lines"], ["C1", LINE_ID])
        self.assertEqual(populated["stations"]["C1-infill-31200"]["lines"], ["C1"])

        unchanged, failure = add_inner_orbit(base, graph, context, southern_way=4082481)
        self.assertIs(unchanged, base)
        self.assertEqual(failure["failed_hypotheses"][0]["southern_way"], 4082481)

    def test_untagged_road_crossing_at_a_vertex_is_rejected(self):
        points = [(44., 33.), (44.01, 33.), (44.02, 33.)]
        track = Track(points)
        context = {"layers": {"water": [{"geometry": {
            "type": "LineString", "coordinates": [[44.01, 32.99], [44.01, 33.01]],
        }}]}}
        edges = {a: {b: (1., 101, False)} for a, b in zip(points, points[1:])}
        with self.assertRaisesRegex(ValueError, "lacks a retained carriageway bridge tag"):
            _water_crossings(track, edges, context)

"""Independent contract checks for the joint-free civil research packet."""
from __future__ import annotations

import unittest

from engineering.design_search.simple_span_prototype import ROOT, OUTPUT, build, encoded


class SimpleSpanPrototypeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build()

    def test_published_packet_is_current_and_candidate_is_separate(self):
        self.assertEqual((ROOT / OUTPUT).read_bytes(), encoded(self.result))
        row = self.result
        self.assertNotEqual(row["physical_candidate_id"], row["jointed_20m_comparator_counts"]["physical_candidate_id"])
        self.assertEqual(row["normal_load"]["physical_civil_component_id"], row["crowd_control_load"]["physical_civil_component_id"])
        self.assertFalse(row["selected_reference_changed"])

    def test_crowd_control_and_independent_envelope(self):
        row = self.result
        self.assertAlmostEqual(row["normal_accounted_mass_kg_per_car"], 25071.998134341986, places=5)
        self.assertAlmostEqual(row["crowd_control_accounted_mass_kg_per_car"], 33621.998134341986, places=5)
        self.assertAlmostEqual(row["crowd_control_load"]["maximum_live_moment_Nm"], row["independent_crowd_moving_load_check"]["maximum_live_moment_Nm"], places=6)
        self.assertEqual(len(row["crowd_control_load"]["moving_load_local_envelope"]), 41)
        self.assertIsNone(row["load_model"]["maximum_support_shear_N"])
        self.assertFalse(row["physical_accepted"])

    def test_quantities_and_qualification_holds(self):
        row = self.result
        quantities = row["straight_two_track_2km_quantities"]
        self.assertEqual((quantities["newly_designed_10m_beams"], quantities["one_piece_lifts"], quantities["independent_pier_and_foundation_supports"], quantities["bearing_units_hypothesis"]), (400, 400, 402, 1600))
        self.assertEqual(quantities["midspan_structural_joints"], 0)
        self.assertIsNone(row["single_installed_price_usd"])
        self.assertIsNone(row["foundation"]["site_ground_and_settlement"])
        self.assertEqual(row["native_solver"]["jobs_executed"], 0)
        self.assertFalse(row["manufacturing_release"])


if __name__ == "__main__":
    unittest.main()

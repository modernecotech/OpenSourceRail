"""Independent checks using slice integration, static equilibrium and source replay."""
import json
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from develop_civil import DIR, evaluate, hash_file
from section_drawing import drawing


class CivilSectionTests(unittest.TestCase):
    def setUp(self):
        self.results = evaluate()

    def test_published_outputs_reproduce(self):
        self.assertEqual(self.results, json.loads((DIR/"section-results.json").read_bytes()))
        self.assertEqual(drawing(), (DIR/"station-and-box.svg").read_text())
        self.assertEqual(ET.fromstring(drawing()).tag, "{http://www.w3.org/2000/svg}svg")

    def test_stale_parent_evaluator_is_rejected(self):
        with patch("develop_civil.hash_file", side_effect=lambda p:
                   "stale" if p.name == "develop.py" else hash_file(p)):
            with self.assertRaisesRegex(ValueError, "Stale mechanical parent: develop.py"):
                evaluate()

    def test_track_dead_moment_from_integrated_slices(self):
        track = self.results["track"]
        weight = 0
        moment_left = 0
        for i in range(1000):
            x = (i+0.5)*0.01
            area = 2*1.4 if x < 0.55 or x > 9.45 else 2*1.4 - 1.64*1
            load = (area*25+3)*0.01
            weight += load
            moment_left += max(0,5-x)*load
        self.assertAlmostEqual(track["dead_end_reaction_kn"], weight/2)
        self.assertAlmostEqual(track["dead_midspan_moment_knm"], weight/2*4.75 - moment_left)
        self.assertLess(track["stock_lift_hogging_knm"], 0)
        self.assertGreater(track["pier_gravity_screen"]["uniform_soil_contact_pressure_kpa"], 200)

    def test_panel_loads_close_on_interior_bent(self):
        panel = self.results["platform"]
        self.assertAlmostEqual(8*panel["panel_end_reaction_kn"]+25*panel["head_volume_m3"],
                               2*panel["symmetric_column_reaction_kn"])
        self.assertEqual(panel["panel_count_template"], 100)
        self.assertGreater(panel["panel_positive_moment_upper_knm"], 0)
        self.assertLess(panel["head_column_hogging_moment_knm"], 0)

"""Check that GIS rail levels retain the Airport route and reach the motion input."""

from itertools import pairwise
import json
import unittest

from . import airport_alignment, site_layers, site_profile


class SiteProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.horizontal = airport_alignment.evaluate()
        cls.layers = site_layers.load_site_layers(alignment=cls.horizontal)

    def test_published_samples_produce_level_platforms_and_matching_stops(self):
        profile = site_profile.derive_site_profile(self.layers, self.horizontal)
        with self.subTest("profile-level clearance"):
            self.assertGreaterEqual(min(row["soffit_height_m"] for row in profile["samples"]), 6 - 1e-9)
            self.assertLessEqual(profile["maximum_absolute_grade_pct"], 0.6 + 1e-8)
            self.assertGreater(profile["maximum_absolute_grade_pct"], 0.0)
        supplied = profile["alignment_input"]
        levels = airport_alignment.rail_level_profile(
            supplied["geometry"]["coordinates"],
            supplied["vertical_profile"]["datum"],
            supplied["vertical_profile"]["elevations_m"],
        )
        for start, end in profile["platform_grade_limits_m"]:
            self.assertAlmostEqual(end - start, 140)
            for (left, right), slope in zip(pairwise(levels["chainages_m"]), levels["grades_pct"], strict=True):
                if left >= start - 1e-6 and right <= end + 1e-6:
                    self.assertAlmostEqual(slope, 0.0)
        for row, chainage in zip(supplied["stops"], self.horizontal["chainages_km"], strict=True):
            self.assertAlmostEqual(levels["chainages_m"][row["vertex"]] / 1000, chainage)
        self.assertEqual(json.loads(json.dumps(supplied, allow_nan=False)), supplied)

    def test_rejects_mismatched_or_sparse_input(self):
        with self.assertRaisesRegex(ValueError, "different horizontal alignment"):
            site_profile.derive_site_profile({**self.layers, "alignment_id": "another-route"}, self.horizontal)
        with self.assertRaisesRegex(ValueError, "gaps"):
            site_profile.derive_site_profile({**self.layers, "samples": self.layers["samples"][::10]}, self.horizontal)

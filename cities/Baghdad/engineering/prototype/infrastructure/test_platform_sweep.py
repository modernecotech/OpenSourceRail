"""Independent checks of the sign convention at the station interface."""
from math import isclose
from unittest import TestCase

from .platform_sweep import HERE, radial_gaps, report


class PlatformSweepTest(TestCase):
    def test_bogie_chord_and_platform_sides(self):
        # A 6 m pivot half-spacing on a 10 m curve puts the chord at 8 m.
        self.assertEqual(radial_gaps(10, 6, 1, 0.5, 0), (-1.5, 2.5))
        inner, outer = radial_gaps(10, 6, 1, 0.5, 12)
        self.assertTrue(isclose(inner, 193 ** 0.5 - 8.5))
        self.assertEqual(outer, -3.5)
        self.assertEqual(radial_gaps(10, 6, 1, 0.5, -12), (inner, outer))
        with self.assertRaises(ValueError):
            radial_gaps(6, 6, 1, 0.5, 0)

    def test_published_enquiry(self):
        self.assertEqual(report(), (HERE / 'PLATFORM-SWEEP.md').read_text())

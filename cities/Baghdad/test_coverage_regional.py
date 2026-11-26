"""Topology screens for regional access through the outer orbital."""

import numpy as np
from shapely import box

from cities.Baghdad import coverage_regional as regional, holistic_network as rail


def track(*points):
    return rail.Track(np.array(points) / rail.LOCAL_METRES)


def test_long_spoke_has_one_contour_departure_and_short_spoke_uses_distal_terminus():
    outer = box(-4000, -4000, 4000, 4000)
    contour = outer.buffer(2500)
    point, basis = regional.departure(track((4000, 0), (12000, 0)), outer, contour)
    assert np.allclose(point, [(6500, 0)])
    assert basis == "2.5 km suburban contour"
    point, basis = regional.departure(track((4000, 0), (6000, 0)), outer, contour)
    assert np.allclose(point, [(6000, 0)])
    assert basis == "Suburban terminus before the contour"


def test_attaching_only_near_an_orbital_or_departing_through_its_interior_fails():
    outer = box(-4000, -4000, 4000, 4000)
    contour = outer.buffer(2500)
    assert regional.departure(track((4300, 0), (12000, 0)), outer, contour) is None
    assert regional.departure(track((4000, 0), (-12000, 0)), outer, contour) is None
    assert regional.departure(track((4000, 0), (8000, 2500), (5000, 3500), (8000, 4000)), outer, contour) is None

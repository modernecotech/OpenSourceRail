from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from osr_geo.rasterize import GridRef, build_water_mask, build_cost_surface
from osr_osm.fetcher import BBox, CityOSM, OverpassError, _parse_overpass


def grid():
    return GridRef(height=12, width=12, cell_m=1, lat0=6,
                   bbox_south=0, bbox_west=0, bbox_north=12, bbox_east=12,
                   m_per_deg_lat=1, m_per_deg_lon=1)


def test_points_just_outside_the_grid_are_not_truncated_into_its_first_cell():
    assert grid().latlon_to_rc(12.2,-.2)==(-1,-1)
    assert grid().latlon_to_rc(11.8,.2)==(0,0)


def member(ref, role, points):
    return dict(type="way", ref=ref, role=role,
                geometry=[dict(lat=lat, lon=lon) for lat, lon in points])


def relation():
    return dict(type="relation", id=9072, tags={"natural": "water", "type": "multipolygon"}, members=[
        # Out of order, reversed fragments; a separate second outer.
        member(4, "outer", [(10, 1), (10, 6)]),
        member(1, "outer", [(4, 1), (4, 6)]),
        member(2, "outer", [(10, 6), (4, 6)]),
        member(3, "outer", [(4, 1), (10, 1)]),
        member(5, "inner", [(6, 3), (6, 4), (8, 4), (8, 3), (6, 3)]),
        member(6, "outer", [(2, 8), (2, 10), (4, 10), (4, 8), (2, 8)]),
    ])


def test_relation_member_geometry_restores_lake_and_preserves_island():
    city = _parse_overpass({"elements": [relation()]}, BBox(0, 0, 12, 12), "fixture")
    assert len(city.water[0]["outer_rings"]) == 2
    assert len(city.water[0]["inner_rings"]) == 1
    water = build_water_mask(city, grid())
    assert water[3, 2] == 100  # lake, formerly absent
    assert water[5, 3] == 0  # island inside lake
    assert water[9, 9] == 100  # separate outer polygon
    assert water[1, 11] == 0
    cost = build_cost_surface(city, grid())
    assert cost[3, 2] >= 80
    assert cost[5, 3] < 80


def test_missing_or_unclosed_relation_members_cannot_silently_pass():
    element = relation()
    element["members"] = element["members"][1:]
    with pytest.raises(OverpassError, match="Unclosed"):
        _parse_overpass({"elements": [element]}, BBox(0, 0, 12, 12), "fixture")
    city = CityOSM(BBox(0, 0, 12, 12), "fixture", 0, water=[dict(id=9072, nodes=[])])
    with pytest.raises(ValueError, match="Missing water geometry"):
        build_water_mask(city, grid())


def test_open_river_is_not_closed_into_a_false_triangle():
    city = CityOSM(BBox(0, 0, 12, 12), "fixture", 0,
                   water=[dict(id=1, kind="river", nodes=[(10, 1), (10, 9), (2, 9)])])
    water = build_water_mask(city, grid())
    cost = build_cost_surface(city, grid())
    assert water[5, 5] == 0
    assert cost[5, 5] < 80
    assert water[2, 5] == 100


def test_gis_relation_export_retains_holes():
    import importlib.util
    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location("gis_water", root / "tools/automation/export-gis-context.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    city = _parse_overpass({"elements": [relation()]}, BBox(0, 0, 12, 12), "fixture")
    geometry = module.feature(city.water[0], "water")["geometry"]
    assert geometry["type"] == "MultiPolygon"
    assert sorted(len(p) for p in geometry["coordinates"]) == [1, 2]
    assert json.loads(json.dumps(geometry)) == geometry

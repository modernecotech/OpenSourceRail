"""A beam clearing a roof must never establish support or terrain clearance."""
from pathlib import Path
import sys

from shapely.geometry import LineString, box
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools/automation'))
from viaduct_clearance import height_metres, projected_buildings, screen_line


def segment(kind='elevated'):
    return dict(from_station_m=0, to_station_m=50, **{'class':kind}, viaduct_product='OSR-Pi25')


def record(height):
    return dict(id='building', height_m=height, floor_based_estimate_m=None)


def test_low_building_overflight_still_collides_with_foundation():
    result = screen_line(LineString([(0, 0), (50, 0)]), [segment()],
                         [box(23, -1, 27, 1)], [record(3)], lambda x, y:0)
    assert result['beam_building_checks'][0]['status'] == 'conditional-roof-overflight'
    assert any(row['status'] == 'foundation-footprint-conflict' for row in result['reference_supports'])
    assert result['physical_release'] is False


def test_tall_and_unknown_buildings_and_missing_terrain_fail_closed():
    route = LineString([(0, 0), (50, 0)])
    for height, status in [(20, 'beam-roof-collision'), (None, 'height-unresolved')]:
        result = screen_line(route, [segment()], [box(10, -1, 11, 1)], [record(height)], lambda x, y:0)
        assert result['beam_building_checks'][0]['status'] == status
    result = screen_line(route, [segment()], [box(10, -1, 11, 1)], [record(3)])
    assert result['beam_building_checks'][0]['status'] == 'height-unresolved'
    assert any(row['kind'] == 'terrain-unavailable' for row in result['unresolved'])


def test_thin_footprint_is_detected_between_sampling_points():
    result = screen_line(LineString([(0, 0), (50, 0)]), [segment('at-grade')],
                         [box(11.01, -1, 11.02, 1)], [record(1)], lambda x, y:0)
    assert result['beam_building_checks'][0]['status'] == 'ground-collision'


def test_terrain_crest_between_piers_collides_with_straight_beam():
    result = screen_line(LineString([(0, 0), (50, 0)]), [segment()], [], [],
                         lambda x, y:20 if 10<=x<=15 else 0)
    assert any(row['status'] == 'beam-terrain-collision' for row in result['terrain_checks'])
    steep = screen_line(LineString([(0, 0), (50, 0)]), [segment()], [], [], lambda x, y:x/10)
    assert all(row['status'] == 'reference-gradient-exceeded' for row in steep['terrain_checks'])


def test_explicit_units_and_floor_estimates_are_not_measured_heights():
    assert height_metres('100 ft') == pytest.approx(30.48)
    assert height_metres('15 m') == 15
    assert height_metres('10;15') is None
    polygons, records, invalid = projected_buildings([
        dict(id=1, nodes=[(0,0),(0,1),(1,1),(1,0),(0,0)], tags={'building:levels':'10'})], lambda lon,lat:(lon,lat))
    assert not invalid and len(polygons) == 1
    assert records[0]['height_m'] is None
    assert records[0]['floor_based_estimate_m'] == 35


def test_special_product_depth_and_lateral_setback_are_separate():
    route=LineString([(0,0),(50,0)])
    special={**segment(),'viaduct_product':'OSR-US'}
    assert screen_line(route,[special],[box(10,-1,11,1)],[record(1)],lambda x,y:0)['beam_building_checks'][0]['status']=='product-depth-unresolved'
    setback=screen_line(route,[segment()],[box(10,5,11,6)],[record(20)],lambda x,y:0)
    assert setback['beam_building_checks'][0]['status']=='lateral-clearance-conflict'
    assert setback['beam_building_checks'][0]['intersects_structural_envelope'] is False

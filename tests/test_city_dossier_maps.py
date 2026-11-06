from copy import deepcopy
import json
import math
import xml.etree.ElementTree as ET

import pytest

from engineering.city_reports.maps import (
    PALETTE, Projection, clip_route, geojson_layers, render, scale_length,
)


@pytest.fixture
def packet():
    stops = [dict(id='long-source-line-1-station-a', lon=44., lat=33., chainage_m=0.),
             dict(id='long-source-line-1-station-b', lon=44.02, lat=33.01, chainage_m=3000.)]
    line = dict(line_id='line-1', shape='radial',
        coordinates=[[44., 33.], [44.01, 33.], [44.01, 33.01], [44.02, 33.01]],
        coordinate_chainages_m=[0., 1000., 2000., 3000.],
        original_stops=stops, operational_stops=stops,
        station_complexes=[dict(operational_stop_id=stops[0]['id'],
            boarding_platform_intervals_m=[[-60., 60.]],
            access_connectors=[dict(original_stop_id='original-access',
                from_coordinates=[44.0002, 33.], to_coordinates=[44., 33.],
                along_route_connector_m=20., geometry_basis='Schematic endpoint connector')])])
    return dict(schema='osr-city-atlas/1', packet_id='packet-source-0123456789',
        identity=dict(selected_alignment_id='selected-source-alignment',
            research_configuration_id='research-configuration'),
        city=dict(name='Fixture & City'), lines=[line],
        physical_accepted=False, operating_release=False,
        interchanges=[dict(id='explicit-interchange', lon=44., lat=33., lines=['line-1'],
                           platforms=[stops[0]['id']])],
        civil=dict(quantities=dict(runs=[
            dict(line_id='line-1', **{'class': 'at-grade'}, from_m=0., to_m=1500.),
            dict(line_id='line-1', **{'class': 'elevated'}, from_m=1500., to_m=3000.)])),
        resources=dict(depot_area_m2=1000., annual_energy_usd=dict(base=100.)),
        costs=dict(capital_lines=[dict(key='network-auxiliary-charging',
            line_id='cost-record', scope='stations-power', quantity=dict(kw=10.))]))


def test_projection_preserves_metric_axes_north_and_scale():
    projection = Projection([[44., 33.], [44.02, 33.02]], (0, 0, 900, 700))
    p = projection([44.01, 33.01])
    north = projection([44.01, 33.01 + 1000 / 111320])
    east = projection([44.01 + 1000 / projection.lon_m, 33.01])
    assert north[1] < p[1] and east[0] > p[0]
    assert east[0] - p[0] == pytest.approx(p[1] - north[1])
    bar_m = scale_length(projection.pixels_per_m)
    assert 0 < bar_m * projection.pixels_per_m <= 140
    assert bar_m / 10 ** math.floor(math.log10(bar_m)) in (1, 2, 5)


def test_clipping_keeps_bends_and_adjacent_continuity(packet):
    line = packet['lines'][0]
    a = clip_route(line['coordinates'], line['coordinate_chainages_m'], 500, 1500)
    b = clip_route(line['coordinates'], line['coordinate_chainages_m'], 1500, 2500)
    for actual, expected in zip(a, [[44.005, 33.], [44.01, 33.], [44.01, 33.005]]):
        assert actual == pytest.approx(expected)
    assert a[-1] == b[0]
    assert b[1] == [44.01, 33.01]
    assert clip_route(line['coordinates'], line['coordinate_chainages_m'], -60, 60)[0] == line['coordinates'][0]
    with pytest.raises(ValueError, match='Monotonic'):
        clip_route(line['coordinates'], [0, 1000, 900, 3000], 0, 500)


def test_gis_identity_exact_geometry_and_unlocated_requirements(packet):
    original = deepcopy(packet)
    layers = geojson_layers(packet)
    assert packet == original
    for layer in layers.values():
        assert layer['packet_id'] == packet['packet_id']
        assert all(f['properties']['packet_id'] == packet['packet_id'] for f in layer['features'])
        json.dumps(layer, allow_nan=False)
    assert layers['routes']['features'][0]['geometry']['coordinates'] == packet['lines'][0]['coordinates']
    assert layers['stations']['features'][0]['id'] == 'long-source-line-1-station-a'
    assert layers['stations']['features'][0]['properties']['label'] == 'L1/01'
    assert len(layers['interchanges']['features']) == 1
    assert layers['civil_segments']['features'][0]['geometry']['coordinates'][-1] == layers['civil_segments']['features'][1]['geometry']['coordinates'][0]
    assert layers['platforms']['features'][0]['properties']['declared_interval_m'] == [-60., 60.]
    assert layers['access_connectors']['features'][0]['properties']['actual_accessible_path_surveyed'] is False
    unknowns = layers['unlocated_requirements']['features']
    assert len(unknowns) == 2
    assert all(f['geometry'] is None and f['properties']['site_count'] is None for f in unknowns)
    assert unknowns[0]['properties']['quantities']['depot_area_m2'] == 1000


def test_natural_order_keeps_current_ui_colours(packet):
    one = packet['lines'][0]
    packet['lines'] = [{**deepcopy(one), 'line_id': name} for name in ['line-1', 'line-10', 'line-2']]
    rows = geojson_layers(packet)['routes']['features']
    assert [f['id'] for f in rows] == ['line-1', 'line-2', 'line-10']
    assert [f['properties']['colour'] for f in rows] == [PALETTE[0], PALETTE[2], PALETTE[1]]


def test_deterministic_render_context_requires_explicit_verification(packet):
    context = dict(attribution=[dict(name='Example source', url='https://example.test', license='ODbL')],
        layers=dict(water=[dict(geometry=dict(type='Polygon', coordinates=[
            [[44., 33.], [44.01, 33.], [44.01, 33.01], [44., 33.]]]))], places=[]))
    svg = render(packet)
    assert svg == render(deepcopy(packet))
    assert svg == render(packet, context)
    assert 'Example source' not in svg
    verified = render(packet, context, context_verified=True)
    assert 'Example source' in verified and 'https://example.test' in verified
    assert 'packet-source-0123456789' in svg
    assert 'selected-source-alignment' in svg
    assert 'long-source-line-1-station-a' in svg
    assert 'L1/01' in svg and 'Physical acceptance' in svg
    assert 'Depot and energy siting: unlocated.' in svg
    assert '0.8 px' in svg
    assert len(svg.encode()) < 100_000
    root = ET.fromstring(svg)
    assert root.attrib['width'] == '1400'
    assert root.find('{http://www.w3.org/2000/svg}metadata') is not None
    selected = root.find('.//{http://www.w3.org/2000/svg}path[@id="selected-route-0"]')
    assert selected is not None
    assert selected.attrib['d'].count('L') + 1 == len(packet['lines'][0]['coordinates'])
    # Halo and foreground are separate SVG text elements for raster backends
    # without paint-order support; no station reference becomes a white blob.
    station_text = [e for e in root.findall('.//{http://www.w3.org/2000/svg}text')
                    if e.text == 'L1/01']
    assert len(station_text) == 2
    assert 'stroke' in station_text[0].attrib and 'stroke' not in station_text[1].attrib


@pytest.mark.parametrize('flag', ['physical_accepted', 'operating_release', 'movement_authority',
    'engineering_accepted', 'physical_reference_changed', 'procurement_ready'])
def test_false_release_guards(packet, flag):
    packet[flag] = True
    with pytest.raises(ValueError, match='release'):
        render(packet)
    with pytest.raises(ValueError, match='release'):
        geojson_layers(packet)


def test_reject_duplicate_lines_and_cross_candidate_civil(packet):
    packet['lines'].append(deepcopy(packet['lines'][0]))
    with pytest.raises(ValueError, match='identities'):
        render(packet)
    packet['lines'].pop()
    packet['civil']['quantities']['runs'][0]['line_id'] = 'another-candidate-line'
    with pytest.raises(ValueError, match='another candidate'):
        geojson_layers(packet)


def test_civil_run_domain_is_checked(packet):
    packet['civil']['quantities']['runs'][-1]['to_m'] = 4000
    with pytest.raises(ValueError, match='outside'):
        geojson_layers(packet)


def test_unknown_depot_energy_is_preserved_as_unknown(packet):
    packet['resources'] = {}
    packet['costs'] = {}
    features = geojson_layers(packet)['unlocated_requirements']['features']
    assert len(features) == 1
    assert features[0]['geometry'] is None
    assert features[0]['properties']['quantities'] is None
    assert features[0]['properties']['site_count'] is None

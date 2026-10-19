"""Actual mapped IFC geometry, city placements and stale-source rejection."""
import importlib.util
import json
from pathlib import Path

import ifcopenshell
import ifcopenshell.geom
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('city_federation', ROOT / 'tools/automation/generate-city-federation.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def fixture_city(tmp_path):
    city = tmp_path / 'city'; connected = city / 'engineering/connected-build'
    (connected / 'ifc').mkdir(parents=True)
    locations = [dict(id='s1', line='line-1', lat=33.0, lon=44.0, s_m=0.0),
                 dict(id='s2', line='line-1', lat=33.001, lon=44.001, s_m=145.0)]
    text = '[city]\nslug="test-city"\n'
    for p in locations:
        text += '\n[[stations]]\n' + '\n'.join(k + '=' + json.dumps(v) for k, v in p.items()) + '\n'
    (city / 'design.toml').write_text(text)
    (city / 'test-city.stations.json').write_bytes(m.encoded(locations))
    (city / 'test-city.corridor.geojson').write_bytes(m.encoded(dict(type='FeatureCollection', features=[dict(
        type='Feature', properties=dict(name='line-1'), geometry=dict(type='LineString', coordinates=[[44., 33.], [44.001, 33.001]]))])))
    stations = [dict(id=p['id'], line=p['line'], s_m=p['s_m'], product_variant='variant-001') for p in locations]
    (connected / 'stations.json').write_bytes(m.encoded(stations))
    f = ifcopenshell.file(schema='IFC4')
    origin = f.createIfcCartesianPoint((0., 0., 0.)); axis = f.createIfcAxis2Placement3D(origin)
    context = f.createIfcGeometricRepresentationContext(None, 'Model', 3, 1e-5, axis, None)
    units = f.createIfcUnitAssignment([f.createIfcSIUnit(None, 'LENGTHUNIT', None, 'METRE')])
    f.createIfcProject(ifcopenshell.guid.new(), None, 'fixture', None, None, None, None, [context], units)
    profile = f.createIfcRectangleProfileDef('AREA', None, None, 2., 4.)
    solid = f.createIfcExtrudedAreaSolid(profile, axis, f.createIfcDirection((0., 0., 1.)), 3.)
    rep = f.createIfcShapeRepresentation(context, 'Body', 'SweptSolid', [solid])
    placement = f.createIfcLocalPlacement(None, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((7., 8., 9.))))
    f.createIfcBuildingElementProxy(ifcopenshell.guid.new(), None, 'actual fixture', None, None, placement,
        f.createIfcProductDefinitionShape(None, None, [rep]), None, 'NOTDEFINED')
    source = connected / 'ifc/station-variant-001.ifc'; f.write(str(source))
    manifest = dict(source_sha256={'city/design.toml': m.digest(city / 'design.toml')}, output_sha256={
        'stations.json': m.digest(connected / 'stations.json'), 'ifc/station-variant-001.ifc': m.digest(source)})
    (connected / 'manifest.json').write_bytes(m.encoded(manifest))
    return city


def test_actual_geometry_reused_at_each_station_with_source_product_transform(tmp_path):
    city = fixture_city(tmp_path)
    report = m.generate(city, root=tmp_path)
    assert report['model']['station_instances'] == 2
    assert len(report['model']['variant_geometry']) == 1
    assert report['manufacturing_release'] is False
    assert report['model']['schema_validated'] is True
    assert report['model']['schema_findings'] == 0
    assert report['media']['native_vertex_count'] == 8
    assert report['media']['native_triangle_count'] == 12
    assert report['media']['source_variant'] == 'variant-001'
    assert 'geometry-preview.png' in report['output_sha256']
    assert 'ifcopenshell' in report['media']['tool_versions']
    assert 'generator_sha256' not in report['source_sha256']
    output = city / 'engineering/federation'
    assert m.verify(city, root=tmp_path) == report
    f = ifcopenshell.open(str(output / 'model.ifc'))
    plan = json.loads((output / 'instances.json').read_text())
    assert len(f.by_type('IfcExtrudedAreaSolid')) == 1
    assert len(f.by_type('IfcElementAssembly')) == 2
    assert f.by_type('IfcMapConversion')[0].TargetCRS.Name == 'EPSG:32638'
    # Inspect real vertices in station coordinates: the original product's
    # nonzero placement must survive nested maps, not disappear on import.
    element = next(e for e in f.by_type('IfcElementAssembly') if e.Name == 's1')
    settings = ifcopenshell.geom.settings(); settings.set(settings.USE_WORLD_COORDS, False)
    shape = ifcopenshell.geom.create_shape(settings, element)
    vertices = np.array(shape.geometry.verts).reshape(-1, 3)
    assert np.allclose(vertices.min(axis=0), [6., 6., 9.])
    assert np.allclose(vertices.max(axis=0), [8., 10., 12.])
    assert all(r['translation_m'][2] == 0 for r in plan['instances'])
    assert report['holds'] == m.HOLDS


def test_source_mutation_rejects_retained_federation(tmp_path):
    city = fixture_city(tmp_path); m.generate(city, root=tmp_path)
    p = city / 'design.toml'; p.write_text(p.read_text() + '\n# changed source\n')
    with pytest.raises(ValueError, match='Stale connected source'):
        m.verify(city, root=tmp_path)


def test_changed_output_rejected(tmp_path):
    city = fixture_city(tmp_path); m.generate(city, root=tmp_path)
    output = city / 'engineering/federation/model.ifc'
    output.write_text(output.read_text() + '\nchanged\n')
    with pytest.raises(ValueError, match='Changed federation output'):
        m.verify(city, root=tmp_path)


def test_missing_source_geometry_never_replaced_by_envelope(tmp_path):
    city = fixture_city(tmp_path)
    (city / 'engineering/connected-build/ifc/station-variant-001.ifc').unlink()
    with pytest.raises(ValueError, match='source IFC geometry'):
        m.generate(city, root=tmp_path)


def test_declared_native_chainage_rounding_preserves_exact_coordinates(tmp_path):
    city = fixture_city(tmp_path)
    p = city / 'test-city.stations.json'; locations = json.loads(p.read_text())
    locations[1]['s_m'] = 145.049
    p.write_bytes(m.encoded(locations))
    report = m.generate(city, root=tmp_path)
    assert report['model']['station_instances'] == 2
    locations[1]['lat'] += 0.00001
    p.write_bytes(m.encoded(locations))
    with pytest.raises(ValueError, match='Station coordinates differ'):
        m.generate(city, root=tmp_path)


def test_no_route_geometry_no_invented_orientation(tmp_path):
    city = fixture_city(tmp_path)
    p = city / 'test-city.corridor.geojson'
    p.write_bytes(m.encoded(dict(type='FeatureCollection', features=[])))
    with pytest.raises(ValueError, match='Missing route tangent'):
        m.generate(city, root=tmp_path)


def shared_city(tmp_path, *, geometry):
    import shutil
    city = fixture_city(tmp_path)
    source_bytes = (city / 'engineering/connected-build/ifc/station-variant-001.ifc').read_bytes()
    shutil.rmtree(city / 'engineering/connected-build')
    design = city / 'design.toml'
    design.write_text(design.read_text().replace('[[stations]]', '[[stations]]\narchetype="standard"'))
    if geometry:
        target = tmp_path / 'build/engineering/interchange/stations/station-standard.ifc'
        target.parent.mkdir(parents=True); target.write_bytes(source_bytes)
    return city


def test_shared_archetype_missing_geometry_is_held_without_fabricated_model(tmp_path):
    city = shared_city(tmp_path, geometry=False)
    report = m.generate(city, root=tmp_path)
    assert report['model']['geometry_status'] == 'geometry-unavailable'
    assert report['model']['station_instances'] == 2
    assert report['model']['geometry_instances'] == 0
    assert report['model']['missing_geometry_variants'] == ['standard']
    assert not (city / 'engineering/federation/model.ifc').exists()
    assert m.verify(city, root=tmp_path) == report


def test_shared_city_geometry_uses_own_southern_hemisphere_coordinates(tmp_path):
    city = shared_city(tmp_path, geometry=True)
    design = city / 'design.toml'
    design.write_text(design.read_text().replace('33.001', '-34.001').replace('33.0', '-34.0').replace('44.001', '18.001').replace('44.0', '18.0'))
    locations = json.loads((city / 'test-city.stations.json').read_text())
    for i, s in enumerate(locations): s.update(lat=-34.0 - i * .001, lon=18.0 + i * .001)
    (city / 'test-city.stations.json').write_bytes(m.encoded(locations))
    (city / 'test-city.corridor.geojson').write_bytes(m.encoded(dict(type='FeatureCollection', features=[dict(
        type='Feature', properties=dict(name='line-1'), geometry=dict(type='LineString', coordinates=[[18., -34.], [18.001, -34.001]]))])))
    report = m.generate(city, root=tmp_path)
    plan = json.loads((city / 'engineering/federation/instances.json').read_text())
    assert plan['epsg'] == 32734
    assert [r['latitude'] for r in plan['instances']] == [-34., -34.001]
    assert report['model']['geometry_status'] == 'placed-retained-geometry'
    assert report['model']['geometry_instances'] == 2
    assert m.verify(city, root=tmp_path) == report

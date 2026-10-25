from copy import deepcopy
import json
import math
import xml.etree.ElementTree as ET

import pytest
from engineering.city_maps import basemap, render


def fixture(tmp_path,monkeypatch):
    design=dict(name='Example & River',city=dict(slug='example'),
        lines=[dict(name='r',shape='radial')],
        stations=[dict(id='a',line='r',s_m=0,lon=44.,lat=33.),
                  dict(id='b',line='r',s_m=1000,lon=44.1,lat=33.1)],
        interchanges=[dict(id='transfer',lon=44.05,lat=33.05)])
    geometry=dict(type='LineString',coordinates=[[44.,33.],[44.1,33.1]])
    geo=tmp_path/'example.corridor.geojson'
    geo.write_text(json.dumps(dict(type='FeatureCollection',features=[dict(type='Feature',properties={'name':'r'},geometry=geometry)])))
    bounds,zoom=render.viewport(design,geo)
    context=dict(bounds_wsen=bounds,zoom=zoom,source=dict(build='20261024'),layers={
        'roads':[dict(type='Feature',geometry=geometry,properties={'name':'Real Road','kind':'major_road'})],
        'water':[dict(type='Feature',geometry=geometry,properties={'kind':'river'})],
        'places':[dict(type='Feature',geometry={'type':'Point','coordinates':[44.025,33.04]},properties={'name':'Actual Town','kind_detail':'town'})]})
    path=tmp_path/'map-context.json.gz';path.write_bytes(b'unit test boundary')
    monkeypatch.setattr(basemap,'load',lambda p:deepcopy(context))
    return design,geo,context


def test_context_layers_labels_marker_styles_and_projection_match(tmp_path,monkeypatch):
    design,geo,context=fixture(tmp_path,monkeypatch)
    output=tmp_path/'map.svg'
    result=render.render(design,geo,output)
    root=ET.fromstring(output.read_bytes());ns={'s':'http://www.w3.org/2000/svg'}
    assert root.find('.//s:g[@id="basemap-roads"]/s:path',ns) is not None
    assert root.find('.//s:g[@id="basemap-water"]/s:path',ns) is not None
    assert root.find('.//s:g[@id="current-proposal"]/s:rect',ns) is not None
    assert 'Actual Town' in output.read_text() and 'OpenStreetMap contributors' in output.read_text()
    road=root.find('.//s:g[@id="basemap-roads"]/s:path',ns).get('d')
    route=root.findall('.//s:g[@id="current-proposal"]/s:polyline',ns)[1].get('points')
    assert road[1:].replace('L',' ')==route
    assert result['projection']=='EPSG:3857' and result['label_count']>=1
    assert not root.findall('.//s:image',ns)  # no hidden live tiles/external assets


def test_missing_context_and_changed_viewport_fail_explicitly(tmp_path,monkeypatch):
    design,geo,context=fixture(tmp_path,monkeypatch)
    (tmp_path/'map-context.json.gz').unlink()
    with pytest.raises(ValueError,match='basemap required'):render.render(design,geo,tmp_path/'map.svg')
    (tmp_path/'map-context.json.gz').write_bytes(b'fixture')
    context['bounds_wsen'][0]-=.1
    with pytest.raises(ValueError,match='viewport differs'):render.render(design,geo,tmp_path/'map.svg')
    assert not (tmp_path/'map.svg').exists()


def test_mercator_roundtrip_and_north_up_are_independent():
    for p in ([44.,33.],[-70.,-15.],[80.,26.]):
        assert render.lonlat(render.mercator(p))==pytest.approx(p)
    assert render.mercator([44.,34.])[1]<render.mercator([44.,33.])[1]
    for p in ([float('nan'),33.],[0.,89.],[181.,0.]):
        with pytest.raises(ValueError):render.mercator(p)


def test_viewport_keeps_stops_and_routes_inside_and_bounds_download(tmp_path,monkeypatch):
    design,geo,context=fixture(tmp_path,monkeypatch)
    bounds,zoom=render.viewport(design,geo)
    assert len(basemap.tiles_for_bounds(bounds,zoom))<=64
    for s in design['stations']:
        assert bounds[0]<s['lon']<bounds[2] and bounds[1]<s['lat']<bounds[3]


def test_static_names_use_source_supported_script_without_fake_translation():
    assert render._name({'name':'लखनऊ','name:en':'Lucknow'})=='Lucknow'
    assert render._name({'name':'लखनऊ'}) is None
    assert render._name({'name':'\ue000'}) is None
    assert render._name({'name':'São Paulo'})=='São Paulo'


def test_offline_check_requires_context_that_renderer_can_use(tmp_path,monkeypatch):
    from engineering.city_maps import __main__ as command
    design,geo,context=fixture(tmp_path,monkeypatch)
    context['layers'].pop('roads')
    path=tmp_path/'city.json';path.write_text(json.dumps(design))
    monkeypatch.setattr(command,'proposal',lambda p:design)
    with pytest.raises(ValueError,match='roads or place'):command.acquire(path,tmp_path/'cache',check=True)

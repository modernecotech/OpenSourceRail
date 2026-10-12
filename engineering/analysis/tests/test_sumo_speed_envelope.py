"""Independent SUMO motion uses the same track and vehicle speed inputs."""
import importlib.util
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('sumo_envelope', ROOT/'engineering/analysis/benchmarks/sumo/city_timetable.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('vehicle_kmh,expected_mps', [(100, 22.0), (36, 10.0)])
def test_exported_track_and_train_speeds_preserve_both_limits(tmp_path, monkeypatch, vehicle_kmh, expected_mps):
    stock = tmp_path/'rolling-stock.toml'
    stock.write_bytes(module.ROLLING_STOCK.read_bytes())
    monkeypatch.setattr(module, 'ROLLING_STOCK', stock)
    monkeypatch.setattr(module, 'REPO_ROOT', tmp_path)
    design = tmp_path/'design.toml'
    design.write_text('''[city]
slug="speed-envelope"
country="TZ"
[[lines]]
name="line-1"
shape="radial"
length_m=3000.0
rolling_stock="metro-6car"
[[stations]]
id="a"
line="line-1"
s_m=0.0
lat=-6.8
lon=39.0
[[stations]]
id="b"
line="line-1"
s_m=3000.0
lat=-6.8
lon=39.027
''')
    (tmp_path/'speed-envelope.corridor.geojson').write_text(json.dumps({
        'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':'line-1','kind':'line'},
        'geometry':{'type':'LineString','coordinates':[[39.0,-6.8],[39.027,-6.8]]}}]}))
    (tmp_path/'speed-envelope.toml').write_text(f'''[consist]
max_speed_kmh={vehicle_kmh}
[[stations]]
id="a"
dwell_seconds=180
[[stations]]
id="b"
dwell_seconds=180
''')
    output=tmp_path/'sumo'
    report=module.generate_city(design,output,generate_only=True)
    assert report['lines'][0]['maximum_speed_mps']==expected_mps
    assert all(float(edge.attrib['speed'])==expected_mps for edge in ET.parse(output/'city.edg.xml').getroot())
    vehicle=ET.parse(output/'city.rou.xml').getroot().find('vType')
    assert float(vehicle.attrib['maxSpeed'])==expected_mps

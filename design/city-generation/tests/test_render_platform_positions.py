"""Complex metadata must never replace the actual platform points on a map."""
from types import SimpleNamespace

from PIL import Image

from osr_scenario.render_map import render_city


def test_transfer_markers_use_platforms_instead_of_the_complex_centroid(tmp_path, monkeypatch):
    import staticmap

    points = []
    links = []

    class Map:
        def __init__(self, *args, **kwargs):
            pass

        def add_line(self, line):
            links.append(line)

        def add_marker(self, marker):
            points.append(marker.coord)

        def render(self, *args, **kwargs):
            return Image.new('RGB', (20, 20))

    monkeypatch.setattr(staticmap, 'StaticMap', Map)
    monkeypatch.setattr(staticmap, 'CircleMarker', lambda coord, *args: SimpleNamespace(coord=coord))
    path = tmp_path / 'design.toml'
    path.write_text('''[city]
slug = "test"
[[lines]]
name = "A"
track_polyline = [[-1.0, 28.0], [-1.01, 28.01]]
[[stations]]
id = "A1"
line = "A"
lat = -1.0
lon = 28.0
junction_group = 0
[[stations]]
id = "B1"
line = "B"
lat = -1.01
lon = 28.01
junction_group = 0
[[interchanges]]
junction_group = 0
lat = -1.005
lon = 28.005
''')
    outputs = render_city(path, tmp_path, route_on_roads=False)
    assert outputs[0].is_file()
    assert set(points) == {(28.0, -1.0), (28.01, -1.01)}
    # One full junction symbol (three layers), one smaller platform dot
    # (two layers). Both remain on actual platforms, with a schematic link.
    assert len(points) == 5
    assert sorted(points.count(point) for point in set(points)) == [2, 3]
    assert len(links) == 3  # railway plus the two-layer complex link

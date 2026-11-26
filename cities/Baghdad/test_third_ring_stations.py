"""Check common platform geometry, duplicate calls and walking-transfer continuity."""

import numpy as np

from cities.Baghdad import holistic_network as model
from cities.Baghdad import third_ring_stations as merge


def _coordinates(east, north):
    return (np.array([44.4, 33.3]) + np.array([east, north]) / model.LOCAL_METRES).tolist()


def _linked_platforms(*, separated=False, duplicate=False):
    def line(code, points):
        geometry = [_coordinates(*xy) for _, xy in points]
        track = model.Track(geometry)
        for (name, _), point in zip(points, geometry, strict=True):
            stations[name] = {"name": name, "coordinates": point, "lines": [code], "basis": "Mapped platform"}
        return {"loop": False, "geometry": geometry, "one_way_km": track.km,
                "station_ids": [name for name, _ in points],
                "station_chainage_km": {name: km / 1000 for (name, _), km in
                                        zip(points, track.chainage, strict=True)}}

    stations = {}
    horizontal = line("A", [("A-start", (-1000, 0)), ("A-near", (-120, 0)),
                            ("A-extra", (120 if duplicate else 500, 0)), ("A-end", (1000, 0))])
    vertical = line("B", [("B-start", (-1000, 70) if separated else (0, -1000)), ("B-near", (0, 120)),
                          ("B-end", (0, 1000))])
    first, second = (stations[name]["coordinates"] for name in ("A-near", "B-near"))
    network = {"lines": {"A": horizontal, "B": vertical}, "stations": stations, "transfers": [],
               "station_site_links": [{"id": "W-1", "station_ids": ["A-near", "B-near"],
                                       "walks_m": [180., 180.], "geometry": [[first, second], [second, first]]}]}
    network["topology"] = model.validate(network)
    return model._identity(network)


def _mock_walks(monkeypatch):
    def path(first, second):
        distance = float(np.linalg.norm((np.asarray(first) - second) * model.LOCAL_METRES))
        return distance, [list(first), list(second)]

    monkeypatch.setattr(merge.sites, "_street_paths", lambda graph, water: (lambda point: point, path))


def test_walk_link_graduates_at_crossing(monkeypatch):
    _mock_walks(monkeypatch)
    source = _linked_platforms()
    revised, audit = merge.consolidate(source, graph=None, context={"layers": {"water": []}})
    assert revised["candidate_id"] != source["candidate_id"]
    assert model.validate(revised) == revised["topology"]
    assert len(source["station_site_links"]) == 1
    assert revised["station_site_links"] == []
    assert revised["lines"]["A"]["geometry"] == source["lines"]["A"]["geometry"]
    assert revised["lines"]["A"]["station_ids"] == ["A-start", "A-near", "A-extra", "A-end"]
    assert revised["lines"]["B"]["station_ids"] == ["B-start", "A-near", "B-end"]
    assert revised["stations"]["A-near"]["lines"] == ["A", "B"]
    assert np.allclose(revised["stations"]["A-near"]["coordinates"], _coordinates(0, 0))
    assert audit["actions"][0]["graduated_walk_link_ids"] == ["W-1"]
    assert audit["train_calls_before"] == audit["train_calls_after"]


def test_disjoint_track_ends_retain_the_separate_walk_transfer(monkeypatch):
    _mock_walks(monkeypatch)
    source = _linked_platforms(separated=True)
    revised, audit = merge.consolidate(source, graph=None, context={"layers": {"water": []}},
                                       protected_stations=["A-near", "A-extra"])
    assert revised["candidate_id"] == source["candidate_id"]
    assert revised["station_site_links"] == source["station_site_links"]
    assert not audit["actions"]
    assert any(row["station_ids"] == ["A-near", "B-near"] and "No common alignment" in row["reason"]
               for row in audit["held"])


def test_adjacent_same_line_calls_are_absorbed_only_once(monkeypatch):
    _mock_walks(monkeypatch)
    source = _linked_platforms(separated=True, duplicate=True)
    revised, audit = merge.consolidate(source, graph=None, context={"layers": {"water": []}},
                                       protected_stations=["A-near"])
    assert revised["lines"]["A"]["station_ids"] == ["A-start", "A-near", "A-end"]
    assert revised["station_site_links"] == source["station_site_links"]
    assert audit["actions"][0]["kind"] == "close_calls"
    assert audit["train_calls_before"] - audit["train_calls_after"] == 1

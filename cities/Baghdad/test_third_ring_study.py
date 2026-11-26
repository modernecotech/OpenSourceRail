"""Reconcile the published three-ring comparison with geometry and service."""

import gzip
from hashlib import sha256
import json

import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree

from cities.Baghdad import central_access, holistic_access, holistic_network, ring_corridors, third_ring_portfolio
from cities.Baghdad import third_ring_publication as publication, third_ring_study as study


def test_published_trial_preserves_ring_shape_station_evidence_and_matching_train_km():
    with gzip.open(study.CITY / publication.DATA, "rt", encoding="utf-8") as stream:
        record = json.load(stream)
    identity = record.pop("publication_id")
    assert identity == sha256(central_access.encode(record)).hexdigest()
    context = central_access.original_cases()[3]
    expected_train_km = record["housing"]["variants"]["published"]["service"]["running_train_km_day"]
    main = record["selection"]["illustrated_trial"]
    for key, network in record["layouts"].items():
        row = record["summary"][key]
        polygons = study.validate_layout(network)
        if "M16" in polygons and "M09" in polygons:
            assert polygons["M16"].boundary.distance(polygons["M09"].boundary) >= 500
        assert row["short_lines"] == study.short_lines(network)
        assert row["through_lines"] == study.classify_through(network, context)
        for assignment in (record["housing"], record["metropolitan"]):
            case = assignment["variants"][key]
            assert case["candidate_id"] == network["candidate_id"]
            assert case["service"]["running_train_km_day"] == expected_train_km
        if key in record["costs"]:
            assert record["costs"][key]["candidate_id"] == network["candidate_id"]
    for path, digest in record["source_sha256"].items():
        assert central_access.digest(central_access.ROOT / path) == digest
    gis = central_access.read(study.CITY / publication.GEOJSON)
    assert gis["publication_id"] == identity
    assert gis["candidate_id"] == record["layouts"][main or "published"]["candidate_id"]


def test_edited_geojson_removes_a_line_and_reroutes_another(tmp_path):
    stops = {"old": [44.26, 33.3], "shared": [44.28, 33.3], "new": [44.28, 33.32]}
    reference = {"candidate_id": "control", "stations": {}, "lines": {
        "keep-new-path": {"geometry": [stops["old"], stops["shared"]], "station_ids": ["old", "shared"], "loop": False},
        "remove": {"geometry": [stops["shared"], stops["new"]], "station_ids": ["shared", "new"], "loop": False}}}
    features = [{"type": "Feature", "properties": {"kind": "line", "line_id": "keep-new-path",
                                                   "station_ids": ["shared", "new"], "loop": False},
                 "geometry": {"type": "LineString", "coordinates": [stops["shared"], stops["new"]]}}]
    features.extend({"type": "Feature", "properties": {"kind": "station", "station_id": key},
                     "geometry": {"type": "Point", "coordinates": coordinates}} for key, coordinates in stops.items())
    path = tmp_path / "revised.geojson"
    path.write_bytes(central_access.encode({"type": "FeatureCollection", "features": features}))
    trial, changes = study.import_layout(path, reference)
    assert changes["removed"] == ["remove"] and changes["changed"] == ["keep-new-path"]
    assert set(trial["stations"]) == {"shared", "new"}
    assert trial["topology"]["connected_components"] == 1


def test_airport_is_a_destination_and_can_be_reserved_to_a_replacement_route():
    coords = {"airport": [44.3, 33.3], "joint": [44.32, 33.3], "centre": [44.34, 33.3]}
    routes = {"C1": ["airport", "joint"], "replacement": ["airport", "joint"], "centre": ["joint", "centre"]}
    stops = {key: {"name": key, "basis": "Test fixture", "coordinates": point,
                   "lines": [line for line, calls in routes.items() if key in calls]} for key, point in coords.items()}
    lines = {line: holistic_network._physical_line([coords[stop] for stop in calls], calls, stops, [], "Test fixture")
             for line, calls in routes.items()}
    library = {"lines": lines, "stations": stops, "transfers": []}
    ring_corridors._refresh_transfers(library)
    holistic_network._identity(library)
    points = np.array(list(coords.values()))
    x, y = points.T
    nodes, xy = np.arange(3), central_access._points(points)
    graph = ({"lon": x, "lat": y}, csr_matrix([[0, 1850, 0], [1850, 0, 1850], [0, 1850, 0]]),
             nodes, cKDTree(xy), {"scope": "Test fixture"})
    people = holistic_access.Population({"dataset": "test"}, points, np.ones(3), np.zeros(3), nodes, xy)
    options = {"populations": {"test": people}, "destinations": {"Airport": coords["airport"], "Centre": coords["centre"]}}
    selected, audit = third_ring_portfolio.assemble(library, graph, **options, excluded_route_ids=("C1",), max_lines=2)
    assert set(selected["lines"]) == {"replacement", "centre"}
    assert audit["chosen"]["destination_walk_m"] == {"Airport": 0., "Centre": 0.}
    assert "C1" in library["lines"]

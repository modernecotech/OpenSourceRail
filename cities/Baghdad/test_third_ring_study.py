"""Reconcile the published three-ring comparison with geometry and service."""

import gzip
from hashlib import sha256
import json

import numpy as np
import pytest
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree
from shapely.geometry import Polygon

from cities.Baghdad import central_access, holistic_access, holistic_network, ring_corridors, third_ring_portfolio
from cities.Baghdad import third_ring_publication as publication, third_ring_study as study


def test_published_trial_reconciles_ring_contacts_station_evidence_and_matching_train_km():
    with gzip.open(study.CITY / publication.DATA, "rt", encoding="utf-8") as stream:
        record = json.load(stream)
    identity = record.pop("publication_id")
    assert identity == sha256(central_access.encode(record)).hexdigest()
    context = central_access.original_cases()[3]
    expected_train_km = record["housing"]["variants"]["published"]["service"]["running_train_km_day"]
    main = record["selection"]["illustrated_trial"]
    assert main != "published"
    assert main in record["layouts"]
    assert len(record["rings"]["generated_orbital_shapes"]) >= 2
    for key, network in record["layouts"].items():
        row = record["summary"][key]
        polygons = study.validate_layout(network)
        if "M16" in polygons and "M09" in polygons:
            metrics = study._orbital_metrics(network, context)
            assert metrics == row["orbital_metrics"]
            assert 0 < metrics["middle_outer_gap_km"]["p10"] < metrics["middle_outer_gap_km"]["p90"]
            assert 0 < metrics["inner_middle_gap_km"]["p10"] < metrics["inner_middle_gap_km"]["p90"]
            assert metrics["inner_foldback_km"] == 0
            assert row["lines"] < record["summary"]["published"]["lines"]
            assert row["stations"] < record["summary"]["published"]["stations"]
            assert row["through_count"] == row["lines"] - 3 - len(row["local_services"])
            assert row["station_screen"]["pairs_closer_than_750_m"] < (
                record["summary"]["published"]["station_screen"]["pairs_closer_than_750_m"])
            trial = record["layout_trials"][key]
            assert trial["candidate_id"] == network["candidate_id"]
            assert trial["evaluation_id"] == network["evaluation_id"]
            assert trial["walking"] == {"worldpop-2026": row["worldpop_1300_pct"], "ghsl-2025": row["ghsl_1300_pct"]}
            assert row["short_lines"] == []
            assert record["coverage"]["worldpop-2026"][key]["1300"]["short_route_catchments"][
                "baseline_short_only_people"] > 0
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
    assert gis["candidate_id"] == record["layouts"][main]["candidate_id"]
    selected = record["layouts"][main]
    colors = publication.route_colors(selected, set(record["summary"][main]["short_lines"]))
    for feature in gis["features"]:
        properties = feature["properties"]
        if properties["kind"] == "line":
            assert properties["stroke-opacity"] == 1
            assert properties["stroke"] == colors[properties["line_id"]]


def test_published_suburban_improvement_uses_the_same_through_services_and_boundary():
    with gzip.open(study.CITY / publication.DATA, "rt", encoding="utf-8") as stream:
        record = json.load(stream)
    key, trial = next((key, row) for key, row in record["layout_trials"].items() if key.endswith("-extended"))
    core_key = trial["core_layout"]
    before, after = (record["layouts"][case] for case in (core_key, key))
    audit = trial["suburban_extensions"]
    regional = trial["regional_access"]
    assert regional["base_candidate_id"] == before["candidate_id"]
    assert set(after["lines"]) - set(before["lines"]) == {row["route"] for row in regional["selected"].values()}
    assert all(after["stations"][stop]["coordinates"] == row["coordinates"]
               and set(row["lines"]) <= set(after["stations"][stop]["lines"])
               for stop, row in before["stations"].items())
    assert all(before["lines"][code] == after["lines"][code] for code in study.RINGS)
    assert len(after["stations"]) - len(before["stations"]) == (
        audit["new_station_sites"] + sum(row["new_station_sites"] for row in regional["selected"].values()))
    added_km = audit["route_km_added"] + sum(row["route_km"] for row in regional["selected"].values())
    assert record["summary"][key]["route_km"] - record["summary"][core_key]["route_km"] == pytest.approx(
        added_km, abs=.02)
    assert "Airport-00" in {after["lines"]["T01"]["station_ids"][i] for i in (0, -1)}
    for case, network in ((core_key, before), (key, after)):
        suburban = study._suburban_metrics(network)
        assert suburban == record["summary"][case]["suburban"]
        assert suburban["missing_contour_crossings"] == []
        assert suburban["close_departures"] == []
        assert suburban["parallel_suburban_corridors"] == []
        assert suburban["minimum_departure_spacing_m"] >= 5000
    for row in audit["extensions"]:
        code = row["route"]
        assert row["former_terminal"] in after["lines"][code]["station_ids"]
        assert row["new_terminal"] == after["lines"][code]["station_ids"][0 if row["end"] == 0 else -1]
        assert 0 < row["route_km"] <= audit["maximum_km_per_end"]
    for grid, cases in record["coverage"].items():
        compact, expanded = (cases[case]["1300"] for case in (core_key, key))
        assert expanded["access_people"] - compact["access_people"] >= audit["newly_reached"][grid] - 1
        outer = [cases[case]["1300"]["outside_trial_outer_ring"] for case in ("published", core_key, key)]
        assert len({row["population"] for row in outer}) == 1
        assert outer[2]["served"] > outer[1]["served"]


def test_published_named_places_and_one_urban_gap_are_connected_and_compared():
    record = central_access.read(study.CITY / publication.DATA)
    selected = record["selection"]["illustrated_trial"]
    network = record["layouts"][selected]
    metadata = record["layout_trials"][selected]
    parent = metadata["urban_gap_parent"]
    added = metadata["urban_gap"]["selected"]
    assert added["line_id"] == "U01"
    assert set(network["lines"]) - set(record["layouts"][parent]["lines"]) == {"U01"}
    graph = central_access.walking_graph()
    context = central_access.original_cases()[3]
    assert study.coverage_gap.validate_gap_line(network, graph, context)["shared_station_ids"] == added["shared_station_ids"]
    rows = study.coverage_regional.validate(network, context, graph)
    assert all(not row["failures"] for row in rows.values())
    for destination, walk in record["summary"][selected]["destination_walk_m"].items():
        assert destination in {"Basmaya", "Nahrawan", "Tajiyat"}
        assert 0 <= walk <= study.WALK_M
    for grid, layouts in record["coverage"].items():
        before, after = (layouts[key]["1300"]["access_people"] for key in (parent, selected))
        assert after - before == pytest.approx(added["newly_reached"][grid], abs=1)
    assert record["metropolitan_comparison"]["method"] == "metropolitan-network/1"
    assert record["metropolitan_comparison"]["assessments"][selected]["destinations_without_walk_access"] == []
    assert "retained-named-gap" in record["layouts"]
    assert any(case.startswith("coverage-") and case.endswith("-gap") for case in record["layouts"])
    assert selected in record["metropolitan_comparison"]["assessments"]


def test_illustrated_trial_carries_all_named_suburbs_through_baghdad():
    record = central_access.read(study.CITY / publication.DATA)
    selected = record["selection"]["through_research_lead"]
    assert selected == record["selection"]["illustrated_trial"]
    network = record["layouts"][selected]
    through = record["summary"][selected]["through_lines"]
    suburbs = record["named_suburban_journeys"]["variants"]
    direct = suburbs[selected]
    feeder = suburbs["retained-named-gap"]
    assert direct["candidate_id"] == network["candidate_id"]
    assert direct["running_train_km_day"] == feeder["running_train_km_day"]
    for name in study.coverage_destinations.ANCHORS:
        origin = direct["origins"][name]
        assert origin["walkable_through_routes"]
        assert origin["walkable_through_routes"].keys() <= through.keys()
        assert all(through[route]["crosses_tigris_centreline"] and
                   all(through[route]["ring_crossing_stations"][ring] for ring in study.RINGS)
                   for route in origin["walkable_through_routes"])
        assert not feeder["origins"][name]["walkable_through_routes"]
        assert origin["destination_count_by_max_transfers"]["2"] > (
            feeder["origins"][name]["destination_count_by_max_transfers"]["2"])
    for name in ("Basmaya", "Tajiyat"):
        assert direct["origins"][name]["direct_through_destination_count"] > 0
        assert direct["origins"][name]["destination_count_by_max_transfers"]["0"] > 0
    assert not record["summary"][selected]["suburban"]["close_departures"]
    assert not record["summary"][selected]["suburban"]["parallel_suburban_corridors"]


def test_rings_can_touch_at_a_shared_station_but_cannot_share_running_track():
    outer = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    inner = Polygon([(2, 2), (5, 0), (8, 2), (6, 5), (4, 5)])
    point = (np.array([5, 0]) / holistic_network.LOCAL_METRES).tolist()
    network = {"lines": {"a": {"station_ids": ["junction"]}, "b": {"station_ids": ["junction"]}},
               "stations": {"junction": {"coordinates": point}}}
    assert study._ring_contacts(network, "a", "b", {"a": inner, "b": outer}) == ["junction"]
    network["lines"]["a"]["station_ids"] = []
    with pytest.raises(ValueError, match="exact shared station"):
        study._ring_contacts(network, "a", "b", {"a": inner, "b": outer})
    shared = Polygon([(2, 0), (4, 0), (6, 2), (4, 5)])
    with pytest.raises(ValueError, match="share guideway"):
        study._ring_contacts(network, "a", "b", {"a": shared, "b": outer})


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

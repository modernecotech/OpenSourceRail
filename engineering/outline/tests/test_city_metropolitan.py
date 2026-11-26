"""Through services and connected portfolios on local mapped inputs."""

from copy import deepcopy

import pytest

from engineering.outline import city_alignment, city_metropolitan
from engineering.station_rail.common import identity


def _line(name, points, shape="radial"):
    chainages = city_alignment.chainages(points)
    stops = [dict(id=f"{name}-{i}", lon=point[0], lat=point[1], dwell_s=35., chainage_m=at)
             for i, (point, at) in enumerate(zip(points, chainages, strict=True))
             if shape == "radial" or i < len(points) - 1]
    line = dict(line_id=name, shape=shape, coordinates=points, coordinate_chainages_m=chainages,
                route_m=chainages[-1], stops=stops)
    city_alignment._legs(line)
    return line


def _fixture():
    west = _line("west", [[-.04, 0], [-.02, 0], [0, 0]])
    east = _line("east", [[0, 0], [.02, 0], [.04, 0]])
    ring = _line("ring", [[-.02, 0], [-.02, -.01], [.02, -.01], [.02, 0],
                          [.02, .01], [-.02, .01], [-.02, 0]], "ring")
    island = _line("island", [[0, .07], [0, .09]])
    lines = [west, east, ring, island]
    city = dict(lines=lines, civil_segments=[
        dict(line_id=row["line_id"], **{"class": "bridge" if row is east else "elevated"},
             from_m=0., to_m=row["route_m"]) for row in lines],
        interchanges=[
            dict(id="centre", lines=["west", "east"], platforms=["west-2", "east-0"]),
            dict(id="west-ring", lines=["west", "ring"], platforms=["west-1", "ring-0"]),
            dict(id="east-ring", lines=["east", "ring"], platforms=["east-1", "ring-3"]),
        ], od=[dict(origin="west-0", destination="east-0", trips=17)], source_sha256={})
    city["input_id"] = identity(city)
    return city


def test_default_search_prices_a_reproducible_join_and_connected_portfolio():
    city = _fixture()
    original = deepcopy(city)
    options, trace = city_metropolitan.search(city, dict(ring_ids=["ring"], river_name="Example River"))
    assert city == original
    assert trace["method"] == city_metropolitan.METHOD
    assert trace["assembly"] == "from-empty-retained-corridor-library"
    assert trace["linked_components"] == [["east", "ring", "west"], ["island"]]
    assert trace["potential_through_joins"] == 1
    joined, connected = options
    network = joined["city_input"]
    line = next(row for row in network["lines"] if row["line_id"].startswith("through-"))
    assert line["coordinates"] == [[.04, 0], [.02, 0], [0, 0], [-.02, 0], [-.04, 0]]
    assert len(line["stops"]) == 5
    assert line["stops"][-1]["chainage_m"] == line["route_m"]
    for row in network["interchanges"]:
        assert row["id"] != "centre"
        assert line["line_id"] in row["lines"]
    assert network["od"] == [dict(origin="west-0", destination="east-0", trips=17)]
    bridge, elevated = [row for row in network["civil_segments"] if row["line_id"] == line["line_id"]]
    assert (bridge["class"], elevated["class"]) == ("bridge", "elevated")
    assert bridge["from_m"] == 0
    assert bridge["to_m"] == pytest.approx(elevated["from_m"])
    assert elevated["to_m"] == pytest.approx(line["route_m"])
    assert {row["line_id"] for row in connected["city_input"]["lines"]} == {"east", "ring", "west"}
    assert all(case["selection_eligibility"]["access_screen"] == "hold" for case in options)


def test_crossing_with_a_right_angle_cannot_merge_into_a_through_route():
    city = _fixture()
    city["lines"][1] = _line("east", [[0, 0], [0, .02], [0, .04]])
    _, trace = city_metropolitan.search(city, dict(ring_ids=["ring"], river_name=None))
    assert trace["potential_through_joins"] == 0


def test_line_bound_inputs_disable_service_reallocation():
    city = _fixture()
    options, trace = city_metropolitan.search(city, dict(ring_ids=[], river_name=None),
                                              allow_line_changes=False)
    assert options == []
    assert trace["line_changes_screened"] is False

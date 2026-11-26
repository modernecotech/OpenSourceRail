"""Check parallel cut layouts against the retained redesign GIS."""

import tomllib

import pytest

from . import central_parallel_routes, holistic_network, rail_duplication, residential_planning
from .central_access import read
from .ring_grid_comparison import PROTECTED
from .ring_network_study import GEOJSON


@pytest.fixture(scope="module")
def pinned_layouts():
    source = read(GEOJSON)
    network = {key: source[key] for key in ("candidate_id", "evaluation_id")}
    network.update(lines={}, stations={}, transfers=[])
    for feature in source["features"]:
        props = dict(feature["properties"])
        coordinates = feature["geometry"]["coordinates"]
        kind = props.pop("kind")
        if kind == "line":
            network["lines"][props.pop("line_id")] = props | {"geometry": coordinates}
        if kind in {"station", "interchange"}:
            stop = props.pop("station_id")
            network["stations"][stop] = props | {"coordinates": coordinates}
            if kind == "interchange":
                network["transfers"].append({"id": stop, "station_ids": [stop], "lines": props["lines"]})
    screen = tomllib.loads(residential_planning.POLICY.read_text())["corridor_screen"]
    variants = central_parallel_routes.alternatives(network, None, None, screen=screen, protected_stations=PROTECTED)
    return network, screen, variants


def _parallel_m(network, screen):
    return sum(row["length_m"] for row in rail_duplication.screen(network["lines"], **screen)["runs"]
               if row["kind"] == "nearby_parallel")


def test_parallel_cuts_retain_rings_airport_and_destinations(pinned_layouts):
    network, screen, variants = pinned_layouts
    reference = _parallel_m(network, screen)
    for key in ("parallel-terminal-trims", "parallel-m01-turnback", "parallel-northern-gap"):
        result = variants[key]
        assert result["rejection_reason"] is None
        candidate = result["network"]
        assert candidate["topology"] == holistic_network.validate(candidate)
        assert all(candidate["lines"][line] == network["lines"][line] for line in ("M09", "M15", "C1"))
        assert all(candidate["stations"][stop]["coordinates"] == network["stations"][stop]["coordinates"]
                   for stop in PROTECTED)
        assert _parallel_m(candidate, screen) < reference * .7
        assert all(len(candidate["stations"][stop]["lines"]) > 1
                   for action in result["actions"] for stop in action["terminals"])


def test_interior_cut_requires_a_retained_rail_bridge(pinned_layouts):
    _, _, variants = pinned_layouts
    northern = variants["parallel-northern-gap"]
    m04 = next(action for action in northern["actions"] if action["line_id"] == "M04")
    assert m04["replacement_rail_path"] == {
        "lines": ["M09", "M01"], "transfer_id": "X-M01-M09-01", "route_km": pytest.approx(4.415),
    }
    assert northern["network"]["lines"]["M04-SE"]["station_ids"][0] == "X-M01-M04-01"
    rejected = variants["parallel-ring-gaps"]
    assert rejected["network"] is None
    assert "C2 gap has no bridge" in rejected["rejection_reason"]


def test_closed_platforms_retire_only_their_walking_links(pinned_layouts):
    network, screen, _ = pinned_layouts
    g09_platform = "G09-infill-15300"
    rg_platform = next(stop for stop in network["lines"]["RG1-92"]["station_ids"]
                       if network["stations"][stop]["lines"] == ["RG1-92"])

    def link(code, first, last):
        points = [network["stations"][stop]["coordinates"] for stop in (first, last)]
        return {"id": code, "station_ids": [first, last], "walks_m": [700, 710],
                "geometry": [points, points[::-1]]}

    affected = link("close-with-g09", g09_platform, rg_platform)
    retained = link("keep-both-platforms", network["lines"]["C1"]["station_ids"][0], "University")
    linked = network | {"station_site_links": [affected, retained]}
    holistic_network.validate(linked)
    variants = central_parallel_routes.alternatives(linked, None, None, screen=screen, protected_stations=PROTECTED)
    change = variants["parallel-terminal-trims"]
    assert change["network"]["station_site_links"] == [retained]
    retired = change["actions"][0]["removed_walking_links"][0]
    assert retired["station_ids"] == [g09_platform, rg_platform]
    assert retired["closed_station_ids"] == [g09_platform]
    assert all(variants[key]["network"]["station_site_links"] == [affected, retained]
               for key in ("parallel-m06-turnback", "parallel-m06-northern-gap"))

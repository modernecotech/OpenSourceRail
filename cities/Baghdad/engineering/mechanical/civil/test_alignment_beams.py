import math
from xml.etree import ElementTree

from shapely.geometry import Polygon, mapping

from cities.Baghdad import holistic_network
from cities.Baghdad.engineering.mechanical.civil import alignment_beams as design


def _coordinates(x, y):
    return [44.4 + x / holistic_network.LOCAL_METRES[0],
            33.3 + y / holistic_network.LOCAL_METRES[1]]


def _network(points, *, stations=None, junctions=()):
    stations = stations or {}
    return {
        "candidate_id": "synthetic-alignment-example",
        "lines": {"T": {"geometry": [_coordinates(*point) for point in points],
                        "station_ids": list(stations)}},
        "stations": {key: {"coordinates": _coordinates(*point)} for key, point in stations.items()},
        "track_junctions": list(junctions),
    }


def test_turning_stock_offset_radii_material_and_schedule():
    record = design.evaluate(_network([(0, 0), (1000, 0), (1000, 1000)]),
                             context={"layers": {"water": []}})
    route = record["routes"]["T"]
    total = record["totals"]
    curved = [row for row in route["bays"] if row["family"] == "curved_ugirder"]
    assert curved
    assert record["water_geometry_used"]
    assert math.isclose(sum(row["sweep_deg"] for row in curved), 90)
    assert all(math.isclose(row["track_pieces"]["outside"]["radius_m"]
                            - row["track_pieces"]["inside"]["radius_m"], design.PITCH_M)
               for row in curved)
    assert all(row["track_pieces"]["outside"]["sagitta_m"] <= design.MAX_SAGITTA_M
               for row in curved)
    assert total["inside_girders"] == total["outside_girders"] == len(curved)
    assert total["girders"] == 2 * len(route["bays"])
    assert total["candidate_loaded_trips"] == total["girders"]
    assert total["mould_occupation_h"] > 48 * total["girders"]
    assert total["launcher_paid_crew_h"] > total["assembly_operating_h"]
    assert total["incremental_allowance_usd"]["base"] > 0
    assert total["integrated_completion_day"] is None
    assert record["physical_acceptance"] is False
    assert math.isclose(route["reference_length_m"], route["bays"][-1]["reference_end_m"])
    assert "Turning bay T" in design.render_svg(record)
    ElementTree.fromstring(design.render_svg(record))
    dxf = design.render_dxf(record)
    assert "9\n$INSUNITS\n70\n6\n" in dxf
    assert dxf.count("0\nARC\n") == 6
    assert dxf.endswith("0\nEOF\n")


def test_water_station_and_turnout_take_precedence_without_phantom_stock():
    corners = [_coordinates(x, y) for x, y in [(140, -10), (320, -10), (320, 10), (140, 10)]]
    water = {"geometry": mapping(Polygon(corners))}
    junction = {"id": "turnout", "line_ids": ["T"], "coordinates": _coordinates(490, 0)}
    network = _network([(0, 0), (1000, 0)], stations={"S": (680, 0)}, junctions=[junction])
    record = design.evaluate(network, context={"layers": {"water": [water]}})
    route = record["routes"]["T"]
    by_family = record["by_family"]
    assert not route["turns"]
    assert math.isclose(route["wet_crossings"][0]["wet_length_m"], 180, rel_tol=1e-8)
    for key in ("river_crossing_hold", "junction_hold", "station_interface_hold"):
        assert by_family[key]["girders"] == 0
    assert record["totals"]["held_cost_usd"] is None
    assert by_family["straight_20m"]["girders"] > 0


def test_short_fillet_can_take_tangent_leads_and_sharp_bend_remains_held():
    shallow = math.radians(1)
    record = design.evaluate(_network([(0, 0), (300, 0),
                                       (300 + 300 * math.cos(shallow), 300 * math.sin(shallow))]))
    bay = record["representative_curved_bay"]
    assert bay["family"] == "short_curved_ugirder"
    assert math.isclose(bay["track_pieces"]["inside"]["arc_length_m"], design.MIN_SHORT_BAY_M)
    assert not record["water_geometry_used"]
    sharp = design.evaluate(_network([(0, 0), (19, 0), (19, 19)]))
    assert sharp["representative_curved_bay"] is None
    assert sharp["routes"]["T"]["turns"][0]["status"] == "held"
    assert sharp["by_family"]["sharp_or_constrained_turn_hold"]["girders"] == 0


def test_exact_shared_edge_is_held_on_both_traces():
    network = _network([(0, 0), (100, 0), (200, 0), (300, 0)])
    network["lines"]["U"] = {
        "geometry": [_coordinates(*point) for point in [(300, 100), (200, 0), (100, 0), (0, -100)]],
        "station_ids": [],
    }
    record = design.evaluate(network)
    shared = record["by_family"]["shared_alignment_hold"]
    register = record["shared_alignment_register"]
    assert shared["girders"] == 0
    assert len(register) == 1
    assert [trace["line_id"] for trace in register[0]["traces"]] == ["T", "U"]
    assert math.isclose(register[0]["physical_edge_m"], 100, rel_tol=1e-8)
    assert math.isclose(shared["route_length_m"], 200, rel_tol=1e-8)
    assert register[0]["fabrication_and_installation_cost_usd"] is None

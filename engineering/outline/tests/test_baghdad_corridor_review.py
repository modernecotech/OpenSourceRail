import json
from collections import Counter

from cities.Baghdad.corridor_review import OUTPUT, build


def test_public_map_is_reproducible_and_keeps_unlocated_waypoints_as_gaps():
    data = build()
    assert data == json.loads(OUTPUT.read_bytes())
    assert data["program_km"] == 148.2
    points = {}
    links = set()
    for feature in data["features"]:
        props = feature["properties"]
        if props["kind"] == "rfi_named":
            points[props["line"], props["order"]] = feature["geometry"]["coordinates"]
        elif props["kind"] == "named_place_sequence":
            links.add((props["line"], props["from_order"], props["to_order"]))
    assert len(points) == 39
    assert len(links) == 25
    assert links == {(line, order, order + 1) for line, order in points if (line, order + 1) in points}
    assert sum(map(len, data["unlocated_named_occurrences"].values())) == 13
    assert points["Red", 3] == [44.359445571899414, 33.36935207602251]
    assert Counter(f["properties"]["kind"] for f in data["features"])["proposed_population_anchor"] == 5

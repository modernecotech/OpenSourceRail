import pytest

from cities.Baghdad.holistic_gaps import prioritize
from cities.Baghdad.holistic_network import LOCAL_METRES


def place(x, y):
    return [(4_108_000 + x) / LOCAL_METRES[0], (3_704_000 + y) / LOCAL_METRES[1]]


@pytest.fixture
def network():
    return {
        "lines": {
            "A": {"name": "First line", "geometry": [place(1000, -1000), place(1000, 3500)],
                  "station_ids": ["start", "transfer"]},
            "B": {"name": "Second line", "geometry": [place(1000, 3500), place(8000, 3500)],
                  "station_ids": ["transfer", "end"]},
        },
        "stations": {
            "start": {"name": None, "coordinates": place(1000, -1000), "lines": ["A"]},
            "transfer": {"name": "Shared station", "coordinates": place(1000, 3500), "lines": ["A", "B"]},
            "end": {"name": "End", "coordinates": place(8000, 3500), "lines": ["B"]},
        },
    }


def test_rank_gaps_with_nonoverlapping_tiles_and_distinct_connection_distances(network):
    cells = [
        {"coordinates": place(500, 500), "people": 150, "beyond_1200_m": 100},
        {"coordinates": place(500, 1500), "people": 220, "beyond_1200_m": 200},
        {"coordinates": place(1500, 500), "people": 130, "beyond_1200_m": 0},
        {"coordinates": place(4500, 500), "people": 50, "beyond_1200_m": 50},
        {"coordinates": place(8500, 500), "people": 10, "beyond_1200_m": 0},
    ]
    first, second = gaps = prioritize(cells, network)
    assert gaps == prioritize(reversed(cells), network)
    assert sum(gap["beyond_1200_m"] for gap in gaps) == 350
    assert (first["rank"], first["people"], first["cell_count"]) == (1, 500, 3)
    assert first["bounds_wsen"][2] == second["bounds_wsen"][0]
    route_a, route_b = first["nearby_rail"]
    assert route_a["line_id"] == "A"
    assert route_a["alignment_distance_m"] == 500
    assert route_a["station_distance_m"] > 500
    assert route_a["station_name"] == "start"
    assert route_b["station_name"] == "Shared station"
    assert route_b["station_lines"] == ["A", "B"]


def test_reject_inconsistent_coverage_counts(network):
    with pytest.raises(ValueError, match="Invalid coverage cell"):
        prioritize([{"coordinates": place(500, 500), "people": 1, "beyond_1200_m": 2}], network)

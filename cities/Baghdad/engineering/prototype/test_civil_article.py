import csv
from copy import deepcopy
from io import StringIO
import math

import pytest

from cities.Baghdad import airport_integration
from cities.Baghdad.engineering.prototype import car, civil_article


def test_cage_coordinates_force_and_stage_quantities():
    record = car.build(airport_integration.build())
    r, files = civil_article.artifacts(record)
    beam = record["civil"]["track"]
    p = r["strand"]
    assert p["strand_count"] == 12 and p["embedded_strand_stock_m"] == 120
    assert p["service_sensitivity"][-1]["service_fibres"]["bottom_compression_mpa"] > 0
    assert p["strand_count"] - 2 < p["zero_bottom_tension_force_kn"] / (261 * 0.70 * 0.70)
    assert r["minimum_nominal_strand_to_bar_surface_gap_m"] > 0
    row = r["bar_schedule_one_beam"][0]
    assert row["developed_length_m"] == pytest.approx(
        1.898 + 1.298 + 0.4 + 2 * 0.036 * (math.pi / 2 - 2), abs=1e-6
    )
    assert (
        len(row["geometry"]["x_m"]) == row["pieces"]
        and len(set(row["geometry"]["x_m"])) == row["pieces"]
    )
    csv_rows = list(csv.DictReader(StringIO(files["beam-bar-strand-schedule.csv"].decode())))
    assert sum(float(row["nominal_stock_kg_per_beam"]) for row in csv_rows) == pytest.approx(
        r["bar_and_strand_kg_per_beam"]
    )
    lift = r["bearing_and_erection"]
    assert lift["two_loaded_legs_with_10pct_dynamic_allowance_kn_each"] == pytest.approx(
        2.2 * beam["sling_leg_kn_equal_four_point"]
    )
    assert r["station_interfaces"]["rainfall_runoff_l_s"][1]["l_s_per_bay"] == pytest.approx(
        100 * 40 * 0.95 / 3600
    )
    assert r["station_interfaces"]["measured_height_difference_m"] is None
    assert not r["fabrication_released"]
    bad = deepcopy(record)
    bad["opening"]["bundle"]["span_m"] = 20
    with pytest.raises(ValueError, match="matching"):
        civil_article.build(bad)

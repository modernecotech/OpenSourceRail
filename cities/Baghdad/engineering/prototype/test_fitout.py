import csv
import io
import json
from xml.etree.ElementTree import fromstring

import pytest

from cities.Baghdad import airport_integration
from cities.Baghdad.engineering.prototype import car, fitout


def test_bogie_coordinates_sheet_and_return_basis():
    article = car.build(airport_integration.build())
    files = fitout.artifacts(article)
    case = json.loads(files["fitout-interfaces.json"])
    assert fromstring(files["powered-bogie-sheet.svg"]).tag.endswith("svg")
    for b in case["bogies"]:
        assert len(b["stock_piece_ids"]) == 12
        assert b["local_axle_planes_x_mm"] == [-1050, 1050]
        assert [p["stock_face_gap_mm"] for p in b["pads"] if p["upper_piece"]] == [156, 156]
        assert sorted(p["local_face_centre_mm"][2] for p in b["pads"]) == [378] * 4 + [602] * 2
    assert case["bogies"][0]["signed_outward_travel_m"] == -case["bogies"][1]["signed_outward_travel_m"]
    rows = list(csv.DictReader(io.StringIO(files["returns/fitout.csv"].decode())))
    assert len(rows) == 8 and len({r["interface"] for r in rows}) == 8
    assert all(
        r["frame_revision"] == article["frame_revision"] and not r["as_built_value_and_units"]
        for r in rows
    )
    article["pieces"][0]["upper_m"][0] += 0.1
    with pytest.raises(ValueError, match="intact"):
        fitout.build(article)

from copy import deepcopy
import csv
import io
from xml.etree import ElementTree

import pytest
from cities.Baghdad import airport_integration
from cities.Baghdad.engineering.prototype import car


def test_compact_mesh_cut_schedule_and_portal():
    r, files = car.artifacts(airport_integration.build())
    exported_names = [
        line[2:] for line in files["car-and-bogies.obj"].decode().splitlines() if line.startswith("o ")
    ]
    assert exported_names == [p["id"] for p in r["pieces"]]
    rows = list(csv.DictReader(io.StringIO(files["revised-cuts.csv"].decode())))
    stock = sum(float(row["gross_mass_kg"]) * (2 if row["assembly"] == "bogie" else 1) for row in rows)
    assert abs(stock - r["mass"]["cut_kg_per_car"]) < 0.01
    assert len(exported_names) == 144
    assert {p["assembly"] for p in r["pieces"]} == {"body", "bogie-A", "bogie-B"}
    assert r["doorway"]["rough_widths_m"] == [1.360] * 8
    assert r["doorway"]["residual_m"] == pytest.approx(0.010)
    assert r["doorway"]["leaf_sweep"]["conservative_stock_box_intersections"] == []
    for result in r["body_vertical_screens"].values():
        assert (
            result["door_width"]["worst_width_loss_mm"]
            < result["door_width"]["combined_allocated_width_loss_mm"]
        )
    assert len(ElementTree.fromstring(files["portal-detail.svg"])) > 8
    assert r["opening"]["candidate_id"] == r["candidate_id"] != r["parent_candidate_id"]
    assert (
        r["opening"]["bundle"]["vehicle_revision"] == r["frame_revision"] != r["parent_frame_revision"]
    )
    assert r["opening"]["power"]["vehicle"]["mass_t"] == pytest.approx(r["planning_crowd_train_t"])
    assert r["civil"]["moving_load"]["max_live_moment_knm_sampled"] > 409.025
    assert r["civil"]["foundation_delta_kpa"] > 0
    assert r["civil"]["meshes"]["track-span"]["counted_volume_m3"] == pytest.approx(13.404)
    assert r["mass"]["complete_installed_tare_kg"] is None and not r["fabrication_released"]


def test_rejects_unbound_parent_service_and_physical_revision():
    p = airport_integration.build()
    changed = deepcopy(p)
    changed["opening"]["bundle"]["vehicle_revision"] += "old"
    with pytest.raises(ValueError, match="source-bound"):
        car.build(changed)
    p["service"]["peak_headway_s"] = 600
    with pytest.raises(ValueError, match="source-bound"):
        car.build(p)

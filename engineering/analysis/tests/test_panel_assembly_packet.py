"""Real represented assembly and demands; no installed-kit qualification."""

from copy import deepcopy
import csv
import json

import pytest

from engineering.analysis.tests.test_design_engine import scope
from engineering.design_engine import adapters
from engineering.design_engine.panel_assembly import packet, write_packet
from engineering.design_engine.registry import get
from engineering.panel_response.plate import solve


@pytest.fixture(scope="module")
def panel():
    charter = get("clipped-side-bay")
    row = adapters.compile_candidate(
        charter,
        scope(),
        dict(support_span_m=0.2, grade_density=80, core_m=0.0246, skin_m=0.0015),
    )
    adapters.screen(charter, row, lambda *args: None, None)
    response = solve(row["definition"]["contract"], mesh_size=0.12)
    row["definition"]["confirmation"] = {"refined": response}
    return row


def test_real_multibody_inventory_and_clip_force_correspondence(panel, tmp_path):
    report = write_packet(panel, tmp_path / "packet")
    assert report["represented_part_count"] == 556
    assert len(report["connections"]) == 48 and len(report["machining"]) == 672
    assert len(report["manufacturing_takeoff"]) == len(report["bill"]["parts"]) == 556
    assert sum(p["mass_kg"] for p in report["manufacturing_takeoff"]) == pytest.approx(
        report["represented_mass_kg"]
    )
    ids = {p["physical_id"] for p in report["manufacturing_takeoff"]}
    for joint in report["connections"]:
        assert set(joint["physical_part_ids"]) <= ids
        assert joint["maximum_recorded_axial_demand_n"] > 0
        assert joint["resistance_n"] is None and joint["preload_n"] is None
        assert not joint["locking_verified"]
    assert report["complete_installed_mass_kg"] is None
    assert not report["complete_installed_kit"] and not report["physical_release"]
    assert "perimeter seal profile" in report["unresolved_allocations"]
    with (tmp_path / "packet/manufacturing-takeoff.csv").open() as stream:
        assert len(list(csv.DictReader(stream))) == 556
    assert (
        json.loads((tmp_path / "packet/assembly-review.json").read_text())["candidate"]
        == panel["id"]
    )


@pytest.mark.parametrize(
    "damage", ["scope", "missing-clip", "duplicate", "nan", "stiffness", "missing-part"]
)
def test_mismatched_or_incomplete_actual_connection_evidence_rejected(panel, damage):
    row = deepcopy(panel)
    response = row["definition"]["confirmation"]["refined"]
    if damage == "scope":
        response["contract_sha256"] = "a" * 64
    elif damage == "missing-clip":
        response["attachments"].pop()
    elif damage == "duplicate":
        response["attachments"].append(response["attachments"][0])
    elif damage == "nan":
        response["attachments"][0]["force_n"] = float("nan")
    elif damage == "stiffness":
        response["attachments"][0]["stiffness_n_m"] = 0
    else:
        row["definition"]["contract"]["parts"].pop()
    with pytest.raises(ValueError):
        packet(row)

"""Exercise mismatches across the reference railway interfaces."""

import json

import pytest

from cities.Baghdad.engineering.simulation import reference_project as project


@pytest.fixture
def inputs():
    return json.loads(project.SITE.read_bytes()), json.loads(project.TRACK.read_bytes())


def test_reconcile_valid_project_with_open_functional_screen(inputs):
    site, _ = inputs
    result = project.reconcile(*inputs)
    assert result["service"]["headway_min"] == 30
    assert result["service"]["operating_screen"] == "passed"
    assert result["decision"]["functional_screen"]["status"] == "failed"
    assert result["decision"]["physical_acceptance"] is False
    assert result["horizontal_parent_id"] == site["civil"]["alignment_id"]
    assert result["civil"]["standard_placements"] + 2 == site["civil_stock"]["placements"]


@pytest.mark.parametrize("interface, message", [
    ("stop", "Stop chainage"),
    ("feeder", "Feeder chainages"),
    ("mass", "Operating mass"),
    ("viaduct", "Standard civil placements"),
    ("lot", "Wrong candidate in lot"),
    ("cash", "cash totals"),
])
def test_reject_different_downstream_inputs(inputs, interface, message):
    site, _ = inputs
    price = site["cash"]["layouts"][project.LAYOUT]
    if interface == "stop":
        site["stops"][1]["chainage_km"] += .01
    elif interface == "feeder":
        site["working_day"]["normal_by_layout"][project.LAYOUT]["site_chainages_m"][1] *= 1000
    elif interface == "mass":
        site["vehicle_loaded_mass_kg"]["central"] += 2500
    elif interface == "viaduct":
        project.only(price["lots"], lot_id="audited-standard-viaduct")["quantity"] += 2
    elif interface == "lot":
        project.only(price["lots"], lot_id="fleet")["supplier_scope"]["context"]["motion_candidate_id"] = "other"
    elif interface == "cash":
        project.only(price["lots"], lot_id="fleet")["usd"]["base"] += 1000
    with pytest.raises(ValueError, match=message):
        project.reconcile(*inputs)


def test_reject_horizontal_replay_for_graded_project(inputs):
    site, _ = inputs
    replay = json.loads(project.REPLAY.read_bytes())
    replay["alignment_id"] = site["horizontal_parent_id"]
    with pytest.raises(ValueError, match="different project"):
        project.control_evidence(project.reconcile(*inputs), site, replay)

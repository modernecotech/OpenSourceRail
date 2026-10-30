from copy import deepcopy

import pytest

from engineering import mass_ledger_audit
from engineering.station_rail import vehicle


def test_occurrence_mass_ledger_reconciles_selected_vehicle_candidate():
    candidate = vehicle.build()
    parent, _ = vehicle._read_parent(vehicle.ROOT)
    ledger = mass_ledger_audit.reconcile(candidate, parent)

    summary = ledger["summary"]
    assert ledger["candidate_id"] == "756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3"
    assert summary["account_row_count"] == 12
    assert summary["retained_source_occurrence_count"] == 2921
    assert summary["located_geometry_occurrence_count"] == 2482
    assert summary["accounted_tare_kg_per_car"] == pytest.approx(19221.998134341986)
    assert summary["located_geometry_mass_kg"] == pytest.approx(9131.798543498426)
    assert summary["residual_reference_or_unlocated_mass_kg"] == pytest.approx(10090.19959084356)
    assert summary["complete_installed_mass_kg"] is None
    assert summary["complete_installed_CG_m"] is None
    assert summary["axle_reactions"] is None

    geometry_ids = [row["occurrence_id"] for row in ledger["candidate_geometry_occurrences"]]
    assigned_ids = [
        occurrence_id
        for account in ledger["accounts"]
        for occurrence_id in account["candidate_geometry_occurrence_ids"]
    ]
    assert len(geometry_ids) == len(set(geometry_ids))
    assert sorted(geometry_ids) == sorted(assigned_ids)


def test_duplicate_geometry_occurrence_stops_mass_reconciliation():
    candidate = deepcopy(vehicle.build())
    parent, _ = vehicle._read_parent(vehicle.ROOT)
    candidate["geometry_parts"].append(deepcopy(candidate["geometry_parts"][0]))

    with pytest.raises(ValueError, match="Duplicate candidate geometry occurrence ID"):
        mass_ledger_audit.reconcile(candidate, parent)


def test_geometry_cannot_exceed_its_parent_mass_account():
    candidate = deepcopy(vehicle.build())
    parent, _ = vehicle._read_parent(vehicle.ROOT)
    body_part = next(part for part in candidate["geometry_parts"] if part["id"].startswith("comfort-shell/"))
    body_part["mass_kg"] += 8000

    with pytest.raises(ValueError, match="Located geometry exceeds retained system account"):
        mass_ledger_audit.reconcile(candidate, parent)


def test_mass_reconciliation_publication_replays_and_verifies(tmp_path):
    result = mass_ledger_audit.publish(output=tmp_path)
    verified = mass_ledger_audit.verify(output=tmp_path)

    assert result["manifest_id"] == verified["manifest_id"]
    assert verified["verified"] is True
    assert verified["complete_installed_mass_kg"] is None

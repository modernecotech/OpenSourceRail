from copy import deepcopy
import gzip
import json

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
    assert all(ledger[key] is False for key in (
        "engineering_accepted", "physical_accepted", "installed_mass_complete",
        "manufacturing_release", "operating_release"))
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


def test_direct_source_occurrence_links_are_disjoint_and_preserve_mass_totals():
    candidate = vehicle.build()
    parent, _ = vehicle._read_parent(vehicle.ROOT)
    ledger = mass_ledger_audit.reconcile(candidate, parent)
    source_rows = {row["occurrence_id"]: row for row in ledger["source_account_occurrences"]}
    geometry_rows = ledger["candidate_geometry_occurrences"]
    direct = [row for row in geometry_rows
              if row["source_occurrence_link_method"] == "exact-retained-source-occurrence-id-and-mass"]
    nested = [row for row in geometry_rows if row["source_geometry_part_id"] is not None]
    direct_ids = {row["occurrence_id"] for row in direct}
    nested_ids = {row["occurrence_id"] for row in nested}

    assert len(direct) == 750
    assert sum(row["mass_kg"] for row in direct) == pytest.approx(1324.3065409912926)
    assert len({row["source_occurrence_id"] for row in direct}) == 750
    assert direct_ids.isdisjoint(nested_ids)
    assert len(nested) == 1516
    assert sum(row["mass_kg"] for row in nested) == pytest.approx(1162.0399443609415)
    for row in direct:
        source_id = row["occurrence_id"].removeprefix("comfort-shell/")
        source = source_rows[source_id]
        assert row["source_occurrence_id"] == source_id
        assert row["source_occurrence_mass_kg"] == pytest.approx(source["mass_kg"])
        assert row["candidate_to_source_occurrence_mass_difference_kg"] == pytest.approx(0.0, abs=1e-7)
        assert row["source_geometry_part_id"] is None
        assert source["source_location_known"] is True
        assert row["account_id"] == "retained-comfort/" + source["source_system"]
        assert {link["candidate_geometry_occurrence_id"] for link in source["candidate_geometry_links"]} >= {row["occurrence_id"]}

    summary = ledger["summary"]
    assert summary["candidate_geometry_with_exact_source_occurrence_link_count"] == 750
    assert summary["candidate_geometry_with_exact_source_occurrence_link_mass_kg"] == pytest.approx(1324.3065409912926)
    assert summary["candidate_geometry_with_exact_source_identity_link_count"] == 2266
    assert summary["candidate_geometry_with_exact_source_identity_link_mass_kg"] == pytest.approx(2486.346485352234)
    assert summary["candidate_geometry_without_exact_source_identity_link_count"] == 216
    assert summary["candidate_geometry_without_exact_source_identity_link_mass_kg"] == pytest.approx(6645.452058146192)
    assert summary["accounted_tare_kg_per_car"] == pytest.approx(19221.998134341986)
    assert summary["located_geometry_mass_kg"] == pytest.approx(9131.798543498426)
    assert summary["residual_reference_or_unlocated_mass_kg"] == pytest.approx(10090.19959084356)
    assert summary["complete_installed_mass_kg"] is None


def test_direct_source_occurrence_link_rejects_mass_mismatch():
    candidate = deepcopy(vehicle.build())
    parent, _ = vehicle._read_parent(vehicle.ROOT)
    retained_ids = {row["id"] for row in mass_ledger_audit._retained_source_rows(parent)}
    part = next(row for row in candidate["geometry_parts"]
                if row["id"].startswith("comfort-shell/")
                and row["id"][len("comfort-shell/"):] in retained_ids)
    part["mass_kg"] += 0.25

    with pytest.raises(ValueError, match="Candidate geometry mass differs from its exact source occurrence"):
        mass_ledger_audit.reconcile(candidate, parent)


def test_direct_source_occurrence_link_rejects_cross_system_mapping():
    candidate = vehicle.build()
    parent, _ = vehicle._read_parent(vehicle.ROOT)
    parent = deepcopy(parent)
    retained_by_id = {row["id"]: row for row in mass_ledger_audit._retained_source_rows(parent)}
    part = next(row for row in candidate["geometry_parts"]
                if row["id"].startswith("comfort-shell/")
                and row["id"][len("comfort-shell/"):] in retained_by_id)
    source_id = part["id"][len("comfort-shell/"):]
    retained_by_id[source_id]["system"] = "glazing"

    with pytest.raises(ValueError, match="Directly linked source occurrence and candidate geometry belong to different mass accounts"):
        mass_ledger_audit.reconcile(candidate, parent)


def test_closure_worksheet_separates_source_mass_geometry_and_account_residuals():
    ledger, selected, _ = mass_ledger_audit._inputs(vehicle.ROOT)
    worksheet = mass_ledger_audit.build_closure_worksheet(ledger)

    assert worksheet["candidate_id"] == ledger["candidate_id"]
    assert worksheet["evaluation_id"] == selected["evaluation_id"]
    assert worksheet["selection_id"] == selected["selection_id"]
    assert worksheet["summary"]["record_count"] == 5418
    assert worksheet["summary"]["source_account_occurrence_count"] == 2924
    assert worksheet["summary"]["candidate_geometry_occurrence_count"] == 2482
    assert worksheet["summary"]["exact_source_occurrence_link_count"] == 750
    assert worksheet["summary"]["exact_source_occurrence_link_mass_kg"] == pytest.approx(1324.3065409912926)
    assert worksheet["summary"]["exact_source_geometry_link_count"] == 1516
    assert worksheet["summary"]["exact_source_identity_link_count"] == 2266
    assert worksheet["summary"]["candidate_geometry_without_exact_source_identity_link_count"] == 216
    assert worksheet["summary"]["account_residual_count"] > 0
    assert worksheet["summary"]["physically_installed_mass_kg"] is None
    assert worksheet["summary"]["complete_installed_CG_m"] is None
    assert worksheet["unknown_is_zero"] is False
    rows = worksheet["rows"]
    assert len({row["row_id"] for row in rows}) == len(rows)
    assert all(row["physically_installed_mass_kg"] is None for row in rows)
    assert all(row["installed_position_m"] is None for row in rows)
    assert all(row["lower_mass_bound_kg"] is None and row["upper_mass_bound_kg"] is None
               for row in rows)
    residual_rows = [row for row in rows if row["record_kind"] == "account-closure"
                     and row["accounting_residual_kg"] > 0]
    assert residual_rows
    assert all(row["mass_evidence_class"] == "accounting-residual-not-physical-component"
               and row["physically_installed_mass_kg"] is None for row in residual_rows)
    geometry_rows = [row for row in rows if row["record_kind"] == "candidate-geometry-occurrence"]
    assert all(row["candidate_geometry_centroid_m"] is not None
               and row["installed_position_m"] is None for row in geometry_rows)
    direct_rows = [row for row in geometry_rows
                   if row.get("source_occurrence_link_method") == "exact-retained-source-occurrence-id-and-mass"]
    assert len(direct_rows) == 750
    assert all(row["source_location_known"] is True
               and row["physically_installed_mass_kg"] is None
               and row["installed_position_m"] is None for row in direct_rows)


def test_duplicate_geometry_occurrence_stops_mass_reconciliation():
    candidate = deepcopy(vehicle.build())
    parent, _ = vehicle._read_parent(vehicle.ROOT)
    candidate["geometry_parts"].append(deepcopy(candidate["geometry_parts"][0]))

    with pytest.raises(ValueError, match="Duplicate candidate geometry occurrence ID"):
        mass_ledger_audit.reconcile(candidate, parent)


def test_geometry_cannot_exceed_its_parent_mass_account():
    candidate = deepcopy(vehicle.build())
    parent, _ = vehicle._read_parent(vehicle.ROOT)
    window_part = next(part for part in candidate["geometry_parts"]
                       if part["id"].startswith("comfort-shell/fixed-window/"))
    window_part["mass_kg"] += 8000

    with pytest.raises(ValueError, match="Located geometry exceeds retained system account"):
        mass_ledger_audit.reconcile(candidate, parent)


def test_mass_reconciliation_publication_replays_and_verifies(tmp_path):
    result = mass_ledger_audit.publish(output=tmp_path)
    verified = mass_ledger_audit.verify(output=tmp_path)
    compressed = (tmp_path / "mass-ledger.json.gz").read_bytes()
    worksheet_bytes = (tmp_path / "mass-closure-worksheet.json.gz").read_bytes()
    worksheet = json.loads(gzip.decompress(worksheet_bytes))
    ledger = json.loads(gzip.decompress(compressed))

    assert result["manifest_id"] == verified["manifest_id"]
    assert verified["verified"] is True
    assert verified["complete_installed_mass_kg"] is None
    assert result["closure_worksheet_record_count"] == 5418
    assert result["closure_worksheet_id"] == worksheet["worksheet_id"]
    assert worksheet["summary"]["physically_installed_mass_kg"] is None
    assert worksheet["summary"]["exact_source_occurrence_link_count"] == 750
    assert worksheet["summary"]["exact_source_identity_link_count"] == 2266
    assert ledger["summary"]["candidate_geometry_with_exact_source_occurrence_link_count"] == 750
    assert ledger["summary"]["candidate_geometry_with_exact_source_identity_link_count"] == 2266
    assert ledger["summary"]["accounted_tare_kg_per_car"] == pytest.approx(19221.998134341986)
    assert ledger["summary"]["located_geometry_mass_kg"] == pytest.approx(9131.798543498426)
    assert ledger["summary"]["residual_reference_or_unlocated_mass_kg"] == pytest.approx(10090.19959084356)
    direct_rows = [row for row in ledger["candidate_geometry_occurrences"]
                   if row["source_occurrence_link_method"] == "exact-retained-source-occurrence-id-and-mass"]
    assert len(direct_rows) == 750
    readme = (tmp_path / "README.md").read_text()
    assert "Exact retained source-occurrence IDs link 750 candidate geometry occurrences" in readme
    assert "2,266 of 2,482" in readme
    assert "mass-closure-worksheet.json.gz" in json.loads((tmp_path / "manifest.json").read_bytes())["files_sha256"]
    assert "mass closure worksheet" in (tmp_path / "README.md").read_text().lower()
    assert compressed[:4] == b"\x1f\x8b\x08\x00"
    assert compressed[4:8] == b"\x00\x00\x00\x00"
    assert compressed[9] == 255
    assert mass_ledger_audit._deterministic_gzip(b"stable") == mass_ledger_audit._deterministic_gzip(b"stable")

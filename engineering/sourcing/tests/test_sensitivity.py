import pytest

from engineering.station_rail.common import identity
from engineering.sourcing.sensitivity import mass_account_reconciliation_priority


def _worksheet():
    candidate = "a" * 64
    evaluation = "b" * 64
    selection = "c" * 64
    rows = []
    for account_id, residual in (("larger-account", "25"), ("smaller-account", "5")):
        row = {
            "record_kind": "account-closure",
            "candidate_id": candidate,
            "evaluation_id": evaluation,
            "selection_id": selection,
            "account_id": account_id,
            "accounted_source_mass_kg": "100",
            "candidate_geometry_mass_kg": str(100 - int(residual)),
            "accounting_residual_kg": residual,
            "source_occurrence_ids": [account_id + "/source"],
            "candidate_geometry_occurrence_ids": [account_id + "/geometry"],
            "evidence_needed": ["weigh and locate the installed items"],
        }
        row["row_id"] = identity(row)
        rows.append(row)
    worksheet = {
        "schema": "osr-v06-mass-closure-worksheet/1",
        "candidate_id": candidate,
        "evaluation_id": evaluation,
        "selection_id": selection,
        "summary": {
            "account_residual_count": 2,
            "accounted_tare_kg_per_car": 200,
            "located_geometry_mass_kg": 170,
            "accounting_residual_kg": 30,
            "complete_installed_mass_kg": None,
        },
        "rows": rows,
    }
    worksheet["worksheet_id"] = identity(worksheet)
    return worksheet


def test_mass_account_queue_ranks_reconciliation_gap_without_calling_it_uncertainty():
    result = mass_account_reconciliation_priority(_worksheet())
    assert [row["account_id"] for row in result["account_reconciliation_investigation_queue"]] == [
        "larger-account", "smaller-account"]
    assert result["account_reconciliation_investigation_queue"][0]["accounting_residual_kg"] == "25"
    assert result["account_reconciliation_investigation_queue"][0]["source_occurrence_count"] == 1
    assert len(result["account_reconciliation_investigation_queue"][0]["account_closure_row_id"]) == 64
    assert result["mass_uncertainty_bounds_available"] is False
    assert result["numeric_mass_sensitivity_rank_count"] == 0
    assert result["research_candidate_cost_ranks_combined"] is False
    assert result["summary"]["complete_installed_mass_kg"] is None
    assert result["summary"]["could_change_preferred"] is None


def test_mass_account_queue_rejects_stale_worksheet_identity():
    worksheet = _worksheet()
    worksheet["rows"][0]["accounting_residual_kg"] = "99"
    with pytest.raises(ValueError, match="worksheet identity"):
        mass_account_reconciliation_priority(worksheet)

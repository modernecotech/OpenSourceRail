"""Cost, RFQ and workforce drafts stay tied to one selected handoff."""

from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import tomllib

import pytest

from services.integration.osr_integration.v07_business import project


ROOT = Path(__file__).resolve().parents[1]


def _inputs():
    with (ROOT / "docs/reference-v07/digital/selected.toml").open("rb") as stream:
        selection = tomllib.load(stream)
    handoff = json.loads((ROOT / "docs/reference-v07/digital/production/handoff.json").read_text())
    return selection, handoff


def test_selected_project_view_reconciles_cash_and_quotations():
    selection, handoff = _inputs()
    result = project(selection, handoff)
    assert result["physical_candidate_id"] == selection["physical_candidate_id"]
    assert result["handoff_evaluation_id"] == handoff["evaluation_id"]
    assert len(result["monthly_direct_draw_usd_m"]) == 43
    assert sum(map(Decimal, result["monthly_direct_draw_usd_m"])) == Decimal("854.356")
    assert Decimal(result["installed_funding_envelope_usd_m"]) == Decimal("1025.2272")
    assert len(result["rfq_lines"]) == 41
    assert all(row["supplier_quote_usd"] is None and Decimal(row["planning_quantity"]) > 0
               for row in result["rfq_lines"])
    assert Decimal(result["known_direct_workshop_hours"]) > 0
    assert result["unmeasured_workshop_steps"]
    assert result["purchase_orders_created"] is result["erp_transactions_created"] is False
    assert result["payroll_usd"] is result["actual_cashflow_usd"] is None
    rated = project(selection, handoff, loaded_workshop_rate_usd_per_hour="25")
    assert Decimal(rated["planning_known_hours_labour_usd_within_capital"]) == (
        Decimal(result["known_direct_workshop_hours"]) * 25)
    assert rated["installed_funding_envelope_usd_m"] == result["installed_funding_envelope_usd_m"]
    assert rated["payroll_usd"] is None


def test_mixed_candidate_or_mutated_handoff_is_rejected():
    selection, handoff = _inputs()
    altered = deepcopy(handoff)
    altered["physical_candidate_id"] = "different"
    with pytest.raises(ValueError, match="identity differs"):
        project(selection, altered)
    altered = deepcopy(handoff)
    altered["production"]["beam_count"] += 1
    with pytest.raises(ValueError, match="identity differs"):
        project(selection, altered)

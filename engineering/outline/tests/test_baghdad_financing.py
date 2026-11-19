import json
from pathlib import Path
import runpy

import pytest

CITY = Path(__file__).resolve().parents[3] / "cities/Baghdad"


def test_schedules_reconcile_by_network_and_year():
    results = json.loads((CITY / "system-results.json").read_text())
    published = json.loads((CITY / "financing-scenarios.json").read_text())
    assert published == runpy.run_path(str(CITY / "financing.py"))["build"]()
    for name, network in published["networks"].items():
        inputs = results["networks"][name]
        for case in network["cases"].values():
            annual = case["annual"]
            debt = 0
            for row in annual:
                debt += row["borrowing"] - row["principal"]
                assert debt == pytest.approx(row["closing_debt"], abs=1e-8)
                uses = sum(row[k] for k in ("capital", "operations", "renewals", "interest", "principal"))
                assert uses == pytest.approx(row["buyer_cash"] + row["borrowing"])
            assert abs(debt) < 1e-8
            assert sum(row["capital"] for row in annual) == pytest.approx(
                inputs["selected_construction_cashflow"]["total_capital_usd_m"])
            assert sum(row["renewals"] for row in annual) == pytest.approx(
                sum(event["usd_m"] for event in inputs["selected_renewals_usd_m"]))

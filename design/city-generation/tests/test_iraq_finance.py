"""Cash conservation, origin eligibility, native currency and liquidity risks."""
import tomllib
from pathlib import Path

import pytest

from osr_scenario.iraq_finance import run_case, scheduled_requirements, validate

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def config():
    return tomllib.loads((ROOT / "lib/templates/iraq-funding.toml").read_text())


def inputs():
    return ([{"bucket": "rolling_stock", "total_usd": 1_000_000, "imported_usd": 350_000}],
            [{"bucket": "rolling_stock", "budget_usd": 1_000_000, "imported_share": .35,
              "planned_start_day": 0, "planned_finish_day": 1040}])


def test_schedule_uses_working_calendar_and_reconciles(config):
    buckets, contracts = inputs()
    requirements = scheduled_requirements(contracts, buckets, config)
    assert requirements[0]["month"] == 0  # mobilisation before NTP
    assert requirements[-1]["month"] == 53  # four working years plus retention
    assert sum(r["capex_usd"] for r in requirements) == 1_000_000
    assert sum(r["eligible_invoice_usd"] for r in requirements) == pytest.approx(350_000 * .85)
    contracts[0]["budget_usd"] = 500_000
    with pytest.raises(ValueError, match="do not reconcile"):
        scheduled_requirements(contracts, buckets, config)


def test_funding_conservation_drawn_interest_and_full_repayment(config):
    requirements = scheduled_requirements(*reversed(inputs()), config)
    result = run_case(requirements, 240_000, 100_000, config)
    metrics = result["metrics"]
    assert sum(metrics["capital_sources_usd"].values()) == pytest.approx(1_000_000)
    assert metrics["max_cash_balance_residual_usd"] < .0001
    assert max(metrics["final_debt_balances_native"].values()) < .01
    initial = result["monthly"][0]
    assert initial["chinese_export_credit_interest_native"] == pytest.approx(initial["chinese_export_credit_draw_usd"] * .05/24)
    assert initial["domestic_bonds_draw_native"] == pytest.approx(initial["domestic_bonds_draw_usd"]*1300)
    assert initial["revenue_usd"] == 0


def test_unavailable_export_finance_and_late_government_stay_unfunded(config):
    requirements = scheduled_requirements(*reversed(inputs()), config)
    denied = run_case(requirements, 240_000, 100_000, config, export_available=False)
    assert denied["metrics"]["capital_sources_usd"]["chinese_export_credit"] == 0
    assert denied["metrics"]["uncovered_export_finance_usd"] > 0
    assert denied["metrics"]["peak_monthly_unfunded_cash_usd"] > 0
    delayed = run_case(requirements, 240_000, 100_000, config, government_delay_months=6)
    assert delayed["monthly"][0]["government_capital_received_usd"] == 0
    assert delayed["metrics"]["peak_monthly_unfunded_cash_usd"] > 0


def test_delay_does_not_extend_loan_grace_and_fx_does_not_index_fares(config):
    requirements = scheduled_requirements(*reversed(inputs()), config)
    base = run_case(requirements, 240_000, 100_000, config)
    delayed = run_case(requirements, 240_000, 100_000, config, commissioning_delay_months=24)
    assert delayed["monthly"][55]["revenue_usd"] == 0
    assert delayed["monthly"][55]["chinese_export_credit_principal_native"] == base["monthly"][55]["chinese_export_credit_principal_native"]
    fx = run_case(requirements, 240_000, 100_000, config, fx_factor=1.35)
    assert fx["monthly"][90]["revenue_usd"] == pytest.approx(base["monthly"][90]["revenue_usd"]/1.35)
    assert fx["monthly"][90]["domestic_bonds_principal_native"] == pytest.approx(base["monthly"][90]["domestic_bonds_principal_native"])


def test_short_bullet_has_redemption_and_no_refinancing(config):
    result = run_case(scheduled_requirements(*reversed(inputs()), config), 0, 100_000, config, retail_bullet=True)
    assert result["monthly"][48]["domestic_bonds_principal_native"] == pytest.approx(result["monthly"][0]["domestic_bonds_draw_native"])
    assert result["monthly"][48]["domestic_bonds_draw_native"] == 0
    assert result["metrics"]["max_cash_balance_residual_usd"] < .001


def test_zero_rates_and_invalid_shares(config):
    for name in ("chinese_export_credit", "domestic_bonds", "bank_credit"):
        config[name]["annual_rate"] = 0
    result = run_case(scheduled_requirements(*reversed(inputs()), config), 0, 0, config)
    assert result["metrics"]["total_interest_usd_equivalent"] == pytest.approx(0, abs=1e-7)
    assert max(result["metrics"]["final_debt_balances_native"].values()) < .01
    config["eligible_imports"]["rolling_stock"]["bogies"] = .9
    with pytest.raises(ValueError, match="exceed"):
        validate(config)
    config["eligible_imports"]["rolling_stock"]["bogies"] = .4
    config["model"]["government_share_of_remainder"] = .8
    with pytest.raises(ValueError, match="sum to one"):
        validate(config)
    config["model"]["government_share_of_remainder"] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        validate(config)

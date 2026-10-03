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


def test_baghdad_25_percent_is_total_capital_and_other_cities_unchanged(config):
    from osr_scenario.iraq_finance import city_funding_config

    selected = city_funding_config(config, "baghdad")
    requirements = scheduled_requirements(*reversed(inputs()), selected)
    result = run_case(requirements, 240_000, 100_000, selected)
    sources = result["metrics"]["capital_sources_usd"]
    assert sources["government"] == pytest.approx(250_000)
    residual = 1_000_000 - 250_000 - sources["chinese_export_credit"]
    assert sources["domestic_bonds"] == pytest.approx(residual * .75)
    assert sources["bank_credit"] == pytest.approx(residual * .25)
    assert result["metrics"]["max_cash_balance_residual_usd"] < .01
    assert result["metrics"]["total_government_cash_usd"] > sources["government"]
    for name in ("samawah", "mosul"):
        standalone = city_funding_config(config, name)
        assert "government_share_of_total" not in standalone["model"]
        assert standalone["model"]["government_share_of_remainder"] == .60
    assert "government_share_of_total" not in config["model"]


def test_baghdad_declined_china_does_not_increase_government_share(config):
    from osr_scenario.iraq_finance import city_funding_config

    selected = city_funding_config(config, "baghdad")
    requirements = scheduled_requirements(*reversed(inputs()), selected)
    base = run_case(requirements, 0, 0, selected)
    denied = run_case(requirements, 0, 0, selected, export_available=False)
    for tranche in ("government", "domestic_bonds", "bank_credit"):
        assert denied["metrics"]["capital_sources_usd"][tranche] == base["metrics"]["capital_sources_usd"][tranche]
    assert denied["metrics"]["uncovered_export_finance_usd"] == pytest.approx(base["metrics"]["capital_sources_usd"]["chinese_export_credit"])


def test_total_share_rejects_overallocation(config):
    from osr_scenario.iraq_finance import city_funding_config

    selected = city_funding_config(config, "baghdad")
    selected["model"]["government_share_of_total"] = .95
    with pytest.raises(ValueError, match="exceed capital uses"):
        run_case(scheduled_requirements(*reversed(inputs()), selected), 0, 0, selected)
    selected["model"]["government_share_of_total"] = 1.1
    with pytest.raises(ValueError, match="finite"):
        validate(selected)


def test_baghdad_imports_split_usd_cash_and_loan_inside_25_percent(config):
    from osr_scenario.iraq_finance import city_funding_config, eligible_components

    selected = city_funding_config(config, "baghdad")
    buckets, contracts = inputs()
    requirements = scheduled_requirements(contracts, buckets, selected)
    assert sum(r["invoice_budget_usd"] for r in eligible_components(buckets, selected)) == pytest.approx(350_000)
    result = run_case(requirements, 240_000, 100_000, selected)
    metrics = result["metrics"]
    assert metrics["capital_sources_usd"]["chinese_export_credit"] == pytest.approx(175_000)
    assert metrics["government_capital_usd_cash"] == pytest.approx(175_000)
    assert metrics["government_capital_iqd_cash"] == pytest.approx(75_000*1300)
    assert metrics["capital_sources_usd"]["government"] == pytest.approx(250_000)
    assert sum(metrics["capital_sources_usd"].values()) == pytest.approx(1_000_000)
    for row in result["monthly"]:
        assert row["government_capital_usd_cash"] + row["government_capital_iqd_cash"]/row["iqd_per_usd"] == pytest.approx(row["government_capital_received_usd"])
        assert row["chinese_export_credit_draw_usd"] == pytest.approx(.5*row["imported_purchases_usd"])
    delayed = run_case(requirements, 0, 0, selected, government_delay_months=6)
    assert delayed["monthly"][0]["government_capital_usd_cash"] == 0
    assert delayed["monthly"][6]["government_capital_usd_cash"] == pytest.approx(result["monthly"][0]["government_capital_usd_cash"])


def test_unqualified_import_basket_does_not_change_other_city_eligibility(config):
    from osr_scenario.iraq_finance import city_funding_config, eligible_components

    buckets, contracts = inputs()
    standalone = city_funding_config(config, "mosul")
    assert sum(r["invoice_budget_usd"] for r in eligible_components(buckets, standalone)) == pytest.approx(350_000*.85)
    selected = city_funding_config(config, "baghdad")
    selected["model"]["government_usd_share_of_imports"] = .60
    with pytest.raises(ValueError, match="cover the import basket exactly"):
        validate(selected)

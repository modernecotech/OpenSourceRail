import pytest

from cities.Baghdad import phased_finance
from cities.Baghdad.financing import CASES, cash_schedule


def test_phased_cash_and_staged_revenue_close_to_first_programme():
    result = phased_finance.build()
    rows = {row["year"]: row for row in result["annual"]}
    full = result["central_iraq_full_service"]
    assert result["full_annual_train_km"] == 24666408
    assert sorted(result["groups"]) == ["Airport", "Blue", "Green", "Purple", "Red", "White", "Yellow"]
    first = rows[2029]
    first_km = sum(result["groups"][name]["annual_train_km"] for name in ("Airport", "Green"))
    assert first["train_km"] == pytest.approx(first_km / 2)
    assert first["fixed_payroll_m"] == pytest.approx(full["payroll_m"] / 2)
    assert first["net_fares_m"] == pytest.approx(
        full["farebox_m"] * (first_km / result["full_annual_train_km"]) * 0.4 / 2
    )
    assert rows[2028]["train_km"] == 0
    assert rows[2032]["operations_m"] == pytest.approx(full["opex_m"])
    assert rows[2032]["net_fares_m"] < rows[2033]["net_fares_m"] == pytest.approx(full["farebox_m"])
    assert sum(r["capital_m"] for r in rows.values()) == pytest.approx(full["installed_m"])
    assert sum(r["principal_m"] for r in rows.values()) == pytest.approx(full["installed_m"] * 0.5)
    assert rows[2061]["closing_debt_m"] == pytest.approx(0)
    for row in rows.values():
        assert row["public_cash_m"] == pytest.approx(
            row["capital_m"]
            - row["borrowing_m"]
            + row["interest_m"]
            + row["principal_m"]
            + row["operations_m"]
            + row["renewals_m"]
            - row["net_fares_m"]
        )


def test_all_lines_at_once_reproduces_parent_renewal_and_service_years():
    cfg, report, network = phased_finance.airport_opening.opening_inputs()
    names = list(report["networks"]["first"]["groups"])
    control = {
        "demand_fraction_by_service_half_year": [1],
        "openings": [{"construction_year": 6, "month": 1, "groups": names}],
    }
    result = phased_finance.build(control)
    service = [r for r in result["annual"] if r["train_km"] > 0]
    base = cash_schedule(network, *CASES["mixed_debt"])
    assert len(service) == 30 and service[0]["year"] == 2032
    assert service[0]["net_fares_m"] == pytest.approx(result["central_iraq_full_service"]["farebox_m"])
    for a, b in zip(result["annual"], base["annual"]):
        assert a["renewals_m"] == pytest.approx(b["renewals"])
        assert a["interest_m"] == pytest.approx(
            b["interest"] * result["central_iraq_full_service"]["capital_factor"]
        )
    control["openings"][0]["groups"] = names[:-1] + ["M05"]
    with pytest.raises(ValueError, match="first-programme"):
        phased_finance.build(control)

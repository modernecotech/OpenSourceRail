"""Procurement-origin and capital-source accounting for OSR programmes.

City CAPEX excludes the shared national trainset factory. Imported content is
the minimum foreign-currency requirement; locally supplied content can be
funded with domestic bonds, public equity, or other local sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "Cargo.toml").is_file():
            return parent
    raise RuntimeError("cannot locate repository root")


_CAPEX = tomllib.loads(
    (_repo_root() / "lib/templates/capex-costs.toml").read_text()
)
IMPORTED_SHARE: dict[str, float] = {
    str(key): float(value)
    for key, value in _CAPEX["procurement_origin"]["imported_share"].items()
}
EPC_FRACTION = float(_CAPEX["overhead"]["epc_fraction"])
NATIONAL_FACTORY_PER_VEHICLE_USD = float(
    _CAPEX["production_plant"]["per_vehicle_usd"]
)


@dataclass(frozen=True)
class CapitalBucket:
    name: str
    total_usd: float
    imported_share: float

    @property
    def imported_usd(self) -> float:
        return self.total_usd * self.imported_share

    @property
    def local_usd(self) -> float:
        return self.total_usd - self.imported_usd


@dataclass(frozen=True)
class CapitalBreakdown:
    buckets: tuple[CapitalBucket, ...]

    @property
    def total_usd(self) -> float:
        return sum(bucket.total_usd for bucket in self.buckets)

    @property
    def imported_usd(self) -> float:
        return sum(bucket.imported_usd for bucket in self.buckets)

    @property
    def local_usd(self) -> float:
        return sum(bucket.local_usd for bucket in self.buckets)

    @property
    def imported_share(self) -> float:
        return self.imported_usd / self.total_usd if self.total_usd else 0.0

    @property
    def local_share(self) -> float:
        return self.local_usd / self.total_usd if self.total_usd else 0.0


@dataclass(frozen=True)
class CapitalFundingPlan:
    breakdown: CapitalBreakdown
    construction_years: int
    tenor_years: int
    external_rate: float
    local_bond_rate: float
    external_grant_usd: float
    external_debt_usd: float
    local_bond_usd: float
    local_equity_usd: float

    @property
    def repayment_years(self) -> int:
        return max(self.tenor_years - self.construction_years, 1)

    @property
    def annual_external_capital_draw_usd(self) -> float:
        return self.breakdown.imported_usd / self.construction_years

    @property
    def annual_local_capital_draw_usd(self) -> float:
        return self.breakdown.local_usd / self.construction_years

    @property
    def annual_local_bond_issuance_usd(self) -> float:
        return self.local_bond_usd / self.construction_years

    @property
    def annual_local_equity_draw_usd(self) -> float:
        return self.local_equity_usd / self.construction_years

    @property
    def annual_external_debt_service_usd(self) -> float:
        return annuity(self.external_debt_usd, self.external_rate, self.repayment_years)

    @property
    def annual_local_bond_service_usd(self) -> float:
        return annuity(self.local_bond_usd, self.local_bond_rate, self.repayment_years)

    @property
    def annual_debt_service_usd(self) -> float:
        return self.annual_external_debt_service_usd + self.annual_local_bond_service_usd

    @property
    def annual_grace_interest_usd(self) -> float:
        return (
            self.external_debt_usd * self.external_rate
            + self.local_bond_usd * self.local_bond_rate
        )

    @property
    def annual_public_construction_commitment_usd(self) -> float:
        return self.annual_local_equity_draw_usd + self.annual_grace_interest_usd


def annuity(principal: float, rate: float, years: int) -> float:
    if principal <= 0.0:
        return 0.0
    if rate <= 0.0:
        return principal / max(years, 1)
    factor = 1.0 - (1.0 + rate) ** -max(years, 1)
    return principal * rate / factor if factor > 0.0 else principal / max(years, 1)


def _cost(costs: dict, stem: str) -> float:
    if f"{stem}_usd" in costs:
        return float(costs[f"{stem}_usd"])
    return 0.0


def city_capital_breakdown(
    costs: dict,
    solar_plant_usd: float = 0.0,
) -> CapitalBreakdown:
    """Return a city-only CAPEX breakdown; national factory is excluded."""

    values = {
        "civil": _cost(costs, "civil_subtotal"),
        "stations": _cost(costs, "stations"),
        "depots": _cost(costs, "depots"),
        "rolling_stock": _cost(costs, "rolling_stock"),
        "solar_plant": max(0.0, float(solar_plant_usd)),
        "signalling": _cost(costs, "signalling"),
        "charging_microgrid": _cost(costs, "charging_microgrid"),
        "epc_overhead": _cost(costs, "epc_overhead"),
    }
    return breakdown_from_values(values)


def breakdown_from_values(values: dict[str, float]) -> CapitalBreakdown:
    buckets = tuple(
        CapitalBucket(
            name=name,
            total_usd=max(0.0, float(value)),
            imported_share=IMPORTED_SHARE[name],
        )
        for name, value in values.items()
        if float(value) > 0.0
    )
    return CapitalBreakdown(buckets=buckets)


def aggregate_breakdowns(
    breakdowns: list[CapitalBreakdown],
    *,
    national_factory_usd: float = 0.0,
) -> CapitalBreakdown:
    values: dict[str, float] = {}
    for breakdown in breakdowns:
        for bucket in breakdown.buckets:
            values[bucket.name] = values.get(bucket.name, 0.0) + bucket.total_usd
    if national_factory_usd > 0.0:
        values["production_plant"] = national_factory_usd
        values["epc_overhead"] = values.get("epc_overhead", 0.0) + (
            national_factory_usd * EPC_FRACTION
        )
    return breakdown_from_values(values)


def funding_plan(
    breakdown: CapitalBreakdown,
    country_finance: dict,
) -> CapitalFundingPlan:
    construction_years = max(int(country_finance.get("capex_grace_years", 5)), 1)
    tenor_years = max(
        int(
            country_finance.get(
                "concessional_loan_tenor_years",
                max(int(country_finance.get("loan_tenor_years", 25)), 40),
            )
        ),
        construction_years + 1,
    )
    external_rate = float(
        country_finance.get(
            "green_concessional_loan_rate",
            country_finance.get("multilateral_loan_rate", 0.045),
        )
    )
    local_bond_rate = float(country_finance.get("sovereign_bond_rate", 0.07))
    grant_share_of_total = max(
        0.0, float(country_finance.get("climate_development_grant_share", 0.0))
    )
    external_grant = min(
        breakdown.imported_usd,
        breakdown.total_usd * grant_share_of_total,
    )
    external_debt = breakdown.imported_usd - external_grant
    local_bond_share = min(
        1.0,
        max(
            0.0,
            float(country_finance.get("local_bond_share_of_local_capex", 0.80)),
        ),
    )
    local_bond = breakdown.local_usd * local_bond_share
    local_equity = breakdown.local_usd - local_bond
    return CapitalFundingPlan(
        breakdown=breakdown,
        construction_years=construction_years,
        tenor_years=tenor_years,
        external_rate=external_rate,
        local_bond_rate=local_bond_rate,
        external_grant_usd=external_grant,
        external_debt_usd=external_debt,
        local_bond_usd=local_bond,
        local_equity_usd=local_equity,
    )


def bucket_rows(breakdown: CapitalBreakdown) -> list[dict[str, float | str]]:
    return [
        {
            "bucket": bucket.name,
            "total_usd": bucket.total_usd,
            "imported_share": bucket.imported_share,
            "imported_usd": bucket.imported_usd,
            "local_share": 1.0 - bucket.imported_share,
            "local_usd": bucket.local_usd,
        }
        for bucket in breakdown.buckets
    ]

"""Planning cash for a GIS site study using the existing Airport ledger."""

from copy import deepcopy
from hashlib import sha256
from math import isclose
import tomllib

from . import audit_feeder_cost, audit_production, production, scenario


LAYOUTS = ("radial30", "paired6")
OPENING = "opening-direct"
OPERATIONS = "first-full-year-operations"
RENEWAL = "renewal-schedule"
OMISSIONS = (
    "Exceptional offsite network reinforcement and utility service charges beyond the per-site tie-in proxy.",
    "Unmapped property, exceptional structures, owner possessions and work outside the supplied site lots.",
    "Tax, customs, financing, escalation, disruption claims and extraordinary equipment replacement.",
)


def _costs(values):
    if not isinstance(values, dict) or set(values) != set(production.PRICES):
        raise ValueError("A site-study price needs low, base and high amounts")
    values = {case: audit_production.quantity(values[case], "planning lot price") for case in production.PRICES}
    if not values["low"] <= values["base"] <= values["high"]:
        raise ValueError("Site-study price bounds must be ordered")
    return values


def _site_rows(rows, layout, alignment_id):
    result = []
    for row in rows:
        if (not isinstance(row, dict)
                or not all(isinstance(row.get(field), str) and row[field].strip()
                           for field in ("lot_id", "source_unit", "cost_evidence"))
                or row.get("group") not in (OPENING, OPERATIONS, RENEWAL)):
            raise ValueError(f"Invalid {layout} site-study lot scope")
        if row.get("alignment_id", alignment_id) != alignment_id:
            raise ValueError("A site cash lot references another Airport alignment")
        year = row.get("year")
        if ((row["group"] == RENEWAL and (type(year) is not int or not 1 <= year <= 30))
                or (row["group"] != RENEWAL and year is not None)):
            raise ValueError("Use an operating year only for a renewal lot")
        quantity = audit_production.quantity(row.get("quantity"), "site quantity")
        values = _costs(row.get("usd"))
        if quantity == 0 and any(values.values()):
            raise ValueError("A nonzero site cost needs a positive scope quantity")
        result.append({**deepcopy(row), "usd": values, "year": year, "estimate_kind": "GIS planning allowance"})
    return result


def _feeder_price_ranges(sensitivity):
    parts = (
        "railway_side_supply_sites_and_plant",
        "protected_positive_and_return_paths",
        "breakers_ties_and_branch_points",
    )
    opening, upkeep, component_prices = {}, {}, {name: {} for name in parts}
    for case in production.PRICES:
        result = sensitivity["cases"][case]
        for name in parts:
            component_prices[name][case] = audit_production.quantity(result["parts_usd"][name], name)
        part_total = sum(component_prices[name][case] for name in parts)
        opening[case] = audit_production.quantity(result["known_rail_side_direct_subtotal_usd"], "feeder subtotal")
        if not isclose(opening[case], part_total, abs_tol=.01):
            raise ValueError("Feeder price components disagree with the subtotal")
        upkeep[case] = audit_production.quantity(result["rail_side_annual_upkeep_usd"], "feeder upkeep")
    return _costs(opening), _costs(upkeep), component_prices


def _fill_feeder(rows, sensitivity, archive, rates):
    """Carry priced returns intact and fill only mutually exclusive open scopes."""
    by_id = {row["lot_id"]: row for row in rows}
    site_count = sensitivity["quantities"]["dc_source_groups"]
    opening, upkeep, parts = _feeder_price_ranges(sensitivity)

    for lot_id, values, overlapping_lots in (
        ("revised-feeder-package", opening, {"traction-line", "traction-sites", "six-site-parallel"}),
        ("revised-feeder-upkeep", upkeep, {"opex-feeder", "six-site-parallel-upkeep"}),
    ):
        if lot_id in by_id and by_id.keys() & overlapping_lots:
            raise ValueError("An audited feeder package overlaps a legacy price lot")
        row = by_id.get(lot_id)
        if row is not None and row["usd"] is None:
            row.update(usd=values, cost_evidence="Layout-specific rail-side planning rate sensitivity",
                       estimate_kind="simulated feeder allowance", source_id=sensitivity["sensitivity_id"],
                       source_date=sensitivity["source_date"])

    if "offsite-feed" not in by_id:
        source = archive["offsite-feed"]
        prices = _costs({case: source[f"{case}_usd"] * site_count / source["quantity"] for case in production.PRICES})
        rows.append({**audit_production.make_lot(
            "offsite-feed", OPENING, site_count, "DC source groups", prices,
            "Dated Baghdad archive allowance per utility tie-in applied to the simulated site count."
        ), "estimate_kind": "transferred budget allowance", "source_date": source["estimate_date"],
            "source_lot_id": source["lot_id"]})

    renewal_lots = any(row["lot_id"] in audit_production.FEEDER_RENEWAL_LOTS
                       or row["lot_id"].startswith("feeder-renewal-") for row in rows)
    # An owner-scoped or legacy renewal programme could cover part of the same asset.
    # Do not stack a whole-system proxy over any of those events.
    if renewal_lots:
        return False

    source_year = archive["renewal-grid-site-power-electronics"]["operating_year"]
    protection_year = archive["renewal-line-section-protection"]["operating_year"]
    path_year = archive["renewal-line-power-equipment"]["operating_year"]
    if protection_year != archive["renewal-midpoint-tie-equipment"]["operating_year"]:
        raise ValueError("The archived line protection and tie renewal years differ")
    historic_sites = archive["traction-sites"]["base_usd"]
    historic_line = archive["traction-line"]
    historic_path = historic_line["quantity"] * rates["protected_conductor_per_track_km"] * 1e6
    historic_protection = historic_line["base_usd"] - historic_path
    historic_protection_replacement = (
        archive["renewal-line-section-protection"]["base_usd"]
        + archive["renewal-midpoint-tie-equipment"]["base_usd"]
    )
    if min(historic_sites, historic_path, historic_protection) <= 0:
        raise ValueError("Archived feeder opening costs need positive source, path and protection scopes")
    fractions = (
        ("source-electronics", source_year, "railway_side_supply_sites_and_plant",
         archive["renewal-grid-site-power-electronics"]["base_usd"] / historic_sites),
        ("protection", protection_year, "breakers_ties_and_branch_points",
         historic_protection_replacement / historic_protection),
        ("line-power", path_year, "protected_positive_and_return_paths",
         archive["renewal-line-power-equipment"]["base_usd"] / historic_path),
    )
    for key, operating_year, component, fraction in fractions:
        values = _costs({case: parts[component][case] * fraction for case in production.PRICES})
        rows.append({**audit_production.make_lot(
            f"simulated-feeder-renewal-{key}", RENEWAL, 1, "renewal event", values,
            "Archived Baghdad replacement timing and cost fraction applied to the matched rail-side component.",
            year=operating_year
        ), "estimate_kind": "simulated renewal allowance", "source_id": sensitivity["sensitivity_id"],
            "source_date": sensitivity["source_date"], "replacement_price_fraction": fraction,
            "installed_price_component": component})
    return True


def evaluate(audit, site_lots_by_layout):
    """Apply explicit site and feeder planning allowances to matched audited prices."""
    alignment_id = audit["alignment"]["alignment_id"]
    if (set(audit["production"]) != set(LAYOUTS) or set(site_lots_by_layout) != set(LAYOUTS)
            or set(audit["feeder_price_sensitivities"]) != set(LAYOUTS)):
        raise ValueError("Simulated cash needs both Airport operating and pricing layouts")
    _, _, estimate, _, _, _, hashes = production.sources()
    archive = {row["lot_id"]: row for row in estimate["lots"]}
    rate_bytes = audit_feeder_cost.SYSTEM.read_bytes()
    rate_digest = sha256(rate_bytes).hexdigest()
    rates = tomllib.loads(rate_bytes.decode())["power_price_allowances_usd_m"]
    layouts = {}
    for layout in LAYOUTS:
        model = audit["production"][layout]
        context = model["inputs"]
        sensitivity = audit["feeder_price_sensitivities"][layout]
        if (context["alignment_id"] != alignment_id or context["feeder"]["name"] != layout
                or context["vehicle_candidate_id"] != audit["vehicle"]["candidate_id"]
                or context["civil_row_id"] != audit["civil_quotation"]["audit_row_id"]
                or context["source_pricing"] != hashes["sourcing-estimate.json"]
                or sensitivity["layout"] != layout
                or sensitivity["source_sha256"]["cities/Baghdad/system.toml"] != rate_digest
                or sensitivity["feeder_physical_id"] != scenario._id(dict(alignment_id=alignment_id, feeder=context["feeder"]))
                or sensitivity["quantities"]["dc_source_groups"] != model["quantities"]["grid_sites"]):
            raise ValueError("Simulated cash received a different Airport candidate or pricing scope")
        audit_production.require_identity(model, "evaluation_id", scenario._id, "Production audit")
        audit_production.require_identity(sensitivity, "sensitivity_id", scenario._id, "Feeder sensitivity")

        rows = deepcopy(model["pricings"])
        if len({row["lot_id"] for row in rows}) != len(rows):
            raise ValueError("Audited ledger contains duplicate lots")
        simulated_renewal = _fill_feeder(rows, sensitivity, archive, rates)
        rows.extend(_site_rows(site_lots_by_layout[layout], layout, alignment_id))
        if len({row["lot_id"] for row in rows}) != len(rows):
            raise ValueError("A site allowance duplicates an existing Airport cash lot")
        costs = [row for row in rows if row["usd"] is not None]
        remaining = [row["lot_id"] for row in rows if row["usd"] is None]
        if not simulated_renewal and "feeder-renewals" in model["unpriced_lots"]:
            remaining.append("feeder-renewals")
        operation = model["operation_basis"]
        cash = production.cash_profile(
            costs, model["cash"]["service_start_year"],
            operation["annual_paid_journeys_proxy"], operation["net_usd_per_paid_journey"], False
        )
        # Document the named low/base/high ranges without republishing
        # uncalibrated synthetic percentiles from the legacy cash function.
        cash.pop("sensitivity")
        for profile in cash["profiles"].values():
            profile["renewals_30y_undiscounted_usd"] = sum(row["renewals_usd"] for row in profile["cash_by_year"])
        layouts[layout] = dict(
            layout=layout, alignment_id=alignment_id, production_evaluation_id=model["evaluation_id"],
            feeder_sensitivity_id=sensitivity["sensitivity_id"], feeder_physical_id=sensitivity["feeder_physical_id"],
            lots=rows, cash=cash, remaining_unpriced_lots=remaining, scope_omissions=OMISSIONS,
            operation_basis=operation, operating_screen=audit["decision"]["candidates"][layout]["operating_screen"],
        )

    comparison = audit["feeder_price_sensitivities"]["paired6"]["priced_cash_break_even"]
    if comparison is None:
        raise ValueError("Simulated cash needs the matched service comparison")
    result = dict(
        schema="osr-baghdad-airport-site-cash/1",
        alignment_id=alignment_id,
        source_audit_evaluation_id=audit["evaluation_id"],
        source_rates_sha256=hashes["sourcing-estimate.json"],
        power_rate_source_sha256=rate_digest,
        status="costed simulated planning scope",
        price_basis="constant 2026 USD; explicit low/base/high scenarios",
        scope="Existing opening cash schedule and 30 operating years, including attributable renewals.",
        service_comparison=dict(
            ordinary_service_comparable=comparison["ordinary_service_comparable"],
            matched_through_required_duties=comparison["achieved_service_comparable"],
            unmatched_duties=comparison["operating_comparison"]["unmatched_duties"],
            failed_operating_layouts=comparison["operating_comparison"]["failed_operating_layouts"],
        ),
        layouts=layouts,
    )
    return {**result, "site_cash_id": scenario._id(result)}

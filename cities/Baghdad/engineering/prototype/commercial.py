"""Apply documented Airport field returns to the same service and buyer cash schedule."""

from datetime import date
from hashlib import file_digest, sha256
from math import isfinite
from pathlib import Path
import tomllib

from cities.Baghdad import airport_finance, airport_opening, financing
from engineering.outline.baghdad_system import _id


def form(opening):
    return {
        "candidate_id": opening["candidate_id"],
        "opening_evaluation_id": opening["evaluation_id"],
        "price_basis": "constant 2026 USD",
        "site_replacements": {},
        "demand_survey": None,
        "public_allocations_usd_m": {},
        "supplier_prices": airport_finance.quote_form(opening),
        "documents": {},
    }


def number(value, label, *, positive=False):
    try:
        valid = type(value) in (float, int) and isfinite(value) and value >= 0 and (not positive or value > 0)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f"Invalid {label}")
    return value


def iso_date(value):
    if not isinstance(value, str):
        raise ValueError("Use a calendar date in YYYY-MM-DD format")
    result = date.fromisoformat(value)
    if result.isoformat() != value:
        raise ValueError("Use a calendar date in YYYY-MM-DD format")
    return result


def has_document(name, docs):
    return isinstance(name, str) and name in docs


def evidence(docs, directory):
    """Limit custody to named local attachments. A hash authenticates bytes, not their signer."""
    if not isinstance(docs, dict):
        raise ValueError("Provide a document mapping")
    result = {}
    for name, item in docs.items():
        if not isinstance(name, str) or not name or Path(name).name != name or name in (".", ".."):
            raise ValueError("Each document needs a local filename")
        if (
            not isinstance(item, dict)
            or item.keys() != {"sha256", "issuer", "date"}
            or not str(item["issuer"]).strip()
            or not isinstance(item["issuer"], str)
        ):
            raise ValueError("Each document needs a digest, issuer and date")
        iso_date(item["date"])
        if directory is None:
            raise ValueError("Supply the directory containing the original attachments")
        path = Path(directory).resolve() / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing or changed attachment {name}")
        with path.open("rb") as attachment:
            if file_digest(attachment, "sha256").hexdigest() != item["sha256"]:
                raise ValueError(f"Missing or changed attachment {name}")
        result[name] = dict(item)
    return result


def survey(row, docs, service, days):
    expected = {
        "document",
        "sample_date_from",
        "sample_date_to",
        "observed_days",
        "od",
        "net_usd_per_paid_journey",
    }
    if not isinstance(row, dict) or row.keys() != expected or not has_document(row["document"], docs):
        raise ValueError("Provide survey provenance, dates, OD counts and net fare")
    first, last = (iso_date(row[k]) for k in ("sample_date_from", "sample_date_to"))
    sample = row["observed_days"]
    if type(sample) is not int or not 1 <= sample <= (last - first).days + 1:
        raise ValueError("Observed days must fit the survey interval")
    stops = {s["id"]: s["fraction"] * service["group"]["one_way_km"] for s in service["patterns"][0]}
    if not isinstance(row["od"], list) or not row["od"]:
        raise ValueError("Supply separate surveyed journeys for each counted OD pair")
    seen, paid, journeys, passenger_km = set(), 0, 0, 0.0
    for line in row["od"]:
        if not isinstance(line, dict) or line.keys() != {"from", "to", "all", "paying"}:
            raise ValueError("Survey rows require origin, destination, all and paying")
        a, b, total, paying = (line[k] for k in ("from", "to", "all", "paying"))
        if (
            not isinstance(a, str)
            or not isinstance(b, str)
            or a not in stops
            or b not in stops
            or a == b
            or (a, b) in seen
            or type(total) is not int
            or type(paying) is not int
            or not 0 <= paying <= total
        ):
            raise ValueError("Check stop IDs, unique OD pairs and counted passengers")
        seen.add((a, b))
        journeys += total
        paid += paying
        passenger_km += total * abs(stops[a] - stops[b])
    annual_paid = days * paid / sample
    return {
        "journeys_per_sample_day": journeys / sample,
        "paid_per_sample_day": paid / sample,
        "annual_passenger_km": days * passenger_km / sample,
        "annual_net_fares_usd_m": annual_paid * number(row["net_usd_per_paid_journey"], "net fare") / 1e6,
        "annualisation_days": days,
        "sample_days": sample,
        "scope": "Surveyed OD pairs extrapolated at the sample daily mean. Seasonal demand, peak loads and mode capture require independent review.",
    }


def assess(opening, service, cfg, submission=None, directory=None):
    inputs = airport_opening.CITY / "system.toml"
    cfg_bytes = inputs.read_bytes()
    service_id = _id({k: v for k, v in service.items() if k != "evaluation_id"})
    opening_eval = _id(
        {
            "bundle": opening["bundle"],
            "sources": opening["sources"],
            "service": service_id,
            "power": opening["power"]["evaluation_id"],
            "feeder": opening["section_power"]["evaluation_id"],
        }
    )
    if (
        opening["candidate_id"] != _id(opening["bundle"])
        or service_id != service["evaluation_id"]
        or opening_eval != opening["evaluation_id"]
        or cfg != tomllib.loads(cfg_bytes.decode())
        or sha256(cfg_bytes).hexdigest() != opening["sources"]["cities/Baghdad/system.toml"]
    ):
        raise ValueError("Return needs the matched opening, service and published price assumptions")
    basis = form(opening)
    data = basis if submission is None else submission
    if (
        not isinstance(data, dict)
        or data.keys() != basis.keys()
        or any(data[k] != basis[k] for k in ("candidate_id", "opening_evaluation_id", "price_basis"))
    ):
        raise ValueError("Financial return belongs to another physical design, price basis or evaluation")
    docs = evidence(data["documents"], directory)
    quotes = data["supplier_prices"]
    if not isinstance(quotes, dict):
        raise ValueError("Supply the matching supplier price form")
    priced = airport_finance.evaluate(
        opening, cfg, cfg["service_plan"]["departures_per_hour_direction"], quotes
    )
    for lot in priced["procurement_changes"].values():
        if lot["review_reference"] not in docs:
            raise ValueError("Each price return must identify its underlying attachment")
    fields = data["site_replacements"]
    base_sites = opening["iraq_site_estimate"]["scenarios"]["base"]["items"]
    if not isinstance(fields, dict) or not fields.keys() <= base_sites.keys():
        raise ValueError("Unknown site scope")
    revised = {}
    for scope, entry in fields.items():
        old = base_sites[scope]
        if (
            not isinstance(entry, dict)
            or entry.keys() != {"document", "unit", "quantity", "unit_usd"}
            or not has_document(entry["document"], docs)
            or entry["unit"] != old["unit"]
        ):
            raise ValueError(f"Unmatched local works return for {scope}")
        if (
            entry["unit"] in ("turnouts", "forecourt", "sites", "crossings")
            and type(entry["quantity"]) is not int
        ):
            raise ValueError(f"Return a whole number of {entry['unit']}")
        cost = (
            number(entry["quantity"], "quantity")
            * number(entry["unit_usd"], "site price", positive=True)
            / 1e6
        )
        number(cost, "extended site price")
        revised[scope] = {"direct_usd_m": cost, "displaced_direct_usd_m": old["direct_usd_m"], **entry}
    rates = cfg["capital_rates_usd_m"]
    factor = (1 + rates["design_fraction"] + rates["testing_fraction"]) * (
        1 + rates["project_allowance_fraction"]
    )
    central = priced["market_scenarios"]["central"]
    capital = central["capital_usd_m"] + factor * sum(
        x["direct_usd_m"] - x["displaced_direct_usd_m"] for x in revised.values()
    )
    days = cfg["vehicle"]["service_days_per_year"]
    demand = survey(data["demand_survey"], docs, service, days) if data["demand_survey"] is not None else None
    fares = demand["annual_net_fares_usd_m"] if demand is not None else central["annual_fares_usd_m"]
    schedule = priced["phased_cash"]["annual"]
    draws = [
        {"year": r["year"], "capital_usd_m": capital * r["capital"] / central["capital_usd_m"]}
        for r in schedule
        if r["capital"] > 0
    ]
    if capital <= 0:
        raise ValueError("Invalid revised opening capital")
    cash = financing.cash_schedule(
        {
            "selected_construction_cashflow": {
                "annual_capital_draw": draws,
                "full_service_start_year_assumption": draws[-1]["year"] + 1,
            },
            "selected_annual_opex_usd_m": {"total": central["annual_opex_usd_m"]},
            "selected_renewals_usd_m": priced["renewals"],
        },
        *financing.CASES["mixed_debt"],
    )
    allocations = data["public_allocations_usd_m"]
    if not isinstance(allocations, dict) or not allocations.keys() <= {str(r["year"]) for r in schedule}:
        raise ValueError("Public allocation years must match the phased cash schedule")
    for row, old in zip(cash["annual"], schedule, strict=True):
        share = old["service_fraction"]
        row.update(
            operations=share * central["annual_opex_usd_m"], net_fares=share * fares, service_fraction=share
        )
        row["buyer_cash"] = (
            row["capital"]
            - row["borrowing"]
            + row["interest"]
            + row["principal"]
            + row["operations"]
            + row["renewals"]
        )
        row["public_cash_after_fares"] = row["buyer_cash"] - row["net_fares"]
        allocation = allocations.get(str(row["year"]))
        row["documented_allocation_usd_m"] = None
        row["uncovered_usd_m"] = None
        if str(row["year"]) in allocations:
            if (
                not isinstance(allocation, dict)
                or allocation.keys() != {"document", "amount"}
                or not has_document(allocation["document"], docs)
            ):
                raise ValueError("Each budget allocation requires a source document and an amount")
            amount = number(allocation["amount"], "allocation")
            row.update(
                documented_allocation_usd_m=amount,
                uncovered_usd_m=max(0.0, row["public_cash_after_fares"] - amount),
            )
    result = {
        "candidate_id": opening["candidate_id"],
        "opening_evaluation_id": opening["evaluation_id"],
        "price_basis": basis["price_basis"],
        "source_documents": docs,
        "site_replacements": revised,
        "matched_supplier_lots": priced["procurement_changes"],
        "demand_survey": demand,
        "priced_capital_usd_m": capital,
        "annual_operating_cost_usd_m": central["annual_opex_usd_m"],
        "annual_net_fares_usd_m": fares,
        "annual_operating_support_usd_m": central["annual_opex_usd_m"] - fares,
        "annual_cash": cash["annual"],
        "price_gaps": priced["unpriced"],
        "opening_date": None,
        "funded_opening_capital_usd_m": None,
        "authorised_for_purchase": False,
    }
    result["evaluation_id"] = _id([result, data])
    return result

"""Compare the stated scope of independent ERP quotations in constant 2026 USD."""
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json


def _amount(value, field):
    if not isinstance(value, (int, float, Decimal, str)) or isinstance(value, bool):
        raise ValueError(f"{field} requires an explicit nonnegative amount")
    try:
        number = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"Invalid {field}") from error
    if not number.is_finite() or number < 0 or number > Decimal("1e18"):
        raise ValueError(f"Invalid {field}")
    return number


def _usd(value):
    return float(value.quantize(Decimal(".01"))) if value is not None else None


def _renewals(schedule):
    if schedule is None:
        return None
    if not isinstance(schedule, dict):
        raise ValueError("Supply the renewal schedule by operating year")
    result = {}
    for year, cost in schedule.items():
        if not isinstance(year, str) or year not in {str(y) for y in range(1, 31)}:
            raise ValueError("Renewal years run from 1 through 30")
        result[int(year)] = _amount(cost, "renewal")
    return result


def _lifecycle(period, direct, upkeep, schedule):
    if upkeep is None or schedule is None:
        return None
    capital = direct
    if period == "annual":
        if upkeep != 0:
            raise ValueError("Annual service is already included in the period price")
        capital, upkeep = Decimal(0), direct
    elif period == "scheduled":
        if upkeep != 0 or sum(schedule.values()) != direct:
            raise ValueError("Scheduled quotation must allocate exactly its period price by year with zero separate upkeep")
        capital = Decimal(0)
    return capital + sum((upkeep + schedule.get(y, 0)) / Decimal("1.04") ** y for y in range(1, 31))


def compare_lot(packet, lot_id, offers):
    """Return price differences and scope holds. Identity or unit mismatches reject the run."""
    lots = [row for row in packet["lots"] if row["lot_id"] == lot_id]
    if len(lots) != 1:
        raise ValueError("Select one unique estimate lot")
    lot = lots[0]
    period = lot["price_period"]
    if period not in ("one-time", "annual", "scheduled"):
        raise ValueError("Unknown price period")
    low, base, high = [
        None if lot.get(name) is None else _amount(lot[name], name)
        for name in ("low_usd", "base_usd", "high_usd")
    ]
    if (low is None) != (high is None) or (low is not None and low > high):
        raise ValueError("Invalid estimate interval")
    equivalent_low, equivalent_base, equivalent_high = low, base, high
    quantities = lot.get("scenario_quantities")
    if quantities:
        # Some local works scenarios vary both the unit price and the quantity.
        # Compare competing quotations at the actual enquiry quantity.
        qty = _amount(lot["quantity"], "enquiry quantity")
        same_quantity = []
        for label, total in zip(("low", "base", "high"), (low, base, high)):
            scenario_qty = _amount(quantities[label], "scenario quantity")
            same_quantity.append(total * qty / scenario_qty if total is not None and scenario_qty else None)
        equivalent_low, equivalent_base, equivalent_high = same_quantity
    seen_suppliers, seen_quotes, kinds = set(), set(), set()
    rows = []
    for offer in offers:
        if any(offer.get(k) != packet[k] for k in ("candidate_id", "evaluation_id")) or offer.get("lot_id") != lot_id:
            raise ValueError("Quotation must identify the exact candidate, estimate edition and lot")
        if (offer.get("currency") != "USD" or offer.get("unit") != lot["unit"]
                or _amount(offer.get("quantity"), "offered quantity") != _amount(lot["quantity"], "lot quantity")):
            raise ValueError("Quotation currency, unit and quantity must match the estimate")
        supplier, quotation = offer.get("supplier"), offer.get("quotation")
        if not all(isinstance(v, str) and v.strip() for v in (supplier, quotation)):
            raise ValueError("Supplier and quotation IDs are required")
        if supplier in seen_suppliers or quotation in seen_quotes:
            raise ValueError("Use one active quotation per independent supplier")
        kind = offer.get("evidence_kind")
        if kind not in ("supplier-offer", "software-fixture"):
            raise ValueError("Identify the source of each price")
        kinds.add(kind)
        if len(kinds) > 1:
            raise ValueError("Fixture and supplier offers require separate comparisons")
        seen_suppliers.add(supplier)
        seen_quotes.add(quotation)
        direct = _amount(offer.get("direct_usd"), "extended quotation price")
        upkeep = offer.get("annual_upkeep_usd")
        if upkeep is not None:
            upkeep = _amount(upkeep, "annual upkeep")
        schedule = _renewals(offer.get("renewals_usd"))
        pv = _lifecycle(period, direct, upkeep, schedule)
        if (period == "scheduled" and lot.get("operating_year") is not None and schedule is not None
                and any(year != lot["operating_year"] and cost for year, cost in schedule.items())):
            raise ValueError("Scheduled renewal must match the requested operating year")
        exclusions = offer.get("exclusions")
        if exclusions is not None and (not isinstance(exclusions, list)
                or not all(isinstance(e, str) and e.strip() for e in exclusions)):
            raise ValueError("List every deviation or explicitly declare full scope")
        reasons = []
        if exclusions is None:
            reasons.append("coverage unconfirmed")
        elif exclusions:
            reasons.append("supplier exclusions require reconciliation")
        complete = not reasons
        if upkeep is None:
            reasons.append("annual upkeep unquoted")
        if schedule is None:
            reasons.append("renewals unquoted")
        band = None
        if complete and equivalent_low is not None and equivalent_high is not None:
            band = "below" if direct < equivalent_low else "above" if direct > equivalent_high else "within"
        rows.append(dict(supplier=supplier, quotation=quotation, evidence_kind=kind,
                         direct_usd=_usd(direct), annual_upkeep_usd=_usd(upkeep),
                         renewals_usd=None if schedule is None else {str(y): _usd(v) for y, v in sorted(schedule.items())},
                         exclusions=exclusions, comparable_direct=complete, estimate_band_position=band,
                         difference_from_base_usd=_usd(direct - equivalent_base) if complete and equivalent_base is not None else None,
                         pv_30y_4pct_usd=_usd(pv) if complete else None, holds=reasons))
    rows.sort(key=lambda r: (r["supplier"], r["quotation"]))
    direct_prices = [r["direct_usd"] for r in rows if r["comparable_direct"]]
    pv_prices = [r["pv_30y_4pct_usd"] for r in rows if r["pv_30y_4pct_usd"] is not None]
    result = dict(schema="osr-lot-quotation-comparison/1", candidate_id=packet["candidate_id"],
                  estimate_evaluation_id=packet["evaluation_id"], lot_id=lot_id, price_period=period,
                  currency_basis="constant 2026 USD", period_benchmark_usd=dict(low=_usd(low), base=_usd(base), high=_usd(high)),
                  enquiry_quantity_benchmark_usd=dict(low=_usd(equivalent_low), base=_usd(equivalent_base), high=_usd(equivalent_high)),
                  scope_comparable_suppliers=len(direct_prices), whole_life_comparable_suppliers=len(pv_prices),
                  direct_spread_usd=round(max(direct_prices)-min(direct_prices), 2) if len(direct_prices) >= 2 else None,
                  pv_spread_usd=round(max(pv_prices)-min(pv_prices), 2) if len(pv_prices) >= 2 else None,
                  offers=rows, selection=None, procurement_authorized=False, physical_acceptance="open")
    result["comparison_id"] = sha256(json.dumps(result, sort_keys=True, separators=(",", ":"),
                                                allow_nan=False).encode()).hexdigest()
    return result

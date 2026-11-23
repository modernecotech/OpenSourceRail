"""Apply explicit, comparable supplier offers to the Airport opening capital allowance."""

from decimal import Decimal

from .sourcing_contract import (
    amount_usd,
    calendar_date,
    decimal_value,
    digest,
    estimate_payload,
    exact_text,
    one_lot,
)

ALLOWANCE_FRACTIONS = {
    "design-assurance": Decimal("0.08"),
    "integrated-test": Decimal("0.025"),
    "programme-allowance": Decimal("0.20"),
}


def _allowances(direct):
    design = direct * ALLOWANCE_FRACTIONS["design-assurance"]
    test = direct * ALLOWANCE_FRACTIONS["integrated-test"]
    project = (direct + design + test) * ALLOWANCE_FRACTIONS["programme-allowance"]
    return dict(zip(ALLOWANCE_FRACTIONS, (design, test, project), strict=True))


def _usd(value):
    return float(amount_usd(value, Decimal(1)))


def _central(value):
    return decimal_value(value, "central amount", places=18, positive=True)


def _same_amount(amount, published):
    # The published packet calculates monetary amounts using binary floats.
    return abs(amount - _central(published)) < Decimal("0.005")


def _baseline(packet):
    if (
        packet.get("schema") != "baghdad-airport-sourcing-estimates/1"
        or packet.get("price_basis") != "constant 2026 USD"
    ):
        raise ValueError("Provide the published Airport opening estimate")
    groups = packet.get("additive_groups", {})
    direct_group = groups.get("opening-direct", {})
    owner_group = groups.get("opening-allowances", {})
    direct = {
        lot["lot_id"]: lot for lot in packet["lots"] if lot.get("inclusion_group") == "opening-direct"
    }
    owner_lots = owner_group.get("lot_ids", [])
    direct_lots = direct_group.get("lot_ids", [])
    if (
        not direct or set(direct_lots) != direct.keys() or len(direct_lots) != len(direct)
        or set(owner_lots) != ALLOWANCE_FRACTIONS.keys() or len(owner_lots) != len(ALLOWANCE_FRACTIONS)
        or any(group.get("price_period") != "one-time" for group in (direct_group, owner_group))
    ):
        raise ValueError("The Airport opening direct and allowance schedules are incomplete")

    direct_total = sum(_central(lot.get("base_usd")) for lot in direct.values())
    allowances = _allowances(direct_total)
    owner_total = sum(allowances.values())
    if (
        not _same_amount(direct_total, direct_group.get("base_usd"))
        or not _same_amount(owner_total, owner_group.get("base_usd"))
        or not _same_amount(
            direct_total + owner_total, packet.get("subtotal_opening_priced_allowances", {}).get("base_usd")
        )
        or any(
            lot.get("inclusion_group") != "opening-allowances" or lot.get("price_period") != "one-time"
            or not _same_amount(allowances[key], lot.get("base_usd"))
            for key in ALLOWANCE_FRACTIONS for lot in (one_lot(packet, key),)
        )
    ):
        raise ValueError("The published central budget does not reconcile to its allowance rules")
    return direct, direct_total, allowances


def _matching_quote(rows, quotation):
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("Provide the native quotation comparison and supplier traces")
    matches = [row for row in rows if row.get("quotation") == quotation]
    if len(matches) != 1:
        raise ValueError("Selected quotation must have one active offer and supplier trace")
    return matches[0]


def _replacement(packet, response, quotation, direct):
    if not isinstance(response, dict):
        raise ValueError("Provide the native RFQ comparison for the selected quotation")
    rfq = exact_text(response.get("rfq"), "RFQ")
    project = exact_text(response.get("project"), "Project")
    date = calendar_date(response.get("as_of"))
    lot_id = exact_text(response.get("lot_id"), "lot ID", 100)
    lot = direct.get(lot_id)
    if (
        lot is None or lot.get("price_period") != "one-time"
        or lot.get("overlaps_lot_ids") or lot.get("alternative_to_lot_ids")
        or lot.get("base_usd") is None
    ):
        raise ValueError("Select a priced, non-overlapping opening direct lot")
    report = response.get("comparison")
    if not isinstance(report, dict):
        raise ValueError("Provide the native quotation comparison")
    comparison_id = digest({key: value for key, value in report.items() if key != "comparison_id"})
    if (
        type(response.get("rfq_docstatus")) is not int or response["rfq_docstatus"] != 1
        or report.get("schema") != "osr-lot-quotation-comparison/1"
        or report.get("candidate_id") != packet["candidate_id"]
        or report.get("estimate_evaluation_id") != packet["evaluation_id"]
        or report.get("lot_id") != lot_id or report.get("price_period") != "one-time"
        or report.get("currency_basis") != packet["price_basis"]
        or report.get("comparison_id") != comparison_id
    ):
        raise ValueError("RFQ comparison does not match the active Airport estimate and lot")

    trace = _matching_quote(response.get("suppliers"), quotation)
    offer = _matching_quote(report.get("offers"), quotation)
    supplier = exact_text(offer.get("supplier"), "supplier")
    if (
        trace.get("supplier") != supplier or trace.get("status") != "received"
        or not calendar_date(trace.get("recorded_on")) <= date <= calendar_date(trace.get("valid_until"))
    ):
        raise ValueError("Selected quotation must be current on the comparison date")
    if (
        offer.get("evidence_kind") != "supplier-offer"
        or offer.get("comparable_direct") is not True
        or offer.get("exclusions") != []
    ):
        raise ValueError("Selected quotation must cover the direct scope without unresolved exclusions")

    quoted = decimal_value(offer.get("direct_usd"), "quoted direct amount", places=2, positive=True)
    displaced = _central(lot["base_usd"])
    return quoted - displaced, {
        "lot_id": lot_id, "rfq": rfq, "quotation": quotation, "supplier": supplier,
        "recorded_on": trace["recorded_on"], "valid_until": trace["valid_until"], "as_of": date.isoformat(),
        "comparison_id": comparison_id, "comparison_receipt_sha256": digest(response),
        "quantity": lot["quantity"], "unit": lot["unit"],
        "displaced_central_direct_usd": _usd(displaced), "quoted_direct_usd": _usd(quoted),
        "direct_delta_usd": _usd(quoted - displaced),
        "comparison_holds": offer["holds"],
        "project": project,
    }


def opening_scenario(packet, selections):
    """Replace each selected opening direct allowance once.

    Selections contain (native compare_rfq response, exact quotation name) pairs.
    The ERP caller supplies freshly read, permission-checked comparisons on the
    same date. This function validates identity and arithmetic for replay.
    """
    packet = estimate_payload(packet)
    if not isinstance(selections, (list, tuple)) or not selections:
        raise ValueError("Select one or more current quotations")
    direct, original_direct, original_allowances = _baseline(packet)
    replacements, delta = [], Decimal(0)
    lots, rfqs, quotations = set(), set(), set()
    for selection in selections:
        if not isinstance(selection, (tuple, list)) or len(selection) != 2:
            raise ValueError("Provide a comparison and one named quotation per selected RFQ")
        response, quotation = selection
        change, replacement = _replacement(packet, response, exact_text(quotation, "quotation"), direct)
        lot_id, rfq = replacement["lot_id"], replacement["rfq"]
        if lot_id in lots or rfq in rfqs or quotation in quotations:
            raise ValueError("Use each opening direct lot, RFQ and quotation only once")
        if replacements and any(replacement[key] != replacements[0][key] for key in ("project", "as_of")):
            raise ValueError("Use one Project and comparison date for all replacements")
        lots.add(lot_id)
        rfqs.add(rfq)
        quotations.add(quotation)
        delta += change
        replacements.append(replacement)

    revised_direct = original_direct + delta
    revised_allowances = _allowances(revised_direct)
    original_opening = original_direct + sum(original_allowances.values())
    revised_opening = revised_direct + sum(revised_allowances.values())
    result = {
        "schema": "osr-opening-price-scenario/1",
        "candidate_id": packet["candidate_id"],
        "estimate_evaluation_id": packet["evaluation_id"],
        "opening_evaluation_id": packet["opening_evaluation_id"],
        "project": replacements[0]["project"], "as_of": replacements[0]["as_of"],
        "price_basis": packet["price_basis"],
        "replacements": sorted(replacements, key=lambda row: row["lot_id"]),
        "original_central_direct_usd": _usd(original_direct),
        "revised_central_direct_usd": _usd(revised_direct),
        "direct_delta_usd": _usd(delta),
        "allowance_fractions": {lot_id: float(value) for lot_id, value in ALLOWANCE_FRACTIONS.items()},
        "allowance_source": packet["sources"]["system-rates"],
        "original_central_allowances_usd": {lot_id: _usd(value) for lot_id, value in original_allowances.items()},
        "revised_central_allowances_usd": {lot_id: _usd(value) for lot_id, value in revised_allowances.items()},
        "original_central_opening_usd": _usd(original_opening),
        "revised_central_opening_usd": _usd(revised_opening),
        "opening_delta_usd": _usd(revised_opening - original_opening),
        "scope": "Central construction allowance with explicit direct replacements. Recurring costs, renewals, finance and other open scope require separate decisions. Displayed dollar amounts are rounded independently to cents.",
        "procurement_authorized": False, "physical_acceptance": "open",
        "complete_opening_cost_usd": None, "funded_opening_capital_usd": None,
    }
    result["scenario_id"] = digest(result)
    return result

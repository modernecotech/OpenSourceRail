"""Compare complete supplier offers and pass only explicit awards to production."""

from copy import deepcopy

from cities.Baghdad.engineering.simulation.audit_production import replace_offers
from engineering.outline.baghdad_system import _id

SCHEMA = "baghdad-airport-buyer-offers/1"
PRICING_OUTPUT_FIELDS = {"supplier_scope", "scope_id", "usd_per_current_unit"}


def choices(document, layout, rows, context):
    """Return awarded offer objects and a comparison for every eligible return."""
    if document is None:
        return [], []
    if (not isinstance(document, dict) or document.keys() != {"schema", "layouts"}
            or document["schema"] != SCHEMA or not isinstance(document["layouts"], dict)):
        raise ValueError("Buyer offer file needs the Airport offer schema and a feeder layout mapping")
    layouts = document["layouts"]
    if any(not isinstance(name, str) or not name or not isinstance(group, dict)
           or group.keys() != {"offers", "awards"}
           or not isinstance(group["offers"], list) or not isinstance(group["awards"], list)
           for name, group in layouts.items()):
        raise ValueError("Each feeder layout needs offers and awards lists")
    if context["feeder"]["name"] != layout:
        raise ValueError("Buyer offers must use the matching feeder pricing context")
    if layout not in layouts:
        return [], []

    baseline = [
        deepcopy({key: value for key, value in row.items() if key not in PRICING_OUTPUT_FIELDS})
        for row in rows
    ]
    reissued = deepcopy(baseline)
    replace_offers(reissued, context, ())
    by_scope = {}
    for supplied, computed, price in zip(rows, reissued, baseline, strict=True):
        scope = computed["scope_id"]
        if (supplied.get("scope_id") != scope or supplied.get("supplier_scope") != computed["supplier_scope"]
                or supplied.get("scope_id") != _id(supplied["supplier_scope"]) or scope in by_scope
                or price["cost_evidence"] == "buyer-referenced offer input"):
            raise ValueError("Buyer offer comparisons require unchanged baseline pricing scopes")
        by_scope[scope] = price

    bids = []
    by_id = {}
    lowest_by_scope = {}
    for offer in layouts[layout]["offers"]:
        scope = offer.get("scope_id") if isinstance(offer, dict) else None
        if not isinstance(scope, str) or scope not in by_scope:
            raise ValueError("Supplier offer scope does not match a priced or requested lot in this layout")
        original = by_scope[scope]
        checked, = replace_offers([deepcopy(original)], context, [offer])
        offer_id = offer["offer_id"]
        if offer_id in by_id:
            raise ValueError("Use a unique offer ID within each feeder layout")
        record = dict(checked, lot_id=original["lot_id"], baseline_usd=checked["displaced_usd"],
                      status="eligible", buyer_award_reference=None)
        bids.append(record)
        by_id[offer_id] = record
        price = offer["price_usd"]
        lowest_by_scope[scope] = min(lowest_by_scope.get(scope, price), price)

    awards = {}
    for award in layouts[layout]["awards"]:
        fields = {"scope_id", "offer_id", "buyer_award_reference"}
        if (not isinstance(award, dict) or award.keys() != fields
                or any(not isinstance(value, str) or not value.strip() for value in award.values())):
            raise ValueError("Each award needs its matched scope, offer ID and buyer award reference")
        scope, offer_id = award["scope_id"], award["offer_id"]
        record = by_id.get(offer_id)
        if record is None or record["offer"]["scope_id"] != scope or scope in awards:
            raise ValueError("Award only one eligible offer per matching scope")
        awards[scope] = record["offer"]
        record.update(status="awarded", buyer_award_reference=award["buyer_award_reference"])

    for record in bids:
        offer = record["offer"]
        baseline_prices = record["baseline_usd"]
        record["difference_vs_base_usd"] = offer["price_usd"] - baseline_prices["base"] if baseline_prices is not None else None
        record["difference_vs_lowest_offer_usd"] = offer["price_usd"] - lowest_by_scope[offer["scope_id"]]
    return list(awards.values()), bids

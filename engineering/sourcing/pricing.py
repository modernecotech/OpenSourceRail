"""Decimal price extension with real order breaks, dated FX and explicit holds."""
from datetime import timedelta
from decimal import Decimal, ROUND_CEILING
from .model import record, validate_record, decimal, decimal_text, day, is_id, identity

_UNITS = {"kg": ("mass", Decimal(1)), "g": ("mass", Decimal(".001")),
          "t": ("mass", Decimal(1000)), "m": ("length", Decimal(1)),
          "mm": ("length", Decimal(".001")), "m2": ("area", Decimal(1)),
          "m3": ("volume", Decimal(1)), "CY": ("volume", Decimal(".764554857984"))}


def convert_quantity(quantity, source_unit, target_unit, product=None):
    value = decimal(quantity, positive=True)
    if source_unit == target_unit:
        return value
    if source_unit in _UNITS and target_unit in _UNITS and _UNITS[source_unit][0] == _UNITS[target_unit][0]:
        return value * _UNITS[source_unit][1] / _UNITS[target_unit][1]
    if {source_unit, target_unit} == {"m", "m2"}:
        fact = (product or {}).get("specifications", {}).get("width_m")
        if not isinstance(fact, dict) or fact.get("unit") != "m" or fact.get("scope") not in ("fabric-roll", "roll-width", "sheet-width"):
            raise ValueError("Area/linear price conversion requires an explicit applicable roll width")
        width = decimal(fact.get("value"), "roll width", positive=True)
        return value / width if source_unit == "m2" else value * width
    raise ValueError("Incompatible commercial quantity units")


def fx_factor(rates, source_currency, target_currency, *, as_of, max_age_days=7):
    when = day(as_of, "estimate date")
    if type(max_age_days) is not int or max_age_days < 0:
        raise ValueError("Explicit nonnegative FX freshness budget required")
    if source_currency == target_currency:
        return Decimal(1), [], None
    eligible = {}
    for rate in rates:
        validate_record(rate, "fx")
        date = day(rate["rate_date"])
        if when - timedelta(days=max_age_days) <= date <= when:
            basis = identity(dict(rate_kind=rate.get("rate_kind"), basis=rate.get("basis",rate.get("rate_basis"))))
            eligible.setdefault(date, {}).setdefault((rate["source_id"],basis), []).append(rate)
    # One complete observation day per conversion. Mixing unrelated days can
    # manufacture a rate that was never available on either day.
    for date in sorted(eligible, reverse=True):
        candidates = []
        for source_group in sorted(eligible[date]):
            graph, seen = {}, {}
            for rate in eligible[date][source_group]:
                base, quote, value = rate["base_currency"], rate["quote_currency"], decimal(rate["rate"], positive=True)
                key = (base, quote)
                if key in seen and seen[key] != value:
                    raise ValueError("Conflicting same-day FX observations")
                seen[key] = value
                graph.setdefault(base, []).append((quote, value, rate["record_id"]))
                graph.setdefault(quote, []).append((base, Decimal(1)/value, rate["record_id"]))
            frontier = [(source_currency, Decimal(1), [])]
            visited = {source_currency}
            resolved = None
            while frontier and resolved is None:
                currency, factor, ids = frontier.pop(0)
                for dest, scale, key in sorted(graph.get(currency, [])):
                    if dest in visited:
                        continue
                    new_ids = ids + [key]
                    if dest == target_currency:
                        resolved = (factor*scale, new_ids, date.isoformat())
                        break
                    visited.add(dest)
                    frontier.append((dest, factor*scale, new_ids))
            if resolved is not None:
                candidates.append(resolved)
        if candidates:
            if len({row[0] for row in candidates}) != 1:
                raise ValueError("Conflicting same-date source-specific FX paths")
            return candidates[0]
    return None, [], None


def _price_assessment(requirement, product, offer, *, status, reasons, **fields):
    return record("assessment", assessment_type="offer-price", candidate_id=requirement["candidate_id"],
        requirement_id=requirement["record_id"], product_id=product["record_id"], product_key=product["product_key"],
        offer_id=offer["record_id"], source_id=offer["source_id"], source_class=offer["source_class"],
        status=status, holds=reasons, complete_installed_cost=None,
        freight_duties_installation_and_lifecycle_included=False, physical_qualification=None, **fields)


def _tier_at(offer, quantity):
    return next((row for row in offer["tiers"] if decimal(row["minimum_quantity"]) <= quantity and
                 (row["maximum_quantity"] is None or quantity < decimal(row["maximum_quantity"]))), None)


def evaluate_offers(requirement, product, offers, fx, *, as_of, target_currency="USD",
                    max_fx_age_days=7, max_price_age_days=30, target_tax_basis="excluded",
                    authenticator=None, authentication_context_id=None):
    validate_record(requirement, "requirement")
    validate_record(product, "product")
    when = day(as_of, "estimate date")
    if target_tax_basis not in ("included", "excluded"):
        raise ValueError("Explicit comparable tax basis required")
    if type(max_price_age_days) is not int or max_price_age_days < 0:
        raise ValueError("Nonnegative catalogue freshness policy required")
    if authenticator is not None and (not callable(authenticator) or not is_id(authentication_context_id)):
        raise ValueError("Trusted external authenticator and context identity required")
    output, seen = [], set()
    for offer in offers:
        validate_record(offer, "offer")
        if offer["product_id"] != product["record_id"]:
            continue
        if offer["record_id"] in seen:
            raise ValueError("Duplicate price evidence")
        seen.add(offer["record_id"])
        reasons = []
        price_date = day(offer["price_date"])
        if price_date > when:
            reasons.append("price-postdates-estimate")
        if offer.get("valid_until") is not None and day(offer["valid_until"]) < when:
            reasons.append("expired-price-evidence")
        if offer["source_class"] != "A" and (when-price_date).days > max_price_age_days:
            reasons.append("catalogue-price-outside-declared-freshness-policy")
        if offer["source_class"] == "A":
            metadata = bool(offer.get("supplier") and is_id(offer.get("source_document_sha256")) and offer.get("valid_until"))
            authenticated = metadata and authenticator is not None and authenticator(offer, "sourcing-price") is True
            if not authenticated:
                reasons.append("actual-quote-needs-external-authentication")
        if requirement.get("quantity") is None:
            reasons.append("unresolved-purchased-quantity")
        if offer.get("supply_scope") is not None and product.get("supply_scope") is not None and offer["supply_scope"] != product["supply_scope"]:
            reasons.append("offer-product-supply-scope-differs")
        if offer.get("intended_market") is not None and requirement.get("required_market") is not None and offer["intended_market"] != requirement["required_market"]:
            reasons.append("offer-market-differs")
        demand = purchase = tier = native = normalized = None
        listing_tier = listing_native = listing_normalized = None
        factor, rate_ids, rate_date = None, [], None
        if requirement.get("quantity") is not None:
            try:
                demand = convert_quantity(requirement["quantity"], requirement["quantity_unit"], offer["quantity_unit"], product)
                listing_tier = _tier_at(offer, demand)
                if listing_tier is not None:
                    listing_native = demand*decimal(listing_tier["unit_price"])
                tax_scale = Decimal(1)
                basis = offer["tax_basis"]
                if basis == "unknown":
                    reasons.append("unknown-tax-basis")
                elif basis != target_tax_basis:
                    if offer.get("tax_rate") is None:
                        reasons.append("tax-conversion-needs-explicit-rate")
                    else:
                        tax = Decimal(1)+decimal(offer["tax_rate"])
                        tax_scale = Decimal(1)/tax if basis == "included" else tax
                factor, rate_ids, rate_date = fx_factor(fx, offer["currency"], target_currency, as_of=as_of, max_age_days=max_fx_age_days)
                if factor is None:
                    reasons.append("missing-dated-compatible-FX")
                # This is a published-price extension at the requested quantity,
                # not a lower/upper bound or an actual attainable order cost.
                if not reasons and listing_native is not None:
                    listing_normalized = listing_native*tax_scale*factor
                if offer.get("minimum_order_quantity") is None or offer.get("order_multiple") is None:
                    reasons.append("held-order-constraints")
                else:
                    minimum = decimal(offer["minimum_order_quantity"], positive=True)
                    multiple = decimal(offer["order_multiple"], positive=True)
                    purchase = (max(demand, minimum)/multiple).to_integral_value(rounding=ROUND_CEILING)*multiple
                    tier = _tier_at(offer, purchase)
                    if tier is None:
                        reasons.append("no-applicable-order-quantity-price-break")
                    else:
                        native = purchase*decimal(tier["unit_price"])
                        if not reasons:
                            normalized = native*tax_scale*factor
            except (ValueError, TypeError) as error:
                reasons.append(str(error))
        output.append(_price_assessment(requirement, product, offer, status="held" if reasons else "priced", reasons=reasons,
            estimate_date=as_of, target_currency=target_currency, target_tax_basis=target_tax_basis,
            demanded_quantity=None if demand is None else decimal_text(demand),
            purchased_quantity=None if purchase is None else decimal_text(purchase), quantity_unit=offer["quantity_unit"],
            surplus_purchase_quantity=None if purchase is None else decimal_text(purchase-demand),
            selected_price_break=tier, listed_currency=offer["currency"],
            listed_order_subtotal=None if native is None else decimal_text(native),
            comparable_order_subtotal=None if reasons or normalized is None else decimal_text(normalized),
            listed_extension_at_requested_quantity=None if listing_native is None else decimal_text(listing_native),
            listed_extension_currency=offer["currency"], listed_extension_price_break=listing_tier,
            comparable_listed_extension=None if listing_normalized is None else decimal_text(listing_normalized),
            listed_extension_is_order_cost=False, listed_extension_is_cost_bound=False,
            fx_record_ids=rate_ids, fx_rate_date=rate_date, fx_factor=None if factor is None else decimal_text(factor),
            authentication_context_id=authentication_context_id if offer["source_class"] == "A" else None,
            source_price_date=offer["price_date"], tax_basis_as_listed=offer["tax_basis"],
            ordering_and_manufacturing_approved=False))
    return sorted(output, key=lambda row:row["offer_id"])

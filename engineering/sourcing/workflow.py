"""Find, screen, price and enqueue design work against one exact twin revision."""
from collections import Counter
from decimal import Decimal
from .model import record, validate_record, decimal, decimal_text
from .requirements import validate_requirements
from .matching import match_products
from .pricing import evaluate_offers
from .erp import build_rfq_drafts
from .twin import discovery_task
from .sensitivity import rank_backlog


def _extend(value, **extra):
    return record(value["kind"], **{k:v for k,v in value.items() if k not in ("record_id", "schema", "kind")}, **extra)


def _scope_paths(requirement):
    return [requirement["namespace"]+"/"+path for path in
            (requirement["occurrence_ids"] or requirement.get("physical_scopes", []))]


def lifecycle(overlay, *, service_context, years=30, discount_rate=.05):
    """Adapt only known catalogue scopes; missing lifecycle categories stay open."""
    validate_record(overlay, "overlay")
    if overlay["currency"] != "USD":
        raise ValueError("Existing lifecycle adapter requires sourced USD conversion")
    from engineering.reference_cell import economics
    from engineering.reference_cell.manufacturing import SCOPES
    service_id = economics.service_identity(service_context)
    charges = []
    for line in overlay["lines"]:
        # Authenticated actual quotations must pass the existing independent
        # authentication workflow too; this adapter does not relabel them B.
        if line["source_class"] == "A":
            continue
        scope = {"civil":"guideway", "track":"guideway", "propulsion":"stations-power", "station":"stations-power",
                 "factory-qa":"factory-tooling", "erection":"construction"}.get(line["category"], "rolling-stock")
        if scope not in SCOPES:
            raise ValueError("Unsupported lifecycle mapping")
        subtotal = float(decimal(line["subtotal"]))
        charges.append(economics.make_record(overlay["candidate_id"], scope, line["physical_scope"],
            [1.,1.], [subtotal,subtotal], 0, line["source_class"], line["source_id"],
            line["source_price_date"], line.get("market") or "catalogue market unspecified; Baghdad delivered cost unresolved",
            "one explicitly bounded catalogue order group; freight/taxes/install/lifecycle missing", service_id,
            method="Dated sourcing offer with exact quantity break and upstream currency conversion; conditional catalogue scope only"))
    return economics.evaluate(overlay["candidate_id"], charges, years, discount_rate, service_context)


def evaluate(store, requirements, *, bindings=None, as_of, target_currency="USD",
             max_fx_age_days=7, max_price_age_days=30, service_context=None,
             years=30, discount_rate=.05, authenticator=None, authentication_context_id=None):
    candidate = validate_requirements(requirements)
    requirements = sorted(requirements, key=lambda r:r["record_id"])
    store.insert_many(requirements)
    products, offers, rates = store.all("product"), store.all("offer"), store.all("fx")
    pmap = {p["record_id"]:p for p in products}
    reqs = {r["record_id"]:r for r in requirements}
    technical = match_products(requirements, products, bindings=bindings)
    commercial, tasks, by_req, listings_by_req = [], [], {}, {}
    for assessment in technical:
        requirement, product = reqs[assessment["requirement_id"]], pmap[assessment["product_id"]]
        if assessment["status"] != "unsuitable":
            prices = evaluate_offers(requirement, product, offers, rates, as_of=as_of,
                target_currency=target_currency, max_fx_age_days=max_fx_age_days,
                max_price_age_days=max_price_age_days, authenticator=authenticator,
                authentication_context_id=authentication_context_id)
            for price in prices:
                scope_known = bool(_scope_paths(requirement))
                price = _extend(price, technical_assessment_id=assessment["record_id"],
                    technical_status=assessment["status"], physical_charge_scope_resolved=scope_known,
                    ledger_holds=[] if scope_known else ["unresolved-physical-charge-scope"],
                    usable_for_candidate_scope=scope_known and assessment["status"]=="compatible" and price["status"]=="priced",
                    listed_extension_usable_for_candidate_scope=scope_known and assessment["status"]=="compatible" and price["comparable_listed_extension"] is not None)
                commercial.append(price)
                if price["usable_for_candidate_scope"]:
                    by_req.setdefault(requirement["record_id"], []).append(price)
                if price["listed_extension_usable_for_candidate_scope"]:
                    listings_by_req.setdefault(requirement["record_id"], []).append(price)
        if assessment["status"] != "compatible":
            tasks.append(discovery_task(requirement, product, assessment))
    store.insert_many(technical+commercial+tasks)
    lines, claimed = [], set()
    for req_id, options in sorted(by_req.items()):
        requirement = reqs[req_id]
        selected = min(options, key=lambda p:(decimal(p["comparable_order_subtotal"]), p["record_id"]))
        paths = _scope_paths(requirement)
        if not paths:
            raise ValueError("Priced requirement lacks an explicit physical charge scope")
        if any(path==old or path.startswith(old+"/") or old.startswith(path+"/") for path in paths for old in claimed):
            raise ValueError("Overlapping parent/child cost scope")
        claimed.update(paths)
        offer = store.get(selected["offer_id"], "offer")
        lines.append(dict(requirement_id=req_id, product_id=selected["product_id"],
            screening_offer_id=selected["offer_id"], price_assessment_id=selected["record_id"],
            physical_scope=paths, namespace=requirement["namespace"], registry_id=requirement.get("registry_id"),
            part_definition_id=requirement.get("part_definition_id"), part_revision_id=requirement.get("part_revision_id"),
            occurrence_ids=requirement["occurrence_ids"], category=requirement.get("category", "other"),
            subtotal=selected["comparable_order_subtotal"], source_class=selected["source_class"],
            source_id=selected["source_id"], source_price_date=selected["source_price_date"],
            fx_record_ids=selected["fx_record_ids"], market=offer.get("market", offer.get("intended_market")),
            procurement_selection_approved=False))
    priced = {line["requirement_id"] for line in lines}
    listing_lines, listing_claimed = [], set()
    for req_id, options in sorted(listings_by_req.items()):
        requirement = reqs[req_id]
        selected = min(options, key=lambda p:(decimal(p["comparable_listed_extension"]), p["record_id"]))
        paths = _scope_paths(requirement)
        if not paths or any(path==old or path.startswith(old+"/") or old.startswith(path+"/") for path in paths for old in listing_claimed):
            raise ValueError("Overlapping or absent listed-extension physical scope")
        listing_claimed.update(paths)
        listing_lines.append(dict(requirement_id=req_id, product_id=selected["product_id"],
            screening_listing_id=selected["offer_id"], price_assessment_id=selected["record_id"],
            physical_scope=paths, subtotal=selected["comparable_listed_extension"], source_id=selected["source_id"],
            source_class=selected["source_class"], source_price_date=selected["source_price_date"],
            fx_record_ids=selected["fx_record_ids"], price_basis="published extension at requested quantity",
            is_order_cost=False, is_cost_bound=False, procurement_selection_approved=False))
    listed = {line["requirement_id"] for line in listing_lines}
    counts = Counter(r["namespace"] for r in requirements)
    mass_known = sum(r.get("mass_per_unit_kg") is not None and r["mass_per_unit_kg"].get("calculated_kg") is not None for r in requirements)
    physical_scope_count = len({(r["namespace"], path) for r in requirements for path in (r.get("physical_scopes") or [])})
    engineering_occurrence_count = len({(r["namespace"], path) for r in requirements for path in r["occurrence_ids"]})
    source_groups = [r for r in requirements if r.get("source_manufacturing_group_id")]
    coverage = dict(requirement_count=len(requirements), priced_requirement_count=len(priced),
        order_price_requirement_count=len(priced), listed_price_requirement_count=len(listed),
        requirement_price_fraction=decimal_text(Decimal(len(priced))/len(requirements)),
        listed_price_fraction=decimal_text(Decimal(len(listed))/len(requirements)),
        unknown_quantity_requirements=sum(r["quantity"] is None for r in requirements),
        physical_scope_count=physical_scope_count,
        engineering_occurrence_count=engineering_occurrence_count,
        source_manufacturing_group_count=len(source_groups),
        source_manufacturing_group_occurrence_count=sum(r.get("engineering_occurrence_count", len(r["occurrence_ids"])) for r in source_groups),
        unlocated_account_count=sum(r.get("scope_kind") == "installed-account" for r in requirements),
        nominal_mass_observed_requirement_count=mass_known, qualified_requirement_count=0,
        validation_fraction="0", quantity_basis=(
            "source-declared manufacturing groups retain exact engineering occurrences; purchase unit and order quantity unresolved"
            if source_groups else "requirement groups, not falsely expanded unlocated accounts"),
        namespaces=dict(sorted(counts.items())))
    overlay = record("overlay", candidate_id=candidate, estimate_date=as_of, currency=target_currency,
        tax_basis="excluded", requirement_ids=[r["record_id"] for r in requirements], lines=lines, listed_extension_lines=listing_lines,
        known_catalogue_subtotal=None if not lines else decimal_text(sum((decimal(line["subtotal"]) for line in lines), Decimal(0))),
        known_listed_extension_subtotal=None if not listing_lines else decimal_text(sum((decimal(line["subtotal"]) for line in listing_lines), Decimal(0))),
        listed_extension_is_order_cost=False, listed_extension_is_cost_bound=False,
        complete_installed_total=None, complete_whole_life_total=None, integrated_winner=None,
        unpriced_requirement_ids=sorted(set(reqs)-priced), coverage=coverage,
        physical_candidate_changed=False, mass_or_geometry_mutated=False,
        price_ranking_purpose="comparable catalogue-order scope only; not complete supplier/railway selection",
        freight_duties_installation_and_renewals_costed=False)
    store.put(overlay)
    unpriced = [r for r in requirements if r["record_id"] not in priced]
    rfqs = build_rfq_drafts(unpriced, technical) if unpriced else []
    store.insert_many(rfqs)
    backlog = rank_backlog(unpriced)
    result = record("run", candidate_id=candidate, estimate_date=as_of, currency=target_currency,
        requirement_ids=[r["record_id"] for r in requirements], technical_assessment_ids=[a["record_id"] for a in technical],
        price_assessment_ids=[a["record_id"] for a in commercial], overlay_id=overlay["record_id"],
        rfq_ids=[r["record_id"] for r in rfqs], redesign_ids=[t["record_id"] for t in tasks],
        summary=dict(coverage, product_observations=len(products), technical_matches=len(technical),
            compatible_matches=sum(a["status"]=="compatible" for a in technical),
            unsuitable_matches=sum(a["status"]=="unsuitable" for a in technical),
            held_price_observations=sum(a["status"]=="held" for a in commercial),
            known_catalogue_subtotal=overlay["known_catalogue_subtotal"], RFQ_drafts=len(rfqs),
            known_listed_extension_subtotal=overlay["known_listed_extension_subtotal"],
            redesign_tasks=len(tasks), complete_installed_cost=None, whole_life_cost=None),
        backlog=backlog, source_record_ids=sorted({source for p in products for source in p["source_ids"]}),
        lifecycle=None if service_context is None else lifecycle(overlay, service_context=service_context, years=years, discount_rate=discount_rate),
        integrated_winner=None, physical_qualification=None,
        supplier_communications_sent=0, existing_manufacturing_orders_changed=0)
    store.put(result)
    return result

"""Specification screening before commercial extension; leads are not selections."""
from .model import record, validate_record, decimal, identity
from .requirements import classify, validate_requirements

_SCALES = {"kg": ("mass", "1"), "g": ("mass", ".001"), "t": ("mass", "1000"),
           "m": ("length", "1"), "mm": ("length", ".001"),
           "W": ("power", "1"), "kW": ("power", "1000"),
           "Pa": ("stress", "1"), "MPa": ("stress", "1000000")}


def _numeric(fact, unit):
    if isinstance(fact, dict):
        observed = fact.get("value")
        observed_unit = fact.get("unit", unit)
    else:
        observed, observed_unit = fact, unit
    if observed is None or isinstance(observed, (list, dict, bool)):
        raise ValueError("Missing scalar specification")
    result = decimal(observed, nonnegative=False)
    if observed_unit != unit:
        if observed_unit not in _SCALES or unit not in _SCALES or _SCALES[observed_unit][0] != _SCALES[unit][0]:
            raise ValueError("Specification units are incompatible")
        result *= decimal(_SCALES[observed_unit][1]) / decimal(_SCALES[unit][1])
    return result


def _constraint(constraint, product):
    field = constraint.get("field")
    if not isinstance(field, str) or not field:
        raise ValueError("Named technical constraint required")
    fact = product["specifications"].get(field)
    if fact is None:
        return dict(field=field, status="pending", reason="missing-specification")
    if constraint.get("scope") is not None and (not isinstance(fact, dict) or fact.get("scope") != constraint["scope"]):
        return dict(field=field, status="pending", reason="specification-scope-differs")
    if "equals" in constraint:
        value = fact.get("value") if isinstance(fact, dict) else fact
        return dict(field=field, status="pass" if value == constraint["equals"] else "fail", reason="categorical-comparison")
    try:
        value = _numeric(fact, constraint.get("unit"))
    except (ValueError, TypeError):
        return dict(field=field, status="pending", reason="missing-or-incompatible-units")
    passed = True
    if constraint.get("minimum") is not None:
        passed &= value >= decimal(constraint["minimum"], nonnegative=False)
    if constraint.get("maximum") is not None:
        passed &= value <= decimal(constraint["maximum"], nonnegative=False)
    return dict(field=field, status="pass" if passed else "fail", observed=str(value), unit=constraint.get("unit"), reason="numeric-domain-comparison")


def _exact_identifier(requirement, product):
    supplied = requirement.get("identifiers", {})
    manufacturer = supplied.get("manufacturer")
    number = next((supplied[k] for k in ("manufacturer_part_number", "part_number", "SKU", "model") if supplied.get(k)), None)
    return bool(manufacturer and number and manufacturer.casefold() == product["manufacturer"].casefold()
                and number.casefold() == product["part_number"].casefold())


def _bindings(requirements, products, bindings):
    if bindings is None:
        return {}
    if not isinstance(bindings, list):
        raise ValueError("Explicit revision-bound mapping records required")
    reqs = {r["record_id"]: r for r in requirements}
    pmap = {p["record_id"]: p for p in products}
    result = {}
    for row in bindings:
        req = reqs.get(row.get("requirement_id"))
        if req is None or row.get("product_id") not in pmap:
            raise ValueError("Binding references an absent exact requirement/product")
        if row.get("candidate_id") != req["candidate_id"]:
            raise ValueError("Mixed sourcing binding candidate")
        for key in ("registry_id", "part_definition_id", "part_revision_id"):
            if req.get(key) is not None and row.get(key) != req[key]:
                raise ValueError("Stale sourcing binding " + key)
        key = (req["record_id"], row["product_id"])
        if key in result:
            raise ValueError("Duplicate sourcing mapping")
        result[key] = row
    return result


def match_products(requirements, products, *, bindings=None):
    validate_requirements(requirements)
    requirements = sorted(requirements, key=lambda r:r["record_id"])
    products = sorted(products, key=lambda r:r["record_id"])
    for product in products:
        validate_record(product, "product")
    if len({p["record_id"] for p in products}) != len(products):
        raise ValueError("Duplicate product observations")
    product_map = {product["record_id"]: product for product in products}
    for requirement in requirements:
        selected_id = requirement.get("selected_product_record_id")
        if selected_id is not None:
            selected = product_map.get(selected_id)
            if selected is None or not _exact_identifier(requirement, selected):
                raise ValueError("Selected immutable product observation is absent or does not match exact source identifiers")
    maps = _bindings(requirements, products, bindings)
    output = []
    for requirement in requirements:
        for product in products:
            selected_id = requirement.get("selected_product_record_id")
            if selected_id is not None and selected_id != product["record_id"]:
                continue
            binding = maps.get((requirement["record_id"], product["record_id"]))
            exact = _exact_identifier(requirement, product)
            family = classify([product["category"], product["description"], product["part_number"]])[0]
            same_family = family == requirement.get("category") or product["category"] == requirement.get("category")
            if not same_family and not binding and not exact:
                continue
            checks = [_constraint(c, product) for c in requirement.get("constraints", [])]
            holds = []
            if not exact and not binding:
                holds.append("family-lead-only-no-exact-product-binding")
            if requirement["quantity"] is None:
                holds.append("unresolved-aggregate-account-has-no-purchased-unit-count")
            wanted_scope = requirement.get("procurement_scope")
            offered_scope = product.get("supply_scope", product.get("scope"))
            # A proposed mapping is not permission to replace a complete assembly
            # with an advertised mechanism, raw cloth or a shipping mass.
            if not wanted_scope:
                holds.append("missing-required-assembly-scope")
            elif not offered_scope:
                holds.append("missing-product-supply-scope")
            elif wanted_scope != offered_scope:
                holds.append("product-and-required-assembly-scope-differ")
            if product.get("specification_conflicts"):
                holds.append("unresolved-publisher-specification-conflict")
            if any(c["status"] == "pending" for c in checks):
                holds.append("missing-required-specification")
            if product.get("source_kind") == "commodity_benchmark":
                holds.append("commodity-is-not-a-manufactured-product")
            failed = any(c["status"] == "fail" for c in checks)
            status = "unsuitable" if failed else "pending" if holds else "compatible"
            output.append(record("assessment", assessment_type="technical-match", candidate_id=requirement["candidate_id"],
                requirement_id=requirement["record_id"], product_id=product["record_id"], product_key=product["product_key"],
                registry_id=requirement.get("registry_id"), part_revision_id=requirement.get("part_revision_id"),
                namespace=requirement["namespace"], status=status, checks=checks, holds=holds,
                exact_product_identifier=exact, explicit_research_mapping_id=None if binding is None else identity(binding),
                suitability_scope="catalogue-screen-only", physical_qualification=None,
                catalogue_mass_is_installed_mass=False, source_ids=product["source_ids"]))
    return output

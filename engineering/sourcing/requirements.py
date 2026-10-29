"""Typed unresolved BOM extraction; an account is never a physical occurrence."""
from collections import defaultdict
from copy import deepcopy
from pathlib import PurePosixPath
import re
from .model import identity, is_id, record, decimal_text, validate_record

PRIORITIES = (
    ("propulsion", ("lim", "propulsion", "winding", "inverter", "motor", "secondary")),
    ("civil", ("foundation", "concrete", "precast", "pier", "beam", "civil")),
    ("body-materials", ("gfrp", "laminate", "body", "floor", "roof", "frame", "resin", "fabric")),
    ("running-gear", ("bogie", "wheel", "axle", "bearing", "suspension", "running-gear")),
    ("braking", ("brake", "braking", "caliper")),
    ("station", ("station", "platform", "lift", "access")),
    ("HVAC", ("hvac", "cooling", "duct", "thermal", "climate", "air-conditioning")),
    ("auxiliary-power", ("battery", "bms", "auxiliary", "converter", "power-supply")),
    ("doors-glazing", ("door", "glazing", "window", "seal")),
    ("erection", ("crane", "erection", "transport", "lifting")),
    ("track", ("rail", "fastening", "baseplate", "pandrol")),
    ("solar", ("solar", "photovoltaic", "pv-module")),
    ("controls", ("control", "sensor", "processor", "electronics", "communication", "atp")),
    ("factory-qa", ("inspection", "factory", "tooling", "mould", "vacuum", "quality")),
)


def classify(value):
    labels = [value] if isinstance(value, str) else list(value)
    normalized = [str(item).strip().lower().replace("_", "-") for item in labels]
    aliases = {"lim-interface":"propulsion", "primary-body":"body-materials",
        "bogie-interfaces":"running-gear", "bogies":"running-gear", "wheelsets":"running-gear",
        "control-safety":"controls", "solar-roof":"solar", "doors":"doors-glazing", "glazing":"doors-glazing"}
    declared = {aliases.get(item, item) for item in normalized}
    # Actual function/category labels precede incidental words in identifiers.
    for index, (category, _) in enumerate(PRIORITIES, 1):
        if category.lower() in declared:
            return category, index
    words = " ".join(normalized)
    for index, (category, terms) in enumerate(PRIORITIES, 1):
        if any(re.search(r"(?<![a-z0-9])"+re.escape(term)+r"(?![a-z0-9])", words) for term in terms):
            return category, index
    return "other", len(PRIORITIES) + 1


def _candidate(value):
    if not is_id(value):
        raise ValueError("Exact physical candidate identity required")
    return value


def _identifiers(part):
    result = {}
    for container in (part.get("procurement", {}), part.get("electrical_thermal", {}), part.get("evidence", {})):
        for field in ("manufacturer", "part_number", "manufacturer_part_number", "SKU", "model"):
            if isinstance(container.get(field), str) and container[field].strip():
                result[field] = container[field]
    return result


def extract_requirements(payload, *, candidate_id=None, namespace=None):
    """Read one typed input without synthesizing missing unit counts.

    Integrated/vehicle bindings require an explicit wrapper containing matching
    candidate_id and body_candidate_id; a string override cannot relabel a body.
    """
    if not isinstance(payload, dict):
        raise ValueError("Typed BOM object required")
    vehicle = payload.get("vehicle", payload)
    registry = vehicle.get("registry") if isinstance(vehicle, dict) else None
    if payload.get("schema") == "osr-component-registry/1":
        registry = payload
    if registry is not None:
        if namespace not in (None, "component_registry"):
            raise ValueError("Registry and scene namespaces are not interchangeable")
        from engineering.component_registry import validate_registry
        validate_registry(registry)
        body = registry["candidate_id"]
        candidate = _candidate(candidate_id or payload.get("candidate_id") or body)
        if candidate != body and (payload.get("candidate_id") != candidate or payload.get("body_candidate_id") != body):
            raise ValueError("Explicit integrated/body candidate binding required")
        if isinstance(vehicle, dict) and vehicle is not registry and vehicle.get("candidate_id", body) != body:
            raise ValueError("Vehicle registry candidate differs")
        parts = {part["physical_definition_id"]: part for part in registry["parts"]}
        groups = defaultdict(list)
        for occurrence in registry["occurrences"]:
            groups[(occurrence["part_definition_id"], occurrence["part_revision_id"])].append(occurrence)
        rows = []
        for (definition, revision), occurrences in sorted(groups.items()):
            part = parts[definition]
            category, priority = classify(part["functions"] + [part["part_id"]])
            scopes = sorted({o["scope"] for o in occurrences})
            rows.append(record("requirement", candidate_id=candidate, input_id=registry["registry_id"],
                namespace="component_registry", scope_kind="actual-part", body_candidate_id=body, registry_id=registry["registry_id"],
                requirement_key=part["part_id"], part_definition_id=definition, part_revision_id=revision,
                description=part["part_id"], functions=part["functions"], category=category, priority=priority,
                quantity=str(len(occurrences)), quantity_unit="each", occurrence_ids=[o["occurrence_id"] for o in occurrences],
                physical_scopes=scopes, procurement_scope=part.get("procurement", {}).get("scope", "one-part"),
                identifiers=_identifiers(part), constraints=deepcopy(part.get("procurement", {}).get("sourcing_constraints", [])),
                geometry=deepcopy(part["geometry"]), material_id=part["material_id"],
                mass_per_unit_kg=deepcopy(part["mass"]), cost_status="unpriced" if part["cost"].get("lower_usd") is None else "retained-price-needs-source-check",
                installed_mass_complete=False, source_evidence=deepcopy(part.get("evidence", {})),
                decision_sensitivity=deepcopy(part.get("decision_sensitivity"))))
        return rows
    if payload.get("schema") == "osr-v06-engineering-bom/1":
        if namespace not in (None, "station-account"):
            raise ValueError("Selected reference accounts are not registry occurrences")
        candidate = _candidate(payload.get("candidate_id"))
        if candidate_id is not None and candidate_id != candidate:
            raise ValueError("Mixed selected reference candidate")
        input_id = identity(payload)
        rows = []
        seen = set()
        for account in payload["stock_inventory_per_car"]:
            key = account["id"]
            if key in seen:
                raise ValueError("Duplicate selected reference account")
            seen.add(key)
            category, priority = classify([account.get("system", ""), key])
            rows.append(record("requirement", candidate_id=candidate, input_id=input_id,
                namespace="station-account", scope_kind="installed-account", body_candidate_id=payload.get("body_candidate_id"), registry_id=None,
                requirement_key=key, part_definition_id=None, part_revision_id=None,
                description=key, category=category, priority=priority, functions=[account.get("system", "unresolved")],
                quantity=None, quantity_unit=None, occurrence_ids=[], physical_scopes=["selected-reference-account/"+key],
                procurement_scope="mixed-subtotal-account-per-car", identifiers={}, constraints=[],
                accounted_mass_kg_per_car=account.get("mass_kg"), mass_per_unit_kg=None,
                quantity_basis="Unresolved aggregate account, not a purchased part; formation is not a unit count",
                source_account=deepcopy(account), cost_status="unresolved-physical-definition", installed_mass_complete=False,
                decision_sensitivity=deepcopy(account.get("decision_sensitivity"))))
        return rows
    if payload.get("schema") == "osr-federated-railway-BOM/1":
        if namespace not in (None, "twin-scene"):
            raise ValueError("Federated scene and registry namespaces differ")
        from engineering.station_rail.common import identity as native_identity
        if payload.get("evaluation_id") != native_identity({k:v for k,v in payload.items() if k != "evaluation_id"}):
            raise ValueError("Federated BOM identity differs")
        candidate = _candidate(payload.get("candidate_id"))
        if candidate_id is not None and candidate_id != candidate:
            raise ValueError("Mixed whole-cell candidate")
        scene_rows, seen = {}, set()
        for item in payload["engineering_BOM"]:
            if item.get("candidate_id") != candidate or item["id"] in seen:
                raise ValueError("Mixed or duplicate scene occurrence")
            seen.add(item["id"])
            located = item["scope"] != "unlocated-account-or-obligation"
            if located and item.get("quantity") != 1:
                raise ValueError("Scene stock rows must represent one actual occurrence")
            scene_rows[item["id"]] = item

        rows = []
        manufacturing_groups = payload.get("manufacturing_BOM")
        grouped_occurrences = set()
        if manufacturing_groups:
            if not isinstance(manufacturing_groups, list):
                raise ValueError("Declared manufacturing groups must be a list")
            group_ids, group_keys = set(), set()
            for group in manufacturing_groups:
                if not isinstance(group, dict) or group.get("candidate_id") != candidate:
                    raise ValueError("Mixed candidate manufacturing group")
                group_id, key = group.get("group_id"), group.get("id")
                occurrence_ids = group.get("engineering_occurrence_ids")
                if (not is_id(group_id) or group_id in group_ids or not isinstance(key, str) or not key.strip()
                        or key in group_keys or not isinstance(occurrence_ids, list) or not occurrence_ids
                        or len(occurrence_ids) != len(set(occurrence_ids))):
                    raise ValueError("Exact, distinct manufacturing group identity and memberships required")
                group_ids.add(group_id); group_keys.add(key)
                members = []
                for occurrence_id in occurrence_ids:
                    item = scene_rows.get(occurrence_id)
                    if item is None or item["scope"] == "unlocated-account-or-obligation" or occurrence_id in grouped_occurrences:
                        raise ValueError("Manufacturing groups must partition located stock occurrences")
                    if item.get("unit") != "stock-occurrence" or item.get("quantity") != 1:
                        raise ValueError("Manufacturing group member is not one located stock occurrence")
                    grouped_occurrences.add(occurrence_id)
                    members.append(item)
                homogeneity = {(item.get("system"), item.get("material"), item.get("scope")) for item in members}
                if len(homogeneity) != 1:
                    raise ValueError("Manufacturing groups cannot combine different system, material or stock scope")
                if group.get("known_gross_stock_mass_kg") is not None:
                    decimal_text(group["known_gross_stock_mass_kg"], "known gross stock mass")
                if group.get("purchased_stock_quantity") is not None or group.get("unit_price_USD") is not None:
                    # Keep these source declarations visible, but do not promote
                    # them to a usable order quantity or price in this adapter.
                    decimal_text(group["purchased_stock_quantity"], "purchased stock quantity", positive=True) if group.get("purchased_stock_quantity") is not None else None
                    decimal_text(group["unit_price_USD"], "source unit price") if group.get("unit_price_USD") is not None else None
                system, material, stock_scope = next(iter(homogeneity))
                category, priority = classify([system or "", key])
                source_group = {field: deepcopy(group.get(field)) for field in (
                    "id", "group_id", "known_gross_stock_mass_kg", "net_fabricated_mass_kg",
                    "purchased_stock_quantity", "yield_fraction", "labour_h", "tooling",
                    "inspection_procedure", "process_qualification", "origin_country",
                    "repair_and_removal_route", "decision_sensitivity")}
                group_occurrences = sorted(occurrence_ids)
                rows.append(record("requirement", candidate_id=candidate, input_id=payload["evaluation_id"], namespace="twin-scene",
                    requirement_key=key, description=key, category=category, priority=priority,
                    scope_kind="source-declared-manufacturing-group", source_manufacturing_group_id=group_id,
                    source_manufacturing_group=source_group, engineering_occurrence_count=len(group_occurrences),
                    scene_component_definition_ids=sorted({item["component_definition_id"] for item in members}),
                    scene_geometry_ids=sorted({item["geometry_id"] for item in members if item.get("geometry_id")}),
                    system=system, material=material, stock_scope=stock_scope,
                    procurement_unit_status="purchase quantity and unit unresolved",
                    registry_id=None, part_definition_id=None, part_revision_id=None,
                    quantity=None, quantity_unit=None, occurrence_ids=group_occurrences,
                    physical_scopes=group_occurrences,
                    procurement_scope="source-declared gross-stock manufacturing group",
                    identifiers={}, constraints=[], accounted_mass_kg=group.get("known_gross_stock_mass_kg"),
                    mass_per_unit_kg=None, source_scene_row=None,
                    cost_status="unpriced; source group is not a purchasing unit", installed_mass_complete=False,
                    decision_sensitivity=deepcopy(group.get("decision_sensitivity"))))
            located_occurrences = {key for key, item in scene_rows.items() if item["scope"] != "unlocated-account-or-obligation"}
            if grouped_occurrences != located_occurrences:
                raise ValueError("Declared manufacturing groups do not completely cover located stock occurrences")

        for item in payload["engineering_BOM"]:
            if item["scope"] != "unlocated-account-or-obligation" and item["id"] in grouped_occurrences:
                continue
            category, priority = classify([item["system"], item["id"]])
            rows.append(record("requirement", candidate_id=candidate, input_id=payload["evaluation_id"], namespace="twin-scene",
                requirement_key=item["id"], description=item["id"], category=category, priority=priority,
                scope_kind="stock-occurrence" if located else "installed-account",
                scene_component_definition_id=item["component_definition_id"], part_definition_id=None, part_revision_id=None,
                registry_id=None, quantity="1" if located else None, quantity_unit="each" if located else None,
                occurrence_ids=[item["id"]] if located else [], physical_scopes=[item["id"]],
                procurement_scope="gross-stock-occurrence" if located else "unlocated-account",
                identifiers={}, constraints=[], accounted_mass_kg=item.get("accounted_mass_kg"),
                mass_per_unit_kg=None, source_scene_row=deepcopy(item), cost_status="unpriced", installed_mass_complete=False,
                decision_sensitivity=deepcopy(item.get("decision_sensitivity"))))
        return rows
    raise ValueError("Unsupported typed sourcing input; provide a registry or declared BOM schema")


def _canonical_scope(value):
    if not isinstance(value, str) or not value or value != value.strip() or "\\" in value or ":" in value:
        raise ValueError("Canonical relative sourcing scope required")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts or path.as_posix() != value:
        raise ValueError("Noncanonical, absolute or traversing sourcing scope")
    return value


def validate_requirements(requirements):
    if not isinstance(requirements, list) or not requirements:
        raise ValueError("Nonempty sourcing requirements required")
    candidate = requirements[0]["candidate_id"]
    binding = tuple(requirements[0].get(key) for key in ("namespace", "input_id", "registry_id", "body_candidate_id"))
    seen, occurrence_keys, cost_scopes = set(), set(), []
    for requirement in requirements:
        validate_record(requirement, "requirement")
        if requirement["candidate_id"] != candidate or requirement["record_id"] in seen:
            raise ValueError("Mixed or duplicate candidate requirements")
        selected_product_id = requirement.get("selected_product_record_id")
        if selected_product_id is not None and not is_id(selected_product_id):
            raise ValueError("Exact selected immutable product record identity required")
        if tuple(requirement.get(key) for key in ("namespace", "input_id", "registry_id", "body_candidate_id")) != binding:
            raise ValueError("Mixed source revision or namespace; an explicit federation is required")
        seen.add(requirement["record_id"])
        for path in requirement.get("physical_scopes") or []:
            _canonical_scope(path)
        for occurrence in requirement["occurrence_ids"]:
            _canonical_scope(occurrence)
            key = (requirement["namespace"], occurrence)
            if key in occurrence_keys:
                raise ValueError("Overlapping sourcing occurrence scope")
            occurrence_keys.add(key)
        effective = requirement["occurrence_ids"] or requirement.get("physical_scopes") or []
        if requirement["quantity"] is not None:
            cost_scopes.extend((requirement["namespace"] + "/" + path) for path in effective)
    previous = None
    for path in sorted(cost_scopes):
        if previous is not None and (path == previous or path.startswith(previous + "/")):
            raise ValueError("Overlapping parent/child sourcing cost scope")
        previous = path
    return candidate

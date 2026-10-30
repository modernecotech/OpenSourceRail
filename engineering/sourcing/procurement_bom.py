"""Build a traceable draft sourcing-package BOM from one federated candidate.

Packages group located engineering stock by explicit vehicle/guideway hierarchy.
They are practical quote scopes, not approved assemblies, purchase quantities or
complete installed bills of material. Unlocated obligations remain separate.
"""
from collections import defaultdict
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import gzip
import json

from . import inputs
from .model import decimal, decimal_text, identity, is_id, validate_record
from .requirements import extract_requirements, validate_requirements

ROOT = Path(__file__).resolve().parents[2]

_PACKAGE_SPECS = {
    "vehicle-body-stock-kit": {
        "label": "Modeled vehicle-body-system stock kit",
        "unit_label": "one body-system stock kit for one car",
        "limitations": [
            "This kit contains only located body-system stock occurrences in the candidate BOM.",
            "It is not a complete car body or installed vehicle; doors, glazing, HVAC, controls, joints, finishes and other unresolved accounts are not supplied by this scope.",
        ],
    },
    "vehicle-bogie-stock-package": {
        "label": "Modeled passive-bogie stock package",
        "unit_label": "one modeled bogie stock package",
        "limitations": [
            "This package contains only the modeled located occurrences under one car/bogie path.",
            "It is not a complete qualified bogie assembly or a supplier order; brake equipment, interfaces, life limits and unresolved components remain open.",
        ],
    },
    "vehicle-secondary-stock-kit": {
        "label": "Modeled passive-secondary stock kit",
        "unit_label": "one modeled vehicle-secondary stock kit for one car",
        "limitations": [
            "This kit contains only located onboard-secondary stock occurrences under one car path.",
            "It is not a complete propulsion installation; verified magnetic design, insulation, clearances, joints, protection and service interfaces remain open.",
        ],
    },
    "civil-rail-stock-pair": {
        "label": "Modeled two-rail span stock package",
        "unit_label": "one modeled rail-pair stock package for one span",
        "limitations": [
            "The candidate labels these stocks as 60E1-mass-equivalent; this does not establish a purchased rail profile, length, weld plan, fastening system or delivered order quantity.",
            "The two rail occurrences are a sourcing scope only; track interfaces, wear, fatigue and installation remain open.",
        ],
    },
    "civil-concrete-stock-package": {
        "label": "Modeled nominal-concrete span stock package",
        "unit_label": "one nominal concrete stock package for one span",
        "limitations": [
            "Nominal stock geometry is not a designed mix, finished precast beam, reinforcement/prestress bill or purchase quantity.",
            "Moulds, production QA, handling, transport, foundations, erection and maintenance are outside this package.",
        ],
    },
    "wayside-lim-primary-material-set": {
        "label": "Modeled station-LIM primary material set",
        "unit_label": "one modeled primary-material set for one bank",
        "limitations": [
            "This set groups only the candidate's located copper and steel primary-stock occurrences for one bank.",
            "It is not a complete station drive or priceable motor assembly; electrical steel grade, windings, insulation, converter, cooling, supports, protection and installation remain unresolved.",
        ],
    },
}

_RULE_VERSION = "osr-procurement-package-rules/2"


def _unlocated_link_target(occurrence_id):
    """Resolve a conservative context link from an open account to a draft scope.

    Links are not package membership or quantity allocation. They only put an
    unresolved account beside a related quote scope using its explicit source
    hierarchy.
    """
    parts = occurrence_id.split("/")
    if len(parts) >= 3 and parts[0] == "car" and parts[1].isdigit():
        car = parts[1]
        system = parts[2]
        if system == "passive-bogie-pair":
            return (f"car/{car}/passive-bogie-pair", "vehicle-bogie-stock-package",
                    f"car/{car}/bogie/", "shared car-level bogie-pair completion account; not allocated per bogie")
        if system == "passive-secondary":
            return (f"car/{car}/passive-secondary", "vehicle-secondary-stock-kit",
                    f"car/{car}/station-secondary", "same-car passive-secondary completion account; excluded from located stock")
        if system in {"weld-interface", "new-frame-joints-and-fin-retention"}:
            return (f"car/{car}/{system}", "vehicle-body-stock-kit", f"car/{car}",
                    "same-car body joint/interface account; excluded from located stock")
        if system in {"retained-comfort", "service-battery", "white-roof-finish"}:
            return (f"car/{car}/{system}", "vehicle-body-stock-kit", f"car/{car}",
                    "same-car completion context only; excluded from the body-stock package")
    if len(parts) >= 3 and parts[0] == "span" and parts[1].isdigit():
        span = parts[1]
        account = parts[2]
        if account in {"direct_fastener_kg", "direct_fastener_anchors"}:
            return (f"span/{span}/track-fastening", "civil-rail-stock-pair", f"span/{span}",
                    "same-span rail-fastening account; excluded from the rail-stock package")
        if account in {"reinforcement_kg", "prestress_kg", "prestress_anchorage_kg"}:
            return (f"span/{span}/precast-reinforcement-and-prestress", "civil-concrete-stock-package",
                    f"span/{span}", "same-span reinforcement/prestress account; excluded from nominal-concrete stock")
    if len(parts) >= 3 and parts[0] == "bank" and parts[1].isdigit():
        return (f"bank/{parts[1]}/{parts[2]}", "wayside-lim-primary-material-set", f"bank/{parts[1]}",
                "same-bank completion account; excluded from primary-material stock")
    return None


def _link_unlocated_obligations(unlocated_ids, packages):
    """Publish hierarchy-only cross-references without allocating open scope."""
    by_package = defaultdict(list)
    for package in packages:
        by_package[(package["package_family"], package["package_key"])].append(package)
    grouped = defaultdict(lambda: {"obligation_ids": [], "package_ids": set()})
    linked_ids = set()
    for occurrence_id in sorted(unlocated_ids):
        rule = _unlocated_link_target(occurrence_id)
        if rule is None:
            continue
        scope_key, family, package_key, relationship = rule
        if family == "vehicle-bogie-stock-package" and package_key.endswith("/"):
            targets = [package for (candidate_family, candidate_key), rows in by_package.items()
                       if candidate_family == family and candidate_key.startswith(package_key)
                       for package in rows]
        else:
            targets = by_package.get((family, package_key), [])
        if not targets:
            continue
        target_ids = tuple(sorted(package["package_id"] for package in targets))
        key = (scope_key, relationship, target_ids)
        grouped[key]["obligation_ids"].append(occurrence_id)
        grouped[key]["package_ids"].update(target_ids)
        linked_ids.add(occurrence_id)

    links = []
    for (scope_key, relationship, target_ids), group in sorted(grouped.items()):
        body = {
            "scope_key": scope_key,
            "relationship": relationship,
            "unlocated_obligation_ids": sorted(group["obligation_ids"]),
            "related_package_ids": list(target_ids),
            "association_is_package_membership": False,
            "allocated_to_package_mass_or_quantity": False,
            "priced": False,
            "quantity": None,
        }
        body["link_id"] = identity(body)
        links.append(body)
    unlinked = sorted(set(unlocated_ids) - linked_ids)
    return {
        "relationship_basis": "exact car/span hierarchy and subsystem path; context-only cross-reference",
        "all_source_obligations_preserved": True,
        "source_obligation_count": len(unlocated_ids),
        "linked_unique_obligation_count": len(linked_ids),
        "unlinked_obligation_count": len(unlinked),
        "package_association_count": sum(len(row["related_package_ids"]) for row in links),
        "links_are_non_additive": True,
        "unlinked_obligation_ids": unlinked,
        "links": links,
    }


def _package_key(row):
    """Return a conservative package hierarchy key, or an individual hold key."""
    occurrence_id = row["id"]
    parts = occurrence_id.split("/")
    system = row.get("system")
    if system == "vehicle/body" and len(parts) >= 3 and parts[0] == "car" and parts[1].isdigit():
        return "vehicle-body-stock-kit", "car/" + parts[1]
    if (system == "vehicle/passive-bogie-pair" and len(parts) >= 5
            and parts[0] == "car" and parts[1].isdigit()
            and parts[2] == "bogie" and parts[3].isdigit()):
        return "vehicle-bogie-stock-package", "/".join(parts[:4])
    if (system == "vehicle/passive-secondary" and len(parts) >= 3
            and parts[0] == "car" and parts[1].isdigit()
            and parts[2] == "station-secondary"):
        return "vehicle-secondary-stock-kit", "/".join(parts[:3])
    if (system == "civil/rails" and len(parts) >= 3
            and parts[0] == "span" and parts[1].isdigit() and parts[2] == "rail"):
        return "civil-rail-stock-pair", "/".join(parts[:2])
    if (system == "civil/concrete" and len(parts) >= 2
            and parts[0] == "span" and parts[1].isdigit()):
        return "civil-concrete-stock-package", "/".join(parts[:2])
    if (system == "wayside/primary" and len(parts) >= 2
            and parts[0] == "bank" and parts[1].isdigit()):
        return "wayside-lim-primary-material-set", "/".join(parts[:2])
    return "unmapped-located-occurrence", occurrence_id


def _sum_field(rows, field):
    present = [decimal(row[field], field, nonnegative=True)
               for row in rows if row.get(field) is not None]
    missing = len(rows) - len(present)
    return (None if missing else decimal_text(sum(present, Decimal(0))), missing)


def _material_breakdown(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row.get("system"), row.get("material"), row.get("scope"))].append(row)
    result = []
    sort_key = lambda item: tuple("" if value is None else str(value) for value in item[0])
    for (system, material, stock_scope), members in sorted(grouped.items(), key=sort_key):
        mass, missing_mass = _sum_field(members, "accounted_mass_kg")
        volume, missing_volume = _sum_field(members, "nominal_stock_volume_m3")
        result.append({
            "system": system,
            "material": material,
            "stock_scope": stock_scope,
            "engineering_occurrence_count": len(members),
            "modeled_gross_stock_mass_kg": mass,
            "missing_mass_occurrence_count": missing_mass,
            "nominal_stock_volume_m3": volume,
            "missing_volume_occurrence_count": missing_volume,
        })
    return result


def _package_record(key, rows, group_by_occurrence, groups, procurement_by_group,
                    operations_by_group, candidate_id, evaluation_id, source_input_id):
    family, hierarchy = key
    rows = sorted(rows, key=lambda row: row["id"])
    occurrence_ids = [row["id"] for row in rows]
    group_ids = sorted({group_by_occurrence[occurrence_id]["group_id"]
                        for occurrence_id in occurrence_ids})
    source_groups = [groups[group_id] for group_id in group_ids]
    gross_values = [decimal(group["known_gross_stock_mass_kg"], "gross stock mass", nonnegative=True)
                    for group in source_groups if group.get("known_gross_stock_mass_kg") is not None]
    missing_gross_group_count = len(source_groups) - len(gross_values)
    gross_total = (None if missing_gross_group_count else
                   decimal_text(sum(gross_values, Decimal(0))))
    nominal_volume, missing_volume_occurrence_count = _sum_field(rows, "nominal_stock_volume_m3")
    accounted_mass, missing_mass_occurrence_count = _sum_field(rows, "accounted_mass_kg")
    spec = _PACKAGE_SPECS.get(family, {
        "label": "Unmapped located occurrence hold",
        "unit_label": "one unresolved located stock occurrence",
        "limitations": ["No reviewed sourcing-package rule matches this located occurrence; it remains a separate held line."],
    })
    procurement_ids = sorted({procurement_by_group[group_id]["id"]
                              for group_id in group_ids if group_id in procurement_by_group})
    operation_ids = sorted({operation_by_group["id"] for group_id in group_ids
                            for operation_by_group in operations_by_group.get(group_id, [])})
    body = {
        "candidate_id": candidate_id,
        "evaluation_id": evaluation_id,
        "source_input_id": source_input_id,
        "package_family": family,
        "package_key": hierarchy,
        "package_label": spec["label"],
        "package_unit_label": spec["unit_label"],
        "internal_package_unit_count": 1,
        "unit_count_basis": "one exact vehicle/bogie/span/bank hierarchy scope; not a supplier order unit",
        "engineering_occurrence_count": len(rows),
        "engineering_occurrence_ids": occurrence_ids,
        "manufacturing_group_count": len(group_ids),
        "manufacturing_group_ids": group_ids,
        "procurement_task_ids": procurement_ids,
        "manufacturing_operation_ids": operation_ids,
        "material_breakdown": _material_breakdown(rows),
        "component_definition_ids": sorted({row["component_definition_id"] for row in rows}),
        "geometry_ids": sorted({row["geometry_id"] for row in rows if row.get("geometry_id")}),
        "modeled_gross_stock_mass_kg": gross_total,
        "missing_gross_mass_group_count": missing_gross_group_count,
        "summed_member_accounted_mass_kg": accounted_mass,
        "missing_member_mass_occurrence_count": missing_mass_occurrence_count,
        "nominal_stock_volume_m3": nominal_volume,
        "missing_nominal_volume_occurrence_count": missing_volume_occurrence_count,
        "commercial_order_quantity": None,
        "commercial_order_unit": None,
        "yield_fraction": None,
        "material_price": None,
        "labour_hours": None,
        "direct_process_cost": None,
        "domestic_cost_estimate_scenarios": [],
        "complete_procurement_cost": None,
        "complete_installed_cost": None,
        "assembly_complete": False,
        "engineering_accepted": False,
        "procurement_approved": False,
        "supplier_rfq_sent": False,
        "physical_qualification": None,
        "limitations": list(spec["limitations"]),
    }
    body["package_id"] = identity(body)
    return body


def _attach_domestic_concrete_estimates(packages, reference, estimate_packets,
                                        candidate_id, source_input_id):
    if reference is None and not estimate_packets:
        return 0, 0, None
    if (not isinstance(reference, dict)
            or reference.get("schema") != "osr-iraq-domestic-cost-reference/1"
            or reference.get("packet_id") != identity(
                {key:value for key,value in reference.items() if key!="packet_id"})
            or reference.get("candidate_id") != candidate_id
            or reference.get("source_input_id") != source_input_id
            or reference.get("takeoff_mapped_for_baghdad_concrete_estimates") is not True):
        raise ValueError("Exact same-candidate regional domestic-cost reference required")
    indexed = {}
    for hours, estimate_packet in estimate_packets:
        if (not isinstance(estimate_packet, dict)
                or estimate_packet.get("schema") != "osr-domestic-fabrication-takeoff-estimate/1"
                or estimate_packet.get("estimate_packet_id") != identity(
                    {key:value for key,value in estimate_packet.items() if key!="estimate_packet_id"})
                or estimate_packet.get("candidate_id") != candidate_id
                or estimate_packet.get("source_input_id") != source_input_id
                or estimate_packet.get("takeoff_id") != reference.get("takeoff_id")
                or estimate_packet.get("candidate_takeoff_mapped") is not True):
            raise ValueError("Domestic cost scenario does not bind to the exact candidate/takeoff")
        hours = str(hours)
        if hours in indexed:
            raise ValueError("Duplicate domestic cost labour-hour scenario")
        process = estimate_packet.get("estimate")
        validate_record(process, "process")
        if (process.get("candidate_id") != candidate_id
                or process.get("input_id") != source_input_id
                or process.get("candidate_takeoff_id") != reference.get("takeoff_id")):
            raise ValueError("Domestic cost process identity differs from candidate/takeoff")
        rows = process.get("candidate_takeoff_group_refs")
        if not isinstance(rows, list) or not rows:
            raise ValueError("Group-level domestic cost allocations are required")
        by_group = {}
        for row in rows:
            group_id = row.get("manufacturing_group_id")
            if not is_id(group_id) or group_id in by_group:
                raise ValueError("Distinct exact manufacturing-group estimate links required")
            if not isinstance(row.get("fabrication_scenario"), dict):
                raise ValueError("Per-group material/labour estimate is missing")
            by_group[group_id] = row
        indexed[str(hours)] = (estimate_packet, process, by_group)

    refs = {str(row["labour_hours_per_nominal_m3"]):row
            for row in reference.get("baghdad_concrete_takeoff_estimates", [])}
    if set(indexed) != set(refs) or not indexed:
        raise ValueError("Regional reference and exact takeoff estimate scenario set differ")
    concrete_group_ids = {group_id for package in packages
                          if package["package_family"] == "civil-concrete-stock-package"
                          for group_id in package["manufacturing_group_ids"]}
    for hours, (estimate_packet, process, by_group) in indexed.items():
        if refs[hours].get("estimate_packet_id") != estimate_packet["estimate_packet_id"]:
            raise ValueError("Regional reference points to a different takeoff estimate packet")
        if set(by_group) != concrete_group_ids:
            raise ValueError("Regional takeoff estimates do not cover exactly the concrete span packages")

    cost_count = 0
    package_count = 0
    for package in packages:
        if package["package_family"] != "civil-concrete-stock-package":
            continue
        if len(package["manufacturing_group_ids"]) != 1:
            raise ValueError("One exact source concrete group per span package is required")
        group_id = package["manufacturing_group_ids"][0]
        scenario_rows = []
        for hours, (estimate_packet, process, by_group) in sorted(indexed.items(), key=lambda item:Decimal(item[0])):
            group = by_group.get(group_id)
            if group is None:
                raise ValueError("Concrete package group has no matching domestic cost estimate")
            if (group.get("engineering_occurrence_ids") != package["engineering_occurrence_ids"]
                    or group.get("engineering_group_key") != package["package_key"] + "/concrete"):
                raise ValueError("Concrete package membership differs from cost estimate membership")
            scenario = group["fabrication_scenario"]
            if Decimal(scenario["output_quantity"]) != Decimal(package["nominal_stock_volume_m3"]):
                raise ValueError("Concrete package volume differs from the cost estimate basis")
            scenario_rows.append({
                "labour_hours_per_nominal_m3": hours,
                "currency": scenario["currency"],
                "nominal_stock_volume_m3": scenario["output_quantity"],
                "direct_material_cost": scenario["direct_material_cost"],
                "direct_labor_cost": scenario["direct_labor_cost"],
                "uplift_fraction": scenario["uplift_fraction"],
                "uplift_amount": scenario["uplift_amount"],
                "estimated_unit_cost_iqd_per_nominal_m3": scenario["estimated_unit_cost"],
                "estimated_total_iqd": scenario["estimated_total"],
                "source_estimate_packet_id": estimate_packet["estimate_packet_id"],
                "source_process_record_id": process["record_id"],
                "supplier_quote": False,
                "commercial_order_quantity": None,
                "commercial_order_unit": None,
                "complete_process_cost": None,
                "complete_installed_cost": None,
                "basis": "CSO 2025 Baghdad material/wage observations; illustrative mix and declared labour scenario; 20% uplift on direct material plus labour",
            })
        package["domestic_cost_estimate_scenarios"] = scenario_rows
        package_count += 1
        cost_count += len(scenario_rows)
        package["package_id"] = identity({key:value for key,value in package.items() if key!="package_id"})
    return package_count, cost_count, reference["packet_id"]


def build_procurement_bom(twin_input, *, source_file_sha256=None, source_file_name=None,
                          source_code_hashes=None, source_evidence_hashes=None,
                          regional_cost_reference=None, concrete_estimate_packets=None):
    """Build reviewed sourcing packages while partitioning exact stock scopes."""
    if (not isinstance(twin_input, dict)
            or twin_input.get("schema") != "osr-sourcing-twin-input/1"
            or twin_input.get("payload_id") != identity(twin_input.get("payload"))):
        raise ValueError("Exact sealed sourcing twin input required")
    payload = twin_input["payload"]
    if not isinstance(payload, dict) or payload.get("schema") != "osr-federated-railway-BOM/1":
        raise ValueError("Procurement package BOM requires a federated railway BOM")
    requirements = extract_requirements(payload)
    candidate_id = validate_requirements(requirements)
    if candidate_id != payload.get("candidate_id"):
        raise ValueError("Procurement package candidate identity differs")

    occurrences = payload.get("engineering_BOM")
    manufacturing = payload.get("manufacturing_BOM")
    if not isinstance(occurrences, list) or not isinstance(manufacturing, list):
        raise ValueError("Exact engineering occurrences and manufacturing-group memberships required")
    rows = {}
    unlocated = []
    for row in occurrences:
        if not isinstance(row, dict) or row.get("candidate_id") != candidate_id:
            raise ValueError("Mixed candidate or malformed engineering occurrence")
        occurrence_id = row.get("id")
        if not isinstance(occurrence_id, str) or occurrence_id in rows:
            raise ValueError("Distinct engineering occurrence identities required")
        rows[occurrence_id] = row
        if row.get("scope") == "unlocated-account-or-obligation":
            unlocated.append(occurrence_id)
        elif row.get("scope") is None:
            raise ValueError("Explicit located/unlocated scope required")

    unresolved_index = payload.get("unresolved_occurrence_ids")
    if (not isinstance(unresolved_index, list)
            or len(unlocated) != len(set(unresolved_index))
            or set(unlocated) != set(unresolved_index)):
        raise ValueError("Unlocated obligations differ from their explicit source index")

    groups = {}
    group_by_occurrence = {}
    for group in manufacturing:
        if not isinstance(group, dict) or group.get("candidate_id") != candidate_id:
            raise ValueError("Mixed candidate manufacturing group")
        group_id = group.get("group_id")
        member_ids = group.get("engineering_occurrence_ids")
        if not is_id(group_id) or group_id in groups or not isinstance(member_ids, list) or not member_ids:
            raise ValueError("Distinct source manufacturing group identity and membership required")
        groups[group_id] = group
        for occurrence_id in member_ids:
            row = rows.get(occurrence_id)
            if row is None or row.get("scope") == "unlocated-account-or-obligation" or occurrence_id in group_by_occurrence:
                raise ValueError("Manufacturing groups must partition located occurrences exactly once")
            group_by_occurrence[occurrence_id] = group
    located_ids = {occurrence_id for occurrence_id, row in rows.items()
                   if row.get("scope") != "unlocated-account-or-obligation"}
    if set(group_by_occurrence) != located_ids:
        raise ValueError("Source manufacturing groups do not cover all located occurrences")

    procurement_by_group = {}
    for task in payload.get("procurement", []):
        group_id = task.get("manufacturing_group_id")
        if group_id not in groups or group_id in procurement_by_group:
            raise ValueError("Procurement tasks must resolve to one source group")
        procurement_by_group[group_id] = task
    operations_by_group = defaultdict(list)
    for operation in payload.get("manufacturing_operations", []):
        group_id = operation.get("manufacturing_group_id")
        if group_id not in groups:
            raise ValueError("Manufacturing operation references an unknown source group")
        operations_by_group[group_id].append(operation)
    if set(procurement_by_group) != set(groups) or set(operations_by_group) != set(groups):
        raise ValueError("Every source manufacturing group needs its exact procurement and operation records")

    buckets = defaultdict(list)
    for occurrence_id in sorted(located_ids):
        row = rows[occurrence_id]
        family, hierarchy = _package_key(row)
        buckets[(family, hierarchy)].append(row)
    packages = [
        _package_record(key, members, group_by_occurrence, groups, procurement_by_group,
                        operations_by_group, candidate_id, payload["evaluation_id"],
                        twin_input["payload_id"])
        for key, members in sorted(buckets.items())
    ]
    concrete_package_count, concrete_estimate_count, regional_reference_id = _attach_domestic_concrete_estimates(
        packages, regional_cost_reference, concrete_estimate_packets or [], candidate_id,
        twin_input["payload_id"])
    unlocated_links = _link_unlocated_obligations(unlocated, packages)

    assigned = [occurrence_id for package in packages
                for occurrence_id in package["engineering_occurrence_ids"]]
    if len(assigned) != len(set(assigned)) or set(assigned) != located_ids:
        raise ValueError("Draft package scopes must partition all located engineering occurrences")
    family_counts = defaultdict(int)
    for package in packages:
        family_counts[package["package_family"]] += 1
    scope_count = len(occurrences)
    result = {
        "schema": "osr-procurement-package-bom/1",
        "rule_version": _RULE_VERSION,
        "rule_set_id": identity({"rule_version": _RULE_VERSION, "families": _PACKAGE_SPECS}),
        "candidate_id": candidate_id,
        "evaluation_id": payload["evaluation_id"],
        "source_input_id": twin_input["payload_id"],
        "source_input_origin": deepcopy(twin_input.get("origin")),
        "source_sha256": {
            "supplied_input_file": source_file_sha256,
            "source_implementation": dict(source_code_hashes or {}),
            "domestic_cost_evidence": dict(source_evidence_hashes or {}),
        },
        "source_file_name": source_file_name,
        "engineering_scope_count": scope_count,
        "located_stock_occurrence_count": len(located_ids),
        "unlocated_obligation_count": len(unlocated),
        "unlocated_obligation_ids": sorted(unlocated),
        "unlocated_obligation_links": unlocated_links,
        "draft_package_count": len(packages),
        "package_family_counts": dict(sorted(family_counts.items())),
        "all_located_occurrences_assigned_exactly_once": True,
        "unmapped_located_occurrence_ids": sorted(
            occurrence_id for package in packages
            if package["package_family"] == "unmapped-located-occurrence"
            for occurrence_id in package["engineering_occurrence_ids"]),
        "commercial_order_quantities_known": False,
        "priced_draft_packages": 0,
        "packages_with_domestic_cost_estimates": concrete_package_count,
        "domestic_cost_estimate_scenario_count": concrete_estimate_count,
        "regional_cost_reference_packet_id": regional_reference_id,
        "complete_installed_bom": False,
        "complete_installed_cost": None,
        "physical_qualification": None,
        "engineering_accepted": False,
        "procurement_approved": False,
        "supplier_communications_sent": 0,
        "selected_reference_changed": False,
        "unknown_is_zero": False,
        "summary": {
            "located_occurrence_count": len(located_ids),
            "draft_package_count": len(packages),
            "unlocated_obligation_count": len(unlocated),
            "linked_unlocated_obligation_count": unlocated_links["linked_unique_obligation_count"],
            "unlinked_unlocated_obligation_count": unlocated_links["unlinked_obligation_count"],
            "unlocated_obligation_package_association_count": unlocated_links["package_association_count"],
            "unmapped_located_occurrence_count": sum(
                package["package_family"] == "unmapped-located-occurrence" for package in packages),
            "all_member_occurrences_preserved": True,
            "internal_package_counts_are_purchase_quantities": False,
            "packages_with_domestic_cost_estimates": concrete_package_count,
            "domestic_cost_estimate_scenario_count": concrete_estimate_count,
            "modeled_gross_stock_mass_kg": _sum_field(
                [row for row in occurrences if row.get("scope") != "unlocated-account-or-obligation"],
                "accounted_mass_kg")[0],
        },
        "limitations": [
            "Package rules reduce located geometry into quote-scope candidates using explicit car/bogie/span/bank hierarchy; they do not claim complete purchasing assemblies.",
            "The exact 4,773 unlocated accounts remain separate and are excluded from package quantities, mass and cost.",
            "Hierarchy-linked unlocated obligations are context-only cross-references to related quote scopes; they are not package membership, allocation or additive mass/quantity.",
            "Internal package counts and modeled gross stock mass are not commercial order quantities or complete installed mass.",
            "No package receives a supplier match, commercial price, material yield, complete process-hour estimate or approval from this grouping step; concrete-only domestic estimates remain explicitly bounded recipe scenarios.",
            "The source candidate is a research configuration. No result transfers to the selected v0.6 reference without a matching candidate identity and renewed evaluation.",
        ],
        "packages": packages,
    }
    result["packet_id"] = identity(result)
    return result


def write_packet(packet, output_path):
    """Write a fresh deterministic JSON or gzip packet."""
    path = Path(output_path).expanduser().resolve()
    if path.exists() or path.is_symlink():
        raise ValueError("Fresh procurement-package output path required")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(packet, sort_keys=True, ensure_ascii=False,
                     allow_nan=False, separators=(",", ":")).encode("utf-8") + b"\n"
    with path.open("xb") as stream:
        stream.write(gzip.compress(raw, mtime=0) if path.name.endswith(".gz") else raw)
    return path


def load_twin_input(path, *, member=None):
    """Load either an already sealed source wrapper or a raw typed twin input."""
    path = Path(path).expanduser().resolve()
    if member is None:
        value = inputs.read_json(path)
        if isinstance(value, dict) and value.get("schema") == "osr-sourcing-twin-input/1":
            if value.get("payload_id") != identity(value.get("payload")):
                raise ValueError("Sealed sourcing input payload ID differs")
            return value
    return inputs.load_twin(path, member=member)


def source_hashes():
    names = ("engineering/sourcing/procurement_bom.py", "engineering/sourcing/inputs.py",
             "engineering/sourcing/requirements.py", "engineering/sourcing/model.py",
             "engineering/station_rail/common.py")
    return {name: inputs.digest(ROOT / name) for name in names}

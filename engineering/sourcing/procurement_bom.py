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

_RULE_VERSION = "osr-procurement-package-rules/3"

_DOMESTIC_LEAD_RULES = {
    ("civil/concrete", "concrete-hypothesis"): {
        "iraq.sc-dpi-ready-mix": "Ready-mix and laboratory capability inquiry; not a precast beam offer.",
        "iraq.dijla-precast": "Precast production inquiry; product and guideway-beam compatibility unassessed.",
        "iraq.karbala-precast": "Precast production inquiry; product and guideway-beam compatibility unassessed.",
        "iraq.al-fayha-precast": "Precast production inquiry; product and guideway-beam compatibility unassessed.",
        "iraq.al-burhan-precast": "Precast production inquiry; product and guideway-beam compatibility unassessed.",
        "iraq.al-burhan-sleeper-factory": "Railway concrete sleeper precedent only; current product acceptance, pricing and guideway-beam compatibility unassessed.",
        "iraq.karbala-precast-bridge-beams": "Prestressed bridge-beam inquiry; section, load test, capacity, price and guideway compatibility unassessed.",
        "iraq.icsc-samawa-cement-plant": "Samawa cement-plant lead; current operation, cement grade, supply availability, concrete-mix and precast-beam capability unassessed.",
    },
    ("civil/rails", "60E1-mass-equivalent"): {},
    ("vehicle/body", "aluminium_reference"): {
        "iraq.asia-aluminium": "Profile/sheet supplier inquiry; alloy, temper, product form and design compatibility unassessed.",
        "iraq.alko-aluminium": "Profile/panel supplier inquiry; alloy, temper, product form and design compatibility unassessed.",
        "iraq.baxi-siwail-aluminium": "Profile/sheet supplier inquiry; alloy, temper, product form and design compatibility unassessed.",
        "iraq.ii-alco-aluminium": "Profile/sheet supplier inquiry; alloy, temper, product form and design compatibility unassessed.",
        "iraq.alkhassaki-aluminium-project": "Planned project lead only; current operating capacity is not established.",
        "iraq.duraid-al-sudani-metal-fabrication": "Metal fabrication inquiry; aluminium scope and design compatibility unassessed.",
        "iraq.scosi-extrusion-press-components-2026-03": "Documented local tooling/machining work for an aluminium-extrusion press; not an aluminium profile supplier or passenger-body fabricator, with capacity and price unassessed.",
    },
    ("vehicle/body", "gfrp_skin_research"): {
        "iraq-nubin-grp-facade": "GRP/GFRP façade manufacturing inquiry; passenger-body qualification unassessed.",
        "iraq.iraqalhur-grp-factory": "GRP pipe capability only; body-panel capability unassessed.",
        "iraq.ncpi-chemical-plastic-industries": "Local foam/adhesive and polymer-operations inquiry; infusion resin, glass reinforcement and structural body qualification unassessed.",
    },
    ("vehicle/passive-bogie-pair", "steel-reference"): {
        "iraq.scosi-steel-industries": "General steel fabrication lead; bogie design, fatigue, material and process qualification unassessed.",
        "iraq.scosi.foundry-forging": "Foundry/forging, heat-treatment and machining inquiry; bogie component identity, grade, fatigue and qualification unassessed.",
        "iraq.al-qader-steel-supply": "Steel plate/billet supply inquiry; origin, grade, current stock, delivery and bogie compatibility unassessed.",
        "iraq.star-steel": "Steel-product lead; bogie scope and qualification unassessed.",
        "iraq.alpha-steel": "Steel-product lead; bogie scope and qualification unassessed.",
        "iraq.duraid-al-sudani-metal-fabrication": "Metal fabrication inquiry; bogie scope and qualification unassessed.",
    },
    ("vehicle/passive-secondary", "6082-T6-proposed"): {
        "iraq.asia-aluminium": "Profile/sheet supplier inquiry; 6082-T6 temper and product compatibility unassessed.",
        "iraq.alko-aluminium": "Profile/panel supplier inquiry; 6082-T6 temper and product compatibility unassessed.",
        "iraq.baxi-siwail-aluminium": "Profile/sheet supplier inquiry; 6082-T6 temper and product compatibility unassessed.",
        "iraq.ii-alco-aluminium": "Profile/sheet supplier inquiry; 6082-T6 temper and product compatibility unassessed.",
        "iraq.alkhassaki-aluminium-project": "Planned project lead only; current operating capacity is not established.",
    },
    ("wayside/primary", "copper-conductor"): {
        "iraq.ms-cable-busbar": "Cable, bare-conductor and busbar inquiry; LIM winding grade and form compatibility unassessed.",
        "iraq.alrowad-cables": "Wire/cable inquiry; LIM winding grade and conductor-form compatibility unassessed.",
        "iraq.dici-copper-wire-line": "Planned production-line lead only; commissioning and current output are unverified.",
    },
    ("wayside/primary", "linear-steel-hypothesis"): {
        "iraq.scosi-steel-industries": "Steel fabrication lead; electrical-steel grade and lamination capability unassessed.",
        "iraq.star-steel": "Steel-product lead; electrical-steel grade and lamination capability unassessed.",
        "iraq.alpha-steel": "Steel-product lead; electrical-steel grade and lamination capability unassessed.",
    },
}


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
            or reference.get("schema") not in {"osr-iraq-domestic-cost-reference/1",
                                                "osr-iraq-domestic-cost-reference/2"}
            or reference.get("packet_id") != identity(
                {key:value for key,value in reference.items() if key!="packet_id"})
            or reference.get("candidate_id") != candidate_id
            or reference.get("source_input_id") != source_input_id
            or reference.get("takeoff_mapped_for_baghdad_concrete_estimates") is not True):
        raise ValueError("Exact same-candidate regional domestic-cost reference required")
    regional_rows = reference.get("regional_concrete_takeoff_estimates")
    if regional_rows is None:
        regional_rows = [dict(row, region="Baghdad", region_slug="baghdad")
                         for row in reference.get("baghdad_concrete_takeoff_estimates", [])]
    if (not isinstance(regional_rows, list) or not regional_rows
            or len({(row.get("region"), str(row.get("labour_hours_per_nominal_m3")))
                    for row in regional_rows if isinstance(row, dict)}) != len(regional_rows)):
        raise ValueError("Distinct region and labour-hour takeoff scenarios are required")
    indexed = {}
    for item in estimate_packets:
        if not isinstance(item, (tuple, list)) or len(item) not in (2, 3):
            raise ValueError("Concrete estimate packets must carry a region and labour-hour scenario")
        if len(item) == 2:
            hours, estimate_packet = item
            region = "Baghdad"
        else:
            region, hours, estimate_packet = item
        if not isinstance(region, str) or not region.strip():
            raise ValueError("A concrete estimate governorate label is required")
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
        key = (region.strip(), str(hours))
        if key in indexed:
            raise ValueError("Duplicate regional concrete estimate scenario")
        indexed[key] = (estimate_packet, process, by_group)

    refs = {(str(row.get("region", "Baghdad")),
             str(row["labour_hours_per_nominal_m3"])): row for row in regional_rows}
    if set(indexed) != set(refs) or not indexed:
        raise ValueError("Regional reference and exact takeoff estimate scenario set differ")
    concrete_group_ids = {group_id for package in packages
                          if package["package_family"] == "civil-concrete-stock-package"
                          for group_id in package["manufacturing_group_ids"]}
    for key, (estimate_packet, process, by_group) in indexed.items():
        if refs[key].get("estimate_packet_id") != estimate_packet["estimate_packet_id"]:
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
        for (region, hours), (estimate_packet, process, by_group) in sorted(
                indexed.items(), key=lambda item:(item[0][0], Decimal(item[0][1]))):
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
                "region": region,
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
                "basis": refs[(region, hours)].get(
                    "basis",
                    "CSO 2025 Baghdad material/wage observations; illustrative mix and declared labour scenario; 20% uplift on direct material plus labour"),
            })
        package["domestic_cost_estimate_scenarios"] = scenario_rows
        package_count += 1
        cost_count += len(scenario_rows)
        package["package_id"] = identity({key:value for key,value in package.items() if key!="package_id"})
    return package_count, cost_count, reference["packet_id"]


def _material_purchasing_rollup(packages, occurrences, groups, procurement_by_group,
                                operations_by_group, unlocated_links,
                                domestic_sources_by_key=None):
    """Publish practical material-demand units without inventing order quantities.

    The output collapses the engineering BOM to material-family lines in kg or
    m3. Those units can anchor a supplier inquiry, but stock yield, grade/form,
    minimum order, packaging and purchase approval remain separate.
    """
    occurrence_by_id = {row["id"]: row for row in occurrences}
    package_by_id = {row["package_id"]: row for row in packages}
    group_by_id = {row["group_id"]: row for row in groups}
    if len(group_by_id) != len(groups):
        raise ValueError("Distinct source manufacturing group identities required")
    group_members = {}
    for group_id, group in group_by_id.items():
        member_ids = group.get("engineering_occurrence_ids")
        if not isinstance(member_ids, list) or not member_ids or len(member_ids) != len(set(member_ids)):
            raise ValueError("Exact source manufacturing group membership required")
        if any(row_id not in occurrence_by_id for row_id in member_ids):
            raise ValueError("Source manufacturing group references an unknown occurrence")
        group_members[group_id] = [occurrence_by_id[row_id] for row_id in member_ids]

    grouped = defaultdict(lambda: {
        "group_ids": [], "occurrence_ids": [], "package_ids": set(),
        "masses": [], "member_masses": [], "volumes": [], "missing_mass_groups": 0,
        "missing_member_mass_groups": 0,
        "missing_volume_groups": 0, "missing_labour_groups": 0,
        "declared_labour_hours": [], "procurement_task_ids": set(), "operation_ids": set(),
    })
    group_to_package = {}
    for package in packages:
        for group_id in package["manufacturing_group_ids"]:
            if group_id in group_to_package:
                raise ValueError("A manufacturing group appears in multiple procurement packages")
            if group_id not in group_by_id:
                raise ValueError("Procurement package references an unknown manufacturing group")
            group_to_package[group_id] = package
    if set(group_to_package) != set(group_by_id):
        raise ValueError("Material-demand roll-up must cover every source manufacturing group")

    for group_id, group in group_by_id.items():
        members = group_members[group_id]
        if any(row.get("scope") == "unlocated-account-or-obligation" for row in members):
            raise ValueError("Unlocated obligations cannot enter material-demand quantities")
        keyset = {(row.get("system"), row.get("material"), row.get("scope")) for row in members}
        if len(keyset) != 1:
            raise ValueError("Material-demand roll-up cannot cross system, material or stock scope")
        system, material, stock_scope = next(iter(keyset))
        key = (system or "unclassified", material or "unclassified", stock_scope or "unclassified")
        package = group_to_package[group_id]
        if not set(row["id"] for row in members) <= set(package["engineering_occurrence_ids"]):
            raise ValueError("Source group membership differs from its quote package")
        acc = grouped[key]
        acc["group_ids"].append(group_id)
        acc["occurrence_ids"].extend(row["id"] for row in members)
        acc["package_ids"].add(package["package_id"])
        gross_mass = group.get("known_gross_stock_mass_kg")
        if gross_mass is None:
            acc["missing_mass_groups"] += 1
        else:
            acc["masses"].append(decimal(gross_mass, "source gross-stock mass", nonnegative=True))
        member_masses = [decimal(row["accounted_mass_kg"], "member accounted mass", nonnegative=True)
                         for row in members if row.get("accounted_mass_kg") is not None]
        if len(member_masses) == len(members):
            acc["member_masses"].append(sum(member_masses, Decimal(0)))
        else:
            acc["missing_member_mass_groups"] += 1
        volumes = [decimal(row["nominal_stock_volume_m3"], "stock volume", nonnegative=True)
                   for row in members if row.get("nominal_stock_volume_m3") is not None]
        if len(volumes) == len(members):
            acc["volumes"].append(sum(volumes, Decimal(0)))
        else:
            acc["missing_volume_groups"] += 1
        labour = group.get("labour_h")
        if labour is None:
            acc["missing_labour_groups"] += 1
        else:
            acc["declared_labour_hours"].append(decimal(labour, "declared process labour hours", nonnegative=True))
        task = procurement_by_group.get(group_id)
        if task is None:
            raise ValueError("Source manufacturing group lacks its procurement task")
        acc["procurement_task_ids"].add(task["id"])
        operations = operations_by_group.get(group_id, [])
        if not operations:
            raise ValueError("Source manufacturing group lacks its manufacturing operation")
        acc["operation_ids"].update(row["id"] for row in operations)

    linked_by_package = defaultdict(set)
    for link in unlocated_links.get("links", []):
        for package_id in link.get("related_package_ids", []):
            linked_by_package[package_id].add(link["link_id"])

    output = []
    for (system, material, stock_scope), acc in sorted(grouped.items()):
        is_concrete = system == "civil/concrete" and material == "concrete-hypothesis"
        unit = "m3" if is_concrete else "kg"
        values = acc["volumes"] if is_concrete else acc["masses"]
        missing = acc["missing_volume_groups"] if is_concrete else acc["missing_mass_groups"]
        quantity = None if missing else decimal_text(sum(values, Decimal(0)))
        gross_mass = (None if acc["missing_mass_groups"]
                      else decimal_text(sum(acc["masses"], Decimal(0))))
        member_mass = (None if acc["missing_member_mass_groups"]
                       else decimal_text(sum(acc["member_masses"], Decimal(0))))
        mass_residual = (None if gross_mass is None or member_mass is None
                         else decimal_text(Decimal(gross_mass) - Decimal(member_mass),
                                           nonnegative=False))
        missing_labour = acc["missing_labour_groups"]
        labour_hours = (None if missing_labour
                        else decimal_text(sum(acc["declared_labour_hours"], Decimal(0))))
        occurrence_ids = sorted(acc["occurrence_ids"])
        group_ids = sorted(acc["group_ids"])
        package_ids = sorted(acc["package_ids"])
        related_links = sorted({link_id for package_id in package_ids
                                for link_id in linked_by_package.get(package_id, set())})
        lead_rules = _DOMESTIC_LEAD_RULES.get((system, material), {})
        domestic_leads = []
        for source_key, relevance in sorted(lead_rules.items()):
            source = (domestic_sources_by_key or {}).get(source_key)
            if source is None:
                continue
            domestic_leads.append({
                "source_id": source["record_id"],
                "source_key": source_key,
                "publisher": source["publisher"],
                "source_url": source["url"],
                "source_retrieved_at": source["retrieved_at"],
                "source_kind": source["source_kind"],
                "manufacturer_location": source.get("manufacturer_location"),
                "source_product_groups": deepcopy(source.get("product_groups", [])),
                "source_access_scope": source["access"],
                "relevance": relevance,
                "relationship": "domestic supplier discovery lead; no product/specification match",
                "technical_compatibility": None,
                "price_recorded": False,
                "supplier_quotation": False,
                "procurement_approved": False,
            })
        domestic_scenarios = []
        if is_concrete:
            by_hours = defaultdict(list)
            for package_id in package_ids:
                for scenario in package_by_id[package_id].get("domestic_cost_estimate_scenarios", []):
                    by_hours[str(scenario["labour_hours_per_nominal_m3"])].append((package_id, scenario))
            for hours, rows in sorted(by_hours.items(), key=lambda item: Decimal(item[0])):
                complete = len(rows) == len(package_ids)
                total_volume = Decimal(0)
                material_cost = labor_cost = uplift = total_cost = Decimal(0)
                packet_ids, process_ids = set(), set()
                bases = set()
                for unused_package_id, scenario in rows:
                    material_cost += decimal(scenario["direct_material_cost"], "direct material cost")
                    labor_cost += decimal(scenario["direct_labor_cost"], "direct labour cost")
                    uplift += decimal(scenario["uplift_amount"], "uplift")
                    total_cost += decimal(scenario["estimated_total_iqd"], "estimate total")
                    total_volume += decimal(scenario["nominal_stock_volume_m3"], "estimated concrete volume")
                    packet_ids.add(scenario["source_estimate_packet_id"])
                    process_ids.add(scenario["source_process_record_id"])
                    bases.add(scenario["basis"])
                domestic_scenarios.append({
                    "labour_hours_per_nominal_m3": hours,
                    "currency": "IQD",
                    "covered_package_count": len(rows),
                    "required_package_count": len(package_ids),
                    "complete_group_coverage": complete,
                    "nominal_stock_volume_m3": None if not complete else decimal_text(total_volume),
                    "direct_material_cost": None if not complete else decimal_text(material_cost),
                    "direct_labour_cost": None if not complete else decimal_text(labor_cost),
                    "uplift_fraction": "0.20",
                    "uplift_amount": None if not complete else decimal_text(uplift),
                    "estimated_total_iqd": None if not complete else decimal_text(total_cost),
                    "estimated_unit_cost_iqd_per_nominal_m3": (
                        None if not complete or total_volume == 0
                        else decimal_text(total_cost / total_volume)),
                    "source_estimate_packet_ids": sorted(packet_ids),
                    "source_process_record_ids": sorted(process_ids),
                    "basis": sorted(bases),
                    "supplier_quote": False,
                    "commercial_order_quantity": None,
                    "complete_process_cost": None,
                    "complete_installed_cost": None,
                })

        body = {
            "system": system,
            "material": material,
            "stock_scope": stock_scope,
            "request_unit": unit,
            "modeled_material_demand": quantity,
            "modeled_gross_stock_mass_kg": gross_mass,
            "summed_member_accounted_mass_kg": member_mass,
            "gross_stock_mass_reconciliation_residual_kg": mass_residual,
            "missing_gross_mass_group_count": acc["missing_mass_groups"],
            "missing_member_mass_group_count": acc["missing_member_mass_groups"],
            "quantity_basis": ("sum of exact nominal concrete stock volumes; mix, reinforcement, prestress, yield and transport remain unresolved"
                               if is_concrete else "sum of exact modeled gross-stock masses; product form, grade compatibility, cut/yield loss and order packaging remain unresolved"),
            "engineering_group_count": len(group_ids),
            "engineering_group_ids": group_ids,
            "engineering_occurrence_count": len(occurrence_ids),
            "engineering_occurrence_ids": occurrence_ids,
            "related_package_ids": package_ids,
            "procurement_task_ids": sorted(acc["procurement_task_ids"]),
            "manufacturing_operation_ids": sorted(acc["operation_ids"]),
            "context_only_unlocated_obligation_link_ids": related_links,
            "context_only_unlocated_link_count": len(related_links),
            "domestic_fabrication_lead_sources": domestic_leads,
            "domestic_fabrication_lead_count": len(domestic_leads),
            "domestic_fabrication_leads_are_supplier_matches": False,
            "missing_demand_group_count": missing,
            "declared_direct_labour_hours": labour_hours,
            "missing_labour_group_count": missing_labour,
            "commercial_order_quantity": None,
            "commercial_order_unit": None,
            "purchase_yield_fraction": None,
            "direct_material_price": None,
            "complete_procurement_cost": None,
            "complete_installed_cost": None,
            "domestic_fabrication_estimate_scenarios": domestic_scenarios,
            "purchase_order_ready": False,
            "engineering_accepted": False,
            "procurement_approved": False,
        }
        body["material_line_id"] = identity(body)
        output.append(body)
    return output


def build_procurement_bom(twin_input, *, source_file_sha256=None, source_file_name=None,
                          source_code_hashes=None, source_evidence_hashes=None,
                          regional_cost_reference=None, concrete_estimate_packets=None,
                          domestic_source_records=None):
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
    domestic_sources = {}
    domestic_source_records = list(domestic_source_records or [])
    for source in domestic_source_records:
        validate_record(source, "source")
        source_key = source.get("source_key")
        if not isinstance(source_key, str) or source_key in domestic_sources:
            raise ValueError("Distinct canonical domestic source keys required")
        domestic_sources[source_key] = source
    material_purchasing_lines = _material_purchasing_rollup(
        packages, occurrences, manufacturing, procurement_by_group, operations_by_group,
        unlocated_links, domestic_sources)
    complete_group_mass_lines = [row for row in material_purchasing_lines
                                 if row["modeled_gross_stock_mass_kg"] is not None]
    complete_member_mass_lines = [row for row in material_purchasing_lines
                                  if row["summed_member_accounted_mass_kg"] is not None]
    material_demand_gross_mass = (None if len(complete_group_mass_lines) != len(material_purchasing_lines)
                                  else decimal_text(sum((decimal(row["modeled_gross_stock_mass_kg"],
                                                                "material-line gross mass")
                                                         for row in complete_group_mass_lines), Decimal(0))))
    material_demand_member_mass = (None if len(complete_member_mass_lines) != len(material_purchasing_lines)
                                   else decimal_text(sum((decimal(row["summed_member_accounted_mass_kg"],
                                                                 "material-line member mass")
                                                          for row in complete_member_mass_lines), Decimal(0))))
    material_demand_mass_residual = (
        None if material_demand_gross_mass is None or material_demand_member_mass is None
        else decimal_text(Decimal(material_demand_gross_mass) - Decimal(material_demand_member_mass),
                          nonnegative=False))

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
        "source_registry_record_set_id": identity(sorted(domestic_source_records,
                                                        key=lambda row: row["record_id"])),
        "source_registry_record_count": len(domestic_source_records),
        "domestic_lead_records_are_products_or_offers": False,
        "material_purchasing_lines": material_purchasing_lines,
        "material_purchasing_line_count": len(material_purchasing_lines),
        "material_demand_groups_preserved": sum(row["engineering_group_count"]
                                                  for row in material_purchasing_lines),
        "material_demand_occurrences_preserved": sum(row["engineering_occurrence_count"]
                                                      for row in material_purchasing_lines),
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
            "material_demand_line_count": len(material_purchasing_lines),
            "material_demand_quantity_count": sum(row["modeled_material_demand"] is not None
                                                   for row in material_purchasing_lines),
            "commercial_order_quantity_count": sum(row["commercial_order_quantity"] is not None
                                                    for row in material_purchasing_lines),
            "material_demand_group_count": sum(row["engineering_group_count"]
                                                for row in material_purchasing_lines),
            "material_demand_occurrence_count": sum(row["engineering_occurrence_count"]
                                                    for row in material_purchasing_lines),
            "material_demand_gross_stock_mass_kg": material_demand_gross_mass,
            "material_demand_member_accounted_mass_kg": material_demand_member_mass,
            "material_demand_mass_reconciliation_residual_kg": material_demand_mass_residual,
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

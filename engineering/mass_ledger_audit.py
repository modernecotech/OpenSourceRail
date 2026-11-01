"""Occurrence-to-account reconciliation for the selected v0.6 vehicle.

This is a reporting layer. It does not create missing installed mass, locations,
or qualification evidence.
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import math
import os
import tomllib
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

from engineering.station_rail import evaluation, vehicle
from engineering.station_rail.common import encoded, identity

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = "docs/design-engine/mass-reconciliation/current"
FLAGS = dict(
    engineering_accepted=False,
    physical_accepted=False,
    installed_mass_complete=False,
    manufacturing_release=False,
    operating_release=False,
)


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _deterministic_gzip(data: bytes) -> bytes:
    """Write a gzip member with a fixed header across supported Python versions."""
    target = io.BytesIO()
    with gzip.GzipFile(fileobj=target, filename="", mode="wb", mtime=0) as stream:
        stream.write(data)
    return target.getvalue()


def _row(**fields):
    fields["row_id"] = identity(fields)
    return fields


def _retained_source_rows(parent):
    excluded = {"magnetics", "propulsion", "protection", "hardpoints"}
    return [
        row for row in parent["inventory"]
        if row["system"] not in excluded
        and "replacement-frame/extrusion/frame/lower-stringer" not in row["id"]
    ]


def _source_geometry_index(retained):
    """Index geometry parts nested under retained source occurrence records."""
    by_part_id = {}
    for source in retained:
        for part in source.get("geometry_parts") or []:
            part_id = part.get("id")
            if not isinstance(part_id, str) or not part_id:
                raise ValueError("Retained source geometry requires an exact part ID")
            if part_id in by_part_id:
                raise ValueError("Retained source geometry part ID is owned more than once: " + part_id)
            by_part_id[part_id] = (source, part)
    return by_part_id


def _derived_source_component_geometry_groups(candidate_geometry, parent, retained):
    """Match explicitly declared material groups to their existing source accounts.

    The pinned comfort-design source stores some generated geometry globally
    while its corresponding inventory rows retain only a component-level mass.
    These rules join those records only when every part is present in the
    selected candidate and the complete group mass equals the source account.
    They are calculated group links, not exact per-part source-occurrence IDs.
    """
    rules = (
        dict(
            rule_id="comfort-design/deleted-door-infill-v1",
            occurrence_id="infill/blanked-door-stock",
            system="body",
            source_part_id="comfort-layout/infill",
            parent_families=("infill/",),
            final_part_ids=frozenset(("outer", "core", "inner", "bond")),
            expected_part_count=8,
        ),
        dict(
            rule_id="comfort-design/glazing-glass-v1",
            occurrence_id="glazing/glazing/glass",
            system="glazing",
            source_part_id="d39c677c95b2dc15006ca75c7f703a28d250b69555400ac0f428f36481f00fce",
            parent_families=("fixed-window/", "door-window/"),
            final_part_ids=frozenset(("glass-inner", "glass-outer")),
            expected_part_count=24,
        ),
        dict(
            rule_id="comfort-design/glazing-pvb-v1",
            occurrence_id="glazing/glazing/PVB",
            system="glazing",
            source_part_id="d39c677c95b2dc15006ca75c7f703a28d250b69555400ac0f428f36481f00fce",
            parent_families=("fixed-window/", "door-window/"),
            final_part_ids=frozenset(("PVB",)),
            expected_part_count=12,
        ),
    )
    parent_by_id = {part["id"]: part for part in parent["geometry_parts"]}
    candidate_by_id = {part["id"]: part for part in candidate_geometry}
    if len(parent_by_id) != len(parent["geometry_parts"]):
        raise ValueError("Parent source geometry part IDs must be unique")
    if len(candidate_by_id) != len(candidate_geometry):
        raise ValueError("Candidate geometry part IDs must be unique")
    retained_by_id = {row["id"]: row for row in retained}
    part_links = {}
    groups = []
    for rule in rules:
        source = retained_by_id.get(rule["occurrence_id"])
        if source is None:
            raise ValueError("Calculated source geometry rule has no retained source occurrence: " + rule["rule_id"])
        if source["system"] != rule["system"] or source.get("source_part_id") != rule["source_part_id"]:
            raise ValueError("Calculated source geometry rule differs from its pinned source component: " + rule["rule_id"])
        if source.get("geometry_parts"):
            # A future parent that carries direct nested geometry should use
            # the stronger exact source-geometry link path instead.
            continue
        selected = [
            part for part in parent["geometry_parts"]
            if part["id"].startswith(rule["parent_families"])
            and part["id"].rsplit("/", 1)[-1] in rule["final_part_ids"]
        ]
        selected.sort(key=lambda part: part["id"])
        if len(selected) != rule["expected_part_count"]:
            raise ValueError("Calculated source geometry group has unexpected part count: " + rule["rule_id"])
        mapped = []
        for source_part in selected:
            candidate_id = "comfort-shell/" + source_part["id"]
            candidate_part = candidate_by_id.get(candidate_id)
            if candidate_part is None:
                raise ValueError("Calculated source geometry part is absent from the selected candidate: " + candidate_id)
            if abs(float(candidate_part["mass_kg"]) - float(source_part["mass_kg"])) > 1e-7:
                raise ValueError("Calculated source geometry part differs from its pinned source mass: " + candidate_id)
            if candidate_id in part_links:
                raise ValueError("Candidate geometry part belongs to multiple calculated source groups: " + candidate_id)
            mapped.append((candidate_id, source_part))
        mapped_mass = math.fsum(float(candidate_by_id[name]["mass_kg"]) for name, _ in mapped)
        source_mass = float(source["mass_kg"])
        difference = mapped_mass - source_mass
        if abs(difference) > 1e-7:
            raise ValueError("Calculated source geometry group does not reconcile to its source account: " + rule["rule_id"])
        group = dict(
            rule_id=rule["rule_id"],
            occurrence_id=source["id"],
            source_system=source["system"],
            source_part_id=source.get("source_part_id"),
            source_account_mass_kg=source_mass,
            parent_geometry_part_ids=[part["id"] for _, part in mapped],
            candidate_geometry_occurrence_ids=[name for name, _ in mapped],
            candidate_geometry_mass_kg=mapped_mass,
            mass_difference_kg=difference,
            mapping_method="declared-geometry-family-and-exact-group-mass",
        )
        groups.append(group)
        for candidate_id, source_part in mapped:
            part_links[candidate_id] = dict(
                source=source,
                parent_geometry_part=source_part,
                rule_id=rule["rule_id"],
                group_mass_kg=mapped_mass,
                group_mass_difference_kg=difference,
            )
    return part_links, groups


def _roof_finish_distribution_estimate(candidate, parent):
    """Estimate a uniform finish distribution without changing located mass."""
    account = next((row for row in candidate["inventory"] if row.get("id") == "white-roof-finish"), None)
    if account is None:
        raise ValueError("Selected candidate has no white-roof-finish account")
    thickness = float(account.get("thickness_m", 0.0))
    density = float(account.get("density_kg_m3", 0.0))
    floor_height = float(candidate["physical_definition"]["vehicle"]["floor_top_above_rail_m"])
    if (not math.isfinite(thickness) or not math.isfinite(density)
            or thickness <= 0.0 or density <= 0.0):
        raise ValueError("Roof finish requires finite positive declared thickness and density")

    source_parts = sorted(
        (part for part in parent["geometry_parts"]
         if part.get("id", "").startswith("roof/panel/")
         and part.get("id", "").endswith("/skin/top")),
        key=lambda part: part["id"],
    )
    if not source_parts:
        raise ValueError("Pinned parent geometry has no roof upper-skin surfaces")
    candidate_ids = {part["id"] for part in candidate["geometry_parts"]}
    areas = []
    for part in source_parts:
        size = part.get("size_m")
        at = part.get("at_m")
        if part.get("kind") != "box" or not isinstance(size, list) or len(size) != 3 or not isinstance(at, list) or len(at) != 3:
            raise ValueError("Roof finish source surfaces require explicit box dimensions and positions")
        if min(float(value) for value in size) <= 0.0:
            raise ValueError("Roof finish source surfaces require positive dimensions")
        if "comfort-shell/" + part["id"] not in candidate_ids:
            raise ValueError("Roof finish source surface is absent from selected candidate geometry: " + part["id"])
        area = float(size[0]) * float(size[1])
        surface_centroid = [
            float(at[0]) + float(size[0]) / 2.0,
            float(at[1]) + float(size[1]) / 2.0,
            float(at[2]) + float(size[2]) + floor_height,
        ]
        areas.append((part["id"], area, surface_centroid))

    area_m2 = sum(area for _, area, _ in areas)
    mass_kg = area_m2 * thickness * density
    if not math.isfinite(area_m2) or not math.isfinite(mass_kg) or area_m2 <= 0.0:
        raise ValueError("Roof finish surface estimate must be finite and positive")
    if abs(mass_kg - float(account["mass_kg"])) > 1e-7:
        raise ValueError("Roof finish surface takeoff does not reconcile to the existing scalar account")
    centroid = [
        sum(area * point[axis] for _, area, point in areas) / area_m2
        for axis in range(3)
    ]
    centroid[2] += thickness / 2.0
    return dict(
        estimate_id=None,
        record_kind="analytical-surface-distribution-estimate",
        account_id="roof-thermal",
        source_account_occurrence_id="white-roof-finish",
        source_geometry_part_ids=[part_id for part_id, _, _ in areas],
        candidate_geometry_occurrence_ids=[],
        surface_area_m2=area_m2,
        coating_thickness_m=thickness,
        assumed_density_kg_m3=density,
        estimated_mass_kg=mass_kg,
        estimated_candidate_centroid_m=centroid,
        candidate_frame_basis="Pinned roof upper-skin surface centroids translated by the selected 1 m floor height; uniform coating centroid offset by half the declared thickness.",
        calculation="sum(roof upper-skin plan areas) × declared coating thickness × declared coating density",
        distribution_assumptions=[
            "The finish covers every modelled roof upper-skin surface uniformly.",
            "No deductions are made for seams, apertures, panel overlaps or solar equipment.",
            "The declared coating thickness and density are assumptions, not supplier or measured evidence.",
        ],
        physical_installation_position_m=None,
        mass_added_to_accounted_tare_kg=0.0,
        located_geometry_mass_change_kg=0.0,
        account_residual_change_kg=0.0,
        account_residual_after_estimate_kg=float(account["mass_kg"]),
        installed_mass_complete=False,
        physical_acceptance=False,
    )


def _service_battery_component_breakdown(item):
    """Expose existing service-pack mass arithmetic without inventing geometry."""
    definition = item.get("basis")
    if not isinstance(definition, dict):
        raise ValueError("Service-battery account requires its candidate-bound electrical definition")
    module_count = definition.get("module_count")
    series_count = definition.get("modules_in_series")
    parallel_strings = definition.get("parallel_strings")
    module_mass = definition.get("supplier_module_mass_kg")
    accessories = definition.get("accessories")
    counts = (module_count, series_count, parallel_strings)
    if (any(type(value) is not int or value <= 0 for value in counts)
            or type(module_mass) not in (int, float)
            or not math.isfinite(module_mass) or module_mass <= 0
            or module_count != series_count * parallel_strings
            or type(accessories) is not list or not accessories):
        raise ValueError("Service-battery module count and mass inputs must be finite and consistent")
    unit_module_mass = float(module_mass) / int(module_count)
    components = [dict(
        component_id="toshiba-type3-20-module-reference",
        description=definition.get("supplier_reference"),
        quantity=int(module_count),
        unit="module",
        unit_mass_kg=unit_module_mass,
        accounted_mass_kg=float(module_mass),
        mass_basis=(f"Supplier-reference module mass multiplied by the declared {series_count}-series by "
                    f"{parallel_strings}-parallel quantity; not rail application approval or a measured installed pack."),
        evidence_class="supplier-reference",
        source_reference_ids=[source.get("title", source.get("url"))
                              for source in definition.get("sources", [])],
        geometry_part_ids=[],
        installed_position_m=None,
        physical_mass_measured=False,
    )]
    accessory_ids = set()
    for accessory in accessories:
        if not isinstance(accessory, dict):
            raise ValueError("Service-battery accessory allowance records must be objects")
        description = accessory.get("component")
        mass = accessory.get("mass_kg")
        if (not isinstance(description, str) or not description.strip()
                or type(mass) not in (int, float) or not math.isfinite(mass) or mass < 0):
            raise ValueError("Service-battery accessories require named finite nonnegative masses")
        component_id = "allowance/" + description.strip().lower().replace(" ", "-")
        if component_id in accessory_ids:
            raise ValueError("Service-battery accessory allowance names must be unique")
        accessory_ids.add(component_id)
        components.append(dict(
            component_id=component_id,
            description=description,
            quantity=1,
            unit="per-car allowance",
            unit_mass_kg=float(mass),
            accounted_mass_kg=float(mass),
            mass_basis="Explicit per-car design allowance from the selected service-battery definition; material, supplier, geometry and installed position are unresolved.",
            evidence_class="engineering-mass-assumption",
            source_reference_ids=["engineering/station_rail/electrical.py"],
            geometry_part_ids=[],
            installed_position_m=None,
            physical_mass_measured=False,
        ))
    total = math.fsum(row["accounted_mass_kg"] for row in components)
    account_mass = float(item["mass_kg"])
    if (abs(total - account_mass) > 1e-8
            or abs(float(definition.get("mass_kg", float("nan"))) - account_mass) > 1e-8
            or abs(unit_module_mass * module_count - float(module_mass)) > 1e-8):
        raise ValueError("Service-battery component masses do not reconcile to the existing account")
    return dict(
        schema="osr-service-battery-account-breakdown/1",
        supplier_reference=definition.get("supplier_reference"),
        battery_component_id=definition.get("component_id"),
        module_count=int(module_count),
        modules_in_series=int(series_count),
        parallel_strings=int(parallel_strings),
        gross_energy_kWh=definition.get("gross_energy_kWh"),
        components=components,
        component_count=len(components),
        calculated_account_mass_kg=total,
        source_account_mass_kg=account_mass,
        account_difference_kg=total - account_mass,
        geometry_complete=False,
        installed_positions_known=False,
        physically_installed_mass_known=False,
        additive_to_source_account=False,
        supplier_railway_approval=definition.get("supplier_railway_approval") is True,
    )


def _retained_account_component_breakdown(account, source_occurrences, geometry_occurrences):
    """Summarize existing source rows against their linked candidate geometry."""
    account_id = account["account_id"]
    source_rows = [row for row in source_occurrences if row["account_id"] == account_id]
    if not source_rows:
        raise ValueError(f"Mass account {account_id} has no source occurrence rows")

    geometry_by_id = {row["occurrence_id"]: row for row in geometry_occurrences}
    groups = {}
    linked_geometry_ids = set()
    for source in source_rows:
        mass = float(source["mass_kg"])
        key = (
            source.get("source_part_id"), source.get("evidence_class"),
            source.get("role"), round(mass, 9),
        )
        group = groups.setdefault(key, {
            "source_rows": [], "geometry_ids": [], "geometry_mass_kg": [],
        })
        group["source_rows"].append(source)
        for occurrence_id in source.get("candidate_geometry_occurrence_ids", []):
            if occurrence_id in linked_geometry_ids:
                raise ValueError(f"Candidate geometry occurrence {occurrence_id} is linked to multiple source rows")
            geometry = geometry_by_id.get(occurrence_id)
            if geometry is None or geometry["account_id"] != account_id:
                raise ValueError(f"Source account {account_id} links an absent or differently-accounted geometry occurrence")
            linked_geometry_ids.add(occurrence_id)
            group["geometry_ids"].append(occurrence_id)
            group["geometry_mass_kg"].append(float(geometry["mass_kg"]))

    ordered = sorted(
        groups.items(),
        key=lambda item: (
            item[0][0] == "ancestor/interior800",
            -item[0][3],
            str(item[0][0]),
        ),
    )
    fixture_class = 0
    components = []
    for key, group in ordered:
        source_part_id, evidence_class, role, unit_mass_kg = key
        source_mass = math.fsum(float(row["mass_kg"]) for row in group["source_rows"])
        geometry_mass = math.fsum(group["geometry_mass_kg"])
        residual_mass = source_mass - geometry_mass
        if residual_mass < -1e-7:
            raise ValueError(f"Source account component exceeds its mass in candidate geometry: {account_id}")
        if residual_mass < 0:
            residual_mass = 0.0
        if account_id == "retained-comfort/HVAC":
            description = "Supplier-reference HVAC package"
            component_id = "supplier-reference-hvac-package"
        elif source_part_id == "ancestor/interior800":
            description = "Other-interior allowance without candidate geometry"
            component_id = "other-interior-unlocated-allowance"
        elif account_id == "retained-comfort/seating":
            fixture_class += 1
            suffix = chr(ord("A") + fixture_class - 1)
            description = f"Seat fixture source mass class {suffix}"
            component_id = f"seat-fixture-class-{suffix.lower()}"
        elif account_id == "retained-comfort/doors":
            if str(source_part_id).startswith("Wabtec-"):
                description = "1300 mm door-operator supplier reference"
                component_id = "door-operator-reference"
            else:
                description = "Proposed door-leaf material"
                component_id = "door-leaf-material"
        elif account_id == "retained-comfort/glazing":
            occurrence_tail = group["source_rows"][0]["occurrence_id"].rsplit("/", 1)[-1]
            description = {
                "EPDM-seal": "EPDM glazing seals",
                "PVB": "PVB interlayers",
                "bond": "Glazing bond allowance",
                "glass": "Glass panes",
                "retention-aluminium": "Aluminium glazing retention",
            }.get(occurrence_tail, occurrence_tail)
            component_id = "glazing/" + occurrence_tail.lower()
        elif account_id == "retained-comfort/frame-joints":
            description = {
                "hardpoints/roof-spreader": "Roof-spreader plates",
                "joints/gusset": "Frame-joint gusset plates",
                "joints/crush-sleeve": "Crush sleeves",
                "joints/M8-shank": "M8 bolt shanks",
                "joints/M8-head-and-nut": "M8 head-and-nut stock envelopes",
                "hardpoints/GFRP-isolator": "GFRP hardpoint isolators",
                "joints/GFRP-isolation": "GFRP joint-isolation pads",
                "joints/bond-film": "Joint bond film",
            }.get(source_part_id, str(source_part_id or role))
            component_id = "frame-joints/" + str(source_part_id).lower().replace("/", "-")
        else:
            description = str(source_part_id or role or "Unspecified source component")
            component_id = "source-component/" + str(source_part_id or description).lower().replace("/", "-")
        components.append(dict(
            component_id=component_id,
            description=description,
            quantity=len(group["source_rows"]),
            unit="source occurrence",
            unit_mass_kg=float(unit_mass_kg),
            source_account_mass_kg=source_mass,
            candidate_geometry_occurrence_count=len(group["geometry_ids"]),
            candidate_geometry_mass_kg=geometry_mass,
            residual_mass_kg=residual_mass,
            evidence_class=evidence_class,
            source_role=role,
            source_part_id=source_part_id,
            source_occurrence_ids=sorted(row["occurrence_id"] for row in group["source_rows"]),
            physical_mass_measured=False,
            installed_position_known=False,
        ))

    source_mass = math.fsum(float(row["mass_kg"]) for row in source_rows)
    geometry_mass = math.fsum(
        float(row["mass_kg"]) for row in geometry_occurrences
        if row["occurrence_id"] in linked_geometry_ids
    )
    residual_mass = source_mass - geometry_mass
    if (abs(source_mass - float(account["accounted_mass_kg"])) > 1e-7
            or abs(geometry_mass - float(account["located_geometry_mass_kg"])) > 1e-7
            or abs(residual_mass - float(account["residual_account_mass_kg"])) > 1e-7):
        raise ValueError(f"Component detail does not reconcile to source mass account {account_id}")
    return dict(
        schema="osr-retained-mass-account-component-breakdown/1",
        account_id=account_id,
        components=components,
        source_account_mass_kg=source_mass,
        candidate_geometry_mass_kg=geometry_mass,
        residual_account_mass_kg=residual_mass,
        additive_to_accounted_tare=False,
        installed_mass_complete=False,
        physical_acceptance=False,
    )


def _bogie_geometry_component_breakdown(account, geometry_occurrences):
    """Group explicitly modelled bogie solids while retaining the account balance."""
    component_labels = {
        "axle": "Axle solids",
        "wheel": "Wheel rims, webs and hubs",
        "brake": "Brake discs",
        "sideframe": "Bogie sideframes",
        "bolster": "Bolsters",
    }
    bogie_parts = [
        row for row in geometry_occurrences
        if row["account_id"] == account["account_id"] and row["occurrence_id"].startswith("bogie/")
    ]
    if not bogie_parts:
        raise ValueError("Passive-bogie account has no explicitly modelled bogie geometry")
    bogie_ids = {row["occurrence_id"].split("/")[1] for row in bogie_parts}
    grouped = defaultdict(list)
    for row in bogie_parts:
        parts = row["occurrence_id"].split("/")
        if len(parts) < 3 or parts[2] not in component_labels:
            raise ValueError(f"Unclassified candidate bogie geometry occurrence: {row['occurrence_id']}")
        grouped[parts[2]].append(row)
    components = [dict(
        component_id=component_id,
        description=component_labels[component_id],
        candidate_geometry_occurrence_count=len(rows),
        candidate_geometry_mass_kg=math.fsum(float(row["mass_kg"]) for row in rows),
        candidate_geometry_occurrence_ids=sorted(row["occurrence_id"] for row in rows),
    ) for component_id, rows in sorted(grouped.items())]
    located_mass = math.fsum(row["candidate_geometry_mass_kg"] for row in components)
    residual_mass = float(account["residual_account_mass_kg"])
    if (len(bogie_ids) < 1
            or abs(located_mass - float(account["located_geometry_mass_kg"])) > 1e-7
            or abs(located_mass + residual_mass - float(account["accounted_mass_kg"])) > 1e-7):
        raise ValueError("Bogie geometry groups do not reconcile to the existing pair account")
    return dict(
        schema="osr-bogie-geometry-component-breakdown/1",
        bogies_per_car=len(bogie_ids),
        reference_account_mass_kg=float(account["accounted_mass_kg"]),
        candidate_geometry_mass_kg=located_mass,
        residual_account_mass_kg=residual_mass,
        residual_per_bogie_kg=residual_mass / len(bogie_ids),
        components=components,
        unallocated_account_residual=True,
        installed_mass_complete=False,
        physical_acceptance=False,
    )


def _retained_body_source_scope_breakdown(account, source_occurrences, geometry_occurrences):
    """Reconcile the retained body source scopes against their candidate solids."""
    account_id = account["account_id"]
    source_rows = [row for row in source_occurrences if row["account_id"] == account_id]
    geometry_by_id = {row["occurrence_id"]: row for row in geometry_occurrences}
    linked_ids = set()
    grouped = {}
    for source in source_rows:
        key = (source.get("evidence_class"), source.get("role"))
        group = grouped.setdefault(key, {
            "source_rows": [], "geometry_ids": [], "geometry_mass_kg": [],
        })
        group["source_rows"].append(source)
        for occurrence_id in source.get("candidate_geometry_occurrence_ids", []):
            if occurrence_id in linked_ids:
                raise ValueError(f"Candidate body geometry occurrence {occurrence_id} is linked to multiple source rows")
            geometry = geometry_by_id.get(occurrence_id)
            if geometry is None or geometry["account_id"] != account_id:
                raise ValueError("Body source scope links absent or differently-accounted candidate geometry")
            linked_ids.add(occurrence_id)
            group["geometry_ids"].append(occurrence_id)
            group["geometry_mass_kg"].append(float(geometry["mass_kg"]))

    scopes = []
    for (evidence_class, role), group in sorted(
        grouped.items(), key=lambda item: (-math.fsum(float(row["mass_kg"]) for row in item[1]["source_rows"]), str(item[0])),
    ):
        source_mass = math.fsum(float(row["mass_kg"]) for row in group["source_rows"])
        geometry_mass = math.fsum(group["geometry_mass_kg"])
        residual = source_mass - geometry_mass
        if residual < -1e-7:
            raise ValueError("Candidate body geometry exceeds its retained source scope")
        scopes.append(dict(
            evidence_class=evidence_class,
            source_role=role,
            source_occurrence_count=len(group["source_rows"]),
            source_occurrence_ids=sorted(row["occurrence_id"] for row in group["source_rows"]),
            source_account_mass_kg=source_mass,
            candidate_geometry_occurrence_count=len(group["geometry_ids"]),
            candidate_geometry_mass_kg=geometry_mass,
            residual_mass_kg=max(0.0, residual),
        ))
    source_mass = math.fsum(float(row["mass_kg"]) for row in source_rows)
    geometry_mass = math.fsum(float(row["mass_kg"]) for row in geometry_occurrences if row["occurrence_id"] in linked_ids)
    residual = source_mass - geometry_mass
    if (abs(source_mass - float(account["accounted_mass_kg"])) > 1e-7
            or abs(geometry_mass - float(account["located_geometry_mass_kg"])) > 1e-7
            or abs(residual - float(account["residual_account_mass_kg"])) > 1e-7):
        raise ValueError("Body source-scope breakdown does not reconcile to the body account")
    return dict(
        schema="osr-retained-body-source-scope-breakdown/1",
        scopes=scopes,
        source_account_mass_kg=source_mass,
        candidate_geometry_mass_kg=geometry_mass,
        residual_account_mass_kg=residual,
        additive_to_accounted_tare=False,
        installed_mass_complete=False,
        physical_acceptance=False,
    )


def reconcile(candidate, parent):
    """Map source accounts and candidate geometry by explicit parent account."""
    geometry = candidate["geometry_parts"]
    geometry_ids = [part["id"] for part in geometry]
    if len(geometry_ids) != len(set(geometry_ids)):
        raise ValueError("Duplicate candidate geometry occurrence ID")
    retained = _retained_source_rows(parent)
    retained_ids = [row["id"] for row in retained]
    if len(set(retained_ids)) != len(retained):
        raise ValueError("Duplicate retained source inventory occurrence ID")
    retained_by_id = {row["id"]: row for row in retained}
    retained_accounts = defaultdict(list)
    for source in retained:
        retained_accounts[source["system"]].append(source)
    source_geometry_by_id = _source_geometry_index(retained)

    # Preserve the stronger existing occurrence-level failures before testing
    # the lower-confidence component-group mappings below.  This also keeps a
    # corrupted candidate from being reported only as a derived group mismatch.
    candidate_system_mass = defaultdict(float)
    for part in geometry:
        part_id = part["id"]
        if not part_id.startswith("comfort-shell/"):
            continue
        suffix = part_id[len("comfort-shell/"):]
        family = suffix.split("/", 1)[0]
        if family == "seat-unit":
            system = "seating"
        elif family == "door":
            system = "doors"
        elif family in ("fixed-window", "door-window"):
            system = "glazing"
        else:
            system = "body"
        candidate_system_mass[system] += float(part["mass_kg"])
        source_occurrence = retained_by_id.get(suffix)
        if source_occurrence is not None:
            if source_occurrence["system"] != system:
                raise ValueError(
                    "Directly linked source occurrence and candidate geometry belong to different mass accounts: "
                    + part_id
                )
            if abs(float(part["mass_kg"]) - float(source_occurrence["mass_kg"])) > 1e-7:
                raise ValueError("Candidate geometry mass differs from its exact source occurrence: " + part_id)
        exact_source_geometry = source_geometry_by_id.get(suffix)
        if exact_source_geometry is not None:
            source, source_part = exact_source_geometry
            if abs(float(part["mass_kg"]) - float(source_part["mass_kg"])) > 1e-7:
                raise ValueError("Candidate comfort geometry mass differs from its exact source geometry part: " + part_id)
    for system, mass in candidate_system_mass.items():
        account_mass = math.fsum(float(row["mass_kg"]) for row in retained_accounts[system])
        if mass - account_mass > 1e-7:
            raise ValueError("Located geometry exceeds retained system account: " + system)

    derived_source_geometry_links, derived_source_geometry_groups = (
        _derived_source_component_geometry_groups(geometry, parent, retained)
    )
    parent_geometry_by_id = {part["id"]: part for part in parent["geometry_parts"]}
    if len(parent_geometry_by_id) != len(parent["geometry_parts"]):
        raise ValueError("Parent source geometry part IDs must be unique")
    source_to_candidate_geometry = defaultdict(list)
    source_geometry_links = {}
    source_to_direct_candidate_geometry = defaultdict(list)
    source_occurrence_links = {}
    source_to_derived_candidate_geometry = defaultdict(list)
    retained_geometry = defaultdict(list)
    new_geometry = defaultdict(list)
    geometry_parent = {}
    for part in geometry:
        part_id = part["id"]
        source_geometry_link = None
        derived_source_geometry_link = None
        if part_id.startswith("comfort-shell/"):
            source_geometry_part_id = part_id[len("comfort-shell/"):]
            source_geometry_link = source_geometry_by_id.get(source_geometry_part_id)
            derived_source_geometry_link = derived_source_geometry_links.get(part_id)
            if source_geometry_link is not None and derived_source_geometry_link is not None:
                raise ValueError("Candidate geometry occurrence cannot use exact and derived source links together")
            if source_geometry_link is not None:
                source, source_geometry = source_geometry_link
                mass_difference = float(part["mass_kg"]) - float(source_geometry["mass_kg"])
                if abs(mass_difference) > 1e-7:
                    raise ValueError("Candidate comfort geometry mass differs from its exact source geometry part: " + part_id)
                source_to_candidate_geometry[source["id"]].append(part_id)
                source_geometry_links[part_id] = (source, source_geometry)
            elif derived_source_geometry_link is not None:
                source_to_derived_candidate_geometry[derived_source_geometry_link["source"]["id"]].append(part_id)
            family = part_id[len("comfort-shell/"):].split("/", 1)[0]
            if family == "seat-unit":
                system = "seating"
            elif family == "door":
                system = "doors"
            elif family in ("fixed-window", "door-window"):
                system = "glazing"
            else:
                system = "body"
            group = "retained-comfort/" + system
            retained_geometry[system].append(part)
        elif part_id.startswith("bogie/"):
            group = "passive-bogie-pair"
            new_geometry[group].append(part)
        elif part_id.startswith("wheel-underframe/"):
            group = "wheel-underframe"
            new_geometry[group].append(part)
        elif part_id.startswith("station-secondary/"):
            group = "passive-secondary"
            new_geometry[group].append(part)
        else:
            raise ValueError("Candidate geometry is not assigned to a mass account: " + part_id)
        if source_geometry_link is not None:
            source, source_geometry = source_geometry_link
            parent_geometry = parent_geometry_by_id.get(source_geometry["id"])
            if parent_geometry is None:
                raise ValueError("Linked source geometry part is absent from the pinned parent geometry: " + part_id)
            if source["system"] != group.removeprefix("retained-comfort/"):
                raise ValueError("Linked source occurrence and candidate geometry belong to different mass accounts: " + part_id)
            if abs(float(parent_geometry["mass_kg"]) - float(source_geometry["mass_kg"])) > 1e-7:
                raise ValueError("Nested source geometry mass differs from the pinned parent geometry: " + part_id)
        if part_id.startswith("comfort-shell/"):
            source_occurrence_id = part_id[len("comfort-shell/"):]
            source_occurrence = retained_by_id.get(source_occurrence_id)
            if source_occurrence is not None:
                if source_geometry_link is not None or derived_source_geometry_link is not None:
                    raise ValueError("Candidate geometry ID ambiguously matches both a source occurrence and nested source geometry: " + part_id)
                if not group.startswith("retained-comfort/") or source_occurrence["system"] != group.removeprefix("retained-comfort/"):
                    raise ValueError("Directly linked source occurrence and candidate geometry belong to different mass accounts: " + part_id)
                occurrence_mass_difference = float(part["mass_kg"]) - float(source_occurrence["mass_kg"])
                if abs(occurrence_mass_difference) > 1e-7:
                    raise ValueError("Candidate geometry mass differs from its exact source occurrence: " + part_id)
                source_to_direct_candidate_geometry[source_occurrence_id].append(part_id)
                source_occurrence_links[part_id] = source_occurrence
        geometry_parent[part_id] = group

    source_occurrences = []
    accounts = []
    for system in sorted(retained_accounts):
        source_rows = retained_accounts[system]
        account_mass = sum(float(row["mass_kg"]) for row in source_rows)
        parts = retained_geometry[system]
        geometry_mass = sum(float(part["mass_kg"]) for part in parts)
        residual = account_mass - geometry_mass
        if residual < -1e-7:
            raise ValueError("Located geometry exceeds retained system account: " + system)
        if residual < 0:
            residual = 0.0
        account_id = "retained-comfort/" + system
        accounts.append(dict(
            account_id=account_id,
            source_system=system,
            accounted_mass_kg=account_mass,
            located_geometry_mass_kg=geometry_mass,
            residual_account_mass_kg=residual,
            source_occurrence_ids=[row["id"] for row in source_rows],
            candidate_geometry_occurrence_ids=[part["id"] for part in parts],
            source_geometry_linked_occurrence_ids=sorted(
                part_id for part_id in (part["id"] for part in parts) if part_id in source_geometry_links
            ),
            source_occurrence_id_linked_geometry_occurrence_ids=sorted(
                part_id for part_id in (part["id"] for part in parts) if part_id in source_occurrence_links
            ),
            derived_source_component_group_linked_geometry_occurrence_ids=sorted(
                part_id for part_id in (part["id"] for part in parts) if part_id in derived_source_geometry_links
            ),
            mapping_method="system account with exact source-occurrence/nested-geometry links and separately declared component-group mass checks; remaining rows stay account-level",
            disposition="retained-source-account-with-candidate-geometry-subset" if parts else "retained-source-account-without-candidate-geometry",
        ))
        for source in source_rows:
            source_parts = source.get("geometry_parts") or []
            direct_geometry_ids = source_to_direct_candidate_geometry.get(source["id"], [])
            nested_geometry_ids = source_to_candidate_geometry.get(source["id"], [])
            derived_geometry_ids = source_to_derived_candidate_geometry.get(source["id"], [])
            if set(direct_geometry_ids) & set(nested_geometry_ids):
                raise ValueError("Candidate geometry occurrence cannot be counted as both direct and nested source link")
            if (set(direct_geometry_ids) | set(nested_geometry_ids)) & set(derived_geometry_ids):
                raise ValueError("Candidate geometry occurrence cannot use both exact and derived source links")
            geometry_links = [
                dict(candidate_geometry_occurrence_id=part_id,
                     mapping_method="exact-retained-source-occurrence-id-and-mass")
                for part_id in direct_geometry_ids
            ] + [
                dict(candidate_geometry_occurrence_id=part_id,
                     mapping_method="exact-nested-source-geometry-part-id-and-mass")
                for part_id in nested_geometry_ids
            ] + [
                dict(candidate_geometry_occurrence_id=part_id,
                     mapping_method="derived-source-component-group-and-exact-total-mass",
                     parent_geometry_part_id=derived_source_geometry_links[part_id]["parent_geometry_part"]["id"],
                     group_rule_id=derived_source_geometry_links[part_id]["rule_id"])
                for part_id in derived_geometry_ids
            ]
            geometry_links.sort(key=lambda row: row["candidate_geometry_occurrence_id"])
            source_occurrences.append(dict(
                account_id=account_id,
                occurrence_id=source["id"],
                occurrence_definition_id=source.get("occurrence_definition_id"),
                source_part_id=source.get("source_part_id"),
                source_system=system,
                role=source.get("role"),
                evidence_class=source.get("evidence_class"),
                source_location_known=source.get("global_installation_location_known"),
                mass_kg=float(source["mass_kg"]),
                source_geometry_part_ids=sorted(part["id"] for part in source_parts),
                derived_source_geometry_groups=[
                    group for group in derived_source_geometry_groups
                    if group["occurrence_id"] == source["id"]
                ],
                candidate_geometry_occurrence_ids=[row["candidate_geometry_occurrence_id"] for row in geometry_links],
                candidate_geometry_links=geometry_links,
            ))

    inventory = {item["id"]: item for item in candidate["inventory"]}
    bogie_account = inventory["passive-bogie-pair"]
    bogie_geometry = new_geometry["passive-bogie-pair"]
    bogie_located = sum(float(part["mass_kg"]) for part in bogie_geometry)
    bogie_residual = float(bogie_account["mass_kg"]) - bogie_located
    if bogie_residual < -1e-7 or abs(bogie_located - float(bogie_account["located_stock_kg"])) > 1e-7:
        raise ValueError("Bogie geometry does not reconcile with its explicit account")
    if abs(bogie_residual - float(bogie_account["unlocated_remainder_kg"])) > 1e-7:
        raise ValueError("Bogie residual differs from the declared unlocated remainder")
    accounts.append(dict(
        account_id="passive-bogie-pair",
        source_system="bogies",
        accounted_mass_kg=float(bogie_account["mass_kg"]),
        located_geometry_mass_kg=bogie_located,
        residual_account_mass_kg=bogie_residual,
        source_occurrence_ids=[],
        candidate_geometry_occurrence_ids=[part["id"] for part in bogie_geometry],
        mapping_method="candidate geometry parts plus retained bogie category balance",
        disposition="partial-proposed-material-with-explicit-reference-residual",
    ))

    scalar_accounts = (
        ("service-battery", "services", "supplier-cell-and-installed-pack-account",
         "Service-cell and installed-pack estimate; geometry, mounts, wiring and cooling are not located."),
        ("white-roof-finish", "roof-thermal", "counted-coating-stock",
         "Coating takeoff; no solid occurrence or installed centre of gravity is represented."),
        ("new-frame-joints-and-fin-retention", "attachments", "explicit-unlocated-allocation",
         "Unlocated allowance for body/bogie joints, fin retention and thermal joints."),
    )
    for item_id, group, evidence, basis in scalar_accounts:
        item = inventory[item_id]
        mass = float(item["mass_kg"])
        component_breakdown = (
            _service_battery_component_breakdown(item)
            if item_id == "service-battery" else None
        )
        accounts.append(dict(
            account_id=group,
            source_system=item["system"],
            accounted_mass_kg=mass,
            located_geometry_mass_kg=0.0,
            residual_account_mass_kg=mass,
            source_occurrence_ids=[item_id],
            candidate_geometry_occurrence_ids=[],
            mapping_method="declared scalar account; no candidate solid occurrence",
            disposition="retained-account-without-candidate-geometry",
        ))
        source_occurrences.append(dict(
            account_id=group,
            occurrence_id=item_id,
            occurrence_definition_id=None,
            source_part_id=None,
            source_system=item["system"],
            role=basis,
            evidence_class=evidence,
            source_location_known=False,
            mass_kg=mass,
            calculated_component_mass_breakdown=component_breakdown,
            source_geometry_part_ids=[],
            candidate_geometry_occurrence_ids=[],
            candidate_geometry_links=[],
        ))

    accounts.extend([
        dict(account_id=group, source_system=group, accounted_mass_kg=sum(float(part["mass_kg"]) for part in parts),
             located_geometry_mass_kg=sum(float(part["mass_kg"]) for part in parts), residual_account_mass_kg=0.0,
             source_occurrence_ids=[], candidate_geometry_occurrence_ids=[part["id"] for part in parts],
             mapping_method="exact candidate geometry occurrence mass", disposition="candidate-geometry-accounted-once")
        for group, parts in (("wheel-underframe", new_geometry["wheel-underframe"]),
                             ("passive-secondary", new_geometry["passive-secondary"]))
    ])

    candidate_ids = set(geometry_ids)
    mapped_ids = [part_id for account in accounts for part_id in account["candidate_geometry_occurrence_ids"]]
    if len(mapped_ids) != len(set(mapped_ids)) or set(mapped_ids) != candidate_ids:
        raise ValueError("Candidate geometry occurrences are not assigned exactly once to mass accounts")

    geometry_occurrences = []
    for part in geometry:
        group = geometry_parent[part["id"]]
        source_link = source_geometry_links.get(part["id"])
        direct_source_link = source_occurrence_links.get(part["id"])
        derived_source_link = derived_source_geometry_links.get(part["id"])
        if sum(link is not None for link in (source_link, direct_source_link, derived_source_link)) > 1:
            raise ValueError("Candidate geometry occurrence cannot be counted under multiple source-link methods")
        source = None if source_link is None else source_link[0]
        source_geometry = None if source_link is None else source_link[1]
        if direct_source_link is not None:
            source = direct_source_link
        if derived_source_link is not None:
            source = derived_source_link["source"]
        direct_linked = direct_source_link is not None
        geometry_occurrences.append(dict(
            occurrence_id=part["id"],
            account_id=group,
            geometry_kind=part.get("kind"),
            material=part.get("material"),
            system=part.get("system"),
            mass_kg=float(part["mass_kg"]),
            cg_m=part.get("cg_m"),
            source_occurrence_id=None if source is None else source["id"],
            source_occurrence_definition_id=None if source is None else source.get("occurrence_definition_id"),
            source_part_id=None if source is None else source.get("source_part_id"),
            source_location_known=None if source is None else source.get("global_installation_location_known"),
            source_occurrence_mass_kg=None if source is None else float(source["mass_kg"]),
            source_occurrence_link_method=(
                "exact-retained-source-occurrence-id-and-mass" if direct_linked else
                "nested-source-geometry-part-id-and-mass" if source_geometry is not None else
                "derived-source-component-group-and-exact-total-mass" if derived_source_link is not None else None
            ),
            candidate_to_source_occurrence_mass_difference_kg=(
                None if not direct_linked else float(part["mass_kg"]) - float(source["mass_kg"])
            ),
            source_geometry_part_id=None if source_geometry is None else source_geometry["id"],
            source_geometry_mass_kg=None if source_geometry is None else float(source_geometry["mass_kg"]),
            source_geometry_cg_m=None if source_geometry is None else source_geometry.get("cg_m"),
            candidate_to_source_geometry_mass_difference_kg=(
                None if source_geometry is None else float(part["mass_kg"]) - float(source_geometry["mass_kg"])
            ),
            derived_parent_geometry_part_id=(
                None if derived_source_link is None else derived_source_link["parent_geometry_part"]["id"]
            ),
            derived_source_geometry_group_rule_id=(
                None if derived_source_link is None else derived_source_link["rule_id"]
            ),
            derived_source_group_mass_kg=(
                None if derived_source_link is None else derived_source_link["group_mass_kg"]
            ),
            derived_source_group_mass_difference_kg=(
                None if derived_source_link is None else derived_source_link["group_mass_difference_kg"]
            ),
            mapping_method=(
                "exact-retained-source-occurrence-id-and-mass" if direct_linked else
                "exact-inherited-source-geometry-part-id-and-mass"
                if source_geometry is not None else
                "derived-source-component-group-and-exact-total-mass" if derived_source_link is not None else
                "geometry-family-to-system-account" if group.startswith("retained-comfort/")
                else "exact-candidate-component-account"
            ),
        ))
    accounted = sum(float(account["accounted_mass_kg"]) for account in accounts)
    located = sum(float(part["mass_kg"]) for part in geometry_occurrences)
    residual = sum(float(account["residual_account_mass_kg"]) for account in accounts)
    if abs(accounted - float(candidate["mass"]["accounted_tare_kg_per_car"])) > 1e-6:
        raise ValueError("Mass ledger rows do not reconcile to accounted vehicle tare")
    if abs(located - float(candidate["mass"]["located_material_kg"])) > 1e-6:
        raise ValueError("Mass ledger rows do not reconcile to located material subtotal")
    if abs(residual - float(candidate["mass"]["unlocated_or_reference_account_kg"])) > 1e-6:
        raise ValueError("Mass ledger residual does not reconcile to the reported account remainder")
    if abs(accounted - located - residual) > 1e-6:
        raise ValueError("Accounted, located and residual mass subtotals do not close")

    for account in accounts:
        if account["account_id"] in {
            "retained-comfort/HVAC", "retained-comfort/seating", "retained-comfort/doors",
            "retained-comfort/glazing", "retained-comfort/frame-joints",
        }:
            account["calculated_component_mass_breakdown"] = _retained_account_component_breakdown(
                account, source_occurrences, geometry_occurrences,
            )
        elif account["account_id"] == "passive-bogie-pair":
            account["candidate_geometry_component_breakdown"] = _bogie_geometry_component_breakdown(
                account, geometry_occurrences,
            )
        elif account["account_id"] == "retained-comfort/body":
            account["source_scope_breakdown"] = _retained_body_source_scope_breakdown(
                account, source_occurrences, geometry_occurrences,
            )

    analytical_estimates = [_roof_finish_distribution_estimate(candidate, parent)]

    account_index = {account["account_id"]: account for account in accounts}
    if len(account_index) != len(accounts):
        raise ValueError("Duplicate top-level mass account ID")
    for group in accounts:
        group["account_id"] = group["account_id"]
    accounts.sort(key=lambda account: account["account_id"])
    source_occurrences.sort(key=lambda row: (row["account_id"], row["occurrence_id"]))
    geometry_occurrences.sort(key=lambda row: row["occurrence_id"])
    return dict(
        schema="osr-v06-mass-reconciliation/2",
        candidate_id=candidate["candidate_id"],
        body_candidate_id=candidate["body_candidate_id"],
        support_component_id=candidate["support_component_id"],
        propulsion_component_id=candidate["propulsion_component_id"],
        accounts=accounts,
        source_account_occurrences=source_occurrences,
        candidate_geometry_occurrences=geometry_occurrences,
        derived_source_component_geometry_groups=derived_source_geometry_groups,
        analytical_occurrence_estimates=analytical_estimates,
        summary=dict(
            account_row_count=len(accounts),
            source_account_occurrence_count=len(source_occurrences),
            retained_source_occurrence_count=len(retained),
            located_geometry_occurrence_count=len(geometry),
            candidate_geometry_with_exact_source_geometry_link_count=len(source_geometry_links),
            source_occurrence_with_candidate_geometry_link_count=sum(
                bool(occurrence_ids) for occurrence_ids in source_to_candidate_geometry.values()
            ),
            candidate_geometry_with_exact_source_geometry_link_mass_kg=sum(
                float(part["mass_kg"]) for part in geometry if part["id"] in source_geometry_links
            ),
            candidate_geometry_without_exact_source_geometry_link_count=len(geometry) - len(source_geometry_links),
            candidate_geometry_without_exact_source_geometry_link_mass_kg=sum(
                float(part["mass_kg"]) for part in geometry if part["id"] not in source_geometry_links
            ),
            exact_source_geometry_links_mass_checked=True,
            candidate_geometry_with_exact_source_occurrence_link_count=len(source_occurrence_links),
            source_occurrence_with_candidate_geometry_occurrence_link_count=sum(
                bool(occurrence_ids) for occurrence_ids in source_to_direct_candidate_geometry.values()
            ),
            candidate_geometry_with_exact_source_occurrence_link_mass_kg=sum(
                float(part["mass_kg"]) for part in geometry if part["id"] in source_occurrence_links
            ),
            exact_source_occurrence_links_mass_checked=True,
            candidate_geometry_with_exact_source_identity_link_count=len(source_geometry_links) + len(source_occurrence_links),
            candidate_geometry_with_exact_source_identity_link_mass_kg=sum(
                float(part["mass_kg"]) for part in geometry
                if part["id"] in source_geometry_links or part["id"] in source_occurrence_links
            ),
            candidate_geometry_without_exact_source_identity_link_count=(
                len(geometry) - len(source_geometry_links) - len(source_occurrence_links)
            ),
            candidate_geometry_without_exact_source_identity_link_mass_kg=sum(
                float(part["mass_kg"]) for part in geometry
                if part["id"] not in source_geometry_links and part["id"] not in source_occurrence_links
            ),
            candidate_geometry_with_derived_source_component_group_link_count=len(derived_source_geometry_links),
            candidate_geometry_with_derived_source_component_group_link_mass_kg=math.fsum(
                float(part["mass_kg"]) for part in geometry if part["id"] in derived_source_geometry_links
            ),
            source_occurrence_with_derived_source_component_group_link_count=len(derived_source_geometry_groups),
            derived_source_component_group_mass_checks_pass=all(
                abs(float(group["mass_difference_kg"])) <= 1e-7
                for group in derived_source_geometry_groups
            ),
            accounted_tare_kg_per_car=accounted,
            located_geometry_mass_kg=located,
            residual_reference_or_unlocated_mass_kg=residual,
            located_material_CG_m=candidate["mass"]["located_material_CG_m"],
            located_material_CG_scope="Candidate geometry subtotal only; excludes account residuals and non-solid equipment.",
            complete_installed_mass_kg=None,
            complete_installed_CG_m=None,
            complete_installed_inertia_kg_m2=None,
            axle_reactions=None,
            analytical_non_additive_estimate_count=len(analytical_estimates),
            analytical_non_additive_estimated_mass_kg=sum(row["estimated_mass_kg"] for row in analytical_estimates),
            all_candidate_geometry_occurrences_assigned_once=True,
            all_account_rows_reconciled=True,
        ),
        **FLAGS,
    )


def _readme(ledger, selected):
    summary = ledger["summary"]
    closure = build_closure_worksheet(ledger)["summary"]
    derived_groups = ledger["derived_source_component_geometry_groups"]
    lines = [
        "# v0.6 vehicle mass reconciliation",
        "",
        f"Physical candidate `{ledger['candidate_id']}`; body `{ledger['body_candidate_id']}`; selection `{selected['selection_id']}`.",
        "",
        "This report preserves every retained source-account occurrence in its system account, then assigns each candidate geometry occurrence to one parent account using explicit component-family rules. It distinguishes exact retained source-occurrence links, exact nested source-geometry links, and separately declared component groups that match a complete source-account mass. These provenance links trace model origin only; they do not establish physical installation, assembly completeness, or measured mass. Newly modelled underframe, bogie, and passive-secondary geometry is assigned once. This is an accounting reconciliation, not a complete installed-mass claim.",
        "",
        "| Ledger result | Value |",
        "|---|---:|",
        f"| Accounted tare | {summary['accounted_tare_kg_per_car']:,.3f} kg/car |",
        f"| Candidate located geometry | {summary['located_geometry_mass_kg']:,.3f} kg/car |",
        f"| Reference or unlocated account residual | {summary['residual_reference_or_unlocated_mass_kg']:,.3f} kg/car |",
        f"| Account rows | {summary['account_row_count']:,} |",
        f"| Located geometry occurrences assigned once | {summary['located_geometry_occurrence_count']:,} |",
        f"| Exact retained source-occurrence ID links (geometry occurrences / source occurrences) | {summary['candidate_geometry_with_exact_source_occurrence_link_count']:,} / {summary['source_occurrence_with_candidate_geometry_occurrence_link_count']:,} |",
        f"| Mass under those exact source-occurrence ID links | {summary['candidate_geometry_with_exact_source_occurrence_link_mass_kg']:,.3f} kg/car |",
        f"| Exact inherited source-geometry links (geometry parts / source occurrences) | {summary['candidate_geometry_with_exact_source_geometry_link_count']:,} / {summary['source_occurrence_with_candidate_geometry_link_count']:,} |",
        f"| Mass under those exact source-geometry links | {summary['candidate_geometry_with_exact_source_geometry_link_mass_kg']:,.3f} kg/car |",
        f"| Combined exact source identity links (disjoint geometry occurrences / mass) | {summary['candidate_geometry_with_exact_source_identity_link_count']:,} / {summary['candidate_geometry_with_exact_source_identity_link_mass_kg']:,.3f} kg/car |",
        f"| Candidate geometry without either exact source identity link | {summary['candidate_geometry_without_exact_source_identity_link_count']:,} occurrences / {summary['candidate_geometry_without_exact_source_identity_link_mass_kg']:,.3f} kg/car |",
        f"| Calculated source-component groups (geometry occurrences / groups) | {summary['candidate_geometry_with_derived_source_component_group_link_count']:,} / {summary['source_occurrence_with_derived_source_component_group_link_count']:,} |",
        f"| Mass under calculated source-component groups | {summary['candidate_geometry_with_derived_source_component_group_link_mass_kg']:,.3f} kg/car |",
        f"| Closure worksheet rows (source / geometry / account) | {closure['record_count']:,} ({closure['source_account_occurrence_count']:,} / {closure['candidate_geometry_occurrence_count']:,} / {summary['account_row_count']:,}) |",
        f"| Separate non-additive analytical estimates | {summary['analytical_non_additive_estimate_count']:,} ({summary['analytical_non_additive_estimated_mass_kg']:,.3f} kg/car already represented in the scalar account) |",
        "| Complete installed mass, CG, inertia, axle reactions | Unknown |",
        "",
        "## Provisional roof-finish distribution estimate",
        "",
        f"The separate analytical estimate links the existing `white-roof-finish` account to {len(ledger['analytical_occurrence_estimates'][0]['source_geometry_part_ids']):,} modelled roof upper-skin surfaces. Their combined plan area is {ledger['analytical_occurrence_estimates'][0]['surface_area_m2']:.3f} m²; the declared {ledger['analytical_occurrence_estimates'][0]['coating_thickness_m'] * 1000:.3f} mm thickness and {ledger['analytical_occurrence_estimates'][0]['assumed_density_kg_m3']:.2f} kg/m³ density give {ledger['analytical_occurrence_estimates'][0]['estimated_mass_kg']:.3f} kg/car.",
        f"The estimated candidate-frame material centroid is ({', '.join(f'{value:.4f}' for value in ledger['analytical_occurrence_estimates'][0]['estimated_candidate_centroid_m'])}) m. It is derived from the roof-surface areas and the 1 m floor translation, with half the assumed coating thickness added vertically. This is not a verified installed position.",
        "The coating mass is already included in the scalar roof-thermal account. This estimate adds 0 kg to accounted tare, adds no candidate CAD occurrence, and changes neither located geometry mass nor the account residual. Uniform coverage, material density, thickness, seams, openings, and solar-panel overlap require confirmation.",
        "",
        "## Account groups",
        "",
        "| Account group | Accounted kg | Geometry kg | Residual kg | Source occurrences | Geometry occurrences |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for group in ledger["accounts"]:
        lines.append(
            f"| {group['account_id']} | {group['accounted_mass_kg']:,.3f} | {group['located_geometry_mass_kg']:,.3f} | "
            f"{group['residual_account_mass_kg']:,.3f} | {len(group['source_occurrence_ids']):,} | "
            f"{len(group['candidate_geometry_occurrence_ids']):,} |"
        )
    body_account = next(row for row in ledger["accounts"] if row["account_id"] == "retained-comfort/body")
    body_detail = body_account["source_scope_breakdown"]
    body_scope_labels = {
        "Residual allocation excluding explicitly resolved800kg interior account; not a physical equipment inventory":
            "Unlocated body reserve; not a physical inventory",
        "Panel stock plus explicitly counted edges/bonds/fasteners; not all hardware located":
            "Panel stock, edges, bonds and fasteners (partial geometry)",
        "panel-side": "Side panels",
        "material-prism-in-one-extrusion": "Extrusion/frame stock",
        "panel-end": "End panels",
        "Original aperture frames retained; opaque skins/core/bond counted": "Door infill and aperture frames",
        "corner-laps": "Corner laps",
        "corner-bonds": "Corner bonds",
    }
    lines.extend([
        "",
        "## Retained body account detail",
        "",
        "This table groups the existing body source rows by evidence class and recorded role. It shows source-account mass, geometry already represented, and the resulting accounting difference; it does not add geometry or treat the reserve as installed hardware.",
        "",
        "| Source scope | Evidence class | Source rows | Source mass (kg/car) | Candidate geometry (count / kg) | Residual (kg/car) |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for scope in body_detail["scopes"]:
        lines.append(
            f"| {body_scope_labels.get(scope['source_role'], scope['source_role'])} | {scope['evidence_class']} | "
            f"{scope['source_occurrence_count']:,} | {scope['source_account_mass_kg']:,.3f} | "
            f"{scope['candidate_geometry_occurrence_count']:,} / {scope['candidate_geometry_mass_kg']:,.3f} | "
            f"{scope['residual_mass_kg']:,.3f} |"
        )
    lines.extend([
        f"| **Account total** |  | {sum(scope['source_occurrence_count'] for scope in body_detail['scopes']):,} | "
        f"**{body_detail['source_account_mass_kg']:,.3f}** | "
        f"{sum(scope['candidate_geometry_occurrence_count'] for scope in body_detail['scopes']):,} / "
        f"**{body_detail['candidate_geometry_mass_kg']:,.3f}** | **{body_detail['residual_account_mass_kg']:,.3f}** |",
        "",
        "The source account identifies 4,778.254 kg/car as a body reserve without a physical-equipment inventory. A further 94.823 kg/car is the difference between panel/edge/bond/fastener source rows and their partially represented candidate geometry. The combined 4,873.077 kg/car remains unlocated; component identity, material, installation and centre of gravity are not established.",
        "",
    ])
    bogie_account = next(row for row in ledger["accounts"] if row["account_id"] == "passive-bogie-pair")
    bogie_detail = bogie_account["candidate_geometry_component_breakdown"]
    lines.extend([
        "",
        "## Passive-bogie geometry detail",
        "",
        f"The existing reference account is {bogie_detail['reference_account_mass_kg']:,.3f} kg for {bogie_detail['bogies_per_car']} passive bogies per car. The table decomposes only the candidate CAD solids; the per-bogie column evenly divides those totals for comparison and is not a measured assembly mass.",
        "",
        "| Modelled component family | Candidate solids | Geometry mass (kg/car) | Even split (kg/bogie) |",
        "|---|---:|---:|---:|",
    ])
    for component in bogie_detail["components"]:
        lines.append(
            f"| {component['description']} | {component['candidate_geometry_occurrence_count']:,} | "
            f"{component['candidate_geometry_mass_kg']:,.3f} | "
            f"{component['candidate_geometry_mass_kg'] / bogie_detail['bogies_per_car']:,.3f} |"
        )
    lines.extend([
        f"| **Located CAD subtotal** | {sum(row['candidate_geometry_occurrence_count'] for row in bogie_detail['components']):,} | "
        f"**{bogie_detail['candidate_geometry_mass_kg']:,.3f}** | "
        f"**{bogie_detail['candidate_geometry_mass_kg'] / bogie_detail['bogies_per_car']:,.3f}** |",
        f"| **Unallocated reference-account residual** | Not modelled | **{bogie_detail['residual_account_mass_kg']:,.3f}** | "
        f"**{bogie_detail['residual_per_bogie_kg']:,.3f}** |",
        f"| **Reference-account total** |  | **{bogie_detail['reference_account_mass_kg']:,.3f}** | "
        f"**{bogie_detail['reference_account_mass_kg'] / bogie_detail['bogies_per_car']:,.3f}** |",
        "",
        "The CAD groups include axles, wheel rims/webs/hubs, brake discs, sideframes and bolsters. The 1,764.182 kg/car residual remains an unallocated account balance; individual suspension, bearing, brake-caliper, fastening and interface masses are not defined by the source account. The candidate's passive secondary-suspension description does not add geometry or mass. This account excludes traction motors and gearing, and it does not establish complete bogie mass or physical installation.",
        "",
    ])
    battery_source = next(
        row for row in ledger["source_account_occurrences"]
        if row["occurrence_id"] == "service-battery"
    )
    battery = battery_source["calculated_component_mass_breakdown"]
    lines.extend([
        "",
        "## Service-battery account detail",
        "",
        "The candidate's existing 1,345 kg service-battery account is disaggregated from its selected electrical definition below. These rows sum within the account and do not create extra tare, CAD solids, or installed positions.",
        "",
        "| Component | Quantity | Unit mass (kg) | Account mass (kg/car) | Evidence class |",
        "|---|---:|---:|---:|---|",
    ])
    for component in battery["components"]:
        unit = component["unit"]
        if component["quantity"] != 1 and unit == "module":
            unit = "modules"
        lines.append(
            f"| {component['description']} | {component['quantity']} {unit} | "
            f"{component['unit_mass_kg']:,.3f} | {component['accounted_mass_kg']:,.3f} | "
            f"{component['evidence_class']} |"
        )
    lines.extend([
        f"| **Calculated account total** |  |  | **{battery['calculated_account_mass_kg']:,.3f}** | Difference to source account: {battery['account_difference_kg']:+.9f} kg |",
        "",
        f"The {battery['module_count']} Type3-20 modules contribute {battery['components'][0]['accounted_mass_kg']:,.3f} kg at the supplier-reference {battery['components'][0]['unit_mass_kg']:,.3f} kg/module. The {len(battery['components']) - 1} named enclosure, protection, cooling, conversion, charging, and retention allowances contribute {math.fsum(row['accounted_mass_kg'] for row in battery['components'][1:]):,.3f} kg and remain design assumptions. No module or accessory geometry, installed position, complete pack mass, or railway approval is established.",
        "",
    ])
    detail_accounts = {
        row["account_id"]: row["calculated_component_mass_breakdown"]
        for row in ledger["accounts"]
        if "calculated_component_mass_breakdown" in row
    }
    for account_id, heading, note in (
        (
            "retained-comfort/HVAC",
            "HVAC reference-package account detail",
            "The five source records are supplier-reference package hardware only. Their source roles leave mounting, ducts, complete equipment mass, geometry, location and railway qualification unresolved.",
        ),
        (
            "retained-comfort/seating",
            "Seat and interior account detail",
            "The fixture source classes and other-interior allowance reconcile the existing 800 kg account. Candidate geometry is counted once; the remaining account balance is not inferred to be a measured part or an installed seat mass.",
        ),
    ):
        detail = detail_accounts[account_id]
        lines.extend([
            f"## {heading}",
            "",
            note,
            "",
            "| Source component group | Quantity | Unit mass (kg) | Source-account mass (kg/car) | Candidate geometry (kg/car) | Residual (kg/car) | Evidence class |",
            "|---|---:|---:|---:|---:|---:|---|",
        ])
        for component in detail["components"]:
            lines.append(
                f"| {component['description']} | {component['quantity']} {component['unit']} | "
                f"{component['unit_mass_kg']:,.3f} | {component['source_account_mass_kg']:,.3f} | "
                f"{component['candidate_geometry_mass_kg']:,.3f} | {component['residual_mass_kg']:,.3f} | "
                f"{component['evidence_class']} |"
            )
        lines.extend([
            f"| **Account total** | {sum(row['quantity'] for row in detail['components'])} source occurrences |  | "
            f"**{detail['source_account_mass_kg']:,.3f}** | **{detail['candidate_geometry_mass_kg']:,.3f}** | "
            f"**{detail['residual_account_mass_kg']:,.3f}** |  |",
            "",
        ])
    lines.extend([
        "## Door, glazing and frame-joint account details",
        "",
        "These source-level groups show the existing counted or supplier-reference components and their mapped CAD mass. An entry with zero candidate geometry remains an accounting item without a demonstrated installed location.",
        "",
        "| Account | Source component | Quantity | Unit mass (kg) | Source mass (kg/car) | Candidate geometry (count / kg) | Residual (kg/car) | Evidence class |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ])
    detailed_account_ids = (
        "retained-comfort/doors", "retained-comfort/glazing", "retained-comfort/frame-joints",
    )
    for account_id in detailed_account_ids:
        account = next(row for row in ledger["accounts"] if row["account_id"] == account_id)
        detail = account["calculated_component_mass_breakdown"]
        for component in detail["components"]:
            lines.append(
                f"| {account_id} | {component['description']} | {component['quantity']:,} | "
                f"{component['unit_mass_kg']:,.3f} | {component['source_account_mass_kg']:,.3f} | "
                f"{component['candidate_geometry_occurrence_count']:,} / {component['candidate_geometry_mass_kg']:,.3f} | "
                f"{component['residual_mass_kg']:,.3f} | {component['evidence_class']} |"
            )
        lines.append(
            f"| **{account_id} total** |  | {sum(row['quantity'] for row in detail['components']):,} source occurrences |  | "
            f"**{detail['source_account_mass_kg']:,.3f}** |  | **{detail['residual_account_mass_kg']:,.3f}** |  |"
        )
    lines.extend([
        "",
        "Door operator figures are 1300 mm product references; the selected 1400 mm openings and deeper leaves are not established compatible installations. The frame-joint component masses are counted stock estimates with no placed candidate geometry. These breakdowns add no mass and do not close installation or qualification.",
        "",
    ])
    lines.extend([
        "The located-material centre of gravity is calculated from the represented geometry subset only. It excludes all residual accounts, including the service pack, HVAC, unlocated bogie balance, roof coating takeoff, attachment allowance, and source-account mass without candidate geometry. It is not the installed vehicle CG. Average axle masses are not axle reactions; longitudinal balance and dynamic wheel loads remain unresolved.",
        "",
        f"Exact retained source-occurrence IDs link {summary['candidate_geometry_with_exact_source_occurrence_link_count']:,} candidate geometry occurrences ({summary['candidate_geometry_with_exact_source_occurrence_link_mass_kg']:,.3f} kg/car) to {summary['source_occurrence_with_candidate_geometry_occurrence_link_count']:,} source occurrences, with each linked mass checked equal. Separately, exact nested source-geometry IDs link {summary['candidate_geometry_with_exact_source_geometry_link_count']:,} occurrences ({summary['candidate_geometry_with_exact_source_geometry_link_mass_kg']:,.3f} kg/car); those nested links are also mass-checked and have distinct candidate geometry IDs. Together, exact links identify {summary['candidate_geometry_with_exact_source_identity_link_count']:,} of {summary['located_geometry_occurrence_count']:,} candidate geometry occurrences and {summary['candidate_geometry_with_exact_source_identity_link_mass_kg']:,.3f} kg/car. An additional {summary['candidate_geometry_with_derived_source_component_group_link_count']:,} occurrences ({summary['candidate_geometry_with_derived_source_component_group_link_mass_kg']:,.3f} kg/car) map to {summary['source_occurrence_with_derived_source_component_group_link_count']:,} source accounts through declared glazing, PVB, and deleted-door-infill groups whose aggregate masses match the source accounts exactly. These are calculated group links, not exact per-part source IDs. The remaining {summary['candidate_geometry_without_exact_source_identity_link_count']:,} occurrences ({summary['candidate_geometry_without_exact_source_identity_link_mass_kg']:,.3f} kg/car) lack an exact source-occurrence or nested-subgeometry link. None of these mappings proves manufacture or physical installation.",
        "The [mass closure worksheet](mass-closure-worksheet.json.gz) has one row for every retained source-account occurrence, candidate geometry occurrence, and account closure. It keeps source-accounted mass, CAD-derived mass, and account residuals in separate fields. Every row's physically installed mass and installed position remain null; a candidate geometry centroid is not an installed position, and a positive accounting residual is not a physical part.",
        "",
        "## Calculated source-component groups",
        "",
        "| Group rule | Source account mass | Candidate parts | Calculated group mass | Difference |",
        "|---|---:|---:|---:|---:|",
    ])
    for group in derived_groups:
        lines.append(
            f"| `{group['rule_id']}` | {group['source_account_mass_kg']:,.6f} kg | {len(group['candidate_geometry_occurrence_ids']):,} | "
            f"{group['candidate_geometry_mass_kg']:,.6f} kg | {group['mass_difference_kg']:+.9f} kg |"
        )
    lines.extend([
        "",
        "These groups improve source-to-geometry traceability only. Their material was already included in located geometry, so they add no mass and reduce no account residual. The associated occurrence IDs identify component-account groupings, not exact per-part identities.",
        "",
        "Source occurrences keep their source IDs and occurrence-definition IDs in [mass-ledger.json.gz](mass-ledger.json.gz). The report is bound by [manifest.json](manifest.json). Regenerate with `python3 -m engineering.mass_ledger_audit build` and verify with `python3 -m engineering.mass_ledger_audit verify`.",
        "",
        "No physical acceptance, manufacturing release, or operating release is asserted.",
        "",
    ])
    return "\n".join(lines).encode()


def _inputs(root):
    root = Path(root)
    candidate = vehicle.build(root)
    parent, parent_sha = vehicle._read_parent(root)
    selected = evaluation.build(root)
    baseline = tomllib.loads((root / "engineering/development-baseline.toml").read_text())
    expected = {
        "vehicle_candidate_id": candidate["candidate_id"],
        "body_candidate_id": candidate["body_candidate_id"],
        "support_component_id": candidate["support_component_id"],
        "propulsion_component_id": candidate["propulsion_component_id"],
    }
    if any(baseline.get(key) != value for key, value in expected.items()):
        raise ValueError("Vehicle mass ledger does not match the selected development candidate")
    selected_expected = dict(
        candidate_id=candidate["candidate_id"],
        body_candidate_id=candidate["body_candidate_id"],
        support_component_id=candidate["support_component_id"],
        propulsion_component_id=candidate["propulsion_component_id"],
    )
    if any(selected.get(key) != value for key, value in selected_expected.items()):
        raise ValueError("Selected evaluation and vehicle mass ledger identities differ")
    ledger = reconcile(candidate, parent)
    ledger["vehicle_evaluation_id"] = candidate.get("evaluation_id")
    ledger["selected_evaluation_id"] = selected["evaluation_id"]
    ledger["selection_id"] = selected["selection_id"]
    for estimate in ledger["analytical_occurrence_estimates"]:
        estimate["evaluation_id"] = selected["evaluation_id"]
        estimate["selection_id"] = selected["selection_id"]
        estimate["candidate_id"] = ledger["candidate_id"]
        estimate["body_candidate_id"] = ledger["body_candidate_id"]
        estimate["support_component_id"] = ledger["support_component_id"]
        estimate["propulsion_component_id"] = ledger["propulsion_component_id"]
        estimate["estimate_id"] = identity({key: value for key, value in estimate.items() if key != "estimate_id"})
    ledger["summary"]["vehicle_evaluation_id"] = candidate.get("evaluation_id")
    ledger["summary"]["selected_evaluation_id"] = selected["evaluation_id"]
    ledger["summary"]["selection_id"] = selected["selection_id"]
    sources = {}
    for source_map in (candidate["source_sha256"], selected["source_sha256"]):
        for name, expected_sha in source_map.items():
            if name in sources and sources[name] != expected_sha:
                raise ValueError("Candidate and selected evaluation source receipts differ: " + name)
            sources[name] = expected_sha
    sources.update({
        "engineering/mass_ledger_audit.py": _digest(Path(__file__)),
        "engineering/development-baseline.toml": _digest(root / "engineering/development-baseline.toml"),
        "engineering/station_rail/evaluation.py": _digest(root / "engineering/station_rail/evaluation.py"),
        "engineering/station_rail/vehicle.py": _digest(root / "engineering/station_rail/vehicle.py"),
        "docs/design-engine/ferrite-maglev/comfort-design/manifest.json": _digest(root / vehicle.PARENT_MANIFEST),
    })
    sources[vehicle.PARENT] = parent_sha
    return ledger, selected, sources


def _payloads(root):
    ledger, selected, sources = _inputs(root)
    worksheet = build_closure_worksheet(ledger)
    ledger_raw = _deterministic_gzip(encoded(ledger))
    summary = dict(schema="osr-v06-mass-reconciliation-summary/1", **ledger["summary"],
                   candidate_id=ledger["candidate_id"], body_candidate_id=ledger["body_candidate_id"],
                   closure_worksheet_id=worksheet["worksheet_id"],
                   closure_worksheet_record_count=worksheet["summary"]["record_count"],
                   closure_worksheet_source_account_occurrence_count=worksheet["summary"]["source_account_occurrence_count"],
                   closure_worksheet_geometry_occurrence_count=worksheet["summary"]["candidate_geometry_occurrence_count"],
                   closure_worksheet_exact_source_geometry_link_count=worksheet["summary"]["exact_source_geometry_link_count"],
                   closure_worksheet_exact_source_geometry_link_mass_kg=worksheet["summary"]["exact_source_geometry_link_mass_kg"],
                   closure_worksheet_exact_source_occurrence_link_count=worksheet["summary"]["exact_source_occurrence_link_count"],
                   closure_worksheet_exact_source_occurrence_link_mass_kg=worksheet["summary"]["exact_source_occurrence_link_mass_kg"],
                   closure_worksheet_exact_source_identity_link_count=worksheet["summary"]["exact_source_identity_link_count"],
                   closure_worksheet_exact_source_identity_link_mass_kg=worksheet["summary"]["exact_source_identity_link_mass_kg"],
                   closure_worksheet_account_residual_count=worksheet["summary"]["account_residual_count"],
                   **FLAGS)
    return {
        "mass-ledger.json.gz": ledger_raw,
        "mass-closure-worksheet.json.gz": _deterministic_gzip(encoded(worksheet)),
        "summary.json": encoded(summary),
        "README.md": _readme(ledger, selected),
    }, sources, ledger, selected


def build_closure_worksheet(ledger):
    """Separate source-account, candidate-geometry, and unresolved installation rows."""
    candidate_id = ledger["candidate_id"]
    evaluation_id = ledger["selected_evaluation_id"]
    selection_id = ledger["selection_id"]
    rows = []
    for source in ledger["source_account_occurrences"]:
        linked_geometry_ids = list(source.get("candidate_geometry_occurrence_ids", []))
        rows.append(_row(
            record_kind="source-account-occurrence",
            candidate_id=candidate_id,
            evaluation_id=evaluation_id,
            selection_id=selection_id,
            account_id=source["account_id"],
            occurrence_id=source["occurrence_id"],
            occurrence_definition_id=source.get("occurrence_definition_id"),
            source_part_id=source.get("source_part_id"),
            source_geometry_part_ids=list(source.get("source_geometry_part_ids", [])),
            candidate_geometry_occurrence_ids=linked_geometry_ids,
            candidate_geometry_links=list(source.get("candidate_geometry_links", [])),
            mass_evidence_class=source.get("evidence_class"),
            accounted_source_mass_kg=source["mass_kg"],
            candidate_geometry_mass_kg=None,
            candidate_geometry_centroid_m=None,
            physically_installed_mass_kg=None,
            installed_position_m=None,
            lower_mass_bound_kg=None,
            upper_mass_bound_kg=None,
            installation_status="not-physically-verified",
            source_location_known=source.get("source_location_known"),
            overlap_or_replacement_status=(
                "source-occurrence-or-geometry-origin-linked; physical installation and assembly completeness unverified"
                if linked_geometry_ids else "unresolved"
            ),
            calculated_component_mass_breakdown=source.get("calculated_component_mass_breakdown"),
            derived_source_geometry_groups=list(source.get("derived_source_geometry_groups", [])),
            accounting_mapping=(
                "retained source occurrence owns exact ID-linked parts and/or the listed calculated component groups; group totals match this source account, while physical installation remains unverified"
                if linked_geometry_ids else
                "source occurrence retained in its parent system account; no candidate geometry-origin link is available"
            ),
            evidence_needed=[
                "supplier or measurement evidence for installed mass",
                "reviewed installation location in the candidate vehicle coordinate frame",
                "identity-level overlap, replacement, and shared-membership review",
            ],
        ))
    for geometry in ledger["candidate_geometry_occurrences"]:
        source_geometry_linked = geometry.get("source_occurrence_id") is not None
        rows.append(_row(
            record_kind="candidate-geometry-occurrence",
            candidate_id=candidate_id,
            evaluation_id=evaluation_id,
            selection_id=selection_id,
            account_id=geometry["account_id"],
            occurrence_id=geometry["occurrence_id"],
            occurrence_definition_id=geometry.get("source_occurrence_definition_id"),
            source_part_id=geometry.get("source_part_id"),
            source_occurrence_id=geometry.get("source_occurrence_id"),
            source_occurrence_mass_kg=geometry.get("source_occurrence_mass_kg"),
            source_occurrence_link_method=geometry.get("source_occurrence_link_method"),
            candidate_to_source_occurrence_mass_difference_kg=geometry.get("candidate_to_source_occurrence_mass_difference_kg"),
            source_geometry_part_id=geometry.get("source_geometry_part_id"),
            source_geometry_mass_kg=geometry.get("source_geometry_mass_kg"),
            source_geometry_centroid_m=geometry.get("source_geometry_cg_m"),
            candidate_to_source_geometry_mass_difference_kg=geometry.get("candidate_to_source_geometry_mass_difference_kg"),
            derived_parent_geometry_part_id=geometry.get("derived_parent_geometry_part_id"),
            derived_source_geometry_group_rule_id=geometry.get("derived_source_geometry_group_rule_id"),
            derived_source_group_mass_kg=geometry.get("derived_source_group_mass_kg"),
            derived_source_group_mass_difference_kg=geometry.get("derived_source_group_mass_difference_kg"),
            mass_evidence_class="candidate-geometry-derived",
            accounted_source_mass_kg=None,
            candidate_geometry_mass_kg=geometry["mass_kg"],
            candidate_geometry_centroid_m=geometry.get("cg_m"),
            physically_installed_mass_kg=None,
            installed_position_m=None,
            lower_mass_bound_kg=None,
            upper_mass_bound_kg=None,
            installation_status="not-physically-verified",
            source_location_known=geometry.get("source_location_known"),
            overlap_or_replacement_status=(
                "source-occurrence-or-geometry-origin-linked; physical installation and assembly completeness unverified"
                if source_geometry_linked else "unresolved"
            ),
            accounting_mapping=geometry["mapping_method"],
            evidence_needed=[
                "manufactured-part weigh record or supplier-documented mass",
                "confirmation that the candidate geometry is installed as modelled",
                "reviewed installation location, overlap, and replacement mapping",
            ],
        ))
    for account in ledger["accounts"]:
        residual = float(account["residual_account_mass_kg"])
        source_identity_linked_ids = [
            row["occurrence_id"] for row in ledger["candidate_geometry_occurrences"]
            if row["occurrence_id"] in account["candidate_geometry_occurrence_ids"]
            and row.get("source_occurrence_link_method") in (
                "exact-retained-source-occurrence-id-and-mass",
                "nested-source-geometry-part-id-and-mass",
            )
        ]
        source_occurrence_linked_ids = [
            row["occurrence_id"] for row in ledger["candidate_geometry_occurrences"]
            if row["occurrence_id"] in account["candidate_geometry_occurrence_ids"]
            and row.get("source_occurrence_link_method") == "exact-retained-source-occurrence-id-and-mass"
        ]
        source_geometry_linked_ids = [
            row["occurrence_id"] for row in ledger["candidate_geometry_occurrences"]
            if row["occurrence_id"] in account["candidate_geometry_occurrence_ids"]
            and row.get("source_geometry_part_id") is not None
        ]
        derived_source_group_linked_ids = [
            row["occurrence_id"] for row in ledger["candidate_geometry_occurrences"]
            if row["occurrence_id"] in account["candidate_geometry_occurrence_ids"]
            and row.get("source_occurrence_link_method") == "derived-source-component-group-and-exact-total-mass"
        ]
        rows.append(_row(
            record_kind="account-closure",
            candidate_id=candidate_id,
            evaluation_id=evaluation_id,
            selection_id=selection_id,
            account_id=account["account_id"],
            occurrence_id=None,
            occurrence_definition_id=None,
            source_part_id=None,
            mass_evidence_class=("accounting-residual-not-physical-component"
                                 if residual > 1e-9 else "accounting-subtotal-reconciled-to-candidate-geometry"),
            accounted_source_mass_kg=account["accounted_mass_kg"],
            candidate_geometry_mass_kg=account["located_geometry_mass_kg"],
            candidate_geometry_centroid_m=None,
            accounting_residual_kg=residual,
            physically_installed_mass_kg=None,
            installed_position_m=None,
            lower_mass_bound_kg=None,
            upper_mass_bound_kg=None,
            installation_status="not-physically-verified",
            source_location_known=False,
            overlap_or_replacement_status=(
                "partial-source-origin-links; residual remains an accounting amount, not a physical component"
                if source_identity_linked_ids or derived_source_group_linked_ids else "unresolved"
            ),
            source_occurrence_ids=list(account["source_occurrence_ids"]),
            candidate_geometry_occurrence_ids=list(account["candidate_geometry_occurrence_ids"]),
            exact_source_geometry_linked_occurrence_ids=source_geometry_linked_ids,
            exact_source_occurrence_linked_occurrence_ids=source_occurrence_linked_ids,
            exact_source_identity_linked_occurrence_ids=source_identity_linked_ids,
            derived_source_component_group_linked_occurrence_ids=derived_source_group_linked_ids,
            accounting_mapping=account["mapping_method"],
            evidence_needed=[
                "disaggregate the account into exact physical component identities",
                "supplier or measurement evidence for installed mass",
                "reviewed installation location in the candidate vehicle coordinate frame",
                "identity-level overlap, replacement, and shared-membership review",
            ],
        ))
    record_ids = [row["row_id"] for row in rows]
    if len(record_ids) != len(set(record_ids)):
        raise ValueError("Mass closure worksheet record identities must be unique")
    if (len(rows) != (len(ledger["source_account_occurrences"])
                      + len(ledger["candidate_geometry_occurrences"])
                      + len(ledger["accounts"]))
            or any(row["physically_installed_mass_kg"] is not None for row in rows)):
        raise ValueError("Mass closure worksheet lost an account/occurrence or inferred installed mass")
    body = dict(
        schema="osr-v06-mass-closure-worksheet/2",
        candidate_id=candidate_id,
        body_candidate_id=ledger["body_candidate_id"],
        support_component_id=ledger["support_component_id"],
        propulsion_component_id=ledger["propulsion_component_id"],
        evaluation_id=evaluation_id,
        vehicle_evaluation_id=ledger["vehicle_evaluation_id"],
        selection_id=selection_id,
        ledger_payload_id=identity(ledger),
        rows=rows,
        summary=dict(
            record_count=len(rows),
            source_account_occurrence_count=len(ledger["source_account_occurrences"]),
            candidate_geometry_occurrence_count=len(ledger["candidate_geometry_occurrences"]),
            exact_source_geometry_link_count=ledger["summary"]["candidate_geometry_with_exact_source_geometry_link_count"],
            exact_source_geometry_link_mass_kg=ledger["summary"]["candidate_geometry_with_exact_source_geometry_link_mass_kg"],
            exact_source_occurrence_link_count=ledger["summary"]["candidate_geometry_with_exact_source_occurrence_link_count"],
            exact_source_occurrence_link_mass_kg=ledger["summary"]["candidate_geometry_with_exact_source_occurrence_link_mass_kg"],
            exact_source_identity_link_count=ledger["summary"]["candidate_geometry_with_exact_source_identity_link_count"],
            exact_source_identity_link_mass_kg=ledger["summary"]["candidate_geometry_with_exact_source_identity_link_mass_kg"],
            candidate_geometry_without_exact_source_identity_link_count=ledger["summary"]["candidate_geometry_without_exact_source_identity_link_count"],
            candidate_geometry_without_exact_source_identity_link_mass_kg=ledger["summary"]["candidate_geometry_without_exact_source_identity_link_mass_kg"],
            source_occurrence_with_candidate_geometry_link_count=ledger["summary"]["source_occurrence_with_candidate_geometry_link_count"],
            derived_source_component_group_link_count=ledger["summary"]["candidate_geometry_with_derived_source_component_group_link_count"],
            derived_source_component_group_link_mass_kg=ledger["summary"]["candidate_geometry_with_derived_source_component_group_link_mass_kg"],
            source_occurrence_with_derived_source_component_group_link_count=ledger["summary"]["source_occurrence_with_derived_source_component_group_link_count"],
            candidate_geometry_without_exact_source_geometry_link_count=ledger["summary"]["candidate_geometry_without_exact_source_geometry_link_count"],
            candidate_geometry_without_exact_source_geometry_link_mass_kg=ledger["summary"]["candidate_geometry_without_exact_source_geometry_link_mass_kg"],
            account_residual_count=sum(float(row["accounting_residual_kg"]) > 1e-9 for row in rows
                                       if row["record_kind"] == "account-closure"),
            analytical_non_additive_estimate_count=len(ledger["analytical_occurrence_estimates"]),
            analytical_non_additive_estimated_mass_kg=ledger["summary"]["analytical_non_additive_estimated_mass_kg"],
            accounted_tare_kg_per_car=ledger["summary"]["accounted_tare_kg_per_car"],
            located_geometry_mass_kg=ledger["summary"]["located_geometry_mass_kg"],
            accounting_residual_kg=ledger["summary"]["residual_reference_or_unlocated_mass_kg"],
            physically_installed_mass_kg=None,
            complete_installed_mass_kg=None,
            complete_installed_CG_m=None,
            complete_installed_inertia_kg_m2=None,
            axle_reactions=None,
        ),
        unknown_is_zero=False,
        physical_acceptance=None,
        **FLAGS,
    )
    body["worksheet_id"] = identity(body)
    return body


def publish(root=ROOT, output=None):
    root = Path(root).resolve()
    output = root / OUTPUT if output is None else Path(output)
    payloads, sources, ledger, selected = _payloads(root)
    output.mkdir(parents=True, exist_ok=True)
    for name, raw in payloads.items():
        path = output / name
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_bytes(raw)
        os.replace(tmp, path)
    manifest = dict(
        schema="osr-v06-mass-reconciliation-publication/1",
        candidate_id=ledger["candidate_id"],
        evaluation_id=selected["evaluation_id"],
        vehicle_evaluation_id=ledger["vehicle_evaluation_id"],
        selection_id=selected["selection_id"],
        source_sha256=sources,
        files_sha256={name: sha256(raw).hexdigest() for name, raw in payloads.items()},
        **FLAGS,
    )
    manifest["manifest_id"] = identity(manifest)
    raw = encoded(manifest)
    tmp = output / "manifest.json.tmp"
    tmp.write_bytes(raw)
    os.replace(tmp, output / "manifest.json")
    return dict(published=True, path=str(output), manifest_id=manifest["manifest_id"],
                account_row_count=ledger["summary"]["account_row_count"],
                closure_worksheet_id=build_closure_worksheet(ledger)["worksheet_id"],
                closure_worksheet_record_count=len(ledger["source_account_occurrences"])
                    + len(ledger["candidate_geometry_occurrences"]) + len(ledger["accounts"]),
                analytical_non_additive_estimate_count=ledger["summary"]["analytical_non_additive_estimate_count"],
                analytical_non_additive_estimated_mass_kg=ledger["summary"]["analytical_non_additive_estimated_mass_kg"],
                accounted_tare_kg_per_car=ledger["summary"]["accounted_tare_kg_per_car"],
                located_geometry_mass_kg=ledger["summary"]["located_geometry_mass_kg"],
                residual_reference_or_unlocated_mass_kg=ledger["summary"]["residual_reference_or_unlocated_mass_kg"],
                complete_installed_mass_kg=None, **FLAGS)


def verify(root=ROOT, output=None):
    root = Path(root).resolve()
    output = root / OUTPUT if output is None else Path(output)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    if manifest.get("manifest_id") != identity({key: value for key, value in manifest.items() if key != "manifest_id"}):
        raise ValueError("Mass reconciliation manifest identity differs")
    for name, expected in manifest["source_sha256"].items():
        if _digest(root / name) != expected:
            raise ValueError("Mass reconciliation source differs: " + name)
    payloads, sources, ledger, selected = _payloads(root)
    if manifest["source_sha256"] != sources:
        raise ValueError("Mass reconciliation source set differs")
    if (manifest["candidate_id"] != ledger["candidate_id"]
            or manifest["evaluation_id"] != selected["evaluation_id"]
            or manifest["vehicle_evaluation_id"] != ledger["vehicle_evaluation_id"]
            or manifest["selection_id"] != selected["selection_id"]):
        raise ValueError("Mass reconciliation candidate or evaluation identity differs")
    actual_files = {path.name: _digest(path) for path in output.iterdir() if path.is_file() and path.name != "manifest.json"}
    expected_files = {name: sha256(raw).hexdigest() for name, raw in payloads.items()}
    if manifest["files_sha256"] != expected_files or actual_files != expected_files:
        raise ValueError("Mass reconciliation payload differs")
    for name, raw in payloads.items():
        if (output / name).read_bytes() != raw:
            raise ValueError("Mass reconciliation generated output differs: " + name)
    if any(manifest.get(key) is not value for key, value in FLAGS.items()):
        raise ValueError("Mass reconciliation cannot grant release")
    return dict(verified=True, replayed=True, manifest_id=manifest["manifest_id"],
                candidate_id=ledger["candidate_id"], evaluation_id=selected["evaluation_id"],
                selection_id=selected["selection_id"], account_row_count=ledger["summary"]["account_row_count"],
                closure_worksheet_id=build_closure_worksheet(ledger)["worksheet_id"],
                closure_worksheet_record_count=len(ledger["source_account_occurrences"])
                    + len(ledger["candidate_geometry_occurrences"]) + len(ledger["accounts"]),
                analytical_non_additive_estimate_count=ledger["summary"]["analytical_non_additive_estimate_count"],
                analytical_non_additive_estimated_mass_kg=ledger["summary"]["analytical_non_additive_estimated_mass_kg"],
                accounted_tare_kg_per_car=ledger["summary"]["accounted_tare_kg_per_car"],
                located_geometry_mass_kg=ledger["summary"]["located_geometry_mass_kg"],
                residual_reference_or_unlocated_mass_kg=ledger["summary"]["residual_reference_or_unlocated_mass_kg"],
                complete_installed_mass_kg=None, **FLAGS)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m engineering.mass_ledger_audit")
    parser.add_argument("action", choices=("build", "verify"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = publish(args.root, args.output) if args.action == "build" else verify(args.root, args.output)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Actual panel inventory, manufacturing takeoff and connection demand.

Unrepresented seals, retention, thread locking and frame interfaces remain open.
Bilateral bolt/potting springs provide demands, never accepted joint capacity.
"""

from copy import deepcopy
import csv
import json
import math
from pathlib import Path

from .bom import candidate_bill
from .contracts import fingerprint
from .manufacturing_rules import part_bounds


def packet(candidate):
    from engineering.design_consistency.contracts import validate

    model = candidate.get("definition", {}).get("contract")
    if not model or model.get("panel_parameters", {}).get("crown_m") != 0:
        raise ValueError("flat physical panel assembly required")
    validate(model)
    bill = candidate_bill(candidate, adapter="panel")
    parts = {p["id"]: p for p in model["parts"]}
    network = model["support_network"]
    sites = network["panel_attachment_sites_m"]
    machining, takeoff, connections = [], [], []
    for part in model["parts"]:
        takeoff.append(
            dict(
                physical_id=part["id"],
                revision=part["revision"],
                quantity=1,
                material=part["material"],
                mass_kg=part["properties"]["mass_kg"],
                geometry_sha256=part["analysis"]["geometry_sha256"],
                assembly_bounds_m=part_bounds(part),
                primitives=deepcopy(part["manufacturing"]["primitives"]),
                inspection_characteristics=part["inspection_characteristics"],
                process_released=False,
                machining_allowance_m=None,
            )
        )
        for primitive in part["manufacturing"]["primitives"]:
            for index, centre in enumerate(primitive.get("holes_xy_m", [])):
                machining.append(
                    dict(
                        physical_id=part["id"],
                        primitive=primitive["id"],
                        hole_index=index,
                        local_xy_m=centre,
                        diameter_m=2 * primitive["hole_radius_m"],
                        depth_m=primitive["dimensions_m"][2],
                        tolerance_m=None,
                        thread_or_clearance="represented clearance; thread law and fit unqualified",
                    )
                )
    for rail in network["rails"]:
        start, end = rail["interval_m"]
        for slot, fraction in enumerate((0.2, 0.8)):
            x, y = start + (end - start) * fraction, rail["station_m"]
            matches = [
                i
                for i, point in enumerate(sites)
                if abs(point[0] - x) < 1e-10 and abs(point[1] - y) < 1e-10
            ]
            if len(matches) != 1:
                raise ValueError(
                    "clip must map to exactly one actual potted-insert site"
                )
            index = matches[0]
            ids = [
                rail["id"],
                f'{rail["id"]}-clip-{slot}',
                f'{rail["id"]}-clip-bolt-{slot}',
                f"potting-{index}",
                f"insert-{index}",
            ]
            if not set(ids) <= parts.keys():
                raise ValueError("connection includes an absent physical component")
            connections.append(
                dict(
                    id=ids[1],
                    physical_part_ids=ids,
                    site_m=[x, y],
                    constitutive_model="series axial bolt/potting compliance; bilateral point spring",
                    resistance_n=None,
                    preload_n=None,
                    locking_verified=False,
                    contact_pullout_bearing_bond_fatigue="unknown",
                    cases=[],
                )
            )
    by_id = {c["id"]: c for c in connections}
    confirmation = candidate["definition"].get("confirmation", {})
    for case in ("refined", "holdout", "combined", "soft_joint"):
        response = confirmation.get(case, {})
        if not response.get("attachments"):
            continue
        if response.get("contract_sha256") != fingerprint(model):
            raise ValueError(
                "connection response belongs to another physical definition"
            )
        if len(response["attachments"]) != len(by_id) or {
            a["id"] for a in response["attachments"]
        } != set(by_id):
            raise ValueError("response omitted or invented an installed clip")
        for attachment in response["attachments"]:
            if (
                type(attachment.get("active")) is not bool
                or not math.isfinite(attachment["force_n"])
                or not math.isfinite(attachment["stiffness_n_m"])
                or attachment["stiffness_n_m"] <= 0
                or (not attachment["active"] and attachment["force_n"] != 0)
            ):
                raise ValueError("complete finite connection demand required")
            by_id[attachment["id"]]["cases"].append(
                dict(
                    case=case,
                    active=attachment["active"],
                    axial_demand_n=attachment["force_n"],
                    stiffness_n_m=attachment["stiffness_n_m"],
                    relative_displacement_m=(
                        attachment["force_n"] / attachment["stiffness_n_m"]
                        if attachment["active"]
                        else None
                    ),
                    pressure_pa=response["pressure_pa"],
                    capacity_check="unknown",
                )
            )
    for connection in connections:
        connection["maximum_recorded_axial_demand_n"] = max(
            (abs(c["axial_demand_n"]) for c in connection["cases"]), default=None
        )
    losses = confirmation.get("all_clip_losses", {})
    if losses and losses.get("contract_sha256") != fingerprint(model):
        raise ValueError("clip-loss envelope belongs to another physical definition")
    return dict(
        schema="osr-panel-assembly-review/1",
        candidate=candidate["id"],
        identity=deepcopy(candidate["identity"]),
        physical_definition_sha256=fingerprint(model),
        represented_part_count=len(parts),
        represented_mass_kg=bill["defined_mass_kg"],
        complete_installed_mass_kg=None,
        complete_installed_kit=False,
        inventory_scope="compiled panel material regions, rails, inserts and represented hardware only",
        bill=bill,
        manufacturing_takeoff=takeoff,
        machining=machining,
        connections=connections,
        single_clip_loss_envelope=deepcopy(losses),
        materials=deepcopy(model["materials"]),
        unresolved_allocations=deepcopy(model.get("unresolved_part_allocations", [])),
        mandatory_checks=deepcopy(candidate["checks"]),
        drawing_status="unissued; native correspondence does not qualify manufacture",
        physical_release=False,
        independently_accepted=False,
        production_released=False,
    )


def write_packet(candidate, output):
    """Write cut/drill/BOM/connection review files without a hidden solver."""
    report = packet(candidate)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / "assembly-review.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    tables = [
        (
            "manufacturing-takeoff.csv",
            [
                "physical_id",
                "revision",
                "quantity",
                "material",
                "mass_kg",
                "geometry_sha256",
                "assembly_bounds_m",
                "machining_allowance_m",
                "process_released",
            ],
            report["manufacturing_takeoff"],
        ),
        (
            "drill-schedule.csv",
            [
                "physical_id",
                "primitive",
                "hole_index",
                "local_xy_m",
                "diameter_m",
                "depth_m",
                "tolerance_m",
                "thread_or_clearance",
            ],
            report["machining"],
        ),
        (
            "connection-demands.csv",
            [
                "id",
                "physical_part_ids",
                "site_m",
                "maximum_recorded_axial_demand_n",
                "resistance_n",
                "preload_n",
                "locking_verified",
                "contact_pullout_bearing_bond_fatigue",
            ],
            report["connections"],
        ),
    ]
    for name, fields, rows in tables:
        with (output / name).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        key: (
                            json.dumps(value)
                            if isinstance(value, (list, dict))
                            else value
                        )
                        for key, value in row.items()
                        if key in fields
                    }
                )
    return report

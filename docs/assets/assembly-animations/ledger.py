"""Bind assembly geometry, quantities, budget allowances and work to the films."""

import argparse
from collections import defaultdict
import csv
from dataclasses import dataclass
import gzip
from hashlib import sha256
import importlib
from io import StringIO
import json
import math
from pathlib import Path
import re

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
WAGES = "docs/operator-review/delivery/workplan/plan.json"
FILMS = ("train", "viaduct")
SCOPES = {
    "train": "One six-car Baghdad Airport prototype study formation",
    "viaduct": "One repeatable 20 m double-track bay and a separate two-front plant and yard inventory",
}


@dataclass(frozen=True)
class Part:
    key: str
    assembly: str
    name: str
    meshes: tuple
    quantity: int
    material: str
    mass_kg: tuple | None
    price_usd: tuple | None
    process: str
    crew: str
    hours: float
    account: str
    basis: str
    density_kg_m3: float | None = None
    kind: str = "installed"
    predecessors: tuple = ()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(data):
    return sha256(data).hexdigest()


def solid_volume(mesh):
    """Obtain volume from a closed, consistently oriented mesh in metres."""
    edges = defaultdict(list)
    reference = mesh.vertices.mean(axis=0)
    volume = 0.0
    for face in mesh.faces:
        for a, b in zip(face, (*face[1:], face[0]), strict=True):
            edges[min(a, b), max(a, b)].append(a < b)
        points = mesh.vertices[list(face)] - reference
        volume += np.sum(np.cross(points[1:-1], points[2:]) @ points[0]) / 6
    if not edges or any(sorted(v) != [False, True] for v in edges.values()) or abs(volume) < 1e-12:
        raise ValueError(f"Mass from {mesh.name} requires a closed, oriented nonzero solid")
    return abs(volume)


def range_values(values, key):
    if values is None:
        return None
    if len(values) != 3 or any(not math.isfinite(v) or v < 0 for v in values) or list(values) != sorted(values):
        raise ValueError(f"Invalid low/base/high estimate for {key}")
    return list(values)


def inventory_document(module, name):
    parts = module.inventory()
    if not parts or len({part.key for part in parts}) != len(parts):
        raise ValueError(f"Duplicate or missing part IDs for {name}")
    records = []
    obj = StringIO()
    obj.write(f"# OpenSourceRail · {SCOPES[name]} · metres · one geometric unit per ledger row\n")
    next_vertex = 1
    for part in parts:
        required = (part.assembly, part.name, part.material, part.process, part.crew, part.account, part.basis, part.kind)
        if (not re.fullmatch(r"[A-Za-z0-9_-]+", part.key) or any(not value.strip() for value in required)
                or not part.meshes or not isinstance(part.quantity, int) or part.quantity <= 0
                or not math.isfinite(part.hours) or part.hours <= 0):
            raise ValueError(f"Incomplete part and work description for {part.key}")
        mass = range_values(part.mass_kg, part.key)
        volume = None
        if part.density_kg_m3 is not None:
            if mass is not None or not math.isfinite(part.density_kg_m3) or part.density_kg_m3 <= 0:
                raise ValueError(f"Choose one mass basis for {part.key}")
            volume = sum(solid_volume(mesh) for mesh in part.meshes)
            mass = [round(volume * part.density_kg_m3, 5)] * 3
        objects = []
        for i, mesh in enumerate(part.meshes, start=1):
            mesh_id = re.sub(r"[^A-Za-z0-9_-]", "_", mesh.name)
            label = f"{part.key}--{i:03}--{mesh_id}"
            objects.append(label)
            obj.write(f"o {label}\n")
            if mesh.vertices.ndim != 2 or mesh.vertices.shape[1] != 3 or not np.isfinite(mesh.vertices).all():
                raise ValueError(f"Invalid vertex coordinates on {label}")
            for vertex in mesh.vertices:
                obj.write("v " + " ".join(f"{value:.8f}" for value in vertex) + "\n")
            for face in mesh.faces:
                if len(face) < 3 or min(face) < 0 or max(face) >= len(mesh.vertices):
                    raise ValueError(f"Invalid facet on {label}")
                obj.write("f " + " ".join(str(index + next_vertex) for index in face) + "\n")
            next_vertex += len(mesh.vertices)
        records.append(dict(
            key=part.key, kind=part.kind, assembly=part.assembly, name=part.name, material=part.material,
            geometry_objects=objects, quantity=part.quantity, unit_mass_kg=mass,
            unit_volume_m3=round(volume, 8) if volume is not None else None,
            unit_price_usd=range_values(part.price_usd, part.key), work=part.process, crew=part.crew,
            unit_person_hours=part.hours, account=part.account, basis=part.basis, predecessors=part.predecessors,
        ))
    validate_dependencies(records)
    mesh_bytes = obj.getvalue().encode()
    return records, mesh_bytes


def validate_dependencies(records):
    pending = {row["key"]: set(row["predecessors"]) for row in records}
    for key, deps in pending.items():
        if not deps.issubset(pending) or key in deps:
            raise ValueError(f"Invalid work dependency on {key}: {deps}")
    while pending:
        ready = {key for key, deps in pending.items() if not deps}
        if not ready:
            raise ValueError("Cyclic assembly workplan")
        pending = {key: deps - ready for key, deps in pending.items() if key not in ready}


def totals(records, field):
    known = [row for row in records if row[field] is not None]
    return [round(sum(row[field][index] * row["quantity"] for row in known), 4) for index in range(3)]


def grouped_totals(records):
    groups = defaultdict(list)
    for row in records:
        groups[row["kind"]].append(row)
    return {kind: dict(rows=len(rows), quantities=sum(row["quantity"] for row in rows),
                       known_mass_kg=totals(rows, "unit_mass_kg"),
                       unknown_mass_rows=sum(row["unit_mass_kg"] is None for row in rows),
                       known_price_usd=totals(rows, "unit_price_usd"),
                       unpriced_rows=sum(row["unit_price_usd"] is None for row in rows),
                       required_person_hours=round(sum(row["unit_person_hours"] * row["quantity"] for row in rows), 3))
            for kind, rows in groups.items()}


def write_bom(path, candidates):
    inputs = ("key", "kind", "assembly", "name", "quantity", "material", "account", "basis", "work", "crew",
              "unit_person_hours", "predecessors", "geometry_objects")
    expanded = tuple(f"{scope}_{metric}_{case}" for metric in ("mass_kg", "price_usd")
                     for scope in ("unit", "extended") for case in ("low", "base", "high"))
    with path.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=("film", "candidate_id", *inputs, *expanded), lineterminator="\n")
        writer.writeheader()
        for film, candidate in candidates.items():
            for row in candidate["parts"]:
                entry = {key: row[key] for key in inputs}
                entry["predecessors"] = ";".join(row["predecessors"])
                entry["geometry_objects"] = ";".join(row["geometry_objects"])
                for metric in ("mass_kg", "price_usd"):
                    values = row[f"unit_{metric}"]
                    if values is None:
                        continue
                    for value, case in zip(values, ("low", "base", "high"), strict=True):
                        entry[f"unit_{metric}_{case}"] = value
                        entry[f"extended_{metric}_{case}"] = round(value * row["quantity"], 5)
                writer.writerow(dict(film=film, candidate_id=candidate["candidate_id"], **entry))


def workplan(candidates, sources):
    wage_rows = json.loads((ROOT / WAGES).read_text())["rows"]
    wages = {row["role"]: (row["rates_cents_per_hour"], row["rate_basis"])
             for row in wage_rows if row["rates_cents_per_hour"]}
    rows, gaps = [], []
    for film, candidate in candidates.items():
        for part in candidate["parts"]:
            minutes = math.ceil(part["unit_person_hours"] * part["quantity"] * 60)
            rates, basis = wages.get(part["crew"], wages["body" if film == "train" else "Alignment and installation"])
            if part["crew"] not in wages:
                basis = f"Skilled trade proxy from published Baghdad workplan. {basis}"
            # Compare staffing in a repeatable eight-hour slot with 85% productive
            # time. Resource sharing and dates are intentionally unassigned.
            posts = 4 if minutes > 4 * 480 else 2
            days = math.ceil(minutes / (posts * 480 * .85))
            rows.append(dict(work_id=f"{film}-{part['key']}", phase=f"{film} / {part['assembly']}",
                             role=part["crew"], shift="Day work package", start_minute=360,
                             minutes_per_shift=480, days=days, assigned_posts=posts,
                             required_minutes=minutes, paid_minutes=days * 480 * posts, utilisation_bps=8500,
                             rates_cents_per_hour=rates, rate_basis=basis, cost_account=part["account"]))
        gaps.append(dict(phase=film, work="Supplier scope and task-time reconciliation",
                         owner="Assembly and procurement leads",
                         cost_basis="Replace covered lines against existing allowances. Confirm resources, task durations, access and inspection with the delivery team."))
    plan = dict(schema="osr-workforce-plan/1",
                scope=dict(label="Baghdad animation assembly packages",
                           calendar_basis="Independent 06:00 eight-hour staffing slots per work package at 85% utilisation. "
                           "Work order dependencies are in the assembly ledger. Shared crew calendars and total elapsed duration remain open.",
                           cost_basis="Allowances use the existing Baghdad wage assumptions. Deduct labour already included in an order before changing the programme estimate.",
                           scope_boundaries="One six-car indicative study and one repeatable civil bay plus separate plant provision.",
                           candidate_ids={key: value["candidate_id"] for key, value in candidates.items()}),
                source_sha256=sources, rows=rows, gaps=gaps)
    return dict(plan, plan_id=digest(encoded(plan)))


def publish(output):
    output.mkdir(exist_ok=True, parents=True)
    candidates = {}
    sources = {}
    for name in FILMS:
        module = importlib.import_module(name)
        records, geometry = inventory_document(module, name)
        geometry_path = output / f"{name}-parts.obj.gz"
        geometry_path.write_bytes(gzip.compress(geometry, mtime=0))
        physical = dict(scope=SCOPES[name], geometry_sha256=digest(geometry),
                        inventory=[{key: row[key] for key in ("key", "quantity", "material", "kind")} for row in records])
        if name == "train":
            physical["operation"] = module.OPERATION
        candidate_sources = (*module.SOURCES, *(f"docs/assets/assembly-animations/{file}"
                              for file in (f"{name}.py", "ledger.py", "scene.py")))
        candidate = dict(candidate_id=digest(encoded(physical)), **physical,
                         part_file=geometry_path.name, parts=records, totals=grouped_totals(records),
                         source_sha256={path: digest((ROOT / path).read_bytes()) for path in sorted(set(candidate_sources))},
                         physical_acceptance=False)
        candidate["evaluation_id"] = digest(encoded(candidate))
        sources.update(candidate["source_sha256"])
        candidates[name] = candidate
    ledger = dict(schema="osr-baghdad-assembly-detail/1", candidates=candidates)
    (output / "assembly-ledger.json").write_bytes(encoded(ledger))
    write_bom(output / "assembly-bom.csv", candidates)
    sources[WAGES] = digest((ROOT / WAGES).read_bytes())
    (output / "assembly-plan.json").write_bytes(encoded(workplan(candidates, sources)))
    return ledger


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    document = publish(args.output)
    for name, record in document["candidates"].items():
        print(f"{name} · {len(record['parts'])} work packages · {record['candidate_id']}")

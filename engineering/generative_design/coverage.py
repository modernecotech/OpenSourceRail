"""Inventory coverage is necessary for a design campaign, never design acceptance."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCOPE = Path(__file__).with_name("data") / "system-scope.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def local(name, root=ROOT):
    path = root / name
    if (
        Path(name).is_absolute()
        or path.is_symlink()
        or not path.resolve().is_relative_to(root.resolve())
    ):
        raise ValueError("safe repository-relative evidence path required")
    return path


def records(document, collection):
    nodes = [document]
    for key in collection.split("."):
        flatten = key.endswith("[]")
        key = key.removesuffix("[]")
        next_nodes = [n[key] for n in nodes]
        nodes = (
            [item for group in next_nodes for item in group] if flatten else next_nodes
        )
    return [item for group in nodes for item in group]


def audit(scope=None, *, root=ROOT):
    scope = scope or json.loads(SCOPE.read_text())
    if (
        scope.get("schema") != "osr-multi-agent-system-scope/1"
        or scope.get("physical_release") is not False
    ):
        raise ValueError("controlled unreleased multi-agent scope required")
    packages = scope["work_packages"]
    ids = [p["id"] for p in packages]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("unique nonempty work packages required")
    from engineering.design_engine.registry import problems

    known = problems()
    covered = {}
    for package in packages:
        if (
            package.get("physical_release") is not False
            or package.get("status") != "open"
        ):
            raise ValueError("scope allocation cannot grant completion or release")
        if (
            set(package["dependencies"]) - set(ids)
            or package["id"] in package["dependencies"]
        ):
            raise ValueError("unknown or self-dependent work package")
        if set(package["mapped_common_problems"]) - set(known):
            raise ValueError("unknown common problem mapping")
        if set(package.get("mapped_generative_lanes", [])) - {"civil", "mechanical"}:
            raise ValueError("unknown generative lane mapping")
        if package["completion_predicate"].get("all_required") is not True:
            raise ValueError("all completion conditions must remain mandatory")
        for source in package["authoritative_sources"]:
            local(source["path"], root).read_bytes()
            covered.setdefault(source["path"], set()).update(source["ids"])
    remaining = {p["id"]: set(p["dependencies"]) for p in packages}
    ordered = []
    while remaining:
        ready = sorted(k for k, deps in remaining.items() if not deps)
        if not ready:
            raise ValueError("cyclic work-package dependencies")
        ordered.extend(ready)
        remaining = {
            k: deps - set(ready) for k, deps in remaining.items() if k not in ready
        }
    inventories = []
    for inventory in scope["source_inventory"]:
        path = local(inventory["path"], root)
        if sha(path) != inventory["sha256"]:
            raise ValueError("source inventory changed: " + inventory["path"])
        document = (
            json.loads(path.read_text())
            if inventory.get("inventory_collections")
            else None
        )
        for spec in inventory.get("inventory_collections", []):
            actual = {
                r[spec["id_field"]] for r in records(document, spec["collection"])
            }
            if actual != set(spec["expected_ids"]):
                raise ValueError(
                    "inventory IDs changed: "
                    + inventory["path"]
                    + ":"
                    + spec["collection"]
                )
            if actual - covered.get(inventory["path"], set()):
                raise ValueError("unassigned source IDs: " + inventory["path"])
            inventories.append(
                dict(
                    path=inventory["path"],
                    collection=spec["collection"],
                    ids=sorted(actual),
                    count=len(actual),
                )
            )
    return dict(
        inventory_coverage_verified=True,
        inventories=inventories,
        work_package_count=len(packages),
        dependency_order=ordered,
        physical_release=False,
    )


def ledger(scope, lanes, common):
    """A representative search cannot close a source package or its authority gates."""
    rows = []
    for package in scope["work_packages"]:
        lane_ids = package.get("mapped_generative_lanes", [])
        lane_evidence = [
            {
                "lane": name,
                "selected_candidate_ids": lanes[name]["selected_candidate_ids"],
            }
            for name in lane_ids
            if name in lanes
        ]
        common_evidence = [
            {
                "problem": problem,
                "job": common[problem]["job"],
                "job_status": common[problem]["status"],
                "candidate_count": common[problem]["candidate_count"],
            }
            for problem in package["mapped_common_problems"]
            if problem in common
        ]
        rows.append(
            dict(
                id=package["id"],
                title=package["title"],
                domain=package["domain"],
                owner_agent_role=package["owner_agent_role"],
                dependencies=package["dependencies"],
                authoritative_sources=package["authoritative_sources"],
                exploration=(
                    "representative-partial"
                    if lane_evidence or common_evidence
                    else "requires-discipline-model"
                ),
                generative_evidence=lane_evidence,
                common_evidence=common_evidence,
                required_gates=package["required_gates"],
                completion_predicate=package["completion_predicate"],
                completion_evidence=None,
                manufacturing_release=False,
                design_complete=False,
                physical_release=False,
            )
        )
    return dict(
        schema="osr-generative-closure-ledger/1",
        work_packages=rows,
        counts=dict(Counter(r["exploration"] for r in rows)),
        completed_packages=0,
        all_systems_design_complete=False,
        physical_release=False,
    )


def validate_ledger(scope, closure):
    expected = {p["id"]: p for p in scope["work_packages"]}
    rows = closure["work_packages"]
    actual = [p["id"] for p in rows]
    if len(actual) != len(set(actual)) or set(actual) != set(expected):
        raise ValueError("closure ledger package IDs differ from exact scope")
    for row in rows:
        parent = expected[row["id"]]
        if any(
            row[key] != parent[key]
            for key in (
                "authoritative_sources",
                "required_gates",
                "completion_predicate",
                "dependencies",
                "owner_agent_role",
            )
        ):
            raise ValueError("closure ledger changed mandatory scope/gates")
        if (
            any(
                row[key] is not False
                for key in (
                    "design_complete",
                    "manufacturing_release",
                    "physical_release",
                )
            )
            or row["completion_evidence"] is not None
        ):
            raise ValueError(
                "partial research cannot close manufacturing work packages"
            )
    if (
        closure["counts"] != dict(Counter(r["exploration"] for r in rows))
        or closure["completed_packages"] != 0
        or closure["all_systems_design_complete"] is not False
    ):
        raise ValueError("closure rollup differs from its open work packages")


def work_queue(scope, closure):
    order = audit(scope)["dependency_order"]
    return dict(
        schema="osr-multi-agent-design-work-queue/1",
        tasks=[
            dict(
                work_package=row["id"],
                owner_agent_role=row["owner_agent_role"],
                dependencies=row["dependencies"],
                state="awaiting-controlled-input-or-model-change",
                next_action=(
                    "Implement and independently validate the missing discipline model, then generate bounded candidates"
                    if row["exploration"] == "requires-discipline-model"
                    else "Resolve adverse/unknown checks and develop configuration-specific manufacturing and interface evidence"
                ),
                required_inputs=row["required_gates"],
                completion_predicate=row["completion_predicate"],
            )
            for row in sorted(
                closure["work_packages"], key=lambda r: order.index(r["id"])
            )
        ],
        restart_rule="Create a fresh source-bound campaign after controlled input/model changes; preserve old attempts and invalidate affected descendants. Do not repeat unchanged inputs as evidence closure.",
        physical_release=False,
    )

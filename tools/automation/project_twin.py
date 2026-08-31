#!/usr/bin/env python3
"""Deterministic project-controls model for a generated OSR city.

The module deliberately separates *planned candidates* from contractual or
actual records.  It turns the city asset/work/BOM graph into a resource-loaded
CPM baseline, budget work packages, procurement requirements, a time-phased
cash requirement and a construction-state timeline.  Issued orders, invoices,
payments and actual progress remain append-only Ops Core records.
"""

from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.0"
PLANNING_STATUS = "planning-digital-twin-not-construction-release"

DEFAULT_RESOURCE_CAPACITY = {
    "project controls": 1,
    "rolling stock plant": 4,
    "rolling stock composite moulding cell": 2,
    "rolling stock clip-on body cell": 2,
    "track civil crew": 2,
    "station civil crew": 2,
    "station systems crew": 2,
    "depot civil and plant crew": 1,
    "wayside bench": 3,
    "wayside installation crew": 3,
    "switch production cell": 2,
    "switch installation crew": 2,
    "energy installation crew": 2,
    "energy commissioning crew": 1,
}

LEAD_TIME_DAYS = {
    "MAKE": 30,
    "BID": 150,
    "SOURCE": 90,
    "COTS": 120,
    "PROJECT_KIT": 60,
}

PAYMENT_TERMS = {
    "MAKE": "10% release / 80% completion / 10% acceptance",
    "BID": "20% order / 70% delivery / 10% acceptance",
    "SOURCE": "20% order / 70% delivery / 10% acceptance",
    "COTS": "30% order / 60% delivery / 10% acceptance",
    "PROJECT_KIT": "10% mobilisation / 80% progress / 10% acceptance",
}

MILESTONES = (
    ("mobilisation", -30, 0.10),
    ("progress", None, 0.55),
    ("delivery-or-completion", 0, 0.30),
    ("retention-release", 90, 0.05),
)


def build_project_twin(
    *,
    meta: dict[str, Any],
    assets: list[dict[str, Any]],
    manufacturing_tasks: list[dict[str, Any]],
    manufacturing_materials: list[dict[str, Any]],
    finance: dict[str, Any] | None,
    source_paths: dict[str, Path],
    resource_capacity: dict[str, Any] | None = None,
    previous_revisions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a complete deterministic planning twin from canonical city data."""

    tasks = deepcopy(manufacturing_tasks)
    capacities = dict(DEFAULT_RESOURCE_CAPACITY)
    for key, value in (resource_capacity or {}).items():
        capacities[str(key)] = max(1, int(value))
    cpm = apply_resource_cpm(tasks, capacities)

    capex = _capex(finance)
    contracts = build_budget_contracts(tasks, capex)
    procurements = build_procurement_plan(tasks, manufacturing_materials)
    cashflow_rows, monthly_cashflow = build_cashflow(contracts, capex)
    timeline = build_visualization_timeline(tasks)
    source_records = {
        name: {
            "path": _relative_or_text(path),
            "sha256": _sha256(path) if path.is_file() else None,
        }
        for name, path in sorted(source_paths.items())
    }

    revision_projection = {
        "city": meta.get("city_slug"),
        "sources": source_records,
        "tasks": [
            {
                "uid": row["manufacturing_uid"],
                "start": row["planned_start_day"],
                "finish": row["planned_finish_day"],
                "predecessors": row["schedule_predecessor_uids"],
                "budget": row.get("budget_usd", 0.0),
            }
            for row in tasks
        ],
        "procurement": [
            {
                "id": row["purchase_order_id"],
                "required": row["required_by_day"],
                "order": row["order_by_day"],
                "cost": row["planning_cost_usd"],
                "cots_candidates": row.get("cots_candidate_ids", ""),
            }
            for row in procurements
        ],
    }
    revision_id = "twin-" + _content_hash(revision_projection)[:16]
    revisions = _revision_history(previous_revisions or [], revision_id, source_records)

    totals = {
        "assets": len(assets),
        "work_packages": len(tasks),
        "critical_work_packages": cpm["critical_task_count"],
        "programme_working_days": cpm["programme_working_days"],
        "budget_contracts": len(contracts),
        "planned_purchase_orders": len(procurements),
        "pre_ntp_order_actions": sum(1 for row in procurements if row["order_by_day"] < 0),
        "cashflow_months": len(monthly_cashflow),
        "planned_capex_usd": round(sum(row["budget_usd"] for row in contracts), 2),
        "priced_procurement_usd": round(sum(row["planning_cost_usd"] for row in procurements), 2),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": PLANNING_STATUS,
        "city": meta.get("city_slug", ""),
        "product_scope": {
            "rolling_stock_family": meta.get("rolling_stock_family", ""),
            "rolling_stock_definition": (
                "detailed LM3 part/BOM/tooling/traveller reference"
                if meta.get("rolling_stock_family") == "light-metro-3car"
                else "family-level schedule and cost only; detailed family release required"
            ),
        },
        "revision_id": revision_id,
        "baseline": {
            "kind": "deterministic-planning-baseline",
            "project_day_zero": "notice-to-proceed",
            "calendar": "working-day offsets; map to an approved local calendar before release",
            "actuals_status": "empty-until-recorded-in-ops-core",
        },
        "sources": source_records,
        "revisions": revisions,
        "totals": totals,
        "critical_path": cpm,
        "resource_capacity": dict(sorted(capacities.items())),
        "work_packages": tasks,
        "budget_contracts": contracts,
        "purchase_orders": procurements,
        "cashflow": {
            "currency": "USD",
            "basis": "schedule-of-values planning requirements; not commitments, invoices or payments",
            "milestones": cashflow_rows,
            "monthly_requirements": monthly_cashflow,
        },
        "visualization_timeline": timeline,
        "actuals": {
            "purchase_orders": [],
            "deliveries": [],
            "invoices": [],
            "payments": [],
            "progress_updates": [],
            "source": "Ops Core append-only project records",
        },
        "release_gates": [
            "approved surveyed alignment, utilities, land and geotechnical baseline",
            "engineer-released civil, station, systems and rolling-stock design packages",
            "supplier-frozen configurations, quotations, lead times and contractual terms",
            "approved resource calendar, risk allowance and construction baseline",
            "funding approvals and independently reviewed schedule-linked cashflow",
            "national approvals, independent safety assessment and competent-person release",
        ],
    }


def apply_resource_cpm(
    tasks: list[dict[str, Any]], capacities: dict[str, int] | None = None
) -> dict[str, Any]:
    """Apply deterministic finite-resource lanes and a CPM forward/backward pass."""

    if not tasks:
        return {
            "programme_working_days": 0,
            "critical_task_count": 0,
            "critical_task_uids": [],
            "unresolved_external_gates": [],
        }
    capacity = {**DEFAULT_RESOURCE_CAPACITY, **(capacities or {})}
    by_uid = {str(row["manufacturing_uid"]): row for row in tasks}
    if len(by_uid) != len(tasks):
        raise ValueError("manufacturing task ids must be unique")
    explicit_predecessors = {
        uid: [item for item in _refs(str(row.get("predecessor_uids", ""))) if item in by_uid]
        for uid, row in by_uid.items()
    }
    topological = _topological_order(by_uid, explicit_predecessors)

    lane_state: dict[str, list[tuple[int, str]]] = {}
    augmented: dict[str, list[str]] = {uid: list(explicit_predecessors[uid]) for uid in by_uid}
    for uid in topological:
        row = by_uid[uid]
        work_center = str(row.get("work_center") or row.get("package_id") or "unallocated")
        count = max(1, int(capacity.get(work_center, _integer(row.get("resource_count"), 1))))
        lanes = lane_state.setdefault(work_center, [(-1, "") for _ in range(count)])
        if len(lanes) < count:
            lanes.extend([(-1, "") for _ in range(count - len(lanes))])
        dependency_start = max(
            (int(by_uid[pred].get("planned_finish_day", -1)) + 1 for pred in augmented[uid]),
            default=0,
        )
        lane_index = min(
            range(len(lanes)),
            key=lambda index: (max(dependency_start, lanes[index][0] + 1), index),
        )
        available_after, resource_predecessor = lanes[lane_index]
        if resource_predecessor and resource_predecessor not in augmented[uid]:
            augmented[uid].append(resource_predecessor)
        start = max(dependency_start, available_after + 1)
        duration = max(1, int(row.get("duration_days", 1)))
        finish = start + duration - 1
        row["planned_start_day"] = start
        row["planned_finish_day"] = finish
        row["planned_start_basis"] = f"project_day_{start}"
        row["planned_finish_basis"] = f"project_day_{finish}"
        row["resource_pool"] = work_center
        row["resource_lane"] = lane_index + 1
        row["resource_capacity"] = count
        row["resource_predecessor_uid"] = resource_predecessor
        row["schedule_predecessor_uids"] = "; ".join(augmented[uid])
        lanes[lane_index] = (finish, uid)

    # Resource edges always point to an already scheduled task, so the first
    # topological order remains valid for the augmented graph.
    successors: dict[str, list[str]] = {uid: [] for uid in by_uid}
    for uid, predecessors in augmented.items():
        for predecessor in predecessors:
            successors[predecessor].append(uid)
    programme_days = max(int(row["planned_finish_day"]) + 1 for row in tasks)
    for uid in reversed(topological):
        row = by_uid[uid]
        duration = max(1, int(row["duration_days"]))
        if successors[uid]:
            late_finish_exclusive = min(int(by_uid[item]["late_start_day"]) for item in successors[uid])
        else:
            late_finish_exclusive = programme_days
        late_start = late_finish_exclusive - duration
        row["late_start_day"] = late_start
        row["late_finish_day"] = late_finish_exclusive - 1
        row["total_float_days"] = late_start - int(row["planned_start_day"])
        row["is_critical"] = row["total_float_days"] == 0

    critical = [uid for uid in topological if by_uid[uid]["is_critical"]]
    unresolved = sorted(
        {
            gate
            for row in tasks
            for gate in _refs(str(row.get("external_predecessors", "")))
        }
    )
    return {
        "method": "finite-resource lane assignment followed by CPM forward/backward pass",
        "programme_working_days": programme_days,
        "critical_task_count": len(critical),
        "critical_task_uids": critical,
        "unresolved_external_gates": unresolved,
        "external_gate_rule": "recorded as pre-baseline release gates; they do not silently receive zero duration",
    }


def build_budget_contracts(
    tasks: list[dict[str, Any]], capex: dict[str, Any]
) -> list[dict[str, Any]]:
    """Allocate the authoritative city CAPEX to auditable schedule-of-values rows."""

    buckets = {str(row["bucket"]): row for row in capex.get("buckets", [])}
    by_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        for bucket in _task_buckets(task):
            by_bucket[bucket].append(task)

    contracts: list[dict[str, Any]] = []
    for bucket_name, bucket in sorted(buckets.items()):
        candidates = sorted(
            by_bucket.get(bucket_name, []),
            key=lambda row: str(row["manufacturing_uid"]),
        )
        if not candidates:
            candidates = sorted(
                by_bucket.get("epc_overhead", []) or tasks[:1],
                key=lambda row: str(row["manufacturing_uid"]),
            )
        total = float(bucket.get("total_usd", 0.0))
        weights = [max(1, int(row.get("duration_days", 1))) for row in candidates]
        allocated = 0.0
        for index, (task, weight) in enumerate(zip(candidates, weights)):
            value = total - allocated if index == len(candidates) - 1 else round(total * weight / sum(weights), 2)
            allocated += value
            task["budget_bucket"] = bucket_name
            task["budget_usd"] = round(float(task.get("budget_usd", 0.0)) + value, 2)
            contract_id = f"{task['manufacturing_uid']}:SOV:{bucket_name}"
            contracts.append(
                {
                    "contract_id": contract_id,
                    "status": "budget-work-package-not-awarded",
                    "bucket": bucket_name,
                    "manufacturing_uid": task["manufacturing_uid"],
                    "asset_id": task.get("asset_id", ""),
                    "package_id": task.get("package_id", ""),
                    "work_title": task.get("work_order_title", ""),
                    "planned_start_day": task["planned_start_day"],
                    "planned_finish_day": task["planned_finish_day"],
                    "budget_usd": round(value, 2),
                    "local_share": float(bucket.get("local_share", 0.0)),
                    "imported_share": float(bucket.get("imported_share", 0.0)),
                    "committed_usd": 0.0,
                    "invoiced_usd": 0.0,
                    "paid_usd": 0.0,
                    "actual_progress_percent": 0.0,
                }
            )
    return contracts


def build_procurement_plan(
    tasks: list[dict[str, Any]], materials: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Deduplicate BOM demand and calculate required/order-by dates."""

    by_task = {str(row["manufacturing_uid"]): row for row in tasks}
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for material in materials:
        key = (
            str(material.get("asset_id", "")),
            str(material.get("bom_source", "")),
            str(material.get("bom_ref", "")),
        )
        grouped[key].append(material)

    rows: list[dict[str, Any]] = []
    for index, (key, group) in enumerate(sorted(grouped.items()), start=1):
        linked = sorted(
            {
                str(item["manufacturing_uid"])
                for item in group
                if str(item.get("manufacturing_uid", "")) in by_task
            }
        )
        required = min((int(by_task[uid]["planned_start_day"]) for uid in linked), default=0)
        first = group[0]
        route = str(first.get("make_buy_source") or "PROJECT_KIT").upper()
        lead = LEAD_TIME_DAYS.get(route, LEAD_TIME_DAYS["PROJECT_KIT"])
        supplier = str(first.get("supplier_name") or "local competitive procurement")
        supplier_family = str(first.get("supplier_family") or first.get("description") or key[2])
        planning_cost = _number(first.get("base_usd"))
        rows.append(
            {
                "purchase_order_id": f"PO-CAND-{index:06d}",
                "status": "planned-not-issued",
                "asset_id": key[0],
                "bom_source": key[1],
                "bom_ref": key[2],
                "description": first.get("description", ""),
                "quantity_basis": first.get("quantity_basis", ""),
                "task_uids": "; ".join(linked),
                "sourcing_route": route,
                "supplier_anchor_id": first.get("supplier_anchor_id", ""),
                "supplier": supplier,
                "supplier_family_or_local_equivalent": supplier_family,
                "supplier_selection_status": first.get("supplier_selection_status", "competitive-source-required"),
                "cots_candidate_ids": first.get("cots_candidate_ids", ""),
                "cots_candidate_models": first.get("cots_candidate_models", ""),
                "cots_selection_states": first.get("cots_selection_states", ""),
                "cots_register_status": first.get("cots_register_status", "no-listed-candidate"),
                "currency": "USD",
                "planning_cost_usd": planning_cost,
                "cost_status": "planning-basis" if planning_cost else "quotation-required",
                "lead_time_days": lead,
                "required_by_day": required,
                "order_by_day": required - lead,
                "incoterm": "TBD-at-RFQ",
                "payment_terms": PAYMENT_TERMS.get(route, PAYMENT_TERMS["PROJECT_KIT"]),
                "committed_usd": 0.0,
                "delivered_quantity": 0.0,
                "invoiced_usd": 0.0,
                "paid_usd": 0.0,
            }
        )
    return rows


def build_cashflow(
    contracts: list[dict[str, Any]], capex: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Create task-linked milestone requirements and 30-day cash buckets."""

    rows: list[dict[str, Any]] = []
    for contract in contracts:
        start = int(contract["planned_start_day"])
        finish = int(contract["planned_finish_day"])
        for milestone, offset, fraction in MILESTONES:
            if offset is None:
                day = start + max(0, (finish - start) // 2)
            elif milestone == "mobilisation":
                day = start + offset
            else:
                day = finish + offset
            value = round(float(contract["budget_usd"]) * fraction, 2)
            rows.append(
                {
                    "cashflow_id": f"{contract['contract_id']}:{milestone}",
                    "contract_id": contract["contract_id"],
                    "manufacturing_uid": contract["manufacturing_uid"],
                    "bucket": contract["bucket"],
                    "milestone": milestone,
                    "project_day": day,
                    "month_index": math.floor(day / 30) + 1,
                    "planned_requirement_usd": value,
                    "local_requirement_usd": round(value * float(contract["local_share"]), 2),
                    "imported_requirement_usd": round(value * float(contract["imported_share"]), 2),
                    "committed_usd": 0.0,
                    "invoiced_usd": 0.0,
                    "paid_usd": 0.0,
                    "status": "forecast-not-committed",
                }
            )

    # Make rounding reconcile exactly to the authoritative total.
    target = round(float(capex.get("total_usd", 0.0)), 2)
    if rows:
        rows[-1]["planned_requirement_usd"] = round(
            rows[-1]["planned_requirement_usd"] + target - sum(row["planned_requirement_usd"] for row in rows),
            2,
        )
        rows[-1]["local_requirement_usd"] = round(
            rows[-1]["planned_requirement_usd"]
            * float(next(item for item in contracts if item["contract_id"] == rows[-1]["contract_id"])["local_share"]),
            2,
        )
        rows[-1]["imported_requirement_usd"] = round(
            rows[-1]["planned_requirement_usd"] - rows[-1]["local_requirement_usd"], 2
        )

    monthly: dict[int, dict[str, float]] = defaultdict(
        lambda: {"planned_requirement_usd": 0.0, "local_requirement_usd": 0.0, "imported_requirement_usd": 0.0}
    )
    for row in rows:
        month = int(row["month_index"])
        for key in monthly[month]:
            monthly[month][key] += float(row[key])
    cumulative = 0.0
    monthly_rows: list[dict[str, Any]] = []
    for month in sorted(monthly):
        planned = round(monthly[month]["planned_requirement_usd"], 2)
        cumulative += planned
        monthly_rows.append(
            {
                "month_index": month,
                "project_day_start": (month - 1) * 30,
                "project_day_finish": month * 30 - 1,
                "planned_requirement_usd": planned,
                "local_requirement_usd": round(monthly[month]["local_requirement_usd"], 2),
                "imported_requirement_usd": round(monthly[month]["imported_requirement_usd"], 2),
                "cumulative_requirement_usd": round(cumulative, 2),
            }
        )
    return rows, monthly_rows


def build_visualization_timeline(tasks: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for task in tasks:
        common = {
            "asset_id": task.get("asset_id", ""),
            "manufacturing_uid": task.get("manufacturing_uid", ""),
            "package_id": task.get("package_id", ""),
            "ifc_lookup": {"asset_id": task.get("asset_id", ""), "task_id": task.get("package_id", "")},
        }
        events.append({**common, "project_day": task["planned_start_day"], "state": "in-progress"})
        events.append({**common, "project_day": task["planned_finish_day"] + 1, "state": "planned-complete"})
    return sorted(events, key=lambda row: (int(row["project_day"]), str(row["asset_id"]), str(row["package_id"])))


def compact_summary(twin: dict[str, Any]) -> dict[str, Any]:
    monthly = twin["cashflow"]["monthly_requirements"]
    peak = max(monthly, key=lambda row: row["planned_requirement_usd"], default=None)
    orders = twin["purchase_orders"]
    priced = sum(1 for row in orders if row["planning_cost_usd"] > 0)
    candidate_linked = [row for row in orders if row.get("cots_candidate_ids")]
    candidate_ids = sorted({
        candidate_id
        for row in candidate_linked
        for candidate_id in _refs(str(row.get("cots_candidate_ids", "")))
    })
    buckets: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {"work_packages": 0, "budget_usd": 0.0}
    )
    for row in twin["budget_contracts"]:
        item = buckets[str(row["bucket"])]
        item["work_packages"] = int(item["work_packages"]) + 1
        item["budget_usd"] = round(float(item["budget_usd"]) + float(row["budget_usd"]), 2)
    return {
        "schema_version": twin["schema_version"],
        "status": twin["status"],
        "city": twin["city"],
        "product_scope": twin["product_scope"],
        "revision_id": twin["revision_id"],
        "baseline": twin["baseline"],
        "sources": twin["sources"],
        "revisions": twin["revisions"],
        "totals": twin["totals"],
        "critical_path": twin["critical_path"],
        "procurement": {
            "planned_purchase_orders": len(orders),
            "priced_rows": priced,
            "quotation_required_rows": len(orders) - priced,
            "manufacturer_candidate_linked_rows": len(candidate_linked),
            "manufacturer_candidate_ids": candidate_ids,
            "candidate_status": "controlled-design-input-not-order",
            "pre_ntp_order_actions": sum(1 for row in orders if row["order_by_day"] < 0),
            "earliest_order_by_day": min((row["order_by_day"] for row in orders), default=None),
        },
        "cashflow": {
            "currency": "USD",
            "total_planned_requirement_usd": round(
                sum(row["planned_requirement_usd"] for row in monthly), 2
            ),
            "peak_month": peak,
            "monthly_requirements": monthly,
        },
        "budget_by_bucket": dict(sorted(buckets.items())),
        "visualization": {
            "event_count": len(twin["visualization_timeline"]),
            "adapter": "visualization_timeline in the generated operations bundle",
        },
        "actuals": twin["actuals"],
        "release_gates": twin["release_gates"],
    }


def _topological_order(
    by_uid: dict[str, dict[str, Any]], predecessors: dict[str, list[str]]
) -> list[str]:
    indegree = {uid: len(items) for uid, items in predecessors.items()}
    successors: dict[str, list[str]] = {uid: [] for uid in by_uid}
    for uid, items in predecessors.items():
        for predecessor in items:
            successors[predecessor].append(uid)
    ready = deque(sorted(uid for uid, value in indegree.items() if value == 0))
    ordered: list[str] = []
    while ready:
        uid = ready.popleft()
        ordered.append(uid)
        for successor in sorted(successors[uid]):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
    if len(ordered) != len(by_uid):
        blocked = sorted(uid for uid, value in indegree.items() if value)
        raise ValueError(f"manufacturing dependency cycle: {', '.join(blocked[:8])}")
    return ordered


def _capex(finance: dict[str, Any] | None) -> dict[str, Any]:
    value = finance or {}
    capex = value.get("capex_usd", {})
    buckets = list(capex.get("procurement_origin_buckets", []))
    total = float(capex.get("reconciled_project_total", 0.0) or 0.0)
    if not buckets and total:
        buckets = [{"bucket": "epc_overhead", "total_usd": total, "local_share": 0.75, "imported_share": 0.25}]
    return {"total_usd": total, "buckets": buckets}


def _task_buckets(task: dict[str, Any]) -> tuple[str, ...]:
    asset_type = str(task.get("asset_type", ""))
    if asset_type == "rolling-stock":
        return ("rolling_stock",)
    if asset_type == "station":
        return ("stations",)
    if asset_type in {"depot", "depots-production"}:
        return ("depots",)
    if asset_type == "energy":
        return ("solar_plant", "charging_microgrid")
    if asset_type in {"signalling-comms", "waypoint", "hot-axle-detector", "switch"}:
        return ("signalling",)
    if asset_type in {"track-section", "structure"}:
        return ("civil",)
    return ("epc_overhead",)


def _revision_history(
    previous: list[dict[str, Any]], revision_id: str, sources: dict[str, Any]
) -> list[dict[str, Any]]:
    clean = [
        row for row in previous
        if isinstance(row, dict) and str(row.get("revision_id", ""))
    ]
    if not any(row.get("revision_id") == revision_id for row in clean):
        clean.append(
            {
                "revision_id": revision_id,
                "sequence": len(clean) + 1,
                "kind": "generated-planning-baseline",
                "source_hash": _content_hash(sources),
                "approval_status": "candidate-not-approved",
            }
        )
    return clean


def _refs(value: str) -> list[str]:
    return [item.strip() for item in value.replace(",", ";").split(";") if item.strip()]


def _integer(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _number(value: Any) -> float:
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return 0.0


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _content_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _relative_or_text(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path(__file__).resolve().parents[2]))
    except ValueError:
        return str(path)

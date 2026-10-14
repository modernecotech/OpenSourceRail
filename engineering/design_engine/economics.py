"""Scope-complete installed/lifecycle objectives and finite-resource schedules.

This layer consumes entered, dated records. Public candidate listings and missing
amounts never become supplier commitments, zero costs or adopted city finance.
"""

from __future__ import annotations
from datetime import date
import math

REQUIRED_SCOPES = {
    "materials",
    "joints-supports-retention-seals",
    "tooling",
    "labour",
    "inspection-rejects",
    "transport",
    "cranes-installation",
    "commissioning",
    "maintenance-replacement",
    "rights-imports",
}


def finite(value, name, minimum=0):
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError("finite scoped " + name + " required")
    return value


def installed_objectives(
    records, *, place, currency, as_of, complete_installed_inventory=False
):
    day = date.fromisoformat(as_of)
    priced = {}
    rejected = []
    for row in records:
        if row.get("state") != "verified-record" or row.get("kind") != "quotation":
            rejected.append(
                dict(id=row.get("id"), reason="unverified or wrong record kind")
            )
            continue
        quote = row["payload"]
        date.fromisoformat(quote["date"])
        if quote["place"] != place or quote["currency"] != currency:
            rejected.append(
                dict(
                    id=row["id"],
                    reason="different place/currency; no inferred FX or localisation",
                )
            )
            continue
        scope = quote["scope"]
        if scope not in REQUIRED_SCOPES:
            raise ValueError("cost must name an explicit installed/lifecycle scope")
        if scope in priced:
            raise ValueError("duplicate/overlapping cost scope")
        if date.fromisoformat(quote["date"]) > day:
            raise ValueError("quote date is after the appraisal date")
        lines = quote["line_items"]
        total = 0
        if not lines:
            raise ValueError("nonempty quoted scope required")
        for line in lines:
            total += finite(line["quantity"], "quantity", 1e-12) * finite(
                line["unit_price"], "unit price"
            )
        priced[scope] = dict(
            record_id=row["id"],
            quoted_amount=total,
            source_reference=quote["source_reference"],
            quote_date=quote["date"],
        )
    missing = sorted(REQUIRED_SCOPES - priced.keys())
    subtotal = sum(r["quoted_amount"] for r in priced.values())
    complete = not missing and complete_installed_inventory
    return dict(
        schema="osr-installed-lifecycle-objectives/1",
        place=place,
        currency=currency,
        as_of=as_of,
        priced_scopes=priced,
        missing_scopes=missing,
        rejected_records=rejected,
        known_scope_subtotal=subtotal if priced else None,
        scope_complete_total=subtotal if complete else None,
        complete_installed_inventory=complete_installed_inventory,
        carbon=None,
        imported_content=None,
        binding_procurement=False,
        global_finance_adopted=False,
        physical_release=False,
    )


def schedule(tasks, resources):
    """Deterministic list schedule with explicit unit capacities and prerequisites."""
    if (
        not isinstance(tasks, list)
        or not tasks
        or not isinstance(resources, list)
        or not resources
    ):
        raise ValueError("nonempty explicit tasks and resource inventory required")
    capacities = {r["id"]: r["capacity"] for r in resources}
    if len(capacities) != len(resources) or any(
        type(c) is not int or c < 1 or c > 100 for c in capacities.values()
    ):
        raise ValueError("unique bounded resource capacities required")
    known = {r["id"]: r for r in tasks}
    if len(known) != len(tasks) or len(tasks) > 10000:
        raise ValueError("unique bounded tasks required")

    def windows(value):
        if value is None:
            return None
        if not isinstance(value, list) or not 1 <= len(value) <= 64:
            raise ValueError("bounded explicit closure/availability windows required")
        previous = -1
        for item in value:
            if not isinstance(item, list) or len(item) != 2:
                raise ValueError("start/end window required")
            start, end = item
            finite(start, "window start")
            finite(end, "window end")
            if start < previous or end <= start:
                raise ValueError("ordered nonoverlapping windows required")
            previous = end
        return value

    resource_windows = {r["id"]: windows(r.get("available_windows")) for r in resources}
    for task in tasks:
        finite(task["duration_hours"], "task duration", 1e-12)
        finite(task.get("release_hour", 0), "procurement/release hour")
        windows(task.get("closure_windows"))
        if not task.get("productivity_source") or not task.get("resources"):
            raise ValueError(
                "sourced productivity and explicit crews/equipment required"
            )
        if len(task["predecessors"]) != len(set(task["predecessors"])) or any(
            p not in known for p in task["predecessors"]
        ):
            raise ValueError("known distinct task prerequisites required")
        for resource, count in task["resources"].items():
            if (
                resource not in capacities
                or type(count) is not int
                or not 1 <= count <= capacities[resource]
            ):
                raise ValueError("task exceeds explicit resource inventory")
    finished = {}
    rows = []
    reservations = {key: [] for key in capacities}
    pending = list(tasks)
    while pending:
        ready = [t for t in pending if all(p in finished for p in t["predecessors"])]
        if not ready:
            raise ValueError("construction/manufacturing dependency cycle")
        task = sorted(ready, key=lambda t: t["id"])[0]
        start = max(
            task.get("release_hour", 0),
            max((finished[p] for p in task["predecessors"]), default=0),
        )
        while True:
            end = start + task["duration_hours"]
            allowed = [
                task.get("closure_windows"),
                *[resource_windows[r] for r in task["resources"]],
            ]
            shifted = False
            for available in allowed:
                if available is None:
                    continue
                fitting = next(
                    (
                        max(start, a)
                        for a, b in available
                        if max(start, a) + task["duration_hours"] <= b
                    ),
                    None,
                )
                if fitting is None:
                    raise ValueError(
                        "task cannot fit explicit closure or resource availability windows"
                    )
                if fitting > start:
                    start = fitting
                    shifted = True
            if shifted:
                continue
            conflicts = []
            for resource, count in task["resources"].items():
                times = sorted(
                    {
                        start,
                        end,
                        *[
                            x
                            for a, b, n in reservations[resource]
                            for x in (a, b)
                            if start < x < end
                        ],
                    }
                )
                for a, b in zip(times, times[1:]):
                    active = [
                        (left, right, n)
                        for left, right, n in reservations[resource]
                        if left < b and right > a
                    ]
                    if (
                        count + sum(n for left, right, n in active)
                        > capacities[resource]
                    ):
                        conflicts.extend(right for left, right, n in active)
            if not conflicts:
                break
            start = min(t for t in conflicts if t > start)
        for resource, count in task["resources"].items():
            reservations[resource].append((start, end, count))
        rows.append(
            dict(
                task=task["id"],
                start_hour=start,
                end_hour=end,
                resources=task["resources"],
                productivity_source=task["productivity_source"],
                closure_windows=task.get("closure_windows"),
            )
        )
        finished[task["id"]] = end
        pending.remove(task)
    return dict(
        schema="osr-finite-resource-objective/1",
        tasks=rows,
        capacity=capacities,
        resource_availability=resource_windows,
        makespan_hours=max(finished.values(), default=0),
        source_is_planning_not_appointment=True,
        actual_work_performed=False,
        closure_disruption_value=None,
        physical_release=False,
    )

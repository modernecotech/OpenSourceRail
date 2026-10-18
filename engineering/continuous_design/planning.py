"""Feasible integration frontier, readable feedback and explicit historical inputs.

Historical measurements never become current acceptance: only candidate input
values are nominated, then rebuilt/re-evaluated in the new source epoch.
"""
from collections import defaultdict
import json
import math

from engineering.twin_workflow import core
from . import tasks

CHILD_KINDS = ("mechanical-detail", "civil-detail", "software-logic")


def lighter_neighbors(kind, parameters):
    """One-coordinate material-saving trials; workers must reassess every check."""
    module, _ = tasks.contexts(kind)
    spec = core.read(module.DATA if kind == "mechanical-detail" else core.ROOT / "engineering/generative_design/data/civil-detail-space.json")
    domains = spec["bounds" if kind == "mechanical-detail" else "domains"]
    directions = (dict(side_depth_m=-1, plate_thickness_m=-1, web_thickness_m=-1,
        spine_wall_m=-1, bolster_depth_m=-1, diaphragm_thickness_m=-1, crossbearer_pitch_m=1)
        if kind == "mechanical-detail" else {name: (1 if name == "stirrup_spacing_m" else -1) for name in domains})
    proposals = []
    for name, direction in directions.items():
        index = domains[name].index(parameters["variables"][name]) + direction
        if 0 <= index < len(domains[name]):
            variables = dict(parameters["variables"])
            variables[name] = domains[name][index]
            proposals.append(variables)
    return proposals


def failed_checks(result):
    explicit = result.get("failed_checks")
    if isinstance(explicit, list):
        return explicit
    failed = []
    for name, value in result.get("checks", {}).items():
        state = value.get("state") if isinstance(value, dict) else value
        if state is False or (isinstance(state, str) and state in {"fail", "failed"}):
            failed.append(name)
    return failed


def mass(result):
    value = result.get("assessment", {}).get("objectives", {}).get("mass_kg")
    return value if type(value) in (int, float) and math.isfinite(value) and value >= 0 else math.inf


def children(store, baseline):
    groups = {k: [] for k in CHILD_KINDS}
    for row in store.db.execute("SELECT * FROM jobs WHERE baseline=? AND status='completed' ORDER BY created", (baseline,)):
        value = json.loads(row["task"])
        if value["kind"] in groups:
            result = store.result(row)
            groups[value["kind"]].append((row, value, result))
    return groups


def integration_frontier(store, baseline, *, admission_budget=8):
    groups = children(store, baseline)
    eligible = {k: [entry for entry in rows if entry[2]["study_pass"]] for k, rows in groups.items()}
    software = eligible["software-logic"]
    if not software:
        return 0
    software.sort(key=lambda e: e[0]["key"])
    frames = sorted(eligible["mechanical-detail"], key=lambda e: (mass(e[2]), e[0]["key"]))
    civil_by_context = defaultdict(list)
    for entry in eligible["civil-detail"]:
        civil_by_context[entry[2]["assessment"]["context_id"]].append(entry)
    for entries in civil_by_context.values():
        entries.sort(key=lambda e: (mass(e[2]), e[0]["key"]))
    added = 0
    # Round-robin across spans/configurations before deepening a single context.
    maximum = max((len(v) for v in civil_by_context.values()), default=0)
    for depth in range(maximum):
        for frame, _, mr in frames:
            for context in sorted(civil_by_context):
                entries = civil_by_context[context]
                if depth >= len(entries):
                    continue
                civil, _, cr = entries[depth]
                if cr["assessment"]["architecture_id"] != mr["assessment"]["configuration_id"]:
                    continue
                value = tasks.task("integration-coupling", dict(children=[frame["key"], civil["key"], software[0][0]["key"]]),
                    "Recompute a configuration-matched triple whose children pass all implemented study checks")
                if store.enqueue(value, baseline, priority=0):
                    added += 1
                if added >= admission_budget:
                    return added
    return added


def feedback(row, value, result=None):
    summary = dict(key=row["key"], task=value, status=row["status"], error=row["error"])
    if result is not None:
        summary.update(study_pass=result["study_pass"], metrics=result.get("metrics"),
            failed_checks=failed_checks(result), checks=result.get("checks", {}),
            check_details=result.get("check_details", []),
            children=result.get("children", []),
            search_blocked=result.get("search_blocked"),
            counterexamples=result.get("counterexamples", [])[:3])
    return summary


def child_catalogue(store, baseline, *, limit=100):
    groups = children(store, baseline)
    buckets = defaultdict(list)
    for kind, entries in groups.items():
        for row, value, result in entries:
            context = value["parameters"].get("context_id", "Boolean-guard-policy")
            buckets[(kind, context)].append((row, value, result))
    for entries in buckets.values():
        entries.sort(key=lambda e: (not e[2]["study_pass"], len(failed_checks(e[2])), mass(e[2]), e[0]["key"]))
    selected = []
    maximum = max((len(v) for v in buckets.values()), default=0)
    for depth in range(maximum):
        for group in sorted(buckets):
            if depth >= len(buckets[group]):
                continue
            row, value, result = buckets[group][depth]
            assessment = result.get("assessment", {})
            selected.append(dict(key=row["key"], kind=value["kind"], status="completed",
                baseline_sha256=baseline, receipt_sha256=row["receipt_sha"],
                context_id=value["parameters"].get("context_id"),
                architecture_id=assessment.get("architecture_id", assessment.get("configuration_id")),
                study_pass=result["study_pass"], failed_checks=failed_checks(result),
                parameters=value["parameters"], metrics=result.get("metrics"),
                release_state=dict(core.FLAGS)))
            if len(selected) >= limit:
                return selected
    return selected


def historical_inputs(store, previous, baseline):
    """Nominate verified old recipes, never old result or integration receipts."""
    rows = list(store.db.execute("SELECT * FROM jobs WHERE baseline=? AND status='completed'", (previous,)))
    selected, closest = [], {}
    passing_architectures = set()
    for row in rows:
        value = json.loads(row["task"])
        if value["kind"].startswith("integration-"):
            continue
        result = store.result(row)
        if result["study_pass"]:
            selected.append((row, value, result))
            if value["kind"] == "mechanical-detail":
                passing_architectures.add(result["assessment"]["configuration_id"])
        elif value["kind"] in CHILD_KINDS:
            context = value["parameters"].get("context_id", "policy")
            group = value["kind"], context
            score = (len(failed_checks(result)), mass(result))
            if group not in closest or score < closest[group][0]:
                closest[group] = score, (row, value, result)
    selected.extend(v[1] for v in closest.values())
    selected.sort(key=lambda e: (
        not e[2]["study_pass"],
        e[1]["kind"] != "software-logic",
        e[1]["kind"] != "mechanical-detail",
        e[2].get("assessment", {}).get("architecture_id") not in passing_architectures,
        -mass(e[2]) if math.isfinite(mass(e[2])) else 0,
        e[0]["key"]))
    records = []
    for row, old, result in selected:
        value = tasks.task(old["kind"], old["parameters"],
            "Fresh evaluation of historical input " + row["key"] + "; no acceptance/result is reused", parent=row["key"])
        try:
            added = store.enqueue(value, baseline, priority=-20 if result["study_pass"] else 15)
        except ValueError as error:
            records.append(dict(previous_key=row["key"], rejected_input=str(error)))
            continue
        records.append(dict(key=tasks.identity(value, baseline), previous_key=row["key"],
            previous_baseline=previous, previous_receipt_sha256=row["receipt_sha"],
            input_values_only=True, acceptance_reused=False, newly_enqueued=added))
    return records

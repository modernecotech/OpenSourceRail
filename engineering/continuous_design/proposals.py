"""Bounded proposer context and keyset-paginated read-only history."""
import json
from pathlib import Path

from engineering.twin_workflow import core
from . import planning

MAX_REQUEST_BYTES = 128 * 1024
MAX_INPUT_BYTES = 512 * 1024
MAX_LOG_BYTES = 4 * 1024**2
MAX_RESPONSE_BYTES = 2 * 1024**2


def history(store, baseline, lane, *, after=0, limit=20):
    if type(after) is not int or after < 0 or type(limit) is not int or not 1 <= limit <= 50:
        raise ValueError("history requires a nonnegative cursor and limit 1..50")
    rows = list(store.db.execute("SELECT rowid AS cursor,* FROM jobs WHERE baseline=? AND lane=? AND rowid>? ORDER BY rowid LIMIT ?",
        (baseline, lane, after, limit + 1)))
    values = []
    for row in rows[:limit]:
        task = json.loads(row["task"])
        values.append(dict(cursor=row["cursor"], key=row["key"], kind=task["kind"],
            parameters=task["parameters"], status=row["status"]))
    return dict(items=values, next_cursor=values[-1]["cursor"] if len(rows) > limit else None,
        baseline_sha256=baseline, lane=lane, deduplication="Controller checks the complete ledger, not this sample")


def compact_feedback(summary):
    details = summary.get("check_details", [])
    summary["check_details"] = sorted(details, key=lambda d: d.get("state") != "fail")[:8]
    summary["check_detail_count"] = len(details)
    task = summary["task"]
    summary["task"] = {k: task[k] for k in ("kind", "parameters")}
    if summary.get("search_blocked"):
        summary["search_blocked"] = {k: summary["search_blocked"].get(k) for k in
            ("research_family_screen_incompatible", "required_decision", "limitation")}
    return summary


def representatives(store, baseline, lane, *, limit=24):
    # Include diverse contexts, then recent work, without reading full history.
    selected = {}
    for row in store.db.execute("SELECT j.key,j.task FROM jobs j JOIN (SELECT MIN(rowid) AS id FROM jobs WHERE baseline=? AND lane=? GROUP BY json_extract(task,'$.kind'),json_extract(task,'$.parameters.context_id')) g ON j.rowid=g.id", (baseline, lane)):
        selected[row["key"]] = dict(key=row["key"], **{k: json.loads(row["task"])[k] for k in ("kind", "parameters")})
    for row in store.db.execute("SELECT key,task FROM jobs WHERE baseline=? AND lane=? ORDER BY rowid DESC LIMIT ?", (baseline, lane, limit)):
        if len(selected) >= limit:
            break
        selected[row["key"]] = dict(key=row["key"], **{k: json.loads(row["task"])[k] for k in ("kind", "parameters")})
    return list(selected.values())[:limit]


def bounded(request):
    # Retain domains and explicit semantics; trim samples before refusing a call.
    for key in ("available_children", "feedback", "existing_designs", "package_scope"):
        while len(core.encoded(request)) > MAX_REQUEST_BYTES and len(request[key]) > 3:
            request[key].pop()
    if len(core.encoded(request)) > MAX_REQUEST_BYTES:
        raise ValueError("proposer request exceeds the 128 KiB input budget")
    return request


def budget_error(folder):
    folder = Path(folder)
    inputs = {"request.json", "prompt.txt", "schema.json", "command.json"}
    sizes = dict(input=0, log=0, response=0)
    for path in folder.rglob("*"):
        if not path.is_file():
            continue
        category = "input" if path.name in inputs else "response" if path.name == "response.json" else "log"
        sizes[category] += path.stat().st_size
    for category, limit in dict(input=MAX_INPUT_BYTES, log=MAX_LOG_BYTES, response=MAX_RESPONSE_BYTES).items():
        if sizes[category] > limit:
            return "proposer " + category + " budget exceeded"
    return None

"""Deterministic city operating packages. No Frappe or network dependency."""
from collections import defaultdict, deque
from copy import deepcopy
from datetime import date, timedelta
import re
from zoneinfo import ZoneInfo

from osr_erpnext.planning import digest, make_plan

CITY_SCHEMA = "osr-erpnext-city/1"
TASK_TYPES = {"manufacturing": "OSR Manufacturing", "maintenance": "OSR Maintenance Planning",
              "qa": "OSR Assurance Coordination", "procurement": "OSR Procurement Planning",
              "programme": "OSR Programme"}


def merge_config(base, override):
    """Tables merge recursively; explicit lists replace rather than append."""
    result = deepcopy(base)
    for key, value in override.items():
        if key not in base and key != "city":
            raise ValueError(f"Unknown configuration key: {key}")
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            result[key] = merge_config(base[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def validate_config(config):
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported city configuration version")
    if not isinstance(config.get("release"), str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,32}", config["release"]):
        raise ValueError("A short configuration release is required")
    city = config.get("city", {})
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", city.get("slug", "")):
        raise ValueError("A valid city slug is required")
    organisation = config["organisation"]
    for key in ["departments", "warehouses"]:
        values = organisation[key]
        if not isinstance(values, list) or len(values) != len(set(values)) or not values:
            raise ValueError(f"{key} must be a non-empty unique list")
        if any(not isinstance(v, str) or not v.strip() or len(v) > 60 for v in values):
            raise ValueError(f"Invalid {key} name")
    calendar = config["calendar"]
    weekdays = calendar["working_weekdays"]
    if not weekdays or len(weekdays) != len(set(weekdays)) or any(type(n) is not int or n not in range(7) for n in weekdays):
        raise ValueError("working_weekdays must be unique weekday numbers 0..6")
    for text in [calendar["start_date"], *calendar["holidays"]]:
        if text:
            date.fromisoformat(text)
    if calendar["timezone"]:
        ZoneInfo(calendar["timezone"])
    for kind in TASK_TYPES:
        if type(config["tasks"].get(kind)) is not bool:
            raise ValueError(f"tasks.{kind} must be boolean")
        if config["departments"][kind] not in organisation["departments"]:
            raise ValueError(f"Unknown department for {kind}")
    if config["departments"]["infrastructure_maintenance"] not in organisation["departments"]:
        raise ValueError("Unknown infrastructure maintenance department")
    ids = set()
    for task in config["programme"] + config.get("city_programme", []):
        if not re.fullmatch(r"[a-z0-9-]+", task["id"]) or task["id"] in ids:
            raise ValueError("Invalid or duplicate programme id")
        ids.add(task["id"])
        if task["department"] not in organisation["departments"]:
            raise ValueError("Unknown programme department")
        if not isinstance(task["title"], str) or not task["title"].strip():
            raise ValueError("Programme title required")
        offsets(task["start_day"], task["finish_day"])
    for task in config["programme"] + config.get("city_programme", []):
        if set(task.get("depends_on", [])) - ids:
            raise ValueError("Unknown programme dependency")


def offsets(start, finish):
    if type(start) is not int or type(finish) is not int or not -10000 <= start <= finish <= 10000:
        raise ValueError("Planning day offsets must be ordered integers within +/-10000")


def working_date(calendar, offset):
    if not calendar["start_date"]:
        return None
    day = date.fromisoformat(calendar["start_date"])
    holidays = {date.fromisoformat(d) for d in calendar["holidays"]}
    def working(d):
        return d.weekday() in calendar["working_weekdays"] and d not in holidays
    while not working(day):
        day += timedelta(days=1)
    direction = 1 if offset >= 0 else -1
    for _ in range(abs(offset)):
        day += timedelta(days=direction)
        while not working(day):
            day += timedelta(days=direction)
    return day.isoformat()


def record_id(record):
    return record["kind"] + ":" + record["uid"]


def ordered_records(records):
    """Validate the whole dependency graph and order predecessors first."""
    index = {record_id(r): r for r in records}
    if len(index) != len(records):
        raise ValueError("Duplicate task identity")
    successors = defaultdict(list)
    pending = {}
    for key, row in index.items():
        deps = row["depends_on"]
        if len(deps) != len(set(deps)) or set(deps) - index.keys():
            raise ValueError(f"Unresolved or duplicate dependencies for {key}")
        pending[key] = len(deps)
        for dep in deps:
            successors[dep].append(key)
    ready = deque(sorted(key for key, count in pending.items() if count == 0))
    result = []
    while ready:
        key = ready.popleft()
        result.append(index[key])
        for child in sorted(successors[key]):
            pending[child] -= 1
            if not pending[child]:
                ready.append(child)
    if len(result) != len(records):
        raise ValueError("Cyclic operating task dependencies")
    return result


def make_city_plan(bundle, config):
    validate_config(config)
    if config["city"]["slug"] != bundle["project_twin"]["city"]:
        raise ValueError("City profile does not match the operations bundle")
    plan = make_plan(bundle)
    records = [r for r in plan["records"] if config["tasks"][r["kind"]]]
    if config["tasks"]["qa"]:
        records += [dict(kind="qa", uid=r["qa_uid"], source=r) for r in bundle["qa_actions"]]
    if config["tasks"]["procurement"]:
        groups = defaultdict(list)
        for row in bundle["project_twin"].get("purchase_orders", []):
            groups[row["sourcing_route"]].append(row)
        for route, rows in sorted(groups.items()):
            records.append(dict(kind="procurement", uid=route, source=dict(
                work_order_title=f"Review {route} sourcing package ({len(rows)} requirements)",
                planned_start_day=min(r["order_by_day"] for r in rows),
                planned_finish_day=max(r["required_by_day"] for r in rows),
                requirements=rows, status="planning-not-issued")))
    if config["tasks"]["programme"]:
        records += [dict(kind="programme", uid=r["id"], source=r)
                    for r in config["programme"] + config.get("city_programme", [])]
    for row in records:
        source = row["source"]
        kind = row["kind"]
        row["depends_on"] = []
        start = source.get("planned_start_day")
        finish = source.get("planned_finish_day")
        if kind == "manufacturing":
            raw = source.get("schedule_predecessor_uids") or source.get("predecessor_uids", "")
            row["depends_on"] = ["manufacturing:" + s.strip() for s in re.split(r"[;,]", raw) if s.strip()]
        if kind == "programme":
            start, finish = source["start_day"], source["finish_day"]
            row["depends_on"] = ["programme:" + s for s in source.get("depends_on", [])]
        row["department"] = source["department"] if kind == "programme" else config["departments"][kind]
        if kind == "maintenance" and source.get("asset_type") != "rolling-stock":
            row["department"] = config["departments"]["infrastructure_maintenance"]
        row["task_type"] = TASK_TYPES[kind]
        row["priority"] = "High" if source.get("priority") == "safety" or kind == "qa" else "Medium"
        row["start_day"], row["finish_day"] = start, finish
        if start is not None or finish is not None:
            offsets(start, finish)
        row["start_date"] = working_date(config["calendar"], start) if start is not None else None
        row["finish_date"] = working_date(config["calendar"], finish) if finish is not None else None
    plan.update(schema=CITY_SCHEMA, config=deepcopy(config), config_sha256=digest(config),
                release=config["release"], records=ordered_records(records),
                source_scope=dict(meta=bundle.get("meta", {}), totals=bundle.get("totals", {})))
    plan["package_sha256"] = digest(plan)
    return plan


def validate_city_plan(plan):
    if plan.get("schema") != CITY_SCHEMA:
        raise ValueError("Unsupported city operating package")
    validate_config(plan["config"])
    if not re.fullmatch(r"[A-Za-z0-9-]{1,100}", plan.get("revision", "")) or not re.fullmatch(r"[a-f0-9]{64}", plan.get("source_sha256", "")):
        raise ValueError("Invalid source revision or checksum")
    if plan["city"] != plan["config"]["city"]["slug"] or plan["release"] != plan["config"]["release"]:
        raise ValueError("City/release mismatch")
    if plan["config_sha256"] != digest(plan["config"]):
        raise ValueError("Configuration checksum mismatch")
    body = {k: v for k, v in plan.items() if k != "package_sha256"}
    if plan["package_sha256"] != digest(body):
        raise ValueError("Operating package checksum mismatch")
    for row in plan["records"]:
        if not isinstance(row.get("uid"), str) or not row["uid"] or len(row["uid"]) > 500:
            raise ValueError("Invalid task identity")
        if row["source"].get("city", plan["city"]) != plan["city"]:
            raise ValueError("Mixed-city operating records")
        if row["kind"] not in TASK_TYPES or row["task_type"] != TASK_TYPES[row["kind"]]:
            raise ValueError("Unknown task kind")
        if row["department"] not in plan["config"]["organisation"]["departments"]:
            raise ValueError("Unknown task department")
        if row["priority"] not in {"Low", "Medium", "High", "Urgent"}:
            raise ValueError("Unknown task priority")
        if row["start_day"] is not None or row["finish_day"] is not None:
            offsets(row["start_day"], row["finish_day"])
        for actual, offset in [(row["start_date"], row["start_day"]), (row["finish_date"], row["finish_day"])]:
            if actual != (working_date(plan["config"]["calendar"], offset) if offset is not None else None):
                raise ValueError("Task dates differ from the configured calendar")
    ordered_records(plan["records"])

"""Pure planning contract shared by the CLI and the Frappe app."""
import hashlib
import json
import re

SCHEMA = "osr-erpnext-plan/1"
KINDS = {"manufacturing": ("manufacturing_tasks", "manufacturing_uid"),
         "maintenance": ("maintenance_tasks", "task_uid")}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def make_plan(bundle, kinds=None):
    city = bundle.get("project_twin", {}).get("city")
    revision = bundle.get("project_twin", {}).get("revision_id")
    if not isinstance(city, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", city):
        raise ValueError("Bundle must contain a valid project_twin.city")
    if not isinstance(revision, str) or not re.fullmatch(r"[A-Za-z0-9-]{1,100}", revision):
        raise ValueError("Bundle must contain project_twin.revision_id")
    records = []
    seen = set()
    for kind in kinds or KINDS:
        if kind not in KINDS:
            raise ValueError("Unknown planning kind")
        collection, id_field = KINDS[kind]
        for row in bundle.get(collection, []):
            uid = row.get(id_field)
            if not isinstance(uid, str) or not uid or len(uid) > 500:
                raise ValueError(f"Invalid {id_field}")
            if (kind, uid) in seen:
                raise ValueError(f"Duplicate source record: {uid}")
            seen.add((kind, uid))
            if row.get("city", city) != city:
                raise ValueError("Mixed-city bundle")
            records.append(dict(kind=kind, uid=uid, source=row))
    return dict(schema=SCHEMA, city=city, revision=revision,
                source_sha256=digest(bundle), records=records)


def source_key(company, plan, kind, uid):
    revision = plan["revision"]
    if plan.get("release", "1") != "1":
        revision += ":operating-" + plan["release"]
    return digest([company, plan["city"], revision, kind, uid])


def validate_plan(plan):
    if plan.get("schema") != SCHEMA:
        raise ValueError("Unsupported planning schema")
    # Reuse the bundle validator; no arbitrary DocTypes or document fields accepted.
    bundle = {"project_twin": {"city": plan.get("city"), "revision_id": plan.get("revision")},
              "manufacturing_tasks": [], "maintenance_tasks": []}
    for row in plan.get("records", []):
        if row.get("kind") not in KINDS:
            raise ValueError("Unknown planning kind")
        collection, id_field = KINDS[row["kind"]]
        if row.get("uid") != row.get("source", {}).get(id_field):
            raise ValueError("Source identity mismatch")
        bundle[collection].append(row["source"])
    make_plan(bundle)
    if not isinstance(plan.get("source_sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", plan["source_sha256"]):
        raise ValueError("Missing bundle SHA-256")

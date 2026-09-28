"""Validated governance, competence, quality-record and asset-identity templates."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from urllib.parse import urlsplit


SCHEMA = "osr-lifecycle-governance/1"
PACKAGE_SCHEMA = "osr-city-lifecycle-governance/1"
IDENTITY_SCHEMA = "osr-asset-identity/1"
LOOKUP_AUTHORITY = "lookup-only"

_ID = re.compile(r"[a-z0-9][a-z0-9.-]{0,79}")
_SOURCE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")
_CITY = re.compile(r"[a-z0-9][a-z0-9-]{0,79}")
_ASSET = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,159}")
_REVISION = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+-]{0,159}")


def _digest(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _unique(rows: list[dict], label: str, pattern: re.Pattern[str] = _ID) -> None:
    identifiers = [row.get("id") for row in rows]
    _require(all(isinstance(value, str) and pattern.fullmatch(value) for value in identifiers),
             f"Invalid {label} identity")
    _require(len(identifiers) == len(set(identifiers)), f"Duplicate {label} identity")


def _strings(value: object, label: str, *, minimum: int = 1) -> list[str]:
    _require(isinstance(value, list) and len(value) >= minimum, f"{label} must be a non-empty list")
    _require(all(isinstance(item, str) and item.strip() for item in value), f"Invalid {label}")
    _require(len(value) == len(set(value)), f"Duplicate {label}")
    return value


def validate_template(template: dict) -> dict:
    """Validate and return a defensive copy of the tracked policy template."""

    _require(isinstance(template, dict), "Lifecycle governance template must be an object")
    expected = {
        "schema", "authority_boundary", "sources", "role_templates",
        "record_templates", "management_cadence", "workflow_templates",
        "qr_identity", "subsystem_profiles",
    }
    _require(set(template) == expected and template.get("schema") == SCHEMA,
             "Invalid lifecycle governance schema or fields")
    _require(isinstance(template["authority_boundary"], str)
             and 40 <= len(template["authority_boundary"]) <= 1000,
             "Invalid lifecycle authority boundary")

    sources = template["sources"]
    _require(isinstance(sources, list) and len(sources) >= 6, "Insufficient source basis")
    _unique(sources, "source", _SOURCE_ID)
    for row in sources:
        _require(set(row) == {"id", "title", "organisation", "url", "applied_as", "limit"},
                 "Invalid source fields")
        parts = urlsplit(row["url"])
        _require(parts.scheme == "https" and bool(parts.netloc) and not parts.username,
                 "Source URLs must be public HTTPS URLs")
        for key in ("title", "organisation", "applied_as", "limit"):
            _require(isinstance(row[key], str) and row[key].strip(), f"Invalid source {key}")

    roles = template["role_templates"]
    _require(isinstance(roles, list) and len(roles) >= 8, "Insufficient role separation")
    _unique(roles, "role")
    role_ids = {row["id"] for row in roles}
    for row in roles:
        _require(set(row) == {"id", "purpose", "may_prepare", "may_not"},
                 "Invalid role fields")
        _require(isinstance(row["purpose"], str) and row["purpose"].strip(), "Invalid role purpose")
        _strings(row["may_prepare"], "role permissions")
        _strings(row["may_not"], "role prohibitions")

    records = template["record_templates"]
    _require(isinstance(records, list) and len(records) >= 8, "Insufficient record controls")
    _unique(records, "record")
    record_ids = {row["id"] for row in records}
    for row in records:
        _require(set(row) == {"id", "owner_role", "review_role", "native_records",
                              "required_fields", "authority_effect"},
                 "Invalid record-template fields")
        _require(row["owner_role"] in role_ids and row["review_role"] in role_ids,
                 "Record template references an unknown role")
        _strings(row["native_records"], "native records")
        _strings(row["required_fields"], "required record fields")
        _require(isinstance(row["authority_effect"], str) and row["authority_effect"].strip(),
                 "Invalid record authority effect")

    cadence = template["management_cadence"]
    _require(isinstance(cadence, list) and len(cadence) >= 4, "Incomplete management cadence")
    _unique(cadence, "cadence")
    for row in cadence:
        _require(set(row) == {"id", "maximum_interval_days", "inputs", "outputs"},
                 "Invalid cadence fields")
        _require(type(row["maximum_interval_days"]) is int
                 and 1 <= row["maximum_interval_days"] <= 366,
                 "Invalid management interval")
        _strings(row["inputs"], "cadence inputs")
        _strings(row["outputs"], "cadence outputs")

    workflows = template["workflow_templates"]
    _require(isinstance(workflows, list) and len(workflows) >= 5, "Incomplete workflows")
    _unique(workflows, "workflow")
    for row in workflows:
        _require(set(row) == {"id", "stages", "hold_points"}, "Invalid workflow fields")
        _strings(row["stages"], "workflow stages", minimum=3)
        _strings(row["hold_points"], "workflow hold points", minimum=2)

    qr = template["qr_identity"]
    _require(set(qr) == {"schema", "authority", "resolver_base", "resolver_path_template",
                         "printable_state", "required_fields", "forbidden_fields",
                         "optional_gs1_key", "offline_rule", "replacement_rule"},
             "Invalid QR identity fields")
    _require(qr["schema"] == IDENTITY_SCHEMA and qr["authority"] == LOOKUP_AUTHORITY,
             "QR identity must remain lookup-only")
    _require(qr["resolver_base"] is None,
             "Tracked template must not invent an operator resolver")
    _require(qr["resolver_path_template"] == "/id/osr/{city}/asset/{asset_id}",
             "Unexpected QR resolver path")
    _require(qr["printable_state"] == "blocked-until-operator-https-resolver-and-physical-binding",
             "Tracked QR labels must fail closed")
    required = set(_strings(qr["required_fields"], "QR required fields"))
    forbidden = set(_strings(qr["forbidden_fields"], "QR forbidden fields"))
    _require({"schema", "city", "asset_id", "engineering_revision", "resolver_path", "authority"} <= required,
             "QR identity omits mandatory traceability fields")
    _require({"credential", "token", "password", "command", "movement_authority", "approval"} <= forbidden,
             "QR identity does not prohibit sensitive or authoritative content")

    profiles = template["subsystem_profiles"]
    _require(set(profiles) == {"mechanical", "station", "civil", "rust"},
             "Subsystem profiles must cover mechanical, station, civil and Rust")
    for name, profile in profiles.items():
        _require(set(profile) == {"records", "release_evidence"}, f"Invalid {name} profile")
        _require(set(_strings(profile["records"], f"{name} records")) <= record_ids,
                 f"{name} profile references an unknown record")
        _strings(profile["release_evidence"], f"{name} release evidence")
    return deepcopy(template)


def validate_resolver_base(value: str) -> str:
    """Accept only an operator-supplied HTTPS origin without credentials or paths."""

    _require(isinstance(value, str) and len(value) <= 240, "Invalid resolver base")
    parts = urlsplit(value)
    _require(parts.scheme == "https" and bool(parts.netloc), "Resolver must be HTTPS")
    _require(not parts.username and not parts.password and not parts.query and not parts.fragment,
             "Resolver must not contain credentials, query or fragment")
    _require(parts.path in ("", "/"), "Resolver base must be an origin, not a path")
    return f"https://{parts.netloc}"


def identity_record(city: str, asset_id: str, revision: str) -> dict[str, str]:
    _require(isinstance(city, str) and bool(_CITY.fullmatch(city)), "Invalid city identity")
    _require(isinstance(asset_id, str) and bool(_ASSET.fullmatch(asset_id)), "Invalid asset identity")
    _require(isinstance(revision, str) and bool(_REVISION.fullmatch(revision)),
             "Invalid engineering revision")
    return {
        "schema": IDENTITY_SCHEMA,
        "city": city,
        "asset_id": asset_id,
        "engineering_revision": revision,
        "resolver_path": f"/id/osr/{city}/asset/{asset_id}",
        "authority": LOOKUP_AUTHORITY,
    }


def qr_payload(record: dict[str, str], resolver_base: str) -> str:
    """Build a printable payload only after deployment supplies a valid resolver."""

    expected = identity_record(record.get("city", ""), record.get("asset_id", ""),
                               record.get("engineering_revision", ""))
    _require(record == expected, "Identity record contains unknown or altered fields")
    return validate_resolver_base(resolver_base) + record["resolver_path"]


def make_city_package(
    template: dict,
    *,
    city: str,
    project: str,
    revision: str,
    asset_ids: list[str],
) -> dict:
    """Compile one deterministic, non-personal city governance package."""

    clean = validate_template(template)
    _require(isinstance(project, str) and 1 <= len(project) <= 160, "Invalid project identity")
    _require(isinstance(asset_ids, list) and asset_ids, "City asset register is empty")
    records = [identity_record(city, asset_id, revision) for asset_id in asset_ids]
    _require(len(records) == len({row["asset_id"] for row in records}), "Duplicate asset identity")
    identity_inventory = {
        "count": len(records),
        "sha256": _digest(records),
        "printable_labels": 0,
        "state": clean["qr_identity"]["printable_state"],
        "resolver_base": None,
        "optional_gs1_mapping": "unassigned",
    }
    package = {
        "schema": PACKAGE_SCHEMA,
        "city": city,
        "project": project,
        "engineering_revision": revision,
        "authority_boundary": clean["authority_boundary"],
        "role_template_count": len(clean["role_templates"]),
        "record_template_count": len(clean["record_templates"]),
        "workflow_template_count": len(clean["workflow_templates"]),
        "management_cadence_count": len(clean["management_cadence"]),
        "asset_identity_inventory": identity_inventory,
        "template_sha256": _digest(clean),
    }
    package["sha256"] = _digest(package)
    return package


def validate_city_package(package: dict) -> None:
    _require(isinstance(package, dict) and package.get("schema") == PACKAGE_SCHEMA,
             "Invalid city lifecycle package")
    _require(package.get("sha256") == _digest({k: v for k, v in package.items() if k != "sha256"}),
             "City lifecycle package checksum mismatch")
    inventory = package.get("asset_identity_inventory", {})
    _require(inventory.get("printable_labels") == 0 and inventory.get("resolver_base") is None,
             "Tracked city package must not claim deployed QR labels")
    _require(inventory.get("state") == "blocked-until-operator-https-resolver-and-physical-binding",
             "City QR state is not fail closed")

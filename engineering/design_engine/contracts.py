"""Versioned shared navigation, problem and evidence contracts.

Navigation identities carry no authentication, appointment or release authority.
Legacy domain payloads remain intact inside an explicit versioned crosswalk.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

SCHEMA = "osr-design-identity/1"
STATES = {
    "draft",
    "running",
    "numerically-verified",
    "physically-correlated",
    "independently-accepted",
    "passed",
    "failed",
    "stale",
    "unknown",
    "not-run",
    "outside-domain",
    "unavailable",
    "budget-exceeded",
    "cancelled",
}
UNITS = {
    "1",
    "ea",
    "m",
    "m2",
    "m3",
    "m/s",
    "m/s2",
    "kg",
    "kg/m3",
    "kg m2",
    "s",
    "rad",
    "N",
    "N m",
    "N/m",
    "N/m2",
    "Pa",
    "Hz",
    "J",
    "W",
    "V",
    "A",
    "Ah",
    "K",
    "degC",
    "kg/s",
    "kg CO2e",
    "USD",
    "IQD",
}


def canonical(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=False,
    ).encode()


def fingerprint(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON field: " + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("nonfinite JSON constant: " + value)

    return json.loads(
        Path(path).read_text(), object_pairs_hook=pairs, parse_constant=invalid
    )


def number(value, name, minimum=None, maximum=None):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("finite numeric " + name + " required")
    if (
        minimum is not None
        and value < minimum
        or maximum is not None
        and value > maximum
    ):
        raise ValueError(name + " outside its declared domain")
    return value


def identity(value):
    required = {
        "schema",
        "city",
        "project",
        "environment",
        "configuration_revision",
        "baseline_sha256",
        "run_id",
        "asset_id",
        "part_id",
    }
    if (
        not isinstance(value, dict)
        or set(value) != required
        or value["schema"] != SCHEMA
    ):
        raise ValueError("versioned scoped identity required")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value["city"]):
        raise ValueError("controlled city identity required")
    if value["environment"] not in {"simulation", "training", "physical"}:
        raise ValueError("explicit asset environment required")
    for key in ("project", "configuration_revision"):
        if not isinstance(value[key], str) or not 0 < len(value[key]) <= 160:
            raise ValueError("nonempty " + key + " required")
    for key in ("baseline_sha256", "run_id", "asset_id", "part_id"):
        if value[key] is not None and (
            not isinstance(value[key], str) or not 0 < len(value[key]) <= 160
        ):
            raise ValueError("invalid optional identity: " + key)
    if value["baseline_sha256"] is not None and not re.fullmatch(
        "[a-f0-9]{64}", value["baseline_sha256"]
    ):
        raise ValueError("exact baseline digest required")
    return value


def from_workbench(context, *, project):
    if context.get("schema_version") != 1:
        raise ValueError("unsupported Workbench context version")
    return identity(
        dict(
            schema=SCHEMA,
            city=context["city"],
            project=project,
            environment=context["environment"],
            configuration_revision=context.get("revision") or "unselected",
            baseline_sha256=context.get("baseline_sha256"),
            run_id=context.get("run_id"),
            asset_id=context.get("selected_asset"),
            part_id=context.get("selected_part"),
        )
    )


def quantity(value):
    if (
        set(value) != {"value", "unit", "state", "basis"}
        or value["unit"] not in UNITS
        or not value["basis"]
    ):
        raise ValueError("quantity requires controlled units, state and basis")
    if value["state"] not in {
        "nominal",
        "synthetic",
        "supplier",
        "measured",
        "unknown",
    }:
        raise ValueError("quantity provenance required")
    if value["value"] is None:
        if value["state"] != "unknown":
            raise ValueError("absent quantity must remain unknown")
    else:
        number(value["value"], "quantity")
        if value["state"] == "unknown":
            raise ValueError("unknown quantity cannot become an objective value")
    return value


def applicability(value):
    if set(value) != {
        "function",
        "environment",
        "model_domain",
        "loads",
        "interfaces",
        "service_life",
        "manufacturing",
        "mandatory_checks",
    }:
        raise ValueError("complete functional applicability charter required")
    for key in value:
        if not value[key]:
            raise ValueError("applicability cannot omit " + key)
    checks = value["mandatory_checks"]
    if not isinstance(checks, list) or len(checks) != len(set(checks)):
        raise ValueError("distinct mandatory checks required")
    for load in value["loads"]:
        if set(load) != {"id", "quantity"} or not load["id"]:
            raise ValueError("named governing load required")
        quantity(load["quantity"])
    return value


def checks_status(checks, mandatory):
    if not mandatory or set(checks) != set(mandatory):
        raise ValueError("exact independently declared verification coverage required")
    if any(
        row.get("state") not in STATES or not row.get("basis")
        for row in checks.values()
    ):
        raise ValueError("structured evidence state and basis required")
    states = {r["state"] for r in checks.values()}
    if states & {
        "failed",
        "outside-domain",
        "budget-exceeded",
        "cancelled",
        "unavailable",
    }:
        return "failed"
    if "stale" in states:
        return "stale"
    if "not-run" in states:
        return "not-run"
    if "unknown" in states:
        return "unknown"
    if "running" in states or "draft" in states:
        return "running"
    # A common experiment only establishes numerical screens. Acceptance is
    # recorded by the separate authenticated reviewer/decision workflow.
    return "numerically-verified"


def problem(value):
    required = {
        "schema",
        "id",
        "revision",
        "adapter",
        "applicability",
        "variables",
        "objectives",
        "budget",
        "scope",
    }
    if set(value) != required or value["schema"] != "osr-design-problem/1":
        raise ValueError("versioned problem charter required")
    if not value["id"] or not value["revision"] or not value["scope"]:
        raise ValueError("problem identity/revision/scope required")
    applicability(value["applicability"])
    if not isinstance(value["variables"], dict):
        raise ValueError("named variable domains required")
    for name, variable in value["variables"].items():
        if not name or variable.get("unit") not in UNITS:
            raise ValueError("variable units required")
        kind = variable.get("kind")
        if kind == "choice":
            choices = variable.get("choices", [])
            if not choices or len({fingerprint(c) for c in choices}) != len(choices):
                raise ValueError("distinct nonempty physical choices required")
        elif kind in {"real", "integer"}:
            low, high = variable["bounds"]
            number(low, name)
            number(high, name)
            if (
                low > high
                or kind == "integer"
                and (type(low) is not int or type(high) is not int)
            ):
                raise ValueError("ordered typed bounds required")
        else:
            raise ValueError("unsupported variable kind")
    if not value["objectives"] or len(value["objectives"]) != len(
        set(value["objectives"])
    ):
        raise ValueError("distinct named objectives required")
    budget = value["budget"]
    if set(budget) != {"evaluations", "wall_seconds", "memory_mib", "artifact_mib"}:
        raise ValueError("complete resource budget required")
    for key, maximum in [
        ("evaluations", 1024),
        ("wall_seconds", 14400),
        ("memory_mib", 16384),
        ("artifact_mib", 2048),
    ]:
        if type(budget[key]) is not int or not 1 <= budget[key] <= maximum:
            raise ValueError("bounded integer " + key + " required")
    canonical(value)
    return value


def variables(charter, values):
    if set(values) != set(charter["variables"]):
        raise ValueError("candidate must supply every declared variable exactly once")
    normalized = {}
    for name, value in values.items():
        spec = charter["variables"][name]
        if spec["kind"] == "choice":
            matches = [
                c
                for c in spec["choices"]
                if fingerprint(value) == fingerprint(c)
                or (
                    type(value) in (int, float)
                    and type(c) in (int, float)
                    and value == c
                )
            ]
            if not matches:
                raise ValueError("undeclared physical option: " + name)
            normalized[name] = matches[0]
        else:
            number(value, name, *spec["bounds"])
            if spec["kind"] == "integer" and type(value) is not int:
                raise ValueError("integer " + name + " required")
            normalized[name] = value
    return normalized


def comparable(left, right):
    # Equality is semantic and exact. A side bay cannot win against a roof by
    # silently changing its required area, loads, service life or interfaces.
    scopes = [
        {k: v for k, v in r["identity"].items() if k != "run_id"} for r in (left, right)
    ]
    if left["problem_sha256"] != right["problem_sha256"] or scopes[0] != scopes[1]:
        raise ValueError(
            "comparison needs the same functional problem and scoped identity"
        )
    return True


def problem_fingerprint(charter):
    """Budgets bound execution, rather than changing the required physical function."""
    return fingerprint(
        {key: value for key, value in charter.items() if key != "budget"}
    )


def legacy_crosswalk(payload, scope, *, domain, schema):
    identity(scope)
    if payload.get("schema") != schema:
        raise ValueError("unsupported legacy domain schema")
    return dict(
        schema="osr-domain-crosswalk/1",
        domain=domain,
        identity=scope,
        original_sha256=fingerprint(payload),
        original=payload,
        decisions_preserved=True,
    )

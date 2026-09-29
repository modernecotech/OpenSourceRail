#!/usr/bin/env python3
"""Validate and project the versioned OSR traction duty-cycle contract.

The contract is deliberately solver-neutral.  It carries the measured or
simulated observations once, with explicit units and provenance, then derives
bounded input rows for battery, site-power and traffic tools.  A planning or
simulated source is never promoted to acceptance evidence by conversion.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


SCHEMA = "org.opensourcerail.duty-cycle.v1"
SAMPLE_FIELDS = {
    "time_s",
    "speed_mps",
    "traction_kw",
    "auxiliary_kw",
    "charge_kw",
    "dc_voltage_v",
    "ambient_c",
    "passenger_load_fraction",
    "degraded_mode",
}
SOURCE_KINDS = {"planning", "simulated", "measured"}


class DutyCycleError(ValueError):
    """A duty-cycle document failed closed validation."""


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True) + "\n").encode()


def semantic_digest(document: dict[str, Any]) -> str:
    """Hash the validated semantic content, independent of JSON whitespace."""

    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DutyCycleError(f"cannot read duty cycle {path}: {error}") from error
    if not isinstance(value, dict):
        raise DutyCycleError("duty cycle root must be an object")
    validate(value)
    return value


def _finite_number(sample: dict[str, Any], field: str) -> float:
    value = sample.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DutyCycleError(f"sample {field} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise DutyCycleError(f"sample {field} must be finite")
    return value


def validate(document: dict[str, Any]) -> None:
    required = {
        "schema",
        "configuration_id",
        "source_kind",
        "source_evidence",
        "instrumentation",
        "units",
        "samples",
    }
    unknown = set(document) - required
    missing = required - set(document)
    if missing or unknown:
        raise DutyCycleError(f"document fields missing={sorted(missing)} unknown={sorted(unknown)}")
    if document["schema"] != SCHEMA:
        raise DutyCycleError(f"unsupported schema {document['schema']!r}")
    if not isinstance(document["configuration_id"], str) or not document["configuration_id"].strip():
        raise DutyCycleError("configuration_id must be a non-empty string")
    if document["source_kind"] not in SOURCE_KINDS:
        raise DutyCycleError("source_kind must be planning, simulated, or measured")
    for field in ("source_evidence", "instrumentation"):
        if not isinstance(document[field], str):
            raise DutyCycleError(f"{field} must be a string")
    if document["source_kind"] == "measured" and (
        not document["source_evidence"].strip() or not document["instrumentation"].strip()
    ):
        raise DutyCycleError("measured duty requires source evidence and instrumentation identity")
    expected_units = {
        "time": "s",
        "speed": "m/s",
        "power": "kW",
        "voltage": "V",
        "temperature": "degC",
        "passenger_load": "fraction",
    }
    if document["units"] != expected_units:
        raise DutyCycleError(f"units must be exactly {expected_units}")
    samples = document["samples"]
    if not isinstance(samples, list) or len(samples) < 2:
        raise DutyCycleError("samples must contain at least two rows")
    previous_time: float | None = None
    step: float | None = None
    for index, sample in enumerate(samples):
        if not isinstance(sample, dict) or set(sample) != SAMPLE_FIELDS:
            fields = set(sample) if isinstance(sample, dict) else set()
            raise DutyCycleError(
                f"sample {index} fields missing={sorted(SAMPLE_FIELDS-fields)} "
                f"unknown={sorted(fields-SAMPLE_FIELDS)}"
            )
        values = {field: _finite_number(sample, field) for field in SAMPLE_FIELDS - {"degraded_mode"}}
        if not isinstance(sample["degraded_mode"], bool):
            raise DutyCycleError(f"sample {index} degraded_mode must be boolean")
        if values["time_s"] < 0 or values["speed_mps"] < 0:
            raise DutyCycleError(f"sample {index} time and speed must be non-negative")
        if values["traction_kw"] < 0 or values["auxiliary_kw"] < 0 or values["charge_kw"] < 0:
            raise DutyCycleError(f"sample {index} power channels must be non-negative")
        if values["dc_voltage_v"] <= 0:
            raise DutyCycleError(f"sample {index} dc_voltage_v must be positive")
        if not 0.0 <= values["passenger_load_fraction"] <= 1.0:
            raise DutyCycleError(f"sample {index} passenger_load_fraction must be in [0,1]")
        if values["traction_kw"] > 0 and values["charge_kw"] > 0:
            raise DutyCycleError(f"sample {index} cannot charge and apply traction simultaneously")
        if previous_time is not None:
            delta = values["time_s"] - previous_time
            if delta <= 0:
                raise DutyCycleError("sample times must increase strictly")
            if step is None:
                step = delta
            elif not math.isclose(delta, step, rel_tol=0.0, abs_tol=1.0e-9):
                raise DutyCycleError("sample interval must be uniform")
        previous_time = values["time_s"]


def project(document: dict[str, Any]) -> dict[str, Any]:
    """Create semantically linked rows for the three adopted analysis families."""

    validate(document)
    battery: list[dict[str, float | bool]] = []
    grid: list[dict[str, float | bool]] = []
    traffic: list[dict[str, float | bool]] = []
    for sample in document["samples"]:
        battery_power_kw = sample["traction_kw"] + sample["auxiliary_kw"] - sample["charge_kw"]
        battery.append(
            {
                "time_s": float(sample["time_s"]),
                "battery_power_kw": float(battery_power_kw),
                "battery_current_a": float(battery_power_kw * 1000.0 / sample["dc_voltage_v"]),
                "ambient_c": float(sample["ambient_c"]),
                "degraded_mode": sample["degraded_mode"],
            }
        )
        grid.append(
            {
                "time_s": float(sample["time_s"]),
                "charger_demand_mw": float(sample["charge_kw"] / 1000.0),
                "degraded_mode": sample["degraded_mode"],
            }
        )
        traffic.append(
            {
                "time_s": float(sample["time_s"]),
                "speed_mps": float(sample["speed_mps"]),
                "passenger_load_fraction": float(sample["passenger_load_fraction"]),
                "degraded_mode": sample["degraded_mode"],
            }
        )
    digest = semantic_digest(document)
    return {
        "schema": "org.opensourcerail.duty-projections.v1",
        "configuration_id": document["configuration_id"],
        "source_kind": document["source_kind"],
        "acceptance_eligible": document["source_kind"] == "measured",
        "source_semantic_sha256": digest,
        "pybamm": battery,
        "pandapower": grid,
        "sumo": traffic,
    }


def verify_projection(document: dict[str, Any], projection: dict[str, Any]) -> None:
    """Reject adapter drift in identity, sample count, time, or conserved power."""

    expected = project(document)
    if projection != expected:
        raise DutyCycleError("derived solver inputs drifted from the canonical duty cycle")
    count = len(document["samples"])
    if any(len(projection[name]) != count for name in ("pybamm", "pandapower", "sumo")):
        raise DutyCycleError("derived solver input lost or duplicated samples")

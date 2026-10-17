"""Read-only, revision-bound observation replay; no live command or certification.

Recorded provenance is an unverified claim. Residual statistics do not establish
sensor calibration, physical validation, or adequate coverage of operating states.
"""
from __future__ import annotations

from datetime import datetime, timezone
from copy import deepcopy
import hashlib
import json
import math


def contract(reference):
    hvac = next(f["instance_id"] for f in reference["features"]
                if f["instance_id"].startswith("car-1/") and f["role"] == "replaceable-hvac-module")
    return dict(schema="osr-design-observation-contract/1",
        configuration_sha256=reference["review"]["configuration_sha256"],
        maximum_records=10000, observation_mode="read-only-no-control-output",
        required_fields=["id", "channel_id", "asset_id", "configuration_sha256", "timestamp",
            "value", "unit", "scenario_id", "sensor_id", "calibration_ref", "source_ref",
            "source_sha256", "evidence_kind"],
        channels=[
            dict(id="car-1.cabin-temperature", asset_id=hvac, unit="degC",
                 scenario_id="hvac-nominal-study-final",
                 model_value=reference["studies"]["hvac_nominal"]["final_temperature_c"],
                 model_time_s=reference["inputs"]["hvac"]["thermal_assumptions"]["duration_s"],
                 residual_limit=0.5, minimum_value=-60.0, maximum_value=120.0,
                 model_basis="Lumped cabin model, nominal study endpoint only; HVAC asset association is provisional"),
            dict(id="infra.static-gauge", asset_id="infra/rail-1", unit="m",
                 scenario_id="static-reference-gauge",
                 model_value=reference["infrastructure"]["measured_surrogate_gauge_m"],
                 residual_limit=0.002, minimum_value=0.5, maximum_value=3.0,
                 model_basis="Generated surrogate static gauge; no installed track survey or running-contact qualification")],
        limit_basis="Illustrative OSR replay thresholds, unaccepted; not engineering or sensor acceptance limits",
        field_evidence_policy="Supplier or sensor names and calibration references are recorded claims until independently authenticated",
        physical_validation=False, manufacturing_release=False, physical_release=False)


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _time(value):
    if not isinstance(value, str):
        raise ValueError("UTC observation timestamp required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("UTC observation timestamp required") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("UTC observation timestamp required")
    return parsed


def replay(observations, specification):
    if specification.get("schema") != "osr-design-observation-contract/1":
        raise ValueError("known observation contract required")
    if not isinstance(observations, list) or not 1 <= len(observations) <= specification["maximum_records"]:
        raise ValueError("nonempty bounded observation batch required")
    channels = {c["id"]: c for c in specification["channels"]}
    identities, last_time, series = set(), {}, {}
    for sample in observations:
        if not isinstance(sample, dict) or any(k not in sample for k in specification["required_fields"]):
            raise ValueError("incomplete observation record")
        for key in ("id", "sensor_id", "calibration_ref", "source_ref"):
            if not isinstance(sample[key], str) or not sample[key].strip():
                raise ValueError("explicit observation identity and provenance required")
        if sample["id"] in identities:
            raise ValueError("duplicate observation ID")
        identities.add(sample["id"])
        channel = channels.get(sample["channel_id"])
        if channel is None:
            raise ValueError("unknown telemetry channel")
        if sample["configuration_sha256"] != specification["configuration_sha256"]:
            raise ValueError("observation belongs to a different model revision")
        if sample["asset_id"] != channel["asset_id"] or sample["unit"] != channel["unit"]:
            raise ValueError("observation asset or unit mismatch")
        if sample["scenario_id"] != channel["scenario_id"]:
            raise ValueError("observation operating context differs from prediction")
        if "model_time_s" in channel and (not _number(sample.get("model_time_s"))
                or abs(sample["model_time_s"] - channel["model_time_s"]) > 1e-9):
            raise ValueError("observation model time differs from study endpoint")
        if sample["evidence_kind"] not in {"synthetic", "field-observation-unverified"}:
            raise ValueError("explicit synthetic or unverified field evidence required")
        sha = sample["source_sha256"]
        if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError("source SHA256 required; reference alone is insufficient")
        if not _number(sample["value"]) or not channel["minimum_value"] <= sample["value"] <= channel["maximum_value"]:
            raise ValueError("non-finite, boolean or out-of-domain observation")
        timestamp = _time(sample["timestamp"])
        identity = (sample["channel_id"], sample["sensor_id"])
        if identity in last_time and timestamp <= last_time[identity]:
            raise ValueError("observations must be strictly chronological per sensor/channel")
        last_time[identity] = timestamp
        residual = sample["value"] - channel["model_value"]
        retained = deepcopy(sample)
        retained.update(observation_id=sample["id"], residual=residual,
                        predicted_value=channel["model_value"])
        series.setdefault(sample["channel_id"], []).append(retained)
    results = []
    for identity, rows in sorted(series.items()):
        residuals = [r["residual"] for r in rows]
        limit = channels[identity]["residual_limit"]
        results.append(dict(channel_id=identity, count=len(rows), unit=channels[identity]["unit"],
            bias=sum(residuals) / len(rows), rmse=math.sqrt(sum(r*r for r in residuals) / len(rows)),
            maximum_abs_residual=max(map(abs, residuals)), provisional_residual_limit=limit,
            within_provisional_residual_limit=all(abs(r) <= limit for r in residuals),
            includes_synthetic=any(r["evidence_kind"] == "synthetic" for r in rows),
            residuals=rows))
    return dict(schema="osr-design-observation-replay/1",
        configuration_sha256=specification["configuration_sha256"],
        observations_sha256=hashlib.sha256(json.dumps(observations, sort_keys=True,
            separators=(",", ":"), allow_nan=False).encode()).hexdigest(),
        channels=results,
        unobserved_channels=sorted(set(channels) - set(series)),
        source_authenticity_verified=False, calibration_authenticated=False,
        physical_validation=False, physical_release=False,
        interpretation="Residuals against declared study endpoints only; no fitted calibration, authenticated field evidence or operating-envelope validation")

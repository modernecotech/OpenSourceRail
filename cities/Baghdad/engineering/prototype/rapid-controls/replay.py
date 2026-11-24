#!/usr/bin/env python3
"""Review a disconnected, revision-bound manufacturing trace."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOTYPE = HERE.parent
SOURCE_FILES = (
    "cam/cam-manifest.json",
    "cam/training/freecad-receipt.json",
    "cam/training/practice.nc",
    "vehicle-factory/installed-ga.json",
    "factory-routes.json",
)
# Synthetic limits in micrometres. They exercise measurement logic without
# assigning drawing acceptance criteria to either the coupon or the vehicle.
DEMO_LIMITS_UM = {"width": (2_850, 3_150), "depth": (850, 1_150)}
FRESHNESS_MS = 2_000
DEMO_CASES = (
    "nominal", "wrong-fixture", "stale-data", "disconnect", "reordered-data",
    "wrong-program", "failed-inspection", "marginal-inspection", "missing-inspection",
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_id(value: dict) -> str:
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def contract(root: Path = PROTOTYPE) -> dict:
    """Derive a training job from the exact existing CAM and factory artifacts."""
    blobs = {path: (root / path).read_bytes() for path in SOURCE_FILES}
    cam, receipt, _, ga, route = SOURCE_FILES
    c, r, g, f = (json.loads(blobs[path]) for path in (cam, receipt, ga, route))
    for key in ("candidate_id", "frame_revision", "opening_evaluation_id"):
        if c[key] != g[key] or c[key] != f[key]:
            raise ValueError(f"source manufacturing identity mismatch: {key}")
    if c["mechanical_evaluation_id"] != g["mechanical_evaluation_id"]:
        raise ValueError("source mechanical evaluation mismatch")
    nc_hash = sha(blobs["cam/training/practice.nc"])
    if (r["input_cam_evaluation_id"] != c["evaluation_id"]
            or r["practice"]["posted_nc_sha256"] != nc_hash
            or c["artifact_sha256"]["training/practice.nc"] != nc_hash):
        raise ValueError("practice program and native CAM receipt mismatch")
    job = {
        "mode": "disconnected-training",
        "candidate_id": c["candidate_id"],
        "drawing_revision": c["frame_revision"],
        "cam_evaluation_id": c["evaluation_id"],
        "route_evaluation_id": f["evaluation_id"],
        "fixture_id": "WAX-TRAINING-VISE",
        "fixture_revision": "SIM-1",
        "program_sha256": nc_hash,
        "post_sha256": r["grbl_post_sha256"],
        "machine_id": "CNC-SIM-01",
        "part_serial": "PRACTICE-WAX-0001",
        "material_batch": "PRACTICE-WAX-BATCH-01",
        "work_order": "TRAINING-WO-01",
        "operation_id": "PRACTICE-COUPON",
    }
    return {
        "schema": "osr-training-job/1",
        "job_id": canonical_id(job),
        "binding": job,
        "source_sha256": {path: sha(raw) for path, raw in blobs.items()},
        "inspection_limits_um": {name: list(bounds) for name, bounds in DEMO_LIMITS_UM.items()},
        "freshness_ms": FRESHNESS_MS,
    }


def demo(job: dict, case: str) -> dict:
    correct = job["binding"]
    first = dict(binding=correct, sequence=1, timestamp_ms=1_000, connected=True, state="setup")
    last = dict(binding=dict(correct), sequence=2, timestamp_ms=3_000, connected=True, state="complete")
    record = {
        "schema": "osr-training-trace/1",
        "job_id": job["job_id"],
        "review_timestamp_ms": 3_200,
        "samples": [first, last],
        "inspection": {
            "job_id": job["job_id"],
            "part_serial": correct["part_serial"],
            "timestamp_ms": 3_100,
            "inspector_id": "QA-SIM-01",
            "gauge_id": "GAUGE-SIM-01",
            "calibration_id": "CAL-SIM-01",
            "readings": {
                "width": {"value_um": 3_000, "uncertainty_um": 20},
                "depth": {"value_um": 1_000, "uncertainty_um": 20},
            },
        },
    }
    if case == "wrong-fixture":
        last["binding"]["fixture_revision"] = "SUPERSEDED-FIXTURE"
    elif case == "stale-data":
        record["review_timestamp_ms"] = 6_000
    elif case == "disconnect":
        last["connected"] = False
    elif case == "reordered-data":
        last["sequence"] = 1
    elif case == "wrong-program":
        last["binding"]["program_sha256"] = "0" * 64
    elif case == "failed-inspection":
        record["inspection"]["readings"]["depth"]["value_um"] = 1_300
    elif case == "marginal-inspection":
        record["inspection"]["readings"]["depth"]["value_um"] = 1_140
    elif case == "missing-inspection":
        record.pop("inspection")
    return record


def tick(value: object) -> bool:
    return type(value) is int and value >= 0


def telemetry_ok(job: dict, trace: dict) -> tuple[str | None, dict | None]:
    if trace.get("schema") != "osr-training-trace/1" or trace.get("job_id") != job["job_id"]:
        return "training job identity mismatch", None
    now, samples = trace.get("review_timestamp_ms"), trace.get("samples")
    if not tick(now) or not isinstance(samples, list) or len(samples) < 2:
        return "insufficient timed samples", None
    expected = job["binding"]
    prior_time = -1
    for sequence, sample in enumerate(samples, 1):
        if not isinstance(sample, dict):
            return "invalid sample", None
        if not tick(sample.get("sequence")) or sample["sequence"] != sequence:
            return "sample sequence gap or replay", None
        timestamp = sample.get("timestamp_ms")
        if not tick(timestamp) or not prior_time < timestamp <= now:
            return "sample timestamp is unordered or in the future", None
        binding = sample.get("binding")
        if not isinstance(binding, dict):
            return "missing sample job binding", None
        for key, value in expected.items():
            if binding.get(key) != value:
                return f"sample does not match {key}", None
        if binding.keys() != expected.keys():
            return "unexpected sample binding fields", None
        if sample.get("connected") is not True:
            return "machine connection lost", None
        required_state = "setup" if sequence == 1 else "complete" if sequence == len(samples) else "working"
        if sample.get("state") != required_state:
            return "invalid machining state sequence", None
        if prior_time >= 0 and timestamp - prior_time > job["freshness_ms"]:
            return "machine sample stream has a freshness gap", None
        prior_time = timestamp
    if now - prior_time > job["freshness_ms"]:
        return "latest machine sample is stale", None
    return None, samples[-1]


def inspection_disposition(job: dict, trace: dict, last: dict) -> tuple[str, str]:
    record = trace.get("inspection")
    if not isinstance(record, dict):
        return "held", "inspection record missing"
    if (record.get("job_id") != job["job_id"]
            or record.get("part_serial") != job["binding"]["part_serial"]):
        return "held", "inspection belongs to another job or part"
    timestamp = record.get("timestamp_ms")
    if not tick(timestamp) or not last["timestamp_ms"] <= timestamp <= trace["review_timestamp_ms"]:
        return "held", "inspection must follow completed machining and precede review"
    if any(not isinstance(record.get(key), str) or not record[key].strip()
           for key in ("inspector_id", "gauge_id", "calibration_id")):
        return "held", "missing inspector, gauge or calibration identity"
    readings = record.get("readings")
    if not isinstance(readings, dict) or readings.keys() != job["inspection_limits_um"].keys():
        return "held", "inspection readings incomplete or unexpected"
    ambiguous = []
    failures = []
    for name, (low, high) in job["inspection_limits_um"].items():
        reading = readings[name]
        if not isinstance(reading, dict) or any(not tick(reading.get(key))
                                                 for key in ("value_um", "uncertainty_um")):
            return "held", "inspection requires value and uncertainty in integer micrometres"
        value, uncertainty = reading["value_um"], reading["uncertainty_um"]
        lower, upper = value - uncertainty, value + uncertainty
        if upper < low or lower > high:
            failures.append(name)
        elif lower < low or upper > high:
            ambiguous.append(name)
    if failures:
        return "rework-review", "measurement outside synthetic limits: " + ", ".join(failures)
    if ambiguous:
        return "held", "measurement uncertainty overlaps synthetic limit: " + ", ".join(ambiguous)
    return "training-review-ready", "synthetic job, sample sequence and inspection evidence match"


def review(job: dict, trace: dict) -> dict:
    reason, last = telemetry_ok(job, trace)
    status, reason = ("held", reason) if reason else inspection_disposition(job, trace, last)
    return {
        "schema": "osr-training-review/1",
        "job_id": job["job_id"],
        "candidate_id": job["binding"]["candidate_id"],
        "part_serial": job["binding"]["part_serial"],
        "cam_evaluation_id": job["binding"]["cam_evaluation_id"],
        "trace_id": canonical_id(trace),
        "state": status,
        "reason": reason,
        "equipment_start_permission": False,
        "fabrication_release": False,
    }


def demo_report() -> dict:
    job = contract()
    return {
        "evaluator_sha256": sha(Path(__file__).read_bytes()),
        "job": job,
        "cases": {case: review(job, demo(job, case)) for case in DEMO_CASES},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--case", choices=DEMO_CASES, help="replay one built-in training trace")
    mode.add_argument("--trace", type=Path, help="review a local training trace JSON")
    mode.add_argument("--check", action="store_true", help="check the tracked example receipt")
    args = parser.parse_args()
    try:
        if args.trace:
            with args.trace.open("rb") as stream:
                raw = stream.read(1_048_577)
            if len(raw) > 1_048_576:
                raise ValueError("training trace exceeds one MiB")
            trace = json.loads(raw)
            if not isinstance(trace, dict):
                raise ValueError("training trace must be an object")
            result = review(contract(), trace)
        elif args.case:
            job = contract()
            trace = demo(job, args.case)
            result = {"job": job, "trace": trace, "review": review(job, trace)}
        else:
            result = demo_report()
        encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.check:
            if (HERE / "example-review.json").read_text() != encoded:
                raise ValueError("tracked training receipt is stale")
            print("Manufacturing handoff replay matches tracked receipt")
        else:
            print(encoded, end="")
    except (KeyError, OSError, TypeError, ValueError) as error:
        parser.exit(2, f"Training replay: {error}\n")


if __name__ == "__main__":
    main()

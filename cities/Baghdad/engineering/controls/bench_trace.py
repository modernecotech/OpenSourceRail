"""Offline screen of independently recorded signals on the Baghdad handover rig."""
import argparse
from bisect import bisect_right
from datetime import timedelta
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))

from engineering.railway_completion.evidence import _attest, number, parse, read_owned, timestamp

CHANNELS = {"door_locked": "bit", "parking_applied": "bit", "hold_force": "kN",
            "inverter_inhibited": "bit", "traction_effort": "kN", "wheel_position": "mm",
            "dispatch_request": "bit", "release_request": "bit"}
LIMITS = ("maximum_sample_gap_ms", "maximum_clock_error_ms", "minimum_hold_kn",
          "released_hold_max_kn", "maximum_inhibited_effort_kn", "minimum_start_effort_kn",
          "maximum_rollback_mm", "maximum_stationary_travel_mm", "dispatch_to_effort_ms")


def binding(opening=None):
    system = (HERE.parents[1] / "system-results.json").read_bytes()
    parent = parse(system)["networks"]["first"]
    sources = [HERE / name for name in ("Cargo.toml", "Cargo.lock", "src/boarding.rs", "src/main.rs")]
    for crate in ("osr-atp", "osr-door-control", "osr-tcms"):
        package = ROOT / "crates" / crate
        sources.extend([package / "Cargo.toml", *sorted((package / "src").rglob("*.rs"))])
    basis = {"selected_candidate": parent["selected_candidate_id"],
            "network_evaluation": parent["selected_evaluation_id"],
            "control_source_sha256": {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in sources}}
    if opening is not None:
        from engineering.outline.baghdad_system import _id

        raw = opening.read_bytes()
        case = parse(raw)
        bundle, power = case["bundle"], case["power"]
        fleet = bundle["active_sets"] + bundle["spares"]
        if (case["parent"] != basis["selected_candidate"] or bundle["parent"] != case["parent"]
                or case["sources"]["cities/Baghdad/system-results.json"] != sha256(system).hexdigest()
                or bundle["service_group"] != "Airport" or bundle["formation_cars"] != 6
                or bundle["supply"] != "protected_conductor" or power["option"] != bundle["supply"]
                or power["parent_candidate_id"] != case["candidate_id"] or _id(bundle) != case["candidate_id"]
                or fleet <= 0 or fleet != power["common_service"]["fleet_trainsets"]
                or case["controls"]["door_controllers"] != 48 * fleet
                or case["controls"]["brake_controllers"] != 12 * fleet):
            raise ValueError("Airport bench return requires the matching opening, train and controller inventory")
        basis.update(opening_candidate=case["candidate_id"], opening_evaluation=case["evaluation_id"],
                     opening_sha256=sha256(raw).hexdigest())
    return basis


def templates(opening=None):
    basis = binding(opening)
    return {
        "manifest": {"schema": "osr-baghdad-bench-handover/1", "binding": basis,
                     "provenance": None, "started_at": None, "article_serial": None, "trial_id": None,
                     "as_tested_build": None, "wiring_revision": None,
                     "direction_sign": None, "clock_error_ms": None,
                     "files": {k: {"path": k + ".json", "sha256": None}
                               for k in ("raw", "limits", "witness", "calibration")},
                     "attestations": {}},
        "raw": {"binding": basis, "article_serial": None, "trial_id": None, "channels": {
            k: {"unit": unit, "input_id": None, "samples": []} for k, unit in CHANNELS.items()}},
        "limits": {"binding": basis, "procedure_revision": None, "approved_at": None,
                   "thresholds": {k: None for k in LIMITS}},
        "calibration": {"trial_id": None, "clock_alignment_method": None, "maximum_clock_error_ms": None,
                        "valid_until": None, "channels": {k: {"input_id": None, "certificate": None}
                        for k in CHANNELS}},
        "witness": {"trial_id": None, "article_serial": None, "observer": None,
                    "load_and_gradient": None, "observations": None},
    }


def require_text(obj, keys):
    for key in keys:
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            raise ValueError(f"Missing {key}")


def signals(raw):
    records = raw["channels"]
    if not isinstance(records, dict) or records.keys() != CHANNELS.keys():
        raise ValueError("Record every named command, contact and transducer")
    channels, inputs = {}, set()
    for name, unit in CHANNELS.items():
        channel = records[name]
        require_text(channel, ["input_id"])
        if channel["unit"] != unit or channel["input_id"] in inputs:
            raise ValueError("Require unique recorder inputs and the specified physical units")
        inputs.add(channel["input_id"])
        data = channel["samples"]
        if not isinstance(data, list) or not 2 <= len(data) <= 250000:
            raise ValueError(f"Require a bounded series for {name}")
        times, values = [], []
        for pair in data:
            if not isinstance(pair, list) or len(pair) != 2:
                raise ValueError(f"Expected [time_ms, value] on {name}")
            t = number(pair[0], "sample time", nonnegative=True)
            v = number(pair[1], name)
            if (times and t <= times[-1]) or (unit == "bit" and v not in (0, 1)):
                raise ValueError(f"Bad time order or digital value on {name}")
            times.append(t)
            values.append(v)
        channels[name] = (times, values)
    return channels


def screen(raw, limits, direction, clock_error):
    channels = signals(raw)
    if limits.keys() != set(LIMITS):
        raise ValueError("Return the complete approved limit set")
    s = {k: number(limits[k], k, nonnegative=True) for k in LIMITS}
    if (s["minimum_hold_kn"] <= s["released_hold_max_kn"]
            or s["minimum_start_effort_kn"] <= s["maximum_inhibited_effort_kn"]
            or min(s["maximum_sample_gap_ms"], s["dispatch_to_effort_ms"]) <= 0):
        raise ValueError("Indistinct force bands or nonpositive time budgets")
    if type(direction) is not int or direction not in (-1, 1):
        raise ValueError("Specify departure direction relative to both force and displacement channels")
    clock_error = number(clock_error, "recorder clock error", nonnegative=True)
    holds, faults, events = set(), set(), {}
    if clock_error > s["maximum_clock_error_ms"]:
        holds.add("Clock alignment exceeds the limit")
    gaps = {k: max(b-a for a, b in zip(t, t[1:])) for k, (t, _) in channels.items()}
    if any(gap > s["maximum_sample_gap_ms"] for gap in gaps.values()):
        holds.add("Recorder interval exceeds the limit")
    start = max(t[0] for t, _ in channels.values())
    end = min(t[-1] for t, _ in channels.values())
    if start >= end:
        raise ValueError("Recorder streams have no common time window")
    timeline = sorted({time for t, _ in channels.values() for time in t if start <= time <= end})
    origin = peak = None
    max_rollback = 0.0
    max_berth_displacement = 0.0
    first_release = False
    for t in timeline:
        v = {name: vals[bisect_right(ts, t)-1] for name, (ts, vals) in channels.items()}
        held = v["hold_force"] >= s["minimum_hold_kn"]
        released = v["hold_force"] <= s["released_hold_max_kn"] and not v["parking_applied"]
        effort = direction * v["traction_effort"] >= s["minimum_start_effort_kn"]
        position = direction * v["wheel_position"]
        if origin is None:
            origin = peak = position
            if not (held and v["parking_applied"] and v["door_locked"] and v["inverter_inhibited"]
                    and not v["dispatch_request"] and not v["release_request"]):
                holds.add("Initial secured and locked berth absent")
        peak = max(peak, position)
        max_rollback = max(max_rollback, peak-position)
        if v["inverter_inhibited"] and abs(v["traction_effort"]) > s["maximum_inhibited_effort_kn"]:
            faults.add("Effort measured while inverter inhibited")
        if not v["door_locked"]:
            if "relock" in events:
                faults.add("Door lock lost after relocking")
            events.setdefault("unlock", t)
            if not (held and v["parking_applied"] and v["inverter_inhibited"]) or v["dispatch_request"]:
                faults.add("Unlocked without retained brakes and traction inhibition")
        elif "unlock" in events:
            events.setdefault("relock", t)
        if v["dispatch_request"]:
            events.setdefault("dispatch", t)
            if "relock" not in events:
                faults.add("Dispatch before relock")
        if not v["inverter_inhibited"] and "dispatch" not in events:
            faults.add("Inverter inhibit withdrawn before dispatch")
        if effort and not v["inverter_inhibited"]:
            events.setdefault("effort", t)
            if "dispatch" not in events:
                faults.add("Starting effort before dispatch")
        if v["release_request"]:
            events.setdefault("release_request", t)
            if not effort or v["inverter_inhibited"] or not v["door_locked"]:
                faults.add("Brake release requested without locks and directed effort")
        if not held or not v["parking_applied"]:
            if not first_release:
                events["hold_break"] = t
                first_release = True
            if "release_request" not in events:
                faults.add("Physical hold fell before release request")
        if released:
            events.setdefault("released", t)
        handover = "release_request" in events and "motion" not in events
        if handover and (not effort or v["inverter_inhibited"]):
            faults.add("Starting effort lost through brake handover")
        if handover and not v["door_locked"]:
            faults.add("Door unlocked through brake handover")
        if "motion" not in events:
            departure_permitted = (released and v["door_locked"] and "dispatch" in events
                                   and "release_request" in events and effort and not v["inverter_inhibited"])
            travel = position - origin
            if not departure_permitted:
                max_berth_displacement = max(max_berth_displacement, abs(travel))
                if abs(travel) > s["maximum_stationary_travel_mm"]:
                    faults.add("Displacement from secured berth exceeds the stationary limit")
            elif travel > s["maximum_stationary_travel_mm"]:
                events["motion"] = t
    if max_rollback > s["maximum_rollback_mm"]:
        faults.add("Rollback exceeds the limit")
    order = ("unlock", "relock", "dispatch", "effort", "release_request", "hold_break", "released", "motion")
    for name in order:
        if name not in events:
            holds.add(f"Missing observed milestone: {name}")
    # For events on separate inputs the actual transition can lead its first
    # observed sample by a sample interval, in addition to relative clock error.
    uncertainty = max(gaps.values()) + 2 * clock_error
    for earlier, later in zip(order, order[1:]):
        if earlier in events and later in events and later != "released":
            if events[later] < events[earlier]:
                faults.add(f"{later} occurred before {earlier}")
            elif events[later] - events[earlier] <= uncertainty:
                holds.add(f"Sampling cannot resolve {earlier} before {later}")
    latency = None
    if "dispatch" in events:
        latency = events.get("effort", end) - events["dispatch"]
        if latency - uncertainty > s["dispatch_to_effort_ms"]:
            faults.add("Dispatch-to-effort time exceeds the limit")
        elif latency + uncertainty > s["dispatch_to_effort_ms"]:
            holds.add("Dispatch-to-effort uncertainty crosses the limit")
    return {"holds": sorted(holds), "observed_faults": sorted(faults), "events_ms": events,
            "maximum_rollback_mm": max_rollback, "maximum_held_berth_displacement_mm": max_berth_displacement, "channel_maximum_gap_ms": gaps,
            "event_time_uncertainty_ms": uncertainty, "dispatch_to_effort_observed_ms": latency}


def assess(root, manifest, *, authenticator=None, opening=None):
    if manifest["schema"] != "osr-baghdad-bench-handover/1" or manifest["binding"] != binding(opening):
        raise ValueError("Bench return differs from the selected Baghdad candidate or controls revision")
    if manifest["provenance"] not in ("synthetic-fixture", "physical-measurement"):
        raise ValueError("Classify source as physical-measurement or synthetic-fixture")
    require_text(manifest, ("trial_id", "article_serial", "as_tested_build", "wiring_revision"))
    if len(manifest["as_tested_build"]) != 64 or any(c not in "0123456789abcdef" for c in manifest["as_tested_build"]):
        raise ValueError("Record the SHA256 of the as-tested build")
    files = manifest["files"]
    if set(files) != {"raw", "limits", "witness", "calibration"}:
        raise ValueError("Raw measurements, limits, witness and calibration files are required")
    source = {k: read_owned(root, ref) for k, ref in files.items()}
    raw, limits, witness = (parse(source[k]) for k in ("raw", "limits", "witness"))
    if any(doc["binding"] != manifest["binding"] for doc in (raw, limits)):
        raise ValueError("Raw samples or limits identify a different candidate")
    calibration = parse(source["calibration"])
    if any(doc["trial_id"] != manifest["trial_id"] for doc in (raw, calibration, witness)):
        raise ValueError("Witness, measurements and calibration must identify the trial")
    require_text(calibration, ["clock_alignment_method"])
    if calibration["maximum_clock_error_ms"] != manifest["clock_error_ms"]:
        raise ValueError("Clock-error budget differs from recorder calibration")
    if calibration["channels"].keys() != CHANNELS.keys():
        raise ValueError("Every channel needs a calibration reference")
    for name, cert in calibration["channels"].items():
        require_text(cert, ("input_id", "certificate"))
        if cert["input_id"] != raw["channels"][name]["input_id"]:
            raise ValueError("Calibration identifies another recorder input")
    if any(doc["article_serial"] != manifest["article_serial"] for doc in (raw, witness)):
        raise ValueError("Instrumented article differs from the witness or manifest")
    require_text(limits, ["procedure_revision"])
    require_text(witness, ["trial_id", "observer", "load_and_gradient", "observations"])
    result = screen(raw, limits["thresholds"], manifest["direction_sign"], manifest["clock_error_ms"])
    holds = set(result["holds"])
    started = timestamp(manifest["started_at"])
    end = started + timedelta(milliseconds=max(row["samples"][-1][0] for row in raw["channels"].values()))
    if timestamp(calibration["valid_until"]) < end:
        holds.add("Calibration expires before trace ends")
    if timestamp(limits["approved_at"]) > started:
        holds.add("Recorded limits postdate the trial")
    claim = {k: v for k, v in manifest.items() if k != "attestations"}
    attest = manifest.get("attestations", {})
    claims = {"record-producer": claim, "independent-reviewer": claim,
              "limit-approver": limits, "calibration-authority": calibration}
    verified = {role: _attest(attest.get(role), payload, role, authenticator)
                for role, payload in claims.items()}
    if not all(verified.values()):
        holds.add("Outstanding externally verified signatures for " + ", ".join(k for k,v in verified.items() if not v))
    if verified["record-producer"] and verified["independent-reviewer"]:
        if attest["record-producer"]["subject_id"] == attest["independent-reviewer"]["subject_id"]:
            holds.add("Reviewer must be independent of producer")
    if manifest["provenance"] == "synthetic-fixture":
        holds.add("Synthetic fixture provides software evidence only")
    return dict(result, holds=sorted(holds), binding=manifest["binding"], raw_sha256=files["raw"]["sha256"],
                provenance=manifest["provenance"], authenticated_roles=verified,
                disposition="fault observed" if result["observed_faults"] else "held" if holds else "ready for qualification review",
                physical_accepted=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--template", choices=("manifest", "raw", "limits", "calibration", "witness"))
    mode.add_argument("--manifest", type=Path)
    parser.add_argument("--opening", type=Path, help="Bind both template and return to the same opening.json")
    args = parser.parse_args()
    try:
        if args.template:
            print(json.dumps(templates(args.opening)[args.template], indent=2))
            return 0
        if args.manifest.stat().st_size > 65536:
            raise ValueError("Manifest exceeds 64 KiB")
        result = assess(args.manifest.parent, parse(args.manifest.read_bytes()), opening=args.opening)
    except (ValueError, KeyError, TypeError, AttributeError, OverflowError, OSError) as exc:
        result = {"disposition": "held", "intake_error": str(exc), "physical_accepted": False}
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["disposition"] == "ready for qualification review" else 2


if __name__ == "__main__":
    raise SystemExit(main())

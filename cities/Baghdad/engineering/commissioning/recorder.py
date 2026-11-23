"""Import a logger CSV and replay an Airport station handover or injected fault."""

import argparse
import csv
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path

from cities.Baghdad.engineering.controls import bench_trace
from engineering.outline.baghdad_system import _id
from engineering.railway_completion.evidence import number, parse, read_owned

BASE = {
    "stimulus": "bit",
    "drive_inhibited": "bit",
    "traction_effort": "kN",
    "dispatch": "bit",
    "parking_contact": "bit",
    "holding_force": "kN",
    "position": "mm",
    "opposite_door_open": "bit",
    "exit_open": "bit",
    "independent_brake_request": "bit",
}
FAULTS = {
    "brake_feedback_loss": {"brake_feedback_ok": "bit"},
    "wrong_side_request": {"wrong_side_command": "bit"},
    "stale_command": {"command_age": "ms"},
    "power_restart": {"supply_healthy": "bit", "boot_epoch": "integer", "reset_key": "bit"},
    "evacuation_blocked": {"egress_authorised": "bit"},
    "evacuation_authorised": {"egress_authorised": "bit"},
}
LIMITS = (
    "clock_error_ms",
    "maximum_gap_ms",
    "response_deadline_ms",
    "minimum_hold_observation_ms",
    "maximum_effort_kn",
    "minimum_holding_force_kn",
    "maximum_displacement_mm",
)
MAX_CSV = 4 * 1024 * 1024


SCHEMA = "baghdad-station-logger/2"
LEGACY_SCHEMA = "baghdad-station-logger/1"
VISIT = ("station_id", "train_id", "arrival_id", "controller_boot_id", "recorder_serial")
EVACUATION = ("evacuation_blocked", "evacuation_authorised")


def template(opening_path, mode, *, schema=SCHEMA):
    channels = bench_trace.CHANNELS if mode == "handover" else {**BASE, **FAULTS[mode]}
    if schema not in (SCHEMA, LEGACY_SCHEMA):
        raise ValueError("Unknown station logger schema")
    if schema == SCHEMA and mode != "handover":
        channels = dict(channels, emergency_brake_output="bit")
        if mode == "stale_command":
            channels.update(command_received="bit", command_sent_ms="ms")
        if mode in EVACUATION:
            channels.update(local_handle="bit", other_same_side_exit_open="bit")
    limits = list(LIMITS)
    if mode == "stale_command":
        limits.append("maximum_command_age_ms")
    form = {
        "schema": schema,
        "binding": bench_trace.binding(opening_path),
        "mode": mode,
        "trial_id": None,
        "article_serial": None,
        "raw_csv_sha256": None,
        "record_kind": None,
        "wiring_revision": None,
        "as_tested_build_sha256": None,
        "inputs": {name: {"input_id": None, "unit": unit} for name, unit in channels.items()},
    }
    if schema == SCHEMA:
        form["visit"] = dict.fromkeys((*VISIT, "direction_sign", "platform_side", "physical_door_slot"))
        for entry in form["inputs"].values():
            entry.update(device_serial=None, device_terminal=None)
    if mode != "handover":
        form.update(
            limits=dict.fromkeys(limits),
            limit_document_revision=None,
            stimulus_record_sha256=None,
            witness_record_sha256=None,
        )
    return form


def _digest(text):
    return isinstance(text, str) and len(text) == 64 and all(c in "0123456789abcdef" for c in text)


def _rows(form, expected, data):
    if len(data) > MAX_CSV or sha256(data).hexdigest() != form["raw_csv_sha256"]:
        raise ValueError("Require exact logger bytes up to 4 MiB")
    if set(form) != set(expected) or any(form[k] != expected[k] for k in ("schema", "binding", "mode")):
        raise ValueError("Capture form differs from the opening or logger procedure")
    if form["record_kind"] not in ("physical-measurement", "synthetic-fixture") or not _digest(
        form["as_tested_build_sha256"]
    ):
        raise ValueError("Identify the recording source kind and as-tested firmware hash")
    bench_trace.require_text(form, ("trial_id", "article_serial", "wiring_revision"))
    if set(form["inputs"]) != set(expected["inputs"]):
        raise ValueError("Capture all required channels")
    current = form["schema"] == SCHEMA
    if current:
        visit = form["visit"]
        if not isinstance(visit, dict) or set(visit) != set(expected["visit"]):
            raise ValueError("Identify the bound station visit and recorder")
        bench_trace.require_text(visit, VISIT)
        slot, side, direction = visit["physical_door_slot"], visit["platform_side"], visit["direction_sign"]
        if (
            type(slot) is not int
            or not 0 <= slot < 48
            or side not in ("left", "right")
            or ("left", "right")[(slot // 4) % 2] != side
            or type(direction) is not int
            or direction not in (-1, 1)
        ):
            raise ValueError("Require the installed platform-side door slot and signed direction")
    pin_to_key = {}
    terminals = set()
    for key, entry in form["inputs"].items():
        bench_trace.require_text(entry, ["input_id"])
        pin = entry["input_id"]
        if current:
            bench_trace.require_text(entry, ("device_serial", "device_terminal"))
            terminal = (entry["device_serial"].strip(), entry["device_terminal"].strip())
            if terminal in terminals:
                raise ValueError("Two distinct quantities cannot use the same device terminal")
            terminals.add(terminal)
        if (
            set(entry) != set(expected["inputs"][key])
            or entry["unit"] != expected["inputs"][key]["unit"]
            or pin in pin_to_key
            or pin == "time_ms"
        ):
            raise ValueError("Require distinct recorder pins in the declared units")
        pin_to_key[pin] = key
    reader = csv.DictReader(StringIO(data.decode("utf-8-sig"), newline=""))
    if (
        not reader.fieldnames
        or len(reader.fieldnames) != len(pin_to_key) + 1
        or set(reader.fieldnames) != {"time_ms", *pin_to_key}
    ):
        raise ValueError("Logger header must identify time_ms and each mapped hardware pin")
    rows, previous = [], -1
    for row in reader:
        if None in row or None in row.values() or len(rows) >= 20000:
            raise ValueError("Return complete rows and at most 20000 common-clock samples")
        t = number(float(row["time_ms"]), "recorder time", nonnegative=True)
        if t <= previous:
            raise ValueError("Logger times must increase strictly")
        previous = t
        values = {"time_ms": t}
        for pin, key in pin_to_key.items():
            unit = form["inputs"][key]["unit"]
            v = number(float(row[pin]), key)
            if (unit == "bit" and v not in (0, 1)) or (
                unit == "integer" and not (v.is_integer() and 0 <= v < 2**53)
            ):
                raise ValueError(f"Invalid digital level or counter on {pin}")
            if unit == "ms" and v < 0:
                raise ValueError(f"Negative command time or age on {pin}")
            values[key] = v
        rows.append(values)
    if len(rows) < 2:
        raise ValueError("Multiple logger samples required")
    return rows


def convert(opening_path, form, csv_bytes):
    mode = form["mode"]
    if mode not in ("handover", *FAULTS):
        raise ValueError("Unknown recorder trial")
    expected = template(opening_path, mode, schema=form["schema"])
    rows = _rows(form, expected, csv_bytes)
    if mode == "handover":
        raw = bench_trace.templates(opening_path)["raw"]
        for key, entry in raw["channels"].items():
            entry.update(
                input_id=form["inputs"][key]["input_id"], samples=[[r["time_ms"], r[key]] for r in rows]
            )
        raw.update(
            trial_id=form["trial_id"],
            article_serial=form["article_serial"],
            capture_id=_id(form),
            record_kind=form["record_kind"],
            raw_csv_sha256=form["raw_csv_sha256"],
        )
        bench_trace.signals(raw)
        return raw

    if (
        set(form["limits"]) != set(expected["limits"])
        or not _digest(form["stimulus_record_sha256"])
        or not _digest(form["witness_record_sha256"])
    ):
        raise ValueError("Supply the limits and identities of the stimulus and witness records")
    bench_trace.require_text(form, ["limit_document_revision"])
    limits = {k: number(v, k, nonnegative=True) for k, v in form["limits"].items()}
    if any(
        limits[k] <= 0
        for k in (
            "minimum_hold_observation_ms",
            "response_deadline_ms",
            "maximum_gap_ms",
            "minimum_holding_force_kn",
        )
    ):
        raise ValueError("Time and holding-force limits must be positive")
    return fault_trial(form, rows, limits)


def fault_trial(form, rows, limits):
    """Score the stimulus, bounded response and retained state through a prescribed observation window."""
    mode = form["mode"]
    times = [r["time_ms"] for r in rows]
    gap = max(b - a for a, b in zip(times, times[1:]))
    uncertainty = 2 * limits["clock_error_ms"] + gap
    failures, holds = set(), set()
    current = form["schema"] == SCHEMA
    if not current:
        holds.add("Legacy capture lacks visit, terminal identities and measured emergency-brake output")
    index = next((i for i, r in enumerate(rows) if r["stimulus"]), None)
    if index is None or index == 0:
        raise ValueError("Record a known undisturbed sample before the stimulus edge")
    t0 = times[index]
    before = rows[index - 1]
    if gap > limits["maximum_gap_ms"]:
        holds.add("sample gap exceeds limit")
    if uncertainty >= limits["response_deadline_ms"]:
        holds.add("timing uncertainty spans the response deadline")
    start = None
    restarted = False
    restoration_epoch = None
    lost = False
    exit_open = False
    if mode == "power_restart" and (not before["supply_healthy"] or before["reset_key"]):
        holds.add("healthy powered sample with released reset key absent before interruption")
    if mode == "brake_feedback_loss" and not before["brake_feedback_ok"]:
        holds.add("healthy feedback before loss absent")
    if mode == "wrong_side_request" and before["wrong_side_command"]:
        holds.add("wrong-side command already present before declared stimulus")
    if mode == "stale_command" and before["command_age"] > limits["maximum_command_age_ms"]:
        holds.add("fresh command absent before stale stimulus")
    if (
        not before["parking_contact"]
        or before["holding_force"] < limits["minimum_holding_force_kn"]
        or before["dispatch"]
    ):
        holds.add("independently held and stationary trial precondition unproved")
    if current:
        if before["emergency_brake_output"]:
            holds.add("Emergency brake output already asserted before the injected fault")
        if mode == "power_restart" and form["visit"]["controller_boot_id"] != str(int(before["boot_epoch"])):
            holds.add("Pre-interruption controller epoch differs from the bound visit")
        if index < 2:
            holds.add("Need two pre-stimulus positions to observe a stationary berth")
        for sample in rows[max(0, index - 2) : index]:
            if (
                not sample["drive_inhibited"]
                or not sample["parking_contact"]
                or sample["dispatch"]
                or abs(sample["traction_effort"]) > limits["maximum_effort_kn"]
                or sample["holding_force"] < limits["minimum_holding_force_kn"]
                or abs(sample["position"] - before["position"]) > limits["maximum_displacement_mm"]
            ):
                holds.add("Secured stationary pre-stimulus samples disagree")
    trigger = rows[index]
    if mode == "brake_feedback_loss" and trigger["brake_feedback_ok"]:
        holds.add("stimulus edge lacks independently recorded feedback loss")
    if mode == "wrong_side_request" and not trigger["wrong_side_command"]:
        holds.add("wrong-side command absent at stimulus edge")
    if mode == "stale_command" and trigger["command_age"] <= limits["maximum_command_age_ms"]:
        holds.add("declared stale age was never exceeded at the stimulus")
    if mode == "power_restart" and trigger["supply_healthy"]:
        holds.add("power loss absent at stimulus edge")
    if current and mode == "stale_command":
        for r, must_be_stale in ((before, False), (trigger, True)):
            observed_age = r["time_ms"] - r["command_sent_ms"]
            age_error = uncertainty
            if (
                not r["command_received"]
                or observed_age < 0
                or abs(observed_age - r["command_age"]) > age_error
            ):
                holds.add("Packet receipt and aligned send time do not corroborate the reported age")
            if (must_be_stale and observed_age - age_error <= limits["maximum_command_age_ms"]) or (
                not must_be_stale and observed_age + age_error > limits["maximum_command_age_ms"]
            ):
                holds.add("Packet age uncertainty does not resolve the injected threshold crossing")
    if current and mode in EVACUATION:
        if before["local_handle"] or not trigger["local_handle"] or before["other_same_side_exit_open"]:
            holds.add("Independent local handle edge and initially closed other exits required")
    if before["opposite_door_open"] or before["exit_open"]:
        holds.add("selected exits must start closed for this fault protocol")
    for j, r in enumerate(rows[index:], start=index):
        if mode in ("evacuation_authorised", "evacuation_blocked"):
            if bool(r["egress_authorised"]) != (mode == "evacuation_authorised"):
                holds.add("proof of safe egress differs from the trial condition")
        allow_exit = (
            mode == "evacuation_authorised"
            and r["egress_authorised"]
            and (not current or r["emergency_brake_output"])
            and r["drive_inhibited"]
            and r["parking_contact"]
            and r["holding_force"] >= limits["minimum_holding_force_kn"]
            and abs(r["traction_effort"]) <= limits["maximum_effort_kn"]
        )
        if current and mode in EVACUATION and r["other_same_side_exit_open"]:
            failures.add("Another exit opened on the nominated side")
        if r["opposite_door_open"] or (r["exit_open"] and not allow_exit):
            failures.add("unpermitted door opening")
        exit_open = exit_open or bool(r["exit_open"])
        if r["dispatch"]:
            failures.add("dispatch after fault")
        if abs(r["position"] - before["position"]) > limits["maximum_displacement_mm"]:
            failures.add("displacement exceeds the secured-berth limit")
        if mode == "power_restart":
            if restarted and not r["supply_healthy"]:
                holds.add("Restored supply lost during the post-restart observation")
            if current and restarted and r["boot_epoch"] != restoration_epoch:
                holds.add("Controller boot identity changed during the post-restart observation")
            lost = lost or not r["supply_healthy"]
            if lost and r["supply_healthy"]:
                if not restarted and (
                    r["boot_epoch"] == before["boot_epoch"]
                    or not r["reset_key"]
                    or not rows[j - 1]["reset_key"]
                ):
                    holds.add("fresh startup and held reset key absent at restored supply")
                if not restarted:
                    restoration_epoch = r["boot_epoch"]
                restarted = True
        # During blackout, independently logged hold, torque and movement remain observable.
        # Powered logic output contacts may be de-energised. Evaluate their response after return.
        live = mode != "power_restart" or bool(r["supply_healthy"])
        restrained = (
            r["parking_contact"]
            and r["holding_force"] >= limits["minimum_holding_force_kn"]
            and abs(r["traction_effort"]) <= limits["maximum_effort_kn"]
        )
        powered_response = (
            r["drive_inhibited"]
            and r["independent_brake_request"]
            and (not current or r["emergency_brake_output"])
        )
        safe = bool(restrained and (not live or powered_response))
        if start is None and safe:
            start = r["time_ms"]
        if start is not None and not safe:
            failures.add("protective response lost during the observation window")
        if not safe and r["time_ms"] - t0 > limits["response_deadline_ms"]:
            failures.add("protective response absent after the deadline")
    if start is None:
        failures.add("no protective response recorded")
    elif start - t0 + uncertainty > limits["response_deadline_ms"]:
        holds.add("cannot resolve timely protective response")
    if start is None or times[-1] - start - uncertainty < limits["minimum_hold_observation_ms"]:
        holds.add("retained response window is too short")
    if mode == "power_restart":
        if not restarted:
            holds.add("service power restoration absent")
        else:
            restored = next(r["time_ms"] for r in rows[index:] if r["supply_healthy"])
            if times[-1] - restored - uncertainty < limits["minimum_hold_observation_ms"]:
                holds.add("post-restoration observation window too short")
    if mode == "evacuation_authorised" and not exit_open:
        failures.add("nominated exit failed to open")
    return {
        "schema": "baghdad-station-fault-screen/2",
        "capture_schema": form["schema"],
        "visit": form.get("visit"),
        "article_serial": form["article_serial"],
        "as_tested_build_sha256": form["as_tested_build_sha256"],
        "binding": form["binding"],
        "mode": mode,
        "form_id": _id(form),
        "raw_csv_sha256": form["raw_csv_sha256"],
        "record_kind": form["record_kind"],
        "stimulus_ms": t0,
        "first_protective_sample_ms": start,
        "time_uncertainty_ms": uncertainty,
        "observed_faults": sorted(failures),
        "sampling_and_protocol_holds": sorted(holds),
        "disposition": (
            "fault observed"
            if failures
            else "incomplete observations" if holds else "observations within supplied limits"
        ),
        "authenticated": False,
        "physical_accepted": False,
    }


def assess_handover(opening_path, form, csv_bytes, manifest_path, *, authenticator=None):
    """Verify that the reviewed bench JSON derives from these exact independent logger bytes."""
    if form["mode"] != "handover":
        raise ValueError("Ordinary departure manifest required")
    generated = convert(opening_path, form, csv_bytes)
    manifest = parse(manifest_path.read_bytes())
    same = {
        "provenance": "record_kind",
        "article_serial": "article_serial",
        "trial_id": "trial_id",
        "as_tested_build": "as_tested_build_sha256",
        "wiring_revision": "wiring_revision",
    }
    if any(manifest[m] != form[f] for m, f in same.items()):
        raise ValueError("Bench manifest differs from capture provenance, firmware, article or trial")
    if form["schema"] == SCHEMA and manifest["direction_sign"] != form["visit"]["direction_sign"]:
        raise ValueError("Bench departure direction differs from the instrumented visit")
    stored = parse(read_owned(manifest_path.parent, manifest["files"]["raw"]))
    if stored != generated:
        raise ValueError("Retained bench measurements differ from the CSV and channel map")
    return bench_trace.assess(
        manifest_path.parent, manifest, opening=opening_path, authenticator=authenticator
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("opening", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--template", choices=["handover", *FAULTS])
    mode.add_argument("--form", type=Path)
    parser.add_argument("--csv", type=Path)
    parser.add_argument(
        "--bench-manifest",
        type=Path,
        help="Assess a completed ordinary handover package against the original CSV",
    )
    args = parser.parse_args()
    if args.template:
        record = template(args.opening, args.template)
    else:
        if args.csv is None or args.csv.stat().st_size > MAX_CSV:
            parser.error("Pass --csv with a raw logger recording up to 4 MiB")
        form = parse(args.form.read_bytes())
        raw = args.csv.read_bytes()
        record = (
            assess_handover(args.opening, form, raw, args.bench_manifest)
            if args.bench_manifest
            else convert(args.opening, form, raw)
        )
    print(json.dumps(record, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

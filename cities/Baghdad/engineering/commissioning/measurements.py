"""Read two recorded steady-load windows from a single Airport radial path."""

import argparse
import csv
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path

from cities.Baghdad.engineering.commissioning import feeder
from engineering.outline.baghdad_system import _id
from engineering.railway_completion.evidence import number, parse

FIELDS = ("time_s", "window", "source_ka", "branch_ka", "bus_kv", "collector_kv", "conductor_c")
UNCERTAINTY = ("current_abs_ka", "voltage_abs_kv", "temperature_abs_c", "source_drift_kv")
MAX_RAW = 4 * 1024 * 1024


def template(opening, option="priced_radial"):
    return {
        "binding": feeder.binding(opening),
        "scope": feeder.topology(opening, option),
        "record_kind": None,
        "serial_and_wiring_record": None,
        "calibration_record": None,
        "trial_id": None,
        "raw_csv_sha256": None,
        "live_site_index": None,
        "failed_site_index": None,
        "track": None,
        "collector_chainage_km": None,
        "minimum_test_temperature_c": None,
        "uncertainty": dict.fromkeys(UNCERTAINTY),
    }


def assess(opening, form, raw):
    if (
        not isinstance(raw, bytes)
        or not 0 < len(raw) <= MAX_RAW
        or sha256(raw).hexdigest() != form["raw_csv_sha256"]
    ):
        raise ValueError("CSV bytes must match the recorded SHA256 and 4 MiB intake limit")
    option = form["scope"]["option"]
    expected = template(opening, option)
    if (
        set(form) != set(expected)
        or form["scope"] != expected["scope"]
        or form["binding"] != expected["binding"]
    ):
        raise ValueError("Hot circuit record refers to another opening or supply circuit")
    if form["record_kind"] not in ("physical-measurement", "synthetic-fixture") or any(
        not isinstance(form[k], str) or not form[k].strip()
        for k in ("trial_id", "calibration_record", "serial_and_wiring_record")
    ):
        raise ValueError("Identify the recorded trial, articles, calibration and wiring")
    live, failed = form["live_site_index"], form["failed_site_index"]
    sites = form["scope"]["design"]["site_chainage_km"]
    if (
        any(type(k) is not int or not 0 <= k < len(sites) for k in (live, failed))
        or abs(live - failed) != 1
        or form["track"] not in ("outward", "inward")
    ):
        raise ValueError("Identify the live and adjacent isolated site of the restored radial path")
    km = number(form["collector_chainage_km"], "chainage")
    if not min(sites[live], sites[failed]) <= km <= max(sites[live], sites[failed]):
        raise ValueError("Collector lies outside the identified restored feed")
    if set(form["uncertainty"]) != set(UNCERTAINTY):
        raise ValueError("Return all meter errors and the bound on source drift between windows")
    di, dv, dt, drift = (number(form["uncertainty"][k], k, nonnegative=True) for k in UNCERTAINTY)
    temp = number(form["minimum_test_temperature_c"], "minimum test temperature")
    reader = csv.DictReader(StringIO(raw.decode("utf-8-sig"), newline=""))
    if reader.fieldnames != list(FIELDS):
        raise ValueError("Use the documented meter columns and units")
    windows = {"low": [], "high": []}
    previous = -1
    for row in reader:
        key = row["window"]
        if key not in windows or (key == "low" and windows["high"]) or None in row or None in row.values():
            raise ValueError("Record a low window followed by a high window with complete meter columns")
        values = {
            k: number(float(row[k]), k, nonnegative=k != "conductor_c") for k in FIELDS if k != "window"
        }
        if values["time_s"] <= previous or min(values["bus_kv"], values["collector_kv"]) <= dv:
            raise ValueError("Require increasing sample times and positive measured operating voltages")
        if (
            values["branch_ka"] - di > values["source_ka"] + di
            or values["collector_kv"] - dv > values["bus_kv"] + dv
        ):
            raise ValueError("Recorded currents or voltage polarity conflict with radial traction loading")
        previous = values["time_s"]
        windows[key].append(values)
    if min(map(len, windows.values())) < 2:
        raise ValueError("Need at least two ordered samples in each meter window")
    low, high = windows.values()
    delta_i = min(h["source_ka"] for h in high) - max(l["source_ka"] for l in low) - 2 * di
    high_branch = min(h["branch_ka"] for h in high) - di
    if min(delta_i, high_branch) <= 0:
        raise ValueError("Meter error obscures the current step or path current")
    # Bound numerator and denominator separately. Euclidean combination of meter errors
    # would need an independence assumption; the interval limits also include window spread.
    max_bus_loss = max(l["bus_kv"] for l in low) - min(h["bus_kv"] for h in high) + 2 * dv + drift
    if max_bus_loss < 0:
        raise ValueError("Source slope is incompatible with passive droop within declared drift")
    source_r = max_bus_loss / delta_i
    path_r = max((h["bus_kv"] - h["collector_kv"] + 2 * dv) / (h["branch_ka"] - di) for h in high)
    result = {
        "binding": expected["binding"],
        "scope": expected["scope"],
        "record_kind": form["record_kind"],
        "raw_csv_sha256": form["raw_csv_sha256"],
        "form_id": _id(form),
        "trial_id": form["trial_id"],
        "path_length_km": abs(km - sites[live]),
        "live_site_index": live,
        "failed_site_index": failed,
        "track": form["track"],
        "low_samples": len(low),
        "high_samples": len(high),
        "maximum_two_point_source_slope_ohm": source_r,
        "maximum_high_window_bus_to_shoe_loop_ohm": path_r,
        "high_window_min_collector_kv": min(h["collector_kv"] for h in high) - dv,
        "high_window_min_branch_power_mw": min(
            (h["collector_kv"] - dv) * (h["branch_ka"] - di) for h in high
        ),
        "high_window_min_temperature_c": min(h["conductor_c"] for h in high) - dt,
        "required_two_pulse_mw": opening["section_power"]["assumptions"][
            "design_two_pulse_load_plus_all_working_auxiliaries_mw"
        ],
        "authenticated": False,
        "physical_accepted": False,
    }
    result["covers_test_temperature"] = result["high_window_min_temperature_c"] >= temp
    result["covers_stated_load"] = (
        result["high_window_min_branch_power_mw"] >= result["required_two_pulse_mw"]
    )
    result["measured_window_above_floor"] = (
        result["high_window_min_collector_kv"] >= opening["section_power"]["floor_kv"]
    )
    result["evaluation_id"] = _id(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("opening", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--template", choices=feeder.OPTIONS)
    mode.add_argument("--record", type=Path)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    opening = parse(args.opening.read_bytes())
    if args.template:
        result = template(opening, args.template)
    else:
        if args.csv is None or args.csv.stat().st_size > MAX_RAW:
            parser.error("Pass --csv with a raw recording of up to 4 MiB")
        result = assess(opening, parse(args.record.read_bytes()), args.csv.read_bytes())
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

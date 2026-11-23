"""Read-only voltage and service exposure after simultaneous source and path loss."""

from collections import defaultdict
from hashlib import sha256
from itertools import pairwise
import json
from math import ceil, isclose
from pathlib import Path

from cities.Baghdad.engineering.commissioning import feeder
from engineering.outline.baghdad_system import _id


def _pulses(service, route, assumptions):
    """Keep separate departure identities while bounding their complete footprints."""
    pulses = []
    for _, direction, departure, _ in [*service["trips"], *service["positioning_trips"]]:
        for index, (a, b) in enumerate(pairwise(service["patterns"][direction])):
            duration = max(
                assumptions["pulse_seconds"],
                ceil(service["leg_profiles"][direction][index]["acceleration_s"]),
            )
            start = departure + a["departure_s"]
            x = route * a["fraction"]
            reach = min(
                route * (b["fraction"] - a["fraction"]), duration * assumptions["speed_cap_m_s"] / 1000
            )
            lo, hi = (x, x + reach) if direction == 0 else (route - x - reach, route - x)
            pulses.append((start, start + duration, round(lo, 9), round(hi, 9)))
    for move in service["terminal"]["yard_moves"]:
        pulses.append((move["start_s"], move["end_s"], 0.0, 0.0))
    return pulses


def _counts(pulses, lo, hi, limit):
    changes = defaultdict(list)
    affected = set()
    for i, (start, end, x, y) in enumerate(pulses):
        if x <= round(hi, 9) and y >= round(lo, 9):
            changes[start].append((i, True))
            changes[end].append((i, False))
            affected.add(i)
    active, conflicts = set(), set()
    for t in sorted(changes):
        for index, starts in changes[t]:
            if starts:
                active.add(index)
            else:
                active.discard(index)
        if len(active) > limit:
            conflicts.update(active)
    return {
        "intersecting_pulses": len(affected),
        "outside_source_area": len(pulses) - len(affected),
        "within_voltage_limit_throughout": len(affected - conflicts),
        "overlap_review_required": len(conflicts),
    }


def artifacts(opening, power, service):
    section = opening["section_power"]
    paired = power["parallel_quotation"]
    scope = feeder.topology(opening, "six_site_parallel")
    if (
        power["binding"] != feeder.binding(opening)
        or power["evaluation_id"] != _id({k: v for k, v in power.items() if k != "evaluation_id"})
        or scope != paired["scope"]
        or _id(service) != section["service_id"]
    ):
        raise ValueError("Require matched opening, service and evaluated six-site paired circuit")
    a = section["assumptions"]
    sites = scope["design"]["site_chainage_km"]
    sets = opening["bundle"]["active_sets"]
    cruise = a["uphill_cruise_bound_mw_per_nonaccelerating_set"]
    auxiliary = sets * a["auxiliaries_mw_per_train"]
    background = auxiliary + sets * cruise
    step = a["train_traction_rating_mw"] - cruise
    floor = power["floor_kv"]
    lost = paired["single_path_lost_with_site_out_combined"]
    _, resistance_factor, _ = feeder.CASES["combined sensitivity"]
    hot_r = lost["loop_ohm"] / resistance_factor
    source = scope["design"]["source_kv"]
    pulses = _pulses(service, scope["design"]["route_km"], a)
    if len(pulses) != paired["replayed_pulses"]:
        raise ValueError("Pulse count differs from the paired-path service replay")
    cases = {}
    for label, (e, r, p) in feeder.CASES.items():
        kv, ohm = e * source, r * hot_r
        limit_ka = (kv - floor) / ohm
        limit_mw = floor * limit_ka
        loads = {
            "two_accelerating": background + 2 * step,
            "one_accelerating": background + step,
            "no_acceleration_with_cruise": background,
            "stopped_auxiliaries_only": auxiliary,
        }
        samples = {name: feeder.voltage(kv, ohm, p * load, floor) for name, load in loads.items()}
        cases[label] = {
            "floor_load_bound_mw": limit_mw,
            "floor_current_bound_ka": limit_ka,
            "loads": samples,
            "maximum_concurrent_scheduled_pulses": sum(
                p * (background + i * step) <= limit_mw for i in range(1, sets + 1)
            ),
        }
    combined = cases["combined sensitivity"]
    if not isclose(
        combined["loads"]["two_accelerating"]["collector_kv"], lost["collector_kv"], abs_tol=1e-10
    ):
        raise ValueError("Combined two-pulse voltage differs from feeder study")
    outages = []
    for failed in range(len(sites)):
        for live in (failed - 1, failed + 1):
            if not 0 <= live < len(sites):
                continue
            other = 2 * live - failed
            outer = (sites[other] + sites[live]) / 2 if 0 <= other < len(sites) else sites[live]
            lo, hi = sorted((outer, sites[failed]))
            outages.append(
                {
                    "isolated_site": failed,
                    "adjacent_source": live,
                    "failed_branch_pair_span_km": sorted((sites[failed], sites[live])),
                    "failed_site_normal_zone_km": [
                        sites[0] if failed == 0 else (sites[failed - 1] + sites[failed]) / 2,
                        sites[-1] if failed + 1 == len(sites) else (sites[failed] + sites[failed + 1]) / 2,
                    ],
                    "conditional_restored_source_area_km": [lo, hi],
                    "counts_by_sensitivity": {
                        label: _counts(pulses, lo, hi, case["maximum_concurrent_scheduled_pulses"])
                        for label, case in cases.items()
                    },
                    **_counts(pulses, lo, hi, combined["maximum_concurrent_scheduled_pulses"]),
                }
            )
    report = {
        "schema": "baghdad-paired-path-degraded-service/1",
        "opening_id": opening["candidate_id"],
        "power_evaluation": power["evaluation_id"],
        "design_id": scope["design_id"],
        "service_id": section["service_id"],
        "source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "floor_kv": floor,
        "total_scheduled_pulses": len(pulses),
        "sensitivity_cases": cases,
        "single_site_and_adjacent_path_pair_outages": outages,
        "motion_authorised": False,
        "energisation_authorised": False,
        "evacuation_authorised": False,
    }
    report["evaluation_id"] = _id(report)
    lines = [
        "# Airport service after a source and conductor-path outage",
        "",
        f"The proposed six-site paired circuit has {len(pulses)} scheduled acceleration and yard pulses. A simultaneous site and positive/return path loss leaves one full longitudinal path. At the longest restored distance, the combined adverse case gives a {combined['floor_load_bound_mw']:.3f} MW collector load limit and {combined['floor_current_bound_ka']:.3f} kA at the {floor:.3f} kV floor.",
        "",
        "| Combined adverse duty | Collector MW | Collector kV | Voltage screen |",
        "|---|---:|---:|---|",
    ]
    for name, sample in combined["loads"].items():
        lines.append(
            f"| {name.replace('_',' ')} | {sample['collector_load_mw']:.3f} | {sample['collector_kv']:.4f} | {sample['physical_screen']} |"
        )
    lines += [
        "",
        "All three active sets retain their auxiliary demand. The moving cases also include uphill cruise for each set outside acceleration. The stopped case assumes all traction has ceased. Station and emergency facility supplies require separate evidence.",
        "",
        "| Isolated site (0–5) | Adjacent source | Source area km | Pulses within voltage limit | Pulses requiring overlap review | Pulses outside area |",
        "|---:|---:|---|---:|---:|---:|",
    ]
    for case in outages:
        lo, hi = case["conditional_restored_source_area_km"]
        lines.append(
            f"| {case['isolated_site']} | {case['adjacent_source']} | {lo:.1f}–{hi:.1f} | {case['within_voltage_limit_throughout']} | {case['overlap_review_required']} | {case['outside_source_area']} |"
        )
    lines += [
        "",
        "Each row is a separate outage hypothesis. Both tracks contribute to the same source bound. A footprint touching a feed boundary counts against either possible source. Rounded chainages use the same precision on both sides of that comparison. Every pulse that overlaps excess demand is flagged for review. The count identifies affected movements and does not assign dispatch priority or calculate a revised timetable. Delay and restart can introduce new coincidences.",
        "",
        "Before restoration the failed site’s normally fed zone is unavailable. The JSON identifies its adjacent midpoints, the lost path span and the hypothesis for the adjacent source. A loss on either track needs its own equipment-tagged isolation plan. Retain the operating hold pending verified topology, utility voltage, live-source and surviving-path current ratings, protective discrimination, thermal duty, train positions and an approved revised timetable.",
        "",
        "For a stranded train identify its occupied section, independent auxiliary duration and accessible detrainment route. Prove dead locally, including adjacent feeds, regeneration and shoe bridging, and obtain the responsible operator’s evacuation authority and accessible egress arrangements. A calculated auxiliary voltage cannot establish emergency power continuity or authorise evacuation.",
    ]
    return {
        "degraded-service.json": (json.dumps(report, indent=2, allow_nan=False) + "\n").encode(),
        "degraded-service.md": ("\n".join(lines) + "\n").encode(),
    }

"""Finite non-preemptive resource calendar for declared factory planning cases.

Each beam is scheduled to completion in input order, filling calendar gaps.
This deterministic list policy is not an optimal or steady-state production model.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import math

TASK_RESOURCES = {
    "reinforcement": ["reinforcement_bench", "reinforcement_crew"],
    "cage_lift": ["crane", "crane_crew", "rigging_crew"],
    "bed_setup_stress": ["stressing_crew"],
    "casting": ["crane", "crane_crew", "casting_crew", "mixer"],
    "release_demould": ["crane", "crane_crew", "rigging_crew", "stressing_crew"],
    "dispatch": ["crane", "crane_crew", "rigging_crew", "haulage"],
}


class Calendar:
    def __init__(self, resources, shift_hours, maintenance=()):
        if not 0 < shift_hours <= 24:
            raise ValueError("shift length must be in (0,24]")
        if not resources or any(
            type(n) is not int or not 1 <= n <= 256 for n in resources.values()
        ):
            raise ValueError("bounded positive integer resource counts required")
        self.shift = shift_hours
        self.units = {
            key: [[] for _ in range(count)] for key, count in resources.items()
        }
        self.events = []
        for block in maintenance:
            if (
                block["resource"] not in self.units
                or type(block["unit"]) is not int
                or not 0 <= block["unit"] < len(self.units[block["resource"]])
            ):
                raise ValueError("maintenance refers to an absent resource")
            self.reserve(
                [(block["resource"], block["unit"])],
                block["start_h"],
                block["end_h"],
                "maintenance",
            )

    def shift_start(self, earliest, duration):
        if (
            not math.isfinite(earliest)
            or earliest < 0
            or not 0 < duration <= self.shift
        ):
            raise ValueError("finite release and single-shift task duration required")
        day = math.floor(earliest / 24)
        return (
            earliest
            if earliest + duration <= day * 24 + self.shift + 1e-9
            else (day + 1) * 24
        )

    def slot(self, needs, earliest, duration, fixed=None):
        if (
            not needs
            or len(needs) != len(set(needs))
            or any(key not in self.units for key in needs)
        ):
            raise ValueError("unique existing task resources required")
        t = self.shift_start(earliest, duration)
        for _ in range(20000):
            selected, next_times = [], []
            for key in needs:
                free = []
                blockers = []
                for unit, blocks in enumerate(self.units[key]):
                    if fixed and key in fixed and fixed[key] != unit:
                        continue
                    conflict = [
                        b
                        for b in blocks
                        if max(t, b[0]) < min(t + duration, b[1]) - 1e-9
                    ]
                    if conflict:
                        blockers.append(max(b[1] for b in conflict))
                    else:
                        free.append(unit)
                if free:
                    selected.append((key, free[0]))
                else:
                    next_times.append(min(blockers))
            if not next_times:
                return t, selected
            t = self.shift_start(max(next_times), duration)
        raise ValueError("resource calendar search budget exhausted")

    def reserve(self, allocations, start, end, task):
        if not math.isfinite(start) or not math.isfinite(end) or not 0 <= start < end:
            raise ValueError("positive finite calendar reservation required")
        for key, unit in allocations:
            blocks = self.units[key][unit]
            if any(max(start, a) < min(end, b) - 1e-9 for a, b, _ in blocks):
                raise ValueError("overlapping resource reservation: " + key)
        for key, unit in allocations:
            self.units[key][unit].append((start, end, task))
            self.units[key][unit].sort()

    def task(self, beam, name, needs, earliest, duration, fixed=None):
        start, allocations = self.slot(needs, earliest, duration, fixed)
        self.reserve(allocations, start, start + duration, beam + "/" + name)
        row = dict(
            beam=beam,
            task=name,
            start_h=start,
            end_h=start + duration,
            resources=[dict(resource=k, unit=u) for k, u in allocations],
        )
        self.events.append(row)
        return row


def validate(report):
    """Independent interval, precedence, shift and continuous-hold checks."""
    occupied = defaultdict(list)
    basis = report["basis"]
    hours = basis["hours"]
    if (
        report["curing_elapsed_h"] != hours["curing_elapsed"]
        or report["storage_elapsed_h"] != hours["storage_elapsed"]
        or report["beam_count"] != basis["beam_count"]
        or report["shift_hours"] != basis["shift_hours"]
        or report["horizon_h"] != basis["horizon_days"] * 24
    ):
        raise ValueError("schedule basis/hold correspondence differs")
    batches = math.ceil(report["beam_volume_m3"] / basis["batch_output_assumption_m3"])
    casting = hours["casting_setup_finish"] + batches * (
        hours["mix_per_batch"] + hours["pour_per_batch"]
    )
    if report["batches_per_beam"] != batches or report["casting_block_h"] != casting:
        raise ValueError("schedule batch/casting correspondence differs")
    durations = {key: hours[key] for key in TASK_RESOURCES if key != "casting"}
    durations["casting"] = casting
    resources = {**report["basis"]["resources"], "bed": report["casting_positions"]}
    maintenance = sorted(
        (m["resource"], m["unit"], m["start_h"], m["end_h"])
        for m in basis["maintenance"]
    )
    actual_maintenance = sorted(
        (m["resource"], m["unit"], m["start_h"], m["end_h"])
        for m in report["reservations"]
        if m["task"] == "maintenance"
    )
    if maintenance != actual_maintenance:
        raise ValueError("maintenance reservation differs")
    consumed = len(maintenance)
    for row in report["reservations"]:
        start, end = row["start_h"], row["end_h"]
        if not 0 <= start < end or not math.isfinite(end):
            raise ValueError("invalid retained reservation")
        if (
            row["resource"] not in resources
            or type(row["unit"]) is not int
            or not 0 <= row["unit"] < resources[row["resource"]]
        ):
            raise ValueError("reservation uses an absent resource unit")
        occupied[(row["resource"], row["unit"])].append((start, end))
    for rows in occupied.values():
        rows.sort()
        if any(a[1] > b[0] + 1e-8 for a, b in zip(rows, rows[1:])):
            raise ValueError("retained schedule resource overlap")
    by_beam = defaultdict(dict)
    for task in report["tasks"]:
        if task["task"] in by_beam[task["beam"]]:
            raise ValueError("duplicate beam task")
        by_beam[task["beam"]][task["task"]] = task
        if task["task"] not in TASK_RESOURCES or sorted(
            r["resource"] for r in task["resources"]
        ) != sorted(TASK_RESOURCES[task["task"]]):
            raise ValueError("task resources omit or duplicate a required allocation")
        if abs(task["end_h"] - task["start_h"] - durations[task["task"]]) > 1e-8:
            raise ValueError("task duration differs from declared process")
        day = math.floor(task["start_h"] / 24)
        if task["end_h"] > day * 24 + report["shift_hours"] + 1e-8:
            raise ValueError("task crosses the declared shift")
        for resource in task["resources"]:
            exact = [
                row
                for row in report["reservations"]
                if row["resource"] == resource["resource"]
                and row["unit"] == resource["unit"]
                and row["task"] == task["beam"] + "/" + task["task"]
                and abs(row["start_h"] - task["start_h"]) < 1e-8
                and abs(row["end_h"] - task["end_h"]) < 1e-8
            ]
            if len(exact) != 1:
                raise ValueError("task/reservation correspondence differs")
            consumed += 1
    order = [
        "reinforcement",
        "cage_lift",
        "bed_setup_stress",
        "casting",
        "release_demould",
        "dispatch",
    ]
    if len(by_beam) != report["beam_count"]:
        raise ValueError("scheduled beam membership differs")
    for beam, tasks in by_beam.items():
        if set(tasks) != set(order):
            raise ValueError("complete beam task chain required")
        if any(
            tasks[a]["end_h"] > tasks[b]["start_h"] + 1e-8
            for a, b in zip(order, order[1:])
        ):
            raise ValueError("beam task precedence violated")
        if (
            tasks["release_demould"]["start_h"]
            < tasks["casting"]["end_h"] + report["curing_elapsed_h"] - 1e-8
        ):
            raise ValueError("planned cure hold violated")
        if (
            tasks["dispatch"]["start_h"]
            < tasks["release_demould"]["end_h"] + report["storage_elapsed_h"] - 1e-8
        ):
            raise ValueError("planned storage dwell violated")
        for resource, start, end in (
            ("bed", tasks["cage_lift"]["start_h"], tasks["release_demould"]["end_h"]),
            (
                "storage_slot",
                tasks["release_demould"]["start_h"],
                tasks["dispatch"]["end_h"],
            ),
        ):
            holds = [
                r
                for r in report["reservations"]
                if r["resource"] == resource
                and r["task"] == beam + "/hold"
                and abs(r["start_h"] - start) < 1e-8
                and abs(r["end_h"] - end) < 1e-8
            ]
            if len(holds) != 1:
                raise ValueError("continuous bed/storage reservation differs")
            consumed += 1
        bench = next(
            r["unit"]
            for r in tasks["reinforcement"]["resources"]
            if r["resource"] == "reinforcement_bench"
        )
        waits = [
            r
            for r in report["reservations"]
            if r["resource"] == "reinforcement_bench"
            and r["unit"] == bench
            and r["task"] == beam + "/cage-wait"
            and r["start_h"] == tasks["reinforcement"]["end_h"]
            and r["end_h"] == tasks["cage_lift"]["end_h"]
        ]
        if len(waits) != 1:
            raise ValueError("cage bench wait reservation differs")
        consumed += 1
    if consumed != len(report["reservations"]):
        raise ValueError("unallocated schedule reservation")
    return True


def schedule(cfg, beam_volume, positions, yield_fraction):
    if (
        cfg.get("schema") != "osr-factory-schedule-basis/1"
        or cfg["state"] != "synthetic"
    ):
        raise ValueError("explicit synthetic factory scheduling basis required")
    for key in ("beam_count", "horizon_days"):
        if type(cfg[key]) is not int or not 1 <= cfg[key] <= 128:
            raise ValueError("bounded campaign/horizon required")
    if (
        type(positions) is not int
        or not 1 <= positions <= 256
        or not 0 < yield_fraction <= 1
    ):
        raise ValueError("bounded positions and declared yield required")
    h = cfg["hours"]
    if (
        any(
            type(v) not in (int, float) or not math.isfinite(v) or v <= 0
            for v in h.values()
        )
        or not math.isfinite(beam_volume)
        or beam_volume <= 0
        or not math.isfinite(cfg["batch_output_assumption_m3"])
        or cfg["batch_output_assumption_m3"] <= 0
    ):
        raise ValueError(
            "positive finite duration, volume and batch assumption required"
        )
    batches = math.ceil(beam_volume / cfg["batch_output_assumption_m3"])
    cast_hours = h["casting_setup_finish"] + batches * (
        h["mix_per_batch"] + h["pour_per_batch"]
    )
    resources = {**cfg["resources"], "bed": positions}
    calendar = Calendar(resources, cfg["shift_hours"], cfg["maintenance"])
    bed_free = [0.0] * positions
    bench_free = [0.0] * resources["reinforcement_bench"]
    storage_free = [0.0] * resources["storage_slot"]
    for index in range(cfg["beam_count"]):
        beam = f"beam-{index+1:03d}"
        bed_id = min(range(positions), key=lambda i: (bed_free[i], i))
        # The cage bench remains occupied until the cage-lift task starts.
        bench_id = min(range(len(bench_free)), key=lambda i: (bench_free[i], i))
        cage = calendar.task(
            beam,
            "reinforcement",
            TASK_RESOURCES["reinforcement"],
            bench_free[bench_id],
            h["reinforcement"],
            {"reinforcement_bench": bench_id},
        )
        lift = calendar.task(
            beam,
            "cage_lift",
            ["crane", "crane_crew", "rigging_crew"],
            max(cage["end_h"], bed_free[bed_id]),
            h["cage_lift"],
        )
        bench = [
            (r["resource"], r["unit"])
            for r in cage["resources"]
            if r["resource"] == "reinforcement_bench"
        ]
        if lift["end_h"] > cage["end_h"]:
            calendar.reserve(bench, cage["end_h"], lift["end_h"], beam + "/cage-wait")
        bench_free[bench_id] = lift["end_h"]
        setup = calendar.task(
            beam,
            "bed_setup_stress",
            ["stressing_crew"],
            lift["end_h"],
            h["bed_setup_stress"],
        )
        casting = calendar.task(
            beam,
            "casting",
            ["crane", "crane_crew", "casting_crew", "mixer"],
            setup["end_h"],
            cast_hours,
        )
        storage_id = min(range(len(storage_free)), key=lambda i: (storage_free[i], i))
        release = calendar.task(
            beam,
            "release_demould",
            ["crane", "crane_crew", "rigging_crew", "stressing_crew"],
            max(casting["end_h"] + h["curing_elapsed"], storage_free[storage_id]),
            h["release_demould"],
        )
        dispatch = calendar.task(
            beam,
            "dispatch",
            ["crane", "crane_crew", "rigging_crew", "haulage"],
            release["end_h"] + h["storage_elapsed"],
            h["dispatch"],
        )
        calendar.reserve(
            [("bed", bed_id)], lift["start_h"], release["end_h"], beam + "/hold"
        )
        calendar.reserve(
            [("storage_slot", storage_id)],
            release["start_h"],
            dispatch["end_h"],
            beam + "/hold",
        )
        bed_free[bed_id], storage_free[storage_id] = release["end_h"], dispatch["end_h"]
    reservations = [
        dict(resource=key, unit=unit, start_h=start, end_h=end, task=task)
        for key, units in calendar.units.items()
        for unit, blocks in enumerate(units)
        for start, end, task in blocks
    ]
    horizon = cfg["horizon_days"] * 24
    completed = sum(
        t["task"] == "dispatch" and t["end_h"] <= horizon for t in calendar.events
    )
    crane_hours = sum(
        max(0, min(r["end_h"], horizon) - r["start_h"])
        for r in reservations
        if r["resource"] == "crane"
        and r["task"] != "maintenance"
        and r["start_h"] < horizon
    )
    result = dict(
        schema="osr-factory-finite-schedule/1",
        state="synthetic",
        basis=deepcopy(cfg),
        beam_count=cfg["beam_count"],
        casting_positions=positions,
        shift_hours=cfg["shift_hours"],
        beam_volume_m3=beam_volume,
        batches_per_beam=batches,
        casting_block_h=cast_hours,
        curing_elapsed_h=h["curing_elapsed"],
        storage_elapsed_h=h["storage_elapsed"],
        horizon_h=horizon,
        dispatched_within_horizon=completed,
        backlog_at_horizon=cfg["beam_count"] - completed,
        planning_accepted_equivalent=completed * yield_fraction,
        crane_booked_hours=crane_hours,
        crane_policy_hours_per_beam=h["cage_lift"]
        + cast_hours
        + h["release_demould"]
        + h["dispatch"],
        tasks=calendar.events,
        reservations=reservations,
        site_or_supplier_validated=False,
        production_release=False,
        limitations=[
            "Finite first-come list schedule; neither steady-state capacity nor an optimum",
            "Batch output, durations, release maturity and shift pattern are unmeasured planning assumptions",
            "Casting dedicates crane and mixer for one continuous block; no mix/pour overlap or hot-concrete queue",
            "No adopted lift plan, transport route, workforce agreement, reliability distribution or accepted output evidence",
        ],
    )
    result["calendar_verified"] = validate(result)
    return result

"""Paired explicit-scenario factorial studies using an actual caller evaluator.

No probability distributions, surrogate values or feasibility are inferred.
The caller supplies a worker-bounded evaluator; this layer counts every call,
checks its own campaign deadline, and retains failures and unexecuted cases.
"""

from copy import deepcopy
from itertools import combinations, product
import math
from pathlib import Path
import random
import time

from .contracts import canonical, fingerprint

SUCCESS = {"completed", "passed", "numerically-verified"}
OUTCOMES = SUCCESS | {
    "failed",
    "unknown",
    "outside-domain",
    "unavailable",
    "budget-exceeded",
    "cancelled",
    "not-run",
}


def interaction_study(
    candidates, factors, evaluate, *, seed, max_evaluations, wall_seconds, output=None
):
    if (
        not isinstance(candidates, dict)
        or not 1 <= len(candidates) <= 16
        or any(not isinstance(k, str) or not 0 < len(k) <= 80 for k in candidates)
    ):
        raise ValueError(
            "one to sixteen named immutable candidate definitions required"
        )
    if not isinstance(factors, dict) or not 2 <= len(factors) <= 6:
        raise ValueError("two to six explicitly supplied uncertainty factors required")
    if (
        type(seed) is not int
        or type(max_evaluations) is not int
        or not 1 <= max_evaluations <= 1024
    ):
        raise ValueError("integer seed and bounded evaluator budget required")
    if (
        type(wall_seconds) not in (int, float)
        or not math.isfinite(wall_seconds)
        or not 0 < wall_seconds <= 14400
    ):
        raise ValueError("finite positive campaign wall budget required")
    for name, levels in factors.items():
        if (
            not isinstance(name, str)
            or not name
            or not isinstance(levels, list)
            or len(levels) != 2
            or fingerprint(levels[0]) == fingerprint(levels[1])
        ):
            raise ValueError("named two-level explicit uncertainty factors required")
    canonical(dict(candidates=candidates, factors=factors))
    candidates, factors = deepcopy(candidates), deepcopy(factors)
    request = dict(
        schema="osr-paired-factorial-request/1",
        candidates=deepcopy(candidates),
        factors=deepcopy(factors),
        seed=seed,
        max_evaluations=max_evaluations,
        wall_seconds=wall_seconds,
        evaluator_is_caller_bounded=True,
        probability_model=None,
        physical_release=False,
    )
    folder = Path(output) if output is not None else None
    if folder is not None:
        from .store import write_new

        folder.mkdir(parents=True, exist_ok=True)
        write_new(folder / "request.json", request)
    names = sorted(factors)
    scenarios = []
    for bits in product((0, 1), repeat=len(names)):
        values = {name: deepcopy(factors[name][bit]) for name, bit in zip(names, bits)}
        scenarios.append(
            dict(id=fingerprint(values), values=values, levels=dict(zip(names, bits)))
        )
    random.Random(seed).shuffle(scenarios)
    candidate_names = sorted(candidates)
    # Alternating the candidate order avoids always favouring the first design
    # when a campaign runs out of time. Every paired comparison uses one scenario.
    started = time.monotonic()
    rows = []
    calls = 0
    for index, scenario in enumerate(scenarios):
        order = (
            candidate_names[index % len(candidate_names) :]
            + candidate_names[: index % len(candidate_names)]
        )
        for name in order:
            row = dict(
                candidate=name,
                candidate_sha256=fingerprint(candidates[name]),
                scenario=deepcopy(scenario),
                state="not-run",
                metrics={},
                basis="campaign evaluator budget exhausted",
                evaluator_called=False,
            )
            if calls < max_evaluations and time.monotonic() - started < wall_seconds:
                calls += 1
                row["evaluator_called"] = True
                call_started = time.monotonic()
                try:
                    evaluated = evaluate(
                        deepcopy(candidates[name]), deepcopy(scenario["values"])
                    )
                    if (
                        not isinstance(evaluated, dict)
                        or evaluated.get("state") not in OUTCOMES
                        or not isinstance(evaluated.get("metrics"), dict)
                    ):
                        raise ValueError(
                            "evaluator must return a declared state and named metric values"
                        )
                    for metric, value in evaluated["metrics"].items():
                        if (
                            not isinstance(metric, str)
                            or not metric
                            or value is not None
                            and (
                                type(value) not in (int, float)
                                or not math.isfinite(value)
                            )
                        ):
                            raise ValueError(
                                "evaluator metrics must be finite numbers or explicit unknowns"
                            )
                    canonical(evaluated)
                    row.update(
                        state=evaluated["state"],
                        metrics=evaluated["metrics"],
                        basis="actual caller evaluator result",
                        result=evaluated,
                    )
                    if time.monotonic() - started > wall_seconds:
                        row.update(
                            state="budget-exceeded",
                            metrics={},
                            basis="caller evaluator returned after the campaign deadline; raw result retained",
                        )
                except (
                    ValueError,
                    RuntimeError,
                    OSError,
                    TimeoutError,
                    TypeError,
                    KeyError,
                    ArithmeticError,
                ) as error:
                    from .runtime import Cancelled, BudgetExceeded

                    if isinstance(error, (Cancelled, BudgetExceeded)):
                        raise
                    row.update(
                        state=(
                            "budget-exceeded"
                            if isinstance(error, TimeoutError)
                            else "failed"
                        ),
                        basis=str(error),
                        error_type=type(error).__name__,
                    )
                row["elapsed_seconds"] = time.monotonic() - call_started
            elif time.monotonic() - started >= wall_seconds:
                row["basis"] = "campaign wall budget exhausted"
            rows.append(row)
            if folder is not None:
                write_new(
                    folder
                    / "cases"
                    / (name.encode().hex() + "-" + scenario["id"] + ".json"),
                    row,
                )
    metric_names = sorted({metric for row in rows for metric in row["metrics"]})
    lookup = {(row["candidate"], row["scenario"]["id"]): row for row in rows}

    def metric_value(row, metric):
        return row["metrics"].get(metric) if row["state"] in SUCCESS else None

    summaries = []
    for name in candidate_names:
        selected = [row for row in rows if row["candidate"] == name]
        ranges = {}
        for metric in metric_names:
            values = [metric_value(row, metric) for row in selected]
            known = [value for value in values if value is not None]
            ranges[metric] = dict(
                minimum=min(known) if known else None,
                maximum=max(known) if known else None,
                known_cases=len(known),
                unknown_or_failed_cases=len(values) - len(known),
                complete_explicit_scenario_envelope=len(known) == len(values),
                probability_interval=False,
            )
        interactions = []
        for first, second in combinations(names, 2):
            others = [key for key in names if key not in (first, second)]
            for metric in metric_names:
                contrasts = []
                missing = 0
                for other_bits in product((0, 1), repeat=len(others)):
                    corners = {}
                    fixed = dict(zip(others, other_bits))
                    for row in selected:
                        levels = row["scenario"]["levels"]
                        if all(levels[key] == bit for key, bit in fixed.items()):
                            corners[(levels[first], levels[second])] = metric_value(
                                row, metric
                            )
                    if len(corners) == 4 and all(
                        v is not None for v in corners.values()
                    ):
                        contrasts.append(
                            corners[(1, 1)]
                            - corners[(1, 0)]
                            - corners[(0, 1)]
                            + corners[(0, 0)]
                        )
                    else:
                        missing += 1
                interactions.append(
                    dict(
                        factors=[first, second],
                        metric=metric,
                        difference_in_differences=(
                            sum(contrasts) / len(contrasts)
                            if contrasts and not missing
                            else None
                        ),
                        retained_conditional_contrasts=contrasts,
                        missing_corner_groups=missing,
                        state="completed" if contrasts and not missing else "unknown",
                        basis="high-high minus high-low minus low-high plus low-low; supplied factor levels, no inferred distribution",
                    )
                )
        summaries.append(
            dict(candidate=name, scenario_ranges=ranges, pair_interactions=interactions)
        )
    paired = []
    for left, right in combinations(candidate_names, 2):
        for scenario in scenarios:
            for metric in metric_names:
                a, b = (
                    metric_value(lookup[(name, scenario["id"])], metric)
                    for name in (left, right)
                )
                paired.append(
                    dict(
                        left=left,
                        right=right,
                        scenario=scenario["id"],
                        metric=metric,
                        right_minus_left=(
                            b - a if a is not None and b is not None else None
                        ),
                        state=(
                            "completed"
                            if a is not None and b is not None
                            else "unknown"
                        ),
                    )
                )
    report = dict(
        schema="osr-paired-factorial-report/1",
        request_sha256=fingerprint(request),
        requested_cases=len(rows),
        evaluator_calls=calls,
        seed=seed,
        factors=deepcopy(factors),
        rows=rows,
        candidate_summaries=summaries,
        paired_comparisons=paired,
        all_cases_executed=all(row["evaluator_called"] for row in rows),
        all_cases_completed=all(row["state"] in SUCCESS for row in rows),
        physical_release=False,
        robust_qualified=False,
        probability_model=None,
        constraint_acceptance="caller results retained; no threshold or unknown-data waiver inferred",
    )
    if folder is not None:
        write_new(folder / "report.json", report)
    return report

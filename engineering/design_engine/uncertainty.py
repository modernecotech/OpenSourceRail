"""Finite in-domain neighbourhood and explicitly sourced interval endpoints.

The supplied evaluator executes the actual controlled model. Every proposal is
charged, including duplicate values served from the local sensitivity cache.
Holdout evaluations use a separate callback and always execute again; this is
independent execution, not evidence of measured calibration or physical validity.
Unknown objectives remain None. No probability distribution or global optimum
is inferred from a finite neighbourhood or two interval endpoints.
"""

from copy import deepcopy
import math

from .contracts import (
    canonical,
    checks_status,
    fingerprint,
    identity,
    problem,
    problem_fingerprint,
    variables,
)

DEFAULT_OBJECTIVES = ("metrics.defined_mass_kg", "installed_cost", "carbon")


def _objective(candidate, path):
    value = candidate
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    if value is None or isinstance(value, dict):
        return None
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("sensitivity objective must be finite scalar or unknown")
    return value


def _error_state(exc):
    return {
        "OutsideDomain": "outside-domain",
        "Unavailable": "unavailable",
        "BudgetExceeded": "budget-exceeded",
    }.get(
        type(exc).__name__,
        "budget-exceeded" if isinstance(exc, TimeoutError) else "failed",
    )


def sensitivity(
    charter,
    scope,
    baseline,
    evaluator,
    charge,
    *,
    max_proposals=64,
    objective_paths=DEFAULT_OBJECTIVES,
    uncertainty_intervals=(),
    holdout_evaluator=None,
):
    """Evaluate baseline/one-variable choices and bounds with fixed scope.

    ``evaluator(values, case)`` returns a normal source-bound design candidate;
    ``charge(1, phase)`` uses the caller's common budget. ``case`` identifies
    the proposed variable and endpoint. The optional holdout callback has the
    same signature but must be a separately executed confirmation function.
    Supplied intervals need variable, lower, upper, unit and basis_reference;
    endpoints must be inside the unchanged charter's declared variable domain.
    """
    charter = deepcopy(problem(charter))
    scope = deepcopy(identity(scope))
    baseline = variables(charter, deepcopy(baseline))
    if type(max_proposals) is not int or not 1 <= max_proposals <= 128:
        raise ValueError("bounded positive sensitivity proposal budget required")
    if (
        not isinstance(objective_paths, (tuple, list))
        or not 1 <= len(objective_paths) <= 16
        or any(not isinstance(p, str) or not p or len(p) > 128 for p in objective_paths)
        or len(objective_paths) != len(set(objective_paths))
    ):
        raise ValueError("distinct bounded objective paths required")
    if not callable(evaluator) or not callable(charge):
        raise ValueError("actual evaluator and common budget charge required")
    if holdout_evaluator is not None and (
        not callable(holdout_evaluator) or holdout_evaluator is evaluator
    ):
        raise ValueError("separate holdout evaluator required")
    if (
        not isinstance(uncertainty_intervals, (list, tuple))
        or len(uncertainty_intervals) > 32
    ):
        raise ValueError("bounded supplied uncertainty interval list required")
    problem_sha = problem_fingerprint(charter)
    fixed_scope_sha = fingerprint(scope)
    cases = [
        dict(id="baseline", arm="sensitivity", variable=None, values=deepcopy(baseline))
    ]
    for name, spec in charter["variables"].items():
        choices = spec["choices"] if spec["kind"] == "choice" else spec["bounds"]
        if len(choices) > 128:
            raise ValueError("variable choices exceed neighbourhood budget")
        for index, value in enumerate(choices):
            changed = variables(charter, {**baseline, name: value})
            if fingerprint(changed) == fingerprint(baseline):
                continue
            cases.append(
                dict(
                    id=f"{name}/{index}",
                    arm="sensitivity",
                    variable=name,
                    values=changed,
                )
            )
    interval_names = set()
    for index, interval in enumerate(uncertainty_intervals):
        required = {"variable", "lower", "upper", "unit", "basis_reference"}
        if not isinstance(interval, dict) or set(interval) != required:
            raise ValueError("exact sourced uncertainty interval fields required")
        name = interval["variable"]
        if (
            not isinstance(name, str)
            or name not in charter["variables"]
            or name in interval_names
        ):
            raise ValueError("unique declared uncertainty variable required")
        interval_names.add(name)
        if (
            interval["unit"] != charter["variables"][name]["unit"]
            or not isinstance(interval["basis_reference"], str)
            or not interval["basis_reference"].strip()
        ):
            raise ValueError("uncertainty unit and explicit source reference required")
        lo, hi = interval["lower"], interval["upper"]
        if (
            any(
                type(v) not in (int, float) or not math.isfinite(v)
                for v in (lo, hi, baseline[name])
            )
            or not lo <= baseline[name] <= hi
        ):
            raise ValueError(
                "finite ordered uncertainty interval containing baseline required"
            )
        for end, value in (("lower", lo), ("upper", hi)):
            changed = variables(charter, {**baseline, name: value})
            cases.append(
                dict(
                    id=f"holdout/{index}/{end}",
                    arm="holdout",
                    variable=name,
                    values=changed,
                    basis_reference=interval["basis_reference"],
                    unit=interval["unit"],
                )
            )
    if len(cases) > 1024:
        raise ValueError("sensitivity case plan exceeds retained-artifact bound")
    rows, cache = [], {}
    charged, oracle_calls, hits = 0, 0, 0
    exhausted = False
    for case in cases:
        row = dict(
            case=deepcopy(case),
            state="not-run",
            candidate=None,
            objectives=None,
            delta_from_baseline=None,
            cache_hit=False,
        )
        if exhausted or charged >= max_proposals:
            row["basis"] = "proposal budget exhausted; case retained without execution"
            rows.append(row)
            continue
        if case["arm"] == "holdout" and holdout_evaluator is None:
            row["basis"] = "no independently executed holdout adapter supplied"
            rows.append(row)
            continue
        try:
            charge(
                1,
                (
                    "sensitivity-proposal"
                    if case["arm"] == "sensitivity"
                    else "uncertainty-holdout-proposal"
                ),
            )
            charged += 1
            key = fingerprint(case["values"])
            if case["arm"] == "sensitivity" and key in cache:
                candidate = deepcopy(cache[key])
                row["cache_hit"] = True
                hits += 1
            else:
                oracle = (
                    evaluator if case["arm"] == "sensitivity" else holdout_evaluator
                )
                oracle_calls += 1
                candidate = oracle(deepcopy(case["values"]), deepcopy(case))
            if (
                not isinstance(candidate, dict)
                or candidate.get("problem_sha256") != problem_sha
                or fingerprint(candidate.get("identity")) != fixed_scope_sha
            ):
                raise ValueError(
                    "sensitivity evaluator changed the controlled problem or scoped identity"
                )
            if fingerprint(
                variables(charter, candidate.get("variables", {}))
            ) != fingerprint(case["values"]):
                raise ValueError(
                    "sensitivity evaluator returned another physical variable map"
                )
            state = checks_status(
                candidate.get("checks", {}),
                charter["applicability"]["mandatory_checks"],
            )
            if any(
                candidate.get(k) is not False
                for k in (
                    "physical_release",
                    "production_released",
                    "independently_accepted",
                )
            ):
                raise ValueError(
                    "sensitivity execution cannot grant physical or production acceptance"
                )
            canonical(candidate)
            objectives = {path: _objective(candidate, path) for path in objective_paths}
            row.update(
                state=state, candidate=deepcopy(candidate), objectives=objectives
            )
            if case["arm"] == "sensitivity":
                cache[key] = deepcopy(candidate)
        except (ValueError, RuntimeError, TimeoutError, OSError) as exc:
            # Cancellation is control flow for the durable parent job. Do not
            # convert it into a failed neighbour and continue the campaign.
            from .runtime import Cancelled

            if isinstance(exc, Cancelled):
                raise
            row.update(
                state=_error_state(exc),
                error=str(exc),
                basis="actual evaluation error retained; no fabricated candidate or objective",
            )
            exhausted = row["state"] == "budget-exceeded"
        rows.append(row)
    reference = rows[0]["objectives"]
    for row in rows:
        if reference is not None and row["objectives"] is not None:
            row["delta_from_baseline"] = {
                path: (
                    None
                    if reference[path] is None or row["objectives"][path] is None
                    else row["objectives"][path] - reference[path]
                )
                for path in objective_paths
            }
    return dict(
        schema="osr-finite-sensitivity/1",
        problem_sha256=problem_sha,
        identity=scope,
        baseline_variables=baseline,
        objective_paths=list(objective_paths),
        cases=rows,
        requested_cases=len(cases),
        proposals_charged=charged,
        oracle_calls=oracle_calls,
        cache_hits=hits,
        max_proposals=max_proposals,
        uncertainty_intervals=deepcopy(list(uncertainty_intervals)),
        source_references_verified=False,
        probabilistic_distribution_assumed=False,
        complete_interaction_coverage=False,
        measured_holdout_available=False,
        global_optimum_claimed=False,
        physical_robustness_accepted=False,
        verified_frontier=[],
        physical_release=False,
        production_released=False,
    )

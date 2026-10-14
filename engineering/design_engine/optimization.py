"""Equal-budget seeded constrained searches over existing physical adapters.

Unknown objectives are never replaced by zero. The search ranks only explicitly
available mass/quantity proxies and labels that frontier conditional; detailed
fault/holdout confirmation may invalidate any screening recommendation.
"""

from __future__ import annotations
from copy import deepcopy
import itertools
import math
import numpy as np

from .contracts import fingerprint, variables, problem_fingerprint


def dominates(left, right):
    if (
        not left
        or len(left) != len(right)
        or any(v is None or not math.isfinite(v) for v in [*left, *right])
    ):
        raise ValueError("known finite equivalent objective axes required")
    return all(a <= b for a, b in zip(left, right)) and any(
        a < b for a, b in zip(left, right)
    )


def frontier(rows):
    eligible = [r for r in rows if r["feasible_screen"]]
    return [
        r["id"]
        for r in eligible
        if not any(dominates(s["objectives"], r["objectives"]) for s in eligible)
    ]


def finite_space(charter):
    if any(v["kind"] != "choice" for v in charter["variables"].values()):
        return None
    keys = list(charter["variables"])
    choices = [v["choices"] for v in charter["variables"].values()]
    if math.prod(map(len, choices)) > 100000:
        raise ValueError("finite search space exceeds its enumerator budget")
    return [dict(zip(keys, row)) for row in itertools.product(*choices)]


def paired(charter, evaluator, *, seeds=(11, 29, 47), evaluations=32):
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.core.variable import Real, Integer, Choice
    from pymoo.core.mixed import MixedVariableGA
    from pymoo.operators.survival.rank_and_crowding import RankAndCrowding
    from pymoo.optimize import minimize

    if (
        not isinstance(evaluations, int)
        or not 4 <= evaluations <= 128
        or len(set(seeds)) < 2
        or len(seeds) > 8
    ):
        raise ValueError(
            "multiple distinct seeds and a bounded equal proposal budget required"
        )
    space = finite_space(charter)
    limit = min(evaluations, len(space)) if space is not None else evaluations
    trials = []
    all_rows = {}
    cache = {}
    cache_hits = 0
    oracle_calls = 0

    def evaluate(value, seed, arm):
        nonlocal cache_hits, oracle_calls
        value = variables(charter, value)
        key = fingerprint(value)
        if key in cache:
            cache_hits += 1
            candidate = deepcopy(cache[key])
            evaluator(None, seed, arm, True)
        else:
            candidate = evaluator(value, seed, arm, False)
            cache[key] = deepcopy(candidate)
            oracle_calls += 1
        metric = candidate["metrics"]
        mass = metric.get("defined_mass_kg")
        count = metric.get("attachment_count")
        if count is None:
            data = candidate.get("definition", {})
            count = len(
                data.get("contract", {}).get(
                    "parts", data.get("model", {}).get("instances", [])
                )
            )
        failed = any(
            c["state"] in {"failed", "outside-domain", "unavailable"}
            for c in candidate["checks"].values()
        )
        known = mass is not None and math.isfinite(mass)
        row = dict(
            id=candidate["id"],
            variables=deepcopy(value),
            objectives=[mass, count] if known else None,
            feasible_screen=known and not failed,
            evidence_state=candidate.get("evidence_state", "unknown"),
            seed=seed,
            arm=arm,
        )
        all_rows[key] = candidate
        return row

    class Problem(ElementwiseProblem):
        def __init__(self, seed):
            specs = {}
            for name, v in charter["variables"].items():
                specs[name] = (
                    Choice(options=v["choices"])
                    if v["kind"] == "choice"
                    else (
                        Integer(bounds=v["bounds"])
                        if v["kind"] == "integer"
                        else Real(bounds=v["bounds"])
                    )
                )
            super().__init__(vars=specs, n_obj=2, n_ieq_constr=1)
            self.rows = []
            self.seed = seed

        def _evaluate(self, x, out, *args, **kwargs):
            if len(self.rows) >= limit:
                raise RuntimeError("optimiser exceeded declared proposal budget")
            value = {k: (v.item() if hasattr(v, "item") else v) for k, v in x.items()}
            row = evaluate(value, self.seed, "optimiser")
            self.rows.append(row)
            # An infeasibility sentinel is solver-internal only; it is never
            # exported as a mass, price, resistance or engineering objective.
            out["F"] = (
                row["objectives"] if row["objectives"] is not None else [1e30, 1e30]
            )
            out["G"] = [-1 if row["feasible_screen"] else 1]

    for seed in seeds:
        model = Problem(seed)
        population = min(16, limit)
        minimize(
            model,
            MixedVariableGA(
                pop_size=population,
                n_offsprings=math.gcd(population, limit),
                survival=RankAndCrowding(),
            ),
            termination=("n_eval", limit),
            seed=int(seed),
            verbose=False,
            copy_algorithm=False,
            copy_termination=False,
        )
        proposals = len(model.rows)
        rng = np.random.default_rng(seed)
        control = []
        for index in range(proposals):
            if space is not None:
                value = space[int(rng.integers(len(space)))]
            else:
                value = {
                    name: (
                        rng.choice(v["choices"]).item()
                        if v["kind"] == "choice"
                        else (
                            int(rng.integers(v["bounds"][0], v["bounds"][1] + 1))
                            if v["kind"] == "integer"
                            else float(rng.uniform(*v["bounds"]))
                        )
                    )
                    for name, v in charter["variables"].items()
                }
            control.append(evaluate(value, seed, "random-control"))
        trials.append(
            dict(
                seed=int(seed),
                equal_proposal_budget=proposals,
                optimiser=model.rows,
                random_control=control,
                conditional_screen_frontier=frontier(model.rows),
                random_screen_frontier=frontier(control),
                equal_budget=True,
                physical_release=False,
            )
        )
    return dict(
        schema="osr-multi-fidelity-search/1",
        problem_sha256=problem_fingerprint(charter),
        ranking_axes=["defined component mass", "defined attachment/part count proxy"],
        unknown_axes=[
            "complete installed/lifecycle cost",
            "production and disruption",
            "imported content",
            "carbon",
            "qualification",
        ],
        trials=trials,
        candidates=list(all_rows.values()),
        cache_hits=cache_hits,
        oracle_calls=oracle_calls,
        proposals=sum(2 * t["equal_proposal_budget"] for t in trials),
        verified_frontier=[],
        surrogate_used=False,
        global_optimum_claimed=False,
        physical_release=False,
    )

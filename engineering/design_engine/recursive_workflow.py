"""Controlled recursive-search presets and common-worker execution.

Clients may tune resources and objectives, never remove a required check. A
numerical incumbent is conditional on this declared model and finite search;
open installation/physical checks remain in every candidate and review export.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from .contracts import fingerprint
from .store import write_new

GENERATED = {"mechanical-cleat", "civil-steel-beam"}
TUNING = {
    "evaluations", "iterations", "confirmations", "objective_axes",
    "real_intervals", "refinements", "stall_rounds", "finite_exhaustive",
    "max_space", "seed",
}


def policy(charter, supplied):
    from .recursive_search import validate_policy

    if not isinstance(supplied, dict) or set(supplied) - TUNING:
        raise ValueError("recursive controls cannot change the verification matrix")
    kind = charter["adapter"]
    if kind in GENERATED:
        screening = ["geometry", "manufacturing"]
        native = ["mass_inertia", "linear_service", "load_equilibrium",
                  "mesh_refinement", "independent_benchmark"]
    elif kind in {"panel", "roof"}:
        screening = ["geometry"]
        native = ["nominal_deflection", "mesh_refinement", "single_attachment_loss",
                  "combined_pressure_fault"]
    elif kind in {"viaduct", "foundation"}:
        # Actual civil screening supplies these checks. Interfaces and degraded
        # service need qualification beyond the native demand/refinement study;
        # retaining their open states must not prevent that study being run.
        screening = ["geometry", "mass_inertia", "service"]
        native = ["refinement"]
    else:
        raise ValueError("this adapter has no controlled recursive native-confirmation preset")
    mandatory = charter["applicability"]["mandatory_checks"]
    count = min(128, charter["budget"]["evaluations"])
    controls = dict(evaluations=count, objective_axes=["defined_mass_kg"])
    controls.update(deepcopy(supplied))
    controls.update(screening_checks=screening, native_checks=native,
                    physical_checks=[key for key in mandatory if key not in screening + native])
    return validate_policy(charter, controls)


def supported(charter):
    return charter["adapter"] in GENERATED | {"panel", "roof", "viaduct", "foundation"}


def execute(req, evaluate, budget, folder, *, confirm):
    """Run the policy using actual common callbacks and immutable progress frames."""
    from .recursive_search import recursive_search

    folder = Path(folder)
    seen = {}
    frames = 0
    previous = None

    def checkpoint(report):
        nonlocal frames, previous
        changed = []
        for row in report["candidates"]:
            digest = fingerprint(row)
            if seen.get(row["id"]) != digest:
                changed.append(row)
                seen[row["id"]] = digest
        frame = {key: value for key, value in report.items() if key not in {"candidates", "lineage"}}
        frame.update(changed_candidates=changed, lineage=report["lineage"],
                     request_sha256=fingerprint(req), frame=frames)
        stable = fingerprint({key: value for key, value in frame.items() if key != "frame"})
        if stable == previous:
            return
        write_new(folder / "recursive-progress" / f"{frames:06d}.json", frame)
        previous = stable
        frames += 1

    def oracle(values, phase, parent):
        # Every attempted compilation consumes budget, including invalid geometry.
        budget.charge(1, "recursive-" + phase)
        return evaluate(values, lambda count, name: budget.charge(0, name))

    result = recursive_search(
        req["problem"], oracle, confirm,
        context=dict(identity=req["identity"], source_sha256=req["dependencies"],
                     toolchain=req["toolchain"], request=req),
        initial=req["candidates"], policy=req["recursive"],
        checkpoint=checkpoint,
        # The worker provides these classes to preserve cancellation semantics.
        stop_exceptions=budget.control_exceptions,
    )
    # Semantic decisions exclude directories, raw execution timings and log bytes.
    trace = [{key: deepcopy(value) for key, value in event.items()
              if key not in {"result_sha256", "cache_hit"}} for event in result["lineage"]]
    result["decision_trace_sha256"] = fingerprint(trace)
    result["determinism_scope"] = (
        "same request, source, actual tools and completed evaluation budget; "
        "raw CAD/log metadata and resource-interrupted prefixes are not byte-reproducibility claims"
    )
    result["common_evaluations_spent"] = budget.spent
    write_new(folder / "recursive-search.json", result)
    return result

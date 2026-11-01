"""Bounded diversity-first next-evaluator requests, independent of acceptance."""
from collections import defaultdict
from math import isfinite

from engineering.station_rail.common import identity

STAGES = (
    "geometry, quantities and provisional process/cost",
    "beam/plate/shell, load-path and manufacturing-domain checks",
    "coarse numerical structural and coupled models",
    "refined convergence, thermal and multidisciplinary models",
    "detailed CAD, joints, tolerances and physical correlation",
)


def plan(rows, retained_candidate_ids, *, maximum_tasks, runtime_s, memory_bytes, source_sha256):
    """Request one cheap next evaluation per family before deeper refinement.

    Cost ranks experiments only within each family. Unknown physics cannot be
    used as a zero penalty or confer admission to a native/physical evaluator.
    Requests remain queued; this function dispatches no numerical work.
    """
    if (type(maximum_tasks) is not int or maximum_tasks < 0
            or type(memory_bytes) is not int or memory_bytes <= 0
            or type(runtime_s) not in (int, float) or not isfinite(runtime_s) or runtime_s <= 0
            or not isinstance(source_sha256, dict) or not source_sha256):
        raise ValueError("Explicit finite task and resource budgets and source epoch required")
    by_id = {r["candidate_id"]: r for r in rows}
    retained = set(retained_candidate_ids)
    if len(by_id) != len(rows) or not retained <= set(by_id):
        raise ValueError("Unique candidate coverage and matching retained identities required")
    for row in rows:
        if (row.get("execution") != "completed" or row.get("fidelity") != 0
                or row.get("evaluation_id") != identity({k:v for k,v in row.items() if k!="evaluation_id"})):
            raise ValueError("Sealed completed stage-zero evaluations required before planning refinement")
    families = defaultdict(list)
    for candidate_id in sorted(retained):
        row = by_id[candidate_id]
        cost = row["metrics"]["scoped_installed_base_iqd"]
        if type(cost) not in (int, float) or not isfinite(cost) or cost < 0:
            raise ValueError("Finite explicit experiment-order cost required")
        families[row["descriptor"]["family"]].append(row)
    requests = []
    for family, alternatives in sorted(families.items()):
        row = min(alternatives, key=lambda r: (r["metrics"]["scoped_installed_base_iqd"], r["candidate_id"]))
        request = dict(candidate_id=row["candidate_id"], parent_evaluation_id=row["evaluation_id"],
            family=family, completed_stage=0, requested_stage=1, execution="queued",
            admission="definition-and-domain-review-required",
            required_checks=["moving axle loads and unequal rail loading", "cracking/prestress or composite-action hypothesis",
                "shear, torsion, local stability and connections", "lifting, bearings and reinforcement/process access"],
            maximum_runtime_s=runtime_s, maximum_memory_bytes=memory_bytes,
            source_sha256=source_sha256, physical_accepted=False, engineering_accepted=False)
        request["request_id"] = identity(request)
        requests.append(request)
    queued = requests[:maximum_tasks]
    deferred = requests[maximum_tasks:]
    result = dict(schema="osr-multifidelity-frontier/1", stages=list(STAGES),
        executed_stages=[0], requests=queued, deferred_requests=deferred,
        retained_candidate_ids=sorted(retained), maximum_tasks=maximum_tasks,
        numerical_jobs_dispatched=0, integrated_selection=None,
        ranking_purpose="next-experiment; family coverage before within-family partial-cost preference",
        physical_accepted=False, engineering_accepted=False)
    result["frontier_id"] = identity(result)
    return result

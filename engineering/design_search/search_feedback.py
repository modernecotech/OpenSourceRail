"""Bounded research-only parent priorities from cost and supported axial models.

Every valid completed stage-zero candidate retains positive sampling weight.
Model holds and unassessed stiffness are never zero-displacement objectives or
whole-body failures. Axial comparisons remain inside an explicit comparable
family/topology/load-policy/model cohort; there is no cross-cohort physics front.
"""
from __future__ import annotations

from copy import deepcopy
from math import isclose, isfinite, sqrt
from pathlib import Path
import sys

from engineering.station_rail import ROOT, common
from engineering.station_rail.common import digest, identity
from . import grammar_structure, native_refinement, native_search, search_archive

PRODUCER = "engineering/design_search/search_feedback.py"
OBJECTIVES = ("nominal_stock_kg", "factory_gate_base_iqd", "factory_process_hours")
SUPPORTED = "rigid-axial-graph-analytical-only"
STATUSES = {SUPPORTED, "graph-mechanism-model-only", "outside-linear-domain-analytical",
            "axial-numerical-failure", "axial-model-domain-unavailable"}
FLAGS = dict(native_search.FLAGS, physical_journey_completed=False, installed_mass_complete=False)
MODULES = ((common, "engineering/station_rail/common.py"),
           (grammar_structure, grammar_structure.PRODUCER),
           (native_refinement, native_refinement.PRODUCER),
           (native_search, native_search.PRODUCER),
           (search_archive, search_archive.PRODUCER))
LOADED = {name: digest(module.__file__) for module, name in MODULES}
LOADED[PRODUCER] = digest(__file__)


def _sealed(value, key, label):
    if (not isinstance(value, dict) or not native_search._hex(value.get(key))
            or value[key] != identity({k: v for k, v in value.items() if k != key})):
        raise ValueError(label + " identity differs")


def _positive(value, label, *, zero=False):
    try:
        valid = type(value) in (int, float) and isfinite(value) and (value >= 0 if zero else value > 0)
    except (OverflowError, ValueError):
        valid = False
    if not valid:
        raise ValueError("Finite " + ("nonnegative " if zero else "positive ") + label + " required")
    return value


def _sources(engine, supplied):
    root = Path(getattr(engine, "root", ROOT))
    if not isinstance(supplied, dict) or not supplied:
        raise ValueError("Explicit current source epoch required")
    if digest(__file__) != LOADED[PRODUCER]:
        raise ValueError("Loaded feedback implementation changed")
    for module, name in MODULES:
        if digest(module.__file__) != LOADED[name]:
            raise ValueError("Loaded feedback dependency changed: " + name)
    for name, expected in LOADED.items():
        if supplied.get(name) != expected:
            raise ValueError("Feedback executing source is absent or stale: " + name)
    for name, expected in supplied.items():
        if not isinstance(name, str):
            raise ValueError("Feedback source paths must be explicit relative strings")
        path = Path(name)
        if (path.is_absolute() or ".." in path.parts
                or not native_search._hex(expected) or digest(root / path) != expected):
            raise ValueError("Feedback source epoch differs: " + str(name))
    return dict(sorted(supplied.items()))


def _subset_sources(values, epoch, label):
    if not isinstance(values, dict) or not values or any(epoch.get(k) != v for k, v in values.items()):
        raise ValueError(label + " source epoch differs")


def _rows(values, epoch):
    result = {}
    requirements, assumptions = set(), set()
    for row in values:
        if len(result) >= 100_000:
            raise ValueError("Feedback parent pool exceeds its resource domain")
        _sealed(row, "evaluation_id", "Stage-zero evaluation")
        cid, did = row.get("candidate_id"), row.get("definition_id")
        if not native_search._hex(cid) or not native_search._hex(did) or cid in result:
            raise ValueError("Unique physical candidate and definition identities required")
        request = row.get("request", {})
        descriptor = row.get("descriptor", {})
        if (not isinstance(request, dict) or request.get("candidate_id") != cid
                or request.get("definition_id") != did or request.get("fidelity") != 0
                or not native_search._hex(request.get("requirements"))
                or not native_search._hex(request.get("assumption_id"))
                or not isinstance(descriptor, dict)
                or any(not isinstance(descriptor.get(k), str) or not descriptor[k] for k in ("family", "topology"))):
            raise ValueError("Stage-zero physical, requirement or descriptor binding differs")
        if (row.get("execution") != "completed" or row.get("fidelity") != 0
                or row.get("engineering_screen") != "unknown"
                or any(row.get(k) is not False for k in ("physical_accepted", "engineering_accepted",
                    "configuration_adopted", "manufacturing_release", "operating_release", "physical_journey_completed", "selected_reference_changed"))
                or row.get("complete_installed_mass_kg") is not None
                or row.get("complete_installed_cost_iqd") is not None):
            raise ValueError("Completed provisional stage-zero evidence without release required")
        _subset_sources(request.get("evaluator_sources"), epoch, "Stage-zero evaluator")
        metrics, cost = row.get("metrics", {}), row.get("cost_estimate", {})
        for key in OBJECTIVES:
            _positive(metrics.get(key), "stage-zero " + key)
        if (cost.get("candidate_id") != cid or cost.get("assumption_id") != request["assumption_id"]
                or cost.get("scenarios_iqd", {}).get("base") != metrics["factory_gate_base_iqd"]
                or cost.get("process_hours", {}).get("base") != metrics["factory_process_hours"]):
            raise ValueError("Stage-zero cost metric or estimate identity differs")
        requirements.add(request["requirements"])
        assumptions.add(request["assumption_id"])
        result[cid] = row
    if len(requirements) > 1 or len(assumptions) > 1:
        raise ValueError("Cost feedback requires common functional requirements and cost assumptions")
    return result


def _assessment(wrapper, row, epoch):
    assessment = wrapper.get("assessment")
    if assessment is None:
        return None
    _sealed(assessment, "assessment_id", "Axial assessment")
    if (assessment.get("schema") != "osr-native-axial-refinement-assessment/1"
            or assessment.get("candidate_id") != row["candidate_id"]
            or assessment.get("definition_id") != row["definition_id"]
            or assessment.get("requirement_revision") != row["request"]["requirements"]
            or assessment.get("axial_status") not in STATUSES
            or assessment.get("scope") != grammar_structure.SCOPE
            or assessment.get("whole_body_rejected") is not False
            or assessment.get("integrated_selection") is not None
            or assessment.get("available_force_map_id") is not None
            or any(assessment.get(k) is not False for k in native_refinement.FLAGS)
            or assessment.get("runtime") != native_refinement._runtime()):
        raise ValueError("Axial assessment physical, definition, requirement, runtime or model binding differs")
    _subset_sources(assessment.get("source_sha256"), epoch, "Axial assessment")
    tasks = assessment.get("next_tasks")
    if not isinstance(tasks, list) or any(not isinstance(task, dict)
            or set(task) != {"kind", "state", "detail"} or task["state"] != "open"
            or any(not isinstance(task[k], str) or not task[k] for k in ("kind", "detail")) for task in tasks):
        raise ValueError("Typed open axial-model tasks required")
    if assessment.get("axial_status") != SUPPORTED:
        return assessment
    basis, diagnostic, reference = [assessment.get(k) for k in ("load_basis", "axial_diagnostic", "axial_reference")]
    if not isinstance(basis, dict) or not isinstance(diagnostic, dict) or not isinstance(reference, dict):
        raise ValueError("Supported axial assessment needs load basis, diagnostic and reference")
    if (not native_search._hex(assessment.get("input_graph_id"))
            or not native_search._hex(assessment.get("physical_graph_id"))
            or diagnostic.get("input_graph_id") != assessment["input_graph_id"]
            or diagnostic.get("physical_graph_id") != assessment["physical_graph_id"]
            or type(diagnostic.get("mechanism_count")) is not int or diagnostic["mechanism_count"] != 0
            or diagnostic.get("necessary_rigidity_screen") != "pass"
            or diagnostic.get("model_scope") != grammar_structure.SCOPE
            or any(diagnostic.get(k) is not False for k in grammar_structure.FLAGS)
            or assessment.get("analytical_linear_domain_limit") != 0.01):
        raise ValueError("Supported axial graph or domain binding differs")
    ratio = _positive(assessment.get("analytical_maximum_member_relative_displacement_to_length"), "axial relative motion")
    if ratio >= 0.01:
        raise ValueError("Supported axial assessment is outside its linear model domain")
    mass = _positive(basis.get("known_body_stock_kg"), "axial stock mass")
    _positive(basis.get("sprung_mass_hypothesis_kg"), "axial own-candidate sprung mass")
    if (type(basis.get("normal_people")) is not int or basis["normal_people"] <= 0
            or basis.get("missing_installed_mass_kg") is not None
            or not isclose(mass, row["metrics"]["nominal_stock_kg"], rel_tol=1e-12, abs_tol=1e-9)):
        raise ValueError("Axial load basis differs from the same candidate's accounted stock")
    displacements = reference.get("displacements_m")
    if not isinstance(displacements, dict) or not displacements:
        raise ValueError("Supported axial displacement field required")
    for vector in displacements.values():
        if (not isinstance(vector, list) or len(vector) != 3
                or any(type(v) not in (int, float) or not isfinite(v) for v in vector)):
            raise ValueError("Finite three-axis displacement vectors required")
    _positive(max(sqrt(sum(v*v for v in u)) for u in displacements.values()), "axial maximum displacement")
    return assessment


def plan(engine, rows, observations, *, source_sha256, maximum_weight=4):
    """Reward known research fronts, preserving every valid parent with weight >=1."""
    if type(maximum_weight) is not int or not 1 <= maximum_weight <= 4:
        raise ValueError("Feedback maximum weight must be an explicit integer from one to four")
    epoch = _sources(engine, source_sha256)
    by_id = _rows(rows, epoch)
    if not isinstance(observations, list) or len(observations) > 64:
        raise ValueError("At most 64 explicit axial observations per feedback plan required")
    seen, cohorts, summaries, tasks, supported, context_policies = set(), {}, [], [], set(), {}
    for wrapper in observations:
        if not isinstance(wrapper, dict):
            raise ValueError("Explicit observation wrapper required")
        cid = wrapper.get("candidate_id")
        if cid not in by_id or cid in seen or wrapper.get("parent_evaluation_id") != by_id[cid]["evaluation_id"]:
            raise ValueError("Unique observation must bind an exact completed parent evaluation")
        if not native_search._hex(wrapper.get("comparison_context_id")):
            raise ValueError("Explicit comparable functional load-policy context required")
        seen.add(cid)
        row = by_id[cid]
        assessment = _assessment(wrapper, row, epoch)
        status = "unassessed" if assessment is None else assessment["axial_status"]
        summaries.append(dict(candidate_id=cid, parent_evaluation_id=row["evaluation_id"],
            comparison_context_id=wrapper["comparison_context_id"], status=status,
            assessment_id=None if assessment is None else assessment["assessment_id"],
            own_load_basis=None if assessment is None else deepcopy(assessment["load_basis"])))
        if assessment is not None:
            tasks.extend(dict(candidate_id=cid, assessment_id=assessment["assessment_id"], **deepcopy(task))
                         for task in assessment["next_tasks"])
        if status != SUPPORTED:
            continue
        supported.add(cid)
        policy = dict(requirement_revision=assessment["requirement_revision"],
            normal_people=assessment["load_basis"]["normal_people"],
            own_candidate_accounted_sprung_mass=True, complete_installed_mass=False)
        context = wrapper["comparison_context_id"]
        if context in context_policies and context_policies[context] != policy:
            raise ValueError("One comparison context cannot mix functional load policies")
        context_policies[context] = policy
        descriptor = dict(row["descriptor"], comparison_context_id=context,
                          model_scope=assessment["scope"], load_policy_id=identity(policy))
        cohort_id = identity(descriptor)
        maximum = max(sqrt(sum(v*v for v in u)) for u in assessment["axial_reference"]["displacements_m"].values())
        cohorts.setdefault(cohort_id, []).append(dict(candidate_id=cid, descriptor=descriptor,
            metrics={**row["metrics"], "axial_model_displacement_m": maximum}))
    cost = search_archive.archive(engine, list(by_id.values()), OBJECTIVES, ("family", "topology"))
    physics, physics_front = [], set()
    for cohort_id, members in sorted(cohorts.items()):
        archive = search_archive.archive(engine, members, (*OBJECTIVES, "axial_model_displacement_m"),
            ("family", "topology", "comparison_context_id", "model_scope", "load_policy_id"))
        physics.append(dict(cohort_id=cohort_id, descriptor=members[0]["descriptor"], archive=archive))
        physics_front.update(archive["retained_candidate_ids"])
    cost_front = set(cost["retained_candidate_ids"])
    unassessed = sorted(set(by_id)-seen | {r["candidate_id"] for r in summaries if r["status"] == "unassessed"})
    tasks.extend(dict(candidate_id=cid, parent_evaluation_id=by_id[cid]["evaluation_id"],
        assessment_id=None, kind="axial-model-assessment", state="open",
        detail="Establish a source-bound model-domain assessment before introducing a stiffness objective; current stiffness remains unknown")
        for cid in unassessed)
    parents = [dict(candidate_id=cid, parent_evaluation_id=row["evaluation_id"],
                    weight=min(maximum_weight, 1 + int(cid in cost_front) + 2*int(cid in physics_front)))
               for cid, row in sorted(by_id.items())]
    result = dict(schema="osr-search-parent-feedback/1", purpose="next-experiment",
        parents=parents, cost_archive=cost, axial_archives=physics,
        observations=sorted(summaries, key=lambda row: row["candidate_id"]),
        coverage=dict(parent_count=len(by_id), observation_count=len(observations),
            supported_axial_candidate_ids=sorted(supported),
            held_candidate_ids=sorted(seen-supported-{r["candidate_id"] for r in summaries if r["status"] == "unassessed"}),
            unassessed_candidate_ids=unassessed),
        model_tasks=sorted(tasks, key=lambda task: (task["candidate_id"], task["kind"])),
        policy=dict(version="positive-baseline-cost-plus-supported-axial/1", maximum_weight=maximum_weight,
            baseline_weight=1, cost_front_bonus=1, supported_axial_front_bonus=2,
            sampling="Global positive-weight parent sampling; this preserves opportunity, not family allocation or guaranteed selection",
            unknown_or_held="No axial objective or physical penalty; retain baseline and any supported cost bonus",
            comparison="Separate family/topology/functional-context/model/load-policy cohorts; each candidate keeps its own accounted load"),
        verification_scope="Source, identity, field and model-domain consistency of caller-verified records; no independent mechanical replay or measurement authentication",
        source_sha256=epoch, runtime_python=sys.version, **FLAGS)
    if _sources(engine, source_sha256) != epoch:
        raise ValueError("Feedback source epoch changed during planning")
    result["feedback_id"] = identity(result)
    return result

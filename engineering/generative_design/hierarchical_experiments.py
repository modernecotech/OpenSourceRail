"""Versioned experimental adoption and truthful, bounded hierarchy pilots.

Role names describe deterministic workers. No LLM invocation, appointed engineering
review, qualified full-bay solver or physical/manufacturing release is implied.
"""

from __future__ import annotations

from copy import deepcopy
import difflib
from hashlib import sha256
import json
import math
import re
import subprocess
from pathlib import Path

from . import coverage

ROOT = coverage.ROOT
FLAGS = dict(
    design_complete=False,
    engineering_design_complete=False,
    manufacturing_release=False,
    physical_release=False,
)
KINDS = {"component", "assembly", "system", "software-subsystem", "work-package"}


def digest(value):
    return sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def _hold(item, capability, inputs, scenarios):
    return dict(
        id="capability-" + digest([item, capability])[:16],
        item_id=item,
        capability=capability,
        missing_inputs=list(inputs),
        scenarios=list(scenarios),
        acceptance=[
            "Independent analytical/reference benchmark and adverse cases pass",
            "Exact item/interface IDs, units, validity domain and numerical uncertainty retained",
            "Parent integration evaluates the same candidate revision and scenarios",
        ],
        state="HOLD",
        **FLAGS,
    )


def plan():
    """Map every controlled item/package, never infer coverage from a role label."""
    scope = json.loads(coverage.SCOPE.read_text())
    audit = coverage.audit(scope)
    rows, requests = [], []
    roots = {
        "mechanical": "vehicle-assembly",
        "civil": "complete-viaduct-bay",
        "station": "station-assembly",
        "factory": "factory-assembly",
        "integration": "integration-assembly",
    }
    for identity in sorted(set(roots.values()) | {"software-subsystem"}):
        missing = _hold(
            identity,
            "qualified whole-assembly integration including every interface and operating stage",
            [
                "Accepted exact interface revisions",
                "Material/site/operating basis",
                "Independent integration evidence",
            ],
            ["normal", "adverse", "construction-maintenance", "fault"],
        )
        requests.append(missing)
        rows.append(
            dict(
                id=identity,
                kind=(
                    "software-subsystem"
                    if identity == "software-subsystem"
                    else "assembly"
                ),
                parents=["railway-system"],
                function=identity,
                requirements=["Complete accepted interface and qualification scope"],
                scenarios=missing["scenarios"],
                evaluators=[],
                missing_capability_ids=[missing["id"]],
                **FLAGS,
            )
        )
    root_request = _hold(
        "railway-system",
        "whole railway coupled qualification",
        [
            "Accepted architecture/loading",
            "Site and operating rules",
            "Validated discipline models",
        ],
        ["normal", "adverse", "fault"],
    )
    requests.append(root_request)
    rows.append(
        dict(
            id="railway-system",
            kind="system",
            parents=[],
            function="Safe railway transport",
            requirements=["All affected subsystem checks at accepted fidelity"],
            scenarios=root_request["scenarios"],
            evaluators=[],
            missing_capability_ids=[root_request["id"]],
            **FLAGS,
        )
    )
    partial = {
        "LM3-FRP-010": "mechanical_detail.assess",
        "BUY-LM3-CAR-A900": "mechanical_detail.assess",
        "BASIS-CONFIGURATION": "mechanical_detail.assess",
        **dict.fromkeys(
            ["CIV-FRP-100", "CIV-FRP-110", "CIV-FRP-120"], "civil_detail.assess"
        ),
    }
    components = {}
    for package in scope["work_packages"]:
        identifier = package["id"]
        scenarios = [
            "source configuration retained",
            "provisional loads",
            "adverse interface case",
        ]
        missing = _hold(
            identifier,
            "full package evaluator: " + package["title"],
            list(package["required_gates"]),
            scenarios,
        )
        requests.append(missing)
        rows.append(
            dict(
                id=identifier,
                kind="work-package",
                parents=[roots[package["domain"]]],
                function=package["title"],
                requirements=deepcopy(package["completion_predicate"]),
                scenarios=scenarios,
                dependency_item_ids=list(package["dependencies"]),
                evaluators=(
                    [
                        dict(
                            id=partial[identifier],
                            coverage="partial declared returned check IDs only",
                        )
                    ]
                    if identifier in partial
                    else []
                ),
                missing_capability_ids=[missing["id"]],
                **FLAGS,
            )
        )
        for source in package["authoritative_sources"]:
            for source_id in source["ids"]:
                key = source["path"] + "#" + source_id
                row = components.setdefault(
                    key,
                    dict(
                        id="component-" + digest(key)[:20],
                        kind="component",
                        source_id=source_id,
                        source_path=source["path"],
                        parents=[],
                        function="Controlled source item " + source_id,
                        requirements=[
                            "Exact source-qualified identity and package acceptance scope"
                        ],
                        scenarios=scenarios,
                        evaluators=[],
                        missing_capability_ids=[],
                        **FLAGS,
                    ),
                )
                row["parents"].append(identifier)
    for key, item in sorted(components.items()):
        missing = _hold(
            item["id"],
            "validated evaluator for " + key,
            [
                "Controlled item geometry/interfaces",
                "Accepted material and load cases",
                "Independent benchmark",
            ],
            item["scenarios"],
        )
        requests.append(missing)
        item["missing_capability_ids"] = [missing["id"]]
        rows.append(item)
    value = dict(
        schema="osr-hierarchical-experiment-plan/1",
        items=rows,
        missing_capabilities=requests,
        work_package_count=audit["work_package_count"],
        controlled_component_count=len(components),
        source_scope_sha256=coverage.sha(coverage.SCOPE),
        physical_feedback="Explicit bounded coupled iterations, never cyclic revision edges",
        **FLAGS,
    )
    validate_plan(value)
    return value


def _acyclic(parents):
    remaining = {key: set(values) for key, values in parents.items()}
    if any(set(values) - set(parents) for values in remaining.values()):
        raise ValueError("unknown provenance or parent identity")
    while remaining:
        ready = {key for key, values in remaining.items() if not values}
        if not ready:
            raise ValueError("cyclic revision or item graph")
        remaining = {
            key: values - ready for key, values in remaining.items() if key not in ready
        }


def validate_plan(value):
    items = value["items"]
    identities = [item["id"] for item in items]
    if len(set(identities)) != len(identities):
        raise ValueError("unique hierarchy identities required")
    requests = {request["id"] for request in value["missing_capabilities"]}
    for item in items:
        if (
            item["kind"] not in KINDS
            or not item["function"]
            or not item["requirements"]
            or not item["scenarios"]
        ):
            raise ValueError("typed item function, requirements and scenarios required")
        if not item["evaluators"] and not item["missing_capability_ids"]:
            raise ValueError(
                "every item requires an evaluator or precise missing-capability request"
            )
        if set(item["missing_capability_ids"]) - requests:
            raise ValueError("missing capability request reference")
        if any(item.get(key) is not False for key in FLAGS):
            raise ValueError("experimental plan cannot release designs")
    _acyclic({item["id"]: item["parents"] for item in items})
    expected = {
        p["id"] for p in json.loads(coverage.SCOPE.read_text())["work_packages"]
    }
    if {item["id"] for item in items if item["kind"] == "work-package"} != expected:
        raise ValueError("exact controlled work-package coverage required")
    return True


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def comparison_context(item_id, function, requirements, scenarios):
    """Caller supplies controlled identities; changed scope cannot compare equal."""
    if not item_id or not function or not requirements or not scenarios:
        raise ValueError("nonempty item/function/requirements/scenarios required")
    return dict(
        item_id=item_id,
        function=function,
        requirements=deepcopy(requirements),
        scenarios=deepcopy(scenarios),
    )


def evaluation(candidate, *, worker, checks, execution_status="completed"):
    """Bind an executor response to exact candidate bytes and comparison scope."""
    if not isinstance(worker, str) or not worker.strip():
        raise ValueError("explicit evaluation worker identity required")
    return dict(
        candidate_sha256=digest(candidate),
        context_sha256=digest(candidate["comparison_context"]),
        worker=worker,
        checks=deepcopy(checks),
        execution_status=execution_status,
    )


def evaluate_promotion(baseline, candidate, policy, *, evidence, history=()):
    """Only controlled, independently checked, parent-safe improvements adopt.

    Evidence is supplied by the trusted executor/controller, outside a proposal.
    This gate adopts computational experimental revisions, never physical designs.
    """
    result = dict(
        candidate_id=candidate["id"],
        baseline_id=baseline["id"],
        disposition="HOLD",
        reasons=[],
        experimental_revision=None,
        work_requests=[],
        **FLAGS,
    )
    why = result["reasons"]
    if baseline["comparison_context"] != candidate["comparison_context"]:
        why.append("function, requirements or scenarios changed")
    if any(candidate.get(flag, False) is not False for flag in FLAGS):
        raise ValueError("candidate cannot claim release")
    paths = candidate.get("changed_paths", [])
    if any(
        not isinstance(path, str)
        or Path(path).is_absolute()
        or ".." in Path(path).parts
        or path.startswith("./")
        for path in paths
    ):
        raise ValueError("canonical repository-relative changed paths required")
    if any(
        path.startswith(prefix)
        for path in candidate.get("changed_paths", [])
        for prefix in policy["protected_paths"]
    ):
        why.append(
            "acceptance machinery or solver policy change needs its own independent review"
        )
    if not evidence or any(
        row.get("execution_status") != "completed" for row in evidence
    ):
        why.append(
            "inconclusive execution; timeout/cancellation is not passing evidence"
        )
    if any(
        row.get("candidate_sha256") != digest(candidate)
        or row.get("context_sha256") != digest(candidate["comparison_context"])
        for row in evidence
    ):
        raise ValueError(
            "evidence belongs to a different candidate or comparison context"
        )
    if not candidate.get("producer") or any(not row.get("worker") for row in evidence):
        raise ValueError("explicit producer and evidence worker identities required")
    checks = {}
    for row in evidence:
        for check in row["checks"]:
            identity = check["id"]
            if (
                identity in checks
                or check.get("state") not in {"pass", "fail", "unknown"}
                or not check.get("evidence_ref")
            ):
                raise ValueError(
                    "unique actual check evidence with explicit state required"
                )
            checks[identity] = dict(check, worker=row["worker"])
    groups = [
        policy[key]
        for key in ("mandatory_checks", "independent_checks", "parent_checks")
    ]
    if any(not isinstance(group, list) for group in groups):
        raise ValueError("explicit required-check lists required")
    flattened = [key for group in groups for key in group]
    if len(flattened) != len(set(flattened)) or any(
        not isinstance(key, str) or not key for key in flattened
    ):
        raise ValueError(
            "distinct mandatory, independent and parent check identities required"
        )
    expected = (
        set(policy["mandatory_checks"])
        | set(policy["independent_checks"])
        | set(policy["parent_checks"])
    )
    if (
        not expected
        or not policy["mandatory_checks"]
        or not policy["independent_checks"]
        or not policy["parent_checks"]
    ):
        raise ValueError(
            "nonempty mandatory, independent and affected-parent checks required"
        )
    failure = sorted(key for key, row in checks.items() if row["state"] == "fail")
    if failure:
        result["disposition"] = "REJECT"
        why.extend("failed " + key for key in failure)
    missing = sorted(
        key
        for key in expected
        if checks.get(key, {}).get("state") not in {"pass", "fail"}
    )
    why.extend("missing mandatory evidence " + key for key in missing)
    result["work_requests"].extend(
        _hold(
            candidate["comparison_context"]["item_id"],
            "revision-bound mandatory check " + key,
            ["Actual completed check evidence for candidate " + candidate["id"]],
            candidate["comparison_context"]["scenarios"],
        )
        for key in missing
    )
    for key in policy["independent_checks"]:
        if key in checks and checks[key]["worker"] in {
            candidate["producer"],
            *candidate.get("contributors", []),
        }:
            why.append(
                "independent check authored by candidate producer/contributor: " + key
            )
    axes = policy["objective_axes"]
    if not axes or len(axes) != len(set(axes)):
        raise ValueError("declared comparable objectives required")
    improved = False
    for axis in axes:
        left, right = baseline["objectives"].get(axis), candidate["objectives"].get(
            axis
        )
        if (
            not isinstance(left, dict)
            or not isinstance(right, dict)
            or any(
                not row.get("basis")
                or not row.get("evidence_ref")
                or row.get("state") not in {"computed", "measured", "counted"}
                for row in (left, right)
            )
            or any(
                not _finite(row.get(k))
                for row in (left, right)
                for k in ("value", "uncertainty")
            )
        ):
            why.append("unknown objective or uncertainty " + axis)
            result["work_requests"].append(
                _hold(
                    candidate["comparison_context"]["item_id"],
                    "comparable objective " + axis,
                    [
                        "Same-scope objective value, units, uncertainty and source-bound calculation/measurement"
                    ],
                    candidate["comparison_context"]["scenarios"],
                )
            )
            continue
        if (
            left["units"] != right["units"]
            or min(left["uncertainty"], right["uncertainty"]) < 0
        ):
            why.append("incomparable objective units/uncertainty " + axis)
            continue
        margin = left["uncertainty"] + right["uncertainty"]
        if right["value"] > left["value"] + margin:
            why.append("objective worsened " + axis)
        if right["value"] < left["value"] - margin:
            improved = True
    if not improved:
        why.append("no objective improvement beyond declared uncertainty")
    revisions = {row["id"]: row for row in history}
    if len(revisions) != len(history):
        raise ValueError("unique revision history required")
    _acyclic({key: row["parents"] for key, row in revisions.items()})
    baseline_revision = baseline.get("revision_id")
    parents = []
    if baseline_revision:
        if baseline_revision not in revisions or revisions[baseline_revision].get(
            "candidate_sha256"
        ) != digest(
            {key: value for key, value in baseline.items() if key != "revision_id"}
        ):
            raise ValueError("baseline must match exact revision candidate ancestry")
        parents = [baseline_revision]
    elif history:
        why.append("baseline revision identity absent from existing history")
    if not why:
        revision = dict(
            parent_revision_ids=parents,
            candidate_sha256=digest(candidate),
            comparison_context_sha256=digest(candidate["comparison_context"]),
            evidence_sha256=digest(evidence),
            policy_sha256=digest(policy),
            baseline_candidate_id=baseline["id"],
            state="experimental-computational-baseline",
            **FLAGS,
        )
        revision["id"] = "experimental-" + digest(revision)[:20]
        revision["parents"] = revision.pop("parent_revision_ids")
        _acyclic(
            {
                **{key: row["parents"] for key, row in revisions.items()},
                revision["id"]: revision["parents"],
            }
        )
        result.update(disposition="ADOPT-EXPERIMENTAL", experimental_revision=revision)
    return result


def coupled_iteration(initial, step, *, scales, tolerance=1e-8, max_iterations=8):
    """Bounded fixed-point execution; residual convergence never supplies physics."""
    if (
        type(max_iterations) is not int
        or not 1 <= max_iterations <= 128
        or not _finite(tolerance)
        or tolerance <= 0
    ):
        raise ValueError(
            "positive finite tolerance and bounded iteration count required"
        )
    if (
        set(initial) != set(scales)
        or not initial
        or any(not _finite(v) for v in initial.values())
        or any(not _finite(v) or v <= 0 for v in scales.values())
    ):
        raise ValueError(
            "finite state and positive same-key dimensional scales required"
        )
    state, trace, status = deepcopy(initial), [], "budget-exhausted"
    for index in range(max_iterations):
        response = step(deepcopy(state))
        updated = response["state"]
        if set(updated) != set(initial) or any(
            not _finite(v) for v in updated.values()
        ):
            raise ValueError("coupled interface keys/finite quantities changed")
        checks = response["checks"]
        if not checks or any(
            c.get("state") not in {"pass", "fail", "unknown"}
            or not c.get("evidence_ref")
            for c in checks
        ):
            raise ValueError("actual coupled checks required")
        residual = max(abs(updated[key] - state[key]) / scales[key] for key in state)
        trace.append(
            dict(
                iteration=index + 1,
                input_state=state,
                output_state=deepcopy(updated),
                normalized_residual=residual,
                checks=checks,
            )
        )
        state = deepcopy(updated)
        if any(c["state"] == "fail" for c in checks):
            status = "rejected-interface-failure"
            break
        if any(c["state"] == "unknown" for c in checks):
            status = "HOLD-missing-capability-or-input"
            break
        if residual <= tolerance:
            status = "converged-declared-interfaces"
            break
    return dict(
        schema="osr-bounded-coupled-iteration/1",
        initial_state=initial,
        final_state=state,
        scales=scales,
        tolerance=tolerance,
        maximum_iterations=max_iterations,
        trace=trace,
        status=status,
        physical_convergence_established=False,
        **FLAGS,
    )


def software_proposals(base_commit):
    """Actual isolated code patches; acceptance fixture belongs to controller.

    The existing section routines accept True as a one-metre dimension. Repair
    this real typed-input defect without changing valid section calculations.
    The attractive shortcut falsifies beam deflection and must be rejected by
    original beam tests plus the controller's independently authored fixture.
    """
    name = "engineering/generative_design/mechanical_detail.py"
    if not isinstance(base_commit, str) or not re.fullmatch(
        r"[a-f0-9]{40}", base_commit
    ):
        raise ValueError("exact Git base commit required")
    controlled = subprocess.run(
        ["git", "show", base_commit + ":" + name],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if controlled.returncode:
        raise ValueError("software pilot base commit source unavailable")
    source = (ROOT / name).read_text()
    if controlled.stdout != source:
        raise ValueError(
            "software proposal working source differs from exact base commit"
        )
    fixed = source.replace(
        "not all(math.isfinite(v) and v > 0 for v in [width, height, flange, web])",
        "not all(type(v) in (int, float) and math.isfinite(v) and v > 0 for v in [width, height, flange, web])",
    ).replace(
        "not all(math.isfinite(v) and v > 0 for v in [width, height, wall])",
        "not all(type(v) in (int, float) and math.isfinite(v) and v > 0 for v in [width, height, wall])",
    )
    if fixed == source:
        raise ValueError(
            "software pilot source defect changed; reauthor against exact baseline"
        )
    shortcut = fixed.replace(
        "maximum_abs_deflection_m=max(abs(y(x)) for x in extrema)",
        "maximum_abs_deflection_m=0.0",
    )
    if shortcut == fixed:
        raise ValueError("software regression target changed")
    records = []
    for identity, text in [
        ("unmodified-baseline", source),
        ("strict-section-dimensions", fixed),
        ("attractive-zero-deflection-regression", shortcut),
    ]:
        patch = "".join(
            difflib.unified_diff(
                source.splitlines(keepends=True),
                text.splitlines(keepends=True),
                fromfile="a/" + name,
                tofile="b/" + name,
            )
        )
        records.append(
            dict(
                id=identity,
                role="software-developer",
                base_commit=base_commit,
                patch=patch,
                allowed_paths=[name],
                source_sha256=sha256(source.encode()).hexdigest(),
                change_scope=(
                    "runtime input validation"
                    if identity == "strict-section-dimensions"
                    else "adverse control"
                ),
                claimed_performance_improvement=None,
                **FLAGS,
            )
        )
    return records


def engineering_pilot():
    """Recompute a connected frame and a full-bay request with both supports.

    The available civil adapter models only one outer-end support. Two separate
    exact-revision records are retained; cross-span/transverse load distribution,
    staged erection and coupled foundation response are explicitly unevaluated.
    """
    from . import mechanical_detail as mechanical, civil_detail as civil

    context = mechanical.contexts()[1]
    light = dict(
        bolster_depth_m=0.45,
        bolt_diameter_m=0.027,
        bolts_per_support=8,
        crossbearer_pitch_m=1.8,
        diaphragm_thickness_m=0.012,
        maximum_stock_piece_length_m=3.8,
        plate_thickness_m=0.016,
        side_depth_m=0.75,
        spine_wall_m=0.016,
        web_thickness_m=0.016,
        weld_throat_m=0.004,
    )
    ordinary = mechanical.assess(light, context)
    heavy = mechanical.assess(
        dict(
            light,
            plate_thickness_m=0.032,
            spine_wall_m=0.032,
            side_depth_m=0.9,
            bolster_depth_m=0.65,
        ),
        context,
    )
    local_ids = {
        "global_service_deflection",
        "gross_member_normal_stress",
        "gross_web_shear",
        "side_flange_elastic_plate_buckling",
        "side_web_elastic_plate_buckling",
    }
    local_checks = [
        row for row in heavy["checks"] if row["id"].split("/")[-1] in local_ids
    ]
    if not local_checks:
        raise ValueError("actual member section screening checks absent")
    mechanical_adverse = dict(
        id="stiffer-section-harms-connected-frame",
        local_checks=local_checks,
        locally_passing=bool(local_checks)
        and all(row["state"] == "pass" for row in local_checks),
        affected_parent="vehicle-assembly",
        parent_failed_check_ids=heavy["failed_check_ids"],
        parent_candidate_id=heavy["id"],
        disposition="REJECT" if heavy["failed_check_ids"] else "HOLD",
        **FLAGS,
    )
    cc = next(
        row
        for row in civil.contexts()
        if row["architecture_id"] == "metro-6car-planning" and row["span_m"] == 25
    )
    coupled = civil.coupled_context(
        cc, ordinary["objectives"]["mass_kg"] * context["body_count"]
    )
    beam = dict(
        beam_depth_m=1.55,
        beam_stem_width_m=0.36,
        stirrup_diameter_m=0.012,
        stirrup_spacing_m=0.2,
        pad_length_m=0.5,
        footing_width_m=3.5,
    )
    bad = civil.assess(beam, coupled)
    good = civil.assess(dict(beam, footing_width_m=5.0), coupled)
    local = [
        row
        for row in bad["checks"]
        if row["id"]
        in {"web_link_steel", "web_concrete_strut", "midspan_live_deflection"}
    ]
    parent = [row for row in bad["checks"] if row["id"].startswith("footing_")]
    civil_adverse = dict(
        id="beam-pass-harms-support",
        local_checks=local,
        locally_passing=all(row["state"] == "pass" for row in local),
        parent_checks=parent,
        parent_candidate_id=bad["id"],
        disposition=(
            "REJECT" if any(row["state"] == "fail" for row in parent) else "HOLD"
        ),
        **FLAGS,
    )
    full_bay = dict(
        id="complete-25m-viaduct-bay",
        item_id="complete-viaduct-bay",
        span_m=25,
        beam_candidate_id=good["id"],
        declared_supports=["left-end-support", "right-end-support"],
        support_records=[
            dict(
                id=side,
                evaluated_outer_end_candidate_id=good["id"],
                scope="Symmetric provisional independent outer-end calculation only; complete support qualification absent",
            )
            for side in ["left-end-support", "right-end-support"]
        ],
        missing_capabilities=[
            "Whole-bay transverse distribution/torsion and actual support stiffness",
            "Both-support compatibility, braking/thermal movement and bearing qualification",
            "Cap/column/footing reinforcement, foundation resistance and settlement",
            "Construction/erection/temporary works, fatigue and seismic load cases",
        ],
        disposition="HOLD",
        complete_bay_evaluator_executed=False,
        **FLAGS,
    )
    coupling = coupled_iteration(
        dict(gross_added_train_mass_kg=0.0),
        lambda state: dict(
            state=dict(
                gross_added_train_mass_kg=ordinary["objectives"]["mass_kg"]
                * context["body_count"]
            ),
            checks=[
                dict(
                    id="gross-steel-transfer",
                    state="pass",
                    evidence_ref="#/mechanical/ordinary/objectives/mass_kg",
                )
            ],
        ),
        scales=dict(gross_added_train_mass_kg=100000.0),
        max_iterations=3,
    )
    coupling["scope"] = (
        "One-way mass-transfer fixed-point consistency only; no two-way physical interaction model"
    )
    coupling["downstream_context"] = coupled
    return dict(
        schema="osr-hierarchical-engineering-pilot/1",
        mechanical=dict(ordinary=ordinary, adverse=heavy),
        civil=dict(adverse=bad, repaired=good),
        adverse_cases=[mechanical_adverse, civil_adverse],
        complete_bay=full_bay,
        coupling=coupling,
        **FLAGS,
    )


def run_pilot(output):
    """Write small replayable numerical evidence; software execution is external."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    report = dict(
        schema="osr-hierarchical-pilot/1",
        plan=plan(),
        engineering=engineering_pilot(),
        software_execution="Controller must execute software_proposals in isolated workspaces against immutable acceptance",
        experimental_adoption_policy="Mandatory + independent + affected parent checks; same function/requirements/scenarios; robust objective improvement",
        **FLAGS,
    )
    target = output / "report.json"
    target.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report

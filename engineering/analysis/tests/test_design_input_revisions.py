"""Actual scoped evidence -> immutable input revision -> local worker search."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time
from types import SimpleNamespace

import pytest

from engineering.design_engine import http
from engineering.design_engine.contracts import canonical, fingerprint
from engineering.design_engine.engineering_inputs import (
    effective_input,
    qualification_template,
)
from engineering.design_engine.input_revisions import InputRevisions
from engineering.design_engine.manufacturing_rules import (
    evaluate as evaluate_manufacturing,
)
from engineering.design_engine.recovery import checkpoint, restore
from engineering.design_engine.review import ReviewStore
from engineering.design_engine.runtime import Manager, comparison, request
from engineering.design_engine.store import Store

PLANNER = dict(
    username="input-fixture-planner",
    roles=["planner", "approver"],
    city_scopes=["samawah"],
)
REVIEWER = dict(
    username="input-fixture-reviewer", roles=["approver"], city_scopes=["samawah"]
)


def wait_job(manager, identifier):
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        job = manager.store.get(identifier)
        if job["status"] not in {"queued", "running", "resuming", "cancelling"}:
            if job["status"] != "completed":
                logs = manager.store.root / "runs" / identifier / "logs"
                details = "\n".join(p.read_text()[-6000:] for p in logs.glob("*.log"))
                pytest.fail(
                    f"Actual local worker {job['status']}: {job['error']}\n{details}"
                )
            return job
        time.sleep(0.05)
    pytest.fail("Actual local worker exceeded the test deadline")


def api(context, path, data, actor=PLANNER):
    text = json.dumps(data)
    handler = SimpleNamespace(
        path="/api/design/" + path,
        headers={
            "Content-Length": str(len(text.encode())),
            "Origin": "http://localhost:1234",
            "Host": "localhost:1234",
        },
        project_twins=SimpleNamespace(_cities={"samawah": {}}),
        user_store=object(),
        evidence_root=context.evidence_root,
        server=SimpleNamespace(design_manager=context.manager),
        _actor=lambda: actor,
        _valid_csrf=lambda actual: True,
        _read_json=lambda: deepcopy(data),
    )
    handler._send_json = lambda code, payload: setattr(
        handler, "response", (code, payload)
    )
    http.post(handler)
    return handler.response


@pytest.fixture(scope="module")
def panel_context(tmp_path_factory):
    folder = tmp_path_factory.mktemp("actual-reviewed-input-loop")
    manager = Manager(folder / "store", recover_pending=False)
    scope = dict(
        schema="osr-design-identity/1",
        city="samawah",
        project="input-fixture-project",
        environment="simulation",
        configuration_revision="input-fixture-parent",
        baseline_sha256="a" * 64,
        run_id=None,
        asset_id=None,
        part_id=None,
    )
    parent = wait_job(
        manager,
        manager.start(
            request(
                "clipped-side-bay",
                scope,
                [
                    dict(
                        support_span_m=1.0,
                        grade_density=60,
                        skin_m=0.0015,
                        core_m=0.02,
                    )
                ],
                budget=dict(evaluations=256, wall_seconds=120),
            )
        )["id"],
    )
    candidate = comparison(manager.store, parent["id"])["candidates"][0]
    contract = candidate["definition"]["contract"]
    physical_id = contract["parts"][0]["id"]
    evidence_root = folder / "evidence"
    evidence_root.mkdir()
    document = evidence_root / "fixture-source.txt"
    document.write_text(
        "Test fixture only. Research stock envelope 0.0001m each axis, minimum wall 0.01m. Not physical qualification."
    )
    source = dict(
        path=document.name, sha256=hashlib.sha256(document.read_bytes()).hexdigest()
    )
    applicability = dict(
        candidate_id=candidate["id"],
        physical_part_id=physical_id,
        material_batch="FIXTURE-BATCH",
        definition_sha256=fingerprint(contract),
    )
    reviews = ReviewStore(manager.store)
    records = []
    for kind, payload in (
        (
            "material",
            dict(
                supplier="Fixture source",
                grade="Fixture grade",
                batch="FIXTURE-BATCH",
                conditions="Numerical test only",
                properties={"stock_bounds_m": [0.0001] * 3, "minimum_wall_m": 0.01},
                source_reference=source,
            ),
        ),
        (
            "measurement",
            dict(
                specimen="Fixture specimen",
                candidate=candidate["id"],
                test_method="Fixture dimensional measurement",
                instrument="Fixture instrument",
                uncertainty="Fixture uncertainty",
                observations="Fixture observations only",
                source_reference=source,
            ),
        ),
    ):
        row = reviews.submit(
            "samawah",
            "simulation",
            kind,
            payload,
            PLANNER["username"],
            "input-loop-key-" + kind,
            identity=scope,
            applicability=applicability,
        )
        reviews.verify(
            row["id"],
            row["revision"],
            REVIEWER,
            city="samawah",
            environment="simulation",
            evidence_root=evidence_root,
            identity=scope,
            applicability=applicability,
        )
        row = next(
            r for r in reviews.list("samawah", "simulation") if r["id"] == row["id"]
        )
        records.append(
            dict(
                id=row["id"],
                revision=row["revision"],
                applicability=row["applicability"],
            )
        )
    context = SimpleNamespace(
        folder=folder,
        manager=manager,
        scope=scope,
        parent=parent,
        candidate=candidate,
        contract=contract,
        physical_id=physical_id,
        evidence_root=evidence_root,
        document=document,
        source=source,
        records=records,
    )
    plan = qualification_template("manufacturing", contract, scope)
    for key in ("tool_envelopes", "removal_paths", "tolerance_stacks", "tooling"):
        plan[key] = []
    plan["part_rules"] = [
        dict(
            physical_id=physical_id,
            stock_bounds_m=[0.0001] * 3,
            minimum_wall_m=0.01,
            basis_reference=records[0]["id"],
        )
    ]
    data = dict(
        identity=scope,
        candidate=candidate["id"],
        contract_sha256=fingerprint(contract),
        kind="manufacturing",
        input_json=json.dumps(plan),
    )
    code, draft = api(context, "jobs/" + parent["id"] + "/qualification-draft", data)
    assert code == 200, draft
    context.plan, context.draft = plan, draft
    return context


def proposal_data(context, name):
    return dict(
        identity=deepcopy(context.scope),
        candidate=context.candidate["id"],
        drafts=[context.draft["draft_sha256"]],
        records=deepcopy(context.records),
        configuration_revision="input-fixture-" + name,
        rationale="Fixture: use the independently retained source in numerical manufacturing checks",
        policy="retained-physical-ids",
    )


def propose(context, name):
    data = proposal_data(context, name)
    code, result = api(
        context, "jobs/" + context.parent["id"] + "/input-revisions", data
    )
    assert code == 200, result
    return data, result


def review(context, row):
    data = dict(
        identity=context.scope,
        revision=row["proposal_sha256"],
        rationale="Fixture independent permission for numerical research use only",
    )
    code, reviewed = api(
        context, "input-revisions/" + row["id"] + "/review", data, REVIEWER
    )
    assert code == 200, reviewed
    return data, reviewed


def test_http_reviewed_source_changes_actual_child_candidate_and_optimiser_rules(
    panel_context,
):
    context = panel_context
    store = context.manager.store
    original_request = (
        store.root / "runs" / context.parent["id"] / "request.json"
    ).read_bytes()
    original_candidate = canonical(context.candidate)
    assert context.candidate["checks"]["nominal_deflection"]["state"] == "failed"
    _, proposed = propose(context, "actual-child-search")
    _, reviewed = review(context, proposed)
    assert reviewed["review"]["technical_acceptance"] is False
    assert {
        "geometry",
        "BOM",
        "optimisation",
        "cost-objectives",
        "CAD-drawings",
    } <= set(reviewed["proposal"]["invalidated"])
    data = dict(
        identity=context.scope,
        search=dict(seeds=[11, 29], evaluations=4),
        refine=False,
        budget=dict(evaluations=128, wall_seconds=120),
    )
    code, started = api(context, "input-revisions/" + proposed["id"] + "/run", data)
    assert code == 200, started
    child = wait_job(context.manager, started["job"]["id"])
    assert (
        child["request"]["identity"]["configuration_revision"]
        == "input-fixture-actual-child-search"
    )
    assert (
        child["request"]["problem"]["revision"]
        != context.parent["request"]["problem"]["revision"]
    )
    assert "+inputs-" in child["request"]["problem"]["revision"]
    report = comparison(store, child["id"])
    assert report["candidates"]
    assert all(row["id"] != context.candidate["id"] for row in report["candidates"])
    represented = [row for row in report["candidates"] if "definition" in row]
    assert represented
    for row in represented:
        definition = row["definition"]
        assert definition["contract"]["manufacturing_plan"] == context.plan
        from osr_mech.engineering_definition import fingerprint as native_fingerprint

        assert definition["correspondence"][
            "configuration_sha256"
        ] == native_fingerprint(definition["contract"])
        assert definition["input_lineage"]["id"] == proposed["id"]
        assert row["checks"]["geometry"]["state"] == "failed"
        # Public dimensional owner evaluates this selected, sourced constraint
        # even when an unrelated nominal panel response already fails.
        checked = evaluate_manufacturing(definition["contract"])
        stock = next(
            r
            for r in checked["checks"]
            if r["id"] == context.physical_id + "/stock-process"
        )
        assert stock["state"] == "failed"
        assert stock["stock_bounds_m"] == [0.0001] * 3
        assert stock["basis_reference"] == context.records[0]["id"]
        assert len(definition["installed_register"]["parts"]) == len(
            definition["contract"]["parts"]
        )
    attempt = (
        store.root / "runs" / child["id"] / ("attempt-%04d" % child["active_attempt"])
    )
    search = json.loads((attempt / "search.json").read_text())
    assert all(
        not row["feasible_screen"]
        for trial in search["trials"]
        for row in trial["optimiser"] + trial["random_control"]
    )
    assert all(
        not trial["conditional_screen_frontier"] and not trial["random_screen_frontier"]
        for trial in search["trials"]
    )
    assert (
        store.root / "runs" / context.parent["id"] / "request.json"
    ).read_bytes() == original_request
    assert (
        canonical(comparison(store, context.parent["id"])["candidates"][0])
        == original_candidate
    )
    assert report["physical_release"] is False
    context.completed_child = child


def test_proposal_retry_preserves_exact_proposal_and_source_snapshots(panel_context):
    context = panel_context
    data, first = propose(context, "lost-proposal-reply")
    code, repeated = api(
        context, "jobs/" + context.parent["id"] + "/input-revisions", data
    )
    assert code == 200 and repeated["id"] == first["id"]
    snapshot = (
        context.manager.store.root
        / "input-revisions"
        / first["id"]
        / "sources"
        / context.source["sha256"]
    )
    assert snapshot.read_bytes() == context.document.read_bytes()
    changed = deepcopy(data)
    changed["rationale"] = "Changed proposed use"
    code, _ = api(context, "jobs/" + context.parent["id"] + "/input-revisions", changed)
    assert code == 400


def test_independent_review_retry_is_idempotent_after_lost_reply(panel_context):
    context = panel_context
    _, proposal = propose(context, "lost-review-reply")
    data, first = review(context, proposal)
    code, repeated = api(
        context, "input-revisions/" + proposal["id"] + "/review", data, REVIEWER
    )
    assert code == 200, repeated
    assert repeated["review"] == first["review"]


def test_revised_run_retry_does_not_launch_a_second_job(panel_context):
    context = panel_context
    _, proposal = propose(context, "lost-run-reply")
    review(context, proposal)
    data = dict(
        identity=context.scope,
        search=None,
        refine=False,
        budget=dict(evaluations=8, wall_seconds=120),
    )
    code, first = api(context, "input-revisions/" + proposal["id"] + "/run", data)
    assert code == 200, first
    code, repeated = api(context, "input-revisions/" + proposal["id"] + "/run", data)
    assert code == 200, repeated
    # Complete both if a regression dispatched twice, so test cleanup leaves no
    # owned worker active even on a failed assertion.
    wait_job(context.manager, first["job"]["id"])
    wait_job(context.manager, repeated["job"]["id"])
    assert repeated["job"]["id"] == first["job"]["id"]


@pytest.mark.parametrize(
    "fault",
    [
        "other-project",
        "other-revision",
        "other-baseline",
        "other-candidate",
        "other-part",
        "other-definition",
        "other-batch",
        "record-revision",
        "forged-review-field",
        "unknown-baseline",
    ],
)
def test_scope_changes_cannot_bind_source_evidence(panel_context, fault):
    context = panel_context
    data = proposal_data(context, "rejected-" + fault)
    if fault == "other-project":
        data["identity"]["project"] = "other-project"
    elif fault == "other-revision":
        data["identity"]["configuration_revision"] = "other-revision"
    elif fault == "other-baseline":
        data["identity"]["baseline_sha256"] = "c" * 64
    elif fault == "other-candidate":
        data["records"][0]["applicability"]["candidate_id"] = "other-candidate"
    elif fault == "other-part":
        data["records"][0]["applicability"]["physical_part_id"] = "absent-part"
    elif fault == "other-definition":
        data["records"][0]["applicability"]["definition_sha256"] = "d" * 64
    elif fault == "other-batch":
        data["records"][0]["applicability"]["material_batch"] = "other-batch"
    elif fault == "record-revision":
        data["records"][0]["revision"] = "forged-revision"
    elif fault == "forged-review-field":
        data["reviewed"] = True
    elif fault == "unknown-baseline":
        data["identity"]["baseline_sha256"] = None
    code, response = api(
        context, "jobs/" + context.parent["id"] + "/input-revisions", data
    )
    assert code in {400, 403}, response


def test_unknown_baseline_cannot_be_promoted_by_filling_only_the_proposal(
    panel_context,
):
    context = panel_context
    scope = {**context.scope, "baseline_sha256": None}
    parent = deepcopy(context.parent)
    parent["request"]["identity"] = scope
    data = proposal_data(context, "no-known-baseline")
    data["identity"] = scope
    with pytest.raises(ValueError, match="known research baseline"):
        InputRevisions(context.manager.store).propose(
            parent,
            context.candidate,
            data,
            scope,
            PLANNER,
            evidence_root=context.evidence_root,
        )


def test_self_review_forged_actor_and_changed_proposal_are_rejected(panel_context):
    context = panel_context
    _, proposal = propose(context, "self-review")
    data = dict(
        identity=context.scope,
        revision=proposal["proposal_sha256"],
        rationale="Fixture review",
    )
    code, _ = api(
        context, "input-revisions/" + proposal["id"] + "/review", data, PLANNER
    )
    assert code == 403
    code, _ = api(
        context,
        "input-revisions/" + proposal["id"] + "/review",
        data,
        {**REVIEWER, "roles": ["planner"]},
    )
    assert code == 403
    data["revision"] = "wrong-revision"
    code, _ = api(
        context, "input-revisions/" + proposal["id"] + "/review", data, REVIEWER
    )
    assert code == 400
    with pytest.raises(ValueError, match="independent input-use review"):
        InputRevisions(context.manager.store).snapshot(proposal["id"])


def test_changed_source_bytes_and_changed_immutable_snapshot_are_rejected(
    panel_context,
):
    context = panel_context
    original = context.document.read_bytes()
    try:
        context.document.write_text("Changed source bytes")
        data = proposal_data(context, "changed-source")
        code, result = api(
            context, "jobs/" + context.parent["id"] + "/input-revisions", data
        )
        assert code == 400 and "source evidence changed" in result["error"]
    finally:
        context.document.write_bytes(original)
    _, proposal = propose(context, "changed-snapshot")
    source = (
        context.manager.store.root
        / "input-revisions"
        / proposal["id"]
        / "sources"
        / context.source["sha256"]
    )
    original = source.read_bytes()
    try:
        source.write_text("Changed retained snapshot")
        with pytest.raises(ValueError, match="source snapshot changed"):
            InputRevisions(context.manager.store).get(proposal["id"])
    finally:
        source.write_bytes(original)


def test_forged_job_review_and_changed_charter_cannot_replace_controlled_inputs(
    panel_context,
):
    context = panel_context
    _, proposal = propose(context, "forged-job-snapshot")
    review(context, proposal)
    revisions = InputRevisions(context.manager.store)
    snapshot = revisions.snapshot(proposal["id"])
    target = snapshot["target_identity"]
    req = request(
        "clipped-side-bay",
        target,
        context.parent["request"]["candidates"],
        reviewed_inputs=snapshot,
    )
    revisions.validate_job(req)
    forged = deepcopy(req)
    forged["reviewed_inputs"]["review_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="reviewed immutable inputs"):
        revisions.validate_job(forged)
    changed = deepcopy(req)
    changed["problem"]["applicability"]["mandatory_checks"] = ["geometry"]
    with pytest.raises(ValueError, match="controlled functional problem"):
        revisions.validate_job(changed)


def test_recovery_preserves_reviewed_input_sources_and_new_child_lineage(
    panel_context, tmp_path
):
    context = panel_context
    _, proposal = propose(context, "recovery-child")
    review(context, proposal)
    code, started = api(
        context,
        "input-revisions/" + proposal["id"] + "/run",
        dict(
            identity=context.scope,
            search=None,
            refine=False,
            budget=dict(evaluations=8, wall_seconds=120),
        ),
    )
    assert code == 200, started
    completed_child = wait_job(context.manager, started["job"]["id"])
    backup = tmp_path / "checkpoint"
    checkpoint(context.manager.store, backup)
    result = restore(backup, tmp_path / "restored")
    assert result["all_sealed_artifacts_verified"]
    restored_store = Store(tmp_path / "restored")
    child = restored_store.verify_request(completed_child["id"])
    snapshot = InputRevisions(restored_store).validate_job(child["request"])
    assert snapshot["id"] == completed_child["request"]["reviewed_inputs"]["id"]
    retained_source = (
        restored_store.root
        / "input-revisions"
        / snapshot["id"]
        / "sources"
        / context.source["sha256"]
    )
    assert retained_source.read_bytes() == context.document.read_bytes()


def test_blank_and_duplicate_nonfinite_drafts_cannot_become_effective_inputs(
    panel_context,
):
    context = panel_context
    blank = qualification_template("manufacturing", context.contract, context.scope)
    assert (
        effective_input("manufacturing", context.contract, context.scope, blank) is None
    )
    from engineering.design_engine.engineering_inputs import decode_input

    for text in ('{"x":1,"x":2}', '{"x":NaN}'):
        with pytest.raises(ValueError):
            decode_input(text)

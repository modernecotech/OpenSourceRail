"""Private offline exports retain every reviewed-input source in their ancestry."""

from copy import deepcopy
import json
import shutil
from types import SimpleNamespace

import pytest

from engineering.analysis.tests.test_design_input_revisions import (
    panel_context,
    api,
    propose,
    review,
    wait_job,
    PLANNER,
    REVIEWER,
)
from engineering.design_engine.contracts import fingerprint
from engineering.design_engine.export import export, verify_export
from engineering.design_engine.input_revisions import InputRevisions
from engineering.design_engine.review import ReviewStore
from engineering.design_engine.runtime import comparison


def run_revision(context, name):
    _, proposed = propose(context, name)
    review(context, proposed)
    code, started = api(
        context,
        "input-revisions/" + proposed["id"] + "/run",
        dict(
            identity=context.scope,
            search=None,
            refine=False,
            budget=dict(evaluations=8, wall_seconds=120),
        ),
    )
    assert code == 200, started
    return wait_job(context.manager, started["job"]["id"]), proposed


def test_export_contains_independently_reviewed_documents_for_both_input_generations(
    panel_context, tmp_path
):
    original = panel_context
    child, first = run_revision(original, "export-child")
    candidate = comparison(original.manager.store, child["id"])["candidates"][0]
    contract = candidate["definition"]["contract"]
    scope = child["request"]["identity"]
    applicability = dict(
        candidate_id=candidate["id"],
        physical_part_id=original.physical_id,
        material_batch="FIXTURE-BATCH",
        definition_sha256=fingerprint(contract),
    )
    reviews = ReviewStore(original.manager.store)
    record = reviews.submit(
        "samawah",
        "simulation",
        "material",
        dict(
            supplier="Fixture source",
            grade="Fixture grade",
            batch="FIXTURE-BATCH",
            conditions="Numerical fixture only",
            properties={"stock_bounds_m": [0.0001] * 3},
            source_reference=original.source,
        ),
        PLANNER["username"],
        "export-child-source",
        identity=scope,
        applicability=applicability,
    )
    reviews.verify(
        record["id"],
        record["revision"],
        REVIEWER,
        city="samawah",
        environment="simulation",
        evidence_root=original.evidence_root,
        identity=scope,
        applicability=applicability,
    )
    plan = deepcopy(original.plan)
    plan["part_rules"][0]["basis_reference"] = record["id"]
    context = SimpleNamespace(
        **{
            **vars(original),
            "scope": scope,
            "parent": child,
            "candidate": candidate,
            "contract": contract,
            "plan": plan,
            "records": [
                dict(
                    id=record["id"],
                    revision=record["revision"],
                    applicability=applicability,
                )
            ],
        }
    )
    code, context.draft = api(
        context,
        "jobs/" + child["id"] + "/qualification-draft",
        dict(
            identity=scope,
            candidate=candidate["id"],
            contract_sha256=fingerprint(contract),
            kind="manufacturing",
            input_json=json.dumps(plan),
        ),
    )
    assert code == 200, context.draft
    grandchild, second = run_revision(context, "export-grandchild")
    assert (
        len(
            InputRevisions(context.manager.store).source_directories(
                grandchild["request"]
            )
        )
        == 2
    )
    destination = tmp_path / "private-review"
    receipt = export(context.manager.store, grandchild["id"], destination)
    assert {row["input_revision"] for row in receipt["reviewed_input_sources"]} == {
        first["id"],
        second["id"],
    }
    for proposal in (first, second):
        folder = destination / "reviewed-inputs" / proposal["id"]
        assert (
            json.loads((folder / "proposal.json").read_text())["source_identity"][
                "project"
            ]
            == original.scope["project"]
        )
        decision = json.loads((folder / "review.json").read_text())
        assert decision["reviewer"] == REVIEWER["username"]
        assert decision["physical_release"] is False
        assert (
            folder / "sources" / original.source["sha256"]
        ).read_bytes() == original.document.read_bytes()
    offline = tmp_path / "offline-machine"
    shutil.copytree(destination, offline)
    assert verify_export(offline)["files"] == receipt["files"]
    source_copy = (
        offline
        / "reviewed-inputs"
        / first["id"]
        / "sources"
        / original.source["sha256"]
    )
    source_copy.write_text("corrupted retained source")
    with pytest.raises(ValueError, match="changed review export"):
        verify_export(offline)
    assert original.document.read_text().startswith("Test fixture only")

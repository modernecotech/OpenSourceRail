"""Exact queue coverage, source tamper detection and non-promotion."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile

import pytest

from engineering.generative_design import campaign, coverage, queue_campaign as queue


@pytest.fixture(scope="module")
def queued_run():
    parent = coverage.ROOT / "build/generative-queue-tests"
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as name:
        output = Path(name) / "run"
        queue.run(output)
        yield output


def test_queue_executes_all_ids_and_retains_failed_feedback(queued_run):
    result = queue.verify(queued_run)
    assert result["work_package_count"] == 63
    report = json.loads((queued_run / "report.json").read_text())
    assert len({p["id"] for p in report["packages"]}) == 63
    assert all(p["preliminary_investigation_executed"] for p in report["packages"])
    assert all(not p["full_discipline_model_qualified"] for p in report["packages"])
    assert all(
        r["minimum_sampled_service_compression_pa"] < 0
        for r in report["integration"]["previous_civil_selection_responses"]
    )
    selected = report["integration"]["provisional_six_car_beam_shortlist"]
    assert len(selected) == 2
    assert all(
        0 < r["minimum_sampled_service_compression_pa"] < 100000 for r in selected
    )
    assert all(
        r["accepted_loading"] is False and r["accepted_material_limit_pa"] is None
        for r in selected
    )
    assert (
        report["manufacturing_evidence_counts"][
            "missing_or_unissued_production_artifacts"
        ]
        == 472
    )


def test_queue_rejects_omission_duplicate_removed_gate_and_false_release(queued_run):
    report = json.loads((queued_run / "report.json").read_text())
    value = campaign.scope()
    for mutate, message in (
        (lambda r: r["packages"].pop(), "package IDs"),
        (lambda r: r["packages"].__setitem__(1, r["packages"][0]), "package IDs"),
        (lambda r: r["packages"][0]["required_gates"].clear(), "mandatory scope"),
        (
            lambda r: r["packages"][0].__setitem__("design_complete", True),
            "cannot grant release",
        ),
        (
            lambda r: r.__setitem__("all_systems_design_complete", True),
            "cannot grant release",
        ),
    ):
        changed = deepcopy(report)
        mutate(changed)
        with pytest.raises(ValueError, match=message):
            queue.validate_report(value, changed)


def test_queue_receipt_detects_membership_and_bytes(queued_run):
    extra = queued_run / "foreign.json"
    extra.write_text("{}")
    try:
        with pytest.raises(ValueError, match="membership differs"):
            queue.verify(queued_run)
    finally:
        extra.unlink()
    target = queued_run / "index.html"
    original = target.read_bytes()
    target.write_bytes(original + b" ")
    try:
        with pytest.raises(ValueError, match="artifact changed"):
            queue.verify(queued_run)
    finally:
        target.write_bytes(original)


def test_queue_source_verification_binds_actual_cad_and_drawing_records():
    state = queue.source_state(campaign.scope())
    assert any("factory-drawings/" in p for p in state)
    assert (
        "design/component-catalogue/src/osr_mech/rolling_stock/product_geometry.py"
        in state
    )
    assert "engineering/generative_design/data/integration-systems.json" in state


def test_queue_submodel_counts_do_not_sum_reused_parent_packages():
    assert queue.investigation_counts(dict(candidates=[{}, {}])) == 2
    assert (
        queue.investigation_counts(
            dict(variants=[dict(candidates=[{}, {}]), dict(candidates=[{}])])
        )
        == 3
    )
    assert queue.investigation_counts(dict(id="fixed-demand-audit")) == 1


def test_resealed_native_receipt_cannot_hide_failed_reopen(queued_run):
    target = queued_run / "report.json"
    seal = queued_run / "receipt.json"
    original, original_seal = target.read_bytes(), seal.read_bytes()
    proof_path = queued_run / "forged-native.json"
    result = json.loads(original)
    native = result["native_geometry"][0]
    model = json.loads((queued_run / native["model"]).read_text())
    native.update(
        status="passed", part_count=len(model["parts"]), receipt=proof_path.name
    )
    campaign.write(
        proof_path,
        dict(
            schema="osr-factory-native-cad/1",
            physical_release=False,
            fcstd_reopened=False,
            step_reopened=True,
            part_count=len(model["parts"]),
            parts=model["parts"],
        ),
    )
    campaign.write(target, result)
    receipt = json.loads(original_seal)
    receipt["files_sha256"] = queue.file_hashes(queued_run, ("receipt.json",))
    campaign.write(seal, receipt)
    try:
        with pytest.raises(ValueError, match="native proof incomplete"):
            queue.verify(queued_run)
    finally:
        target.write_bytes(original)
        seal.write_bytes(original_seal)
        proof_path.unlink()


def test_queue_rejects_current_source_drift(queued_run, monkeypatch):
    monkeypatch.setattr(queue, "source_state", lambda value: {})
    with pytest.raises(ValueError, match="another source revision"):
        queue.verify(queued_run)
    assert queue.verify(queued_run, current=False)["current_sources_checked"] is False


def test_source_changing_proposals_cannot_be_silently_selected():
    proposal = dict(id="new-gap", existing_configuration_compatible=False)
    for selected, proposed, message in [
        (["new-gap"], ["new-gap"], "identities conflict"),
        (["new-gap"], [], "source-compatible"),
        (["missing"], [], "identities conflict"),
    ]:
        with pytest.raises(ValueError, match=message):
            queue.validate_selections(
                dict(
                    candidates=[proposal],
                    selected_candidate_ids=selected,
                    proposed_candidate_ids=proposed,
                )
            )
    queue.validate_selections(
        dict(
            candidates=[proposal],
            selected_candidate_ids=[],
            proposed_candidate_ids=["new-gap"],
        )
    )

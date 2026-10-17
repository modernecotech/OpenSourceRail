"""Actual feedback, retained adverse results, resume and untrusted evidence guards."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from engineering.generative_design import design_iteration as d


def adapter():
    def assess(v, context):
        return dict(
            id=f"trial-{context['id']}-{v['depth']}",
            variables=dict(v),
            checks=[
                dict(
                    id="resistance",
                    state="pass" if v["depth"] >= 3 else "fail",
                    value=v["depth"],
                    limit=3,
                ),
                dict(
                    id="material-qualification", state="unknown", value=None, limit=None
                ),
            ],
            geometry={"depth": v["depth"]},
            materials={"accepted": False},
            connections={"qualified": False},
            manufacturing={"issued": False},
            physical_release=False,
        )

    return SimpleNamespace(
        seed=lambda c: dict(depth=1),
        assess=assess,
        propose=lambda candidate, c: [
            dict(depth=candidate["variables"]["depth"] + 1),
            dict(candidate["variables"]),
        ],
    )


def test_feedback_changes_failed_dimension_and_preserves_parents_and_unknowns():
    trace = d.iterate(adapter(), dict(id="beam"), budget=8)
    assert len(trace["candidates"]) == 3
    assert trace["termination"] == "provisional-solution-held-for-qualification"
    assert trace["selected_candidate_id"] == "trial-beam-3"
    assert trace["candidates"][0]["checks"][0]["state"] == "fail"
    assert trace["candidates"][1]["iteration_provenance"]["parent_candidate_ids"] == [
        "trial-beam-1"
    ]
    assert trace["candidates"][1]["iteration_provenance"]["repair_reasons"] == [
        "resistance"
    ]
    assert trace["critique"]["unknown_check_ids"] == ["material-qualification"]
    assert (
        not trace["physical_release"]
        and not trace["critique"]["independent_engineering_review_performed"]
    )


def test_resume_uses_frontier_without_repeating_completed_evaluations():
    first = d.iterate(adapter(), dict(id="beam"), budget=1)
    assert first["termination"] == "budget-exhausted"
    resumed = d.iterate(adapter(), dict(id="beam"), budget=5, previous=first)
    assert resumed["new_evaluations"] == 2
    assert (
        resumed["candidates"]
        == d.iterate(adapter(), dict(id="beam"), budget=5)["candidates"]
    )
    unchanged = d.iterate(adapter(), dict(id="beam"), budget=5, previous=resumed)
    assert unchanged["new_evaluations"] == 0
    with pytest.raises(ValueError, match="changed context"):
        d.iterate(adapter(), dict(id="other"), budget=5, previous=first)


def test_unknown_only_evaluation_never_becomes_numerical_solution():
    a = adapter()
    original = a.assess

    def unknown(v, c):
        row = original(v, c)
        row["checks"][0]["state"] = "unknown"
        return row

    a.assess = unknown
    a.propose = lambda r, c: []
    trace = d.iterate(a, dict(id="beam"))
    assert trace["selected_candidate_id"] is None
    assert trace["termination"] == "no-solution-in-declared-repair-domain"


@pytest.mark.parametrize("flag", d.FLAGS)
def test_no_adapter_can_claim_release(flag):
    row = adapter().assess(dict(depth=3), dict(id="beam"))
    row[flag] = True
    with pytest.raises(ValueError, match="release"):
        d.validate_candidate(row)


def test_separate_critic_and_missing_assembly_definition():
    row = adapter().assess(dict(depth=3), dict(id="beam"))
    with pytest.raises(ValueError, match="own candidate"):
        d.critique(row, producer="same", reviewer="same")
    row.pop("connections")
    result = d.critique(row, producer="designer")
    assert result["missing_definition_fields"] == ["connections"]
    assert result["disposition"] == "hold-missing-definition"


def test_unretained_resume_parent_and_invalid_budgets_rejected():
    first = d.iterate(adapter(), dict(id="beam"), budget=1)
    first["frontier"][0]["parent"] = "invented"
    with pytest.raises(ValueError, match="parent"):
        d.iterate(adapter(), dict(id="beam"), budget=4, previous=first)
    for invalid in (0, 513, True):
        with pytest.raises(ValueError, match="budget"):
            d.iterate(adapter(), dict(id="beam"), budget=invalid)


def test_unknown_architecture_is_rejected_and_interrupted_attempts_are_retained():
    with pytest.raises(ValueError, match="architecture"):
        d._architecture(dict(configuration_id="unassigned-train"))
    a = adapter()
    original = a.assess
    captured = []

    def interrupted(v, c):
        if v["depth"] == 2:
            raise RuntimeError("declared solver failure")
        return original(v, c)

    a.assess = interrupted
    with pytest.raises(RuntimeError, match="solver failure"):
        d.iterate(a, dict(id="beam"), checkpoint=captured.append)
    assert captured[0]["checks"][0]["state"] == "fail"
    assert captured[1]["parent_candidate_id"] == captured[0]["id"]
    assert "solver failure" in captured[1]["error"]


@pytest.fixture(scope="module")
def actual_campaign(tmp_path_factory):
    folder = tmp_path_factory.mktemp("detail-campaign") / "actual"
    result = d.run(folder, budget=1, native=False, baseline=False)
    assert result["detail_contexts"] == 6 and result["packages"] == 63
    return folder


def test_real_campaign_recomputes_results_and_requires_all_native_contexts(
    actual_campaign,
):
    result = d.verify(actual_campaign)
    assert result["numerical_detail_calculations_recomputed"]
    assert not result["manufacturing_release"]
    with pytest.raises(ValueError, match="native proof"):
        d.verify(actual_campaign, require_native=True)
    with pytest.raises(ValueError, match="current-source"):
        d.verify(actual_campaign, current=False, require_native=True)


def test_real_unchanged_resume_performs_no_repeated_evaluations(
    actual_campaign, tmp_path
):
    result = d.run(
        tmp_path / "resume",
        budget=1,
        native=False,
        baseline=False,
        resume=actual_campaign,
    )
    assert result["new_evaluations"] == 0
    assert result["evaluated_variations"] == 6


@pytest.mark.parametrize(
    "mutation",
    ["exchange", "frontier", "package", "release", "production", "inspection"],
)
def test_resealing_cannot_invent_coverage_or_repair_results(
    actual_campaign, tmp_path, mutation
):
    import shutil
    from engineering.generative_design.campaign import write

    folder = tmp_path / "copy"
    shutil.copytree(actual_campaign, folder)
    report = d._read(folder / "report.json")
    if mutation == "exchange":
        report["exchanges"][0]["component_ids"].append("invented-completed-component")
    elif mutation == "frontier":
        report["traces"][0]["frontier"] = []
    elif mutation == "package":
        report["packages"][0]["required_gates"] = {}
    elif mutation == "release":
        report["packages"][0]["design_complete"] = True
    elif mutation == "production":
        report["packages"][0]["production_artifact_ids"].append(
            "fabricated-issued-drawing"
        )
    else:
        report["packages"][0]["inspection_characteristic_ids"].append(
            "fabricated-measurement"
        )
    write(folder / "report.json", report)
    receipt = d._read(folder / "receipt.json")
    receipt["files_sha256"] = d._files(folder)
    write(folder / "receipt.json", receipt)
    with pytest.raises(ValueError):
        d.verify(folder)

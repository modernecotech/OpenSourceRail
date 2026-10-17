"""A compact view must preserve failures, unknowns and source applicability."""

from copy import deepcopy

import pytest

from engineering.generative_design.review_flow import (
    candidate_row,
    build,
    gate_labels,
    pack_data,
)


def record():
    return dict(
        id="part",
        checks=[
            dict(id="fit", status="passed", basis="local"),
            dict(id="material", status="unknown", basis="Hot/wet resistance absent"),
        ],
        variables={},
        metrics={},
        conditional_screen_feasible=True,
        physical_release=False,
    )


def test_unknown_check_basis_is_not_dropped_from_mechanical_projection():
    row = candidate_row(
        record(),
        packet="queued",
        family="frame",
        case="lm3",
        source="../queued-systems/report.json",
    )
    assert row["screen"] == "local-pass"
    assert row["unknown_gates"] == ["material: Hot/wet resistance absent"]
    assert row["manufacturing_release"] is False
    assert gate_labels(
        [
            dict(
                id="wind",
                requirement="Approved wind and anchor actions absent",
                status="unknown",
            )
        ]
    ) == ["wind: Approved wind and anchor actions absent"]


def test_known_failure_and_release_claim_cannot_be_hidden_in_summary():
    item = record()
    item["checks"][0]["status"] = "failed"
    with pytest.raises(ValueError, match="failed known check"):
        candidate_row(item, packet="x", family="x", case="x", source="x")
    item = record()
    item["physical_release"] = True
    with pytest.raises(ValueError, match="conceal a release"):
        candidate_row(item, packet="x", family="x", case="x", source="x")
    item = record()
    item["existing_configuration_compatible"] = False
    with pytest.raises(ValueError, match="source-compatible"):
        candidate_row(item, packet="x", family="x", case="x", source="x", selected=True)


def test_review_exact_coverage_and_history_remain_explicit():
    result = build()
    assert len(result["packages"]) == 63
    assert len({r["id"] for r in result["candidates"]}) == len(result["candidates"])
    assert len(result["candidates"]) > 4250
    assert all(p["integrity_verified"] for p in result["packets"])
    assert all(p["applicability"] == "historical" for p in result["packets"])
    mechanical = [
        r
        for r in result["candidates"]
        if r["packet"] == "queued" and r["case"] == "lm3-system-submodels"
    ]
    assert len(mechanical) == 694 and all(r["unknown_gates"] for r in mechanical)
    assert all(not r["manufacturing_release"] for r in result["candidates"])
    assert (
        next(c for c in result["cases"] if c["id"] == "queued-BASIS-CONFIGURATION")[
            "architecture"
        ]
        == "metro-6car-planning"
    )
    partial = [
        r for r in result["candidates"] if r["family"] == "six-car-envelope-response"
    ]
    assert len(partial) == 864 and any(
        r["screen"] == "failed" and r["metrics"]["minimum_service_compression_pa"] < 0
        for r in partial
    )
    packed = pack_data(result)
    assert len(packed["records"]) == len(result["candidates"])
    assert len(packed["tables"]["gates"]) < len(result["candidates"]) / 3

"""Cross-candidate, budget and integrity regressions for the civil handoff."""
from copy import deepcopy
import json
import random

import pytest

from engineering.design_search import civil_demonstrator as d
from engineering.station_rail.common import digest, encoded, identity


def seal(value, key):
    value[key] = identity({k: v for k, v in value.items() if k != key})


@pytest.fixture(scope="module")
def inputs():
    return d.load_inputs()


@pytest.fixture(scope="module")
def handoff(inputs):
    return d.consolidate(*inputs)


def test_same_candidate_evidence_and_unknowns_are_preserved(inputs, handoff):
    p, definitions, m = inputs
    assert handoff["portfolio_id"] == p["portfolio_id"]
    assert handoff["mechanics_study_id"] == m["study_id"]
    for key in ("vehicle_candidate_id", "vehicle_evaluation_id", "selection_id"):
        assert handoff[key] == m["load_context"][key]
    comparison = handoff['reference_comparison']
    assert comparison['selection_role'] == 'retired-reference-control-comparison'
    assert comparison['reference_selection_id'] == m['load_context']['selection_id']
    assert comparison['reference_selection_id'] != comparison['active_selection_id']
    assert comparison['current_evaluator_admission'] is False
    assert comparison['numerical_reexecuted'] is False
    assert comparison['active_installed_propulsion_selected'] is False
    assert handoff["linked_mechanics_cases"] == 189
    assert handoff["candidate_count"] == 18
    assert handoff["integrated_selection"] is None
    assert not handoff["stage_1_complete"] and not handoff["stage_2_admission"]
    quantities = {r["candidate_id"]: r for r in p["evaluations"]}
    for row in handoff["evidence"]:
        source = quantities[row["candidate_id"]]
        assert row["quantity_evaluation_id"] == source["evaluation_id"]
        assert row["nominal_quantity_evaluation_id"] == source["quantities"]["evaluation_id"]
        assert row["material_quantities"] == source["quantities"]["by_material"]
        assert row["cost_estimate"] == source["cost_estimate"]
        assert row["cost_estimate"]["production_shifts_per_day"] == 2
        assert row["cost_estimate"]["civil_shifts_per_day"] == 2
        assert {x["case"] for x in row["cost_estimate"]["cases"]} == {"low", "base", "high"}
        assert row["installed_mass_kg"] is None and row["strength_allowable_Pa"] is None
        assert row["physical_deflection_limit_m"] is None
        assert row["evidence_status"]["strength"] == "unknown"
        assert not row["stage_2_admission"]
        assert all(row[key] is False for key in d.FLAGS)
    assert any("relative LIM air-gap" in item for item in handoff["limitations"])
    assert any("never structural resistance" in item for item in handoff["limitations"])


def test_balanced_shortlist_uses_mechanics_and_keeps_all_deferred(inputs, handoff):
    m = inputs[2]
    follow = handoff["followup"]
    assert len(follow["queued_candidate_ids"]) == 6
    assert len(follow["deferred_candidate_ids"]) == 12
    assert len({r["family"] for r in follow["decisions"] if r["state"] == "queued"}) == 6
    assert len(follow["decisions"]) == 18
    assert all(req["stage"] == 1 and not req["stage_2_admission"] and req["native_jobs"] == 0 for req in follow["requests"])
    shuffled = deepcopy(m["evaluations"])
    random.Random(2026).shuffle(shuffled)
    assert d.plan_followup(shuffled, m["archive"]["retained_candidate_ids"]) == follow
    # The reference-profile box balances cost/mass against stiffness rather than
    # merely repeating the cheapest lean-profile stage-zero request.
    queued = {r["candidate_id"]: r for r in handoff["evidence"] if r["candidate_id"] in follow["queued_candidate_ids"]}
    assert any(r["family"] == "reference_box" and r["profile"] == "reference" for r in queued.values())
    assert all(r["candidate_id"] in m["archive"]["retained_candidate_ids"] for r in queued.values())


@pytest.mark.parametrize("budget", [0, 1, 2, 6])
def test_invocation_budget_defers_without_losing_candidates(inputs, budget):
    m = inputs[2]
    value = d.plan_followup(m["evaluations"], m["archive"]["retained_candidate_ids"], budget)
    assert len(value["queued_candidate_ids"]) == budget
    assert len(value["deferred_candidate_ids"]) == 18-budget
    assert len(value["representative_candidate_ids"]) == 6
    assert set(value["queued_candidate_ids"]).isdisjoint(value["deferred_candidate_ids"])
    assert len(value["decisions"]) == 18


@pytest.mark.parametrize("budget", [-1, 7, True, 1.5, None])
def test_invalid_budget_rejected(inputs, budget):
    with pytest.raises(ValueError, match="budget"):
        d.plan_followup(inputs[2]["evaluations"], inputs[2]["archive"]["retained_candidate_ids"], budget)


@pytest.mark.parametrize("metric", d.OBJECTIVES)
@pytest.mark.parametrize("bad", [None, float("nan"), float("inf"), -1, True])
def test_unknown_invalid_objectives_never_become_favourable_zero(inputs, metric, bad):
    rows = deepcopy(inputs[2]["evaluations"])
    rows[0]["metrics"][metric] = bad
    with pytest.raises(ValueError, match="metric"):
        d.plan_followup(rows, inputs[2]["archive"]["retained_candidate_ids"])


@pytest.mark.parametrize("field", ["stage_1_complete", "stage_2_admission", "physical_accepted"])
def test_planner_does_not_promote_unresolved_stage_one(inputs, field):
    rows = deepcopy(inputs[2]["evaluations"])
    rows[0][field] = True
    with pytest.raises(ValueError):
        d.plan_followup(rows, inputs[2]["archive"]["retained_candidate_ids"])


@pytest.mark.parametrize("field", ["parent_portfolio_id", "source_sha256"])
def test_resealed_wrong_parent_or_source_is_rejected(inputs, field):
    p, definitions, m = deepcopy(inputs)
    m[field] = "0"*64 if field == "parent_portfolio_id" else {}
    seal(m, "study_id")
    with pytest.raises(ValueError, match="parent, source"):
        d.consolidate(p, definitions, m)


@pytest.mark.parametrize("field", ["vehicle_candidate_id", "vehicle_evaluation_id", "selection_id", "context_id"])
def test_resealed_selected_vehicle_or_load_swap_is_rejected(inputs, field):
    p, definitions, m = deepcopy(inputs)
    m["load_context"][field] = "0"*64
    if field != "context_id":
        seal(m["load_context"], "context_id")
    seal(m, "study_id")
    with pytest.raises(ValueError, match="load context"):
        d.consolidate(p, definitions, m)


@pytest.mark.parametrize("mutation", ["duplicate-case", "missing-case", "wrong-quantity", "wrong-load", "wrong-model", "wrong-mass", "wrong-cells"])
def test_resealed_case_coverage_and_crosslinks_are_rejected(inputs, mutation):
    p, definitions, m = deepcopy(inputs)
    case = m["cases"][0]
    if mutation == "duplicate-case":
        m["cases"][1] = deepcopy(case)
    elif mutation == "missing-case":
        m["cases"].pop()
        m["calculated_case_count"] -= 1
    else:
        key = {"wrong-quantity": "quantity_evaluation_id", "wrong-load": "load_context_id",
            "wrong-model": "section_model_id", "wrong-mass": "accounted_span_mass_kg", "wrong-cells": "cells"}[mutation]
        old_id = case["evaluation_id"]
        case[key] = [] if mutation == "wrong-cells" else -1 if mutation == "wrong-mass" else "0"*64
        seal(case, "evaluation_id")
        summary = next(r for r in m["evaluations"] if r["candidate_id"] == case["candidate_id"])
        summary["case_evaluation_ids"] = [case["evaluation_id"] if x == old_id else x for x in summary["case_evaluation_ids"]]
        seal(summary, "evaluation_id")
    seal(m, "study_id")
    with pytest.raises(ValueError):
        d.consolidate(p, definitions, m)


def test_resealed_wrong_cost_and_quantity_are_rejected(inputs):
    p, definitions, m = deepcopy(inputs)
    row = p["evaluations"][0]
    row["cost_estimate"]["cases"][1]["scoped_installed_iqd"] = 0
    seal(row, "evaluation_id"); seal(p, "portfolio_id")
    m["parent_portfolio_id"] = p["portfolio_id"]; seal(m, "study_id")
    with pytest.raises(ValueError, match="cost"):
        d.consolidate(p, definitions, m)
    p, definitions, m = deepcopy(inputs)
    row = p["evaluations"][0]
    row["quantities"]["total_nominal_stock_mass_kg"] = 0
    seal(row["quantities"], "evaluation_id"); seal(row, "evaluation_id"); seal(p, "portfolio_id")
    m["parent_portfolio_id"] = p["portfolio_id"]; seal(m, "study_id")
    with pytest.raises(ValueError, match="quantity"):
        d.consolidate(p, definitions, m)


def test_output_verification_is_immutable_and_rejects_resealed_tampering(tmp_path):
    output = tmp_path/"handoff"
    receipt = d.build(output=output, maximum_tasks=2)
    assert receipt["queued"] == 2 and receipt["deferred"] == 16
    original = (output/"result.json").read_bytes()
    assert d.verify(output=output) == receipt
    with pytest.raises(ValueError, match="already exists"):
        d.build(output=output)
    assert (output/"result.json").read_bytes() == original
    value = json.loads(original)
    value["evidence"][0]["installed_mass_kg"] = 0
    seal(value, "handoff_id")
    (output/"result.json").write_bytes(encoded(value))
    manifest = json.loads((output/"manifest.json").read_bytes())
    manifest["handoff_id"] = value["handoff_id"]
    manifest["files_sha256"]["result.json"] = digest(output/"result.json")
    seal(manifest, "manifest_id")
    (output/"manifest.json").write_bytes(encoded(manifest))
    with pytest.raises(ValueError, match="does not reproduce"):
        d.verify(output=output)
    # Verification did not write a refreshed receipt over the tampered payload.
    assert json.loads((output/"result.json").read_bytes())["evidence"][0]["installed_mass_kg"] == 0


def test_stale_receipt_source_and_extra_or_linked_files_are_rejected(tmp_path):
    output = tmp_path/"handoff"
    d.build(output=output)
    manifest = json.loads((output/"manifest.json").read_bytes())
    original = deepcopy(manifest)
    manifest["source_sha256"][d.PRODUCER] = "0"*64
    seal(manifest, "manifest_id")
    (output/"manifest.json").write_bytes(encoded(manifest))
    with pytest.raises(ValueError, match="source epoch"):
        d.verify(output=output)
    (output/"manifest.json").write_bytes(encoded(original))
    (output/"extra").write_text("unexpected")
    with pytest.raises(ValueError, match="payload"):
        d.verify(output=output)
    (output/"extra").unlink()
    (output/"extra").symlink_to(output/"result.json")
    with pytest.raises(ValueError, match="non-symlink"):
        d.verify(output=output)


def test_executing_consumer_must_match_declared_source_root(inputs, tmp_path):
    alternate = tmp_path/d.PRODUCER
    alternate.parent.mkdir(parents=True)
    alternate.write_bytes((d.ROOT/d.PRODUCER).read_bytes()+b"\n# a different consumer implementation\n")
    with pytest.raises(ValueError, match="Loaded civil demonstrator producer"):
        d.consolidate(*inputs, root=tmp_path)


def test_overlapping_parent_and_mechanics_sources_cannot_conflict(inputs):
    p, definitions, m = deepcopy(inputs)
    key = next(iter(p["source_sha256"]))
    assert key in m["source_sha256"]
    p["source_sha256"][key] = "0"*64
    seal(p, "portfolio_id")
    m["parent_portfolio_id"] = p["portfolio_id"]
    seal(m, "study_id")
    with pytest.raises(ValueError, match="source epochs conflict"):
        d.consolidate(p, definitions, m)


@pytest.mark.parametrize("change_control", [True, False])
def test_consistently_resealed_numerical_payload_cannot_borrow_packet_provenance(inputs, change_control):
    p, definitions, m = deepcopy(inputs)
    summary = m["evaluations"][0]
    control = next(case for case in m["cases"]
        if case["candidate_id"] == summary["candidate_id"]
        and case["elastic_hypothesis"] == summary["primary_elastic_hypothesis"]
        and case["load_case"] == "crowd_control" and case["dead_mass_case"] == "high")
    if not change_control:
        control = next(case for case in m["cases"] if case["candidate_id"] == summary["candidate_id"])
    old = control["evaluation_id"]
    if change_control:
        control["all_pose_all_observation_model_deflection_upper_m"] *= 2
    else:
        control["representative_sampled_deflection_m"] = 0
    seal(control, "evaluation_id")
    summary["case_evaluation_ids"] = [control["evaluation_id"] if item == old else item
        for item in summary["case_evaluation_ids"]]
    if change_control:
        summary["metrics"]["crowd_high_mass_model_deflection_upper_m"] = control["all_pose_all_observation_model_deflection_upper_m"]
    seal(summary, "evaluation_id")
    m["archive"] = d.quality_diversity.archive(m["evaluations"], d.OBJECTIVES, ("family",))
    seal(m, "study_id")
    with pytest.raises(ValueError, match="checked publication payloads"):
        d.consolidate(p, definitions, m)


def test_retired_civil_integrity_hold_is_not_a_current_source_bypass(monkeypatch):
    def refuse(root):
        raise ValueError('retired fixture integrity differs')
    monkeypatch.setattr(d.retired_station_reference, 'verify', refuse)
    with pytest.raises(ValueError, match='retired fixture integrity'):
        d.load_inputs()


def test_retired_civil_comparison_rejects_different_current_physical_vehicle(monkeypatch):
    selected = d.selection.load()
    selected['vehicle']['body_candidate_id'] = '0'*64
    monkeypatch.setattr(d.selection, 'load', lambda root: selected)
    with pytest.raises(ValueError, match='physical reference differs'):
        d.load_inputs()

"""Coupled architecture boundaries, modular fit and retained release gates."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

import pytest

from engineering.generative_design import architecture_campaign as feedback
from engineering.generative_design import architecture_mechanical, campaign, coverage


@pytest.mark.parametrize(
    "length,modules,platform",
    [(49.5, 9, 54), (53.1, 10, 60), (53.5, 10, 60), (111, 20, 120)],
)
def test_complete_modules_include_both_end_allowances(length, modules, platform):
    result = feedback.platform_case(length)
    assert result["complete_modules_per_platform_edge"] == modules
    assert result["complete_module_platform_length_m"] == platform
    assert result["minimum_actual_end_allowance_m"] >= 2
    assert result["previous_116m_branch_uses_only_full_modules"] is False
    assert not result["partial_module_adopted"] and not result["site_fit_accepted"]


@pytest.mark.parametrize(
    "length,module,allowance",
    [(0, 6, 2), (111, 0, 2), (111, 6, -1), (float("nan"), 6, 2)],
)
def test_invalid_platform_hypothesis_rejected(length, module, allowance):
    with pytest.raises(ValueError):
        feedback.platform_case(length, module_m=module, end_allowance_m=allowance)


def test_changed_lm3_balances_and_six_car_masses_are_independent():
    mechanical = architecture_mechanical.run()
    for case in mechanical["cases"]:
        feedback.validate_case(feedback.canonical_case(case))
    basis = feedback.read(feedback.BASIS)
    cases = feedback.six_car_cases(basis)
    assert len(cases) == 6
    assert {c["total_mass_kg"] for c in cases} == {384000, 460800}
    assert all(
        c["architecture_id"] == "metro-6car-planning" and len(c["axles"]) == 24
        for c in cases
    )
    for case in cases:
        feedback.validate_case(feedback.canonical_case(case))
    changed = deepcopy(cases[0])
    changed["axles"][0]["force_n"] *= 2
    with pytest.raises(ValueError, match="equilibrium"):
        feedback.validate_case(changed)
    changed = feedback.canonical_case(mechanical["cases"][0])
    changed["architecture_id"] = "metro-6car-planning"
    with pytest.raises(ValueError, match="support identity"):
        feedback.validate_case(changed)


def test_simple_vehicle_demand_scales_with_explicit_mass_without_adopting_capacity():
    basis = feedback.read(feedback.BASIS)
    first = dict(total_mass_kg=100000, cars=3)
    double = dict(total_mass_kg=200000, cars=3)
    a, b = feedback.vehicle_demands(first, basis), feedback.vehicle_demands(
        double, basis
    )
    assert b["kinetic_energy_j"] == 2 * a["kinetic_energy_j"]
    assert b["translational_braking_force_n"] == 2 * a["translational_braking_force_n"]
    assert (
        b["ideal_constant_deceleration_distance_m"]
        == a["ideal_constant_deceleration_distance_m"]
    )
    assert all(
        x["accepted_jack_rating_kg"] is None for x in b["per_point_lift_demands"]
    )
    assert not b["physical_release"]


def test_diagram_matches_symmetric_full_module_end_allowances():
    case = feedback.canonical_case(architecture_mechanical.run()["cases"][1])
    platform = feedback.platform_case(case["train_length_m"])
    root = ET.fromstring(
        feedback.figure(
            dict(cases=[dict(case=case, architecture_id="LM3", platform=platform)])
        )
    )
    rects = root.findall(".//{http://www.w3.org/2000/svg}rect")
    cars = [r for r in rects if r.get("height") == "18"]
    modules = [r for r in rects if r.get("height") == "8"]
    left = float(cars[0].get("x")) - float(modules[0].get("x"))
    right = (
        float(modules[-1].get("x"))
        + float(modules[-1].get("width"))
        - float(cars[-1].get("x"))
        - float(cars[-1].get("width"))
    )
    assert left == pytest.approx(right)
    assert left == pytest.approx(platform["minimum_actual_end_allowance_m"] * 5)


@pytest.fixture(scope="module")
def architecture_run():
    parent = coverage.ROOT / "build/architecture-tests"
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as name:
        output = Path(name) / "run"
        feedback.run(output)
        yield output


def test_full_run_preserves_each_case_scope_and_all_input_gates(architecture_run):
    result = feedback.verify(architecture_run)
    assert result["case_count"] == 12 and result["beam_response_records"] == 12 * 193
    report = feedback.read(architecture_run / "report.json")
    scope = {p["id"]: p for p in campaign.scope()["work_packages"]}
    for affected in report["affected_scope"]:
        assert affected["required_gates"] == scope[affected["id"]]["required_gates"]
        assert (
            affected["completion_predicate"]
            == scope[affected["id"]]["completion_predicate"]
        )
        assert all(affected[k] is False for k in feedback.FLAGS)
    assert all(
        row["required_gates"] == report["basis"]["open_gates"]
        for row in report["cases"]
    )
    assert all(not row["manufacturing_release"] for row in report["cases"])


def test_artifact_tampering_and_stale_sources_are_rejected(
    architecture_run, monkeypatch
):
    target = architecture_run / "architecture-demands.csv"
    original = target.read_bytes()
    target.write_bytes(original + b"changed")
    try:
        with pytest.raises(ValueError, match="artifact changed"):
            feedback.verify(architecture_run)
    finally:
        target.write_bytes(original)
    monkeypatch.setattr(feedback, "sources", lambda: {})
    with pytest.raises(ValueError, match="another source revision"):
        feedback.verify(architecture_run)
    assert (
        feedback.verify(architecture_run, current=False)["current_sources_checked"]
        is False
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("historical integrity must not regenerate planning inputs")

    monkeypatch.setattr(feedback, "six_car_cases", forbidden)
    assert feedback.verify(architecture_run, current=False)["integrity_verified"]


def test_resealed_release_claim_still_fails(architecture_run):
    target = architecture_run / "report.json"
    seal = architecture_run / "receipt.json"
    original, original_seal = target.read_bytes(), seal.read_bytes()
    report = json.loads(original)
    report["engineering_design_complete"] = True
    campaign.write(target, report)
    receipt = json.loads(original_seal)
    receipt["files_sha256"] = feedback.queue_campaign.file_hashes(
        architecture_run, ("receipt.json",)
    )
    campaign.write(seal, receipt)
    try:
        with pytest.raises(ValueError, match="cannot grant release"):
            feedback.verify(architecture_run)
    finally:
        target.write_bytes(original)
        seal.write_bytes(original_seal)

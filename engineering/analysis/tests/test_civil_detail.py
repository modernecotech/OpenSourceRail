"""Independent mechanics and honest closure checks for civil detail search."""

from copy import deepcopy
from hashlib import sha256
import json
import math

import pytest

from engineering.generative_design import civil_detail as civil


@pytest.fixture(scope="module")
def contexts():
    return civil.contexts()


@pytest.fixture(scope="module")
def report():
    return civil.run(budget_per_context=128)


def test_point_load_deflection_matches_closed_form_and_force_scaling():
    L, P, EI = 25.0, 123456.0, 8.7e9
    result = civil.moving_midspan_deflection(L, [{"x_m": 12.0, "force_n": P}], EI)
    assert result["deflection_m"] == pytest.approx(P * L**3 / (48 * EI), rel=1e-13)
    assert result["governing_origin_m"] == pytest.approx(L / 2 - 12.0)
    doubled = civil.moving_midspan_deflection(L, [{"x_m": 12.0, "force_n": 2 * P}], EI)
    assert doubled["deflection_m"] == pytest.approx(2 * result["deflection_m"])
    assert result["full_span_maximum"] is False


def test_asymmetric_axles_against_independent_virtual_work():
    # Independent midpoint deflection: integral M(unit-midpoint)*M(actual)/EI
    # with Simpson quadrature. Dense origin scan checks the analytical optimum
    # without using the analytical displacement implementation in the module.
    L, EI = 20.0, 2.1e9
    axles = [{"x_m": 0.0, "force_n": 80000.0}, {"x_m": 7.3, "force_n": 230000.0}]
    result = civil.moving_midspan_deflection(L, axles, EI)

    def virtual_work(origin):
        n = 800
        h = L / n
        total = 0.0
        for i in range(n + 1):
            x = h * i
            unit_moment = min(x, L - x) / 2
            moment = 0.0
            for axle in axles:
                a = origin + axle["x_m"]
                if 0 <= a <= L:
                    moment += axle["force_n"] * ((L - a) * x / L - max(0, x - a))
            weight = 1 if i in (0, n) else 4 if i % 2 else 2
            total += weight * unit_moment * moment
        return total * h / (3 * EI)

    assert virtual_work(result["governing_origin_m"]) == pytest.approx(
        result["deflection_m"], rel=2e-5
    )
    dense = max(virtual_work(-7.3 + i * 27.3 / 120) for i in range(121))
    assert dense <= result["deflection_m"] * 1.00002
    assert dense >= result["deflection_m"] * 0.999


def test_footing_diagram_satisfies_force_moment_and_rejects_soil_tension():
    N, M, B = 1e6, 4e5, 3.5
    result = civil.footing_pressure(N, M, B)
    low, high = (
        result["linear_minimum_pressure_pa"],
        result["linear_maximum_pressure_pa"],
    )
    assert (low + high) * B**2 / 2 == pytest.approx(N)
    assert (high - low) * B**3 / 12 == pytest.approx(M)
    assert result["full_contact"] is True
    partial = civil.footing_pressure(N, N * 0.8, B)
    contact = partial["compression_contact_length_m"]
    assert partial["full_contact"] is False
    assert partial[
        "compression_maximum_pressure_pa"
    ] * contact * B / 2 == pytest.approx(N)
    assert B / 2 - contact / 3 == pytest.approx(0.8)
    overturning = civil.footing_pressure(N, N * B / 2, B)
    assert overturning["equilibrium_possible"] is False
    assert overturning["compression_maximum_pressure_pa"] is None


def test_architectures_remain_distinct_and_context_tampering_rejected(contexts):
    assert len(contexts) == 4
    assert {c["span_m"] for c in contexts} == {20.0, 25.0}
    assert {len(c["source_case"]["axles"]) for c in contexts} == {12, 24}
    for context in contexts:
        original = deepcopy(context)
        row = civil.assess(civil.seed(context), context)
        assert context == original
        assert row["configuration_id"] == context["configuration_id"]
        assert row["source_case_sha256"] == context["source_case_sha256"]
        assert row["source_changing_proposal"] is True
    tampered = deepcopy(contexts[0])
    tampered["live_end_reaction_n"] *= 0.5
    with pytest.raises(ValueError, match="exact current"):
        civil.assess(civil.seed(tampered), tampered)


def test_shear_depth_uses_declared_lower_chord_centroid_not_extreme_strand(contexts):
    # Independent hand case:96strands at64lower/32upper. The lower chord has
    # eight equal-area rows at100,160,...520mm, so its centroid is310mm.
    # Extreme-bottom100mm would overstate d by210mm and both shear capacities.
    context = contexts[0]
    assert context["source_beam_variables"]["strand_count"] == 96
    row = civil.assess(civil.seed(context), context)
    geometry = row["geometry"]
    assert geometry["provisional_tension_chord_strand_count"] == 64
    assert geometry["provisional_tension_chord_centroid_z_m"] == pytest.approx(0.310)
    assert geometry["provisional_effective_depth_m"] == pytest.approx(1.090)
    assert geometry["provisional_shear_lever_arm_m"] == pytest.approx(0.981)
    # Four12mm vertical legs,300mm pitch,500/1.15MPa and cot(theta)=2.5.
    # Concrete web total600mm; nu=.48, fcd=.85*50/1.5MPa.
    assert row["metrics"]["link_shear_resistance_n"] == pytest.approx(
        1_607_949.075, rel=1e-8
    )
    assert row["metrics"]["strut_shear_resistance_n"] == pytest.approx(
        2_760_331.034, rel=1e-8
    )
    assert geometry["provisional_effective_depth_m"] < geometry["beam_variables"][
        "depth_m"
    ] - min(p["z_m"] for p in context["strand_points"])
    assert any(
        c["id"] == "beam_flexural_resistance" and c["state"] == "unknown"
        for c in row["checks"]
    )


def test_controlled_targets_preserve_source_revision_without_claiming_adoption(
    contexts,
):
    register = json.loads(civil.CONTROLLED_TYPES.read_text())
    inventory = {r["type_id"]: r for r in register["type_register"]}
    digest = sha256(civil.CONTROLLED_TYPES.read_bytes()).hexdigest()
    for context in contexts[:2]:
        row = civil.assess(civil.seed(context), context)
        mappings = row["controlled_target_mappings"]
        assert len(mappings) == (3 if context["span_m"] == 20 else 4)
        assert set(row["component_ids"]) == set(row["proposed_detail_component_ids"])
        assert not set(row["proposed_detail_component_ids"]) & set(inventory)
        assert (
            "OUTER-END-FOOTING-RESEARCH"
            in row["unmapped_proposed_detail_component_ids"]
        )
        for mapping in mappings:
            source = inventory[mapping["type_id"]]
            assert mapping["source_revision_sha256"] == digest
            assert mapping["source_geometry"] == source["source_geometry"]
            assert mapping["package_id"] == source["package_id"]
            assert not mapping["exact_fit_or_adoption"]
            assert not mapping["full_component_coverage"]
            assert not mapping["configuration_compatible"]
        beam = [m for m in mappings if m["type_id"] == "OSR-TYPE-D36A7871D9B7"]
        assert len(beam) == (context["span_m"] == 25)
        assert not row["exact_fit_or_adoption"]
        assert not row["full_component_coverage"]
        if context["span_m"] == 20:
            assert "PI20" in row["unmapped_proposed_detail_component_ids"]


def test_coupled_gross_mass_recomputes_force_reaction_moment_deflection(contexts):
    original = contexts[0]
    original_copy = deepcopy(original)
    coupled = civil.coupled_context(original, original["source_case"]["total_mass_kg"])
    baseline = civil.assess(civil.seed(original), original)
    new = civil.assess(civil.seed(coupled), coupled)
    assert original == original_copy
    assert (
        coupled["source_case"]["total_mass_kg"]
        == 2 * original["source_case"]["total_mass_kg"]
    )
    assert coupled["parent_source_case"] == original["source_case"]
    assert coupled["architecture_id"] == original["architecture_id"]
    assert coupled["source_case_sha256"] != original["source_case_sha256"]
    for a, b in zip(coupled["applied_axles"], original["applied_axles"]):
        assert a["x_m"] == b["x_m"]
        assert a["force_n"] == pytest.approx(2 * b["force_n"])
    assert coupled["live_end_reaction_n"] == pytest.approx(
        2 * original["live_end_reaction_n"]
    )
    assert new["metrics"]["peak_live_moment_nm"] == pytest.approx(
        2 * baseline["metrics"]["peak_live_moment_nm"]
    )
    assert new["metrics"]["live_midspan_deflection"]["deflection_m"] == pytest.approx(
        2 * baseline["metrics"]["live_midspan_deflection"]["deflection_m"]
    )
    assert new["configuration_id"] != baseline["configuration_id"]
    with pytest.raises(ValueError, match="original uncoupled"):
        civil.coupled_context(coupled, 1)
    assert civil.model_definition(new)["physical_release"] is False


def test_coupled_six_car_footing_geometry_repair_preserves_soil_limit_and_mass(
    contexts,
):
    # Exact root scenario counterexample:59.879914t gross added train-member
    # sensitivity, not a claimed net mass or accepted railway/geotechnical case.
    original = next(
        c
        for c in contexts
        if c["architecture_id"] == "metro-6car-planning" and c["span_m"] == 25
    )
    context = civil.coupled_context(original, 59879.91426942624)
    variables = dict(
        beam_depth_m=1.55,
        beam_stem_width_m=0.36,
        footing_width_m=4.5,
        pad_length_m=0.5,
        stirrup_diameter_m=0.012,
        stirrup_spacing_m=0.2,
    )
    failed = civil.assess(variables, context)
    assert failed["failed_checks"] == ["footing_pressure"]
    pressure = next(c for c in failed["checks"] if c["id"] == "footing_pressure")
    assert pressure["value"] == pytest.approx(150291.47794014745, rel=1e-12)
    assert pressure["limit"] == 150000
    larger = dict(variables, footing_width_m=5.0)
    assert larger in civil.propose(failed, context)
    repaired = civil.assess(larger, context)
    assert not repaired["failed_checks"]
    repaired_pressure = next(
        c for c in repaired["checks"] if c["id"] == "footing_pressure"
    )
    assert repaired_pressure["value"] < repaired_pressure["limit"] == 150000
    # (5^2-4.5^2)*0.8*2500 =9.5t extra concrete must propagate into N and mass.
    assert repaired["objectives"]["mass_kg"] - failed["objectives"][
        "mass_kg"
    ] == pytest.approx(9500)
    assert repaired["metrics"]["foundation_vertical_n"] - failed["metrics"][
        "foundation_vertical_n"
    ] == pytest.approx(9500 * 9.80665)
    assert repaired["geometry"]["site_footprint_accepted"] is False
    assert any(
        c["id"] == "site_ground" and c["state"] == "unknown" for c in repaired["checks"]
    )
    assert not repaired["manufacturing_release"]
    footing = next(
        p
        for p in civil.model_definition(repaired)["parts"]
        if p["id"] == "footing-concrete-envelope"
    )
    assert footing["size_m"] == [5.0, 5.0, 0.8]


def test_search_repairs_actual_failures_and_retains_rejections(report, contexts):
    by_id = {r["id"]: r for r in report["candidates"]}
    by_context = {c["id"]: c for c in contexts}
    assert len(civil.candidate_family()) == 432
    assert report["rejected_candidate_count"] > 0
    assert all(h["evaluations"] <= 128 for h in report["iteration_history"])
    for row in report["candidates"]:
        if row["parent_id"]:
            parent = by_id[row["parent_id"]]
            assert parent["failed_checks"]
            assert row["generation"] == parent["generation"] + 1
            assert row["variables"] in civil.propose(
                parent, by_context[row["context_id"]]
            )
            assert (
                sum(
                    row["variables"][k] != parent["variables"][k]
                    for k in row["variables"]
                )
                == 1
            )
        assert row["local_screen_feasible"] == (not row["failed_checks"])
        assert row["rejected_known_checks"] == bool(row["failed_checks"])
    assert "tendon_link_clearance" in report["candidates"][0]["failed_checks"]
    # Width repair alone must not inherit the original beam's stress pass.
    initial = civil.assess(civil.seed(contexts[1]), contexts[1])
    wider = dict(initial["variables"], beam_stem_width_m=0.36)
    wide_row = civil.assess(wider, contexts[1])
    assert (
        wide_row["geometry"]["beam_section"]["area_m2"]
        > initial["geometry"]["beam_section"]["area_m2"]
    )
    assert "beam_service_no_tension" in wide_row["failed_checks"]


def test_local_survivors_keep_unknown_qualification_and_native_envelopes(report):
    selected = [r for r in report["candidates"] if r["local_screen_feasible"]]
    assert (
        len(selected) == 4
    ), "each independent current context must reach a local detail survivor"
    for row in selected:
        assert all(c["state"] != "fail" for c in row["checks"])
        assert sum(c["state"] == "unknown" for c in row["checks"]) >= 10
        assert not row["engineering_design_complete"]
        assert not row["manufacturing_release"]
        assert not row["physical_release"]
        assert row["materials"]["accepted"] is False
        assert row["manufacturing"]["issued_bar_schedule"] is False
        assert row["objectives"]["cost"] is None
        assert "one beam" in row["objectives"]["mass_scope"]
        model = civil.model_definition(row)
        assert len({p["id"] for p in model["parts"]}) == len(model["parts"])
        assert any(p["id"] == "footing-concrete-envelope" for p in model["parts"])
        assert model["physical_release"] is False
    assert all(
        not report[k]
        for k in (
            "physical_release",
            "manufacturing_release",
            "engineering_design_complete",
        )
    )


@pytest.mark.parametrize("invalid", [True, 0, 433, 1.5])
def test_invalid_search_budgets_rejected(invalid):
    with pytest.raises(ValueError):
        civil.run(budget_per_context=invalid)


@pytest.mark.parametrize("invalid", [math.nan, math.inf, True, -1])
def test_invalid_mechanics_inputs_rejected(invalid):
    with pytest.raises(ValueError):
        civil.footing_pressure(invalid, 1, 3)
    with pytest.raises(ValueError):
        civil.moving_midspan_deflection(invalid, [{"x_m": 0, "force_n": 1}], 1)

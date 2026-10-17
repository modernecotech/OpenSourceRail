"""Independent influence-line, compatibility, geometry and force-unit controls."""

from collections import Counter
import json
import math

import pytest
from engineering.generative_design import architecture_civil as a
from engineering.design_engine.civil_qualification import elastic_shortening
from engineering.factory_examples.models import volume


def variables(**changes):
    v = dict(
        depth_m=1.55,
        stem_width_m=0.36,
        strand_count=144,
        lower_strand_fraction=0.75,
        lift_fraction=0.22,
    )
    v.update(changes)
    return v


def test_exact_single_axle_events_and_continuous_peak_with_one_explicit_scale():
    envelope = a.live_envelope([dict(x_m=9, force_n=1000)], sensitivity=1.25)
    assert envelope["pattern"]["source_axles"][0]["force_n"] == 1000
    assert envelope["pattern"]["axles"][0]["force_n"] == 1250
    for L in (20.0, 25.0):
        r = envelope["responses"][str(L)]
        assert r["peak_live_moment_nm"] == pytest.approx(1250 * L / 4)
        assert r["maximum_live_reaction_n"] == pytest.approx(1250)
        assert r["continuous_peak"]["x_m"] == pytest.approx(L / 2)
        assert len(r["stations"]) == 41
    legacy = a.normalise_pattern([dict(x_m=1, force_n=86450.625)], sensitivity=1)
    assert legacy["source_total_force_n"] == 86450.625
    assert legacy["applied_total_force_n"] == 86450.625
    assert not legacy["source_forces_renormalised"]


def test_two_axle_peak_matches_classical_formula_and_translation_reversal():
    p = [dict(x_m=3, force_n=1000), dict(x_m=6, force_n=1000)]
    first = a.live_envelope(p, sensitivity=1)
    translated = a.live_envelope(
        [dict(x_m=r["x_m"] + 100, force_n=r["force_n"]) for r in p], sensitivity=1
    )
    for L in (20.0, 25.0):
        assert first["responses"][str(L)]["peak_live_moment_nm"] == pytest.approx(
            1000 * (2 * L - 3) ** 2 / (8 * L)
        )
        assert first["responses"][str(L)] == translated["responses"][str(L)]
    p = [
        dict(x_m=0, force_n=1000),
        dict(x_m=3, force_n=2000),
        dict(x_m=7.1, force_n=800),
    ]
    forward = a.live_envelope(p, sensitivity=1)
    reverse = a.live_envelope(
        [dict(x_m=7.1 - r["x_m"], force_n=r["force_n"]) for r in p], sensitivity=1
    )
    for L in (20.0, 25.0):
        assert forward["responses"][str(L)]["peak_live_moment_nm"] == pytest.approx(
            reverse["responses"][str(L)]["peak_live_moment_nm"]
        )
        assert forward["responses"][str(L)]["maximum_live_reaction_n"] == pytest.approx(
            reverse["responses"][str(L)]["maximum_live_reaction_n"]
        )


def test_train_off_fibre_extreme_is_retained_separately_from_loaded_section():
    r = a.fibre_stresses(
        force_n=1e6,
        prestress_moment_nm=1e5,
        gravity_moment_nm=2e5,
        live_moment_nm=3e5,
        retention=0.8,
        section=dict(area_m2=2, inertia_x_m4=0.4, centroid_z_m=0.7, depth_m=1.5),
    )
    assert r["train_off"]["top_pa"] == pytest.approx(640000)
    assert r["train_off"]["soffit_pa"] == pytest.approx(190000)
    assert r["train_on"]["top_pa"] == pytest.approx(1240000)
    assert r["train_on"]["soffit_pa"] == pytest.approx(-335000)
    assert r["minimum_compression_pa"] == pytest.approx(-335000)
    assert r["maximum_compression_pa"] == pytest.approx(1240000)


def test_affine_shortening_cache_matches_direct_coupled_group_solve():
    state = a.mechanical_state(variables())
    section = state["section"]
    counts = Counter(p["z_m"] for p in state["strand_points"])
    groups = [
        dict(
            metallic_area_m2=n * 0.00014,
            pretransfer_stress_pa=1100e6,
            steel_modulus_pa=195e9,
            eccentricity_m=section["centroid_z_m"] - z,
        )
        for z, n in sorted(counts.items())
    ]
    row = state["cases"]["25.0"]["stations"][37]
    losses = elastic_shortening(
        groups,
        area_m2=section["area_m2"],
        inertia_m4=section["inertia_x_m4"],
        concrete_modulus_pa=30e9,
        self_weight_moment_nm=row["dead_moment_nm"],
    )
    forces = [
        g["metallic_area_m2"] * (g["pretransfer_stress_pa"] - v)
        for g, v in zip(groups, losses)
    ]
    assert row["prestress"]["force_n"] == pytest.approx(sum(forces), rel=1e-12)
    assert row["prestress"]["prestress_moment_nm"] == pytest.approx(
        sum(f * g["eccentricity_m"] for f, g in zip(forces, groups)), rel=1e-12
    )
    Pe = sum(f * g["eccentricity_m"] for f, g in zip(forces, groups))
    top = (
        sum(forces) / section["area_m2"]
        - (Pe - row["dead_moment_nm"])
        * (section["depth_m"] - section["centroid_z_m"])
        / section["inertia_x_m4"]
    )
    soffit = (
        sum(forces) / section["area_m2"]
        + (Pe - row["dead_moment_nm"])
        * section["centroid_z_m"]
        / section["inertia_x_m4"]
    )
    assert row["transfer"]["train_off"]["top_pa"] == pytest.approx(top, rel=1e-12)
    assert row["transfer"]["train_off"]["soffit_pa"] == pytest.approx(soffit, rel=1e-12)
    # Returned public state must not mutate the cache shared across patterns.
    state["section"]["area_m2"] = 0
    assert a.mechanical_state(variables())["section"]["area_m2"] > 0


def test_cached_mechanics_rebinds_to_actual_changed_basis_and_space_files(
    tmp_path, monkeypatch
):
    for relative in a.SOURCES:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((a.ROOT / relative).read_bytes())
    monkeypatch.setattr(a, "ROOT", tmp_path)
    monkeypatch.setattr(
        a.civil,
        "SPACE",
        tmp_path / "engineering/generative_design/data/civil-space.json",
    )
    first = a.mechanical_state(variables())
    path = tmp_path / "engineering/factory_examples/data/basis.json"
    basis = json.loads(path.read_text())
    basis["assumptions"]["strand_initial_stress_pa"] = 1e9
    path.write_text(json.dumps(basis))
    second = a.mechanical_state(variables())
    assert first["source_fingerprint"] != second["source_fingerprint"]
    assert second["initial_bed_force_n"] == pytest.approx(144 * 0.00014 * 1e9)
    path = a.civil.SPACE
    space = json.loads(path.read_text())
    space["geometry"]["deck_width_m"] = 3
    path.write_text(json.dumps(space))
    third = a.mechanical_state(variables())
    assert second["source_fingerprint"] != third["source_fingerprint"]
    assert third["section"]["area_m2"] - second["section"]["area_m2"] == pytest.approx(
        0.1 * 0.22
    )


def test_expanded_native_geometry_mass_and_strand_count_are_actual():
    v = variables(depth_m=1.7, strand_count=160)
    state = a.mechanical_state(v)
    model = a.model_definition(v)
    concrete = sum(volume(p) for p in model["parts"] if p["role"] == "design-solid")
    mass = concrete * 2500 + 160 * 0.00014 * 25 * (7850 - 2500)
    assert state["cases"]["25.0"][
        "known_concrete_plus_strand_mass_kg"
    ] == pytest.approx(mass)
    assert state["initial_bed_force_n"] == pytest.approx(160 * 0.00014 * 1100e6)
    assert sum(p["role"] == "strand-envelope" for p in model["parts"]) == 160
    assert state["section"]["depth_m"] == 1.7
    assert not model["physical_release"]


def test_failed_crowded_layout_and_unknown_acceptance_are_not_hidden():
    v = variables(depth_m=1.155, stem_width_m=0.3, strand_count=160)
    r = a.assess_pattern(
        [dict(variables=v)], [dict(x_m=0, force_n=1e8)], sensitivity=1.25
    )
    row = r["candidates"][0]
    assert row["metrics"]["minimum_strand_surface_gap_m"] < 0
    assert row["checks"]["strand_geometry"]["status"] == "failed"
    assert row["checks"]["grip_spacing"]["status"] == "failed"
    assert row["checks"]["service_no_tension"]["status"] == "failed"
    assert not row["conditional_stress_and_geometry_pass"]
    assert not r["selected_candidate_ids"]
    assert all(g["status"] == "unknown" for g in row["remaining_gates"])
    assert (
        row["accepted_bed_capacity_n"] is None
        and row["accepted_hook_capacity_kg"] is None
    )
    assert not row["engineering_design_complete"] and not row["physical_release"]


def test_finite_family_stable_ids_and_invalid_inputs():
    family = a.candidate_family()
    assert len(family) == 193 and len({r["id"] for r in family}) == 193
    assert family == a.candidate_family()
    for p in (
        [],
        [dict(x_m=0, force_n=-1)],
        [dict(x_m=0, force_n=1), dict(x_m=0, force_n=1)],
        [dict(x_m=float("inf"), force_n=1)],
    ):
        with pytest.raises(ValueError):
            a.live_envelope(p)
    for factor in (0.9, 2.1, True, float("nan")):
        with pytest.raises(ValueError):
            a.live_envelope([dict(x_m=0, force_n=1)], sensitivity=factor)
    with pytest.raises(ValueError):
        a.mechanical_state(variables(depth_m=2))

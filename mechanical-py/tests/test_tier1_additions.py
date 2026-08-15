"""Smoke tests for the Tier-1 additions: turnouts, depot, clearance,
PRM accessibility. Each test builds the parametric geometry and
checks that it has non-zero volume + sensible bounding-box extents."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from osr_mech.accessibility import (
    add_prm_zones_to_car,
    platform_tactile_path,
    ACCESSIBILITY_SPEC,
)
from osr_mech.clearance import (
    EN_15273_INFERRED,
    InfrastructureFeature,
    check_feature,
    envelope_swept_on_curve,
    reference_envelope,
    swept_envelope_part,
)
from osr_mech.depot import DEFAULT_STALLS, DepotArchetype, depot_footprint, depot_layout, throat_turnout_count
from osr_mech.track.turnout import CATALOGUE, TurnoutTangent, turnout, turnout_footprint_mm


# ---------------------------------------------------------------------------
# Turnout catalogue
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tangent", list(TurnoutTangent))
def test_turnout_builds_non_zero_volume(tangent: TurnoutTangent) -> None:
    t = turnout(tangent)
    assert t.volume > 0, f"{tangent.value} turnout has zero volume"


def test_turnout_lengths_increase_with_flatter_tangent() -> None:
    """A 1:18.5 turnout must be strictly longer than a 1:9 — flatter
    tangent = gentler diverging curve = more length."""
    L_1_9, _ = turnout_footprint_mm(TurnoutTangent.T_1_9)
    L_1_14, _ = turnout_footprint_mm(TurnoutTangent.T_1_14)
    L_1_18_5, _ = turnout_footprint_mm(TurnoutTangent.T_1_18_5)
    assert L_1_9 < L_1_14 < L_1_18_5


def test_turnout_reverse_speed_scales_with_tangent() -> None:
    """Flatter tangent + bigger radius → higher reverse-route speed."""
    speeds = [CATALOGUE[t].max_reverse_speed_kmh for t in TurnoutTangent]
    assert speeds == sorted(speeds)


def test_turnout_template_matches_mechanical_catalogue() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    kits = tomllib.loads((repo_root / "lib/templates/switches.toml").read_text())["kits"]
    template_ids = {
        TurnoutTangent.T_1_9: "no-9-mainline",
        TurnoutTangent.T_1_14: "no-14-crossover",
        TurnoutTangent.T_1_18_5: "no-185-shared",
    }
    for tangent, kit_id in template_ids.items():
        geometry = CATALOGUE[tangent]
        kit = kits[kit_id]
        assert float(kit["total_length_m"]) * 1000 == geometry.total_length_mm
        assert float(kit["switch_blade_length_m"]) * 1000 == geometry.switch_blade_length_mm
        assert float(kit["crossing_length_m"]) * 1000 == geometry.crossing_length_mm
        assert float(kit["diverging_radius_m"]) == geometry.diverging_radius_m
        assert int(kit["sleeper_count"]) == geometry.sleeper_count


# ---------------------------------------------------------------------------
# Depot layout
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("archetype", list(DepotArchetype))
def test_depot_builds_within_ceiling(archetype: DepotArchetype) -> None:
    d = depot_layout(archetype=archetype)
    assert d.volume > 0


def test_depot_stall_count_clamped_to_ceiling() -> None:
    """Over-requesting stalls is silently clamped to the archetype
    ceiling per RFC 0014."""
    fp = depot_footprint(DepotArchetype.LAYUP_MINIMAL, stalls=100)
    assert fp.stall_count == 6


@pytest.mark.parametrize("archetype", list(DepotArchetype))
def test_depot_default_stalls_and_throat_turnouts_match_reference(archetype: DepotArchetype) -> None:
    fp = depot_footprint(archetype)
    model = depot_layout(archetype)
    assert fp.stall_count == DEFAULT_STALLS[archetype]
    turnout_children = [child for child in model.children if child.label.startswith("Depot throat turnout")]
    assert len(turnout_children) == throat_turnout_count(fp.stall_count)


def test_main_heavy_has_wheel_lathe() -> None:
    fp = depot_footprint(DepotArchetype.MAIN_HEAVY)
    assert fp.has_wheel_lathe


def test_layup_minimal_has_no_shed() -> None:
    fp = depot_footprint(DepotArchetype.LAYUP_MINIMAL)
    assert fp.shed_length_m == 0


def test_training_wing_only_on_main_heavy() -> None:
    fp_main = depot_footprint(
        DepotArchetype.MAIN_HEAVY, with_training_wing=True
    )
    fp_sec = depot_footprint(
        DepotArchetype.SECONDARY_MEDIUM, with_training_wing=True
    )
    assert fp_main.has_training_wing
    assert not fp_sec.has_training_wing


# ---------------------------------------------------------------------------
# Kinematic envelope + clearance
# ---------------------------------------------------------------------------


def test_reference_envelope_has_nonzero_sway() -> None:
    e = reference_envelope()
    assert e.lateral_sway_mm > 0
    assert e.vertical_mm > 0


def test_tight_curve_increases_end_throw() -> None:
    base = reference_envelope()
    e200 = envelope_swept_on_curve(base, radius_m=200.0)
    e1000 = envelope_swept_on_curve(base, radius_m=1_000.0)
    assert e200.end_throw_mm > e1000.end_throw_mm


def test_tangent_radius_keeps_base_envelope() -> None:
    base = reference_envelope()
    e = envelope_swept_on_curve(base, radius_m=1e10)
    assert e.end_throw_mm == base.end_throw_mm
    assert e.mid_throw_mm == base.mid_throw_mm


def test_tunnel_wall_pass() -> None:
    """A tunnel wall at 2 000 mm lateral offset passes for the
    reference envelope (body half-width 1 325 + sway 60 = 1 385)."""
    wall = InfrastructureFeature(
        name="tunnel wall",
        lateral_offset_mm=2_000.0,
        min_z_mm=0.0,
        max_z_mm=4_500.0,
    )
    report = check_feature(reference_envelope(), wall)
    assert report.passes
    assert report.lateral_clearance_mm > 500.0


def test_tight_curve_platform_edge_fails() -> None:
    """A platform edge at exactly 1 385 mm fails once end-throw is
    added from a tight curve."""
    base = reference_envelope()
    e = envelope_swept_on_curve(base, radius_m=150.0)
    edge = InfrastructureFeature(
        name="platform edge (too tight curve)",
        lateral_offset_mm=1_385.0,
        min_z_mm=0.0,
        max_z_mm=1_100.0,
    )
    report = check_feature(
        e, edge, body_end_from_midpoint_mm=_REF_BODY_HALF_LENGTH
    )
    assert not report.passes, f"expected fail, got {report}"


_REF_BODY_HALF_LENGTH = 11_000.0


def test_swept_envelope_part_has_volume() -> None:
    e = reference_envelope()
    p = swept_envelope_part(e)
    assert p.volume > 0


# ---------------------------------------------------------------------------
# PRM accessibility
# ---------------------------------------------------------------------------


def test_prm_zones_have_expected_counts() -> None:
    zones = add_prm_zones_to_car()
    children = list(zones.children)
    labels = [getattr(c, "label", "") or "" for c in children]
    assert sum("Wheelchair bay" in l for l in labels) == 2
    assert sum("Priority seat" in l for l in labels) == 4
    assert sum("Tactile" in l for l in labels) == 3


def test_prm_catalogue_constants_match_car() -> None:
    """The catalogue count must match what the geometry actually emits."""
    spec = ACCESSIBILITY_SPEC
    zones = add_prm_zones_to_car()
    labels = [getattr(c, "label", "") or "" for c in zones.children]
    assert (
        sum("Wheelchair bay" in l for l in labels) == spec.wheelchair_bays_per_car
    )
    assert sum("Priority seat" in l for l in labels) == spec.priority_seats_per_car


def test_platform_tactile_path_scales_with_length() -> None:
    short = platform_tactile_path(75.0)
    long = platform_tactile_path(150.0)
    assert long.volume > short.volume
    bb_short = short.bounding_box()
    bb_long = long.bounding_box()
    assert (bb_long.max.X - bb_long.min.X) == pytest.approx(150_000.0, abs=1.0)
    assert (bb_short.max.X - bb_short.min.X) == pytest.approx(75_000.0, abs=1.0)

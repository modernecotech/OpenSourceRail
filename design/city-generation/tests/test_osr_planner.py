"""Tests for the auto-planner. Uses the Samawah OSM cache so they
run offline."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from osr_planner.anchors import Anchor, DEFAULT_WEIGHTS
from osr_planner.lines import (
    LinePlan, curvature_penalty, plan_lines, transfer_reachability,
)
from osr_planner.stations import (
    StationCandidate, coverage_score, place_stations, target_station_count,
)


REPO = Path(__file__).resolve().parents[3]
OSM_CACHE = REPO / "docs/screenshots/.cache/osm"
SAMAWAH_BBOX = (31.265, 45.200, 31.360, 45.340)


# ---------------------------------------------------------------------------
# Anchors + weights
# ---------------------------------------------------------------------------


def test_weights_have_expected_ordering() -> None:
    """Railway > university > city > suburb > neighbourhood."""
    W = DEFAULT_WEIGHTS
    assert W["railway-station"] > W["university"]
    assert W["university"] > W["city"]
    assert W["city"] > W["suburb"]
    assert W["suburb"] > W["neighbourhood"]


# ---------------------------------------------------------------------------
# Station placement
# ---------------------------------------------------------------------------


def _fake_anchors(n: int = 20) -> list[Anchor]:
    """Synthetic anchors in a 0.05° grid for offline tests."""
    out = []
    for i in range(n):
        la = 31.30 + (i % 5) * 0.010
        lo = 45.25 + (i // 5) * 0.010
        out.append(Anchor(
            kind="neighbourhood",
            name=f"area-{i}",
            lat=la, lon=lo,
            weight=18.0,
        ))
    return out


def test_target_scales_with_population() -> None:
    assert target_station_count(50_000) == 8  # clamped
    assert target_station_count(100_000) == 10
    assert target_station_count(220_000) == 22
    assert target_station_count(1_000_000) == 40  # clamped


def test_place_stations_respects_min_spacing() -> None:
    anchors = _fake_anchors()
    stations = place_stations(
        anchors=anchors, population=100_000,
        min_spacing_m=1_500.0,
    )
    # Every pair of stations must be ≥ min_spacing apart.
    from osr_planner.anchors import haversine_m
    for i, a in enumerate(stations):
        for b in stations[i + 1:]:
            assert haversine_m((a.lat, a.lon), (b.lat, b.lon)) >= 1_500.0


def test_coverage_score_bounds() -> None:
    anchors = _fake_anchors(10)
    cov_zero = coverage_score([], anchors)
    assert cov_zero == 0.0
    # One station at the centre should cover the centre ±walk_radius.
    mid = StationCandidate(
        id="mid", name="mid",
        lat=31.320, lon=45.270,
        archetype="standard", score=1.0, serves=(),
    )
    cov = coverage_score([mid], anchors, walk_radius_m=2_000.0)
    assert 0.0 < cov <= 1.0


# ---------------------------------------------------------------------------
# Line planning
# ---------------------------------------------------------------------------


def test_plan_lines_respects_max_lines() -> None:
    anchors = _fake_anchors(20)
    stations = place_stations(anchors=anchors, population=200_000)
    lines = plan_lines(stations, max_lines=2)
    assert len(lines) <= 2


def test_transfer_reachability_hub_and_spoke() -> None:
    """When every line includes the hub, reachability is 100%."""
    anchors = _fake_anchors(15)
    stations = place_stations(anchors=anchors, population=150_000)
    lines = plan_lines(stations)
    assert transfer_reachability(lines) == pytest.approx(1.0, abs=1e-9), (
        "hub-and-spoke topology should give 100% transfer reachability"
    )


def test_single_line_for_small_city() -> None:
    stations = [
        StationCandidate(id=f"s{i}", name=f"s{i}",
                         lat=31.3 + i * 0.005, lon=45.25,
                         archetype="standard", score=1.0, serves=())
        for i in range(3)
    ]
    lines = plan_lines(stations)
    assert len(lines) == 1


def test_curvature_penalty_zero_for_straight_line() -> None:
    """A perfectly straight line has zero curvature."""
    stations = [
        StationCandidate(id=f"s{i}", name=f"s{i}",
                         lat=31.3, lon=45.25 + i * 0.005,
                         archetype="standard", score=1.0, serves=())
        for i in range(5)
    ]
    line = LinePlan(id="x", name="x", station_ids=[s.id for s in stations])
    penalty = curvature_penalty(line, stations)
    assert penalty < 0.1, f"straight line got curvature {penalty:.3f}"


def test_curvature_penalty_large_for_zigzag() -> None:
    """A V-shape has large curvature."""
    stations = [
        StationCandidate(id="a", name="a", lat=31.30, lon=45.25,
                         archetype="standard", score=1.0, serves=()),
        StationCandidate(id="b", name="b", lat=31.31, lon=45.25,
                         archetype="standard", score=1.0, serves=()),
        StationCandidate(id="c", name="c", lat=31.30, lon=45.26,
                         archetype="standard", score=1.0, serves=()),
    ]
    line = LinePlan(id="x", name="x", station_ids=["a", "b", "c"])
    penalty = curvature_penalty(line, stations)
    assert penalty > 1.5, f"V-shape should have large curvature, got {penalty:.3f}"


# ---------------------------------------------------------------------------
# End-to-end: Samawah plan beats hand-crafted on coverage + transfers.
#
# Runs only if the OSM cache is present (CI-optional).
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not OSM_CACHE.exists() or not any(OSM_CACHE.glob("anchors-*.json")),
    reason="OSM Overpass cache not present; run once with network access.",
)
def test_samawah_plan_meets_quality_thresholds() -> None:
    from osr_planner.planner import CityInputs, plan_city

    inputs = CityInputs(
        slug="west-asia/Iraq/Samawah",
        country_iso="IQ",
        city_name="As-Samawah",
        center_lat=31.308,
        center_lon=45.283,
        bbox=SAMAWAH_BBOX,
        population=220_000,
        climate_preset="hot-desert",
        peak_sun_hours=6.0,
    )
    plan = plan_city(inputs, cache_dir=OSM_CACHE)

    # Criteria:
    # 1. Transfers: every pair of lines shares ≥ 1 station → 100%.
    assert plan.transfer_reachability == pytest.approx(1.0), (
        f"hub-and-spoke should give 100% reachability, got "
        f"{plan.transfer_reachability:.1%}"
    )
    # 2. Coverage: ≥ 55% of anchor-weighted demand within walking
    # distance of a station. The corridor-first algorithm trades raw
    # coverage for straight-line routes (stations OFF corridor get
    # dropped rather than dragged as detours) — the previous 70%
    # target assumed the older greedy-station + PCA-line pipeline
    # that produced zigzags.
    assert plan.coverage >= 0.55, (
        f"coverage must be ≥ 55%, got {plan.coverage:.1%}"
    )
    # 3. Curvature proxy: station-to-station segments. With the
    # linear-logic planner each station sits on a real arterial
    # polyline (which has bends), so the straight-line curvature
    # between stations is an upper bound — it reflects road bends,
    # not zigzag detours. Keep the bar loose (≤ 15 rad) as a
    # regression guard for the residential-grid zigzag case rather
    # than a fine-grained quality metric.
    max_curv = max(plan.curvatures.values(), default=0.0)
    assert max_curv < 15.0, (
        f"max per-line curvature {max_curv:.2f} rad exceeds 15 — "
        f"suggests the line is zigzagging through residential streets "
        f"rather than following arterials"
    )

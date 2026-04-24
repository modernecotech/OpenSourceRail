"""Station placement — greedy max-coverage on demand density.

Algorithm:

1. Seed stations at every "must-have" POI: railway station, major
   airport, every university + hospital. These are hard demand
   anchors a network cannot miss.
2. Compute uncovered demand on a 100 m-ish grid: sum of anchor
   weights within `walk_radius_m` of each grid cell, minus demand
   already served by a seeded station.
3. Greedy loop: pick the grid cell with the highest uncovered
   demand, add a station there, repeat. Enforce a minimum
   inter-station spacing (typically 600 m in dense core, 1000 m
   elsewhere — we use a single value simplified).
4. Snap each station to the nearest OSM arterial intersection so
   track can actually be laid. Fall back to the demand-weighted
   centroid of nearby anchors if no road graph is supplied.

Target station count is sized from population: one station per
~10 000–12 000 residents in the service area (about right for a
light-metro density of 0.6–1 km platform spacing in the core).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .anchors import Anchor, haversine_m


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class StationCandidate:
    """A proposed station location with its name + demand score."""

    id: str
    name: str
    lat: float
    lon: float
    archetype: str
    score: float
    """IDs of the anchors this station covers (walked-to)."""
    serves: tuple[str, ...]


# --------------------------------------------------------------------------
# Placement
# --------------------------------------------------------------------------


def target_station_count(population: int) -> int:
    """One station per ~10 000 people, clamped to [8, 40].

    Below 80 k: 8 stations (tram-scale). Above 400 k: 40 stations
    (metro-scale). Matches Amiens + Tours + Orléans class at the
    lower end, and Marseille + Lyon at the upper end."""
    n = max(8, min(40, round(population / 10_000)))
    return int(n)


def place_stations(
    anchors: list[Anchor],
    population: int,
    *,
    walk_radius_m: float = 800.0,
    min_spacing_m: float = 600.0,
    max_spacing_m: float = 1_400.0,
    snap_to_roads: "callable | None" = None,
) -> list[StationCandidate]:
    """Return a list of station candidates optimised for coverage.

    Algorithm: sort anchors by weight (descending), walk the list,
    accept as station if no existing station is within
    `min_spacing_m`. Stop at target count. The weight ranking means
    the railway station + universities + hospitals still come first
    (they have the highest weights), but OSM-mis-tagged "hospitals"
    (pharmacies / clinics) with the same weight as other hospitals
    no longer flood the seed pool because station count caps out.

    `snap_to_roads`, if given, is a callable `(lat, lon) -> (lat, lon)`
    that snaps the candidate to the nearest arterial intersection.
    """
    if not anchors:
        return []

    target_n = target_station_count(population)
    stations: list[StationCandidate] = []
    ranked = sorted(anchors, key=lambda a: -a.weight)

    # Track seen-name slugs so we don't place two stations at the same
    # OSM feature (sometimes OSM has duplicates).
    seen_slugs: set[str] = set()

    for a in ranked:
        if len(stations) >= target_n:
            break
        sid = _slug(a.name)
        if sid in seen_slugs:
            continue
        # Spacing guard: reject if too close to an existing station.
        if any(
            haversine_m((a.lat, a.lon), (s.lat, s.lon)) < min_spacing_m
            for s in stations
        ):
            continue
        seen_slugs.add(sid)
        stations.append(
            StationCandidate(
                id=sid,
                name=a.name,
                lat=a.lat,
                lon=a.lon,
                archetype=_archetype_for_seed(a.kind),
                score=a.weight,
                serves=(sid,),
            )
        )

    # Optional road-snap.
    if snap_to_roads is not None:
        snapped: list[StationCandidate] = []
        for s in stations:
            la, lo = snap_to_roads(s.lat, s.lon)
            snapped.append(
                StationCandidate(
                    id=s.id, name=s.name, lat=la, lon=lo,
                    archetype=s.archetype, score=s.score, serves=s.serves,
                )
            )
        stations = snapped

    return stations


def _archetype_for_seed(kind: str) -> str:
    if kind == "railway-station":
        return "terminal"  # intercity interchange
    if kind in ("university", "airport"):
        return "major"
    if kind == "hospital":
        return "major"
    return "standard"


def _mark_covered(
    station: StationCandidate,
    anchors: list[Anchor],
    covered: set[str],
    walk_radius_m: float,
) -> None:
    for a in anchors:
        if haversine_m((station.lat, station.lon), (a.lat, a.lon)) <= walk_radius_m:
            covered.add(_slug(a.name))


# --------------------------------------------------------------------------
# ID slugging
# --------------------------------------------------------------------------


def _slug(name: str) -> str:
    """Transliterate + lower + dash-join. No external dep — fall
    back to a hash if the name is entirely non-ASCII."""
    import unicodedata

    ascii_ = (
        unicodedata.normalize("NFKD", name)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    ascii_ = ascii_.strip().lower()
    keep = [c if c.isalnum() else "-" for c in ascii_]
    slug = "".join(keep).strip("-")
    # Collapse repeated dashes.
    while "--" in slug:
        slug = slug.replace("--", "-")
    if not slug:
        # Fallback to a short hash of the name.
        import hashlib
        slug = "sta-" + hashlib.sha256(name.encode()).hexdigest()[:6]
    # Cap length for TOML-friendly IDs.
    return slug[:48]


# --------------------------------------------------------------------------
# Coverage scoring
# --------------------------------------------------------------------------


def coverage_score(
    stations: list[StationCandidate],
    anchors: list[Anchor],
    walk_radius_m: float = 800.0,
) -> float:
    """Fraction of total anchor weight served by at least one station
    (within walking distance). Higher is better, 1.0 is perfect."""
    total = sum(a.weight for a in anchors)
    if total <= 0:
        return 0.0
    covered = 0.0
    for a in anchors:
        if any(
            haversine_m((a.lat, a.lon), (s.lat, s.lon)) <= walk_radius_m
            for s in stations
        ):
            covered += a.weight
    return covered / total


# --------------------------------------------------------------------------
# Road-snap helper
# --------------------------------------------------------------------------


def make_road_snapper(road_graph, nodes: dict):
    """Build a callable `(lat, lon) → (lat, lon)` that returns the
    nearest road-graph node's coords. Used by `place_stations`."""
    # Brute-force is fine for 10-station counts; upgrade to KDTree
    # for cities > 100 stations.
    keys = list(road_graph.nodes)

    def snap(lat: float, lon: float) -> tuple[float, float]:
        best = None
        bd = float("inf")
        for n in keys:
            p = nodes[n]
            d = (p[0] - lat) ** 2 + (p[1] - lon) ** 2
            if d < bd:
                bd, best = d, n
        return nodes[best] if best is not None else (lat, lon)

    return snap

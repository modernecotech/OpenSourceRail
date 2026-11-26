"""Compare bounded metropolitan network alternatives on a common planning basis."""

from collections.abc import Mapping
from math import isfinite
from pathlib import Path

from engineering.station_rail.common import digest

METHOD = "metropolitan-network/1"
PRODUCER = "engineering/outline/metro_network.py"
SOURCE_SHA256 = {PRODUCER: digest(Path(__file__))}
SCOPE_KEYS = ("walking", "service", "cost")


def pattern_options(*, pedestrian_network, population_grids, mapped_destinations):
    """Return applicable pattern families for a city adapter to generate."""
    missing = []
    if not pedestrian_network:
        missing.append("Walkable street network")
    if not population_grids:
        missing.append("Population grid")
    if not mapped_destinations:
        missing.append("Mapped destinations")
    if missing:
        return {
            "method": METHOD,
            "status": "retained-corridor-only",
            "families": ["retained-corridor"],
            "missing": missing,
        }
    return {
        "method": METHOD,
        "status": "bounded-metropolitan-search",
        "families": ["network-from-empty", "retained-corridor", "shared-cross-city-trunks",
                     "linked-orbitals", "suburban-extensions", "urban-gap-connector"],
        "missing": [],
    }


def _valid_number(value, low=0, high=None):
    return (type(value) in (int, float) and isfinite(value) and value >= low
            and (high is None or value <= high))


def _scope_key(scope):
    values = tuple(scope.get(name) for name in SCOPE_KEYS) if isinstance(scope, Mapping) else ()
    return values if values and all(isinstance(value, str) and value.strip() for value in values) else None


def _pareto(ids, criteria):
    """Keep alternatives with no equal-or-better rival in every criterion."""
    result = []
    for candidate in ids:
        score = criteria[candidate]
        if not any(
                all(a <= b for a, b in zip(criteria[other], score, strict=True))
                and criteria[other] != score for other in ids):
            result.append(candidate)
    return result


def compare(cases, *, required_destinations, population_grids, walk_limit_m=1300,
            minimum_access_pct=None, reference_id=None):
    """Compare priced cases and keep diagnostic ranking separate from eligibility.

    Each case supplies walking distances by destination, modeled access shares by
    grid, installed and whole-life cost, route and station counts, and explicit
    engineering holds. Scope identifiers name the walking inputs, service offer
    and price/cash basis. The caller verifies those source bindings.
    """
    destination_ids = tuple(sorted(set(required_destinations)))
    grids = tuple(sorted(set(population_grids)))
    if not _valid_number(walk_limit_m) or not walk_limit_m:
        raise ValueError("A positive finite walking distance limit is required")
    minimum = {} if minimum_access_pct is None else minimum_access_pct
    if set(minimum) - set(grids) or any(not _valid_number(value, high=100) for value in minimum.values()):
        raise ValueError("Minimum access percentages must use the declared population grids")
    if reference_id is not None and reference_id not in cases:
        raise ValueError("The declared scope reference is absent")

    scopes = {key: _scope_key(row.get("scope")) for key, row in cases.items()}
    unique_scopes = {scope for scope in scopes.values() if scope is not None}
    expected = scopes[reference_id] if reference_id is not None else (
        next(iter(unique_scopes)) if len(unique_scopes) == 1 else None
    )
    assessments, criteria = {}, {}
    for key, row in sorted(cases.items()):
        walk = row.get("destination_walk_m")
        access = row.get("population_access_pct")
        walk = walk if isinstance(walk, Mapping) else {}
        access = access if isinstance(access, Mapping) else {}
        covered = [site for site in destination_ids if _valid_number(walk.get(site), high=walk_limit_m)]
        unserved = sorted(set(destination_ids) - set(covered))
        evidence_holds = []
        if not destination_ids:
            evidence_holds.append("Mapped destination requirements are needed for metropolitan comparison")
        if not grids or not all(_valid_number(access.get(grid), high=100) for grid in grids):
            evidence_holds.append("Comparable population access on all declared grids is required")
        if expected is None or scopes[key] != expected:
            evidence_holds.append("Common walking, service and cost scope is required")
        for metric in ("installed_cost", "whole_life_cost"):
            if not _valid_number(row.get(metric), low=1e-12):
                evidence_holds.append(f"Missing or invalid {metric.replace('_', ' ')}")
        for metric in ("route_count", "station_count"):
            if type(row.get(metric)) is not int or row[metric] <= 0:
                evidence_holds.append(f"Missing or invalid {metric.replace('_', ' ')}")
        reported = row.get("holds")
        if not isinstance(reported, (tuple, list)) or any(not isinstance(message, str) for message in reported):
            evidence_holds.append("Explicit engineering screen results are required")
            reported = []
        unmet = [f"{grid} population access is below the planning floor"
                 for grid, threshold in sorted(minimum.items())
                 if _valid_number(access.get(grid), high=100) and access[grid] < threshold]
        requirements = ["Required destinations outside the walking threshold"] if unserved else []
        assessments[key] = {
            "covered_destinations": covered,
            "destinations_without_walk_access": unserved,
            "comparable": not evidence_holds,
            "holds": [*evidence_holds, *requirements, *unmet, *reported],
        }
        if not evidence_holds:
            criteria[key] = (*(int(site in unserved) for site in destination_ids),
                             *(-access[grid] for grid in grids), row["installed_cost"],
                             row["whole_life_cost"], row["route_count"], row["station_count"])

    comparable = list(criteria)
    eligible = [key for key in comparable if not assessments[key]["holds"] and key != reference_id]

    def research_rank(key):
        row = cases[key]
        percentages = [row["population_access_pct"][grid] for grid in grids]
        return (-len(assessments[key]["covered_destinations"]), -min(percentages), -sum(percentages),
                row["whole_life_cost"], row["installed_cost"], row["route_count"], row["station_count"], key)

    def cost_rank(key):
        row = cases[key]
        return (row["whole_life_cost"], row["installed_cost"], row["route_count"], row["station_count"],
                research_rank(key))

    return {
        "method": METHOD,
        "scope": dict(zip(SCOPE_KEYS, expected, strict=True)) if expected else None,
        "walk_limit_m": walk_limit_m,
        "required_destinations": list(destination_ids),
        "population_grids": list(grids),
        "assessments": assessments,
        "research_pareto": _pareto(comparable, criteria),
        "eligible_pareto": _pareto(eligible, criteria),
        "reference_id": reference_id,
        "research_lead": min((key for key in comparable if key != reference_id), key=research_rank, default=None),
        "eligible_economic_lead": min(eligible, key=cost_rank, default=None),
        "eligible_coverage_lead": min(eligible, key=research_rank, default=None),
    }

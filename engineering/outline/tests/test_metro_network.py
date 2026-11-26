"""Hold incomparable networks and retain meaningful coverage and cost trade-offs."""

from engineering.outline import metro_network


SCOPE = {
    "walking": "2026-walk-graph-and-population-tiles",
    "service": "matched-six-minute-offer",
    "cost": "matched-2026-usd-30-year-scope",
}


def case(coverage, cost, *, walks=None, holds=(), scope=SCOPE, stations=20):
    return {
        "destination_walk_m": {"edge": 1000, "town": 500} if walks is None else walks,
        "population_access_pct": {"world": coverage, "regional": coverage},
        "installed_cost": cost,
        "whole_life_cost": 2 * cost,
        "station_count": stations,
        "route_count": 5,
        "scope": scope,
        "holds": list(holds),
    }


def test_economic_choice_respects_named_destinations_and_population_floor():
    result = metro_network.compare({
        "reference": case(70, 500),
        "too-cheap": case(95, 50, walks={"edge": None, "town": 500}),
        "too-narrow": case(58, 75),
        "economic": case(72, 100),
        "coverage": case(81, 200, stations=23),
        "redundant": case(69, 110, stations=21),
    }, required_destinations=("edge", "town"), population_grids=("world", "regional"),
        minimum_access_pct={"world": 65, "regional": 65}, reference_id="reference")

    assert result["eligible_economic_lead"] == "economic"
    assert result["eligible_coverage_lead"] == result["research_lead"] == "coverage"
    assert result["eligible_pareto"] == ["coverage", "economic"]
    assert result["assessments"]["too-cheap"]["destinations_without_walk_access"] == ["edge"]
    assert result["assessments"]["too-narrow"]["holds"]


def test_service_cost_and_walking_scope_must_match_before_ranking():
    different = {**SCOPE, "cost": "bridges-excluded"}
    result = metro_network.compare({
        "reference": case(71, 300),
        "promising-but-held": case(90, 400, holds=("Flood crossing unresolved",)),
        "scope-mismatch": case(95, 5, scope=different),
        "no-street-evidence": case(92, 20, scope={**SCOPE, "walking": None}),
    }, required_destinations=("edge", "town"), population_grids=("world", "regional"),
        reference_id="reference")

    assert result["eligible_economic_lead"] is None
    assert result["research_lead"] == "promising-but-held"
    assert not result["assessments"]["scope-mismatch"]["comparable"]
    assert not result["assessments"]["no-street-evidence"]["comparable"]


def test_no_declared_graph_defers_greenfield_design():
    context = metro_network.pattern_options(pedestrian_network=None, population_grids=("world",),
                                            mapped_destinations=("edge", "town"))
    assert context["families"] == ["retained-corridor"]
    assert "Walkable street network" in context["missing"]
    context = metro_network.pattern_options(pedestrian_network="streets", population_grids=("world",),
                                            mapped_destinations=("edge", "town"))
    assert "network-from-empty" in context["families"]
    assert "urban-gap-connector" in context["families"]

from copy import deepcopy
from math import fsum

import pytest

from engineering.design_search import design_grammar as g, dfma, grammar_geometry
from engineering.design_search import grammar_structure, interface_graph, topology_mutation as t
from engineering.station_rail.common import identity


@pytest.fixture(scope="module")
def parent():
    return g.build(g.parameters())


def apply(parent, operator, **kwargs):
    return t.mutate(parent, operator, requirement_revision=parent["requirement_revision"], **kwargs)


@pytest.mark.parametrize("operator", t.OPERATORS)
def test_connectivity_changes_create_real_stock_and_same_candidate_projections(parent, operator):
    result = apply(parent, operator)
    g.validate(result)
    assert result["candidate_id"] != parent["candidate_id"]
    assert result["parent_candidate_ids"] == [parent["candidate_id"]]
    assert result["requirement_revision"] == parent["requirement_revision"]
    stations = len([n for n in parent["physical"]["nodes"] if n["id"].endswith("-0-0")])
    nodes = stations if operator == t.OPERATORS[0] else stations-1
    members = 5*stations-1 if operator == t.OPERATORS[0] else 8*(stations-1)
    assert len(result["physical"]["nodes"]) == len(parent["physical"]["nodes"])+nodes
    assert len(result["physical"]["members"]) == len(parent["physical"]["members"])+members
    assert len(result["parts"]) == len(parent["parts"])+members
    assert len(result["connections"]) == 2*len(result["physical"]["members"])
    assert result["structure"]["candidate_id"] == result["candidate_id"]
    assert result["structure"]["nodes"] == result["physical"]["nodes"]
    assert result["structure"]["members"] == result["physical"]["members"]
    # Validate the method input without invoking a linear solver or FEA process.
    grammar_structure._validated(result["structure"])
    graph = grammar_geometry.interface_projection(result)
    assert interface_graph.validate_identity(graph)["candidate_id"] == result["candidate_id"]
    assert grammar_geometry.mass_properties(result)["candidate_id"] == result["candidate_id"]
    route = dfma.evaluate(result)
    assert route["candidate_id"] == result["candidate_id"]


@pytest.mark.parametrize("operator", t.OPERATORS)
def test_mass_bom_interfaces_operations_and_loading_count_added_stock_once(parent, operator):
    result = apply(parent, operator)
    old_ids = {p["id"] for p in parent["parts"]}
    added = [p for p in result["parts"] if p["id"] not in old_ids]
    delta = fsum(p["mass_kg"] for p in added)
    assert delta > 0
    assert result["known_structure_stock_kg"] == pytest.approx(parent["known_structure_stock_kg"]+delta)
    assert result["topology_mutations"][-1]["added_gross_stock_mass_kg"] == pytest.approx(delta)
    assert result["structure"]["load_basis"]["sprung_mass_hypothesis_kg"] == pytest.approx(
        parent["structure"]["load_basis"]["sprung_mass_hypothesis_kg"]+delta)
    total_force = -fsum(row["force_N"][2] for row in result["structure"]["loads"])
    assert total_force == pytest.approx(result["structure"]["load_basis"]["sprung_mass_hypothesis_kg"]*9.80665)
    coordinates = {n["id"]: n["at_m"] for n in result["physical"]["nodes"]}
    parts = {p["id"]: p for p in result["parts"]}
    components = {p["occurrence_id"]: p for p in result["components"]}
    for m in result["physical"]["members"]:
        assert parts[m["part_id"]]["start_m"] == coordinates[m["start_node"]]
        assert parts[m["part_id"]]["end_m"] == coordinates[m["end_node"]]
        assert len(components[m["part_id"]]["ports"]) == 2
    for joint in result["joins"]:
        assert components[joint["id"]]["component_definition_id"] == identity(joint)
        assert joint["net_hardware_mass_kg"] is None
    assembly = {o["id"]: o for o in result["assembly"]}
    op = "topology/"+operator+"/join-and-inspect"
    assert op in assembly["chassis"]["requires"]
    assert assembly[op]["requires"] == ["cut"] and assembly[op]["hours"] is None
    assert all(p["id"] in assembly["cut"]["occurrences"] for p in added)


@pytest.mark.parametrize("operator", t.OPERATORS)
def test_accommodation_bogies_and_inherited_equipment_do_not_change(parent, operator):
    before = deepcopy(parent)
    result = apply(parent, operator)
    assert parent == before
    for key in ("architecture", "envelope", "apertures", "retained_equipment", "required_functions"):
        assert result["physical"][key] == parent["physical"][key]
    for key in ("parameters", "materials", "retained_equipment_accounts", "retained_reference_candidate_id"):
        assert result[key] == parent[key]
    assert result["structure"]["supports"] == parent["structure"]["supports"]
    retained_ids = {row["id"] for row in parent["retained_equipment_accounts"]}
    a = {row["occurrence_id"]: row for row in parent["components"] if row["occurrence_id"] in retained_ids}
    b = {row["occurrence_id"]: row for row in result["components"] if row["occurrence_id"] in retained_ids}
    assert a == b
    assert result["complete_installed_mass_kg"] is None
    assert result["complete_cost_USD"] is None
    assert result["full_body_evaluator"] == "unavailable-for-new-topology"
    assert all(result[flag] is False for flag in g.FLAGS)
    assert result["topology_unresolved_domains"]


@pytest.mark.parametrize("operator", t.OPERATORS)
def test_repeated_application_is_duplicate_safe_and_reason_is_not_physical_identity(parent, operator):
    first = apply(parent, operator, reason="first research hypothesis")
    assert apply(first, operator) == first
    other = apply(parent, operator, reason="another explanation of the same geometry")
    assert first["candidate_id"] == other["candidate_id"]
    assert first["definition_id"] != other["definition_id"]


def test_two_additive_operators_have_commutative_physical_identity(parent):
    a = apply(apply(parent, t.OPERATORS[0]), t.OPERATORS[1])
    b = apply(apply(parent, t.OPERATORS[1]), t.OPERATORS[0])
    assert a["physical"] == b["physical"]
    assert a["candidate_id"] == b["candidate_id"]
    assert a["definition_id"] != b["definition_id"]  # distinct ordered ancestry
    assert a["known_structure_stock_kg"] == b["known_structure_stock_kg"]


def test_unsupported_or_different_requirements_are_explicitly_rejected(parent):
    with pytest.raises(ValueError, match="Unsupported topology"):
        apply(parent, "invent-an-unimplemented-shell")
    with pytest.raises(ValueError, match="requirement revision"):
        t.mutate(parent, t.OPERATORS[0], requirement_revision="different")


def test_existing_braced_parent_still_gets_new_connectivity_without_coincident_graph_edges():
    params = g.parameters(); params["braced"] = True
    parent = g.build(params)
    for operator in t.OPERATORS:
        result = apply(parent, operator)
        assert len(result["physical"]["members"]) > len(parent["physical"]["members"])
        grammar_structure._validated(result["structure"])


def test_resealed_inconsistent_member_stock_or_release_cannot_be_inherited(parent):
    bad = deepcopy(parent)
    bad["physical_accepted"] = True
    bad.pop("definition_id"); bad["definition_id"] = identity(bad)
    with pytest.raises(ValueError, match="physical release"):
        apply(bad, t.OPERATORS[0])
    bad = deepcopy(parent)
    member = bad["physical"]["members"][0]
    member["start_node"] = bad["physical"]["nodes"][-1]["id"]
    bad["structure"]["members"] = deepcopy(bad["physical"]["members"])
    bad["candidate_id"] = identity(bad["physical"])
    bad["structure"]["candidate_id"] = bad["candidate_id"]
    bad.pop("definition_id"); bad["definition_id"] = identity(bad)
    with pytest.raises(ValueError, match="endpoint coordinates"):
        apply(bad, t.OPERATORS[0])

"""Removal revisions must propagate every physical and accounting projection."""
from copy import deepcopy
from math import fsum

import pytest

from engineering.design_search import design_grammar as g, dfma, grammar_geometry, grammar_structure
from engineering.design_search import interface_graph, model_cost, design_portfolio
from engineering.design_search import topology_mutation, topology_revision as t
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity


@pytest.fixture(scope="module")
def parent():
    return g.build(dict(g.parameters(), braced=True))


@pytest.fixture(scope="module")
def revised(parent):
    return t.mutate(parent, requirement_revision=parent["requirement_revision"])


def reseal(value):
    value["candidate_id"] = identity(value["physical"])
    value["structure"]["candidate_id"] = value["candidate_id"]
    value["definition_id"] = identity({k:v for k,v in value.items() if k != "definition_id"})
    return value


def test_odd_interior_crossframes_are_removed_with_end_and_bogie_stations_protected(parent, revised):
    t.validate(revised); g.validate(revised)
    record = revised["topology_mutations"][0]
    removed = {m["id"]: m for m in parent["physical"]["members"] if m["id"] in record["removed_member_ids"]}
    assert removed
    assert all(m["role"] == "crossframe-diagonal" for m in removed.values())
    assert all(i % 2 for i in record["removed_station_indices"])
    assert not set(record["removed_station_indices"]) & set(record["protected_station_indices"])
    assert len(revised["physical"]["members"]) == len(parent["physical"]["members"])-len(removed)
    assert revised["physical"]["nodes"] == parent["physical"]["nodes"]
    assert revised["structure"]["supports"] == parent["structure"]["supports"]
    assert revised["candidate_id"] != parent["candidate_id"]
    assert revised["parent_candidate_ids"] == [parent["candidate_id"]]
    assert record["parent_definition_id"] == parent["definition_id"]


def test_removed_components_ports_connections_and_assembly_occurrences_never_reappear(parent, revised):
    record = revised["topology_mutations"][0]
    retired = set(record["retired_component_occurrence_ids"])
    assert retired == set(record["removed_part_ids"])
    parts = {p["id"] for p in revised["parts"]}
    components = {c["occurrence_id"] for c in revised["components"]}
    assert not retired & components and not retired & parts
    assert len(parent["components"])-len(revised["components"]) == len(retired)
    for connection in revised["connections"]:
        assert connection["from"][0] in components and connection["to"][0] in components
        assert connection["from"][0] not in retired
    assert len(revised["connections"]) == 2*len(revised["physical"]["members"])
    assert all(not retired & set(op["occurrences"]) for op in revised["assembly"])
    for joint in revised["joins"]:
        assert set(joint["part_ids"]) <= parts
        assert joint["net_hardware_mass_kg"] is None
    graph = grammar_geometry.interface_projection(revised)
    assert interface_graph.validate_identity(graph)["candidate_id"] == revised["candidate_id"]
    assert dfma.evaluate(revised)["candidate_id"] == revised["candidate_id"]


def test_removed_stock_and_uniform_own_mass_load_are_counted_exactly_once(parent, revised):
    record = revised["topology_mutations"][0]
    removed = fsum(p["mass_kg"] for p in parent["parts"] if p["id"] in record["removed_part_ids"])
    known = fsum(p["mass_kg"] for p in revised["parts"])
    assert known < parent["known_structure_stock_kg"]
    assert record["removed_gross_stock_mass_kg"] == removed
    assert record["signed_gross_stock_mass_delta_kg"] == pytest.approx(-removed, abs=1e-8)
    assert revised["known_structure_stock_kg"] == known
    assert revised["retained_equipment_accounts"] == parent["retained_equipment_accounts"]
    basis = revised["structure"]["load_basis"]
    expected = known+fsum(r["mass_kg"] for r in parent["retained_equipment_accounts"] if r["system"] != "bogies")+46*75.
    assert basis["sprung_mass_hypothesis_kg"] == expected
    assert -fsum(load["force_N"][2] for load in revised["structure"]["loads"]) == pytest.approx(expected*9.80665, rel=1e-12)
    assert grammar_geometry.mass_properties(revised)["known_gross_stock_mass_kg"] == pytest.approx(known)
    grammar_structure._validated(revised["structure"])
    assumptions=model_cost.assumptions()
    before=design_portfolio._factory_gate_stock_estimate(parent,assumptions,ROOT)
    after=design_portfolio._factory_gate_stock_estimate(revised,assumptions,ROOT)
    assert after["candidate_id"] == revised["candidate_id"]
    assert after["scenarios_iqd"]["base"] < before["scenarios_iqd"]["base"]


def test_inherited_architecture_material_and_passenger_interfaces_and_unknowns_remain_explicit(parent, revised):
    for field in ("architecture", "envelope", "apertures", "required_functions", "retained_equipment"):
        assert revised["physical"][field] == parent["physical"][field]
    assert revised["materials"] == parent["materials"]
    assert revised["complete_installed_mass_kg"] is None
    assert revised["complete_cost_USD"] is None
    assert revised["topology_mutations"][0]["unknown_joint_hardware_mass_kg"] is None
    assert all(revised[k] is False for k in g.FLAGS)


def test_deterministic_idempotence_is_recognized_without_removing_more_members(parent, revised):
    assert t.mutate(parent,requirement_revision=parent["requirement_revision"]) == revised
    duplicate=t.mutate(revised,requirement_revision=revised["requirement_revision"])
    assert duplicate == revised
    duplicate["parts"].clear()
    assert revised["parts"]


def test_unbraced_and_unsupported_parent_chains_are_explicit_model_holds(parent, revised):
    unbraced=g.build(g.parameters())
    with pytest.raises(ValueError,match="explicitly braced"):
        t.mutate(unbraced,requirement_revision=unbraced["requirement_revision"])
    additive=topology_mutation.mutate(parent,topology_mutation.OPERATORS[0],requirement_revision=parent["requirement_revision"])
    with pytest.raises(ValueError,match="standalone removal ancestry"):
        t.mutate(additive,requirement_revision=additive["requirement_revision"])
    with pytest.raises(ValueError,match="different producer source epoch"):
        topology_mutation.mutate(revised,topology_mutation.OPERATORS[0],requirement_revision=revised["requirement_revision"])


@pytest.mark.parametrize("kind", ["retired-component", "joint-parts", "load", "history", "assembly"])
def test_consistently_resealed_bad_projection_is_rejected(parent, revised, kind):
    value=deepcopy(revised)
    if kind == "retired-component":
        retired=value["topology_mutations"][0]["retired_component_occurrence_ids"][0]
        value["components"].append(deepcopy(next(c for c in parent["components"] if c["occurrence_id"] == retired)))
    elif kind == "joint-parts":
        value["joins"][0]["part_ids"].append(value["topology_mutations"][0]["removed_part_ids"][0])
        value["physical"]["joins"]=deepcopy(value["joins"])
    elif kind == "load":value["structure"]["loads"][0]["force_N"][2] *= 2
    elif kind == "history":value["topology_mutations"][0]["signed_gross_stock_mass_delta_kg"]=0.
    else:value["assembly"][0]["occurrences"].append(value["topology_mutations"][0]["removed_part_ids"][0])
    reseal(value)
    with pytest.raises(ValueError):t.validate(value)

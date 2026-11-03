"""Exact parity with the unchanged independent axial graph implementation."""
from copy import deepcopy

import numpy as np
import pytest

from engineering.design_search import axial_analysis as a, design_grammar as g
from engineering.design_search import grammar_structure as oracle, topology_mutation
from engineering.station_rail.common import identity


@pytest.fixture(scope="module")
def graphs():
    benchmark = oracle.benchmark_plan()
    values = {row["id"]: row["graph"] for row in benchmark["native_jobs"]}
    for row in benchmark["necessary_controls"]:
        values[row["id"]] = row["graph"]
    for braced in (False, True):
        candidate = g.build(dict(g.parameters(), braced=braced))
        values["body-braced" if braced else "body-unbraced"] = candidate["structure"]
    parent = g.build(g.parameters())
    for operator in topology_mutation.OPERATORS:
        values[operator] = topology_mutation.mutate(parent, operator,
            requirement_revision=parent["requirement_revision"])["structure"]
    return values


def test_every_control_and_generated_topology_matches_oracle_exactly(graphs):
    for graph in graphs.values():
        prepared = a.prepare(graph)
        expected = oracle.diagnose_rigidity(graph)
        assert prepared.diagnose() == expected
        assert prepared.stock == oracle._validated(graph)[3]
        assert all(prepared.diagnose()[k] is False for k in oracle.FLAGS)
        if expected["mechanism_count"]:
            with pytest.raises(ValueError, match="Necessary rigidity failure"):
                prepared.linear_reference()
        else:
            assert prepared.linear_reference() == oracle.linear_reference(graph)


def test_one_assembly_and_one_diagnostic_svd_per_preparation(graphs, monkeypatch):
    graph = graphs["body-braced"]
    expected_diagnostic = oracle.diagnose_rigidity(graph)
    expected_reference = oracle.linear_reference(graph)
    original_system, original_svd = oracle._system, np.linalg.svd
    calls = dict(system=0, svd=0)
    def system(value):
        calls["system"] += 1
        return original_system(value)
    def svd(*args, **kwargs):
        assert kwargs == dict(full_matrices=True)
        calls["svd"] += 1
        return original_svd(*args, **kwargs)
    monkeypatch.setattr(oracle, "_system", system)
    monkeypatch.setattr(np.linalg, "svd", svd)
    prepared = a.prepare(graph)
    assert prepared.diagnose() == prepared.diagnose() == expected_diagnostic
    assert prepared.linear_reference() == prepared.linear_reference() == expected_reference
    assert prepared.stock and calls == dict(system=1, svd=1)


def test_input_diagnostic_stock_and_reference_mutations_do_not_escape(graphs):
    graph = deepcopy(graphs["body-braced"])
    expected_diagnostic = oracle.diagnose_rigidity(graph)
    expected_reference = oracle.linear_reference(graph)
    prepared = a.prepare(graph)
    graph["nodes"][0]["at_m"][0] += 100.0
    graph["loads"][0]["force_N"] = [0.0, 0.0, 0.0]
    stock = prepared.stock
    stock[0]["section"]["wall_m"] = 100.0
    diagnostic = prepared.diagnose()
    diagnostic["singular_values"].clear()
    diagnostic["mechanism_vectors"].append(dict(fake=True))
    diagnostic["physical_accepted"] = True
    reference = prepared.linear_reference()
    next(iter(reference["displacements_m"].values()))[0] = 1000.0
    reference["member_axial_forces_N"].clear()
    assert prepared.diagnose() == expected_diagnostic
    assert prepared.linear_reference() == expected_reference
    assert prepared.stock[0]["section"]["wall_m"] != 100.0


def test_identical_geometry_with_changed_load_has_distinct_input_and_correct_response(graphs):
    original = deepcopy(graphs["body-braced"])
    doubled = deepcopy(original)
    for load in doubled["loads"]:
        load["force_N"] = [2 * v for v in load["force_N"]]
    p, q = a.prepare(original), a.prepare(doubled)
    assert p.diagnose()["physical_graph_id"] == q.diagnose()["physical_graph_id"]
    assert p.diagnose()["input_graph_id"] != q.diagnose()["input_graph_id"]
    assert q.diagnose()["input_graph_id"] == identity(doubled)
    p_reference, q_reference = p.linear_reference(), q.linear_reference()
    assert q_reference == oracle.linear_reference(doubled)
    for key, vector in p_reference["displacements_m"].items():
        assert q_reference["displacements_m"][key] == pytest.approx([2*v for v in vector], rel=1e-12)


def test_unknown_density_is_preserved_without_zero_mass_or_new_qualification(graphs):
    graph = deepcopy(graphs["body-braced"])
    for material in graph["materials"].values():
        material["density_kg_m3"] = None
    prepared = a.prepare(graph)
    assert prepared.diagnose() == oracle.diagnose_rigidity(graph)
    assert prepared.diagnose()["counted_member_stock_mass_kg"] is None
    assert prepared.diagnose()["unknown_density_member_ids"]
    assert prepared.diagnose()["unknown_joint_hardware_mass_kg"] is None
    assert prepared.linear_reference() == oracle.linear_reference(graph)


@pytest.mark.parametrize("kind", ["empty", "duplicate-member", "nonfinite-load", "invalid-wall", "coincident-nodes"])
def test_malformed_graphs_retain_existing_method_rejection(graphs, kind):
    graph = deepcopy(graphs["body-braced"])
    if kind == "empty":
        graph = {}
    elif kind == "duplicate-member":
        member = deepcopy(graph["members"][0])
        member["id"] += "-duplicate"
        graph["members"].append(member)
    elif kind == "nonfinite-load":
        graph["loads"][0]["force_N"][0] = float("nan")
    elif kind == "invalid-wall":
        graph["members"][0]["section"]["wall_m"] = 1.0
    else:
        ends = graph["members"][0]
        coords = {node["id"]:node for node in graph["nodes"]}
        coords[ends["end_node"]]["at_m"] = coords[ends["start_node"]]["at_m"][:]
    with pytest.raises(ValueError):
        oracle.diagnose_rigidity(graph)
    with pytest.raises(ValueError):
        a.prepare(graph)

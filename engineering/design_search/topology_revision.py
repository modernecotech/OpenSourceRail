"""Remove bounded alternate crossframe diagonals from a braced grammar body.

This is a physical stock/connectivity revision, not a retrofit instruction or a
structural acceptance decision. End and bogie-support stations remain protected;
remaining load paths and real connections require their own evaluators.
"""
from __future__ import annotations

from copy import deepcopy
from math import fsum
import re

from engineering.station_rail.common import digest, identity
from . import design_grammar as grammar, interface_graph

PRODUCER = "engineering/design_search/topology_revision.py"
OPERATOR = "remove-alternate-crossframe-bracing"
LOADED = {PRODUCER: digest(__file__), grammar.PRODUCER: digest(grammar.__file__),
          interface_graph.PRODUCER: digest(interface_graph.__file__)}
DEFAULT_REASON = "Remove alternate interior crossframe diagonals while preserving end and bogie-support stations"
OPEN_DOMAINS = [
    "Removed axial members require fresh graph/frame/shell stiffness, stability and load-transfer assessment",
    "Joint hardware, stiffness, fastening, fatigue and net installed mass remain unknown",
    "Nominal reduced stock and process quantities do not establish full vehicle or whole-life savings",
    "Uniform own-candidate sprung-mass load remains a research hypothesis, not detailed installed loading",
]


def _sources():
    actual = {PRODUCER: digest(__file__), grammar.PRODUCER: digest(grammar.__file__),
              interface_graph.PRODUCER: digest(interface_graph.__file__)}
    if actual != LOADED:
        raise ValueError("Topology revision source changed after import")
    return actual


def _canonical(candidate):
    grammar.validate(candidate)
    parameters = candidate["parameters"]
    if parameters["braced"] is not True or parameters["cars"] != 6 or parameters["length_m"] != 17.:
        raise ValueError("Removal model domain requires an explicitly braced six-car 17 m grammar parent")
    expected = grammar.build(parameters, recipes=candidate["recipe_registry"],
        parent_ids=candidate["parent_candidate_ids"], reason=candidate["revision_reason"])
    if candidate != expected:
        raise ValueError("Removal parent differs from its complete canonical grammar projection")
    return candidate


def _station(node_id):
    match = re.fullmatch(r"n-(\d+)-([01])-([01])", node_id)
    if not match:
        raise ValueError("Canonical underfloor station-corner nodes required")
    return int(match.group(1))


def _apply(parent, reason):
    source = _sources()
    nodes = parent["physical"]["nodes"]
    stations = sorted({_station(n["id"]) for n in nodes})
    if stations != list(range(len(stations))):
        raise ValueError("Contiguous original underfloor station indexing required")
    protected = {_station(s["node_id"]) for s in parent["structure"]["supports"]}
    protected.update((stations[0], stations[-1]))
    eligible = {i for i in stations[1:-1] if i % 2 and i not in protected}
    removed = [m for m in parent["physical"]["members"] if m["role"] == "crossframe-diagonal"
               and _station(m["start_node"]) == _station(m["end_node"])
               and _station(m["start_node"]) in eligible]
    if not removed:
        raise ValueError("Removal model domain has no eligible interior crossframe bracing")
    removed_ids = {m["id"] for m in removed}
    removed_parts = {m["part_id"] for m in removed}
    value = deepcopy(parent)
    members = [m for m in value["physical"]["members"] if m["id"] not in removed_ids]
    parts = [p for p in value["parts"] if p["id"] not in removed_parts]
    value["parts"] = parts
    value["physical"]["members"] = members
    joins = deepcopy(value["joins"])
    for joint in joins:
        joint["part_ids"] = [pid for pid in joint["part_ids"] if pid not in removed_parts]
    value["joins"] = joins
    value["physical"]["joins"] = deepcopy(joins)
    geometry = [{k: v for k, v in part.items() if k not in ("mass_kg", "access", "process", "joint_end_detail")}
                for part in parts]
    value["physical"]["geometry"] = geometry
    cid = identity(value["physical"])
    value["candidate_id"] = cid
    value["sources"] = {**value["sources"], **source}
    geometry_by_id = {part["id"]: geom for part, geom in zip(parts, geometry)}
    joins_by_id = {j["id"]: j for j in joins}
    retired = [c for c in value["components"] if c["occurrence_id"] in removed_parts]
    components = [c for c in value["components"] if c["occurrence_id"] not in removed_parts]
    for component in components:
        uid = component["occurrence_id"]
        if uid in geometry_by_id:
            component["component_definition_id"] = identity(geometry_by_id[uid])
        elif uid in joins_by_id:
            component["component_definition_id"] = identity(joins_by_id[uid])
        if "candidate_id" in component:
            component["candidate_id"] = cid
    value["components"] = components
    value["connections"] = [c for c in value["connections"]
                            if c["from"][0] not in removed_parts and c["to"][0] not in removed_parts]
    for operation in value["assembly"]:
        operation["occurrences"] = [uid for uid in operation["occurrences"] if uid not in removed_parts]
    known = fsum(p["mass_kg"] for p in parts)
    value["known_structure_stock_kg"] = known
    basis = value["structure"]["load_basis"]
    load_mass = known + fsum(r["mass_kg"] for r in value["retained_equipment_accounts"] if r["system"] != "bogies") + basis["normal_people"]*75.
    station_nodes = {_station(n["id"]): n["at_m"][0] for n in nodes}
    xs = [station_nodes[i] for i in stations]
    loads = []
    for i, x in enumerate(xs):
        left = -8.5 if i == 0 else (xs[i-1]+x)/2
        right = 8.5 if i == len(xs)-1 else (x+xs[i+1])/2
        for side in (0, 1):
            loads.append(dict(node_id=f"n-{i}-{side}-1", force_N=[0., 0., -load_mass*9.80665*(right-left)/17/2]))
    value["structure"].update(candidate_id=cid, members=deepcopy(members), loads=loads,
        source_sha256={**value["structure"]["source_sha256"], **source})
    basis.update(known_body_stock_kg=known, sprung_mass_hypothesis_kg=load_mass,
        mutation_load_hypothesis="Uniform tributary own-candidate sprung mass over unchanged station corners; complete installed loading unresolved")
    value["topology_mutations"] = [dict(operator=OPERATOR,
        parent_candidate_id=parent["candidate_id"], parent_definition_id=parent["definition_id"],
        parent_parent_candidate_ids=deepcopy(parent["parent_candidate_ids"]),
        parent_revision_reason=parent["revision_reason"], requirement_revision=parent["requirement_revision"],
        producer_sha256=source[PRODUCER], source_sha256=source,
        removed_member_ids=sorted(removed_ids), removed_part_ids=sorted(removed_parts),
        removed_station_indices=sorted({_station(m["start_node"]) for m in removed}),
        protected_station_indices=sorted(protected),
        retired_component_occurrence_ids=sorted(c["occurrence_id"] for c in retired),
        retired_component_definition_ids=sorted(c["component_definition_id"] for c in retired),
        removed_gross_stock_mass_kg=fsum(p["mass_kg"] for p in parent["parts"] if p["id"] in removed_parts),
        signed_gross_stock_mass_delta_kg=known-parent["known_structure_stock_kg"],
        unknown_joint_hardware_mass_kg=None,
        retained_equipment_accounting="Unchanged inherited accounts; retired located stock is not reintroduced as an allowance")]
    value["parent_candidate_ids"] = [parent["candidate_id"]]
    value["revision_reason"] = reason
    value["topology_unresolved_domains"] = OPEN_DOMAINS.copy()
    value["full_body_evaluator"] = "unavailable-for-new-topology"
    value.pop("definition_id")
    value["definition_id"] = identity(value)
    grammar.validate(value)
    interface_graph._check_identity(dict(schema=interface_graph.SCHEMA, candidate_id=cid,
        requirement_revision=value["requirement_revision"], components=components,
        connections=value["connections"], required_functions=value["required_functions"]))
    return value


def validate(candidate):
    """Reconstruct a recognized removal revision, rejecting resealed bad projections."""
    _sources()
    grammar.validate(candidate)
    history = candidate.get("topology_mutations")
    if (not isinstance(history, list) or len(history) != 1 or not isinstance(history[0], dict)
            or history[0].get("operator") != OPERATOR):
        raise ValueError("Only the explicit standalone removal ancestry is supported")
    if not isinstance(candidate.get("revision_reason"), str) or not candidate["revision_reason"].strip():
        raise ValueError("Explicit member-removal revision reason required")
    record = history[0]
    if record.get("producer_sha256") != LOADED[PRODUCER] or candidate["sources"].get(PRODUCER) != LOADED[PRODUCER]:
        raise ValueError("Removal parent belongs to another source epoch")
    parent = grammar.build(candidate["parameters"], recipes=candidate["recipe_registry"],
        parent_ids=record.get("parent_parent_candidate_ids", []), reason=record.get("parent_revision_reason"))
    _canonical(parent)
    if parent["candidate_id"] != record.get("parent_candidate_id") or parent["definition_id"] != record.get("parent_definition_id"):
        raise ValueError("Removal ancestry differs from its complete canonical parent")
    if candidate != _apply(parent, candidate["revision_reason"]):
        raise ValueError("Removal revision physical, interface, assembly or accounting projection differs")
    return candidate


def mutate(candidate, operator=OPERATOR, *, requirement_revision, reason=DEFAULT_REASON):
    _sources()
    if operator != OPERATOR:
        raise ValueError("Unsupported member-removal production")
    if requirement_revision != candidate.get("requirement_revision"):
        raise ValueError("Member-removal requirement revision differs")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("Explicit member-removal revision reason required")
    if candidate.get("topology_mutations"):
        return deepcopy(validate(candidate))
    return _apply(_canonical(candidate), reason)

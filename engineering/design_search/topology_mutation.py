"""Executable underfloor graph productions with counted gross RHS stock.

These two bounded operators change connectivity, not only section dimensions.
They preserve passenger accommodation and inherited equipment. Added stock is
untrimmed: member intersections, joint hardware, installation and clearances need
their own evidence. The pin graph cannot qualify a bonded shell or rigid body.
"""
from copy import deepcopy
from math import fsum, isfinite, sqrt
from pathlib import Path
import re

from engineering.station_rail.common import digest, identity
from . import design_grammar as grammar, interface_graph

PRODUCER = "engineering/design_search/topology_mutation.py"
OPERATORS = ("add-longitudinal-spine", "add-cellular-diaphragms")
LOADED_SOURCE_SHA256 = digest(__file__)
OPEN_DOMAINS = [
    "Gross overlapping cut stock requires net mitres, branch intersection and attachment geometry",
    "Joint hardware mass, transfer, preload/slip, stiffness, fatigue and strength are unknown",
    "Underfloor equipment, suspension, secondary, wiring and maintenance swept clearances remain unverified",
    "Uniform sprung-mass loading is inherited for the axial research graph, not a detailed self-weight or body load model",
    "An axial mechanism diagnoses this pin graph only; shell/frame participation needs its own evaluator",
]


def _anchors(candidate):
    """Resolve the existing typed station-corner anchors; never invent interfaces."""
    stations = {}
    for node in candidate["physical"]["nodes"]:
        match = re.fullmatch(r"n-(\d+)-([01])-([01])", node["id"])
        if match:
            i, side, level = map(int, match.groups())
            stations.setdefault(i, {})[side, level] = node
    if sorted(stations) != list(range(len(stations))) or len(stations) < 2:
        raise ValueError("Existing contiguous underfloor station-corner anchors required")
    for station in stations.values():
        if set(station) != {(j, k) for j in (0, 1) for k in (0, 1)}:
            raise ValueError("Four explicit station-corner anchors required")
        coords = [node["at_m"] for node in station.values()]
        if any(len(p) != 3 or any(type(v) not in (int, float) or not isfinite(v) for v in p) for p in coords):
            raise ValueError("Finite existing station coordinates required")
        if len({p[0] for p in coords}) != 1:
            raise ValueError("A station must have one longitudinal coordinate")
        for j in (0, 1):
            if station[j, 0]["at_m"][1] != station[j, 1]["at_m"][1]:
                raise ValueError("Vertical corner anchors required")
        for k in (0, 1):
            if station[0, k]["at_m"][2] != station[1, k]["at_m"][2]:
                raise ValueError("Level transverse corner anchors required")
    ordered = [stations[i] for i in sorted(stations)]
    xs = [s[0, 0]["at_m"][0] for s in ordered]
    if any(b <= a for a, b in zip(xs, xs[1:])):
        raise ValueError("Ordered distinct station coordinates required")
    return ordered, xs


def _port(uid):
    return dict(id=uid, kind="mechanical", unit="N", frame_id="vehicle",
        direction="bidirectional", connector="pin-node-hypothesis", dofs=["Fx", "Fy", "Fz"],
        data_validity={"validity": "unknown"})


def _projection_checks(value):
    grammar.validate(value)
    if any(value.get(key) is not False for key in grammar.FLAGS) or value.get("complete_installed_mass_kg") is not None:
        raise ValueError("Topology research cannot inherit physical release or installed mass completeness")
    physical = value["physical"]
    if physical["joins"] != value["joins"]:
        raise ValueError("Joint projection differs from physical topology")
    node_ids = {n["id"] for n in physical["nodes"]}
    parts = {p["id"]: p for p in value["parts"]}
    if len(node_ids) != len(physical["nodes"]) or len(parts) != len(value["parts"]):
        raise ValueError("Unique physical node and stock identities required")
    edges = set()
    coordinates = {n["id"]: n["at_m"] for n in physical["nodes"]}
    for member in physical["members"]:
        ends = member["start_node"], member["end_node"]
        if any(n not in node_ids for n in ends) or ends[0] == ends[1] or member["part_id"] not in parts:
            raise ValueError("Physical member endpoints or stock identity differ")
        edge = tuple(sorted(ends))
        if edge in edges:
            raise ValueError("Duplicate graph edge requires explicit physical resolution")
        edges.add(edge)
        part = parts[member["part_id"]]
        if part.get("kind") != "oriented-RHS" or part.get("start_m") != coordinates[ends[0]] or part.get("end_m") != coordinates[ends[1]]:
            raise ValueError("Member endpoint coordinates differ from actual stock geometry")
        if any(member["section"][key] != part[key] for key in ("width_m", "height_m", "wall_m", "material_id")):
            raise ValueError("Member section differs from its physical stock")
    if abs(fsum(p["mass_kg"] for p in value["parts"]) - value["known_structure_stock_kg"]) > 1e-8:
        raise ValueError("Known stock mass differs from the complete gross part projection")
    interface_graph._check_identity(dict(schema=interface_graph.SCHEMA,
        candidate_id=value["candidate_id"], requirement_revision=value["requirement_revision"],
        components=value["components"], connections=value["connections"],
        required_functions=value["required_functions"]))
    return value


def mutate(candidate, operator, *, requirement_revision, reason="Connectivity-changing underfloor research production"):
    """Return a fully projected new grammar candidate, or the same duplicate."""
    if operator not in OPERATORS:
        raise ValueError("Unsupported topology operator; register an executable physical production")
    if digest(__file__) != LOADED_SOURCE_SHA256:
        raise ValueError("Topology producer changed after import")
    _projection_checks(candidate)
    if requirement_revision != candidate["requirement_revision"]:
        raise ValueError("Topology mutation requirement revision differs from its parent")
    p = candidate["parameters"]
    if p["length_m"] != 17.0 or p["cars"] != 6 or candidate["physical"]["architecture"] != dict(
            cars=6, car_length_m=17.0, width_m=p["width_m"]):
        raise ValueError("This topology adapter is bounded to the six-car 17 m accommodation context")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("Explicit topology revision reason required")
    history = candidate.get("topology_mutations", [])
    if history and candidate["sources"].get(PRODUCER) != LOADED_SOURCE_SHA256:
        raise ValueError("Topology parent belongs to a different producer source epoch")
    prefix = "chassis/topology/" + operator + "/"
    if any(row["operator"] == operator for row in history):
        if not any(part["id"].startswith(prefix) for part in candidate["parts"]):
            raise ValueError("Mutation ancestry has no corresponding physical stock")
        return deepcopy(candidate)
    if any(part["id"].startswith(prefix) for part in candidate["parts"]):
        raise ValueError("Unbound topology stock cannot borrow mutation ancestry")
    stations, xs = _anchors(candidate)
    value = deepcopy(candidate)
    nodes, members, parts = value["physical"]["nodes"], value["physical"]["members"], value["parts"]
    lookup = {n["id"]: n["at_m"] for n in nodes}
    frame_material = value["recipe_registry"][p["family"]]["frame"]
    material = value["materials"][frame_material]
    width, height, wall = p["chord_width_m"], p["chord_height_m"], p["chord_wall_m"]
    area = width*height-(width-2*wall)*(height-2*wall)
    if area <= 0 or material["density_kg_m3"] <= 0:
        raise ValueError("Positive explicit RHS stock and material density required")
    added_nodes, added_members = [], []
    def node(label, at):
        uid = prefix + "node/" + str(label)
        if uid in lookup:
            raise ValueError("Topology node identity collision")
        nodes.append(dict(id=uid, at_m=list(at))); lookup[uid] = list(at); added_nodes.append(uid)
        return uid
    def edge(label, start, end, role):
        uid = prefix + "member/" + str(label)
        a, b = lookup[start], lookup[end]
        length = sqrt(fsum((y-x)**2 for x, y in zip(a, b)))
        if length <= 0:
            raise ValueError("Distinct physical member endpoints required")
        volume = area*length
        parts.append(dict(id=uid, kind="oriented-RHS", start_m=a.copy(), end_m=b.copy(),
            width_m=width, height_m=height, wall_m=wall, material_id=frame_material,
            volume_m3=volume, mass_kg=volume*material["density_kg_m3"], functions=["support-loads"],
            load_roles=["primary"], form=material["form"], process="cut-drill-and-join",
            manufacturing_occurrence_id=uid, joint_end_detail="Gross cut stock; branch cuts, mitres and joint hardware unresolved",
            removable=False, access="not-designed"))
        members.append(dict(id=uid, start_node=start, end_node=end,
            section=dict(width_m=width, height_m=height, wall_m=wall, area_m2=area, material_id=frame_material),
            role=role, part_id=uid)); added_members.append(uid)
    centres = []
    if operator == "add-longitudinal-spine":
        for i, station in enumerate(stations):
            a, b = station[0, 0]["at_m"], station[1, 1]["at_m"]
            centre = node(i, [xs[i], (a[1]+b[1])/2, a[2]+.37*(b[2]-a[2])])
            centres.append(centre)
            for (j, k), corner in sorted(station.items()):
                edge(f"{i}/branch/{j}/{k}", centre, corner["id"], "spine-load-transfer-branch")
            if i:
                edge(f"{i}/longitudinal", centres[i-1], centre, "central-longitudinal-spine")
    else:
        for i, (left, right) in enumerate(zip(stations, stations[1:])):
            a, b = left[0, 0]["at_m"], left[1, 1]["at_m"]
            centre = node(i, [(xs[i]+xs[i+1])/2, (a[1]+b[1])/2, a[2]+.63*(b[2]-a[2])])
            for side, station in enumerate((left, right)):
                for (j, k), corner in sorted(station.items()):
                    edge(f"{i}/branch/{side}/{j}/{k}", centre, corner["id"], "cellular-pyramidal-diaphragm")
    # Canonical physical order avoids assigning different geometry IDs merely
    # because the two commutative additive productions ran in a different order.
    nodes.sort(key=lambda row: row["id"]); members.sort(key=lambda row: row["id"]); parts.sort(key=lambda row: row["id"])
    old_joins = {row["id"]: row for row in value["joins"]}
    joins = []
    for n in nodes:
        uid = "joint/" + n["id"]
        row = deepcopy(old_joins.get(uid, dict(id=uid, method="pin/clevis-underfloor-hypothesis",
            net_hardware_mass_kg=None, preload_slip_strength="unknown")))
        row["part_ids"] = sorted(m["part_id"] for m in members if n["id"] in (m["start_node"], m["end_node"]))
        joins.append(row)
    value["joins"] = joins; value["physical"]["joins"] = deepcopy(joins)
    geometry = [{k: v for k, v in q.items() if k not in ("mass_kg", "access", "process", "joint_end_detail")} for q in parts]
    value["physical"]["geometry"] = geometry
    cid = identity(value["physical"]); value["candidate_id"] = cid
    source = dict(value["sources"], **{PRODUCER: LOADED_SOURCE_SHA256,
        interface_graph.PRODUCER: digest(Path(interface_graph.__file__))})
    value["sources"] = source
    old_components = {row["occurrence_id"]: row for row in value["components"]}
    components = []
    for part, geom in zip(parts, geometry):
        row = deepcopy(old_components.get(part["id"], dict(occurrence_id=part["id"], part_id=part["id"],
            functions=part["functions"], mass_kg=part["mass_kg"], stock={"mass_kg": part["mass_kg"]}, inventory_status="located")))
        row.update(component_definition_id=identity(geom), ports=[])
        if "candidate_id" in row: row["candidate_id"] = cid
        components.append(row)
    for joint in joins:
        row = deepcopy(old_components.get(joint["id"], dict(occurrence_id=joint["id"], part_id=joint["id"],
            functions=["transfer-loads"], stock={"mass_kg": None}, inventory_status="unknown")))
        row.update(component_definition_id=identity(joint), ports=[_port("load-transfer")])
        if "candidate_id" in row: row["candidate_id"] = cid
        components.append(row)
    by_component = {row["occurrence_id"]: row for row in components}
    connections = []
    for member in members:
        for end, key in enumerate(("start_node", "end_node")):
            port = "end-" + str(end)
            by_component[member["part_id"]]["ports"].append(_port(port))
            connections.append(dict(id=member["id"] + "/" + port,
                **{"from": [member["part_id"], port], "to": ["joint/" + member[key], "load-transfer"]}))
    occupied = {row["occurrence_id"] for row in components}
    components.extend(deepcopy(row) for uid, row in old_components.items() if uid not in occupied)
    value["components"] = sorted(components, key=lambda row: row["occurrence_id"])
    value["connections"] = sorted(connections, key=lambda row: row["id"])
    known = fsum(part["mass_kg"] for part in parts); value["known_structure_stock_kg"] = known
    basis = value["structure"]["load_basis"]
    load_mass = known + fsum(row["mass_kg"] for row in value["retained_equipment_accounts"] if row["system"] != "bogies") + basis["normal_people"]*75.0
    loads = []
    for i, x in enumerate(xs):
        left = -8.5 if i == 0 else (xs[i-1]+x)/2
        right = 8.5 if i == len(xs)-1 else (x+xs[i+1])/2
        for j in (0, 1):
            loads.append(dict(node_id=stations[i][j, 1]["id"], force_N=[0., 0., -load_mass*9.80665*(right-left)/17/2]))
    value["structure"].update(candidate_id=cid, nodes=deepcopy(nodes), members=deepcopy(members), loads=loads,
        source_sha256={**value["structure"]["source_sha256"], **source})
    basis.update(known_body_stock_kg=known, sprung_mass_hypothesis_kg=load_mass,
        mutation_load_hypothesis="Uniform tributary sprung mass over original station corners; detailed stock self-weight distribution unresolved")
    for op in value["assembly"]:
        if op["id"] in ("cut", "inspect"): op["occurrences"] = [part["id"] for part in parts]
        elif op["id"] == "chassis":
            op["occurrences"] = [part["id"] for part in parts if part["id"].startswith("chassis/")] + [row["id"] for row in joins]
    operation_id = "topology/" + operator + "/join-and-inspect"
    operation = dict(id=operation_id, occurrences=added_members + ["joint/"+uid for uid in added_nodes],
        requires=["cut"], hours=None, data_validity={"validity": "unknown"})
    value["assembly"].insert(1, operation)
    next(op for op in value["assembly"] if op["id"] == "chassis")["requires"].append(operation_id)
    value["topology_mutations"] = deepcopy(history) + [dict(operator=operator,
        parent_candidate_id=candidate["candidate_id"], parent_definition_id=candidate["definition_id"],
        requirement_revision=requirement_revision, producer_sha256=LOADED_SOURCE_SHA256,
        added_node_ids=added_nodes, added_member_ids=added_members,
        added_gross_stock_mass_kg=known-candidate["known_structure_stock_kg"])]
    value["parent_candidate_ids"] = [candidate["candidate_id"]]; value["revision_reason"] = reason
    value["topology_unresolved_domains"] = OPEN_DOMAINS.copy()
    value["full_body_evaluator"] = "unavailable-for-new-topology"
    value.pop("definition_id"); value["definition_id"] = identity(value)
    return _projection_checks(value)

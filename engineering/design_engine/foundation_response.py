"""Source-qualified elastic pile/cap response and cyclic stiffness sensitivity.

The existing three-dimensional Timoshenko kernel supplies the pile elements.
Entered soil springs and section rigidities remain conditional research inputs;
this is neither a site resistance model nor a calibrated p-y/t-z/q-z law.
"""

from __future__ import annotations

import math

import numpy as np

from .contracts import fingerprint, identity, number

REFERENCES = {
    "lateral_soil_and_group_scope": "https://www.fhwa.dot.gov/engineering/geotech/pubs/hif18031.pdf",
    "pile_group_settlement_scope": "https://www.publications.usace.army.mil/Portals/76/Publications/EngineerManuals/EM_1110-2-2906.pdf",
}
SECTION_UNITS = {
    "EA_n": "N", "EIy_nm2": "N m2", "EIz_nm2": "N m2",
    "GJ_nm2": "N m2", "GAy_n": "N", "GAz_n": "N",
}


def _blank(unit):
    return dict(value=None, unit=unit, source=dict(reference=None, sha256=None, basis=None))


def _contains(cap, pile):
    primitives = cap["manufacturing"]["primitives"]
    if len(primitives) != 1 or primitives[0]["kind"] != "box":
        raise ValueError("actual rectangular foundation cap geometry required")
    centre = cap["properties"]["cg_m"]
    dimensions = primitives[0]["dimensions_m"]
    x, y, z = pile["centre_m"]
    head_z = z+pile["length_m"]/2
    return (abs(x-centre[0])+pile["radius_m"] <= dimensions[0]/2+1e-9
            and abs(y-centre[1])+pile["radius_m"] <= dimensions[1]/2+1e-9
            and abs(head_z-centre[2]) <= dimensions[2]/2+1e-9)


def input_template(contract, context):
    """Map existing cap and pile IDs, leaving all engineering properties blank."""
    from .civil_qualification import foundation_geometry

    geometry = foundation_geometry(contract)
    caps = [p for p in contract["parts"] if p["id"].startswith("foundation-cap-")]
    groups = [dict(physical_cap_id=p["id"], pile_ids=[]) for p in caps]
    unmapped = []
    for pile in geometry["piles"]:
        matches = []
        for cap, group in zip(caps, groups, strict=True):
            if _contains(cap, pile):
                matches.append(group)
        if len(matches) == 1:
            matches[0]["pile_ids"].append(pile["physical_part_id"])
        else:
            unmapped.append(pile["physical_part_id"])
    return dict(
        schema="osr-foundation-response-input/1", identity=identity(context),
        contract_sha256=fingerprint(contract), basis=None, elements_per_pile=8,
        cap_groups=groups, unmapped_physical_pile_ids=unmapped,
        pile_parameters=[dict(
            physical_part_id=p["physical_part_id"],
            section_rigidities={k: _blank(unit) for k, unit in SECTION_UNITS.items()},
            soil=dict(axial_per_length=_blank("N/m2"), lateral_x_per_length=_blank("N/m2"),
                      lateral_y_per_length=_blank("N/m2"),
                      toe_translation=[_blank("N/m") for _ in range(3)],
                      toe_rotation=[_blank("N m/rad") for _ in range(3)]),
            group_stiffness_factor=_blank("1"),
            cyclic=dict(degradation_per_cycle=_blank("1"), minimum_stiffness_fraction=_blank("1")),
        ) for p in geometry["piles"]],
        load_cases=[dict(id="fill-load-case-"+g["physical_cap_id"], physical_cap_id=g["physical_cap_id"],
                         force=[_blank("N") for _ in range(3)], moment=[_blank("N m") for _ in range(3)],
                         cycles=_blank("1")) for g in groups],
    )


def _missing(value, path=""):
    if isinstance(value, dict):
        return [field for key, child in value.items() for field in _missing(child, path+"/"+key)]
    if isinstance(value, list):
        return [field for i, child in enumerate(value) for field in _missing(child, path+"/"+str(i))]
    return [path] if value is None else []


def _vector(rows, unit, name):
    from .civil_qualification import scalar

    if not isinstance(rows, list) or len(rows) != 3:
        raise ValueError("three source-qualified components required for " + name)
    return np.asarray([scalar(row, unit, name, minimum=None) for row in rows])


def cyclic_retention(rate, minimum_fraction, cycles):
    """Declared exponential tangent degradation, not a published soil law.

    All three arguments are entered, source-qualified at the assessment boundary.
    There is no default rate, residual fraction, fatigue rule or hysteretic law.
    """
    number(rate, "cyclic degradation rate", minimum=0)
    number(minimum_fraction, "minimum retained stiffness", minimum=1e-9)
    number(cycles, "cycle count", minimum=0)
    if minimum_fraction > 1 or cycles > 1e12 or rate > 1e6:
        raise ValueError("cyclic response inputs outside bounded research domain")
    return minimum_fraction + (1-minimum_fraction)*math.exp(-rate*cycles)


def _pile_operator(part, pile, parameters, elements, factor):
    """Condense the actual pile's internal nodes to its six head coordinates."""
    from engineering.civil_exploration.spatial_structure import element_matrices
    from .civil_qualification import scalar

    length = number(pile["length_m"], "actual pile length", minimum=1e-6)
    section = parameters["section_rigidities"]
    if set(section) != set(SECTION_UNITS):
        raise ValueError("complete six-direction section rigidities required")
    props = {k: scalar(section[k], unit, k, minimum=1e-9) for k, unit in SECTION_UNITS.items()}
    # The kernel returns M and K. Actual matrix-part mass/inertia supplies its
    # positive mass fields; only K is used in this static calculation.
    props["mass_kg_m"] = number(part["properties"]["mass_kg"], "actual pile matrix mass", minimum=1e-9)/length
    props["polar_mass_kg_m"] = number(part["properties"]["inertia_tensor_kg_m2"][2][2], "actual pile polar inertia", minimum=1e-9)/length
    soil = parameters["soil"]
    if set(soil) != {"axial_per_length", "lateral_x_per_length", "lateral_y_per_length", "toe_translation", "toe_rotation"}:
        raise ValueError("explicit axial, lateral and toe stiffness components required")
    per_length = np.asarray([scalar(soil[key], "N/m2", key) for key in ("lateral_x_per_length", "lateral_y_per_length", "axial_per_length")])
    toe = np.concatenate([_vector(soil["toe_translation"], "N/m", "toe translation"),
                          _vector(soil["toe_rotation"], "N m/rad", "toe rotation")])
    if np.any(toe < 0):
        raise ValueError("nonnegative soil stiffness components required")
    n = 6*(elements+1)
    stiffness = np.zeros((n, n))
    springs = np.zeros(n)
    head = np.asarray(pile["centre_m"], dtype=float) + np.array([0., 0., length/2])
    coordinates = [head + np.array([0., 0., -length*i/elements]) for i in range(elements+1)]
    for i in range(elements):
        _, block, _, _ = element_matrices(coordinates[i], coordinates[i+1], props)
        indices = np.arange(6*i, 6*i+12)
        stiffness[np.ix_(indices, indices)] += block
    for i in range(elements+1):
        tributary = length/elements*(.5 if i in (0, elements) else 1.)
        springs[6*i:6*i+3] = per_length*tributary*factor
    springs[-6:] += toe*factor
    stiffness += np.diag(springs)
    try:
        transfer = np.linalg.solve(stiffness[6:, 6:], -stiffness[6:, :6])
    except np.linalg.LinAlgError as error:
        raise ValueError("unrestrained pile internal degrees of freedom; supply applicable toe/soil laws") from error
    condensed = stiffness[:6, :6] + stiffness[:6, 6:]@transfer
    return dict(K=(condensed+condensed.T)/2, transfer=transfer, springs=springs,
                coordinates=coordinates, head=head)


def assess_foundation_response(contract, inputs, *, context):
    """Solve explicitly entered six-DOF cap demands on complete defined groups."""
    from .civil_qualification import foundation_geometry, scalar
    from engineering.civil_exploration.spatial_structure import skew

    result = dict(schema="osr-foundation-response-assessment/1", state="unknown", cases=[],
                  physical_release=False, foundation_qualified=False, source_files_verified=False,
                  physical_validation=False, spatial_refinement_performed=False,
                  resistance="unknown", consolidation_settlement="unknown", cyclic_capacity="unknown",
                  references=REFERENCES,
                  coordinate_convention="Cap/soil forces and movements use contract global x,y,z. Pile local x runs head-to-toe; local y is global y and local z is global x for these vertical piles.",
                  limitations=[
                      "Entered effective section rigidities; no composite, cracking, reinforcement/bond or cap resistance derived.",
                      "Rigid cap and independent uniform distributed elastic soil springs; group factor reduces entered springs and is not a continuum or layered-ground interaction solution.",
                      "Static load-displacement settlement only; consolidation, creep, uplift separation, liquefaction, scour and ultimate resistance remain open.",
                      "Exponential stiffness sensitivity is a declared research assumption, not calibrated cyclic hysteresis or fatigue acceptance.",
                      "Input source SHA syntax is checked; retained evidence and independent technical review remain separate.",
                      "No spatial/soil-law refinement or measured calibration is established by this solve.",
                  ])
    if inputs is None:
        result["missing_inputs"] = ["source-qualified foundation mechanics"]
        return result
    if inputs.get("schema") != "osr-foundation-response-input/1":
        raise ValueError("versioned foundation response input required")
    if set(inputs) != {"schema", "identity", "contract_sha256", "basis", "elements_per_pile", "cap_groups", "unmapped_physical_pile_ids", "pile_parameters", "load_cases"}:
        raise ValueError("foundation response input fields missing or unknown")
    actual, expected = identity(inputs["identity"]), identity(context)
    if any(actual[k] != expected[k] for k in expected if k != "run_id"):
        raise ValueError("foundation response evidence scope mismatch")
    if inputs.get("contract_sha256") != fingerprint(contract):
        raise ValueError("foundation response refers to a different physical contract")
    missing = _missing({k: v for k, v in inputs.items() if k != "identity"})
    if missing:
        result["missing_inputs"] = missing
        return result
    if not isinstance(inputs.get("basis"), str) or not inputs["basis"].strip():
        raise ValueError("named foundation model assumptions required")
    elements = inputs.get("elements_per_pile")
    if type(elements) is not int or not 2 <= elements <= 32:
        raise ValueError("pile discretisation bounded to 2..32 elements")
    geometry = foundation_geometry(contract)
    piles = {p["physical_part_id"]: p for p in geometry["piles"]}
    parts = {p["id"]: p for p in contract["parts"]}
    rows = inputs.get("pile_parameters")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 32:
        raise ValueError("bounded nonempty actual pile parameter records required")
    parameters = {p["physical_part_id"]: p for p in rows}
    if len(parameters) != len(rows) or set(parameters) != set(piles):
        raise ValueError("each defined physical pile requires exactly one parameter record")
    groups = inputs.get("cap_groups")
    if not isinstance(groups, list) or not 1 <= len(groups) <= 8:
        raise ValueError("bounded nonempty physical cap groups required")
    cap_map, assigned = {}, []
    for group in groups:
        if set(group) != {"physical_cap_id", "pile_ids"}:
            raise ValueError("physical cap and pile identities required")
        cap_id = group["physical_cap_id"]
        if cap_id in cap_map or cap_id not in parts or not cap_id.startswith("foundation-cap-"):
            raise ValueError("unique actual foundation cap identity required")
        if not isinstance(group["pile_ids"], list) or not group["pile_ids"]:
            raise ValueError("each actual cap requires its defined pile IDs")
        cap_map[cap_id] = group["pile_ids"]
        assigned += group["pile_ids"]
    if len(set(assigned)) != len(assigned) or set(assigned) != set(piles) or inputs.get("unmapped_physical_pile_ids"):
        raise ValueError("physical pile groups must cover the full contract exactly once")
    for cap_id, physical_ids in cap_map.items():
        if not all(_contains(parts[cap_id], piles[pid]) for pid in physical_ids):
            raise ValueError("assigned pile head/footprint lies outside its actual cap geometry")
    cases = inputs.get("load_cases")
    if not isinstance(cases, list) or not 1 <= len(cases) <= 8 or len(cases)*len(piles)*elements > 4096:
        raise ValueError("bounded foundation case/discretisation budget required")
    seen = set()
    for case in cases:
        if not isinstance(case.get("id"), str) or not case["id"] or case["id"] in seen:
            raise ValueError("unique named foundation load cases required")
        seen.add(case["id"])
        cap_id = case["physical_cap_id"]
        if cap_id not in cap_map:
            raise ValueError("load case targets an undefined cap group")
        demand = np.concatenate([_vector(case["force"], "N", "cap force"), _vector(case["moment"], "N m", "cap moment")])
        cycles = scalar(case["cycles"], "1", "cycle count")
        cap_position = np.asarray(parts[cap_id]["properties"]["cg_m"], dtype=float)
        operators = []
        cap_k = np.zeros((6, 6))
        for pid in cap_map[cap_id]:
            p = parameters[pid]
            group_factor = scalar(p["group_stiffness_factor"], "1", "group stiffness factor", minimum=1e-9)
            if group_factor > 1:
                raise ValueError("group stiffness factor must be at most unity")
            cyclic = p["cyclic"]
            retained = cyclic_retention(scalar(cyclic["degradation_per_cycle"], "1", "cyclic rate"),
                                        scalar(cyclic["minimum_stiffness_fraction"], "1", "minimum cyclic stiffness", minimum=1e-9), cycles)
            operator = _pile_operator(parts[pid], piles[pid], p, elements, group_factor*retained)
            transform = np.eye(6)
            transform[:3, 3:] = -skew(operator["head"]-cap_position)
            cap_k += transform.T@operator["K"]@transform
            operators.append((pid, operator, transform, retained))
        try:
            if np.min(np.linalg.eigvalsh(cap_k)) <= 0:
                raise np.linalg.LinAlgError("nonpositive cap energy")
            movement = np.linalg.solve(cap_k, demand)
        except np.linalg.LinAlgError as error:
            raise ValueError("unrestrained cap coordinates; supplied soil/pile laws cannot support this model") from error
        if not np.isfinite(movement).all():
            raise ValueError("nonfinite foundation response")
        reactions = np.zeros(6)
        pile_results = []
        for pid, operator, transform, retained in operators:
            q_head = transform@movement
            q = np.concatenate([q_head, operator["transfer"]@q_head])
            soil_reactions = -operator["springs"]*q
            for i, position in enumerate(operator["coordinates"]):
                spring = soil_reactions[6*i:6*i+6]
                reactions[:3] += spring[:3]
                reactions[3:] += spring[3:] + np.cross(position-cap_position, spring[:3])
            pile_results.append(dict(physical_part_id=pid, head_displacement_m=q_head[:3].tolist(),
                                     head_rotation_rad=q_head[3:].tolist(),
                                     head_force_moment_si=(operator["K"]@q_head).tolist(),
                                     cyclic_stiffness_fraction=retained,
                                     spring_reactions_si=soil_reactions.reshape(-1, 6).tolist(),
                                     node_displacements_si=q.reshape(-1, 6).tolist()))
        residual = reactions+demand
        force_error = float(np.max(np.abs(residual[:3]))/max(1., np.max(np.abs(demand[:3]))))
        moment_error = float(np.max(np.abs(residual[3:]))/max(1., np.max(np.abs(demand[3:]))))
        if max(force_error, moment_error) > 1e-6:
            raise ValueError("foundation spring reactions fail force/moment equilibrium")
        result["cases"].append(dict(id=case["id"], physical_cap_id=cap_id, cap_reference_m=cap_position.tolist(),
                                    force_moment_si=demand.tolist(), cap_displacement_m=movement[:3].tolist(),
                                    cap_rotation_rad=movement[3:].tolist(), settlement_m=-float(movement[2]),
                                    lateral_displacement_m=float(np.linalg.norm(movement[:2])),
                                    cap_stiffness_si=cap_k.tolist(), soil_resultant_si=reactions.tolist(),
                                    force_balance_relative_error=force_error, moment_balance_relative_error=moment_error,
                                    numerical_equilibrium="passed", piles=pile_results))
    result.update(state="conditional", input_sha256=fingerprint(inputs), contract_sha256=fingerprint(contract),
                  input_sources=inputs, elements_per_pile=elements,
                  completed_cap_ids=sorted({c["physical_cap_id"] for c in cases}),
                  unassessed_cap_ids=sorted(set(cap_map)-{c["physical_cap_id"] for c in cases}))
    return result

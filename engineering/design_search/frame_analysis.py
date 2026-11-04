"""Bounded six-DOF isotropic Euler--Bernoulli RHS frame research model.

The declared rigid joints and thin-wall torsion are hypotheses. Neither a linear
solution nor a nonsingular matrix establishes real connection, short-member,
strength, fatigue, shell, vehicle or physical acceptance.
"""
from __future__ import annotations

from copy import deepcopy
from math import isclose, isfinite

import numpy as np

from engineering.station_rail.common import identity

PRODUCER = "engineering/design_search/frame_analysis.py"
SCHEMA = "osr-rigid-3d-frame-model/1"
JOINT = "rigid-moment-continuity-research-only"
LAW = "isotropic-linear-elastic-research"
FLAGS = dict(physical_accepted=False, engineering_accepted=False, configuration_adopted=False,
             manufacturing_release=False, operating_release=False, installed_mass_complete=False)
REFERENCES = [
    "https://calfem-python-manual.readthedocs.io/en/latest/element_functions.html#beam3e",
    "https://mechanics.ju.se/SolidMechanics/Torsion.html",
]
LIMITATIONS = [
    "Euler-Bernoulli kinematics exclude shear deformation; short-member applicability remains unverified",
    "Rigid moment-continuity joints do not establish welding, fastener, attachment or real joint stiffness",
    "RHS area and bending inertias use exact four-wall geometry; torsion uses Bredt unless an explicit source-bound section evaluation is supplied",
    "Local plate buckling, shear-centre/warping effects, strength, fatigue, modal response and crash remain unknown",
    "Only explicitly declared isotropic elastic laws are supported; GFRP anisotropy is not inferred",
    "Installed equipment, joint masses, load paths, tolerances and independent physical qualification remain open",
]


def _positive(value, label):
    try:
        valid = type(value) in (int, float) and isfinite(value) and value > 0
    except (OverflowError, ValueError):
        valid = False
    if not valid:
        raise ValueError("Positive finite " + label + " required")
    return float(value)


def _vector(value, label):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError("Explicit three-component " + label + " required")
    if any(type(v) not in (int, float) or not isfinite(v) for v in value):
        raise ValueError("Finite " + label + " required")
    return np.asarray(value, dtype=float)


def section_properties(section):
    """Outer width follows local y; outer height follows local z."""
    b, h, t = [_positive(section.get(k), "RHS " + k) for k in ("width_m", "height_m", "wall_m")]
    if 2*t >= min(b, h):
        raise ValueError("Positive hollow four-wall RHS section required")
    area = b*h - (b-2*t)*(h-2*t)
    iy = (b*h**3 - (b-2*t)*(h-2*t)**3)/12
    iz = (h*b**3 - (h-2*t)*(b-2*t)**3)/12
    am = (b-t)*(h-t)
    j = 4*am*am / (2*(b+h-2*t)/t)
    used,method,basis_id=j,"closed-thin-wall-Bredt-approximation",None
    if "torsion_basis" in section:
        basis=section["torsion_basis"]
        keys={"schema","geometry","geometry_id","request_id","selected_evaluation_id","J_m4","method",
              "source_epoch_id","runtime_id","convergence_rule_id","basis_id"}
        if (not isinstance(basis,dict) or set(basis)!=keys or basis.get("schema")!="osr-section-torsion-basis/1"
                or basis.get("method")!="actual-wall-saint-venant-P1/1"
                or basis.get("geometry")!=dict(width_m=b,height_m=h,wall_m=t)
                or basis.get("geometry_id")!=identity(dict(kind="rhs",width_m=b,height_m=h,wall_m=t))
                or basis.get("basis_id")!=identity({k:v for k,v in basis.items() if k!="basis_id"})):
            raise ValueError("Explicit same-geometry sealed section torsion basis required")
        for key in ("request_id","selected_evaluation_id","source_epoch_id","runtime_id","convergence_rule_id"):
            value=basis[key]
            if not isinstance(value,str) or len(value)!=64 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError("Explicit section torsion evaluation/source/runtime identities required")
        used=_positive(basis["J_m4"],"evaluated section torsion constant")
        if used>iy+iz:raise ValueError("Evaluated torsion constant exceeds geometric polar-inertia bound")
        method,basis_id=basis["method"],basis["basis_id"]
    return dict(area_m2=area, I_y_m4=iy, I_z_m4=iz, J_thin_wall_m4=j,J_used_m4=used,
                torsion_basis_id=basis_id,wall_to_min_outer_dimension=t/min(b, h),torsion_model=method)


def _material(value):
    if (not isinstance(value, dict) or value.get("law") != LAW
            or not isinstance(value.get("source_basis"), str) or not value["source_basis"].strip()):
        raise ValueError("Explicit isotropic elastic research law and source basis required")
    e = _positive(value.get("E_Pa"), "elastic modulus")
    density = _positive(value.get("density_kg_m3"), "stock density")
    nu, shear = value.get("nu"), value.get("G_Pa")
    if nu is not None:
        if type(nu) not in (int, float) or not isfinite(nu) or not -1 < nu < 0.5:
            raise ValueError("Stable finite isotropic Poisson ratio required")
        derived = e/(2*(1+nu))
        if shear is not None and not isclose(_positive(shear, "shear modulus"), derived, rel_tol=1e-10):
            raise ValueError("Conflicting isotropic E, nu and G laws")
        shear = derived
    else:
        shear = _positive(shear, "explicit shear modulus or Poisson ratio")
        nu = e/(2*shear)-1
        if not -1 < nu < 0.5:
            raise ValueError("Declared isotropic E/G ratio is outside stable material domain")
    return dict(E_Pa=e, G_Pa=shear, nu=float(nu), density_kg_m3=density,
                law=LAW, source_basis=value["source_basis"])


def _local_stiffness(length, section, material):
    e, shear = material["E_Pa"], material["G_Pa"]
    k = np.zeros((12, 12))
    for dofs, stiffness in (([0, 6], e*section["area_m2"]/length),
                            ([3, 9], shear*section["J_used_m4"]/length)):
        k[np.ix_(dofs, dofs)] += stiffness*np.array([[1., -1.], [-1., 1.]])
    l = length
    bending = np.array([[12., 6*l, -12., 6*l], [6*l, 4*l*l, -6*l, 2*l*l],
                        [-12., -6*l, 12., -6*l], [6*l, 2*l*l, -6*l, 4*l*l]])
    k[np.ix_([1, 5, 7, 11], [1, 5, 7, 11])] += e*section["I_z_m4"]/l**3*bending
    sign = np.diag([1., -1., 1., -1.])
    k[np.ix_([2, 4, 8, 10], [2, 4, 8, 10])] += e*section["I_y_m4"]/l**3*(sign@bending@sign)
    return k


def _assemble(model):
    if (not isinstance(model, dict) or model.get("schema") != SCHEMA
            or model.get("joint_hypothesis") != JOINT):
        raise ValueError("Explicit rigid research frame model required")
    nodes, members = model.get("nodes"), model.get("members")
    if not isinstance(nodes, list) or not isinstance(members, list) or not 2 <= len(nodes) <= 128 or not 1 <= len(members) <= 1024:
        raise ValueError("Frame method domain is 2..128 nodes and 1..1024 members")
    ids = [node.get("id") for node in nodes]
    if any(not isinstance(n, str) or not n for n in ids) or len(set(ids)) != len(ids):
        raise ValueError("Unique explicit frame node IDs required")
    xyz = {node["id"]: _vector(node.get("at_m"), "node coordinates") for node in nodes}
    index = {key: i for i, key in enumerate(ids)}
    raw_materials = model.get("materials")
    if not isinstance(raw_materials, dict) or not raw_materials:
        raise ValueError("Explicit isotropic frame materials required")
    materials = {key: _material(value) for key, value in raw_materials.items()}
    k = np.zeros((6*len(ids), 6*len(ids)))
    records, seen, edges = [], set(), set()
    for member in members:
        uid, a, b = [member.get(key) for key in ("id", "start_node", "end_node")]
        if not isinstance(uid, str) or not uid or uid in seen or a not in xyz or b not in xyz or a == b:
            raise ValueError("Unique member IDs and declared distinct endpoints required")
        seen.add(uid)
        edge = tuple(sorted((a, b)))
        if edge in edges:
            raise ValueError("Coincident frame members need explicit physical resolution")
        edges.add(edge)
        material = materials.get(member.get("material_id"))
        if material is None:
            raise ValueError("Declared member material is unavailable")
        section = section_properties(member.get("section", {}))
        length = _positive(float(np.linalg.norm(xyz[b]-xyz[a])), "member length")
        x = (xyz[b]-xyz[a])/length
        y_input = _vector(member.get("local_y"), "member local_y roll orientation")
        y = y_input - np.dot(y_input, x)*x
        y_length = float(np.linalg.norm(y))
        if y_length <= 1e-10*max(1., float(np.linalg.norm(y_input))):
            raise ValueError("Explicit local_y orientation must not be parallel to member")
        y /= y_length
        rotation = np.vstack((x, y, np.cross(x, y)))
        transform = np.zeros((12, 12))
        for start in (0, 3, 6, 9):
            transform[start:start+3, start:start+3] = rotation
        local = _local_stiffness(length, section, material)
        dofs = list(range(6*index[a], 6*index[a]+6)) + list(range(6*index[b], 6*index[b]+6))
        k[np.ix_(dofs, dofs)] += transform.T@local@transform
        records.append(dict(id=uid, start_node=a, end_node=b, dofs=dofs, transform=transform,
            local=local, length_m=length, section=section, material=material,
            slenderness=length/max(member["section"]["width_m"], member["section"]["height_m"])))
    loads = model.get("loads")
    if not isinstance(loads, list) or not loads:
        raise ValueError("Explicit nonempty frame load records required; absent demand is not zero")
    force = np.zeros(6*len(ids))
    for load in loads:
        key = load.get("node_id")
        if key not in index:
            raise ValueError("Load node is undeclared")
        start = 6*index[key]
        force[start:start+3] += _vector(load.get("force_N"), "force_N")
        force[start+3:start+6] += _vector(load.get("moment_Nm"), "moment_Nm")
    fixed = set()
    for support in model.get("supports", []):
        key, dofs = support.get("node_id"), support.get("dofs")
        if key not in index or not isinstance(dofs, list) or not dofs or any(type(d) is not int or d not in range(1, 7) for d in dofs):
            raise ValueError("Declared frame support DOFs 1..6 required")
        fixed.update(6*index[key]+d-1 for d in dofs)
    if not np.all(np.isfinite(k)) or not np.all(np.isfinite(force)):
        raise ValueError("Frame stiffness/load arithmetic exceeds finite numerical domain")
    return ids, xyz, records, k, force, sorted(fixed), materials


def evaluate(model):
    """Solve a declared frame or return an explicit numerical model hold."""
    model = deepcopy(model)
    ids, xyz, members, k, force, fixed, materials = _assemble(model)
    free = sorted(set(range(len(force)))-set(fixed))
    eigenvalues = np.array([])
    tolerance = 1e-12
    if free:
        reduced = k[np.ix_(free, free)]
        diagonal = np.diag(reduced)
        scale = np.ones(len(free))
        positive = diagonal > 0
        scale[positive] = 1/np.sqrt(diagonal[positive])
        normalized = scale[:, None]*reduced*scale[None, :]
        eigenvalues = np.linalg.eigvalsh((normalized+normalized.T)*.5)
        tolerance = max(1e-12, float(max(abs(eigenvalues)))*1e-10)
    rank = int(sum(eigenvalues > tolerance))
    held = rank != len(free)
    value = dict(schema="osr-linear-3d-frame-result/1", model_id=identity(model),
        state="held-singular-frame-model" if held else "completed-linear-frame-research-only",
        joint_hypothesis=JOINT, material_laws=materials,
        displacements_m=None, rotations_rad=None, reactions_N=None, reaction_moments_Nm=None,
        member_end_forces_local=None, strain_energy_J=None, external_work_J=None,
        force_equilibrium_residual_N=None, moment_equilibrium_residual_Nm=None,
        maximum_nodal_rotation_rad=None, maximum_nodal_displacement_m=None,
        numerical=dict(free_dofs=len(free), scaled_stiffness_rank=rank, eigenvalue_rank_tolerance=tolerance,
            scaled_stiffness_eigenvalues=eigenvalues.tolist(), rank_test="Diagonal-scaled stiffness; numerical conditioning screen only"),
        member_properties={m["id"]: dict(length_m=m["length_m"], slenderness_length_over_max_section=m["slenderness"],
            **m["section"]) for m in members},
        domain=dict(status="Euler-Bernoulli and rigid-joint applicability unverified",
            kinematic_domain_status="Unverified; maximum rotation and member-relative translation are reported without an acceptance limit",
            minimum_member_slenderness=min(m["slenderness"] for m in members),
            short_member_ids_advisory_lt_10=[m["id"] for m in members if m["slenderness"] < 10],
            advisory_is_not_universal_engineering_acceptance_limit=True),
        limitations=LIMITATIONS, references=REFERENCES, complete_installed_mass_kg=None,
        integrated_selection=None, whole_body_rejected=False, **FLAGS)
    if not held:
        displacement = np.zeros(len(force))
        if free:
            displacement[free] = np.linalg.solve(k[np.ix_(free, free)], force[free])
        reaction = k@displacement-force
        reaction_fixed = np.zeros(len(force))
        reaction_fixed[fixed] = reaction[fixed]
        balance = force+reaction_fixed
        total_force = sum((balance[6*i:6*i+3] for i in range(len(ids))), np.zeros(3))
        total_moment = sum((np.cross(xyz[key], balance[6*i:6*i+3])+balance[6*i+3:6*i+6]
                            for i, key in enumerate(ids)), np.zeros(3))
        vectors = lambda start: {key: displacement[6*i+start:6*i+start+3].tolist() for i, key in enumerate(ids)}
        value.update(displacements_m=vectors(0), rotations_rad=vectors(3),
            reactions_N={key: reaction_fixed[6*i:6*i+3].tolist() for i, key in enumerate(ids)},
            reaction_moments_Nm={key: reaction_fixed[6*i+3:6*i+6].tolist() for i, key in enumerate(ids)},
            member_end_forces_local={m["id"]: (m["local"]@m["transform"]@displacement[m["dofs"]]).tolist() for m in members},
            strain_energy_J=float(.5*displacement@k@displacement), external_work_J=float(.5*force@displacement),
            force_equilibrium_residual_N=total_force.tolist(), moment_equilibrium_residual_Nm=total_moment.tolist(),
            maximum_nodal_rotation_rad=max(float(np.linalg.norm(displacement[6*i+3:6*i+6])) for i in range(len(ids))),
            maximum_nodal_displacement_m=max(float(np.linalg.norm(displacement[6*i:6*i+3])) for i in range(len(ids))),
            maximum_member_relative_translation_over_length=max(float(np.linalg.norm(
                displacement[6*ids.index(m["end_node"]):6*ids.index(m["end_node"])+3]-
                displacement[6*ids.index(m["start_node"]):6*ids.index(m["start_node"])+3]))/m["length_m"] for m in members))
        value["numerical"].update(
            free_force_residual_N_max=max([abs(float(reaction[d])) for d in free if d % 6 < 3], default=0.),
            free_moment_residual_Nm_max=max([abs(float(reaction[d])) for d in free if d % 6 >= 3], default=0.),
            force_equilibrium_relative_residual=float(np.linalg.norm(total_force))/max(1.,sum(float(np.linalg.norm(force[6*i:6*i+3])) for i in range(len(ids)))),
            moment_equilibrium_relative_residual=float(np.linalg.norm(total_moment))/max(1.,sum(float(np.linalg.norm(
                np.cross(xyz[key],force[6*i:6*i+3])+force[6*i+3:6*i+6])) for i,key in enumerate(ids))),
            energy_work_relative_residual=abs(value["strain_energy_J"]-value["external_work_J"])/max(1.,abs(value["strain_energy_J"]),abs(value["external_work_J"])))
    value["evaluation_id"] = identity(value)
    return value

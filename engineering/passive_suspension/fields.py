"""Independent transverse magnetostatic P1 finite-element research evaluator.

Travel is x, transverse is y, up is z. A_x has units Wb/m; B_y=dA/dz,
B_z=-dA/dy. Stock is extruded by length_x_m. The infinite-x approximation
does not calculate end, joint, eddy-current, hysteresis or travel drag losses.
This module does not confer physical acceptance, including on converged maps.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
import math
from pathlib import Path
import tomllib

import numpy as np
import scipy
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

MU0 = 4e-7 * math.pi
ROOT = Path(__file__).resolve().parents[2]
MATERIAL_SOURCE = ROOT / "engineering/ferrite_maglev/candidate-magnetics.toml"
SCHEMA = "osr-passive-transverse-fields/1"


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


def sources():
    """Exact local implementation/material dependencies, not retained outputs."""
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__).resolve(), MATERIAL_SOURCE)}


def material_reference():
    """Retained grade proxies; the steel table is not a measured DC B-H law."""
    value = tomllib.loads(MATERIAL_SOURCE.read_text())["materials"]
    return {"ferrite": value["ferrite"], "steel": value["steel"],
            "copper": value["copper"], "source_sha256": sources()[str(MATERIAL_SOURCE.relative_to(ROOT))]}


def _finite(value, name):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _vertices(region):
    if "vertices_yz_m" in region:
        p = np.asarray(region["vertices_yz_m"], dtype=float)
    else:
        if "bounds_yz_m" in region:
            a, b, c, d = region["bounds_yz_m"]
        else:
            a, b, c, d = (region[k] for k in ("ymin", "ymax", "zmin", "zmax"))
        if not (a < b and c < d):
            raise ValueError("rectangle bounds must have positive area")
        p = np.array([[a, c], [b, c], [b, d], [a, d]], dtype=float)
    if p.ndim != 2 or p.shape[1] != 2 or len(p) < 3 or not np.isfinite(p).all():
        raise ValueError("vertices must be finite y,z pairs")
    q = np.roll(p, -1, axis=0)
    cross = p[:, 0]*q[:, 1]-p[:, 1]*q[:, 0]
    signed_area = float(cross.sum() / 2)
    if abs(signed_area) < 1e-12:
        raise ValueError("region polygon must have positive area")
    if signed_area < 0:
        p = p[::-1].copy()
    # Simple polygons only: a convex region is sufficient for this first solver.
    edge = np.roll(p, -1, axis=0) - p
    next_edge = np.roll(edge, -1, axis=0)
    turns = edge[:, 0]*next_edge[:, 1]-edge[:, 1]*next_edge[:, 0]
    if np.min(turns) < -1e-12:
        raise ValueError("only convex non-self-intersecting polygons are supported")
    return p


def _inside(points, polygon, tolerance=1e-11):
    result = np.ones(len(points), dtype=bool)
    for first, second in zip(polygon, np.roll(polygon, -1, axis=0)):
        edge = second-first
        result &= edge[0]*(points[:, 1]-first[1])-edge[1]*(points[:, 0]-first[0]) >= -tolerance
    return result


def _area(p):
    q = np.roll(p, -1, axis=0)
    return float(np.sum(p[:, 0]*q[:, 1]-p[:, 1]*q[:, 0])/2)


def _settings(settings):
    out = dict(mesh_size_m=0.008, outer_margin_m=0.35, max_nodes=90000,
               steel_model="linear_bound", steel_relative_permeability=1000.,
               nonlinear_max_iterations=100, nonlinear_relaxation=0.35,
               nonlinear_tolerance=2e-4, contour_points_per_cell=3,
               check_convergence=False, refinement_factor=1.5,
               boundary_expansion_factor=1.5, force_relative_tolerance=0.08,
               force_absolute_tolerance_N=2., linkage_relative_tolerance=0.05,
               derivative_relative_tolerance=0.15,
               max_solves=160)
    if settings:
        unknown = set(settings)-set(out)
        if unknown:
            raise ValueError(f"unknown field settings: {sorted(unknown)}")
        out.update(settings)
    for key in ("mesh_size_m", "outer_margin_m", "refinement_factor", "boundary_expansion_factor"):
        if _finite(out[key], key) <= 0:
            raise ValueError(f"{key} must be positive")
    if out["refinement_factor"] <= 1 or out["boundary_expansion_factor"] <= 1:
        raise ValueError("mesh refinement and boundary expansion factors must exceed one")
    if out["steel_model"] not in ("linear_bound", "nonlinear_repo_proxy"):
        raise ValueError("steel model must be a declared linear bound or retained nonlinear proxy")
    if not 1 <= out["steel_relative_permeability"] <= 1e6:
        raise ValueError("steel relative permeability outside supported range")
    for key in ("max_nodes", "max_solves", "nonlinear_max_iterations", "contour_points_per_cell"):
        if type(out[key]) is not int or out[key] < 1:
            raise ValueError(f"{key} must be a positive integer")
    if not 0 < out["nonlinear_relaxation"] <= 1:
        raise ValueError("nonlinear relaxation must lie in (0,1]")
    for key in ("nonlinear_tolerance", "force_relative_tolerance", "force_absolute_tolerance_N",
                "linkage_relative_tolerance", "derivative_relative_tolerance"):
        if _finite(out[key], key) <= 0:
            raise ValueError(f"{key} must be finite and positive")
    return out


def _prepare(geometry, gap_m, lateral_m, roll_rad, currents_A, temperature_C):
    length = _finite(geometry["length_x_m"], "length_x_m")
    if length <= 0:
        raise ValueError("extrusion length must be positive")
    reference_gap = _finite(geometry.get("reference_gap_m", 0), "reference_gap_m")
    gap = reference_gap if gap_m is None else _finite(gap_m, "gap_m")
    if gap < 0:
        raise ValueError("gap cannot be negative")
    roll = _finite(roll_rad, "roll_rad")
    rotation = np.array([[math.cos(roll), -math.sin(roll)], [math.sin(roll), math.cos(roll)]])
    origin = np.asarray(geometry.get("origin_yz_m", [0., -reference_gap]), dtype=float)
    if origin.shape != (2,) or not np.isfinite(origin).all():
        raise ValueError("origin_yz_m must be a finite pair")
    offset = np.array([_finite(lateral_m, "lateral_m"), -(gap-reference_gap)])
    currents = {str(k): _finite(v, "current_A") for k, v in (currents_A or {}).items()}
    reference = material_reference()
    materials = geometry.get("materials", {})
    rows = []
    ids = set()
    circuit_integrals = {}
    for item in geometry["regions"]:
        item = deepcopy(item)
        region_id = str(item["id"])
        if region_id in ids:
            raise ValueError("region identifiers must be unique")
        ids.add(region_id)
        group = item.get("group")
        if group not in ("train", "guideway"):
            raise ValueError("region group must be train or guideway")
        material = str(item["material"])
        mat = materials.get(material, {})
        kind = mat.get("kind", material)
        if kind not in ("air", "steel", "ferrite", "copper", "concrete", "aluminium"):
            raise ValueError(f"unsupported material kind {kind}")
        vertices = _vertices(item)
        br = np.array([_finite(item.get("Br_y_T", 0), "Br_y_T"),
                       _finite(item.get("Br_z_T", 0), "Br_z_T")])
        if np.any(br) and kind != "ferrite":
            raise ValueError("remanence is supported only in a declared ferrite region")
        winding = _finite(item.get("turns_per_m2", 0), "turns_per_m2")
        current_density = _finite(item.get("J_x_A_m2", 0), "J_x_A_m2")
        circuit = item.get("circuit_id")
        if winding and (not circuit or kind != "copper"):
            raise ValueError("winding density requires a copper region and circuit_id")
        if winding and current_density:
            raise ValueError("declare either fixed J_x or a circuit winding, not both")
        if group == "guideway" and (np.any(br) or winding or current_density):
            raise ValueError("guideway must remain passive: no magnets or current sources")
        if group == "train":
            vertices = (vertices-origin) @ rotation.T + origin + offset
            br = rotation @ br
        if kind == "ferrite":
            alpha = mat.get("br_temperature_coefficient_per_k",
                            reference["ferrite"]["br_temperature_coefficient_per_k"])
            br *= 1 + alpha*(temperature_C-20)
        mur = _finite(mat.get("relative_permeability", mat.get("recoil_relative_permeability",
                     reference["ferrite"]["recoil_relative_permeability"] if kind == "ferrite" else 1.)), "relative_permeability")
        if mur < 1:
            raise ValueError("relative permeability must be at least one")
        if winding:
            circuit = str(circuit)
            circuit_integrals[circuit] = circuit_integrals.get(circuit, 0.) + winding*_area(vertices)
            current_density = winding*currents.get(circuit, 0.)
        rows.append(dict(id=region_id, material=material, kind=kind, group=group,
                         vertices=vertices, br=br, mur=mur, J=current_density,
                         winding=winding, circuit=circuit, area=_area(vertices)))
    if not rows or not any(r["group"] == "train" for r in rows):
        raise ValueError("at least one train region is required")
    for circuit, net in circuit_integrals.items():
        total = sum(abs(r["winding"])*r["area"] for r in rows if r["circuit"] == circuit)
        if abs(net) > max(1e-8, total*1e-9):
            raise ValueError(f"circuit {circuit} lacks a balanced forward/return winding")
    if set(currents)-set(circuit_integrals):
        raise ValueError("current requested for an undeclared winding circuit")
    net_current = sum(row["J"]*row["area"] for row in rows)
    absolute_current = sum(abs(row["J"])*row["area"] for row in rows)
    if abs(net_current) > max(1e-8, absolute_current*1e-9):
        raise ValueError("longitudinal current sources require a balanced return path")
    return rows, length, dict(gap_m=gap, lateral_m=float(lateral_m), roll_rad=roll,
                              currents_A=currents, temperature_C=float(temperature_C))


def _axis(lo, hi, knots, h):
    candidates = sorted(set([float(lo), float(hi), *(float(k) for k in knots if lo < k < hi)]))
    points = []
    for value in candidates:
        if not points or value-points[-1] > 1e-11:
            points.append(value)
    out = [points[0]]
    for a, b in zip(points, points[1:]):
        # Uniform subdivisions between every exact rectangular material boundary.
        count = max(1, math.ceil((b-a)/h-1e-10))
        out.extend(np.linspace(a, b, count+1)[1:])
    return np.asarray(out)


def _mesh(rows, settings):
    vertices = np.vstack([r["vertices"] for r in rows])
    lo, hi = vertices.min(axis=0), vertices.max(axis=0)
    margin, h = settings["outer_margin_m"], settings["mesh_size_m"]
    y = _axis(lo[0]-margin, hi[0]+margin, vertices[:, 0], h)
    z = _axis(lo[1]-margin, hi[1]+margin, vertices[:, 1], h)
    if len(y)*len(z) > settings["max_nodes"]:
        raise ValueError(f"mesh node budget exceeded: {len(y)*len(z)} > {settings['max_nodes']}")
    yy, zz = np.meshgrid(y, z)
    nodes = np.column_stack([yy.ravel(), zz.ravel()])
    a = np.arange(len(nodes)).reshape(len(z), len(y))
    ll, lr, ul, ur = (a[:-1, :-1].ravel(), a[:-1, 1:].ravel(),
                      a[1:, :-1].ravel(), a[1:, 1:].ravel())
    triangles = np.vstack([np.column_stack([ll, lr, ur]), np.column_stack([ll, ur, ul])])
    p = nodes[triangles]
    area2 = (p[:, 1, 0]-p[:, 0, 0])*(p[:, 2, 1]-p[:, 0, 1])-(p[:, 2, 0]-p[:, 0, 0])*(p[:, 1, 1]-p[:, 0, 1])
    dy = np.column_stack([p[:, 1, 1]-p[:, 2, 1], p[:, 2, 1]-p[:, 0, 1], p[:, 0, 1]-p[:, 1, 1]])/area2[:, None]
    dz = np.column_stack([p[:, 2, 0]-p[:, 1, 0], p[:, 0, 0]-p[:, 2, 0], p[:, 1, 0]-p[:, 0, 0]])/area2[:, None]
    centres = p.mean(axis=1)
    owner = np.full(len(triangles), -1, dtype=int)
    for index, row in enumerate(rows):
        selected = _inside(centres, row["vertices"], tolerance=-1e-13)
        if np.any((owner >= 0) & selected):
            raise ValueError("overlapping material regions (including train/guideway contact)")
        owner[selected] = index
    boundary = np.zeros(len(nodes), dtype=bool)
    boundary[a[[0, -1], :].ravel()] = True
    boundary[a[:, [0, -1]].ravel()] = True
    return y, z, nodes, triangles, area2/2, dy, dz, owner, ~boundary


def _field_at(points, y, z, nodes, triangles, values):
    """P1 interpolation of scalar or nodal recovered vector values."""
    points = np.asarray(points)
    iy = np.searchsorted(y, points[:, 0], side="right")-1
    iz = np.searchsorted(z, points[:, 1], side="right")-1
    if np.any(iy < 0) or np.any(iy >= len(y)-1) or np.any(iz < 0) or np.any(iz >= len(z)-1):
        raise ValueError("field sample outside mesh")
    u = (points[:, 0]-y[iy])/(y[iy+1]-y[iy])
    v = (points[:, 1]-z[iz])/(z[iz+1]-z[iz])
    first = u >= v
    cell = iz*(len(y)-1)+iy
    index = cell + np.where(first, 0, (len(y)-1)*(len(z)-1))
    weights = np.where(first[:, None], np.column_stack([1-u, u-v, v]), np.column_stack([1-v, u, v-u]))
    # Bilinear recovery preserves reflection symmetry of the orthogonal nodal
    # field; selecting a single triangle would privilege one diagonal.
    ll = iz*len(y)+iy
    corners = np.column_stack([ll, ll+1, ll+len(y), ll+len(y)+1])
    weights = np.column_stack([(1-u)*(1-v), u*(1-v), (1-u)*v, u*v])
    vals = values[corners]
    return np.einsum("ij,ij...->i...", weights, vals), index


def _air_recovery(potential, y, z, rows):
    """Second-order nodal derivatives with stencils confined to air edges.

    Unlike averaging P1 element gradients, the orthogonal reconstruction does
    not introduce a preferred diagonal direction into a symmetric fixture.
    At material boundaries use an outward air-only one-sided stencil.
    """
    A = potential.reshape(len(z), len(y))
    outputs = []
    for axis, coords in ((1, y), (0, z)):
        values = A if axis == 1 else A.T
        yy, zz = np.meshgrid((y[:-1]+y[1:])/2, z) if axis == 1 else np.meshgrid(y, (z[:-1]+z[1:])/2)
        points = np.column_stack([yy.ravel(), zz.ravel()])
        good = np.ones(len(points), dtype=bool)
        for row in rows:
            good &= ~_inside(points, row["vertices"], tolerance=-1e-12)
        edges = good.reshape(yy.shape)
        if axis == 0:
            edges = edges.T
        derivative = np.gradient(values, coords, axis=1, edge_order=2)
        for direction in (-1, 1):
            available = np.zeros_like(values, dtype=bool)
            two = np.zeros_like(values, dtype=bool)
            if direction == 1:
                available[:, :-1] = edges
                two[:, :-2] = edges[:, :-1] & edges[:, 1:]
                opposite = np.zeros_like(available)
                opposite[:, 1:] = edges
            else:
                available[:, 1:] = edges
                two[:, 2:] = edges[:, 1:] & edges[:, :-1]
                opposite = np.zeros_like(available)
                opposite[:, :-1] = edges
            selected = available & ~opposite
            rr, cc = np.where(selected)
            x0, x1 = coords[cc], coords[cc+direction]
            derivative[rr, cc] = (values[rr, cc+direction]-values[rr, cc])/(x1-x0)
            rr, cc = np.where(selected & two)
            x0, x1, x2 = coords[cc], coords[cc+direction], coords[cc+2*direction]
            w0 = (2*x0-x1-x2)/((x0-x1)*(x0-x2))
            w1 = (x0-x2)/((x1-x0)*(x1-x2))
            w2 = (x0-x1)/((x2-x0)*(x2-x1))
            derivative[rr, cc] = w0*values[rr, cc]+w1*values[rr, cc+direction]+w2*values[rr, cc+2*direction]
        outputs.append(derivative if axis == 1 else derivative.T)
    return np.column_stack([outputs[1].ravel(), -outputs[0].ravel()])


def _contour(rows, geometry, h, padding_fraction):
    if "contour_yz_m" in geometry:
        contour = _vertices({"vertices_yz_m": geometry["contour_yz_m"]})
    else:
        train = np.vstack([r["vertices"] for r in rows if r["group"] == "train"])
        lo, hi = train.min(axis=0), train.max(axis=0)
        # Determine available top/bottom/side space from the closest guideway box.
        separation = []
        for row in rows:
            if row["group"] != "guideway":
                continue
            rlo, rhi = row["vertices"].min(axis=0), row["vertices"].max(axis=0)
            dy = max(rlo[0]-hi[0], lo[0]-rhi[0], 0.)
            dz = max(rlo[1]-hi[1], lo[1]-rhi[1], 0.)
            if dy == 0 and dz == 0:
                raise ValueError("guideway enters train bounding box; supply an air-only enclosing contour")
            separation.append(math.hypot(dy, dz))
        pad = min(separation)*padding_fraction if separation else 3*h
        if pad < h*0.2:
            raise ValueError("air gap too small for force contour at requested mesh")
        lo -= pad
        hi += pad
        contour = np.array([[lo[0], lo[1]], [hi[0], lo[1]], [hi[0], hi[1]], [lo[0], hi[1]]])
    for row in rows:
        if row["group"] == "train" and not np.all(_inside(row["vertices"], contour)):
            raise ValueError("force contour does not enclose every train region")
        if row["group"] == "guideway" and np.any(_inside(row["vertices"], contour)):
            raise ValueError("force contour encloses guideway stock")
    return contour


def _maxwell(contour, rows, y, z, nodes, triangles, recovered, owner, length, about, settings):
    force = np.zeros(2)
    torque = 0.
    for first, second in zip(contour, np.roll(contour, -1, axis=0)):
        edge = second-first
        ds = np.linalg.norm(edge)
        count = max(8, math.ceil(ds/settings["mesh_size_m"]*settings["contour_points_per_cell"]))
        samples = first + ((np.arange(count)+0.5)/count)[:, None]*edge
        # Check exact geometry too, rather than relying only on centroid labels.
        if any(np.any(_inside(samples, r["vertices"], tolerance=0)) for r in rows):
            raise ValueError("Maxwell stress contour intersects material; AIR contour required")
        B, elements = _field_at(samples, y, z, nodes, triangles, recovered)
        if np.any(owner[elements] >= 0):
            raise ValueError("Maxwell stress contour lacks an air element buffer")
        normal = np.array([edge[1], -edge[0]])/ds
        traction = (B*(B@normal)[:, None]-0.5*np.sum(B*B, axis=1)[:, None]*normal)/MU0
        integrated = traction*ds/count*length
        force += integrated.sum(axis=0)
        lever = samples-about
        torque += np.sum(lever[:, 0]*integrated[:, 1]-lever[:, 1]*integrated[:, 0])
    return dict(F_y_N=float(force[0]), F_z_N=float(force[1]), M_x_Nm=float(torque))


def _single(geometry, *, gap_m=None, lateral_m=0., roll_rad=0., currents_A=None,
            temperature_C=20., settings=None):
    cfg = _settings(settings)
    temperature_C = _finite(temperature_C, "temperature_C")
    rows, length, operating = _prepare(geometry, gap_m, lateral_m, roll_rad, currents_A, temperature_C)
    y, z, nodes, triangles, area, dy, dz, owner, free = _mesh(rows, cfg)
    n, ne = len(nodes), len(triangles)
    mur = np.ones(ne)
    br = np.zeros((ne, 2))
    J = np.zeros(ne)
    steel = np.zeros(ne, dtype=bool)
    for index, row in enumerate(rows):
        sel = owner == index
        mur[sel] = cfg["steel_relative_permeability"] if row["kind"] == "steel" else row["mur"]
        br[sel] = row["br"]
        J[sel] = row["J"]
        steel[sel] = row["kind"] == "steel"
    gradients = np.stack([dy, dz], axis=2)
    shape = np.einsum("nik,njk->nij", gradients, gradients)*area[:, None, None]
    ii = np.repeat(triangles, 3, axis=1).ravel()
    jj = np.tile(triangles, (1, 3)).ravel()
    ref = material_reference()
    for material in geometry.get("materials", {}).values():
        if "h_a_m" in material or "j_t" in material:
            if material.get("h_a_m") != ref["steel"]["h_a_m"] or material.get("j_t") != ref["steel"]["j_t"]:
                raise ValueError("unsupported alternate B-H table; only the declared retained steel proxy is implemented")
    table_H = np.asarray(ref["steel"]["h_a_m"])
    table_B = np.asarray(ref["steel"]["j_t"]) + MU0*table_H
    changes = []
    converged = cfg["steel_model"] == "linear_bound" or not np.any(steel)
    potential = np.zeros(n)
    for iteration in range(1 if converged else cfg["nonlinear_max_iterations"]):
        nu = 1/(MU0*mur)
        matrix = coo_matrix(((shape*nu[:, None, None]).ravel(), (ii, jj)), shape=(n, n)).tocsr()
        source = area[:, None]*(J[:, None]/3+nu[:, None]*(br[:, 0, None]*dz-br[:, 1, None]*dy))
        rhs = np.bincount(triangles.ravel(), weights=source.ravel(), minlength=n)
        potential[free] = spsolve(matrix[free][:, free], rhs[free])
        if not np.isfinite(potential).all():
            raise ValueError("non-finite finite-element solution")
        B = np.column_stack([np.sum(potential[triangles]*dz, axis=1), -np.sum(potential[triangles]*dy, axis=1)])
        if converged:
            break
        magnitude = np.linalg.norm(B[steel], axis=1)
        H = np.interp(magnitude, table_B, table_H)
        high = magnitude > table_B[-1]
        H[high] = table_H[-1]+(magnitude[high]-table_B[-1])/MU0
        updated = np.divide(magnitude, MU0*H, out=np.full_like(H, 2000.), where=H > 1e-10)
        updated = np.clip(updated, 1., 100000.)
        relative = float(np.max(abs(np.log(updated/mur[steel]))))
        changes.append(relative)
        if relative < cfg["nonlinear_tolerance"]:
            converged = True
            break
        relaxation = cfg["nonlinear_relaxation"]
        mur[steel] = np.exp((1-relaxation)*np.log(mur[steel])+relaxation*np.log(updated))
    residual = float(np.linalg.norm((matrix@potential-rhs)[free])/max(np.linalg.norm(rhs[free]), 1e-30))
    recovered = _air_recovery(potential, y, z, rows)
    about = np.asarray(geometry.get("moment_origin_yz_m", [0., 0.]), dtype=float)
    contours = [_contour(rows, geometry, cfg["mesh_size_m"], f) for f in (0.35, 0.55)]
    forces = [_maxwell(c, rows, y, z, nodes, triangles, recovered, owner, length, about, cfg) for c in contours]
    force = forces[0]
    linkage = {}
    represented_turns = {}
    for index, row in enumerate(rows):
        if not row["winding"]:
            continue
        selected = owner == index
        circuit = row["circuit"]
        linkage[circuit] = linkage.get(circuit, 0.) + float(length*np.sum(area[selected]*row["winding"]*potential[triangles[selected]].mean(axis=1)))
        represented_turns[circuit] = represented_turns.get(circuit, 0.) + float(np.sum(area[selected]*row["winding"]))
    represented = {}
    for index, row in enumerate(rows):
        mask = owner == index
        if not np.any(mask):
            raise ValueError(f"region {row['id']} disappeared at requested mesh")
        entry = {"exact_area_m2": row["area"], "mesh_area_m2": float(area[mask].sum()),
                 "area_relative_error": float(abs(area[mask].sum()/row["area"]-1))}
        if row["kind"] == "steel":
            entry["B_peak_T"] = float(np.linalg.norm(B[mask], axis=1).max())
        if row["kind"] == "ferrite":
            direction = row["br"]/max(np.linalg.norm(row["br"]), 1e-30)
            H = (B[mask]-row["br"])/(MU0*row["mur"])
            entry["H_parallel_min_A_per_m"] = float((H@direction).min())
        represented[row["id"]] = entry
    # Structured triangles exactly conform to axis-aligned rectangles only.
    conforming = all(len(r["vertices"]) == 4 and all(abs(e[0]) < 1e-12 or abs(e[1]) < 1e-12
                     for e in np.roll(r["vertices"], -1, axis=0)-r["vertices"]) for r in rows)
    contour_error = max(abs(forces[0][k]-forces[1][k])/
                        max(abs(forces[0][k]), abs(forces[1][k]), cfg["force_absolute_tolerance_N"])
                        for k in ("F_y_N", "F_z_N"))
    circuits = geometry.get("circuits", {})
    if isinstance(circuits, list):
        circuits = {c["id"]: c for c in circuits}
    resistance = {}
    for circuit in linkage:
        declared = circuits.get(circuit, {})
        r20 = declared.get("resistance_20C_ohm", declared.get("resistance_20c_ohm", declared.get("R20_ohm")))
        if r20 is not None and (_finite(r20, "resistance_20c_ohm") <= 0):
            raise ValueError("declared copper winding resistance must be positive")
        resistance[circuit] = None if r20 is None else float(r20*(1+ref["copper"]["resistance_temperature_coefficient_per_k"]*(temperature_C-20)))
    ferrite = geometry.get("materials", {}).get("ferrite", ref["ferrite"])
    lower_hcj = (ferrite.get("hcj_20c_a_m", ref["ferrite"]["hcj_20c_a_m"])-
                 ferrite.get("hcj_tolerance_a_m", ref["ferrite"]["hcj_tolerance_a_m"])) * (
                 1+ferrite.get("hcj_temperature_coefficient_per_k", ref["ferrite"]["hcj_temperature_coefficient_per_k"])*(temperature_C-20))
    demag_limit = lower_hcj*ferrite.get("demag_hcj_fraction_limit", ref["ferrite"]["demag_hcj_fraction_limit"])
    minimum_H = min([v["H_parallel_min_A_per_m"] for v in represented.values() if "H_parallel_min_A_per_m" in v], default=None)
    material_domain = (ferrite.get("minimum_temperature_c", -20) <= temperature_C <= ferrite.get("maximum_temperature_c", 120)
                       and (minimum_H is None or minimum_H >= -demag_limit))
    return dict(schema=SCHEMA, geometry_id=_digest(geometry), source_sha256=sources(),
                environment=dict(numpy_version=np.__version__, scipy_version=scipy.__version__),
                operating_point=operating, settings=cfg, length_x_m=length, **force,
                flux_linkage_Wb_turn=linkage, coil_R_ohm=resistance,
                coenergy_source_J=float(0.5*rhs@potential*length) if cfg["steel_model"] == "linear_bound" else None,
                steel_B_peak_T=max([v.get("B_peak_T", 0) for v in represented.values()], default=0),
                PM_H_parallel_min_A_per_m=minimum_H,
                PM_recoil_knee_limit_A_per_m=demag_limit,
                PM_demagnetisation_margin_A_per_m=None if minimum_H is None else minimum_H+demag_limit,
                material_model_domain_pass=bool(material_domain),
                region_diagnostics=represented,
                numerical_status="converged" if converged and residual < 1e-8 else "nonconverged",
                diagnostics=dict(nodes=n, triangles=ne, linear_relative_residual=residual,
                                 nonlinear_iterations=iteration+1, nonlinear_last_log_mu_change=changes[-1] if changes else 0.,
                                 rectangle_conforming=conforming,
                                 winding_mesh_net_turns=represented_turns,
                                 air_contours_yz_m=[c.tolist() for c in contours],
                                 contour_forces=forces, contour_relative_difference=contour_error,
                                 contour_check_pass=contour_error <= cfg["force_relative_tolerance"],
                                 mesh_check="not_assessed", boundary_check="not_assessed"),
                validity_scope="2D infinite-travel-length magnetostatics; conditional material proxy",
                steel_model=cfg["steel_model"], material_proxy=ref,
                declared_material_definitions=deepcopy(geometry.get("materials", {})),
                travel_drag_N=None, end_joint_eddy_hysteresis_losses_W=None,
                physical_accepted=False, material_correlated=False,
                _samples=dict(y=y, z=z, nodes=nodes, triangles=triangles, field=recovered,
                              element_B=B, owner=owner))


def _clean(result):
    result.pop("_samples", None)
    return result


def _comparison(first, second, cfg):
    errors = {k: abs(first[k]-second[k])/max(abs(first[k]), abs(second[k]), cfg["force_absolute_tolerance_N"])
              for k in ("F_y_N", "F_z_N")}
    errors.update({"linkage:"+c: abs(first["flux_linkage_Wb_turn"][c]-second["flux_linkage_Wb_turn"][c])/
                   max(abs(first["flux_linkage_Wb_turn"][c]), abs(second["flux_linkage_Wb_turn"][c]), 1e-7)
                   for c in first["flux_linkage_Wb_turn"]})
    errors["steel_B_peak_T"] = abs(first["steel_B_peak_T"]-second["steel_B_peak_T"])/max(first["steel_B_peak_T"], second["steel_B_peak_T"], .01)
    if first["PM_H_parallel_min_A_per_m"] is not None:
        a, b = first["PM_H_parallel_min_A_per_m"], second["PM_H_parallel_min_A_per_m"]
        errors["PM_H_parallel_min_A_per_m"] = abs(a-b)/max(abs(a), abs(b), 100.)
    passed = all(value <= (cfg["linkage_relative_tolerance"] if key.startswith("linkage:") else cfg["force_relative_tolerance"])
                 for key, value in errors.items())
    return dict(relative_differences=errors, passed=passed)


def _quantities(result):
    return {key: deepcopy(result[key]) for key in ("F_y_N", "F_z_N", "M_x_Nm", "flux_linkage_Wb_turn")}


def solve(geometry, *, gap_m=None, lateral_m=0., roll_rad=0., currents_A=None,
          temperature_C=20., settings=None):
    """Solve the spatial PDE; optional refinement/domain checks use fresh solves.

    Positive F_z is upward. Increasing gap moves train downward. A reported
    converged linear solve alone is not a mesh/domain/interpolation pass.
    """
    before = sources()
    cfg = _settings(settings)
    kwargs = dict(gap_m=gap_m, lateral_m=lateral_m, roll_rad=roll_rad,
                  currents_A=currents_A, temperature_C=temperature_C)
    result = _single(geometry, **kwargs, settings=cfg)
    if cfg["check_convergence"]:
        refined_cfg = dict(cfg, mesh_size_m=cfg["mesh_size_m"]/cfg["refinement_factor"], check_convergence=False)
        refined = _single(geometry, **kwargs, settings=refined_cfg)
        expanded = _single(geometry, **kwargs, settings=dict(refined_cfg, outer_margin_m=cfg["outer_margin_m"]*cfg["boundary_expansion_factor"]))
        mesh_check, boundary_check = _comparison(result, refined, cfg), _comparison(refined, expanded, cfg)
        coarse = result
        result = refined
        result["diagnostics"].update(mesh_check=mesh_check, boundary_check=boundary_check,
                                     validation_solves=3, requested_settings=cfg,
                                     validation_quantities={"coarse": _quantities(coarse),
                                                            "refined": _quantities(refined),
                                                            "expanded": _quantities(expanded)},
                                     validation_statuses=[r["numerical_status"] for r in (coarse, refined, expanded)])
        # Preserve the actual mesh used in settings, not the requested coarse mesh.
    else:
        result["diagnostics"]["validation_solves"] = 1
    diagnostic = result["diagnostics"]
    result["interpolation_usable"] = bool(result["numerical_status"] == "converged" and result["material_model_domain_pass"] and diagnostic["rectangle_conforming"]
        and diagnostic["contour_check_pass"] and isinstance(diagnostic["mesh_check"], dict)
        and diagnostic["mesh_check"]["passed"] and diagnostic["boundary_check"]["passed"]
        and all(s == "converged" for s in diagnostic.get("validation_statuses", []))
        and max(v["area_relative_error"] for v in result["region_diagnostics"].values()) < 1e-8
        and max((abs(v) for v in diagnostic["winding_mesh_net_turns"].values()), default=0) < 1e-7)
    if sources() != before:
        raise ValueError("field evaluator/material sources changed during solve")
    result["source_sha256"] = before
    _clean(result)
    result["result_id"] = _digest(result)
    return result


def sample_field(geometry, points_yz_m, **kwargs):
    """Diagnostic AIR B samples for independent analytical fixtures (Tesla)."""
    before = sources()
    result = _single(geometry, **kwargs)
    samples = result.pop("_samples")
    B, elements = _field_at(np.asarray(points_yz_m, dtype=float), samples["y"], samples["z"],
                     samples["nodes"], samples["triangles"], samples["field"])
    if np.any(samples["owner"][elements] >= 0):
        raise ValueError("sample_field currently supports air samples only")
    if sources() != before:
        raise ValueError("field sources changed during sampling")
    return B.tolist()


def _difference(a, b, width):
    return (a-b)/width


def field_map(geometry, *, gaps_m, laterals_m, currents_A, temperatures_C=(20.,),
              circuit_id=None, series_circuits=None, settings=None, derivative_steps=None):
    """Regular-grid force/linkage map with independently solved central differences.

    One circuit or explicit signed series connection is varied; others remain
    at zero. series_circuits maps actual circuit IDs to +1/-1 current polarity.
    The connection is an evaluation hypothesis, not altered physical stock.
    Every row
    retains its own point and twelve central/half-step FD solve identities.
    A trial budget counts refinement/domain checks as solves. Unchecked or
    invalid FD points make interpolation_usable false, never a successful map.
    """
    cfg = _settings(settings)
    before = sources()
    axes = {"gap_m": sorted(set(_finite(v, "gap_m") for v in gaps_m)),
            "lateral_m": sorted(set(_finite(v, "lateral_m") for v in laterals_m)),
            "current_A": sorted(set(_finite(v, "current_A") for v in currents_A)),
            "temperature_C": sorted(set(_finite(v, "temperature_C") for v in temperatures_C))}
    if any(not a for a in axes.values()):
        raise ValueError("all field map axes must be nonempty")
    circuits = sorted({r["circuit_id"] for r in geometry["regions"] if r.get("turns_per_m2")})
    if series_circuits is not None:
        connection = {str(k): float(v) for k, v in series_circuits.items()}
        if not connection or set(connection)-set(circuits) or any(v not in (-1., 1.) for v in connection.values()):
            raise ValueError("series_circuits must map declared circuits to +1/-1 polarity")
        circuit_id = circuit_id or "declared-series-connection"
    elif circuit_id is None:
        if len(circuits) != 1:
            raise ValueError("field map requires one explicitly selected declared circuit")
        circuit_id = circuits[0]
        connection = {circuit_id: 1.}
    else:
        connection = {circuit_id: 1.}
    if series_circuits is None and circuit_id not in circuits:
        raise ValueError("field map circuit does not exist")
    steps = dict(gap_m=min(axes["gap_m"])*0.12, lateral_m=0.002, current_A=1.)
    if derivative_steps:
        steps.update(derivative_steps)
    if any(_finite(v, "derivative step") <= 0 for v in steps.values()):
        raise ValueError("derivative steps must be positive")
    requested = list(product(*axes.values()))
    needed = set()
    for coordinates in requested:
        if coordinates[0]-steps["gap_m"] <= 0:
            raise ValueError("gap derivative would leave the positive-gap domain")
        needed.add(tuple(round(v, 12) for v in coordinates))
        for axis, step in enumerate(steps.values()):
            for factor in (-1., -.5, .5, 1.):
                values = list(coordinates)
                values[axis] += factor*step
                needed.add(tuple(round(v, 12) for v in values))
    expected_solves = len(needed)*(3 if cfg["check_convergence"] else 1)
    if expected_solves > cfg["max_solves"]:
        raise ValueError(f"field-map numerical trial budget exceeded before launch: {expected_solves} > {cfg['max_solves']}")
    cache = {}
    count = 0
    def run(g, l, i, t):
        nonlocal count
        key = tuple(round(v, 12) for v in (g, l, i, t))
        if key not in cache:
            increment = 3 if cfg["check_convergence"] else 1
            if count+increment > cfg["max_solves"]:
                raise ValueError("field-map numerical trial budget exceeded")
            count += increment
            cache[key] = solve(geometry, gap_m=g, lateral_m=l, currents_A={c: sign*i for c, sign in connection.items()}, temperature_C=t, settings=cfg)
        return cache[key]
    rows = []
    for gap, lateral, current, temp in requested:
        point = run(gap, lateral, current, temp)
        dg, dl, di = steps["gap_m"], steps["lateral_m"], steps["current_A"]
        if gap-dg <= 0:
            raise ValueError("gap derivative would leave the positive-gap domain")
        gp, gm = run(gap+dg, lateral, current, temp), run(gap-dg, lateral, current, temp)
        lp, lm = run(gap, lateral+dl, current, temp), run(gap, lateral-dl, current, temp)
        ip, im = run(gap, lateral, current+di, temp), run(gap, lateral, current-di, temp)
        ghp, ghm = run(gap+dg/2, lateral, current, temp), run(gap-dg/2, lateral, current, temp)
        lhp, lhm = run(gap, lateral+dl/2, current, temp), run(gap, lateral-dl/2, current, temp)
        ihp, ihm = run(gap, lateral, current+di/2, temp), run(gap, lateral, current-di/2, temp)
        nominal = [gp, gm, lp, lm, ip, im]
        half = [ghp, ghm, lhp, lhm, ihp, ihm]
        def derivatives(points, factor, level=None):
            if level:
                points = [p["diagnostics"]["validation_quantities"][level] for p in points]
            a, b, c, d, e, ff = points
            flux = lambda p: sum(sign*p["flux_linkage_Wb_turn"][key] for key, sign in connection.items())
            return dict(dFz_dg_N_per_m=(a["F_z_N"]-b["F_z_N"])/(2*dg*factor),
                        dFz_dI_N_per_A=(e["F_z_N"]-ff["F_z_N"])/(2*di*factor),
                        dFy_dg_N_per_m=(a["F_y_N"]-b["F_y_N"])/(2*dg*factor),
                        dFy_dI_N_per_A=(e["F_y_N"]-ff["F_y_N"])/(2*di*factor),
                        dFy_dy_N_per_m=(c["F_y_N"]-d["F_y_N"])/(2*dl*factor),
                        dFz_dy_N_per_m=(c["F_z_N"]-d["F_z_N"])/(2*dl*factor),
                        dflux_dgap_Wb_turn_per_m=(flux(a)-flux(b))/(2*dg*factor),
                        dflux_dlateral_Wb_turn_per_m=(flux(c)-flux(d))/(2*dl*factor),
                        L_H=(flux(e)-flux(ff))/(2*di*factor))
        main_derivatives = derivatives(half, .5)
        step_derivatives = derivatives(nominal, 1.)
        derivative_checks = {}
        if cfg["check_convergence"]:
            coarse_derivatives = derivatives(half, .5, "coarse")
            boundary_derivatives = derivatives(half, .5, "expanded")
            for key, value in main_derivatives.items():
                # These absolute tolerances only recognise floating numerical
                # zero; they do not establish a useful restoring/damping margin.
                absolute = 1e-5 if key.startswith("dF") else (1e-10 if key == "L_H" else 1e-9)
                errors = dict(mesh=abs(value-coarse_derivatives[key]),
                              boundary=abs(value-boundary_derivatives[key]),
                              half_step=abs(value-step_derivatives[key]))
                uncertainty = max(errors.values())
                passed = uncertainty <= absolute+cfg["derivative_relative_tolerance"]*abs(value)
                derivative_checks[key] = dict(value=value, absolute_uncertainty_estimate=uncertainty,
                                              error_components=errors, numerical_zero_tolerance=absolute,
                                              relative_tolerance=cfg["derivative_relative_tolerance"],
                                              sign_resolved=abs(value)>2*uncertainty+absolute,
                                              passed=passed)
        row = {k: v for k, v in zip(axes, (gap, lateral, current, temp))}
        row.update({k: point[k] for k in ("F_z_N", "F_y_N", "M_x_Nm", "steel_B_peak_T", "PM_H_parallel_min_A_per_m")})
        lam = lambda p: sum(sign*p["flux_linkage_Wb_turn"][c] for c, sign in connection.items())
        resistance_values = [point["coil_R_ohm"][c] for c in connection]
        row.update(flux_linkage_Wb_turn=lam(point), **main_derivatives,
                   R_ohm=None if any(v is None for v in resistance_values) else sum(resistance_values),
                   numerical_status=point["numerical_status"], result_id=point["result_id"],
                   finite_difference_result_ids=[r["result_id"] for r in nominal+half],
                   derivative_checks=derivative_checks,
                   derivatives_validated=bool(derivative_checks) and all(v["passed"] for v in derivative_checks.values()))
        reciprocal = row["dflux_dgap_Wb_turn_per_m"]+row["dFz_dI_N_per_A"]
        row["reciprocity_residual_Wb_turn_per_m"] = reciprocal
        row["reciprocity_relative_residual"] = abs(reciprocal)/max(abs(row["dflux_dgap_Wb_turn_per_m"]), abs(row["dFz_dI_N_per_A"]), 1e-5)
        row.update(dF_z_dgap_N_per_m=row["dFz_dg_N_per_m"],
                   dF_z_dcurrent_N_per_A=row["dFz_dI_N_per_A"],
                   dF_y_dlateral_N_per_m=row["dFy_dy_N_per_m"],
                   dF_y_dcurrent_N_per_A=row["dFy_dI_N_per_A"],
                   dF_y_dgap_N_per_m=row["dFy_dg_N_per_m"],
                   dF_z_dlateral_N_per_m=row["dFz_dy_N_per_m"])
        row["interpolation_usable"] = all(r["interpolation_usable"] for r in [point]+nominal+half) and row["L_H"] > 0 and row["reciprocity_relative_residual"] <= 0.15 and row["derivatives_validated"]
        rows.append(row)
    if sources() != before or any(record["source_sha256"] != before for record in cache.values()):
        raise ValueError("field sources changed during map execution")
    result = dict(schema="osr-passive-field-map/1", geometry_id=_digest(geometry), source_sha256=before,
                  axes=axes, circuit_id=circuit_id, control_circuit_id=circuit_id,
                  series_circuits=connection,
                  unit_scope="per-module-extruded-length", length_x_m=geometry["length_x_m"],
                  derivative_steps=steps, rows=rows,
                  solves=count, solve_records=list(cache.values()),
                  domain=dict(gap_m=[min(axes["gap_m"]), max(axes["gap_m"])],
                              lateral_m=[min(axes["lateral_m"]), max(axes["lateral_m"])],
                              current_A=[min(axes["current_A"]), max(axes["current_A"])],
                              temperature_C=[min(axes["temperature_C"]), max(axes["temperature_C"])],
                              model="finite transverse width, infinite travel length"),
                  numerical_status="converged" if all(r["numerical_status"] == "converged" for r in cache.values()) else "nonconverged",
                  interpolation_usable=all(r["interpolation_usable"] for r in rows),
                  physical_accepted=False, material_correlated=False, travel_drag_N=None,
                  end_joint_eddy_hysteresis_losses_W=None)
    result["domain_id"] = _digest(result["domain"])
    result["map_id"] = _digest(result)
    return result


def benchmarks():
    """Execute compact independent numerical-method fixtures, not vehicle proof.

    The air-PM reference integrates magnetic surface charge analytically. The
    coenergy derivative is independent of the AIR Maxwell force extraction.
    Bounds are declared numerical benchmark tolerances, not engineering gates.
    """
    before = sources()
    air = dict(length_x_m=1., materials={"ferrite": dict(relative_permeability=1., br_temperature_coefficient_per_k=0.)},
               regions=[dict(id="air-pm", material="ferrite", group="train", bounds_yz_m=[-.1,.1,-.05,0.], Br_z_T=.45)])
    sampled = sample_field(air, [[0.,.05],[0.,.1]], settings=dict(mesh_size_m=.01, outer_margin_m=1.))
    analytic = [.45/math.pi*(math.atan(.1/d)-math.atan(.1/(d+.05))) for d in (.05,.1)]
    relative = [abs(value[1]/expected-1) for value, expected in zip(sampled, analytic)]
    isolated = solve(air, settings=dict(mesh_size_m=.01, outer_margin_m=.3))
    fixture = dict(length_x_m=.25, reference_gap_m=.03, regions=[
        dict(id="pm", material="ferrite", group="train", bounds_yz_m=[-.05,.05,-.09,-.03], Br_z_T=.45),
        dict(id="facing", material="steel", group="guideway", bounds_yz_m=[-.18,.18,0.,.04]),
        dict(id="plus", material="copper", group="train", bounds_yz_m=[-.08,-.06,-.08,-.04], turns_per_m2=100000., circuit_id="c"),
        dict(id="minus", material="copper", group="train", bounds_yz_m=[.06,.08,-.08,-.04], turns_per_m2=-100000., circuit_id="c")])
    states = [solve(fixture, gap_m=gap, settings=dict(mesh_size_m=.004, outer_margin_m=.2)) for gap in (.029,.03,.031)]
    energy_force = -(states[2]["coenergy_source_J"]-states[0]["coenergy_source_J"])/.002
    force_error = abs(states[1]["F_z_N"]/energy_force-1)
    map_value = field_map(fixture, gaps_m=[.03], laterals_m=[0.], currents_A=[0.],
                          settings=dict(mesh_size_m=.01, outer_margin_m=.15, check_convergence=True, max_solves=50))
    map_row = map_value["rows"][0]
    result = dict(schema="osr-passive-field-benchmarks/1", source_sha256=before,
                  analytical_pm=dict(reference="Exact infinite-x unit-recoil rectangular PM surface-charge field on symmetry axis",
                                     expected_Bz_T=analytic, computed_B_yz_T=sampled, relative_errors=relative,
                                     relative_tolerance=.025, passed=max(relative)<.025),
                  isolated_self_force=dict(F_y_N=isolated["F_y_N"], F_z_N=isolated["F_z_N"],
                                           absolute_tolerance_N=1e-6,
                                           passed=max(abs(isolated[k]) for k in ("F_y_N","F_z_N"))<1e-6),
                  maxwell_vs_coenergy=dict(maxwell_F_z_N=states[1]["F_z_N"], energy_derivative_F_z_N=energy_force,
                                           relative_difference=force_error, relative_tolerance=.035,
                                           passed=force_error<.035,
                                           result_ids=[r["result_id"] for r in states]),
                  symmetry=dict(F_y_N=states[1]["F_y_N"], M_x_Nm=states[1]["M_x_Nm"],
                                passed=abs(states[1]["F_y_N"])<1e-6 and abs(states[1]["M_x_Nm"])<1e-6),
                  reciprocity=dict(dlambda_dgap_Wb_turn_per_m=map_row["dflux_dgap_Wb_turn_per_m"],
                                   negative_dFz_dI_N_per_A=-map_row["dF_z_dcurrent_N_per_A"],
                                   relative_residual=map_row["reciprocity_relative_residual"],
                                   relative_tolerance=.15, passed=map_row["reciprocity_relative_residual"]<=.15,
                                   L_H=map_row["L_H"], map_id=map_value["map_id"],
                                   derivatives_validated=map_row["derivatives_validated"],
                                   derivative_checks=map_row["derivative_checks"]),
                  numerical_method_benchmark_pass=False,
                  independent_3d_physics_confirmation=False, physical_accepted=False,
                  scope="Method fixtures only: no ferrite coupon correlation, complete installed mass, nonlinear DC material validation, finite-x/end/joint/drag or controller qualification")
    result["numerical_method_benchmark_pass"] = all(result[key]["passed"] for key in
        ("analytical_pm", "isolated_self_force", "maxwell_vs_coenergy", "symmetry", "reciprocity"))
    if sources() != before:
        raise ValueError("field sources changed during benchmarks")
    result["benchmark_id"] = _digest(result)
    return result

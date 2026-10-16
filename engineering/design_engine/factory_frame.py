"""Connected gross elastic bed, with finite base springs and no ideal end pins.

Rigid joint/offset, thin-wall torsion and linear ground are research hypotheses.
This first-order spatial model complements the retained second-order rail cases;
it does not replace them or qualify local plates, welds, anchors or ground.
"""

from __future__ import annotations

from copy import deepcopy
import math
import numpy as np
from scipy.linalg import cho_factor, cho_solve

from engineering.design_consistency.analysis import beam_stiffness, _skew
from engineering.factory_examples import connections, models
from osr_mech.section_contract import rhs
from .factory_stages import states
from .factory_restraint import support_parts


def arm(offset):
    H = np.eye(6)
    H[:3, 3:] = -_skew(offset)
    return H


def whole_bed(cfg, strongback, restraint_cfg, bed):
    """Manufactured primitives; complete both heads, rails and all 16 supports."""
    source = connections.strongback_parts(cfg, strongback)
    parts = []
    mirror = 2 * bed["origin_x_m"] + bed["active_length_m"]
    for end in (0, 1):
        for item in source:
            if item["role"] in {"return-rail-steel", "post-steel"}:
                continue
            item = deepcopy(item)
            item["id"] = f"end-{end}/" + item["id"]
            if end:
                item["at_m"][0] = mirror - item["at_m"][0] - models.global_size(item)[0]
            parts.append(item)
    for y in (-1.85, 1.85):
        parts.append(
            models.part(
                f"full-return-{y}",
                [bed["active_length_m"], 0.3, 0.5],
                [bed["origin_x_m"], y - 0.15, strongback["axis_z_m"] - 0.25],
                kind="tube",
                axis=0,
                wall_m=0.016,
                role="return-rail-steel",
            )
        )
    for station in bed["brace_stations_m"]:
        support_cfg = dict(cfg, restraint_station_m=station)
        for y in (-1.85, 1.85):
            parts.append(
                models.part(
                    f"post-{station}-{y}",
                    [cfg["post_outer_m"]] * 2 + [strongback["post_length_m"]],
                    [station - cfg["post_outer_m"] / 2, y - cfg["post_outer_m"] / 2, 0],
                    kind="tube",
                    axis=2,
                    wall_m=cfg["post_wall_m"],
                    role="post-steel",
                )
            )
        for item in support_parts(restraint_cfg, support_cfg):
            item["id"] = f"station-{station}/" + item["id"]
            parts.append(item)
    return dict(
        id="OSR-WHOLE-STRESSING-BED",
        parts=parts,
        interference_roles=[
            "strongback-steel",
            "return-rail-steel",
            "post-steel",
            "support-baseplate-steel",
            "support-washer-steel",
        ],
    )


def definition(a, bed, cfg, strongback, native, ground):
    nodes, members, springs = [], [], []
    node_index = {}

    def node(point):
        key = tuple(round(float(v), 10) for v in point)
        if key not in node_index:
            node_index[key] = len(nodes)
            nodes.append(list(key))
        return node_index[key]

    def member(label, i, j, section, oi=(0, 0, 0), oj=(0, 0, 0)):
        members.append(
            dict(
                id=label,
                i=i,
                j=j,
                offset_i_m=list(oi),
                offset_j_m=list(oj),
                section=section,
            )
        )

    E = a["steel_elastic_modulus_pa"]
    rho = a["steel_density_kg_m3"]
    rail_section = rhs(0.3, 0.5, 0.016, density_kg_m3=rho)
    head_section = rhs(
        cfg["box_depth_x_m"], cfg["box_height_z_m"], cfg["wall_m"], density_kg_m3=rho
    )
    post_section = rhs(
        cfg["post_outer_m"], cfg["post_outer_m"], cfg["post_wall_m"], density_kg_m3=rho
    )
    z = strongback["axis_z_m"]
    start = bed["origin_x_m"]
    end = start + bed["active_length_m"]
    head_x = [start - cfg["box_depth_x_m"] / 2, end + cfg["box_depth_x_m"] / 2]
    ys = sorted(
        set(
            [-cfg["box_length_y_m"] / 2, cfg["box_length_y_m"] / 2, -1.85, 1.85]
            + [sign * p["y_m"] for p in strongback["points"] for sign in (-1, 1)]
            + [-0.7175, 0, 0.7175]
        )
    )
    head_nodes = []
    for e, x in enumerate(head_x):
        own = [node([x, y, z]) for y in ys]
        head_nodes.append(own)
        for i, j in zip(own, own[1:]):
            member(f"head-{e}-{i}", i, j, head_section)
    xs = sorted(
        set(
            [start, end]
            + list(bed["brace_stations_m"])
            + [start + k for k in range(1, int(bed["active_length_m"]))]
        )
    )
    for y in (-1.85, 1.85):
        own = (
            [head_nodes[0][ys.index(y)]]
            + [node([x, y, z]) for x in xs[1:-1]]
            + [head_nodes[1][ys.index(y)]]
        )
        for k, (i, j) in enumerate(zip(own, own[1:])):
            member(
                f"rail-{y}-{k}",
                i,
                j,
                rail_section,
                (cfg["box_depth_x_m"] / 2, 0, 0) if k == 0 else (0, 0, 0),
                (-cfg["box_depth_x_m"] / 2, 0, 0) if k == len(own) - 2 else (0, 0, 0),
            )
        for x in bed["brace_stations_m"]:
            top = node([x, y, z])
            base = node([x, y, 0])
            member(f"post-{x}-{y}", base, top, post_section, oj=(0, 0, -0.25))
            springs.append(
                dict(
                    node=base,
                    k=list(ground["translation_n_m"]) + list(ground["rotation_nm_rad"]),
                )
            )
    gravity = np.zeros(6 * len(nodes))
    # Native steel primitives supply nominal mass/CG loads; bought-in envelopes
    # and foundation reservations do not acquire invented mass.
    steel_mass = 0.0
    for part in native["parts"]:
        if not part["role"].endswith("steel"):
            continue
        mass = models.volume(part) * rho
        steel_mass += mass
        cg = np.array(part["at_m"]) + np.array(models.global_size(part)) / 2
        if part["role"] == "strongback-steel":
            e = 0 if cg[0] < start else 1
            indices = head_nodes[e]
        elif part["role"] == "return-rail-steel":
            indices = [
                k
                for k, p in enumerate(nodes)
                if abs(p[1] - cg[1]) < 1e-8 and abs(p[2] - z) < 1e-8
            ]
            # Split uniform rail gravity over the physical member lengths below.
            for m in members:
                if not m["id"].startswith(f"rail-{cg[1]}-"):
                    continue
                i, j = m["i"], m["j"]
                pi = np.array(nodes[i]) + m["offset_i_m"]
                pj = np.array(nodes[j]) + m["offset_j_m"]
                L = np.linalg.norm(pj - pi)
                q = -rail_section["mass_kg_m"] * 9.80665
                local = np.array(
                    [
                        0,
                        0,
                        q * L / 2,
                        0,
                        -q * L * L / 12,
                        0,
                        0,
                        0,
                        q * L / 2,
                        0,
                        q * L * L / 12,
                        0,
                    ]
                )
                # Rails lie along global +x: local/global axes coincide.
                H = np.zeros((12, 12))
                H[:6, :6] = arm(m["offset_i_m"])
                H[6:, 6:] = arm(m["offset_j_m"])
                ids = list(range(6 * i, 6 * i + 6)) + list(range(6 * j, 6 * j + 6))
                gravity[ids] += H.T @ local
            continue
        elif part["role"] == "post-steel":
            indices = [
                node_index[(round(float(cg[0]), 10), round(float(cg[1]), 10), 0.0)]
            ]
            # Axial post gravity shared by its two ends; its bending eccentricity
            # is zero for this vertical gross member.
            top = node_index[
                (round(float(cg[0]), 10), round(float(cg[1]), 10), round(z, 10))
            ]
            for i in (indices[0], top):
                gravity[6 * i + 2] -= mass * 9.80665 / 2
            continue
        else:
            indices = [
                min(
                    range(len(nodes)),
                    key=lambda k: np.linalg.norm(np.array(nodes[k]) - cg),
                )
            ]
        # Two adjacent head nodes preserve the gravity first moment along y.
        ordered = sorted(indices, key=lambda k: nodes[k][1])
        if len(ordered) > 1:
            upper = next(
                (k for k in range(1, len(ordered)) if nodes[ordered[k]][1] >= cg[1]),
                len(ordered) - 1,
            )
            pair = ordered[upper - 1 : upper + 1]
            lo, hi = [nodes[k][1] for k in pair]
            weights = [(hi - cg[1]) / (hi - lo), (cg[1] - lo) / (hi - lo)]
        else:
            pair, weights = ordered, [1]
        for i, w in zip(pair, weights):
            f = np.array([0, 0, -mass * 9.80665 * w])
            gravity[6 * i : 6 * i + 3] += f
            gravity[6 * i + 3 : 6 * i + 6] += np.cross(cg - nodes[i], f)
    return dict(
        schema="osr-factory-spatial-frame/1",
        nodes_m=nodes,
        members=members,
        springs=springs,
        young_pa=E,
        poisson=0.3,
        gravity_load=gravity.tolist(),
        represented_steel_mass_kg=steel_mass,
        head_nodes=head_nodes,
        head_y_m=ys,
        head_x_m=head_x,
        axis_z_m=z,
        ground=ground,
        actual_ground=None,
        physical_release=False,
    )


def system(model):
    n = 6 * len(model["nodes_m"])
    K = np.zeros((n, n))
    for m in model["members"]:
        i, j = m["i"], m["j"]
        p = np.array(model["nodes_m"][i]) + m["offset_i_m"]
        q = np.array(model["nodes_m"][j]) + m["offset_j_m"]
        H = np.zeros((12, 12))
        H[:6, :6] = arm(m["offset_i_m"])
        H[6:, 6:] = arm(m["offset_j_m"])
        k = (
            H.T
            @ beam_stiffness(p, q, m["section"], model["young_pa"], model["poisson"])
            @ H
        )
        ids = list(range(6 * i, 6 * i + 6)) + list(range(6 * j, 6 * j + 6))
        K[np.ix_(ids, ids)] += k
    for s in model["springs"]:
        if len(s["k"]) != 6 or any(not math.isfinite(k) or k < 0 for k in s["k"]):
            raise ValueError("six finite nonnegative ground springs required")
        ids = range(6 * s["node"], 6 * s["node"] + 6)
        K[np.ix_(ids, ids)] += np.diag(s["k"])
    return K


def loads(model, stage):
    F = np.array(model["gravity_load"], dtype=float)
    for y, z, force in stage["forces"]:
        index = min(
            range(len(model["head_y_m"])), key=lambda k: abs(model["head_y_m"][k] - y)
        )
        if abs(model["head_y_m"][index] - y) > 1e-9:
            raise ValueError("strand must load its actual head node")
        for end, sign in ((0, 1), (1, -1)):
            i = model["head_nodes"][end][index]
            F[6 * i] += sign * force
            F[6 * i + 4] += sign * force * (z - model["axis_z_m"])
    return F


def balance(model, applied, displacement):
    force = np.zeros(3)
    moment = np.zeros(3)
    force_scale = 0.0
    moment_scale = 0.0
    for i, p in enumerate(model["nodes_m"]):
        force += applied[6 * i : 6 * i + 3]
        moment += applied[6 * i + 3 : 6 * i + 6] + np.cross(
            p, applied[6 * i : 6 * i + 3]
        )
        force_scale += float(np.linalg.norm(applied[6 * i : 6 * i + 3]))
        moment_scale += float(
            np.linalg.norm(applied[6 * i + 3 : 6 * i + 6])
            + np.linalg.norm(np.cross(p, applied[6 * i : 6 * i + 3]))
        )
    reactions = []
    for spring in model["springs"]:
        i = spring["node"]
        reaction = -np.array(spring["k"]) * displacement[6 * i : 6 * i + 6]
        reactions.append(dict(node=i, wrench_on_structure=reaction.tolist()))
        force += reaction[:3]
        moment += reaction[3:] + np.cross(model["nodes_m"][i], reaction[:3])
        force_scale += float(np.linalg.norm(reaction[:3]))
        moment_scale += float(
            np.linalg.norm(reaction[3:])
            + np.linalg.norm(np.cross(model["nodes_m"][i], reaction[:3]))
        )
    return dict(
        force_residual_n=force.tolist(),
        moment_residual_nm=moment.tolist(),
        reactions=reactions,
        force_tolerance_n=1e-4 + 1e-7 * force_scale,
        moment_tolerance_nm=1e-3 + 1e-7 * moment_scale,
    )


def assess(model, strongback, values):
    sequence = states(strongback, values["stressing_order"], values["release_order"], 2)
    K = system(model)
    F = np.column_stack([loads(model, s) for s in sequence])
    try:
        U = cho_solve(cho_factor(K), F)
    except np.linalg.LinAlgError as error:
        raise ValueError("spatial bed has an unrestrained mechanism") from error
    rows = []
    worst = 0
    peak = 0
    for col, stage in enumerate(sequence):
        u = U[:, col]
        result = balance(model, F[:, col], u)
        demand = max(
            np.linalg.norm(r["wrench_on_structure"][:3]) for r in result["reactions"]
        )
        if demand > peak:
            peak, worst = float(demand), col
        rows.append(
            dict(
                index=col,
                phase=stage["phase"],
                strand=stage["strand"],
                remaining_fraction=stage["remaining_fraction"],
                maximum_translation_m=float(
                    max(np.linalg.norm(u.reshape(-1, 6)[:, :3], axis=1))
                ),
                maximum_rotation_rad=float(
                    max(np.linalg.norm(u.reshape(-1, 6)[:, 3:], axis=1))
                ),
                maximum_base_force_resultant_n=float(demand),
                linear_residual_n_nm=float(max(abs(K @ u - F[:, col]))),
                **result,
            )
        )
    indices = sorted(
        set([len(strongback["sequences"][values["stressing_order"]]["stages"]), worst])
    )
    if len(indices) == 1:
        indices = [0, *indices]
    return dict(
        schema="osr-factory-spatial-results/1",
        model=model,
        stages=rows,
        native_cases=[
            dict(index=i, load=F[:, i].tolist(), displacement=U[:, i].tolist())
            for i in indices
        ],
        equilibrium_verified=all(
            max(map(abs, r["force_residual_n"])) < r["force_tolerance_n"]
            and max(map(abs, r["moment_residual_nm"])) < r["moment_tolerance_nm"]
            for r in rows
        ),
        maximum_base_force_resultant_n=peak,
        maximum_translation_m=max(r["maximum_translation_m"] for r in rows),
        maximum_rotation_rad=max(r["maximum_rotation_rad"] for r in rows),
        all_base_resistances_qualified=False,
        physical_release=False,
        limitations=[
            "Gross first-order elastic spatial frame; rigid joints/offsets and finite linear six-axis base springs are unmeasured hypotheses",
            "Shear deformation, distortion, warping, local holes/diaphragm stresses, joint slip, contact and material/geometric nonlinearity remain open",
            "Retained second-order independent rail failures are separate mandatory checks; this model cannot clear them",
            "Base spring wrenches include coupled forces and moments; the earlier one-axis anchor/pad screens cannot qualify these biaxial/torsional demands",
            "Native complete bed contains steel geometry and supplier/foundation envelopes; rail splices, mould, product, reinforcement, crane and site qualification remain open",
        ],
    )


def native(source, destination):
    """Actual independent OpenSees element/rigid-link solve of retained cases."""
    import json
    import hashlib
    from pathlib import Path
    import openseespy.opensees as ops

    study = json.loads(Path(source).read_text())
    model = study["model"]
    outputs = []
    for case in study["native_cases"]:
        ops.wipe()
        ops.model("basic", "-ndm", 3, "-ndf", 6)
        for i, p in enumerate(model["nodes_m"], 1):
            ops.node(i, *p)
        next_node = len(model["nodes_m"]) + 1
        for tag, m in enumerate(model["members"], 1):
            physical = []
            points = []
            for key, off in (("i", "offset_i_m"), ("j", "offset_j_m")):
                parent = m[key] + 1
                point = np.array(model["nodes_m"][parent - 1]) + m[off]
                points.append(point)
                if any(m[off]):
                    child = next_node
                    next_node += 1
                    ops.node(child, *point)
                    ops.rigidLink("beam", parent, child)
                    physical.append(child)
                else:
                    physical.append(parent)
            axis = points[1] - points[0]
            axis /= np.linalg.norm(axis)
            reference = [0, 0, 1] if abs(axis[2]) < 0.9 else [0, 1, 0]
            ops.geomTransf("Linear", tag, *reference)
            section = m["section"]
            E = model["young_pa"]
            G = E / (2 * (1 + model["poisson"]))
            ops.element(
                "elasticBeamColumn",
                tag,
                *physical,
                section["area_m2"],
                E,
                G,
                section["j_torsion_m4"],
                section["iy_m4"],
                section["iz_m4"],
                tag,
            )
        grounds = []
        for s_index, spring in enumerate(model["springs"]):
            ground = next_node
            next_node += 1
            grounds.append(ground)
            ops.node(ground, *model["nodes_m"][spring["node"]])
            ops.fix(ground, *([1] * 6))
            mats = []
            for dof, k in enumerate(spring["k"]):
                tag = 10000 + 6 * s_index + dof
                ops.uniaxialMaterial("Elastic", tag, k)
                mats.append(tag)
            ops.element(
                "zeroLength",
                10000 + s_index,
                ground,
                spring["node"] + 1,
                "-mat",
                *mats,
                "-dir",
                1,
                2,
                3,
                4,
                5,
                6,
            )
        ops.timeSeries("Linear", 1)
        ops.pattern("Plain", 1, 1)
        for i in range(len(model["nodes_m"])):
            ops.load(i + 1, *case["load"][6 * i : 6 * i + 6])
        ops.constraints("Transformation")
        ops.numberer("RCM")
        ops.system("BandGeneral")
        ops.integrator("LoadControl", 1)
        ops.algorithm("Linear")
        ops.analysis("Static")
        if ops.analyze(1) != 0:
            raise ValueError("OpenSees spatial solve failed")
        u = np.array(
            [ops.nodeDisp(i + 1) for i in range(len(model["nodes_m"]))]
        ).reshape(-1)
        expected = np.array(case["displacement"])
        if not np.allclose(u, expected, rtol=1e-5, atol=1e-9):
            raise ValueError("independent spatial displacement comparison failed")
        ops.reactions()
        reactions = [ops.nodeReaction(g) for g in grounds]
        expected_reactions = [
            (-np.array(s["k"]) * u[6 * s["node"] : 6 * s["node"] + 6]).tolist()
            for s in model["springs"]
        ]
        if not np.allclose(reactions, expected_reactions, rtol=1e-5, atol=1e-4):
            raise ValueError("independent spatial reaction comparison failed")
        outputs.append(
            dict(
                index=case["index"],
                displacement=u.tolist(),
                ground_reactions=reactions,
                maximum_abs_translation_difference_m=float(
                    max(abs((u - expected).reshape(-1, 6)[:, :3]).flat)
                ),
                maximum_abs_rotation_difference_rad=float(
                    max(abs((u - expected).reshape(-1, 6)[:, 3:]).flat)
                ),
            )
        )
    version = ops.version()
    ops.wipe()
    Path(destination).write_text(
        json.dumps(
            dict(
                schema="osr-factory-spatial-native/1",
                input_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
                opensees=version,
                cases=outputs,
                case_count=len(outputs),
                numerical_comparison_passed=True,
                physical_release=False,
            ),
            indent=2,
        )
        + "\n"
    )

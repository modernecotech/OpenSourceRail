"""Static stressing/unloading hypotheses over the common pinned return rails.

The transverse strongback allocates axial forces and eccentric couples by linear
lever weights. This is an explicit load-allocation hypothesis, not a 3-D box or
strand-to-concrete transfer solution. Every stage keeps the same ideal springs.
"""

from __future__ import annotations

import math
import numpy as np
from scipy.linalg import cho_factor, cho_solve

from engineering.factory_examples import development
from . import factory_restraint as restraint


def states(strongback, order, release, substeps=2):
    if order not in {"balanced_pairs", "lower_first"} or release not in {
        "reverse_stress",
        "same_stress",
    }:
        raise ValueError("controlled stressing and static release orders required")
    if type(substeps) is not int or not 1 <= substeps <= 4:
        raise ValueError("one to four static unloading increments required")
    sequence = strongback["sequences"][order]["stages"]
    if not sequence or len({s["strand"] for s in sequence}) != len(sequence):
        raise ValueError("unique nonempty strand sequence required")
    active = {}
    rows = []

    def retain(phase, strand=None, fraction=None):
        rows.append(
            dict(
                index=len(rows),
                phase=phase,
                strand=strand,
                remaining_fraction=fraction,
                forces=list(active.values()),
            )
        )

    retain("unloaded")
    for strand in sequence:
        active[strand["strand"]] = (
            strand["strand_y_m"],
            strand["strand_z_m"],
            strand["force_per_strand_n"],
        )
        retain("stressing", strand["strand"], 1)
    for strand in reversed(sequence) if release == "reverse_stress" else sequence:
        for step in range(1, substeps + 1):
            fraction = 1 - step / substeps
            active[strand["strand"]] = (
                strand["strand_y_m"],
                strand["strand_z_m"],
                strand["force_per_strand_n"] * fraction,
            )
            retain("unloading", strand["strand"], fraction)
        del active[strand["strand"]]
    return rows


def allocate(forces, rail_y, axis_z):
    """Preserve total axial force, its transverse first moment and vertical couple."""
    left, right = rail_y
    if not math.isfinite(left + right + axis_z) or left >= right:
        raise ValueError("ordered finite rail axes required")
    axial, couples = [0.0, 0.0], [0.0, 0.0]
    for y, z, force in forces:
        if not left <= y <= right or not math.isfinite(z):
            raise ValueError("finite strands between return axes required")
        restraint.positive(force, "strand force", zero=True)
        weights = [(right - y) / (right - left), (y - left) / (right - left)]
        for side, weight in enumerate(weights):
            axial[side] += force * weight
            couples[side] += force * (z - axis_z) * weight
    return dict(
        axial_n=axial,
        end_couple_nm=couples,
        total_force_n=math.fsum(f for _, _, f in forces),
        transverse_first_moment_nm=math.fsum(y * f for y, _, f in forces),
        total_vertical_couple_nm=math.fsum((z - axis_z) * f for _, z, f in forces),
    )


class Rail:
    """Reuse the existing Euler-Bernoulli/geometric matrices with explicit loads."""

    def __init__(self, length, E, I, elements, springs):
        self.K, self.Kg, self.free, self.x = development.column_system(
            length, E, I, elements, springs
        )
        self.critical = development.column_buckling(length, E, I, elements, springs)
        self.length, self.springs = length, springs
        self.nodes = [round(x / (length / elements)) for x, _ in springs]
        self.cache = {}

    def response(self, force, bow, couple=0.0, distributed=0.0):
        for value in (force, bow):
            restraint.positive(value, "axial force/bow", zero=True)
        if not math.isfinite(couple + distributed):
            raise ValueError("finite end couple and distributed load required")
        if force >= self.critical:
            return None
        key = (force, bow, couple, distributed)
        if key in self.cache:
            return self.cache[key]
        h = self.x[1] - self.x[0]
        initial = np.zeros(len(self.K))
        initial[::2] = bow * np.sin(math.pi * self.x / self.length)
        initial[1::2] = (
            bow * math.pi / self.length * np.cos(math.pi * self.x / self.length)
        )
        loads = np.zeros(len(self.K))
        # Positive displacement is upward. Generalized moments act on dz/dx;
        # a positive physical y couple at the left is a negative rotation load.
        loads[1], loads[-1] = -couple, couple
        for j in range(len(self.x) - 1):
            loads[2 * j : 2 * j + 4] += distributed * np.array(
                [h / 2, h * h / 12, h / 2, -h * h / 12]
            )
        rhs = np.column_stack([loads, force * self.Kg @ initial])
        tangent = self.K - force * self.Kg
        delta = np.zeros((len(self.K), 2))
        delta[self.free] = cho_solve(
            cho_factor(tangent[np.ix_(self.free, self.free)]), rhs[self.free]
        )
        residual = tangent @ delta - rhs
        result = dict(
            displacements=delta,
            residual=residual,
            applied=loads,
            free_force_residual_n=float(
                np.max(np.abs(residual[[j for j in self.free if j % 2 == 0]]))
            ),
            free_moment_residual_nm=float(
                np.max(np.abs(residual[[j for j in self.free if j % 2 == 1]]))
            ),
        )
        self.cache[key] = result
        return result

    def actions(self, response, sign):
        delta = response["displacements"][:, 0] + sign * response["displacements"][:, 1]
        residual = response["residual"][:, 0] + sign * response["residual"][:, 1]
        brace = [float(k * delta[2 * n]) for (_, k), n in zip(self.springs, self.nodes)]
        pins = [float(residual[0]), float(residual[-2])]
        load = response["applied"]
        force_balance = math.fsum(pins) - math.fsum(brace) + float(sum(load[::2]))
        moment_balance = (
            pins[1] * self.length
            - math.fsum(x * f for (x, _), f in zip(self.springs, brace))
            + float(self.x @ load[::2] + sum(load[1::2]))
        )
        return dict(
            brace_force_on_support_n=brace,
            pin_force_on_rail_n=pins,
            maximum_additional_displacement_m=float(max(abs(delta[::2]))),
            force_balance_n=force_balance,
            moment_balance_nm=moment_balance,
            free_force_residual_n=response["free_force_residual_n"],
            free_moment_residual_nm=response["free_moment_residual_nm"],
        )


def support_case(cfg, reference, post_length, E, Fy, Fz):
    """Same contact/weld/pad kernels as the retained full-force screen."""
    B, t = cfg["post_outer_m"], cfg["post_wall_m"]
    area = B * B - (B - 2 * t) ** 2
    inertia = (B**4 - (B - 2 * t) ** 4) / 12
    b, d, thickness = cfg["baseplate_m"]
    anchor_k = (
        E
        * math.pi
        * cfg["anchor_proxy_diameter_m"] ** 2
        / 4
        / cfg["anchor_free_length_m"]
    )
    N = reference["post_and_baseplate_dead_force_n"] - Fz
    M = Fy * post_length
    plate = restraint.contact(
        b,
        d,
        cfg["anchor_xy_m"],
        cfg["grout_normal_spring_per_area_n_m3"],
        anchor_k,
        N,
        M,
        strips=cfg["contact_strips"],
    )
    ground_M = Fy * (
        post_length + thickness + cfg["grout_thickness_m"] + cfg["pad_reservation_m"][2]
    )
    return dict(
        lateral_force_n=Fy,
        vertical_upward_force_n=Fz,
        post_downward_force_n=N,
        post_base_moment_nm=M,
        baseplate=plate,
        nominal_post_normal_extreme_pa=max(
            abs(N / area + M * B / 2 / inertia), abs(N / area - M * B / 2 / inertia)
        ),
        post_base_weld=restraint.weld_group(
            B, cfg["post_nominal_fillet_leg_m"], N, M, Fy
        ),
        pad=restraint.pad_pressure(
            *cfg["pad_reservation_m"][:2], N + reference["pad_selfweight_n"], ground_M
        ),
    )


def assess(a, bed, section, strongback, values, cfg, reference, stage_basis):
    if (
        stage_basis.get("schema") != "osr-factory-static-stages/1"
        or stage_basis.get("state") != "synthetic"
    ):
        raise ValueError("explicit synthetic static-stage basis required")
    rail_y = stage_basis["rail_axes_y_m"]
    if rail_y != [-1.85, 1.85]:
        raise ValueError("stage rail axes must match the fixed native strongback")
    stages = states(
        strongback,
        values["stressing_order"],
        values["release_order"],
        stage_basis["release_substeps"],
    )
    stations = [x - bed["origin_x_m"] for x in bed["brace_stations_m"]]
    H, W, t = [v / 1000 for v in section["side_box_mm"]]
    area = W * H - (W - 2 * t) * (H - 2 * t)
    gravity = -area * a["steel_density_kg_m3"] * 9.80665
    inertias = dict(
        lateral=section["weak_inertia_m4"],
        vertical=(W * H**3 - (W - 2 * t) * (H - 2 * t) ** 3) / 12,
    )
    rails = {
        p: Rail(
            bed["active_length_m"],
            a["steel_elastic_modulus_pa"],
            I,
            bed["elements"],
            [(x, values[p + "_spring_n_m"]) for x in stations],
        )
        for p, I in inertias.items()
    }
    rows, governing = [], {}
    solved_cases = 0
    maxima = dict(anchor=0.0, post=0.0, weld=0.0, grout=0.0, pad=0.0)
    for stage in stages:
        allocation = allocate(stage["forces"], rail_y, strongback["axis_z_m"])
        row = {k: v for k, v in stage.items() if k != "forces"}
        row.update(
            allocation,
            stable=True,
            maximum_anchor_tension_n=None,
            maximum_vertical_pin_force_n=None,
            maximum_force_balance_residual_n=0.0,
            maximum_moment_balance_residual_nm=0.0,
            pad_compression_equilibrium=True,
            pin_cases=[],
            unstable_sides=[],
            maximum_lateral_additional_sway_m=0.0,
            maximum_vertical_additional_sway_m=0.0,
        )
        peak_anchor, peak_pin = 0.0, 0.0
        for side, P in enumerate(allocation["axial_n"]):
            responses = {
                p: rail.response(
                    P,
                    bed["initial_sway_m"],
                    allocation["end_couple_nm"][side] if p == "vertical" else 0.0,
                    gravity if p == "vertical" else 0.0,
                )
                for p, rail in rails.items()
            }
            if any(r is None for r in responses.values()):
                row["stable"] = False
                row["unstable_sides"].append(side)
                continue
            for sy in (-1, 1):
                lateral = rails["lateral"].actions(responses["lateral"], sy)
                for sz in (-1, 1):
                    vertical = rails["vertical"].actions(responses["vertical"], sz)
                    row["maximum_lateral_additional_sway_m"] = max(
                        row["maximum_lateral_additional_sway_m"],
                        lateral["maximum_additional_displacement_m"],
                    )
                    row["maximum_vertical_additional_sway_m"] = max(
                        row["maximum_vertical_additional_sway_m"],
                        vertical["maximum_additional_displacement_m"],
                    )
                    if sy == -1:
                        row["pin_cases"].append(
                            dict(
                                side=side,
                                vertical_sign=sz,
                                force_on_foundation_n=[
                                    -v for v in vertical["pin_force_on_rail_n"]
                                ],
                                x_m=[
                                    bed["origin_x_m"],
                                    bed["origin_x_m"] + bed["active_length_m"],
                                ],
                            )
                        )
                    peak_pin = max(peak_pin, *map(abs, vertical["pin_force_on_rail_n"]))
                    for response in (lateral, vertical):
                        row["maximum_force_balance_residual_n"] = max(
                            row["maximum_force_balance_residual_n"],
                            abs(response["force_balance_n"]),
                            response["free_force_residual_n"],
                        )
                        row["maximum_moment_balance_residual_nm"] = max(
                            row["maximum_moment_balance_residual_nm"],
                            abs(response["moment_balance_nm"]),
                            response["free_moment_residual_nm"],
                        )
                    for station, Fy, Fz in zip(
                        bed["brace_stations_m"],
                        lateral["brace_force_on_support_n"],
                        vertical["brace_force_on_support_n"],
                        strict=True,
                    ):
                        case = support_case(
                            cfg,
                            reference,
                            strongback["post_length_m"],
                            a["steel_elastic_modulus_pa"],
                            Fy,
                            Fz,
                        )
                        case.update(
                            stage=row["index"],
                            phase=row["phase"],
                            side=side,
                            global_x_m=station,
                            lateral_sign=sy,
                            vertical_sign=sz,
                            axial_return_force_n=P,
                            end_couple_nm=allocation["end_couple_nm"][side],
                        )
                        solved_cases += 1
                        anchor = max(case["baseplate"]["anchor_tensions_n"])
                        peak_anchor = max(peak_anchor, anchor)
                        row["pad_compression_equilibrium"] &= case["pad"][
                            "compression_equilibrium"
                        ]
                        demands = dict(
                            anchor=anchor,
                            post=case["nominal_post_normal_extreme_pa"],
                            weld=case["post_base_weld"]["nominal_combined_demand_pa"],
                            grout=case["baseplate"][
                                "maximum_sampled_contact_pressure_pa"
                            ],
                            pad=case["pad"]["maximum_pressure_pa"] or 0,
                        )
                        for name, value in demands.items():
                            if name not in governing or value > maxima[name]:
                                maxima[name], governing[name] = value, case
        if row["stable"]:
            row["maximum_anchor_tension_n"], row["maximum_vertical_pin_force_n"] = (
                peak_anchor,
                peak_pin,
            )
        rows.append(row)
    return dict(
        schema="osr-factory-staged-load-path/1",
        basis=stage_basis,
        stressing_order=values["stressing_order"],
        release_order=values["release_order"],
        stages=rows,
        stage_count=len(rows),
        contact_cases_solved=solved_cases,
        all_stages_stable=all(r["stable"] for r in rows),
        all_pad_cases_equilibrate=all(r["pad_compression_equilibrium"] for r in rows),
        numerical_equilibrium_verified=all(
            r["maximum_force_balance_residual_n"] <= 1e-3
            and r["maximum_moment_balance_residual_nm"] <= 1e-2
            for r in rows
        ),
        maximum_anchor_tension_n=(
            maxima["anchor"] if all(r["stable"] for r in rows) else None
        ),
        maximum_vertical_pin_force_n=(
            max((r["maximum_vertical_pin_force_n"] or 0 for r in rows), default=None)
            if all(r["stable"] for r in rows)
            else None
        ),
        governing_cases=governing,
        rail_gravity_n_m=gravity,
        physical_release=False,
        limitations=[
            "Linear transverse lever allocation of rail axial forces/couples is a hypothesis; strongback torsion/warping and 3-D connection stiffness remain unresolved",
            "Opposite end rotation loads assume mirrored tendon fields at the two bed ends; independent end operation is unmodelled",
            "Quasistatic strand unloading is a bed-force hypothesis, not an approved release procedure or strand-to-concrete transmission solution",
            "Ideal end pins remain externally grounded. Their vertical demand is reported; axial closure, foundation resistance and actual end details are unqualified",
            "Rail gravity is included; strongback/mould/service weights, thermal actions, preload, losses, jacking overpull and dynamics remain unmodelled",
            "One-axis post/grout/anchor/pad screens retain fixed ideal spring properties; no self-consistent nonlinear ground or local resistance acceptance",
            "Only the specified stressing endpoints and unloading increments are evaluated; no continuous transient envelope is claimed",
        ],
    )

"""Iteration-two mechanics: explicit alternatives, restraint and interface demands.

No resistance or physical acceptance is inferred from these numerical screens.
"""

from __future__ import annotations

from copy import deepcopy
import math

import numpy as np
from scipy.linalg import eigvalsh

from .models import part, positive, point_beam, pi, volume
from engineering.design_engine.civil_qualification import elastic_shortening

G = 9.80665


def workholding(a, inputs, fix, clamp):
    preload = positive(inputs["requested_clamp_preload_n_each"], "clamp preload")
    horizontal = positive(inputs["tool_horizontal_n"], "tool action")
    upward = positive(inputs["tool_upward_n"], "tool action")
    height = positive(inputs["tool_height_above_datum_m"], "tool height")
    points = np.array([[-0.5, -0.25], [0.5, -0.25], [0, 0.25]])
    matrix = np.vstack([np.ones(3), points[:, 0], points[:, 1]])
    W = fix["payload_demand_n"]
    cases = []
    for cg in inputs["payload_cg_cases_xy_m"]:
        for tool in inputs["tool_cases_xy_m"]:
            for sign in (-1, 1):
                # Horizontal action normal to either datum direction; these are alternatives, not simultaneous maxima.
                for axis in (0, 1):
                    resultant = [
                        W + 3 * preload - upward,
                        W * cg[0] + preload * points[:, 0].sum() - upward * tool[0],
                        W * cg[1] + preload * points[:, 1].sum() - upward * tool[1],
                    ]
                    resultant[axis + 1] += sign * horizontal * height
                    reaction = np.linalg.solve(matrix, resultant)
                    cases.append(
                        dict(
                            payload_cg_xy_m=cg,
                            tool_xy_m=tool,
                            lateral_axis=axis,
                            horizontal_action_n=sign * horizontal,
                            vertical_reactions_n=reaction.tolist(),
                            all_vertical_contacts_compressive=bool(min(reaction) >= 0),
                        )
                    )
    throat = inputs["nominal_crossrail_fillet_leg_m"] / math.sqrt(2)
    weld_length = 2 * (0.05 + 0.1)
    maximum = max(max(c["vertical_reactions_n"]) for c in cases)
    return dict(
        cases=cases,
        minimum_contact_reaction_n=min(min(c["vertical_reactions_n"]) for c in cases),
        all_cases_vertical_contact_screen=all(
            c["all_vertical_contacts_compressive"] for c in cases
        ),
        requested_preload_n_each=preload,
        published_nominal_holding_force_n=clamp["published"][
            "nominal_holding_force_dan"
        ]
        * 10,
        preload_demonstrated=False,
        clamp_force_compatibility=None,
        purchased_clamp_mass_kg=3 * clamp["published"]["mass_kg"],
        crossrail_connection_shear_screen=dict(
            nominal_fillet_leg_m=inputs["nominal_crossrail_fillet_leg_m"],
            weld_length_per_end_m=weld_length,
            throat_area_per_end_m2=throat * weld_length,
            conservative_force_n=maximum,
            nominal_shear_demand_pa=maximum / (throat * weld_length),
            resistance_pa=None,
            all_round_access_unconfirmed=True,
        ),
        open=[
            "Holding force is not applied clamping preload; exact spindle position and actual force require supplier/trial evidence",
            "Lateral locator contact, pin bending, friction, mount bolts, weld eccentricity, wall/local plate deformation and anchors remain unqualified",
            "Load cases are declared tool/CG research scenarios, not a qualified operating envelope",
            "Weld demand uses the full largest support reaction at one crossrail end; shear-only nominal throat screen omits joint bending and resistance",
        ],
        released=False,
    )


def developed_selfweight(span, x, count, a):
    """Simply supported gravity moment, including explicit end-fill patches.

    Gross canonical concrete envelope is displaced by known strand metallic area.
    Additional conventional reinforcement is unknown, never counted as zero final mass.
    """
    rho = pi.CONCRETE_DENSITY_KG_PER_M3
    A = pi.section_area_m2()
    q = (A * rho + count * a["strand_area_m2"] * (a["steel_density_kg_m3"] - rho)) * G
    end = 0.55
    patch_area = (2.9 - 2 * 0.3) * 0.935
    patch_q = patch_area * rho * G
    reaction = q * span / 2 + patch_q * end
    M = reaction * x - q * x * x / 2
    for start in (0, span - end):
        covered = max(0, min(end, x - start))
        if covered:
            M -= patch_q * covered * (x - start - covered / 2)
    mass = (q * span + 2 * patch_q * end) / G
    return M, mass


def prestress_alternatives(a, inputs, section):
    A, I, zc, depth = (
        section[k] for k in ("area_m2", "inertia_x_m4", "centroid_z_m", "depth_m")
    )
    n = inputs["stations_per_span"]
    if type(n) is not int or n < 3:
        raise ValueError("at least three prestress stations required")
    alternatives = []
    for layout in inputs["alternatives"]:
        rows = layout["rows"]
        if not rows or any(
            type(count) is not int or count < 2 or count % 2 or not 0 < z < depth
            for z, count in rows
        ):
            raise ValueError(
                "even positive per-row strand count, within section required"
            )
        count = sum(count for _, count in rows)
        groups = [
            dict(
                metallic_area_m2=count * a["strand_area_m2"],
                pretransfer_stress_pa=a["strand_initial_stress_pa"],
                steel_modulus_pa=a["strand_modulus_pa"],
                eccentricity_m=zc - z,
            )
            for z, count in rows
        ]
        scenarios = []
        for L in pi.CATALOGUE_SPANS_M:
            stations = []
            for j in range(n):
                x = L * j / (n - 1)
                M, mass = developed_selfweight(L, x, count, a)
                losses = elastic_shortening(
                    groups,
                    area_m2=A,
                    inertia_m4=I,
                    concrete_modulus_pa=a["concrete_transfer_modulus_pa"],
                    self_weight_moment_nm=max(M, 0),
                )
                forces = [
                    g["metallic_area_m2"] * (g["pretransfer_stress_pa"] - loss)
                    for g, loss in zip(groups, losses)
                ]
                stresses = {}
                for stage, factor in (
                    ("transfer", 1),
                    ("service_dead_only", 1 - a["additional_prestress_loss_fraction"]),
                ):
                    P = sum(forces) * factor
                    Pe = (
                        sum(p * g["eccentricity_m"] for p, g in zip(forces, groups))
                        * factor
                    )
                    stresses[stage] = dict(
                        force_n=P,
                        prestress_moment_nm=Pe,
                        top_pa=P / A - (Pe - M) * (depth - zc) / I,
                        soffit_pa=P / A + (Pe - M) * zc / I,
                    )
                stations.append(dict(x_m=x, gravity_moment_nm=M, **stresses))
            minima = {
                stage: min(
                    st[stage][fiber]
                    for st in stations
                    for fiber in ("top_pa", "soffit_pa")
                )
                for stage in ("transfer", "service_dead_only")
            }
            maxima = {
                stage: max(
                    st[stage][fiber]
                    for st in stations
                    for fiber in ("top_pa", "soffit_pa")
                )
                for stage in ("transfer", "service_dead_only")
            }
            scenarios.append(
                dict(
                    span_m=L,
                    stations=stations,
                    minimum_compression_pa_by_stage=minima,
                    maximum_compression_pa_by_stage=maxima,
                    no_tension_research_screen=all(
                        v >= inputs["zero_tension_research_limit_pa"]
                        for v in minima.values()
                    ),
                    known_concrete_plus_strand_mass_kg=mass,
                    handling_equivalent_kg_lower_bound=(mass + a["rigging_mass_kg"])
                    * a["lifting_dynamic_factor"],
                    other_reinforcement_mass_kg=None,
                    release=False,
                )
            )
        alternatives.append(
            dict(
                id=layout["id"],
                rows=rows,
                strands=count,
                initial_force_n=count
                * a["strand_area_m2"]
                * a["strand_initial_stress_pa"],
                scenarios=scenarios,
            )
        )
    if len({r["id"] for r in alternatives}) != len(alternatives):
        raise ValueError("unique prestress layout identities required")
    candidate = next(r for r in alternatives if r["id"] == inputs["candidate_id"])
    return dict(
        alternatives=alternatives,
        candidate_id=candidate["id"],
        scope="Gross prismatic section at full-force stations, including end-fill gravity patches and known strand displacement. Full force extrapolated to ends is a diagnostic; actual transmission/end-zone behaviour is unresolved.",
        transfer_length_qualified=False,
        material_stress_limits_qualified=False,
        railway_live_load_qualified=False,
        compression_positive=True,
        physical_release=False,
        open=[
            "Zero tension is a research screen, not an adopted design criterion; concrete compression limits unknown",
            "Transfer length, bond, local end stresses, bursting, bearing/insert zones and actual end-section stiffness need separate design",
            "Gross prismatic elastic shortening with local gravity moment is an idealisation; no measured total loss or nonlinear cracking model",
            "Additional reinforcement, equipment/track/railway loads, fatigue, shear, deflection and concrete transfer strength remain open",
        ],
    )


def column_system(length, E, I, elements, springs):
    """Pinned Euler-Bernoulli beam-column with nodal ground springs; SI matrices."""
    L = positive(length, "length")
    EI = positive(E, "E") * positive(I, "I")
    if type(elements) is not int or elements < 2:
        raise ValueError("at least two finite elements required")
    h = L / elements
    K = np.zeros((2 * (elements + 1),) * 2)
    Kg = np.zeros_like(K)
    ke = (
        EI
        / h**3
        * np.array(
            [
                [12, 6 * h, -12, 6 * h],
                [6 * h, 4 * h * h, -6 * h, 2 * h * h],
                [-12, -6 * h, 12, -6 * h],
                [6 * h, 2 * h * h, -6 * h, 4 * h * h],
            ]
        )
    )
    ge = (
        1
        / (30 * h)
        * np.array(
            [
                [36, 3 * h, -36, 3 * h],
                [3 * h, 4 * h * h, -3 * h, -h * h],
                [-36, -3 * h, 36, -3 * h],
                [3 * h, -h * h, -3 * h, 4 * h * h],
            ]
        )
    )
    for j in range(elements):
        ids = np.arange(2 * j, 2 * j + 4)
        K[np.ix_(ids, ids)] += ke
        Kg[np.ix_(ids, ids)] += ge
    for x, k in springs:
        if not 0 < x < L or not math.isfinite(k) or k < 0:
            raise ValueError("nonnegative finite interior spring required")
        node = round(x / h)
        if abs(node * h - x) > 1e-9:
            raise ValueError("spring must coincide with actual FE node")
        K[2 * node, 2 * node] += k
    free = [j for j in range(len(K)) if j not in (0, 2 * elements)]
    return K, Kg, free, np.linspace(0, L, elements + 1)


def column_buckling(length, E, I, elements, springs):
    """(K + Kspring) v = Pcr Kg v; springs restrain absolute common sway."""
    K, Kg, free, _ = column_system(length, E, I, elements, springs)
    eigen = eigvalsh(
        K[np.ix_(free, free)], Kg[np.ix_(free, free)], subset_by_index=[0, 0]
    )[0]
    return float(eigen)


def imperfect_column(length, E, I, elements, springs, force, bow):
    """Incremental second-order sway from stress-free sinusoidal bow.

    Springs start unstressed at the unloaded crooked position. Physical bow,
    installation/preload and anchorage stiffness need measurement.
    """
    for name, value in (("axial force", force), ("initial bow", bow)):
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError("finite nonnegative " + name + " required")
    critical = column_buckling(length, E, I, elements, springs)
    if force >= critical:
        return dict(
            stable_elastic_tangent=False, additional_sway_m=None, brace_reactions=None
        )
    K, Kg, free, x = column_system(length, E, I, elements, springs)
    initial = np.zeros(len(K))
    initial[0::2] = bow * np.sin(math.pi * x / length)
    initial[1::2] = bow * math.pi / length * np.cos(math.pi * x / length)
    rhs = force * Kg @ initial
    delta = np.zeros(len(K))
    delta[free] = np.linalg.solve((K - force * Kg)[np.ix_(free, free)], rhs[free])
    residual = (K - force * Kg) @ delta - rhs
    reactions = [
        dict(
            x_m=station,
            spring_n_m=k,
            force_n=k * delta[2 * round(station / (length / elements))],
        )
        for station, k in springs
    ]
    return dict(
        stable_elastic_tangent=True,
        additional_sway_m=float(max(abs(delta[0::2]))),
        brace_reactions=reactions,
        free_force_residual_n=float(max(abs(residual[j]) for j in free if j % 2 == 0)),
        free_moment_residual_nm=float(
            max(abs(residual[j]) for j in free if j % 2 == 1)
        ),
        maximum_abs_brace_force_n=max(
            (abs(r["force_n"]) for r in reactions), default=0
        ),
    )


def bed_restraint(a, inputs, section, initial_force):
    E = a["steel_elastic_modulus_pa"]
    I = section["weak_inertia_m4"]
    L = inputs["active_length_m"]
    origin = inputs["origin_x_m"]
    spring_stations = [x - origin for x in inputs["brace_stations_m"]]
    force = initial_force / 2
    if inputs["proposed_spring_n_m"] not in inputs["spring_stiffness_cases_n_m"]:
        raise ValueError("proposed spring must have an analysed case")
    cases = []
    for k in inputs["spring_stiffness_cases_n_m"]:
        critical = column_buckling(
            L, E, I, inputs["elements"], [(x, k) for x in spring_stations]
        )
        cases.append(
            dict(
                spring_n_m=k,
                critical_force_per_side_n=critical,
                elastic_load_factor=critical / force,
                imperfect_response=imperfect_column(
                    L,
                    E,
                    I,
                    inputs["elements"],
                    [(x, k) for x in spring_stations],
                    force,
                    inputs["initial_sway_m"],
                ),
                stiffness_measured=False,
                resistance_qualified=False,
            )
        )
    for case in cases:
        for row in case["imperfect_response"].get("brace_reactions") or []:
            row["global_x_m"] = origin + row["x_m"]
    return dict(
        assumed_pinned_end_planes_x_m=[origin, origin + L],
        active_length_m=L,
        initial_stressing_force_n=initial_force,
        force_each_side_n=force,
        cases=cases,
        proposed_spring_n_m=inputs["proposed_spring_n_m"],
        common_sway_with_cross_ties_only_critical_n=column_buckling(
            L, E, I, inputs["elements"], []
        ),
        requirement="Provide an absolute lateral restraint load path in BOTH buckling planes; transverse ties alone leave the common-sway mode unrestrained",
        brace_response_basis="Linearised second-order response about a stress-free sinusoidal bow with initially unstressed springs; this is not a qualified brace force or capacity",
        foundation_stiffness_measured_n_m=inputs["foundation_stiffness_measured_n_m"],
        nominal_side_box_axial_demand_pa=force / (0.5 * 0.3 - 0.468 * 0.268),
        strongback_in_plane_moment_demand_nm=force * (1.85 - 0.7175),
        strongback_resistance=None,
        initial_bow_basis="Sinusoidal 10 mm research bow; springs unstressed in that initial shape. No fabrication tolerance or brace design criterion adopted.",
        physical_release=False,
    )


def runway(a, inputs):
    for key, value in inputs.items():
        if isinstance(value, (int, float)):
            positive(value, key)
    span = inputs["bridge_span_m"]
    approach = inputs["crab_approach_m"]
    if not 0 < approach < span / 2 or inputs["wheels_per_runway"] != 2:
        raise ValueError("two-wheel runway and interior crab approach required")
    Q = (
        inputs["rated_lift_kg"] * inputs["vertical_lift_factor"]
        + inputs["crab_mass_kg"]
    ) * G
    bridge = inputs["bridge_mass_kg"] * G
    near = Q * (span - approach) / span + bridge / 2
    far = Q * approach / span + bridge / 2
    wheels = [near / 2, far / 2]
    d, b, t, tw = (
        inputs[k]
        for k in (
            "girder_depth_m",
            "flange_width_m",
            "flange_thickness_m",
            "web_thickness_m",
        )
    )
    if min(d - 2 * t, b - tw) <= 0:
        raise ValueError("positive web height and clear flange width required")
    I = (b * d**3 - (b - tw) * (d - 2 * t) ** 3) / 12
    A = 2 * b * t + tw * (d - 2 * t)
    L = inputs["bay_span_m"]
    worst_moment = worst_delta = worst_support = 0
    worst_positions = []
    # Travel the larger rail's two equal wheel loads over one simply supported bay.
    for j in range(301):
        offset = -inputs["wheelbase_m"] + (L + inputs["wheelbase_m"]) * j / 300
        positions = [offset, offset + inputs["wheelbase_m"]]
        loads = [(x, wheels[0]) for x in positions if 0 <= x <= L]
        if not loads:
            continue
        r = point_beam(L, loads, a["steel_elastic_modulus_pa"], I, samples=101)
        if r["maximum_abs_moment_nm"] > worst_moment:
            worst_moment = r["maximum_abs_moment_nm"]
            worst_positions = positions
        worst_delta = max(worst_delta, r["maximum_abs_deflection_m"])
        worst_support = max(worst_support, r["left_reaction_n"], r["right_reaction_n"])
    q = A * a["steel_density_kg_m3"] * G
    moment = worst_moment + q * L * L / 8
    delta = worst_delta + 5 * q * L**4 / (384 * a["steel_elastic_modulus_pa"] * I)
    column_dead = 0.6**2 - (0.6 - 0.05) ** 2
    column_weight = (
        (column_dead * 8.95 + 0.9 * 0.9 * 0.05) * a["steel_density_kg_m3"] * G
    )
    # A column supports two adjacent bays; summing independent support maxima is a conservative scenario envelope.
    support = 2 * (worst_support + q * L / 2) + column_weight
    pad = inputs["pad_reservation_m"]
    pad_weight = math.prod(pad) * pi.CONCRETE_DENSITY_KG_PER_M3 * G
    return dict(
        assumed_configuration=inputs,
        near_rail_vertical_n=near,
        far_rail_vertical_n=far,
        near_wheel_n=wheels[0],
        far_wheel_n=wheels[1],
        vertical_sum_n=near + far,
        rated_lift_basis=True,
        supplier_reactions_confirmed=False,
        gross_girder_area_m2=A,
        gross_girder_inertia_m4=I,
        wheel_travel_moment_max_positions_m=worst_positions,
        gravity_moment_envelope_nm=moment,
        nominal_bending_demand_pa=moment * d / 2 / I,
        sampled_elastic_deflection_envelope_m=delta,
        research_deflection_limit_m=L / inputs["research_deflection_span_divisor"],
        two_adjacent_bays_column_gravity_envelope_n=support,
        horizontal_transverse_interface_n=inputs["horizontal_transverse_fraction"] * Q,
        horizontal_column_base_moment_scenario_nm=inputs[
            "horizontal_transverse_fraction"
        ]
        * Q
        * 9,
        pad_average_gravity_pressure_scenario_pa=(support + pad_weight)
        / (pad[0] * pad[1]),
        pad_resistance_established=False,
        open=[
            "Masses, dynamic factor, wheel count/spacing and approach are OSR scenarios, not Street configuration data",
            "Runway stress/deflection are gross elastic demands: wheel contact/web patch/local buckling, lateral stability, torsion, weld fatigue, rail clips and end stops remain open",
            "Nominal 2.5 m pads are CAD reservations; pressure excludes eccentricity, uplift, seismic, adjacent foundations and actual ground capacity",
            "Horizontal action is a separate assumed interface scenario; no project load combination or base stiffness adopted",
            "Rail, clips, stiffeners and connections are not included in the stated girder/column dead-load takeoff; final dead loads unknown",
            "Adjacent-bay gravity envelope sums incompatible independent maxima conservatively; not a final column reaction",
        ],
        physical_release=False,
    )


def workholding_parts(fix, inputs):
    parts = deepcopy(fix["parts"])
    for i, (x, sign) in enumerate(((-0.5, -1), (0.5, -1), (0, 1))):
        plate_y = -0.6 if sign < 0 else 0.4
        parts.append(
            part(
                f"clamp-mount-plate-{i+1}",
                [0.18, 0.2, 0.02],
                [x - 0.09, plate_y, 0.8],
                role="clamp-mount-concept",
            )
        )
        size = inputs["clamp_envelope_allowance_m"]
        parts.append(
            part(
                f"brauer-clamp-reservation-{i+1}",
                size,
                [x - size[0] / 2, -0.75 if sign < 0 else 0.25, 0.82],
                role="equipment-envelope",
                equipment_id=inputs["clamp_model"],
                basis="OSR operation/clearance reservation, not manufacturer external dimensions; mounting/spindle height and holes require GA",
            )
        )
    return parts


def revised_bed_parts(original, layout, bed_inputs):
    parts = [deepcopy(p) for p in original if p["role"] != "strand-envelope"]
    for row, (z, count) in enumerate(layout["rows"]):
        each = count // 2
        for stem in (-0.7175, 0.7175):
            for col in range(each):
                y = stem + (col - (each - 1) / 2) * 0.045
                parts.append(
                    part(
                        f"revised-strand-{row}-{stem}-{col}",
                        [0.015, 0.015, 26],
                        [-0.5, y - 0.0075, 0.8 + z - 0.0075],
                        kind="cylinder",
                        cylinder_axis="x",
                        role="strand-envelope",
                    )
                )
    for x in bed_inputs["brace_stations_m"]:
        for y in (-1.85, 1.85):
            # Separate ground pads represent required restraint interfaces, not designed foundations.
            parts.append(
                part(
                    f"restraint-pad-{x}-{y}",
                    [0.8, 0.8, 0.4],
                    [x - 0.4, y - 0.4, -0.4],
                    role="foundation-reservation",
                )
            )
            parts.append(
                part(
                    f"restraint-stool-{x}-{y}",
                    [0.2, 0.5, 0.25],
                    [x - 0.1, y - 0.25, 0],
                    role="restraint-interface",
                )
            )
    return parts


def runway_parts(inputs):
    L = inputs["bay_span_m"]
    span = inputs["bridge_span_m"]
    d, b, t, tw = (
        inputs[k]
        for k in (
            "girder_depth_m",
            "flange_width_m",
            "flange_thickness_m",
            "web_thickness_m",
        )
    )
    parts = []
    for y in (0, span):
        for label, z in (("bottom", 9), ("top", 9 + d - t)):
            parts.append(
                part(
                    f"girder-{y}-{label}",
                    [L, b, t],
                    [0, y - b / 2, z],
                    role="runway-girder-concept",
                )
            )
        parts.append(
            part(
                f"girder-{y}-web",
                [L, tw, d - 2 * t],
                [0, y - tw / 2, 9 + t],
                role="runway-girder-concept",
            )
        )
        parts.append(
            part(
                f"rail-reservation-{y}",
                [L, 0.1, 0.1],
                [0, y - 0.05, 9 + d],
                role="rail-reservation",
            )
        )
        for x in (0, L):
            parts.append(
                part(
                    f"runway-column-{x}-{y}",
                    [0.6, 0.6, 8.95],
                    [x - 0.3, y - 0.3, 0.05],
                    kind="tube",
                    axis=2,
                    wall_m=0.025,
                    role="runway-column-concept",
                )
            )
            parts.append(
                part(
                    f"runway-baseplate-{x}-{y}",
                    [0.9, 0.9, 0.05],
                    [x - 0.45, y - 0.45, 0],
                    role="baseplate-concept",
                )
            )
            px, py, pz = inputs["pad_reservation_m"]
            parts.append(
                part(
                    f"runway-pad-{x}-{y}",
                    [px, py, pz],
                    [x - px / 2, y - py / 2, -pz],
                    role="foundation-reservation",
                )
            )
    return parts


def build(a, inputs, fix, civil, equipment):
    import sys
    import scipy
    import matplotlib

    prestress = prestress_alternatives(a, inputs["prestress"], civil["section"])
    candidate = next(
        r for r in prestress["alternatives"] if r["id"] == prestress["candidate_id"]
    )
    bed = bed_restraint(
        a, inputs["bed"], civil["bed_screen"], candidate["initial_force_n"]
    )
    strand_z = sum(z * n for z, n in candidate["rows"]) / candidate["strands"] + 0.8
    bed["tendon_centroid_z_m"] = strand_z
    bed["return_box_centroid_z_m"] = 0.5
    bed["end_vertical_eccentric_couple_nm"] = candidate["initial_force_n"] * (
        strand_z - 0.5
    )
    runway_report = runway(a, inputs["runway"])
    machine = equipment["mazak-cv5-500"]["published"]
    plate_mass = 0.9 * 0.9 * 0.05 * a["steel_density_kg_m3"]
    runway_report["manufacturing_interfaces"] = dict(
        baseplate_blank_m=[0.9, 0.9, 0.05],
        baseplate_nominal_mass_kg=plate_mass,
        baseplate_cv5_diameter_screen=math.hypot(0.9, 0.9)
        <= machine["workpiece_diameter_m"],
        baseplate_cv5_mass_screen=plate_mass <= machine["workpiece_kg"],
        baseplate_cv5_height_screen=0.05 <= machine["workpiece_height_m"],
        route="Baseplate drilling/machining and long-girder fabrication require an additional qualified route; the pilot CV5 cell does not cover them",
        fabrication_supplier_selected=False,
    )
    return dict(
        schema="osr-factory-development-iteration/2",
        revision=inputs["revision"],
        numerical_toolchain=dict(
            python=sys.version.split()[0],
            numpy=np.__version__,
            scipy=scipy.__version__,
            matplotlib=matplotlib.__version__,
        ),
        basis=inputs,
        workholding=workholding(
            a, inputs["fixture"], fix, equipment[inputs["fixture"]["clamp_model"]]
        ),
        prestress=prestress,
        bed=bed,
        runway=runway_report,
        physical_release=False,
    )

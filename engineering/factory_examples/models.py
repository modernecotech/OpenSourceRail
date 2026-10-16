"""SI development geometry, analytical demand screens and factory reservations.

Primitives are OSR solids or external envelopes, never manufacturer internals.
Numerical demand is deliberately separate from unestablished design resistance.
"""

from __future__ import annotations

import math
from pathlib import Path
import tomllib

import numpy as np

from engineering.industrialisation.assembly import fixture_constraints
from engineering.design_engine.civil_qualification import elastic_shortening
from osr_mech.civil import decked_pi as pi


def positive(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name}: finite positive number required")
    return float(value)


def part(identifier, size, at, *, kind="box", role="design-solid", **kw):
    for x in size:
        positive(x, identifier)
    if len(size) != 3 or len(at) != 3 or not all(math.isfinite(x) for x in at):
        raise ValueError("three-dimensional geometry required")
    return dict(
        id=identifier, kind=kind, size_m=list(size), at_m=list(at), role=role, **kw
    )


def volume(p):
    if p["kind"] not in {"box", "tube", "cylinder", "stepped-cylinder"}:
        raise ValueError("unsupported factory solid primitive")
    x, y, z = p["size_m"]
    result = x * y * z
    if p["kind"] == "tube":
        axis, wall = p["axis"], p["wall_m"]
        positive(wall, "wall")
        inner = list(p["size_m"])
        for j in range(3):
            if j != axis:
                inner[j] -= 2 * wall
                positive(inner[j], "tube bore")
        result -= math.prod(inner)
    elif p["kind"] == "cylinder":
        result = math.pi * x * y * z / 4
    elif p["kind"] == "stepped-cylinder":
        if abs(sum(s["length_m"] for s in p["steps"]) - z) > 1e-10:
            raise ValueError("step lengths must cover declared cylinder height")
        result = sum(
            math.pi * s["diameter_m"] ** 2 / 4 * s["length_m"] for s in p["steps"]
        )
    for h in p.get("holes", []):
        result -= (
            math.pi
            * h["diameter_m"] ** 2
            / 4
            * h.get("length_m", p["size_m"]["xyz".index(h.get("axis", "z"))])
        )
    return result


def global_size(p):
    size = list(p["size_m"])
    if p["kind"] == "cylinder":
        size = [p["size_m"][0]] * 3
        size["xyz".index(p.get("cylinder_axis", "z"))] = p["size_m"][2]
    return size


def bounds(parts):
    low = [min(p["at_m"][j] for p in parts) for j in range(3)]
    high = [max(p["at_m"][j] + global_size(p)[j] for p in parts) for j in range(3)]
    return low + high


def point_beam(length, loads, modulus, inertia, *, samples=301):
    """Simply supported beam, exact point-load deflection; sampled extrema.

    Loads are (distance from left support [m], downward force [N]).
    Superposition includes signed forces; no span end fixity is implied.
    """
    L = positive(length, "span")
    EI = positive(modulus, "modulus") * positive(inertia, "inertia")
    if not loads or any(not 0 <= a <= L or not math.isfinite(p) for a, p in loads):
        raise ValueError("finite loads within span required")
    left = sum(p * (L - a) / L for a, p in loads)
    right = sum(p * a / L for a, p in loads)
    positions = sorted(
        set([L * i / (samples - 1) for i in range(samples)] + [a for a, _ in loads])
    )
    bending, deflections = [], []
    for x in positions:
        bending.append(left * x - sum(p * max(x - a, 0) for a, p in loads))
        delta = 0
        for a, force in loads:
            b = L - a
            if x <= a:
                delta += force * b * x * (L * L - b * b - x * x) / (6 * L * EI)
            else:
                delta += (
                    force * a * (L - x) * (L * L - a * a - (L - x) ** 2) / (6 * L * EI)
                )
        deflections.append(delta)
    return dict(
        left_reaction_n=left,
        right_reaction_n=right,
        maximum_abs_moment_nm=max(map(abs, bending)),
        maximum_abs_deflection_m=max(map(abs, deflections)),
        extremum_sampling_points=len(positions),
    )


def fixture(a):
    """Welded datum bench: cut stock, drilled mounting plates and six locators."""
    solids = []

    def tube(identifier, size, at, axis):
        solids.append(part(identifier, size, at, kind="tube", axis=axis, wall_m=0.005))

    for y in (-0.475, 0.475):
        tube(f"longitudinal-{y}", [1.6, 0.05, 0.1], [-0.8, y - 0.025, 0.7], 0)
    for x in (-0.5, 0, 0.5, 0.775):
        tube(f"crossrail-{x}", [0.05, 0.9, 0.1], [x - 0.025, -0.45, 0.7], 1)
    for x in (-0.75, 0.75):
        for y in (-0.475, 0.475):
            tube(f"leg-{x}-{y}", [0.1, 0.05, 0.68], [x - 0.05, y - 0.025, 0.02], 2)
            holes = [
                dict(x_m=dx, y_m=dy, diameter_m=0.018)
                for dx in (0.04, 0.16)
                for dy in (0.035, 0.125)
            ]
            solids.append(
                part(
                    f"foot-{x}-{y}",
                    [0.2, 0.16, 0.02],
                    [x - 0.1, y - 0.08, 0],
                    holes=holes,
                )
            )
    locator_points = [
        [-0.5, -0.25, 0.84],
        [0.5, -0.25, 0.84],
        [0, 0.25, 0.84],
        [-0.45, 0.4, 0.95],
        [0.45, 0.4, 0.95],
        [0.7, 0, 0.95],
    ]
    for i, (x, y, _) in enumerate(locator_points[:3]):
        solids.append(
            part(
                f"datum-plate-{i+1}",
                [0.18, 0.12, 0.02],
                [x - 0.09, y - 0.06, 0.8],
                holes=[dict(x_m=0.09, y_m=0.06, diameter_m=0.02)],
            )
        )
        solids.append(
            part(
                f"vertical-locator-{i+1}",
                [0.02, 0.02, 0.04],
                [x - 0.01, y - 0.01, 0.8],
                kind="cylinder",
            )
        )
    for i, x in enumerate((-0.45, 0.45)):
        solids.append(
            part(
                f"side-upright-{i+1}",
                [0.12, 0.02, 0.25],
                [x - 0.06, 0.465, 0.8],
                role="welded-locator-mount",
            )
        )
        # Horizontal pins have an explicit rotation from the cylinder's local z axis.
        solids.append(
            part(
                f"side-locator-{i+1}",
                [0.02, 0.02, 0.065],
                [x - 0.01, 0.4, 0.94],
                kind="cylinder",
                cylinder_axis="y",
            )
        )
    solids.append(
        part(
            "end-upright",
            [0.02, 0.12, 0.25],
            [0.765, -0.06, 0.8],
            role="welded-locator-mount",
        )
    )
    solids.append(
        part(
            "end-locator",
            [0.02, 0.02, 0.065],
            [0.7, -0.01, 0.94],
            kind="cylinder",
            cylinder_axis="x",
        )
    )
    mass = sum(volume(p) for p in solids) * a["steel_density_kg_m3"]
    payload = (
        positive(a["fixture_payload_kg"], "payload")
        * 9.80665
        * positive(a["fixture_load_factor"], "factor")
    )
    xy = a["fixture_payload_cg_xy_m"]
    reaction_matrix = np.array([[1, 1, 1], [-0.5, 0.5, 0], [-0.25, -0.25, 0.25]])
    reactions = np.linalg.solve(
        reaction_matrix, [payload, payload * xy[0], payload * xy[1]]
    )
    # Nominal sharp-corner 100 high x 50 wide x 5 wall RHS; actual corner properties unresolved.
    I = (0.05 * 0.1**3 - 0.04 * 0.09**3) / 12
    cross, transfers = [], [[], []]
    for x, y, force in zip((-0.5, 0.5, 0), (-0.25, -0.25, 0.25), reactions):
        check = point_beam(
            0.95, [(y + 0.475, float(force))], a["steel_elastic_modulus_pa"], I
        )
        cross.append(check)
        transfers[0].append((x + 0.75, check["left_reaction_n"]))
        transfers[1].append((x + 0.75, check["right_reaction_n"]))
    long = [point_beam(1.5, row, a["steel_elastic_modulus_pa"], I) for row in transfers]
    # Support-to-ground compliance adds at crossrail ends; conservative sum of maxima.
    delta = max(r["maximum_abs_deflection_m"] for r in cross) + max(
        r["maximum_abs_deflection_m"] for r in long
    )
    return dict(
        id="OSR-FIX-500",
        parts=solids,
        mass_kg=mass,
        geometry_basis="Nominal sharp-corner RHS; rounded mill sections, welds and fasteners not represented",
        payload_demand_n=payload,
        vertical_reactions_n=reactions.tolist(),
        payload_cg_within_support_triangle=bool(min(reactions) >= 0),
        nominal_rhs_inertia_m4=I,
        crossrail_screens=cross,
        longitudinal_screens=long,
        payload_only_combined_deflection_bound_m=delta,
        provisional_deflection_review_limit_m=a["fixture_deflection_review_limit_m"],
        payload_only_below_review_limit=delta <= a["fixture_deflection_review_limit_m"],
        restraint=fixture_constraints(
            locator_points, [[0, 0, 1]] * 3 + [[0, -1, 0]] * 2 + [[-1, 0, 0]]
        ),
        open=[
            "No clamps selected; unilateral locator separation under reversed loads remains open",
            "Payload-only beam bending omits frame self-weight, torsion, weld flexibility, local walls and lateral loads",
            "Nominal geometry mass is a stock estimate, not certified purchased mass",
            "Pin fits, hardness, shims, weld size/procedure, residual distortion and anchor design unqualified",
            "Vertical locator through-holes need retention; side/end pins need removable mount detail",
            "Survey complete assembly separately; part CMM cannot contain full fixture",
        ],
        released=False,
    )


def civil(a):
    w, tf, sw, sh = (
        pi.DECK_WIDTH_MM / 1000,
        pi.FLANGE_THICKNESS_MM / 1000,
        pi.STEM_WIDTH_MM / 1000,
        pi.STEM_DEPTH_MM / 1000,
    )
    A = pi.section_area_m2()
    rectangles = [(w, tf, sh + tf / 2), (sw, sh, sh / 2), (sw, sh, sh / 2)]
    centroid = sum(b * h * z for b, h, z in rectangles) / A
    I = sum(b * h**3 / 12 + b * h * (z - centroid) ** 2 for b, h, z in rectangles)
    levels = [0.1, 0.16, 0.22, 0.28]
    groups = [
        dict(
            metallic_area_m2=10 * a["strand_area_m2"],
            pretransfer_stress_pa=a["strand_initial_stress_pa"],
            steel_modulus_pa=a["strand_modulus_pa"],
            eccentricity_m=centroid - z,
        )
        for z in levels
    ]
    initial_force = sum(
        g["metallic_area_m2"] * g["pretransfer_stress_pa"] for g in groups
    )
    scenarios = []
    diaphragm_extra = (w - 2 * sw) * sh * 2 * pi.END_DIAPHRAGM_LENGTH_MM / 1000
    for L in pi.CATALOGUE_SPANS_M:
        mass = pi.approx_mass_kg(L)
        q = mass / L * 9.80665
        M = q * L * L / 8
        losses = elastic_shortening(
            groups,
            area_m2=A,
            inertia_m4=I,
            concrete_modulus_pa=a["concrete_transfer_modulus_pa"],
            self_weight_moment_nm=M,
        )
        transfer = sum(
            g["metallic_area_m2"] * (g["pretransfer_stress_pa"] - loss)
            for g, loss in zip(groups, losses)
        )
        transfer_moment = sum(
            g["metallic_area_m2"]
            * (g["pretransfer_stress_pa"] - loss)
            * g["eccentricity_m"]
            for g, loss in zip(groups, losses)
        )

        def fiber_stress(force, prestress_moment):
            # Compression positive; positive gravity moment puts soffit in tension.
            net = prestress_moment - M
            return dict(
                soffit_pa=force / A + net * centroid / I,
                top_pa=force / A - net * (sh + tf - centroid) / I,
                compression_positive=True,
                allowable_stress_pa=None,
            )

        service_moment = sum(
            g["metallic_area_m2"]
            * (g["pretransfer_stress_pa"] - loss)
            * (1 - a["additional_prestress_loss_fraction"])
            * g["eccentricity_m"]
            for g, loss in zip(groups, losses)
        )
        E = a["concrete_service_modulus_pa"]
        dead_delta = 5 * q * L**4 / (384 * E * I)
        camber = service_moment * L * L / (8 * E * I)
        developed_mass = mass + diaphragm_extra * pi.CONCRETE_DENSITY_KG_PER_M3
        handling = (developed_mass + a["rigging_mass_kg"]) * a["lifting_dynamic_factor"]
        scenarios.append(
            dict(
                span_m=L,
                bare_volume_m3=A * L,
                bare_mass_kg=mass,
                optional_solid_end_diaphragms_extra_m3=diaphragm_extra,
                developed_mass_kg=developed_mass,
                bare_dead_load_n_m=q,
                bare_dead_moment_nm=M,
                bare_dead_elastic_deflection_m=dead_delta,
                elastic_shortening_loss_pa=losses,
                transfer_force_n=transfer,
                transfer_prestress_moment_nm=transfer_moment,
                transfer_fiber_stress=fiber_stress(transfer, transfer_moment),
                hypothetical_service_fiber_stress=fiber_stress(
                    transfer * (1 - a["additional_prestress_loss_fraction"]),
                    service_moment,
                ),
                assumed_additional_loss_fraction=a[
                    "additional_prestress_loss_fraction"
                ],
                hypothetical_service_camber_m=camber,
                hypothetical_dead_minus_camber_m=dead_delta - camber,
                handling_equivalent_kg=handling,
                eighty_tonne_screen=handling <= 80000,
                requested_125_tonne_screen=handling <= 125000,
                one_m3_batches_lower_bound=math.ceil((A * L + diaphragm_extra) / 1),
                railway_live_load_result=None,
            )
        )
    # Two idealised fabricated 500x300x16 boxes share initial stressing force.
    box_area = 0.5 * 0.3 - (0.5 - 0.032) * (0.3 - 0.032)
    weak_I = (0.5 * 0.3**3 - (0.5 - 0.032) * (0.3 - 0.032) ** 3) / 12
    force_each = initial_force / 2
    euler = {
        str(L): math.pi**2 * a["steel_elastic_modulus_pa"] * weak_I / L**2
        for L in (25, 3)
    }
    return dict(
        section=dict(
            area_m2=A, centroid_z_m=centroid, inertia_x_m4=I, depth_m=sh + tf, width_m=w
        ),
        scenarios=scenarios,
        prestress_hypothesis=dict(
            strands=40,
            levels_z_m=levels,
            strands_per_stem_per_level=5,
            group_inputs=groups,
            initial_force_n=initial_force,
            initial_force_per_strand_n=initial_force / 40,
            ccl_246kn_scalar_demand_screen=initial_force / 40 <= 246000,
            exact_strand_grip_compatibility=None,
        ),
        bed_screen=dict(
            side_box_mm=[500, 300, 16],
            force_per_side_n=force_each,
            axial_demand_pa=force_each / box_area,
            weak_inertia_m4=weak_I,
            euler_pinned_force_n_by_unbraced_length_m=euler,
            full_25m_euler_ratio=force_each / euler["25"],
            assumed_3m_braced_euler_ratio=force_each / euler["3"],
            brace_capacity_established=False,
            foundation_resistance=None,
        ),
        open=[
            "Solid end diaphragms are a new geometry hypothesis; canonical zones do not establish this concrete design",
            "Prestress screen uses bare prismatic section and self-weight only; it omits local diaphragm stiffness/weight effects",
            "No railway live-load model adopted here; this is not a railway beam acceptance calculation",
            "Hypothetical 40-strand layout needs cover, spacing, release strength, stress, cracking, shear and fatigue checks",
            "Additional 20% loss is a research scenario after elastic shortening, not a measured total loss",
            "Euler is ideal elastic pinned screening; brace forces, restraints, imperfections and bed abutments unqualified",
            "Crane scalar capacity screen excludes lifting insert, rigging geometry, eccentricity, stability and runway resistance",
        ],
        released=False,
    )


def pi_parts(span=25, *, offset=(0, 0, 0), developed=True):
    x, y, z = offset
    parts = [part("flange", [span, 2.9, 0.22], [x, y - 1.45, z + 0.935])]
    for j, sy in enumerate((-0.7175, 0.7175)):
        parts.append(part(f"stem-{j}", [span, 0.3, 0.935], [x, y + sy - 0.15, z]))
    if developed:
        # Only fill the gaps between/outside stems; no double-counted overlaps.
        intervals = [(-1.45, -0.8675), (-0.5675, 0.5675), (0.8675, 1.45)]
        for end in (0, span - 0.55):
            for j, (lo, hi) in enumerate(intervals):
                parts.append(
                    part(
                        f"diaphragm-fill-{end}-{j}",
                        [0.55, hi - lo, 0.935],
                        [x + end, y + lo, z],
                    )
                )
    return parts


def mould_bed():
    parts = pi_parts(offset=(0, 0, 0.8))
    for p in parts:
        p["role"] = "concrete-hypothesis"
    # Flat soffit and sides: only coordination surfaces, deliberately open stem pockets.
    for y in (-0.7175, 0.7175):
        parts.append(
            part(
                f"stem-soffit-{y}",
                [25, 0.34, 0.012],
                [0, y - 0.17, 0.788],
                role="mould-concept",
            )
        )
        for sign in (-1, 1):
            yy = y + sign * 0.15
            parts.append(
                part(
                    f"stem-face-{y}-{sign}",
                    [25, 0.01, 0.935],
                    [0, yy - (0.01 if sign < 0 else 0), 0.8],
                    role="mould-concept",
                )
            )
    for i, (lo, hi) in enumerate([(-1.45, -0.8675), (-0.5675, 0.5675), (0.8675, 1.45)]):
        parts.append(
            part(
                f"flange-soffit-{i}",
                [23.9, hi - lo, 0.012],
                [0.55, lo, 1.723],
                role="mould-concept",
            )
        )
    for y in (-1.46, 1.45):
        parts.append(
            part(
                f"flange-edge-{y}",
                [25, 0.01, 0.22],
                [0, y, 1.735],
                role="mould-concept",
            )
        )
    for y in (-2, 1.7):
        parts.append(
            part(
                f"bed-side-{y}",
                [27, 0.3, 0.5],
                [-1, y, 0.25],
                kind="tube",
                axis=0,
                wall_m=0.016,
                role="bed-concept",
            )
        )
    for x in range(0, 26, 3):
        parts.append(
            part(
                f"bed-tie-{x}",
                [0.2, 4, 0.15],
                [x - 0.1, -2, 0.1],
                role="unqualified-brace",
            )
        )
    for x in (-1, 25.5):
        parts.append(
            part(
                f"strongback-{x}",
                [0.5, 4, 1.8],
                [x, -2, 0.1],
                role="abutment-reservation",
            )
        )
    # Tendon axes and grip envelopes: not detailed strand/wedge geometry.
    for stem in (-0.7175, 0.7175):
        for row, z in enumerate((0.1, 0.16, 0.22, 0.28)):
            for col in range(5):
                y = stem + (col - 2) * 0.045
                parts.append(
                    part(
                        f"strand-axis-{stem}-{row}-{col}",
                        [0.015, 0.015, 26],
                        [-0.5, y - 0.0075, z + 0.8 - 0.0075],
                        kind="cylinder",
                        cylinder_axis="x",
                        role="strand-envelope",
                    )
                )
    return parts


def overlaps(a, b):
    return all(
        min(a[i] + a[i + 2], b[i] + b[i + 2]) - max(a[i], b[i]) > 1e-8 for i in (0, 1)
    )


def check_layout(layout):
    W, H = layout["size_m"]
    rows = layout["zones"]
    errors = []
    if len({r["id"] for r in rows}) != len(rows):
        errors.append("duplicate zone identity")
    for i, row in enumerate(rows):
        x, y, w, h = row["rect_m"]
        if (
            not all(math.isfinite(v) for v in (x, y, w, h))
            or min(w, h) <= 0
            or x < 0
            or y < 0
            or x + w > W
            or y + h > H
        ):
            errors.append("outside/invalid: " + row["id"])
        for other in rows[i + 1 :]:
            if overlaps(row["rect_m"], other["rect_m"]):
                errors.append("overlap: " + row["id"] + " / " + other["id"])
    return dict(
        valid=not errors,
        errors=errors,
        reserved_area_m2=sum(r["rect_m"][2] * r["rect_m"][3] for r in rows),
        qualification="2D reservations only; door sweeps, evacuation, services, fire separation, swept-paths and crane hook coverage need design",
    )


def layouts(root: Path):
    canonical = tomllib.loads((root / "lib/templates/baghdad-factory.toml").read_text())

    # Retain canonical source in publication; exact values are checked by tests.
    def zone(identifier, label, rect, equipment=None):
        return dict(id=identifier, label=label, rect_m=rect, equipment=equipment)

    vehicle = dict(
        id="vehicle-factory",
        size_m=[144, 60],
        zones=[
            zone("assembly", "Six-car assembly lane 135 x 6.5 m", [4, 4, 135, 6.5]),
            zone("transfer", "6 m transport aisle", [0, 12, 144, 6]),
            zone(
                "laser",
                "Photon cutting + laser/filter space",
                [4, 20, 16, 10],
                "esprit-photon-3015",
            ),
            zone("cnc", "CV5-500 machining", [23, 20, 8, 8], "mazak-cv5-500"),
            zone(
                "weld",
                "MULTIMIG fabrication/extraction",
                [34, 20, 8, 8],
                "oxford-multimig-333",
            ),
            zone(
                "metrology",
                "Conditioned Axiom 900 room",
                [46, 20, 8, 8],
                "aberlink-axiom-900",
            ),
            zone(
                "incoming",
                "Incoming / stock / Prosaw-BOMAR saw",
                [58, 20, 24, 12],
                "prosaw-bomar-510",
            ),
            zone(
                "battery", "Imported cells/BMS: pack integration area", [86, 20, 20, 12]
            ),
            zone("qa", "Electrical/pressure/component tests", [110, 20, 28, 12]),
            zone(
                "pedestrian", "3 m protected circulation reservation", [0, 34, 144, 3]
            ),
            zone("resin", "CIJECT pilot resin room", [4, 40, 8, 8], "ciject-1"),
            zone(
                "oven",
                "Bespoke Airflow oven + loading",
                [16, 40, 14, 10],
                "airflow-oven",
            ),
            zone("mould", "Panel mould / layup / trim", [34, 40, 20, 12]),
            zone("finishing", "Finishing / extraction enquiry", [58, 40, 20, 12]),
            zone("mep", "Utility / maintenance / services", [82, 40, 20, 12]),
            zone("staff", "Welfare, engineering and stores", [106, 40, 32, 12]),
        ],
    )
    yard = dict(
        id="precast-yard",
        size_m=[160, 100],
        zones=[
            zone(
                "casting",
                "Four 29 x 8 m casting reservations",
                [4, 4, 60, 18],
                "matravers-pi25",
            ),
            zone(
                "exclusion", "Stressing abutment exclusion reservation", [66, 4, 10, 18]
            ),
            zone(
                "batch",
                "Rapid mixer + batching plant enquiry",
                [80, 4, 16, 14],
                "rapid-planetary",
            ),
            zone(
                "aggregate", "Aggregate bins / silo / loading enquiry", [100, 4, 32, 18]
            ),
            zone("water", "Water conditioning / washout/reclaim", [136, 4, 20, 18]),
            zone("haul", "8 m heavy transport corridor", [0, 26, 160, 8]),
            zone("rebar", "Rebar/strand cut/prepare enquiry", [4, 38, 40, 18]),
            zone(
                "stressing",
                "CCL stressing/calibration station",
                [48, 38, 8, 8],
                "ccl-sla15",
            ),
            zone(
                "mould-care", "Mould maintenance / release-agent bay", [60, 38, 20, 18]
            ),
            zone("lab", "Concrete sampling / curing lab enquiry", [84, 38, 16, 12]),
            zone("stores", "Cement/admixture stores reservation", [104, 38, 24, 18]),
            zone("mep", "Yard utilities and maintenance", [132, 38, 24, 18]),
            zone("transport", "8 m heavy transport corridor", [0, 60, 160, 8]),
            zone(
                "beam-storage", "Four isolated beam storage positions", [4, 72, 112, 20]
            ),
            zone("dispatch", "Heavy trailer loading enquiry", [120, 72, 36, 20]),
        ],
    )
    for layout in (vehicle, yard):
        layout["check"] = check_layout(layout)
        if not layout["check"]["valid"]:
            raise ValueError(layout["check"]["errors"])
    return dict(vehicle=vehicle, precast=yard, canonical_factory=canonical)


def envelope(e):
    pub, plan = e["published"], e["planning"]
    if "dimensions_m" in pub:
        return pub["dimensions_m"], "published external envelope"
    if "dimensions_xy_m" in pub:
        return [
            *pub["dimensions_xy_m"],
            plan["height_m"],
        ], "published floor footprint; assumed height"
    if "diameter_m" in pub:
        return [
            pub["diameter_m"],
            pub["diameter_m"],
            pub["length_m"],
        ], "published grip external envelope"
    if "dimensions_m" in plan:
        return plan["dimensions_m"], "OSR space reservation; supplier GA unknown"
    return None, "stock material, no machine envelope"


def factory_scene(layout, equipment, *, roof_load_pa, slab_thickness):
    W, H = layout["size_m"]
    scene = []
    if layout["id"] == "vehicle-factory":
        scene.append(
            part(
                "slab-reservation",
                [W, H, slab_thickness],
                [0, 0, -slab_thickness],
                role="slab-concept",
            )
        )
        # Separate runway structures remain an enquiry; these are roof-only column/beam concepts.
        for x in range(0, 145, 12):
            for y in (0, 30, 60):
                scene.append(
                    part(
                        f"roof-column-{x}-{y}",
                        [0.3, 0.3, 10],
                        [x - 0.15, y - 0.15, 0],
                        kind="tube",
                        axis=2,
                        wall_m=0.016,
                        role="roof-frame-concept",
                    )
                )
            for y in (0, 30):
                scene.append(
                    part(
                        f"roof-beam-{x}-{y}",
                        [0.25, 30, 0.7],
                        [x - 0.125, y, 10],
                        kind="tube",
                        axis=1,
                        wall_m=0.016,
                        role="roof-frame-concept",
                    )
                )
        roof = dict(
            grid_m=[12, 30],
            roof_dead_load_pa=roof_load_pa,
            typical_interior_column_tributary_m2=360,
            roof_dead_load_only_column_n=roof_load_pa * 360,
            slab_volume_m3=W * H * slab_thickness,
            allowable_ground_bearing_pa=None,
            required_pad_area_m2=None,
            frame_resistance=None,
            crane_runway_design=None,
        )
    else:
        roof = None
        for i, (x, y) in enumerate(((5, 5), (35, 5), (5, 14), (35, 14))):
            scene.append(
                part(
                    f"casting-bed-{i+1}",
                    [27, 4.5, 0.5],
                    [x, y, 0],
                    role="mould-reservation",
                )
            )
            for p in pi_parts(offset=(x + 1, y + 2.25, 0.5)):
                p["id"] = f"cast-{i+1}-" + p["id"]
                p["role"] = "concrete-hypothesis"
                scene.append(p)
        for i in range(4):
            for p in pi_parts(offset=(5 + i * 27.5, 81, 0.5)):
                p["id"] = f"stored-{i+1}-" + p["id"]
                p["role"] = "storage-envelope"
                scene.append(p)
    placements = []
    for zone in layout["zones"]:
        identifier = zone["equipment"]
        if identifier is None or identifier == "matravers-pi25":
            continue
        e = equipment[identifier]
        size, basis = envelope(e)
        if size is None:
            continue
        x, y, w, h = zone["rect_m"]
        if size[0] > w - 1 or size[1] > h - 1:
            raise ValueError("equipment doesn't fit reserved cell: " + identifier)
        machine_x = x + (10 if identifier == "prosaw-bomar-510" else 1)
        scene.append(
            part(
                identifier,
                size,
                [machine_x, y + 1, 0],
                role="supplier-envelope",
                equipment_id=identifier,
                basis=basis,
            )
        )
        placements.append(
            dict(
                id=identifier,
                envelope_basis=basis,
                cell=zone["id"],
                dimensions_m=size,
                margin_xy_m=[w - size[0], h - size[1]],
            )
        )
        if identifier == "esprit-photon-3015":
            scene.append(
                part(
                    "laser-filter-reservation",
                    e["planning"]["auxiliary_reservation_m"],
                    [x + 11.5, y + 1, 0],
                    role="auxiliary-reservation",
                )
            )
        if identifier == "prosaw-bomar-510":
            for suffix, xx in (
                ("infeed", machine_x - 7),
                ("outfeed", machine_x + size[0]),
            ):
                scene.append(
                    part(
                        "saw-" + suffix,
                        [7, 0.6, 0.761],
                        [xx, y + 1.2, 0],
                        role="auxiliary-reservation",
                        basis="OSR stock-flow reservation; actual saw feed axis/roller GA to confirm",
                    )
                )
    if layout["id"] == "vehicle-factory":
        scene.append(
            part(
                "street-zx8-bridge-reservation",
                [2, 18, 2],
                [12, 0, 8],
                role="overhead-equipment-reservation",
                equipment_id="street-zx8",
                basis="OSR 18 m bridge requirement; ZX8 trolley dimensions are not bridge dimensions; runway supports unselected",
            )
        )
    else:
        for i, x in enumerate((4, 34)):
            scene.append(
                part(
                    f"street-open-winch-bridge-{i+1}",
                    [30, 3, 3],
                    [x, 21, 8],
                    role="overhead-equipment-reservation",
                    equipment_id="street-open-winch",
                    basis="Two OSR 30 m-span, 125 t configured bridge reservations; runway/wheel reactions and hook coverage unqualified",
                )
            )
    return dict(
        id=layout["id"],
        parts=scene,
        equipment_placements=placements,
        building_screen=roof,
        native_geometry_scope="Roof frame/slab concepts and equipment outer envelopes; no manufacturer internal CAD or site release",
    )


def capability(equipment, fix):
    plate = [0.18, 0.12, 0.02]
    mazak = equipment["mazak-cv5-500"]["published"]
    cmm = equipment["aberlink-axiom-900"]["published"]
    laser = equipment["esprit-photon-3015"]["published"]
    plate_mass = math.prod(plate) * 7850
    box = bounds(fix["parts"])
    fixture_size = [box[j + 3] - box[j] for j in range(3)]
    return dict(
        locator_plate_m=plate,
        blank_mass_kg=plate_mass,
        plate_mazak_envelope_screen=math.hypot(*plate[:2])
        <= mazak["workpiece_diameter_m"]
        and plate[2] <= mazak["workpiece_height_m"]
        and plate_mass <= mazak["workpiece_kg"],
        plate_cmm_envelope_screen=all(
            x <= y for x, y in zip(plate, cmm["measuring_range_m"])
        )
        and plate_mass <= cmm["table_capacity_kg"],
        full_fixture_dimensions_m=fixture_size,
        full_fixture_cmm_envelope_screen=all(
            x <= y for x, y in zip(fixture_size, cmm["measuring_range_m"])
        )
        and fix["mass_kg"] <= cmm["table_capacity_kg"],
        full_fixture_cmm_reason="Fixture X extent >=1.6 m exceeds Axiom X 0.64 m and Y 0.9 m; separate assembled survey required",
        plate_laser_sheet_screen=all(
            x <= y for x, y in zip(plate[:2], laser["sheet_m"])
        )
        and plate_mass <= laser["workpiece_kg"],
        laser_thickness_cut_quality=None,
        welding_procedure_qualified=False,
        limits=[
            "Envelope screens omit workholding/probe/stylus access and machining force; cutting/machining/metrology trials remain required"
        ],
    )


def capacity(a):
    n = a["bed_positions"]
    if type(n) is not int or n < 1:
        raise ValueError("integer casting positions required")
    d = positive(a["bed_occupation_working_days"], "bed occupation")
    for key in (
        "bed_availability",
        "accepted_beam_yield",
        "additional_prestress_loss_fraction",
    ):
        if not 0 < a[key] < 1:
            raise ValueError("fraction strictly between zero and one: " + key)
    yield_factor = a["bed_availability"] * a["accepted_beam_yield"]
    return dict(
        casting_positions=n,
        occupation_working_days=d,
        theoretical_beams_per_working_day=n / d,
        planning_accepted_beams_per_working_day=n / d * yield_factor,
        programme_target_beams_per_working_day=a["programme_beams_per_working_day"],
        positions_required_at_same_assumptions=math.ceil(
            a["programme_beams_per_working_day"] * d / yield_factor
        ),
        limiting_evidence="Bed-only estimate, not a factory throughput guarantee. Mixing, reinforcing, stressing, concrete release strength, cranage, storage, transport and labour cycles unmeasured.",
        occupation_definition="Two working days for full bed occupation including preparation, cure, stripping and turnaround. Not inferred from 48 h cure alone.",
        measured_production=False,
    )


def cutting_plan(fix, *, stock_length=6, end_trim=0.02, kerf=0.003):
    """Descending first-fit stock plan; actual cut accuracy/yield require trials."""
    usable = positive(stock_length, "stock length") - 2 * end_trim
    if end_trim < 0 or kerf < 0 or usable <= 0:
        raise ValueError("nonnegative trim/kerf and usable stock required")
    cuts = sorted(
        [
            (p["size_m"][p["axis"]], p["id"])
            for p in fix["parts"]
            if p["kind"] == "tube"
        ],
        reverse=True,
    )
    bars = []
    for length, identifier in cuts:
        if length + kerf > usable:
            raise ValueError("stock too short for " + identifier)
        target = next(
            (b for b in bars if b["remaining_m"] + 1e-10 >= length + kerf), None
        )
        if target is None:
            target = dict(
                stock_length_m=stock_length,
                trim_total_m=2 * end_trim,
                cuts=[],
                remaining_m=usable,
            )
            bars.append(target)
        target["cuts"].append(
            dict(id=identifier, finished_length_m=length, kerf_m=kerf)
        )
        target["remaining_m"] -= length + kerf
    return dict(
        bars=bars,
        stock_count=len(bars),
        finished_length_m=sum(l for l, _ in cuts),
        kerf_total_m=len(cuts) * kerf,
        trim_total_m=len(bars) * 2 * end_trim,
        residual_total_m=sum(b["remaining_m"] for b in bars),
        basis="6 m stock, 20 mm trim per end and 3 mm kerf are planning assumptions; exact supply length and blade required",
    )

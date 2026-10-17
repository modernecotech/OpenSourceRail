"""Failure-directed provisional beam cage, bearing and support detail variations.

The current architecture force patterns stay distinct. This extends actual
mechanics and fit checks; missing material/site/code acceptance stays unknown.
No bounded search can supply physical tests or issue manufacturing authority.
"""

from __future__ import annotations

from collections import Counter, deque
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json
import math
from pathlib import Path

from . import architecture_civil, architecture_mechanical, architecture_campaign
from engineering.factory_examples.models import part

ROOT = Path(__file__).resolve().parents[2]
SPACE = Path(__file__).with_name("data") / "civil-detail-space.json"
CONTROLLED_TYPES = (
    ROOT
    / "design/component-catalogue/catalog/buildable-civil/reusable-type-release-register.json"
)
G = 9.80665
WORK_PACKAGES = ["CIV-FRP-100", "CIV-FRP-110", "CIV-FRP-120"]


def _read():
    return json.loads(SPACE.read_text())


def _digest(value):
    return sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def _variables(variables):
    domains = _read()["domains"]
    if not isinstance(variables, dict) or set(variables) != set(domains):
        raise ValueError("exact civil-detail variables required")
    if any(
        type(v) not in (int, float) or v not in domains[k] for k, v in variables.items()
    ):
        raise ValueError("civil-detail variation outside bounded domains")
    return dict(variables)


def candidate_family():
    """432 detail genotypes, independent of the actual failure-directed search."""
    domains = _read()["domains"]
    return [dict(zip(domains, v)) for v in product(*domains.values())]


def seed(context=None):
    result = dict(_read()["seed"])
    if context is not None:
        result["beam_depth_m"] = context["source_beam_variables"]["depth_m"]
        result["beam_stem_width_m"] = context["source_beam_variables"]["stem_width_m"]
    return result


def moving_midspan_deflection(span_m, axles, rigidity_nm2):
    """Exact moving-origin maximum at midspan of a constant-EI simple beam.

    The point-load Green function is piecewise cubic in axle coordinate.
    Entry, midspan crossing and exit delimit branches; derivative roots and
    branch endpoints exhaust the origin extrema. This does not find the
    maximum along the entire beam and grants no cracked/long-term stiffness.
    """
    if (
        type(span_m) not in (int, float)
        or not math.isfinite(span_m)
        or span_m <= 0
        or type(rigidity_nm2) not in (int, float)
        or not math.isfinite(rigidity_nm2)
        or rigidity_nm2 <= 0
        or not isinstance(axles, list)
        or not 1 <= len(axles) <= 64
    ):
        raise ValueError("positive finite span/rigidity and bounded axles required")
    if any(
        any(
            type(a.get(k)) not in (int, float) or not math.isfinite(a[k])
            for k in ("x_m", "force_n")
        )
        or a["force_n"] <= 0
        for a in axles
    ):
        raise ValueError("finite axle coordinates and positive forces required")
    L, EI = span_m, rigidity_nm2
    events = sorted({x - a["x_m"] for a in axles for x in (0, L / 2, L)})

    def displacement(origin):
        total = 0.0
        for a in axles:
            x = origin + a["x_m"]
            if 0 <= x <= L:
                b = min(x, L - x)
                total += a["force_n"] * b * (0.75 * L * L - b * b) / (12 * EI)
        return total

    origins = list(events)
    for left, right in zip(events, events[1:]):
        midpoint = (left + right) / 2
        aa = bb = cc = 0.0
        for axle in axles:
            offset, force = axle["x_m"], axle["force_n"]
            x = midpoint + offset
            if not 0 < x < L:
                continue
            k = force / (12 * EI)
            if x <= L / 2:
                aa -= 3 * k
                bb -= 6 * k * offset
                cc += k * (0.75 * L * L - 3 * offset * offset)
            else:
                b = L - offset
                aa += 3 * k
                bb -= 6 * k * b
                cc += k * (3 * b * b - 0.75 * L * L)
        roots = []
        # Scale-relative cancellation handling keeps the polynomial dimension
        # independent of EI and ignores only roundoff-sized leading terms.
        scale = max(abs(aa) * L * L, abs(bb) * L, abs(cc), 1e-300)
        if abs(aa) * L * L <= 1e-13 * scale:
            if abs(bb) * L > 1e-13 * scale:
                roots = [-cc / bb]
        else:
            disc = bb * bb - 4 * aa * cc
            if disc >= 0:
                r = math.sqrt(disc)
                roots = [(-bb - r) / (2 * aa), (-bb + r) / (2 * aa)]
        origins.extend(r for r in roots if left < r < right)
    origin = max(origins, key=lambda t: (displacement(t), -t))
    return dict(
        deflection_m=displacement(origin),
        governing_origin_m=origin,
        examined_origin_count=len(origins),
        method="exact piecewise-cubic midspan Green function and derivative roots",
        full_span_maximum=False,
    )


def footing_pressure(vertical_n, moment_nm, width_m):
    """Square rigid base, uniaxial moment; no soil tension permitted.

    A full-contact linear diagram integrates exactly to N and M. If e>B/6,
    record the failed full-contact assumption and a compression-only triangle.
    An overturning resultant outside B/2 has no finite static soil reaction.
    """
    if (
        any(
            type(v) not in (int, float) or not math.isfinite(v)
            for v in (vertical_n, moment_nm, width_m)
        )
        or vertical_n <= 0
        or width_m <= 0
    ):
        raise ValueError("finite positive vertical load and footing width required")
    N, M, B = vertical_n, abs(moment_nm), width_m
    e = M / N
    qmin = N / (B * B) - 6 * M / B**3
    qmax = N / (B * B) + 6 * M / B**3
    contact = B if e <= B / 6 else 3 * (B / 2 - e)
    return dict(
        eccentricity_m=e,
        full_contact=e <= B / 6,
        equilibrium_possible=e < B / 2,
        linear_minimum_pressure_pa=qmin,
        linear_maximum_pressure_pa=qmax,
        compression_contact_length_m=max(0, contact),
        compression_maximum_pressure_pa=(
            qmax if e <= B / 6 else 2 * N / (B * contact) if contact > 0 else None
        ),
        vertical_equilibrium_n=N,
        moment_equilibrium_nm=M,
    )


@lru_cache(maxsize=1)
def _contexts():
    mechanical = architecture_mechanical.run()
    lm3 = max(mechanical["cases"], key=lambda r: (r["total_mass_kg"], r["id"]))
    basis = json.loads((SPACE.parent / "architecture-feedback.json").read_text())
    six = max(
        architecture_campaign.six_car_cases(basis),
        key=lambda r: (r["total_mass_kg"], r["id"]),
    )
    result = []
    for case in (architecture_campaign.canonical_case(lm3), six):
        report = architecture_civil.assess_pattern(
            architecture_civil.candidate_family(),
            case,
            sensitivity=basis["force_sensitivity_multiplier"],
        )
        if not report["selected_candidate_ids"]:
            raise ValueError(
                "current architecture has no locally screened beam for detail study"
            )
        beam = next(
            r
            for r in report["candidates"]
            if r["id"] == report["selected_candidate_ids"][0]
        )
        state = architecture_civil.mechanical_state(beam)
        for scenario in beam["scenarios"]:
            span = scenario["span_m"]
            static = state["cases"][str(span)]
            result.append(
                dict(
                    id=f"{case['id']}/pi{span:g}",
                    configuration_id=case["id"],
                    architecture_id=case["architecture_id"],
                    span_m=span,
                    source_case=case,
                    source_case_sha256=_digest(case),
                    source_beam_id=beam["id"],
                    source_beam_variables=beam["variables"],
                    section=beam["section"],
                    strand_points=state["strand_points"],
                    dead_end_reaction_n=static["dead_end_reaction_n"],
                    live_end_reaction_n=scenario["maximum_live_reaction_n"],
                    known_beam_mass_kg=scenario["known_concrete_plus_strand_mass_kg"],
                    applied_axles=report["live_envelope"]["pattern"]["axles"],
                    force_sensitivity_multiplier=basis["force_sensitivity_multiplier"],
                    accepted_loading=False,
                    existing_configuration_compatible=False,
                    source_changing_proposal=True,
                    work_package_ids=WORK_PACKAGES,
                )
            )
    return result


def contexts():
    """Four independent contexts; max studied mass is not project adoption."""
    return deepcopy(_contexts())


@lru_cache(maxsize=32)
def _coupled(base_id, gross_added_train_mass_kg):
    base = deepcopy(next(c for c in _contexts() if c["id"] == base_id))
    original = base["source_case"]
    multiplier = 1 + gross_added_train_mass_kg / original["total_mass_kg"]
    case = {
        k: deepcopy(original[k])
        for k in (
            "id",
            "architecture_id",
            "cars",
            "train_length_m",
            "total_mass_kg",
            "axles",
        )
    }
    case["id"] += "-gross-addition-" + _digest(gross_added_train_mass_kg)[:10]
    case["total_mass_kg"] += gross_added_train_mass_kg
    for axle in case["axles"]:
        axle["force_n"] *= multiplier
    case.update(
        accepted_loading=False,
        physical_release=False,
        proportional_axle_force_sensitivity=True,
        gross_added_train_mass_kg=gross_added_train_mass_kg,
        force_multiplier=multiplier,
        actual_cg_allocation_known=False,
    )
    base.update(
        id=f"{case['id']}/pi{base['span_m']:g}",
        configuration_id=case["id"],
        parent_context_id=base_id,
        parent_source_case=original,
        gross_added_train_mass_kg=gross_added_train_mass_kg,
        source_case=case,
        source_case_sha256=_digest(case),
        coupling_basis="Gross added proposed train-member mass without removal credit, distributed proportionally over source axle forces. Replacement net mass and real axle/CG redistribution unknown.",
    )
    env = architecture_civil.live_envelope(
        case, sensitivity=base["force_sensitivity_multiplier"]
    )
    response = architecture_civil.response(
        dict(variables=base["source_beam_variables"]), env
    )
    scenario = next(s for s in response["scenarios"] if s["span_m"] == base["span_m"])
    base["applied_axles"] = env["pattern"]["axles"]
    base["live_end_reaction_n"] = scenario["maximum_live_reaction_n"]
    base["coupled_peak_live_moment_nm"] = scenario["continuous_peak_live_moment_nm"]
    return base


def coupled_context(context, gross_added_train_mass_kg):
    """Recompute forces/reactions for one explicitly gross-added-mass sensitivity.

    Input must be an original context, preventing accidental repeated additions.
    Original LM3 and six-car physical architectures never cross this boundary.
    """
    if (
        type(gross_added_train_mass_kg) not in (int, float)
        or not math.isfinite(gross_added_train_mass_kg)
        or not 0 <= gross_added_train_mass_kg <= 2e6
    ):
        raise ValueError("bounded finite nonnegative gross addition required")
    if context not in _contexts():
        raise ValueError("original uncoupled civil context required")
    return deepcopy(_coupled(context["id"], gross_added_train_mass_kg))


def _validate_context(context):
    if not isinstance(context, dict):
        raise ValueError("exact current civil-detail context required")
    if context in _contexts():
        return
    parent_id = context.get("parent_context_id")
    if parent_id in {c["id"] for c in _contexts()} and type(
        context.get("gross_added_train_mass_kg")
    ) in (int, float):
        expected = coupled_context(
            next(c for c in _contexts() if c["id"] == parent_id),
            context["gross_added_train_mass_kg"],
        )
        if context == expected:
            return
    raise ValueError("exact current civil-detail context required; no load transfer")


@lru_cache(maxsize=128)
def _beam_response(case_json, beam_json, sensitivity):
    case = json.loads(case_json)
    variables = json.loads(beam_json)
    envelope = architecture_civil.live_envelope(case, sensitivity=sensitivity)
    return architecture_civil.response(
        dict(variables=variables), envelope
    ), architecture_civil.mechanical_state(dict(variables=variables))


def _check(identity, value, limit, units, basis, *, lower=False):
    passed = value >= limit - 1e-10 if lower else value <= limit + 1e-10
    return dict(
        id=identity,
        state="pass" if passed else "fail",
        value=value,
        limit=limit,
        units=units,
        basis=basis,
        accepted_basis=False,
    )


def _unknown(identity, basis):
    return dict(
        id=identity,
        state="unknown",
        value=None,
        limit=None,
        units=None,
        basis=basis,
        accepted_basis=False,
    )


def controlled_target_mappings(span_m):
    """Related source-owned targets, never a declaration of fit or coverage.

    The register contains a25m Pi beam and8m pier interfaces. It has no20m beam
    or isolated-footing product. Proposed5m solid supports differ from source.
    """
    register = json.loads(CONTROLLED_TYPES.read_text())
    digest = sha256(CONTROLLED_TYPES.read_bytes()).hexdigest()
    targets = {
        "OSR-TYPE-3FD9673EF391": (
            "PIER-CAP-RESEARCH",
            "related cap target; proposed solid cap differs from source hollow/precast-shell8m pier cap",
        ),
        "OSR-TYPE-99A11C1DC30D": (
            "PIER-COLUMN-RESEARCH",
            "related column target; proposed5m square column differs from source8m column",
        ),
        "OSR-TYPE-C966BC7372EC": (
            "BEARING-RESERVATION-RESEARCH",
            "related bearing/jacking target; pad reservation is not an offered or adopted bearing",
        ),
    }
    if span_m == 25:
        targets["OSR-TYPE-D36A7871D9B7"] = (
            "PI25",
            "span-matched25m beam target; proposed section, strands and reinforcement differ",
        )
    rows = {r["type_id"]: r for r in register["type_register"]}
    if not set(targets) <= set(rows):
        raise ValueError("controlled civil target identities changed; review mapping")
    if (
        span_m == 25
        and rows["OSR-TYPE-D36A7871D9B7"]["source_geometry"]
        != "civil.decked_pi_structural_placeholder(span_m=25)"
    ):
        raise ValueError("controlled beam source span changed; review mapping")
    return [
        dict(
            source_path=str(CONTROLLED_TYPES.relative_to(ROOT)),
            source_revision_sha256=digest,
            type_id=identity,
            package_id=rows[identity]["package_id"],
            proposed_detail_component_id=proposed,
            relation=relation,
            source_geometry=rows[identity]["source_geometry"],
            source_status=rows[identity]["status"],
            exact_fit_or_adoption=False,
            full_component_coverage=False,
            configuration_compatible=False,
        )
        for identity, (proposed, relation) in targets.items()
    ]


def assess(variables, context):
    """Detail one selected beam/support under its exact provisional case."""
    v = _variables(variables)
    _validate_context(context)
    context_record = deepcopy(context)
    beam_variables = dict(context["source_beam_variables"])
    beam_variables["stem_width_m"] = v["beam_stem_width_m"]
    beam_variables["depth_m"] = v["beam_depth_m"]
    beam_response, beam_state = _beam_response(
        json.dumps(context["source_case"], sort_keys=True),
        json.dumps(beam_variables, sort_keys=True),
        context["force_sensitivity_multiplier"],
    )
    beam_scenario = next(
        s for s in beam_response["scenarios"] if s["span_m"] == context["span_m"]
    )
    context = dict(context)
    context.update(
        source_beam_variables=beam_variables,
        section=beam_state["section"],
        strand_points=beam_state["strand_points"],
        dead_end_reaction_n=beam_state["cases"][str(context["span_m"])][
            "dead_end_reaction_n"
        ],
        known_beam_mass_kg=beam_scenario["known_concrete_plus_strand_mass_kg"],
    )
    cfg = _read()
    a = cfg["assumptions"]
    beam_space = json.loads(architecture_civil.civil.SPACE.read_text())
    L, D, bw = (
        context["span_m"],
        context["section"]["depth_m"],
        2 * context["source_beam_variables"]["stem_width_m"],
    )
    dia, spacing = v["stirrup_diameter_m"], v["stirrup_spacing_m"]
    cover = a["research_cover_m"]
    lower_chord = [p for p in context["strand_points"] if p["region"] == "lower"]
    if not lower_chord:
        raise ValueError("declared lower-region tension chord required")
    # Equal-area strands: area centroid equals their coordinate mean. The
    # lowest strand is not the tension-resultant centroid and must never be
    # used to inflate effective depth. Ultimate chord qualification stays open.
    tension_chord_centroid = math.fsum(p["z_m"] for p in lower_chord) / len(lower_chord)
    effective_depth = D - tension_chord_centroid
    z = 0.9 * effective_depth
    # Four vertical legs: a closed link in each of the two stems. Equal web
    # sharing is an explicit hypothesis; torsion/transverse distribution unknown.
    Asw = 4 * math.pi * dia * dia / 4
    fyd = a["steel_characteristic_yield_pa"] / a["gamma_steel"]
    fcd = a["alpha_cc"] * a["concrete_characteristic_strength_pa"] / a["gamma_concrete"]
    cot = a["cot_theta"]
    Vsteel = Asw / spacing * z * fyd * cot
    nu = 0.6 * (1 - a["concrete_characteristic_strength_pa"] / 250e6)
    Vstrut = a["alpha_cw"] * bw * z * nu * fcd / (cot + 1 / cot)
    Rd, Rl = context["dead_end_reaction_n"], context["live_end_reaction_n"]
    Vdemand = a["gravity_demand_multiplier"] * Rd + a["live_demand_multiplier"] * Rl
    stem_width = bw / 2
    # Actual perpendicular clearance from every strand to each enclosing link's
    # straight inner surface. Bend/hook closure is separately reserved below.
    strand_radius = beam_space["manufacturing"]["strand_envelope_diameter_m"] / 2
    stem_centres = beam_space["geometry"]["stem_centres_y_m"]
    link_gap = min(
        min(
            stem_width / 2
            - cover
            - dia
            - abs(p["y_m"] - min(stem_centres, key=lambda y: abs(y - p["y_m"]))),
            p["z_m"] - cover - dia,
            D - cover - dia - p["z_m"],
        )
        - strand_radius
        for p in context["strand_points"]
    )
    link_inside_width = stem_width - 2 * (cover + dia)
    former_diameter = a["research_bend_former_diameters"] * dia
    hook_reservation = (
        a["research_hook_straight_diameters"] * dia + former_diameter + dia
    )
    link_count_per_stem = math.ceil((L - 2 * cover) / spacing) + 1
    actual_spacing = (L - 2 * cover) / (link_count_per_stem - 1)
    # Geometric procurement estimate includes two research hook lengths; no
    # BS8666 shape code/cutting schedule is issued by this estimate.
    link_centre_width = stem_width - 2 * cover - dia
    link_centre_height = D - 2 * cover - dia
    estimated_link_length = (
        2 * (link_centre_width + link_centre_height)
        + 2 * a["research_hook_straight_diameters"] * dia
    )
    links_mass = (
        2
        * link_count_per_stem
        * estimated_link_length
        * math.pi
        * dia**2
        / 4
        * a["steel_density_kg_m3"]
    )
    # Added links increase gravity/shear and the declared mass, never disappear
    # from support demand. Other conventional rebar/attachments remain unknown.
    link_end_reaction = links_mass * G / 2
    Vdemand += a["gravity_demand_multiplier"] * link_end_reaction
    support_reaction = Rd + Rl + link_end_reaction
    pad_pressure = (Vdemand / 2) / (a["pad_width_m"] * v["pad_length_m"])
    beam_end_length = beam_space["geometry"]["end_fill_length_m"]
    B = v["footing_width_m"]
    support_volume = (
        a["column_width_m"] ** 2 * a["column_height_m"]
        + a["cap_length_m"] * a["cap_width_m"] * a["cap_depth_m"]
        + B * B * a["footing_thickness_m"]
    )
    support_mass = support_volume * a["concrete_density_kg_m3"]
    N = support_reaction + support_mass * G
    H = a["research_horizontal_reaction_fraction"] * Rl
    lever = (
        a["column_height_m"]
        + a["cap_depth_m"]
        + a["pad_height_m"]
        + a["footing_thickness_m"]
    )
    M = H * lever
    foundation = footing_pressure(N, M, B)
    deflection = moving_midspan_deflection(
        L,
        context["applied_axles"],
        a["concrete_modulus_pa"] * context["section"]["inertia_x_m4"],
    )
    checks = [
        _check(
            "web_link_steel",
            Vdemand,
            Vsteel,
            "N",
            "Provisional vertical-link truss V=Asw/s*z*fyd*cot(theta), d to declared lower-region equal-area tendon centroid, z=0.9d; no prestress, concrete-tension or reduced-support-shear credit; ultimate chord force/anchorage unqualified",
        ),
        _check(
            "web_concrete_strut",
            Vdemand,
            Vstrut,
            "N",
            "Separate provisional strut crushing V=alpha_cw*bw*z*nu*fcd/(cot(theta)+tan(theta)); d to lower-region tendon centroid, z=0.9d, alpha_cw=1; ultimate chord/strut geometry unqualified",
        ),
        _check(
            "tendon_link_clearance",
            link_gap,
            a["research_tendon_link_clearance_m"],
            "m",
            "Minimum actual strand-surface distance to link inner straight surfaces; hook regions unresolved",
            lower=True,
        ),
        _check(
            "link_bend_envelope",
            link_inside_width,
            former_diameter + 2 * dia,
            "m",
            "Research four-diameter former plus two bar thicknesses must fit stem link interior",
            lower=True,
        ),
        _check(
            "link_hook_reservation",
            link_inside_width,
            hook_reservation,
            "m",
            "Research straight-hook plus bend reservation; congestion and code anchorage still unqualified",
            lower=True,
        ),
        _check(
            "concrete_placement_access",
            actual_spacing - dia,
            a["research_maximum_aggregate_m"]
            * a["research_aggregate_access_multiplier"],
            "m",
            "Longitudinal access between links; full three-dimensional cage and vibrator path not established",
            lower=True,
        ),
        _check(
            "bearing_pressure",
            pad_pressure,
            a["research_pad_pressure_pa"],
            "Pa",
            "Two equal-load pad reservations under provisional shear combination; supplier rating, bulging, rotation and anchorage unknown",
        ),
        _check(
            "bearing_end_block_fit",
            v["pad_length_m"] + 2 * a["end_block_edge_reservation_m"],
            beam_end_length,
            "m",
            "Bearing length plus two25mm research edge reservations must fit existing550mm end block",
        ),
        _check(
            "footing_full_contact",
            foundation["eccentricity_m"],
            B / 6,
            "m",
            "Uniaxial service N,M rigid square base; e<=B/6 required before full-contact linear pressure can be used",
        ),
        _check(
            "footing_pressure",
            foundation["compression_maximum_pressure_pa"] or 1e300,
            a["hypothetical_soil_pressure_pa"],
            "Pa",
            "Gross service pressure against purely hypothetical150kPa screen; not Baghdad ground bearing capacity or settlement acceptance",
        ),
        _check(
            "midspan_live_deflection",
            deflection["deflection_m"],
            L / a["research_live_midspan_deflection_divisor"],
            "m",
            "Exact maximum moving-origin midspan instantaneous gross-EI live response versus unacceptedL/800 screen; not full-span deflection/camber/dynamics acceptance",
        ),
    ]
    # Widening the web changes self-weight, centroid, stiffness and shortening;
    # the original beam's gross stress pass cannot be copied to the new beam.
    values = {
        "transfer_no_tension": (
            beam_scenario["minimum_sampled_transfer_compression_pa"],
            -1e-6,
            "Pa",
        ),
        "service_no_tension": (
            beam_scenario["minimum_sampled_service_compression_pa"],
            -1e-6,
            "Pa",
        ),
        "handling_no_tension": (
            beam_scenario["minimum_sampled_handling_compression_pa"],
            -1e-6,
            "Pa",
        ),
        "concrete_geometric_cover": (
            beam_response["metrics"]["minimum_clear_concrete_cover_m"],
            beam_space["manufacturing"]["concrete_research_cover_m"],
            "m",
        ),
        "grip_spacing": (
            beam_response["metrics"]["minimum_grip_surface_gap_m"],
            beam_space["manufacturing"]["grip_research_gap_m"],
            "m",
        ),
        "strand_geometry": (
            beam_response["metrics"]["minimum_strand_surface_gap_m"],
            0,
            "m",
        ),
        "retained_strand_tension": (
            beam_scenario["minimum_retained_strand_stress_pa"],
            0,
            "Pa",
        ),
    }
    for key, (value, limit, units) in values.items():
        check = _check(
            "beam_" + key,
            value,
            limit,
            units,
            beam_response["checks"][key]["basis"]
            + f"; recomputed for this {L:g}m context after detail geometry change",
            lower=True,
        )
        if key in ("strand_geometry", "retained_strand_tension"):
            check["state"] = "pass" if value > 0 else "fail"
        checks.append(check)
    unknowns = dict(
        adopted_loading="Approved axle allocation, permanent loads, railway combinations, braking, transverse distribution, torsion, derailment and earthquake actions absent; one span end only, not an interior pier carrying adjacent spans",
        adopted_materials="Concrete/steel/strand properties, cover, exposure/fire and fatigue/endurance not approved; all numerical resistances use stated provisional values",
        beam_flexural_resistance="Prestressed ultimate flexure, longitudinal truss tie/shift rule, cracking, development and bond not solved by these web link checks",
        end_zone_and_transfer="Transmission-length force buildup, splitting/bursting, end diaphragm strut-and-tie, cut-off sequence and actual release strength require design and tests",
        reinforcement_detail="Actual bend/hook/longitudinal bar intersections, bar schedule, laps/couplers, lifting inserts, tolerances, cage assembly and mould access require dimensioned details and fabricator review",
        bearing_configuration="No selected bearing model, pressure rating, movements/rotation, shear keys, restraint, jacking/replacement clearance, pads/seats/grout anchors or supplier GA accepted",
        support_resistance="Pier cap flexure/shear, column second-order and biaxial response, cap-column and column-footing connections, footing flexure/punching/shear/rebar unresolved",
        site_ground="Baghdad survey, boreholes, groundwater, chemical exposure, bearing resistance, settlement, liquefaction and piled/shallow choice absent;150kPa is hypothetical only. Up to5m footing footprint, excavation, utilities, adjacent foundations and route/site permission unconfirmed",
        full_service_response="Full-span deflection, cracking, timed losses, creep/shrinkage, camber, track interaction and coupled vehicle dynamics remain open",
        revised_permanent_loads="Gross beam fibre screens include changed concrete/strand geometry; estimated added links are included in support demand but their distributed gravity/transfer/handling fibre effects and other conventional reinforcement/attachments require a revised staged full beam calculation",
        manufacturing_acceptance="Concrete/rebar trials, stressing equipment qualification, inspection evidence, issued production drawings and independent acceptance absent",
    )
    checks += [_unknown(k, b) for k, b in unknowns.items()]
    failed = [c["id"] for c in checks if c["state"] == "fail"]
    return dict(
        id="civil-detail-" + _digest([context["id"], v])[:16],
        configuration_id=context["configuration_id"],
        context_id=context["id"],
        architecture_id=context["architecture_id"],
        work_package_ids=WORK_PACKAGES,
        component_ids=[
            "PI20" if L == 20 else "PI25",
            "PIER-CAP-RESEARCH",
            "PIER-COLUMN-RESEARCH",
            "OUTER-END-FOOTING-RESEARCH",
            "BEARING-RESERVATION-RESEARCH",
        ],
        proposed_detail_component_ids=[
            "PI20" if L == 20 else "PI25",
            "PIER-CAP-RESEARCH",
            "PIER-COLUMN-RESEARCH",
            "OUTER-END-FOOTING-RESEARCH",
            "BEARING-RESERVATION-RESEARCH",
        ],
        component_identity_scope="Proposed detail identifiers only; controlled_target_mappings identify related source targets without fit, adoption or full coverage",
        controlled_target_mappings=controlled_target_mappings(L),
        unmapped_proposed_detail_component_ids=["OUTER-END-FOOTING-RESEARCH"]
        + (["PI20"] if L == 20 else []),
        exact_fit_or_adoption=False,
        full_component_coverage=False,
        context_record=context_record,
        source_case_sha256=context["source_case_sha256"],
        source_beam_id=context_record["source_beam_id"],
        proposed_beam_id=beam_response["id"],
        variables=v,
        variable_units={k: "m" for k in v},
        geometry=dict(
            span_m=L,
            beam_variables=context["source_beam_variables"],
            beam_section=context["section"],
            provisional_tension_chord_centroid_z_m=tension_chord_centroid,
            provisional_tension_chord_strand_count=len(lower_chord),
            provisional_effective_depth_m=effective_depth,
            provisional_shear_lever_arm_m=z,
            provisional_tension_chord_basis="Equal-area strands explicitly labelled lower region; upper region excluded; force-resultant/ultimate chord and anchorage not qualified",
            bearing_support_x_m=beam_end_length / 2,
            bearing_support_y_m=stem_centres,
            link_diameter_m=dia,
            links_each_stem=link_count_per_stem,
            actual_link_spacing_m=actual_spacing,
            link_outer_width_m=stem_width - 2 * cover,
            link_outer_height_m=D - 2 * cover,
            research_bend_former_diameter_m=former_diameter,
            two_pad_dimensions_m=[
                v["pad_length_m"],
                a["pad_width_m"],
                a["pad_height_m"],
            ],
            column_dimensions_m=[
                a["column_width_m"],
                a["column_width_m"],
                a["column_height_m"],
            ],
            cap_dimensions_m=[a["cap_length_m"], a["cap_width_m"], a["cap_depth_m"]],
            footing_dimensions_m=[B, B, a["footing_thickness_m"]],
            site_footprint_accepted=False,
            full_detail_complete=False,
        ),
        materials=dict(
            concrete_strength_pa=a["concrete_characteristic_strength_pa"],
            steel_yield_pa=a["steel_characteristic_yield_pa"],
            concrete_modulus_pa=a["concrete_modulus_pa"],
            accepted=False,
        ),
        connections=dict(
            bearing_load_path="beam -> two provisional pads -> cap -> column -> isolated footing -> hypothetical soil",
            detailing_qualified=False,
            scope="single outer span-end support only; no adjacent-span reaction included",
        ),
        manufacturing=dict(
            route=[
                "fabricator-reviewed dimensioned cage and hooks",
                "assemble cage around prestressing strands with verified insertion path",
                "fit split mould/end diaphragm and accepted inserts",
                "trial cast/cure/transfer/demould",
                "inspect qualified bearing seat and erect with accepted rig",
                "inspect independent pier/footing reinforcement and pour/erect",
            ],
            issued_bar_schedule=False,
            estimated_link_length_each_m=estimated_link_length,
            links_mass_estimate_kg=links_mass,
            accepted=False,
        ),
        metrics=dict(
            design_shear_n=Vdemand,
            link_shear_resistance_n=Vsteel,
            strut_shear_resistance_n=Vstrut,
            provisional_tension_chord_centroid_z_m=tension_chord_centroid,
            provisional_effective_depth_m=effective_depth,
            provisional_shear_lever_arm_m=z,
            tendon_link_clearance_m=link_gap,
            bearing_pressure_pa=pad_pressure,
            support_service_reaction_n=support_reaction,
            foundation_vertical_n=N,
            foundation_horizontal_n=H,
            foundation_moment_nm=M,
            foundation=foundation,
            live_midspan_deflection=deflection,
            added_links_mass_kg=links_mass,
            support_concrete_mass_kg=support_mass,
            gross_beam_stress_response=beam_response["metrics"],
            peak_live_moment_nm=beam_scenario["continuous_peak_live_moment_nm"],
        ),
        checks=checks,
        objectives=dict(
            mass_kg=context["known_beam_mass_kg"] + links_mass + support_mass,
            cost=None,
            mass_scope="one beam gross concrete+strands plus estimated links and one outer-end cap/column/footing gross concrete; excludes pads, anchors, support rebar, other beam reinforcement and second support",
        ),
        local_screen_feasible=not failed,
        rejected_known_checks=bool(failed),
        failed_checks=failed,
        next_actions=(
            ["Change bounded detail variables in response to: " + ", ".join(failed)]
            if failed
            else [
                "Retain as local-screen proposal; obtain adopted loading/material/site data and independently design all open load paths before manufacturing selection"
            ]
        ),
        remaining_gates=list(unknowns),
        source_changing_proposal=True,
        existing_configuration_compatible=False,
        manufacturing_release=False,
        engineering_design_complete=False,
        physical_release=False,
    )


def propose(candidate, context):
    """One-coordinate repairs triggered by the candidate's actual failures."""
    if candidate["context_id"] != context["id"]:
        raise ValueError("candidate/context mismatch")
    v = _variables(candidate["variables"])
    failed = set(candidate["failed_checks"])
    actions = []
    if failed & {"web_link_steel"}:
        actions += [("stirrup_spacing_m", -1), ("stirrup_diameter_m", 1)]
    if failed & {
        "tendon_link_clearance",
        "link_bend_envelope",
        "link_hook_reservation",
        "concrete_placement_access",
    }:
        actions += [
            ("beam_stem_width_m", 1),
            ("stirrup_diameter_m", -1),
            ("stirrup_spacing_m", 1),
        ]
    if failed & {
        "web_concrete_strut",
        "beam_service_no_tension",
        "beam_transfer_no_tension",
        "midspan_live_deflection",
    }:
        actions += [("beam_depth_m", 1), ("beam_stem_width_m", 1)]
    if "bearing_pressure" in failed:
        actions += [("pad_length_m", 1)]
    if "bearing_end_block_fit" in failed:
        actions += [("pad_length_m", -1)]
    if failed & {"footing_full_contact", "footing_pressure"}:
        actions += [("footing_width_m", 1)]
    domains = _read()["domains"]
    proposals = []
    for name, direction in actions:
        index = domains[name].index(v[name]) + direction
        if 0 <= index < len(domains[name]):
            child = dict(v)
            child[name] = domains[name][index]
            if child not in proposals:
                proposals.append(child)
    return proposals


def model_definition(candidate):
    """Native spatial envelopes for a single outer support, no rebar fiction."""
    context = candidate["context_record"]
    _validate_context(context)
    if candidate != assess(candidate["variables"], context):
        # run() adds search metadata; validate the immutable evaluated fields.
        evaluated = assess(candidate["variables"], context)
        if any(candidate.get(k) != value for k, value in evaluated.items()):
            raise ValueError("candidate differs from current civil evaluation")
    a = _read()["assumptions"]
    model = architecture_civil.model_definition(
        dict(variables=candidate["geometry"]["beam_variables"]), span=context["span_m"]
    )
    model["id"] = candidate["id"]
    x = candidate["geometry"]["bearing_support_x_m"]
    pad = candidate["geometry"]["two_pad_dimensions_m"]
    for i, y in enumerate(candidate["geometry"]["bearing_support_y_m"]):
        model["parts"].append(
            part(
                f"bearing-reservation-{i}",
                pad,
                [x - pad[0] / 2, y - pad[1] / 2, -pad[2]],
                role="unoffered-bearing-envelope",
            )
        )
    cap = candidate["geometry"]["cap_dimensions_m"]
    zcap = -a["pad_height_m"] - cap[2]
    model["parts"].append(
        part(
            "cap-concrete-envelope",
            cap,
            [x - cap[0] / 2, -cap[1] / 2, zcap],
            role="unreinforced-gross-envelope",
        )
    )
    column = candidate["geometry"]["column_dimensions_m"]
    zcolumn = zcap - column[2]
    model["parts"].append(
        part(
            "column-concrete-envelope",
            column,
            [x - column[0] / 2, -column[1] / 2, zcolumn],
            role="unreinforced-gross-envelope",
        )
    )
    footing = candidate["geometry"]["footing_dimensions_m"]
    model["parts"].append(
        part(
            "footing-concrete-envelope",
            footing,
            [x - footing[0] / 2, -footing[1] / 2, zcolumn - footing[2]],
            role="unreinforced-gross-envelope",
        )
    )
    model["notes"] = (
        "One beam with one outer-end support gross envelopes. Rebar bends/hooks, bearing internals, anchors, second support and ground absent. Native solid validity cannot qualify load paths, manufacture or site suitability."
    )
    model["physical_release"] = False
    return model


def run(output=None, *, budget_per_context=432):
    if type(budget_per_context) is not int or not 1 <= budget_per_context <= 432:
        raise ValueError("civil detail budget must be integer1..432 per context")
    rows, histories = [], []
    for context in contexts():
        queue = deque([(seed(context), None, 0, [])])
        seen = set()
        local = []
        termination = "domain-exhausted"
        while queue and len(local) < budget_per_context:
            variables, parent, generation, repaired = queue.popleft()
            identity = _digest(variables)
            if identity in seen:
                continue
            seen.add(identity)
            row = assess(variables, context)
            row.update(
                parent_id=parent, generation=generation, mutation_targets=repaired
            )
            local.append(row)
            if row["local_screen_feasible"]:
                termination = "local-screen-feasible-with-open-gates"
                break
            for child in propose(row, context):
                if _digest(child) not in seen:
                    queue.append(
                        (child, row["id"], generation + 1, row["failed_checks"])
                    )
        else:
            if queue:
                termination = "budget-exhausted"
        rows.extend(local)
        histories.append(
            dict(
                context_id=context["id"],
                termination=termination,
                evaluations=len(local),
                selected_candidate_ids=[
                    r["id"] for r in local if r["local_screen_feasible"]
                ],
                rejected_candidate_ids=[
                    r["id"] for r in local if r["rejected_known_checks"]
                ],
            )
        )
    sources = {
        str(SPACE.relative_to(ROOT)): sha256(SPACE.read_bytes()).hexdigest(),
        str(Path(__file__).relative_to(ROOT)): sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
    }
    sources.update(
        {r["path"]: r["sha256"] for r in architecture_civil.source_inventory()}
    )
    sources.update(architecture_mechanical.run()["source_sha256"])
    for path in (
        "engineering/generative_design/architecture_campaign.py",
        "engineering/generative_design/architecture_mechanical.py",
        "engineering/generative_design/data/architecture-feedback.json",
        str(CONTROLLED_TYPES.relative_to(ROOT)),
    ):
        sources[path] = sha256((ROOT / path).read_bytes()).hexdigest()
    report = dict(
        schema="osr-civil-detail-campaign/1",
        method="deterministic failure-directed one-coordinate bounded repair; first local-screen survivor per independent context, no unknown gate counted as passed",
        contexts=contexts(),
        candidates=rows,
        iteration_history=histories,
        candidate_count=len(rows),
        finite_domain_per_context=432,
        geometry_domain_revision=_read()["geometry_domain_revision"],
        selected_candidate_ids=[r["id"] for r in rows if r["local_screen_feasible"]],
        rejected_candidate_count=sum(r["rejected_known_checks"] for r in rows),
        check_counts=dict(Counter(c["state"] for r in rows for c in r["checks"])),
        references=_read()["references"],
        source_sha256=sources,
        open_scope=[
            "All other source system work packages remain outside this detail adapter",
            "Interior piers, adjacent-span loading, complete conventional reinforcement and physical qualification remain open",
        ],
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )
    if output is not None:
        folder = Path(output)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "civil-detail.json").write_text(
            json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
        )
        for row in rows:
            if row["local_screen_feasible"]:
                path = folder / row["id"]
                path.mkdir(exist_ok=True)
                (path / "model.json").write_text(
                    json.dumps(model_definition(row), indent=2, sort_keys=True) + "\n"
                )
    return report

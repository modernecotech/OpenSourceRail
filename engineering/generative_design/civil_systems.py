"""Explicit queued civil/factory interface investigations and bounded repairs.

Analytical demands and assembly/tool envelopes, never RC/soil/code acceptance.
All reported loads and numerical targets retain a research basis and SI units.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import ast
import json
import math

from . import civil
from engineering.factory_examples import development
from engineering.factory_examples.models import part

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).with_name("data") / "civil-systems.json"
CAT = "design/component-catalogue/src/osr_mech/"
SOURCES = {
    "canopy": CAT + "station/portal.py",
    "auxiliary": CAT + "station/auxiliary_canopy.py",
    "pier": CAT + "civil/substructure.py",
    "interfaces": CAT + "civil/railway_interfaces.py",
    "turnout": CAT + "track/turnout.py",
    "depot": CAT + "depot/layout.py",
    "platform": CAT + "civil/platform_l_unit.py",
    "edge": CAT + "civil/guideway_channel_edge.py",
    "slab": CAT + "civil/slab.py",
    "station_layout": CAT + "station/layout.py",
    "factory": "engineering/factory_examples/examples/report.json",
    "factory_basis": "engineering/factory_examples/data/basis.json",
    "factory_development": "engineering/factory_examples/data/development.json",
    "connections": "engineering/factory_examples/data/connections.json",
    "beam_search": "engineering/generative_design/civil.py",
    "legacy_axles": "engineering/industrialisation/vehicle-civil-load-trace.json",
    "provisional_axles": "engineering/generative_design/integration.py",
}
REFERENCES = [
    dict(
        url="https://www.fhwa.dot.gov/engineering/hydraulics/pubs/hif24006.pdf",
        use="HEC22 rational method and open-channel hydraulics; no Baghdad rainfall or drainage design criteria adopted",
    ),
    dict(
        url="https://www.fhwa.dot.gov/bridge/pubs/nhi15047.pdf",
        use="Bearing movement and replacement/jacking interfaces; no highway code adopted for the railway",
    ),
]


def _read(path):
    return json.loads(Path(path).read_text())


def _constant(source, name):
    for node in ast.parse((ROOT / SOURCES[source]).read_text()).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == name for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise ValueError("missing audited source constant " + name)


def _audit():
    expected = [
        ("canopy", "BAY_SPACING_MM", 6000),
        ("canopy", "PLATFORM_DEPTH_MM", 3500),
        ("canopy", "CLEAR_HEIGHT_MM", 3800),
        ("pier", "PIER_CAP_Y_MM", 7000),
        ("pier", "PIER_CAP_X_MM", 2500),
        ("pier", "WEB_BEARING_OFFSET_MM", None),
        ("auxiliary", "AUX_MODULE_WIDTH_MM", 22000),
        ("platform", "UNIT_LENGTH_MM", 3000),
        ("slab", "PANEL_LENGTH_MM", 6000),
        ("edge", "PLATFORM_TO_TOR_HEIGHT_MM", 350),
    ]
    for source, name, value in expected:
        if value is not None and _constant(source, name) != value:
            raise ValueError("audited catalogue geometry changed: " + name)
    return [
        dict(path=p, sha256=sha256((ROOT / p).read_bytes()).hexdigest())
        for p in SOURCES.values()
    ]


def status(ok, basis):
    return dict(status="passed" if ok else "failed", basis=basis)


def variant(identifier, variables, metrics, checks):
    return dict(
        id=identifier,
        variables=variables,
        metrics=metrics,
        checks=checks,
        conditional_local_pass=all(x["status"] == "passed" for x in checks.values()),
        engineering_design_complete=False,
        physical_release=False,
    )


def package(identifier, title, investigations, gates, artifacts=None):
    return dict(
        work_package_id=identifier,
        title=title,
        investigations=investigations,
        generated_artifacts=artifacts or [],
        unresolved_gates=[
            dict(id=f"{identifier}-gate-{i+1}", status="unknown", requirement=g)
            for i, g in enumerate(gates)
        ],
        engineering_design_complete=False,
        physical_release=False,
    )


def investigation(identifier, basis, candidates, sources, method):
    return dict(
        id=identifier,
        basis=basis,
        method=method,
        source_paths=[SOURCES[s] for s in sources],
        candidates=candidates,
        selected_candidate_ids=[
            r["id"] for r in candidates if r["conditional_local_pass"]
        ][:2],
        termination="bounded_variations_exhausted",
        engineering_design_complete=False,
    )


def rational_runoff(area_m2, intensity_mm_h, coefficient):
    if not area_m2 > 0 or not intensity_mm_h > 0 or not 0 <= coefficient <= 1:
        raise ValueError("positive area/rainfall and runoff coefficient 0..1 required")
    return area_m2 * intensity_mm_h / 1000 / 3600 * coefficient


def channel_flow(width, depth, slope, n):
    if min(width, depth, slope, n) <= 0:
        raise ValueError(
            "positive rectangular channel geometry/slope/roughness required"
        )
    A = width * depth
    R = A / (width + 2 * depth)
    return A * R ** (2 / 3) * math.sqrt(slope) / n


def beam_strip(point_load, span, width, thickness, modulus):
    if min(point_load, span, width, thickness, modulus) <= 0:
        raise ValueError("positive simply-supported strip inputs required")
    M = point_load * span / 4
    I = width * thickness**3 / 12
    return dict(
        moment_nm=M,
        nominal_bending_demand_pa=M * thickness / 2 / I,
        elastic_deflection_m=point_load * span**3 / (48 * modulus * I),
    )


def contact_pressure(vertical, moment, width, length):
    """Elastic full-contact pressure distribution only inside the middle third."""
    if min(vertical, width, length) <= 0:
        raise ValueError("positive pad dimensions and vertical force required")
    e = abs(moment) / vertical
    if e > width / 6:
        return dict(
            eccentricity_m=e,
            full_contact=False,
            minimum_pressure_pa=None,
            maximum_pressure_pa=None,
            partial_contact_analysis_required=True,
        )
    mean = vertical / (width * length)
    return dict(
        eccentricity_m=e,
        full_contact=True,
        minimum_pressure_pa=mean * (1 - 6 * e / width),
        maximum_pressure_pa=mean * (1 + 6 * e / width),
        partial_contact_analysis_required=False,
    )


def _drainage(area, cfg, prefix):
    d = cfg["drainage"]
    rows = []
    for width, depth in zip(d["channel_width_m"], d["water_depth_m"]):
        Q = channel_flow(width, depth, d["slope"], d["manning_n_s_m_third"])
        required = max(
            rational_runoff(area, i, d["runoff_coefficient"])
            for i in d["rainfall_intensity_mm_h"]
        )
        rows.append(
            variant(
                f"{prefix}-channel-{width:g}",
                dict(
                    width_m=width,
                    water_depth_m=depth,
                    slope=d["slope"],
                    manning_n=d["manning_n_s_m_third"],
                ),
                dict(
                    catchment_m2=area,
                    peak_runoff_m3_s=required,
                    rainfall_sensitivity=[
                        dict(
                            intensity_mm_h=i,
                            peak_runoff_m3_s=rational_runoff(
                                area, i, d["runoff_coefficient"]
                            ),
                        )
                        for i in d["rainfall_intensity_mm_h"]
                    ],
                    full_uniform_flow_m3_s=Q,
                    usable_uniform_flow_m3_s=Q * d["usable_capacity_fraction"],
                    illustrative_constant_peak_storage_m3=max(
                        0, required - d["allowable_outfall_m3_s"]
                    )
                    * d["storm_duration_s"],
                ),
                dict(
                    research_conveyance=status(
                        Q * d["usable_capacity_fraction"] >= required,
                        "70% of uniform-flow Manning conveyance vs 100 mm/h research peak; not inlet/backwater/IDF/flood acceptance",
                    )
                ),
            )
        )
    return rows


def _tolerances(cfg):
    t = cfg["tolerances"]
    rows = []
    for name, errors in [
        ("baseline", t["baseline_errors_m"]),
        ("survey-shim-adjustable-coping", t["repaired_errors_m"]),
    ]:
        e = sum(errors)
        lo = t["platform_nominal_gap_m"] - e
        hi = t["platform_nominal_gap_m"] + e
        rows.append(
            variant(
                "gap-" + name,
                dict(
                    independent_bounded_errors_m=errors,
                    error_order=[
                        "guideway_construction",
                        "rail_fastening",
                        "coping_installation",
                        "vehicle_static_lateral",
                    ],
                ),
                dict(
                    worst_case_error_m=e,
                    rss_diagnostic_m=math.sqrt(sum(x * x for x in errors)),
                    minimum_static_gap_m=lo,
                    maximum_static_gap_m=hi,
                    coping_adjustment_m=t["coping_adjustment_m"],
                ),
                dict(
                    static_research_gap=status(
                        lo >= t["minimum_research_gap_m"]
                        and hi <= t["maximum_research_gap_m"],
                        "Worst-case arithmetic sum against 50..100 mm OSR static research interval; dynamic swept envelope/platform accessibility limits unqualified",
                    )
                ),
            )
        )
    return rows


def _station(cfg):
    c = cfg["canopy"]
    rows = []
    L = 4.2
    for bay, I in [(6, 0.00004), (4, 0.00008), (3, 0.00016)]:
        w = c["gravity_pressure_pa"] * bay
        M = w * L * L / 2
        delta = w * L**4 / (8 * c["steel_modulus_pa"] * I)
        uplift = c["uplift_pressure_pa"] * bay * L
        rows.append(
            variant(
                f"canopy-bay-{bay}",
                dict(bay_spacing_m=bay, cantilever_m=L, rafter_inertia_m4=I),
                dict(
                    gravity_root_moment_nm=M,
                    gravity_shear_n=w * L,
                    elastic_tip_deflection_m=delta,
                    research_tip_limit_m=L / c["deflection_span_divisor"],
                    uplift_anchor_couple_tension_n=c["uplift_pressure_pa"]
                    * bay
                    * L**2
                    / (2 * c["anchor_lever_m"]),
                    uplift_vertical_n=uplift,
                ),
                dict(
                    deflection=status(
                        delta <= L / c["deflection_span_divisor"],
                        "Uniform cantilever elastic model and L/200 OSR research target; actual portal brace/joint stiffness and steel resistance unknown",
                    )
                ),
            )
        )
    canopy = investigation(
        "canopy-root-and-bay-repair",
        "Catalogue 6 m bay, 3.5 m platform plus .7 m eave; pressures and I are research hypotheses",
        rows,
        ["canopy"],
        "Exact UDL cantilever actions/deflection; reduced bay and increased I repair",
    )
    aux = []
    for depth in [1, 2, 2.5]:
        M = 1000 * 8.5 * 22**2 / 8
        N = M / depth
        aux.append(
            variant(
                f"aux-truss-{depth}",
                dict(span_m=22, tributary_bay_m=8.5, truss_depth_m=depth),
                dict(
                    gravity_moment_nm=M,
                    chord_force_pair_n=N,
                    end_reaction_n=1000 * 8.5 * 22 / 2,
                    roof_area_m2=187,
                ),
                dict(
                    envelope=status(
                        depth >= 2,
                        "Catalogue 2m truss reservation retained; chord/web/joint buckling and reversal resistance unknown",
                    )
                ),
            )
        )
    approach = []
    for length in cfg["approach"]["pedestrian_lengths_m"]:
        slope = 0.35 / length
        approach.append(
            variant(
                f"access-ramp-{length}",
                dict(
                    rise_m=0.35, run_m=length, clear_width_m=1.8, landing_length_m=1.8
                ),
                dict(
                    gradient=slope,
                    landing_count=2,
                    overall_reserved_length_m=length + 3.6,
                ),
                dict(
                    gradient=status(
                        slope <= 0.05,
                        "1:20 OSR research gradient only; Iraqi accessibility rules, guards, lifts, crowd/evacuation/fire and drainage absent",
                    )
                ),
            )
        )
    plinth = []
    for width in [1.2, 1.8, 2.4]:
        available = 3.5 - width - 0.4
        plinth.append(
            variant(
                f"passenger-plinth-{width}",
                dict(
                    platform_width_m=3.5,
                    service_plinth_width_m=0.4,
                    equipment_door_sweep_m=width,
                ),
                dict(
                    remaining_clear_walkway_m=available, minimum_reserved_walkway_m=1.8
                ),
                dict(
                    access=status(
                        available >= 1.8,
                        "Reserved 1.8m clear route with equipment door open; actual passenger demand, cabinet GA, anchorage and access standards unknown",
                    )
                ),
            )
        )
    charging = []
    for offset in [0.5, 1.2, 1.8]:
        charging.append(
            variant(
                f"charging-offset-{offset}",
                dict(
                    cabinet_m=[2, 1, 2.2],
                    maintainer_zone_m=1.2,
                    offset_from_walkway_m=offset,
                    pad_m=[2.4, 1.4, 0.3],
                ),
                dict(
                    clear_maintenance_width_m=offset,
                    illustrative_equipment_weight_n=2000 * 9.80665,
                    pad_contact_pressure_pa=(
                        2000 * 9.80665 + 2.4 * 1.4 * 0.3 * 2500 * 9.80665
                    )
                    / (2.4 * 1.4),
                ),
                dict(
                    access=status(
                        offset >= 1.2,
                        "Research 1.2m maintainer zone; live electrical clearances, cable bends, earthing, HVAC, actual cabinet loads and vehicle charging alignment unknown",
                    )
                ),
            )
        )
    turnout = []
    for length, ratio in [(27, 9), (43, 14), (60, 18.5)]:
        width = 1.435 + 0.3 + length / ratio
        for reserve in [5, 8]:
            turnout.append(
                variant(
                    f"turnout-{ratio}-{reserve}",
                    dict(
                        catalogue_length_m=length,
                        tangent_ratio=ratio,
                        available_width_m=reserve,
                        service_strip_each_side_m=1,
                    ),
                    dict(
                        catalogue_footprint_width_m=width,
                        required_with_access_m=width + 2,
                        drain_offset_from_track_m=width / 2 + 0.5,
                    ),
                    dict(
                        civil_access=status(
                            reserve >= width + 2,
                            "Exact catalogue planning-footprint formula plus two1m service strips; turnout supplier GA, kinematic swept path, point-machine/cable/drain clashes unknown",
                        )
                    ),
                )
            )
    depot = []
    for throat in [80, 120, 160]:
        length = throat + 160 + 180 + 40
        depot.append(
            variant(
                f"depot-throat-{throat}",
                dict(
                    throat_m=throat,
                    stabling_track_m=160,
                    workshop_m=[180, 45, 12],
                    stalls=10,
                    track_centres_m=6,
                ),
                dict(
                    site_length_m=length,
                    site_width_m=80,
                    catalogue_minimum_throat_m=120,
                    throat_turnout_27m_count=math.floor(throat / 27),
                ),
                dict(
                    throat=status(
                        throat >= 120,
                        "120m retained depot throat plus separate160m six-car planning tracks; actual ladder alignment and stopping/fouling clearances unknown",
                    )
                ),
            )
        )
    service = []
    for aisle in [0.6, 1.2, 1.8]:
        service.append(
            variant(
                f"depot-services-{aisle}",
                dict(
                    bay_pitch_m=6,
                    train_envelope_width_m=2.65,
                    research_service_spine_width_m=0.6,
                    clear_aisle_each_side_m=aisle,
                ),
                dict(
                    width_required_m=2.65 + 0.6 + 2 * aisle,
                    inspection_pit_m=[120, 1.2, 1.5],
                    pit_research_water_head_m=1.5,
                    pit_research_hydrostatic_pressure_pa=1000 * 9.80665 * 1.5,
                ),
                dict(
                    bay_fit=status(
                        2.65 + 0.6 + 2 * aisle <= 6,
                        "6m depot spacing; simultaneous side aisles and .6m service spine; pit wall structural, groundwater, vehicle lift and actual workshop equipment remain open",
                    )
                ),
            )
        )
    common = [
        "Accepted Baghdad wind/seismic, steel grades, joints, anchors, foundations and corrosion/fire requirements",
        "Actual site coordinates, passenger demand, accessibility and independent qualified design review",
    ]
    return [
        package(
            "STN-FRP-020",
            "Platform canopy roots, framing and foundations",
            [canopy],
            common,
        ),
        package(
            "STN-FRP-030",
            "Auxiliary 22m solar canopy truss",
            [
                investigation(
                    "auxiliary-truss-chord-force",
                    "8.5×22m catalogue module; gravity1kPa research",
                    aux,
                    ["auxiliary"],
                    "Simply supported UDL moment divided by chord couple depth",
                )
            ],
            common,
        ),
        package(
            "STN-FRP-050",
            "Pedestrian ramps, landings and core reservations",
            [
                investigation(
                    "stepfree-approach",
                    "350mm station/ToR datum; pedestrian alignment illustrative",
                    approach,
                    ["edge", "interfaces"],
                    "Rise/run and exact reserved landings",
                )
            ],
            common
            + [
                "Lift/stair/overbridge actual structural scheme, equipment, fire evacuation and door/headroom/access cases"
            ],
        ),
        package(
            "STN-FRP-040",
            "Passenger services plinth and maintenance circulation",
            [
                investigation(
                    "passenger-plinth-open-door",
                    "Platform3.5m geometry and explicit assumed service sweep",
                    plinth,
                    ["canopy", "platform"],
                    "Worst-case width allocation with doors open",
                )
            ],
            common
            + [
                "Actual PIS/CCTV/ticketing/lighting cabinet configurations and utilities"
            ],
        ),
        package(
            "STN-FRP-060",
            "Charging cabinet pad and maintainer access",
            [
                investigation(
                    "charging-cabinet-site-interface",
                    "2t cabinet is OSR research scenario, not supplier mass",
                    charging,
                    ["interfaces", "station_layout"],
                    "Clear zone and nominal dead-weight bearing pressure",
                )
            ],
            common
            + [
                "Charging equipment GA, protection, electrical segregation, live clearances, thermal rejection and accepted foundation reactions"
            ],
        ),
        package(
            "STN-FRP-070",
            "Turnout civil, cable and drainage clearance",
            [
                investigation(
                    "catalogue-turnout-width-repair",
                    "Catalogue 1:9/14/18.5 planning dimensions",
                    turnout,
                    ["turnout"],
                    "Catalogue gauge+.3+L/tangent width and access allocation",
                )
            ],
            [
                "Supplier rail/blade/actuator and detection GA; accepted railway forces, trackform, earthing, drainage invert and vehicle swept envelope"
            ],
        ),
        package(
            "STN-FRP-080",
            "Depot throat, track and drainage envelope",
            [
                investigation(
                    "depot-throat-footprint",
                    "Catalogue180m main shed,160m tracks,120m throat",
                    depot,
                    ["depot", "turnout"],
                    "Direct catalogue footprint decomposition",
                ),
                investigation(
                    "depot-drainage",
                    "80×500m illustrative main-heavy catchment; no site rainfall",
                    _drainage(40000, cfg, "depot"),
                    ["depot"],
                    "Rational peak and Manning uniform flow",
                ),
            ],
            [
                "Survey/land ownership, real ladder geometry, geotechnics, flood datum, outfall/IDF and contaminated washwater segregation"
            ],
        ),
        package(
            "STN-FRP-090",
            "Depot workshop service aisle and pit interfaces",
            [
                investigation(
                    "depot-service-cross-section",
                    "6m track spacing;2.65m train research width",
                    service,
                    ["depot"],
                    "Additive cross-section and hydrostatic-equivalent wall pressure demand",
                )
            ],
            [
                "Actual six-car envelope/lifting jacks, wheel-lathe and bogie-change machinery; pit groundwater, RC, ventilation, extraction, earthing, emergency egress and washwater treatment"
            ],
        ),
    ]


def _civil_packages(cfg, beam, reaction_basis):
    span = beam["scenarios"][1]
    dead = span["known_concrete_plus_strand_mass_kg"] * 9.80665
    # Four independent end maxima are a conservative research envelope, not
    # a traffic simultaneity or accepted railway load combination.
    live_reaction = reaction_basis["maximum_live_reaction_n"]
    end = dead / 2 + live_reaction
    total = 4 * end
    ys = [-2.4675, -1.0325, 1.0325, 2.4675]
    # Two longitudinal bearings per web combine to one beam-end resultant.
    centreline_moment = end * (2.4675 + 1.0325)
    column_side_face_y = 2.0 / 2
    face_moment = end * sum(y - column_side_face_y for y in (2.4675, 1.0325))
    cap = []
    for depth in [1.2, 1.5, 1.8]:
        cap.append(
            variant(
                f"pier-cap-depth-{depth}",
                dict(
                    cap_m=[2.5, 7, depth],
                    column_m=[1.5, 2, 8],
                    bearing_y_m=ys,
                    beam_ends=4,
                ),
                dict(
                    one_beam_end_diagnostic_n=end,
                    one_beam_end_dead_reaction_n=dead / 2,
                    one_beam_end_live_reaction_n=live_reaction,
                    total_support_diagnostic_n=total,
                    one_side_cap_column_centreline_moment_nm=centreline_moment,
                    one_side_cap_column_face_moment_nm=face_moment,
                    column_side_face_y_m=column_side_face_y,
                    average_column_compression_demand_pa=total / (1.5 * 2),
                    illustrative_braking_base_moment_nm=total
                    * cfg["site"]["research_pier_braking_fraction"]
                    * 8,
                    cap_solid_upper_mass_kg=2.5 * 7 * depth * 2500,
                    existing_hollow_cap_concrete_mass_kg=(2.5 * 7 * 1.2 - 2 * 6.5 * 0.8)
                    * 2500,
                    nominal_couple_force_n=face_moment / (0.8 * depth),
                    support_reaction_basis=reaction_basis,
                ),
                dict(
                    web_line_alignment=status(
                        all(abs(y) < 3.5 for y in ys),
                        "Actual shared cap web-axis geometry; eight bearings(two rows) combine to four transverse resultants; stiffness, RC and actual continuity distribution unqualified",
                    )
                ),
            )
        )
    bearing = []
    m = cfg["movement"]
    for length, travel in zip(m["unit_lengths_m"], m["travel_reservations_m"]):
        demand = (
            length
            * (
                m["thermal_expansion_per_k"] * m["temperature_range_k"]
                + m["shrinkage_strain"]
            )
            + m["installation_allowance_m"]
        )
        bearing.append(
            variant(
                f"bearing-unit-{length}",
                dict(
                    expansion_length_m=length,
                    travel_reservation_m=travel,
                    bearing_m=[0.6, 0.5, 0.1],
                ),
                dict(
                    full_temperature_range_travel_m=length
                    * m["thermal_expansion_per_k"]
                    * m["temperature_range_k"],
                    shrinkage_offset_m=length * m["shrinkage_strain"],
                    combined_one_direction_envelope_m=demand,
                    nominal_end_pressure_pa=(end / 2) / (0.6 * 0.5),
                    one_beam_end_live_reaction_n=live_reaction,
                    research_jack_load_each_n=1.1 * end / 2,
                    support_reaction_basis=reaction_basis,
                    jack_reservation_m=[0.25, 0.5, 0.08],
                ),
                dict(
                    travel=status(
                        travel >= demand,
                        "Conservative additive thermal range+shrinkage+installation reservation; thermal strain range not ±range; creep, braking, bearing rotation and actual fixity unknown",
                    )
                ),
            )
        )
    replacement = []
    for height in [0.02, 0.1, 0.2, 0.3]:
        needed = 0.18 + 0.05 + 0.04
        replacement.append(
            variant(
                f"bearing-jack-headroom-{height}",
                dict(
                    available_jack_height_m=height,
                    proposed_bearing_pedestal_above_cap_m=max(0, height + 0.08 - 0.1),
                    assumed_jack_closed_height_m=0.18,
                    stroke_m=0.05,
                    pack_m=0.04,
                ),
                dict(
                    required_height_m=needed,
                    extraction_width_m=0.6,
                    temporary_web_reaction_n=end / 2 * 1.1,
                    support_reaction_basis=reaction_basis,
                ),
                dict(
                    jack_access=status(
                        height >= needed,
                        "Supplier-independent explicit jack envelope; height created by raised bearing pedestal over cap (.08m jack pad, .1m bearing); grade/interface and pedestal RC redesign required, no certified jack selection",
                    )
                ),
            )
        )
    transition = []
    for L in cfg["approach"]["transition_lengths_m"]:
        rotation = 0.02 / L
        transition.append(
            variant(
                f"transition-{L}",
                dict(
                    length_m=L,
                    width_m=3.2,
                    thickness_m=0.42,
                    differential_settlement_m=0.02,
                ),
                dict(
                    chord_rotation_rad=rotation,
                    concrete_volume_m3=L * 3.2 * 0.42,
                    nominal_settlement_ramp_gradient=rotation,
                ),
                dict(
                    rotation=status(
                        rotation <= 0.002,
                        "2mm/m OSR research rotation target,20mm scenario differential settlement; soil/rail stress/dynamic response unqualified",
                    )
                ),
            )
        )
    tolerances = investigation(
        "static-platform-tolerance-repair",
        "75mm source static gap; bounded error allowances are OSR research",
        _tolerances(cfg),
        ["station_layout", "edge", "slab"],
        "Arithmetic worst-case stack; RSS diagnostic is not acceptance",
    )
    platform = []
    for pitch in [0.65, 0.6, 0.5]:
        count = math.ceil(6 / pitch)
        actual = 6 / count
        edge = actual / 2 - 0.26 / 2
        platform.append(
            variant(
                f"fastener-seat-{pitch}",
                dict(panel_length_m=6, maximum_pitch_m=pitch, baseplate_length_m=0.26),
                dict(
                    seat_count=count,
                    actual_pitch_m=actual,
                    first_seat_centre_m=actual / 2,
                    edge_footprint_clearance_m=edge,
                    platform_unit_length_m=3,
                    platform_L_gross_volume_m3=3 * (0.15 * 1.1 + (2.5 - 0.15) * 0.2),
                ),
                dict(
                    seat_footprint=status(
                        edge >= 0,
                        "Exact centred-seat catalogue construction; anchor edge distances, rail loads, slab reinforcement and earthing unqualified",
                    )
                ),
            )
        )
    return [
        package(
            "CIV-FRP-110",
            "Shared pier cap and column diagnostic load path",
            [
                investigation(
                    "four-beam-end-shared-pier",
                    f"Four Pi25 ends plus four independent {reaction_basis['mode']} support maxima form conservative research envelope; not a simultaneous traffic/load combination",
                    cap,
                    ["pier", "beam_search", reaction_basis["source_key"]],
                    "Vertical equilibrium and actual web axes; separate cap moments at column centreline and side face y=±1m; chord couple uses side-face moment",
                )
            ],
            [
                "Accepted six-car actions/continuity distribution, RC cap strut-and-tie, column seismic/collision, foundations/geotechnics, cap lifting and erection"
            ],
            ["pier-bearing-model"],
        ),
        package(
            "CIV-FRP-120",
            "Bearing movement, loads and replacement",
            [
                investigation(
                    "movement-and-jack-demand",
                    "Inherited600×500×100mm bearing reservations; no supplier capacity",
                    bearing,
                    ["pier", "interfaces"],
                    "Thermal+shrinkage travel; end reaction shared between two web bearings",
                ),
                investigation(
                    "replacement-headroom-repair",
                    "Dedicated jacking platform required separate from bearing gap",
                    replacement,
                    ["pier", "interfaces"],
                    "Explicit closed height+stroke+packing fit",
                ),
            ],
            [
                "Bearing supplier compression/shear/rotation/fatigue/temperature approval, fixed-guided-free restraint scheme, jacking local RC resistance and actual replacement method",
                "Proposed280mm bearing pedestals raise beam/rail datum280mm unless cap or geometry changes; grade, approach, clearance and local RC constraints require actual coordinated redesign",
            ],
            ["pier-bearing-model"],
        ),
        package(
            "CIV-FRP-130",
            "At-grade panels and graded transitions",
            [
                investigation(
                    "settlement-transition-length-repair",
                    "Catalogue12×3.2×.42m transition,20mm OSR settlement sensitivity",
                    transition,
                    ["interfaces", "slab"],
                    "Chord rotation and cast volume",
                )
            ],
            [
                "Accepted settlement/ground stiffness and ballastless transition reinforcement, fatigue, drainage, stray-current and fastener/rail interaction"
            ],
        ),
        package(
            "CIV-INT-200",
            "Track seat, tolerance and station deck interfaces",
            [
                tolerances,
                investigation(
                    "centred-fastener-seat-layout",
                    "Catalogue6m module and260mm baseplate footprint",
                    platform,
                    ["slab", "platform"],
                    "Equal-cell seat coordinates/edge footprint",
                ),
            ],
            [
                "Measured survey/installation tolerances, accepted fastener adjustability and anchorage, rail-structure interaction and station deck capacity"
            ],
        ),
        package(
            "CIV-INT-210",
            "Vehicle/platform swept envelope and coping adjustment",
            [tolerances],
            [
                "Actual six-car kinematic envelope, suspension/track wear/twist/wind/curvature and boarding/accessibility limits; static75mm gap alone insufficient"
            ],
        ),
        package(
            "STN-FRP-010",
            "Platform L-unit, edge channel and drainage",
            [
                investigation(
                    "platform-unit-and-drain",
                    "Actual3m L-unit and350mm platform/ToR datum",
                    platform,
                    ["platform", "edge"],
                    "Nonoverlapping L-section volume and fastening coordination",
                ),
                investigation(
                    "platform-channel-sizing",
                    "One6×4.2m canopy bay runoff100mm/h research",
                    _drainage(25.2, cfg, "station"),
                    ["edge", "canopy"],
                    "Rational peak and rectangular Manning flow",
                ),
            ],
            [
                "Platform crowd/impact actions, retaining/foundation/reinforcement, edge loading, tactile/boarding dimensions, actual drainage outfall and accessibility"
            ],
        ),
    ]


def _factory(cfg, beam):
    s = cfg["strongback"]
    F = beam["metrics"]["initial_force_per_strand_n"]
    N = beam["variables"]["strand_count"]
    P = N * F
    plate = []
    for t, L in zip(s["plate_thickness_m"], s["local_strip_span_m"]):
        stress = 6 * (F * L / 4) / (0.06 * t * t)
        plate.append(
            variant(
                f"strongback-strip-{t}",
                dict(
                    face_plate_thickness_m=t,
                    local_support_span_m=L,
                    tributary_strip_width_m=0.06,
                ),
                dict(
                    per_hole_force_n=F,
                    local_strip_bending_demand_pa=stress,
                    hole_bearing_demand_pa=F / (s["hole_diameter_m"] * t),
                    net_ligament_m=0.06 - s["hole_diameter_m"],
                    total_initial_prestress_n=P,
                ),
                dict(
                    research_strip_target=status(
                        stress <= s["research_nominal_stress_target_pa"],
                        "250MPa research optimisation target only; not material yield/allowable, weld or plate/contact resistance",
                    )
                ),
            )
        )
    tool = []
    for pitch in s["pitch_m"]:
        holegap = pitch - 0.05
        jackgap = pitch - 0.09
        tool.append(
            variant(
                f"grip-jack-pitch-{pitch}",
                dict(
                    pitch_m=pitch,
                    grip_envelope_diameter_m=0.05,
                    assumed_jack_nose_diameter_m=0.09,
                ),
                dict(
                    grip_surface_gap_m=holegap,
                    jack_to_adjacent_grip_gap_m=pitch - (0.09 + 0.05) / 2,
                    adjacent_jack_surface_gap_m=jackgap,
                    initial_force_n=P,
                ),
                dict(
                    grip_fit=status(
                        holegap >= 0.005 - 1e-10,
                        "Existing50mm candidate grip +5mm research gap",
                    ),
                    simultaneous_jack_fit=status(
                        jackgap >= 0.005 - 1e-10,
                        "90mm OSR assumed jack nose, not supplier GA;100mm candidate routing pitch fits, requires new splayed transfer/grip layout",
                    ),
                ),
            )
        )
    tool.append(
        variant(
            "straight-tails-four-axial-tiers",
            dict(
                tendon_pitch_m=0.06,
                axial_tier_count=4,
                axial_tier_pitch_m=0.25,
                assumed_jack_axial_length_m=0.2,
                assumed_jack_diameter_m=0.09,
                tail_free_length_m=1.25,
                assumed_available_stroke_m=0.2,
            ),
            dict(
                same_tier_minimum_axis_spacing_m=0.12,
                same_tier_jack_surface_gap_m=0.12 - 0.09,
                adjacent_tier_jack_axial_gap_m=0.25 - 0.2,
                jack_to_adjacent_straight_strand_gap_m=0.06 - 0.09 / 2 - 0.0152 / 2,
                maximum_stagger_offset_m=0.75,
                extra_tail_elastic_extension_m=F * 1.25 / (195e9 * 0.00014),
                beam25_elastic_extension_m=F * 25 / (195e9 * 0.00014),
                total_initial_prestress_n=P,
                per_grip_seat_force_n=F,
            ),
            dict(
                research_tool_envelopes=status(
                    0.06 - 0.09 / 2 - 0.0152 / 2 >= 0.005,
                    "Four-color2×2 grid routing preserves straight60mm tendon axes; assumed90mm×200mm jacks on250mm axial tiers; local envelopes only",
                ),
                stroke=status(
                    0.2 >= F * 26.25 / (195e9 * 0.00014),
                    "Elastic strand extension estimate only; seating losses, hydraulic stroke and supplier limits unknown",
                ),
                staggered_seat_resistance=dict(
                    status="unknown",
                    basis=f"Each staggered grip seat/standoff must transfer{F/1000:g}kN;{P/1e6:g}MN total path, standoff buckling/bending, sockets, welds, sequential interference and actual supplier tool/tail access unresolved",
                ),
            ),
        )
    )
    endzone = []
    for L in s["transfer_lengths_m"]:
        bond = F / (math.pi * 0.0152 * L)
        endzone.append(
            variant(
                f"transfer-length-{L}",
                dict(
                    assumed_transmission_length_m=L, strand_clearance_diameter_m=0.0152
                ),
                dict(
                    average_force_transfer_bond_demand_pa=bond,
                    transferred_force_per_stem_n=P / 2,
                    assumed_transfer_zone_within_550mm_endfill=L <= 0.55,
                ),
                dict(
                    bond_and_transmission=dict(
                        status="unknown",
                        basis="Sensitivity domain only; transmission length and bond resistance not determined from clearance diameter or this average-bond demand",
                    )
                ),
            )
        )
    mould = []
    # Full pour surface is at the top of the flange, so bottom form pressure
    # includes the flange head as well as the stem depth.
    h = beam["variables"]["depth_m"]
    for spacing, t in zip(
        s["mould_panel_stiffener_spacing_m"], s["mould_plate_thickness_m"]
    ):
        p = 2500 * 9.80665 * h
        I = t**3 / 12
        delta = 5 * p * spacing**4 / (384 * s["steel_modulus_pa"] * I)
        mould.append(
            variant(
                f"mould-panel-{spacing}",
                dict(
                    stiffener_spacing_m=spacing,
                    steel_skin_thickness_m=t,
                    waterlike_head_m=h,
                ),
                dict(
                    hydrostatic_peak_pressure_pa=p,
                    side_resultant_n_per_m=2500 * 9.80665 * h * h / 2,
                    uniform_peak_pressure_strip_deflection_m=delta,
                    uniform_peak_pressure_bending_demand_pa=(p * spacing**2 / 8)
                    * 6
                    / t**2,
                ),
                dict(
                    research_skin_deflection=status(
                        delta <= 0.001,
                        "Uniform peak fluid pressure over simply-supported1m steel strip;1mm OSR target only; concrete rate/vibration/temperature and stiffener/weld/skin resistance unknown",
                    )
                ),
            )
        )
    slabs = []
    for h in cfg["slab"]["thickness_m"]:
        response = beam_strip(100000, 1, 1, h, 30e9)
        slabs.append(
            variant(
                f"factory-slab-{h}",
                dict(
                    thickness_m=h,
                    research_point_load_n=100000,
                    local_void_span_m=1,
                    strip_width_m=1,
                ),
                response,
                dict(
                    geometric_depth=status(
                        h >= 0.3,
                        "300mm OSR manufacturing-floor reservation repair from250mm baseline; bending demand is uncracked strip, not RC/ground design",
                    )
                ),
            )
        )
    a = _read(ROOT / SOURCES["factory_basis"])["assumptions"]
    dev = _read(ROOT / SOURCES["factory_development"])
    runway = development.runway(a, dev["runway"])
    pads = []
    vertical = runway["two_adjacent_bays_column_gravity_envelope_n"]
    moment = runway["horizontal_column_base_moment_scenario_nm"]
    for b in cfg["site"]["foundation_width_m"]:
        weight = b * b * 1.2 * 2500 * 9.80665
        res = contact_pressure(vertical + weight, moment, b, b)
        pads.append(
            variant(
                f"runway-pad-{b}",
                dict(
                    pad_m=[b, b, 1.2],
                    assumed_column_gravity_n=vertical,
                    horizontal_base_moment_nm=moment,
                ),
                res,
                dict(
                    full_contact=status(
                        res["full_contact"],
                        "Middle-third geometric contact only; ground allowable/settlement/sliding/uplift/RC resistance UNKNOWN",
                    )
                ),
            )
        )
    frame = []
    for depth in [1.5, 2, 2.5]:
        M = 0.6e3 * 12 * 30**2 / 8
        frame.append(
            variant(
                f"hall-truss-{depth}",
                dict(span_m=30, frame_spacing_m=12, depth_m=depth),
                dict(
                    gravity_root_moment_nm=M,
                    ideal_chord_pair_force_n=M / depth,
                    gravity_end_reaction_n=0.6e3 * 12 * 30 / 2,
                ),
                dict(
                    truss_envelope=status(
                        depth >= 2,
                        "Roof-only600Pa retained dead load;2m research truss reservation, no wind/seismic/live actions or member/joint buckling resistance",
                    )
                ),
            )
        )
    return [
        package(
            "FACTORY-PRECAST",
            f"{N}-strand strongback, jack access, transmission and split mould",
            [
                investigation(
                    "strongback-hole-strip-repair",
                    f"154kN per strand;{P/1e6:g}MN new initial force; no existing bed resistance inherited",
                    plate,
                    ["connections", "beam_search"],
                    "Single154kN point load on bounded face-plate support strips",
                ),
                investigation(
                    "jack-grip-access-repair",
                    "50mm inherited candidate grip,90mm new explicit assumed jack nose",
                    tool,
                    ["connections"],
                    "Centre pitch minus envelope diameters",
                ),
                investigation(
                    "endzone-average-bond-demand",
                    f"{N} strands; assumed transmission lengths are sensitivities only",
                    endzone,
                    ["beam_search"],
                    "Force/(nominal circular perimeter×length), not a bond resistance or accepted transmission model",
                ),
                investigation(
                    "mould-steel-skin-repair",
                    f"Full selected{h:g}m concrete pour head; fluid-head pressure assumption",
                    mould,
                    ["connections", "beam_search"],
                    "Hydrostatic pressure and conservative uniform-peak1m strip bending/deflection",
                ),
            ],
            [
                f"{N}-strand return boxes/braces/strongbacks/new temporary stressing stages and foundations need coupled load path resistance",
                "100mm grip/tool routing pitch cannot preserve current straight60mm tendon alignment without actual deflected/splayed transfer and new design;90mm assumed jack access is unqualified",
                "550mm end fills do not establish transfer/end-zone reinforcement; bond/bursting/splitting/local reinforcement and material limits unknown",
                "Collapsible/removable segmented intrados tooling with end fills, actual rebar/inserts, stripping clearance/draft/suction/sequence, welding/flatness and trial release",
            ],
            ["mould-strongback-model"],
        ),
        package(
            "FACTORY-SITE",
            "Factory grading, catchments, channels and drainage storage",
            [
                investigation(
                    "yard-and-hall-channel-repair",
                    "160×100m yard plus120×72m hall, synthetic100mm/h storm",
                    _drainage(16000 + 8640, cfg, "factory"),
                    ["factory", "factory_basis"],
                    "Rational runoff, Manning open-channel uniform conveyance and constant-peak storage sensitivity",
                )
            ],
            [
                "Actual Baghdad topographic/utility survey, geotechnics, rainfall IDF/duration, inlet/blockage/backwater/flood level/outfall consent",
                "Storage is constant-peak rectangular15min sensitivity, not a routed design hydrograph; oily/washwater systems remain separate and need treatment",
            ],
        ),
        package(
            "FACTORY-BUILDINGS",
            "Hall truss, machine slab, runway reactions and pads",
            [
                investigation(
                    "roof-frame-depth",
                    "Actual30m span/12m bay and600Pa roof dead load",
                    frame,
                    ["factory", "factory_basis"],
                    "Uniform beam moment and ideal truss chord couple",
                ),
                investigation(
                    "factory-local-slab-void",
                    "100kN single-wheel1m hypothetical unsupported strip",
                    slabs,
                    ["factory_basis"],
                    "Exact simply-supported centre point load and gross elastic strip",
                ),
                investigation(
                    "runway-column-pad-contact",
                    "Existing125t planning crane,30m bridge,two wheels/runway,6m bay; supplier configuration unaccepted",
                    pads,
                    ["factory_development"],
                    "Reuse actual two-wheel travel envelope and separate horizontal research base moment; middle-third full-contact test",
                ),
                dict(
                    id="runway-retained-demand",
                    basis="Existing analytical demand only; supplier reactions/resistance remain unknown",
                    method="Existing factory_examples.development.runway",
                    source_paths=[SOURCES["factory_development"]],
                    metrics=runway,
                    engineering_design_complete=False,
                ),
            ],
            [
                "Wind/seismic/roof live loads and crane duty/actions, actual supplier wheel/rail/column/base reactions, steel buckling/joints/fatigue",
                "Floor wheel/contact, joints/dowels/fibre/rebar/cracking, machine dynamic forces/vibration, pits/utilities and ground support unknown",
                "No soil capacity from pad pressures: real bearing, settlement, sliding, partial contact, piles, RC anchorage and foundation tests required",
            ],
        ),
    ]


def run(*, beam_variables=None, provisional_six_car_support_reaction_n=None):
    cfg = _read(DATA)
    audit = _audit()
    if provisional_six_car_support_reaction_n is not None and (
        type(provisional_six_car_support_reaction_n) not in (int, float)
        or not math.isfinite(provisional_six_car_support_reaction_n)
        or provisional_six_car_support_reaction_n < 0
    ):
        raise ValueError(
            "finite nonnegative provisional six-car support reaction in N required"
        )
    legacy_reaction = civil._live(25)["maximum_total_reaction_n"]
    supplied = provisional_six_car_support_reaction_n is not None
    source_key = "provisional_axles" if supplied else "legacy_axles"
    reaction_basis = dict(
        mode=(
            "provisional-six-car-sensitivity"
            if supplied
            else "legacy-three-car-diagnostic"
        ),
        maximum_live_reaction_n=(
            provisional_six_car_support_reaction_n if supplied else legacy_reaction
        ),
        legacy_three_car_maximum_live_reaction_n=legacy_reaction,
        source_key=source_key,
        source_path=SOURCES[source_key],
        source_method=(
            "integration.live_envelopes: caller-supplied maximum_live_reaction_n over explicit provisional six-car sensitivities"
            if supplied
            else "civil._live(25): retained three-car12-axle planning reference"
        ),
        caller_supplied=supplied,
        accepted=False,
        dead_reaction_scope="Known gross concrete plus strand-displacement mass only; conventional reinforcement, track plinth/rail/fasteners, equipment, surfacing and attachments are additional unresolved permanent actions",
        scope="One Pi25 beam-end maximum; independent maxima conservatively repeated over four beam ends. No continuity/traffic simultaneity or accepted railway load combination adopted.",
    )
    # Re-evaluate an exact selected proposal rather than trusting prior files.
    beam = civil.assess(
        beam_variables
        or dict(
            depth_m=1.4,
            stem_width_m=0.3,
            strand_count=112,
            lower_strand_fraction=0.75,
            lift_fraction=0.22,
        )
    )
    packages = (
        _station(cfg) + _civil_packages(cfg, beam, reaction_basis) + _factory(cfg, beam)
    )
    packages.append(
        package(
            "CIV-FRP-100",
            "Pi20/Pi25 section, strand and end-zone coordination",
            [
                dict(
                    id=f"actual-{beam['variables']['strand_count']}-strand-beam-reassessment",
                    basis="Legacy three-car12-axle diagnostic only; accepted six-car load absent",
                    source_paths=[SOURCES["beam_search"]],
                    metrics=beam["metrics"],
                    section=beam["section"],
                    tendon_rows=beam["tendon_rows"],
                    scenarios=beam["scenarios"],
                    checks=beam["checks"],
                    engineering_design_complete=False,
                )
            ],
            [
                "All actual beam remaining gates retained: six-car railway loading, concrete/strand/material strength/losses, end zones, shear/torsion/fatigue/deflection, reinforcement, bearing/lift/transport and independent qualification"
            ],
            ["mould-strongback-model"],
        )
    )
    return dict(
        schema="osr-generative-civil-systems/1",
        research_basis=cfg,
        source_inventory=audit,
        primary_references=REFERENCES,
        packages=packages,
        work_package_count=len(packages),
        beam_candidate=beam,
        support_reaction_basis=reaction_basis,
        beam_scope="112-strand1.4m proposal follows orchestrator provisional six-car shortlist. Beam stresses recomputed in THIS module remain the retained three-car12-axle diagnostic only; six-car numerical verification belongs to the separate orchestrator load study. No actual accepted railway loads adopted.",
        limits="Local research investigations complete only; no RC/soil/crash/fire/lifting/material/code or physical release acceptance. Missing project inputs stay unknown.",
        engineering_design_complete=False,
        physical_release=False,
    )


def _mould_model(report):
    beam = report["beam_candidate"]
    parts = civil.native_model(beam)["parts"]
    # A single transverse tool-access study rather than duplicating full25m steel.
    parts = [p for p in parts if p["role"] != "strand-envelope"]
    z0 = -0.15
    holes = [
        dict(axis="x", y_m=p["y_m"] + 2, z_m=p["z_m"] - z0, diameter_m=0.022)
        for p in beam["strand_points"]
    ]
    parts.append(
        part(
            f"{beam['variables']['strand_count']}-hole-front-plate",
            [0.08, 4, 1.5],
            [-0.8, -2, z0],
            holes=holes,
            role="strongback-steel",
        )
    )
    # Separate exploded segmented forms, not certified demouldable mechanism.
    for j, (lo, hi) in enumerate([(-1.45, -0.8675), (-0.5675, 0.5675), (0.8675, 1.45)]):
        parts.append(
            part(
                f"exploded-removable-core-{j}",
                [1, hi - lo, 0.8],
                [3, lo, -1.5],
                role="proposed-tool-envelope",
            )
        )
    for j, y in enumerate([-1.5, 1.5]):
        parts.append(
            part(
                f"opened-side-form-{j}",
                [25, 0.01, beam["variables"]["depth_m"]],
                [0, y, 0],
                role="proposed-tool-envelope",
            )
        )
    return dict(
        id=f"OSR-GENERATIVE-{beam['variables']['strand_count']}-STRAND-TOOL-INTERFACES",
        parts=parts,
        physical_release=False,
        notes="Gross concrete+80mm perforated faceplate; exploded1m segmented intrados envelopes and opened side forms. No represented mechanism, qualified strip/draft/rebar/access/steel resistance or demouldability.",
    )


def _pier_model():
    parts = [part("column", [1.5, 2, 8], [-0.75, -1, 0])]
    # Nonoverlapping rectangular cap shell, exact actual catalogue void.
    parts.extend(
        [
            part("cap-bottom", [2.5, 7, 0.2], [-1.25, -3.5, 8]),
            part("cap-top", [2.5, 7, 0.2], [-1.25, -3.5, 9]),
            part("cap-side-a", [0.25, 7, 0.8], [-1.25, -3.5, 8.2]),
            part("cap-side-b", [0.25, 7, 0.8], [1, -3.5, 8.2]),
            part("cap-end-a", [2, 0.25, 0.8], [-1, -3.5, 8.2]),
            part("cap-end-b", [2, 0.25, 0.8], [-1, 3.25, 8.2]),
        ]
    )
    for j, y in enumerate([-2.4675, -1.0325, 1.0325, 2.4675]):
        for k, x in enumerate([-0.45, 0.45]):
            parts.append(
                part(
                    f"raised-pedestal-{j}-{k}",
                    [0.6, 0.5, 0.28],
                    [x - 0.3, y - 0.25, 9.2],
                    role="proposed-concrete-pedestal",
                )
            )
            parts.append(
                part(
                    f"bearing-{j}-{k}",
                    [0.6, 0.5, 0.1],
                    [x - 0.3, y - 0.25, 9.48],
                    role="supplier-envelope",
                )
            )
        parts.append(
            part(
                f"jack-pad-{j}",
                [0.25, 0.5, 0.08],
                [-0.125, y - 0.25, 9.2],
                role="jacking-interface",
            )
        )
        parts.append(
            part(
                f"jack-clearance-{j}",
                [0.25, 0.5, 0.3],
                [-0.125, y - 0.25, 9.28],
                role="maintenance-clearance",
            )
        )
    return dict(
        id="OSR-GENERATIVE-PIER-BEARING-REPLACEMENT",
        parts=parts,
        physical_release=False,
        notes="Actual7×2.5×1.2m hollow cap,8m column and eight bearings at source web/row axes. Proposed280mm pedestals raise beam/rail datum280mm to create300mm headroom above80mm jack pads. Grade, clearance, access, pedestal RC and bearing/jack resistance remain unqualified.",
    )


def write_artifacts(report, output: Path):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    results = []
    for identifier, model in [
        ("mould-strongback-model", _mould_model(report)),
        ("pier-bearing-model", _pier_model()),
    ]:
        folder = output / identifier
        folder.mkdir(exist_ok=True)
        path = folder / "model.json"
        path.write_text(json.dumps(model, indent=2, sort_keys=True) + "\n")
        results.append(dict(id=identifier, model=str(path), physical_release=False))
    return results

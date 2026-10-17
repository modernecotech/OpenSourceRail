"""Executable, source-bound civil design twins, not measured physical twins.

Three geometry/cage/support seeds and their failure-directed repairs are evaluated in each independent
vehicle/span context. Unknown procurement and site fields are explicit records,
never fabricated specifications. Numerical limits retain their research status.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from . import civil_detail, architecture_civil

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "osr-domain-design-twin/1"
SOURCES = (
    "engineering/generative_design/twin_civil.py",
    "engineering/generative_design/civil_detail.py",
    "engineering/generative_design/architecture_civil.py",
    "engineering/generative_design/architecture_mechanical.py",
    "engineering/generative_design/architecture_campaign.py",
    "engineering/generative_design/mechanical_systems.py",
    "engineering/generative_design/civil.py",
    "engineering/generative_design/data/civil-detail-space.json",
    "engineering/generative_design/data/civil-space.json",
    "engineering/generative_design/data/architecture-feedback.json",
    "engineering/factory_examples/data/basis.json",
    "engineering/design_engine/factory_beam.py",
    "engineering/design_engine/civil_qualification.py",
    "engineering/design_engine/contracts.py",
    "engineering/factory_examples/models.py",
    "engineering/factory_examples/development.py",
    "engineering/industrialisation/assembly.py",
    "engineering/industrialisation/common.py",
    "design/component-catalogue/src/osr_mech/civil/decked_pi.py",
    "design/component-catalogue/catalog/buildable-civil/reusable-type-release-register.json",
    "docs/civil/baghdad-qualification.md",
    "docs/civil/station-construction-method.md",
    "docs/commercial/baghdad-uk-factory-suppliers-2026-10-15.md",
)


def _read(path):
    return json.loads((ROOT / path).read_text())


def _part(identity, parent, title, specifications, material, process, inspections):
    return {
        "id": identity,
        "parent_id": parent,
        "title": title,
        "specifications": {
            "datum": "bay origin at beam near end, x along span, y transverse, z from beam soffit; support local vertical datum separately surveyed",
            "tolerance": {
                "value": None,
                "unit": "m",
                "state": "unknown",
                "basis": "Project and supplier tolerance stack not accepted",
            },
            "acceptance_state": "provisional-unreleased",
            **specifications,
        },
        "material": material,
        "manufacturing": {"process": process, "accepted": False},
        "inspection": {
            "requirements": inspections,
            "records": [],
            "state": "not-executed",
        },
    }


def _parts(row):
    g, v = row["geometry"], row["variables"]
    cfg = _read("engineering/generative_design/data/civil-detail-space.json")
    beam_cfg = _read("engineering/generative_design/data/civil-space.json")
    a = cfg["assumptions"]
    strand = _read("engineering/factory_examples/data/basis.json")["assumptions"]
    L = row["context_record"]["span_m"]
    concrete = {
        "family": "prestressed/reinforced concrete",
        "research_strength_pa": a["concrete_characteristic_strength_pa"],
        "accepted": False,
        "mix_design": None,
        "exposure_class": None,
    }
    rebar = {
        "family": "reinforcing steel",
        "research_yield_pa": a["steel_characteristic_yield_pa"],
        "accepted": False,
        "grade": None,
    }
    unknown_material = {"family": None, "grade": None, "accepted": False}
    result = [
        _part(
            "bay",
            None,
            f"{L:g}m single-track precast Pi bay",
            {
                "span_m": L,
                "width_m": beam_cfg["geometry"]["deck_width_m"],
                "accepted_loading": False,
                "support_count": 2,
                "scope": "Both outer-end support envelopes; each uses the moving-load maximum end-reaction envelope, not simultaneous reactions; interior shared piers excluded",
            },
            concrete,
            [
                "survey and setting-out",
                "foundations",
                "substructure",
                "precast erection",
                "bearing alignment and grout",
            ],
            ["survey closure", "independent temporary and permanent stage acceptance"],
        )
    ]
    result.append(
        _part(
            "beam",
            "bay",
            "Precast prestressed Pi beam",
            {
                "length_m": L,
                "depth_m": v["beam_depth_m"],
                "stem_width_m": v["beam_stem_width_m"],
                "section": g["beam_section"],
                "end_fill_length_m": beam_cfg["geometry"]["end_fill_length_m"],
                "strand_count": g["beam_variables"]["strand_count"],
            },
            concrete,
            row["manufacturing"]["route"],
            [
                "mould survey",
                "concrete trials",
                "release-strength witness",
                "strand elongation/force reconciliation",
                "camber and crack survey",
            ],
        )
    )
    # Individually address each tendon, preserving location and region. Grouped
    # links carry a quantity and spacing rule; uncalculated rebar has no count.
    for i, p in enumerate(architecture_civil.civil.strand_points(g["beam_variables"])):
        result.append(
            _part(
                f"strand-{i + 1:03d}",
                "beam",
                "Pretensioning strand",
                {
                    "length_in_beam_m": L,
                    "cut_length_m": None,
                    "axis_y_m": p["y_m"],
                    "axis_z_m": p["z_m"],
                    "region": p["region"],
                    "envelope_diameter_m": beam_cfg["manufacturing"][
                        "strand_envelope_diameter_m"
                    ],
                    "metallic_area_m2": strand["strand_area_m2"],
                    "research_initial_stress_pa": strand["strand_initial_stress_pa"],
                    "research_initial_force_n": strand["strand_initial_stress_pa"]
                    * strand["strand_area_m2"],
                },
                {"family": "prestressing strand", "grade": None, "accepted": False},
                [
                    "supplier certify",
                    "thread through approved grip/anchor",
                    "stress and record",
                    "controlled release and trim",
                ],
                [
                    "heat/coil trace",
                    "force and elongation",
                    "grip slip",
                    "transfer cracking",
                ],
            )
        )
    for i, y in enumerate(beam_cfg["geometry"]["stem_centres_y_m"]):
        result.append(
            _part(
                f"web-links-{i + 1}",
                "beam",
                "Stem closed-link reinforcement group",
                {
                    "quantity": g["links_each_stem"],
                    "diameter_m": v["stirrup_diameter_m"],
                    "axis_y_m": y,
                    "first_station_x_m": a["research_cover_m"],
                    "last_station_x_m": L - a["research_cover_m"],
                    "spacing_m": g["actual_link_spacing_m"],
                    "outer_width_m": g["link_outer_width_m"],
                    "outer_height_m": g["link_outer_height_m"],
                    "estimated_cut_length_each_m": row["manufacturing"][
                        "estimated_link_length_each_m"
                    ],
                    "research_former_diameter_m": g["research_bend_former_diameter_m"],
                    "approved_shape_code": None,
                    "hook_layout": None,
                },
                rebar,
                [
                    "review dimensioned cage",
                    "cut/bend trial",
                    "place and secure before stressing/casting",
                ],
                [
                    "bar certificates",
                    "diameter/shape check",
                    "cover and tendon clearance",
                    "fabricator congestion trial",
                ],
            )
        )
    for identity, title in (
        ("end-zone-cage", "End-zone splitting/bursting reinforcement"),
        ("longitudinal-rebar", "Longitudinal reinforcement and ties"),
        ("lifting-inserts", "Lifting inserts and local reinforcement"),
    ):
        result.append(
            _part(
                identity,
                "beam",
                title,
                {"quantity": None, "dimensions_m": None, "design_state": "unknown"},
                rebar if identity != "lifting-inserts" else unknown_material,
                ["design and supplier/fabricator review required"],
                [
                    "approved drawings",
                    "traceable certificates",
                    "first article verification",
                ],
            )
        )
    for end, x in (("near", 0.0), ("far", L)):
        sid = f"support-{end}"
        result.append(
            _part(
                sid,
                "bay",
                f"{end.title()} independent outer-end support",
                {
                    "bay_end_x_m": x,
                    "research_service_reaction_n": row["metrics"][
                        "support_service_reaction_n"
                    ],
                    "surveyed_local_datum_m": None,
                },
                concrete,
                ["survey", "construct foundation", "cast column and cap"],
                ["survey control", "concrete and rebar release"],
            )
        )
        for i, y in enumerate(g["bearing_support_y_m"]):
            bid = f"{sid}-bearing-{i + 1}"
            result.append(
                _part(
                    bid,
                    sid,
                    "Bearing engineering reservation",
                    {
                        "quantity": 1,
                        "axis_x_m": (
                            g["bearing_support_x_m"]
                            if end == "near"
                            else L - g["bearing_support_x_m"]
                        ),
                        "axis_y_m": y,
                        "envelope_dimensions_m": g["two_pad_dimensions_m"],
                        "manufacturer_model": None,
                        "rated_vertical_force_n": None,
                        "movement_m": None,
                        "rotation_rad": None,
                        "restraint_role": None,
                        "preferred_manufacturing_origin": "UK; Ekspan lead from controlled source, offered model and capacity unconfirmed",
                    },
                    unknown_material,
                    [
                        "obtain project bearing design",
                        "set surveyed seats",
                        "install to approved restraint/movement plan",
                    ],
                    [
                        "supplier acceptance",
                        "seat level",
                        "installation orientation",
                        "replacement/jacking access",
                    ],
                )
            )
            for suffix, title in (
                ("seat", "Bearing seat and grout"),
                ("anchors", "Bearing anchor/shear-key group"),
            ):
                result.append(
                    _part(
                        f"{bid}-{suffix}",
                        bid,
                        title,
                        {
                            "quantity": None,
                            "dimensions_m": None,
                            "anchor_embedment_m": None,
                            "design_state": "unknown",
                        },
                        unknown_material,
                        ["supplier design and constructability review required"],
                        [
                            "substrate/edge distances",
                            "approved anchor and grout tests",
                            "as-built survey",
                        ],
                    )
                )
        for tag, title, dims in (
            ("cap", "Pier cap", g["cap_dimensions_m"]),
            ("column", "Pier column", g["column_dimensions_m"]),
            ("footing", "Square shallow-footing hypothesis", g["footing_dimensions_m"]),
        ):
            pid = f"{sid}-{tag}"
            result.append(
                _part(
                    pid,
                    sid,
                    title,
                    {
                        "envelope_dimensions_m": dims,
                        "concrete_volume_m3": dims[0] * dims[1] * dims[2],
                        "cover_m": None,
                        "soil_capacity_accepted": False,
                    },
                    concrete,
                    [
                        "approved cage and formwork",
                        "pre-pour inspection",
                        "place/compact/cure",
                        "survey and handover",
                    ],
                    [
                        "rebar before pour",
                        "mix/strength records",
                        "dimensions and cover",
                        "groundwater/exposure review",
                    ],
                )
            )
            result.append(
                _part(
                    f"{pid}-reinforcement",
                    pid,
                    f"{title} reinforcement group",
                    {
                        "bar_diameter_m": None,
                        "spacing_m": None,
                        "quantity": None,
                        "laps_and_anchorage_m": None,
                        "issued_schedule": False,
                    },
                    rebar,
                    [
                        "flexure/shear/punching/connection design",
                        "bar schedule and fabricator review",
                    ],
                    [
                        "independent resistance check",
                        "approved bending schedule",
                        "cover and placement inspection",
                    ],
                )
            )
    result.append(
        _part(
            "mould-and-bed-interface",
            "beam",
            "Reusable split mould and pretensioning-bed interface",
            {
                "beam_envelope_m": [
                    L,
                    beam_cfg["geometry"]["deck_width_m"],
                    v["beam_depth_m"],
                ],
                "total_initial_prestress_force_n": g["beam_variables"]["strand_count"]
                * strand["strand_area_m2"]
                * strand["strand_initial_stress_pa"],
                "accepted_stressing_equipment": None,
                "bed_and_anchors_designed": False,
            },
            unknown_material,
            [
                "design mould draft/splits",
                "verify bed/strongback/return/anchors",
                "trial stressing and demould",
            ],
            [
                "structural bed proof",
                "tool/grip access",
                "dimensional and demould trials",
            ],
        )
    )
    for p in result:
        proposed = (
            "PI25"
            if p["id"] == "beam" and L == 25
            else (
                "PIER-CAP-RESEARCH"
                if p["id"].endswith("-cap")
                else (
                    "PIER-COLUMN-RESEARCH"
                    if p["id"].endswith("-column")
                    else (
                        "BEARING-RESERVATION-RESEARCH"
                        if "-bearing-" in p["id"]
                        and not p["id"].endswith(("-seat", "-anchors"))
                        else None
                    )
                )
            )
        )
        links = [
            m
            for m in row["controlled_target_mappings"]
            if m["proposed_detail_component_id"] == proposed
        ]
        p["source_target_ids"] = [m["type_id"] for m in links]
        p["source_target_mappings"] = links
        p["source_mapping_state"] = (
            "related-target-only-not-exact-fit"
            if links
            else "new-research-part-no-controlled-target-match"
        )
    return result


def _variants(context):
    seed = civil_detail.seed(context)
    choices = [
        (
            "compact-control",
            "Compact precast beam with sparse links and shallow isolated footing",
            seed,
        ),
        (
            "reinforced-wide-base",
            "Deeper/wider precast beam with dense links and enlarged isolated footing",
            {
                **seed,
                "beam_depth_m": 1.7,
                "beam_stem_width_m": 0.36,
                "stirrup_diameter_m": 0.016,
                "stirrup_spacing_m": 0.1,
                "pad_length_m": 0.5,
                "footing_width_m": 5.0,
            },
        ),
        (
            "intermediate-base",
            "Intermediate precast beam/cage with medium footing and bearing reservation",
            {
                **seed,
                "beam_depth_m": 1.55,
                "beam_stem_width_m": 0.36,
                "stirrup_diameter_m": 0.012,
                "stirrup_spacing_m": 0.2,
                "pad_length_m": 0.35,
                "footing_width_m": 3.5,
            },
        ),
    ]
    choices = [
        (identity, concept, variables, None, [])
        for identity, concept, variables in choices
    ]
    variants, seen = [], set()
    while choices and len(variants) < 9:
        identity, concept, variables, parent_id, reasons = choices.pop(0)
        key = json.dumps(variables, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        row = civil_detail.assess(variables, context)
        checks = [{**c, "unit": c["units"]} for c in row["checks"]]
        checks.append(
            {
                "id": "handling_attached_rebar_and_equipment",
                "state": "unknown",
                "value": None,
                "limit": None,
                "unit": None,
                "basis": "Gross beam handling stresses exclude added cage/attachments, lifting insert and sling local effects; complete lifted assembly and temporary stages require independent design",
                "accepted_basis": False,
            }
        )
        parts = _parts(row)
        lift_fraction = row["geometry"]["beam_variables"]["lift_fraction"]
        variants.append(
            {
                "id": f"{context['id']}/{identity}",
                "concept": concept,
                "parameters": {
                    **variables,
                    "span_m": context["span_m"],
                    "beam_architecture": row["geometry"]["beam_variables"],
                },
                "parts": parts,
                "checks": checks,
                "objectives": {
                    **row["objectives"],
                    "two_support_known_mass_kg": row["objectives"]["mass_kg"]
                    + row["metrics"]["support_concrete_mass_kg"],
                    "full_cost_usd": None,
                    "imported_equipment_cost_usd": None,
                    "mass_boundary": "Both support gross concrete plus one beam concrete/strands/link estimate; excludes uncalculated support/longitudinal/end-zone rebar, bearings, anchors, grout, track and utilities",
                },
                "selection_state": (
                    "rejected-known-checks"
                    if row["rejected_known_checks"]
                    else "conditional-research-candidate"
                ),
                "metrics": row["metrics"],
                "source_case_sha256": row["source_case_sha256"],
                "controlled_target_mappings": row["controlled_target_mappings"],
                "construction_routes": [
                    {
                        "id": "two-point-crane",
                        "lifting_stations_x_m": [
                            context["span_m"] * lift_fraction,
                            context["span_m"] * (1 - lift_fraction),
                        ],
                        "state": "gross-beam-handling-screen-only",
                        "reaction_basis": "Handling stress in existing elastic beam evaluator; lifting-insert, sling, crane chart, transport and temporary restraint capacities absent",
                        "supplier_capacity_accepted": False,
                    },
                    {
                        "id": "launching-gantry",
                        "lifting_stations_x_m": None,
                        "state": "unknown",
                        "basis": "Alternative erection concept requires staged support and launcher/temporary-pier analysis; crane checks cannot qualify it",
                        "supplier_capacity_accepted": False,
                    },
                ],
                "manufacturing_release": False,
                "physical_twin_correlated": False,
                "full_specification_complete": False,
                "parent_variant_id": parent_id,
                "generation_basis": (
                    "initial engineering concept"
                    if parent_id is None
                    else "failure-directed civil_detail.propose; acceptance values unchanged"
                ),
                "repair_trigger_checks": reasons,
            }
        )
        for child in civil_detail.propose(row, context):
            digest = sha256(json.dumps(child, sort_keys=True).encode()).hexdigest()[:12]
            choices.append(
                (
                    f"feedback-{digest}",
                    "Failure-directed geometry/cage/support repair",
                    child,
                    variants[-1]["id"],
                    row["failed_checks"],
                )
            )
    return variants


def build():
    """Build deterministic, independent vehicle/span experiments in memory."""
    systems, experiments, requests = [], [], []
    for context in civil_detail.contexts():
        variants = _variants(context)
        systems.append(
            {
                "id": f"civil/{context['id']}",
                "title": f"{context['span_m']:g}m precast bay under {context['configuration_id']}",
                "configuration_id": context["configuration_id"],
                "search": {
                    "strategy": "three-seed FIFO failure-directed one-coordinate repairs with deduplication",
                    "evaluation_budget": 9,
                    "evaluated_count": len(variants),
                    "termination": (
                        "finite-budget-reached"
                        if len(variants) == 9
                        else "generated-frontier-exhausted"
                    ),
                    "global_optimum_claimed": False,
                },
                "requirements": [
                    {
                        "id": "load-source",
                        "state": "provisional",
                        "basis": "Preserve exact vehicle axle identities and one recorded force sensitivity; approved six-car loads absent",
                    },
                    {
                        "id": "site-and-material",
                        "state": "unknown",
                        "basis": "Baghdad survey, boreholes, groundwater, exposure, seismic and adopted material/railway basis required",
                    },
                    {
                        "id": "manufacturing-and-repair",
                        "state": "unknown",
                        "basis": "Local cage/mould/bed, lifting, bearing replacement and inspection access require supplier/fabricator demonstrations",
                    },
                ],
                "interfaces": {
                    "vehicle": {
                        "source_case_sha256": context["source_case_sha256"],
                        "applied_axles": context["applied_axles"],
                        "force_sensitivity_multiplier": context[
                            "force_sensitivity_multiplier"
                        ],
                        "accepted": False,
                    },
                    "support": "Independent outer-end supports; shared/interior pier and station loads not represented",
                    "factory": "Explicit mould envelope, initial prestress force and lifting stations; no equipment ratings assumed",
                    "station": "Station, concourse, lift shaft, platform and roof loads require separate evaluators; running beam qualification cannot transfer",
                },
                "variants": variants,
            }
        )
        for v in variants:
            experiments.append(
                {
                    "id": f"experiment/{v['id']}",
                    "system_id": f"civil/{context['id']}",
                    "variant_id": v["id"],
                    "parent_variant_id": v["parent_variant_id"],
                    "generation_basis": v["generation_basis"],
                    "repair_trigger_checks": v["repair_trigger_checks"],
                    "evaluator": "civil_detail.assess",
                    "parameters": deepcopy(v["parameters"]),
                    "check_counts": {
                        state: sum(c["state"] == state for c in v["checks"])
                        for state in ("pass", "fail", "unknown")
                    },
                    "selfweight_recomputed": True,
                    "demand_recomputed": True,
                    "accepted_basis": False,
                }
            )
        for check in variants[0]["checks"]:
            if check["state"] == "unknown":
                requests.append(
                    {
                        "id": f"request/{context['id']}/{check['id']}",
                        "system_id": f"civil/{context['id']}",
                        "state": "open",
                        "required_evidence": check["basis"],
                        "blocks": [
                            "full-specification",
                            "manufacturing-release",
                            "physical-twin-correlation",
                        ],
                    }
                )
    for identity, evidence in (
        (
            "physical-correlation",
            "Instrumented prototype strain, deflection, camber, modal, crack and settlement observations; sensor calibration, timestamps, as-built properties and independent model/measurement residual acceptance",
        ),
        (
            "network-civil-coverage",
            "Validated station, retaining wall, drainage, utility, tunnel, turnout, depot/factory slab, seismic and temporary-works evaluators and accepted inputs; current bay model does not cover these systems",
        ),
        (
            "bearing-supplier",
            "Project-specific UK-manufactured bearing configuration, restraint/movement/rotation capacities, anchors, tolerances, replacement/jacking design and quotation",
        ),
    ):
        requests.append(
            {
                "id": f"request/civil/{identity}",
                "state": "open",
                "required_evidence": evidence,
                "blocks": [
                    "full-specification",
                    "manufacturing-release",
                    "physical-twin-correlation",
                ],
            }
        )
    sources = {p: sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}
    sources.update(civil_detail.architecture_mechanical.run()["source_sha256"])
    return {
        "schema": SCHEMA,
        "domain": "civil",
        "source_files": sources,
        "systems": systems,
        "experiments": experiments,
        "open_requests": requests,
        "status": "executable-provisional-design-twin",
        "physical_twin_correlated": False,
        "manufacturing_release": False,
        "full_specification_complete": False,
        "scope": "Four independent vehicle/span contexts, three seed beam/cage/shallow-foundation concepts and bounded failure-directed repairs (up to nine evaluated per context); explicit part records and missing specifications. Research screens only; no whole-network or measured digital twin completion claim.",
    }

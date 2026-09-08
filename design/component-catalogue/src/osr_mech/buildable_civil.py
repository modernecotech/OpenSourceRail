"""Generate the controlled reusable-civil release register.

The reference IFC proves coordination coverage, not construction readiness.
This module reconciles every reusable IFC type with one release lane and emits
bounded drawing-definition briefs for the standard guideway kit.  Site survey,
ground, structural calculations, reinforcement, prestress, temporary works and
statutory acceptance deliberately remain external release evidence.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_IFC_INDEX = REPO_ROOT / "engineering/models/bim/reference/civil-coordination.index.json"
DEFAULT_CATALOG_DIR = REPO_ROOT / "design/component-catalogue/catalog/buildable-civil"
STATUS = "definition-seed-not-issued"
BOUNDARY = (
    "Planning/RFQ definition only. Fabrication or construction release requires "
    "project survey, geotechnical model, checked calculations, reinforcement/prestress "
    "design, supplier data, temporary-works design and signed engineering acceptance."
)


@dataclass(frozen=True)
class TypeAssignment:
    type_id: str
    release_lane: str
    package_id: str
    drawing_ids: tuple[str, ...]
    authority: str
    disposition: str


@dataclass(frozen=True)
class DrawingDefinition:
    id: str
    title: str
    owner: str
    scope_type: str
    type_ids: tuple[str, ...]
    source_refs: tuple[str, ...]
    required_views: tuple[str, ...]
    frozen_inputs: tuple[str, ...]
    verification: tuple[str, ...]


@dataclass(frozen=True)
class ReleasePackage:
    id: str
    title: str
    delivery_lane: str
    drawing_ids: tuple[str, ...]
    tooling_ids: tuple[str, ...]
    controlled_outputs: tuple[str, ...]
    hold_points: tuple[str, ...]


def type_assignments() -> tuple[TypeAssignment, ...]:
    """Map the current deterministic federation types to accountable lanes."""

    civil = "civil-structure-owned"
    track = "track-supplier-interface"
    station = "station-interface"
    vehicle = "vehicle-envelope-interface"
    return (
        TypeAssignment("OSR-TYPE-D36A7871D9B7", civil, "CIV-FRP-100", ("CIV-SUP-100",), "civil structures + precast designer", "reusable precast product definition"),
        TypeAssignment("OSR-TYPE-D4376465ACD5", civil, "CIV-FRP-100", ("CIV-SUP-110",), "civil structures + track engineer", "reusable elevated deck/trackform definition"),
        TypeAssignment("OSR-TYPE-FDB074324FD0", civil, "CIV-FRP-100", ("CIV-EGR-120",), "civil structures + operations", "reusable walkway cassette definition"),
        TypeAssignment("OSR-TYPE-99A11C1DC30D", civil, "CIV-FRP-110", ("CIV-SUB-200",), "deployment structural/geotechnical engineer", "catalogue column envelope; project reinforcement and foundation"),
        TypeAssignment("OSR-TYPE-3FD9673EF391", civil, "CIV-FRP-110", ("CIV-SUB-210",), "civil structures + precast designer", "reusable hollow/precast-shell cap definition"),
        TypeAssignment("OSR-TYPE-C966BC7372EC", civil, "CIV-FRP-120", ("CIV-BRG-300",), "bridge engineer + bearing supplier", "supplier-configured bearing and jacking interface"),
        TypeAssignment("OSR-TYPE-33216A9A4A24", civil, "CIV-FRP-130", ("CIV-ATG-400",), "track/civil engineer", "reusable at-grade slab envelope; project ground treatment"),
        TypeAssignment("OSR-TYPE-0B5DD2286469", civil, "CIV-FRP-130", ("CIV-ATG-400",), "track/civil engineer", "long-panel transition/interface geometry"),
        TypeAssignment("OSR-TYPE-239C28547990", civil, "CIV-INT-200", ("CIV-INT-500",), "civil/station integration", "coordination-only virtual deck interface; not a structural product"),
        TypeAssignment("OSR-TYPE-EACE63284F07", track, "CIV-INT-200", ("CIV-INT-500",), "permanent-way engineer + rail supplier", "supplier rail and fastening interface"),
        TypeAssignment("OSR-TYPE-F2832317E733", track, "CIV-INT-200", ("CIV-INT-500",), "permanent-way engineer + rail supplier", "supplier rail and fastening interface"),
        TypeAssignment("OSR-TYPE-38460DD866EF", track, "CIV-INT-200", ("CIV-INT-500",), "permanent-way/signalling engineer + turnout supplier", "supplier turnout interface"),
        TypeAssignment("OSR-TYPE-15CA3C9B2913", station, "CIV-INT-210", ("CIV-INT-510",), "station/civil integration", "guideway edge and platform clearance interface"),
        TypeAssignment("OSR-TYPE-24181B037817", station, "CIV-INT-210", ("CIV-INT-510",), "station/civil integration", "mirrored guideway edge and platform clearance interface"),
        TypeAssignment("OSR-TYPE-6336CC3F3205", station, "CIV-INT-210", ("CIV-INT-510",), "station/civil integration", "platform product interface controlled by station package"),
        TypeAssignment("OSR-TYPE-7406FA0925A0", station, "CIV-INT-210", ("CIV-INT-510",), "station/civil integration", "platform product interface controlled by station package"),
        TypeAssignment("OSR-TYPE-4891C9E3C493", station, "CIV-INT-210", ("CIV-INT-510",), "station/civil integration", "canopy clearance/load interface controlled by station package"),
        TypeAssignment("OSR-TYPE-7BF63285B921", station, "CIV-INT-210", ("CIV-INT-510",), "station/civil integration", "canopy clearance/load interface controlled by station package"),
        TypeAssignment("OSR-TYPE-661239622B15", vehicle, "CIV-INT-210", ("CIV-INT-510",), "system integration + rolling-stock authority", "vehicle swept/envelope interface; not a civil product"),
    )


def drawing_definitions() -> tuple[DrawingDefinition, ...]:
    docs = "docs/civil"
    return (
        DrawingDefinition(
            "CIV-SUP-100", "20 m / 25 m decked pi-beam reusable product definition",
            "civil structures + precast designer", "reusable-fabrication-definition",
            ("OSR-TYPE-D36A7871D9B7",),
            (f"{docs}/viaduct-design-basis.md", f"{docs}/viaduct-transport-and-erection-envelope.md"),
            ("general arrangement, end zones and web/deck sections", "prestress, reinforcement, inserts, drains and tolerances", "mould, lifting, transport, bearing and diaphragm interfaces"),
            ("selected 20 m or 25 m span", "project action set and durability exposure", "approved transport route and erection method"),
            ("independent 3-D structural check", "prestress/reinforcement and fatigue check", "first mould, proof/load and dimensional records"),
        ),
        DrawingDefinition(
            "CIV-SUP-110", "elevated slab, plinth and rail-seat definition",
            "track/civil integration", "reusable-fabrication-definition",
            ("OSR-TYPE-D4376465ACD5",),
            (f"{docs}/slab-trackforms.md", f"{docs}/viaduct-bearing-and-movement-schedule.md"),
            ("slab/plinth plans and typical sections", "rail seat, fastener, earthing and drainage details", "closure, diaphragm, movement-joint and tolerance interfaces"),
            ("surveyed alignment and cant", "selected fastening system", "bridge/CWR interaction and movement schedule"),
            ("gauge/cant and electrical-continuity inspection", "crack, drainage and restraint checks", "trial trackform installation"),
        ),
        DrawingDefinition(
            "CIV-EGR-120", "walkway cassette, parapet, drainage and services edge",
            "civil structures + operations", "reusable-fabrication-definition",
            ("OSR-TYPE-FDB074324FD0",),
            (f"{docs}/viaduct-kinematic-egress-envelope.md", f"{docs}/viaduct-first-article-test-plan.md"),
            ("cassette and support layout", "parapet, anti-climb, joint and handrail details", "drain, cable route, access and replaceability details"),
            ("project evacuation strategy", "vehicle swept envelope", "local drainage and service loads"),
            ("clear-width and parapet-height survey", "crowd/maintenance load check", "drainage and replaceability trial"),
        ),
        DrawingDefinition(
            "CIV-SUB-200", "pier column and foundation interface",
            "deployment structural/geotechnical engineer", "deployment-led-definition",
            ("OSR-TYPE-99A11C1DC30D",),
            (f"{docs}/viaduct-substructure-kit.md", f"{docs}/deployment-release-checklist.md"),
            ("pier schedule, elevations and setting out", "column reinforcement, joints, embeds and collision protection", "foundation reaction, pile/cap/shaft and test interfaces"),
            ("survey and utility model", "borehole-zoned ground model", "seismic, flood, scour and collision actions"),
            ("foundation and column calculations", "independent geotechnical/structural check", "foundation tests, concrete and survey records"),
        ),
        DrawingDefinition(
            "CIV-SUB-210", "hollow/precast-shell pier-cap definition",
            "civil structures + precast designer", "hybrid-fabrication-definition",
            ("OSR-TYPE-3FD9673EF391",),
            (f"{docs}/viaduct-substructure-kit.md", f"{docs}/viaduct-first-article-test-plan.md"),
            ("cap geometry, voids and bearing-seat plan", "reinforcement, joints, grout, inserts and tolerances", "lifting, temporary support and column connection"),
            ("project pier reactions", "bearing schedule", "erection crane/launcher and temporary state"),
            ("cap shell/final-state calculation", "lifting and temporary-state check", "first-article dimensional and proof records"),
        ),
        DrawingDefinition(
            "CIV-BRG-300", "bearing, restraint, movement and jacking schedule",
            "bridge engineer + bearing supplier", "supplier-interface-definition",
            ("OSR-TYPE-C966BC7372EC",),
            (f"{docs}/viaduct-bearing-and-movement-schedule.md", f"{docs}/viaduct-substructure-kit.md"),
            ("fixed/guided/free bearing layout", "loads, rotations, movements and setting schedule", "anchors, seats, jacking shelves and replacement sequence"),
            ("thermal/creep/shrinkage model", "CWR bridge interaction", "supplier certified capacities and installation temperature"),
            ("bearing design and movement check", "seat/jacking local checks", "factory certificates and installed survey"),
        ),
        DrawingDefinition(
            "CIV-ATG-400", "at-grade slab and elevated/at-grade transition",
            "track/civil/geotechnical integration", "deployment-led-definition",
            ("OSR-TYPE-33216A9A4A24", "OSR-TYPE-0B5DD2286469"),
            (f"{docs}/slab-trackforms.md", f"{docs}/deployment-release-checklist.md"),
            ("slab panel, rail-seat and transition plans", "subbase, reinforcement, drainage and duct sections", "settlement, movement, earthing and maintainability details"),
            ("surveyed profile and crossfall", "ground stiffness/settlement zones", "flood levels, outfalls and utility conflicts"),
            ("formation/slab/transition calculation", "drainage and settlement check", "trial panel, gauge and ride-quality records"),
        ),
        DrawingDefinition(
            "CIV-INT-500", "rail, turnout and station-deck coordination interfaces",
            "civil/track/station integration", "coordination-interface-definition",
            ("OSR-TYPE-239C28547990", "OSR-TYPE-EACE63284F07", "OSR-TYPE-F2832317E733", "OSR-TYPE-38460DD866EF"),
            (f"{docs}/bonsai-ifc-workflow.md", "docs/rfcs/0012-switches-and-crossings.md"),
            ("alignment, chainage, rail and turnout interface plans", "trackform loads, fixings, drainage and cable crossings", "station-deck limits, clearances and maintainability zones"),
            ("surveyed alignment", "rail/fastener/turnout supplier data", "station structural and operational interface data"),
            ("IFC/IDS and clash review", "track geometry and clearance check", "signed civil-track-station interface schedule"),
        ),
        DrawingDefinition(
            "CIV-INT-510", "platform, canopy and vehicle envelope interfaces",
            "system integration", "coordination-interface-definition",
            ("OSR-TYPE-15CA3C9B2913", "OSR-TYPE-24181B037817", "OSR-TYPE-6336CC3F3205", "OSR-TYPE-7406FA0925A0", "OSR-TYPE-4891C9E3C493", "OSR-TYPE-7BF63285B921", "OSR-TYPE-661239622B15"),
            (f"{docs}/bonsai-ifc-workflow.md", "design/component-catalogue/catalog/buildable-stations/factory-release-work-packages.md", "docs/rolling-stock/light-metro-3car/interfaces.md"),
            ("platform edge, stepping and swept-envelope sections", "canopy support/load and electrical clearance interfaces", "evacuation, maintenance, rescue and replacement envelopes"),
            ("surveyed platform and track geometry", "accepted vehicle dynamic envelope", "station canopy reactions and services"),
            ("IFC/IDS and clash review", "kinematic/platform stepping check", "signed civil-station-vehicle interface schedule"),
        ),
    )


def release_packages() -> tuple[ReleasePackage, ...]:
    return (
        ReleasePackage("CIV-FRP-100", "precast superstructure and guideway edge", "reusable-product", ("CIV-SUP-100", "CIV-SUP-110", "CIV-EGR-120"), ("CIV-TOL-001", "CIV-MLD-010", "CIV-JIG-020", "CIV-GGE-030"), ("checked product drawings", "mould and insert schedules", "inspection/test plan", "first-article dossier"), ("project action set accepted", "independent check closed", "first mould and girder accepted")),
        ReleasePackage("CIV-FRP-110", "pier column and precast cap", "hybrid-project-product", ("CIV-SUB-200", "CIV-SUB-210"), ("CIV-TPL-100", "CIV-MLD-110", "CIV-GGE-120"), ("pier/foundation schedule", "column and cap drawings", "reinforcement and lifting schedules", "survey/test dossier"), ("survey/geotechnics accepted", "foundation and pier calculations signed", "first cap accepted")),
        ReleasePackage("CIV-FRP-120", "bearing, restraint and replacement interfaces", "supplier-configured", ("CIV-BRG-300",), ("CIV-TPL-200", "CIV-JCK-210", "CIV-GGE-220"), ("bearing and movement schedule", "supplier data/certificates", "seat and jacking details", "installed survey"), ("movement/CWR model accepted", "supplier capacities approved", "trial jack/replacement method accepted")),
        ReleasePackage("CIV-FRP-130", "at-grade slab and transition", "deployment-led-product", ("CIV-ATG-400",), ("CIV-RIG-300", "CIV-TPL-310", "CIV-GGE-320"), ("formation and slab drawings", "ground-treatment schedule", "drainage/utility details", "track survey and test record"), ("survey/ground/drainage inputs accepted", "formation and slab checks signed", "trial panel accepted")),
        ReleasePackage("CIV-INT-200", "track and station-deck interfaces", "coordination-interface", ("CIV-INT-500",), ("CIV-GGE-400", "CIV-CHK-410"), ("supplier interface control document", "IFC/IDS issue", "clash and disposition report"), ("rail/turnout data frozen", "station deck data frozen", "interdisciplinary review signed")),
        ReleasePackage("CIV-INT-210", "station and vehicle envelope interfaces", "coordination-interface", ("CIV-INT-510",), ("CIV-GGE-500", "CIV-CHK-510"), ("platform/canopy/vehicle ICD", "IFC/IDS issue", "kinematic and access report"), ("vehicle envelope accepted", "station interface data frozen", "interdisciplinary review signed")),
    )


def construction_control_payload() -> dict[str, Any]:
    """Return practical factory/site defaults below the engineering release line."""

    controls = [
        {
            "id": "CIV-MFG-010",
            "scope": "survey, datums and set-out",
            "sequence": [
                "establish protected project control outside the work zone",
                "transfer primary control independently to factory bed or work front",
                "set mould, foundation, bearing and rail-seat datums from primary control",
                "record as-built coordinates before the work is concealed or loaded",
            ],
            "default": "Use one project grid and vertical datum; close each set-out from two independent control points. Survey all first-article interfaces and every foundation, bearing seat, rail seat, platform edge and movement joint.",
            "crew_and_plant": "two-person survey crew, total station, digital level and traceable check artefact",
            "hold": "control closure fails, benchmark disturbed, design/survey revision mismatch, or required accuracy is absent from the released survey plan",
            "release_evidence": "accepted survey control report, set-out sheets and signed as-built survey",
        },
        {
            "id": "CIV-MFG-020",
            "scope": "precast mould, reinforcement and inserts",
            "sequence": [
                "clean and survey mould/bed datums",
                "apply release system and fit cages, ducts, drains, lifting anchors and inserts",
                "independently check cover, restraint and insert templates",
                "photograph and sign the pre-pour hold point",
            ],
            "default": "Use rigid reusable steel moulds with replaceable end boxes and positive insert templates. First mould and every repaired/reset mould receive a full dimensional survey; subsequent pours receive datum, closure and insert checks before each pour.",
            "crew_and_plant": "mould/carpentry 2–3, reinforcement 4–6, one independent inspector, mould survey kit and cover/insert gauges",
            "hold": "unreleased reinforcement/prestress drawing, unidentified steel/insert, cover failure, dirty duct, loose insert, mould outside drawing tolerance, or unsigned pre-pour checklist",
            "release_evidence": "mould acceptance, material lots, cage/insert/cover report and signed pre-pour record",
        },
        {
            "id": "CIV-MFG-030",
            "scope": "concrete placement, curing and prestress transfer",
            "sequence": [
                "accept batch and fresh-concrete tests",
                "place in the released sequence without displacing cages or ducts",
                "finish and cure with temperature/maturity records",
                "confirm specified release/transfer strength before demoulding or prestress transfer",
            ],
            "default": "Reject site water addition unless the approved mix procedure permits and records it. Concrete class, exposure, w/c ratio, workability window, test frequency, curing cycle, release strength and prestress sequence remain calculation/specification values—not catalogue defaults.",
            "crew_and_plant": "placement 6–8 plus pump/crane operator, finishing 2–3, laboratory technician and independent inspector at hold points",
            "hold": "batch ticket mismatch, workability/temperature outside specification, interrupted placement beyond permitted joint time, curing excursion, failed strength result, or prestress anomaly",
            "release_evidence": "batch/test records, curing history, transfer/release strength, prestress elongation/force record and approved deviation/NCR closure",
        },
        {
            "id": "CIV-MFG-040",
            "scope": "demould, dimensional acceptance and storage",
            "sequence": [
                "confirm release strength and approved lifting arrangement",
                "demould without prying at unapproved points",
                "inspect surfaces, cracks, geometry, inserts, ducts and bearing/rail interfaces",
                "mark unique ID, orientation, mass and approved support points before storage",
            ],
            "default": "Inspect 100% of the first three units of each mould/type and every safety/interface feature thereafter. Routine non-interface dimensions may move to first/last plus 10% minimum three only through an approved control plan. Support units at the drawing-defined points on level, verified bearers.",
            "crew_and_plant": "lift supervisor, certified crane operator, four riggers, two survey/inspection staff and rated lifting frame",
            "hold": "strength not accepted, crack/damage beyond acceptance limits, interface out of tolerance, blocked duct/drain, unidentified unit, or storage support not verified",
            "release_evidence": "dimensional/crack report, concrete and lift records, traceability mark and storage inspection",
        },
        {
            "id": "CIV-MFG-050",
            "scope": "transport and delivery acceptance",
            "sequence": [
                "match unit, mass and centre of gravity to transport schedule",
                "inspect route, trailer, temporary supports and restraints",
                "load only from approved points and record restraint installation",
                "inspect and survey interfaces again after delivery",
            ],
            "default": "Use the approved transport orientation and support spacing; do not support on bearing seats, walkway edges, drains or rail plinths. The route survey, permits, dynamic allowances and temporary-state calculation are deployment-specific.",
            "crew_and_plant": "transport supervisor, certified operator, four riggers, escort/traffic staff as permitted, inspected trailer and rated lifting equipment",
            "hold": "route/permit absent, actual unit mass exceeds schedule, support/restraint mismatch, weather beyond method limits, transport damage, or delivery survey failure",
            "release_evidence": "route/permit pack, checked transport calculation, pre/post condition records and delivery acceptance",
        },
        {
            "id": "CIV-MFG-060",
            "scope": "foundation, pier and cap construction",
            "sequence": [
                "verify utilities, ground horizon and formation",
                "construct/test foundation and survey starter interface",
                "erect or cast column with temporary stability maintained",
                "install cap, closure/grout and bearing-seat survey",
            ],
            "default": "Release one work front at a time from accepted survey, utility and geotechnical zone data. Never extrapolate a foundation selection across an uninvestigated ground boundary. Keep column/cap temporary stability independent of incomplete permanent connections.",
            "crew_and_plant": "site engineer, supervisor, survey pair, foundation crew sized to selected method, 4–6 erection riggers and independent quality hold-point inspector",
            "hold": "unexpected ground/water/utility, foundation test failure, starter or bearing-seat survey failure, uncontrolled temporary state, grout/material mismatch, or open structural NCR",
            "release_evidence": "ground log, foundation tests, concrete/grout records, temporary-works inspection and pier/cap as-built survey",
        },
        {
            "id": "CIV-MFG-070",
            "scope": "girder erection, bearings and closures",
            "sequence": [
                "accept bearing seats, bearings, unit and erection plant",
                "set bearing orientation/temperature and install temporary restraints",
                "lift or launch to the released sequence and survey before de-rigging",
                "complete diaphragms/closures and remove temporary restraints only at the authorised stage",
            ],
            "default": "Plan one lift controller, one command channel and a controlled exclusion zone. Set each bearing by ID and orientation; protect movement surfaces and retain access for inspection/replacement. No person enters beneath a suspended or incompletely restrained unit.",
            "crew_and_plant": "lift supervisor, crane/launcher operator(s), four riggers, survey pair, two closure/grout workers and safety lead; plant capacity follows the checked lift study",
            "hold": "seat/bearing/unit not accepted, wind or visibility beyond method limits, plant configuration mismatch, loss of communication, unplanned movement, survey failure, or incomplete restraint",
            "release_evidence": "checked erection/lift plan, plant and personnel certificates, bearing schedule, lift record, closure strength and final survey",
        },
        {
            "id": "CIV-MFG-080",
            "scope": "at-grade formation, slab and transition",
            "sequence": [
                "prove utilities, drainage outfall and formation level",
                "place and test ground treatment/subbase by lot",
                "set rail-seat/duct/drain templates and sign pre-pour hold",
                "cast/cure, survey and trial the first complete transition panel",
            ],
            "default": "Build a full-width trial panel including drainage, ducts and rail-seat fixings before repetitive work. Divide earthworks and pavement testing into traceable lots no larger than one shift or one material/source change; the project specification sets test values and lot size if smaller.",
            "crew_and_plant": "site engineer, survey pair, earthworks 5–8 plus selected plant, concrete 6–8, laboratory technician and track-interface inspector",
            "hold": "soft spot or groundwater differs from model, drainage unavailable, compaction/plate test failure, template movement, concrete/cure failure, or transition survey outside released limits",
            "release_evidence": "formation lot tests, drainage proof, pre-pour record, concrete tests, trial-panel acceptance and as-built survey",
        },
        {
            "id": "CIV-MFG-090",
            "scope": "track, platform and systems interface handover",
            "sequence": [
                "clean and survey rail-seat/plinth, platform and equipment interfaces",
                "install accepted fastening/rail/turnout products to supplier procedures",
                "measure gauge, alignment, cant, stepping, clearances, drainage and electrical continuity",
                "hand over an as-built interface model with all NCRs and temporary conditions visible",
            ],
            "default": "Use a common chainage and asset ID across survey, IFC, inspection and maintenance records. Perform 100% measurement at turnouts, movement joints, stations, transitions and first article; routine interval and acceptance values come from the released track/vehicle/interface plan.",
            "crew_and_plant": "permanent-way supervisor, 6–10 track workers, survey pair, signalling/power representatives, calibrated track gauge and clearance gauge",
            "hold": "supplier revision mismatch, missing vehicle envelope, failed gauge/cant/stepping/continuity, obstructed drainage/access, or interface NCR not accepted by both owners",
            "release_evidence": "supplier installation records, track/clearance survey, signed civil-track-station-vehicle ICD and configuration handover",
        },
        {
            "id": "CIV-MFG-100",
            "scope": "nonconformance, repair and work-front handback",
            "sequence": [
                "identify, contain and preserve the original evidence",
                "assess structural, durability, geometry and downstream interface effects",
                "obtain authorised use-as-is, rework, repair, return/scrap or design-change disposition",
                "perform repair and repeat every invalidated inspection before handback",
            ],
            "default": "No field cutting, drilling, heat straightening, reinforcement/strand exposure, concrete repair, bearing adjustment, grout substitution or tolerance concession without a written disposition by the accountable designer and checker where required.",
            "crew_and_plant": "responsible construction engineer, quality lead, accountable designer and independent checker according to consequence; repair team only after disposition",
            "hold": "unapproved repair, repeat defect trend, hidden defect extent, missing retest, configuration mismatch, or any open safety/structural NCR",
            "release_evidence": "NCR, engineering assessment, approved repair method, repeat-test/survey result, as-built update and signed handback",
        },
    ]
    return {
        "schema": "org.opensourcerail.civil-construction-controls.v1",
        "status": "reference-defaults-not-ifc-release",
        "authority_boundary": BOUNDARY,
        "control_count": len(controls),
        "controls": controls,
        "workface_release_rule": "No work starts from coordination geometry alone: released drawings/method, accepted inputs, competent people/plant and open-hold-point authorization must all identify the same asset and revision.",
    }


CIVIL_PACKAGE_CONTROLS: dict[str, tuple[str, ...]] = {
    "CIV-FRP-100": ("CIV-MFG-010", "CIV-MFG-020", "CIV-MFG-030", "CIV-MFG-040", "CIV-MFG-050", "CIV-MFG-070", "CIV-MFG-100"),
    "CIV-FRP-110": ("CIV-MFG-010", "CIV-MFG-020", "CIV-MFG-030", "CIV-MFG-040", "CIV-MFG-050", "CIV-MFG-060", "CIV-MFG-100"),
    "CIV-FRP-120": ("CIV-MFG-010", "CIV-MFG-060", "CIV-MFG-070", "CIV-MFG-100"),
    "CIV-FRP-130": ("CIV-MFG-010", "CIV-MFG-030", "CIV-MFG-080", "CIV-MFG-090", "CIV-MFG-100"),
    "CIV-INT-200": ("CIV-MFG-010", "CIV-MFG-090", "CIV-MFG-100"),
    "CIV-INT-210": ("CIV-MFG-010", "CIV-MFG-090", "CIV-MFG-100"),
}


def render_construction_controls(payload: dict[str, Any] | None = None) -> str:
    data = payload or construction_control_payload()
    lines = [
        "# Civil Fabrication and Construction Reference Controls",
        "",
        "> Status: **reference defaults — not issued for fabrication or construction**.",
        "",
        "This workface handbook fills repeatable moulding, inspection, handling, erection and",
        "handover gaps around the reusable civil kit. It deliberately leaves site actions,",
        "ground, reinforcement/prestress, temporary works and statutory release with the",
        "competent project organisations.",
        "",
        "## Workface release rule",
        "",
        data["workface_release_rule"],
        "",
        data["authority_boundary"],
        "",
    ]
    for control in data["controls"]:
        lines += [f"## {control['id']} — {control['scope'].title()}", "", "Default sequence:", ""]
        lines += [f"{index}. {step}." for index, step in enumerate(control["sequence"], 1)]
        lines += [
            "",
            f"Planning default: {control['default']}",
            "",
            f"Typical first-shift crew/plant: {control['crew_and_plant']}. This is a resource-planning allowance, not authorisation or a minimum safe crew.",
            "",
            f"Hold the work when: {control['hold']}.",
            "",
            f"Required handback: {control['release_evidence']}.",
            "",
        ]
    return "\n".join(lines)


def _load_types(index_path: Path) -> list[dict[str, Any]]:
    data = json.loads(index_path.read_text(encoding="utf-8"))
    types = data.get("types")
    if not isinstance(types, list):
        raise ValueError(f"missing types list in {index_path}")
    return types


def build_payload(index_path: Path = DEFAULT_IFC_INDEX) -> dict[str, Any]:
    types = _load_types(index_path)
    assignments = {item.type_id: item for item in type_assignments()}
    actual_ids = {str(item["type_id"]) for item in types}
    expected_ids = set(assignments)
    if actual_ids != expected_ids:
        raise ValueError(
            "civil IFC reusable-type set changed; classify it before release output: "
            f"missing={sorted(expected_ids - actual_ids)}, new={sorted(actual_ids - expected_ids)}"
        )

    drawings = drawing_definitions()
    drawing_ids = {item.id for item in drawings}
    packages = release_packages()
    package_ids = {item.id for item in packages}
    if len(drawing_ids) != len(drawings) or len(package_ids) != len(packages):
        raise ValueError("duplicate civil drawing or release package id")
    covered_by_drawings = {type_id for item in drawings for type_id in item.type_ids}
    if covered_by_drawings != actual_ids:
        raise ValueError("civil drawing briefs do not cover the exact IFC type set")
    if any(item.package_id not in package_ids for item in assignments.values()):
        raise ValueError("civil type assignment references an unknown release package")
    if any(drawing_id not in drawing_ids for item in assignments.values() for drawing_id in item.drawing_ids):
        raise ValueError("civil type assignment references an unknown drawing")

    rows = []
    for item in sorted(types, key=lambda row: str(row["type_id"])):
        assignment = assignments[str(item["type_id"])]
        rows.append(
            {
                "type_id": item["type_id"],
                "asset_class": item["asset_class"],
                "ifc_class": item["ifc_class"],
                "occurrence_count": item["occurrence_count"],
                "source_geometry": item["source_geometry"],
                **asdict(assignment),
                "status": STATUS,
            }
        )

    construction_controls = construction_control_payload()
    control_ids = {row["id"] for row in construction_controls["controls"]}
    package_rows = []
    for package in packages:
        references = CIVIL_PACKAGE_CONTROLS.get(package.id)
        if not references or not set(references) <= control_ids:
            raise ValueError(f"civil package {package.id} has an invalid construction-control route")
        package_rows.append(
            asdict(package)
            | {
                "status": STATUS,
                "release_boundary": BOUNDARY,
                "reference_control_ids": list(references),
            }
        )
    payload = {
        "schema": "org.opensourcerail.buildable-civil-release.v1",
        "status": STATUS,
        "authority_boundary": BOUNDARY,
        "source_ifc_index": str(index_path.relative_to(REPO_ROOT)),
        "summary": {
            "ifc_reusable_types": len(rows),
            "ifc_occurrences": sum(int(row["occurrence_count"]) for row in rows),
            "civil_owned_types": sum(row["release_lane"] == "civil-structure-owned" for row in rows),
            "controlled_interface_types": sum(row["release_lane"] != "civil-structure-owned" for row in rows),
            "release_packages": len(packages),
            "drawing_definition_briefs": len(drawings),
            "tooling_and_gauge_families": len({tool for package in packages for tool in package.tooling_ids}),
        },
        "type_register": rows,
        "release_packages": package_rows,
        "drawing_definitions": [asdict(item) | {"status": STATUS, "release_boundary": BOUNDARY} for item in drawings],
        "construction_controls": construction_controls,
        "validation": {
            "all_ifc_types_classified_once": True,
            "all_ifc_types_have_drawing_coverage": True,
            "all_packages_have_hold_points": True,
            "site_specific_evidence_remains_open": True,
            "all_construction_controls_have_hold_and_handback": all(
                row["hold"] and row["release_evidence"]
                for row in construction_controls["controls"]
            ),
            "all_packages_have_construction_control_routes": True,
        },
    }
    # Keep the in-memory contract identical to its JSON representation so
    # callers never have to special-case dataclass tuple fields.
    return json.loads(json.dumps(payload))


def _table(values: tuple[str, ...] | list[str]) -> str:
    return "<br>".join(values)


def render_register(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Reusable Civil Type Release Register", "",
        "> Status: **definition seed — not issued for fabrication or construction**.", "",
        "This register reconciles every reusable type in the reference civil IFC with one accountable release lane. " + BOUNDARY,
        "",
        "## Coverage", "",
        "| Measure | Count |", "|---|---:|",
    ]
    for key, value in summary.items():
        lines.append(f"| {key.replace('_', ' ')} | {value} |")
    lines += ["", "## Type Register", "", "| IFC type | Asset class | Occurrences | Release lane | Package | Drawing brief | Disposition |", "|---|---|---:|---|---|---|---|"]
    for row in payload["type_register"]:
        lines.append(f"| `{row['type_id']}` | `{row['asset_class']}` | {row['occurrence_count']} | {row['release_lane']} | `{row['package_id']}` | {_table([f'`{value}`' for value in row['drawing_ids']])} | {row['disposition']} |")
    lines += ["", "## Release Boundary", "", "The hashes identify deterministic coordination geometry. They are not drawing revisions, certificates, approvals, or permission to build. A geometry change intentionally fails generation until its new type is classified.", ""]
    return "\n".join(lines)


def render_packages(payload: dict[str, Any]) -> str:
    lines = [
        "# Civil Factory/Release Work Packages", "",
        "> Status: **definition seed — not issued**.", "",
        "These packages define the smallest reusable handoffs around the current civil kit. Hold points remain open until real project evidence is recorded.", "",
    ]
    for package in payload["release_packages"]:
        lines += [f"## {package['id']} — {package['title']}", "", f"Lane: `{package['delivery_lane']}`", "", f"Drawing briefs: {_table([f'`{value}`' for value in package['drawing_ids']])}", "", "Tooling/gauges: " + ", ".join(f"`{value}`" for value in package["tooling_ids"]), "", "Reference workface controls: " + ", ".join(f"[`{value}`](fabrication-and-construction-controls.md)" for value in package["reference_control_ids"]), "", "Controlled outputs:", ""]
        lines += [f"- {value}" for value in package["controlled_outputs"]]
        lines += ["", "Open hold points:", ""] + [f"- [ ] {value}" for value in package["hold_points"]] + [""]
    lines += ["## Authority Boundary", "", BOUNDARY, ""]
    return "\n".join(lines)


def render_drawing(definition: dict[str, Any]) -> str:
    lines = [
        f"# {definition['id']} — {definition['title']}", "",
        "> Status: **definition seed — not issued for fabrication or construction**.", "",
        f"Owner: {definition['owner']}", "",
        f"Scope: `{definition['scope_type']}`", "",
        "IFC types: " + ", ".join(f"`{value}`" for value in definition["type_ids"]), "",
        "## Source References", "",
    ]
    lines += [f"- [`{value}`](../../../../../{value})" for value in definition["source_refs"]]
    lines += ["", "## Required Drawing Content", ""] + [f"- {value}" for value in definition["required_views"]]
    lines += ["", "## Inputs To Freeze", ""] + [f"- [ ] {value}" for value in definition["frozen_inputs"]]
    lines += ["", "## Verification To Record", ""] + [f"- [ ] {value}" for value in definition["verification"]]
    lines += ["", "## Release Boundary", "", BOUNDARY, ""]
    return "\n".join(lines)


def render_readme(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    return f"""# Buildable Civil Release Catalogue

This generated catalogue reconciles all **{summary['ifc_reusable_types']} reusable IFC types** ({summary['ifc_occurrences']} occurrences) into **{summary['release_packages']} bounded release packages** and **{summary['drawing_definition_briefs']} drawing-definition briefs**. It distinguishes the {summary['civil_owned_types']} civil-owned geometry types from {summary['controlled_interface_types']} track, station, vehicle, and coordination interfaces.

Nothing here is issued for fabrication or construction. Site survey, geotechnics, per-span structural analysis, reinforcement/prestress, supplier certification, erection engineering, permits, independent check, and signed release remain open.

## Outputs

| File | Purpose |
|---|---|
| [`reusable-type-release-register.md`](reusable-type-release-register.md) | Exact one-to-one accountability for every deterministic IFC type |
| [`factory-release-work-packages.md`](factory-release-work-packages.md) | Outputs, tools/gauges, and open hold points for six release packages |
| [`factory-drawings/index.md`](factory-drawings/index.md) | Nine controlled, non-issued drawing-definition briefs |
| [`fabrication-and-construction-controls.md`](fabrication-and-construction-controls.md) | Ten practical moulding, survey, precast, transport, erection, track-interface and handback controls |
| [`evidence/civil-release-record-template.json`](evidence/civil-release-record-template.json) | Empty evidence record that project authorities must complete |
| [`reusable-type-release-register.json`](reusable-type-release-register.json) | Machine-readable register, packages, briefs, and validation flags |

## Regenerate

```bash
tools/automation/buildable-civil.sh
```

The generator deliberately fails if the reference IFC type hashes change without a corresponding ownership and release-path decision.
"""


def write_outputs(out_dir: Path = DEFAULT_CATALOG_DIR, index_path: Path = DEFAULT_IFC_INDEX) -> None:
    payload = build_payload(index_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "factory-drawings").mkdir(exist_ok=True)
    (out_dir / "evidence").mkdir(exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    (out_dir / "reusable-type-release-register.json").write_text(encoded, encoding="utf-8")
    (out_dir / "reusable-type-release-register.md").write_text(render_register(payload), encoding="utf-8")
    (out_dir / "factory-release-work-packages.json").write_text(json.dumps(payload["release_packages"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "factory-release-work-packages.md").write_text(render_packages(payload), encoding="utf-8")
    (out_dir / "fabrication-and-construction-controls.json").write_text(
        json.dumps(payload["construction_controls"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "fabrication-and-construction-controls.md").write_text(
        render_construction_controls(payload["construction_controls"]),
        encoding="utf-8",
    )
    drawings = payload["drawing_definitions"]
    index_lines = ["# Civil Drawing-Definition Briefs", "", "> All entries are definition seeds, not issued fabrication or construction drawings.", "", "| ID | Title | Owner | IFC types |", "|---|---|---|---:|"]
    for drawing in drawings:
        (out_dir / "factory-drawings" / f"{drawing['id']}.md").write_text(render_drawing(drawing), encoding="utf-8")
        index_lines.append(f"| [`{drawing['id']}`]({drawing['id']}.md) | {drawing['title']} | {drawing['owner']} | {len(drawing['type_ids'])} |")
    index_lines += ["", BOUNDARY, ""]
    (out_dir / "factory-drawings/index.md").write_text("\n".join(index_lines), encoding="utf-8")
    evidence = {
        "schema": "org.opensourcerail.civil-release-record.v1",
        "status": "unfilled-template",
        "project_id": "",
        "package_id": "",
        "drawing_revisions": [],
        "survey_and_ground_evidence": [],
        "calculation_and_independent_check_evidence": [],
        "supplier_and_first_article_evidence": [],
        "nonconformances_and_dispositions": [],
        "approvals": {"designer": "", "checker": "", "construction_authority": "", "date": ""},
        "release_statement": "",
    }
    (out_dir / "evidence/civil-release-record-template.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(render_readme(payload), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ifc-index", type=Path, default=DEFAULT_IFC_INDEX)
    parser.add_argument("--out", type=Path, default=DEFAULT_CATALOG_DIR)
    args = parser.parse_args(argv)
    write_outputs(args.out, args.ifc_index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

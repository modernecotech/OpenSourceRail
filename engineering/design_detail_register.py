#!/usr/bin/env python3
"""Generate the route-impact, BIM and LM3 mechanical-detail control register."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
DEFAULT_JSON = REPO_ROOT / "engineering/models/bim/design-detail-register.json"
DEFAULT_MD = REPO_ROOT / "engineering/models/bim/design-detail-register.md"

RELEASE_BOUNDARY = (
    "Design-reference coordination data only. Open DEM and water data are screening evidence, "
    "not survey, geotechnical, hydraulic or navigation evidence. Candidate dimensions, loads "
    "and tolerances are not fabrication or construction release values until their stated "
    "closure evidence is accepted by the competent design authority."
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source(relative_path: str) -> dict[str, str]:
    path = REPO_ROOT / relative_path
    return {"file": relative_path, "sha256": _sha256(path)}


DESIGN_IMPACTS: tuple[dict[str, Any], ...] = (
    {
        "id": "OSR-IMP-TOPO-001",
        "trigger": "terrain elevation or slope changes the feasible vertical alignment",
        "disposition": "redesign-required",
        "affected_domains": ["alignment", "earthworks", "drainage", "structures", "traction-energy"],
        "required_actions": [
            "re-fit horizontal and vertical alignment against surveyed control",
            "reclassify each chainage as at-grade, cutting, embankment, retained, viaduct or special structure",
            "recalculate gradients, vertical curves, cut/fill balance, drainage and transition zones",
            "rerun vehicle traction, braking, thermal and energy duty over the released profile",
        ],
        "release_evidence": ["surveyed terrain model", "geotechnical model", "released alignment", "independent design check"],
    },
    {
        "id": "OSR-IMP-WATER-002",
        "trigger": "route intersects mapped water or its hydraulic/flood influence zone",
        "disposition": "bridge-or-reroute-required",
        "affected_domains": ["alignment", "bridge", "hydrology", "environment", "operations"],
        "required_actions": [
            "exclude ordinary at-grade and viaduct foundations from the open-water mask",
            "define bridge limits, freeboard, scour, navigation and debris cases from competent studies",
            "provide approach transitions, drainage isolation, inspection access and rescue strategy",
            "prohibit station placement until water and flood exclusions are demonstrably cleared",
        ],
        "release_evidence": ["survey", "hydraulic and scour study", "navigation constraints", "environmental consent", "bridge design check"],
    },
    {
        "id": "OSR-IMP-STRUCT-003",
        "trigger": "planner selects viaduct, bridge, retained or transition civil class",
        "disposition": "asset-family-and-site-design-required",
        "affected_domains": ["substructure", "superstructure", "track", "egress", "maintenance"],
        "required_actions": [
            "select a catalogue family only after span, curvature, skew, movement and erection screening",
            "derive foundations from ground investigation and site reactions",
            "close rail-structure interaction, bearing, expansion-joint, approach-slab and differential-settlement interfaces",
            "coordinate kinematic envelope, evacuation walkway, parapet, drainage and inspection access in BIM",
        ],
        "release_evidence": ["site investigation", "structural calculations", "CWR interaction", "erection study", "IFC coordination review"],
    },
    {
        "id": "OSR-IMP-STN-004",
        "trigger": "terrain, water, structure or access evidence moves or elevates a station",
        "disposition": "station-configuration-redesign-required",
        "affected_domains": ["platform", "accessibility", "fire-life-safety", "MEP", "urban-interface"],
        "required_actions": [
            "confirm station is outside water, flood, unstable-slope and structure-transition exclusions",
            "recalculate platform elevation, gap/step, vertical circulation and evacuation capacity",
            "coordinate foundations, drainage, charging, fire access, utilities and pedestrian catchment",
            "rerun passenger flow and inclusive-access review for the selected station variant",
        ],
        "release_evidence": ["station siting record", "platform gauge survey", "accessibility review", "fire strategy", "multidiscipline clash review"],
    },
    {
        "id": "OSR-IMP-LM3-005",
        "trigger": "released route profile, structures or platforms differ from the vehicle design basis",
        "disposition": "compatibility-requalification-before-vehicle-redesign",
        "affected_domains": ["rolling-stock", "wheel-rail", "traction", "braking", "energy", "evacuation"],
        "required_actions": [
            "retain the current three-car architecture unless a compatibility gate fails",
            "check gauge, curvature, cant, gradients, vertical curves, platform gap/step and structure deflection",
            "check axle loads, dynamic augmentation, braking distance, adhesion, energy and thermal duty",
            "check crosswind/exposure, water crossing evacuation, communications and recovery access",
            "raise a controlled vehicle redesign only for failed requirements with traced product and analysis impacts",
        ],
        "release_evidence": ["route compatibility dossier", "vehicle dynamics", "traction/braking simulation", "gauging study", "operations and evacuation acceptance"],
    },
    {
        "id": "OSR-IMP-DEPOT-006",
        "trigger": "topography or alignment changes depot access, stabling or recovery routes",
        "disposition": "site-layout-revalidation-required",
        "affected_domains": ["depot", "maintenance", "logistics", "energy", "recovery"],
        "required_actions": [
            "revalidate depot lead gradients/curves and disabled-train access",
            "coordinate drainage, flood resilience, lifting, bogie change and fire-service access",
            "recalculate charging topology and operational empty mileage",
        ],
        "release_evidence": ["surveyed depot layout", "vehicle swept path", "recovery trial", "drainage/fire/energy reviews"],
    },
)


BIM_REQUIREMENTS: tuple[dict[str, Any], ...] = (
    {
        "asset_type": "corridor-and-alignment",
        "required_objects": ["alignment", "profile", "terrain", "water", "civil-class segment", "exclusion volume"],
        "required_information": ["CRS and vertical datum", "chainage", "source/license/date/resolution", "confidence", "civil disposition", "design status"],
        "required_relations": ["segment-to-source-cell", "segment-to-structure", "station-to-exclusion", "alignment-to-revision"],
        "acceptance": ["georeference round-trip", "no station intersects exclusion volume", "every route segment has exactly one civil disposition"],
    },
    {
        "asset_type": "bridge-and-viaduct",
        "required_objects": ["foundation", "pier/abutment", "bearing", "deck/span", "trackform", "walkway", "parapet", "drainage", "movement joint"],
        "required_information": ["span/skew/curvature", "datum and reactions", "load model", "movement range", "exposure", "inspection zone", "calculation/evidence IDs"],
        "required_relations": ["foundation-to-ground-model", "bearing-to-movement-unit", "track-to-deck", "asset-to-work-package"],
        "acceptance": ["reaction and movement closure", "kinematic/egress clash check", "constructability and access review"],
    },
    {
        "asset_type": "station",
        "required_objects": ["platform edge", "track", "access route", "lift/stair", "canopy", "MEP/fire/charging equipment", "drainage", "foundation"],
        "required_information": ["platform gap/step basis", "accessible route", "occupancy/egress", "asset tags", "maintainer", "inspection and replacement clearances"],
        "required_relations": ["platform-to-track", "equipment-to-system", "space-to-egress route", "station-to-catchment"],
        "acceptance": ["gap/step analysis", "inclusive-access and flow check", "MEP/structure clash review", "no unresolved terrain/water exclusion"],
    },
    {
        "asset_type": "rolling-stock",
        "required_objects": ["carbody", "bogie", "wheelset", "door", "articulation", "coupler", "battery", "traction", "brake", "HVAC", "service/removal envelope"],
        "required_information": ["product ID", "configuration", "mass/CG status", "datum", "interface/load/tolerance status", "material/process", "verification evidence"],
        "required_relations": ["product-to-parent assembly", "product-to-interface", "interface-to-datum", "product-to-analysis/evidence"],
        "acceptance": ["complete controlled product graph", "interface and datum coverage", "route compatibility closure", "configuration-specific release boundary"],
    },
    {
        "asset_type": "manufacturing-resource",
        "required_objects": ["fixture", "gauge", "mould", "tool", "work centre", "inspection zone"],
        "required_information": ["tool ID", "controlled product/interface", "calibration", "capacity", "revision", "release status"],
        "required_relations": ["tool-to-process", "gauge-to-datum/interface", "process-to-product", "record-to-built serial"],
        "acceptance": ["tooling coverage", "calibration evidence", "first-article correlation", "as-built record linkage"],
    },
)


DATUMS: tuple[dict[str, Any], ...] = (
    {"id": "LM3-DAT-000", "title": "trainset track datum", "parent": None, "origin": "lead-end car centreline at top-of-rail reference plane", "axes": "+X forward, +Y left, +Z up", "applies_to": ["LM3-TRAINSET-A000"]},
    {"id": "LM3-DAT-100", "title": "carbody primary datum", "parent": "LM3-DAT-000", "origin": "car longitudinal centre at nominal low-floor structural plane", "axes": "parallel to trainset axes", "applies_to": ["LM3-CAR-A900", "LM3-BDY-SA110", "LM3-BDY-SA120"]},
    {"id": "LM3-DAT-110", "title": "body-to-bogie interface datum", "parent": "LM3-DAT-100", "origin": "secondary-suspension centre at nominal ride height", "axes": "X longitudinal, Y axle direction, Z suspension reaction", "applies_to": ["LM3-BOG-SA610", "LM3-BOG-SA620", "LM3-BOG-P046", "LM3-BOG-P061"]},
    {"id": "LM3-DAT-120", "title": "door and platform datum", "parent": "LM3-DAT-100", "origin": "door opening centre at finished threshold", "axes": "X along car, Y outboard, Z up", "applies_to": ["LM3-DOOR-SA310", "LM3-BDY-P100", "LM3-DOOR-P010", "LM3-EXT-P010"]},
    {"id": "LM3-DAT-130", "title": "roof equipment rail datum", "parent": "LM3-DAT-100", "origin": "roof rail grid intersection at car centre", "axes": "X rail pitch, Y cross-car, Z mounting normal", "applies_to": ["LM3-ROOF-SA410", "LM3-ROOF-P010", "LM3-HV-P020"]},
    {"id": "LM3-DAT-140", "title": "under-seat battery cassette datum", "parent": "LM3-DAT-100", "origin": "battery tray locating-pin centre", "axes": "X withdrawal, Y cassette row, Z support reaction", "applies_to": ["LM3-HV-SA510", "LM3-BDY-P050", "LM3-HV-P010"]},
    {"id": "LM3-DAT-200", "title": "wheelset and rail datum", "parent": "LM3-DAT-110", "origin": "axle centre at nominal wheel/rail contact geometry", "axes": "X travel, Y axle, Z radial/up", "applies_to": ["LM3-BOG-SA611", "LM3-BOG-SA621", "LM3-BOG-P040", "LM3-BOG-P041"]},
    {"id": "LM3-DAT-300", "title": "articulation interface datum", "parent": "LM3-DAT-100", "origin": "articulation yaw-axis centre at nominal ride height", "axes": "X connection chord, Y left, Z yaw axis", "applies_to": ["LM3-ART-SA800", "LM3-ART-SA810", "LM3-ART-SA820", "LM3-ART-SA830"]},
    {"id": "LM3-DAT-400", "title": "train-end and coupler datum", "parent": "LM3-DAT-100", "origin": "coupler centreline at nominal ride height", "axes": "X coupling axis, Y left, Z up", "applies_to": ["LM3-END-SA700", "LM3-EIF-SA650", "LM3-END-P050", "LM3-END-P060"]},
)


def _interface(
    identity: str,
    title: str,
    parent_datum: str,
    child_datum: str,
    products: list[str],
    geometry_control: str,
    load_control: str,
    services: list[str],
    verification: list[str],
    route_gate: str,
) -> dict[str, Any]:
    return {
        "id": identity,
        "title": title,
        "parent_datum": parent_datum,
        "child_datum": child_datum,
        "source_product_ids": products,
        "geometry_control": geometry_control,
        "tolerance_status": "allocation-open-until-stack-and-supplier-freeze",
        "load_control": load_control,
        "services": services,
        "maintainability": "model installation, inspection and replacement envelopes; demonstrate with a representative first article",
        "verification": verification,
        "route_requalification_gate": route_gate,
        "evidence_status": "design-reference-definition-complete; release-evidence-open",
    }


INTERFACES: tuple[dict[str, Any], ...] = (
    _interface("LM3-ICD-001", "wheel to rail and route geometry", "LM3-DAT-000", "LM3-DAT-200", ["LM3-BOG-SA611", "LM3-BOG-SA621", "LM3-BOG-P040", "LM3-BOG-P041"], "1435 mm standard-gauge planning basis; profile, back-to-back, wear and contact tolerances require supplier and track-system freeze", "static/dynamic axle, curving, traction, braking and derailment cases from accepted vehicle/track dynamics", [], ["wheelset dimensional report", "gauging and dynamics analysis", "instrumented route acceptance"], "gradient, curvature, cant, vertical curve, rail profile or track tolerance changes"),
    _interface("LM3-ICD-002", "carbody to powered bogie", "LM3-DAT-100", "LM3-DAT-110", ["LM3-BDY-P030", "LM3-BOG-SA610", "LM3-BOG-P046"], "pivot, air-spring, yaw-link and damper datums controlled as one replaceable interface set", "AW0/AW2/AW3 vertical, lateral, yaw, traction, braking, anti-lift and jacking cases", ["pneumatic suspension", "height sensing", "earth bond"], ["datum survey", "load calculation", "ride-height and full-motion test"], "curve/cant/gradient, axle-load, crosswind or structure-deflection envelope changes"),
    _interface("LM3-ICD-003", "carbody to trailer bogie", "LM3-DAT-100", "LM3-DAT-110", ["LM3-BDY-P030", "LM3-BOG-SA620", "LM3-BOG-P061"], "common body connection with configuration-controlled trailer-bogie adapter details", "AW0/AW2/AW3 vertical, lateral, yaw, braking, anti-lift and jacking cases", ["pneumatic suspension", "height sensing", "earth bond"], ["A/B interchange gauge", "load calculation", "ride-height and full-motion test"], "curve/cant/gradient, axle-load, crosswind or structure-deflection envelope changes"),
    _interface("LM3-ICD-004", "door cassette, body portal and platform", "LM3-DAT-100", "LM3-DAT-120", ["LM3-DOOR-SA310", "LM3-BDY-P100", "LM3-DOOR-P010", "LM3-EXT-P010"], "1500 x 2050 mm design-reference carrier gauge; final aperture, threshold, seal compression, leaf sweep and platform gap/step by frozen door and route ICD", "door equipment, passenger crowd, abuse, aerodynamic pressure and emergency-operation cases", ["LV power", "safety loop", "communications", "drainage"], ["carrier proof", "gap/step analysis", "obstruction/closed-and-locked/water/replacement tests"], "platform offset/height, cant, curvature or suspension-deflection changes"),
    _interface("LM3-ICD-005", "articulation structure and passenger gangway", "LM3-DAT-100", "LM3-DAT-300", ["LM3-ART-SA800", "LM3-ART-SA810", "LM3-ART-SA820", "LM3-ART-SA830"], "yaw/pitch/roll axes, anti-lift path, bellows, bridge, turntable and pinch keep-outs controlled through full motion", "buff/draft, vertical shear, torsion, curving, emergency braking, derailment and recovery cases", ["HV trainline", "LV/data", "pneumatic", "earth bond", "drainage"], ["structural proof", "full-motion sweep", "gap/pinch gauge", "water and passenger bridge load tests"], "minimum curve, reverse curve, vertical curve, cant transition or recovery regime changes"),
    _interface("LM3-ICD-006", "train end, coupler and rescue vehicle", "LM3-DAT-100", "LM3-DAT-400", ["LM3-END-SA700", "LM3-EIF-SA650", "LM3-END-P050", "LM3-END-P060"], "coupler axis, anti-climber, energy absorber, carrier ring and rescue adapter share a surveyed end datum", "buff/draft, coupling impact, crash, rescue tow, lifting and asymmetric recovery cases", ["pneumatic brake", "LV/data jumper", "earth bond"], ["end survey", "coupler/adapter proof", "rescue compatibility and recovery trial"], "maximum gradient, minimum curve, disabled-train mass or rescue fleet changes"),
    _interface("LM3-ICD-007", "battery cassette, tray and carbody", "LM3-DAT-100", "LM3-DAT-140", ["LM3-HV-SA510", "LM3-BDY-P050", "LM3-HV-P010"], "locating pins, retention, withdrawal path, lid/gasket, vent, drain and fire barrier controlled as a replaceable cassette", "mass/CG, longitudinal/lateral acceleration, shock/vibration, crash, thermal-runaway pressure and lifting cases", ["traction HV", "HVIL", "LV/data", "cooling/fire connection", "vent/drain"], ["tray proof", "retention and withdrawal tests", "isolation/HVIL", "thermal propagation and drainage tests"], "route energy, gradient, ambient/flood exposure or duty-cycle changes"),
    _interface("LM3-ICD-008", "traction motor, gearbox, axle and bogie frame", "LM3-DAT-110", "LM3-DAT-200", ["LM3-TRC-SA615", "LM3-TRC-P010", "LM3-TRC-P020", "LM3-BOG-P050"], "shaft, foot, torque-link, coupling, oil-port and removal envelopes frozen by supplier RFQ and bogie ICD", "peak/continuous torque, gear mesh, axle motion, torque reaction, shock, thermal and overspeed cases", ["traction HV", "temperature/speed sensing", "earth bond", "lubricant service"], ["alignment and runout", "mount/torque-link proof", "thermal map", "rotation and removal trial"], "gradient, adhesion, braking blend, speed or thermal duty changes"),
    _interface("LM3-ICD-009", "roof HVAC and equipment rail", "LM3-DAT-100", "LM3-DAT-130", ["LM3-ROOF-SA410", "LM3-ROOF-P010", "LM3-HV-P020", "LM3-EXT-P040"], "rail pitch, curb flatness, drop duct, condensate, keep-out and removal lift envelope controlled together", "equipment mass/CG, acceleration, crosswind, roof snow/maintenance, lifting and fatigue cases", ["HV/LV power", "controls/data", "supply/return air", "condensate drain", "earth bond"], ["rail/curb survey", "attachment proof", "air/leak/drain tests", "removal trial"], "crosswind, ambient temperature, dust/rain or tunnel/structure clearance changes"),
    _interface("LM3-ICD-010", "brake, WSP and wheelset", "LM3-DAT-110", "LM3-DAT-200", ["LM3-BOG-SA611", "LM3-BOG-SA621", "LM3-BOG-P060", "LM3-BOG-P061"], "disc/caliper, sensor target, cable sweep and wear/removal clearances controlled over suspension travel", "service/emergency/parking braking, low adhesion, thermal fade, wheel-slide and failed-channel cases", ["pneumatic brake", "LV power", "WSP/speed data", "earth bond"], ["static brake/WSP test", "thermal capacity", "stopping-distance and low-adhesion route tests"], "gradient, line speed, adhesion, station spacing or stopping-margin changes"),
    _interface("LM3-ICD-011", "vehicle envelope to structure and evacuation walkway", "LM3-DAT-000", "LM3-DAT-100", ["LM3-TRAINSET-A000", "LM3-CAR-A900", "LM3-SHELL-A200"], "2850 mm body-width concept envelope plus dynamic movement, throw, wear, construction and maintenance allowances; released swept envelope is open", "crosswind, cant deficiency, suspension failure, passenger load and structure movement combinations", ["emergency lighting/communications interaction"], ["static/dynamic gauging", "BIM swept-volume clash", "evacuation and detraining demonstration"], "all alignment, platform, parapet, tunnel, bridge movement or crosswind changes"),
    _interface("LM3-ICD-012", "lifting, jacking and field rerailing", "LM3-DAT-000", "LM3-DAT-100", ["LM3-CAR-A900", "LM3-BDY-P010", "LM3-END-P050"], "four-point lifting/jacking, transverse bridge and equipment keep-outs tied to measured car mass/CG", "normal/asymmetric lift, one-point pressure loss, rerailing side load, tiedown and damaged-vehicle cases", ["hydraulic/mechanical equipment", "bonding and communications"], ["point survey", "structural calculation", "proof load", "trained-crew recovery demonstration"], "route access, viaduct parapet/walkway, depot equipment or final mass/CG changes"),
)


LOAD_CASES: tuple[dict[str, Any], ...] = (
    {"id": "LM3-LC-001", "title": "AW0/AW2/AW3 static mass, axle load and CG", "status": "measured-mass-and-loading-definition-required"},
    {"id": "LM3-LC-002", "title": "traction, service/emergency braking and low adhesion", "status": "released-route-and-brake-supplier-model-required"},
    {"id": "LM3-LC-003", "title": "curve, cant, vertical curve and full suspension motion", "status": "vehicle-dynamics-model-and-route-profile-required"},
    {"id": "LM3-LC-004", "title": "crosswind, aerodynamic pressure and exposed structures", "status": "site-wind-and-vehicle-aerodynamic-evidence-required"},
    {"id": "LM3-LC-005", "title": "buff/draft, coupling, rescue tow and crash energy", "status": "structural-and-crash-authority-definition-required"},
    {"id": "LM3-LC-006", "title": "fatigue and vibration duty spectrum", "status": "route-spectrum-and-joint-classification-required"},
    {"id": "LM3-LC-007", "title": "battery/HV thermal, fault, fire and environmental exposure", "status": "supplier-data-and-hazard-analysis-required"},
    {"id": "LM3-LC-008", "title": "lifting, jacking, rerailing and damaged-vehicle recovery", "status": "measured-mass-cg-and-recovery-method-required"},
    {"id": "LM3-LC-009", "title": "passenger, accessibility, door and evacuation operation", "status": "loading-and-operational-rules-required"},
    {"id": "LM3-LC-010", "title": "thermal, dust, rain, flood splash and water ingress", "status": "route-environment-and-ingress-classification-required"},
)


ROUTE_GATES: tuple[dict[str, Any], ...] = (
    {"id": "LM3-RCG-001", "question": "Does the released static/dynamic swept envelope clear track, platforms and structures?", "decision": "redesign geometry only if gauging cannot be closed by infrastructure tolerance or operational control", "evidence": ["surveyed alignment", "structure/platform as-built model", "vehicle gauging model"]},
    {"id": "LM3-RCG-002", "question": "Do gradient, curvature, cant and vertical curves remain within vehicle capability?", "decision": "change route first where reasonable; otherwise requalify bogie, articulation, traction or braking", "evidence": ["released profile", "vehicle dynamics", "traction/braking results"]},
    {"id": "LM3-RCG-003", "question": "Does the timetable duty fit usable battery energy and thermal limits with reserve?", "decision": "adjust timetable/charging before changing battery capacity; redesign only after whole-life comparison", "evidence": ["route simulation", "supplier battery/motor/inverter/HVAC maps", "degraded-mode cases"]},
    {"id": "LM3-RCG-004", "question": "Are axle/load spectra accepted by track, bridge and viaduct designs?", "decision": "iterate vehicle mass and civil structures through one controlled load model", "evidence": ["measured mass/CG", "dynamic augmentation", "structural calculations"]},
    {"id": "LM3-RCG-005", "question": "Are crosswind and exposed-water/viaduct operations acceptable?", "decision": "define wind monitoring/operating limits or vehicle aerodynamic changes through hazard assessment", "evidence": ["site wind study", "vehicle characteristic wind curve", "operating rules"]},
    {"id": "LM3-RCG-006", "question": "Can passengers evacuate and responders recover a failed train everywhere?", "decision": "coordinate walkway, detraining and access provision; change vehicle emergency interfaces only where necessary", "evidence": ["evacuation model/drill", "BIM access review", "recovery demonstration"]},
    {"id": "LM3-RCG-007", "question": "Do station platform gap, step and door-zone flows meet the accessibility basis?", "decision": "coordinate platform and suspension control; modify threshold/door system only after system trade study", "evidence": ["platform survey", "suspension cases", "gap/step and passenger-flow assessment"]},
)


VERIFICATION_MATRIX: tuple[dict[str, Any], ...] = (
    {"id": "LM3-VER-001", "scope": "product graph and configuration", "method": "inspection", "interface_ids": [], "load_case_ids": [], "evidence": "manifest/IFC ID reconciliation and configuration record"},
    {"id": "LM3-VER-002", "scope": "datum and tolerance-chain closure", "method": "analysis+inspection", "interface_ids": [item["id"] for item in INTERFACES], "load_case_ids": [], "evidence": "released ICDs, stack calculations, calibrated surveys and NCR disposition"},
    {"id": "LM3-VER-003", "scope": "vehicle/route dynamic compatibility", "method": "analysis+test", "interface_ids": ["LM3-ICD-001", "LM3-ICD-002", "LM3-ICD-003", "LM3-ICD-005", "LM3-ICD-011"], "load_case_ids": ["LM3-LC-001", "LM3-LC-002", "LM3-LC-003", "LM3-LC-004"], "evidence": "independently checked simulations and instrumented route acceptance"},
    {"id": "LM3-VER-004", "scope": "carbody, bogie, articulation and end structure", "method": "analysis+test", "interface_ids": ["LM3-ICD-002", "LM3-ICD-003", "LM3-ICD-005", "LM3-ICD-006", "LM3-ICD-012"], "load_case_ids": ["LM3-LC-001", "LM3-LC-005", "LM3-LC-006", "LM3-LC-008"], "evidence": "calculations, material/process qualification, NDT, proof and fatigue evidence"},
    {"id": "LM3-VER-005", "scope": "door/platform/accessibility", "method": "analysis+demonstration", "interface_ids": ["LM3-ICD-004"], "load_case_ids": ["LM3-LC-003", "LM3-LC-009"], "evidence": "gap/step, obstruction, emergency release, water and passenger-flow evidence"},
    {"id": "LM3-VER-006", "scope": "traction, braking and energy", "method": "analysis+test", "interface_ids": ["LM3-ICD-001", "LM3-ICD-008", "LM3-ICD-010"], "load_case_ids": ["LM3-LC-002", "LM3-LC-003", "LM3-LC-007", "LM3-LC-010"], "evidence": "supplier maps, HIL, dynamometer and route test results"},
    {"id": "LM3-VER-007", "scope": "battery/HV fire and environmental", "method": "analysis+test", "interface_ids": ["LM3-ICD-007"], "load_case_ids": ["LM3-LC-006", "LM3-LC-007", "LM3-LC-010"], "evidence": "hazard analysis, propagation/containment, ingress, isolation and emergency-response evidence"},
    {"id": "LM3-VER-008", "scope": "HVAC/roof equipment", "method": "analysis+test", "interface_ids": ["LM3-ICD-009"], "load_case_ids": ["LM3-LC-004", "LM3-LC-006", "LM3-LC-010"], "evidence": "attachment, airflow, thermal, EMC, ingress and removal evidence"},
    {"id": "LM3-VER-009", "scope": "gauging, bridge/viaduct evacuation and recovery", "method": "analysis+demonstration", "interface_ids": ["LM3-ICD-006", "LM3-ICD-011", "LM3-ICD-012"], "load_case_ids": ["LM3-LC-004", "LM3-LC-008", "LM3-LC-009"], "evidence": "swept-volume BIM review plus representative evacuation/recovery drills"},
)


def build_register() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    product_ids = {str(item["id"]) for item in manifest["product_items"]}
    assembly_ids = {str(item["id"]) for item in manifest["assemblies"]}
    known_ids = product_ids | assembly_ids
    datum_ids = {item["id"] for item in DATUMS}
    interface_ids = {item["id"] for item in INTERFACES}
    load_case_ids = {item["id"] for item in LOAD_CASES}
    if len(datum_ids) != len(DATUMS) or len(interface_ids) != len(INTERFACES):
        raise ValueError("duplicate datum or interface ID")
    for datum in DATUMS:
        if datum["parent"] is not None and datum["parent"] not in datum_ids:
            raise ValueError(f"unknown parent datum {datum['parent']}")
        if not set(datum["applies_to"]) <= known_ids:
            raise ValueError(f"unknown product in datum {datum['id']}")
    for interface in INTERFACES:
        if {interface["parent_datum"], interface["child_datum"]} - datum_ids:
            raise ValueError(f"unknown datum in {interface['id']}")
        if not set(interface["source_product_ids"]) <= known_ids:
            raise ValueError(f"unknown product in {interface['id']}")
    for row in VERIFICATION_MATRIX:
        if not set(row["interface_ids"]) <= interface_ids:
            raise ValueError(f"unknown interface in {row['id']}")
        if not set(row["load_case_ids"]) <= load_case_ids:
            raise ValueError(f"unknown load case in {row['id']}")

    controlled = sorted(
        {product for row in INTERFACES for product in row["source_product_ids"]}
        | {product for row in DATUMS for product in row["applies_to"]}
    )
    return {
        "schema": "org.opensourcerail.design-detail-register.v1",
        "revision": "A-DRAFT",
        "status": "design-reference-not-released",
        "release_boundary": RELEASE_BOUNDARY,
        "sources": {
            "trainset_manifest": _source(str(MANIFEST.relative_to(REPO_ROOT))),
            "terrain_module": _source("design/city-generation/src/osr_geo/terrain.py"),
            "track_geometry": _source("lib/templates/track-geometry.toml"),
            "water_and_civil_raster": _source("design/city-generation/src/osr_geo/rasterize.py"),
        },
        "change_policy": {
            "changed_now": ["alignment/civil disposition", "bridge/viaduct need", "station siting/configuration", "route compatibility evidence", "BIM information requirements"],
            "not_automatically_changed": ["LM3 three-car architecture", "car length/width concept", "battery/traction topology", "bogie and articulation concept"],
            "vehicle_redesign_rule": "A vehicle parameter changes only after a route-compatibility gate fails and a controlled whole-system trade study accepts that change.",
        },
        "design_impacts": list(DESIGN_IMPACTS),
        "bim_information_requirements": list(BIM_REQUIREMENTS),
        "datum_systems": list(DATUMS),
        "mechanical_interfaces": list(INTERFACES),
        "load_cases": list(LOAD_CASES),
        "route_compatibility_gates": list(ROUTE_GATES),
        "verification_matrix": list(VERIFICATION_MATRIX),
        "controlled_lm3_ids": controlled,
        "summary": {
            "design_impacts": len(DESIGN_IMPACTS),
            "bim_asset_types": len(BIM_REQUIREMENTS),
            "datum_systems": len(DATUMS),
            "mechanical_interfaces": len(INTERFACES),
            "load_cases": len(LOAD_CASES),
            "route_compatibility_gates": len(ROUTE_GATES),
            "verification_rows": len(VERIFICATION_MATRIX),
            "controlled_lm3_ids": len(controlled),
        },
        "passed": True,
    }


def render_markdown(register: dict[str, Any]) -> str:
    changed = register["change_policy"]
    lines = [
        "# Topography redesign, BIM and mechanical detail register",
        "",
        "This generated register says what the new terrain/water evidence changes, what remains",
        "provisional, and what information must be closed before design or fabrication release.",
        "",
        "> " + register["release_boundary"],
        "",
        "## Redesign decision",
        "",
        "Changed now: " + "; ".join(changed["changed_now"]) + ".",
        "",
        "Not automatically changed: " + "; ".join(changed["not_automatically_changed"]) + ".",
        "",
        changed["vehicle_redesign_rule"],
        "",
        "## Delivery plan and completed implementation",
        "",
        "1. Classify terrain/water evidence and trace each trigger to affected design domains.",
        "2. Define BIM objects, information, relations and acceptance checks for each asset type.",
        "3. Establish the LM3 datum hierarchy, mechanical ICDs, load cases and route gates.",
        "4. Publish the register into IFC property sets and the model-coverage report.",
        "5. Enforce ID integrity, source traceability, deterministic output and IFC round-trip tests.",
        "",
        "All five steps are implemented in the repository; engineering evidence remains open where",
        "the status below says supplier, survey, calculation, test or authority acceptance is required.",
        "",
        "## Design impacts",
        "",
        "| ID | Disposition | Trigger | Domains |",
        "|---|---|---|---|",
    ]
    for row in register["design_impacts"]:
        lines.append(f"| `{row['id']}` | `{row['disposition']}` | {row['trigger']} | {', '.join(row['affected_domains'])} |")
    lines += ["", "## BIM information requirements", ""]
    for row in register["bim_information_requirements"]:
        lines += [
            f"### {row['asset_type']}",
            "",
            "- Objects: " + ", ".join(row["required_objects"]),
            "- Information: " + ", ".join(row["required_information"]),
            "- Relations: " + ", ".join(row["required_relations"]),
            "- Acceptance: " + "; ".join(row["acceptance"]),
            "",
        ]
    lines += [
        "## LM3 datum hierarchy",
        "",
        "| ID | Datum | Parent | Origin and axes |",
        "|---|---|---|---|",
    ]
    for row in register["datum_systems"]:
        lines.append(f"| `{row['id']}` | {row['title']} | `{row['parent'] or 'ROOT'}` | {row['origin']}; {row['axes']} |")
    lines += ["", "## Mechanical interface control", ""]
    for row in register["mechanical_interfaces"]:
        lines += [
            f"### {row['id']} — {row['title']}",
            "",
            f"- Datums: `{row['parent_datum']}` → `{row['child_datum']}`",
            "- Products: " + ", ".join(f"`{value}`" for value in row["source_product_ids"]),
            "- Geometry: " + row["geometry_control"],
            "- Loads: " + row["load_control"],
            "- Services: " + (", ".join(row["services"]) or "none"),
            "- Verification: " + "; ".join(row["verification"]),
            "- Route gate: " + row["route_requalification_gate"],
            f"- Status: `{row['evidence_status']}`; tolerance `{row['tolerance_status']}`.",
            "",
        ]
    lines += ["## Load cases", "", "| ID | Case | Closure status |", "|---|---|---|"]
    for row in register["load_cases"]:
        lines.append(f"| `{row['id']}` | {row['title']} | `{row['status']}` |")
    lines += ["", "## Route compatibility gates", ""]
    for row in register["route_compatibility_gates"]:
        lines += [f"### {row['id']}", "", row["question"], "", f"Decision rule: {row['decision']}.", "", "Evidence: " + "; ".join(row["evidence"]) + ".", ""]
    lines += [
        "## Verification matrix",
        "",
        "| ID | Scope | Method | Interfaces | Load cases | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    for row in register["verification_matrix"]:
        lines.append(
            f"| `{row['id']}` | {row['scope']} | `{row['method']}` | "
            f"{', '.join(row['interface_ids']) or '—'} | {', '.join(row['load_case_ids']) or '—'} | {row['evidence']} |"
        )
    lines += ["", "The complete machine-readable record is [`design-detail-register.json`](design-detail-register.json).", ""]
    return "\n".join(lines)


def write(json_path: Path = DEFAULT_JSON, markdown_path: Path = DEFAULT_MD) -> dict[str, Any]:
    register = build_register()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(register, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(register), encoding="utf-8")
    return register


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.check:
        register = build_register()
        expected_json = json.dumps(register, indent=2, sort_keys=True) + "\n"
        expected_md = render_markdown(register)
        stale = []
        if not args.json.is_file() or args.json.read_text(encoding="utf-8") != expected_json:
            stale.append(str(args.json))
        if not args.markdown.is_file() or args.markdown.read_text(encoding="utf-8") != expected_md:
            stale.append(str(args.markdown))
        if stale:
            raise SystemExit("stale design-detail outputs: " + ", ".join(stale))
        print("design-detail register current")
        return 0
    result = write(args.json, args.markdown)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

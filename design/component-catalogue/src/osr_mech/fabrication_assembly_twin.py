"""Source-linked fabrication and assembly digital twin.

The operational twins describe assets after handover.  This module describes
how four representative assets become those assets: a 6 m track panel, a
standard station bay, an OSR-Pi25 viaduct bay, and an LM3 three-car trainset.
It deliberately stays dependency-light so FreeCAD, Blender, CI, and ordinary
Python can consume the same work-package and quality-gate state model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


TWIN_SCHEMA = "org.opensourcerail.fabrication-assembly-twin.v1"
ANIMATION_DURATION_S = 48.0
VISUAL_TOUR_DURATION_S = 88.0
VISUAL_TOUR_PHASES = (
    {
        "stream_id": "track",
        "start_s": 1.0,
        "end_s": 18.0,
        "title": "Track panel: plinths, fasteners, rails and geometry release",
    },
    {
        "stream_id": "station",
        "start_s": 21.0,
        "end_s": 38.0,
        "title": "Station kit: platforms, portals, roof cassettes and systems",
    },
    {
        "stream_id": "viaduct",
        "start_s": 41.0,
        "end_s": 60.0,
        "title": "Viaduct bay: substructure, bearings, beams, links and egress",
    },
    {
        "stream_id": "train",
        "start_s": 63.0,
        "end_s": 82.0,
        "title": "LM3 trainset: bogies, bodies, systems, fit-out and release",
    },
)
REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEDULE_PATH = REPO_ROOT / "lib/templates/manufacturing-schedule.toml"
STATION_MANIFEST_PATH = (
    REPO_ROOT / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
)
TRAINSET_MANIFEST_PATH = (
    REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
)


@dataclass(frozen=True)
class FabricationStage:
    id: str
    stream_id: str
    title: str
    work_center: str
    duration_days: float
    predecessor: str | None
    inputs: tuple[str, ...]
    output: str
    qa_hold: str
    evidence: tuple[str, ...]
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class FabricationStream:
    id: str
    title: str
    exemplar: str
    quantity_basis: str
    stages: tuple[FabricationStage, ...]


@dataclass(frozen=True)
class StageState:
    stream_id: str
    stage_id: str
    stage_title: str
    status: str
    progress_percent: float
    qa_status: str


def _stage(
    stage_id: str,
    stream_id: str,
    title: str,
    work_center: str,
    duration_days: float,
    predecessor: str | None,
    inputs: tuple[str, ...],
    output: str,
    qa_hold: str,
    evidence: tuple[str, ...],
    source_refs: tuple[str, ...],
) -> FabricationStage:
    return FabricationStage(
        stage_id,
        stream_id,
        title,
        work_center,
        duration_days,
        predecessor,
        inputs,
        output,
        qa_hold,
        evidence,
        source_refs,
    )


def _manufacturing_packages() -> dict[str, dict[str, Any]]:
    with SCHEDULE_PATH.open("rb") as handle:
        raw = tomllib.load(handle)
    return {item["id"]: item for item in raw["manufacturing_package"]}


def fabrication_streams() -> tuple[FabricationStream, ...]:
    train_manifest = json.loads(TRAINSET_MANIFEST_PATH.read_text(encoding="utf-8"))
    """Return the four controlled exemplar production routes."""

    packages = _manufacturing_packages()
    common_track_refs = (
        "lib/templates/manufacturing-schedule.toml",
        "docs/civil/slab-trackforms.md",
        "design/component-catalogue/src/osr_mech/track/panel.py",
    )
    track = FabricationStream(
        "track",
        "Rail and track-panel fabrication",
        "6 m direct-fixation track panel",
        "two rails, ten seat pairs, alignment layer and plinths",
        (
            _stage("TRK-10", "track", "Inspect and batch rails", "rail preparation cell", 1, None,
                   ("rail bars", "mill certificates"), "released rail pair", "material and ultrasonic release",
                   ("mill certificates", "rail identification", "UT record"), common_track_refs),
            _stage("TRK-20", "track", "Cast alignment layer and plinth modules", "precast trackform cell", 2, "TRK-10",
                   ("reinforcement", "concrete", "embedded inserts"), "surveyed 6 m trackform", "concrete strength and insert survey",
                   ("batch ticket", "strength result", "casting-bed survey"), common_track_refs),
            _stage("TRK-30", "track", "Fit pads, baseplates and fasteners", "track panel fixture", 1, "TRK-20",
                   ("pads", "adjustable baseplates", "anchor kits"), "fastener-equipped trackform", "fastener identity and torque witness",
                   ("fastener lot", "torque record", "bonding record"), common_track_refs),
            _stage("TRK-40", "track", "Place rails and close panel geometry", "track panel fixture", 1, "TRK-30",
                   ("released rail pair", "fastener-equipped trackform"), "assembled track panel", "gauge, cant and rail-seat survey",
                   ("gauge survey", "cant survey", "as-built panel ID"), common_track_refs),
            _stage("TRK-50", "track", packages["trk-30-trackform-rail"]["work_order_title"], "site track installation", 4, "TRK-40",
                   ("assembled panels", "weld kit", "survey control"), "installed and aligned running rail", "weld NDT and final geometry release",
                   ("weld record", "NDT", "final geometry car"), common_track_refs),
        ),
    )

    station_refs = (
        "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json",
        "lib/templates/stations.toml",
        "docs/rfcs/0010-station-design-standard.md",
    )
    station = FabricationStream(
        "station",
        "Station kit fabrication and assembly",
        "standard 59.5 m twin-platform station",
        "controlled standard station product tree and traveler",
        (
            _stage("STN-10", "station", "Cast platform and foundation modules", "precast station cell", 4, None,
                   ("reinforcement cages", "concrete", "lifting inserts"), "released platform module kit", "strength, dimensions and lifting points",
                   ("concrete certificate", "dimensional report", "lifting-point inspection"), station_refs),
            _stage("STN-20", "station", "Fabricate canopy portal frames", "steel fabrication cell", 3, "STN-10",
                   ("structural sections", "connection plates", "coating system"), "numbered portal-frame kit", "weld/NDT and trial-fit release",
                   ("material heat trace", "weld map", "coating DFT", "trial-fit record"), station_refs),
            _stage("STN-30", "station", "Build PV roof and MEP cassettes", "station systems cell", 3, "STN-20",
                   ("PV modules", "roof panels", "lighting and drainage looms"), "tested roof cassette kit", "electrical isolation and water test",
                   ("PV flash test", "bond test", "drainage flow test"), station_refs),
            _stage("STN-40", "station", packages["st-10-civil-structure"]["work_order_title"], "station erection site", 8, "STN-30",
                   ("platform modules", "portal frames", "roof cassettes"), "structurally complete station", "350 mm platform/rail datum and structural survey",
                   ("foundation survey", "bolt torque map", "platform datum survey"), station_refs),
            _stage("STN-50", "station", packages["st-20-mep-passenger-systems"]["work_order_title"], "station commissioning", 6, "STN-40",
                   ("passenger systems", "fare equipment", "safety and communications kit"), "commissioned standard station", "integrated passenger and life-safety acceptance",
                   ("MEP test pack", "accessibility checklist", "fire and evacuation evidence"), station_refs),
        ),
    )

    viaduct_refs = (
        "docs/civil/viaduct-first-article-test-plan.md",
        "docs/civil/viaduct-transport-and-erection-envelope.md",
        "docs/civil/viaduct-design-basis.md",
        "design/component-catalogue/src/osr_mech/civil/viaduct.py",
        "lib/templates/foundation-catalog.toml",
        "lib/templates/civil-construction-systems.toml",
        "design/component-catalogue/src/osr_mech/civil/construction.py",
    )
    viaduct = FabricationStream(
        "viaduct",
        "Viaduct fabrication and erection",
        "OSR-Pi25 twin-track erected bay",
        "two <=75 t, 2.9 m wide decked pi-beams plus selected foundation, hollow cap, bearings, walkway cassettes and trackform",
        (
            _stage("VIA-05", "viaduct", "Construct and test foundation, pier column and hollow cap", "substructure erection front", 13, None,
                   ("geotechnical zone", "utility clearance", "actual pile/shaft schedule", "test plan", "released column and cap design"), "tested foundation, completed pier column and erected hollow cap", "actual foundation length/cost, representative load-test release, column records and cap seat survey",
                   ("foundation schedule", "actual installed lengths", "test result", "column concrete record", "cap lifting record", "bearing-seat as-built survey"), viaduct_refs),
            _stage("VIA-10", "viaduct", "Prepare Pi-beam mould, cage and tendons", "decked pi-beam precast yard", 2, "VIA-05",
                   ("surveyed Pi25 mould", "reinforcement", "prestress strand", "cast-in items"), "released pre-pour assembly", "mould, cage, tendon and insert hold point",
                   ("bed survey", "rebar and cover record", "tendon calibration"), viaduct_refs),
            _stage("VIA-20", "viaduct", "Cast, cure and transfer prestress", "decked pi-beam precast yard", 2, "VIA-10",
                   ("released pre-pour assembly", "concrete batch"), "demoulded OSR-Pi25 unit", "strength, maturity and transfer release",
                   ("batch records", "cube strength", "prestress elongation", "transfer sequence"), viaduct_refs),
            _stage("VIA-30", "viaduct", "Survey and first-article proof", "precast QA bay", 1, "VIA-20",
                   ("demoulded Pi25", "survey and NDT equipment"), "accepted Pi25 production unit", "dimensions, camber, cover, NDT and drainage",
                   ("dimensional report", "camber survey", "NDT", "drain test"), viaduct_refs),
            _stage("VIA-40", "viaduct", "Transport and certify erection system", "controlled transport route", 1, "VIA-30",
                   ("<=75 t Pi25", "modular transporter", "portal launcher or crane load chart", "certified rigging"), "beam and erection plant released inside envelope", "route, radius, rigging, wind and ground-bearing release",
                   ("route clearance", "actual load chart", "rigging certificate", "wind-limit and ground-pressure record"), viaduct_refs),
            _stage("VIA-50", "viaduct", "Set bearings and erect two Pi-beams", "portal/short-launcher erection front", 1, "VIA-40",
                   ("tested pier and 7 m cap", "four internal-support bearings", "two Pi25 units", "synchronized strand jacks"), "stable twin-track erected bay after two main lifts", "bearing identity/orientation, synchronization and one-line internal-support survey",
                   ("bearing schedule", "strand-jack log", "seat survey", "beam level and gap survey"), viaduct_refs),
            _stage("VIA-55", "viaduct", "Connect short semi-continuous unit", "continuity connection front", 1, "VIA-50",
                   ("surveyed adjacent Pi spans", "released link-slab or diaphragm cage", "small closure or grouted-socket materials"), "four-span unit structurally connected at internal support", "CWR/braking/temperature/seismic/foundation-flexibility analysis and connection fatigue release",
                   ("connection traveller", "rebar and cover record", "maturity/grout record", "waterproofing and survey acceptance"), viaduct_refs),
            _stage("VIA-60", "viaduct", "Install trackform, egress and containment", "viaduct finishing front", 2, "VIA-55",
                   ("local plinths", "track panels", "walkway and containment kits"), "released operational viaduct bay", "track, drainage, earthing and egress release",
                   ("track geometry", "drain test", "1.0 m walkway gauge", "1.4 m containment survey"), viaduct_refs),
        ),
    )

    train_refs = (
        "lib/templates/manufacturing-schedule.toml",
        "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json",
        "docs/rolling-stock/light-metro-3car/assembly-plan.md",
    )
    train_stages: list[FabricationStage] = []
    previous: str | None = None
    for package_id in (
        "rs-10-material-kit", "rs-20-carbody-bogie", "rs-23-moulded-body-modules",
        "rs-25-clip-on-body", "rs-30-traction-battery-control",
        "rs-40-fitout-static-test", "rs-50-dynamic-commissioning",
    ):
        package = packages[package_id]
        stage_id = package_id.upper()
        train_stages.append(
            _stage(
                stage_id, "train", package["work_order_title"], package["work_center"],
                float(package["duration_days"]), previous,
                tuple(package["materials_or_inputs"].split(", ")),
                package["deliverables"], package["qa_gate_hint"],
                tuple(package["evidence_required"].split(", ")), train_refs,
            )
        )
        previous = stage_id
    train = FabricationStream(
        "train",
        "LM3 fabrication and final assembly",
        "49.5 m three-car driverless LM3",
        f"{len(train_manifest['product_items'])} product items, "
        f"{len(train_manifest['assemblies'])} controlled assemblies, one production traveler",
        tuple(train_stages),
    )
    return track, station, viaduct, train


def assembly_state(elapsed_s: float) -> tuple[StageState, ...]:
    """Map real animation time to concurrent work-in-progress states."""

    elapsed_s = min(max(float(elapsed_s), 0.0), ANIMATION_DURATION_S)
    fraction = elapsed_s / ANIMATION_DURATION_S
    states: list[StageState] = []
    for stream in fabrication_streams():
        total = sum(stage.duration_days for stage in stream.stages)
        cursor = 0.0
        selected = stream.stages[-1]
        progress = 100.0
        status = "complete"
        for stage in stream.stages:
            start = cursor / total
            cursor += stage.duration_days
            end = cursor / total
            if fraction < start:
                continue
            if fraction < end or stage is stream.stages[-1]:
                selected = stage
                progress = min(100.0, max(0.0, (fraction - start) / (end - start) * 100.0))
                status = "active" if progress < 100.0 else "complete"
                break
        states.append(
            StageState(
                stream.id,
                selected.id,
                selected.title,
                status,
                round(progress, 1),
                "released" if status == "complete" else "hold-point-open",
            )
        )
    return tuple(states)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def twin_checks(streams: tuple[FabricationStream, ...] | None = None) -> tuple[dict[str, Any], ...]:
    streams = streams or fabrication_streams()
    stages = [stage for stream in streams for stage in stream.stages]
    ids = {stage.id for stage in stages}
    source_paths = {REPO_ROOT / ref for stage in stages for ref in stage.source_refs}
    station_manifest = json.loads(STATION_MANIFEST_PATH.read_text(encoding="utf-8"))
    train_manifest = json.loads(TRAINSET_MANIFEST_PATH.read_text(encoding="utf-8"))
    checks = (
        ("four-product-streams", len(streams) == 4, len(streams)),
        ("unique-stage-identifiers", len(ids) == len(stages), len(stages)),
        ("predecessors-resolve", all(s.predecessor is None or s.predecessor in ids for s in stages), len(ids)),
        ("qa-evidence-on-every-stage", all(s.qa_hold and s.evidence for s in stages), len(stages)),
        ("source-references-resolve", all(path.is_file() for path in source_paths), len(source_paths)),
        ("station-product-tree-loaded", len(station_manifest["variants"]) == 7, len(station_manifest["variants"])),
        ("train-product-tree-loaded", len(train_manifest["product_items"]) >= 101 and len(train_manifest["assemblies"]) == 26,
         {"items": len(train_manifest["product_items"]), "assemblies": len(train_manifest["assemblies"])}),
    )
    return tuple({"id": check_id, "passed": passed, "observed": observed} for check_id, passed, observed in checks)


def fabrication_assembly_manifest() -> dict[str, Any]:
    streams = fabrication_streams()
    source_paths = sorted({REPO_ROOT / ref for stream in streams for stage in stream.stages for ref in stage.source_refs})
    manifest = {
        "schema": TWIN_SCHEMA,
        "title": "OpenSourceRail fabrication and assembly digital twin",
        "status": "planning / first-article release control",
        "scope": "representative track, station, viaduct, and LM3 trainset production routes",
        "animation_duration_s": ANIMATION_DURATION_S,
        "visual_tour": {
            "duration_s": VISUAL_TOUR_DURATION_S,
            "presentation": "sequential close-up assembly tour; not a project schedule",
            "phases": list(VISUAL_TOUR_PHASES),
            "final_overview_s": [82.0, VISUAL_TOUR_DURATION_S],
        },
        "streams": [asdict(stream) for stream in streams],
        "integration_dependencies": [
            {"from": "VIA-55", "to": "VIA-60", "interface": "continuity-connection and deck-to-trackform"},
            {"from": "STN-40", "to": "TRK-50", "interface": "350 mm platform/rail datum"},
            {"from": "TRK-50", "to": "RS-50-DYNAMIC-COMMISSIONING", "interface": "released test-track geometry"},
        ],
        "state_snapshots": {
            str(second): [asdict(state) for state in assembly_state(second)]
            for second in (0, 12, 24, 36, 48)
        },
        "source_register": {
            str(path.relative_to(REPO_ROOT)): {"bytes": path.stat().st_size, "sha256": _sha256(path)}
            for path in source_paths
        },
        "checks": list(twin_checks(streams)),
        "limitations": [
            "planning twin, not released shop drawings or construction methodology",
            "numeric weld procedures, torques, lift studies, temporary works, and supplier instructions remain release inputs",
            "animation time is normalized; duration_days retains the production planning basis",
        ],
    }
    manifest["passed"] = all(check["passed"] for check in manifest["checks"])
    return manifest


def write_manifest(path: Path) -> Path:
    manifest = fabrication_assembly_manifest()
    if not manifest["passed"]:
        raise ValueError("fabrication and assembly twin checks failed")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = write_manifest(args.out)
    print(f"wrote {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

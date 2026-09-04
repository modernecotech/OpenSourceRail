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
        "release_packages": [asdict(item) | {"status": STATUS, "release_boundary": BOUNDARY} for item in packages],
        "drawing_definitions": [asdict(item) | {"status": STATUS, "release_boundary": BOUNDARY} for item in drawings],
        "validation": {
            "all_ifc_types_classified_once": True,
            "all_ifc_types_have_drawing_coverage": True,
            "all_packages_have_hold_points": True,
            "site_specific_evidence_remains_open": True,
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
        lines += [f"## {package['id']} — {package['title']}", "", f"Lane: `{package['delivery_lane']}`", "", f"Drawing briefs: {_table([f'`{value}`' for value in package['drawing_ids']])}", "", "Tooling/gauges: " + ", ".join(f"`{value}`" for value in package["tooling_ids"]), "", "Controlled outputs:", ""]
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

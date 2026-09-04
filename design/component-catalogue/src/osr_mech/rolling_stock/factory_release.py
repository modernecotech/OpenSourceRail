"""Controlled v2A factory drawing and interface-release work packages.

The product tree identifies what exists; these packages identify the drawing,
datum, tooling and verification records needed to turn the dedicated LM3 part
families into controlled factory information.  They deliberately stop before
supplier selection, structural approval or physical first-article acceptance.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FactoryReleasePackage:
    id: str
    title: str
    drawing_ids: tuple[str, ...]
    product_ids: tuple[str, ...]
    tooling_ids: tuple[str, ...]
    frozen_inputs: tuple[str, ...]
    controlled_outputs: tuple[str, ...]
    verification: tuple[str, ...]
    release_boundary: str


@dataclass(frozen=True)
class FactoryDrawingMetadata:
    id: str
    title: str
    owner: str
    source_refs: tuple[str, ...]
    required_views: tuple[str, ...]


def factory_drawing_metadata() -> tuple[FactoryDrawingMetadata, ...]:
    """Return drawing-specific ownership, source and minimum-view controls."""

    rs = "docs/rolling-stock/light-metro-3car"
    return (
        FactoryDrawingMetadata(
            "LM3-BDY-100",
            "carbody primary steel and recovery load-path assembly",
            "vehicle structures + fabricator",
            (f"{rs}/body.md", f"{rs}/field-rerailing-concept.md"),
            (
                "carbody plan, side and end elevations",
                "primary datum and support-point scheme",
                "welded load-path and recovery-interface details",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-BDY-110",
            "underframe ladder, floor and equipment-support assembly",
            "vehicle structures + fabricator",
            (f"{rs}/body.md", f"{rs}/dedicated-parts-and-moulds.md"),
            (
                "underframe plan and longitudinal section",
                "cross-bearer and bolster station sections",
                "cut/bend/weld and fixture datum details",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-BDY-120",
            "sidewall and roof spaceframe assembly",
            "vehicle structures + fabricator",
            (f"{rs}/body.md", f"{rs}/dedicated-parts-and-moulds.md"),
            (
                "left/right sideframe elevations",
                "door/window aperture details",
                "roof bow, cantrail and equipment-rail sections",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-BDY-150",
            "exterior GFRP material, mould and trim control",
            "composites engineering + fabricator",
            (f"{rs}/modular-fiberglass-body.md", f"{rs}/dedicated-parts-and-moulds.md"),
            (
                "tool-face and split-line views",
                "laminate/core/insert sections",
                "trim, drill, edge and repair-zone maps",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-BDY-155",
            "identical A/B-end GFRP cowl cast kit",
            "composites engineering + vehicle integration",
            (f"{rs}/end-cowl.md", f"{rs}/dedicated-parts-and-moulds.md"),
            (
                "front, side and plan exterior surfaces",
                "six-piece split, flange and trim scheme",
                "glass, lamp, sensor, drain and service-access sections",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-BDY-160",
            "one-metre clip-on GFRP body module system",
            "composites engineering + fabricator",
            (f"{rs}/modular-fiberglass-body.md", f"{rs}/dedicated-parts-and-moulds.md"),
            (
                "common side and roof module views",
                "clip, anti-lift, seal and drain sections",
                "master-frame and replacement-clearance details",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-BDY-165",
            "exterior module trim and bay configuration",
            "configuration engineering + composites fabricator",
            (f"{rs}/dedicated-parts-and-moulds.md",),
            (
                "solid/window/door/roof trim nests",
                "serialized car bay map",
                "datum, drill, seal and repair overlays",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-FAS-180",
            "panoramic glass carrier, seal and drainage interface",
            "vehicle integration + glazing supplier",
            (f"{rs}/end-cowl.md", f"{rs}/dedicated-parts-and-moulds.md"),
            (
                "front carrier and pane-edge elevation",
                "setting-block and secondary-retention sections",
                "seal compression, drain, heater and removal-path details",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-FAS-185",
            "reversible front-lamp cassette and aiming interface",
            "vehicle integration + lamp supplier",
            (f"{rs}/end-cowl.md", f"{rs}/dedicated-parts-and-moulds.md"),
            (
                "A/B cassette installation views",
                "optical-axis and adjuster datum diagram",
                "harness, earth, drip-loop and service-clearance details",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-HVAC-220",
            "roof HVAC installation and duct interface",
            "HVAC supplier + vehicle integration",
            (f"{rs}/roof-fitout.md", f"{rs}/traction.md"),
            (
                "roof unit plan and side installation",
                "curb, duct and condensate sections",
                "service lift, airflow and adjacent-equipment clearances",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-ROOF-225",
            "roof fairing, penetration and service-zone coordination",
            "vehicle integration",
            (f"{rs}/roof-fitout.md", f"{rs}/dedicated-parts-and-moulds.md"),
            (
                "complete roof equipment plan",
                "curb, rail, gland, drain and fairing sections",
                "removal, worker-access and finish/heat/electrical keep-out zones",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-HV-325",
            "rooftop PV and charge-input assembly",
            "traction energy + vehicle integration",
            (f"{rs}/roof-fitout.md", f"{rs}/traction.md", f"{rs}/interfaces.md"),
            (
                "PV/string/MPPT roof plan",
                "rail, clamp, bonded-laminate and cable-gland sections",
                "isolation, bonding, fire-switch and cleaner-service diagram",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-INT-230",
            "interior fit-out installation",
            "interior integration",
            (f"{rs}/interior-layout.md", f"{rs}/dedicated-parts-and-moulds.md"),
            (
                "saloon plan and reflected ceiling plan",
                "sidewall and transverse sections",
                "seat, rail, lighting, equipment and sequential-removal details",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-INT-231",
            "interior moulded-panel, trim and access family",
            "interior/composites engineering",
            (f"{rs}/dedicated-parts-and-moulds.md", f"{rs}/cabin-fiberglass.md"),
            (
                "panel family elevations and nesting map",
                "tool-face, split, trim and insert views",
                "edge radius, gaps, hatches and service-access sections",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-FIX-235",
            "common service rail, fastener and fixture adapters",
            "vehicle integration + manufacturing engineering",
            (f"{rs}/interior-layout.md",),
            (
                "rail extrusion and installed-coordinate views",
                "foot, end-stop and adapter variants",
                "grip, locking, isolation and accessible-removal details",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-FIN-240",
            "pre-cut livery film artwork, application and repair",
            "operator identity + finish engineering",
            (f"{rs}/exterior-finish-process.md",),
            (
                "flattened bay-numbered artwork sheets",
                "seam, overlap, edge and keep-out maps",
                "datum-mark, patch and complete-module removal details",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-FIN-245",
            "radiative roof-coating qualification and trial",
            "materials/test authority + finish engineering",
            (f"{rs}/exterior-finish-process.md", f"{rs}/roof-fitout.md"),
            (
                "coupon and exposure matrix",
                "one-car paired roof-zone application plan",
                "sensor, keep-out, inspection, cleaning and repair maps",
            ),
        ),
        FactoryDrawingMetadata(
            "LM3-REC-270",
            "jacking, lifting, towing and field-rerailing interface",
            "vehicle structures + recovery engineer",
            (f"{rs}/field-rerailing-concept.md", f"{rs}/body.md"),
            (
                "J1--J4 underside and side-location views",
                "keyed adapter, pad, eye and lug sections",
                "support combinations, reactions, stop conditions and recovery sequence diagrams",
            ),
        ),
    )


def factory_release_packages() -> tuple[FactoryReleasePackage, ...]:
    """Return the ordered v2A work packages owned by the local factory team."""

    return (
        FactoryReleasePackage(
            "LM3-FRP-010",
            "primary chassis, transverse structure and stepped-floor drawing pack",
            ("LM3-BDY-100", "LM3-BDY-110", "LM3-BDY-120"),
            (
                "LM3-BDY-P010", "LM3-BDY-P020", "LM3-BDY-P021", "LM3-BDY-P030",
                "LM3-BDY-P060", "LM3-BDY-P061", "LM3-BDY-P070", "LM3-BDY-P080",
            ),
            ("LM3-TOOL-STEEL-FIXTURE", "LM3-TOOL-DATUM-GAUGE"),
            (
                "released structural load cases and material grades",
                "door, window, bogie, battery, coupler and roof interface reactions",
                "weld-class, distortion and corrosion-process requirements",
            ),
            (
                "member and plate drawings with datums, tolerances and material callouts",
                "cut, bend, machining and weld maps with heat/part trace fields",
                "fixture loading sequence and dimensional inspection characteristic list",
                "mass-properties contribution and controlled centre-of-gravity ledger rows",
            ),
            (
                "independent calculation review",
                "fixture and tack survey",
                "post-weld datum/straightness survey",
                "weld/NDT and corrosion hold-point records",
            ),
            "No steel cutting release until structural calculations, WPS/PQR, material certificates and drawing approval are present.",
        ),
        FactoryReleasePackage(
            "LM3-FRP-020",
            "one-metre exterior module variant and retention drawing pack",
            ("LM3-BDY-150", "LM3-BDY-160", "LM3-BDY-165"),
            ("LM3-BDY-P130", "LM3-BDY-P131", "LM3-BDY-P132", "LM3-BDY-P133", "LM3-BDY-P140"),
            ("LM3-TOOL-SIDE-MOULD", "LM3-TOOL-SIDE-VARIANT-NEST", "LM3-TOOL-ROOF-MOULD", "LM3-TOOL-TRIM-DRILL"),
            (
                "accepted laminate, core, gelcoat, insert, seal and fire-material system",
                "frozen car bay map and door/window/roof service-clearance model",
                "released clip, anti-lift, pressure and debris load cases",
            ),
            (
                "A/B tool-face, split, draft, trim and insert drawings",
                "solid/window/door/roof variant CNC trim and drill definitions",
                "clip, seal, anti-lift and drain interface drawing",
                "serialized module/bay configuration and repair map",
            ),
            (
                "mould survey and witness coupon",
                "trim/drill first article",
                "master-frame interchange and anti-lift proof",
                "water, vibration and timed module replacement trial",
            ),
            "Module skins remain non-structural and may not close primary carbody or roof-equipment load paths.",
        ),
        FactoryReleasePackage(
            "LM3-FRP-030",
            "panoramic front-glass carrier, seal and drainage interface pack",
            ("LM3-BDY-155", "LM3-FAS-180"),
            ("LM3-CWL-P016", "LM3-FAS-P010", "LM3-FAS-P030", "LM3-EXT-P030"),
            ("LM3-TOOL-COWL-MOULD", "LM3-TOOL-GLASS-CARRIER-NEST", "LM3-TOOL-WATER-TEST"),
            (
                "supplier glass construction, edge, mass, heater and retention loads",
                "accepted glazing adhesive/gasket and EPDM compatibility data",
                "released steel backing-ring and cowl flange datums",
            ),
            (
                "carrier segments, corner joints, setting blocks and secondary-retention drawing",
                "glass-edge clearance and seal-compression characteristic map",
                "drain rail, washer sleeve, earth and heater-service route",
                "protected removal path and lifting-tool access drawing",
            ),
            (
                "carrier and backing-ring datum survey",
                "retention calculation and representative proof",
                "compression/drain map and controlled spray test",
                "heated-pane service isolation and timed removal/refit trial",
            ),
            "The selected glazing supplier retains responsibility for pane construction and its bonded cassette process.",
        ),
        FactoryReleasePackage(
            "LM3-FRP-040",
            "reversible front-lamp cassette and fascia-service pack",
            ("LM3-BDY-155", "LM3-FAS-185"),
            ("LM3-CWL-P014", "LM3-CWL-P015", "LM3-FAS-P020", "LM3-END-P050"),
            ("LM3-TOOL-COWL-MOULD", "LM3-TOOL-LAMP-AIM"),
            (
                "selected lamp photometric, thermal, EMC, IP and connector data",
                "A/B end configuration and cowl service-hatch envelope",
                "released lamp reaction, aiming and retention requirements",
            ),
            (
                "common reversible tray, adjuster and retained service-bracket drawing",
                "lamp optical-axis datum and adjustment-limit schedule",
                "harness, earth, drip-loop and connector-access route",
                "A/B interchange and lamp-cassette configuration record",
            ),
            (
                "tray and optical-axis datum gauge",
                "aim range, lock and vibration-retention test",
                "thermal/IP/functional evidence review",
                "service-hatch and cassette removal demonstration",
            ),
            "The jig establishes mechanical aim only; supplier and vehicle photometric evidence remains mandatory.",
        ),
        FactoryReleasePackage(
            "LM3-FRP-050",
            "roof curb, HVAC, PV, antenna, fairing and access-zone pack",
            ("LM3-HVAC-220", "LM3-HV-325", "LM3-ROOF-225"),
            (
                "LM3-BDY-P080", "LM3-BDY-P133", "LM3-ROOF-P010", "LM3-ROOF-P020",
                "LM3-ROOF-P030", "LM3-ROOF-P040", "LM3-EXT-P040", "LM3-EXT-P050",
                "LM3-EXT-P070", "LM3-TRC-P050",
            ),
            ("LM3-TOOL-ROOF-MOULD", "LM3-TOOL-ROOF-FAIRING-MOULD", "LM3-TOOL-WATER-TEST"),
            (
                "supplier HVAC, PV, resistor and antenna mass/reaction/service envelopes",
                "released roof-rail capacity, vehicle gauge and lifting/fall-access constraints",
                "accepted sealing, bonding, fire and electrical-isolation systems",
            ),
            (
                "roof equipment coordinate and penetration schedule",
                "curb, duct, drain, rail/pad, gland, bond and fairing drawings",
                "HVAC/PV/antenna removal paths and tool/worker access zones",
                "finish, anti-slip, heat and electrical keep-out mask map",
            ),
            (
                "rail/curb datum and equipment fit survey",
                "attachment proof, bond continuity and isolation checks",
                "roof/condensate water tests and airflow clearance review",
                "service-removal demonstration with adjacent equipment retained",
            ),
            "No supplier unit or person load may be reacted through a clip-on skin or non-structural fairing.",
        ),
        FactoryReleasePackage(
            "LM3-FRP-060",
            "interior moulding, floor, service-access and fitout pack",
            ("LM3-INT-230", "LM3-INT-231"),
            (
                "LM3-INT-P010", "LM3-INT-P020", "LM3-INT-P021", "LM3-INT-P022",
                "LM3-INT-P030", "LM3-INT-P031", "LM3-INT-P032", "LM3-INT-P040",
                "LM3-INT-P041", "LM3-INT-P050", "LM3-INT-P051", "LM3-INT-P052",
                "LM3-EXT-P060", "LM3-EXT-P061", "LM3-EXT-P062", "LM3-EXT-P063",
                "LM3-EXT-P064", "LM3-EXT-P065", "LM3-EXT-P066",
            ),
            (
                "LM3-TOOL-INT-CEILING-MOULD", "LM3-TOOL-INT-SIDE-MOULD",
                "LM3-TOOL-INT-STRAKE-MOULD", "LM3-TOOL-INT-DOOR-PRM-MOULD",
                "LM3-TOOL-FLOOR-TEMPLATE", "LM3-TOOL-SERVICE-RAIL",
            ),
            (
                "accepted fire/smoke material and supplier equipment evidence",
                "frozen door/window/HVAC/lighting/seat/PRM equipment envelopes",
                "released passenger load, egress, accessibility and cleaning requirements",
            ),
            (
                "individual panel, mould, trim, edge-radius and insert drawings",
                "floor board/covering seam, hatch, ramp and threshold definitions",
                "service-access and sequential removal map for every concealed system",
                "serialized panel, fastener, equipment and label configuration schedule",
            ),
            (
                "mould/trim first article and fire-material trace review",
                "dry fit, gap, rattle, sharp-edge and captive-fastener inspections",
                "door/window/equipment removal sweeps and accessibility survey",
                "floor load, slip, seam, cleaning and water-path evidence",
            ),
            "Interior finish panels carry no seat, handrail, equipment or passenger restraint load.",
        ),
        FactoryReleasePackage(
            "LM3-FRP-070",
            "common service rail, fastener and fixture-adapter pack",
            ("LM3-INT-230", "LM3-FIX-235"),
            ("LM3-FIX-P010", "LM3-FIX-P020", "LM3-FIX-P030"),
            ("LM3-TOOL-SERVICE-RAIL", "LM3-TOOL-FIXTURE-PROOF"),
            (
                "fixture-specific service/ultimate loads and attachment envelopes",
                "selected rail alloy/temper, fastener, isolator and finish data",
                "carbody attachment capacity and electrical/galvanic constraints",
            ),
            (
                "rail extrusion, cut/drill, end-stop and foot drawing",
                "seat, handrail, PIS/CCTV and cable-support adapter variants",
                "fastener grip, locking, torque-authority and captive-part schedule",
                "installed coordinate, orientation and accessible-removal map",
            ),
            (
                "rail/foot and fixture-specific calculation review",
                "adapter and installed-grip gauges",
                "representative pull/slip/rotation proof",
                "egress, snag, isolation and timed replacement inspection",
            ),
            "Each adapter needs its own released load case; one generic proof result cannot qualify every fixture.",
        ),
        FactoryReleasePackage(
            "LM3-FRP-080",
            "pre-cut exterior film artwork, application and repair pack",
            ("LM3-FIN-240",),
            ("LM3-FIN-P010", "LM3-BDY-P130", "LM3-BDY-P131", "LM3-BDY-P132", "LM3-CWL-P011", "LM3-CWL-P012", "LM3-CWL-P013", "LM3-CWL-P014", "LM3-CWL-P015"),
            ("LM3-TOOL-FILM-TEMPLATE", "LM3-TOOL-COATING-COUPON"),
            (
                "approved artwork, colours, logos and operator/legal markings",
                "selected rail-use film/ink/overlaminate/edge system",
                "accepted cured steel/GFRP base finishes and cleaning process",
            ),
            (
                "bay-numbered cut files with controlled seams, overlaps and datum marks",
                "substrate acceptance, environment and installer record forms",
                "edge/keep-out inspection map and patch/one-metre module repair instruction",
                "film material, print batch and retained-coupon trace schedule",
            ),
            (
                "actual-substrate adhesion/removal coupon",
                "first-car edge, seam and appearance inspection",
                "wash/water and cleaning-chemical compatibility test",
                "local patch and complete module removal demonstration",
            ),
            "Film replaces decorative masking only and never substitutes for corrosion, fire, sealing or electrical protection.",
        ),
        FactoryReleasePackage(
            "LM3-FRP-090",
            "radiative roof-coating coupon and one-car trial pack",
            ("LM3-FIN-245",),
            ("LM3-FIN-P020", "LM3-BDY-P133", "LM3-ROOF-P030", "LM3-ROOF-P040"),
            ("LM3-TOOL-RADIATIVE-COUPON", "LM3-TOOL-COATING-RACK"),
            (
                "controlled formulation and application process",
                "accepted rail fire/chemical and GFRP compatibility evidence",
                "frozen roof equipment, service, drainage and keep-out map",
            ),
            (
                "coupon dimensions, substrate, coating thickness and exposure matrix",
                "new/aged/soiled/cleaned optical measurement procedure",
                "one-car paired roof-zone sensor and HVAC-energy trial plan",
                "inspection, cleaning, local repair and trial-removal instructions",
            ),
            (
                "adhesion, flexibility, thermal-cycle, UV, abrasion and wash ageing",
                "new and aged solar reflectance/emittance measurement",
                "glare, runoff, soiling and service-access review",
                "representative hot-service one-car trial and independent disposition",
            ),
            "Research values are screening targets only; the baseline qualified light roof finish remains available if the trial fails.",
        ),
        FactoryReleasePackage(
            "LM3-FRP-100",
            "vehicle jacking, lifting, towing and field-rerailing interface pack",
            ("LM3-BDY-100", "LM3-REC-270"),
            ("LM3-BDY-P120",),
            ("LM3-TOOL-STEEL-FIXTURE", "LM3-TOOL-DATUM-GAUGE", "LM3-TOOL-LIFT-COLUMNS"),
            (
                "individual-car mass and centre-of-gravity envelopes",
                "released underframe, articulation, bogie-retention and coupler load cases",
                "selected depot and portable recovery equipment interfaces",
            ),
            (
                "J1--J4 pad, lifting eye, tow/rerailing lug and keyed-adapter drawings",
                "permitted support combinations, reactions, stop conditions and labels",
                "vehicle isolation, brake release, bogie retention and recovery diagrams",
                "proof-load, inspection, NDT, maintenance and damage-rejection schedule",
            ),
            (
                "structural and weld/NDT calculation review",
                "four-point datum/interchange gauge",
                "representative proof and asymmetric/loss-of-pressure trials",
                "timed depot lift and field rerailing demonstration by trained crews",
            ),
            "Automotive scissor jacks, unilateral lifts and work beneath an uncribbed hydraulic load remain prohibited.",
        ),
    )


def factory_release_payload() -> dict[str, object]:
    packages = factory_release_packages()
    return {
        "schema": "org.opensourcerail.lm3-factory-release-work-packages.v1",
        "design_id": "LM3-V2A-FACTORY-RELEASE",
        "status": "controlled-work-package-definitions; release evidence open",
        "package_count": len(packages),
        "packages": [
            {
                key: list(value) if isinstance(value, tuple) else value
                for key, value in asdict(package).items()
            }
            for package in packages
        ],
        "global_release_boundary": (
            "These work packages define drawing and evidence scope. They are not approved drawings, "
            "supplier selections, signed calculations or physical first-article records."
        ),
    }


def factory_release_record_template(payload: dict[str, object]) -> dict[str, object]:
    """Build an unfilled drawing/tooling/verification release record.

    The enriched payload is supplied by ``buildable_trainset`` after product
    and tooling IDs have been checked against the live design registries.
    Empty issue, evidence and approval fields are intentional: this artifact
    is a controlled work surface, never evidence that factory release occurred.
    """

    packages: list[dict[str, object]] = []
    for raw in payload["packages"]:  # type: ignore[union-attr]
        package = dict(raw)
        packages.append(
            {
                "package_id": package["id"],
                "title": package["title"],
                "release_status": "open-unissued",
                "release_boundary": package["release_boundary"],
                "prerequisite_records": [
                    {
                        "requirement": requirement,
                        "status": "open",
                        "evidence_ref": "",
                        "evidence_sha256": "",
                        "reviewed_by": "",
                    }
                    for requirement in package["frozen_inputs"]
                ],
                "drawing_records": [
                    {
                        "drawing_id": drawing_id,
                        "definition_seed_ref": f"factory-drawings/{drawing_id}.json",
                        "revision": "",
                        "issue_status": "unissued",
                        "native_file_ref": "",
                        "published_file_ref": "",
                        "published_file_sha256": "",
                        "drawn_by": "",
                        "checked_by": "",
                        "approved_by": "",
                        "issue_date": "",
                    }
                    for drawing_id in package["drawing_ids"]
                ],
                "product_configuration_records": [
                    {
                        "product_id": product["id"],
                        "title": product["title"],
                        "route": product["route"],
                        "reference_quantity": product["quantity_per_trainset"],
                        "unit": product["unit"],
                        "controlled_revision_or_supplier_configuration": "",
                        "mass_record_ref": "",
                        "drawing_coverage_status": "unverified",
                    }
                    for product in package["product_rows"]
                ],
                "tooling_release_records": [
                    {
                        "tooling_id": tooling_id,
                        "revision": "",
                        "survey_or_calibration_ref": "",
                        "evidence_sha256": "",
                        "accepted_by": "",
                        "status": "unreleased",
                    }
                    for tooling_id in package["tooling_ids"]
                ],
                "controlled_output_records": [
                    {
                        "deliverable": deliverable,
                        "status": "open",
                        "artifact_ref": "",
                        "artifact_sha256": "",
                        "checked_by": "",
                    }
                    for deliverable in package["controlled_outputs"]
                ],
                "verification_records": [
                    {
                        "verification": verification,
                        "status": "not-performed",
                        "procedure_revision": "",
                        "equipment_or_gauge_refs": [],
                        "result_artifact_ref": "",
                        "result_artifact_sha256": "",
                        "performed_by": "",
                        "independently_reviewed_by": "",
                    }
                    for verification in package["verification"]
                ],
                "approvals": {
                    "design_authority": "",
                    "manufacturing_engineering": "",
                    "quality": "",
                    "independent_check": "",
                    "release_date": "",
                },
            }
        )

    drawing_ids = {
        row["drawing_id"]
        for package in packages
        for row in package["drawing_records"]  # type: ignore[union-attr]
    }
    return {
        "schema": "org.opensourcerail.lm3-factory-release-record.v1",
        "template_status": "unfilled-not-release-evidence",
        "design_id": payload["design_id"],
        "source_work_packages": "design/component-catalogue/catalog/buildable-trainset/factory-release-work-packages.json",
        "first_article_id": "LM3-FA-001",
        "coverage": {
            "package_count": len(packages),
            "open_package_count": len(packages),
            "unique_drawing_count": len(drawing_ids),
            "controlled_product_count": payload["controlled_product_count"],
            "unique_tooling_count": len(payload["tooling_ids"]),  # type: ignore[arg-type]
        },
        "instructions": [
            "retain all packages and rows; supersede by controlled revision rather than deleting history",
            "bind every issued drawing, prerequisite and result artifact by repository-relative reference and SHA-256",
            "record exact supplier configurations and production-part revisions before drawing approval",
            "do not mark a verification complete from design-reference geometry or an unperformed template",
            "release a package only when all prerequisites, drawings, product configurations, tooling, outputs, verifications and approvals are accepted",
        ],
        "packages": packages,
        "release_warning": payload["global_release_boundary"],
    }


def render_factory_release_readiness(record: dict[str, object]) -> str:
    """Render the intentionally open factory-package readiness summary."""

    coverage = dict(record["coverage"])  # type: ignore[arg-type]
    lines = [
        "# LM3 factory drawing and interface readiness",
        "",
        "Generated by `tools/automation/buildable-trainset.sh`. This register is",
        "the review surface for issuing the ten factory packages; blank template",
        "fields and `open-unissued` states are deliberate and are not release evidence.",
        "",
        f"- Template status: `{record['template_status']}`",
        f"- Packages: **{coverage['package_count']}**; open: **{coverage['open_package_count']}**",
        f"- Unique drawing IDs: **{coverage['unique_drawing_count']}**",
        f"- Controlled product rows: **{coverage['controlled_product_count']}**",
        f"- Referenced tooling families: **{coverage['unique_tooling_count']}**",
        "",
        "| Package | Status | Drawings | Products | Prerequisites | Outputs | Verifications |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for raw in record["packages"]:  # type: ignore[union-attr]
        package = dict(raw)
        lines.append(
            f"| `{package['package_id']}` — {package['title']} | `{package['release_status']}` | "
            f"{len(package['drawing_records'])} | {len(package['product_configuration_records'])} | "
            f"{len(package['prerequisite_records'])} | {len(package['controlled_output_records'])} | "
            f"{len(package['verification_records'])} |"
        )
    lines.extend(
        [
            "",
            "Fill the machine-readable [`factory-release-record-template.json`](evidence/factory-release-record-template.json)",
            "during controlled drawing production. A package remains open until every",
            "source input, issued drawing, exact product configuration, tool/gauge record,",
            "required output, performed verification and named approval is accepted.",
            "Use the per-drawing [`factory-drawings/`](factory-drawings/index.md) seeds",
            "as drafting/checking briefs, never as issued manufacturing drawings.",
            "",
            f"Boundary: {record['release_warning']}",
            "",
        ]
    )
    return "\n".join(lines)


def factory_drawing_seed_payloads(payload: dict[str, object]) -> list[dict[str, object]]:
    """Build one non-issued drawing-definition seed per controlled drawing ID."""

    metadata = {row.id: row for row in factory_drawing_metadata()}
    packages = [dict(row) for row in payload["packages"]]  # type: ignore[union-attr]
    expected_ids = {
        drawing_id
        for package in packages
        for drawing_id in package["drawing_ids"]
    }
    if set(metadata) != expected_ids:
        raise ValueError(
            "factory drawing metadata mismatch: "
            f"missing={sorted(expected_ids - set(metadata))}, "
            f"extra={sorted(set(metadata) - expected_ids)}"
        )

    def unique(values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))

    seeds: list[dict[str, object]] = []
    for drawing_id in sorted(expected_ids):
        meta = metadata[drawing_id]
        drawing_packages = [
            package for package in packages if drawing_id in package["drawing_ids"]
        ]
        product_rows = {
            product["id"]: dict(product)
            for package in drawing_packages
            for product in package["product_rows"]
        }
        seeds.append(
            {
                "schema": "org.opensourcerail.lm3-factory-drawing-seed.v1",
                "drawing_id": drawing_id,
                "title": meta.title,
                "owner": meta.owner,
                "document_revision": "A-DRAFT",
                "issue_status": "definition-seed-not-issued",
                "package_ids": [package["id"] for package in drawing_packages],
                "source_refs": list(meta.source_refs),
                "units": "millimetres unless explicitly stated",
                "coordinate_basis": (
                    "vehicle X longitudinal from car centre, Y lateral from vehicle "
                    "centreline, Z vertical from top of rail; drawing-specific fabrication "
                    "datums must be released and related back to this basis"
                ),
                "required_views": list(meta.required_views),
                "unresolved_inputs": unique(
                    [
                        requirement
                        for package in drawing_packages
                        for requirement in package["frozen_inputs"]
                    ]
                ),
                "required_outputs": unique(
                    [
                        output
                        for package in drawing_packages
                        for output in package["controlled_outputs"]
                    ]
                ),
                "required_verification": unique(
                    [
                        verification
                        for package in drawing_packages
                        for verification in package["verification"]
                    ]
                ),
                "tooling_ids": unique(
                    [tool for package in drawing_packages for tool in package["tooling_ids"]]
                ),
                "product_rows": [product_rows[key] for key in sorted(product_rows)],
                "mandatory_drawing_controls": [
                    "drawing number, title, sheet, scale, units, projection, revision and issue status",
                    "named design, checking, manufacturing, quality and approval responsibilities",
                    "material/grade, finish/protection, mass and applicable process specification",
                    "functional datums, geometric tolerances, fits, clearances and inspection characteristics",
                    "part/assembly IDs, quantities, configuration applicability and revision-compatible BOM",
                    "joining method, weld/adhesive/fastener authority and special-process hold points",
                    "supplier-controlled dimensions and keep-outs identified rather than assumed",
                    "tooling/gauge references, inspection method, acceptance criteria and evidence route",
                ],
                "issue_record": {
                    "native_source_ref": "",
                    "published_drawing_ref": "",
                    "published_drawing_sha256": "",
                    "sheet_size": "",
                    "scale": "",
                    "drawn_by": "",
                    "checked_by": "",
                    "manufacturing_reviewed_by": "",
                    "quality_reviewed_by": "",
                    "approved_by": "",
                    "issue_date": "",
                },
                "release_boundary": (
                    "This seed aggregates controlled scope and design-reference envelopes. "
                    "It is not a dimensioned production drawing, released tool surface, NC "
                    "definition, signed calculation or authority to manufacture."
                ),
            }
        )
    return seeds


def render_factory_drawing_seed(seed: dict[str, object]) -> str:
    """Render one drawing seed as a compact drafting and checking brief."""

    lines = [
        f"# {seed['drawing_id']} — {seed['title']}",
        "",
        f"- Revision: `{seed['document_revision']}`",
        f"- Issue status: `{seed['issue_status']}`",
        f"- Owner: {seed['owner']}",
        "- Factory package: " + ", ".join(f"`{value}`" for value in seed["package_ids"]),
        "- Source: " + ", ".join(f"`{value}`" for value in seed["source_refs"]),
        f"- Coordinate basis: {seed['coordinate_basis']}",
        "",
        "## Controlled product scope",
        "",
        "| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |",
        "|---|---|---:|---:|---|",
    ]
    for raw in seed["product_rows"]:  # type: ignore[union-attr]
        product = dict(raw)
        envelope = " × ".join(
            f"{float(value):g}" for value in product["design_reference_envelope_mm"]
        )
        lines.append(
            f"| `{product['id']}` — {product['title']} | `{product['route']}` / `{product['maturity']}` | "
            f"{float(product['quantity_per_trainset']):g} {product['unit']} | {envelope} | "
            f"{product['geometry_representation']} |"
        )
    for heading, key in (
        ("Required views", "required_views"),
        ("Unresolved inputs", "unresolved_inputs"),
        ("Required outputs", "required_outputs"),
        ("Required verification", "required_verification"),
        ("Mandatory drawing controls", "mandatory_drawing_controls"),
    ):
        lines.extend(["", f"## {heading}", ""])
        lines.extend(f"- {value}" for value in seed[key])
    lines.extend(
        [
            "",
            "## Tooling and issue record",
            "",
            "Tooling: " + ", ".join(f"`{value}`" for value in seed["tooling_ids"]) + ".",
            "",
            "The machine-readable JSON beside this page contains the deliberately blank",
            "native/published file references, checksum, sheet/scale and approval fields.",
            "",
            f"Boundary: {seed['release_boundary']}",
            "",
        ]
    )
    return "\n".join(lines)


def render_factory_drawing_index(seeds: list[dict[str, object]]) -> str:
    """Render navigation and coverage for all controlled drawing seeds."""

    product_ids = {
        product["id"]
        for seed in seeds
        for product in seed["product_rows"]  # type: ignore[union-attr]
    }
    lines = [
        "# LM3 factory drawing definition seeds",
        "",
        "Generated by `tools/automation/buildable-trainset.sh`. These files give the",
        "drafting team one controlled brief per factory drawing ID. They aggregate the",
        "current product envelopes and release requirements but contain no invented",
        "production dimensions, tolerances, material selections or approvals.",
        "",
        f"- Drawing seeds: **{len(seeds)}**",
        f"- Controlled products represented: **{len(product_ids)}**",
        "- Issue state: **all definition seeds; none issued for manufacture**",
        "",
        "| Drawing | Owner | Packages | Products | JSON |",
        "|---|---|---|---:|---|",
    ]
    for seed in seeds:
        drawing_id = str(seed["drawing_id"])
        packages = "<br>".join(f"`{value}`" for value in seed["package_ids"])
        lines.append(
            f"| [`{drawing_id}`]({drawing_id}.md) — {seed['title']} | {seed['owner']} | "
            f"{packages} | {len(seed['product_rows'])} | [`json`]({drawing_id}.json) |"
        )
    lines.extend(
        [
            "",
            "Issue and verification state remains controlled by",
            "[`factory-release-readiness.md`](../factory-release-readiness.md).",
            "",
        ]
    )
    return "\n".join(lines)


__all__ = [
    "FactoryReleasePackage",
    "factory_release_packages",
    "factory_release_payload",
    "factory_release_record_template",
    "factory_drawing_metadata",
    "factory_drawing_seed_payloads",
    "render_factory_drawing_index",
    "render_factory_drawing_seed",
    "render_factory_release_readiness",
]

"""Controlled station/civil definition and release work packages.

The station product tree says what is installed.  These packages say which
drawings, inputs, tools and verification records must exist before reusable
parts may be fabricated or deployment-specific work may be released.  They do
not turn catalogue geometry into construction information.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class StationReleasePackage:
    id: str
    title: str
    delivery_lane: str
    drawing_ids: tuple[str, ...]
    product_ids: tuple[str, ...]
    tooling_ids: tuple[str, ...]
    frozen_inputs: tuple[str, ...]
    controlled_outputs: tuple[str, ...]
    verification: tuple[str, ...]
    release_boundary: str


@dataclass(frozen=True)
class StationDrawingMetadata:
    id: str
    title: str
    owner: str
    scope_type: str
    product_ids: tuple[str, ...]
    source_refs: tuple[str, ...]
    required_views: tuple[str, ...]


def station_drawing_metadata() -> tuple[StationDrawingMetadata, ...]:
    """Return drawing ownership, exact product scope and minimum views."""

    docs = "docs/stations/standard-archetype"
    catalogue = "design/component-catalogue/catalog/buildable-stations"
    return (
        StationDrawingMetadata(
            "STN-CIV-100", "precast platform and guideway product definition",
            "civil structures + precast fabricator", "reusable-fabrication-definition",
            ("STN-CIV-P010", "STN-CIV-P020", "STN-CIV-P040", "STN-PLT-P010"),
            (f"{docs}/envelope.md", f"{catalogue}/default-product-specifications.md"),
            ("module plan, elevations and typical sections", "mould, reinforcement, inserts and lifting details", "platform edge, tactile, service-trough and joint interfaces"),
        ),
        StationDrawingMetadata(
            "STN-CIV-110", "site set-out, levelling, drainage and closure coordination",
            "deployment civil engineer", "deployment-interface-definition",
            ("STN-CIV-P020", "STN-CIV-P030", "STN-CIV-P040"),
            (f"{docs}/envelope.md", f"{docs}/services.md"),
            ("survey-control and set-out plan", "longitudinal/crossfall and drainage profiles", "levelling, grout, closure-pour and outfall details"),
        ),
        StationDrawingMetadata(
            "STN-CNP-200", "platform canopy steel, footing and roof assembly",
            "structural engineer + steel fabricator", "hybrid-fabrication-definition",
            ("STN-CNP-P010", "STN-CNP-P020", "STN-CNP-P030"),
            (f"{docs}/canopy.md", f"{catalogue}/default-product-specifications.md"),
            ("canopy framing plan and elevations", "member, weld/bolt, baseplate and anchor sections", "roof cassette, joint, gutter and erection details"),
        ),
        StationDrawingMetadata(
            "STN-CNP-210", "platform canopy PV strings, bonding and drainage interfaces",
            "electrical engineer + PV integrator", "supplier-interface-definition",
            ("STN-CNP-P030", "STN-CNP-P040"),
            (f"{docs}/canopy.md", f"{docs}/services.md", f"{catalogue}/default-product-specifications.md"),
            ("module/string roof plan", "single-line, isolation, SPD and earthing diagram", "connector, cable, downlink, drain and maintenance-access details"),
        ),
        StationDrawingMetadata(
            "STN-CNP-220", "auxiliary canopy truss, roof bay and foundation interface",
            "structural engineer + steel fabricator", "deployment-led-fabrication-definition",
            ("STN-CNP-P050", "STN-CNP-P060", "STN-CNP-P070"),
            (f"{docs}/canopy.md", f"{catalogue}/default-product-specifications.md"),
            ("module row plan and elevations", "truss member, node, splice, column and base sections", "foundation reactions, anchor template and erection sequence"),
        ),
        StationDrawingMetadata(
            "STN-CNP-230", "auxiliary canopy PV, drainage, lightning and safe access",
            "electrical/civil integration", "deployment-interface-definition",
            ("STN-CNP-P050", "STN-CNP-P080", "STN-CNP-P090"),
            (f"{docs}/canopy.md", f"{catalogue}/default-product-specifications.md"),
            ("PV group and roof drainage plan", "string/protection/bonding/lightning diagrams", "gutter, outlet, walkway, guardrail and cleaning-access sections"),
        ),
        StationDrawingMetadata(
            "STN-SYS-300", "station LV, UPS, fire and services cabinet integration",
            "station MEP engineer", "supplier-interface-definition",
            ("STN-MEP-P010", "STN-MEP-P020", "STN-MEP-P030", "STN-MEP-P040"),
            (f"{docs}/services.md", f"{catalogue}/default-product-specifications.md"),
            ("equipment and maintainability layout", "LV/UPS single-line and load schedule", "earthing, fire cause/effect, lighting and containment details"),
        ),
        StationDrawingMetadata(
            "STN-SYS-310", "passenger systems, fare equipment and plinth coordination",
            "passenger systems integrator", "supplier-interface-definition",
            (
                "STN-PAX-P010", "STN-PAX-P020", "STN-PAX-P030", "STN-PAX-P040",
                "STN-PAX-P050", "STN-PAX-P060", "STN-PAX-P070", "STN-PAX-P080",
            ),
            (f"{docs}/accessibility.md", f"{docs}/services.md", f"{catalogue}/default-product-specifications.md"),
            ("equipment, coverage, sightline and accessible-route plan", "power/data/network and OCC interface diagram", "gate/TVM plinth, anchor, service-entry and replacement-clearance details"),
        ),
        StationDrawingMetadata(
            "STN-ACC-400", "at-grade pedestrian approach and protected route",
            "deployment civil/accessibility engineer", "deployment-interface-definition",
            ("STN-ACC-P010",),
            (f"{docs}/accessibility.md",),
            ("site approach and boundary plan", "route gradient/crossfall and kerb/ramp profiles", "crossing, surface, drainage, lighting and protection details"),
        ),
        StationDrawingMetadata(
            "STN-ACC-410", "lift, stair and pedestrian overbridge coordination",
            "structural/accessibility engineer + lift supplier", "deployment-led-supplier-interface",
            ("STN-ACC-P020", "STN-ACC-P030"),
            (f"{docs}/accessibility.md", f"{catalogue}/default-product-specifications.md"),
            ("concourse, bridge and vertical-circulation plans", "structure, shaft, stair, enclosure and clearance sections", "accessible route, evacuation, rescue, fire recall and service interfaces"),
        ),
        StationDrawingMetadata(
            "STN-PWR-500", "wayside charger cabinet and vehicle docking interface",
            "traction power + vehicle integration", "supplier-interface-definition",
            ("STN-CHG-P010",),
            ("docs/rolling-stock/light-metro-3car/interfaces.md", f"{catalogue}/default-product-specifications.md"),
            ("cabinet/contact arrangement and service clearances", "DC power, protection, isolation and interlock diagram", "vehicle/contact alignment datum, guarded envelope and abort sequence"),
        ),
        StationDrawingMetadata(
            "STN-PWR-510", "traction substation utility and DC distribution interface",
            "traction power + utility", "deployment-led-supplier-interface",
            ("STN-CHG-P020",),
            (f"{docs}/services.md", f"{catalogue}/default-product-specifications.md"),
            ("substation arrangement, access and fire separation", "MV/DC single-line, protection and metering diagram", "foundation reactions, cable entries, earthing and SCADA interfaces"),
        ),
        StationDrawingMetadata(
            "STN-TRK-600", "1:9 turnout rail, crossing, bearer and track-end definition",
            "permanent-way engineer + turnout supplier", "hybrid-fabrication-definition",
            ("STN-TRK-P010", "STN-TRK-P020", "STN-TRK-P030", "STN-TRK-P070"),
            ("docs/rfcs/0012-switches-and-crossings.md", f"{catalogue}/default-product-specifications.md"),
            ("turnout layout, chainage and rail geometry", "switch, closure, frog, check-rail and bearer details", "track-end, foundation, gauge and inspection schedules"),
        ),
        StationDrawingMetadata(
            "STN-TRK-610", "point operation, lock, detection, heating and harness",
            "signalling/track integration", "supplier-interface-definition",
            ("STN-TRK-P040", "STN-TRK-P050", "STN-TRK-P060"),
            ("docs/rfcs/0012-switches-and-crossings.md", f"{catalogue}/default-product-specifications.md"),
            ("actuator, lock, detection and heater installation plan", "power/safety circuits and W-SBC interface diagram", "hand-wind, cable, drainage, adjustment and bench-test details"),
        ),
        StationDrawingMetadata(
            "STN-DEP-700", "depot site, formation, drainage and service-road layout",
            "deployment civil engineer", "deployment-definition",
            ("STN-DEP-P010", "STN-DEP-P020"),
            ("docs/rfcs/0014-depot-design-standard.md", f"{catalogue}/default-product-specifications.md"),
            ("surveyed general arrangement and phasing", "earthworks, pavement and drainage plans/profiles", "boundary, access, swept path, track and utility coordination"),
        ),
        StationDrawingMetadata(
            "STN-DEP-710", "depot throat turnout, routes and track geometry",
            "permanent-way + signalling integration", "deployment-interface-definition",
            ("STN-DEP-P030",),
            ("docs/rfcs/0014-depot-design-standard.md", "docs/rfcs/0012-switches-and-crossings.md"),
            ("depot throat and route layout", "turnout assembly, detection and cable interfaces", "clearance, stop, hand-wind and degraded-operation details"),
        ),
        StationDrawingMetadata(
            "STN-DEP-720", "depot charging, PV, stationary storage and isolation",
            "depot energy integrator + fire engineer", "deployment-led-supplier-interface",
            ("STN-DEP-P040", "STN-DEP-P050"),
            ("docs/rfcs/0014-depot-design-standard.md", f"{catalogue}/default-product-specifications.md"),
            ("energy compound and stall-equipment layout", "PV/storage/PCS/charger single-line and protection diagram", "separation, containment, cooling, detection, remote isolation and replacement paths"),
        ),
        StationDrawingMetadata(
            "STN-DEP-730", "depot workshop, vehicle lift and building-services integration",
            "depot equipment + building services integration", "deployment-led-supplier-interface",
            ("STN-DEP-P060", "STN-DEP-P070"),
            ("docs/rfcs/0014-depot-design-standard.md", "docs/rolling-stock/light-metro-3car/field-rerailing-concept.md", f"{catalogue}/default-product-specifications.md"),
            ("workshop equipment, bays and service-clearance plan", "lift/crane/lathe/wash foundations and structural reactions", "cooling, LV, air, fire, data, emergency isolation and bogie-extraction sequence"),
        ),
    )


REUSABLE_DEFINITION_IDS = frozenset(
    {
        "STN-CIV-P010", "STN-CIV-P020", "STN-CIV-P030", "STN-CIV-P040",
        "STN-PLT-P010", "STN-CNP-P010", "STN-CNP-P020", "STN-MEP-P010",
        "STN-MEP-P030", "STN-MEP-P040", "STN-PAX-P010", "STN-PAX-P020",
        "STN-PAX-P060", "STN-PAX-P070", "STN-PAX-P080", "STN-ACC-P010",
        "STN-CNP-P060", "STN-TRK-P010",
    }
)

SUPPLIER_CONFIGURATION_IDS = frozenset(
    {
        "STN-CNP-P030", "STN-CNP-P040", "STN-CNP-P050", "STN-CNP-P080",
        "STN-MEP-P020", "STN-PAX-P030", "STN-PAX-P040", "STN-PAX-P050",
        "STN-CHG-P010", "STN-TRK-P020", "STN-TRK-P030", "STN-TRK-P040",
        "STN-TRK-P050", "STN-TRK-P060",
    }
)

DEPLOYMENT_SPECIFIC_IDS = frozenset(
    {
        "STN-CNP-P070", "STN-CNP-P090", "STN-CHG-P020", "STN-ACC-P020",
        "STN-ACC-P030", "STN-TRK-P070", "STN-DEP-P010", "STN-DEP-P020",
        "STN-DEP-P030", "STN-DEP-P040", "STN-DEP-P050", "STN-DEP-P060",
        "STN-DEP-P070",
    }
)


def station_product_release_path(product_id: str) -> str:
    """Return the authority boundary for one stable station product ID."""

    matches = [
        name
        for name, identifiers in (
            ("reusable-definition", REUSABLE_DEFINITION_IDS),
            ("supplier-configuration", SUPPLIER_CONFIGURATION_IDS),
            ("deployment-specific", DEPLOYMENT_SPECIFIC_IDS),
        )
        if product_id in identifiers
    ]
    if len(matches) != 1:
        raise ValueError(f"station release path is not unique for {product_id}: {matches}")
    return matches[0]


def station_release_packages() -> tuple[StationReleasePackage, ...]:
    """Return the ordered station/civil drawing and interface work packages."""

    return (
        StationReleasePackage(
            "STN-FRP-010",
            "precast platform, guideway edge, drainage and closure pack",
            "hybrid-prefabrication-and-site",
            ("STN-CIV-100", "STN-CIV-110"),
            ("STN-CIV-P010", "STN-CIV-P020", "STN-CIV-P030", "STN-CIV-P040", "STN-PLT-P010"),
            ("STN-TOOL-PRECAST-MOULD", "STN-TOOL-EDGE-GAUGE", "STN-TOOL-LIFTING-GAUGE"),
            (
                "accepted survey control, track alignment and platform stepping/gap envelope",
                "site geotechnical, drainage/outfall and foundation design",
                "released concrete, reinforcement, tactile and joint/seal systems",
            ),
            (
                "repeatable precast mould, reinforcement, insert and lifting drawings",
                "site set-out, levelling, drainage and closure-pour schedule",
                "platform-edge datum, tolerance and interface-control plan",
            ),
            (
                "mould and first-article dimensional survey",
                "concrete, reinforcement and lifting-insert records",
                "installed track/platform gap-step and drainage survey",
            ),
            "The reusable mould and panel definition does not release site excavation, foundations, drainage falls or track/platform geometry.",
        ),
        StationReleasePackage(
            "STN-FRP-020",
            "platform canopy steel, footing and solar-roof pack",
            "hybrid-prefabrication-and-supplier",
            ("STN-CNP-200", "STN-CNP-210"),
            ("STN-CNP-P010", "STN-CNP-P020", "STN-CNP-P030", "STN-CNP-P040"),
            ("STN-TOOL-PORTAL-FIXTURE", "STN-TOOL-ANCHOR-TEMPLATE", "STN-TOOL-ROOF-WATER-TEST"),
            (
                "site wind, snow, seismic, thermal and maintenance load cases",
                "accepted steel, coating, roof-panel, PV and connector systems",
                "surveyed foundation, platform, electrical and drainage interfaces",
            ),
            (
                "portal cut/weld, baseplate, anchor-template and erection drawings",
                "roof-panel layout, joints, gutters, penetrations and edge details",
                "PV string, isolation, bonding and cable-route schedule",
            ),
            (
                "steel certificates, weld/NDT and frame survey",
                "anchor-template and erected-frame survey",
                "roof watertightness, PV insulation/polarity and bond-continuity tests",
            ),
            "Catalogue bay geometry is not a structural release; foundations and every site load case require the deployment design authority.",
        ),
        StationReleasePackage(
            "STN-FRP-030",
            "auxiliary solar-canopy module, truss and site-interface pack",
            "deployment-led-hybrid",
            ("STN-CNP-220", "STN-CNP-230"),
            ("STN-CNP-P050", "STN-CNP-P060", "STN-CNP-P070", "STN-CNP-P080", "STN-CNP-P090"),
            ("STN-TOOL-TRUSS-FIXTURE", "STN-TOOL-AUX-ANCHOR-TEMPLATE", "STN-TOOL-AUX-ROOF-GAUGE"),
            (
                "released site layout, egress, fire, drainage and maintenance-access plan",
                "site-specific structural calculation and foundation reactions",
                "selected roof/PV/lightning/edge-protection supplier configurations",
            ),
            (
                "repeatable truss fabrication and roof-bay module drawings",
                "site footing, anchor, erection, gutter/downpipe and access drawings",
                "PV string, protection, bonding and commissioning schedule",
            ),
            (
                "truss weld/NDT and dimensional survey",
                "foundation pre-pour, anchor and erected-geometry surveys",
                "water, electrical, lightning and edge-protection acceptance tests",
            ),
            "The 8.5 m by 22 m catalogue module is an area-planning unit only until site structure, foundations, egress and electrical integration are signed.",
        ),
        StationReleasePackage(
            "STN-FRP-040",
            "station services, passenger equipment and plinth integration pack",
            "supplier-interface",
            ("STN-SYS-300", "STN-SYS-310"),
            (
                "STN-MEP-P010", "STN-MEP-P020", "STN-MEP-P030", "STN-MEP-P040",
                "STN-PAX-P010", "STN-PAX-P020", "STN-PAX-P030", "STN-PAX-P040",
                "STN-PAX-P050", "STN-PAX-P060", "STN-PAX-P070", "STN-PAX-P080",
            ),
            ("STN-TOOL-CABINET-PLINTH-GAUGE", "STN-TOOL-FARE-PLINTH-GAUGE", "STN-TOOL-ACCESSIBILITY-GAUGE"),
            (
                "frozen operator equipment, communications, fare and cyber interfaces",
                "utility, UPS, cooling, earthing, fire and evacuation requirements",
                "released accessibility, sightline, coverage and maintainability zones",
            ),
            (
                "cabinet/plinth fabrication and coordinated equipment-layout drawings",
                "power, data, containment, earth and fire-interface schedules",
                "equipment anchorage, accessible reach and replacement-clearance map",
            ),
            (
                "plinth and anchorage dimensional/proof checks",
                "supplier FAT and station integrated functional tests",
                "accessibility, CCTV/PA coverage and power-loss survey",
            ),
            "Generic plinths may be prepared from controlled envelopes; holes, anchors and services may not be released against assumed supplier equipment.",
        ),
        StationReleasePackage(
            "STN-FRP-050",
            "pedestrian approach, lift/stair core and overbridge interface pack",
            "deployment-led-hybrid",
            ("STN-ACC-400", "STN-ACC-410"),
            ("STN-ACC-P010", "STN-ACC-P020", "STN-ACC-P030"),
            ("STN-TOOL-ACCESSIBILITY-GAUGE", "STN-TOOL-STAIR-RISER-GAUGE"),
            (
                "topographical survey, land boundary, pedestrian demand and road interfaces",
                "site structural, geotechnical, fire/egress and accessibility approvals",
                "selected lift, enclosure and emergency-power configuration",
            ),
            (
                "approach, ramp, kerb, boundary and accessible-route drawings",
                "lift/stair/overbridge structure, enclosure and service-interface drawings",
                "evacuation, rescue, drainage and inspection-access plan",
            ),
            (
                "route gradient, crossfall, width, surface and obstacle survey",
                "structural, clearance and weatherproofing acceptance",
                "lift certification, fire recall, backup power and egress test",
            ),
            "No catalogue access arrangement substitutes for a site accessibility, egress, highway or structural approval.",
        ),
        StationReleasePackage(
            "STN-FRP-060",
            "wayside charging and traction substation interface pack",
            "supplier-and-utility-interface",
            ("STN-PWR-500", "STN-PWR-510"),
            ("STN-CHG-P010", "STN-CHG-P020"),
            ("STN-TOOL-CHARGER-ALIGNMENT", "STN-TOOL-EARTH-BOND-TEST"),
            (
                "utility fault level, capacity, metering and protection requirements",
                "selected charger and transformer/rectifier supplier data",
                "released vehicle docking envelope and operational charging duty",
            ),
            (
                "equipment arrangement, foundation reaction and maintainability drawings",
                "single-line, protection, earthing, isolation and cable schedules",
                "vehicle/wayside datum, alignment, interlock and abort interface control",
            ),
            (
                "supplier FAT and protection-coordination review",
                "earthing, insulation, isolation and utility witness tests",
                "vehicle alignment, charge, abort and emergency-isolation SAT",
            ),
            "Rated catalogue power is a requirement, not authority to connect; the utility and electrical design authority retain release.",
        ),
        StationReleasePackage(
            "STN-FRP-070",
            "1:9 turnout, actuation, detection, heating and track-end pack",
            "hybrid-fabrication-and-supplier",
            ("STN-TRK-600", "STN-TRK-610"),
            tuple(f"STN-TRK-P0{index}0" for index in range(1, 8)),
            ("STN-TOOL-TURNOUT-BENCH", "STN-TOOL-BLADE-PROFILE-GAUGE", "STN-TOOL-TRACK-GEOMETRY"),
            (
                "released wheel/rail interface, axle loads, route speed and climate envelope",
                "selected rail, frog, sleeper, actuator, detector and heater configurations",
                "site track alignment, signalling, drainage and track-end geometry",
            ),
            (
                "rail machining, switch/closure, gauge and weld drawings",
                "complete turnout assembly, harness, detection, heating and bench-test schedule",
                "site set-out, installation, stop-block and commissioning drawings",
            ),
            (
                "material, machining, weld/NDT and dimensional records",
                "bench throw, lock, detection, hand-wind and heating proof",
                "installed geometry, route/detection and stop-block acceptance",
            ),
            "The catalogue tangent and geometry do not release rail machining or site installation without controlled drawings and supplier qualifications.",
        ),
        StationReleasePackage(
            "STN-FRP-080",
            "depot site, drainage, track and throat-turnout pack",
            "deployment-specific",
            ("STN-DEP-700", "STN-DEP-710"),
            ("STN-DEP-P010", "STN-DEP-P020", "STN-DEP-P030"),
            ("STN-TOOL-DEPOT-SET-OUT", "STN-TOOL-TRACK-GEOMETRY", "STN-TOOL-DRAINAGE-TEST"),
            (
                "boundary/topographical/utility/geotechnical surveys and environmental approvals",
                "released fleet plan, movements, swept paths and maintenance concept",
                "controlled depot layout, gradients, drainage/outfall and track standards",
            ),
            (
                "earthworks, pavement, drainage, boundary and service-road drawings",
                "stabling, inspection, wash and workshop track-layout drawings",
                "turnout, stop-block, walkways, crossings and clearance-control schedule",
            ),
            (
                "formation, compaction, drainage and pavement records",
                "track geometry, clearance and stop-block proof",
                "route, detection and vehicle swept-path demonstration",
            ),
            "These are deployment drawings: the reference depot quantities do not authorize site works or fix a universal depot layout.",
        ),
        StationReleasePackage(
            "STN-FRP-090",
            "depot charging, energy, workshop and services integration pack",
            "deployment-and-supplier",
            ("STN-DEP-720", "STN-DEP-730"),
            ("STN-DEP-P040", "STN-DEP-P050", "STN-DEP-P060", "STN-DEP-P070"),
            ("STN-TOOL-VEHICLE-LIFT-GAUGE", "STN-TOOL-CHARGER-ALIGNMENT", "STN-TOOL-ENERGY-ISOLATION-TEST"),
            (
                "selected equipment loads, heat rejection, utilities and maintenance envelopes",
                "site building, fire, structural, energy and environmental approvals",
                "released LM3 lift points, bogie extraction path and service requirements",
            ),
            (
                "equipment layouts, foundations, clearances and replacement paths",
                "power/microgrid/battery isolation, fire, cooling and controls drawings",
                "workshop lift, crane, pit, wash, stores and maintenance-data schedules",
            ),
            (
                "supplier FAT, certification and equipment foundation survey",
                "charging, energy, fire, cooling and emergency-isolation SAT",
                "synchronised lift, mechanical lock, bogie extraction and crane proof",
            ),
            "Reference duties and envelopes do not select suppliers or release a depot building, stationary battery compound, crane or lifting system.",
        ),
    )


def base_release_payload() -> dict[str, object]:
    """Serialize package definitions before live product rows are attached."""

    packages = station_release_packages()
    return {
        "schema": "org.opensourcerail.station-factory-release-work-packages.v1",
        "design_id": "STN-FAMILY-FACTORY-RELEASE",
        "status": "controlled-work-package-definitions; release evidence open",
        "package_count": len(packages),
        "packages": [
            {key: list(value) if isinstance(value, tuple) else value for key, value in asdict(package).items()}
            for package in packages
        ],
        "global_release_boundary": (
            "These packages define reusable drafting and deployment handoff scope. "
            "They are not approved fabrication/construction drawings, supplier selections, "
            "signed calculations, permits, surveys or performed acceptance records."
        ),
    }


def station_release_record_template(payload: dict[str, object]) -> dict[str, object]:
    """Build an intentionally unfilled release-evidence record."""

    packages: list[dict[str, object]] = []
    for raw in payload["packages"]:  # type: ignore[union-attr]
        package = dict(raw)
        packages.append(
            {
                "package_id": package["id"],
                "title": package["title"],
                "delivery_lane": package["delivery_lane"],
                "release_status": "open-unissued",
                "release_boundary": package["release_boundary"],
                "prerequisite_records": [
                    {"requirement": value, "status": "open", "evidence_ref": "", "evidence_sha256": "", "reviewed_by": ""}
                    for value in package["frozen_inputs"]
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
                        "catalogue_maturity": product["maturity"],
                        "release_path": product["release_path"],
                        "reference_default": product["reference_default"],
                        "applicable_variants": product["applicable_variants"],
                        "controlled_revision_or_supplier_configuration": "",
                        "deployment_drawing_ref": "",
                        "coverage_status": "unverified",
                    }
                    for product in package["product_rows"]
                ],
                "tooling_release_records": [
                    {"tooling_id": value, "revision": "", "survey_or_calibration_ref": "", "evidence_sha256": "", "accepted_by": "", "status": "unreleased"}
                    for value in package["tooling_ids"]
                ],
                "controlled_output_records": [
                    {"deliverable": value, "status": "open", "artifact_ref": "", "artifact_sha256": "", "checked_by": ""}
                    for value in package["controlled_outputs"]
                ],
                "verification_records": [
                    {"verification": value, "status": "not-performed", "procedure_revision": "", "result_artifact_ref": "", "result_artifact_sha256": "", "performed_by": "", "reviewed_by": ""}
                    for value in package["verification"]
                ],
                "approvals": {"design_authority": "", "site_design_authority": "", "quality": "", "operator": "", "release_date": ""},
            }
        )
    return {
        "schema": "org.opensourcerail.station-factory-release-record.v1",
        "template_status": "unfilled-not-release-evidence",
        "design_id": payload["design_id"],
        "source_work_packages": "design/component-catalogue/catalog/buildable-stations/factory-release-work-packages.json",
        "coverage": {
            "package_count": len(packages),
            "open_package_count": len(packages),
            "unique_drawing_count": payload["drawing_count"],
            "controlled_product_count": payload["controlled_product_count"],
            "unique_tooling_count": payload["tooling_count"],
        },
        "instructions": [
            "retain every package and product row; supersede records under controlled revision",
            "bind drawings, surveys, calculations, supplier data and test results by repository-relative reference and SHA-256",
            "keep reusable fabrication release separate from each deployment construction release",
            "do not mark template rows complete from catalogue geometry or unperformed analysis",
            "release only after all prerequisites, drawings, configurations, tooling, outputs, verifications and named approvals are accepted",
        ],
        "packages": packages,
        "release_warning": payload["global_release_boundary"],
    }


def render_station_release_readiness(record: dict[str, object]) -> str:
    """Render a concise, explicitly open readiness register."""

    coverage = dict(record["coverage"])  # type: ignore[arg-type]
    lines = [
        "# Station and civil factory/release readiness",
        "",
        "Generated with the station catalogue. Blank evidence fields and",
        "`open-unissued` states are deliberate; this is not construction release.",
        "",
        f"- Template status: `{record['template_status']}`",
        f"- Packages: **{coverage['package_count']}**; open: **{coverage['open_package_count']}**",
        f"- Drawing/interface IDs: **{coverage['unique_drawing_count']}**",
        f"- Controlled unique products: **{coverage['controlled_product_count']}**",
        f"- Tool/gauge families: **{coverage['unique_tooling_count']}**",
        "",
        "| Package | Delivery lane | Status | Drawings | Products | Inputs | Outputs | Tests |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for raw in record["packages"]:  # type: ignore[union-attr]
        package = dict(raw)
        lines.append(
            f"| `{package['package_id']}` — {package['title']} | `{package['delivery_lane']}` | "
            f"`{package['release_status']}` | {len(package['drawing_records'])} | "
            f"{len(package['product_configuration_records'])} | {len(package['prerequisite_records'])} | "
            f"{len(package['controlled_output_records'])} | {len(package['verification_records'])} |"
        )
    lines.extend(
        [
            "",
            "Populate [`factory-release-record-template.json`](evidence/factory-release-record-template.json)",
            "under document control. Reusable factory information may be released independently",
            "only where its package boundary permits; site work still requires the deployment",
            "survey, calculations, supplier configuration, permits and named approvals.",
            "Use the individual [`factory-drawings/`](factory-drawings/index.md) seeds",
            "as drafting/checking briefs, never as issued fabrication or construction drawings.",
            "",
            f"Boundary: {record['release_warning']}",
            "",
        ]
    )
    return "\n".join(lines)


def station_drawing_seed_payloads(payload: dict[str, object]) -> list[dict[str, object]]:
    """Build one non-issued drawing brief per controlled drawing/interface ID."""

    metadata = {row.id: row for row in station_drawing_metadata()}
    packages = [dict(row) for row in payload["packages"]]  # type: ignore[union-attr]
    expected_ids = {
        drawing_id for package in packages for drawing_id in package["drawing_ids"]
    }
    if set(metadata) != expected_ids:
        raise ValueError(
            "station drawing metadata mismatch: "
            f"missing={sorted(expected_ids - set(metadata))}; "
            f"extra={sorted(set(metadata) - expected_ids)}"
        )

    package_products = {
        package["id"]: {product["id"]: dict(product) for product in package["product_rows"]}
        for package in packages
    }
    seeds: list[dict[str, object]] = []
    for drawing_id in sorted(expected_ids):
        meta = metadata[drawing_id]
        drawing_packages = [
            package for package in packages if drawing_id in package["drawing_ids"]
        ]
        available = {
            product_id: product
            for package in drawing_packages
            for product_id, product in package_products[package["id"]].items()
        }
        missing = set(meta.product_ids) - set(available)
        if missing:
            raise ValueError(f"{drawing_id} references products outside its package: {sorted(missing)}")

        def unique(key: str) -> list[str]:
            return list(
                dict.fromkeys(
                    value for package in drawing_packages for value in package[key]
                )
            )

        seeds.append(
            {
                "schema": "org.opensourcerail.station-factory-drawing-seed.v1",
                "drawing_id": drawing_id,
                "title": meta.title,
                "owner": meta.owner,
                "scope_type": meta.scope_type,
                "document_revision": "A-DRAFT",
                "issue_status": "definition-seed-not-issued",
                "package_ids": [package["id"] for package in drawing_packages],
                "source_refs": list(meta.source_refs),
                "units": "millimetres unless explicitly stated",
                "coordinate_basis": (
                    "catalogue station X is along track from platform centre, Y is lateral "
                    "from track/station centreline and Z is vertical in the local station "
                    "frame; deployment drawings must transform this frame to accepted survey "
                    "control while preserving the 350 mm platform-to-top-of-rail interface"
                ),
                "required_views": list(meta.required_views),
                "unresolved_inputs": unique("frozen_inputs"),
                "required_outputs": unique("controlled_outputs"),
                "required_verification": unique("verification"),
                "tooling_ids": unique("tooling_ids"),
                "product_rows": [available[product_id] for product_id in meta.product_ids],
                "mandatory_drawing_controls": [
                    "drawing number, title, sheet, scale, units, projection, revision and issue status",
                    "named catalogue, deployment, supplier, checking, quality and approval responsibilities",
                    "survey coordinate reference system, horizontal/vertical datums and controlled transformation",
                    "material/grade, protection, durability life and applicable process specification",
                    "functional datums, tolerances, fits, clearances and measurable inspection characteristics",
                    "product/assembly IDs, configuration applicability, quantities and revision-compatible BOM",
                    "supplier-controlled dimensions, reactions, access zones and utility interfaces identified rather than assumed",
                    "temporary works, lifting/erection sequence, hold points and safe access where applicable",
                    "tool/gauge references, inspection method, acceptance criteria and evidence route",
                    "reusable definition and deployment-specific construction release shown as separate statuses",
                ],
                "issue_record": {
                    "native_source_ref": "",
                    "published_drawing_ref": "",
                    "published_drawing_sha256": "",
                    "survey_or_supplier_configuration_ref": "",
                    "calculation_ref": "",
                    "sheet_size": "",
                    "scale": "",
                    "drawn_by": "",
                    "checked_by": "",
                    "supplier_reviewed_by": "",
                    "site_design_authority": "",
                    "quality_reviewed_by": "",
                    "approved_by": "",
                    "issue_date": "",
                },
                "release_boundary": (
                    "This is a drafting/checking brief built from catalogue products, reference "
                    "defaults and open inputs. It is not a dimensioned fabrication or construction "
                    "drawing, supplier selection, signed calculation, survey, permit or authority "
                    "to manufacture, build, energise or operate."
                ),
            }
        )

    represented = {
        product["id"] for seed in seeds for product in seed["product_rows"]
    }
    expected_products = set(payload["controlled_product_ids"])  # type: ignore[arg-type]
    if represented != expected_products:
        raise ValueError(
            "station drawing seeds do not cover the product register: "
            f"missing={sorted(expected_products - represented)}; "
            f"extra={sorted(represented - expected_products)}"
        )
    return seeds


def station_drawing_index_payload(seeds: list[dict[str, object]]) -> dict[str, object]:
    """Return deterministic navigation and coverage for drawing seeds."""

    product_ids = {
        product["id"] for seed in seeds for product in seed["product_rows"]
    }
    default_ids = {
        product["id"]
        for seed in seeds
        for product in seed["product_rows"]
        if str(product["reference_default"]).startswith("default-product-specifications.json::")
    }
    return {
        "schema": "org.opensourcerail.station-factory-drawing-seed-index.v1",
        "issue_status": "definition-seeds-not-issued",
        "drawing_count": len(seeds),
        "controlled_product_count": len(product_ids),
        "reference_default_product_count": len(default_ids),
        "drawings": [
            {
                "drawing_id": seed["drawing_id"],
                "title": seed["title"],
                "owner": seed["owner"],
                "scope_type": seed["scope_type"],
                "package_ids": seed["package_ids"],
                "product_ids": [product["id"] for product in seed["product_rows"]],
                "json_file": f"{seed['drawing_id']}.json",
                "markdown_file": f"{seed['drawing_id']}.md",
            }
            for seed in seeds
        ],
    }


def render_station_drawing_seed(seed: dict[str, object]) -> str:
    """Render one seed as a human-readable drafting and checking brief."""

    lines = [
        f"# {seed['drawing_id']} — {seed['title']}",
        "",
        f"- Revision: `{seed['document_revision']}`",
        f"- Issue status: `{seed['issue_status']}`",
        f"- Scope type: `{seed['scope_type']}`",
        f"- Owner: {seed['owner']}",
        "- Release package: " + ", ".join(f"`{value}`" for value in seed["package_ids"]),
        "- Source: " + ", ".join(f"`{value}`" for value in seed["source_refs"]),
        f"- Coordinate basis: {seed['coordinate_basis']}",
        "",
        "## Controlled product scope",
        "",
        "| Product | Route / maturity | Release path | Variants | Reference default |",
        "|---|---|---|---:|---|",
    ]
    for raw in seed["product_rows"]:  # type: ignore[union-attr]
        product = dict(raw)
        default = (
            f"[`specified`](../default-product-specifications.md#{product['id'].lower()})"
            if str(product["reference_default"]).startswith("default-product-specifications.json::")
            else "not required"
        )
        lines.append(
            f"| `{product['id']}` — {product['title']} | `{product['route']}` / "
            f"`{product['maturity']}` | `{product['release_path']}` | "
            f"{len(product['applicable_variants'])} | {default} |"
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
            "Tools/gauges: " + ", ".join(f"`{value}`" for value in seed["tooling_ids"]) + ".",
            "",
            "The JSON beside this page retains deliberately blank native/published file,",
            "checksum, survey/supplier, calculation and named approval fields.",
            "",
            f"Boundary: {seed['release_boundary']}",
            "",
        ]
    )
    return "\n".join(lines)


def render_station_drawing_index(seeds: list[dict[str, object]]) -> str:
    """Render navigation and release status for all drawing seeds."""

    index = station_drawing_index_payload(seeds)
    lines = [
        "# Station and civil drawing-definition seeds",
        "",
        "Generated with the station catalogue. Each seed is a bounded drafting brief",
        "that connects product families, affordable defaults, unresolved site/supplier",
        "inputs, tools, outputs and verification without inventing construction release.",
        "",
        f"- Drawing seeds: **{index['drawing_count']}**",
        f"- Controlled product families represented: **{index['controlled_product_count']}**",
        f"- Open products with reference defaults: **{index['reference_default_product_count']}**",
        "- Issue state: **all definition seeds; none issued for fabrication or construction**",
        "",
        "| Drawing | Scope | Owner | Package | Products | JSON |",
        "|---|---|---|---|---:|---|",
    ]
    for seed in seeds:
        drawing_id = str(seed["drawing_id"])
        packages = "<br>".join(f"`{value}`" for value in seed["package_ids"])
        lines.append(
            f"| [`{drawing_id}`]({drawing_id}.md) — {seed['title']} | "
            f"`{seed['scope_type']}` | {seed['owner']} | {packages} | "
            f"{len(seed['product_rows'])} | [`json`]({drawing_id}.json) |"
        )
    lines.extend(
        [
            "",
            "Package issue and evidence state remains controlled by the",
            "[`factory-release-readiness.md`](../factory-release-readiness.md) register.",
            "",
        ]
    )
    return "\n".join(lines)

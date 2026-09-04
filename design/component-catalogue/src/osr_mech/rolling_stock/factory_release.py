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


__all__ = [
    "FactoryReleasePackage",
    "factory_release_packages",
    "factory_release_payload",
]

"""Buildable trainset product breakdown and current-design review.

The parametric CAD describes shapes. The design iterator chooses a good
candidate architecture. This module starts the manufacturing design
package: a product tree made from real fabricated parts, bought-in
components, subassemblies, car assemblies, and the final trainset.

The output is still a release-candidate manifest, not shop drawings.
It exists so gaps are visible before a fabricator cuts steel.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path

from osr_mech.common import ConsistFamily
from osr_mech.design_definition import CAR_COUNT, DesignCandidate, iterate_design_space
from osr_mech.rolling_stock.baseline import (
    PROMOTED_BATTERY_USABLE_KWH_PER_CAR,
    PROMOTED_BATTERY_GROSS_KWH_PER_CAR,
    PROMOTED_ENGINEERING_MASS_RESERVE_KG,
    PROMOTED_HVAC_THERMAL_KW_PER_CAR,
    PROMOTED_LIGHT_METRO_CAR_LENGTH_M,
    PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG,
    PROMOTED_MOTOR_CONTINUOUS_KW,
    PROMOTED_MOTOR_PEAK_KW,
    PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG,
    PROMOTED_ROOF_SOLAR_MODULES_PER_CAR,
)
from osr_mech.rolling_stock.bom_trace import (
    PROCUREMENT_BOM_ENGINEERING_IDS,
    bom_line_ids_for_engineering_id,
)


class Route(str, Enum):
    MAKE = "MAKE"
    BID = "BID"
    SOURCE = "SOURCE"


class Layer(str, Enum):
    FABRICATED_PART = "fabricated-part"
    EXTERNAL_COMPONENT = "external-component"
    SUBASSEMBLY = "subassembly"
    ASSEMBLY = "assembly"
    TRAINSET = "trainset"


class Maturity(str, Enum):
    CONCEPT = "concept"
    ENVELOPE = "supplier-neutral-envelope"
    RELEASE_CANDIDATE = "release-candidate"
    BUILDABLE_AFTER_SUPPLIER_FREEZE = "buildable-after-supplier-freeze"


@dataclass(frozen=True)
class ProductItem:
    id: str
    title: str
    layer: Layer
    route: Route
    quantity_per_trainset: float
    unit: str
    parent: str
    source_refs: tuple[str, ...]
    make_or_buy_basis: str
    acceptance: tuple[str, ...]
    maturity: Maturity = Maturity.RELEASE_CANDIDATE
    notes: str = ""


@dataclass(frozen=True)
class MaterialSpec:
    material_family: str
    grade_or_part_class: str
    governing_standard: str
    form_factor: str
    nominal_section: str
    finish_or_protection: str
    traceability: str
    evidence_required: tuple[str, ...]


@dataclass(frozen=True)
class ProcessSpec:
    primary_processes: tuple[str, ...]
    joining_methods: tuple[str, ...]
    special_process_controls: tuple[str, ...]
    inspection_methods: tuple[str, ...]
    tooling_basis: str
    release_level: str


@dataclass(frozen=True)
class AssemblyNode:
    id: str
    title: str
    layer: Layer
    quantity_per_trainset: float
    children: tuple[str, ...]
    build_cell: str
    hold_points: tuple[str, ...]
    source_refs: tuple[str, ...]
    maturity: Maturity = Maturity.RELEASE_CANDIDATE


@dataclass(frozen=True)
class ReviewFinding:
    id: str
    status: str
    scope: str
    finding: str
    action: str


@dataclass(frozen=True)
class BuildableTrainsetDesign:
    family: ConsistFamily
    candidate: DesignCandidate
    current_cad_baseline: dict[str, str | float]
    target_candidate: dict[str, str | float]
    product_items: tuple[ProductItem, ...]
    assemblies: tuple[AssemblyNode, ...]
    bom_crosswalk: dict[str, tuple[str, ...]]
    review_findings: tuple[ReviewFinding, ...]


@dataclass(frozen=True)
class DefinitionPackPaths:
    index_json: Path
    index_md: Path
    definition_files: tuple[Path, ...]


@dataclass(frozen=True)
class ShopTravelerPackPaths:
    index_json: Path
    index_md: Path
    traveler_files: tuple[Path, ...]


@dataclass(frozen=True)
class CriticalPathTask:
    id: str
    title: str
    level: str
    duration_days: float
    labor_hours: float
    work_center: str
    space_requirement: str
    predecessors: tuple[str, ...]
    parallelisation_notes: str


CURRENT_CAD_BASELINE: dict[str, str | float] = {
    "family": ConsistFamily.LIGHT_METRO_3CAR.value,
    "car_length_m": PROMOTED_LIGHT_METRO_CAR_LENGTH_M,
    "motor": "motor-350kw-hm47-class",
    "battery": "battery-225kwh-lfp-800v",
    "hvac": "hvac-24kw-direct-hv-dc",
    "pv_modules_per_car": float(PROMOTED_ROOF_SOLAR_MODULES_PER_CAR),
}


def buildable_trainset_design(family: ConsistFamily = ConsistFamily.LIGHT_METRO_3CAR) -> BuildableTrainsetDesign:
    run = iterate_design_space(family)
    candidate = run.optimum
    target = {
        "family": candidate.parameters.family.value,
        "car_length_m": candidate.parameters.car_length_m,
        "motor": candidate.parameters.motor_id,
        "battery": candidate.parameters.battery_id,
        "hvac": candidate.parameters.hvac_id,
        "pv_modules_per_car": float(candidate.parameters.pv_modules_per_car),
    }
    return BuildableTrainsetDesign(
        family=family,
        candidate=candidate,
        current_cad_baseline=CURRENT_CAD_BASELINE,
        target_candidate=target,
        product_items=_product_items(candidate),
        assemblies=_assemblies(family),
        bom_crosswalk=dict(PROCUREMENT_BOM_ENGINEERING_IDS),
        review_findings=_review_findings(candidate, target),
    )


def _product_items(candidate: DesignCandidate) -> tuple[ProductItem, ...]:
    cars = CAR_COUNT[candidate.parameters.family]
    articulations = max(0, cars - 1)
    return (
        # Fabricated carbody datum structure.
        ProductItem(
            "LM3-BDY-P010",
            "laser-cut side sill beam, LH/RH",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars * 2,
            "ea",
            "LM3-BDY-SA110",
            ("car_body.py", "cad_templates/rolling_stock.py", "LM3-BDY-110"),
            "S355 RHS/folded section cut, formed, drilled, and fixture-welded locally.",
            ("heat traceability", "dimensional check", "weld VT/MT where classed"),
        ),
        ProductItem(
            "LM3-BDY-P020",
            "underframe centre spine and cross-bearer kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "kit",
            "LM3-BDY-SA110",
            ("car_body.py", "fabrication-plan.md", "LM3-BDY-110"),
            "Cut plate/RHS kit for one car; QR-marked before welding.",
            ("tube/plate certs", "fixture survey", "bogie-centre datum report"),
        ),
        ProductItem(
            "LM3-BDY-P030",
            "bolster box, air-spring pad, and centre-pivot insert set",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars * 2,
            "set",
            "LM3-BDY-SA110",
            ("cad_templates/rolling_stock.py", "LM3-BDY-120", "LM3-BOG-400"),
            "Folded and welded bolster boxes, machined after weld where required.",
            ("line-bore report", "air-spring datum survey", "NDT report"),
        ),
        ProductItem(
            "LM3-BDY-P040",
            "coupler pocket, shear plate, and crash-can insert kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            2,
            "set",
            "LM3-END-SA700",
            ("systems.py", "interfaces.md", "LM3-BDY-130"),
            "Welded/machined pocket accepting certified coupler and crash absorber.",
            ("coupler face datum", "bolt-hole survey", "crash-load drawing check"),
        ),
        ProductItem(
            "LM3-BDY-P050",
            "battery tray rails, vent plenum, and service-lid gutter kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "kit",
            "LM3-HV-SA510",
            ("car_body.py", "systems.py", "LM3-BDY-140"),
            "Under-seat cassette structure with drainage, fire vent, and service access.",
            ("battery gauge fit", "vent-path inspection", "gasket land check"),
        ),
        ProductItem(
            "LM3-BDY-P060",
            "low-floor centre pan and raised bogie-end deck set",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "set",
            "LM3-BDY-SA120",
            ("car_body.py", "body.md", "LM3-BDY-100"),
            "Stepped floor structure preserving low centre zone and high bogie-end decks.",
            ("PRM floor height", "egress aisle gauge", "deck weld inspection"),
        ),
        ProductItem(
            "LM3-BDY-P070",
            "side-wall post, door portal, waist rail, and cant rail kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars * 2,
            "side",
            "LM3-BDY-SA120",
            ("car_body.py", "fabrication-plan.md", "LM3-BDY-120"),
            "Side frame welded in fixture before body close-up.",
            ("door cassette gauge", "window cassette gauge", "side-frame survey"),
        ),
        ProductItem(
            "LM3-BDY-P080",
            "roof bow, HVAC rail, PV rail, and cable-tray bracket kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "kit",
            "LM3-ROOF-SA410",
            ("car_body.py", "systems.py", "LM3-HV-325"),
            "Roof datum kit for HVAC, PV, antennas, service walkways, and ducts.",
            ("roof rail pitch", "HVAC curb gauge", "PV clamp pull test"),
        ),
        ProductItem(
            "LM3-BDY-P090",
            "end ring frame and anti-climber beam set",
            Layer.FABRICATED_PART,
            Route.MAKE,
            2,
            "set",
            "LM3-END-SA700",
            ("sensor_cowl.py", "end-cowl.md", "LM3-BDY-155"),
            "Steel datum for identical fiberglass end cowl and panoramic glass.",
            ("A/B interchange check", "glass carrier land survey", "anti-climber datum"),
        ),
        ProductItem(
            "LM3-END-P060",
            "common reversible end-interface carrier ring, option bolt grid, and sealing datum kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            2,
            "end position",
            "LM3-EIF-SA650",
            ("articulation.md", "end-cowl.md", "interfaces.md", "LM3-END-650"),
            "Common structural and sealing datum that lets the same train end accept either the panoramic closed nose or the open mid-train connection.",
            ("option bolt-grid survey", "seal datum continuity", "A/B interchange check", "end-option fit gauge"),
        ),
        ProductItem(
            "LM3-END-P061",
            "panoramic-end option shim, cowl/glass carrier, and sensor datum closeout kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            2,
            "option kit",
            "LM3-EIF-SA650",
            ("sensor_cowl.py", "end-cowl.md", "LM3-END-650"),
            "Default end-option kit that closes the common interface with the panoramic glass cowl, T-OBS sensor datum, coupler access, and weather seals.",
            ("panoramic option fit gauge", "glass/cowl datum transfer", "sensor datum check", "water-ingress pre-test"),
        ),
        ProductItem(
            "LM3-END-P062",
            "mid open-connection option portal trim, bellows clamp, threshold bridge, and drain kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            0,
            "option kit",
            "LM3-EIF-SA650",
            ("articulation.md", "assembly-plan.md", "LM3-END-650-MID"),
            "Optional end treatment for marrying two train modules into a walk-through consist; it replaces the panoramic cowl/glass with an open passenger portal and gangway clamp datum.",
            ("open-portal gauge", "bellows clamp fit", "threshold/turntable level check", "drain-path water test"),
            notes="Quantity is zero in the reference three-car trainset. Select two kits for a train module whose ends are configured as mid open connections.",
        ),
        ProductItem(
            "LM3-BDY-P100",
            "door portal reinforcement, threshold beam, and cassette shim kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars * 4,
            "opening kit",
            "LM3-DOOR-SA310",
            ("car_body.py", "systems.py", "LM3-DOOR-200"),
            "Machined/folded datum frame that turns the body aperture into a repeatable COTS door cassette interface.",
            ("door aperture gauge", "threshold height survey", "cassette shim record", "water-drain path check"),
        ),
        ProductItem(
            "LM3-BDY-P110",
            "window carrier ring, bonded-gasket land, and replacement jack-point inserts",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars * 6,
            "opening kit",
            "LM3-WIN-SA320",
            ("car_body.py", "cots_equipment.py", "LM3-WIN-210"),
            "Laser-cut carrier ring and local backing plates for bonded/gasketed glazing replacement.",
            ("aperture gauge", "bond-land surface check", "water-ingress witness", "replacement tool clearance"),
        ),
        ProductItem(
            "LM3-BDY-P120",
            "jacking pad, lifting eye, towing lug, and recovery-label kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "car kit",
            "LM3-BDY-SA110",
            ("bom-skeleton.md B26", "car_body.py", "LM3-BDY-100"),
            "Locally fabricated and proof-marked recovery fittings tied into released underframe load paths.",
            ("material traceability", "weld/NDT record", "proof load", "datum and label inspection"),
        ),
        ProductItem(
            "LM3-BDY-P130",
            "one-metre clip-on fiberglass side and roof body module",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars * 48,
            "module",
            "LM3-SHELL-A200",
            ("modular_fiberglass_body.py", "body.md", "LM3-BDY-160"),
            "One common 1,000 mm longitudinal mould pitch; CNC-trimmed side/window/door and roof variants hang from the same released clip grid.",
            ("material/fire certificate", "trim gauge", "insert pull-out", "master-frame dry fit"),
        ),
        ProductItem(
            "LM3-BDY-P140",
            "keyed clip rail, captive retainer, anti-lift, and dry-seal car kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "car kit",
            "LM3-SHELL-A200",
            ("modular_fiberglass_body.py", "assembly-plan.md", "LM3-BDY-160"),
            "Laser-cut/folded stainless clip hardware and replaceable EPDM seals install without a production adhesive cure cycle.",
            ("clip proof load", "anti-reversal gauge", "retainer witness-mark check", "water ingress test"),
        ),
        ProductItem(
            "LM3-ROOF-P010",
            "HVAC curb, drop-duct collar, condensate tray, and drain fitting kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "kit",
            "LM3-ROOF-SA410",
            ("car_body.py", "mechanical_interfaces.py", "LM3-HVAC-220"),
            "Bolted/gasketed roof opening and drain tray that decouples final HVAC supplier choice from primary roof steel.",
            ("curb flatness", "drop-duct gauge", "condensate drain flow test", "roof leak test"),
        ),
        ProductItem(
            "LM3-ROOF-P020",
            "PV bonded-pad lands, raised rail kit, bonding jumpers, and roof isolation labels",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "car kit",
            "LM3-ROOF-SA410",
            ("car_body.py", "systems.py", "LM3-HV-325"),
            "Mixed flexible/rigid PV mounting datum with accessible clamps and electrical bonding points.",
            ("rail pitch survey", "bond pull coupon", "earth continuity", "module keep-out gauge"),
        ),
        ProductItem(
            "LM3-CWL-P010",
            "end-cowl fiberglass laminate, insert, adhesive, and coupon material kit",
            Layer.FABRICATED_PART,
            Route.SOURCE,
            2,
            "kit",
            "LM3-CWL-SA710",
            ("end-cowl.md", "bom-skeleton.md B8", "LM3-BDY-155"),
            "Fire-retardant E-glass/vinyl-ester or basalt composite consumables, inserts, coupons, and adhesive/sealant for one reversible end cowl kit.",
            ("material batch trace", "fire/smoke certificate", "coupon layup record", "adhesive shelf-life check"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-CWL-P011",
            "CWL-FRP-01 upper brow and roof-cap fiberglass cast",
            Layer.FABRICATED_PART,
            Route.MAKE,
            2,
            "ea",
            "LM3-CWL-SA710",
            ("sensor_cowl.py", "end-cowl.md", "LM3-BDY-155-CWL-FRP-01"),
            "Locally moulded upper brow/roof-cap cast with washer-cover lands and roof transition flange.",
            ("mould release record", "laminate coupon", "trim-line gauge", "roof-flange fit"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-CWL-P012",
            "CWL-FRP-02 left cheek fiberglass cast",
            Layer.FABRICATED_PART,
            Route.MAKE,
            2,
            "ea",
            "LM3-CWL-SA710",
            ("sensor_cowl.py", "end-cowl.md", "LM3-BDY-155-CWL-FRP-02"),
            "Locally moulded left cheek/side-return cast carrying the green livery return and split-line closure.",
            ("mould release record", "laminate coupon", "insert pull-out", "split-gap gauge"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-CWL-P013",
            "CWL-FRP-03 right cheek fiberglass cast",
            Layer.FABRICATED_PART,
            Route.MAKE,
            2,
            "ea",
            "LM3-CWL-SA710",
            ("sensor_cowl.py", "end-cowl.md", "LM3-BDY-155-CWL-FRP-03"),
            "Locally moulded right cheek/side-return cast using the mirrored cheek datum and common hole pattern.",
            ("mould release record", "laminate coupon", "insert pull-out", "split-gap gauge"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-CWL-P014",
            "CWL-FRP-04 lower apron and anti-climber cover fiberglass cast",
            Layer.FABRICATED_PART,
            Route.MAKE,
            2,
            "ea",
            "LM3-CWL-SA710",
            ("sensor_cowl.py", "end-cowl.md", "LM3-BDY-155-CWL-FRP-04"),
            "Locally moulded lower apron cast with lamp recess support and removable coupler/recovery access envelope.",
            ("mould release record", "laminate coupon", "lamp pocket gauge", "drain-path water test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-CWL-P015",
            "CWL-FRP-05 lamp, washer, and service-hatch fiberglass cast set",
            Layer.FABRICATED_PART,
            Route.MAKE,
            4,
            "hatch",
            "LM3-CWL-SA710",
            ("sensor_cowl.py", "end-cowl.md", "LM3-BDY-155-CWL-FRP-05"),
            "Small removable hatch casts with potted inserts, continuous gasket land, and retained-fastener access.",
            ("mould release record", "insert pull-out", "gasket compression check", "hatch removal trial"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-CWL-P016",
            "CWL-FRP-06 backing-ring flange fiberglass cast set",
            Layer.FABRICATED_PART,
            Route.MAKE,
            8,
            "flange section",
            "LM3-CWL-SA710",
            ("sensor_cowl.py", "end-cowl.md", "LM3-BDY-155-CWL-FRP-06"),
            "Solid-laminate backing-ring flange sections that carry seals, glass-carrier lands, and split-line closures without carrying crash loads.",
            ("mould release record", "glass-carrier land survey", "bond-line witness", "A/B interchange check"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-ART-P010",
            "articulation adapter frame, anti-lift keeper, and shim kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            articulations,
            "kit",
            "LM3-ART-SA800",
            ("systems.py", "articulation.md", "LM3-SYS-170"),
            "Machined/welded adapter frames for lower pivot, upper links, bellows, and trainlines.",
            ("motion envelope", "bearing proof", "shim pack record"),
        ),
        # Bogie fabricated structure.
        ProductItem(
            "LM3-BOG-P010",
            "powered bogie welded H-frame and motor-cradle weldment",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "ea",
            "LM3-BOG-SA610",
            ("bogie/frame.py", "bogie/assembly.py", "LM3-BOG-400"),
            "Fresh EN 15085-controlled bogie frame; no recovered freight-frame splice.",
            ("bogie fixture survey", "weld/NDT record", "motor-cradle proof"),
        ),
        ProductItem(
            "LM3-BOG-P020",
            "trailer bogie welded H-frame",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "ea",
            "LM3-BOG-SA620",
            ("bogie/frame.py", "bogie/assembly.py", "LM3-BOG-410"),
            "Common trailer frame without motor cradle and traction gearbox mounts.",
            ("bogie fixture survey", "weld/NDT record", "air-spring datum survey"),
        ),
        ProductItem(
            "LM3-BOG-P030",
            "powered-bogie guards, cable guides, WSP brackets, and inspection covers",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "kit",
            "LM3-BOG-SA610",
            ("bogie/assembly.py", "systems.py", "LM3-BOG-400"),
            "Powered-bogie removable guards and harness brackets installed after wheelset fit.",
            ("service access check", "harness clearance", "fastener torque record"),
        ),
        ProductItem(
            "LM3-BOG-P031",
            "trailer-bogie guards, cable guides, WSP brackets, and inspection covers",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "kit",
            "LM3-BOG-SA620",
            ("bogie/assembly.py", "systems.py", "LM3-BOG-410"),
            "Trailer-bogie removable guards and harness brackets installed after wheelset fit.",
            ("service access check", "harness clearance", "fastener torque record"),
        ),
        ProductItem(
            "LM3-BOG-P050",
            "powered-bogie motor torque link, anti-rotation stop, and safety lanyard bracket kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "bogie kit",
            "LM3-BOG-SA610",
            ("bogie/assembly.py", "bogie/motor.py", "LM3-TRC-500"),
            "Local fabricated brackets close the motor reaction path into the powered bogie frame.",
            ("torque-link gauge", "bracket NDT", "motor removal clearance", "fastener locking record"),
        ),
        ProductItem(
            "LM3-BOG-P060",
            "powered-bogie brake/WSP/speed-sensor harness and junction-bracket kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "bogie kit",
            "LM3-BOG-SA610",
            ("bogie/brake.py", "systems.py", "LM3-ELC-300"),
            "Locally built, continuity-tested rugged harness with fabricated sensor brackets and junctions for powered-bogie brake and wheel-slide protection.",
            ("continuity test", "connector IP rating", "wheelset clearance", "dynamic cable sweep"),
        ),
        ProductItem(
            "LM3-BOG-P061",
            "trailer-bogie brake/WSP/speed-sensor harness and junction-bracket kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "bogie kit",
            "LM3-BOG-SA620",
            ("bogie/brake.py", "systems.py", "LM3-ELC-300"),
            "Locally built, continuity-tested rugged harness with fabricated sensor brackets and junctions for trailer-bogie brake and wheel-slide protection.",
            ("continuity test", "connector IP rating", "wheelset clearance", "dynamic cable sweep"),
        ),
        # External carbody and passenger modules.
        ProductItem(
            "LM3-EXT-P010",
            "electric plug/sliding door cassette",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars * 4,
            "ea",
            "LM3-DOOR-SA310",
            ("bom-skeleton.md B11/B25", "systems.py", "LM3-DOOR-200"),
            "Certified rail door supplier owns mechanics, seals, controller, and lifecycle evidence.",
            ("EN 14752 evidence", "obstruction test", "closed-and-locked loop test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P020",
            "side laminated glazing cassette",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars * 6,
            "ea",
            "LM3-WIN-SA320",
            ("cots_equipment.py", "bom-skeleton.md B10", "LM3-WIN-210"),
            "Supplier-neutral bonded/gasketed cassette sized by OSR aperture.",
            ("glazing certificate", "water ingress test", "replacement method"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P030",
            "single panoramic heated end-glass assembly",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            2,
            "ea",
            "LM3-END-SA700",
            ("sensor_cowl.py", "bom-skeleton.md B27", "LM3-BDY-155"),
            "RF-transparent heated/de-iced panoramic glass for cabless end.",
            ("glass certificate", "heater test", "bond/gasket procedure"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P040",
            f"{candidate.parameters.hvac_id} roof HVAC",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "ea",
            "LM3-ROOF-SA410",
            ("design-iteration-summary.md", "cots_equipment.py", "LM3-HVAC-220"),
            "Optimizer-selected hot-climate HVAC must fit the roof curb and aux-power budget.",
            ("+50 C capacity evidence", "condensate drain test", "EMC/vibration evidence"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P050",
            "roof PV module and edge-clamp kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars * candidate.parameters.pv_modules_per_car,
            "module",
            "LM3-ROOF-SA410",
            ("systems.py", "car_body.py", "LM3-HV-325"),
            "Flexible/rigid PV modules plus isolators and roof harness.",
            ("module datasheet", "clamp pull test", "isolation/bonding check"),
        ),
        ProductItem(
            "LM3-EXT-P060",
            "seats, grab rails, flooring, lighting, PIS, CCTV, intercom, signage kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "car kit",
            "LM3-INT-SA330",
            ("cots_equipment.py", "bom-skeleton.md B12-B19/A1-A4", "LM3-INT-230"),
            "Late-installed passenger fit-out kit after shell paint and leak checks.",
            ("fire certificates", "egress gauge", "lighting lux test", "network enumeration"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P070",
            "roof antennas, service walkway pads, lifting covers, and maintenance labels",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "car kit",
            "LM3-ROOF-SA410",
            ("systems.py", "interfaces.md", "LM3-ELC-300"),
            "Service and radio-accessory roof package integrated around HVAC and PV keep-outs.",
            ("antenna VSWR test", "walkway slip certificate", "lifting-cover fit", "roof bonding check"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P080",
            "fire-rated GFRP side-module laminate, core, gelcoat, and consumable kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars * 2,
            "side kit",
            "LM3-SHELL-A200",
            ("bom-skeleton.md B6", "modular_fiberglass_body.py", "LM3-BDY-160"),
            "Supplier-qualified glass-fibre, resin, core, gelcoat/paint, release film, and coupons feed local 1 m side-module moulding; no full-side bonded panel is used.",
            ("EN 45545 evidence", "laminate coupon", "resin/fibre batch trace", "mould release record"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P090",
            "fire-rated GFRP roof-module, dry-seal, and removable skirt material kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "car kit",
            "LM3-SHELL-A200",
            ("bom-skeleton.md B7", "modular_fiberglass_body.py", "LM3-BDY-160"),
            "Supplier-qualified roof-module laminate consumables, EPDM seal stock, trim materials, and removable skirt blanks feed the local mould/trim/clip process.",
            ("EN 45545 evidence", "roof laminate coupon", "seal certificate", "service-removal trial", "water and debris-ingress check"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-INT-P010",
            "HVAC diffusers, side return ducts, saloon grilles, and access panels",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "car kit",
            "LM3-INT-SA330",
            ("car_body.py", "cots_equipment.py", "LM3-HVAC-220"),
            "Interior air distribution kit between roof HVAC drops and the passenger saloon.",
            ("airflow balance", "rattle check", "access-panel removal", "fire-material certificate"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-INT-P020",
            "FRP/phenolic ceiling liner, light trough, and HVAC plenum cover set",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "car kit",
            "LM3-INT-SA330",
            ("cabin-fiberglass.md", "body.md", "LM3-INT-240"),
            "Locally moulded or CNC-trimmed fire-rated cabin ceiling panels with light troughs, diffuser openings, and removable service covers.",
            ("fire-material certificate", "trim-line gauge", "fastener insert pull-out", "rattle check"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-INT-P030",
            "FRP/phenolic sidewall liner, window reveal, and cable-cover panel set",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars * 2,
            "side kit",
            "LM3-INT-SA330",
            ("cabin-fiberglass.md", "body.md", "LM3-INT-245"),
            "Fire-rated cabin sidewall panels and window reveals that hide secondary structure while preserving window replacement and cable-tray access.",
            ("fire-material certificate", "window-reveal gauge", "access-panel removal", "edge-radius inspection"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-INT-P040",
            "FRP battery strake covers, seat-base fairings, and service-hatch shells",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "car kit",
            "LM3-INT-SA330",
            ("cabin-fiberglass.md", "traction.md", "LM3-INT-250"),
            "Sacrificial fire-rated fiberglass covers over under-seat battery strakes, with removable hatches and seat-base fairing returns.",
            ("fire-material certificate", "service-hatch removal", "HV warning label check", "sharp-edge inspection"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-INT-P050",
            "FRP vestibule kick panels, PRM ramp/step covers, and door-pocket trims",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars * 4,
            "door-zone kit",
            "LM3-INT-SA330",
            ("cabin-fiberglass.md", "body.md", "LM3-INT-255"),
            "Durable molded fiberglass/phenolic trim around door thresholds, PRM transitions, and high-floor step faces.",
            ("fire-material certificate", "PRM transition gauge", "anti-slip witness", "kick-panel retention test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        # External running gear and traction modules.
        ProductItem(
            "LM3-TRC-P010",
            f"{candidate.parameters.motor_id} axle traction motor",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars * 2,
            "ea",
            "LM3-BOG-SA610",
            ("design-iteration-summary.md", "bogie/motor.py", "LM3-TRC-500"),
            f"Optimizer-selected {PROMOTED_MOTOR_CONTINUOUS_KW:.0f} kW motor class; CAD baseline carries the promoted envelope.",
            ("motor datasheet", "thermal curve", "mounting-foot load proof", "EMC evidence"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-TRC-P020",
            "single-stage reduction gearbox and flexible coupling",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars * 2,
            "ea",
            "LM3-BOG-SA610",
            ("bogie/gearbox.py", "bom-skeleton.md T2/G19", "LM3-TRC-500"),
            "Gearbox mounted on powered bogie axle with supplier coupling.",
            ("gear ratio certificate", "oil access check", "coupling alignment"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-TRC-P030",
            "two independent motor controllers, isolated LV DC/DC, MPPT, station protection, and cooling-loop kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "car kit",
            "LM3-HV-SA510",
            ("systems.py", "bom-skeleton.md T3/T12/T13/T20/T23", "LM3-HV-320"),
            "Per-car 800 V-class traction, auxiliary, PV, and station-interface electronics; no central AC bus.",
            ("HVIL test", "coolant pressure test", "EMC/bonding check"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-TRC-P040",
            f"{candidate.parameters.battery_id} under-seat traction battery pack",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "ea",
            "LM3-HV-SA510",
            ("design-iteration-summary.md", "systems.py", "LM3-BDY-140"),
            "Optimizer-selected per-car pack; final supplier must fit tray, cooling, BMS, and vent path.",
            ("cell/module certificate", "isolation test", "vent/fire containment data"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-HV-P010",
            "battery sliding trays, retention straps, service interlocks, and drain pans",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "car kit",
            "LM3-HV-SA510",
            ("car_body.py", "systems.py", "LM3-BDY-140"),
            "Local mechanical retention and service hardware for the supplier battery modules.",
            ("battery module gauge", "retention pull test", "tray slide/removal test", "drain-path inspection"),
        ),
        ProductItem(
            "LM3-HV-P020",
            "segregated HV cable tray, bonding studs, grommets, and orange cover set",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "car kit",
            "LM3-HV-SA510",
            ("systems.py", "mechanical_interfaces.py", "LM3-HV-310"),
            "Maintains HV/LV segregation from battery, inverter, roof PV, and side-pin charger interfaces.",
            ("bend-radius gauge", "bond continuity", "cover fastener torque", "orange-label inspection"),
        ),
        ProductItem(
            "LM3-HV-P030",
            "coolant manifold brackets, bleed/drain points, and insulated pipe clamp kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "car kit",
            "LM3-HV-SA510",
            ("systems.py", "car_body.py", "LM3-HV-320"),
            "Fabricated support and maintainability kit for HVAC/battery/inverter thermal loops.",
            ("pressure-test access", "bleed point height check", "pipe clamp pitch", "thermal isolation inspection"),
        ),
        ProductItem(
            "LM3-TRC-P050",
            "roof-mounted regen dump resistor and thermal shield kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "ea",
            "LM3-ROOF-SA410",
            ("bom-skeleton.md T15", "systems.py", "LM3-HV-325"),
            "Per-car roof resistor path for regen overvoltage and commissioning load tests.",
            ("resistance certificate", "thermal clearance", "roof bonding", "hot-surface label"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-TRC-P060",
            "station side-pin charging connector, actuator, shutter, and alignment target",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "car kit",
            "LM3-HV-SA510",
            ("bom-skeleton.md T12/T19", "systems.py", "LM3-HV-310"),
            "Conductive station charging interface with mechanical guide datum and safety interlocks.",
            ("dock alignment test", "HVIL test", "shutter cycle test", "emergency release"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-TRC-P070",
            "HV contactor, fuse, pre-charge, service-disconnect, and current-sensor panel",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "car kit",
            "LM3-HV-SA510",
            ("bom-skeleton.md T11/T16", "systems.py", "LM3-HV-310"),
            "Supplier-certified high-voltage protection panel between battery, charger, PV, and inverter.",
            ("isolation test", "pre-charge timing", "fuse rating evidence", "service-disconnect lockout"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-SAF-P010",
            "battery temperature/off-gas detection, electrical-enclosure smoke detection, and localized mist kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "car kit",
            "LM3-HV-SA510",
            ("bom-skeleton.md T9/T10", "systems.py", "LM3-SAF-340"),
            "Per-car battery reservoir, DC pump, stainless pipe, nozzles, outward vents, and diagnostic sensors; no saloon or electrical-bay suppression.",
            ("detector certificate", "loop continuity", "mist proof-flow", "reservoir/pump/pressure diagnostic", "event-recorder input"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-BOG-P040",
            "powered-bogie certified wheelset, axlebox, suspension, brake, centre-pivot, yaw-link, and sensor kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "bogie kit",
            "LM3-BOG-SA610",
            ("bogie/wheelset.py", "bogie/brake.py", "bogie/suspension.py", "LM3-BOG-400"),
            "The powered-bogie G3-G16 safety-critical rotating, suspension, braking, pivot, restraint, and sensing package stays supplier-certified.",
            ("wheelset certificates", "bearing records", "spring/damper certificates", "brake test", "sensor test", "ride-height report"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-BOG-P041",
            "trailer-bogie certified wheelset, axlebox, suspension, brake, centre-pivot, yaw-link, and sensor kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "bogie kit",
            "LM3-BOG-SA620",
            ("bogie/wheelset.py", "bogie/brake.py", "bogie/suspension.py", "LM3-BOG-410"),
            "The trailer-bogie G3-G16 safety-critical rotating, suspension, braking, pivot, restraint, and sensing package stays supplier-certified.",
            ("wheelset certificates", "bearing records", "spring/damper certificates", "brake test", "sensor test", "ride-height report"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-AUX-P010",
            "secondary-suspension compressor, dryer, reservoir, and isolation-manifold kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "car kit",
            "LM3-CAR-A900",
            ("bom-skeleton.md G21", "bogie/suspension.py", "systems.py"),
            "One local air-supply package per car serves its two secondary-suspension bogies without creating a trainwide pneumatic brake line.",
            ("pressure certificate", "leak test", "dryer function", "relief-valve test", "service-access check"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        # Train-end and control modules.
        ProductItem(
            "LM3-END-P010",
            "automatic end coupler and crash-energy absorber",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            2,
            "ea",
            "LM3-END-SA700",
            ("systems.py", "bom-skeleton.md B22/B23", "LM3-SYS-160"),
            "Certified coupler/crash absorber bolted into OSR pocket.",
            ("EN 15227 absorber evidence", "recovery procedure", "bolt torque record"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-ART-P020",
            "gangway, lower spherical pivot, upper links, bellows, turntable, and trainline kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            articulations,
            "kit",
            "LM3-ART-SA800",
            ("systems.py", "articulation.md", "LM3-SYS-170"),
            "Supplier gangway/articulation kit integrated through OSR adapter frame.",
            ("motion-envelope proof", "fire evidence", "water ingress/drain test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-CTRL-P010",
            "T-ECU/S and T-ECU/A compute and safety-control cabinet kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            1,
            "trainset kit",
            "LM3-SYS-SA900",
            ("systems.py", "hardware/rolling-stock-integration.md", "LM3-ELC-300"),
            "The controlled train-compute and safety-output cabinets are integrated after power, cooling, and network interfaces are frozen.",
            ("hardware BOM check", "self-test", "network enumeration", "firmware record", "safety-output test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-CTRL-P020",
            "navigation, balise, 5G, LoRa, GNSS, IMU, and roof-antenna kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            1,
            "trainset kit",
            "LM3-SYS-SA900",
            ("bom-skeleton.md E3-E8/E21", "systems.py", "LM3-COM-600"),
            "Commodity navigation and communications devices are installed as individually traceable modules on the train network.",
            ("SKU/firmware record", "antenna VSWR", "GNSS/IMU test", "balise read", "radio link test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-CTRL-P030",
            "maintenance HMI, depot pendant, emergency controls, and safety-relay kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            1,
            "trainset kit",
            "LM3-SYS-SA900",
            ("bom-skeleton.md E10-E13/E16", "systems.py", "LM3-ELC-300"),
            "Human-service and hardwired emergency interfaces remain segregated from normal unattended operation.",
            ("key/guarded-control test", "emergency input test", "2oo2 relay test", "stowage and access check"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-CTRL-P040",
            "pre-terminated LV trainline harness, DIN cabinet, and terminal-distribution kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "car kit",
            "LM3-SYS-SA900",
            ("bom-skeleton.md E17/E20/E22", "systems.py", "LM3-ELC-300"),
            "Locally built harness/cabinet kits implement the released connector, segregation, label, and clamp schedules.",
            ("continuity/hipot", "pinout check", "label inspection", "segregation survey", "configuration record"),
        ),
        ProductItem(
            "LM3-CTRL-P050",
            "operational and crashworthy event-recorder storage kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            1,
            "trainset kit",
            "LM3-SYS-SA900",
            ("bom-skeleton.md E9/E23", "systems.py", "LM3-ELC-300"),
            "Operational NVMe storage and the crashworthy memory module are separately serialized but released as one recorder kit.",
            ("write/read test", "retention configuration", "crashworthy certificate", "download/recovery test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-END-P020",
            "T-OBS nose sensor pack, heated window services, and washer kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            2,
            "ea",
            "LM3-END-SA700",
            ("systems.py", "sensor_cowl.py", "LM3-OBS-330"),
            "Per-end obstacle-detection module aligned to the cowl optical/radar datum.",
            ("sensor calibration", "washer/heater test", "2oo2 verdict interface test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-END-P030",
            "cowl service hatch, sensor backing bracket, washer-tube, and heater-cable clip kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            2,
            "end kit",
            "LM3-END-SA700",
            ("sensor_cowl.py", "mechanical_interfaces.py", "LM3-OBS-330"),
            "Local brackets and service access hardware for the nose sensor and heated glass services.",
            ("hatch water test", "sensor datum check", "heater-cable separation", "washer tube leak test"),
        ),
        ProductItem(
            "LM3-END-P040",
            "e-coupler LV jumper, recovery trainline, and end harness breakaway kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            2,
            "end kit",
            "LM3-END-SA700",
            ("systems.py", "interfaces.md", "LM3-SYS-160"),
            "Electrical trainline and rescue interface paired with the automatic mechanical coupler.",
            ("pinout test", "breakaway force check", "ingress protection", "rescue compatibility"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-END-P050",
            "sealed headlight, tail/marker light, threshold-warning, and end-lamp harness kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            2,
            "end kit",
            "LM3-END-SA700",
            ("bom-skeleton.md B17", "sensor_cowl.py", "systems.py"),
            "One reversible lamp and warning-light package fits either cabless end cowl.",
            ("photometric certificate", "function/polarity test", "ingress protection", "A/B-end interchange check"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-ART-P030",
            "inter-car HV/LV jumper, coolant hose loop, energy chain, and drain sleeve kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            articulations,
            "articulation kit",
            "LM3-ART-SA800",
            ("articulation.md", "systems.py", "LM3-SYS-170"),
            "Flexible services package that follows articulation yaw/pitch/roll without violating segregation or bend radius.",
            ("bend-radius sweep", "trainline continuity", "coolant pressure test", "water-drain test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-ART-P040",
            "train-to-train open-end articulation, gangway, drawbar, turntable, and service-jumper cassette",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            0,
            "joint kit",
            "LM3-TTART-SA850",
            ("systems.py", "articulation.md", "interfaces.md", "LM3-SYS-175"),
            "Supplier open-end gangway/articulation cassette for joining two otherwise complete train modules through their common end-interface frames.",
            ("train-to-train motion-envelope proof", "walk-through gangway fire evidence", "trainline continuity", "water ingress/drain test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
            notes="Optional for modular consists. The reference LM3-3car uses closed panoramic ends and therefore carries zero of this kit.",
        ),
        ProductItem(
            "LM3-ART-P041",
            "train-to-train jumper blanking, transition harness, isolation label, and dust-cover kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            0,
            "joint kit",
            "LM3-TTART-SA850",
            ("articulation.md", "interfaces.md", "LM3-SYS-175"),
            "Pre-terminated service transition and blanking hardware for open-end train-to-train gangway joints and protected unused end connectors.",
            ("pinout test", "blanking cover ingress check", "isolation label inspection", "bend-radius sweep"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
            notes="Optional for open mid-connection end configuration.",
        ),
    )


def _assemblies(family: ConsistFamily) -> tuple[AssemblyNode, ...]:
    cars = CAR_COUNT[family]
    return (
        AssemblyNode(
            "LM3-BDY-SA110",
            "underframe datum weldment",
            Layer.SUBASSEMBLY,
            cars,
            (
                "LM3-BDY-P010",
                "LM3-BDY-P020",
                "LM3-BDY-P030",
                "LM3-BDY-P120",
            ),
            "weld and fixture cell",
            ("material release", "fixture tack survey", "weld/NDT release", "post-weld datum survey"),
            ("fabrication-plan.md", "LM3-BDY-110"),
        ),
        AssemblyNode(
            "LM3-BDY-SA120",
            "carbody spaceframe and floor assembly",
            Layer.SUBASSEMBLY,
            cars,
            ("LM3-BDY-SA110", "LM3-BDY-P060", "LM3-BDY-P070"),
            "weld and fixture cell",
            ("door/window aperture survey", "roof rail survey", "carbody dimensional report"),
            ("car_body.py", "LM3-BDY-100"),
        ),
        AssemblyNode(
            "LM3-SHELL-A200",
            "painted carbody frame with one-metre clip-on fiberglass exterior",
            Layer.ASSEMBLY,
            cars,
            (
                "LM3-BDY-SA120",
                "LM3-BDY-P130",
                "LM3-BDY-P140",
                "LM3-WIN-SA320",
                "LM3-EXT-P080",
                "LM3-EXT-P090",
            ),
            "paint / clip-on body / glazing cells",
            ("corrosion report", "clip and anti-lift witness map", "eight-hour trainset body route", "water ingress pre-test"),
            ("modular_fiberglass_body.py", "sensor_cowl.py", "fabrication-plan.md"),
        ),
        AssemblyNode(
            "LM3-WIN-SA320",
            "side glazing cassette installation",
            Layer.SUBASSEMBLY,
            cars * 6,
            ("LM3-BDY-P110", "LM3-EXT-P020"),
            "composite / glazing cell",
            ("aperture gauge", "bond/gasket procedure", "water ingress test"),
            ("cots_equipment.py", "LM3-WIN-210"),
        ),
        AssemblyNode(
            "LM3-DOOR-SA310",
            "door cassette and threshold assembly",
            Layer.SUBASSEMBLY,
            cars * 4,
            ("LM3-BDY-P100", "LM3-EXT-P010"),
            "final assembly and commissioning cell",
            ("door gauge fit", "obstruction test", "closed-and-locked test"),
            ("systems.py", "LM3-DOOR-200"),
        ),
        AssemblyNode(
            "LM3-INT-SA330",
            "interior and passenger systems fit-out",
            Layer.SUBASSEMBLY,
            cars,
            ("LM3-EXT-P060", "LM3-INT-P010", "LM3-INT-P020", "LM3-INT-P030", "LM3-INT-P040", "LM3-INT-P050"),
            "final assembly and commissioning cell",
            ("egress check", "fire-material pack", "liner/trim fit survey", "lighting/PIS/CCTV static test"),
            ("cots_equipment.py", "cabin-fiberglass.md", "LM3-INT-230", "LM3-INT-240"),
        ),
        AssemblyNode(
            "LM3-ROOF-SA410",
            "roof HVAC, PV, antenna, and service-equipment assembly",
            Layer.SUBASSEMBLY,
            cars,
            (
                "LM3-BDY-P080",
                "LM3-ROOF-P010",
                "LM3-ROOF-P020",
                "LM3-EXT-P040",
                "LM3-EXT-P050",
                "LM3-EXT-P070",
                "LM3-TRC-P050",
            ),
            "final assembly and commissioning cell",
            ("roof leak test", "HVAC drain test", "PV isolation/bonding check"),
            ("systems.py", "LM3-HVAC-220", "LM3-HV-325"),
        ),
        AssemblyNode(
            "LM3-HV-SA510",
            "per-car LFP battery, two controllers, DC auxiliary/charge interface, mist, and cooling assembly",
            Layer.SUBASSEMBLY,
            cars,
            (
                "LM3-BDY-P050",
                "LM3-HV-P010",
                "LM3-HV-P020",
                "LM3-HV-P030",
                "LM3-TRC-P030",
                "LM3-TRC-P040",
                "LM3-TRC-P060",
                "LM3-TRC-P070",
                "LM3-SAF-P010",
            ),
            "final assembly and commissioning cell",
            ("HVIL test", "insulation resistance", "coolant pressure test", "first energisation release"),
            ("systems.py", "LM3-HV-310", "LM3-HV-320"),
        ),
        AssemblyNode(
            "LM3-BOG-SA610",
            "powered bogie assembly",
            Layer.SUBASSEMBLY,
            cars,
            (
                "LM3-BOG-P010",
                "LM3-BOG-P030",
                "LM3-BOG-P040",
                "LM3-BOG-P050",
                "LM3-BOG-P060",
                "LM3-TRC-P010",
                "LM3-TRC-P020",
            ),
            "bogie weld and assembly cell",
            ("frame NDT", "wheelset/bearing certificate", "motor/gearbox alignment", "static brake test"),
            ("bogie/assembly.py", "LM3-BOG-400"),
        ),
        AssemblyNode(
            "LM3-BOG-SA620",
            "trailer bogie assembly",
            Layer.SUBASSEMBLY,
            cars,
            ("LM3-BOG-P020", "LM3-BOG-P031", "LM3-BOG-P041", "LM3-BOG-P061"),
            "bogie weld and assembly cell",
            ("frame NDT", "wheelset/bearing certificate", "ride-height setup", "static brake test"),
            ("bogie/assembly.py", "LM3-BOG-410"),
        ),
        AssemblyNode(
            "LM3-CWL-SA710",
            "front/back fiberglass cowl cast kit",
            Layer.SUBASSEMBLY,
            2,
            (
                "LM3-CWL-P010",
                "LM3-CWL-P011",
                "LM3-CWL-P012",
                "LM3-CWL-P013",
                "LM3-CWL-P014",
                "LM3-CWL-P015",
                "LM3-CWL-P016",
            ),
            "composite moulding and trim cell",
            ("laminate coupon release", "insert pull-out", "trim/drill survey", "A/B-end dry-build water test"),
            ("end-cowl.md", "sensor_cowl.py", "LM3-BDY-155"),
        ),
        AssemblyNode(
            "LM3-EIF-SA650",
            "common configurable train-end interface set",
            Layer.SUBASSEMBLY,
            2,
            ("LM3-END-P060", "LM3-END-P061", "LM3-END-P062"),
            "end-interface fixture / final assembly cell",
            (
                "common bolt-grid survey",
                "selected end-option fit gauge",
                "seal and drain continuity",
                "panoramic-or-open-mid configuration record",
            ),
            ("articulation.md", "end-cowl.md", "interfaces.md", "LM3-END-650"),
        ),
        AssemblyNode(
            "LM3-END-SA700",
            "train-end cowl, coupler, crash, and sensor assembly",
            Layer.ASSEMBLY,
            2,
            (
                "LM3-BDY-P040",
                "LM3-BDY-P090",
                "LM3-CWL-SA710",
                "LM3-EXT-P030",
                "LM3-END-P010",
                "LM3-END-P020",
                "LM3-END-P030",
                "LM3-END-P040",
                "LM3-END-P050",
            ),
            "composite / final assembly and commissioning cells",
            ("A/B end interchange", "coupler datum survey", "sensor calibration", "recovery interface check"),
            ("sensor_cowl.py", "systems.py", "LM3-SYS-160", "LM3-OBS-330"),
        ),
        AssemblyNode(
            "LM3-TTART-SA850",
            "optional train-to-train open mid-connection articulation",
            Layer.ASSEMBLY,
            0,
            ("LM3-EIF-SA650", "LM3-ART-P040", "LM3-ART-P041"),
            "final assembly and commissioning cell",
            (
                "open-end option configuration record",
                "train-to-train motion-envelope proof",
                "walk-through gangway continuity",
                "water ingress/drain test",
            ),
            ("articulation.md", "systems.py", "LM3-SYS-175"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        AssemblyNode(
            "LM3-ART-SA800",
            "inter-car articulation and trainline assembly",
            Layer.ASSEMBLY,
            max(0, cars - 1),
            ("LM3-ART-P010", "LM3-ART-P020", "LM3-ART-P030"),
            "final assembly and commissioning cell",
            ("motion-envelope proof", "trainline continuity", "water ingress/drain test"),
            ("articulation.md", "systems.py", "LM3-SYS-170"),
        ),
        AssemblyNode(
            "LM3-SYS-SA900",
            "train control, communication, and safety electronics assembly",
            Layer.ASSEMBLY,
            1,
            (
                "LM3-CTRL-P010",
                "LM3-CTRL-P020",
                "LM3-CTRL-P030",
                "LM3-CTRL-P040",
                "LM3-CTRL-P050",
            ),
            "final assembly and commissioning cell",
            ("network enumeration", "firmware record", "self-test", "event-recorder write/read test"),
            ("systems.py", "hardware/rolling-stock-integration.md", "LM3-ELC-300"),
        ),
        AssemblyNode(
            "LM3-CAR-A900",
            "complete repeated car module",
            Layer.ASSEMBLY,
            cars,
            (
                "LM3-SHELL-A200",
                "LM3-DOOR-SA310",
                "LM3-INT-SA330",
                "LM3-ROOF-SA410",
                "LM3-HV-SA510",
                "LM3-BOG-SA610",
                "LM3-BOG-SA620",
                "LM3-AUX-P010",
            ),
            "final assembly and commissioning cell",
            ("car weigh", "door/HVAC/static systems test", "bogie marriage report", "low-speed yard movement"),
            ("trainset.py", "freecad_trainset.py", "fabrication-plan.md"),
        ),
        AssemblyNode(
            "LM3-TRAINSET-A000",
            "complete light-metro trainset",
            Layer.TRAINSET,
            1,
            ("LM3-CAR-A900", "LM3-EIF-SA650", "LM3-END-SA700", "LM3-ART-SA800", "LM3-SYS-SA900"),
            "final assembly and commissioning cell",
            ("trainset weigh", "static brake/door/HVAC/HV tests", "FEM screening accepted", "dynamic-test release"),
            ("trainset.py", "freecad_assembly_review.py", "freecad_fea.py", "drawing-register.md"),
        ),
        AssemblyNode(
            "LM3-FULLSET-A300",
            "three LM3 train modules joined as one walk-through full set",
            Layer.TRAINSET,
            1,
            ("LM3-TRAINSET-A000", "LM3-TTART-SA850", "LM3-SYS-SA900"),
            "long final assembly track / depot commissioning road",
            (
                "three-train alignment and end-option configuration record",
                "two train-to-train open gangway joint motion sweeps",
                "full-set trainline continuity and safety-loop proof",
                "long-consist FEM screening accepted",
                "static and dynamic release for full-set operation",
            ),
            (
                "train-end-interface.md",
                "full-set-3train-assembly.md",
                "freecad_trainset.py",
                "freecad_fea.py",
                "LM3-SYS-175",
            ),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
    )


def _review_findings(candidate: DesignCandidate, target: dict[str, str | float]) -> tuple[ReviewFinding, ...]:
    def _same(current: str | float, wanted: str | float) -> bool:
        if isinstance(current, float) or isinstance(wanted, float):
            return abs(float(current) - float(wanted)) < 1e-6
        return current == wanted

    baseline_aligned = all(
        _same(CURRENT_CAD_BASELINE[key], target[key])
        for key in ("family", "car_length_m", "motor", "battery", "hvac", "pv_modules_per_car")
    )
    if baseline_aligned:
        bdr003_status = "green"
        bdr003_finding = (
            f"The promoted FreeCAD/product-tree baseline matches the optimizer target: "
            f"{target['car_length_m']} m cars, {target['motor']}, {target['battery']}, "
            f"{target['hvac']}, and {target['pv_modules_per_car']:.0f} PV modules per car."
        )
        bdr003_action = (
            f"Treat this as the v2A buildable seed: {PROMOTED_MOTOR_CONTINUOUS_KW:.0f} kW continuous / "
            f"{PROMOTED_MOTOR_PEAK_KW:.0f} kW peak motors, "
            f"{PROMOTED_BATTERY_USABLE_KWH_PER_CAR:.0f} kWh usable / "
            f"{PROMOTED_BATTERY_GROSS_KWH_PER_CAR:.0f} kWh gross batteries per car, "
            f"{PROMOTED_HVAC_THERMAL_KW_PER_CAR:.0f} kW/car HVAC, and supplier-freeze envelopes before drawings."
        )
    else:
        bdr003_status = "yellow"
        bdr003_finding = (
            f"The optimizer target is {target['car_length_m']} m / {target['motor']} / "
            f"{target['battery']} / {target['hvac']} / {target['pv_modules_per_car']:.0f} PV modules per car, "
            "while the current FreeCAD baseline still differs."
        )
        bdr003_action = (
            "Decide whether to promote the optimizer candidate or freeze the current CAD reference; "
            "then update CAD parameters and BOM together."
        )

    findings: list[ReviewFinding] = [
        ReviewFinding(
            "BDR-001",
            "green",
            "architecture",
            "The current design already uses repeated self-contained car modules with one powered and one trailer bogie per car.",
            "Keep repeated-car architecture as the buildable baseline; it simplifies fixtures, spares, and training.",
        ),
        ReviewFinding(
            "BDR-002",
            "green",
            "COTS/fabricated delineation",
            "The procurement BOM now carries a controlled many-to-many crosswalk from all 100 commercial lines to LM3 product or assembly IDs; definitions and travelers carry the reverse references.",
            "Keep the generated crosswalk mandatory as component kits are split and supplier routes are frozen.",
        ),
        ReviewFinding(
            "BDR-003",
            bdr003_status,
            "candidate/CAD alignment",
            bdr003_finding,
            bdr003_action,
        ),
        ReviewFinding(
            "BDR-004",
            "yellow",
            "supplier freeze",
            "Buildability still depends on supplier-frozen doors, HVAC, batteries, traction, wheelsets, brakes, couplers, and gangways.",
            "Issue RFQ envelopes from the manifest, accept alternates only through fit/power/mass/evidence checks, then lock v2A supplier interfaces.",
        ),
        ReviewFinding(
            "BDR-005",
            "yellow",
            "definition package / shop travelers / shop drawings",
            "Every product-tree node now has a generated definition and signable shop-traveler template with structured material specs, process specs, labor, tooling, QA gates, revision approvals, and signoff blocks; controlled cut lists, weld maps, tolerance stacks, flat patterns, and harness/plumbing drawings are still v2A drawing-package work.",
            "Use the generated material/process definitions and travelers as the drawing/RFQ/traveler index, then promote each MAKE/BID/SOURCE node into controlled LM3-BDY/BOG/HV/ELC drawings before first steel cut.",
        ),
        ReviewFinding(
            "BDR-006",
            "yellow",
            "proof evidence",
            "FEA screening exists and the previously coarse local bracket, coupler-pocket, battery-tray, door-portal, roof-equipment, and bogie-frame items now have generated definitions and assembly integration steps; local proof cases are still not complete.",
            "Attach proof load cases to the generated component definitions and make FEM/static-test acceptance a release gate for each affected subassembly.",
        ),
        ReviewFinding(
            "BDR-007",
            "yellow",
            "mass properties",
            "The generated mass budget now reconciles the 75.308 t optimizer subtotal with the 78.75 t controlled planning tare through an explicit 3.442 t engineering reserve; drawing-level and as-built category closure remains open.",
            "Replace estimates with supplier-frozen, CAD-derived, and weighed values while transferring consumed reserve to the affected category.",
        ),
        ReviewFinding(
            "BDR-008",
            "yellow",
            "joint and fastener control",
            "Every assembly integration step now carries machine-readable join classes, torque authority, and release status; numerical torque, locking, and re-torque values remain open until supplier instructions or joint calculations are released.",
            "Close the generated joint-control schedule by joint ID and reference the accepted values from interface drawings and shop travelers.",
        ),
    ]
    if not candidate.feasible:
        findings.append(
            ReviewFinding(
                "BDR-009",
                "red",
                "optimizer feasibility",
                f"The selected candidate is infeasible: {', '.join(candidate.violations)}.",
                "Loosen requirements only by design authority review, or add better candidate components to the design space.",
            )
        )
    return tuple(findings)


def _serialise(value):
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    raise TypeError(f"cannot serialise {type(value)!r}")


def _definition_bucket_for_layer(layer: Layer) -> str:
    if layer in (Layer.FABRICATED_PART, Layer.EXTERNAL_COMPONENT):
        return "parts"
    if layer is Layer.SUBASSEMBLY:
        return "subassemblies"
    if layer is Layer.ASSEMBLY:
        return "assemblies"
    if layer is Layer.TRAINSET:
        return "trainsets"
    raise ValueError(f"unknown layer {layer!r}")


def _path_from_id(root: Path, bucket: str, definition_id: str, suffix: str) -> Path:
    return root / bucket / f"{definition_id}{suffix}"


def _spec_payload(spec: MaterialSpec | ProcessSpec) -> dict[str, object]:
    return asdict(spec)


def _item_material_spec(item: ProductItem) -> MaterialSpec:
    text = f"{item.id} {item.title} {item.make_or_buy_basis} {' '.join(item.source_refs)}".lower()
    evidence = ("certificate of conformity", "incoming inspection record")

    if item.id == "LM3-BDY-P130":
        return MaterialSpec(
            "fire-retardant exterior fiberglass sandwich",
            "UV-stable E-glass/vinyl-ester 1,000 mm body module with local core and potted inserts",
            "project exterior laminate schedule plus EN 45545 fire/smoke, insert, vibration, and aerodynamic evidence",
            "994 mm finished side/window/door/roof variants CNC-trimmed from a common 1,000 mm mould pitch",
            "28 mm nominal sandwich with solid clip lands, sealed edges, and replaceable 6 mm EPDM joints",
            "UV-stable exterior gelcoat/paint, sealed cut edges, drained joints, and mixed-metal isolation",
            "laminate/resin/cure batch, module serial, trim record, insert batch, and fire certificate",
            evidence + ("laminate coupon", "insert/clip proof", "master-frame fit", "water/vibration evidence"),
        )
    if item.id == "LM3-BDY-P140":
        return MaterialSpec(
            "stainless retention hardware and elastomer seal kit",
            "keyed hook, captive over-centre clip, independent anti-lift retainer, backing plate, and railway-grade EPDM seal",
            "released LM3-BDY-160 joint calculation plus project corrosion, fatigue, fire, and ingress requirements",
            "laser-cut/folded clip rails, captive hardware, potted backing plates, and extruded dry seals",
            "common 1,000 mm pitch with asymmetric key and visible closed witness mark",
            "passivated stainless hardware, isolated mixed-metal interfaces, UV/ozone-resistant EPDM",
            "hardware heat/batch, seal batch, proof-lot record, and car module map",
            evidence + ("clip proof-load lot", "seal certificate", "water-ingress record"),
        )
    if item.id == "LM3-END-P060":
        return MaterialSpec(
            "common structural end-interface steel and seal datum kit",
            "S355 machined carrier ring, stainless option bolt-grid inserts, drain lands, and EPDM sealing datums",
            "released LM3-END-650 interface-control drawing plus EN 15085 weld, corrosion, and ingress evidence",
            "jig-welded/machined end carrier ring with common panoramic/open-mid bolt pattern and replaceable seal lands",
            "one common end position envelope accepting either LM3-END-SA700 or LM3-TTART-SA850 without primary-frame rework",
            "blast/prime/topcoat on steel, passivated stainless inserts, sealed drain edges, and isolated mixed-metal joints",
            "steel heat, weld consumable, insert batch, machining survey, seal batch, and configuration record",
            evidence + ("option bolt-grid survey", "seal datum continuity", "configuration fit gauge"),
        )
    if item.id == "LM3-END-P061":
        return MaterialSpec(
            "panoramic end-option interface closeout kit",
            "machined shim/closeout plates, cowl/glass carrier transfer brackets, sensor datum plates, and EPDM seal stock",
            "released LM3-END-650 panoramic option drawing plus glazing, sensor, corrosion, and water-ingress evidence",
            "kitted interface hardware between common carrier ring, fiberglass cowl, panoramic glass, lamps, and T-OBS sensors",
            "selected for the two outer ends of the reference three-car trainset",
            "painted/passivated hardware, isolated stainless inserts, replaceable EPDM seals, and protected glass/sensor datums",
            "hardware heat/batch, seal batch, shim map, datum survey, and selected-option record",
            evidence + ("panoramic option fit gauge", "glass/cowl datum transfer", "sensor datum check"),
        )
    if item.id == "LM3-END-P062":
        return MaterialSpec(
            "open mid-connection end-option interface kit",
            "machined bellows clamp frame, threshold bridge, turntable edge trim, drain tray, and fire-rated passenger portal closeout",
            "released LM3-END-650-MID option drawing plus gangway, fire/smoke, slip, corrosion, and ingress evidence",
            "kitted open portal hardware replacing the panoramic cowl/glass at a train-to-train walk-through joint",
            "selected only for train modules configured as mid open connections",
            "painted/passivated hardware, replaceable rubber seals, anti-slip threshold finish, and cleanable passenger trim",
            "hardware heat/batch, trim/seal batch, threshold survey, drain test, and selected-option record",
            evidence + ("open-portal gauge", "bellows clamp fit", "threshold/turntable level check"),
        )
    if item.id == "LM3-EXT-P080":
        return MaterialSpec(
            "supplier-qualified exterior GFRP side-module material pack",
            "UV-stable E-glass/vinyl-ester or equivalent fire-rated side-module laminate, core, gelcoat, release, and coupon consumables",
            "supplier laminate certificate plus project EN 45545 fire/smoke and LM3-BDY-160 mould-process evidence",
            "kitted dry reinforcement, resin system, local core, gelcoat/paint-primer, release consumables, insert-potting consumables, and witness-coupon stock",
            "supports 1,000 mm side-module mould pitch, 994 mm finished module width, solid/window/door trim variants, and solid clip lands",
            "UV-stable exterior finish system with sealed cut-edge compatibility and mixed-metal insert isolation",
            "fibre/resin/core/gelcoat batch, shelf-life record, cure/coupon trace, and fire certificate",
            evidence + ("EN 45545 evidence", "laminate coupon", "resin/fibre batch trace", "mould release record"),
        )
    if item.id == "LM3-EXT-P090":
        return MaterialSpec(
            "supplier-qualified exterior GFRP roof-module and seal material pack",
            "fire-rated roof-module laminate consumables, EPDM dry-seal stock, removable skirt blanks, and retained-fastener consumables",
            "supplier laminate and seal certificates plus project EN 45545, ozone/UV, ingress, and LM3-BDY-160 mould-process evidence",
            "kitted roof-module reinforcement/core/resin/finish consumables, extruded EPDM seals, skirt blanks, trim stock, and coupon material",
            "supports 1,000 mm roof-module mould pitch, dry joints, drain paths, removable skirts, and anti-lift/clip hardware interfaces",
            "UV-stable roof finish, sealed cut edges, ozone-resistant EPDM, and galvanic isolation at retained hardware",
            "laminate batch, seal batch, cure/coupon trace, service-removal record, and water-test record",
            evidence + ("EN 45545 evidence", "roof laminate coupon", "seal certificate", "water and debris-ingress check"),
        )

    if item.route in (Route.BID, Route.SOURCE) or item.layer is Layer.EXTERNAL_COMPONENT:
        if any(word in text for word in ("cowl", "fiberglass", "fibreglass", "frp", "phenolic", "composite", "laminate", "liner", "trim")):
            if any(word in text for word in ("ceiling", "sidewall", "battery strake", "vestibule", "prm", "interior", "cabin")):
                return MaterialSpec(
                    "fire-rated cabin fiberglass / phenolic composite",
                    "EN 45545 HL2 candidate FRP, phenolic, or glass/basalt-fibre sandwich interior panel",
                    "EN 45545-2 interior material evidence plus supplier laminate/phenolic panel certificate",
                    "moulded or CNC-trimmed liner, reveal, cover, hatch, and kick-panel shells with potted inserts",
                    "panel thickness, edge return, insert pattern, and clip grid per LM3-INT v2A drawing",
                    "cleanable interior gelcoat/paint or decorative film with sealed edges and anti-slip finish where walked on",
                    "laminate/panel batch, resin/cure or board batch, insert batch, adhesive batch, and fire certificate",
                    evidence + ("fire-material certificate", "insert pull-out evidence", "trim/cure record"),
                )
            return MaterialSpec(
                "fire-retardant fiberglass composite",
                "E-glass or basalt-fibre/vinyl-ester end-cowl laminate and insert kit",
                "supplier laminate schedule plus project fire/smoke, coupon, and insert pull-out evidence",
                "moulded cowl cast, solid flanges, local core in broad skins, potted inserts, and trim/repair coupons",
                "laminate thickness, ply drop, core map, insert pattern, split line, and trim datum per LM3-BDY-155",
                "UV-stable exterior gelcoat/paint, sealed cut edges, gasketed seams, and mixed-metal isolation",
                "laminate batch, resin batch, cure record, insert pull-out record, adhesive batch, and coupon traceability",
                evidence + ("laminate coupon", "cure record", "insert pull-out evidence", "fire-smoke certificate"),
            )
        if any(word in text for word in ("door", "cassette")):
            return MaterialSpec(
                "supplier-certified rail door system",
                "COTS/BID electric passenger door cassette",
                "supplier rail door specification plus EN 14752 evidence where applicable",
                "preassembled door cassette with seals, drive, controller, and emergency release",
                "supplier envelope frozen by RFQ drawing",
                "supplier corrosion/fire/smoke protection accepted by OSR evidence pack",
                "serialised supplier CoC, revision, and lifecycle evidence",
                evidence + ("obstruction / locked-loop evidence", "fire-smoke certificate pack"),
            )
        if any(word in text for word in ("glazing", "glass", "window")):
            return MaterialSpec(
                "rail laminated safety glazing",
                "bonded/gasketed laminated safety-glass cassette",
                "supplier rail glazing specification plus project fire/smoke and impact evidence",
                "laminated glass cassette with heater/bond/gasket hardware as required",
                "aperture envelope and bond/gasket land frozen by RFQ drawing",
                "edge seal, heater isolation, and supplier-approved cleaning/protection",
                "pane/cassette serial number, CoC, heater record, and installation batch",
                evidence + ("glazing certificate", "heater/isolation record"),
            )
        if any(word in text for word in ("hvac", "diffuser", "duct", "grille")):
            return MaterialSpec(
                "supplier HVAC and air-distribution kit",
                "hot-climate roof HVAC / fire-rated interior duct kit",
                "supplier rail/bus HVAC specification plus project EMC, vibration, and fire evidence",
                "packaged roof unit, curb gasket, diffusers, ducts, grilles, and access panels",
                "roof curb and saloon envelope frozen by RFQ drawing",
                "supplier coating, condensate protection, and fire-rated interior surfaces",
                "unit serial number, refrigerant/coolant data, CoC, and fire-material batch",
                evidence + ("capacity test evidence", "fire-material certificate"),
            )
        if any(word in text for word in ("pv", "solar", "resistor")):
            return MaterialSpec(
                "roof electrical energy equipment",
                "PV module / resistor / clamp / isolator kit",
                "supplier datasheet plus project bonding, isolation, fire, and vibration evidence",
                "module, thermal shield, aluminum/stainless clamp hardware, and UV-rated harness",
                "roof keep-out, clamp pitch, and thermal clearance frozen by RFQ drawing",
                "UV/weather protection, hot-surface labelling, and galvanic isolation where required",
                "module serials, resistance/PV flash data, CoC, and harness batch",
                evidence + ("electrical datasheet", "bonding/isolation record"),
            )
        if any(word in text for word in ("battery", "contactor", "inverter", "charge", "hvil", "high-voltage")):
            return MaterialSpec(
                "supplier high-voltage traction equipment",
                "battery / inverter / contactor / charger certified equipment class",
                "supplier rail traction specification plus project HVIL, EMC, isolation, and thermal evidence",
                "sealed HV module, enclosure, orange HV harness, connectors, cooling interfaces, and labels",
                "tray, connector, bend-radius, vent, and service envelope frozen by RFQ drawing",
                "supplier enclosure protection, orange HV marking, bonding, and coolant compatibility",
                "serialised HV equipment CoC, firmware/config revision, insulation record, and evidence pack",
                evidence + ("isolation test record", "HVIL / EMC evidence"),
            )
        if any(word in text for word in ("wheelset", "axlebox", "bearing", "brake", "air spring", "damper")):
            return MaterialSpec(
                "supplier-certified running gear",
                "wheelset / bearing / brake / suspension safety-critical kit",
                "supplier rail running-gear specification plus project brake, ride-height, and traceability evidence",
                "machined/forged rotating parts, brake hardware, suspension elements, and fastener kit",
                "bogie interface envelope frozen by RFQ drawing",
                "supplier corrosion protection and lubrication preservation",
                "serialised wheelset, bearing, brake, and suspension records",
                evidence + ("wheelset/bearing certificates", "brake evidence"),
            )
        if any(word in text for word in ("motor", "gearbox", "coupling")):
            return MaterialSpec(
                "supplier traction drive equipment",
                "traction motor / gearbox / coupling certified equipment class",
                "supplier rail traction specification plus project EMC, thermal, and mount-load evidence",
                "preassembled motor, gearbox, coupling, seals, oil ports, and mounting hardware",
                "bogie motor-cradle and axle interface frozen by RFQ drawing",
                "supplier coating, lubrication preservation, earthing/bonding, and thermal labels",
                "serialised drive equipment CoC, test report, oil data, and revision record",
                evidence + ("thermal curve", "mounting-foot proof evidence"),
            )
        if any(word in text for word in ("coupler", "crash", "absorber")):
            return MaterialSpec(
                "supplier crash/coupler system",
                "automatic coupler and crash-energy absorber kit",
                "supplier crashworthiness specification plus project recovery and interface evidence",
                "coupler head, draft gear, absorber, jumper hardware, and bolted mounting kit",
                "coupler pocket envelope and load path frozen by RFQ drawing",
                "supplier coating, preservation, and rescue/recovery labels",
                "serialised coupler/absorber CoC, overhaul status, and proof evidence",
                evidence + ("crash-energy evidence", "bolt/torque evidence"),
            )
        if any(word in text for word in ("harness", "jumper", "sensor", "antenna", "t-ecu", "pis", "cctv", "intercom")):
            return MaterialSpec(
                "rail-rated electrical / control equipment",
                "LV/data harness, cabinet, sensor, antenna, and trainline kit",
                "supplier rail electronics specification plus project EMC, IP, and fire evidence",
                "cabinet, harness, connector, sensor, bracket, antenna, and label kit",
                "connector, bend-radius, service-loop, and mounting envelope frozen by RFQ drawing",
                "halogen/fire-rated cable where required, IP sealing, bonding, and label protection",
                "serialised equipment CoC, firmware/config record, harness batch, and continuity record",
                evidence + ("continuity test", "EMC/IP evidence"),
            )
        if any(word in text for word in ("seat", "flooring", "interior", "lighting", "signage", "grab")):
            return MaterialSpec(
                "passenger interior COTS kit",
                "fire-rated seat, flooring, trim, lighting, PIS, CCTV, signage, and grab-rail kit",
                "supplier interior specification plus project EN 45545/fire-smoke evidence where applicable",
                "late-installed saloon kit with fasteners, access panels, looms, and labels",
                "saloon, PRM aisle, emergency egress, and service-panel envelope frozen by RFQ drawing",
                "fire/smoke compliant finish, anti-slip flooring, and cleanable passenger surfaces",
                "batch CoC, fire-material certificates, and installation traceability",
                evidence + ("fire-material certificate pack", "egress/lighting evidence"),
            )
        return MaterialSpec(
            "supplier-controlled external component",
            "COTS/BID component class matched to OSR envelope",
            "supplier specification plus project interface, safety, EMC/fire, and lifecycle evidence",
            "preassembled supplier module with installation kit",
            "mass, volume, mounting datum, service clearance, and connector envelope frozen by RFQ drawing",
            "supplier finish/protection accepted by OSR evidence pack",
            "serialised CoC, datasheet, revision, and incoming inspection record",
            evidence + ("datasheet / evidence pack",),
        )

    if any(word in text for word in ("ceiling", "sidewall", "battery strake", "vestibule", "prm", "interior", "cabin", "liner", "trim")) and any(
        word in text for word in ("fiberglass", "fibreglass", "frp", "phenolic", "composite")
    ):
        return MaterialSpec(
            "fire-rated cabin fiberglass / phenolic composite",
            "EN 45545 HL2 candidate FRP, phenolic, or glass/basalt-fibre sandwich interior panel",
            "EN 45545-2 interior material evidence plus supplier laminate/phenolic panel certificate",
            "moulded or CNC-trimmed liner, reveal, cover, hatch, and kick-panel shells with potted inserts",
            "panel thickness, edge return, insert pattern, and clip grid per LM3-INT v2A drawing",
            "cleanable interior gelcoat/paint or decorative film with sealed edges and anti-slip finish where walked on",
            "laminate/panel batch, resin/cure or board batch, insert batch, adhesive batch, and fire certificate",
            ("fire-material certificate", "laminate/panel batch record", "insert pull-out evidence", "trim/cure record"),
        )
    if _is_composite_make_item(item):
        return MaterialSpec(
            "fire-retardant fiberglass composite",
            "E-glass FRP cast kit with bonded/moulded inserts",
            "supplier laminate schedule plus project fire/smoke and structural coupon evidence",
            "multi-part moulded shell, bonded inserts, service hatch lands, and trim edges",
            "laminate schedule, insert pattern, split line, and trim datum frozen by supplier drawing",
            "UV-stable exterior gelcoat/paint with sealed cut edges and insert corrosion isolation",
            "laminate batch, resin batch, cure record, insert pull-out record, and coupon traceability",
            ("laminate coupon", "cure record", "insert pull-out evidence", "fire-smoke certificate"),
        )
    if item.id.startswith("LM3-BOG") or "bogie" in text or "torque link" in text:
        return MaterialSpec(
            "rail structural steel",
            "EN 10025 S355/S460 candidate bogie structural plate/RHS",
            "EN 10025 material certificate; EN 15085 weld-quality evidence for classed rail weldments",
            "laser/plasma-cut plate, RHS/folded sections, machined bosses, and bracket kit",
            "thickness/section per v2A controlled drawing and FEM release",
            "blast, primer/topcoat, cavity/weld-edge protection, and torque-stripe where applicable",
            "heat number, weld consumable batch, WPS/WPQR, welder ID, and NDT record",
            ("mill certificate", "weld consumable certificate", "WPS/WPQR", "NDT report"),
        )
    if any(word in text for word in ("hv cable tray", "bonding stud", "orange cover", "bracket", "tray", "manifold", "drain pan")):
        return MaterialSpec(
            "formed sheet metal / stainless local hardware",
            "S355 or 304/316 stainless local bracket/tray candidate, selected by exposure zone",
            "EN 10025 / EN 10088 certificate as applicable plus project bonding/corrosion evidence",
            "laser-cut, folded, drilled sheet/plate with inserts, studs, clips, and labels",
            "thickness, stainless grade, and galvanic isolation frozen by v2A controlled drawing",
            "zinc/paint/stainless passivation, orange HV marking, edge protection, and sealing as applicable",
            "heat number, coating batch, bonding test, and installation batch traceability",
            ("mill certificate", "coating/passivation record", "bonding continuity record"),
        )
    return MaterialSpec(
        "rail structural steel",
        "EN 10025 S355 candidate primary-structure RHS/folded plate",
        "EN 10025 material certificate; EN 15085 weld-quality evidence for classed rail weldments",
        "laser-cut RHS/plate, press-brake folds, drilled/machined inserts, and bracket kit",
        "thickness/section per v2A controlled drawing and FEM release",
        "blast, rail primer/topcoat, cavity wax/sealant, and weld-edge protection",
        "heat number, weld consumable batch, WPS/WPQR, welder ID, and NDT record",
        ("mill certificate", "weld consumable certificate", "WPS/WPQR", "NDT report"),
    )


def _item_process_spec(item: ProductItem) -> ProcessSpec:
    text = f"{item.id} {item.title} {item.make_or_buy_basis} {' '.join(item.acceptance)}".lower()
    if item.route is Route.MAKE:
        if _is_composite_make_item(item):
            is_cabin = any(word in text for word in ("ceiling", "sidewall", "battery strake", "vestibule", "prm", "cabin", "interior"))
            primary = [
                "inspect mould/trim fixture",
                "apply release system",
                "cut dry reinforcement or panel blank",
                "lay up / infuse / press laminate",
                "controlled cure",
                "demould and post-cure where required",
                "trim/drill to controlled datum",
                "fit inserts/clips/gaskets",
                "dry-fit to parent fixture",
            ]
            joining = [
                "potted/captive inserts",
                "retained fasteners or clip grid",
                "adhesive/sealant only where removal and repair rules allow",
            ]
            controls = [
                "released laminate schedule",
                "resin/adhesive batch and shelf-life check",
                "mould release record",
                "cure temperature/time record",
                "fire-material certificate check",
                "edge sealing and dust-control rule",
            ]
            inspections = [
                "laminate coupon",
                "void/delamination visual tap check",
                "trim-line gauge",
                "insert pull-out where classed",
                "fit-up survey",
                *item.acceptance,
            ]
            if is_cabin:
                controls.extend(["passenger-facing edge-radius rule", "anti-slip rule for PRM/step panels"])
                inspections.extend(["sharp-edge inspection", "rattle check", "cleanability inspection"])
            else:
                controls.extend(["A/B-end interchange rule", "glass carrier and sensor datum protection"])
                inspections.extend(["split-line gap check", "water-ingress test", "repair coupon demonstration"])
            return ProcessSpec(
                tuple(dict.fromkeys(primary)),
                tuple(dict.fromkeys(joining)),
                tuple(dict.fromkeys(controls)),
                tuple(dict.fromkeys(inspections)),
                f"MOULD/FIX-{item.id} plus TRIM-GAUGE-{item.id}",
                "v2A composite-process controlled MAKE item; generated traveler is unsigned until build",
            )
        joining = ["fixture tack and weld where structural", "bolted/torqued installation to parent datum"]
        controls = ["released drawing/revision check", "material certificate check", "datum gauge before parent release"]
        inspections = ["dimensional inspection", "visual inspection"]
        primary = ["cut", "form", "drill/machine", "de-burr", "trial fit"]
        if any(word in text for word in ("weld", "bogie", "side sill", "bolster", "underframe", "frame", "coupler")):
            primary.extend(["fixture weld", "controlled cool / stress relief where WPS requires", "post-weld machine where required"])
            controls.extend(["WPS/WPQR release", "welder qualification", "weld map and heat-input control"])
            inspections.extend(["VT", "MT/UT where classed", "post-weld datum survey"])
        if any(word in text for word in ("bond", "pv", "window", "glazing")):
            joining.append("adhesive bonding or gasketed interface preparation")
            controls.extend(["surface-preparation record", "adhesive batch/pot-life record", "bond coupon where required"])
            inspections.extend(["bond-land inspection", "water/leak test where applicable"])
        if any(word in text for word in ("hv", "battery", "cable", "bonding", "orange", "coolant")):
            joining.extend(["bonding/earthing hardware", "segregated clipped service routing"])
            controls.extend(["HV/LV segregation check", "bend-radius check", "label/revision check"])
            inspections.extend(["bond continuity", "insulation/isolation check where applicable"])
        return ProcessSpec(
            tuple(dict.fromkeys(primary)),
            tuple(dict.fromkeys(joining)),
            tuple(dict.fromkeys(controls)),
            tuple(dict.fromkeys(inspections + list(item.acceptance))),
            f"FIX-{_tooling_prefix_for_id(item.id)}-FAB plus GAUGE-{item.id}-DATUM",
            "v2A drawing-controlled MAKE process; generated traveler is unsigned until build",
        )

    controls = ["RFQ envelope freeze", "supplier certificate/revision check", "incoming quarantine until evidence accepted"]
    inspections = ["incoming visual inspection", "envelope fit check", *item.acceptance]
    joining = ["bolted/torqued installation", "sealed, gasketed, bonded, or clipped interface as supplier envelope requires"]
    if any(word in text for word in ("hv", "battery", "inverter", "contactor", "charging", "pv", "motor", "resistor")):
        controls.extend(["HV safety plan", "LOTO/service-disconnect rule", "EMC/bonding evidence review"])
        inspections.extend(["bond continuity", "insulation/isolation check", "HVIL functional check where applicable"])
    if any(word in text for word in ("coolant", "hvac", "drain", "washer", "suppression", "thermal")):
        controls.extend(["fluid compatibility check", "hose/pipe routing release"])
        inspections.extend(["pressure/leak test", "drain-flow test where applicable"])
    if any(word in text for word in ("door", "brake", "coupler", "articulation", "gangway", "bellows", "train-to-train")):
        controls.extend(["safety interlock interface freeze", "supplier lifecycle evidence review"])
        inspections.extend(["functional static test", "emergency/recovery function check where applicable"])
    return ProcessSpec(
        ("receive", "quarantine", "evidence review", "incoming fit check", "release to parent kit"),
        tuple(dict.fromkeys(joining)),
        tuple(dict.fromkeys(controls)),
        tuple(dict.fromkeys(inspections)),
        f"RFQ-{item.id}, CERT-{item.id}, GAUGE-{item.id}-ENVELOPE",
        f"{item.route.value} supplier-controlled process; OSR controls envelope and acceptance evidence",
    )


def _assembly_material_spec(
    node: AssemblyNode,
    items: dict[str, ProductItem],
    assemblies: dict[str, AssemblyNode],
) -> MaterialSpec:
    child_materials: list[str] = []
    for child_id in node.children:
        if child_id in items:
            child_materials.append(_item_material_spec(items[child_id]).material_family)
        elif child_id in assemblies:
            child_materials.append(f"{child_id} child assembly material set")
    material_summary = ", ".join(dict.fromkeys(child_materials)) or "child material set"
    return MaterialSpec(
        "assembly material set",
        f"{node.id} inherits released child material specifications",
        "all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls",
        material_summary,
        "as defined by child drawings and assembly interface control drawing",
        "protect damaged coating, exposed edges, seals, bonds, and labels during assembly",
        "child serial/heat/batch records plus assembly traveler traceability",
        ("child material certificates accepted", "assembly traveler traceability", "interface-control drawing revision"),
    )


def _assembly_process_spec(node: AssemblyNode) -> ProcessSpec:
    text = f"{node.id} {node.title} {node.build_cell} {' '.join(node.hold_points)}".lower()
    primary = ["release child kit", "fixture or datum setup", "install children", "torque/fit-up record", "release to parent"]
    joining = ["bolted/torqued interfaces", "shimmed datum interfaces as required"]
    controls = ["child definition/revision check", "tooling calibration check", "parent interface freeze"]
    inspections = ["child acceptance evidence review", *node.hold_points]
    if "weld" in text:
        primary.insert(2, "fixture tack/weld")
        joining.append("WPS-controlled structural welding")
        controls.extend(["weld map release", "WPS/WPQR and welder qualification"])
        inspections.extend(["VT", "MT/UT where classed", "post-weld datum survey"])
    if any(word in text for word in ("composite", "glazing", "leak", "water", "roof")):
        joining.append("adhesive/bonded/gasketed sealing interfaces")
        controls.extend(["surface preparation record", "adhesive/sealant batch and cure record"])
        inspections.extend(["water/leak test", "bond/gasket witness check"])
    if any(word in text for word in ("hv", "electrical", "commissioning", "traction", "control")):
        joining.extend(["bonding/earthing", "segregated harness/fluid routing"])
        controls.extend(["LOTO/HV safety rule", "EMC/bonding release", "software/configuration record where applicable"])
        inspections.extend(["continuity", "insulation/isolation", "functional static test"])
    if "bogie" in text:
        controls.extend(["wheelset/bearing certificate review", "ride-height setup"])
        inspections.extend(["alignment survey", "static brake test"])
    return ProcessSpec(
        tuple(dict.fromkeys(primary)),
        tuple(dict.fromkeys(joining)),
        tuple(dict.fromkeys(controls)),
        tuple(dict.fromkeys(inspections)),
        f"FIX-{node.id}, KIT-{node.id}, calibrated torque/gauge set",
        "assembly traveler controlled; generated template is unsigned until build",
    )


def _item_payload(item: ProductItem) -> dict[str, object]:
    material_spec = _item_material_spec(item)
    process_spec = _item_process_spec(item)
    return {
        "id": item.id,
        "title": item.title,
        "definition_type": "product-item",
        "layer": item.layer.value,
        "route": item.route.value,
        "quantity_per_trainset": item.quantity_per_trainset,
        "unit": item.unit,
        "parent": item.parent,
        "bom_line_ids": list(bom_line_ids_for_engineering_id(item.id)),
        "source_refs": list(item.source_refs),
        "make_or_buy_basis": item.make_or_buy_basis,
        "acceptance": list(item.acceptance),
        "material_spec": _spec_payload(material_spec),
        "process_spec": _spec_payload(process_spec),
        "maturity": item.maturity.value,
        "notes": item.notes,
    }


def _child_title(child_id: str, items: dict[str, ProductItem], assemblies: dict[str, AssemblyNode]) -> str:
    if child_id in items:
        return items[child_id].title
    if child_id in assemblies:
        return assemblies[child_id].title
    return "unresolved child"


def _placement_zone(child_id: str, title: str) -> str:
    text = f"{child_id} {title}".lower()
    if child_id.startswith("LM3-SAF"):
        return "battery/traction/HVAC safety loop spanning HV bay, roof equipment, and event-recorder input"
    if child_id in {"LM3-BDY-P130", "LM3-BDY-P140"}:
        return "one-metre body-module clip rail, dry seal, and anti-lift datum grid"
    if "end-interface" in text or "end interface" in text:
        return "common configurable train-end interface, option bolt grid, seal/drain datums, and selected-end record"
    if "open-connection" in text or "open mid" in text or "train-to-train" in text:
        return "configurable end-interface, open gangway, train-to-train articulation, and service-jumper envelope"
    if "door" in text or "threshold" in text:
        return "side door aperture and low-floor threshold datum"
    if "window" in text or "glazing" in text or "glass" in text:
        return "side/end glazing aperture and bonded carrier datum"
    if "roof" in text or "hvac" in text or "pv" in text or "antenna" in text or "resistor" in text:
        return "roof equipment rail, curb, and service-access zone"
    if "battery" in text or "hv" in text or "inverter" in text or "contactor" in text or "charging" in text:
        return "under-seat HV bay, side-pin dock zone, and segregated cable route"
    if "bogie" in text or "wheelset" in text or "motor" in text or "gearbox" in text or "brake" in text:
        return "bogie frame, axle, brake, suspension, and underframe marriage datums"
    if "cowl" in text or "coupler" in text or "sensor" in text or "nose" in text:
        return "train-end cowl, crash, coupler, and sensor datum stack"
    if "articulation" in text or "gangway" in text or "jumper" in text:
        return "inter-car articulation, gangway, trainline, and flexible-service envelope"
    if "interior" in text or "seat" in text or "saloon" in text:
        return "saloon interior, PRM aisle, ceiling, and service-panel zone"
    if "control" in text or "t-ecu" in text or "trainline" in text or "harness" in text:
        return "LV cabinet, trainline, network, and diagnostic harness zone"
    return "primary structure datum and final assembly interface"


def _interface_classes(child_id: str, title: str) -> list[str]:
    text = f"{child_id} {title}".lower()
    classes: list[str] = ["mechanical datum"]
    if any(word in text for word in ("hv", "battery", "inverter", "motor", "pv", "contactor", "charging", "resistor")):
        classes.append("high-voltage electrical")
    if any(word in text for word in ("control", "t-ecu", "sensor", "wsp", "harness", "trainline", "antenna", "pis", "cctv")):
        classes.append("low-voltage/data")
    if any(word in text for word in ("hvac", "coolant", "condensate", "drain", "washer", "thermal", "suppression", "mist")):
        classes.append("fluid/thermal")
    if any(word in text for word in ("door", "coupler", "brake", "articulation", "gangway", "bellows", "open-connection")):
        classes.append("safety interlock")
    return classes


def _join_classes(child_id: str, title: str, interface_classes: list[str]) -> list[str]:
    """Classify physical joins independently from the services they carry.

    These values are manufacturing controls, not inferred prose labels.  A
    released interface drawing may narrow the list, but it may not silently
    introduce a joining process absent from this schedule.
    """

    text = f"{child_id} {title}".lower()
    classes: list[str] = []
    if any(
        word in text
        for word in (
            "underframe",
            "side sill",
            "cross-bearer",
            "bolster",
            "spaceframe",
            "bogie welded",
            "end ring frame",
            "portal reinforcement",
            "roof bow",
        )
    ):
        classes.append("structural-weld")
    dry_clip_body = child_id in {"LM3-BDY-P130", "LM3-BDY-P140"}
    if any(word in text for word in ("composite", "fiberglass", "glazing", "window", "pv bonded")) and not dry_clip_body:
        classes.append("adhesive-bonded-panel")
    if any(
        word in text
        for word in (
            "hatch",
            "skirt",
            "service lid",
            "service cover",
            "cowl",
            "door cassette",
            "hvac",
            "bellows",
            "open-connection",
        )
    ):
        classes.append("gasketed-removable-panel")
    if dry_clip_body:
        classes.append("gasketed-removable-panel")

    # Every child has a positively located mechanical interface.  Electrical
    # connectors and hoses never substitute for physical retention.
    classes.append("bolted-structural-datum")
    if "high-voltage electrical" in interface_classes or "low-voltage/data" in interface_classes:
        classes.append("electrical-data")
    if "fluid/thermal" in interface_classes:
        classes.append("fluid-thermal")
    return list(dict.fromkeys(classes))


def _torque_authority(
    child_id: str,
    join_classes: list[str],
    items: dict[str, ProductItem],
) -> tuple[str, str]:
    """Return the required torque source and current release state.

    Numeric torque is deliberately not synthesized from nominal bolt size:
    coatings, lubrication, prevailing-torque devices, captive inserts, and
    supplier bearing limits materially change preload.
    """

    item = items.get(child_id)
    if item is not None and item.route in {Route.BID, Route.SOURCE}:
        return (
            "accepted supplier installation manual plus released OSR interface-control drawing",
            "supplier-freeze-required",
        )
    if "structural-weld" in join_classes or "bolted-structural-datum" in join_classes:
        return (
            "released joint calculation plus interface-control drawing and calibrated-tool procedure",
            "joint-calculation-required",
        )
    return ("released assembly procedure", "procedure-release-required")


def _verification_for_child(
    child_id: str,
    items: dict[str, ProductItem],
    assemblies: dict[str, AssemblyNode],
) -> list[str]:
    if child_id in items:
        return list(items[child_id].acceptance)
    if child_id in assemblies:
        return list(assemblies[child_id].hold_points)
    return ["resolve child before release"]


def _integration_steps(
    node: AssemblyNode,
    items: dict[str, ProductItem],
    assemblies: dict[str, AssemblyNode],
) -> list[dict[str, object]]:
    steps: list[dict[str, object]] = []
    for sequence, child_id in enumerate(node.children, start=1):
        title = _child_title(child_id, items, assemblies)
        interface_classes = _interface_classes(child_id, title)
        join_classes = _join_classes(child_id, title, interface_classes)
        torque_authority, joint_release_status = _torque_authority(child_id, join_classes, items)
        steps.append(
            {
                "sequence": sequence,
                "child_id": child_id,
                "child_title": title,
                "placement_zone": _placement_zone(child_id, title),
                "interface_classes": interface_classes,
                "join_classes": join_classes,
                "torque_authority": torque_authority,
                "joint_release_status": joint_release_status,
                "verification": _verification_for_child(child_id, items, assemblies),
            }
        )
    return steps


def _assembly_payload(
    node: AssemblyNode,
    items: dict[str, ProductItem],
    assemblies: dict[str, AssemblyNode],
) -> dict[str, object]:
    material_spec = _assembly_material_spec(node, items, assemblies)
    process_spec = _assembly_process_spec(node)
    return {
        "id": node.id,
        "title": node.title,
        "definition_type": "assembly-node",
        "layer": node.layer.value,
        "quantity_per_trainset": node.quantity_per_trainset,
        "children": list(node.children),
        "build_cell": node.build_cell,
        "bom_line_ids": list(bom_line_ids_for_engineering_id(node.id)),
        "hold_points": list(node.hold_points),
        "source_refs": list(node.source_refs),
        "integration_steps": _integration_steps(node, items, assemblies),
        "material_spec": _spec_payload(material_spec),
        "process_spec": _spec_payload(process_spec),
        "maturity": node.maturity.value,
    }


def render_product_item_definition(item: ProductItem) -> str:
    material_spec = _item_material_spec(item)
    process_spec = _item_process_spec(item)
    lines = [
        f"# {item.id} — {item.title}",
        "",
        "| Field | Value |",
        "|---|---|",
        "| Definition type | Product item |",
        f"| Layer | `{item.layer.value}` |",
        f"| Route | `{item.route.value}` |",
        f"| Quantity per trainset | {item.quantity_per_trainset:g} {item.unit} |",
        f"| Parent assembly | `{item.parent}` |",
        f"| Procurement BOM lines | {', '.join(f'`{line_id}`' for line_id in bom_line_ids_for_engineering_id(item.id))} |",
        f"| Maturity | `{item.maturity.value}` |",
        "",
        "## Make / buy basis",
        "",
        item.make_or_buy_basis,
        "",
        "## Material specification",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Material family | {material_spec.material_family} |",
        f"| Grade / part class | {material_spec.grade_or_part_class} |",
        f"| Governing standard | {material_spec.governing_standard} |",
        f"| Form factor | {material_spec.form_factor} |",
        f"| Nominal section | {material_spec.nominal_section} |",
        f"| Finish / protection | {material_spec.finish_or_protection} |",
        f"| Traceability | {material_spec.traceability} |",
        "",
        "Evidence required:",
        "",
    ]
    lines.extend(f"- {evidence}" for evidence in material_spec.evidence_required)
    lines.extend(
        [
            "",
            "## Process specification",
            "",
            f"- Primary processes: {', '.join(process_spec.primary_processes)}",
            f"- Joining methods: {', '.join(process_spec.joining_methods)}",
            f"- Special process controls: {', '.join(process_spec.special_process_controls)}",
            f"- Inspection methods: {', '.join(process_spec.inspection_methods)}",
            f"- Tooling basis: {process_spec.tooling_basis}",
            f"- Release level: {process_spec.release_level}",
            "",
        ]
    )
    lines.extend(
        [
        "## Acceptance gates",
        "",
        ]
    )
    lines.extend(f"- {gate}" for gate in item.acceptance)
    lines.extend(["", "## Source references", ""])
    lines.extend(f"- `{ref}`" for ref in item.source_refs)
    if item.notes:
        lines.extend(["", "## Notes", "", item.notes])
    lines.append("")
    return "\n".join(lines)


def render_assembly_definition(
    node: AssemblyNode,
    items: dict[str, ProductItem],
    assemblies: dict[str, AssemblyNode],
) -> str:
    integration_steps = _integration_steps(node, items, assemblies)
    material_spec = _assembly_material_spec(node, items, assemblies)
    process_spec = _assembly_process_spec(node)
    lines = [
        f"# {node.id} — {node.title}",
        "",
        "| Field | Value |",
        "|---|---|",
        "| Definition type | Assembly node |",
        f"| Layer | `{node.layer.value}` |",
        f"| Quantity per trainset | {node.quantity_per_trainset:g} |",
        f"| Build cell | {node.build_cell} |",
        f"| Procurement BOM lines | {', '.join(f'`{line_id}`' for line_id in bom_line_ids_for_engineering_id(node.id)) or 'None directly assigned'} |",
        f"| Maturity | `{node.maturity.value}` |",
        "",
        "## Children",
        "",
    ]
    lines.extend(f"- `{child}`" for child in node.children)
    lines.extend(
        [
            "",
            "## Material specification",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| Material family | {material_spec.material_family} |",
            f"| Grade / part class | {material_spec.grade_or_part_class} |",
            f"| Governing standard | {material_spec.governing_standard} |",
            f"| Form factor | {material_spec.form_factor} |",
            f"| Nominal section | {material_spec.nominal_section} |",
            f"| Finish / protection | {material_spec.finish_or_protection} |",
            f"| Traceability | {material_spec.traceability} |",
            "",
            "Evidence required:",
            "",
        ]
    )
    lines.extend(f"- {evidence}" for evidence in material_spec.evidence_required)
    lines.extend(
        [
            "",
            "## Process specification",
            "",
            f"- Primary processes: {', '.join(process_spec.primary_processes)}",
            f"- Joining methods: {', '.join(process_spec.joining_methods)}",
            f"- Special process controls: {', '.join(process_spec.special_process_controls)}",
            f"- Inspection methods: {', '.join(process_spec.inspection_methods)}",
            f"- Tooling basis: {process_spec.tooling_basis}",
            f"- Release level: {process_spec.release_level}",
            "",
        ]
    )
    lines.extend(["", "## Integration design", ""])
    for step in integration_steps:
        interface_classes = ", ".join(f"`{klass}`" for klass in step["interface_classes"])
        join_classes = ", ".join(f"`{klass}`" for klass in step["join_classes"])
        lines.extend(
            [
                f"### {step['sequence']}. `{step['child_id']}` — {step['child_title']}",
                "",
                f"- Placement zone: {step['placement_zone']}",
                f"- Interfaces: {interface_classes}",
                f"- Join classes: {join_classes}",
                f"- Torque authority: {step['torque_authority']}",
                f"- Joint release status: `{step['joint_release_status']}`",
                "- Verification:",
            ]
        )
        lines.extend(f"  - {gate}" for gate in step["verification"])
        lines.append("")
    lines.extend(["", "## Hold points", ""])
    lines.extend(f"- {hold_point}" for hold_point in node.hold_points)
    lines.extend(["", "## Source references", ""])
    lines.extend(f"- `{ref}`" for ref in node.source_refs)
    lines.append("")
    return "\n".join(lines)


def render_definition_index(design: BuildableTrainsetDesign, root: Path) -> str:
    lines = [
        "# Buildable trainset definition pack",
        "",
        "Generated by `scripts/buildable-trainset.sh` from the product tree in",
        "`osr_mech.buildable_trainset`. Each part, external component,",
        "subassembly, assembly, and final trainset node has both JSON and",
        "Markdown definitions with structured material and process specs.",
        "",
        f"- Family: `{design.family.value}`",
        f"- Candidate: `{design.candidate.id}`",
        f"- Product item definitions: `{len(design.product_items)}`",
        f"- Assembly definitions: `{len(design.assemblies)}`",
        "",
        "## Product items",
        "",
        "| ID | Layer | Route | Parent | Definition |",
        "|---|---|---|---|---|",
    ]
    for item in design.product_items:
        bucket = _definition_bucket_for_layer(item.layer)
        md_path = _path_from_id(root, bucket, item.id, ".md")
        lines.append(
            f"| `{item.id}` | {item.layer.value} | `{item.route.value}` | `{item.parent}` | "
            f"[md]({md_path.relative_to(root).as_posix()}) |"
        )
    lines.extend(
        [
            "",
            "## Assemblies",
            "",
            "| ID | Layer | Qty/trainset | Children | Definition |",
            "|---|---|---:|---|---|",
        ]
    )
    for node in design.assemblies:
        bucket = _definition_bucket_for_layer(node.layer)
        md_path = _path_from_id(root, bucket, node.id, ".md")
        children = "<br>".join(f"`{child}`" for child in node.children)
        lines.append(
            f"| `{node.id}` | {node.layer.value} | {node.quantity_per_trainset:g} | {children} | "
            f"[md]({md_path.relative_to(root).as_posix()}) |"
        )
    lines.append("")
    return "\n".join(lines)


def write_definition_pack(design: BuildableTrainsetDesign, root: Path) -> DefinitionPackPaths:
    root.mkdir(parents=True, exist_ok=True)
    for bucket in ("parts", "subassemblies", "assemblies", "trainsets"):
        (root / bucket).mkdir(parents=True, exist_ok=True)

    definition_files: list[Path] = []
    entries: list[dict[str, object]] = []
    items_by_id = {item.id: item for item in design.product_items}
    assemblies_by_id = {node.id: node for node in design.assemblies}

    for item in design.product_items:
        bucket = _definition_bucket_for_layer(item.layer)
        json_path = _path_from_id(root, bucket, item.id, ".json")
        md_path = _path_from_id(root, bucket, item.id, ".md")
        json_path.write_text(json.dumps(_item_payload(item), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(render_product_item_definition(item), encoding="utf-8")
        definition_files.extend([json_path, md_path])
        entries.append(
            {
                "id": item.id,
                "definition_type": "product-item",
                "layer": item.layer.value,
                "route": item.route.value,
                "json": json_path.relative_to(root).as_posix(),
                "markdown": md_path.relative_to(root).as_posix(),
            }
        )

    for node in design.assemblies:
        bucket = _definition_bucket_for_layer(node.layer)
        json_path = _path_from_id(root, bucket, node.id, ".json")
        md_path = _path_from_id(root, bucket, node.id, ".md")
        json_path.write_text(
            json.dumps(_assembly_payload(node, items_by_id, assemblies_by_id), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(render_assembly_definition(node, items_by_id, assemblies_by_id), encoding="utf-8")
        definition_files.extend([json_path, md_path])
        entries.append(
            {
                "id": node.id,
                "definition_type": "assembly-node",
                "layer": node.layer.value,
                "json": json_path.relative_to(root).as_posix(),
                "markdown": md_path.relative_to(root).as_posix(),
            }
        )

    index_json = root / "index.json"
    index_md = root / "index.md"
    index_payload = {
        "family": design.family.value,
        "candidate": design.candidate.id,
        "product_item_count": len(design.product_items),
        "assembly_count": len(design.assemblies),
        "definition_count": len(entries),
        "entries": entries,
    }
    index_json.write_text(json.dumps(index_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    index_md.write_text(render_definition_index(design, root), encoding="utf-8")
    definition_files.extend([index_json, index_md])
    return DefinitionPackPaths(index_json=index_json, index_md=index_md, definition_files=tuple(definition_files))


def _tooling_prefix_for_id(definition_id: str) -> str:
    prefix = "-".join(definition_id.split("-")[:2])
    return prefix or "LM3"


def _qa_tool_for_text(text: str) -> str:
    lower = text.lower()
    if "gauge" in lower or "datum" in lower or "survey" in lower:
        return "GAUGE"
    if "ndt" in lower or "weld" in lower:
        return "NDT"
    if "isolation" in lower or "hvil" in lower or "continuity" in lower:
        return "ELEC-TEST"
    if "pressure" in lower or "drain" in lower or "water" in lower or "leak" in lower:
        return "LEAK-TEST"
    if "torque" in lower or "fastener" in lower:
        return "TORQUE"
    return "QA"


def _is_composite_make_item(item: ProductItem) -> bool:
    if item.route is not Route.MAKE:
        return False
    if item.id == "LM3-BDY-P130":
        return True
    if item.id.startswith("LM3-CWL-P"):
        return True
    return item.id in {"LM3-INT-P020", "LM3-INT-P030", "LM3-INT-P040", "LM3-INT-P050"}


def _signoff_blocks() -> list[dict[str, str]]:
    return [
        {"role": "operator", "name": "", "date": "", "signature": "", "status": "blank"},
        {"role": "cell lead", "name": "", "date": "", "signature": "", "status": "blank"},
        {"role": "quality inspector", "name": "", "date": "", "signature": "", "status": "blank"},
        {"role": "manufacturing engineer", "name": "", "date": "", "signature": "", "status": "blank"},
    ]


def _revision_approvals(definition_id: str) -> list[dict[str, str]]:
    return [
        {
            "role": "manufacturing engineering",
            "approval_id": f"APP-{definition_id}-MFG",
            "name": "",
            "date": "",
            "signature": "",
            "status": "pending",
        },
        {
            "role": "quality",
            "approval_id": f"APP-{definition_id}-QA",
            "name": "",
            "date": "",
            "signature": "",
            "status": "pending",
        },
        {
            "role": "design authority",
            "approval_id": f"APP-{definition_id}-DA",
            "name": "",
            "date": "",
            "signature": "",
            "status": "pending",
        },
    ]


def _operation(
    sequence: int,
    title: str,
    work_center: str,
    labor_hours: float,
    tooling: list[str],
    qa_gate: str,
    signoff_role: str = "operator",
) -> dict[str, object]:
    return {
        "sequence": sequence,
        "title": title,
        "work_center": work_center,
        "labor_hours": round(labor_hours, 2),
        "tooling_ids": tooling,
        "qa_gate": qa_gate,
        "signoff_role": signoff_role,
    }


def _item_operations(item: ProductItem) -> list[dict[str, object]]:
    prefix = _tooling_prefix_for_id(item.id)
    operations = [
        _operation(
            10,
            "release traveler, revision, material/certificate pack, and parent interface",
            "production control",
            0.35,
            [f"TRV-{item.id}", f"DOC-{item.parent}"],
            "traveler rev and parent assembly match released manifest",
            "cell lead",
        )
    ]
    if item.route is Route.MAKE:
        if _is_composite_make_item(item):
            operations.extend(
                [
                    _operation(
                        20,
                        "inspect mould and trim fixture, release material batch, and apply release system",
                        "composite moulding cell",
                        0.65,
                        [f"MOULD-{item.id}", f"TRIM-GAUGE-{item.id}"],
                        "mould release record and material shelf-life accepted",
                    ),
                    _operation(
                        30,
                        "lay up glass-fibre reinforcement, core, solid lands, and insert bosses in mould",
                        "composite moulding cell",
                        1.35,
                        [f"MOULD-{item.id}", f"PLYBOOK-{item.id}"],
                        "ply/core/insert checklist matches released laminate schedule",
                    ),
                    _operation(
                        40,
                        "infuse or wet-lay laminate, control cure, demould, and retain witness coupons",
                        "controlled cure area",
                        1.1,
                        [f"CURE-{item.id}", f"COUPON-{item.id}"],
                        "cure record, demould inspection, and coupon trace are complete",
                    ),
                    _operation(
                        50,
                        "CNC trim and drill to datum, seal cut edges, and mark serial/revision",
                        "trim and drill cell",
                        0.85,
                        [f"TRIM-GAUGE-{item.id}", f"GAUGE-{item.id}-DATUM"],
                        "trim, drill, and sealed-edge records match the released variant",
                    ),
                    _operation(
                        60,
                        "fit inserts, clips, retainers, gaskets, or captive fasteners and dry-fit to parent fixture",
                        "module fit-up cell",
                        0.8,
                        [f"FIX-{item.parent}", f"TORQUE-{item.id}", f"GAUGE-{item.id}"],
                        "fit-up evidence recorded before release to assembly",
                    ),
                ]
            )
        else:
            operations.extend(
                [
                    _operation(
                        20,
                        "cut, form, machine, or fabricate local hardware",
                        "fabrication cell",
                        1.8 if item.layer is Layer.FABRICATED_PART else 1.1,
                        [f"FIX-{prefix}-FAB", f"GAUGE-{item.id}-DATUM"],
                        "fabricated geometry matches datum/gauge requirements",
                    ),
                    _operation(
                        30,
                        "trial-fit to parent interface and record shim/adjustment pack",
                        "fit-up cell",
                        0.8,
                        [f"FIX-{item.parent}", f"TORQUE-{item.id}"],
                        "fit-up evidence recorded before release to assembly",
                    ),
                ]
            )
    else:
        operations.extend(
            [
                _operation(
                    20,
                    "receive supplier component and quarantine until evidence pack passes",
                    "receiving inspection",
                    0.45,
                    [f"RFQ-{item.id}", f"CERT-{item.id}"],
                    "supplier certificate/datasheet/revision accepted",
                    "quality inspector",
                ),
                _operation(
                    30,
                    "perform envelope, mounting, service-removal, and connector checks",
                    "incoming fit-check cell",
                    0.75,
                    [f"GAUGE-{item.id}-ENVELOPE", f"FIX-{item.parent}"],
                    "component fits without parent datum rework",
                ),
            ]
        )
    sequence = 70 if _is_composite_make_item(item) else 40
    for gate in item.acceptance:
        operations.append(
            _operation(
                sequence,
                f"verify acceptance gate: {gate}",
                "quality inspection",
                0.25,
                [f"{_qa_tool_for_text(gate)}-{item.id}"],
                gate,
                "quality inspector",
            )
        )
        sequence += 10
    operations.append(
        _operation(
            sequence,
            "final item release to parent assembly",
            "production control",
            0.25,
            [f"REL-{item.id}", f"KIT-{item.parent}"],
            "item is released, tagged, and staged for parent assembly",
            "cell lead",
        )
    )
    return operations


def _assembly_operations(
    node: AssemblyNode,
    items: dict[str, ProductItem],
    assemblies: dict[str, AssemblyNode],
) -> list[dict[str, object]]:
    operations = [
        _operation(
            10,
            "release traveler, fixture, child kit, and latest definition package",
            node.build_cell,
            0.45 + 0.08 * len(node.children),
            [f"TRV-{node.id}", f"FIX-{node.id}", f"KIT-{node.id}"],
            "all child definitions/revisions match the traveler index",
            "cell lead",
        )
    ]
    sequence = 20
    for step in _integration_steps(node, items, assemblies):
        child_id = str(step["child_id"])
        interface_classes = list(step["interface_classes"])
        join_classes = list(step["join_classes"])
        labor = (
            0.55
            + 0.18 * len(interface_classes)
            + 0.12 * len(join_classes)
            + 0.05 * len(list(step["verification"]))
        )
        operations.append(
            _operation(
                sequence,
                f"install and integrate {child_id}: {step['child_title']}",
                node.build_cell,
                labor,
                [f"FIX-{node.id}", f"GAUGE-{child_id}", f"TORQUE-{child_id}"],
                f"placement zone and joint controls accepted: {step['placement_zone']}",
            )
        )
        sequence += 10
    for hold_point in node.hold_points:
        operations.append(
            _operation(
                sequence,
                f"hold point: {hold_point}",
                "quality inspection",
                0.35,
                [f"{_qa_tool_for_text(hold_point)}-{node.id}"],
                hold_point,
                "quality inspector",
            )
        )
        sequence += 10
    operations.append(
        _operation(
            sequence,
            "close traveler, attach nonconformance/deviation log, and release to next parent",
            "production control",
            0.3,
            [f"REL-{node.id}", f"NCR-{node.id}"],
            "all operation and QA signoffs are complete",
            "manufacturing engineer",
        )
    )
    return operations


def _traveler_payload_for_item(item: ProductItem) -> dict[str, object]:
    operations = _item_operations(item)
    material_spec = _item_material_spec(item)
    process_spec = _item_process_spec(item)
    return {
        "id": item.id,
        "title": item.title,
        "traveler_type": "product-item",
        "document_revision": "A-DRAFT",
        "release_status": "unsigned-template",
        "parent": item.parent,
        "route": item.route.value,
        "quantity_per_trainset": item.quantity_per_trainset,
        "unit": item.unit,
        "bom_line_ids": list(bom_line_ids_for_engineering_id(item.id)),
        "estimated_labor_hours": round(sum(float(op["labor_hours"]) for op in operations), 2),
        "material_spec": _spec_payload(material_spec),
        "process_spec": _spec_payload(process_spec),
        "revision_approvals": _revision_approvals(item.id),
        "operations": operations,
        "signoff_blocks": _signoff_blocks(),
    }


def _traveler_payload_for_assembly(
    node: AssemblyNode,
    items: dict[str, ProductItem],
    assemblies: dict[str, AssemblyNode],
) -> dict[str, object]:
    operations = _assembly_operations(node, items, assemblies)
    material_spec = _assembly_material_spec(node, items, assemblies)
    process_spec = _assembly_process_spec(node)
    return {
        "id": node.id,
        "title": node.title,
        "traveler_type": "assembly-node",
        "document_revision": "A-DRAFT",
        "release_status": "unsigned-template",
        "layer": node.layer.value,
        "quantity_per_trainset": node.quantity_per_trainset,
        "build_cell": node.build_cell,
        "children": list(node.children),
        "bom_line_ids": list(bom_line_ids_for_engineering_id(node.id)),
        "estimated_labor_hours": round(sum(float(op["labor_hours"]) for op in operations), 2),
        "material_spec": _spec_payload(material_spec),
        "process_spec": _spec_payload(process_spec),
        "revision_approvals": _revision_approvals(node.id),
        "operations": operations,
        "signoff_blocks": _signoff_blocks(),
    }


def render_shop_traveler(payload: dict[str, object]) -> str:
    operations = list(payload["operations"])  # type: ignore[index]
    approvals = list(payload["revision_approvals"])  # type: ignore[index]
    signoffs = list(payload["signoff_blocks"])  # type: ignore[index]
    material_spec = dict(payload["material_spec"])  # type: ignore[arg-type]
    process_spec = dict(payload["process_spec"])  # type: ignore[arg-type]
    lines = [
        f"# Shop traveler — {payload['id']} — {payload['title']}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Traveler type | `{payload['traveler_type']}` |",
        f"| Document revision | `{payload['document_revision']}` |",
        f"| Release status | `{payload['release_status']}` |",
        f"| Estimated labor | {payload['estimated_labor_hours']} h |",
    ]
    if "build_cell" in payload:
        lines.append(f"| Build cell | {payload['build_cell']} |")
    if "route" in payload:
        lines.append(f"| Route | `{payload['route']}` |")
    bom_line_ids = list(payload.get("bom_line_ids", []))
    lines.append(
        "| Procurement BOM lines | "
        + (", ".join(f"`{line_id}`" for line_id in bom_line_ids) if bom_line_ids else "None directly assigned")
        + " |"
    )
    lines.extend(
        [
            "",
            "## Material specification",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| Material family | {material_spec['material_family']} |",
            f"| Grade / part class | {material_spec['grade_or_part_class']} |",
            f"| Governing standard | {material_spec['governing_standard']} |",
            f"| Form factor | {material_spec['form_factor']} |",
            f"| Nominal section | {material_spec['nominal_section']} |",
            f"| Finish / protection | {material_spec['finish_or_protection']} |",
            f"| Traceability | {material_spec['traceability']} |",
            "",
            "Evidence required:",
            "",
        ]
    )
    lines.extend(f"- {evidence}" for evidence in material_spec["evidence_required"])  # type: ignore[index]
    lines.extend(
        [
            "",
            "## Process specification",
            "",
            f"- Primary processes: {', '.join(process_spec['primary_processes'])}",  # type: ignore[arg-type]
            f"- Joining methods: {', '.join(process_spec['joining_methods'])}",  # type: ignore[arg-type]
            f"- Special process controls: {', '.join(process_spec['special_process_controls'])}",  # type: ignore[arg-type]
            f"- Inspection methods: {', '.join(process_spec['inspection_methods'])}",  # type: ignore[arg-type]
            f"- Tooling basis: {process_spec['tooling_basis']}",
            f"- Release level: {process_spec['release_level']}",
            "",
            "",
            "## Revision approval block",
            "",
            "| Role | Approval ID | Name | Date | Signature | Status |",
            "|---|---|---|---|---|---|",
        ]
    )
    for approval in approvals:
        lines.append(
            f"| {approval['role']} | `{approval['approval_id']}` |  |  |  | `{approval['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Operation router",
            "",
            "| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |",
            "|---:|---|---|---:|---|---|---|",
        ]
    )
    for op in operations:
        tooling = "<br>".join(f"`{tool}`" for tool in op["tooling_ids"])  # type: ignore[index]
        lines.append(
            f"| {op['sequence']} | {op['title']} | {op['work_center']} | {op['labor_hours']} | "
            f"{tooling} | {op['qa_gate']} | {op['signoff_role']} |"
        )
    lines.extend(
        [
            "",
            "## Operator / inspection signoff block",
            "",
            "| Role | Name | Date | Signature | Status |",
            "|---|---|---|---|---|",
        ]
    )
    for signoff in signoffs:
        lines.append(f"| {signoff['role']} |  |  |  | `{signoff['status']}` |")
    lines.extend(
        [
            "",
            "## Nonconformance / deviation log",
            "",
            "| NCR / deviation ID | Operation seq | Disposition | Approver | Closure date |",
            "|---|---:|---|---|---|",
            "|  |  |  |  |  |",
            "",
        ]
    )
    return "\n".join(lines)


def render_shop_traveler_index(design: BuildableTrainsetDesign, root: Path) -> str:
    lines = [
        "# Buildable trainset shop traveler pack",
        "",
        "Generated by `scripts/buildable-trainset.sh`. These are signable",
        "manufacturing traveler templates with labor estimates, tooling IDs,",
        "structured material/process specs, revision approval blocks, operation",
        "routers, QA gates, and operator / inspector signoff blocks. They are",
        "unsigned until a real build cell uses and approves them.",
        "",
        f"- Family: `{design.family.value}`",
        f"- Candidate: `{design.candidate.id}`",
        f"- Traveler templates: `{len(design.product_items) + len(design.assemblies)}`",
        "",
        "| ID | Type | Route/layer | Traveler |",
        "|---|---|---|---|",
    ]
    for item in design.product_items:
        bucket = _definition_bucket_for_layer(item.layer)
        md_path = _path_from_id(root, bucket, item.id, ".md")
        lines.append(f"| `{item.id}` | product item | `{item.route.value}` | [md]({md_path.relative_to(root).as_posix()}) |")
    for node in design.assemblies:
        bucket = _definition_bucket_for_layer(node.layer)
        md_path = _path_from_id(root, bucket, node.id, ".md")
        lines.append(f"| `{node.id}` | assembly node | `{node.layer.value}` | [md]({md_path.relative_to(root).as_posix()}) |")
    lines.append("")
    return "\n".join(lines)


def write_shop_traveler_pack(design: BuildableTrainsetDesign, root: Path) -> ShopTravelerPackPaths:
    root.mkdir(parents=True, exist_ok=True)
    for bucket in ("parts", "subassemblies", "assemblies", "trainsets"):
        (root / bucket).mkdir(parents=True, exist_ok=True)

    traveler_files: list[Path] = []
    entries: list[dict[str, object]] = []
    items_by_id = {item.id: item for item in design.product_items}
    assemblies_by_id = {node.id: node for node in design.assemblies}

    for item in design.product_items:
        bucket = _definition_bucket_for_layer(item.layer)
        json_path = _path_from_id(root, bucket, item.id, ".json")
        md_path = _path_from_id(root, bucket, item.id, ".md")
        payload = _traveler_payload_for_item(item)
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(render_shop_traveler(payload), encoding="utf-8")
        traveler_files.extend([json_path, md_path])
        entries.append(
            {
                "id": item.id,
                "traveler_type": "product-item",
                "json": json_path.relative_to(root).as_posix(),
                "markdown": md_path.relative_to(root).as_posix(),
            }
        )

    for node in design.assemblies:
        bucket = _definition_bucket_for_layer(node.layer)
        json_path = _path_from_id(root, bucket, node.id, ".json")
        md_path = _path_from_id(root, bucket, node.id, ".md")
        payload = _traveler_payload_for_assembly(node, items_by_id, assemblies_by_id)
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(render_shop_traveler(payload), encoding="utf-8")
        traveler_files.extend([json_path, md_path])
        entries.append(
            {
                "id": node.id,
                "traveler_type": "assembly-node",
                "json": json_path.relative_to(root).as_posix(),
                "markdown": md_path.relative_to(root).as_posix(),
            }
        )

    index_json = root / "index.json"
    index_md = root / "index.md"
    index_payload = {
        "family": design.family.value,
        "candidate": design.candidate.id,
        "traveler_count": len(entries),
        "entries": entries,
    }
    index_json.write_text(json.dumps(index_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    index_md.write_text(render_shop_traveler_index(design, root), encoding="utf-8")
    traveler_files.extend([index_json, index_md])
    return ShopTravelerPackPaths(index_json=index_json, index_md=index_md, traveler_files=tuple(traveler_files))


def mass_budget_payload(design: BuildableTrainsetDesign) -> dict[str, object]:
    modeled_subtotal = round(sum(design.candidate.mass_breakdown_kg.values()))
    if modeled_subtotal != PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG:
        raise ValueError(
            "promoted optimizer mass subtotal does not match the current winning candidate: "
            f"{PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG} kg != {modeled_subtotal} kg"
        )
    return {
        "document_revision": "A-DRAFT",
        "release_status": "planning-control",
        "candidate": design.candidate.id,
        "modeled_categories_kg": design.candidate.mass_breakdown_kg,
        "modeled_subtotal_kg": PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG,
        "engineering_reserve_kg": PROMOTED_ENGINEERING_MASS_RESERVE_KG,
        "controlled_planning_tare_kg": PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG,
        "reserve_percent_of_modeled_subtotal": round(
            100.0 * PROMOTED_ENGINEERING_MASS_RESERVE_KG / PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG,
            2,
        ),
        "closure_rule": (
            "Replace category estimates with weighed, supplier-frozen, or CAD-derived masses; "
            "transfer consumed reserve to the affected category; do not reduce controlled tare "
            "until the signed trainset weigh establishes the as-built value."
        ),
    }


def render_mass_budget(design: BuildableTrainsetDesign) -> str:
    payload = mass_budget_payload(design)
    categories = dict(payload["modeled_categories_kg"])  # type: ignore[arg-type]
    lines = [
        "# LM3 controlled mass budget",
        "",
        "Generated from the promoted design candidate and baseline constants. This",
        "record resolves the earlier ambiguity between the optimizer subtotal and the",
        "planning tare; it is not a substitute for drawing-level or as-built weighing.",
        "",
        f"- Candidate: `{payload['candidate']}`",
        f"- Document revision: `{payload['document_revision']}`",
        f"- Release status: `{payload['release_status']}`",
        "",
        "| Category | Modeled mass (kg) |",
        "|---|---:|",
    ]
    for category, mass_kg in categories.items():
        lines.append(f"| {category} | {float(mass_kg):,.2f} |")
    lines.extend(
        [
            f"| **Modeled subtotal** | **{int(payload['modeled_subtotal_kg']):,}** |",
            f"| Engineering reserve ({payload['reserve_percent_of_modeled_subtotal']} %) | "
            f"{int(payload['engineering_reserve_kg']):,} |",
            f"| **Controlled planning tare** | **{int(payload['controlled_planning_tare_kg']):,}** |",
            "",
            "## Closure rule",
            "",
            str(payload["closure_rule"]),
            "",
            "The reserve currently covers unclosed wiring, fluids, fasteners, coatings,",
            "production tolerances, and supplier mass growth. Every released drawing or",
            "supplier selection must update its category without hiding growth in another",
            "line. Final closure requires individual car weights and a complete trainset",
            "weight recorded by serial number.",
            "",
        ]
    )
    return "\n".join(lines)


def joint_control_rows(design: BuildableTrainsetDesign) -> list[dict[str, object]]:
    items = {item.id: item for item in design.product_items}
    assemblies = {node.id: node for node in design.assemblies}
    rows: list[dict[str, object]] = []
    for node in design.assemblies:
        for step in _integration_steps(node, items, assemblies):
            rows.append(
                {
                    "joint_id": f"J-{node.id}-{int(step['sequence']):02d}",
                    "parent_id": node.id,
                    "child_id": step["child_id"],
                    "child_title": step["child_title"],
                    "join_classes": step["join_classes"],
                    "interface_classes": step["interface_classes"],
                    "torque_authority": step["torque_authority"],
                    "release_status": step["joint_release_status"],
                    "verification": step["verification"],
                }
            )
    return rows


def render_joint_control_schedule(design: BuildableTrainsetDesign) -> str:
    rows = joint_control_rows(design)
    lines = [
        "# LM3 joint and fastener control schedule",
        "",
        "Generated from every parent/child integration step in the trainset product",
        "tree. It makes joining method and torque authority machine-readable. Numeric",
        "torques are intentionally prohibited until the named supplier instruction or",
        "joint calculation is accepted; nominal bolt diameter alone is not a safe",
        "preload specification.",
        "",
        f"Controlled integration joints: **{len(rows)}**.",
        "",
        "| Joint ID | Parent → child | Join classes | Torque authority | Release status |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        join_classes = "<br>".join(f"`{value}`" for value in row["join_classes"])  # type: ignore[union-attr]
        lines.append(
            f"| `{row['joint_id']}` | `{row['parent_id']}` → `{row['child_id']}` | "
            f"{join_classes} | {row['torque_authority']} | `{row['release_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Release use",
            "",
            "A traveler may reference a joint ID, but no fastener is released for final",
            "torque until its status is closed by the authority named above. The released",
            "record must also state fastener grade, coating/lubrication condition, locking",
            "method, calibrated tool range, witness marking, and re-torque rule. Supplier",
            "wheelset, bearing, brake, coupler, door, HVAC, battery, traction, and gangway",
            "values remain supplier-controlled and must not be replaced with generic tables.",
            "",
        ]
    )
    return "\n".join(lines)


def critical_path_tasks() -> tuple[CriticalPathTask, ...]:
    """Rough first-train build network with parallel fabrication assumptions.

    The durations are planning values for one three-car LM3 trainset after
    design release and material availability. They intentionally model a lean
    pilot plant: most parts are fabricated off the final assembly track, and
    only complete, released subassemblies enter the long final bay.
    """

    return (
        CriticalPathTask(
            "CP-010",
            "release traveler pack, work orders, QA gates, and material lots",
            "program release",
            2.0,
            72.0,
            "project controls / production planning",
            "planning desk plus controlled document store",
            (),
            "Freeze the build sequence once so steel, composite, bogie, HV, and interior cells can start together.",
        ),
        CriticalPathTask(
            "CP-020",
            "cut, form, drill, and kit structural steel chassis/body parts",
            "parts fabrication",
            3.0,
            288.0,
            "steel prep cell",
            "one saw/laser/plasma area, one press brake, pallet lanes for three car kits",
            ("CP-010",),
            "Batch all three car kits; do not occupy car-length fixtures until parts are deburred, marked, and inspected.",
        ),
        CriticalPathTask(
            "CP-030",
            "weld three underframe datum weldments",
            "subassembly",
            4.0,
            384.0,
            "weld and fixture cell",
            "two 18 m rotating underframe fixtures plus local bolster/coupler subfixtures",
            ("CP-020",),
            "Two fixtures keep the third underframe from extending the train-level path while avoiding three full weld bays.",
        ),
        CriticalPathTask(
            "CP-040",
            "add side/roof spaceframes, floors, portals, roof rails, and chassis interfaces",
            "subassembly",
            4.0,
            420.0,
            "weld and fixture cell",
            "two side/roof frame fixtures and one transfer stand",
            ("CP-030",),
            "Run side-frame and floor close-up as a rolling wave from released underframes.",
        ),
        CriticalPathTask(
            "CP-050",
            "assemble powered/trailer bogies, wheelsets, suspension, brake, and bogie harness kits",
            "subassembly",
            8.0,
            520.0,
            "bogie assembly cell",
            "three bogie stands, one wheelset lane, and one brake/sensor bench",
            ("CP-020",),
            "Bogie work is fully parallel to carbody welding; final track waits only for released bogies.",
        ),
        CriticalPathTask(
            "CP-060",
            "mould, cure, demould, trim, drill, and kit 144 GFRP exterior modules",
            "parts fabrication",
            5.0,
            420.0,
            "composite moulding and trim cell",
            "four short module moulds, one trim table, one master-frame dry-fit stand",
            ("CP-010",),
            "Short moulds and CNC trim keep the composite work off the final train bay.",
        ),
        CriticalPathTask(
            "CP-065",
            "prebuild internal furnishings and cabin trim kits",
            "parts fabrication",
            5.0,
            360.0,
            "interior bench / supplier receiving",
            "trim bench, seat/grab-rail rack, electrical label bench, quarantine shelves",
            ("CP-010",),
            "Pre-kit seats, grab rails, floor finish, ceiling/sidewall liners, PIS, CCTV, lighting, and labels by car/door zone.",
        ),
        CriticalPathTask(
            "CP-070",
            "blast, prime, topcoat, cavity-wax, and release painted carbody frames",
            "subassembly",
            2.0,
            192.0,
            "paint and corrosion cell",
            "one car-length paint bay plus flash-off/inspection lane",
            ("CP-040",),
            "Paint only dimensionally accepted steel frames; clip rails and drain lands are masked and gauged before release.",
        ),
        CriticalPathTask(
            "CP-080",
            "install clip-on GFRP side/roof modules and complete water/rattle pre-test",
            "assembly",
            1.0,
            96.0,
            "clip-on body cell",
            "three parallel car positions for one shift",
            ("CP-060", "CP-070"),
            "Use the one-shift six-crew route; no production adhesive cure blocks the path.",
        ),
        CriticalPathTask(
            "CP-090",
            "install doors, windows, roof HVAC/PV hardware, and exterior service details",
            "assembly",
            3.0,
            360.0,
            "final assembly track with glazing/roof access",
            "one 55 m final track, two mobile roof platforms, glazing stands",
            ("CP-080",),
            "Door/window/HVAC crews work car-by-car while electrical rough-in starts in released zones.",
        ),
        CriticalPathTask(
            "CP-100",
            "install HV battery, traction, LV/control, safety loops, coolant, and fire interfaces",
            "assembly",
            4.0,
            480.0,
            "final assembly electrical/HV cell",
            "same 55 m final track with lockout boundary and two under-seat service carts",
            ("CP-080",),
            "HV/LV/coolant crews work in parallel with roof and door installation but release independently.",
        ),
        CriticalPathTask(
            "CP-110",
            "install internal furnishings, flooring, liners, seats, grab rails, PIS, CCTV, lighting, and signage",
            "assembly",
            3.0,
            420.0,
            "final assembly interior fit-out cell",
            "same 55 m final track, three car interiors worked as zones",
            ("CP-065", "CP-090"),
            "Use pre-kitted interiors; keep floor/seat/liner installation behind tested doors/windows to avoid rework from leaks.",
        ),
        CriticalPathTask(
            "CP-120",
            "marry bogies to carbodies and close brake/ride-height static checks",
            "assembly",
            2.0,
            240.0,
            "final assembly bogie marriage station",
            "same 55 m final track with jacks or shallow pit and bogie drop/lift equipment",
            ("CP-050", "CP-080"),
            "Released bogies enter late; this keeps wheelset/brake work out of the carbody assembly bay.",
        ),
        CriticalPathTask(
            "CP-130",
            "install articulation, gangways, end cowls, couplers, sensor packs, and trainlines",
            "final trainset assembly",
            3.0,
            360.0,
            "final assembly track",
            "same 55 m final track plus end-cowl access stands",
            ("CP-110", "CP-120"),
            "Close car-to-car mechanical interfaces after interiors and bogie marriage are stable.",
        ),
        CriticalPathTask(
            "CP-140",
            "static commissioning, insulation, door/HVAC/brake tests, snag closeout, and QA release",
            "commissioning",
            4.0,
            480.0,
            "final assembly / static test cell",
            "same 55 m final track with shore power and station-charge simulator",
            ("CP-100", "CP-130"),
            "Static testing is the first convergence of HV, brakes, doors, HVAC, onboard controls, and passenger systems.",
        ),
        CriticalPathTask(
            "CP-150",
            "dynamic commissioning and trial-running release",
            "commissioning",
            6.0,
            432.0,
            "test track / depot",
            "short test track, charging interface, fault desk",
            ("CP-140",),
            "Do not move unresolved static defects onto the test track; protect dynamic-test access as the last bottleneck.",
        ),
    )


def _scheduled_critical_path_tasks() -> list[dict[str, object]]:
    tasks = critical_path_tasks()
    by_id = {task.id: task for task in tasks}
    early_start: dict[str, float] = {}
    early_finish: dict[str, float] = {}
    for task in tasks:
        missing = set(task.predecessors) - set(by_id)
        if missing:
            raise ValueError(f"{task.id} references missing predecessors: {sorted(missing)}")
        early_start[task.id] = max((early_finish[pred] for pred in task.predecessors), default=0.0)
        early_finish[task.id] = early_start[task.id] + task.duration_days

    project_duration = max(early_finish.values())
    successors: dict[str, list[str]] = {task.id: [] for task in tasks}
    for task in tasks:
        for predecessor in task.predecessors:
            successors[predecessor].append(task.id)

    late_finish: dict[str, float] = {}
    late_start: dict[str, float] = {}
    for task in reversed(tasks):
        late_finish[task.id] = min((late_start[succ] for succ in successors[task.id]), default=project_duration)
        late_start[task.id] = late_finish[task.id] - task.duration_days

    scheduled: list[dict[str, object]] = []
    for task in tasks:
        float_days = round(late_start[task.id] - early_start[task.id], 2)
        crew_equivalent = task.labor_hours / (task.duration_days * 8.0)
        scheduled.append(
            {
                "id": task.id,
                "title": task.title,
                "level": task.level,
                "duration_days": task.duration_days,
                "labor_hours": task.labor_hours,
                "crew_equivalent": round(crew_equivalent, 1),
                "work_center": task.work_center,
                "space_requirement": task.space_requirement,
                "predecessors": list(task.predecessors),
                "early_start_day": round(early_start[task.id], 2),
                "early_finish_day": round(early_finish[task.id], 2),
                "late_start_day": round(late_start[task.id], 2),
                "late_finish_day": round(late_finish[task.id], 2),
                "total_float_days": float_days,
                "critical": abs(float_days) < 1e-9,
                "parallelisation_notes": task.parallelisation_notes,
            }
        )
    return scheduled


def critical_path_payload(design: BuildableTrainsetDesign) -> dict[str, object]:
    tasks = _scheduled_critical_path_tasks()
    labor_by_work_center: dict[str, float] = {}
    for task in tasks:
        work_center = str(task["work_center"])
        labor_by_work_center[work_center] = labor_by_work_center.get(work_center, 0.0) + float(task["labor_hours"])
    critical_ids = [str(task["id"]) for task in tasks if task["critical"]]
    return {
        "document_revision": "A-DRAFT",
        "release_status": "rough-order planning; not a shop-approved baseline",
        "family": design.family.value,
        "candidate": design.candidate.id,
        "planning_basis": (
            "one first-article three-car LM3 trainset after design release/material availability; "
            "one long final assembly track; off-line steel, composite, bogie, and interior benches run in parallel"
        ),
        "project_duration_days": max(float(task["early_finish_day"]) for task in tasks),
        "total_labor_hours": round(sum(float(task["labor_hours"]) for task in tasks), 1),
        "critical_path": critical_ids,
        "labor_by_work_center": {key: round(value, 1) for key, value in sorted(labor_by_work_center.items())},
        "minimum_space_model": {
            "long_train_bays": 1,
            "carbody_weld_fixtures": 2,
            "underframe_rotating_fixtures": 2,
            "paint_bays": 1,
            "bogie_stands": 3,
            "short_gfrp_moulds": 4,
            "interior_trim_benches": 1,
            "principle": "keep parts and kits off the 55 m final track until they are accepted subassemblies",
        },
        "tasks": tasks,
    }


def render_critical_path(design: BuildableTrainsetDesign) -> str:
    payload = critical_path_payload(design)
    tasks = list(payload["tasks"])  # type: ignore[index]
    critical = " -> ".join(f"`{task_id}`" for task_id in payload["critical_path"])  # type: ignore[index]
    lines = [
        "# LM3 fabrication and final-assembly critical path",
        "",
        "Generated by `scripts/buildable-trainset.sh`. This is a rough-order",
        "first-train manufacturing plan for parts, subassemblies, final train",
        "assembly, internal furnishings, and commissioning. It is intended for",
        "layout and takt planning; it is not a released shop baseline.",
        "",
        f"- Family: `{payload['family']}`",
        f"- Candidate: `{payload['candidate']}`",
        f"- Planning basis: {payload['planning_basis']}",
        f"- Rough elapsed duration: **{payload['project_duration_days']:.1f} working days**",
        f"- Rough direct labour: **{payload['total_labor_hours']:,.0f} h**",
        f"- Critical path: {critical}",
        "",
        "## Critical-path table",
        "",
        "| ID | Task | Level | Work center | Pred | Duration d | Labour h | Crew eq | ES | EF | Float | Critical |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for task in tasks:
        predecessors = ", ".join(f"`{pred}`" for pred in task["predecessors"]) or "-"
        critical_flag = "yes" if task["critical"] else ""
        lines.append(
            f"| `{task['id']}` | {task['title']} | {task['level']} | {task['work_center']} | "
            f"{predecessors} | {task['duration_days']:.1f} | {task['labor_hours']:.0f} | "
            f"{task['crew_equivalent']:.1f} | {task['early_start_day']:.1f} | "
            f"{task['early_finish_day']:.1f} | {task['total_float_days']:.1f} | {critical_flag} |"
        )
    lines.extend(
        [
            "",
            "## Space and parallelism",
            "",
            "| Area | Minimum planning allowance | Why it is enough |",
            "|---|---|---|",
        ]
    )
    space = dict(payload["minimum_space_model"])  # type: ignore[arg-type]
    lines.extend(
        [
            f"| Long final assembly track | {space['long_train_bays']} x 55 m bay | Doors, roof systems, HV, interior, bogie marriage, articulation, and static test share one controlled train-length space. |",
            f"| Underframe fixtures | {space['underframe_rotating_fixtures']} fixtures | Two fixtures let three underframes move through without a third full-length weld bay. |",
            f"| Side/roof frame fixtures | {space['carbody_weld_fixtures']} fixtures | Keeps side/roof spaceframe work ahead of paint without holding the final track. |",
            f"| Paint bay | {space['paint_bays']} car-length bay | Frames enter only after dimensional acceptance, then leave for clip-on body installation. |",
            f"| Bogie stands | {space['bogie_stands']} stands | Bogies are assembled off-line while carbody welding is on the critical path. |",
            f"| Short GFRP moulds | {space['short_gfrp_moulds']} moulds | Repeated 1 m modules are produced without a full-car mould or final-bay cure hold. |",
            f"| Interior trim benches | {space['interior_trim_benches']} bench set | Furnishings are pre-kitted by car/door zone, then installed after leak-sensitive work closes. |",
            "",
            "Key minimisation rule: keep the 55 m final assembly track for accepted",
            "subassemblies only. Steel parts, GFRP modules, bogies, HVAC/PV kits,",
            "doors/windows, cabin liners, seats, grab rails, lighting, PIS, CCTV,",
            "flooring, signage, and labels are all prepared off-line and enter the",
            "train only as released kits.",
            "",
            "## Labour by work center",
            "",
            "| Work center | Labour h |",
            "|---|---:|",
        ]
    )
    for work_center, labor in dict(payload["labor_by_work_center"]).items():  # type: ignore[arg-type]
        lines.append(f"| {work_center} | {float(labor):,.0f} |")
    lines.extend(
        [
            "",
            "## Float use",
            "",
            "Composite module fabrication, bogie assembly, HV install, and interior",
            "pre-kitting have float in this rough network. Use that float to absorb",
            "first-article rework without expanding the final assembly track. Do not",
            "spend the float by letting incomplete kits enter the long bay; that trades",
            "cheap bench work for expensive train-length blockage.",
            "",
        ]
    )
    return "\n".join(lines)


def train_end_interface_payload(design: BuildableTrainsetDesign) -> dict[str, object]:
    """Return the configurable end-interface design basis.

    The reference LM3 trainset still selects panoramic glass at both outer
    ends.  This payload records the alternate open mid-connection so the
    same train module can be configured for a longer walk-through consist
    without inventing a second carbody design.
    """

    return {
        "document_revision": "A-DRAFT",
        "release_status": "interface-design-basis",
        "candidate": design.candidate.id,
        "principle": (
            "One train/car end structure is carried as a common configurable "
            "interface. Each end position is dressed with exactly one option: "
            "the closed panoramic glass end or the open mid-train connection."
        ),
        "common_interface": {
            "assembly_id": "LM3-EIF-SA650",
            "owned_item_ids": ["LM3-END-P060", "LM3-END-P061", "LM3-END-P062"],
            "interfaces": [
                "common S355 end carrier ring and option bolt grid",
                "replaceable EPDM sealing datum and drain lands",
                "shared underframe/coupler/articulation load-path datums",
                "protected HV/LV/trainline/coolant/HVAC service routes",
                "configuration record that locks each end as panoramic or open-mid",
            ],
            "manufacturing_route": [
                "jig-weld and machine the common end carrier ring",
                "survey the common bolt grid and seal lands",
                "fit either panoramic closeout hardware or open-portal clamp/threshold hardware",
                "record selected end option before final trainset integration",
            ],
        },
        "options": [
            {
                "id": "panoramic-glass-front-end",
                "assembly_id": "LM3-END-SA700",
                "reference_quantity": 2,
                "use_case": "outer A and C ends of the reference three-car trainset",
                "uses": [
                    "LM3-END-P061 panoramic option shim/closeout kit",
                    "LM3-CWL-SA710 multi-part fiberglass cowl",
                    "LM3-EXT-P030 heated panoramic glass",
                    "LM3-END-P010 automatic coupler/crash absorber",
                    "LM3-END-P020 T-OBS sensor pack",
                ],
                "omits": [
                    "open passenger portal",
                    "train-to-train bellows and turntable",
                    "through-passenger threshold bridge",
                ],
                "acceptance": [
                    "panoramic option fit gauge",
                    "glass/cowl datum transfer",
                    "sensor calibration",
                    "coupler datum survey",
                    "water-ingress pre-test",
                ],
            },
            {
                "id": "mid-open-train-to-train-connection",
                "assembly_id": "LM3-TTART-SA850",
                "reference_quantity": 0,
                "use_case": (
                    "optional end treatment when two complete train modules are "
                    "semi-permanently married into one walk-through consist"
                ),
                "uses": [
                    "LM3-END-P062 open-portal clamp/threshold/drain kit",
                    "LM3-ART-P040 train-to-train articulation and gangway cassette",
                    "LM3-ART-P041 service-jumper blanking and transition kit",
                ],
                "omits": [
                    "panoramic glass",
                    "fiberglass nose cowl",
                    "nose-mounted T-OBS sensor pack at the joined end",
                ],
                "acceptance": [
                    "open-portal gauge",
                    "bellows clamp fit",
                    "threshold/turntable level check",
                    "train-to-train motion-envelope proof",
                    "trainline continuity",
                    "water ingress/drain test",
                ],
            },
        ],
        "selection_rule": (
            "Each end position must select one option only. A panoramic end may "
            "not carry the open-portal threshold hardware, and an open-mid end "
            "may not carry the panoramic cowl/glass/sensor stack."
        ),
        "assembly_rule": (
            "Keep the common end-interface survey before option fit-out. Install "
            "panoramic hardware during outer-end assembly, or install the open "
            "gangway cassette only after both train modules are on the final "
            "assembly track and aligned at the train-to-train joint."
        ),
    }


def render_train_end_interface(design: BuildableTrainsetDesign) -> str:
    payload = train_end_interface_payload(design)
    common = dict(payload["common_interface"])  # type: ignore[arg-type]
    options = list(payload["options"])  # type: ignore[index]
    lines = [
        "# LM3 configurable train-end interface",
        "",
        "Generated by `scripts/buildable-trainset.sh`. This design note records",
        "the single train end structure that can be dressed as either the normal",
        "panoramic glass front/end or a mid-train open connection for joining two",
        "train modules into a longer walk-through consist.",
        "",
        f"- Candidate: `{payload['candidate']}`",
        f"- Document revision: `{payload['document_revision']}`",
        f"- Release status: `{payload['release_status']}`",
        f"- Principle: {payload['principle']}",
        "",
        "## Common Interface",
        "",
        f"- Assembly: `{common['assembly_id']}`",
        f"- Owned items: {', '.join(f'`{item_id}`' for item_id in common['owned_item_ids'])}",
        "",
        "Interfaces:",
        "",
    ]
    lines.extend(f"- {item}" for item in common["interfaces"])  # type: ignore[index]
    lines.extend(["", "Manufacturing route:", ""])
    lines.extend(f"- {item}" for item in common["manufacturing_route"])  # type: ignore[index]
    lines.extend(
        [
            "",
            "## Selectable End Options",
            "",
            "| Option | Assembly | Ref qty | Use case | Uses | Omits | Acceptance |",
            "|---|---|---:|---|---|---|---|",
        ]
    )
    for option in options:
        opt = dict(option)
        uses = "<br>".join(opt["uses"])  # type: ignore[index]
        omits = "<br>".join(opt["omits"])  # type: ignore[index]
        acceptance = "<br>".join(opt["acceptance"])  # type: ignore[index]
        lines.append(
            f"| `{opt['id']}` | `{opt['assembly_id']}` | {opt['reference_quantity']} | "
            f"{opt['use_case']} | {uses} | {omits} | {acceptance} |"
        )
    lines.extend(
        [
            "",
            "## Selection And Assembly Rules",
            "",
            f"- {payload['selection_rule']}",
            f"- {payload['assembly_rule']}",
            "",
        ]
    )
    return "\n".join(lines)


def full_set_3train_payload(design: BuildableTrainsetDesign) -> dict[str, object]:
    """Return the worked example for three LM3 train modules as one set."""

    module_length_m = 3 * PROMOTED_LIGHT_METRO_CAR_LENGTH_M
    full_set_length_m = 3 * module_length_m
    planning_tare_t = 3 * PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG / 1000.0
    modeled_subtotal_t = 3 * PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG / 1000.0
    reserve_t = 3 * PROMOTED_ENGINEERING_MASS_RESERVE_KG / 1000.0
    return {
        "document_revision": "A-DRAFT",
        "release_status": "worked-example-not-release-baseline",
        "candidate": design.candidate.id,
        "assembly_id": "LM3-FULLSET-A300",
        "title": "three LM3 train modules joined as one walk-through full set",
        "configuration": {
            "train_modules": 3,
            "cars_total": 9,
            "outer_panoramic_ends": 2,
            "train_to_train_open_joints": 2,
            "inter_car_joints_inside_modules": 6,
            "module_length_m": round(module_length_m, 1),
            "full_set_length_m": round(full_set_length_m, 1),
            "controlled_planning_tare_t": round(planning_tare_t, 3),
            "modeled_subtotal_t": round(modeled_subtotal_t, 3),
            "engineering_reserve_t": round(reserve_t, 3),
        },
        "freecad_designs": [
            {
                "artifact": "mechanical-py/catalog/freecad/trainset-light-metro-3car-fullset-3train.FCStd",
                "source": "mechanical-py/src/osr_mech/freecad_trainset.py",
                "command": "scripts/freecad_trainset.sh --family light-metro-3car-fullset-3train",
                "purpose": "Full 9-car / 3-train review assembly with two open train-to-train joints.",
            },
            {
                "artifact": "mechanical-py/catalog/freecad/fea-screening-models.FCStd",
                "source": "mechanical-py/src/osr_mech/freecad_fea.py",
                "command": "scripts/freecad_fea.sh",
                "purpose": "Beam-model FEM visual document including long-consist and train-to-train joint screening cases.",
            },
        ],
        "principal_parts_and_subassemblies": [
            ("LM3-TRAINSET-A000", 3, "three complete LM3 train modules"),
            ("LM3-EIF-SA650", 6, "common configurable end interfaces, two per module"),
            ("LM3-END-SA700", 2, "panoramic glass outer-end assemblies at the full-set ends only"),
            ("LM3-TTART-SA850", 2, "open train-to-train articulation/gangway assemblies between modules"),
            ("LM3-ART-SA800", 6, "normal inter-car articulation/gangway assemblies inside the three modules"),
            ("LM3-CAR-A900", 9, "complete repeated car modules"),
            ("LM3-BOG-SA610", 9, "powered bogie assemblies"),
            ("LM3-BOG-SA620", 9, "trailer bogie assemblies"),
            ("LM3-SYS-SA900", 3, "per-module control/electronics packs enumerated into one consist"),
        ],
        "assembly_instructions": [
            {
                "step": 1,
                "title": "release the three module build packs",
                "work_center": "production control",
                "instructions": [
                    "Release three signed LM3-TRAINSET-A000 build packs with matching software/configuration baselines.",
                    "Freeze which two end positions become outer panoramic ends and which four become open mid-connection ends.",
                    "Issue serialised LM3-EIF-SA650 option records for all six module ends before any cowl or open-portal hardware is fitted.",
                ],
                "qa": ["configuration baseline", "module serial list", "selected end-option record"],
            },
            {
                "step": 2,
                "title": "complete the three individual train modules",
                "work_center": "standard LM3 final assembly track",
                "instructions": [
                    "Build each three-car module through the normal LM3 carbody, bogie, interior, HV, roof, door, and static-test sequence.",
                    "Fit panoramic LM3-END-SA700 only at the two full-set outer ends.",
                    "Leave the four future mid-connection ends as surveyed LM3-EIF-SA650 open-option interfaces with protected service connectors and temporary weather covers.",
                ],
                "qa": ["module static release", "outer-end water test", "open-interface preservation record"],
            },
            {
                "step": 3,
                "title": "align modules on the long commissioning road",
                "work_center": "long final assembly track / depot commissioning road",
                "instructions": [
                    "Place the three modules on a level road with train centrelines and end-interface carrier rings aligned.",
                    "Set temporary supports or ride-height correction only at the released bogie/air-spring datum points.",
                    "Survey both train-to-train joint gaps, yaw angle, floor height, and lateral offset before opening the protected service covers.",
                ],
                "qa": ["joint gap survey", "floor/threshold level report", "centreline alignment record"],
            },
            {
                "step": 4,
                "title": "install two LM3-TTART-SA850 open connections",
                "work_center": "train-to-train articulation cell",
                "instructions": [
                    "Install the open portal clamp frames, lower drawbar/spherical pivot, anti-lift keepers, upper links, bellows, and turntable threshold bridges.",
                    "Route HV, LV/data, safety-loop, coolant, HVAC sleeve, drain, and diagnostic jumpers through the released train-to-train service cassette.",
                    "Fit blanking/dust covers to unused outer-end transition connectors and record connector serials.",
                ],
                "qa": ["motion sweep", "bend-radius sweep", "trainline continuity", "water ingress/drain test"],
            },
            {
                "step": 5,
                "title": "close passenger and interior continuity",
                "work_center": "interior fit-out cell",
                "instructions": [
                    "Install the walk-through floor transition trims, bellows interior side walls, ceiling panels, lighting continuation, signage, CCTV coverage, and emergency communication labels.",
                    "Check PRM threshold transitions and trip hazards through both train-to-train joints.",
                    "Run passenger information, lighting, CCTV/intercom, and emergency egress checks across all nine cars.",
                ],
                "qa": ["PRM/egress gauge", "lighting/PIS/CCTV enumeration", "rattle and edge-radius inspection"],
            },
            {
                "step": 6,
                "title": "commission the 9-car full set",
                "work_center": "static test cell and dynamic test track",
                "instructions": [
                    "Enumerate all three LM3-SYS-SA900 control packs as one full-set consist with clear leading/trailing-end roles.",
                    "Run insulation, HVIL, brake, door, HVAC, charging, emergency loop, event-recorder, and rescue-mode tests end to end.",
                    "Release dynamic running only after the long-consist FEM screening cases, trainline tests, and both open-joint motion sweeps are signed.",
                ],
                "qa": ["full-set static test record", "FEM screening accepted", "dynamic-test release"],
            },
        ],
        "fem_screening_matrix": [
            {
                "slug": "full-set-longitudinal-buff-screen",
                "scope": "148.5 m full set under longitudinal buff/draft load through the three train modules and two open joints",
            },
            {
                "slug": "full-set-vertical-service-screen",
                "scope": "nine-car supported vertical service gravity screen with all module bogie supports active",
            },
            {
                "slug": "train-to-train-joint-vertical-screen",
                "scope": "local open-end carrier rings, threshold bridge, lower joint, and upper-link load path under vertical passenger/joint load",
            },
            {
                "slug": "train-to-train-joint-lateral-sway-screen",
                "scope": "local open-end carrier rings and gangway cassette under lateral/racking load",
            },
        ],
        "release_caveats": [
            "This is a worked example and does not change the reference three-car trainset baseline.",
            "The 148.5 m full set needs route/platform, evacuation, traction-power, braking-distance, depot-road, and regulation checks before use.",
            "The FEM cases are gross beam-model screens; detailed shell/solid meshes, weld fatigue, supplier gangway certification, crash, derailment, modal, and thermal cases remain release work.",
        ],
    }


def render_full_set_3train_assembly(design: BuildableTrainsetDesign) -> str:
    payload = full_set_3train_payload(design)
    cfg = dict(payload["configuration"])  # type: ignore[arg-type]
    lines = [
        "# LM3 Full-Set 3-Train Assembly Example",
        "",
        "Generated by `scripts/buildable-trainset.sh`. This is a worked",
        "example for assembling three complete LM3 three-car train modules",
        "into one nine-car walk-through full set using the configurable",
        "open train-to-train articulation ends.",
        "",
        f"- Assembly ID: `{payload['assembly_id']}`",
        f"- Candidate: `{payload['candidate']}`",
        f"- Document revision: `{payload['document_revision']}`",
        f"- Release status: `{payload['release_status']}`",
        "",
        "## Configuration",
        "",
        "| Parameter | Value |",
        "|---|---:|",
    ]
    for key, value in cfg.items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## FreeCAD Design Artifacts",
            "",
            "| Artifact | Source | Command | Purpose |",
            "|---|---|---|---|",
        ]
    )
    for item in payload["freecad_designs"]:  # type: ignore[index]
        row = dict(item)
        lines.append(
            f"| `{row['artifact']}` | `{row['source']}` | `{row['command']}` | {row['purpose']} |"
        )
    lines.extend(
        [
            "",
            "## Principal Parts And Subassemblies",
            "",
            "| ID | Qty for full set | Role |",
            "|---|---:|---|",
        ]
    )
    for item_id, qty, role in payload["principal_parts_and_subassemblies"]:  # type: ignore[index]
        lines.append(f"| `{item_id}` | {qty} | {role} |")
    lines.extend(
        [
            "",
            "## Assembly Instructions",
            "",
        ]
    )
    for step in payload["assembly_instructions"]:  # type: ignore[index]
        row = dict(step)
        lines.extend(
            [
                f"### {row['step']}. {row['title']}",
                "",
                f"- Work center: {row['work_center']}",
                "- Instructions:",
            ]
        )
        lines.extend(f"  - {instruction}" for instruction in row["instructions"])  # type: ignore[index]
        lines.append("- QA / hold points:")
        lines.extend(f"  - {gate}" for gate in row["qa"])  # type: ignore[index]
        lines.append("")
    lines.extend(
        [
            "## FEM Screening Matrix",
            "",
            "| Slug | Scope |",
            "|---|---|",
        ]
    )
    for study in payload["fem_screening_matrix"]:  # type: ignore[index]
        row = dict(study)
        lines.append(f"| `{row['slug']}` | {row['scope']} |")
    lines.extend(["", "## Release Caveats", ""])
    lines.extend(f"- {caveat}" for caveat in payload["release_caveats"])  # type: ignore[index]
    lines.append("")
    return "\n".join(lines)


def write_outputs(
    design: BuildableTrainsetDesign,
    out_dir: Path,
) -> tuple[Path, Path, Path, DefinitionPackPaths, ShopTravelerPackPaths]:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_json = out_dir / "buildable-trainset-manifest.json"
    manifest_md = out_dir / "buildable-trainset-manifest.md"
    review_md = out_dir / "current-design-buildability-review.md"
    gaps_md = out_dir / "open-release-gaps.md"
    mass_json = out_dir / "mass-budget.json"
    mass_md = out_dir / "mass-budget.md"
    joints_json = out_dir / "joint-control-schedule.json"
    joints_md = out_dir / "joint-control-schedule.md"
    critical_json = out_dir / "critical-path.json"
    critical_md = out_dir / "critical-path.md"
    end_interface_json = out_dir / "train-end-interface.json"
    end_interface_md = out_dir / "train-end-interface.md"
    full_set_json = out_dir / "full-set-3train-assembly.json"
    full_set_md = out_dir / "full-set-3train-assembly.md"
    manifest_json.write_text(
        json.dumps(asdict(design), default=_serialise, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest_md.write_text(render_manifest(design), encoding="utf-8")
    review_md.write_text(render_review(design), encoding="utf-8")
    gaps_md.write_text(render_open_release_gaps(design), encoding="utf-8")
    mass_json.write_text(json.dumps(mass_budget_payload(design), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    mass_md.write_text(render_mass_budget(design), encoding="utf-8")
    joints_json.write_text(
        json.dumps(
            {
                "document_revision": "A-DRAFT",
                "release_status": "joint-authority-defined-values-open",
                "candidate": design.candidate.id,
                "joints": joint_control_rows(design),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    joints_md.write_text(render_joint_control_schedule(design), encoding="utf-8")
    critical_json.write_text(json.dumps(critical_path_payload(design), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    critical_md.write_text(render_critical_path(design), encoding="utf-8")
    end_interface_json.write_text(
        json.dumps(train_end_interface_payload(design), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    end_interface_md.write_text(render_train_end_interface(design), encoding="utf-8")
    full_set_json.write_text(
        json.dumps(full_set_3train_payload(design), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    full_set_md.write_text(render_full_set_3train_assembly(design), encoding="utf-8")
    definition_pack = write_definition_pack(design, out_dir / "definitions")
    traveler_pack = write_shop_traveler_pack(design, out_dir / "travelers")
    return manifest_json, manifest_md, review_md, definition_pack, traveler_pack


def render_manifest(design: BuildableTrainsetDesign) -> str:
    route_counts: dict[str, float] = {}
    for item in design.product_items:
        route_counts[item.route.value] = route_counts.get(item.route.value, 0.0) + item.quantity_per_trainset
    lines = [
        "# Buildable trainset manifest",
        "",
        "Generated by `scripts/buildable-trainset.sh`. This is the first structured",
        "product breakdown for a buildable OpenSourceRail trainset: parts →",
        "subassemblies → assemblies → final trainset.",
        "",
        f"- Family: `{design.family.value}`",
        f"- Candidate: `{design.candidate.id}`",
        f"- Candidate score: `{design.candidate.score:.3f}`",
        f"- Candidate feasible: `{str(design.candidate.feasible).lower()}`",
        f"- Product item rows: `{len(design.product_items)}`",
        f"- Assembly nodes: `{len(design.assemblies)}`",
        f"- Open supplier/component rows: `{sum(item.maturity is not Maturity.RELEASE_CANDIDATE for item in design.product_items)}` ([register](open-release-gaps.md))",
        "",
        "## Candidate metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in design.candidate.metrics.items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Current CAD baseline vs optimizer target",
            "",
            "| Parameter | Current CAD baseline | Optimizer target |",
            "|---|---:|---:|",
        ]
    )
    for key in ("car_length_m", "motor", "battery", "hvac", "pv_modules_per_car"):
        lines.append(f"| `{key}` | `{design.current_cad_baseline[key]}` | `{design.target_candidate[key]}` |")
    lines.extend(
        [
            "",
            "## Product item route summary",
            "",
            "| Route | Quantity sum |",
            "|---|---:|",
        ]
    )
    for route in (Route.MAKE, Route.BID, Route.SOURCE):
        lines.append(f"| `{route.value}` | {route_counts.get(route.value, 0):.0f} |")
    lines.extend(
        [
            "",
            "## Assembly tree",
            "",
            "| ID | Layer | Qty/trainset | Build cell | Children | Hold points |",
            "|---|---|---:|---|---|---|",
        ]
    )
    for node in design.assemblies:
        children = "<br>".join(f"`{child}`" for child in node.children)
        hold_points = "<br>".join(node.hold_points)
        lines.append(
            f"| `{node.id}` | {node.layer.value} | {node.quantity_per_trainset:g} | "
            f"{node.build_cell} | {children} | {hold_points} |"
        )
    lines.extend(
        [
            "",
            "## Product items",
            "",
            "| ID | BOM lines | Layer | Route | Qty/trainset | Parent | Title | Acceptance |",
            "|---|---|---|---|---:|---|---|---|",
        ]
    )
    for item in design.product_items:
        acceptance = "<br>".join(item.acceptance)
        bom_lines = "<br>".join(f"`{line_id}`" for line_id in bom_line_ids_for_engineering_id(item.id))
        lines.append(
            f"| `{item.id}` | {bom_lines} | {item.layer.value} | `{item.route.value}` | "
            f"{item.quantity_per_trainset:g} {item.unit} | `{item.parent}` | {item.title} | {acceptance} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_open_release_gaps(design: BuildableTrainsetDesign) -> str:
    """Render component closures from the product-tree maturity field."""

    open_items = [
        item
        for item in design.product_items
        if item.maturity is not Maturity.RELEASE_CANDIDATE
    ]
    lines = [
        "# Trainset open release gap register",
        "",
        "Generated from the same controlled product rows used by the definition",
        "and shop-traveler packs. Product ownership and procurement-BOM links are",
        "already resolved; the rows below still require supplier, component, or",
        "interface evidence before their maturity can become `release-candidate`.",
        "",
        f"Open product rows: **{len(open_items)} of {len(design.product_items)}**.",
        "",
        "| Engineering ID | BOM lines | Route | Maturity / blocker | Component | Parent assembly | Closure evidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in open_items:
        bom_lines = ", ".join(
            f"`{line_id}`" for line_id in bom_line_ids_for_engineering_id(item.id)
        )
        acceptance = "; ".join(item.acceptance)
        lines.append(
            f"| `{item.id}` | {bom_lines} | `{item.route.value}` | "
            f"`{item.maturity.value}` | {item.title} | `{item.parent}` | {acceptance} |"
        )
    lines.extend(
        [
            "",
            "## Non-product release gates",
            "",
            "The product rows above do not close controlled manufacturing drawings,",
            "supplier-specific mass/power/envelope freezes, structural proof, physical",
            "first-article inspection, or signed shop-traveler evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def render_review(design: BuildableTrainsetDesign) -> str:
    lines = [
        "# Current basic design buildability review",
        "",
        "This review uses the generated design-system optimum and the current",
        "rolling-stock CAD/BOM/fabrication package to identify what is already",
        "buildable, what is only an envelope, and what must be closed before",
        "first steel cut.",
        "",
        "## Summary",
        "",
        "| Status | Meaning |",
        "|---|---|",
        "| green | current design is good enough to carry into v2A build package |",
        "| yellow | concept is sound but supplier/CAD/BOM alignment must be closed |",
        "| red | missing build-release evidence or shop-drawing detail |",
        "",
        "## Findings",
        "",
        "| ID | Status | Scope | Finding | Action |",
        "|---|---|---|---|---|",
    ]
    for finding in design.review_findings:
        lines.append(
            f"| `{finding.id}` | `{finding.status}` | {finding.scope} | "
            f"{finding.finding} | {finding.action} |"
        )
    lines.extend(
        [
            "",
            "## Immediate build-package work",
            "",
            "1. Treat the generated definition and shop-traveler packs as the",
            "   product-tree index for parts, external components, subassemblies,",
            "   assemblies, and trainsets.",
            "2. Convert each `MAKE` definition into controlled drawings: cut list,",
            "   flat pattern, weld class, datum scheme, tolerance, and inspection method.",
            "3. Convert each `BID`/`SOURCE` definition into an RFQ envelope: mass, power,",
            "   volume, mounting datum, service clearance, evidence pack, and alternate",
            "   acceptance rule.",
            "4. Close the generated mass-budget categories and joint-control rows as",
            "   supplier, calculation, CAD, and weighing evidence becomes available.",
            "5. Attach local proof cases to the structural subassemblies: underframe,",
            "   bolsters, coupler pocket, door portals, battery tray, roof equipment,",
            "   bogie frames, and articulation adapters.",
            "6. Fill traveler approval/signoff blocks only during a real build; do not",
            "   pre-sign generated templates.",
            "7. Regenerate FreeCAD/FEM only after the promoted candidate parameters are",
            "   reflected in the parametric source.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate buildable trainset product breakdown and review.")
    parser.add_argument(
        "--family",
        choices=[family.value for family in ConsistFamily],
        default=ConsistFamily.LIGHT_METRO_3CAR.value,
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "catalog" / "buildable-trainset",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    design = buildable_trainset_design(ConsistFamily(args.family))
    json_path, manifest_path, review_path, definition_pack, traveler_pack = write_outputs(design, args.out)
    print(f"candidate: {design.candidate.id}")
    print(f"product item rows: {len(design.product_items)}")
    print(f"assembly nodes: {len(design.assemblies)}")
    print(f"wrote {json_path}")
    print(f"wrote {manifest_path}")
    print(f"wrote {review_path}")
    print(f"wrote {definition_pack.index_json}")
    print(f"wrote {definition_pack.index_md}")
    print(f"definition files: {len(definition_pack.definition_files)}")
    print(f"wrote {traveler_pack.index_json}")
    print(f"wrote {traveler_pack.index_md}")
    print(f"shop traveler files: {len(traveler_pack.traveler_files)}")


if __name__ == "__main__":
    main()

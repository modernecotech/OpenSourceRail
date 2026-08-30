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
import tempfile
import tomllib
from dataclasses import asdict, dataclass
from enum import Enum
from functools import lru_cache
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
from osr_mech.rolling_stock.small_components import small_component_standard_payload


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


BUILD_COST_LABOR_RATE_USD_PER_HOUR = 10.0
BUILD_COST_UNEXPECTED_PREMIUM_FRACTION = 0.20


CURRENT_CAD_BASELINE: dict[str, str | float] = {
    "family": ConsistFamily.LIGHT_METRO_3CAR.value,
    "car_length_m": PROMOTED_LIGHT_METRO_CAR_LENGTH_M,
    "motor": "motor-350kw-hm47-class",
    "battery": "battery-225kwh-lfp-800v",
    "hvac": "hvac-24kw-direct-hv-dc",
    "pv_modules_per_car": float(PROMOTED_ROOF_SOLAR_MODULES_PER_CAR),
}

SUPPLIER_ANCHOR_SOURCE = Path(__file__).resolve().parents[4] / "lib/templates/trainset-supplier-anchors.toml"


@lru_cache(maxsize=1)
def _supplier_anchor_data() -> dict[str, object]:
    source = tomllib.loads(SUPPLIER_ANCHOR_SOURCE.read_text(encoding="utf-8"))
    by_product: dict[str, dict[str, object]] = {}
    for anchor in source["anchor"]:
        for product_id in anchor["product_ids"]:
            by_product[str(product_id)] = anchor
    return {"source": source, "by_product": by_product}


def _supplier_anchor_payload(item_id: str) -> dict[str, object] | None:
    data = _supplier_anchor_data()
    anchor = data["by_product"].get(item_id)
    if anchor is None:
        return None
    source = data["source"]
    return {
        "id": anchor["id"],
        "manufacturer": anchor["manufacturer"],
        "product_family": anchor["product_family"],
        "manufacturer_url": anchor["manufacturer_url"],
        "anchor_type": anchor["anchor_type"],
        "procurement_state": anchor["procurement_state"],
        "local_equivalent_allowed": True,
        "localisation": anchor["localisation"],
        "fit_gaps": list(anchor["fit_gaps"]),
        "mandatory_equivalence": list(source["equivalence"]["required"]),
        "checked_on": source["checked_on"],
        "release_boundary": source["release_boundary"],
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
            "LM3-ART-SA810",
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
            "LM3-TRC-SA615",
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
            "stepped floor-board and removable service-hatch system",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            135,
            "m2",
            "LM3-INT-SA330",
            ("cots_equipment.py", "bom-skeleton.md B12", "LM3-INT-230"),
            "Locally CNC-cut floor-board panels and removable hatches mount to surveyed support rails without trapping wet services.",
            ("fire certificate", "panel load and deflection evidence", "hatch removal trial", "level/step and egress survey"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P061",
            "welded resilient floor covering, cove, nosing, and adhesive system",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            135,
            "m2",
            "LM3-INT-SA330",
            ("cots_equipment.py", "bom-skeleton.md B13", "LM3-INT-230"),
            "One supplier-qualified rail flooring system covers the board joints, coved edges, steps, hatches, thresholds and repair patches.",
            ("fire/smoke certificate", "adhesive compatibility and cure record", "welded-seam peel sample", "slip and cleanability evidence"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P062",
            "longitudinal passenger and priority-seat modules",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            60,
            "seat",
            "LM3-INT-SA330",
            ("cots_equipment.py", "bom-skeleton.md B14", "LM3-INT-230"),
            "Repeatable seat modules use the common service rail and calculated saddle adapters instead of unique brackets through floor panels.",
            ("fire/smoke certificate", "seat/occupant load evidence", "fastener and anti-rotation record", "egress and cleaning-clearance gauge"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P063",
            "stainless grab-pole, handrail, joint, and insulated adapter kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "car kit",
            "LM3-INT-SA330",
            ("cots_equipment.py", "bom-skeleton.md B15", "LM3-INT-230"),
            "Cut-to-length modular tubes terminate in replaceable common-rail saddles; primary passenger loads bypass liners and trim.",
            ("material/finish certificate", "joint locking record", "fixture-specific proof-load evidence", "reach, egress and snag survey"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P064",
            "passenger-information display, speaker, amplifier, and mounting kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "car kit",
            "LM3-INT-SA330",
            ("cots_equipment.py", "bom-skeleton.md B18", "LM3-INT-230"),
            "Plug-in PIS modules attach to standard equipment adapters with keyed LV/data connectors and service loops.",
            ("fire/EMC evidence", "network enumeration", "audio/intelligibility test", "display visibility and service-removal trial"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P065",
            "CCTV camera, passenger intercom, PoE/data, and mounting kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "car kit",
            "LM3-INT-SA330",
            ("cots_equipment.py", "bom-skeleton.md B19", "LM3-INT-230"),
            "Replaceable cameras and intercoms use keyed connectors and common adapters while preserving coverage, privacy and accessible call locations.",
            ("fire/EMC/IP evidence", "network enumeration", "camera coverage/privacy review", "intercom call and service-removal trial"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-EXT-P066",
            "PRM, safety-signage, emergency-lighting, extinguisher, and first-aid kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "car kit",
            "LM3-INT-SA330",
            ("cots_equipment.py", "bom-skeleton.md A1-A4", "LM3-INT-230"),
            "A controlled location schedule separates fixed PRM/call-button/signage/emergency-light equipment from operator-replenished extinguishers, first aid and seals.",
            ("accessible reach/contrast review", "emergency-light duration test", "equipment certificate/expiry audit", "location and egress survey"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-FIX-P010",
            "OSR-RAIL-42 common ceiling, waist, and seat-zone service rail kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "car kit",
            "LM3-FIX-SA340",
            ("small_components.py", "bom-skeleton.md B2/B15/B21", "LM3-INT-230"),
            "One cut/drill gauge produces all common extruded aluminium equipment rails; local adapters, not rail variants, accommodate equipment.",
            ("rail datum survey", "end-deburr check", "isolation/finish inspection", "representative pull/slip test"),
        ),
        ProductItem(
            "LM3-FIX-P020",
            "four-family captive fastener, floating nut, isolator, and access-fastener kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars,
            "car kit",
            "LM3-FIX-SA340",
            ("small_components.py", "bom-skeleton.md B2/B21", "LM3-INT-230"),
            "M6 captive, M8 calculated-fixture, quarter-turn access, and M10 sealed exterior families replace ad-hoc fastener selection.",
            ("supplier certificate", "batch/finish trace", "installed-grip gauge", "locking and captive-part audit"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-FIX-P030",
            "standard passenger-fixture saddle and equipment adapter kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars,
            "car kit",
            "LM3-FIX-SA340",
            ("small_components.py", "bom-skeleton.md B14/B15/E14", "LM3-INT-230"),
            "A small adapter family attaches seats, handrails, PIS, CCTV and cable supports to the common rail without unique body brackets.",
            ("adapter gauge", "fixture-specific load calculation", "proof-load sample", "egress and snag check"),
            Maturity.CONCEPT,
        ),
        ProductItem(
            "LM3-WIN-P010",
            "replaceable window pressure frame, dry seal, drain, and captive retention kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars * 6,
            "opening kit",
            "LM3-WIN-SA320",
            ("small_components.py", "cots_equipment.py", "bom-skeleton.md B10", "LM3-WIN-210"),
            "Supplier bonds glass within its aluminium cassette; the OSR pressure frame and dry seal allow routine removal without cutting adhesive at the carbody.",
            ("pressure-frame gauge", "retention calculation", "seal compression record", "water-ingress and replacement trial"),
            Maturity.CONCEPT,
        ),
        ProductItem(
            "LM3-DOOR-P010",
            "door four-point adjustable carrier, datum pin, dry seal, and keyed connector bracket kit",
            Layer.FABRICATED_PART,
            Route.MAKE,
            cars * 4,
            "opening kit",
            "LM3-DOOR-SA310",
            ("small_components.py", "systems.py", "bom-skeleton.md B11/B25", "LM3-DOOR-200"),
            "The certified door remains a complete supplier cassette; four common adjustable shoes absorb body tolerance and make removal predictable.",
            ("carrier datum gauge", "interface load calculation", "seal compression record", "connector keying and cassette replacement trial"),
            Maturity.CONCEPT,
        ),
        ProductItem(
            "LM3-LGT-P010",
            "1.2 m plug-in main LED lighting cassette and captive mounting kit",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            cars * 22,
            "module",
            "LM3-LGT-SA350",
            ("small_components.py", "cots_equipment.py", "bom-skeleton.md B16", "LM3-INT-230"),
            "Twenty-two identical replaceable cassettes per car eliminate field-cut strip, loose terminations, and long fragile light runs.",
            ("rail fire certificate", "shock/vibration evidence", "photometric/lux test", "plug polarity and retention test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-LGT-P020",
            "emergency and doorway lighting modules with independent keyed feeder kit",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "car kit",
            "LM3-LGT-SA350",
            ("small_components.py", "cots_equipment.py", "bom-skeleton.md B16/A4", "LM3-INT-230"),
            "Independent-feed emergency and doorway modules share service-rail mechanics but cannot be cross-connected to the main-light feed.",
            ("emergency duration/effectiveness evidence", "evacuation visibility test", "feed isolation test", "doorway illumination test"),
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
            "Sacrificial fire-rated saloon barriers over the side battery enclosures; battery service access and pressure relief remain exterior-only.",
            ("fire-material certificate", "no-saloon-opening inspection", "HV warning label check", "sharp-edge inspection"),
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
            "LM3-TRC-SA615",
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
            "LM3-TRC-SA615",
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
            f"{candidate.parameters.battery_id} saloon-isolated side traction battery pack",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "ea",
            "LM3-HV-SA510",
            ("design-iteration-summary.md", "systems.py", "LM3-BDY-140"),
            "Optimizer-selected per-car pack; final supplier must fit the externally accessed side tray, cooling, BMS, fire separation, and outward-only vent path.",
            ("cell/module certificate", "isolation test", "no-saloon-opening inspection", "outward vent/fire containment data"),
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
            "powered-bogie wheelset with axle-mounted brake discs",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars * 2,
            "wheelset",
            "LM3-BOG-SA611",
            ("bogie/wheelset.py", "bogie/brake.py", "LM3-BOG-400"),
            "Supplier-machined axle, wheels and brake-disc seats are procured as a dynamically balanced, traceable railway wheelset; wheels or axles are not mixed between qualified families.",
            ("wheel/axle heat certificates", "press-force chart", "back-to-back and runout report", "ultrasonic inspection", "balance record"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-BOG-P041",
            "trailer-bogie wheelset with axle-mounted brake discs",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars * 2,
            "wheelset",
            "LM3-BOG-SA621",
            ("bogie/wheelset.py", "bogie/brake.py", "LM3-BOG-410"),
            "Supplier-machined axle, wheels and brake-disc seats are procured as a dynamically balanced, traceable railway wheelset using the same released wheel profile as the powered bogie.",
            ("wheel/axle heat certificates", "press-force chart", "back-to-back and runout report", "ultrasonic inspection", "balance record"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-BOG-P042",
            "powered-wheelset axlebox, sealed bearing unit, speed and temperature sensor set",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars * 2,
            "wheelset set",
            "LM3-BOG-SA611",
            ("bogie/wheelset.py", "systems.py", "LM3-BOG-400"),
            "Ready-to-mount railway axlebox bearing units keep bearing setting, seals and sensor interfaces under one supplier responsibility.",
            ("bearing serial/clearance record", "grease and seal certificate", "axle journal fit", "speed/temperature sensor calibration", "rotation test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-BOG-P043",
            "trailer-wheelset axlebox, sealed bearing unit, speed and temperature sensor set",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars * 2,
            "wheelset set",
            "LM3-BOG-SA621",
            ("bogie/wheelset.py", "systems.py", "LM3-BOG-410"),
            "Ready-to-mount railway axlebox bearing units share the powered-bogie bearing and sensor interface where load calculations permit.",
            ("bearing serial/clearance record", "grease and seal certificate", "axle journal fit", "speed/temperature sensor calibration", "rotation test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-BOG-P044",
            "powered-bogie primary suspension spring, guide and bump-stop set",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "bogie set",
            "LM3-BOG-SA611",
            ("bogie/suspension.py", "LM3-BOG-400"),
            "Matched, batch-traceable primary springs and elastomer guides are selected from the released axle-load and dynamic model.",
            ("load-deflection curves", "matched-height report", "compound/batch certificates", "installed preload and clearance survey"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-BOG-P045",
            "trailer-bogie primary suspension spring, guide and bump-stop set",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "bogie set",
            "LM3-BOG-SA621",
            ("bogie/suspension.py", "LM3-BOG-410"),
            "Matched, batch-traceable primary springs and elastomer guides are selected from the released trailer axle-load and dynamic model.",
            ("load-deflection curves", "matched-height report", "compound/batch certificates", "installed preload and clearance survey"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-BOG-P046",
            "powered-bogie to carbody connection: air springs, emergency spring, centre pivot, yaw links and dampers",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "bogie set",
            "LM3-BOG-SA610",
            ("bogie/suspension.py", "car_body.py", "LM3-BOG-400"),
            "The complete body-to-bogie load path is one interface-controlled package even when springs, pivot and dampers are sourced from different qualified suppliers.",
            ("vertical/lateral load curves", "pivot proof and articulation limit", "damper curves hot/cold", "ride-height and anti-lift survey"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-BOG-P047",
            "trailer-bogie to carbody connection: air springs, emergency spring, centre pivot, yaw links and dampers",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "bogie set",
            "LM3-BOG-SA620",
            ("bogie/suspension.py", "car_body.py", "LM3-BOG-410"),
            "The trailer body-to-bogie load path shares the powered-bogie interfaces where released loads and kinematics permit.",
            ("vertical/lateral load curves", "pivot proof and articulation limit", "damper curves hot/cold", "ride-height and anti-lift survey"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-BOG-P048",
            "powered-bogie brake calipers, parking actuators, pads and wheel-slide hardware",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "bogie set",
            "LM3-BOG-SA611",
            ("bogie/brake.py", "systems.py", "LM3-BOG-400"),
            "A rail brake supplier matches caliper, actuator, disc and pad friction pair to the released stopping, thermal and parking-brake cases.",
            ("brake-force calculation", "friction-pair certificate", "thermal capacity", "parking holding test", "WSP functional test"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-BOG-P049",
            "trailer-bogie brake calipers, parking actuators, pads and wheel-slide hardware",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            cars,
            "bogie set",
            "LM3-BOG-SA621",
            ("bogie/brake.py", "systems.py", "LM3-BOG-410"),
            "A rail brake supplier matches caliper, actuator, disc and pad friction pair to the released stopping, thermal and parking-brake cases.",
            ("brake-force calculation", "friction-pair certificate", "thermal capacity", "parking holding test", "WSP functional test"),
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
            "articulation lower spherical pivot, bearing housing and pin set",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            articulations,
            "joint set",
            "LM3-ART-SA810",
            ("systems.py", "articulation.md", "LM3-SYS-170"),
            "Supplier-sized spherical bearing, housing, pin, bushes and retainers transmit the released draw, buff, vertical and anti-lift loads through the OSR adapter.",
            ("bearing static/dynamic capacity", "pin material/NDT", "proof load", "lubrication/sealing plan", "motion-envelope proof"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-ART-P021",
            "articulation upper lateral/yaw links, spherical joints and retained pins",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            articulations,
            "joint set",
            "LM3-ART-SA810",
            ("systems.py", "articulation.md", "LM3-SYS-170"),
            "Paired upper links stabilize roll/yaw while the lower pivot carries the primary articulation loads; all rod ends and pins remain positively retained.",
            ("link buckling/fatigue proof", "joint angular capacity", "pin retention inspection", "full-motion sweep"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-ART-P022",
            "inter-car double-wall corrugated bellows and clamp-frame set",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            articulations,
            "gangway set",
            "LM3-ART-SA820",
            ("articulation.md", "LM3-SYS-170"),
            "A supplier-tailored metro gangway bellows seals the passenger connection without becoming part of the structural draw/buff load path.",
            ("fire/smoke evidence", "pressure/water ingress test", "fatigue-cycle evidence", "replaceable-clamp demonstration"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-ART-P023",
            "inter-car passenger bridge, turntable and flexible interior-panel set",
            Layer.EXTERNAL_COMPONENT,
            Route.BID,
            articulations,
            "gangway set",
            "LM3-ART-SA820",
            ("articulation.md", "LM3-SYS-170"),
            "The bridge and turntable provide a flush, anti-slip passenger path across the full released articulation envelope with guarded pinch zones.",
            ("passenger load proof", "anti-slip evidence", "gap/step gauge", "pinch/shear hazard review", "full-motion sweep"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        ProductItem(
            "LM3-ART-P024",
            "articulation trainline carrier, support arms, abrasion liners and drain path",
            Layer.EXTERNAL_COMPONENT,
            Route.SOURCE,
            articulations,
            "carrier set",
            "LM3-ART-SA830",
            ("articulation.md", "systems.py", "LM3-SYS-170"),
            "A replaceable energy-chain/support system controls service-loop bend radius and separates HV, LV/data and coolant across the joint.",
            ("rated bend radius", "dynamic sweep", "abrasion/fire evidence", "drain test", "service replacement trial"),
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
            ("systems.py", "control-electronics/rolling-stock-integration.md", "LM3-ELC-300"),
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
            "LM3-ART-SA830",
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
            ("LM3-BDY-P110", "LM3-WIN-P010", "LM3-EXT-P020"),
            "composite / glazing cell",
            ("aperture gauge", "bond/gasket procedure", "water ingress test"),
            ("cots_equipment.py", "LM3-WIN-210"),
        ),
        AssemblyNode(
            "LM3-DOOR-SA310",
            "door cassette and threshold assembly",
            Layer.SUBASSEMBLY,
            cars * 4,
            ("LM3-BDY-P100", "LM3-DOOR-P010", "LM3-EXT-P010"),
            "final assembly and commissioning cell",
            ("door gauge fit", "obstruction test", "closed-and-locked test"),
            ("systems.py", "LM3-DOOR-200"),
        ),
        AssemblyNode(
            "LM3-INT-SA330",
            "interior and passenger systems fit-out",
            Layer.SUBASSEMBLY,
            cars,
            (
                "LM3-EXT-P060",
                "LM3-EXT-P061",
                "LM3-EXT-P062",
                "LM3-EXT-P063",
                "LM3-EXT-P064",
                "LM3-EXT-P065",
                "LM3-EXT-P066",
                "LM3-INT-P010",
                "LM3-INT-P020",
                "LM3-INT-P030",
                "LM3-INT-P040",
                "LM3-INT-P050",
            ),
            "final assembly and commissioning cell",
            ("egress check", "fire-material pack", "liner/trim fit survey", "lighting/PIS/CCTV static test"),
            ("cots_equipment.py", "cabin-fiberglass.md", "LM3-INT-230", "LM3-INT-240"),
        ),
        AssemblyNode(
            "LM3-FIX-SA340",
            "common service-rail, captive-fastener, and fixture-adapter installation",
            Layer.SUBASSEMBLY,
            cars,
            ("LM3-FIX-P010", "LM3-FIX-P020", "LM3-FIX-P030"),
            "interior pre-fit and final assembly cell",
            ("rail datum survey", "fastener-family audit", "fixture load-evidence check", "service/removal demonstration"),
            ("small_components.py", "LM3-INT-230"),
            Maturity.CONCEPT,
        ),
        AssemblyNode(
            "LM3-LGT-SA350",
            "modular main, emergency, and doorway lighting installation",
            Layer.SUBASSEMBLY,
            cars,
            ("LM3-LGT-P010", "LM3-LGT-P020"),
            "interior pre-fit and commissioning cell",
            ("connector key audit", "lighting lux map", "emergency-feed isolation and duration test", "module replacement demonstration"),
            ("small_components.py", "cots_equipment.py", "LM3-INT-230"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
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
            "LM3-BOG-SA611",
            "powered-bogie running unit: wheelsets, axleboxes, primary suspension and brakes",
            Layer.SUBASSEMBLY,
            cars,
            ("LM3-BOG-P040", "LM3-BOG-P042", "LM3-BOG-P044", "LM3-BOG-P048"),
            "bogie clean assembly and brake cell",
            ("wheelset identity", "bearing installation", "primary-height match", "static brake/WSP test", "free rotation"),
            ("bogie/wheelset.py", "bogie/brake.py", "bogie/suspension.py", "LM3-BOG-400"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        AssemblyNode(
            "LM3-TRC-SA615",
            "bogie-mounted motor, gearbox, flexible coupling and torque-reaction drive unit",
            Layer.SUBASSEMBLY,
            cars,
            ("LM3-TRC-P010", "LM3-TRC-P020", "LM3-BOG-P050"),
            "traction drive clean assembly cell",
            ("motor/gearbox serial match", "coupling alignment", "torque-link proof", "insulation/rotation test", "removal-envelope trial"),
            ("bogie/motor.py", "bogie/gearbox.py", "bogie/assembly.py", "LM3-TRC-500"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        AssemblyNode(
            "LM3-BOG-SA610",
            "complete powered bogie with running unit, bogie-mounted drive and body connection",
            Layer.SUBASSEMBLY,
            cars,
            (
                "LM3-BOG-P010",
                "LM3-BOG-P030",
                "LM3-BOG-SA611",
                "LM3-TRC-SA615",
                "LM3-BOG-P046",
                "LM3-BOG-P060",
            ),
            "bogie weld and assembly cell",
            ("frame NDT", "wheelset/bearing certificate", "motor/gearbox alignment", "static brake test"),
            ("bogie/assembly.py", "LM3-BOG-400"),
        ),
        AssemblyNode(
            "LM3-BOG-SA621",
            "trailer-bogie running unit: wheelsets, axleboxes, primary suspension and brakes",
            Layer.SUBASSEMBLY,
            cars,
            ("LM3-BOG-P041", "LM3-BOG-P043", "LM3-BOG-P045", "LM3-BOG-P049"),
            "bogie clean assembly and brake cell",
            ("wheelset identity", "bearing installation", "primary-height match", "static brake/WSP test", "free rotation"),
            ("bogie/wheelset.py", "bogie/brake.py", "bogie/suspension.py", "LM3-BOG-410"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        AssemblyNode(
            "LM3-BOG-SA620",
            "complete trailer bogie with running unit and body connection",
            Layer.SUBASSEMBLY,
            cars,
            ("LM3-BOG-P020", "LM3-BOG-P031", "LM3-BOG-SA621", "LM3-BOG-P047", "LM3-BOG-P061"),
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
            "LM3-ART-SA810",
            "structural articulation joint and anti-lift load path",
            Layer.SUBASSEMBLY,
            max(0, cars - 1),
            ("LM3-ART-P010", "LM3-ART-P020", "LM3-ART-P021"),
            "articulation bench and proof-load cell",
            ("pin/bearing identity", "shimmed datum survey", "proof load", "lubrication/seal release", "motion sweep"),
            ("articulation.md", "systems.py", "LM3-SYS-170"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        AssemblyNode(
            "LM3-ART-SA820",
            "passenger gangway bellows, bridge and turntable subassembly",
            Layer.SUBASSEMBLY,
            max(0, cars - 1),
            ("LM3-ART-P022", "LM3-ART-P023"),
            "gangway clean assembly cell",
            ("fire-material pack", "bridge load test", "gap/pinch gauge", "water test", "full-motion sweep"),
            ("articulation.md", "LM3-SYS-170"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        AssemblyNode(
            "LM3-ART-SA830",
            "articulation service-transfer and segregated trainline subassembly",
            Layer.SUBASSEMBLY,
            max(0, cars - 1),
            ("LM3-ART-P024", "LM3-ART-P030"),
            "harness, hose and articulation bench",
            ("HV/LV segregation", "continuity/pressure test", "bend-radius sweep", "drain test", "replaceability trial"),
            ("articulation.md", "systems.py", "LM3-SYS-170"),
            Maturity.BUILDABLE_AFTER_SUPPLIER_FREEZE,
        ),
        AssemblyNode(
            "LM3-ART-SA800",
            "complete inter-car structural articulation, passenger gangway and service transfer",
            Layer.ASSEMBLY,
            max(0, cars - 1),
            ("LM3-ART-SA810", "LM3-ART-SA820", "LM3-ART-SA830"),
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
            ("systems.py", "control-electronics/rolling-stock-integration.md", "LM3-ELC-300"),
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
                "LM3-FIX-SA340",
                "LM3-LGT-SA350",
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
            "Every assembly integration step now carries machine-readable join classes and torque authority. Interior small parts have been rationalised into four fastener families and one common datum rail instead of treating every attachment as a bespoke structural joint; numerical values remain open until the applicable standard, supplier instruction, or load calculation is released.",
            "Close the generated joint-control schedule by joint ID, qualify the common rail/fastener samples, and reference accepted values from interface drawings and shop travelers.",
        ),
        ReviewFinding(
            "BDR-009",
            "green",
            "small components and serviceability",
            "Door and glazing interfaces, passenger-fixture adapters, lighting cassettes, captive fasteners, seals, drain rails, keyed plugs, and emergency illumination are now explicit CAD/product-tree items rather than an opaque interior-kit allowance.",
            "Keep the simplified interface families fixed while suppliers freeze detailed door, glass, luminaire, connector, and fastener parts; release safety-critical loads and tests through their stated gates.",
        ),
    ]
    if not candidate.feasible:
        findings.append(
            ReviewFinding(
                "BDR-010",
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
    if item.id == "LM3-EXT-P060":
        return MaterialSpec(
            "fire-rated structural floor-board and hatch system",
            "rail-qualified aluminium-honeycomb/composite board candidate with aluminium edge closures, stainless retained hatch hardware, isolating pads and sealed inspection plugs",
            "supplier rail floor specification plus project fire/smoke, concentrated/distributed load, fatigue, moisture, slip-interface and toxicity evidence",
            "CNC-cut numbered boards and flush removable hatches supported continuously at released crossmember/service-rail datums",
            "board thickness, core/skin schedule, support pitch, edge distance, hatch rebates, service clearances and step transitions fixed by LM3-INT-230 drawings and calculation",
            "sealed cut edges and penetrations, isolated mixed-metal joints, no water-trapping pockets, and floor-covering-compatible prepared face",
            "board/panel batch, cut nest, edge-seal batch, retained-fastener lot, installed position, datum survey and load-test record",
            evidence + ("fire/smoke certificate", "floor load/deflection evidence", "hatch removal trial", "level/step survey"),
        )
    if item.id == "LM3-EXT-P061":
        return MaterialSpec(
            "rail fire-rated resilient floor-covering system",
            "supplier-matched sheet covering, welded-seam rod, coving, step nosing, primer, adhesive and repair-patch system",
            "supplier rail flooring specification plus project fire/smoke/toxicity, slip, wear, cleaning-agent and substrate-compatibility evidence",
            "single-system sheet layout with heat-welded seams, coved edges, sealed penetrations, removable hatch cuts and replaceable threshold pieces",
            "roll direction, seam map, cove radius, nosing, threshold termination, adhesive spread and hatch joint fixed by the released installation drawing",
            "anti-slip cleanable finish with no open edges, water traps or incompatible sealant/adhesive combinations",
            "covering/rod/primer/adhesive batch and expiry, substrate moisture/cleanliness record, cure log, seam sample and installed zone map",
            evidence + ("fire/smoke certificate", "adhesive compatibility/cure record", "seam peel sample", "slip evidence"),
        )
    if item.id == "LM3-EXT-P062":
        return MaterialSpec(
            "rail passenger-seat module and calculated mounting kit",
            "fire-rated longitudinal seat shells/cushions, metallic frame, common-rail saddles, anti-rotation keys, isolators and captive locking hardware",
            "supplier rail-seat specification plus project fire/smoke, occupant/abuse load, sharp-edge, accessibility, corrosion and cleanability evidence",
            "replaceable seat modules mounted only through LM3-FIX saddles to structural/common rails, never through finish panels",
            "seat pitch, cant, aisle/PRM clearance, hand clearance, saddle engagement and fastener grip fixed by LM3-INT-230 drawings and released load calculation",
            "cleanable graffiti-resistant finish, radiused passenger edges, isolated dissimilar metals and accessible captive service fasteners",
            "seat serial/batch, fire certificate, adapter variant, fastener lot, torque/locking witness and installed position map",
            evidence + ("seat/occupant load evidence", "fixture proof", "egress/cleaning gauge", "timed module replacement"),
        )
    if item.id == "LM3-EXT-P063":
        return MaterialSpec(
            "modular passenger handrail and stanchion system",
            "304/316 stainless tube candidate, radiused cast/machined joints, insulated common-rail saddles, anti-rotation keys and captive locking hardware",
            "supplier material/finish specification plus project passenger load, fatigue, fire, accessibility, corrosion, electrical-isolation and snag evidence",
            "cut-to-length repeated tubes and replaceable elbows/tees fixed at structural floor/ceiling/service-rail datums without loading liners",
            "tube diameter/wall, joint engagement, support span, reachable zones, adapter geometry and fastener grip fixed by LM3-INT-230 drawings and calculation",
            "brushed/passivated cleanable surface, radiused ends, no exposed threads, isolated mixed metals and sealed floor penetrations",
            "tube heat/batch, fitting/fastener lot, cut list, joint locking witness, installed survey and proof-test record",
            evidence + ("fixture-specific proof-load evidence", "reach/egress survey", "locking audit", "timed joint replacement"),
        )
    if item.id in {"LM3-EXT-P064", "LM3-EXT-P065"}:
        equipment = "passenger-information/audio" if item.id.endswith("064") else "CCTV/passenger-intercom"
        return MaterialSpec(
            f"rail-rated {equipment} equipment kit",
            "serialised display/camera/intercom/audio modules, keyed power/data connectors, fire-rated harness tails, common-rail adapters and captive service fasteners",
            "supplier rail electronics specification plus project fire/smoke, EMC, IP, cybersecurity/configuration, accessibility and lifecycle evidence",
            "plug-in line-replaceable modules with labelled connectors, strain relief, bend-radius/service loops and no hidden joints behind fixed trim",
            "field of view/visibility/reach, mounting envelope, connector keying, heat rejection and service clearance fixed by LM3-INT-230 interface drawings",
            "cleanable tamper-resistant passenger finish, sealed penetrations, galvanic/electrical isolation and protected labels",
            "equipment serial, hardware/firmware/configuration revision, harness batch, adapter position, network address and functional-test record",
            evidence + ("fire/EMC/IP evidence", "network enumeration", "coverage/intelligibility test", "timed module replacement"),
        )
    if item.id == "LM3-EXT-P066":
        return MaterialSpec(
            "controlled PRM and emergency-equipment location kit",
            "passenger call controls, tactile/visual labels, battery-backed exit markers, certified extinguisher/first-aid brackets, tamper seals and common adapters",
            "selected national accessibility/fire rules plus supplier fire, photometric, battery-duration, extinguisher/bracket, label-durability and lifecycle evidence",
            "fixed equipment installed to the released location schedule; replenishable/expiring contents remain separately recorded operator stock",
            "reachable controls, contrast/tactile content, illuminated sightlines, bracket loads, egress keep-outs and service access fixed by project review",
            "cleanable UV/chemical-resistant labels, radiused tamper-resistant brackets and protected emergency battery/connector interfaces",
            "equipment serial/batch, label revision/language, battery date, extinguisher/first-aid expiry, seal number and installed location audit",
            evidence + ("accessible reach/contrast review", "emergency-light duration test", "expiry audit", "egress survey"),
        )
    if item.id == "LM3-WIN-P010":
        return MaterialSpec(
            "replaceable aluminium window-retention and elastomer seal kit",
            "6061/6082 plate or 6063 extrusion candidate pressure frame, nonmetallic setting blocks, closed-cell/EPDM seal, aluminium drain rail, and captive stainless retainers",
            "released LM3-WIN-210 retention calculation and drawing plus supplier glazing, aluminium, elastomer, fire, corrosion, and ingress evidence",
            "CNC-cut/extruded pressure-frame segments with keyed dry seal, protected glass-edge clearances, drain path, secondary retention, and cassette jack points",
            "profile, corner joint, fastener pitch, setting blocks, seal compression and glass clearance fixed by the controlled window interface drawing",
            "anodised or coated aluminium, passivated retained hardware, isolated mixed-metal contacts, UV/ozone-resistant seal, and open inspected drains",
            "aluminium batch, seal batch/date, retained-fastener lot, cassette position map, compression record, and water/replacement test",
            evidence + ("retention proof", "seal compression map", "drain test", "water-ingress and replacement trial"),
        )
    if item.id == "LM3-DOOR-P010":
        return MaterialSpec(
            "adjustable steel/stainless door-carrier and replaceable seal kit",
            "calculated S355/304 carrier shoes, hardened datum pins, sealed floating nutplates, galvanic isolators, EPDM perimeter seal, and keyed connector bracket",
            "released LM3-DOOR-200 interface calculation/drawing plus supplier door, fastener, elastomer, corrosion, fire and EN 14752/national evidence as applicable",
            "four separately adjustable carrier shoes on two repeatable datum pins with mechanical locking, dry seal, recorded shim/adjuster map, and body-side keyed connector support",
            "adjustment range, carrier section, fastener grip, pin fit, seal compression and supplier cassette load envelope fixed by the controlled interface drawing",
            "painted/passivated hardware, isolated mixed-metal interfaces, sealed wet-zone nutplates and UV/ozone-resistant replaceable elastomer",
            "hardware heat/batch, pin and fastener lot, seal batch/date, cassette serial, adjuster map, torque record, and replacement test",
            evidence + ("carrier load proof", "datum gauge", "seal map", "door safety and replacement tests"),
        )
    if item.id == "LM3-FIX-P010":
        return MaterialSpec(
            "common extruded aluminium passenger/service datum rail",
            "6063-T6 or equivalent 42 x 18 mm extrusion candidate with 50 mm datum pitch, isolated body feet and floating-nut capture",
            "released LM3-INT-230 rail/attachment calculation plus aluminium, fire, corrosion, shock/vibration and galvanic-isolation evidence",
            "locally cut, drilled and deburred OSR-RAIL-42 lengths with end stops, isolating feet, datum marks and captive floating-nut channels",
            "42 x 18 mm reference section; wall, foot, pitch and nut channel remain controlled drawing dimensions",
            "anodised/coated cleanable finish with isolated steel fasteners, sealed cut ends and no passenger-facing sharp edges",
            "extrusion batch, finish batch, cut list, drill-gauge record, foot/fastener lot and installed rail survey",
            evidence + ("rail pull-out/slip proof", "datum survey", "galvanic-isolation check"),
        )
    if item.id == "LM3-FIX-P030":
        return MaterialSpec(
            "calculated passenger-fixture saddle and adapter family",
            "laser-cut/folded 304/316 or coated S355 saddles with radiused edges, anti-rotation keys, isolators and M8 captive/floating joints",
            "fixture-specific released load calculation/drawing plus material, fastener, fire, corrosion, proof-load and passenger-safety evidence",
            "common rail-side saddle blank CNC-trimmed/drilled into seat, handrail and equipment variants without transferring primary loads through trim panels",
            "rail engagement, edge radius, anti-rotation feature, hole/slot range and fixture keep-out fixed by the controlled adapter drawing",
            "passivated or coated surfaces, electrically/galvanically isolated interfaces and cleanable snag-free passenger edges",
            "material/finish batch, adapter variant, fastener lot, installed position map, torque/locking record and first-article proof test",
            evidence + ("adapter gauge", "fixture load proof", "egress and snag inspection"),
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
        if item.id == "LM3-WIN-P010":
            return ProcessSpec(
                ("receive and edge-inspect supplier cassette", "machine and deburr pressure frame", "gauge aperture and drains", "dry-fit on protected setting blocks", "install keyed seal and pressure frame", "cross-pattern tighten", "water and timed replacement test"),
                ("supplier cassette bond retained within its aluminium frame", "replaceable dry elastomer compression seal", "captive pressure-frame fasteners", "nonmetallic setting blocks and secondary retention"),
                ("released retention calculation and window interface drawing", "no glass-edge metal contact", "seal batch and compression map", "supplier surface-preparation/adhesive evidence", "open drain and mixed-metal isolation checks"),
                tuple(dict.fromkeys(("edge inspection", "aperture/pressure-frame gauge", "seal compression measurement", "drain-flow test", "heater/isolation test where fitted", "controlled spray test", "timed cassette removal/refit", *item.acceptance))),
                "LM3-TOOL-WINDOW-GAUGE plus LM3-TOOL-WATER-TEST",
                "design-reference window route; drawing, retention proof, supplier and first-article evidence required before release",
            )
        if item.id == "LM3-DOOR-P010":
            return ProcessSpec(
                ("fabricate and gauge four carrier shoes", "accept supplier cassette", "gauge body portal", "lift, pin and adjust cassette", "close sealed joints and keyed services", "static safety tests", "water and timed replacement test"),
                ("four adjustable calculated carrier shoes", "two repeatable datum pins", "sealed high-integrity fasteners", "replaceable perimeter seal", "keyed body-side connector bracket"),
                ("released carrier calculation and interface drawing", "supplier lift/installation procedure", "adjustment-range and shim map", "joint/locking schedule", "seal compression map", "door safety-test script"),
                tuple(dict.fromkeys(("carrier gauge and proof", "leaf/aperture survey", "closed-and-locked loop", "obstacle and traction-interlock test", "emergency/manual release", "water test", "timed cassette removal/refit", *item.acceptance))),
                "LM3-TOOL-DOOR-GAUGE plus LM3-TOOL-SEAL-GAUGE",
                "design-reference door interface; supplier freeze, structural proof and applicable door-system acceptance remain mandatory",
            )
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
    payload: dict[str, object] = {
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
    anchor = _supplier_anchor_payload(item.id)
    if anchor is not None:
        payload["supplier_anchor"] = anchor
    return payload


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
        return "exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route"
    if "bogie" in text or "wheelset" in text or "motor" in text or "gearbox" in text or "brake" in text:
        return "bogie frame, axle, brake, suspension, and underframe marriage datums"
    if "cowl" in text or "coupler" in text or "sensor" in text or "nose" in text:
        return "train-end cowl, crash, coupler, and sensor datum stack"
    if "articulation" in text or "gangway" in text or "jumper" in text:
        return "inter-car articulation, gangway, trainline, and flexible-service envelope"
    if "interior" in text or "seat" in text or "saloon" in text:
        return "saloon interior, PRM aisle, ceiling, and service-panel zone"
    if child_id.startswith(("LM3-FIX", "LM3-LGT")) or "lighting" in text or "fixture" in text:
        return "common OSR-RAIL-42 interior datum and keyed low-voltage service zone"
    if "control" in text or "t-ecu" in text or "trainline" in text or "harness" in text:
        return "LV cabinet, trainline, network, and diagnostic harness zone"
    return "primary structure datum and final assembly interface"


def _interface_classes(child_id: str, title: str) -> list[str]:
    text = f"{child_id} {title}".lower()
    classes: list[str] = ["mechanical datum"]
    if any(word in text for word in ("hv", "battery", "inverter", "motor", "pv", "contactor", "charging", "resistor")):
        classes.append("high-voltage electrical")
    if any(word in text for word in ("control", "t-ecu", "sensor", "wsp", "harness", "trainline", "antenna", "pis", "cctv", "lighting", "connector")):
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
    service_rail_hardware = child_id.startswith(("LM3-FIX", "LM3-LGT"))
    cassette_hardware = child_id in {"LM3-WIN-P010", "LM3-DOOR-P010"}
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
    if (
        any(word in text for word in ("composite", "fiberglass", "glazing", "window", "pv bonded"))
        and not dry_clip_body
        and not cassette_hardware
    ):
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

    # These classes keep small service hardware out of the bespoke structural
    # joint bucket without relaxing passenger-fixture or cassette load gates.
    if service_rail_hardware:
        classes.append("service-rail-captive-fastener")
    elif cassette_hardware:
        classes.append("cassette-floating-fastener")
    else:
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
    if "service-rail-captive-fastener" in join_classes:
        return (
            "released OSR small-component standard plus accepted hardware batch and calibrated-tool procedure",
            "standard-hardware-release-required",
        )
    if "cassette-floating-fastener" in join_classes:
        return (
            "released cassette interface drawing and calculation plus supplier installation manual",
            "cassette-interface-release-required",
        )
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
    ]
    anchor = _supplier_anchor_payload(item.id)
    if anchor is not None:
        lines.extend(
            [
                "## Supplier anchor and local-equivalent route",
                "",
                f"- Anchor: `{anchor['id']}` — [{anchor['manufacturer']} {anchor['product_family']}]({anchor['manufacturer_url']})",
                f"- Procurement state: `{anchor['procurement_state']}`",
                f"- Local equivalent allowed: yes, after the controlled equivalence dossier",
                f"- Localisation route: {anchor['localisation']}",
                f"- Known fit gaps: {'; '.join(anchor['fit_gaps'])}",
                "- Mandatory equivalence:",
            ]
        )
        lines.extend(f"  - {rule}" for rule in anchor["mandatory_equivalence"])
        lines.append("")
    lines.extend(
        [
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
        "Generated by `tools/automation/buildable-trainset.sh` from the product tree in",
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
        "Generated by `tools/automation/buildable-trainset.sh`. These are signable",
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


def trainset_build_cost_payload(design: BuildableTrainsetDesign) -> dict[str, object]:
    """Return the explicit build-cost rollup for one three-car LM3 trainset."""

    direct_material_and_supplier_cost_usd = float(design.candidate.metrics["cost_usd"])
    included_fitout_scope = [
        {
            "scope": "seats, floors, grab rails, and interior lighting",
            "bom_lines": ["B12", "B13", "B14", "B15", "B16"],
            "basis": "floor boards/hatches, floor covering, 60 longitudinal seats, grab rails, and three-car LED lighting kit",
            "included_base_usd": 17_500.0,
        },
        {
            "scope": "roof HVAC",
            "bom_lines": ["T14"],
            "basis": "three direct-HV DC 24 kW roof HVAC units, one per car",
            "included_base_usd": 17_250.0,
        },
        {
            "scope": "side windows, side doors, door sill/emergency kits, and panoramic end glass",
            "bom_lines": ["B10", "B11", "B25", "B27"],
            "basis": "18 laminated side-window cassettes, 12 powered door cassettes, sill/emergency kits, and two panoramic end-glass assemblies",
            "included_base_usd": 112_000.0,
        },
    ]
    critical = critical_path_payload(design)
    labor_hours = float(critical["total_labor_hours"])
    labor_cost_usd = labor_hours * BUILD_COST_LABOR_RATE_USD_PER_HOUR
    subtotal_before_premium_usd = direct_material_and_supplier_cost_usd + labor_cost_usd
    unexpected_cost_premium_usd = subtotal_before_premium_usd * BUILD_COST_UNEXPECTED_PREMIUM_FRACTION
    total_build_cost_usd = subtotal_before_premium_usd + unexpected_cost_premium_usd
    return {
        "document_revision": "A-DRAFT",
        "release_status": "rough-order planning; not a supplier quote or signed production budget",
        "candidate": design.candidate.id,
        "family": design.family.value,
        "cars_per_trainset": int(design.candidate.metrics["cars"]),
        "currency": "USD",
        "direct_material_and_supplier_cost_usd": round(direct_material_and_supplier_cost_usd, 2),
        "labor_hours": round(labor_hours, 1),
        "labor_rate_usd_per_hour": BUILD_COST_LABOR_RATE_USD_PER_HOUR,
        "labor_cost_usd": round(labor_cost_usd, 2),
        "subtotal_before_premium_usd": round(subtotal_before_premium_usd, 2),
        "unexpected_cost_premium_fraction": BUILD_COST_UNEXPECTED_PREMIUM_FRACTION,
        "unexpected_cost_premium_usd": round(unexpected_cost_premium_usd, 2),
        "total_build_cost_usd": round(total_build_cost_usd, 2),
        "rounded_local_owner_unit_usd": 900_000,
        "included_fitout_doors_glazing_scope": included_fitout_scope,
        "included_fitout_doors_glazing_total_base_usd": round(
            sum(float(row["included_base_usd"]) for row in included_fitout_scope), 2
        ),
        "basis": (
            "Direct material and supplier-module cost comes from the promoted design candidate; "
            "labour hours come from the generated critical-path plan; the 20% premium covers "
            "unexpected local fabrication, rework, logistics, consumables, and shop-learning costs."
        ),
        "exclusions": [
            "route/platform compatibility changes",
            "supplier certification and homologation campaigns",
            "warranty and initial spares",
            "production-plant fixtures and tooling carried in the separate plant allowance",
        ],
    }


def render_trainset_build_cost(design: BuildableTrainsetDesign) -> str:
    payload = trainset_build_cost_payload(design)
    premium_pct = 100.0 * float(payload["unexpected_cost_premium_fraction"])
    lines = [
        "# LM3 trainset build cost estimate",
        "",
        "Generated by `tools/automation/buildable-trainset.sh`. This is a rough-order",
        "build cost for one three-car LM3 trainset using the updated modular",
        "glass-fibre body, explicit assembly labour plan, and requested",
        "unexpected-cost premium.",
        "",
        f"- Candidate: `{payload['candidate']}`",
        f"- Family: `{payload['family']}`",
        f"- Release status: {payload['release_status']}",
        "",
        "| Cost bucket | Basis | Cost |",
        "|---|---|---:|",
        "| Direct material and supplier modules | Promoted design candidate cost metric | "
        f"${float(payload['direct_material_and_supplier_cost_usd']):,.0f} |",
        "| Direct labour | "
        f"{float(payload['labor_hours']):,.0f} h at ${float(payload['labor_rate_usd_per_hour']):,.0f}/h | "
        f"${float(payload['labor_cost_usd']):,.0f} |",
        "| Subtotal before premium | Material/supplier modules plus direct labour | "
        f"${float(payload['subtotal_before_premium_usd']):,.0f} |",
        f"| Unexpected-cost premium | {premium_pct:.0f}% for rework, logistics, consumables, local fabrication variation, and shop learning | "
        f"${float(payload['unexpected_cost_premium_usd']):,.0f} |",
        "| **Total per 3-car trainset** | Recalculated build estimate | "
        f"**${float(payload['total_build_cost_usd']):,.0f}** |",
        "| Rounded local-owner planning unit | Retained city-CAPEX reporting bucket | "
        f"${float(payload['rounded_local_owner_unit_usd']):,.0f} |",
        "",
        "## Basis",
        "",
        str(payload["basis"]),
        "",
        "## Included Fit-Out, Doors, And Glazing Scope",
        "",
        "The direct material and supplier-module bucket already includes the",
        "interior fit-out, HVAC, windows, and doors below; do not add a",
        "second $20k interior allowance unless a separate contingency is",
        "intentionally being carried.",
        "",
        "| Included scope | BOM lines | Included base cost |",
        "|---|---|---:|",
    ]
    lines.extend(
        "| "
        f"{row['scope']} | "
        f"{', '.join(str(line) for line in row['bom_lines'])} | "
        f"${float(row['included_base_usd']):,.0f} |"
        for row in payload["included_fitout_doors_glazing_scope"]  # type: ignore[index]
    )
    lines.extend(
        [
            "| **Requested scope total** | Seats/floors/lighting + HVAC + doors/windows/end glass | "
            f"**${float(payload['included_fitout_doors_glazing_total_base_usd']):,.0f}** |",
            "",
            "The seats/floors/grab-rail/lighting subset is $17,500, close to",
            "the $20k check value. HVAC adds $17,250, and doors/glazing add",
            "$112,000 before labour and premium.",
            "",
        ]
    )
    lines.extend(
        [
            "Exclusions:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["exclusions"])  # type: ignore[index]
    lines.append("")
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
        "Generated by `tools/automation/buildable-trainset.sh`. This is a rough-order",
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


def factory_plan_payload(design: BuildableTrainsetDesign) -> dict[str, object]:
    """Return a first-pass factory sizing and machinery plan for one LM3 line."""

    tasks = {str(task["id"]): task for task in _scheduled_critical_path_tasks()}

    def rollup(task_ids: tuple[str, ...], label: str) -> dict[str, object]:
        rows = [tasks[task_id] for task_id in task_ids]
        start = min(float(row["early_start_day"]) for row in rows)
        finish = max(float(row["early_finish_day"]) for row in rows)
        labor = sum(float(row["labor_hours"]) for row in rows)
        event_days = sorted(
            {float(row["early_start_day"]) for row in rows}
            | {float(row["early_finish_day"]) for row in rows}
        )
        sample_days = [(a + b) / 2.0 for a, b in zip(event_days, event_days[1:])]
        peak_crew = max(
            (
                sum(
                    float(row["crew_equivalent"])
                    for row in rows
                    if float(row["early_start_day"]) <= sample_day < float(row["early_finish_day"])
                )
                for sample_day in sample_days
            ),
            default=0.0,
        )
        return {
            "id": label,
            "task_ids": list(task_ids),
            "early_start_day": round(start, 1),
            "early_finish_day": round(finish, 1),
            "elapsed_window_days": round(finish - start, 1),
            "touch_labor_hours": round(labor, 1),
            "peak_parallel_crew_equivalent": round(peak_crew, 1),
        }

    process_cells = [
        {
            "id": "FP-CELL-010",
            "name": "steel prep and chassis parts cell",
            "qty": 1,
            "nominal_dimensions_m": "18 x 10",
            "net_area_m2": 180,
            "supports": ["CP-020"],
            "included_work": "saw/plasma cutting, press-brake forming, drilling, deburr, and three-car chassis/body kitting",
        },
        {
            "id": "FP-CELL-020",
            "name": "chassis weld and body-frame fixture cell",
            "qty": 1,
            "nominal_dimensions_m": "32 x 20",
            "net_area_m2": 640,
            "supports": ["CP-030", "CP-040"],
            "included_work": "two underframe rotating fixtures, two side/roof frame fixtures, local bolster/coupler subfixtures, weld extraction, and fixture survey access",
        },
        {
            "id": "FP-CELL-030",
            "name": "composite moulding, cure, trim, and dry-fit cell",
            "qty": 1,
            "nominal_dimensions_m": "22 x 12",
            "net_area_m2": 264,
            "supports": ["CP-060", "CP-080"],
            "included_work": "four short GFRP moulds, lay-up tables, cure racks, CNC trim/drill table, master-frame dry-fit stand, and module staging",
        },
        {
            "id": "FP-CELL-040",
            "name": "paint and corrosion protection cell",
            "qty": 1,
            "nominal_dimensions_m": "28 x 12",
            "net_area_m2": 336,
            "supports": ["CP-070"],
            "included_work": "one car-length paint booth, prep/mask lane, flash-off/inspection space, seam-seal and cavity-wax station",
        },
        {
            "id": "FP-CELL-050",
            "name": "bogie assembly and test cell",
            "qty": 1,
            "nominal_dimensions_m": "20 x 12",
            "net_area_m2": 240,
            "supports": ["CP-050", "CP-120"],
            "included_work": "three bogie stands, wheelset lane, brake/sensor bench, ride-height setup, and bogie-to-car marriage support tools",
        },
        {
            "id": "FP-CELL-060",
            "name": "interior, HVAC duct, harness, and supplier kit bench",
            "qty": 1,
            "nominal_dimensions_m": "16 x 10",
            "net_area_m2": 160,
            "supports": ["CP-065", "CP-110"],
            "included_work": "seat/grab-rail racks, floor and liner trim bench, lighting/PIS/CCTV label bench, quarantine shelves, and car-zone kitting",
        },
        {
            "id": "FP-CELL-070",
            "name": "final assembly, bogie marriage, and static-test track",
            "qty": 1,
            "nominal_dimensions_m": "60 x 10",
            "net_area_m2": 600,
            "supports": ["CP-090", "CP-100", "CP-110", "CP-120", "CP-130", "CP-140"],
            "included_work": "one 55 m controlled train bay with side access, roof platforms, HV lockout, shore power, charge simulator, jacks/mobile columns, and end-cowl stands",
        },
        {
            "id": "FP-CELL-080",
            "name": "stores, incoming inspection, QA, toolroom, and offices",
            "qty": 1,
            "nominal_dimensions_m": "28 x 14",
            "net_area_m2": 392,
            "supports": ["CP-010"],
            "included_work": "controlled document desk, stores, receiving inspection, calibrated-tool cage, NCR quarantine, compressor/electrical room, and welfare/office space",
        },
    ]
    net_process_area_m2 = sum(int(cell["net_area_m2"]) for cell in process_cells)
    circulation_and_services_m2 = round(net_process_area_m2 * 0.25)
    enclosed_area_m2 = net_process_area_m2 + circulation_and_services_m2
    outside_area_m2 = 2_200

    machinery = [
        ("M-010", "4x8 or 5x10 CNC plasma table with extraction", 1, 20_000, "steel prep", "CNC plasma listings show 4x8 tables roughly in the $7k-$17k range; allowance includes extraction and industrialization."),
        ("M-020", "RHS/tube saw and general fabrication saws", 2, 6_000, "steel prep", "Shop-floor allowance for repeatable chassis tube cutting and backup saw capacity."),
        ("M-030", "100-160 t CNC press brake", 1, 45_000, "steel prep", "Market check shows low FOB offers around $18k and local/dealer reality nearer $45k for 100 t class machines."),
        ("M-040", "drill/mill/magnetic-drill and deburr package", 1, 18_000, "steel prep", "Datum holes, inserts, fixtures, bracket slots, and local machining support."),
        ("M-050", "500 A MIG/MAG welding sets", 8, 2_000, "weld cell", "Industrial 500 A MIG/MAG machines are commonly listed from sub-$1k FOB to around $1.5k-$2.5k retail; allowance includes torches/leads."),
        ("M-060", "weld fume extraction and screens", 1, 25_000, "weld cell", "Shared extraction, curtains, and local arms for two long fixtures plus bracket benches."),
        ("M-070", "underframe rotating weld fixtures", 2, 40_000, "weld cell", "Custom datum tooling for 16.5 m chassis underframes."),
        ("M-080", "side/roof frame fixtures", 2, 30_000, "weld cell", "Custom fixtures for door/window portals, roof bows, HVAC rails, and clip-grid datums."),
        ("M-090", "bogie frame fixture, three stands, and brake/sensor bench", 1, 45_000, "bogie cell", "Local assembly tooling for powered/trailer bogie frames and supplier wheelset/brake installation."),
        ("M-100", "10 t bridge/gantry crane coverage and hoists", 2, 37_500, "lifting", "Crane price guides show 10 t single-girder equipment in the high single-digit to low tens of thousands FOB; allowance includes runway/installation margin."),
        ("M-110", "3 t electric forklift", 1, 25_000, "material handling", "2026 3 t electric forklift guide ranges around $18k-$30k for higher-spec lithium machines."),
        ("M-120", "mobile columns/jacks or shallow-pit bogie marriage kit", 1, 75_000, "final assembly", "Heavy-vehicle mobile-column sets range from lower-cost import sets to about $60k+ for branded 72,000 lb sets; allowance covers trainset adaptation."),
        ("M-130", "bus/truck-length paint booth and prep ventilation", 1, 70_000, "paint cell", "Truck/bus booth market checks show roughly $13k-$50k FOB and $80k-$90k for larger custom booths; allowance sits between."),
        ("M-140", "blast/strip prep, seam-seal, and cavity-wax package", 1, 35_000, "paint cell", "Lean in-house prep package; full blast hall can be outsourced or added later."),
        ("M-150", "four short GFRP moulds with trim/drill jigs", 1, 40_000, "composite cell", "Reusable one-metre side/roof mould set plus master trim gauges; no full-car mould."),
        ("M-160", "vacuum infusion/wet-layup pumps, reusable membranes, tables, and cure racks", 1, 20_000, "composite cell", "Vacuum infusion equipment is low-cost at tool level; allowance covers shop-ready pumps, membranes, gauges, and racks."),
        ("M-170", "CNC router/trim table and composite dust extraction", 1, 45_000, "composite cell", "Trim/drill accuracy for side/window/door/roof variants and cabin liners."),
        ("M-180", "metrology, laser level/track, torque tools, and calibrated gauges", 1, 35_000, "QA", "Factory datum surveys, torque control, clip gauges, door/window gauges, and calibration control."),
        ("M-190", "HV insulation, continuity, shore-power, and charge-simulator tools", 1, 70_000, "final assembly", "Static commissioning of HV battery, traction, charging, door/HVAC, and train-control interfaces."),
        ("M-200", "interior trim benches, carts, racks, and hand tools", 1, 25_000, "interior cell", "Pre-kitting seats, floors, lighting, liners, PIS/CCTV, and labels by car zone."),
        ("M-210", "factory IT, traveler terminals, printers, labels, and document control", 1, 15_000, "production control", "Shop traveler, QR label, NCR, and QA evidence capture support."),
    ]
    machinery_rows = [
        {
            "id": item_id,
            "item": item,
            "quantity": qty,
            "unit_cost_usd": unit_cost,
            "extended_cost_usd": qty * unit_cost,
            "cell": cell,
            "basis": basis,
        }
        for item_id, item, qty, unit_cost, cell, basis in machinery
    ]
    machinery_subtotal_usd = sum(int(row["extended_cost_usd"]) for row in machinery_rows)
    setup_contingency_usd = round(machinery_subtotal_usd * 0.20)
    machinery_total_usd = machinery_subtotal_usd + setup_contingency_usd

    return {
        "document_revision": "A-DRAFT",
        "release_status": "rough-order planning; not a lease plan or equipment RFQ",
        "family": design.family.value,
        "candidate": design.candidate.id,
        "planning_basis": (
            "minimum pilot factory for one first-article LM3 three-car trainset at a time; "
            "one 55 m final assembly bay; chassis, bogies, moulded GFRP modules, and interiors run off-line in parallel"
        ),
        "factory_size": {
            "net_process_area_m2": net_process_area_m2,
            "circulation_services_and_safety_allowance_fraction": 0.25,
            "circulation_services_and_safety_area_m2": circulation_and_services_m2,
            "recommended_enclosed_factory_area_m2": enclosed_area_m2,
            "recommended_enclosed_factory_area_ft2": round(enclosed_area_m2 * 10.7639),
            "outside_yard_and_test_apron_m2": outside_area_m2,
            "outside_yard_and_test_apron_ft2": round(outside_area_m2 * 10.7639),
            "minimum_clear_height_m": "6 m general, 8 m preferred over final bay and weld/fixture cell",
            "dynamic_test_track": "separate short depot/test track, nominal 150-300 m plus charging interface; not counted in enclosed factory area",
        },
        "process_cells": process_cells,
        "assembly_time_rollups": [
            rollup(("CP-020", "CP-030", "CP-040", "CP-070"), "chassis and painted carbody frame fabrication"),
            rollup(("CP-050", "CP-120"), "bogie build and bogie-to-carbody integration"),
            rollup(("CP-060", "CP-080"), "GFRP moulding and clip-on body installation"),
            rollup(("CP-065", "CP-110"), "interior furnishing pre-kit and installation"),
            rollup(("CP-090", "CP-100", "CP-110", "CP-120", "CP-130", "CP-140"), "final assembly and static commissioning"),
            rollup(("CP-150",), "dynamic commissioning and trial-running release"),
        ],
        "production_takt_scenarios": [
            {
                "scenario": "first article / learning build",
                "trainsets_per_year": 4,
                "basis": "35 working-day elapsed build with protected rework float and one final bay",
                "final_bays_required": 1,
            },
            {
                "scenario": "low-rate repeat build",
                "trainsets_per_year": 8,
                "basis": "25 working-day repeat takt after fixtures, supplier kits, and QA gates are stable",
                "final_bays_required": 1,
            },
            {
                "scenario": "steady modular local production",
                "trainsets_per_year": 12,
                "basis": "20 working-day repeat takt; add second final bay only if static commissioning or supplier rework blocks the first bay",
                "final_bays_required": 1,
            },
        ],
        "machinery": machinery_rows,
        "machinery_cost": {
            "machinery_subtotal_usd": machinery_subtotal_usd,
            "setup_contingency_fraction": 0.20,
            "setup_contingency_usd": setup_contingency_usd,
            "rough_order_machinery_total_usd": machinery_total_usd,
            "exclusions": [
                "land, building shell, leasehold works, taxes, freight, duty, and utility connection upgrades",
                "full homologation test laboratory and destructive crash/fire testing rigs",
                "working capital, warranty spares, and production payroll",
            ],
        },
        "market_anchor_sources": [
            {
                "scope": "press brake",
                "source": "Alibaba/ADHMT 2026 press-brake market notes",
                "url": "https://pressbrake.adhmt.com/the-alibaba-press-brake-illusion-why-a-15000-cnc-machine-can-cost-50000/",
            },
            {
                "scope": "CNC plasma table",
                "source": "StyleCNC 2026 4x8 CNC plasma table listings",
                "url": "https://www.stylecnc.com/plasma-cutter/cnc-plasma-cutting-table.html",
            },
            {
                "scope": "truck/bus paint booth",
                "source": "Made-in-China 2026 bus spray booth listings",
                "url": "https://wldspraybooth.en.made-in-china.com/product-group/jbKGuNtwSgWs/Bus-Spray-Booth-1.html",
            },
            {
                "scope": "vacuum infusion equipment",
                "source": "Easy Composites vacuum bagging/infusion equipment listings",
                "url": "https://www.easycomposites.eu/vacuum-bagging-for-resin-infusion",
            },
            {
                "scope": "cranes",
                "source": "Voitto Crane 2026 overhead crane price guide",
                "url": "https://www.voittocrane.com/blog/overhead-crane-for-sale",
            },
            {
                "scope": "mobile column lifts",
                "source": "BendPak mobile column lift listings",
                "url": "https://www.bendpak.com/car-lifts/mobile-column-lifts/",
            },
            {
                "scope": "forklift",
                "source": "Hongli 2026 3-ton electric forklift guide",
                "url": "https://hongli-mach.com/7-best-3-ton-electric-forklift-china-2026/",
            },
        ],
    }


def render_factory_plan(design: BuildableTrainsetDesign) -> str:
    payload = factory_plan_payload(design)
    size = dict(payload["factory_size"])  # type: ignore[arg-type]
    machinery_cost = dict(payload["machinery_cost"])  # type: ignore[arg-type]
    lines = [
        "# LM3 pilot factory sizing and machinery plan",
        "",
        "Generated by `tools/automation/buildable-trainset.sh`. This is a rough-order",
        "factory layout and machinery plan for the basic three-car LM3 trainset.",
        "It sizes a lean pilot plant, not a turnkey rolling-stock works.",
        "",
        f"- Family: `{payload['family']}`",
        f"- Candidate: `{payload['candidate']}`",
        f"- Planning basis: {payload['planning_basis']}",
        f"- Recommended enclosed factory: **{size['recommended_enclosed_factory_area_m2']:,.0f} m2** ({size['recommended_enclosed_factory_area_ft2']:,.0f} ft2)",
        f"- Outside yard/test apron: **{size['outside_yard_and_test_apron_m2']:,.0f} m2** ({size['outside_yard_and_test_apron_ft2']:,.0f} ft2)",
        f"- Dynamic test track: {size['dynamic_test_track']}",
        f"- Rough-order machinery/setup: **${float(machinery_cost['rough_order_machinery_total_usd']):,.0f}** including {float(machinery_cost['setup_contingency_fraction']) * 100:.0f}% setup contingency",
        "",
        "## Factory Area By Cell",
        "",
        "| Cell | Area | Supports | Included work |",
        "|---|---:|---|---|",
    ]
    for cell in payload["process_cells"]:  # type: ignore[index]
        row = dict(cell)
        lines.append(
            f"| {row['name']} | {int(row['net_area_m2']):,} m2 ({row['nominal_dimensions_m']} m) | "
            f"{', '.join(f'`{task}`' for task in row['supports'])} | {row['included_work']} |"
        )
    lines.extend(
        [
            f"| Circulation, services, safety aisles | {int(size['circulation_services_and_safety_area_m2']):,} m2 | all cells | 25% allowance over net process cells for forklifts, carts, fire egress, utilities, compressors, and WIP buffering |",
            f"| **Total enclosed factory** | **{int(size['recommended_enclosed_factory_area_m2']):,} m2** | all cells | Minimum recommended lease/building area before offices are expanded or production rate is increased |",
            "",
            "## Assembly-Time Rollup",
            "",
            "| Scope | Tasks | Start d | Finish d | Elapsed d | Touch labour h | Peak crew eq |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for rollup_row in payload["assembly_time_rollups"]:  # type: ignore[index]
        row = dict(rollup_row)
        lines.append(
            f"| {row['id']} | {', '.join(f'`{task}`' for task in row['task_ids'])} | "
            f"{float(row['early_start_day']):.1f} | {float(row['early_finish_day']):.1f} | "
            f"{float(row['elapsed_window_days']):.1f} | {float(row['touch_labor_hours']):,.0f} | "
            f"{float(row['peak_parallel_crew_equivalent']):.1f} |"
        )
    lines.extend(
        [
            "",
            "## Machinery And Setup Estimate",
            "",
            "| ID | Item | Qty | Unit | Extended | Cell | Basis |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for item in payload["machinery"]:  # type: ignore[index]
        row = dict(item)
        lines.append(
            f"| `{row['id']}` | {row['item']} | {int(row['quantity'])} | "
            f"${float(row['unit_cost_usd']):,.0f} | ${float(row['extended_cost_usd']):,.0f} | "
            f"{row['cell']} | {row['basis']} |"
        )
    lines.extend(
        [
            f"| **Subtotal** |  |  |  | **${float(machinery_cost['machinery_subtotal_usd']):,.0f}** |  |  |",
            f"| Setup contingency | 20% install/adaptation/commissioning allowance |  |  | **${float(machinery_cost['setup_contingency_usd']):,.0f}** |  |  |",
            f"| **Rough-order machinery total** | Excludes building/land/taxes/freight/duty |  |  | **${float(machinery_cost['rough_order_machinery_total_usd']):,.0f}** |  |  |",
            "",
            "## Production Takt Scenarios",
            "",
            "| Scenario | Trainsets/year | Final bays | Basis |",
            "|---|---:|---:|---|",
        ]
    )
    for scenario in payload["production_takt_scenarios"]:  # type: ignore[index]
        row = dict(scenario)
        lines.append(
            f"| {row['scenario']} | {int(row['trainsets_per_year'])} | "
            f"{int(row['final_bays_required'])} | {row['basis']} |"
        )
    lines.extend(
        [
            "",
            "## Exclusions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in machinery_cost["exclusions"])  # type: ignore[index]
    lines.extend(
        [
            "",
            "## Market Anchor Sources",
            "",
            "The equipment costs are rough 2026 planning anchors, not supplier",
            "quotes. Final procurement must replace them with landed, installed,",
            "warranted offers.",
            "",
        ]
    )
    lines.extend(
        f"- {row['scope']}: [{row['source']}]({row['url']})"
        for row in payload["market_anchor_sources"]  # type: ignore[index]
    )
    lines.append("")
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
        "Generated by `tools/automation/buildable-trainset.sh`. This design note records",
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


def render_small_component_standard() -> str:
    """Render the common rail, fastener, connector, light and cassette rules."""

    payload = small_component_standard_payload()
    rail = dict(payload["service_rail"])  # type: ignore[arg-type]
    lighting = dict(payload["lighting"])  # type: ignore[arg-type]
    door = dict(payload["door_interface"])  # type: ignore[arg-type]
    window = dict(payload["window_interface"])  # type: ignore[arg-type]
    lines = [
        "# LM3 small-component and fixture standard",
        "",
        "Generated by `tools/automation/buildable-trainset.sh`. This is the controlled",
        "supplier-neutral design reference for repeatable interior and cassette",
        "hardware. It does not release structural loads or numeric torque values.",
        "",
        f"- Revision: `{payload['document_revision']}`",
        f"- Status: `{payload['release_status']}`",
        f"- Principle: {payload['principle']}",
        "",
        "## Common datum rail",
        "",
        f"- ID: `{rail['id']}`",
        f"- Section: `{rail['nominal_section_mm'][0]} × {rail['nominal_section_mm'][1]} mm`",  # type: ignore[index]
        f"- Datum pitch: `{rail['datum_pitch_mm']} mm`",
        f"- Material/interface: {rail['material']}",
        "- Functions: " + "; ".join(rail["functions"]),  # type: ignore[arg-type]
        "- Release evidence: " + "; ".join(rail["release_evidence"]),  # type: ignore[arg-type]
        "",
        "## Four fastener families",
        "",
        "| ID | Nominal arrangement | Intended uses | Prohibited uses | Installation control | Release authority |",
        "|---|---|---|---|---|---|",
    ]
    for raw in payload["fastener_families"]:  # type: ignore[union-attr]
        row = dict(raw)
        lines.append(
            f"| `{row['id']}` | {row['nominal']} | {'; '.join(row['intended_uses'])} | "
            f"{'; '.join(row['prohibited_uses'])} | {row['installation_control']} | {row['release_authority']} |"
        )
    lines.extend(
        [
            "",
            "## Keyed connector families",
            "",
            "| ID | Service | Interface | Keying | Release evidence |",
            "|---|---|---|---|---|",
        ]
    )
    for raw in payload["connector_families"]:  # type: ignore[union-attr]
        row = dict(raw)
        lines.append(
            f"| `{row['id']}` | {row['service']} | {row['interface']} | {row['keying']} | "
            f"{'; '.join(row['release_evidence'])} |"
        )
    lines.extend(
        [
            "",
            "## Modular illumination",
            "",
            f"- Main modules per car: `{lighting['main_modules_per_car']}` × `{lighting['module_length_mm']} mm`.",
            f"- Independent emergency modules per car: `{lighting['emergency_modules_per_car']}`.",
            f"- Door-threshold modules per car: `{lighting['door_threshold_modules_per_car']}`.",
            f"- Replacement rule: {lighting['replacement_rule']}",
            "",
            "## Door cassette boundary",
            "",
            f"- Supplier boundary: {door['boundary']}",
            f"- OSR interface: {door['osr_interface']}",
            f"- Release gate: {door['release_gate']}",
            "",
            "## Window cassette boundary",
            "",
            f"- Supplier boundary: {window['boundary']}",
            f"- OSR interface: {window['osr_interface']}",
            f"- Replacement rule: {window['replacement_rule']}",
            f"- Release gate: {window['release_gate']}",
            "",
            "## Design sources",
            "",
        ]
    )
    for raw in payload["authoritative_references"]:  # type: ignore[union-attr]
        source = dict(raw)
        lines.append(f"- [{source['title']}]({source['url']}): {source['use']}.")
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
    build_cost_json = out_dir / "trainset-build-cost.json"
    build_cost_md = out_dir / "trainset-build-cost.md"
    joints_json = out_dir / "joint-control-schedule.json"
    joints_md = out_dir / "joint-control-schedule.md"
    critical_json = out_dir / "critical-path.json"
    critical_md = out_dir / "critical-path.md"
    factory_json = out_dir / "factory-plan.json"
    factory_md = out_dir / "factory-plan.md"
    end_interface_json = out_dir / "train-end-interface.json"
    end_interface_md = out_dir / "train-end-interface.md"
    small_components_json = out_dir / "small-component-standard.json"
    small_components_md = out_dir / "small-component-standard.md"
    manifest_json.write_text(
        json.dumps(asdict(design), default=_serialise, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest_md.write_text(render_manifest(design), encoding="utf-8")
    review_md.write_text(render_review(design), encoding="utf-8")
    gaps_md.write_text(render_open_release_gaps(design), encoding="utf-8")
    mass_json.write_text(json.dumps(mass_budget_payload(design), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    mass_md.write_text(render_mass_budget(design), encoding="utf-8")
    build_cost_json.write_text(
        json.dumps(trainset_build_cost_payload(design), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    build_cost_md.write_text(render_trainset_build_cost(design), encoding="utf-8")
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
    factory_json.write_text(json.dumps(factory_plan_payload(design), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    factory_md.write_text(render_factory_plan(design), encoding="utf-8")
    end_interface_json.write_text(
        json.dumps(train_end_interface_payload(design), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    end_interface_md.write_text(render_train_end_interface(design), encoding="utf-8")
    small_components_json.write_text(
        json.dumps(small_component_standard_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    small_components_md.write_text(render_small_component_standard(), encoding="utf-8")
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
        "Generated by `tools/automation/buildable-trainset.sh`. This is the first structured",
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
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare every generated buildable-trainset file with the tracked output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    design = buildable_trainset_design(ConsistFamily(args.family))
    if args.check:
        with tempfile.TemporaryDirectory(prefix="osr-buildable-trainset-check-") as temporary:
            temporary_root = Path(temporary)
            write_outputs(design, temporary_root)
            stale = []
            for expected in sorted(path for path in temporary_root.rglob("*") if path.is_file()):
                relative = expected.relative_to(temporary_root)
                current = args.out / relative
                if not current.is_file() or current.read_bytes() != expected.read_bytes():
                    stale.append(str(relative))
            if stale:
                raise SystemExit("stale generated buildable-trainset files: " + ", ".join(stale))
        print(f"buildable trainset current: {len(design.product_items)} products / {len(design.assemblies)} assemblies")
        return
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

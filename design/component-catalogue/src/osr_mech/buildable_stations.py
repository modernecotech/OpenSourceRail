"""Generate station engineering BOMs and matched assembly travelers.

The station template is the operational source of truth.  This generator turns
each configured archetype into a quantified product tree using the canonical
platform and canopy geometry, then emits a CSV EBOM/MBOM and a traveler whose
steps use the same stable ``STN-*`` identifiers.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

from osr_mech.civil.platform_l_unit import units_per_platform
from osr_mech.common import ConsistFamily, StationArchetype, archetype_platform_length_m
from osr_mech.depot import throat_turnout_count
from osr_mech.station.canopy import bay_count
from osr_mech.station.auxiliary_canopy import (
    AUX_MODULE_AREA_M2,
    auxiliary_canopy_kwp,
    auxiliary_foundation_count,
    auxiliary_frame_count,
    auxiliary_installed_area_m2,
    auxiliary_module_count,
)
from osr_mech.station.portal import BAY_SPACING_MM, PLATFORM_DEPTH_MM
from osr_mech.station.solar_roof import EAVE_OVERHANG_MM
from osr_mech.track.turnout import CATALOGUE as TURNOUT_CATALOGUE
from osr_mech.track.turnout import TurnoutTangent


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_TEMPLATE = REPO_ROOT / "lib/templates/stations.toml"
DEFAULT_DEPOT_TEMPLATE = REPO_ROOT / "lib/templates/depots.toml"
DEFAULT_CATALOG_DIR = REPO_ROOT / "design/component-catalogue/catalog/buildable-stations"
DEFAULT_BOM_DIR = REPO_ROOT / "build/bom/stations"


@dataclass(frozen=True)
class StationProductItem:
    id: str
    title: str
    route: str
    quantity: float
    unit: str
    parent: str
    maturity: str
    quantity_basis: str
    acceptance: tuple[str, ...]
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class StationAssemblyNode:
    id: str
    title: str
    children: tuple[str, ...]
    work_cell: str
    instructions: tuple[str, ...]
    hold_points: tuple[str, ...]


@dataclass(frozen=True)
class StationVariant:
    archetype: str
    consist: str
    parameters: dict[str, str | float | int | bool]
    product_items: tuple[StationProductItem, ...]
    assemblies: tuple[StationAssemblyNode, ...]
    baseline_exclusions: tuple[str, ...]


FARE_EQUIPMENT: dict[StationArchetype, tuple[int, int]] = {
    StationArchetype.HALT: (0, 0),
    StationArchetype.STANDARD: (4, 2),
    StationArchetype.MAJOR: (6, 4),
    StationArchetype.INTERCHANGE: (8, 4),
    StationArchetype.INTERCHANGE_ELEVATED: (8, 4),
    StationArchetype.TERMINAL: (6, 4),
    StationArchetype.DEPOT_TERMINAL: (6, 4),
}


def _item(
    item_id: str,
    title: str,
    route: str,
    quantity: float,
    unit: str,
    parent: str,
    basis: str,
    acceptance: tuple[str, ...],
    refs: tuple[str, ...],
    maturity: str = "release-candidate",
) -> StationProductItem:
    return StationProductItem(
        item_id,
        title,
        route,
        quantity,
        unit,
        parent,
        maturity,
        basis,
        acceptance,
        refs,
    )


def _template_archetypes(template: Path) -> dict[str, dict[str, object]]:
    raw = tomllib.loads(template.read_text(encoding="utf-8"))
    return raw["archetypes"]


def _main_depot_reference() -> dict[str, object]:
    """Return the controlled reference scope co-located at depot-terminal."""

    raw = tomllib.loads(DEFAULT_DEPOT_TEMPLATE.read_text(encoding="utf-8"))
    return raw["archetypes"]["main-heavy"]


def station_variant(
    archetype: StationArchetype,
    config: dict[str, object],
    consist: ConsistFamily = ConsistFamily.LIGHT_METRO_3CAR,
) -> StationVariant:
    platform_count = int(config["platform_count"])
    elevated_platform = archetype is StationArchetype.INTERCHANGE_ELEVATED
    platform_length_m = archetype_platform_length_m(archetype, consist)
    units_each = units_per_platform(platform_length_m)
    track_channel_count = max(1, math.ceil(platform_count / 2))
    at_grade_slab_panels = math.ceil(platform_length_m / 6.0) * track_channel_count
    bays_each = bay_count(archetype, consist)
    total_bays = bays_each * platform_count
    total_columns = (bays_each + 1) * platform_count
    platform_edge_m = platform_length_m * platform_count
    platform_canopy_area_m2 = (
        total_bays
        * (BAY_SPACING_MM / 1000.0)
        * ((PLATFORM_DEPTH_MM + EAVE_OVERHANG_MM) / 1000.0)
    )
    site_canopy_target_m2 = float(config["canopy_area_m2"])
    auxiliary_canopy_m2 = max(0.0, site_canopy_target_m2 - platform_canopy_area_m2)
    auxiliary_modules = auxiliary_module_count(auxiliary_canopy_m2)
    auxiliary_installed_m2 = auxiliary_installed_area_m2(auxiliary_modules)
    fare_gates, tvms = FARE_EQUIPMENT[archetype]
    charging_kw = int(config["charging_power_kw"])
    tpss_kva = int(config["tpss_kva"])
    access_bridges = int(config["access_bridge_count"])
    step_free_cores = int(config["step_free_core_count"])
    turnout_count = 1 if bool(config.get("has_turnback_tracks", False)) else 0
    turnout_geometry = TURNOUT_CATALOGUE[TurnoutTangent.T_1_9]

    items: list[StationProductItem] = [
        _item(
            "STN-CIV-P010",
            (
                "precast reinforced-concrete elevated platform L-unit"
                if elevated_platform
                else "6 m ground-level station slab and depressed double-track guideway-channel panel"
            ),
            "MAKE",
            units_each * platform_count if elevated_platform else at_grade_slab_panels,
            "ea",
            "STN-PLT-SA200",
            (
                f"ceil({platform_length_m:g} m / 3 m) × {platform_count} elevated platforms"
                if elevated_platform
                else f"ceil({platform_length_m:g} m / 6 m) × {track_channel_count} at-grade track channels"
            ),
            ("concrete certificate", "dimensional inspection", "lifting-point inspection"),
            (
                ("civil/platform_l_unit.py", "RFC 0010 §4")
                if elevated_platform
                else ("civil/slab.py", "RFC 0010 §4.2", "RFC 0011 §4")
            ),
        ),
        _item(
            "STN-CIV-P020",
            "platform sub-base, levelling pad, grout, and closure-pour kit",
            "MAKE",
            platform_count,
            "platform kit",
            "STN-PLT-SA200",
            "one placement and closure kit per configured platform",
            ("compaction test", "grout batch record", "finished-level survey"),
            ("civil/platform_l_unit.py", "RFC 0011"),
        ),
        _item(
            "STN-CIV-P030",
            "platform and track drainage channel, pipe, catch-pit, and outlet kit",
            "MAKE",
            platform_edge_m,
            "m",
            "STN-CIV-SA100",
            "platform length × configured platform count",
            ("invert survey", "flow test", "outfall approval"),
            ("standard-archetype/services.md", "OSR-STD-M-002"),
        ),
        _item(
            "STN-CIV-P040",
            "3 m at-grade guideway-channel edge beam, coping/tactile carrier, and drained service trough",
            "MAKE",
            0 if elevated_platform else units_each * platform_count,
            "edge module",
            "STN-PLT-SA200",
            "one controlled edge module per 3 m of at-grade boarding edge",
            ("concrete certificate", "350 mm platform/ToR datum survey", "coping/gap survey", "drainage flow test"),
            ("civil/guideway_channel_edge.py", "RFC 0010 §4.2", "OSR-STD-A-011"),
        ),
        _item(
            "STN-PLT-P010",
            "platform coping, tactile strip, warning line, and edge-marker kit",
            "SOURCE",
            platform_edge_m,
            "m",
            "STN-PLT-SA200",
            "full boarding edge length",
            ("contrast check", "tactile layout inspection", "platform-gap survey"),
            ("standard-archetype/accessibility.md", "OSR-STD-A-011"),
        ),
        _item(
            "STN-CNP-P010",
            "6 m galvanised HEA portal-frame steel kit",
            "MAKE",
            total_bays,
            "bay kit",
            "STN-CNP-SA300",
            "canopy bay count × configured platform count",
            ("steel certificates", "galvanising report", "member dimensional check"),
            ("station/portal.py", "RFC 0010 §9"),
        ),
        _item(
            "STN-CNP-P020",
            "canopy footing, reinforcement, base plate, and anchor-bolt kit",
            "MAKE",
            total_columns,
            "column kit",
            "STN-CIV-SA100",
            "one foundation/anchor set per leading and trailing canopy column",
            ("geotechnical release", "rebar inspection", "anchor-template survey", "concrete test"),
            ("station/canopy.py", "OSR-STD-S-001", "OSR-STD-S-002"),
        ),
        _item(
            "STN-CNP-P030",
            "factory-bonded solar roof sandwich panel with MC4 leads",
            "BID",
            total_bays,
            "ea",
            "STN-CNP-SA300",
            "one 6 m × 4.2 m panel per canopy bay",
            ("fire/material certificate", "insulation test", "connector inspection", "watertightness test"),
            ("station/solar_roof.py", "OSR-STD-E-003"),
            "buildable-after-supplier-freeze",
        ),
        _item(
            "STN-CNP-P040",
            "platform-canopy PV string, combiner, isolation, bonding, and downlink kit",
            "BID",
            platform_count,
            "platform kit",
            "STN-CNP-SA300",
            "one controlled DC string and isolation package per platform canopy",
            ("polarity test", "insulation resistance", "bond continuity", "string commissioning"),
            ("OSR-STD-E-003", "OSR-STD-E-004", "OSR-STD-E-008"),
            "buildable-after-supplier-freeze",
        ),
        _item(
            "STN-MEP-P010",
            "weatherproof services cabinet, plinth, cooling, and maintenance-light kit",
            "MAKE",
            1,
            "station kit",
            "STN-MEP-SA400",
            "one coordinated services cabinet per station",
            ("IP inspection", "thermal test", "plinth/door clearance", "condensate test"),
            ("standard-archetype/services.md", "OSR-STD-A-013", "OSR-STD-M-001"),
        ),
        _item(
            "STN-MEP-P020",
            "incoming switchboard, distribution board, metering, UPS, and earthing kit",
            "BID",
            1,
            "station kit",
            "STN-MEP-SA400",
            "one coordinated LV and emergency-power package per station",
            ("factory acceptance test", "protection test", "earth test", "one-hour UPS test"),
            ("standard-archetype/services.md", "OSR-STD-E-001", "OSR-STD-E-005"),
            "buildable-after-supplier-freeze",
        ),
        _item(
            "STN-MEP-P030",
            "platform and emergency LED luminaire, support, and cable kit",
            "SOURCE",
            total_bays * 2,
            "luminaire point",
            "STN-MEP-SA400",
            "two maintained lighting points per canopy bay",
            ("illuminance survey", "emergency-mode test", "RCD test"),
            ("standard-archetype/services.md", "OSR-STD-E-002", "OSR-STD-E-005"),
        ),
        _item(
            "STN-MEP-P040",
            "fire detection, alarm interface, extinguisher, and evacuation-sign kit",
            "SOURCE",
            1,
            "station kit",
            "STN-MEP-SA400",
            "one life-safety kit sized to the configured platform count",
            ("cause-and-effect test", "OCC alarm test", "extinguisher inspection", "egress walkdown"),
            ("standard-archetype/services.md", "OSR-STD-F-001", "OSR-STD-F-004"),
        ),
        _item(
            "STN-PAX-P010",
            "S-SBC station/depot host and rack enclosure",
            "SOURCE",
            1,
            "ea",
            "STN-PAX-SA500",
            "one live host per station; depot-held cold spare excluded",
            ("hardware BOM check", "image checksum", "self-test", "network enumeration"),
            ("control-electronics/s-sbc/diy-assembly/README.md", "control-electronics/s-sbc/schematics/v2-spec/README.md"),
        ),
        _item(
            "STN-PAX-P020",
            "passenger-information display and route-strip kit",
            "SOURCE",
            platform_count * 2,
            "display point",
            "STN-PAX-SA500",
            "two primary visual-information points per configured platform",
            ("content test", "visibility check", "emergency-message test"),
            ("standard-archetype/accessibility.md", "OSR-STD-E-007"),
        ),
        _item(
            "STN-PAX-P030",
            "CCTV, PA loudspeaker, help-point, radio, and station-LAN kit",
            "BID",
            platform_count,
            "platform kit",
            "STN-PAX-SA500",
            "one coordinated communications/security kit per configured platform",
            ("camera coverage", "speech intelligibility", "help-point call", "OCC failover test"),
            ("standard-archetype/services.md", "OSR-STD-E-006", "OSR-STD-E-007"),
            "buildable-after-supplier-freeze",
        ),
        _item(
            "STN-PAX-P040",
            "fare gate, accessible gate, and validator equipment kit",
            "BID",
            fare_gates if fare_gates else 2,
            "lane/validator",
            "STN-PAX-SA500",
            "RFC 0010 gate lanes; halt uses two open-platform validators",
            ("accessible-lane gauge", "AFC transaction test", "power-loss release", "plinth anchor test"),
            ("RFC 0010 §8", "OSR-STD-A-003", "OSR-STD-A-014"),
            "buildable-after-supplier-freeze",
        ),
        _item(
            "STN-PAX-P050",
            "ticket-vending machine equipment kit",
            "BID",
            tvms,
            "ea",
            "STN-PAX-SA500",
            "RFC 0010 TVM count; zero at halt",
            ("transaction test", "accessibility reach check", "cabinet ingress test"),
            ("RFC 0010 §8", "OSR-STD-A-003"),
            "buildable-after-supplier-freeze",
        ),
        _item(
            "STN-PAX-P070",
            "anchored rolled-steel fare-lane / validator plinth with protected cable void",
            "MAKE",
            fare_gates if fare_gates else 2,
            "lane plinth",
            "STN-PAX-SA500",
            "one separate fabricated plinth per fare lane or halt validator",
            ("fabrication drawing", "anchor proof", "level/edge inspection", "accessible-route clearance", "bond continuity"),
            ("station/plinth.py", "OSR-STD-A-014", "OSR-STD-S-007"),
        ),
        _item(
            "STN-PAX-P080",
            "anchored rolled-steel TVM plinth with protected power/data entry",
            "MAKE",
            tvms,
            "TVM plinth",
            "STN-PAX-SA500",
            "one separately replaceable plinth per configured TVM",
            ("fabrication drawing", "anchor proof", "level inspection", "accessible-reach clearance", "bond continuity"),
            ("station/plinth.py", "OSR-STD-A-003", "OSR-STD-S-007"),
        ),
        _item(
            "STN-PAX-P060",
            "seating, wheelchair-zone marking, wayfinding, and accessible-signage kit",
            "SOURCE",
            platform_count,
            "platform kit",
            "STN-PAX-SA500",
            "one passenger-amenity kit per configured platform",
            ("wheelchair-zone survey", "signage schedule check", "circulation gauge"),
            ("standard-archetype/accessibility.md", "OSR-STD-T-001", "OSR-STD-T-003"),
        ),
        _item(
            "STN-ACC-P010",
            "direct/protected pedestrian approach, kerb, ramp, and boundary kit",
            "MAKE",
            1,
            "station kit",
            "STN-ACC-SA600",
            str(config["access_type"]),
            ("step-free route survey", "surface/slip inspection", "protected-crossing interface test"),
            ("RFC 0010 §5", "OSR-STD-A-012", "OSR-STD-M-004"),
        ),
    ]
    # Variant EBOMs contain installed scope only. Optional equipment with a
    # configured quantity of zero belongs in the template decision, not as a
    # zero-quantity manufacturing row.
    items = [item for item in items if item.quantity > 0]

    if auxiliary_canopy_m2 > 0.01:
        items.extend(
            [
                _item(
                    "STN-CNP-P050",
                    "8.5 m × 22 m factory-bonded auxiliary solar-roof bay module",
                    "BID",
                    auxiliary_modules,
                    "187 m2 module",
                    "STN-CNP-SA300",
                    f"ceil({auxiliary_canopy_m2:.1f} m2 required / {AUX_MODULE_AREA_M2:g} m2 module)",
                    ("panel fire/material certificate", "module dimensional report", "watertightness test", "PV insulation/polarity test"),
                    ("station/auxiliary_canopy.py", "station/solar_roof.py", "RFC 0010 §9"),
                    "buildable-after-supplier-and-structural-release",
                ),
                _item(
                    "STN-CNP-P060",
                    "22 m S355 transverse Warren-truss frame with two HSS 200 columns",
                    "MAKE",
                    auxiliary_frame_count(auxiliary_modules),
                    "shared frame",
                    "STN-CNP-SA300",
                    "N + 1 shared transverse frames for N adjacent auxiliary roof modules",
                    ("controlled fabrication drawing", "steel certificates", "weld/NDT record", "frame dimensional survey", "galvanising report"),
                    ("station/auxiliary_canopy.py", "standard-archetype/canopy.md", "RFC 0010 §9"),
                    "buildable-after-structural-calculation-and-drawing-release",
                ),
                _item(
                    "STN-CNP-P070",
                    "auxiliary-canopy pad footing, reinforcement, base plate, and anchor-bolt kit",
                    "MAKE",
                    auxiliary_foundation_count(auxiliary_modules),
                    "column kit",
                    "STN-CIV-SA100",
                    "two column foundations for each shared transverse frame",
                    ("site geotechnical release", "foundation calculation", "rebar/pre-pour inspection", "anchor-template survey", "concrete test"),
                    ("station/auxiliary_canopy.py", "standard-archetype/canopy.md", "RFC 0010 §9"),
                    "buildable-after-site-structural-release",
                ),
                _item(
                    "STN-CNP-P080",
                    "auxiliary-canopy PV string, combiner, isolation, bonding, and downlink kit",
                    "BID",
                    (auxiliary_modules + 9) // 10,
                    "string group",
                    "STN-CNP-SA300",
                    "one independently isolated electrical group for each ten or fewer roof modules",
                    ("string schedule", "polarity/insulation test", "bond continuity", "protection settings", "energy-site commissioning"),
                    ("station/auxiliary_canopy.py", "OSR-STD-E-003", "OSR-STD-E-004"),
                    "buildable-after-electrical-and-supplier-freeze",
                ),
                _item(
                    "STN-CNP-P090",
                    "auxiliary-canopy gutter, downpipe, lightning, maintenance-access, and edge-protection kit",
                    "SOURCE",
                    auxiliary_modules,
                    "roof-bay kit",
                    "STN-CNP-SA300",
                    "one coordinated drainage, lightning, and safe-access kit per roof bay",
                    ("drainage flow test", "lightning/bond test", "edge-protection inspection", "maintenance-access walkdown"),
                    ("station/auxiliary_canopy.py", "standard-archetype/canopy.md", "RFC 0010 §9"),
                    "buildable-after-site-and-supplier-freeze",
                ),
            ]
        )
    if charging_kw > 0:
        items.append(
            _item(
                "STN-CHG-P010",
                "station charging cabinet, protection, cable, and wayside connector kit",
                "BID",
                charging_kw,
                "kW installed",
                "STN-CHG-SA700",
                "configured station charging power",
                ("FAT", "insulation/protection test", "vehicle alignment test", "abort/interlock test"),
                ("lib/templates/stations.toml", "RFC 0026"),
                "buildable-after-supplier-freeze",
            )
        )
    if tpss_kva > 0:
        items.append(
            _item(
                "STN-CHG-P020",
                "traction power substation transformer/rectifier and protection interface",
                "BID",
                tpss_kva,
                "kVA installed",
                "STN-CHG-SA700",
                "configured TPSS capacity",
                ("utility approval", "FAT/SAT", "protection coordination", "earthing test"),
                ("lib/templates/stations.toml", "RFC 0002"),
                "buildable-after-utility-and-supplier-freeze",
            )
        )
    if step_free_cores > 0:
        items.append(
            _item(
                "STN-ACC-P020",
                "lift/stair step-free circulation core",
                "BID",
                step_free_cores,
                "core",
                "STN-ACC-SA600",
                "configured step-free-core count",
                ("lift certification", "fire recall test", "backup-power test", "accessibility survey"),
                ("lib/templates/stations.toml", "RFC 0010 §5"),
                "buildable-after-site-and-supplier-freeze",
            )
        )
    if access_bridges > 0:
        items.append(
            _item(
                "STN-ACC-P030",
                "pedestrian overbridge/concourse structural and enclosure kit",
                "BID",
                access_bridges,
                "ea",
                "STN-ACC-SA600",
                "configured access-bridge count",
                ("structural release", "clearance survey", "egress test", "weatherproofing inspection"),
                ("lib/templates/stations.toml", "RFC 0011 §7"),
                "buildable-after-site-and-supplier-freeze",
            )
        )
    if turnout_count:
        items.extend(
            [
                _item(
                    "STN-TRK-P010",
                    "1:9 UIC60 stock-rail, machined switch-blade, and closure-rail kit",
                    "MAKE",
                    turnout_count,
                    "turnout kit",
                    "STN-TRK-SA800",
                    f"one {turnout_geometry.total_length_mm / 1000:g} m 1:9 turnback turnout per terminal interface",
                    ("rail certificates", "blade profile/CMM report", "rail geometry inspection", "weld/NDT release"),
                    ("track/turnout.py", "RFC 0012 §4/§8", "RFC 0025 §3"),
                    "buildable-after-controlled-drawing-release",
                ),
                _item(
                    "STN-TRK-P020",
                    "cast-manganese frog, check-rail, stretcher-bar, and mechanical-lock kit",
                    "BID",
                    turnout_count,
                    "turnout kit",
                    "STN-TRK-SA800",
                    "one crossing and mechanically locked stretcher set per 1:9 turnout",
                    ("material certificate", "frog/check-rail gauge", "lock proof", "stretcher dimensional report"),
                    ("track/turnout.py", "RFC 0012 §4.1", "RFC 0025 §3.2"),
                    "buildable-after-supplier-freeze",
                ),
                _item(
                    "STN-TRK-P030",
                    "prestressed turnout sleeper, slide-chair, and elastic-fastener set",
                    "SOURCE",
                    turnout_geometry.sleeper_count * turnout_count,
                    "sleeper position",
                    "STN-TRK-SA800",
                    f"{turnout_geometry.sleeper_count} controlled positions per 1:9 turnout",
                    ("EN 13145 certificate", "fastener certificate", "chair/fastener torque", "sleeper-position survey"),
                    ("lib/templates/switches.toml", "track/turnout.py", "RFC 0012 §4.1"),
                    "buildable-after-supplier-freeze",
                ),
                _item(
                    "STN-TRK-P040",
                    "6 kN nominal / 12 kN peak point-machine actuator, crank, and hand-wind kit",
                    "BID",
                    turnout_count,
                    "ea",
                    "STN-TRK-SA800",
                    "one electro-mechanical point machine per turnout",
                    ("18 kN ultimate proof", "three-second throw test", "manual operation", "endurance/environment qualification"),
                    ("RFC 0012 §4.2", "RFC 0025 §4/§6"),
                    "buildable-after-actuator-qualification",
                ),
                _item(
                    "STN-TRK-P050",
                    "dual position detector, W-SBC interface, junction, and turnout harness kit",
                    "SOURCE",
                    turnout_count,
                    "turnout kit",
                    "STN-TRK-SA800",
                    "one 2oo2 fail-open detection chain per turnout",
                    ("channel independence inspection", "normal/reverse detection proof", "unknown-state test", "W-SBC route-lock interface test"),
                    ("RFC 0012 §5", "control-electronics/w-sbc/diy-assembly/README.md", "osr-wayside-points"),
                    "buildable-after-hardware-freeze",
                ),
                _item(
                    "STN-TRK-P060",
                    "3 kW points-heating strip, thermostat, IP67 cabinet, isolation, and cabling kit",
                    "SOURCE",
                    turnout_count,
                    "turnout kit",
                    "STN-TRK-SA800",
                    "one conditioned points-heating and cabinet package per turnout",
                    ("insulation/protection test", "thermostat test", "cabinet ingress inspection", "hot/cold function test"),
                    ("RFC 0012 §4.2", "lib/templates/climate-adapters.toml"),
                    "buildable-after-climate-and-supplier-freeze",
                ),
                _item(
                    "STN-TRK-P070",
                    "terminal stop-block, passive end marker, foundation, and fixing kit",
                    "SOURCE",
                    platform_count,
                    "track-end kit",
                    "STN-TRK-SA800",
                    "one protected stop/end-marker package per terminal platform track",
                    ("track-end geometry release", "foundation inspection", "stop-block proof", "marker visibility check"),
                    ("lib/templates/stations.toml", "RFC 0012 §9"),
                    "buildable-after-site-geometry-freeze",
                ),
            ]
        )
    if bool(config.get("is_depot", False)):
        depot = _main_depot_reference()
        depot_stalls = int(depot["default_fleet_stalls"])
        depot_turnouts = throat_turnout_count(depot_stalls)
        items.extend(
            [
                _item(
                    "STN-DEP-P010",
                    "main-heavy depot site formation, drainage, service-road, and secure-boundary kit",
                    "MAKE",
                    float(depot["approx_footprint_m2"]),
                    "m2 site",
                    "STN-DEP-SA850",
                    "main-heavy reference footprint from the controlled depot template",
                    ("site/geotechnical release", "drainage/outfall approval", "road swept-path test", "secure-boundary inspection"),
                    ("lib/templates/depots.toml", "depot/layout.py", "RFC 0014 §5.5"),
                    "buildable-after-site-design-release",
                ),
                _item(
                    "STN-DEP-P020",
                    "stabling, inspection, wash, and workshop track-panel/stop-block package",
                    "MAKE",
                    float(depot["stabling_length_m"]),
                    "track-m",
                    "STN-DEP-SA850",
                    f"controlled main-heavy allocation for {depot_stalls} stalls",
                    ("track layout release", "rail/fastener certificates", "geometry survey", "stop-block proof", "wash-track drainage test"),
                    ("lib/templates/depots.toml", "depot/layout.py", "RFC 0014 §5.2"),
                    "buildable-after-controlled-layout-release",
                ),
                _item(
                    "STN-DEP-P030",
                    "1:9 depot-throat turnout assembly replicated from the terminal turnout standard",
                    "MAKE",
                    depot_turnouts,
                    "turnout assembly",
                    "STN-DEP-SA850",
                    f"ceil({depot_stalls} reference stalls / 2) throat turnouts",
                    ("controlled STN-TRK-SA800 definition", "shop bench proof", "yard geometry survey", "route/detection proof"),
                    ("depot/layout.py", "track/turnout.py", "RFC 0012 §9", "RFC 0014 §5.4"),
                    "buildable-after-turnout-design-and-site-freeze",
                ),
                _item(
                    "STN-DEP-P040",
                    "per-stall plug-in charger, isolation, suspended cable, and data-dock kit",
                    "BID",
                    depot_stalls,
                    "stall kit",
                    "STN-DEP-SA850",
                    "one controlled charging/data dock per reference stall",
                    ("supplier FAT", "protection/isolation test", "vehicle reach/alignment test", "charge/abort/data-sync SAT"),
                    ("depot/layout.py", "RFC 0014 §5.3", "RFC 0021 §6.1"),
                    "buildable-after-supplier-and-energy-freeze",
                ),
                _item(
                    "STN-DEP-P050",
                    "depot PV canopy, inverter, microgrid switchgear, and stationary battery package",
                    "BID",
                    1,
                    "energy-site kit",
                    "STN-DEP-SA850",
                    f"{depot['pv_canopy_m2']} m2 / {depot['pv_nominal_kwp']} kWp PV with {depot['battery_kwh']} kWh storage",
                    ("structural/PV layout release", "utility/protection approval", "battery fire/thermal evidence", "energy-site SAT"),
                    ("lib/templates/depots.toml", "RFC 0014 §5.3", "RFC 0002"),
                    "buildable-after-energy-site-and-supplier-freeze",
                ),
                _item(
                    "STN-DEP-P060",
                    "main workshop, overhaul/inspection bays, 40 t crane, wash plant, stores, and wheel-lathe package",
                    "BID",
                    float(depot["workshop_m2"]),
                    "m2 workshop",
                    "STN-DEP-SA850",
                    "main-heavy workshop envelope and enabled equipment from the depot template",
                    ("building/egress release", "crane certification", "pit/fall-protection inspection", "lathe acceptance", "wash/recycling SAT"),
                    ("lib/templates/depots.toml", "depot/layout.py", "RFC 0014 §5.1/§5.2"),
                    "buildable-after-building-and-equipment-freeze",
                ),
                _item(
                    "STN-DEP-P070",
                    "depot LV, compressed-air, fire, lighting, CCTV, LAN, access-control, and maintenance-data kit",
                    "BID",
                    1,
                    "depot services kit",
                    "STN-DEP-SA850",
                    "one coordinated services and security package per main-heavy depot",
                    ("utility capacity", "fire cause/effect test", "air-system pressure test", "coverage/access test", "maintenance-data sync"),
                    ("RFC 0014 §5", "standard-archetype/services.md", "control-electronics/s-sbc/diy-assembly/README.md"),
                    "buildable-after-services-and-supplier-freeze",
                ),
            ]
        )
    else:
        depot_stalls = 0
        depot_turnouts = 0

    item_ids = {item.id for item in items}

    def children(prefix: str) -> tuple[str, ...]:
        return tuple(sorted(item_id for item_id in item_ids if item_id.startswith(prefix)))

    assemblies = (
        StationAssemblyNode(
            "STN-CIV-SA100",
            "site, foundation, drainage, and track/depot interface works",
            tuple(item_id for item_id in ("STN-CIV-P030", "STN-CNP-P020", "STN-CNP-P070") if item_id in item_ids),
            "civil works",
            (
                "release survey, utilities, geotechnical report, drainage outfall, and temporary-works plan",
                "set out platform, track, canopy-column, cabinet, and access datums",
                "construct drainage, footing reinforcement, anchor templates, and concrete works",
                "cure, test, survey, and release foundations before precast or steel placement",
            ),
            ("survey/geotechnical release", "pre-pour inspection", "foundation and drainage survey"),
        ),
        StationAssemblyNode(
            "STN-PLT-SA200",
            "platform, guideway-channel, and boarding-edge assembly",
            children("STN-CIV-P01")
            + tuple(item_id for item_id in ("STN-CIV-P020", "STN-CIV-P040", "STN-PLT-P010") if item_id in item_ids),
            "civil/platform construction",
            (
                "inspect delivery certificates, lifting points, and platform datum",
                (
                    "place elevated L-units on the released structure using the approved lifting plan"
                    if elevated_platform
                    else "construct/place ground-level slab panels and the depressed guideway channel on the released sub-base"
                ),
                "install and survey guideway edge modules where required, maintaining the 350 mm platform-to-ToR datum",
                "grout bearing lands and complete non-critical closure pours",
                "install coping, tactile strip, warning line, and edge markers",
                "survey height, horizontal gap, straightness, crossfall, and egress width",
            ),
            ("first-unit placement", "grout/cure release", "boarding-interface survey"),
        ),
        StationAssemblyNode(
            "STN-CNP-SA300",
            "modular canopy, roof, and PV assembly",
            tuple(
                item_id
                for item_id in (
                    "STN-CNP-P010",
                    "STN-CNP-P030",
                    "STN-CNP-P040",
                    "STN-CNP-P050",
                    "STN-CNP-P060",
                    "STN-CNP-P080",
                    "STN-CNP-P090",
                )
                if item_id in item_ids
            ),
            "steel erection and solar",
            (
                "verify foundation/anchor survey and incoming galvanised-steel certificates",
                "erect columns, rafters, braces, and temporary stability system bay by bay",
                "complete structural bolt torque/marking and frame plumb survey",
                "lift and fasten factory roof panels using the released panel clamp plan",
                "connect PV strings, combiner, isolation, bonding, lightning protection, and downlinks",
                "erect auxiliary shared truss frames and roof bays to the released site layout, including drainage and safe-access systems",
                "complete roof water test and PV insulation/polarity/commissioning records",
            ),
            ("first portal plumb/torque", "structural frame release", "roof/PV electrical release"),
        ),
        StationAssemblyNode(
            "STN-MEP-SA400",
            "station mechanical, electrical, drainage-services, and fire assembly",
            children("STN-MEP-P"),
            "MEP installation",
            (
                "install and anchor the service cabinet after civil release",
                "install LV distribution, UPS, earthing, lighting, fire, and communications containment",
                "install charging/TPSS equipment only after supplier and utility release",
                "terminate, label, inspect, energise, and execute discipline test sheets",
            ),
            ("cabinet/plinth release", "electrical safe-to-energise", "MEP integrated test"),
        ),
        StationAssemblyNode(
            "STN-CHG-SA700",
            "station charging and traction-power interface assembly",
            children("STN-CHG-P"),
            "traction power and charging",
            (
                "release utility, protection, vehicle-interface, and supplier drawings",
                "install charging cabinet, TPSS equipment, containment, earthing, and physical guards",
                "complete FAT record review, cable tests, protection injection, and safe energisation",
                "run vehicle alignment, handshake, charge, abort, isolation, and emergency-release tests",
            ),
            ("utility/supplier release", "safe-to-energise", "vehicle charging SAT"),
        ),
        StationAssemblyNode(
            "STN-PAX-SA500",
            "passenger systems, fare, information, security, and amenity assembly",
            children("STN-PAX-P"),
            "systems fit-out",
            (
                "install the S-SBC from its controlled hardware BOM and record image/configuration hashes",
                "install fare, PIS, CCTV, PA, help-point, LAN, seating, and signage equipment",
                "verify accessible reach, circulation, sightlines, audio coverage, and emergency messages",
                "run station self-test and end-to-end OCC communications/alarms",
            ),
            ("control-electronics/configuration release", "accessibility walkdown", "station systems SAT"),
        ),
        StationAssemblyNode(
            "STN-ACC-SA600",
            "station access and vertical-circulation assembly",
            children("STN-ACC-P"),
            "access works",
            (
                "release pedestrian desire-line, boundary, road-crossing, and egress interfaces",
                "construct direct paths, kerbs, ramps, bridge/concourse, and step-free cores as applicable",
                "commission lifts, protected crossings, lighting, drainage, and emergency recall",
                "complete independent step-free and evacuation-route walkdowns",
            ),
            ("access geometry release", "vertical-circulation certification", "egress acceptance"),
        ),
        *(
            (
                StationAssemblyNode(
                    "STN-TRK-SA800",
                    "terminal 1:9 turnout, point machine, detection, and stop-block assembly",
                    children("STN-TRK-P"),
                    "track/switch assembly and commissioning",
                    (
                        "release the controlled turnout geometry, rail/blade drawings, supplier documents, site trackform, and drainage",
                        "assemble switch rails, frog, check rails, sleepers, chairs, fasteners, stretcher bars, and mechanical lock in the shop fixture",
                        "install actuator, hand-wind provision, detection channels, W-SBC interface, heating, cabinet, and labelled harness",
                        "bench-prove blade throw, force, time, mechanical lock, normal/reverse detection, disagreement response, and manual operation",
                        "install to the released site datum; align, stress, weld/bolt, drain, and survey the complete turnout and track ends",
                        "execute route locking, detection, heating, stop-block, and integrated train-movement proof tests",
                    ),
                    ("controlled geometry/drawing release", "shop bench proof", "site geometry and route proof"),
                ),
            )
            if turnout_count
            else ()
        ),
        *(
            (
                StationAssemblyNode(
                    "STN-DEP-SA850",
                    "co-located main-heavy depot civil, track, workshop, energy, and systems assembly",
                    children("STN-DEP-P"),
                    "depot construction and systems integration",
                    (
                        "release the deployment fleet/stall count, site survey, geotechnical model, utility capacities, depot layout, and phasing plan",
                        "construct site formation, drainage, secure boundary, service roads, trackform, stabling tracks, throat turnouts, pits, and stop blocks",
                        "erect and fit out workshop, inspection/overhaul bays, stores, crane, wash plant, wheel lathe, and safe access systems",
                        "install PV canopy, stationary storage, microgrid, per-stall charging, LV, compressed air, fire, CCTV, LAN, and access control",
                        "commission track geometry/routes, workshop equipment, energy site, charging/data docks, fire/security, and maintenance-data interfaces",
                        "compile the asset register, lifting plans, certifications, spares, maintenance instructions, as-builts, and operator handover evidence",
                    ),
                    ("site/layout release", "track/building completion", "energy and workshop SAT", "operator depot handover"),
                ),
            )
            if depot_stalls
            else ()
        ),
        StationAssemblyNode(
            "STN-STATION-A900",
            "complete commissioned station",
            (
                "STN-CIV-SA100",
                "STN-PLT-SA200",
                "STN-CNP-SA300",
                "STN-MEP-SA400",
                "STN-CHG-SA700",
                "STN-PAX-SA500",
                "STN-ACC-SA600",
            )
            + (("STN-TRK-SA800",) if turnout_count else ())
            + (("STN-DEP-SA850",) if depot_stalls else ()),
            "station integration",
            (
                "confirm every child traveler, NCR, certificate, survey, and as-built drawing is closed",
                "perform integrated passenger-flow, accessibility, fire, power-loss, charging, and OCC tests",
                "compile asset register, spares, maintenance instructions, configuration baseline, and handover pack",
            ),
            ("construction completion", "integrated SAT", "operator/AOR handover"),
        ),
    )

    parameters: dict[str, str | float | int | bool] = {
        "platform_count": platform_count,
        "platform_layout": str(config["platform_layout"]),
        "platform_length_m": platform_length_m,
        "platform_l_units": units_each * platform_count if elevated_platform else 0,
        "at_grade_track_channel_count": 0 if elevated_platform else track_channel_count,
        "at_grade_slab_panels": 0 if elevated_platform else at_grade_slab_panels,
        "guideway_edge_modules": 0 if elevated_platform else units_each * platform_count,
        "canopy_bays_per_platform": bays_each,
        "total_canopy_bays": total_bays,
        "platform_canopy_area_m2": round(platform_canopy_area_m2, 1),
        "site_canopy_target_m2": site_canopy_target_m2,
        "auxiliary_canopy_required_area_m2": round(auxiliary_canopy_m2, 1),
        "auxiliary_canopy_module_area_m2": AUX_MODULE_AREA_M2,
        "auxiliary_canopy_module_count": auxiliary_modules,
        "auxiliary_canopy_installed_area_m2": auxiliary_installed_m2,
        "auxiliary_canopy_target_overbuild_m2": round(auxiliary_installed_m2 - auxiliary_canopy_m2, 1),
        "auxiliary_canopy_kwp": round(auxiliary_canopy_kwp(auxiliary_modules), 1),
        "charging_power_kw": charging_kw,
        "dwell_seconds": int(config["dwell_seconds"]),
        "tpss_kva": tpss_kva,
        "access_type": str(config["access_type"]),
        "turnout_count": turnout_count,
        "turnout_tangent": TurnoutTangent.T_1_9.value if turnout_count else "none",
        "turnout_total_length_m": turnout_geometry.total_length_mm / 1000 if turnout_count else 0,
        "turnout_switch_blade_length_m": turnout_geometry.switch_blade_length_mm / 1000 if turnout_count else 0,
        "turnout_sleeper_count": turnout_geometry.sleeper_count * turnout_count,
        "depot_archetype": "main-heavy" if depot_stalls else "none",
        "depot_reference_stalls": depot_stalls,
        "depot_throat_turnouts": depot_turnouts,
    }
    return StationVariant(
        archetype.value,
        consist.value,
        parameters,
        tuple(items),
        assemblies,
        (
            "platform screen doors are optional for light-metro-3car and are not included",
            "site survey, geotechnical design, utilities, permits, and stamped calculations remain deployment-specific",
            "auxiliary canopy requires deployment structural, foundation, drainage, egress, and electrical release",
        ),
    )


BOM_FIELDS = (
    "archetype",
    "engineering_id",
    "title",
    "route",
    "quantity",
    "unit",
    "parent_assembly",
    "maturity",
    "quantity_basis",
    "acceptance",
    "source_refs",
)


def render_bom_csv(variant: StationVariant) -> str:
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=BOM_FIELDS, lineterminator="\n")
    writer.writeheader()
    for item in variant.product_items:
        writer.writerow(
            {
                "archetype": variant.archetype,
                "engineering_id": item.id,
                "title": item.title,
                "route": item.route,
                "quantity": f"{item.quantity:g}",
                "unit": item.unit,
                "parent_assembly": item.parent,
                "maturity": item.maturity,
                "quantity_basis": item.quantity_basis,
                "acceptance": ";".join(item.acceptance),
                "source_refs": ";".join(item.source_refs),
            }
        )
    return out.getvalue()


def render_traveler(variant: StationVariant) -> str:
    items = {item.id: item for item in variant.product_items}
    lines = [
        f"# Station assembly traveler — `{variant.archetype}`",
        "",
        "Generated from `lib/templates/stations.toml` and the canonical mechanical",
        "platform/canopy geometry. This is an unsigned template; deployment survey,",
        "engineering approvals, supplier documents, and inspector signatures are required.",
        "",
        "## Configuration",
        "",
        "| Parameter | Value |",
        "|---|---:|",
    ]
    lines.extend(f"| `{key}` | {value} |" for key, value in variant.parameters.items())
    for node in variant.assemblies:
        lines.extend(
            [
                "",
                f"## `{node.id}` — {node.title}",
                "",
                f"Work cell: {node.work_cell}.",
                "",
                "### BOM release",
                "",
                "| Engineering ID | Qty | Unit | Route | Maturity |",
                "|---|---:|---|---|---|",
            ]
        )
        for child_id in node.children:
            if child_id in items:
                item = items[child_id]
                lines.append(
                    f"| `{item.id}` | {item.quantity:g} | {item.unit} | `{item.route}` | `{item.maturity}` |"
                )
            else:
                lines.append(f"| `{child_id}` | 1 | assembly | `RELEASED CHILD` | `traveler required` |")
        lines.extend(["", "### Work instructions", ""])
        lines.extend(f"{sequence}. {instruction}." for sequence, instruction in enumerate(node.instructions, 1))
        lines.extend(["", "### Hold points", ""])
        lines.extend(f"- [ ] {hold_point} — inspector/signature/date: __________" for hold_point in node.hold_points)
    lines.extend(["", "## Baseline exclusions and open release conditions", ""])
    lines.extend(f"- {entry}" for entry in variant.baseline_exclusions)
    lines.extend(
        [
            "",
            "## Final signoff",
            "",
            "| Role | Name | Date | Signature |",
            "|---|---|---|---|",
            "| Civil/AOR |  |  |  |",
            "| MEP lead |  |  |  |",
            "| Systems integrator |  |  |  |",
            "| Quality/inspection |  |  |  |",
            "| Operator acceptance |  |  |  |",
            "",
        ]
    )
    return "\n".join(lines)


def product_drawing_id(variant: StationVariant, item: StationProductItem) -> str:
    """Return the stable definition-sheet identity for one product row."""

    return f"{item.id}-DRW-{variant.archetype.upper()}"


def product_connection_id(item: StationProductItem) -> str:
    """Return a stable connection-control identity or an explicit non-applicable marker."""

    connection_terms = (
        "anchor",
        "bolt",
        "fastener",
        "fixing",
        "mount",
        "connector",
        "joint",
        "weld",
        "grout",
        "plinth",
    )
    searchable = " ".join((item.title, item.quantity_basis, *item.acceptance)).lower()
    return f"{item.id}-CONN" if any(term in searchable for term in connection_terms) else "not-applicable"


def product_standard_drawings(item: StationProductItem) -> tuple[str, ...]:
    """Extract controlled shared drawing references from the product source links."""

    matches: list[str] = []
    for source in item.source_refs:
        matches.extend(re.findall(r"OSR-STD-[A-Z]-\d{3}", source))
    return tuple(dict.fromkeys(matches))


def render_variant_page(variant: StationVariant, standard: StationVariant) -> str:
    """Render the complete but compact documentation delta for one archetype."""

    standard_parameters = standard.parameters
    deltas = [
        (key, standard_parameters.get(key, "not-used"), value)
        for key, value in variant.parameters.items()
        if standard_parameters.get(key) != value
    ]
    standard_ids = {item.id for item in standard.product_items}
    unique_ids = [item.id for item in variant.product_items if item.id not in standard_ids]
    lines = [
        f"# `{variant.archetype}` station definition",
        "",
        "**Status:** deterministic design-reference package; not construction release.",
        "",
        "The shared envelope, canopy, accessibility, services, compliance and",
        "43-drawing register live in [`docs/stations/standard-archetype/`](../../../../../docs/stations/standard-archetype/).",
        "This page is the complete archetype delta and stable-ID bridge into its BOM,",
        "traveler, FreeCAD installed/exploded states and IFC4.3 assembly.",
        "",
        "## Parameter delta from `standard`",
        "",
        "| Parameter | Standard | This variant |",
        "|---|---:|---:|",
    ]
    if deltas:
        lines.extend(f"| `{key}` | {old} | {new} |" for key, old, new in deltas)
    else:
        lines.append("| _none_ | — | — |")
    lines.extend(
        [
            "",
            "Unique product rows: " + (", ".join(f"`{item_id}`" for item_id in unique_ids) if unique_ids else "none; this is the governing shared variant."),
            "",
            "## Controlled handoffs",
            "",
            f"- BOM: `build/bom/stations/{variant.archetype}.csv`",
            f"- traveler: [`../travelers/{variant.archetype}.md`](../travelers/{variant.archetype}.md)",
            f"- FreeCAD: [`../../../models/cad/stations/station-{variant.archetype}.FCStd`](../../../models/cad/stations/station-{variant.archetype}.FCStd)",
            f"- assembly-state map: [`../../../models/cad/stations/station-{variant.archetype}.assembly-review.json`](../../../models/cad/stations/station-{variant.archetype}.assembly-review.json)",
            f"- IFC4.3: [`../../../../../engineering/models/bim/reference/stations/station-{variant.archetype}.ifc`](../../../../../engineering/models/bim/reference/stations/station-{variant.archetype}.ifc)",
            "",
            "## Product/drawing/connection identity",
            "",
            "The definition-sheet ID keeps the product ID intact. It identifies the",
            "deployment drawing that must be produced and approved; it does not claim",
            "that a construction drawing has already been released. `CONN` rows identify",
            "where a controlled fastener, anchor, seal, terminal, weld or grout schedule is required.",
            "",
            "| Product ID | Parent | Route | Definition sheet | Shared drawings | Connection control |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in variant.product_items:
        shared = ", ".join(f"`{drawing}`" for drawing in product_standard_drawings(item)) or "—"
        connection = product_connection_id(item)
        connection_cell = f"`{connection}`" if connection != "not-applicable" else "—"
        lines.append(
            f"| `{item.id}` | `{item.parent}` | `{item.route}` | "
            f"`{product_drawing_id(variant, item)}` | {shared} | {connection_cell} |"
        )
    lines.extend(
        [
            "",
            "## Assembly hierarchy",
            "",
            "| Assembly ID | Work cell | Direct children |",
            "|---|---|---|",
        ]
    )
    for node in variant.assemblies:
        lines.append(
            f"| `{node.id}` | {node.work_cell} | "
            + ", ".join(f"`{child}`" for child in node.children)
            + " |"
        )
    lines.extend(
        [
            "",
            "## Release boundary",
            "",
            "Site survey, geotechnical and structural calculations, supplier selections,",
            "local accessibility/fire approval, signed drawings, inspection records and",
            "as-built survey remain mandatory before construction or operation.",
            "",
        ]
    )
    return "\n".join(lines)


def render_index(variants: tuple[StationVariant, ...]) -> str:
    lines = [
        "# Buildable station kit catalogue",
        "",
        "Generated station EBOM/MBOM and unsigned assembly travelers for the six",
        "base station shells and the controlled elevated-interchange variant.",
        "",
        "| Archetype | Platforms | Platform length m | Bays/platform | Product rows | Open product gaps | Auxiliary modules / installed m² | Definition | Traveler |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for variant in variants:
        key = variant.archetype
        p = variant.parameters
        lines.append(
            f"| `{key}` | {p['platform_count']} | {p['platform_length_m']} | "
            f"{p['canopy_bays_per_platform']} | {len(variant.product_items)} | "
            f"{sum(item.maturity != 'release-candidate' for item in variant.product_items)} | "
            f"{p['auxiliary_canopy_module_count']} / {p['auxiliary_canopy_installed_area_m2']} | "
            f"[`md`](variants/{key}.md) | "
            f"[`md`](travelers/{key}.md) |"
        )
    lines.extend(
        [
            "",
            "Auxiliary area is quantised upward into repeatable 8.5 m × 22 m solar-roof",
            "modules rather than left as an unbuildable square-metre allowance.",
            "Site structural, foundation, drainage, egress, and electrical approvals remain gates.",
            "See the generated [`open release gap register`](open-release-gaps.md) for",
            "the supplier, site, utility, and component-design closures behind these counts.",
            "",
        ]
    )
    return "\n".join(lines)


def open_release_items(variants: tuple[StationVariant, ...]) -> list[dict[str, str | float]]:
    """Return machine-readable non-release-candidate product rows."""

    return [
        {
            "archetype": variant.archetype,
            "engineering_id": item.id,
            "title": item.title,
            "route": item.route,
            "quantity": item.quantity,
            "unit": item.unit,
            "maturity": item.maturity,
            "closure_evidence": "; ".join(item.acceptance),
        }
        for variant in variants
        for item in variant.product_items
        if item.maturity != "release-candidate"
    ]


def render_gap_register(variants: tuple[StationVariant, ...]) -> str:
    """Render the station component gaps directly from EBOM maturity fields."""

    grouped: dict[tuple[str, str, str, str], list[tuple[str, float, str, tuple[str, ...]]]] = {}
    for variant in variants:
        for item in variant.product_items:
            if item.maturity == "release-candidate":
                continue
            key = (item.id, item.title, item.route, item.maturity)
            grouped.setdefault(key, []).append(
                (variant.archetype, item.quantity, item.unit, item.acceptance)
            )

    lines = [
        "# Station open release gap register",
        "",
        "Generated from the same product rows as the station EBOMs and assembly",
        "travelers. A row disappears only when its product maturity is promoted to",
        "`release-candidate`; acceptance evidence remains mandatory at build time.",
        "",
        "| Engineering ID | Component | Route | Maturity / blocker | Variant quantities | Closure evidence |",
        "|---|---|---|---|---|---|",
    ]
    for (item_id, title, route, maturity), occurrences in sorted(grouped.items()):
        quantities = "; ".join(
            f"`{archetype}`={quantity:g} {unit}"
            for archetype, quantity, unit, _acceptance in occurrences
        )
        acceptance = "; ".join(dict.fromkeys(occurrences[0][3]))
        lines.append(
            f"| `{item_id}` | {title} | `{route}` | `{maturity}` | {quantities} | {acceptance} |"
        )
    lines.extend(
        [
            "",
            "## Package-level exclusions",
            "",
            "These conditions are not product rows and therefore remain explicit package gates:",
            "",
        ]
    )
    exclusions = dict.fromkeys(
        exclusion for variant in variants for exclusion in variant.baseline_exclusions
    )
    lines.extend(f"- {exclusion}" for exclusion in exclusions)
    lines.append("")
    return "\n".join(lines)


def write_outputs(
    template: Path = DEFAULT_TEMPLATE,
    catalog_dir: Path = DEFAULT_CATALOG_DIR,
    bom_dir: Path = DEFAULT_BOM_DIR,
    consist: ConsistFamily = ConsistFamily.LIGHT_METRO_3CAR,
) -> tuple[StationVariant, ...]:
    configs = _template_archetypes(template)
    variants = tuple(
        station_variant(archetype, configs[archetype.value], consist)
        for archetype in StationArchetype
    )
    catalog_dir.mkdir(parents=True, exist_ok=True)
    (catalog_dir / "travelers").mkdir(parents=True, exist_ok=True)
    (catalog_dir / "variants").mkdir(parents=True, exist_ok=True)
    bom_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "source_template": str(template.relative_to(REPO_ROOT)),
        "consist": consist.value,
        "open_release_items": open_release_items(variants),
        "variants": [asdict(variant) for variant in variants],
    }
    (catalog_dir / "station-kit-manifest.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (catalog_dir / "README.md").write_text(render_index(variants), encoding="utf-8")
    (catalog_dir / "open-release-gaps.md").write_text(
        render_gap_register(variants), encoding="utf-8"
    )
    for variant in variants:
        (bom_dir / f"{variant.archetype}.csv").write_text(
            render_bom_csv(variant), encoding="utf-8"
        )
        (catalog_dir / "travelers" / f"{variant.archetype}.md").write_text(
            render_traveler(variant), encoding="utf-8"
        )
        (catalog_dir / "variants" / f"{variant.archetype}.md").write_text(
            render_variant_page(
                variant,
                next(row for row in variants if row.archetype == StationArchetype.STANDARD.value),
            ),
            encoding="utf-8",
        )
    return variants


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--catalog-dir", type=Path, default=DEFAULT_CATALOG_DIR)
    parser.add_argument("--bom-dir", type=Path, default=DEFAULT_BOM_DIR)
    parser.add_argument(
        "--consist",
        choices=[family.value for family in ConsistFamily],
        default=ConsistFamily.LIGHT_METRO_3CAR.value,
    )
    args = parser.parse_args()
    variants = write_outputs(
        args.template,
        args.catalog_dir,
        args.bom_dir,
        ConsistFamily(args.consist),
    )
    print(f"station variants: {len(variants)}")
    print(f"product rows: {sum(len(variant.product_items) for variant in variants)}")
    print(f"wrote {args.catalog_dir}")
    print(f"wrote {args.bom_dir}")


if __name__ == "__main__":
    main()

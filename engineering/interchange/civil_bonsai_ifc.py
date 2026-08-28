#!/usr/bin/env python3
"""Generate a deterministic IFC4.3 civil coordination model for Bonsai.

OpenSourceRail remains authoritative for alignment rules and parametric civil
geometry.  This exporter turns the checked design-reference twin into a native
IFC project with rail-domain spatial structure, inspectable geometry,
quantities, provenance, and an IfcWorkSchedule suitable for Bonsai's 4D tools.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tomllib
import uuid
import zipfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterable

import numpy as np
from bcf.v3.bcfxml import BcfXml
from xsdata.models.datatype import XmlDateTime

REPO_ROOT = Path(__file__).resolve().parents[2]
MECHANICAL_SRC = REPO_ROOT / "mechanical-py/src"
if str(MECHANICAL_SRC) not in sys.path:
    sys.path.insert(0, str(MECHANICAL_SRC))

import ifcopenshell
import ifcopenshell.validate as ifc_validate
from ifcopenshell.util.element import get_material, get_psets
from ifcopenshell.util.classification import get_references
from ifctester import ids as ids_module
from ifctester import open as open_ids
from ifctester import reporter as ids_reporter
from ifcopenshell.api.aggregate import assign_object
from ifcopenshell.api.alignment import (
    add_stationing_referent,
    create as create_alignment,
    create_layout_segment,
    create_representation as create_alignment_representation,
    get_curve as get_alignment_curve,
    get_horizontal_layout,
    get_layout_segments,
    get_vertical_layout,
)
from ifcopenshell.api.classification import (
    add_classification,
    add_reference as add_classification_reference,
    edit_classification,
    edit_reference as edit_classification_reference,
)
from ifcopenshell.api.context import add_context
from ifcopenshell.api.constraint import (
    add_metric,
    add_objective,
    assign_constraint,
    edit_metric,
    edit_objective,
)
from ifcopenshell.api.cost import (
    add_cost_item,
    add_cost_schedule as add_ifc_cost_schedule,
    add_cost_value,
    edit_cost_item,
    edit_cost_schedule,
    edit_cost_value,
)
from ifcopenshell.api.document import (
    add_information,
    add_reference,
    assign_document,
    edit_information,
    edit_reference,
)
from ifcopenshell.api.geometry import (
    add_mesh_representation,
    add_profile_representation,
    assign_representation,
    edit_object_placement,
)
from ifcopenshell.api.georeference import add_georeferencing, edit_georeferencing
from ifcopenshell.api.group import add_group, assign_group, edit_group
from ifcopenshell.api.layer import add_layer, assign_layer, edit_layer
from ifcopenshell.api.material import (
    add_material,
    add_material_set,
    add_profile,
    assign_material,
)
from ifcopenshell.api.profile import add_arbitrary_profile
from ifcopenshell.api.project import assign_declaration, create_file
from ifcopenshell.api.pset import add_pset, add_qto, edit_pset, edit_qto
from ifcopenshell.api.pset_template import add_prop_template, add_pset_template
from ifcopenshell.api.root import create_entity
from ifcopenshell.api.sequence import (
    add_task,
    add_task_time,
    add_work_schedule,
    assign_product,
    assign_sequence,
    edit_task_time,
)
from ifcopenshell.api.spatial import assign_container, reference_structure
from ifcopenshell.api.style import add_style, add_surface_style, assign_representation_styles
from ifcopenshell.api.system import add_system, assign_system, edit_system
from ifcopenshell.api.type import assign_type
from ifcopenshell.api.unit import add_monetary_unit, assign_unit

from osr_mech.cad import Compound, Part
from osr_mech.civil_systems_integration import (
    asset_class_for_component,
    asset_id_for_component,
    assert_integration_checks,
    digital_twin_manifest,
    integration_components,
    ZONE_ASSET_IDS,
)
from osr_mech.fabrication_assembly_twin import fabrication_streams
from osr_mech.civil.quantity_model import structure_quantities_per_km
from osr_mech.common import RAIL_GEOMETRY, RailProfile
from osr_mech.track.rail import rail_profile_points_mm


SCHEMA = "org.opensourcerail.bonsai-civil-ifc.v1"
NAMESPACE = uuid.UUID("5b6994b4-1642-48df-a10b-796985904590")
FIXED_HEADER_TIMESTAMP = "2026-01-01T00:00:00"
FIXED_REVIEW_TIMESTAMP = "2026-01-01T00:00:00Z"
FIXED_ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)
DEFAULT_START = datetime(2026, 1, 5, 8, 0, tzinfo=timezone.utc)
MAX_DETAIL_PARTS = 450

BOX_FACES = [
    [0, 1, 3, 2],
    [4, 6, 7, 5],
    [0, 4, 5, 1],
    [2, 3, 7, 6],
    [0, 2, 6, 4],
    [1, 5, 7, 3],
]

DISCIPLINES = {
    "track": ("Track", "TRACK"),
    "substructure": ("Substructure", "SUBSTRUCTURE"),
    "above-track": ("Stations and above-track systems", "ABOVETRACK"),
    "lineside": ("Clearance and lineside coordination", "LINESIDE"),
}

PRESENTATION_LAYERS = {
    "track": {
        "layer_id": "OSR-LAYER-TRACK",
        "name": "OSR Track",
        "description": "Track geometry for simple CAD/BIM visibility filtering.",
    },
    "substructure": {
        "layer_id": "OSR-LAYER-SUBSTRUCTURE",
        "name": "OSR Substructure",
        "description": "Substructure geometry for simple CAD/BIM visibility filtering.",
    },
    "above-track": {
        "layer_id": "OSR-LAYER-ABOVE-TRACK",
        "name": "OSR Stations and above-track systems",
        "description": "Station and above-track geometry for simple CAD/BIM visibility filtering.",
    },
    "lineside": {
        "layer_id": "OSR-LAYER-LINESIDE",
        "name": "OSR Clearance and lineside coordination",
        "description": "Clearance and lineside geometry for simple CAD/BIM visibility filtering.",
    },
}

OPTIONAL_PROPERTY_TEMPLATE_FIELDS = {
    "OSR_Georeferencing": {"ProjectedCrsName": "IfcLabel"},
}

COLOURS = {
    "track": (0.12, 0.18, 0.23),
    "substructure": (0.58, 0.64, 0.68),
    "above-track": (0.10, 0.55, 0.62),
    "lineside": (0.95, 0.48, 0.13),
}

MATERIAL_FAMILIES = {
    "OSR-MAT-FAMILY-RAIL-STEEL": {
        "label": "Rail steel family",
        "category": "steel",
        "description": "Running-rail steel; grade, heat treatment, supplier, and certificate remain unresolved.",
        "source_authority": "mechanical-py/src/osr_mech/track/rail.py",
    },
    "OSR-MAT-FAMILY-PRESTRESSED-CONCRETE": {
        "label": "Prestressed concrete family",
        "category": "concrete",
        "description": "Prestressed concrete beam family; mix, reinforcement, prestress, durability, and release remain unresolved.",
        "source_authority": "mechanical-py/src/osr_mech/civil/decked_pi.py",
    },
    "OSR-MAT-FAMILY-PRECAST-CONCRETE": {
        "label": "Precast concrete family",
        "category": "concrete",
        "description": "Precast platform-unit concrete family; grade, reinforcement, finish, and release remain unresolved.",
        "source_authority": "mechanical-py/src/osr_mech/civil/platform_l_unit.py",
    },
}

RAIL_PROFILE_ID = "OSR-PROFILE-UIC-60E1-REVIEW"

ASSET_CLASSIFICATION = {
    "name": "OpenSourceRail Asset Classification",
    "edition": "1.0",
    "description": (
        "Internal deterministic OSR asset classes for federation and automation; "
        "not equivalent to a nominated national or client classification."
    ),
    "specification": (
        "docs/civil/bonsai-ifc-workflow.md#native-osr-asset-classification"
    ),
    "references": {
        "civil.bearing": "Elastomeric bridge bearing",
        "civil.decked-pi-beam": "Decked Pi structural beam",
        "civil.foundation-interface": "Unreleased pier foundation interface",
        "civil.jacking-interface": "Bearing-replacement jacking interface",
        "civil.pier-cap": "Shared pier cap",
        "civil.pier-column": "Reinforced-concrete pier column",
        "civil.station-deck-interface": "Station deck structural interface",
        "civil.trackform": "Civil trackform",
        "civil.walkway-cassette": "Civil walkway and containment cassette",
        "clearance.reference-envelope": "Reference clearance envelope",
        "rolling-stock.trainset": "Rolling-stock trainset",
        "station.platform-interface": "Station platform interface",
        "station.solar-canopy": "Station solar canopy",
        "track.rail": "Running rail",
        "track.turnout": "Track turnout assembly",
    },
}

FUNCTIONAL_SYSTEMS = {
    "OSR-SYS-CIVIL-INTERFACES": {
        "name": "Civil design interfaces",
        "role": "unreleased-civil-interfaces",
        "ifc_class": "IfcSystem",
        "predefined_type": None,
        "asset_classes": {
            "civil.foundation-interface",
            "civil.jacking-interface",
        },
    },
    "OSR-SYS-CLEARANCE": {
        "name": "Clearance assurance system",
        "role": "clearance-assurance",
        "ifc_class": "IfcSystem",
        "predefined_type": None,
        "asset_classes": {"clearance.reference-envelope"},
    },
    "OSR-SYS-GUIDEWAY": {
        "name": "Guideway structural system",
        "role": "guideway-structure",
        "ifc_class": "IfcBuiltSystem",
        "predefined_type": "LOADBEARING",
        "asset_classes": {
            "civil.bearing",
            "civil.decked-pi-beam",
            "civil.pier-cap",
            "civil.pier-column",
            "civil.walkway-cassette",
        },
    },
    "OSR-SYS-ROLLING-STOCK": {
        "name": "Rolling-stock reference system",
        "role": "rolling-stock-reference",
        "ifc_class": "IfcSystem",
        "predefined_type": None,
        "asset_classes": {"rolling-stock.trainset"},
    },
    "OSR-SYS-STATION": {
        "name": "Station interface system",
        "role": "station-interface",
        "ifc_class": "IfcBuiltSystem",
        "predefined_type": "USERDEFINED",
        "asset_classes": {
            "civil.station-deck-interface",
            "station.platform-interface",
            "station.solar-canopy",
        },
    },
    "OSR-SYS-TRACK": {
        "name": "Track and running-way system",
        "role": "track-and-running-way",
        "ifc_class": "IfcBuiltSystem",
        "predefined_type": "RAILWAYTRACK",
        "asset_classes": {"civil.trackform", "track.rail", "track.turnout"},
    },
}

CONSTRAINT_EVIDENCE_SCOPES = {
    "complete-rolling-stock-present": {
        "asset_selectors": [
            {
                "asset_classes": {"rolling-stock.trainset"},
                "group_ids": {"OSR-DT-ZONE-RST-001"},
            }
        ],
        "group_ids": {"OSR-DT-ZONE-RST-001"},
        "system_ids": {"OSR-SYS-ROLLING-STOCK"},
    },
    "elevated-platform-horizontal-envelope-gap": {
        "asset_selectors": [
            {
                "asset_classes": {
                    "clearance.reference-envelope",
                    "station.platform-interface",
                },
                "group_ids": {"OSR-DT-ZONE-STN-ELEVATED-001"},
            }
        ]
    },
    "elevated-platform-vertical-datum": {
        "asset_selectors": [
            {
                "asset_classes": {"station.platform-interface", "track.rail"},
                "group_ids": {"OSR-DT-ZONE-STN-ELEVATED-001"},
            }
        ]
    },
    "ground-platform-horizontal-envelope-gap": {
        "asset_selectors": [
            {
                "asset_classes": {
                    "clearance.reference-envelope",
                    "station.platform-interface",
                },
                "group_ids": {"OSR-DT-ZONE-STN-GROUND-001"},
            }
        ]
    },
    "ground-platform-vertical-datum": {
        "asset_selectors": [
            {
                "asset_classes": {"station.platform-interface", "track.rail"},
                "group_ids": {"OSR-DT-ZONE-STN-GROUND-001"},
            }
        ]
    },
    "junction-turnout-present": {
        "asset_selectors": [
            {
                "asset_classes": {"track.turnout"},
                "group_ids": {"OSR-DT-ZONE-JCT-001"},
            }
        ]
    },
    "pier-bearing-to-girder-soffit": {
        "asset_selectors": [
            {
                "asset_classes": {
                    "civil.bearing",
                    "civil.decked-pi-beam",
                    "civil.pier-cap",
                },
                "group_ids": {"OSR-DT-ZONE-VIA-001"},
            }
        ]
    },
    "requested-system-zones-present": {
        "asset_selectors": [],
        "group_ids": set(ZONE_ASSET_IDS.values()),
    },
    "viaduct-to-station-track-support-datum": {
        "asset_selectors": [
            {"asset_classes": {"civil.decked-pi-beam"}},
            {"asset_classes": {"civil.station-deck-interface"}},
        ]
    },
}

EXTERNAL_ENGINEERING_DECISIONS = (
    {
        "decision_id": "OSR-DEC-SURVEY-ALIGNMENT",
        "title": "Accept survey-controlled horizontal and vertical alignment",
        "authority_required": "project surveyor and alignment engineer",
        "evidence_required": [
            "accepted CRS and vertical datum",
            "survey control and uncertainty",
            "design radii, transitions, vertical curves and cant",
        ],
        "blocked_capabilities": [
            "survey-grade IFC alignment",
            "product linear placement",
            "surveyed spatial zones",
        ],
        "safe_current_state": "validated local grid or explicit project map conversion",
    },
    {
        "decision_id": "OSR-DEC-GEOTECH-FOUNDATION",
        "title": "Release geotechnical model and foundation schedule",
        "authority_required": "geotechnical and foundation engineer",
        "evidence_required": [
            "ground investigation",
            "foundation type, depth and capacity schedule",
            "settlement, scour and groundwater assessment",
        ],
        "blocked_capabilities": [
            "physical IfcFooting or IfcDeepFoundation products",
            "foundation quantities and construction release",
        ],
        "safe_current_state": "nine explicit virtual foundation interfaces",
    },
    {
        "decision_id": "OSR-DEC-STRUCTURAL-RELEASE",
        "title": "Release structural design and reinforcement",
        "authority_required": "competent structural engineer",
        "evidence_required": [
            "load combinations and structural analysis",
            "reinforcement, prestress and connection schedules",
            "seismic, drainage, construction-stage and code checks",
        ],
        "blocked_capabilities": [
            "reinforcement and prestress IFC detailing",
            "structural capacity or construction-release claims",
        ],
        "safe_current_state": "non-overlapping design-reference envelopes",
    },
    {
        "decision_id": "OSR-DEC-BEARING-SUPPLIER",
        "title": "Select and release bridge bearings",
        "authority_required": "structural engineer and bearing supplier",
        "evidence_required": [
            "bearing loads and movement schedule",
            "stiffness, restraint and replacement requirements",
            "supplier model and certification",
        ],
        "blocked_capabilities": [
            "analytical bearing conditions",
            "supplier performance and release properties",
        ],
        "safe_current_state": "typed envelopes and physical support topology only",
    },
    {
        "decision_id": "OSR-DEC-MATERIAL-SPECIFICATION",
        "title": "Nominate project material specifications",
        "authority_required": "designer, client and procurement authority",
        "evidence_required": [
            "material grades, durability and finish requirements",
            "supplier certificates and approved substitutions",
        ],
        "blocked_capabilities": [
            "grade-specific IFC materials",
            "mixed-material constituent and certification data",
        ],
        "safe_current_state": "three source-backed family declarations",
    },
    {
        "decision_id": "OSR-DEC-CLASSIFICATION",
        "title": "Nominate jurisdiction and client classification",
        "authority_required": "client information manager",
        "evidence_required": [
            "classification system and edition",
            "approved OSR crosswalk and client requirements",
        ],
        "blocked_capabilities": ["national or client classification references"],
        "safe_current_state": "complete internal OSR asset classification",
    },
    {
        "decision_id": "OSR-DEC-COMMERCIAL-SCOPE",
        "title": "Approve commercial scope and rates",
        "authority_required": "client commercial and cost authority",
        "evidence_required": [
            "selected project scope",
            "approved unit rates and measurement rules",
            "supplier quotations and risk allowances",
        ],
        "blocked_capabilities": [
            "element-level cost assignments",
            "bill, tender or project total",
        ],
        "safe_current_state": "three mutually exclusive planning rates only",
    },
    {
        "decision_id": "OSR-DEC-ROLLING-STOCK-SUPPLIER",
        "title": "Release rolling-stock supplier data",
        "authority_required": "operator and rolling-stock supplier",
        "evidence_required": [
            "manufacturer and vehicle configuration",
            "mass, capacity, availability and operational data",
        ],
        "blocked_capabilities": [
            "supplier identity and operational vehicle property sets"
        ],
        "safe_current_state": "two dimensional design-reference trainsets",
    },
    {
        "decision_id": "OSR-DEC-CDE-DOCUMENT-CONTROL",
        "title": "Nominate drawing and common-data-environment controls",
        "authority_required": "client information manager and project approver",
        "evidence_required": [
            "naming and suitability convention",
            "CDE locations, transmittal and approval workflow",
        ],
        "blocked_capabilities": [
            "issued drawing records",
            "transmittal, suitability and approval claims",
        ],
        "safe_current_state": "hash-locked repository source register",
    },
)

DOCUMENT_SOURCES = {
    "OSR-DOC-ALIGNMENT-CONTRACT": {
        "name": "OSR alignment exchange contract",
        "path": "docs/civil/osr-aln-format.md",
        "purpose": "Alignment information contract",
        "scope": "Project and IFC reference alignment",
        "intended_use": "Design-reference alignment exchange and traceability",
        "media_type": "text/markdown",
    },
    "OSR-DOC-BIM-WORKFLOW": {
        "name": "OSR Bonsai IFC workflow and release boundary",
        "path": "docs/civil/bonsai-ifc-workflow.md",
        "purpose": "IFC workflow and engineering release boundary",
        "scope": "Project",
        "intended_use": "Coordination review; not construction release",
        "media_type": "text/markdown",
    },
    "OSR-DOC-CIVIL-COST-CONTRACT": {
        "name": "OSR generated civil planning-cost contract",
        "path": "lib/templates/civil-cost-model.toml",
        "purpose": "Planning cost and quantity contract",
        "scope": "Project; no element-level tender rates",
        "intended_use": "Planning sensitivity and deterministic regeneration",
        "media_type": "application/toml",
    },
    "OSR-DOC-IFC-EXPORTER": {
        "name": "OSR deterministic civil IFC exporter",
        "path": "engineering/interchange/civil_bonsai_ifc.py",
        "purpose": "IFC generation implementation",
        "scope": "Project",
        "intended_use": "Reproducible design-reference exchange generation",
        "media_type": "text/x-python",
    },
    "OSR-DOC-SOURCE-CIVIL-INTEGRATION": {
        "name": "OSR civil systems integration source",
        "path": "mechanical-py/src/osr_mech/civil_systems_integration.py",
        "purpose": "Federation placement and interface source",
        "scope": "Project, all component occurrences, and reusable types",
        "intended_use": "Design-reference geometry orchestration",
        "media_type": "text/x-python",
    },
    "OSR-DOC-SOURCE-CLEARANCE": {
        "name": "OSR clearance envelope source",
        "path": "mechanical-py/src/osr_mech/clearance/envelope.py",
        "purpose": "Clearance review geometry source",
        "scope": "Clearance-envelope occurrences and types",
        "intended_use": "Interface screening; not gauging release",
        "media_type": "text/x-python",
    },
    "OSR-DOC-SOURCE-DECKED-PI": {
        "name": "OSR decked Pi and walkway source",
        "path": "mechanical-py/src/osr_mech/civil/decked_pi.py",
        "purpose": "Viaduct beam and walkway geometry source",
        "scope": "Decked-Pi and walkway occurrences and types",
        "intended_use": "Design-reference civil coordination",
        "media_type": "text/x-python",
    },
    "OSR-DOC-SOURCE-GUIDEWAY-EDGE": {
        "name": "OSR guideway edge source",
        "path": "mechanical-py/src/osr_mech/civil/guideway_channel_edge.py",
        "purpose": "Guideway edge geometry source",
        "scope": "Guideway-edge occurrences and types",
        "intended_use": "Design-reference platform and drainage coordination",
        "media_type": "text/x-python",
    },
    "OSR-DOC-SOURCE-PLATFORM": {
        "name": "OSR platform unit source",
        "path": "mechanical-py/src/osr_mech/civil/platform_l_unit.py",
        "purpose": "Platform unit geometry source",
        "scope": "Platform-unit occurrences and types",
        "intended_use": "Design-reference platform coordination",
        "media_type": "text/x-python",
    },
    "OSR-DOC-SOURCE-RAIL": {
        "name": "OSR rail profile and bar source",
        "path": "mechanical-py/src/osr_mech/track/rail.py",
        "purpose": "Rail profile and extrusion source",
        "scope": "Rail occurrences, types, and native profile",
        "intended_use": "Coordination profile; full mill profile remains required",
        "media_type": "text/x-python",
    },
    "OSR-DOC-SOURCE-ROLLING-STOCK": {
        "name": "OSR trainset geometry source",
        "path": "mechanical-py/src/osr_mech/rolling_stock/trainset.py",
        "purpose": "Rolling-stock coordination geometry source",
        "scope": "Trainset occurrences and types",
        "intended_use": "Physical-envelope and interface review",
        "media_type": "text/x-python",
    },
    "OSR-DOC-SOURCE-SLAB": {
        "name": "OSR slab trackform source",
        "path": "mechanical-py/src/osr_mech/civil/slab.py",
        "purpose": "At-grade and elevated trackform geometry source",
        "scope": "Trackform occurrences and types",
        "intended_use": "Design-reference civil coordination",
        "media_type": "text/x-python",
    },
    "OSR-DOC-SOURCE-STATION-CANOPY": {
        "name": "OSR station canopy source",
        "path": "mechanical-py/src/osr_mech/station/canopy.py",
        "purpose": "Station canopy geometry source",
        "scope": "Canopy occurrences and types",
        "intended_use": "Design-reference station coordination",
        "media_type": "text/x-python",
    },
    "OSR-DOC-SOURCE-SUBSTRUCTURE": {
        "name": "OSR viaduct substructure source",
        "path": "mechanical-py/src/osr_mech/civil/substructure.py",
        "purpose": "Pier and foundation-interface geometry source",
        "scope": "Pier occurrences and types",
        "intended_use": "Interface review; foundation design remains unresolved",
        "media_type": "text/x-python",
    },
    "OSR-DOC-SOURCE-TURNOUT": {
        "name": "OSR turnout geometry source",
        "path": "mechanical-py/src/osr_mech/track/turnout.py",
        "purpose": "Turnout coordination geometry source",
        "scope": "Turnout occurrences and types",
        "intended_use": "Design-reference track coordination",
        "media_type": "text/x-python",
    },
}

COMPONENT_DOCUMENT_PREFIXES = (
    ("civil.at_grade_slab_panel", "OSR-DOC-SOURCE-SLAB"),
    ("civil.decked_pi_structural_placeholder", "OSR-DOC-SOURCE-DECKED-PI"),
    ("civil.elevated_deck_slab_panel", "OSR-DOC-SOURCE-SLAB"),
    ("civil.guideway_channel_edge_module", "OSR-DOC-SOURCE-GUIDEWAY-EDGE"),
    ("civil.platform_l_unit", "OSR-DOC-SOURCE-PLATFORM"),
    ("civil.viaduct_pier", "OSR-DOC-SOURCE-SUBSTRUCTURE"),
    ("civil.walkway_cassette", "OSR-DOC-SOURCE-DECKED-PI"),
    ("clearance.swept_envelope_part", "OSR-DOC-SOURCE-CLEARANCE"),
    ("integration.elevated_station_deck_interface", "OSR-DOC-SOURCE-CIVIL-INTEGRATION"),
    ("rolling_stock.trainset", "OSR-DOC-SOURCE-ROLLING-STOCK"),
    ("station.station_canopy", "OSR-DOC-SOURCE-STATION-CANOPY"),
    ("track.rail_bar", "OSR-DOC-SOURCE-RAIL"),
    ("track.turnout", "OSR-DOC-SOURCE-TURNOUT"),
)


def stable_guid(value: str) -> str:
    return ifcopenshell.guid.compress(uuid.uuid5(NAMESPACE, value).hex)


def stable_uuid(value: str) -> str:
    return str(uuid.uuid5(NAMESPACE, value))


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def component_document_ids(source_geometry: str) -> tuple[str, ...]:
    """Resolve each component to its orchestration and direct geometry sources."""

    direct = next(
        (
            document_id
            for prefix, document_id in COMPONENT_DOCUMENT_PREFIXES
            if source_geometry.startswith(prefix)
        ),
        None,
    )
    if direct is None:
        raise ValueError(f"no repository source document mapped for {source_geometry!r}")
    return tuple(sorted({"OSR-DOC-SOURCE-CIVIL-INTEGRATION", direct}))


def flatten_parts(part: Part | Compound) -> list[Part]:
    if isinstance(part, Compound):
        leaves: list[Part] = []
        for child in part.children:
            leaves.extend(flatten_parts(child))
        return leaves
    return [part]


@dataclass(frozen=True)
class IfcExportComponent:
    """One non-overlapping IFC occurrence derived from source CAD geometry."""

    zone: str
    label: str
    source: str
    asset_id: str
    asset_class: str
    source_component_id: str
    source_part_role: str
    geometry: Part | Compound

    def build(self) -> Part | Compound:
        return self.geometry


PIER_PART_RULES = {
    "Common pier-to-foundation interface; foundation depth intentionally not modelled": (
        "civil.foundation-interface",
        "foundation-interface",
        "FND",
    ),
    "Single reinforced-concrete pier column": (
        "civil.pier-column",
        "column",
        "COL",
    ),
    "Hollow/precast-shell shared pier cap envelope": (
        "civil.pier-cap",
        "pier-cap",
        "CAP",
    ),
    "Permanent bearing-replacement jacking shelf interface": (
        "civil.jacking-interface",
        "jacking-interface",
        "JCK",
    ),
    "Elastomeric/PTFE girder bearing": (
        "civil.bearing",
        "bearing",
        "BRG",
    ),
}


def ifc_export_components() -> tuple[IfcExportComponent, ...]:
    """Split source pier compounds only where leaf identity is authoritative.

    The original coordination model treats a complete pier kit as one source
    component. IFC needs non-overlapping occurrences for native bearing and
    structural-element semantics. Foundation and jacking geometry remain
    interfaces rather than falsely released physical products.
    """

    exported: list[IfcExportComponent] = []
    for component in integration_components():
        source_component_id = asset_id_for_component(component)
        asset_class = asset_class_for_component(component)
        built = component.build()
        if asset_class != "civil.pier":
            exported.append(
                IfcExportComponent(
                    zone=component.zone,
                    label=component.label,
                    source=component.source,
                    asset_id=source_component_id,
                    asset_class=asset_class,
                    source_component_id=source_component_id,
                    source_part_role="whole-source-component",
                    geometry=built,
                )
            )
            continue

        role_counts: Counter[str] = Counter()
        leaves = [leaf for leaf in flatten_parts(built) if leaf.bounding_box().volume > 0.0]
        for leaf in leaves:
            if leaf.label not in PIER_PART_RULES:
                raise ValueError(f"unmapped authoritative pier part {leaf.label!r}")
            part_class, part_role, suffix = PIER_PART_RULES[leaf.label]
            role_counts[part_role] += 1
            ordinal = role_counts[part_role]
            exported.append(
                IfcExportComponent(
                    zone=component.zone,
                    label=f"{component.label} · {leaf.label} {ordinal}",
                    source=f"{component.source}#{part_role}",
                    asset_id=f"{source_component_id}-{suffix}-{ordinal:02d}",
                    asset_class=part_class,
                    source_component_id=source_component_id,
                    source_part_role=part_role,
                    geometry=leaf,
                )
            )
        expected = {
            "foundation-interface": 1,
            "column": 1,
            "pier-cap": 1,
            "jacking-interface": 4,
            "bearing": 4,
        }
        if dict(role_counts) != expected:
            raise ValueError(
                f"pier part inventory changed for {component.label!r}: "
                f"observed={dict(role_counts)!r}, expected={expected!r}"
            )
    return tuple(exported)


def bbox_tuple(part: Part) -> tuple[float, float, float, float, float, float]:
    box = part.bounding_box()
    return (box.min.X, box.min.Y, box.min.Z, box.max.X, box.max.Y, box.max.Z)


def bbox_union(boxes: Iterable[tuple[float, float, float, float, float, float]]) -> tuple[float, ...]:
    values = list(boxes)
    return (
        min(box[0] for box in values),
        min(box[1] for box in values),
        min(box[2] for box in values),
        max(box[3] for box in values),
        max(box[4] for box in values),
        max(box[5] for box in values),
    )


def box_mesh(box: tuple[float, ...], origin: tuple[float, float, float]) -> list[tuple[float, float, float]]:
    x0, y0, z0, x1, y1, z1 = (value / 1000.0 for value in box)
    ox, oy, oz = origin
    return [
        (x - ox, y - oy, z - oz)
        for x in (x0, x1)
        for y in (y0, y1)
        for z in (z0, z1)
    ]


def component_discipline(asset_class: str) -> str:
    if asset_class in {"track.rail", "track.turnout", "civil.trackform"}:
        return "track"
    if asset_class in {
        "civil.bearing",
        "civil.pier",
        "civil.foundation-interface",
        "civil.jacking-interface",
        "civil.pier-cap",
        "civil.pier-column",
        "civil.decked-pi-beam",
        "civil.walkway-cassette",
        "civil.u-girder",
        "civil.station-deck-interface",
    }:
        return "substructure"
    if asset_class.startswith("station.") or asset_class == "rolling-stock.trainset":
        return "above-track"
    return "lineside"


def ifc_type(asset_class: str) -> tuple[str, str | None]:
    return {
        "track.rail": ("IfcRail", "RAIL"),
        "track.turnout": ("IfcElementAssembly", "USERDEFINED"),
        "civil.trackform": ("IfcSlab", "BASESLAB"),
        "civil.bearing": ("IfcBearing", "ELASTOMERIC"),
        "civil.foundation-interface": ("IfcVirtualElement", None),
        "civil.jacking-interface": ("IfcVirtualElement", None),
        "civil.pier-cap": ("IfcBeam", "PIERCAP"),
        "civil.pier-column": ("IfcColumn", None),
        "civil.decked-pi-beam": ("IfcBeam", "GIRDER_SEGMENT"),
        "civil.walkway-cassette": ("IfcSlab", "USERDEFINED"),
        "civil.u-girder": ("IfcBeam", "GIRDER_SEGMENT"),
        "civil.station-deck-interface": ("IfcSlab", "BASESLAB"),
        "station.solar-canopy": ("IfcRoof", None),
        "station.platform-interface": ("IfcSlab", "FLOOR"),
        "clearance.reference-envelope": ("IfcVirtualElement", None),
        "rolling-stock.trainset": ("IfcVehicle", "ROLLINGSTOCK"),
    }.get(asset_class, ("IfcCivilElement", None))


def ifc_type_class(ifc_class: str) -> str | None:
    """Return a reusable IFC4.3 type class when the occurrence supports one."""

    return {
        "IfcRail": "IfcRailType",
        "IfcBearing": "IfcBearingType",
        "IfcElementAssembly": "IfcElementAssemblyType",
        "IfcSlab": "IfcSlabType",
        "IfcColumn": "IfcColumnType",
        "IfcBeam": "IfcBeamType",
        "IfcRoof": "IfcRoofType",
        "IfcVehicle": "IfcVehicleType",
    }.get(ifc_class)


def component_type_identity(asset_class: str, source_geometry: str) -> tuple[str, str]:
    """Create stable type identity from the exact authoritative geometry recipe."""

    digest = sha256_bytes(
        canonical_json({"asset_class": asset_class, "source_geometry": source_geometry})
    )
    return f"OSR-TYPE-{digest[:12].upper()}", digest


def material_family_id(asset_class: str, source_geometry: str) -> str | None:
    """Return only material families explicitly supported by authoritative source."""

    if asset_class == "track.rail":
        return "OSR-MAT-FAMILY-RAIL-STEEL"
    if asset_class == "civil.decked-pi-beam":
        return "OSR-MAT-FAMILY-PRESTRESSED-CONCRETE"
    if asset_class == "station.platform-interface" and "platform_l_unit" in source_geometry:
        return "OSR-MAT-FAMILY-PRECAST-CONCRETE"
    return None


def material_ids_from_assignment(material: Any) -> tuple[str, ...]:
    """Resolve physical IfcMaterial names through sets and set usages."""

    if material is None:
        return ()
    if material.is_a("IfcMaterial"):
        return (material.Name,)
    if material.is_a("IfcMaterialProfileSetUsage"):
        material = material.ForProfileSet
    elif material.is_a("IfcMaterialLayerSetUsage"):
        material = material.ForLayerSet
    if material.is_a("IfcMaterialProfileSet"):
        return tuple(
            item.Material.Name
            for item in material.MaterialProfiles or ()
            if item.Material is not None
        )
    if material.is_a("IfcMaterialLayerSet"):
        return tuple(
            item.Material.Name
            for item in material.MaterialLayers or ()
            if item.Material is not None
        )
    if material.is_a("IfcMaterialConstituentSet"):
        return tuple(
            item.Material.Name
            for item in material.MaterialConstituents or ()
            if item.Material is not None
        )
    return ()


def profile_id_for_component(asset_class: str, source_geometry: str) -> str | None:
    if asset_class == "track.rail" and "UIC_60E1" in source_geometry:
        return RAIL_PROFILE_ID
    return None


def rail_profile_points_m() -> tuple[tuple[float, float], ...]:
    """Return the CAD rail polygon in metres, centred at cardinal point 5."""

    geometry = RAIL_GEOMETRY[RailProfile.UIC_60E1]
    half_height_m = geometry.height_mm / 2_000.0
    points = tuple(
        (x_mm / 1_000.0, y_mm / 1_000.0 - half_height_m)
        for x_mm, y_mm in rail_profile_points_mm(RailProfile.UIC_60E1)
    )
    return points + (points[0],)


def polygon_area(points: tuple[tuple[float, float], ...]) -> float:
    return abs(
        sum(
            x1 * y2 - x2 * y1
            for (x1, y1), (x2, y2) in zip(points, points[1:])
        )
    ) / 2.0


def make_style(model: ifcopenshell.file, name: str, colour: tuple[float, float, float], transparency: float = 0.0):
    style = add_style(model, name=name)
    add_surface_style(
        model,
        style=style,
        ifc_class="IfcSurfaceStyleRendering",
        attributes={
            "SurfaceColour": {"Name": None, "Red": colour[0], "Green": colour[1], "Blue": colour[2]},
            "Transparency": transparency,
            "ReflectanceMethod": "NOTDEFINED",
        },
    )
    return style


def set_properties(model: ifcopenshell.file, product: Any, name: str, values: dict[str, Any]) -> None:
    pset = add_pset(model, product=product, name=name)
    edit_pset(model, pset=pset, properties=values)


def set_quantities(
    model: ifcopenshell.file,
    product: Any,
    name: str,
    values: dict[str, Any],
) -> None:
    """Attach measured values as native IFC quantities, not generic properties."""

    quantity_set = add_qto(model, product=product, name=name)
    quantity_set.MethodOfMeasurement = "OSR deterministic geometry v1"
    edit_qto(model, qto=quantity_set, properties=values)


def validate_georeferencing(value: Any) -> dict[str, Any] | None:
    """Validate an explicit survey/GIS transform without inventing project coordinates."""

    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("georeferencing must be an object")
    allowed = {
        "crs_name",
        "description",
        "geodetic_datum",
        "vertical_datum",
        "map_projection",
        "map_zone",
        "eastings",
        "northings",
        "orthogonal_height",
        "x_axis_abscissa",
        "x_axis_ordinate",
        "scale",
        "source",
    }
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"unsupported georeferencing fields: {', '.join(unknown)}")
    required = {"crs_name", "eastings", "northings", "orthogonal_height"}
    missing = sorted(required - set(value))
    if missing:
        raise ValueError(f"georeferencing requires: {', '.join(missing)}")
    crs_name = value["crs_name"]
    if (
        not isinstance(crs_name, str)
        or not crs_name.startswith("EPSG:")
        or not crs_name[5:].isdigit()
    ):
        raise ValueError("georeferencing crs_name must be a single EPSG identifier such as EPSG:9306")
    numeric_fields = {
        "eastings": 0.0,
        "northings": 0.0,
        "orthogonal_height": 0.0,
        "x_axis_abscissa": 1.0,
        "x_axis_ordinate": 0.0,
        "scale": 1.0,
    }
    result = dict(value)
    for field, default in numeric_fields.items():
        number = result.get(field, default)
        if (
            isinstance(number, bool)
            or not isinstance(number, (int, float))
            or not math.isfinite(number)
        ):
            raise ValueError(f"georeferencing {field} must be a finite number")
        result[field] = float(number)
    if result["scale"] <= 0.0:
        raise ValueError("georeferencing scale must be greater than zero")
    if math.hypot(result["x_axis_abscissa"], result["x_axis_ordinate"]) < 1e-12:
        raise ValueError("georeferencing x-axis direction must be non-zero")
    for field in (
        "description",
        "geodetic_datum",
        "vertical_datum",
        "map_projection",
        "map_zone",
        "source",
    ):
        if field in result and (not isinstance(result[field], str) or not result[field].strip()):
            raise ValueError(f"georeferencing {field} must be a non-empty string")
    return result


def load_alignment(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    points = value.get("points")
    if not isinstance(points, list) or len(points) < 2:
        raise ValueError("alignment input requires at least two local XYZ points")
    for point in points:
        if (
            not isinstance(point, list)
            or len(point) != 3
            or not all(
                not isinstance(item, bool)
                and isinstance(item, (int, float))
                and math.isfinite(item)
                for item in point
            )
        ):
            raise ValueError("alignment points must be numeric [x, y, z] triples in metres")
    for point_index, (start, finish) in enumerate(zip(points, points[1:])):
        if math.hypot(finish[0] - start[0], finish[1] - start[1]) <= 1e-9:
            raise ValueError(
                f"alignment points {point_index} and {point_index + 1} "
                "must have distinct horizontal coordinates"
            )
    if "start_chainage_m" in value:
        start_chainage = value["start_chainage_m"]
        if (
            isinstance(start_chainage, bool)
            or not isinstance(start_chainage, (int, float))
            or not math.isfinite(start_chainage)
        ):
            raise ValueError("alignment start_chainage_m must be a finite number")
        value["start_chainage_m"] = float(start_chainage)
    if "georeferencing" in value:
        value["georeferencing"] = validate_georeferencing(value["georeferencing"])
    return value


def apply_georeferencing(
    model: ifcopenshell.file,
    project: Any,
    alignment_input: dict[str, Any] | None,
) -> dict[str, Any]:
    """Write IFC map conversion only when an explicit, validated CRS is supplied."""

    georeferencing = validate_georeferencing((alignment_input or {}).get("georeferencing"))
    if georeferencing is None:
        result = {
            "mode": "local-engineering-grid",
            "native_ifc_georeferencing": False,
            "status": "project-crs-unresolved",
            "source": "No accepted CRS/map conversion supplied",
        }
    else:
        add_georeferencing(model, ifc_class="IfcMapConversion", name=georeferencing["crs_name"])
        projected_crs = {
            "Name": georeferencing["crs_name"],
        }
        for source_name, ifc_name in (
            ("description", "Description"),
            ("geodetic_datum", "GeodeticDatum"),
            ("vertical_datum", "VerticalDatum"),
            ("map_projection", "MapProjection"),
            ("map_zone", "MapZone"),
        ):
            if source_name in georeferencing:
                projected_crs[ifc_name] = georeferencing[source_name]
        coordinate_operation = {
            "Eastings": georeferencing["eastings"],
            "Northings": georeferencing["northings"],
            "OrthogonalHeight": georeferencing["orthogonal_height"],
            "XAxisAbscissa": georeferencing["x_axis_abscissa"],
            "XAxisOrdinate": georeferencing["x_axis_ordinate"],
            "Scale": georeferencing["scale"],
        }
        edit_georeferencing(
            model,
            projected_crs=projected_crs,
            coordinate_operation=coordinate_operation,
        )
        result = {
            "mode": "ifc-map-conversion",
            "native_ifc_georeferencing": True,
            "status": "declared-from-project-input",
            "crs_name": georeferencing["crs_name"],
            "source": georeferencing.get("source", "Alignment input"),
            "map_conversion": {
                "eastings": georeferencing["eastings"],
                "northings": georeferencing["northings"],
                "orthogonal_height": georeferencing["orthogonal_height"],
                "x_axis_abscissa": georeferencing["x_axis_abscissa"],
                "x_axis_ordinate": georeferencing["x_axis_ordinate"],
                "scale": georeferencing["scale"],
            },
        }
    pset_values = {
        "CoordinateReferenceStatus": result["status"],
        "NativeIfcGeoreferencing": result["native_ifc_georeferencing"],
        "TransformSource": result["source"],
    }
    if result.get("crs_name"):
        pset_values["ProjectedCrsName"] = result["crs_name"]
    set_properties(model, project, "OSR_Georeferencing", pset_values)
    return result


def add_alignment(
    model: ifcopenshell.file,
    alignment_input: dict[str, Any] | None,
    revision_id: str,
) -> tuple[Any, dict[str, Any]]:
    """Create a semantic IFC4.3 planning alignment without inventing design curves."""

    name = (alignment_input or {}).get("line_slug", "osr-civil-reference-axis")
    points = [
        tuple(float(coordinate) for coordinate in point)
        for point in (alignment_input or {}).get(
            "points", [[0.0, 0.0, 0.0], [320.0, 0.0, 0.0]]
        )
    ]
    start_station = float((alignment_input or {}).get("start_chainage_m", 0.0))
    alignment = create_alignment(
        model,
        name=name,
        include_vertical=True,
        include_geometry=False,
        start_station=start_station,
    )
    horizontal = get_horizontal_layout(alignment)
    vertical = get_vertical_layout(alignment)
    horizontal.Name = f"{name} · horizontal planning layout"
    vertical.Name = f"{name} · vertical planning layout"

    total_length = 0.0
    final_bearing = 0.0
    final_grade = 0.0
    for segment_index, (start, finish) in enumerate(zip(points, points[1:]), start=1):
        dx = finish[0] - start[0]
        dy = finish[1] - start[1]
        horizontal_length = math.hypot(dx, dy)
        if horizontal_length <= 1e-9:
            raise ValueError(
                f"alignment segment {segment_index} has no horizontal length"
            )
        bearing = math.atan2(dy, dx)
        grade = (finish[2] - start[2]) / horizontal_length
        horizontal_parameters = model.create_entity(
            "IfcAlignmentHorizontalSegment",
            StartPoint=model.create_entity(
                "IfcCartesianPoint", Coordinates=(start[0], start[1])
            ),
            StartDirection=bearing,
            StartRadiusOfCurvature=0.0,
            EndRadiusOfCurvature=0.0,
            SegmentLength=horizontal_length,
            PredefinedType="LINE",
        )
        create_layout_segment(
            model,
            layout=horizontal,
            design_parameters=horizontal_parameters,
        )
        horizontal_segment = get_layout_segments(horizontal)[-2]
        horizontal_segment.Name = f"{name} · H{segment_index:03d} · LINE"

        vertical_parameters = model.create_entity(
            "IfcAlignmentVerticalSegment",
            StartDistAlong=total_length,
            HorizontalLength=horizontal_length,
            StartHeight=start[2],
            StartGradient=grade,
            EndGradient=grade,
            PredefinedType="CONSTANTGRADIENT",
        )
        create_layout_segment(
            model,
            layout=vertical,
            design_parameters=vertical_parameters,
        )
        vertical_segment = get_layout_segments(vertical)[-2]
        vertical_segment.Name = (
            f"{name} · V{segment_index:03d} · CONSTANTGRADIENT"
        )
        total_length += horizontal_length
        final_bearing = bearing
        final_grade = grade

    horizontal_end = get_layout_segments(horizontal)[-1]
    horizontal_end.Name = f"{name} · horizontal end"
    horizontal_end.DesignParameters.StartPoint.Coordinates = points[-1][:2]
    horizontal_end.DesignParameters.StartDirection = final_bearing
    vertical_end = get_layout_segments(vertical)[-1]
    vertical_end.Name = f"{name} · vertical end"
    vertical_end.DesignParameters.StartDistAlong = total_length
    vertical_end.DesignParameters.StartHeight = points[-1][2]
    vertical_end.DesignParameters.StartGradient = final_grade
    vertical_end.DesignParameters.EndGradient = final_grade

    # IfcOpenShell's incremental geometry update evaluates the complete curve
    # after every inserted segment. City GIS lines commonly contain hundreds
    # of vertices, so author the semantic layouts first and map them once.
    create_alignment_representation(model, alignment=alignment)
    add_stationing_referent(
        model,
        alignment=alignment,
        distance_along=0.0,
        station=start_station,
        name=f"{start_station:.3f} m · alignment start",
        positioned_product=alignment,
    )
    add_stationing_referent(
        model,
        alignment=alignment,
        distance_along=total_length,
        station=start_station + total_length,
        name=f"{start_station + total_length:.3f} m · alignment end",
        positioned_product=alignment,
    )
    set_properties(
        model,
        alignment,
        "OSR_AlignmentAuthority",
        {
            "Authority": "OpenSourceRail deterministic alignment engine",
            "RevisionId": revision_id,
            "DesignSpeedKmh": float((alignment_input or {}).get("design_speed_kmh", 80.0)),
            "GeometryRole": (
                "Native IFC4.3 horizontal/vertical planning polyline; detailed "
                "engineering rules remain upstream"
            ),
            "PointCount": len(points),
        },
    )
    curve = get_alignment_curve(alignment)
    referents = model.by_type("IfcReferent")
    return alignment, {
        "name": name,
        "ifc_class": "IfcAlignment",
        "semantic_model": "native-ifc4.3-horizontal-and-vertical-layouts",
        "geometry_curve": curve.is_a() if curve is not None else None,
        "representation_identifiers": sorted(
            representation.RepresentationIdentifier
            for representation in alignment.Representation.Representations
        ),
        "start_station_m": start_station,
        "control_point_count": len(points),
        "control_points_m": [list(point) for point in points],
        "horizontal_segment_count": len(points) - 1,
        "horizontal_segment_type": "LINE",
        "vertical_segment_count": len(points) - 1,
        "vertical_segment_type": "CONSTANTGRADIENT",
        "stationing_referent_count": len(referents),
        "total_horizontal_length_m": round(total_length, 6),
        "cant_status": "not-modelled; accepted cant design unavailable",
        "transition_status": "not-modelled; planning polyline has no accepted radii",
        "release_status": "design-reference; not for construction",
    }


def add_schedule(
    model: ifcopenshell.file,
    products: dict[str, Any],
    product_classes: dict[str, str],
    product_names: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    schedule = add_work_schedule(
        model,
        name="OSR civil fabrication and construction sequence",
        predefined_type="PLANNED",
        start_time=DEFAULT_START,
    )
    stream_classes = {
        "track": {"track.rail", "track.turnout", "civil.trackform"},
        "station": {"station.solar-canopy", "station.platform-interface", "civil.station-deck-interface"},
        "viaduct": {
            "civil.bearing",
            "civil.foundation-interface",
            "civil.jacking-interface",
            "civil.pier-cap",
            "civil.pier-column",
            "civil.decked-pi-beam",
            "civil.walkway-cassette",
            "civil.u-girder",
            "civil.trackform",
            "track.rail",
        },
    }
    stage_output_classes = {
        "TRK-50": {"track.rail", "track.turnout", "civil.trackform"},
        "STN-40": {
            "station.solar-canopy",
            "station.platform-interface",
            "civil.station-deck-interface",
        },
        "VIA-05": {"civil.pier-column", "civil.pier-cap"},
        "VIA-50": {"civil.bearing", "civil.decked-pi-beam"},
        "VIA-60": {"civil.walkway-cassette", "civil.trackform", "track.rail"},
    }
    stage_review_classes = {
        "VIA-05": {"civil.foundation-interface"},
        "VIA-50": {"civil.jacking-interface"},
    }
    schedule_rows: list[dict[str, Any]] = []
    assignments: dict[str, list[str]] = {}
    schedule_candidate_ids: set[str] = set()
    cursor_by_stream: dict[str, datetime] = {}
    tasks_by_id: dict[str, Any] = {}
    for stream in fabrication_streams():
        if stream.id not in stream_classes:
            continue
        cursor = cursor_by_stream.setdefault(stream.id, DEFAULT_START)
        for stage in stream.stages:
            task = add_task(
                model,
                work_schedule=schedule,
                name=stage.title,
                description=f"{stage.work_center}; QA hold: {stage.qa_hold}",
                identification=stage.id,
                predefined_type="CONSTRUCTION",
            )
            task_time = add_task_time(model, task=task)
            finish = cursor + timedelta(days=stage.duration_days)
            edit_task_time(
                model,
                task_time=task_time,
                attributes={
                    "ScheduleStart": cursor,
                    "ScheduleFinish": finish,
                    "ScheduleDuration": f"P{stage.duration_days:g}D",
                },
            )
            if stage.predecessor and stage.predecessor in tasks_by_id:
                assign_sequence(
                    model,
                    relating_process=tasks_by_id[stage.predecessor],
                    related_process=task,
                    sequence_type="FINISH_START",
                )
            tasks_by_id[stage.id] = task
            candidate_ids = []
            for asset_id in products:
                asset_class = product_classes[asset_id]
                name = product_names[asset_id]
                if asset_class not in stream_classes[stream.id]:
                    continue
                if stream.id == "track" and not (
                    name.startswith("Ground-station") or "turnout" in name.lower()
                ):
                    continue
                if stream.id == "viaduct" and not (
                    name.startswith("Viaduct")
                    or name.startswith("Shared double-track pier")
                    or name.startswith("Elevated-station")
                ):
                    continue
                candidate_ids.append(asset_id)
            schedule_candidate_ids.update(candidate_ids)
            assigned_ids = sorted(
                asset_id
                for asset_id in candidate_ids
                if product_classes[asset_id] in stage_output_classes.get(stage.id, set())
            )
            review_gate_asset_ids = sorted(
                asset_id
                for asset_id in candidate_ids
                if product_classes[asset_id] in stage_review_classes.get(stage.id, set())
            )
            if assigned_ids:
                for asset_id in assigned_ids:
                    relationship = assign_product(
                        model,
                        relating_product=products[asset_id],
                        related_object=task,
                    )
                    relationship.Name = "OSR physical construction output"
                    relationship.Description = (
                        "Physical product completed by this task for deterministic 4D review."
                    )
                assignments[stage.id] = assigned_ids
            for asset_id in review_gate_asset_ids:
                relationship = assign_product(
                    model,
                    relating_product=products[asset_id],
                    related_object=task,
                )
                relationship.Name = "OSR virtual review interface"
                relationship.Description = (
                    "Virtual coordination interface checked by this task; not a constructed output."
                )
            schedule_rows.append(
                {
                    "id": stage.id,
                    "stream": stream.id,
                    "title": stage.title,
                    "start": cursor.isoformat(),
                    "finish": finish.isoformat(),
                    "duration_days": stage.duration_days,
                    "predecessor": stage.predecessor,
                    "qa_hold": stage.qa_hold,
                    "evidence": list(stage.evidence),
                    "assigned_asset_ids": assigned_ids,
                    "review_gate_asset_ids": review_gate_asset_ids,
                    "product_semantics": (
                        "physical outputs completed by this task"
                        if assigned_ids
                        else "no exported physical output at this task"
                    ),
                    "review_gate_semantics": (
                        "virtual coordination interfaces checked by this task; not constructed products"
                        if review_gate_asset_ids
                        else "none"
                    ),
                }
            )
            cursor = finish
        cursor_by_stream[stream.id] = cursor
    assigned_ids_flat = [asset_id for values in assignments.values() for asset_id in values]
    expected_output_ids = {
        asset_id
        for asset_id in schedule_candidate_ids
        if product_classes[asset_id]
        in {asset_class for classes in stage_output_classes.values() for asset_class in classes}
    }
    review_ids_flat = [
        asset_id
        for row in schedule_rows
        for asset_id in row["review_gate_asset_ids"]
    ]
    expected_review_ids = {
        asset_id
        for asset_id in schedule_candidate_ids
        if product_classes[asset_id]
        in {asset_class for classes in stage_review_classes.values() for asset_class in classes}
    }
    if len(assigned_ids_flat) != len(set(assigned_ids_flat)):
        raise ValueError("construction outputs must be assigned to exactly one task")
    if set(assigned_ids_flat) != expected_output_ids:
        raise ValueError("construction output mapping does not cover the eligible physical assets")
    if set(review_ids_flat) != expected_review_ids:
        raise ValueError("construction review gates do not cover the eligible virtual interfaces")
    if set(assigned_ids_flat) & set(review_ids_flat):
        raise ValueError("virtual review interfaces cannot also be construction outputs")
    return schedule_rows, assignments


def add_planning_rate_schedule(
    model: ifcopenshell.file,
    *,
    cost_model: dict[str, Any],
    cost_model_hash: str,
    length_unit: Any,
) -> tuple[Any, dict[str, Any]]:
    """Embed the generated planning rates without asserting a project estimate."""

    schedule = add_ifc_cost_schedule(
        model,
        name="OSR generated civil planning schedule of rates",
        predefined_type="SCHEDULEOFRATES",
    )
    edit_cost_schedule(
        model,
        cost_schedule=schedule,
        attributes={
            "Identification": "OSR-COST-RATES-001",
            "Description": (
                f"{cost_model['schema']['basis']}. Generated contract sha256:"
                f"{cost_model_hash}. This is a planning schedule of rates, not a "
                "bill, tender, quotation, or element-level estimate."
            ),
            "Status": cost_model["schema"]["maturity"],
            "UpdateDate": FIXED_REVIEW_TIMESTAMP,
        },
    )
    class_mapping = (
        ("at-grade", "at_grade", "At-grade civil works"),
        ("elevated", "elevated", "Elevated civil works"),
        ("bridge", "bridge", "Bridge civil works"),
    )
    item_rows: list[dict[str, Any]] = []
    for class_name, rate_key, label in class_mapping:
        rate = float(cost_model["civil_usd_per_km"][rate_key])
        class_data = cost_model["classes"][class_name]
        item = add_cost_item(model, cost_schedule=schedule)
        edit_cost_item(
            model,
            cost_item=item,
            attributes={
                "Identification": f"OSR-RATE-{class_name.upper()}",
                "Name": label,
                "Description": (
                    "Generated design-target unit rate; planning sensitivity only. "
                    "No IFC products or element quantities are assigned."
                ),
                "PredefinedType": "USERDEFINED",
                "ObjectType": "Planning civil unit-rate alternative",
            },
        )
        value = add_cost_value(model, parent=item)
        edit_cost_value(
            model,
            cost_value=value,
            attributes={
                "Name": "Generated design target",
                "Description": (
                    "USD per route-kilometre from the hash-locked OSR civil cost contract"
                ),
                "AppliedValue": rate,
                "UnitBasis": {
                    "ValueComponent": 1_000.0,
                    "UnitComponent": length_unit,
                },
                "Category": "PLANNING_TARGET",
                "Condition": cost_model["schema"]["maturity"],
            },
        )
        item_rows.append(
            {
                "rate_id": item.Identification,
                "name": label,
                "civil_class": class_name,
                "ifc_class": "IfcCostItem",
                "rate_usd_per_route_km": rate,
                "benchmark_usd_per_route_km": float(
                    cost_model["benchmark_civil_usd_per_km"][rate_key]
                ),
                "design_to_benchmark_ratio": float(
                    class_data["design_to_benchmark_ratio"]
                ),
                "unit_basis_value_m": 1_000.0,
                "cost_value_category": "PLANNING_TARGET",
                "quantity_status": "none; schedule-of-rates entry only",
                "product_assignment_status": "none; alternatives are not selected scope",
                "drivers": [dict(driver) for driver in class_data.get("drivers", [])],
            }
        )
    return schedule, {
        "schedule_id": schedule.Identification,
        "name": schedule.Name,
        "ifc_class": "IfcCostSchedule",
        "predefined_type": schedule.PredefinedType,
        "currency": cost_model["schema"]["currency"],
        "unit_basis": "1 route-kilometre (1,000 project metres)",
        "maturity": cost_model["schema"]["maturity"],
        "basis": cost_model["schema"]["basis"],
        "source_path": "lib/templates/civil-cost-model.toml",
        "source_sha256": cost_model_hash,
        "item_count": len(item_rows),
        "items": item_rows,
        "scope_boundary": (
            "mutually exclusive planning alternatives; no selected scenario, "
            "product assignment, quantity multiplication, or project total"
        ),
    }


def add_asset_classification(
    model: ifcopenshell.file,
    *,
    project: Any,
    products: dict[str, Any],
    type_products: dict[tuple[str, str, str], Any],
    index_rows: list[dict[str, Any]],
    type_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Classify from authoritative OSR codes, inheriting through types where possible."""

    classification = add_classification(model, classification=ASSET_CLASSIFICATION["name"])
    edit_classification(
        model,
        classification=classification,
        attributes={
            "Source": "OpenSourceRail",
            "Edition": ASSET_CLASSIFICATION["edition"],
            "Name": ASSET_CLASSIFICATION["name"],
            "Description": ASSET_CLASSIFICATION["description"],
            "Specification": ASSET_CLASSIFICATION["specification"],
            "ReferenceTokens": ["."],
        },
    )
    set_properties(
        model,
        project,
        "OSR_Classification",
        {
            "System": ASSET_CLASSIFICATION["name"],
            "Edition": ASSET_CLASSIFICATION["edition"],
            "ReferenceCount": len(ASSET_CLASSIFICATION["references"]),
            "Status": "internal-deterministic-classification",
            "ExternalMappingStatus": "country-and-client-mapping-not-nominated",
        },
    )

    types_by_id = {item.Tag: item for item in type_products.values()}
    references: list[dict[str, Any]] = []
    for code, name in sorted(ASSET_CLASSIFICATION["references"].items()):
        type_ids = sorted(
            row["type_id"] for row in type_rows.values() if row["asset_class"] == code
        )
        inherited_asset_ids = sorted(
            row["asset_id"]
            for row in index_rows
            if row["asset_class"] == code and row["ifc_type_id"] is not None
        )
        direct_asset_ids = sorted(
            row["asset_id"]
            for row in index_rows
            if row["asset_class"] == code and row["ifc_type_id"] is None
        )
        targets = [types_by_id[type_id] for type_id in type_ids]
        targets.extend(products[asset_id] for asset_id in direct_asset_ids)
        reference = add_classification_reference(
            model,
            products=targets,
            classification=classification,
            identification=code,
            name=name,
        )
        if reference is None:
            raise ValueError(f"classification reference {code!r} has no IFC targets")
        edit_classification_reference(
            model,
            reference=reference,
            attributes={
                "Description": (
                    "Internal OSR automation class; map to the deployment's nominated "
                    "classification only through an approved crosswalk."
                )
            },
        )
        references.append(
            {
                "code": code,
                "name": name,
                "assignment": (
                    "direct-occurrence" if direct_asset_ids else "inherited-from-type"
                ),
                "assigned_type_ids": type_ids,
                "direct_asset_ids": direct_asset_ids,
                "inherited_asset_ids": inherited_asset_ids,
                "classified_asset_count": len(direct_asset_ids) + len(inherited_asset_ids),
            }
        )
    return {
        "name": ASSET_CLASSIFICATION["name"],
        "edition": ASSET_CLASSIFICATION["edition"],
        "description": ASSET_CLASSIFICATION["description"],
        "specification": ASSET_CLASSIFICATION["specification"],
        "status": "internal-deterministic-classification",
        "external_mapping_status": "country-and-client-mapping-not-nominated",
        "references": references,
    }


def add_coordination_groups(
    model: ifcopenshell.file,
    *,
    products: dict[str, Any],
    index_rows: list[dict[str, Any]],
    revision_id: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Preserve source review zones as non-spatial IFC groups."""

    group_entities: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    for source_zone, group_id in sorted(ZONE_ASSET_IDS.items()):
        asset_ids = sorted(
            row["asset_id"] for row in index_rows if row["coordination_group_id"] == group_id
        )
        if not asset_ids:
            raise ValueError(f"coordination group {group_id!r} has no assets")
        group = add_group(
            model,
            name=source_zone,
            description=(
                "OSR non-spatial coordination review group; the separated reference "
                "layout is not a surveyed city zone or functional engineering system."
            ),
        )
        edit_group(
            model,
            group=group,
            attributes={"ObjectType": "OSR coordination review group"},
        )
        set_properties(
            model,
            group,
            "OSR_CoordinationGroup",
            {
                "GroupId": group_id,
                "SourceZone": source_zone,
                "GroupRole": "non-spatial-review-group",
                "RevisionId": revision_id,
                "SpatialMeaning": "separated review layout; not a surveyed spatial zone",
                "SystemMeaning": "inspection grouping; not a functional engineering system",
            },
        )
        assign_group(
            model,
            products=[products[asset_id] for asset_id in asset_ids],
            group=group,
        )
        group_entities[group_id] = group
        rows.append(
            {
                "group_id": group_id,
                "name": source_zone,
                "ifc_class": "IfcGroup",
                "role": "non-spatial-review-group",
                "spatial_meaning": "separated review layout; not a surveyed spatial zone",
                "system_meaning": "inspection grouping; not a functional engineering system",
                "asset_ids": asset_ids,
                "asset_count": len(asset_ids),
            }
        )
    return group_entities, rows


def add_functional_systems(
    model: ifcopenshell.file,
    *,
    products: dict[str, Any],
    index_rows: list[dict[str, Any]],
    spatial_parts: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Assign every asset once to a native functional engineering system."""

    declared_classes = {
        asset_class
        for definition in FUNCTIONAL_SYSTEMS.values()
        for asset_class in definition["asset_classes"]
    }
    observed_classes = {row["asset_class"] for row in index_rows}
    if declared_classes != observed_classes:
        missing = sorted(observed_classes - declared_classes)
        unused = sorted(declared_classes - observed_classes)
        raise ValueError(
            "functional system asset-class coverage mismatch: "
            f"missing={missing!r}, unused={unused!r}"
        )

    system_entities: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    membership_counts: Counter[str] = Counter()
    for system_id, definition in sorted(FUNCTIONAL_SYSTEMS.items()):
        asset_ids = sorted(
            row["asset_id"]
            for row in index_rows
            if row["asset_class"] in definition["asset_classes"]
        )
        if not asset_ids:
            raise ValueError(f"functional system {system_id!r} has no assets")
        description = (
            f"OSR {definition['role']} functional design-reference system derived "
            "from authoritative asset classes; not a spatial zone, commissioned "
            "operational system, or safety release."
        )
        system = add_system(model, ifc_class=definition["ifc_class"])
        attributes = {
            "Name": definition["name"],
            "Description": description,
            "ObjectType": system_id,
        }
        if definition["ifc_class"] == "IfcBuiltSystem":
            attributes.update(
                {
                    "PredefinedType": definition["predefined_type"],
                    "LongName": f"OSR {definition['role']} design-reference system",
                }
            )
        edit_system(
            model,
            system=system,
            attributes=attributes,
        )
        relationship = assign_system(
            model,
            products=[products[asset_id] for asset_id in asset_ids],
            system=system,
        )
        if relationship is None:
            raise ValueError(f"functional system {system_id!r} was not assigned")
        spatial_disciplines = sorted(
            {row["discipline"] for row in index_rows if row["asset_id"] in asset_ids}
        )
        for discipline in spatial_disciplines:
            spatial_relationship = reference_structure(
                model,
                products=[system],
                relating_structure=spatial_parts[discipline],
            )
            if spatial_relationship is None:
                raise ValueError(
                    f"functional system {system_id!r} was not referenced from "
                    f"railway part {discipline!r}"
                )
        for row in index_rows:
            if row["asset_id"] in asset_ids:
                row["functional_system_id"] = system_id
                row["functional_system_name"] = definition["name"]
                membership_counts[row["asset_id"]] += 1
        system_entities[system_id] = system
        rows.append(
            {
                "system_id": system_id,
                "name": definition["name"],
                "ifc_class": definition["ifc_class"],
                "ifc_predefined_type": definition["predefined_type"],
                "long_name": getattr(system, "LongName", None),
                "role": definition["role"],
                "asset_classes": sorted(definition["asset_classes"]),
                "asset_ids": asset_ids,
                "asset_count": len(asset_ids),
                "semantics": "functional-engineering-system",
                "spatial_meaning": "none; not an IfcSpatialZone",
                "operational_status": "design-reference; not commissioned or operational",
                "membership_policy": (
                    "exactly one system per asset from authoritative OSR asset class"
                ),
                "spatial_disciplines": spatial_disciplines,
                "spatial_part_names": [
                    spatial_parts[discipline].Name
                    for discipline in spatial_disciplines
                ],
                "description": description,
            }
        )
    expected_assets = set(products)
    if set(membership_counts) != expected_assets or any(
        count != 1 for count in membership_counts.values()
    ):
        raise ValueError("functional systems must cover every asset exactly once")
    return system_entities, rows


def add_bearing_connections(
    model: ifcopenshell.file,
    *,
    products: dict[str, Any],
    index_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Connect caps to supported superstructure through source bearing geometry.

    Physical connectivity is inferred only from deterministic face contact:
    bearing top equals superstructure soffit, their plan envelopes overlap,
    and the bearing belongs to the same source pier as the cap. No analytical
    boundary condition, stiffness, movement capacity, or connection geometry
    is inferred.
    """

    rows_by_id = {row["asset_id"]: row for row in index_rows}
    bearings = [row for row in index_rows if row["asset_class"] == "civil.bearing"]
    caps = [row for row in index_rows if row["asset_class"] == "civil.pier-cap"]
    supported = [
        row
        for row in index_rows
        if row["asset_class"]
        in {"civil.decked-pi-beam", "civil.station-deck-interface"}
    ]

    def overlap(first: list[float], second: list[float], low: int, high: int) -> float:
        return min(first[high], second[high]) - max(first[low], second[low])

    connection_rows: list[dict[str, Any]] = []
    bearing_connection_ids: dict[str, list[str]] = defaultdict(list)
    element_connection_ids: dict[str, list[str]] = defaultdict(list)
    for cap in sorted(caps, key=lambda row: row["asset_id"]):
        cap_bearings = [
            bearing
            for bearing in bearings
            if bearing["source_component_id"] == cap["source_component_id"]
        ]
        if len(cap_bearings) != 4:
            raise ValueError(
                f"pier cap {cap['asset_id']!r} must resolve exactly four source bearings"
            )
        for superstructure in sorted(supported, key=lambda row: row["asset_id"]):
            realizing = [
                bearing
                for bearing in cap_bearings
                if abs(bearing["bbox_m"][5] - superstructure["bbox_m"][2]) <= 1e-6
                and overlap(bearing["bbox_m"], superstructure["bbox_m"], 0, 3) > 1e-9
                and overlap(bearing["bbox_m"], superstructure["bbox_m"], 1, 4) > 1e-9
            ]
            if not realizing:
                continue
            expected_realizers = (
                2 if superstructure["asset_class"] == "civil.decked-pi-beam" else 4
            )
            if len(realizing) != expected_realizers:
                raise ValueError(
                    f"bearing realization count changed for {cap['asset_id']!r} -> "
                    f"{superstructure['asset_id']!r}: {len(realizing)}"
                )
            connection_id = (
                f"OSR-CONN-{cap['asset_id'].removeprefix('OSR-DT-')}-"
                f"{superstructure['asset_id'].removeprefix('OSR-DT-')}"
            )
            relationship = model.create_entity(
                "IfcRelConnectsWithRealizingElements",
                GlobalId=stable_guid(f"bearing-connection:{connection_id}"),
                Name="OSR bearing-realized support connection",
                Description=(
                    "Geometrically derived design-reference connection; bearing family "
                    "is known but stiffness, loads, movements, supplier and release are unresolved."
                ),
                ConnectionGeometry=None,
                RelatingElement=products[cap["asset_id"]],
                RelatedElement=products[superstructure["asset_id"]],
                RealizingElements=[products[bearing["asset_id"]] for bearing in realizing],
                ConnectionType="elastomeric/PTFE support",
            )
            realizing_ids = sorted(bearing["asset_id"] for bearing in realizing)
            for bearing_id in realizing_ids:
                bearing_connection_ids[bearing_id].append(connection_id)
            element_connection_ids[cap["asset_id"]].append(connection_id)
            element_connection_ids[superstructure["asset_id"]].append(connection_id)
            connection_rows.append(
                {
                    "connection_id": connection_id,
                    "ifc_guid": relationship.GlobalId,
                    "ifc_class": relationship.is_a(),
                    "name": relationship.Name,
                    "connection_type": relationship.ConnectionType,
                    "relating_cap_asset_id": cap["asset_id"],
                    "related_superstructure_asset_id": superstructure["asset_id"],
                    "related_superstructure_asset_class": superstructure["asset_class"],
                    "realizing_bearing_asset_ids": realizing_ids,
                    "realizing_bearing_count": len(realizing_ids),
                    "derivation": "source bbox face contact; no connection geometry or analytical condition inferred",
                    "release_status": "design-reference; bearing schedule and structural release unresolved",
                }
            )

    if set(bearing_connection_ids) != {bearing["asset_id"] for bearing in bearings}:
        raise ValueError("every native bearing must realize at least one support connection")
    beam_ids = {
        row["asset_id"] for row in supported if row["asset_class"] == "civil.decked-pi-beam"
    }
    if any(len(element_connection_ids[asset_id]) != 2 for asset_id in beam_ids):
        raise ValueError("every decked Pi beam must resolve two bearing-supported ends")
    station_decks = [
        row for row in supported if row["asset_class"] == "civil.station-deck-interface"
    ]
    if any(len(element_connection_ids[row["asset_id"]]) != 3 for row in station_decks):
        raise ValueError("the station deck interface must resolve its three source pier supports")

    for bearing in bearings:
        connection_ids = sorted(bearing_connection_ids[bearing["asset_id"]])
        bearing["bearing_connection_ids"] = connection_ids
        bearing["bearing_connection_count"] = len(connection_ids)
        connected_cap_id = next(
            row["relating_cap_asset_id"]
            for row in connection_rows
            if bearing["asset_id"] in row["realizing_bearing_asset_ids"]
        )
        connected_superstructure_ids = sorted(
            row["related_superstructure_asset_id"]
            for row in connection_rows
            if bearing["asset_id"] in row["realizing_bearing_asset_ids"]
        )
        set_properties(
            model,
            products[bearing["asset_id"]],
            "OSR_BearingConnectivity",
            {
                "RealizedConnectionCount": len(connection_ids),
                "ConnectedCapAssetId": connected_cap_id,
                "ConnectedSuperstructureAssetIds": ",".join(connected_superstructure_ids),
                "ConnectivityDerivation": "source bbox face contact",
            },
        )
    for asset_id, connection_ids in element_connection_ids.items():
        rows_by_id[asset_id]["bearing_connection_ids"] = sorted(connection_ids)
        rows_by_id[asset_id]["bearing_connection_count"] = len(connection_ids)
    return sorted(connection_rows, key=lambda row: row["connection_id"])


def add_presentation_layers(
    model: ifcopenshell.file,
    *,
    products: dict[str, Any],
    index_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Assign each asset shape representation to one native discipline layer."""

    rows: list[dict[str, Any]] = []
    for discipline, declaration in sorted(PRESENTATION_LAYERS.items()):
        asset_ids = sorted(
            row["asset_id"] for row in index_rows if row["discipline"] == discipline
        )
        representations = [
            representation
            for asset_id in asset_ids
            for representation in products[asset_id].Representation.Representations
        ]
        if not representations:
            raise ValueError(f"presentation layer {declaration['layer_id']!r} has no geometry")
        layer = add_layer(model, name=declaration["name"])
        edit_layer(
            model,
            layer=layer,
            attributes={
                "Description": declaration["description"],
                "Identifier": declaration["layer_id"],
            },
        )
        assign_layer(model, items=representations, layer=layer)
        rows.append(
            {
                "layer_id": declaration["layer_id"],
                "name": declaration["name"],
                "description": declaration["description"],
                "ifc_class": "IfcPresentationLayerAssignment",
                "discipline": discipline,
                "assignment_scope": "IfcShapeRepresentation",
                "asset_ids": asset_ids,
                "asset_count": len(asset_ids),
                "representation_count": len(representations),
            }
        )
    return rows


def add_interface_constraints(
    model: ifcopenshell.file,
    *,
    project: Any,
    checks: Iterable[Any],
    products: dict[str, Any],
    index_rows: list[dict[str, Any]],
    group_entities: dict[str, Any],
    system_entities: dict[str, Any],
    document_references: dict[str, Any],
) -> list[dict[str, Any]]:
    """Publish source checks with project governance and precise IFC evidence."""

    rows: list[dict[str, Any]] = []
    objectives: list[Any] = []
    metrics: list[Any] = []
    for check in sorted(checks, key=lambda item: item.name):
        scope = CONSTRAINT_EVIDENCE_SCOPES.get(check.name)
        if scope is None:
            raise ValueError(f"interface constraint {check.name!r} has no evidence scope")
        asset_ids = sorted(
            {
                row["asset_id"]
                for selector in scope.get("asset_selectors", [])
                for row in index_rows
                if row["asset_class"] in selector["asset_classes"]
                and (
                    not selector.get("group_ids")
                    or row["coordination_group_id"] in selector["group_ids"]
                )
            }
        )
        group_ids = sorted(scope.get("group_ids", set()))
        system_ids = sorted(scope.get("system_ids", set()))
        if not asset_ids and not group_ids and not system_ids:
            raise ValueError(f"interface constraint {check.name!r} has empty evidence")
        related_objects = [
            project,
            *(products[asset_id] for asset_id in asset_ids),
            *(group_entities[group_id] for group_id in group_ids),
            *(system_entities[system_id] for system_id in system_ids),
        ]
        objective = add_objective(model)
        edit_objective(
            model,
            objective=objective,
            attributes={
                "Name": check.name,
                "Description": (
                    f"Current deterministic observation: {check.detail}. "
                    f"Evaluation status: {'PASS' if check.passed else 'FAIL'}."
                ),
                "ConstraintGrade": "HARD",
                "ConstraintSource": (
                    "mechanical-py/src/osr_mech/civil_systems_integration.py"
                ),
                "CreationTime": FIXED_REVIEW_TIMESTAMP,
                "ObjectiveQualifier": "DESIGNINTENT",
            },
        )
        relationship = assign_constraint(
            model,
            products=related_objects,
            constraint=objective,
        )
        if relationship is None:
            raise ValueError(f"interface constraint {check.name!r} has no IFC scope")
        relationship.Intent = "DESIGN VALIDATION EVIDENCE"
        objectives.append(objective)
        metric_row: dict[str, Any] | None = None
        if check.metric is not None:
            metric = add_metric(model, objective=objective)
            metric_id = f"{check.name}-metric"
            edit_metric(
                model,
                metric=metric,
                attributes={
                    "Name": metric_id,
                    "Description": (
                        f"{check.metric.name}: observed "
                        f"{check.metric.observed_value_m:.6f} {check.metric.unit}; "
                        f"target {check.metric.target_value_m:.6f} "
                        f"{check.metric.unit}. {check.metric.reference_path_status}."
                    ),
                    "ConstraintGrade": "HARD",
                    "ConstraintSource": (
                        "mechanical-py/src/osr_mech/civil_systems_integration.py"
                    ),
                    "CreationTime": FIXED_REVIEW_TIMESTAMP,
                    "Benchmark": check.metric.benchmark,
                    "ValueSource": (
                        "OpenSourceRail deterministic civil integration constants; "
                        f"SI {check.metric.unit}"
                    ),
                    "DataValue": model.create_entity(
                        check.metric.measure_type,
                        check.metric.target_value_m,
                    ),
                    "ReferencePath": None,
                },
            )
            metrics.append(metric)
            metric_row = {
                "metric_id": metric_id,
                "name": check.metric.name,
                "ifc_class": metric.is_a(),
                "benchmark": check.metric.benchmark,
                "measure_type": check.metric.measure_type,
                "unit": check.metric.unit,
                "observed_value": check.metric.observed_value_m,
                "target_value": check.metric.target_value_m,
                "value_source": metric.ValueSource,
                "reference_path": None,
                "reference_path_status": check.metric.reference_path_status,
            }
        rows.append(
            {
                "constraint_id": check.name,
                "name": check.name,
                "ifc_class": "IfcObjective",
                "constraint_grade": "HARD",
                "objective_qualifier": "DESIGNINTENT",
                "constraint_source": (
                    "mechanical-py/src/osr_mech/civil_systems_integration.py"
                ),
                "scope": "IfcProject governance plus deterministic related evidence",
                "association_intent": relationship.Intent,
                "related_asset_ids": asset_ids,
                "related_group_ids": group_ids,
                "related_system_ids": system_ids,
                "related_object_count": len(related_objects),
                "evaluation_status": "PASS" if check.passed else "FAIL",
                "observation": check.detail,
                "metric": metric_row,
                "metric_status": (
                    "structured-native-ifc-metric"
                    if metric_row is not None
                    else "qualitative-objective; no fabricated numeric benchmark"
                ),
            }
        )
    source_document_id = "OSR-DOC-SOURCE-CIVIL-INTEGRATION"
    source_relationship = model.create_entity(
        "IfcExternalReferenceRelationship",
        Name="OSR constraint source-document linkage",
        Description=(
            "Native link from each deterministic civil objective and metric to its "
            "registered, hash-locked repository source; not an approval or "
            "engineering release."
        ),
        RelatingReference=document_references[source_document_id],
        RelatedResourceObjects=[*objectives, *metrics],
    )
    for row in rows:
        row["external_source_document_ids"] = [source_document_id]
        row["external_reference_relationship"] = source_relationship.is_a()
    return rows


def add_property_templates(
    model: ifcopenshell.file,
    *,
    project: Any,
) -> list[dict[str, Any]]:
    """Embed typed templates for every OSR property and quantity set."""

    definitions_by_name: dict[str, list[Any]] = defaultdict(list)
    for ifc_class in (
        "IfcPropertySet",
        "IfcElementQuantity",
        "IfcMaterialProperties",
        "IfcProfileProperties",
    ):
        for definition in model.by_type(ifc_class):
            if definition.Name and definition.Name.startswith("OSR_"):
                definitions_by_name[definition.Name].append(definition)

    quantity_template_types = {
        "IfcQuantityLength": "Q_LENGTH",
        "IfcQuantityArea": "Q_AREA",
        "IfcQuantityVolume": "Q_VOLUME",
        "IfcQuantityCount": "Q_COUNT",
        "IfcQuantityWeight": "Q_WEIGHT",
        "IfcQuantityTime": "Q_TIME",
    }
    rows: list[dict[str, Any]] = []
    templates: list[Any] = []
    for name, definitions in sorted(definitions_by_name.items()):
        definition_class = definitions[0].is_a()
        if definition_class in {"IfcPropertySet", "IfcElementQuantity"}:
            owners = {
                owner
                for definition in definitions
                for relationship in definition.DefinesOccurrence
                for owner in relationship.RelatedObjects
            }
            owners.update(
                owner for definition in definitions for owner in definition.DefinesType
            )
        elif definition_class == "IfcMaterialProperties":
            owners = {definition.Material for definition in definitions}
        else:
            owners = {definition.ProfileDefinition for definition in definitions}
        applicable_entities = sorted({owner.is_a() for owner in owners})
        is_quantity = definition_class == "IfcElementQuantity"
        is_material = definition_class == "IfcMaterialProperties"
        is_profile = definition_class == "IfcProfileProperties"
        is_type_only = bool(owners) and all(owner.is_a("IfcTypeObject") for owner in owners)
        template_type = (
            "QTO_OCCURRENCEDRIVEN"
            if is_quantity
            else "PSET_MATERIALDRIVEN"
            if is_material
            else "PSET_PROFILEDRIVEN"
            if is_profile
            else "PSET_TYPEDRIVENONLY"
            if is_type_only
            else "PSET_OCCURRENCEDRIVEN"
        )
        template = add_pset_template(
            model,
            name=name,
            template_type=template_type,
            applicable_entity=",".join(applicable_entities),
        )
        template.Description = (
            "OpenSourceRail custom property dictionary embedded for deterministic "
            "authoring and exchange; not a buildingSMART standard property set."
        )
        templates.append(template)
        property_rows: list[dict[str, Any]] = []
        if is_quantity:
            members = {
                quantity.Name: quantity
                for definition in definitions
                for quantity in definition.Quantities
            }
            for property_name, quantity in sorted(members.items()):
                property_template_type = quantity_template_types[quantity.is_a()]
                add_prop_template(
                    model,
                    pset_template=template,
                    name=property_name,
                    description=f"OSR-defined {property_name} quantity.",
                    template_type=property_template_type,
                )
                property_rows.append(
                    {
                        "name": property_name,
                        "template_type": property_template_type,
                        "primary_measure_type": None,
                    }
                )
        else:
            members: dict[str, Any] = {}
            for definition in definitions:
                property_values = (
                    definition.HasProperties
                    if definition_class == "IfcPropertySet"
                    else definition.Properties
                )
                for property_value in property_values:
                    existing = members.get(property_value.Name)
                    if existing is not None and (
                        existing.NominalValue.is_a()
                        != property_value.NominalValue.is_a()
                    ):
                        raise ValueError(
                            f"property {name}.{property_value.Name} has inconsistent IFC types"
                        )
                    members[property_value.Name] = property_value
            measure_types = {
                property_name: property_value.NominalValue.is_a()
                for property_name, property_value in members.items()
            }
            measure_types.update(OPTIONAL_PROPERTY_TEMPLATE_FIELDS.get(name, {}))
            for property_name, primary_measure_type in sorted(measure_types.items()):
                add_prop_template(
                    model,
                    pset_template=template,
                    name=property_name,
                    description=f"OSR-defined {property_name} property.",
                    template_type="P_SINGLEVALUE",
                    primary_measure_type=primary_measure_type,
                )
                property_rows.append(
                    {
                        "name": property_name,
                        "template_type": "P_SINGLEVALUE",
                        "primary_measure_type": primary_measure_type,
                    }
                )
        supports_definition_relationship = definition_class in {
            "IfcPropertySet",
            "IfcElementQuantity",
        }
        if supports_definition_relationship:
            model.create_entity(
                "IfcRelDefinesByTemplate",
                GlobalId=stable_guid(f"property-template|{name}"),
                Name=f"Template assignment · {name}",
                RelatedPropertySets=definitions,
                RelatingTemplate=template,
            )
        rows.append(
            {
                "name": name,
                "ifc_class": "IfcPropertySetTemplate",
                "definition_class": definition_class,
                "template_type": template_type,
                "applicable_entities": applicable_entities,
                "property_count": len(property_rows),
                "matched_definition_count": len(definitions),
                "linked_definition_count": (
                    len(definitions) if supports_definition_relationship else 0
                ),
                "linkage": (
                    "IfcRelDefinesByTemplate"
                    if supports_definition_relationship
                    else "template-name-and-type; resource-property relationship unavailable"
                ),
                "properties": property_rows,
                "status": "osr-custom-template; not-buildingSMART-standard-pset",
            }
        )
    declaration = assign_declaration(
        model,
        definitions=templates,
        relating_context=project,
    )
    if declaration is None:
        raise ValueError("OSR property templates could not be declared in the IFC project")
    return rows


def add_document_register(
    model: ifcopenshell.file,
    *,
    project: Any,
    alignment: Any,
    cost_schedule: Any,
    products: dict[str, Any],
    type_products: dict[tuple[str, str, str], Any],
    index_rows: list[dict[str, Any]],
    type_rows: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Create hash-locked native IFC references to real repository sources."""

    assets_by_document: dict[str, list[str]] = {key: [] for key in DOCUMENT_SOURCES}
    types_by_document: dict[str, list[str]] = {key: [] for key in DOCUMENT_SOURCES}
    for row in index_rows:
        for document_id in row["document_ids"]:
            assets_by_document[document_id].append(row["asset_id"])
    for row in type_rows.values():
        for document_id in row["document_ids"]:
            types_by_document[document_id].append(row["type_id"])

    project_documents = {
        "OSR-DOC-ALIGNMENT-CONTRACT",
        "OSR-DOC-BIM-WORKFLOW",
        "OSR-DOC-CIVIL-COST-CONTRACT",
        "OSR-DOC-IFC-EXPORTER",
        "OSR-DOC-SOURCE-CIVIL-INTEGRATION",
    }
    alignment_documents = {"OSR-DOC-ALIGNMENT-CONTRACT"}
    cost_documents = {"OSR-DOC-CIVIL-COST-CONTRACT"}
    types_by_id = {item.Tag: item for item in type_products.values()}
    reference_entities: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    for document_id, declaration in sorted(DOCUMENT_SOURCES.items()):
        source_path = REPO_ROOT / declaration["path"]
        if not source_path.is_file():
            raise ValueError(f"IFC source document does not exist: {declaration['path']}")
        source_sha256 = sha256_bytes(source_path.read_bytes())
        information = add_information(model)
        edit_information(
            model,
            information=information,
            attributes={
                "Identification": document_id,
                "Name": declaration["name"],
                "Description": (
                    "Git-repository source locked by the complete SHA-256 revision. "
                    "Regenerate the IFC after any source change."
                ),
                "Location": declaration["path"],
                "Purpose": declaration["purpose"],
                "IntendedUse": declaration["intended_use"],
                "Scope": declaration["scope"],
                "Revision": f"sha256:{source_sha256}",
                "ElectronicFormat": declaration["media_type"],
                "Status": "REVISION",
            },
        )
        reference = add_reference(model, information=information)
        edit_reference(
            model,
            reference=reference,
            attributes={
                "Identification": document_id,
                "Location": declaration["path"],
            },
        )
        reference_entities[document_id] = reference
        asset_ids = sorted(set(assets_by_document[document_id]))
        type_ids = sorted(set(types_by_document[document_id]))
        targets: list[Any] = []
        if document_id in project_documents:
            targets.append(project)
        if document_id in alignment_documents:
            targets.append(alignment)
        if document_id in cost_documents:
            targets.append(cost_schedule)
        targets.extend(types_by_id[type_id] for type_id in type_ids)
        targets.extend(products[asset_id] for asset_id in asset_ids)
        if targets:
            assign_document(model, products=targets, document=reference)
        rows.append(
            {
                "document_id": document_id,
                "name": declaration["name"],
                "location": declaration["path"],
                "sha256": source_sha256,
                "revision": f"sha256:{source_sha256}",
                "purpose": declaration["purpose"],
                "intended_use": declaration["intended_use"],
                "scope": declaration["scope"],
                "media_type": declaration["media_type"],
                "status": "REVISION",
                "registered_with_project": True,
                "associated_project": document_id in project_documents,
                "associated_alignment": document_id in alignment_documents,
                "associated_cost_schedule": document_id in cost_documents,
                "associated_asset_ids": asset_ids,
                "associated_type_ids": type_ids,
                "associated_object_count": len(targets),
                "associated_constraint_ids": [],
                "associated_constraint_count": 0,
            }
        )

    set_properties(
        model,
        project,
        "OSR_DocumentRegister",
        {
            "RegisterStatus": "native-ifc-hash-locked-repository-sources",
            "DocumentCount": len(rows),
            "HashAlgorithm": "SHA-256",
            "LocationPolicy": "repository-relative URI",
            "AssociationPolicy": "project plus direct source-to-type-and-occurrence links",
        },
    )
    return reference_entities, rows


def deterministic_roots(model: ifcopenshell.file) -> None:
    counters: Counter[tuple[str, str]] = Counter()
    for root in model.by_type("IfcRoot"):
        key = (root.is_a(), getattr(root, "Name", None) or getattr(root, "Identification", None) or "")
        counters[key] += 1
        root.GlobalId = stable_guid(f"{key[0]}|{key[1]}|{counters[key]}")


def stabilize_unordered_collections(model: ifcopenshell.file) -> None:
    """Canonicalise IFC SET attributes whose Python order is hash-randomised."""

    attributes = {
        "IfcUnitAssignment": ("Units",),
        "IfcRelAggregates": ("RelatedObjects",),
        "IfcRelContainedInSpatialStructure": ("RelatedElements",),
        "IfcRelReferencedInSpatialStructure": ("RelatedElements",),
        "IfcRelAssignsToControl": ("RelatedObjects",),
        "IfcRelAssignsToGroup": ("RelatedObjects",),
        "IfcRelAssignsToProcess": ("RelatedObjects",),
        "IfcRelDefinesByProperties": ("RelatedObjects",),
        "IfcRelDefinesByTemplate": ("RelatedPropertySets",),
        "IfcRelDeclares": ("RelatedDefinitions",),
        "IfcRelDefinesByType": ("RelatedObjects",),
        "IfcRelAssociatesClassification": ("RelatedObjects",),
        "IfcRelAssociatesConstraint": ("RelatedObjects",),
        "IfcRelAssociatesDocument": ("RelatedObjects",),
        "IfcRelAssociatesMaterial": ("RelatedObjects",),
        "IfcExternalReferenceRelationship": ("RelatedResourceObjects",),
        "IfcPresentationLayerAssignment": ("AssignedItems",),
        "IfcElementQuantity": ("Quantities",),
        "IfcPropertySetTemplate": ("HasPropertyTemplates",),
        "IfcTypeObject": ("HasPropertySets",),
        "IfcMaterialProperties": ("Properties",),
        "IfcProfileProperties": ("Properties",),
    }
    for ifc_class, names in attributes.items():
        for entity in model.by_type(ifc_class):
            for name in names:
                values = getattr(entity, name, None)
                if values:
                    setattr(entity, name, tuple(sorted(values, key=lambda item: item.id())))


def build_model(
    *,
    alignment_input: dict[str, Any] | None,
    revision_id: str,
) -> tuple[ifcopenshell.file, dict[str, Any], dict[str, Any]]:
    assert_integration_checks()
    twin = digital_twin_manifest()
    cost_model_path = REPO_ROOT / "lib/templates/civil-cost-model.toml"
    cost_model = tomllib.loads(cost_model_path.read_text(encoding="utf-8"))
    cost_model_hash = sha256_bytes(cost_model_path.read_bytes())
    civil_quantities = structure_quantities_per_km()
    source_hash = sha256_bytes(canonical_json({"twin": twin, "alignment": alignment_input}))

    model = create_file("IFC4X3")
    model.header.file_name.name = "civil-coordination.ifc"
    model.header.file_name.time_stamp = FIXED_HEADER_TIMESTAMP
    model.header.file_name.author = ("OpenSourceRail",)
    model.header.file_name.organization = ("OpenSourceRail",)
    model.header.file_name.preprocessor_version = f"IfcOpenShell {version('ifcopenshell')}"
    model.header.file_name.originating_system = "OpenSourceRail deterministic Bonsai civil exporter"
    model.header.file_name.authorization = "design-reference / not for construction"

    project = create_entity(model, ifc_class="IfcProject", name="OpenSourceRail civil coordination")
    site = create_entity(model, ifc_class="IfcSite", name="OSR local engineering grid")
    railway = create_entity(model, ifc_class="IfcRailway", name="OpenSourceRail reference railway")
    assign_unit(model, length={"is_metric": True, "raw": "METERS"})
    monetary_unit = add_monetary_unit(
        model, currency=cost_model["schema"]["currency"]
    )
    assign_unit(model, units=[monetary_unit])
    length_unit = next(
        unit
        for unit in model.by_type("IfcSIUnit")
        if unit.UnitType == "LENGTHUNIT"
    )
    model_context = add_context(model, context_type="Model")
    body_context = add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model_context,
    )
    add_context(
        model,
        context_type="Model",
        context_identifier="Axis",
        target_view="GRAPH_VIEW",
        parent=model_context,
    )
    assign_object(model, products=[site], relating_object=project)
    assign_object(model, products=[railway], relating_object=site)
    edit_object_placement(model, product=site, matrix=np.eye(4), is_si=True)
    edit_object_placement(model, product=railway, matrix=np.eye(4), is_si=True)
    georeferencing = apply_georeferencing(model, project, alignment_input)

    set_properties(
        model,
        project,
        "OSR_Provenance",
        {
            "Schema": SCHEMA,
            "RevisionId": revision_id,
            "CanonicalSourceSha256": source_hash,
            "IfcOpenShellVersion": version("ifcopenshell"),
            "GeometryAuthority": "OpenSourceRail parametric civil and alignment models",
            "CoordinationEnvironment": "Bonsai 0.8.5 / IFC4.3",
            "ReleaseStatus": "design-reference; not for construction",
        },
    )
    set_properties(
        model,
        project,
        "OSR_CostModel",
        {
            "Maturity": cost_model["schema"]["maturity"],
            "CostModelSha256": cost_model_hash,
            "AtGradeUsdPerRouteKm": float(cost_model["civil_usd_per_km"]["at_grade"]),
            "ElevatedUsdPerRouteKm": float(cost_model["civil_usd_per_km"]["elevated"]),
            "BridgeUsdPerRouteKm": float(cost_model["civil_usd_per_km"]["bridge"]),
            "Regeneration": "python3 scripts/generate-civil-cost-model.py",
        },
    )

    spatial_parts: dict[str, Any] = {}
    for key, (name, predefined_type) in DISCIPLINES.items():
        part = create_entity(
            model,
            ifc_class="IfcRailwayPart",
            predefined_type=predefined_type,
            name=name,
        )
        # These four discipline containers are a vertical organisation of the
        # railway, as described by the IFC4.3 railway-domain guidance.
        part.UsageType = "VERTICAL"
        assign_object(model, products=[part], relating_object=railway)
        edit_object_placement(model, product=part, matrix=np.eye(4), is_si=True)
        spatial_parts[key] = part

    styles = {
        key: make_style(model, f"OSR {key}", colour, 0.72 if key == "lineside" else 0.0)
        for key, colour in COLOURS.items()
    }
    alignment, alignment_index = add_alignment(
        model,
        alignment_input,
        revision_id,
    )

    products: dict[str, Any] = {}
    product_classes: dict[str, str] = {}
    product_names: dict[str, str] = {}
    type_products: dict[tuple[str, str, str], Any] = {}
    type_rows: dict[str, dict[str, Any]] = {}
    materials: dict[str, Any] = {}
    material_rows: dict[str, dict[str, Any]] = {}
    profile_definitions: dict[str, Any] = {}
    profile_sets: dict[str, Any] = {}
    profile_rows: dict[str, dict[str, Any]] = {}
    index_rows: list[dict[str, Any]] = []
    for component in ifc_export_components():
        asset_id = component.asset_id
        asset_class = component.asset_class
        coordination_group_id = ZONE_ASSET_IDS[component.zone]
        discipline = component_discipline(asset_class)
        presentation_layer = PRESENTATION_LAYERS[discipline]
        ifc_class, predefined_type = ifc_type(asset_class)
        profile_id = profile_id_for_component(asset_class, component.source)
        document_ids = component_document_ids(component.source)
        type_class = ifc_type_class(ifc_class)
        type_product = None
        type_id = None
        if type_class is not None:
            type_key = (type_class, asset_class, component.source)
            type_product = type_products.get(type_key)
            if type_product is None:
                type_id, type_source_hash = component_type_identity(asset_class, component.source)
                type_predefined_type = predefined_type or "NOTDEFINED"
                type_product = create_entity(
                    model,
                    ifc_class=type_class,
                    predefined_type=type_predefined_type,
                    name=f"{asset_class} · {type_id}",
                )
                type_product.Tag = type_id
                if type_predefined_type == "USERDEFINED":
                    type_product.ElementType = asset_class
                set_properties(
                    model,
                    type_product,
                    "OSR_Type",
                    {
                        "TypeId": type_id,
                        "AssetClass": asset_class,
                        "SourceGeometry": component.source,
                        "SourceSha256": type_source_hash,
                        "RevisionId": revision_id,
                        "LifecycleState": "design-reference",
                        "GeometryRole": "shared recipe metadata; occurrence geometry remains authoritative",
                    },
                )
                type_products[type_key] = type_product
                material_id = material_family_id(asset_class, component.source)
                if material_id is not None:
                    material = materials.get(material_id)
                    if material is None:
                        declaration = MATERIAL_FAMILIES[material_id]
                        material = add_material(
                            model,
                            name=material_id,
                            category=declaration["category"],
                            description=declaration["description"],
                        )
                        set_properties(
                            model,
                            material,
                            "OSR_MaterialStatus",
                            {
                                "MaterialId": material_id,
                                "Label": declaration["label"],
                                "SpecificationStatus": "family-declared; grade-and-design-unresolved",
                                "GradeStatus": "unresolved",
                                "SourceAuthority": declaration["source_authority"],
                                "RevisionId": revision_id,
                                "ReleaseStatus": "design-reference; not for procurement or construction",
                            },
                        )
                        materials[material_id] = material
                        material_rows[material_id] = {
                            "material_id": material_id,
                            **declaration,
                            "specification_status": "family-declared; grade-and-design-unresolved",
                            "assigned_type_count": 0,
                            "inherited_occurrence_count": 0,
                        }
                    if profile_id is not None:
                        profile_definition = profile_definitions.get(profile_id)
                        if profile_definition is None:
                            points_m = rail_profile_points_m()
                            geometry = RAIL_GEOMETRY[RailProfile.UIC_60E1]
                            profile_definition = add_arbitrary_profile(
                                model,
                                profile=points_m,
                                name=profile_id,
                            )
                            set_properties(
                                model,
                                profile_definition,
                                "OSR_Profile",
                                {
                                    "ProfileId": profile_id,
                                    "StandardDesignation": "UIC 60E1",
                                    "GeometryStatus": "simplified-straight-line-review-polygon",
                                    "SourceAuthority": "mechanical-py/src/osr_mech/track/rail.py",
                                    "FullMillProfileStatus": "required for procurement and detailed rail design",
                                    "PublishedLinearMassKgPerM": geometry.linear_mass_kg_per_m,
                                    "RevisionId": revision_id,
                                },
                            )
                            profile_set = add_material_set(
                                model,
                                name=profile_id,
                                set_type="IfcMaterialProfileSet",
                            )
                            profile_set.Description = (
                                "UIC 60E1 straight-line review profile; full mill fillets and "
                                "supplier tolerances remain procurement inputs."
                            )
                            add_profile(
                                model,
                                profile_set=profile_set,
                                material=material,
                                profile=profile_definition,
                                name="Running rail section",
                            )
                            profile_definitions[profile_id] = profile_definition
                            profile_sets[profile_id] = profile_set
                            profile_rows[profile_id] = {
                                "profile_id": profile_id,
                                "ifc_class": profile_definition.is_a(),
                                "material_id": material_id,
                                "standard_designation": "UIC 60E1",
                                "geometry_status": "simplified-straight-line-review-polygon",
                                "source_authority": "mechanical-py/src/osr_mech/track/rail.py",
                                "width_m": geometry.foot_width_mm / 1_000.0,
                                "height_m": geometry.height_mm / 1_000.0,
                                "area_m2": round(polygon_area(points_m), 9),
                                "published_linear_mass_kg_per_m": geometry.linear_mass_kg_per_m,
                                "cardinal_point": 5,
                                "points_m": [
                                    [round(x, 6), round(y, 6)] for x, y in points_m
                                ],
                                "assigned_type_count": 0,
                                "usage_count": 0,
                            }
                        assign_material(
                            model,
                            products=[type_product],
                            type="IfcMaterialProfileSet",
                            material=profile_sets[profile_id],
                        )
                        set_properties(
                            model,
                            type_product,
                            "OSR_ProfileAssignment",
                            {
                                "ProfileId": profile_id,
                                "StandardDesignation": "UIC 60E1",
                                "GeometryStatus": "simplified-straight-line-review-polygon",
                                "OccurrenceUsage": "IfcMaterialProfileSetUsage; cardinal point 5",
                                "SourceAuthority": "mechanical-py/src/osr_mech/track/rail.py",
                            },
                        )
                        profile_rows[profile_id]["assigned_type_count"] += 1
                    else:
                        assign_material(model, products=[type_product], material=material)
                    material_rows[material_id]["assigned_type_count"] += 1
                type_rows[type_id] = {
                    "type_id": type_id,
                    "name": type_product.Name,
                    "asset_class": asset_class,
                    "ifc_class": type_class,
                    "ifc_predefined_type": type_predefined_type,
                    "source_geometry": component.source,
                    "source_sha256": type_source_hash,
                    "material_id": material_id,
                    "profile_id": profile_id,
                    "classification_code": asset_class,
                    "document_ids": list(document_ids),
                    "occurrence_count": 0,
                }
            else:
                type_id = type_product.Tag
        product = create_entity(
            model,
            ifc_class=ifc_class,
            predefined_type=predefined_type,
            name=component.label,
        )
        if predefined_type == "USERDEFINED":
            product.ObjectType = asset_class
        if type_product is not None:
            assign_type(
                model,
                related_objects=[product],
                relating_type=type_product,
                should_map_representations=False,
            )
            if getattr(type_product, "PredefinedType", None) != "NOTDEFINED":
                product.PredefinedType = "NOTDEFINED"
                product.ObjectType = None
            type_rows[type_id]["occurrence_count"] += 1
            if type_rows[type_id]["material_id"] is not None:
                material_rows[type_rows[type_id]["material_id"]][
                    "inherited_occurrence_count"
                ] += 1
            if type_rows[type_id]["profile_id"] is not None:
                assign_material(
                    model,
                    products=[product],
                    type="IfcMaterialProfileSetUsage",
                )
                usage = get_material(
                    product,
                    should_skip_usage=False,
                    should_inherit=False,
                )
                usage.CardinalPoint = 5
                profile_rows[type_rows[type_id]["profile_id"]]["usage_count"] += 1
        product.Tag = asset_id
        built = component.build()
        leaves = [leaf for leaf in flatten_parts(built) if leaf.bounding_box().volume > 0.0]
        detail_mode = "component-parts"
        if len(leaves) > MAX_DETAIL_PARTS:
            leaves = [built]
            detail_mode = "coordination-envelope"
        boxes = [bbox_tuple(leaf) for leaf in leaves]
        overall = bbox_union(boxes)
        length_m = (overall[3] - overall[0]) / 1000.0
        width_m = (overall[4] - overall[1]) / 1000.0
        height_m = (overall[5] - overall[2]) / 1000.0
        if profile_id is not None:
            origin = (
                overall[0] / 1000.0,
                (overall[1] + overall[4]) / 2000.0,
                (overall[2] + overall[5]) / 2000.0,
            )
            representation = add_profile_representation(
                model,
                context=body_context,
                profile=profile_definitions[profile_id],
                depth=length_m,
                cardinal_point=5,
                placement_zx_axes=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
            )
            detail_mode = "native-profile-extrusion"
        else:
            origin = (
                (overall[0] + overall[3]) / 2000.0,
                (overall[1] + overall[4]) / 2000.0,
                (overall[2] + overall[5]) / 2000.0,
            )
            vertices = [box_mesh(box, origin) for box in boxes]
            faces = [[face[:] for face in BOX_FACES] for _ in boxes]
            representation = add_mesh_representation(
                model,
                context=body_context,
                vertices=vertices,
                faces=faces,
                unit_scale=1.0,
            )
        assign_representation(model, product=product, representation=representation)
        matrix = np.eye(4)
        matrix[:3, 3] = origin
        edit_object_placement(model, product=product, matrix=matrix, is_si=True)
        assign_container(model, products=[product], relating_structure=spatial_parts[discipline])
        assign_representation_styles(model, shape_representation=representation, styles=[styles[discipline]])

        source_volume_m3 = built.volume / 1_000_000_000.0
        set_properties(
            model,
            product,
            "OSR_Asset",
            {
                "AssetId": asset_id,
                "AssetClass": asset_class,
                "CoordinationGroupId": coordination_group_id,
                "SourceComponentId": component.source_component_id,
                "SourcePartRole": component.source_part_role,
                "SourceGeometry": component.source,
                "SourceSha256": sha256_bytes(canonical_json({"asset_id": asset_id, "source": component.source})),
                "RevisionId": revision_id,
                "DetailMode": detail_mode,
                "LifecycleState": "design-reference",
            },
        )
        set_quantities(
            model,
            product,
            "OSR_CoordinationEnvelopeQuantities",
            {
                "OverallLength": round(length_m, 6),
                "OverallWidth": round(width_m, 6),
                "OverallHeight": round(height_m, 6),
                "SourceNetVolume": round(source_volume_m3, 6),
                "RepresentationParts": len(boxes),
            },
        )
        standard_quantity_sets: list[str] = []
        engineering_status: dict[str, Any] | None = None
        if asset_class == "civil.bearing":
            engineering_status = {
                "bearing_family": "elastomeric/PTFE",
                "supplier_selection_status": "unresolved",
                "load_schedule_status": "unresolved",
                "movement_schedule_status": "unresolved",
                "replacement_access": "separate jacking interfaces modelled",
                "release_status": "design-reference; supplier freeze required",
            }
            set_properties(
                model,
                product,
                "OSR_BearingStatus",
                {
                    "BearingFamily": "elastomeric/PTFE",
                    "NominalLength": round(length_m, 6),
                    "NominalWidth": round(width_m, 6),
                    "NominalHeight": round(height_m, 6),
                    "SupplierSelectionStatus": "unresolved",
                    "LoadScheduleStatus": "unresolved",
                    "MovementScheduleStatus": "unresolved",
                    "ReplacementAccess": "separate jacking interfaces modelled",
                    "ReleaseStatus": "design-reference; supplier freeze required",
                },
            )
        elif asset_class == "civil.foundation-interface":
            engineering_status = {
                "interface_type": "common pier-to-foundation interface",
                "actual_foundation_type": "unresolved",
                "actual_foundation_depth": "intentionally-not-modelled",
                "geotechnical_release_status": "required",
                "ifc_semantics": "virtual interface; not an IfcFooting or IfcDeepFoundation",
                "release_status": "design-reference; not for construction",
            }
            set_properties(
                model,
                product,
                "OSR_FoundationInterfaceStatus",
                {
                    "InterfaceType": "common pier-to-foundation interface",
                    "ModelledDepth": round(height_m, 6),
                    "ActualFoundationType": "unresolved",
                    "ActualFoundationDepth": "intentionally-not-modelled",
                    "GeotechnicalReleaseStatus": "required",
                    "IfcSemantics": "virtual interface; not an IfcFooting or IfcDeepFoundation",
                    "ReleaseStatus": "design-reference; not for construction",
                },
            )
        if asset_class == "rolling-stock.trainset":
            set_quantities(
                model,
                product,
                "Qto_VehicleBaseQuantities",
                {
                    "Length": round(length_m, 6),
                    "Width": round(width_m, 6),
                    "Height": round(height_m, 6),
                },
            )
            standard_quantity_sets.append("Qto_VehicleBaseQuantities")
        products[asset_id] = product
        product_classes[asset_id] = asset_class
        product_names[asset_id] = component.label
        index_rows.append(
            {
                "asset_id": asset_id,
                "name": component.label,
                "asset_class": asset_class,
                "ifc_class": product.is_a(),
                "ifc_predefined_type": predefined_type,
                "ifc_occurrence_predefined_type": getattr(product, "PredefinedType", None),
                "ifc_type_id": type_id,
                "ifc_type_class": type_product.is_a() if type_product is not None else None,
                "ifc_type_name": type_product.Name if type_product is not None else None,
                "ifc_type_predefined_type": (
                    getattr(type_product, "PredefinedType", None)
                    if type_product is not None
                    else None
                ),
                "material_id": (
                    type_rows[type_id]["material_id"] if type_id is not None else None
                ),
                "profile_id": (
                    type_rows[type_id]["profile_id"] if type_id is not None else None
                ),
                "classification_code": asset_class,
                "classification_assignment": (
                    "inherited-from-type" if type_id is not None else "direct-occurrence"
                ),
                "coordination_group_id": coordination_group_id,
                "coordination_group_name": component.zone,
                "presentation_layer_id": presentation_layer["layer_id"],
                "presentation_layer_name": presentation_layer["name"],
                "discipline": discipline,
                "source_geometry": component.source,
                "source_component_id": component.source_component_id,
                "source_part_role": component.source_part_role,
                "document_ids": list(document_ids),
                "detail_mode": detail_mode,
                "representation_parts": len(boxes),
                "bbox_m": [round(value / 1000.0, 6) for value in overall],
                "source_net_volume_m3": round(source_volume_m3, 6),
                "standard_quantity_sets": standard_quantity_sets,
                "engineering_status": engineering_status,
            }
        )

    bearing_connection_rows = add_bearing_connections(
        model,
        products=products,
        index_rows=index_rows,
    )
    layer_rows = add_presentation_layers(
        model,
        products=products,
        index_rows=index_rows,
    )
    group_entities, group_rows = add_coordination_groups(
        model,
        products=products,
        index_rows=index_rows,
        revision_id=revision_id,
    )
    system_entities, system_rows = add_functional_systems(
        model,
        products=products,
        index_rows=index_rows,
        spatial_parts=spatial_parts,
    )
    classification_index = add_asset_classification(
        model,
        project=project,
        products=products,
        type_products=type_products,
        index_rows=index_rows,
        type_rows=type_rows,
    )
    cost_schedule, cost_schedule_index = add_planning_rate_schedule(
        model,
        cost_model=cost_model,
        cost_model_hash=cost_model_hash,
        length_unit=length_unit,
    )
    document_references, document_rows = add_document_register(
        model,
        project=project,
        alignment=alignment,
        cost_schedule=cost_schedule,
        products=products,
        type_products=type_products,
        index_rows=index_rows,
        type_rows=type_rows,
    )
    constraint_rows = add_interface_constraints(
        model,
        project=project,
        checks=assert_integration_checks(),
        products=products,
        index_rows=index_rows,
        group_entities=group_entities,
        system_entities=system_entities,
        document_references=document_references,
    )
    constraint_resource_ids = sorted(
        [row["constraint_id"] for row in constraint_rows]
        + [row["metric"]["metric_id"] for row in constraint_rows if row["metric"]]
    )
    for document_row in document_rows:
        if document_row["document_id"] == "OSR-DOC-SOURCE-CIVIL-INTEGRATION":
            document_row["associated_constraint_ids"] = constraint_resource_ids
            document_row["associated_constraint_count"] = len(
                constraint_resource_ids
            )
    schedule_rows, assignments = add_schedule(model, products, product_classes, product_names)
    property_template_rows = add_property_templates(model, project=project)
    for work_schedule in model.by_type("IfcWorkSchedule"):
        work_schedule.CreationDate = DEFAULT_START.isoformat()
    deterministic_roots(model)
    stabilize_unordered_collections(model)
    for row in index_rows:
        row["ifc_guid"] = products[row["asset_id"]].GlobalId
        if row["ifc_type_id"] is not None:
            row["ifc_type_guid"] = next(
                item.GlobalId for item in type_products.values() if item.Tag == row["ifc_type_id"]
            )
        else:
            row["ifc_type_guid"] = None
    for type_id, row in type_rows.items():
        row["ifc_guid"] = next(item.GlobalId for item in type_products.values() if item.Tag == type_id)
    for row in group_rows:
        row["ifc_guid"] = group_entities[row["group_id"]].GlobalId
    for row in system_rows:
        row["ifc_guid"] = system_entities[row["system_id"]].GlobalId
    index_rows.sort(key=lambda row: row["asset_id"])
    sorted_type_rows = sorted(type_rows.values(), key=lambda row: row["type_id"])
    sorted_material_rows = sorted(
        material_rows.values(), key=lambda row: row["material_id"]
    )
    sorted_profile_rows = sorted(profile_rows.values(), key=lambda row: row["profile_id"])
    external_decision_rows = [
        {**decision, "status": "external-evidence-required"}
        for decision in EXTERNAL_ENGINEERING_DECISIONS
    ]
    index = {
        "schema": SCHEMA,
        "revision_id": revision_id,
        "canonical_source_sha256": source_hash,
        "ifc_schema": "IFC4X3",
        "ifcopenshell_version": version("ifcopenshell"),
        "authority_boundary": {
            "authoritative": ["OSR alignment rules", "OSR parametric civil geometry", "OSR validation gates"],
            "bonsai_ifc": ["federation", "civil detail review", "quantities", "drawings", "4D construction sequence"],
        },
        "capability_closure": {
            "status": "source-supported-ifc-work-complete",
            "implementable_open_task_count": 0,
            "external_decision_count": len(external_decision_rows),
            "boundary": (
                "Further promotion requires named external engineering, client, "
                "supplier, commercial, survey or information-management evidence."
            ),
        },
        "cost_model": {
            "path": "lib/templates/civil-cost-model.toml",
            "sha256": cost_model_hash,
            "maturity": cost_model["schema"]["maturity"],
            "civil_usd_per_km": cost_model["civil_usd_per_km"],
            "quantities_per_route_km": civil_quantities,
        },
        "cost_schedule": cost_schedule_index,
        "georeferencing": georeferencing,
        "alignment": alignment_index,
        "classification": classification_index,
        "summary": {
            "assets": len(index_rows),
            "types": len(sorted_type_rows),
            "typed_assets": sum(row["ifc_type_id"] is not None for row in index_rows),
            "native_rolling_stock_vehicles": sum(
                row["ifc_class"] == "IfcVehicle" for row in index_rows
            ),
            "vehicle_base_quantity_sets": sum(
                "Qto_VehicleBaseQuantities" in row["standard_quantity_sets"]
                for row in index_rows
            ),
            "native_bearings": sum(
                row["ifc_class"] == "IfcBearing" for row in index_rows
            ),
            "bearing_connection_relationships": len(bearing_connection_rows),
            "bearing_connection_realizations": sum(
                row["realizing_bearing_count"] for row in bearing_connection_rows
            ),
            "connected_bearings": sum(
                bool(row.get("bearing_connection_ids"))
                for row in index_rows
                if row["asset_class"] == "civil.bearing"
            ),
            "connected_pier_caps": sum(
                bool(row.get("bearing_connection_ids"))
                for row in index_rows
                if row["asset_class"] == "civil.pier-cap"
            ),
            "connected_superstructure_assets": sum(
                bool(row.get("bearing_connection_ids"))
                for row in index_rows
                if row["asset_class"]
                in {"civil.decked-pi-beam", "civil.station-deck-interface"}
            ),
            "foundation_interfaces": sum(
                row["asset_class"] == "civil.foundation-interface"
                for row in index_rows
            ),
            "jacking_interfaces": sum(
                row["asset_class"] == "civil.jacking-interface"
                for row in index_rows
            ),
            "pier_caps": sum(
                row["asset_class"] == "civil.pier-cap" for row in index_rows
            ),
            "pier_columns": sum(
                row["asset_class"] == "civil.pier-column" for row in index_rows
            ),
            "materials": len(sorted_material_rows),
            "material_associated_assets": sum(
                row["material_id"] is not None for row in index_rows
            ),
            "profiles": len(sorted_profile_rows),
            "profiled_assets": sum(row["profile_id"] is not None for row in index_rows),
            "documents": len(document_rows),
            "document_associated_assets": sum(
                bool(row["document_ids"]) for row in index_rows
            ),
            "classifications": 1,
            "classification_references": len(classification_index["references"]),
            "classified_assets": sum(
                bool(row["classification_code"]) for row in index_rows
            ),
            "coordination_groups": len(group_rows),
            "grouped_assets": sum(
                bool(row["coordination_group_id"]) for row in index_rows
            ),
            "functional_systems": len(system_rows),
            "built_systems": sum(
                row["ifc_class"] == "IfcBuiltSystem" for row in system_rows
            ),
            "system_associated_assets": sum(
                bool(row["functional_system_id"]) for row in index_rows
            ),
            "system_spatial_part_references": sum(
                len(row["spatial_disciplines"]) for row in system_rows
            ),
            "presentation_layers": len(layer_rows),
            "layer_associated_assets": sum(
                bool(row["presentation_layer_id"]) for row in index_rows
            ),
            "ifc_classes": dict(sorted(Counter(row["ifc_class"] for row in index_rows).items())),
            "disciplines": dict(sorted(Counter(row["discipline"] for row in index_rows).items())),
            "interface_checks": len(assert_integration_checks()),
            "interface_constraints": len(constraint_rows),
            "interface_metrics": sum(
                row["metric"] is not None for row in constraint_rows
            ),
            "qualitative_only_interface_constraints": sum(
                row["metric"] is None for row in constraint_rows
            ),
            "interface_constraint_related_objects": sum(
                row["related_object_count"] for row in constraint_rows
            ),
            "interface_constraint_asset_links": sum(
                len(row["related_asset_ids"]) for row in constraint_rows
            ),
            "interface_constraint_group_links": sum(
                len(row["related_group_ids"]) for row in constraint_rows
            ),
            "interface_constraint_system_links": sum(
                len(row["related_system_ids"]) for row in constraint_rows
            ),
            "constraint_source_document_relationships": len(
                model.by_type("IfcExternalReferenceRelationship")
            ),
            "source_linked_constraint_resources": sum(
                (1 + (row["metric"] is not None))
                * bool(row["external_source_document_ids"])
                for row in constraint_rows
            ),
            "external_engineering_decisions": len(external_decision_rows),
            "horizontal_alignment_segments": alignment_index[
                "horizontal_segment_count"
            ],
            "vertical_alignment_segments": alignment_index[
                "vertical_segment_count"
            ],
            "alignment_stationing_referents": alignment_index[
                "stationing_referent_count"
            ],
            "planning_rate_schedules": 1,
            "planning_rate_items": cost_schedule_index["item_count"],
            "property_set_templates": len(property_template_rows),
            "property_templates": sum(
                row["property_count"] for row in property_template_rows
            ),
            "template_linked_definitions": sum(
                row["linked_definition_count"] for row in property_template_rows
            ),
            "template_matched_definitions": sum(
                row["matched_definition_count"] for row in property_template_rows
            ),
            "construction_tasks": len(schedule_rows),
            "construction_output_tasks": len(assignments),
            "scheduled_physical_assets": sum(len(values) for values in assignments.values()),
            "virtual_review_gate_assets": sum(
                len(row["review_gate_asset_ids"]) for row in schedule_rows
            ),
        },
        "materials": sorted_material_rows,
        "profiles": sorted_profile_rows,
        "bearing_connections": bearing_connection_rows,
        "documents": document_rows,
        "groups": group_rows,
        "systems": system_rows,
        "layers": layer_rows,
        "constraints": constraint_rows,
        "external_engineering_decisions": external_decision_rows,
        "property_set_templates": property_template_rows,
        "types": sorted_type_rows,
        "objects": index_rows,
        "validation": [asdict(check) for check in assert_integration_checks()],
        "limitations": twin["limitations"] + [
            "IFC geometry is deterministic review/detail geometry, not engineer-released analysis geometry.",
            "Bonsai is not used to calculate alignment radii, transitions, cant, sight distance, earthworks, or structural capacity.",
        ],
    }
    sequence = {
        "schema": "org.opensourcerail.bonsai-construction-sequence.v1",
        "revision_id": revision_id,
        "schedule_name": "OSR civil fabrication and construction sequence",
        "start": DEFAULT_START.isoformat(),
        "tasks": schedule_rows,
        "product_assignments": assignments,
        "review_gate_assignments": {
            row["id"]: row["review_gate_asset_ids"]
            for row in schedule_rows
            if row["review_gate_asset_ids"]
        },
        "animation": {
            "fps": 24,
            "duration_seconds": 48,
            "frame_start": 1,
            "frame_end": 1152,
            "semantics": "normalized review animation; IFC task dates retain planning durations",
        },
    }
    return model, index, sequence


def build_civil_ids(index: dict[str, Any]) -> ids_module.Ids:
    """Build the information requirements for the generated IFC exchange."""

    document = ids_module.Ids(
        title="OSR IFC4.3 civil information requirements",
        version="1.0",
        description=(
            "Machine-checkable requirements for the OpenSourceRail design-reference "
            "civil coordination exchange. Passing does not constitute construction release."
        ),
        author="OpenSourceRail",
        date="2026-01-01",
        purpose="Civil BIM federation, coordination, and review",
        milestone="Design reference",
    )
    concrete_elements = sorted({row["ifc_class"].upper() for row in index["objects"]})
    asset_specification = ids_module.Specification(
        name="Civil elements carry stable OSR identity and coordination quantities",
        description="Every exported physical or virtual asset remains traceable to its deterministic source.",
        instructions="Do not accept untagged or revision-ambiguous objects into the civil federation.",
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-CIV-001",
    )
    asset_specification.applicability.append(
        ids_module.Entity(name=ids_module.Restriction({"enumeration": concrete_elements}))
    )
    asset_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Attribute(name="Tag"),
            ids_module.Property(propertySet="OSR_Asset", baseName="AssetId"),
            ids_module.Property(propertySet="OSR_Asset", baseName="AssetClass"),
            ids_module.Property(
                propertySet="OSR_Asset", baseName="CoordinationGroupId"
            ),
            ids_module.Property(propertySet="OSR_Asset", baseName="SourceSha256"),
            ids_module.Property(propertySet="OSR_Asset", baseName="RevisionId"),
            ids_module.Property(propertySet="OSR_Asset", baseName="LifecycleState"),
            ids_module.Property(
                propertySet="OSR_CoordinationEnvelopeQuantities", baseName="OverallLength"
            ),
            ids_module.Property(
                propertySet="OSR_CoordinationEnvelopeQuantities", baseName="OverallWidth"
            ),
            ids_module.Property(
                propertySet="OSR_CoordinationEnvelopeQuantities", baseName="OverallHeight"
            ),
        ]
    )
    document.specifications.append(asset_specification)

    vehicle_specification = ids_module.Specification(
        name="Rolling-stock references use native vehicle geometry quantities",
        description=(
            "Each generated trainset is an IfcVehicle with the standard measured "
            "length, width, and height quantities derived from OSR geometry."
        ),
        instructions=(
            "Treat these as design-reference geometry dimensions only; capacity, "
            "mass, availability, serial identity, and operational release remain upstream."
        ),
        minOccurs=2,
        maxOccurs=2,
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-VEHICLE-001",
    )
    vehicle_specification.applicability.append(ids_module.Entity(name="IFCVEHICLE"))
    vehicle_specification.requirements.extend(
        [
            ids_module.Property(
                propertySet="Qto_VehicleBaseQuantities", baseName="Length"
            ),
            ids_module.Property(
                propertySet="Qto_VehicleBaseQuantities", baseName="Width"
            ),
            ids_module.Property(
                propertySet="Qto_VehicleBaseQuantities", baseName="Height"
            ),
        ]
    )
    document.specifications.append(vehicle_specification)

    bearing_specification = ids_module.Specification(
        name="Native bearings preserve source dimensions and unresolved release gates",
        description=(
            "Each source bearing leaf is a native IfcBearing with deterministic "
            "dimensions and explicit supplier, loading, and movement boundaries."
        ),
        instructions=(
            "Do not treat the elastomeric/PTFE family label as a selected supplier "
            "product or an accepted bearing and movement schedule."
        ),
        minOccurs=36,
        maxOccurs=36,
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-BEARING-001",
    )
    bearing_specification.applicability.append(ids_module.Entity(name="IFCBEARING"))
    bearing_specification.requirements.extend(
        [
            ids_module.Property(propertySet="OSR_BearingStatus", baseName="BearingFamily"),
            ids_module.Property(propertySet="OSR_BearingStatus", baseName="NominalLength"),
            ids_module.Property(propertySet="OSR_BearingStatus", baseName="NominalWidth"),
            ids_module.Property(propertySet="OSR_BearingStatus", baseName="NominalHeight"),
            ids_module.Property(
                propertySet="OSR_BearingStatus", baseName="SupplierSelectionStatus"
            ),
            ids_module.Property(
                propertySet="OSR_BearingStatus", baseName="LoadScheduleStatus"
            ),
            ids_module.Property(
                propertySet="OSR_BearingStatus", baseName="MovementScheduleStatus"
            ),
            ids_module.Property(propertySet="OSR_BearingStatus", baseName="ReleaseStatus"),
            ids_module.Property(
                propertySet="OSR_BearingConnectivity", baseName="RealizedConnectionCount"
            ),
            ids_module.Property(
                propertySet="OSR_BearingConnectivity", baseName="ConnectedCapAssetId"
            ),
            ids_module.Property(
                propertySet="OSR_BearingConnectivity",
                baseName="ConnectedSuperstructureAssetIds",
            ),
            ids_module.Property(
                propertySet="OSR_BearingConnectivity", baseName="ConnectivityDerivation"
            ),
        ]
    )
    document.specifications.append(bearing_specification)

    foundation_interface_rows = [
        row for row in index["objects"] if row["asset_class"] == "civil.foundation-interface"
    ]
    foundation_specification = ids_module.Specification(
        name="Foundation envelopes remain explicit virtual geotechnical interfaces",
        description=(
            "The source foundation envelope is exported for coordination without "
            "misrepresenting it as a released shallow or deep foundation."
        ),
        instructions=(
            "Select and design the actual foundation from project geotechnical evidence "
            "before replacing this virtual interface."
        ),
        minOccurs=9,
        maxOccurs=9,
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-FOUNDATION-INTERFACE-001",
    )
    foundation_specification.applicability.extend(
        [
            ids_module.Entity(name="IFCVIRTUALELEMENT"),
            ids_module.Attribute(
                name="Tag",
                value=ids_module.Restriction(
                    {"enumeration": sorted(row["asset_id"] for row in foundation_interface_rows)}
                ),
            ),
        ]
    )
    foundation_specification.requirements.extend(
        [
            ids_module.Property(
                propertySet="OSR_FoundationInterfaceStatus", baseName="InterfaceType"
            ),
            ids_module.Property(
                propertySet="OSR_FoundationInterfaceStatus", baseName="ModelledDepth"
            ),
            ids_module.Property(
                propertySet="OSR_FoundationInterfaceStatus", baseName="ActualFoundationType"
            ),
            ids_module.Property(
                propertySet="OSR_FoundationInterfaceStatus", baseName="ActualFoundationDepth"
            ),
            ids_module.Property(
                propertySet="OSR_FoundationInterfaceStatus",
                baseName="GeotechnicalReleaseStatus",
            ),
            ids_module.Property(
                propertySet="OSR_FoundationInterfaceStatus", baseName="IfcSemantics"
            ),
            ids_module.Property(
                propertySet="OSR_FoundationInterfaceStatus", baseName="ReleaseStatus"
            ),
        ]
    )
    document.specifications.append(foundation_specification)

    reusable_type_classes = sorted({row["ifc_class"].upper() for row in index["types"]})
    type_specification = ids_module.Specification(
        name="Reusable component types carry deterministic OSR recipe identity",
        description=(
            "Each safely typable component family exposes a reusable IFC type while "
            "occurrences retain their own geometry and placement."
        ),
        instructions=(
            "Use the exact source-recipe type for schedules and coordination; do not "
            "infer materials, profiles, or construction specifications from it."
        ),
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-TYPE-001",
    )
    type_specification.applicability.append(
        ids_module.Entity(name=ids_module.Restriction({"enumeration": reusable_type_classes}))
    )
    type_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Attribute(name="Tag"),
            ids_module.Property(propertySet="OSR_Type", baseName="TypeId"),
            ids_module.Property(propertySet="OSR_Type", baseName="AssetClass"),
            ids_module.Property(propertySet="OSR_Type", baseName="SourceGeometry"),
            ids_module.Property(propertySet="OSR_Type", baseName="SourceSha256"),
            ids_module.Property(propertySet="OSR_Type", baseName="RevisionId"),
            ids_module.Property(propertySet="OSR_Type", baseName="LifecycleState"),
            ids_module.Property(propertySet="OSR_Type", baseName="GeometryRole"),
        ]
    )
    document.specifications.append(type_specification)

    materialized_types = [row for row in index["types"] if row["material_id"]]
    material_specification = ids_module.Specification(
        name="Declared material families remain explicit and procurement-unresolved",
        description=(
            "Only source-supported single-material families receive native IFC material "
            "associations; the family record explicitly withholds grade and design release."
        ),
        instructions=(
            "Do not substitute this family declaration for a project material grade, "
            "supplier certificate, structural design, or procurement release."
        ),
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-MAT-001",
    )
    material_specification.applicability.extend(
        [
            ids_module.Entity(
                name=ids_module.Restriction(
                    {"enumeration": sorted({row["ifc_class"].upper() for row in materialized_types})}
                )
            ),
            ids_module.Attribute(
                name="Tag",
                value=ids_module.Restriction(
                    {"enumeration": sorted(row["type_id"] for row in materialized_types)}
                ),
            ),
        ]
    )
    material_specification.requirements.append(
        ids_module.Material(
            value=ids_module.Restriction(
                {"enumeration": sorted(row["material_id"] for row in materialized_types)}
            )
        )
    )
    document.specifications.append(material_specification)

    profiled_types = [row for row in index["types"] if row["profile_id"]]
    profile_specification = ids_module.Specification(
        name="Profiled rail types declare their native review section and usage",
        description=(
            "Each straight UIC 60E1 rail type identifies the native material profile "
            "used by its occurrence extrusion."
        ),
        instructions=(
            "The straight-line polygon is coordination geometry only; use the full mill "
            "profile, tolerances, and released grade for procurement and detailed design."
        ),
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-PROFILE-001",
    )
    profile_specification.applicability.extend(
        [
            ids_module.Entity(
                name=ids_module.Restriction(
                    {"enumeration": sorted({row["ifc_class"].upper() for row in profiled_types})}
                )
            ),
            ids_module.Attribute(
                name="Tag",
                value=ids_module.Restriction(
                    {"enumeration": sorted(row["type_id"] for row in profiled_types)}
                ),
            ),
        ]
    )
    profile_specification.requirements.extend(
        [
            ids_module.Property(
                propertySet="OSR_ProfileAssignment", baseName="ProfileId"
            ),
            ids_module.Property(
                propertySet="OSR_ProfileAssignment", baseName="GeometryStatus"
            ),
            ids_module.Property(
                propertySet="OSR_ProfileAssignment", baseName="OccurrenceUsage"
            ),
        ]
    )
    document.specifications.append(profile_specification)

    document_register_specification = ids_module.Specification(
        name="Project declares a native hash-locked source-document register",
        description=(
            "The IFC carries repository-relative source locations, complete SHA-256 "
            "revisions, and direct document associations without implying a CDE issue."
        ),
        instructions=(
            "Resolve each native document reference against the accompanying Git "
            "revision before relying on the model for coordination."
        ),
        minOccurs=1,
        maxOccurs=1,
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-DOC-001",
    )
    document_register_specification.applicability.append(
        ids_module.Entity(name="IFCPROJECT")
    )
    document_register_specification.requirements.extend(
        [
            ids_module.Property(
                propertySet="OSR_DocumentRegister", baseName="RegisterStatus"
            ),
            ids_module.Property(
                propertySet="OSR_DocumentRegister", baseName="DocumentCount"
            ),
            ids_module.Property(
                propertySet="OSR_DocumentRegister", baseName="HashAlgorithm"
            ),
            ids_module.Property(
                propertySet="OSR_DocumentRegister", baseName="AssociationPolicy"
            ),
        ]
    )
    document.specifications.append(document_register_specification)

    classification_specification = ids_module.Specification(
        name="Every civil asset carries its native OSR automation class",
        description=(
            "OSR asset codes are represented as lightweight IFC classification "
            "references and inherited from reusable types where possible."
        ),
        instructions=(
            "Treat this as an internal automation classification. Do not claim a "
            "national or client mapping without an approved deployment crosswalk."
        ),
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-CLASS-001",
    )
    classification_specification.applicability.append(
        ids_module.Entity(name=ids_module.Restriction({"enumeration": concrete_elements}))
    )
    classification_specification.requirements.append(
        ids_module.Classification(
            value=ids_module.Restriction(
                {
                    "enumeration": sorted(
                        reference["code"]
                        for reference in index["classification"]["references"]
                    )
                }
            ),
            system=ASSET_CLASSIFICATION["name"],
        )
    )
    document.specifications.append(classification_specification)

    group_specification = ids_module.Specification(
        name="Source review zones remain explicit non-spatial coordination groups",
        description=(
            "Each source layout zone is represented by an IfcGroup with an explicit "
            "semantic boundary and deterministic membership."
        ),
        instructions=(
            "Use these groups for review filtering only; do not treat them as surveyed "
            "spatial zones or functional engineering systems."
        ),
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-GROUP-001",
    )
    group_specification.applicability.extend(
        [
            ids_module.Entity(name="IFCGROUP"),
            ids_module.Attribute(
                name="ObjectType", value="OSR coordination review group"
            ),
        ]
    )
    group_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Property(
                propertySet="OSR_CoordinationGroup", baseName="GroupId"
            ),
            ids_module.Property(
                propertySet="OSR_CoordinationGroup", baseName="SourceZone"
            ),
            ids_module.Property(
                propertySet="OSR_CoordinationGroup", baseName="GroupRole"
            ),
            ids_module.Property(
                propertySet="OSR_CoordinationGroup", baseName="SpatialMeaning"
            ),
            ids_module.Property(
                propertySet="OSR_CoordinationGroup", baseName="SystemMeaning"
            ),
        ]
    )
    document.specifications.append(group_specification)

    system_specification = ids_module.Specification(
        name="Civil assets form explicit native functional engineering systems",
        description=(
            "Each authoritative OSR asset class maps to one functional IfcSystem, "
            "with complete and non-overlapping occurrence membership."
        ),
        instructions=(
            "Use these systems for functional design-reference filtering only; do "
            "not infer a surveyed spatial zone, commissioned system, or safety release."
        ),
        minOccurs=5,
        maxOccurs=5,
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-SYSTEM-001",
    )
    system_specification.applicability.append(
        ids_module.Entity(
            name=ids_module.Restriction(
                {"enumeration": ["IFCBUILTSYSTEM", "IFCSYSTEM"]}
            )
        )
    )
    system_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Attribute(name="Description"),
            ids_module.Attribute(name="ObjectType"),
        ]
    )
    document.specifications.append(system_specification)

    layer_specification = ids_module.Specification(
        name="Civil geometry exposes native presentation layers",
        description=(
            "Each discipline layer has a stable identifier and human-readable name "
            "for simple geometry visibility control in CAD/BIM tools."
        ),
        instructions=(
            "Treat layers as presentation filters only; asset meaning remains in IFC "
            "objects, types, classification, and coordination groups."
        ),
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-LAYER-001",
    )
    layer_specification.applicability.append(
        ids_module.Entity(name="IFCPRESENTATIONLAYERASSIGNMENT")
    )
    layer_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Attribute(name="Identifier"),
        ]
    )
    document.specifications.append(layer_specification)

    constraint_specification = ids_module.Specification(
        name="Civil interface requirements are native objectives",
        description=(
            "Each deterministic civil integration check is exposed as an IfcObjective "
            "with project governance and related asset evidence. Source-supported "
            "numeric checks carry nested IfcMetric benchmarks."
        ),
        instructions=(
            "Read the current evaluation from the accompanying index and validation "
            "report; the IFC objective records requirement intent and revision evidence."
        ),
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-CONSTRAINT-001",
    )
    constraint_specification.applicability.append(
        ids_module.Entity(name="IFCOBJECTIVE")
    )
    constraint_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Attribute(name="Description"),
            ids_module.Attribute(name="ConstraintGrade"),
            ids_module.Attribute(name="ConstraintSource"),
            ids_module.Attribute(name="CreationTime"),
            ids_module.Attribute(name="ObjectiveQualifier"),
        ]
    )
    document.specifications.append(constraint_specification)

    metric_specification = ids_module.Specification(
        name="Numeric civil interface checks use native IFC metrics",
        description=(
            "Every source-supported numeric interface target is a nested IfcMetric "
            "using SI length values; multi-object derived checks do not claim a false "
            "single-attribute reference path."
        ),
        instructions=(
            "Compare DataValue with the structured observed value in the civil index "
            "and retain the source-document relationship during review."
        ),
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-METRIC-001",
    )
    metric_specification.applicability.append(ids_module.Entity(name="IFCMETRIC"))
    metric_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Attribute(name="Description"),
            ids_module.Attribute(name="ConstraintGrade"),
            ids_module.Attribute(name="ConstraintSource"),
            ids_module.Attribute(name="CreationTime"),
            ids_module.Attribute(name="Benchmark"),
            ids_module.Attribute(name="ValueSource"),
            ids_module.Attribute(name="DataValue"),
        ]
    )
    document.specifications.append(metric_specification)

    pset_template_specification = ids_module.Specification(
        name="OSR property dictionaries are native IFC templates",
        description=(
            "Every custom OSR property or quantity set has a named native template "
            "with explicit applicability and template type."
        ),
        instructions=(
            "Treat OSR_ names as project-defined dictionaries, not buildingSMART "
            "standard Pset_ definitions."
        ),
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-PSET-TEMPLATE-001",
    )
    pset_template_specification.applicability.append(
        ids_module.Entity(name="IFCPROPERTYSETTEMPLATE")
    )
    pset_template_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Attribute(name="TemplateType"),
            ids_module.Attribute(name="ApplicableEntity"),
        ]
    )
    document.specifications.append(pset_template_specification)

    property_template_specification = ids_module.Specification(
        name="OSR template fields declare native property or quantity types",
        description=(
            "Each field in the embedded OSR dictionaries has a stable name and "
            "IfcSimplePropertyTemplate type."
        ),
        instructions=(
            "Use the declared single-value measure or quantity template type when "
            "editing the associated property and quantity sets."
        ),
        minOccurs=1,
        maxOccurs="unbounded",
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-PROP-TEMPLATE-001",
    )
    property_template_specification.applicability.append(
        ids_module.Entity(name="IFCSIMPLEPROPERTYTEMPLATE")
    )
    property_template_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Attribute(name="TemplateType"),
        ]
    )
    document.specifications.append(property_template_specification)

    cost_schedule_specification = ids_module.Specification(
        name="Civil planning rates use a native IFC schedule of rates",
        description=(
            "The generated cost contract is exposed as a schedule of unit rates, "
            "not a bill, tender, quotation, or project estimate."
        ),
        minOccurs=1,
        maxOccurs=1,
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-COST-SCHEDULE-001",
    )
    cost_schedule_specification.applicability.append(
        ids_module.Entity(name="IFCCOSTSCHEDULE")
    )
    cost_schedule_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Attribute(name="Identification"),
            ids_module.Attribute(name="PredefinedType"),
            ids_module.Attribute(name="Status"),
            ids_module.Attribute(name="UpdateDate"),
        ]
    )
    document.specifications.append(cost_schedule_specification)

    cost_item_specification = ids_module.Specification(
        name="Civil planning alternatives carry explicit native unit rates",
        description=(
            "Each at-grade, elevated, or bridge alternative is a named cost item "
            "with one generated cost value and no implied selected scope."
        ),
        minOccurs=3,
        maxOccurs=3,
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-COST-ITEM-001",
    )
    cost_item_specification.applicability.append(
        ids_module.Entity(name="IFCCOSTITEM")
    )
    cost_item_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Attribute(name="Identification"),
            ids_module.Attribute(name="PredefinedType"),
            ids_module.Attribute(name="ObjectType"),
            ids_module.Attribute(name="CostValues"),
        ]
    )
    document.specifications.append(cost_item_specification)

    alignment_specification = ids_module.Specification(
        name="Alignment exposes authority and revision",
        description="The IFC axis declares that detailed alignment engineering remains upstream in OSR.",
        minOccurs=1,
        maxOccurs=1,
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-ALN-001",
    )
    alignment_specification.applicability.append(ids_module.Entity(name="IFCALIGNMENT"))
    alignment_specification.requirements.extend(
        [
            ids_module.Attribute(name="Name"),
            ids_module.Property(propertySet="OSR_AlignmentAuthority", baseName="Authority"),
            ids_module.Property(propertySet="OSR_AlignmentAuthority", baseName="RevisionId"),
            ids_module.Property(propertySet="OSR_AlignmentAuthority", baseName="GeometryRole"),
        ]
    )
    document.specifications.append(alignment_specification)

    provenance_specification = ids_module.Specification(
        name="Project declares deterministic provenance and release status",
        description="The exchange identifies its source revision, canonical content hash, and maturity boundary.",
        minOccurs=1,
        maxOccurs=1,
        ifcVersion=["IFC4X3_ADD2"],
        identifier="OSR-IDS-PROV-001",
    )
    provenance_specification.applicability.append(ids_module.Entity(name="IFCPROJECT"))
    provenance_specification.requirements.extend(
        [
            ids_module.Property(propertySet="OSR_Provenance", baseName="CanonicalSourceSha256"),
            ids_module.Property(propertySet="OSR_Provenance", baseName="RevisionId"),
            ids_module.Property(propertySet="OSR_Provenance", baseName="GeometryAuthority"),
            ids_module.Property(propertySet="OSR_Provenance", baseName="ReleaseStatus"),
            ids_module.Property(
                propertySet="OSR_Georeferencing",
                baseName="CoordinateReferenceStatus",
            ),
        ]
    )
    document.specifications.append(provenance_specification)
    return document


def write_and_validate_ids(
    ifc_path: Path,
    ids_path: Path,
    report_path: Path,
    index: dict[str, Any],
) -> dict[str, Any]:
    requirements = build_civil_ids(index)
    requirements.to_xml(ids_path)
    reopened_requirements = open_ids(ids_path)
    if reopened_requirements is None:
        raise ValueError("written civil IDS could not be reopened")
    reopened_requirements.validate(
        ifcopenshell.open(str(ifc_path)),
        should_filter_version=True,
        filepath=ifc_path.name,
    )
    report = ids_reporter.Json(reopened_requirements)
    report.report()
    result = json.loads(report.to_string())
    result.update(
        {
            "schema": "org.opensourcerail.bonsai-civil-ids-report.v1",
            "date": FIXED_REVIEW_TIMESTAMP,
            "filepath": ifc_path.name,
            "filename": ifc_path.name,
            "ids_filename": ids_path.name,
        }
    )
    # IfcTester records passing entities in sets. Preserve its full evidence but
    # canonicalise those arrays before hashing or presenting the report.
    for specification in result["specifications"]:
        specification["applicable_entities"].sort(
            key=lambda item: (item.get("global_id") or "", item.get("id") or 0)
        )
        for requirement in specification["requirements"]:
            for key in ("passed_entities", "failed_entities"):
                requirement[key].sort(
                    key=lambda item: (item.get("global_id") or "", item.get("id") or 0)
                )
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not result["status"]:
        raise ValueError("written civil IFC failed its IDS information requirements")
    return result


def canonicalize_zip(source: Path, destination: Path) -> None:
    """Rewrite a ZIP with stable ordering and metadata for byte reproducibility."""

    with zipfile.ZipFile(source, "r") as incoming, zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as outgoing:
        for name in sorted(incoming.namelist()):
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0
            info.external_attr = 0
            outgoing.writestr(info, incoming.read(name), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def _bbox_target(rows: list[dict[str, Any]]) -> np.ndarray:
    if not rows:
        return np.array([160.0, 0.0, 0.0], dtype=np.float64)
    union = bbox_union(tuple(row["bbox_m"]) for row in rows)
    return np.array(
        [(union[0] + union[3]) / 2.0, (union[1] + union[4]) / 2.0, (union[2] + union[5]) / 2.0],
        dtype=np.float64,
    )


def write_coordination_bcf(
    ifc_path: Path,
    bcf_path: Path,
    bcf_index_path: Path,
    index: dict[str, Any],
    alignment_input: dict[str, Any] | None,
) -> dict[str, Any]:
    """Write deterministic BCF 3.0 release issues linked to IFC GUIDs."""

    model = ifcopenshell.open(str(ifc_path))
    alignment = model.by_type("IfcAlignment")[0]
    decisions = {
        issue["id"]: issue
        for issue in (alignment_input or {}).get("coordination_issues", [])
        if isinstance(issue, dict) and isinstance(issue.get("id"), str)
    }
    bcf_statuses = {
        "open": "Open",
        "in-progress": "In Progress",
        "resolved": "Resolved",
        "closed": "Closed",
    }
    topic_definitions = [
        {
            "key": "alignment-survey-authority",
            "title": "Replace planning alignment with accepted survey geometry",
            "description": (
                "The current IfcAlignment is a deterministic coordination axis. Before design release, "
                "accept the project CRS, surveyed control, horizontal and vertical geometry, transitions, "
                "cant, tolerances, and design-speed checks in the authoritative OSR alignment model."
            ),
            "rows": [],
            "ifc_guids": [alignment.GlobalId],
            "target": np.array([160.0, 0.0, 0.0], dtype=np.float64),
        },
        {
            "key": "station-deck-release",
            "title": "Release elevated station deck structural design",
            "description": (
                "The elevated station deck is a coordination interface only. Resolve governing loads, "
                "member and reinforcement design, bearings, movements, drainage, seismic detailing, "
                "constructability, and engineer acceptance before construction use."
            ),
            "rows": [row for row in index["objects"] if row["asset_class"] == "civil.station-deck-interface"],
        },
        {
            "key": "viaduct-design-release",
            "title": "Complete viaduct span, bearing, pier, and foundation schedule",
            "description": (
                "Decked Pi-beams, walkway cassettes and piers currently define deterministic coordination envelopes. Confirm span "
                "arrangement, bearing schedule, ground model, foundation selection, load combinations, "
                "dynamic response, durability, drainage, and engineer-released reinforcement details."
            ),
            "rows": [
                row
                for row in index["objects"]
                if row["asset_class"]
                in {"civil.decked-pi-beam", "civil.walkway-cassette", "civil.u-girder", "civil.pier"}
            ],
        },
    ]
    built_in_keys = {definition["key"] for definition in topic_definitions}
    rows_by_asset_id = {row["asset_id"]: row for row in index["objects"]}
    for issue_id in sorted(set(decisions) - built_in_keys):
        decision = decisions[issue_id]
        asset_ids = decision.get("asset_ids", [])
        if not issue_id.startswith("custom-") or not isinstance(asset_ids, list) or not asset_ids:
            raise ValueError(f"invalid custom coordination issue {issue_id!r}")
        title = str(decision.get("title", "")).strip()
        description = str(decision.get("description", "")).strip()
        if not (4 <= len(title) <= 160) or not (12 <= len(description) <= 2_000):
            raise ValueError(f"custom coordination issue {issue_id!r} has invalid title or description")
        missing_asset_ids = sorted(set(asset_ids) - set(rows_by_asset_id))
        if missing_asset_ids:
            raise ValueError(
                f"custom coordination issue {issue_id!r} selects unknown assets {missing_asset_ids!r}"
            )
        topic_definitions.append(
            {
                "key": issue_id,
                "title": title,
                "description": description,
                "rows": [rows_by_asset_id[asset_id] for asset_id in sorted(set(asset_ids))],
            }
        )

    bcf = BcfXml.create_new(project_name="OpenSourceRail civil coordination")
    if bcf.project is None:
        raise ValueError("BCF project metadata was not created")
    bcf.project.project_id = stable_uuid("bcf-project|civil-coordination")
    topic_rows = []
    for definition in topic_definitions:
        rows = definition["rows"]
        decision = decisions.get(definition["key"], {})
        intent_status = decision.get("status", "open")
        if intent_status not in bcf_statuses:
            raise ValueError(f"unsupported coordination status {intent_status!r}")
        bcf_status = bcf_statuses[intent_status]
        resolution = str(decision.get("resolution", "")).strip()
        reviewed_by = str(decision.get("reviewed_by", "")).strip()
        assignee = str(decision.get("assignee", "")).strip()
        description = definition["description"]
        if resolution:
            description += f"\n\nRecorded resolution: {resolution}"
        if reviewed_by:
            description += f"\nReviewed by: {reviewed_by}"
        selected_guids = definition.get("ifc_guids") or [row["ifc_guid"] for row in rows]
        target = definition.get("target") if "target" in definition else _bbox_target(rows)
        handler = bcf.add_topic(
            definition["title"],
            description,
            "engineering@opensourcerail.org",
            topic_type="Engineering",
            topic_status=bcf_status,
        )
        generated_topic_guid = handler.guid
        topic_guid = stable_uuid(f"bcf-topic|{definition['key']}")
        bcf.topics.pop(generated_topic_guid)
        handler.topic.guid = topic_guid
        handler.topic.creation_date = XmlDateTime.from_string(FIXED_REVIEW_TIMESTAMP)
        if assignee:
            handler.topic.assigned_to = assignee
        handler._topic_dir = Path(topic_guid)
        bcf.topics[topic_guid] = handler

        viewpoint = handler.add_viewpoint_from_point_and_guids(target, *selected_guids)
        generated_viewpoint_name = viewpoint.guid + ".bcfv"
        viewpoint_guid = stable_uuid(f"bcf-viewpoint|{definition['key']}")
        viewpoint.visualization_info.guid = viewpoint_guid
        handler.viewpoints.pop(generated_viewpoint_name)
        handler.viewpoints[viewpoint_guid + ".bcfv"] = viewpoint
        markup_viewpoint = handler.topic.viewpoints.view_point[-1]
        markup_viewpoint.guid = viewpoint_guid
        markup_viewpoint.viewpoint = viewpoint_guid + ".bcfv"
        topic_rows.append(
            {
                "topic_guid": topic_guid,
                "viewpoint_guid": viewpoint_guid,
                "title": definition["title"],
                "description": description,
                "type": "Engineering",
                "status": bcf_status,
                "intent_status": intent_status,
                "issue_id": definition["key"],
                "assignee": assignee,
                "resolution": resolution,
                "reviewed_by": reviewed_by,
                "asset_ids": [row["asset_id"] for row in rows],
                "ifc_guids": selected_guids,
            }
        )

    with TemporaryDirectory(prefix="osr-bcf-") as temporary:
        generated = Path(temporary) / "generated.bcf"
        bcf.save(generated)
        canonicalize_zip(generated, bcf_path)
    result = {
        "schema": "org.opensourcerail.bonsai-civil-bcf-index.v1",
        "bcf_version": "3.0",
        "project_id": bcf.project.project_id,
        "ifc_filename": ifc_path.name,
        "topic_count": len(topic_rows),
        "open_topic_count": sum(
            row["intent_status"] in {"open", "in-progress"} for row in topic_rows
        ),
        "topics": topic_rows,
    }
    bcf_index_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def validate_coordination_bcf(bcf_path: Path, ifc_path: Path) -> dict[str, Any]:
    coordination = BcfXml.load(bcf_path)
    if coordination is None:
        raise ValueError("written civil BCF could not be reopened")
    model = ifcopenshell.open(str(ifc_path))
    model_guids = {root.GlobalId for root in model.by_type("IfcRoot")}
    selected_guids: list[str] = []
    for topic in coordination.topics.values():
        for viewpoint in topic.viewpoints.values():
            selected_guids.extend(viewpoint.get_selected_guids() or [])
    return {
        "version": coordination.version.version_id,
        "topic_count": len(coordination.topics),
        "selected_ifc_guids": len(selected_guids),
        "all_selected_guids_resolve": bool(selected_guids) and set(selected_guids).issubset(model_guids),
    }


def validate_written(
    paths: dict[str, Path],
    index: dict[str, Any],
    sequence: dict[str, Any],
    ids_report: dict[str, Any],
    bcf_index: dict[str, Any],
) -> dict[str, Any]:
    ifc_path = paths["ifc"]
    reopened = ifcopenshell.open(str(ifc_path))
    schema_logger = ifc_validate.json_logger()
    ifc_validate.validate(str(ifc_path), schema_logger, express_rules=True)
    schema_issues = []
    for issue in schema_logger.statements:
        instance = issue.get("instance")
        schema_issues.append(
            {
                "level": issue.get("level"),
                "type": issue.get("type"),
                "message": (issue.get("message") or "").splitlines()[0],
                "attribute": issue.get("attribute"),
                "instance_id": instance.id() if instance is not None else None,
                "instance_type": instance.is_a() if instance is not None else None,
            }
        )
    schema_issues.sort(
        key=lambda issue: (
            issue["instance_id"] or 0,
            issue["attribute"] or "",
            issue["message"] or "",
        )
    )
    bcf_validation = validate_coordination_bcf(paths["bcf"], ifc_path)
    tagged = {product.Tag for product in reopened.by_type("IfcProduct") if getattr(product, "Tag", None)}
    expected = {row["asset_id"] for row in index["objects"]}
    expected_types = {row["type_id"] for row in index["types"]}
    exported_types = {
        product.Tag
        for product in reopened.by_type("IfcTypeProduct")
        if getattr(product, "Tag", None)
    }
    type_assignments_match = True
    native_vehicle_semantics_match = True
    material_assignments_match = True
    profile_geometry_usage_matches = True
    profiles_by_id = {row["profile_id"]: row for row in index["profiles"]}
    for row in index["objects"]:
        product = reopened.by_guid(row["ifc_guid"])
        relationships = getattr(product, "IsTypedBy", ()) or ()
        observed_type_ids = [relationship.RelatingType.Tag for relationship in relationships]
        expected_type_ids = [row["ifc_type_id"]] if row["ifc_type_id"] is not None else []
        if observed_type_ids != expected_type_ids:
            type_assignments_match = False
        if row["asset_class"] == "rolling-stock.trainset":
            vehicle_quantities = get_psets(product).get(
                "Qto_VehicleBaseQuantities", {}
            )
            native_vehicle_semantics_match &= (
                product.is_a() == "IfcVehicle"
                and len(relationships) == 1
                and relationships[0].RelatingType.is_a() == "IfcVehicleType"
                and relationships[0].RelatingType.PredefinedType == "ROLLINGSTOCK"
                and math.isclose(
                    vehicle_quantities.get("Length", -1.0),
                    row["bbox_m"][3] - row["bbox_m"][0],
                    abs_tol=1e-9,
                )
                and math.isclose(
                    vehicle_quantities.get("Width", -1.0),
                    row["bbox_m"][4] - row["bbox_m"][1],
                    abs_tol=1e-9,
                )
                and math.isclose(
                    vehicle_quantities.get("Height", -1.0),
                    row["bbox_m"][5] - row["bbox_m"][2],
                    abs_tol=1e-9,
                )
                and row["standard_quantity_sets"]
                == ["Qto_VehicleBaseQuantities"]
            )
        material = get_material(product, should_inherit=True)
        observed_material_ids = material_ids_from_assignment(material)
        observed_material_id = (
            observed_material_ids[0] if len(observed_material_ids) == 1 else None
        )
        if observed_material_id != row["material_id"]:
            material_assignments_match = False
        if row["profile_id"] is not None:
            usage = get_material(
                product,
                should_skip_usage=False,
                should_inherit=False,
            )
            solids = [
                item
                for representation in product.Representation.Representations
                for item in representation.Items
                if item.is_a("IfcExtrudedAreaSolid")
            ]
            profile_row = profiles_by_id[row["profile_id"]]
            length_m = row["bbox_m"][3] - row["bbox_m"][0]
            expected_volume_m3 = profile_row["area_m2"] * length_m
            profile_geometry_usage_matches &= (
                usage is not None
                and usage.is_a("IfcMaterialProfileSetUsage")
                and usage.CardinalPoint == 5
                and usage.ForProfileSet.Name == row["profile_id"]
                and len(solids) == 1
                and solids[0].SweptArea.ProfileName == row["profile_id"]
                and math.isclose(solids[0].Depth, length_m, abs_tol=1e-9)
                and math.isclose(
                    row["source_net_volume_m3"],
                    expected_volume_m3,
                    abs_tol=2e-6,
                )
            )
    expected_materials = {row["material_id"] for row in index["materials"]}
    native_vehicle_semantics_match &= (
        len(reopened.by_type("IfcVehicle")) == 2
        and len(reopened.by_type("IfcVehicleType")) == 1
        and not reopened.by_type("IfcBuildingElementProxy")
        and not reopened.by_type("IfcBuildingElementProxyType")
    )
    exported_materials = {material.Name for material in reopened.by_type("IfcMaterial")}
    material_catalog_matches = all(
        get_psets(material).get("OSR_MaterialStatus", {}).get("MaterialId")
        == material.Name
        and get_psets(material)
        .get("OSR_MaterialStatus", {})
        .get("SpecificationStatus")
        == "family-declared; grade-and-design-unresolved"
        for material in reopened.by_type("IfcMaterial")
    )
    expected_profiles = {row["profile_id"] for row in index["profiles"]}
    exported_profile_definitions = {
        profile.ProfileName: profile
        for profile in reopened.by_type("IfcArbitraryClosedProfileDef")
        if profile.ProfileName in expected_profiles
    }
    profile_catalog_matches = set(exported_profile_definitions) == expected_profiles and all(
        get_psets(profile).get("OSR_Profile", {}).get("ProfileId")
        == profile.ProfileName
        for profile in exported_profile_definitions.values()
    )
    document_information = {
        item.Identification: item for item in reopened.by_type("IfcDocumentInformation")
    }
    document_references = {
        item.Identification: item for item in reopened.by_type("IfcDocumentReference")
    }
    expected_document_ids = {row["document_id"] for row in index["documents"]}
    document_catalog_matches = (
        set(document_information) == expected_document_ids
        and set(document_references) == expected_document_ids
    )
    document_associations_match = True
    for row in index["documents"]:
        information = document_information.get(row["document_id"])
        reference = document_references.get(row["document_id"])
        source_path = REPO_ROOT / row["location"]
        document_catalog_matches &= (
            information is not None
            and reference is not None
            and reference.ReferencedDocument == information
            and information.Location == row["location"]
            and information.Revision == row["revision"]
            and information.ElectronicFormat == row["media_type"]
            and source_path.is_file()
            and sha256_bytes(source_path.read_bytes()) == row["sha256"]
        )
        relationships = [
            relationship
            for relationship in reopened.by_type("IfcRelAssociatesDocument")
            if relationship.RelatingDocument == reference
        ]
        registration_relationships = [
            relationship
            for relationship in reopened.by_type("IfcRelAssociatesDocument")
            if relationship.RelatingDocument == information
        ]
        document_catalog_matches &= (
            row["registered_with_project"]
            and len(registration_relationships) == 1
            and len(registration_relationships[0].RelatedObjects) == 1
            and registration_relationships[0].RelatedObjects[0].is_a("IfcProject")
        )
        observed_targets: set[str] = set()
        for relationship in relationships:
            for target in relationship.RelatedObjects:
                if target.is_a("IfcProject"):
                    observed_targets.add("project")
                elif target.is_a("IfcAlignment"):
                    observed_targets.add("alignment")
                elif target.is_a("IfcCostSchedule"):
                    observed_targets.add("cost-schedule")
                elif getattr(target, "Tag", None):
                    observed_targets.add(target.Tag)
        expected_targets = set(row["associated_asset_ids"]) | set(
            row["associated_type_ids"]
        )
        if row["associated_project"]:
            expected_targets.add("project")
        if row["associated_alignment"]:
            expected_targets.add("alignment")
        if row["associated_cost_schedule"]:
            expected_targets.add("cost-schedule")
        document_associations_match &= (
            len(relationships) == 1
            and observed_targets == expected_targets
            and row["associated_object_count"] == len(expected_targets)
        )
    document_register_pset = get_psets(reopened.by_type("IfcProject")[0]).get(
        "OSR_DocumentRegister", {}
    )
    document_catalog_matches &= (
        document_register_pset.get("RegisterStatus")
        == "native-ifc-hash-locked-repository-sources"
        and document_register_pset.get("DocumentCount") == len(index["documents"])
        and document_register_pset.get("HashAlgorithm") == "SHA-256"
    )
    classifications = reopened.by_type("IfcClassification")
    classification_catalog_matches = len(classifications) == 1
    classification_assignments_match = True
    if classifications:
        classification = classifications[0]
        classification_catalog_matches &= (
            classification.Name == index["classification"]["name"]
            and classification.Edition == index["classification"]["edition"]
            and classification.Description == index["classification"]["description"]
            and classification.Specification == index["classification"]["specification"]
            and classification.ReferenceTokens == (".",)
        )
        classification_references = {
            reference.Identification: reference
            for reference in reopened.by_type("IfcClassificationReference")
            if reference.ReferencedSource == classification
        }
        expected_codes = {
            reference["code"] for reference in index["classification"]["references"]
        }
        classification_catalog_matches &= set(classification_references) == expected_codes
        project_relationships = [
            relationship
            for relationship in reopened.by_type("IfcRelAssociatesClassification")
            if relationship.RelatingClassification == classification
        ]
        classification_catalog_matches &= (
            len(project_relationships) == 1
            and len(project_relationships[0].RelatedObjects) == 1
            and project_relationships[0].RelatedObjects[0].is_a("IfcProject")
        )
        for reference_row in index["classification"]["references"]:
            reference = classification_references.get(reference_row["code"])
            relationships = [
                relationship
                for relationship in reopened.by_type("IfcRelAssociatesClassification")
                if relationship.RelatingClassification == reference
            ]
            observed_targets = {
                target.Tag
                for relationship in relationships
                for target in relationship.RelatedObjects
                if getattr(target, "Tag", None)
            }
            expected_targets = set(reference_row["assigned_type_ids"]) | set(
                reference_row["direct_asset_ids"]
            )
            classification_assignments_match &= (
                reference is not None
                and reference.Name == reference_row["name"]
                and len(relationships) == 1
                and observed_targets == expected_targets
            )
        for row in index["objects"]:
            product = reopened.by_guid(row["ifc_guid"])
            observed_codes = {
                reference.Identification
                for reference in get_references(product, should_inherit=True)
                if reference.is_a("IfcClassificationReference")
                and reference.ReferencedSource == classification
            }
            classification_assignments_match &= observed_codes == {
                row["classification_code"]
            }
    else:
        classification_assignments_match = False
    classification_pset = get_psets(reopened.by_type("IfcProject")[0]).get(
        "OSR_Classification", {}
    )
    classification_catalog_matches &= (
        classification_pset.get("System") == ASSET_CLASSIFICATION["name"]
        and classification_pset.get("Edition") == ASSET_CLASSIFICATION["edition"]
        and classification_pset.get("ReferenceCount")
        == len(index["classification"]["references"])
        and classification_pset.get("ExternalMappingStatus")
        == "country-and-client-mapping-not-nominated"
    )
    exported_groups = {
        get_psets(group).get("OSR_CoordinationGroup", {}).get("GroupId"): group
        for group in reopened.by_type("IfcGroup")
        if group.is_a() == "IfcGroup"
    }
    expected_group_ids = {row["group_id"] for row in index["groups"]}
    group_catalog_matches = set(exported_groups) == expected_group_ids
    group_memberships_match = True
    observed_asset_memberships: Counter[str] = Counter()
    for group_row in index["groups"]:
        group = exported_groups.get(group_row["group_id"])
        if group is None:
            group_catalog_matches = False
            group_memberships_match = False
            continue
        properties = get_psets(group).get("OSR_CoordinationGroup", {})
        group_catalog_matches &= (
            group.GlobalId == group_row["ifc_guid"]
            and group.Name == group_row["name"]
            and group.ObjectType == "OSR coordination review group"
            and properties.get("GroupId") == group_row["group_id"]
            and properties.get("SourceZone") == group_row["name"]
            and properties.get("GroupRole") == group_row["role"]
            and properties.get("SpatialMeaning") == group_row["spatial_meaning"]
            and properties.get("SystemMeaning") == group_row["system_meaning"]
        )
        relationships = [
            relationship
            for relationship in reopened.by_type("IfcRelAssignsToGroup")
            if relationship.RelatingGroup == group
        ]
        observed_asset_ids = {
            product.Tag
            for relationship in relationships
            for product in relationship.RelatedObjects
            if getattr(product, "Tag", None)
        }
        observed_asset_memberships.update(observed_asset_ids)
        group_memberships_match &= (
            len(relationships) == 1
            and observed_asset_ids == set(group_row["asset_ids"])
            and group_row["asset_count"] == len(observed_asset_ids)
        )
    for row in index["objects"]:
        product = reopened.by_guid(row["ifc_guid"])
        observed_group_ids = {
            get_psets(relationship.RelatingGroup)
            .get("OSR_CoordinationGroup", {})
            .get("GroupId")
            for relationship in (getattr(product, "HasAssignments", ()) or ())
            if relationship.is_a("IfcRelAssignsToGroup")
            and relationship.RelatingGroup.is_a() == "IfcGroup"
        }
        group_memberships_match &= observed_group_ids == {
            row["coordination_group_id"]
        }
    group_memberships_match &= (
        set(observed_asset_memberships) == expected
        and all(count == 1 for count in observed_asset_memberships.values())
    )
    exported_systems = {
        system.ObjectType: system
        for system in reopened.by_type("IfcSystem")
    }
    expected_system_ids = {row["system_id"] for row in index["systems"]}
    system_catalog_matches = set(exported_systems) == expected_system_ids
    specialized_systems_match = True
    system_memberships_match = True
    system_spatial_references_match = True
    observed_system_memberships: Counter[str] = Counter()
    observed_system_spatial_references = 0
    for system_row in index["systems"]:
        system = exported_systems.get(system_row["system_id"])
        if system is None:
            system_catalog_matches = False
            system_memberships_match = False
            continue
        system_catalog_matches &= (
            system.GlobalId == system_row["ifc_guid"]
            and system.Name == system_row["name"]
            and system.Description == system_row["description"]
            and system.ObjectType == system_row["system_id"]
            and system_row["ifc_class"] == system.is_a()
            and getattr(system, "PredefinedType", None)
            == system_row["ifc_predefined_type"]
            and getattr(system, "LongName", None) == system_row["long_name"]
            and system_row["semantics"] == "functional-engineering-system"
            and system_row["spatial_meaning"] == "none; not an IfcSpatialZone"
            and system_row["operational_status"]
            == "design-reference; not commissioned or operational"
        )
        specialized_systems_match &= (
            system.is_a() == system_row["ifc_class"]
            and getattr(system, "PredefinedType", None)
            == system_row["ifc_predefined_type"]
        )
        relationships = [
            relationship
            for relationship in reopened.by_type("IfcRelAssignsToGroup")
            if relationship.RelatingGroup == system
        ]
        observed_asset_ids = {
            product.Tag
            for relationship in relationships
            for product in relationship.RelatedObjects
            if getattr(product, "Tag", None)
        }
        observed_system_memberships.update(observed_asset_ids)
        system_memberships_match &= (
            len(relationships) == 1
            and observed_asset_ids == set(system_row["asset_ids"])
            and system_row["asset_count"] == len(observed_asset_ids)
        )
        observed_spatial_part_names = {
            relationship.RelatingStructure.Name
            for relationship in (getattr(system, "ReferencedInStructures", ()) or ())
            if relationship.is_a("IfcRelReferencedInSpatialStructure")
        }
        observed_system_spatial_references += len(observed_spatial_part_names)
        system_spatial_references_match &= observed_spatial_part_names == set(
            system_row["spatial_part_names"]
        )
    for row in index["objects"]:
        product = reopened.by_guid(row["ifc_guid"])
        observed_system_ids = {
            relationship.RelatingGroup.ObjectType
            for relationship in (getattr(product, "HasAssignments", ()) or ())
            if relationship.is_a("IfcRelAssignsToGroup")
            and relationship.RelatingGroup.is_a("IfcSystem")
        }
        system_memberships_match &= observed_system_ids == {
            row["functional_system_id"]
        }
    system_memberships_match &= (
        set(observed_system_memberships) == expected
        and all(count == 1 for count in observed_system_memberships.values())
    )
    system_spatial_references_match &= observed_system_spatial_references == sum(
        len(row["spatial_part_names"]) for row in index["systems"]
    )
    exported_layers = {
        layer.Identifier: layer
        for layer in reopened.by_type("IfcPresentationLayerAssignment")
    }
    expected_layer_ids = {row["layer_id"] for row in index["layers"]}
    layer_catalog_matches = set(exported_layers) == expected_layer_ids
    layer_assignments_match = True
    representation_layer_ids: dict[int, list[str]] = {}
    for layer_row in index["layers"]:
        layer = exported_layers.get(layer_row["layer_id"])
        if layer is None:
            layer_catalog_matches = False
            layer_assignments_match = False
            continue
        observed_representation_ids = {item.id() for item in layer.AssignedItems}
        expected_representations = [
            representation
            for asset_id in layer_row["asset_ids"]
            for representation in reopened.by_guid(
                next(row["ifc_guid"] for row in index["objects"] if row["asset_id"] == asset_id)
            ).Representation.Representations
        ]
        expected_representation_ids = {
            representation.id() for representation in expected_representations
        }
        layer_catalog_matches &= (
            layer.Name == layer_row["name"]
            and layer.Description == layer_row["description"]
            and layer_row["ifc_class"] == layer.is_a()
        )
        layer_assignments_match &= (
            observed_representation_ids == expected_representation_ids
            and layer_row["asset_count"] == len(layer_row["asset_ids"])
            and layer_row["representation_count"] == len(observed_representation_ids)
        )
        for representation_id in observed_representation_ids:
            representation_layer_ids.setdefault(representation_id, []).append(
                layer_row["layer_id"]
            )
    for row in index["objects"]:
        product = reopened.by_guid(row["ifc_guid"])
        observed_layer_ids = {
            layer_id
            for representation in product.Representation.Representations
            for layer_id in representation_layer_ids.get(representation.id(), [])
        }
        layer_assignments_match &= observed_layer_ids == {
            row["presentation_layer_id"]
        }
    layer_assignments_match &= (
        len(representation_layer_ids) == len(index["objects"])
        and all(len(layer_ids) == 1 for layer_ids in representation_layer_ids.values())
    )
    exported_constraints = {
        objective.Name: objective for objective in reopened.by_type("IfcObjective")
    }
    expected_constraint_ids = {
        row["constraint_id"] for row in index["constraints"]
    }
    exported_metrics = {
        metric.Name: metric for metric in reopened.by_type("IfcMetric")
    }
    expected_metric_ids = {
        row["metric"]["metric_id"]
        for row in index["constraints"]
        if row["metric"] is not None
    }
    constraint_catalog_matches = set(exported_constraints) == expected_constraint_ids
    metric_catalog_matches = set(exported_metrics) == expected_metric_ids
    constraint_associations_match = True
    for constraint_row in index["constraints"]:
        objective = exported_constraints.get(constraint_row["constraint_id"])
        if objective is None:
            constraint_catalog_matches = False
            constraint_associations_match = False
            continue
        metric_row = constraint_row["metric"]
        benchmark_values = list(objective.BenchmarkValues or [])
        constraint_catalog_matches &= (
            objective.Description
            == (
                f"Current deterministic observation: {constraint_row['observation']}. "
                f"Evaluation status: {constraint_row['evaluation_status']}."
            )
            and objective.ConstraintGrade == constraint_row["constraint_grade"]
            and objective.ConstraintSource == constraint_row["constraint_source"]
            and objective.CreationTime == FIXED_REVIEW_TIMESTAMP
            and objective.ObjectiveQualifier
            == constraint_row["objective_qualifier"]
            and len(benchmark_values) == (1 if metric_row is not None else 0)
        )
        if metric_row is None:
            metric_catalog_matches &= constraint_row["metric_status"] == (
                "qualitative-objective; no fabricated numeric benchmark"
            )
        else:
            metric = exported_metrics.get(metric_row["metric_id"])
            metric_catalog_matches &= (
                metric is not None
                and benchmark_values == [metric]
                and metric.Description
                == (
                    f"{metric_row['name']}: observed "
                    f"{metric_row['observed_value']:.6f} {metric_row['unit']}; "
                    f"target {metric_row['target_value']:.6f} {metric_row['unit']}. "
                    f"{metric_row['reference_path_status']}."
                )
                and metric.ConstraintGrade == "HARD"
                and metric.ConstraintSource == constraint_row["constraint_source"]
                and metric.CreationTime == FIXED_REVIEW_TIMESTAMP
                and metric.Benchmark == metric_row["benchmark"]
                and metric.DataValue.is_a() == metric_row["measure_type"]
                and abs(
                    metric.DataValue.wrappedValue - metric_row["target_value"]
                )
                <= 1e-12
                and metric.ReferencePath is None
                and constraint_row["metric_status"]
                == "structured-native-ifc-metric"
            )
        relationships = [
            relationship
            for relationship in reopened.by_type("IfcRelAssociatesConstraint")
            if relationship.RelatingConstraint == objective
        ]
        observed_scope_ids: set[str] = set()
        if len(relationships) == 1:
            for related in relationships[0].RelatedObjects:
                if related.is_a("IfcProject"):
                    observed_scope_ids.add("IfcProject")
                elif related.is_a() == "IfcGroup":
                    observed_scope_ids.add(
                        get_psets(related)["OSR_CoordinationGroup"]["GroupId"]
                    )
                elif related.is_a("IfcSystem"):
                    observed_scope_ids.add(related.ObjectType)
                elif getattr(related, "Tag", None):
                    observed_scope_ids.add(related.Tag)
        expected_scope_ids = {
            "IfcProject",
            *constraint_row["related_asset_ids"],
            *constraint_row["related_group_ids"],
            *constraint_row["related_system_ids"],
        }
        constraint_associations_match &= (
            len(relationships) == 1
            and relationships[0].Intent == constraint_row["association_intent"]
            and len(relationships[0].RelatedObjects)
            == constraint_row["related_object_count"]
            and observed_scope_ids == expected_scope_ids
            and constraint_row["scope"]
            == "IfcProject governance plus deterministic related evidence"
        )
    constraint_source_relationships = [
        relationship
        for relationship in reopened.by_type("IfcExternalReferenceRelationship")
        if relationship.Name == "OSR constraint source-document linkage"
    ]
    expected_source_document_id = "OSR-DOC-SOURCE-CIVIL-INTEGRATION"
    expected_constraint_resource_ids = expected_constraint_ids | expected_metric_ids
    constraint_source_documents_match = (
        len(constraint_source_relationships) == 1
        and constraint_source_relationships[0].Name
        == "OSR constraint source-document linkage"
        and constraint_source_relationships[0].RelatingReference.is_a(
            "IfcDocumentReference"
        )
        and constraint_source_relationships[0].RelatingReference.Identification
        == expected_source_document_id
        and {
            constraint.Name
            for constraint in constraint_source_relationships[0].RelatedResourceObjects
        }
        == expected_constraint_resource_ids
        and all(
            len(constraint.HasExternalReferences) == 1
            for constraint in [*exported_constraints.values(), *exported_metrics.values()]
        )
        and all(
            row["external_source_document_ids"] == [expected_source_document_id]
            and row["external_reference_relationship"]
            == "IfcExternalReferenceRelationship"
            for row in index["constraints"]
        )
        and next(
            row
            for row in index["documents"]
            if row["document_id"] == expected_source_document_id
        )["associated_constraint_ids"]
        == sorted(expected_constraint_resource_ids)
    )
    external_decisions = index.get("external_engineering_decisions", [])
    external_decision_ids = [row.get("decision_id") for row in external_decisions]
    external_decision_register_valid = (
        len(external_decisions) == len(EXTERNAL_ENGINEERING_DECISIONS)
        and len(external_decision_ids) == len(set(external_decision_ids))
        and all(
            row.get("status") == "external-evidence-required"
            and row.get("authority_required")
            and row.get("evidence_required")
            and row.get("blocked_capabilities")
            and row.get("safe_current_state")
            for row in external_decisions
        )
        and index.get("capability_closure", {}).get("status")
        == "source-supported-ifc-work-complete"
        and index.get("capability_closure", {}).get("implementable_open_task_count")
        == 0
        and index.get("capability_closure", {}).get("external_decision_count")
        == len(external_decisions)
    )
    custom_definitions = [
        definition
        for ifc_class in (
            "IfcPropertySet",
            "IfcElementQuantity",
            "IfcMaterialProperties",
            "IfcProfileProperties",
        )
        for definition in reopened.by_type(ifc_class)
        if definition.Name and definition.Name.startswith("OSR_")
    ]
    invalid_custom_pset_names = [
        definition.Name
        for ifc_class in (
            "IfcPropertySet",
            "IfcMaterialProperties",
            "IfcProfileProperties",
        )
        for definition in reopened.by_type(ifc_class)
        if definition.Name and definition.Name.startswith("Pset_OSR_")
    ]
    exported_templates = {
        template.Name: template
        for template in reopened.by_type("IfcPropertySetTemplate")
    }
    expected_template_names = {
        row["name"] for row in index["property_set_templates"]
    }
    property_template_catalog_matches = (
        set(exported_templates) == expected_template_names
    )
    property_template_links_match = True
    linked_definition_ids: Counter[int] = Counter()
    for template_row in index["property_set_templates"]:
        template = exported_templates.get(template_row["name"])
        if template is None:
            property_template_catalog_matches = False
            property_template_links_match = False
            continue
        observed_properties = {
            property_template.Name: {
                "name": property_template.Name,
                "template_type": property_template.TemplateType,
                "primary_measure_type": property_template.PrimaryMeasureType,
            }
            for property_template in template.HasPropertyTemplates
        }
        expected_properties = {
            property_row["name"]: property_row
            for property_row in template_row["properties"]
        }
        property_template_catalog_matches &= (
            template.TemplateType == template_row["template_type"]
            and template.ApplicableEntity
            == ",".join(template_row["applicable_entities"])
            and observed_properties == expected_properties
            and template_row["property_count"] == len(observed_properties)
            and template_row["matched_definition_count"]
            == sum(
                definition.Name == template_row["name"]
                and definition.is_a() == template_row["definition_class"]
                for definition in custom_definitions
            )
            and template_row["status"]
            == "osr-custom-template; not-buildingSMART-standard-pset"
        )
        relationships = [
            relationship
            for relationship in reopened.by_type("IfcRelDefinesByTemplate")
            if relationship.RelatingTemplate == template
        ]
        relationship_expected = template_row["linkage"] == "IfcRelDefinesByTemplate"
        observed_definitions = list(relationships[0].RelatedPropertySets) if relationships else []
        linked_definition_ids.update(definition.id() for definition in observed_definitions)
        property_template_links_match &= (
            len(relationships) == (1 if relationship_expected else 0)
            and len(observed_definitions) == template_row["linked_definition_count"]
            and all(
                definition.Name == template_row["name"]
                and definition.is_a() == template_row["definition_class"]
                for definition in observed_definitions
            )
        )
    property_template_links_match &= (
        set(linked_definition_ids)
        == {
            definition.id()
            for definition in custom_definitions
            if definition.is_a() in {"IfcPropertySet", "IfcElementQuantity"}
        }
        and all(count == 1 for count in linked_definition_ids.values())
    )
    template_declarations = [
        relationship
        for relationship in reopened.by_type("IfcRelDeclares")
        if relationship.RelatingContext.is_a("IfcProject")
        and any(
            definition.is_a("IfcPropertySetTemplate")
            for definition in relationship.RelatedDefinitions
        )
    ]
    property_template_declarations_match = (
        len(template_declarations) == 1
        and {
            definition
            for definition in template_declarations[0].RelatedDefinitions
            if definition.is_a("IfcPropertySetTemplate")
        }
        == set(exported_templates.values())
    )
    exported_cost_schedules = reopened.by_type("IfcCostSchedule")
    planning_rate_schedule_matches = False
    planning_rate_items_match = False
    if len(exported_cost_schedules) == 1:
        exported_cost_schedule = exported_cost_schedules[0]
        expected_cost_schedule = index["cost_schedule"]
        control_relationships = [
            relationship
            for relationship in reopened.by_type("IfcRelAssignsToControl")
            if relationship.RelatingControl == exported_cost_schedule
        ]
        observed_cost_items = {
            item.Identification: item
            for relationship in control_relationships
            for item in relationship.RelatedObjects
            if item.is_a("IfcCostItem")
        }
        monetary_units = reopened.by_type("IfcMonetaryUnit")
        planning_rate_schedule_matches = (
            exported_cost_schedule.Identification
            == expected_cost_schedule["schedule_id"]
            and exported_cost_schedule.Name == expected_cost_schedule["name"]
            and exported_cost_schedule.PredefinedType == "SCHEDULEOFRATES"
            and exported_cost_schedule.Status
            == "planning-target-not-a-quotation"
            and exported_cost_schedule.UpdateDate == FIXED_REVIEW_TIMESTAMP
            and "not a bill, tender, quotation, or element-level estimate"
            in exported_cost_schedule.Description
            and len(monetary_units) == 1
            and monetary_units[0].Currency == expected_cost_schedule["currency"]
            and len(control_relationships) == 1
            and len(observed_cost_items) == expected_cost_schedule["item_count"]
        )
        planning_rate_items_match = set(observed_cost_items) == {
            row["rate_id"] for row in expected_cost_schedule["items"]
        }
        for rate_row in expected_cost_schedule["items"]:
            item = observed_cost_items.get(rate_row["rate_id"])
            values = list(item.CostValues or ()) if item is not None else []
            value = values[0] if len(values) == 1 else None
            planning_rate_items_match &= (
                item is not None
                and item.Name == rate_row["name"]
                and item.PredefinedType == "USERDEFINED"
                and item.ObjectType == "Planning civil unit-rate alternative"
                and not item.CostQuantities
                and not item.Controls
                and value is not None
                and value.AppliedValue.is_a("IfcMonetaryMeasure")
                and math.isclose(
                    value.AppliedValue.wrappedValue,
                    rate_row["rate_usd_per_route_km"],
                    abs_tol=1e-6,
                )
                and value.UnitBasis is not None
                and math.isclose(
                    value.UnitBasis.ValueComponent.wrappedValue,
                    rate_row["unit_basis_value_m"],
                    abs_tol=1e-9,
                )
                and value.UnitBasis.UnitComponent.is_a("IfcSIUnit")
                and value.UnitBasis.UnitComponent.UnitType == "LENGTHUNIT"
                and value.UnitBasis.UnitComponent.Name == "METRE"
                and value.Category == "PLANNING_TARGET"
                and value.Condition == "planning-target-not-a-quotation"
                and rate_row["quantity_status"]
                == "none; schedule-of-rates entry only"
                and rate_row["product_assignment_status"]
                == "none; alternatives are not selected scope"
            )
    exported_alignments = reopened.by_type("IfcAlignment")
    native_alignment_structure_matches = False
    native_alignment_geometry_matches = False
    if len(exported_alignments) == 1:
        exported_alignment = exported_alignments[0]
        horizontal_layout = get_horizontal_layout(exported_alignment)
        vertical_layout = get_vertical_layout(exported_alignment)
        horizontal_segments = (
            list(get_layout_segments(horizontal_layout))
            if horizontal_layout is not None
            else []
        )
        vertical_segments = (
            list(get_layout_segments(vertical_layout))
            if vertical_layout is not None
            else []
        )
        expected_alignment = index["alignment"]
        expected_points = expected_alignment["control_points_m"]
        horizontal_design_segments = horizontal_segments[:-1]
        vertical_design_segments = vertical_segments[:-1]
        aggregation = [
            relationship
            for relationship in exported_alignment.Decomposes
            if relationship.is_a("IfcRelAggregates")
        ]
        native_alignment_structure_matches = (
            horizontal_layout is not None
            and vertical_layout is not None
            and len(horizontal_design_segments)
            == expected_alignment["horizontal_segment_count"]
            and len(vertical_design_segments)
            == expected_alignment["vertical_segment_count"]
            and len(horizontal_segments)
            == expected_alignment["horizontal_segment_count"] + 1
            and len(vertical_segments)
            == expected_alignment["vertical_segment_count"] + 1
            and horizontal_segments[-1].DesignParameters.SegmentLength == 0.0
            and vertical_segments[-1].DesignParameters.HorizontalLength == 0.0
            and len(aggregation) == 1
            and aggregation[0].RelatingObject.is_a("IfcProject")
            and len(reopened.by_type("IfcReferent"))
            == expected_alignment["stationing_referent_count"]
            and all(
                referent.PredefinedType == "STATION"
                for referent in reopened.by_type("IfcReferent")
            )
        )
        observed_length = sum(
            segment.DesignParameters.SegmentLength
            for segment in horizontal_design_segments
        )
        native_alignment_geometry_matches = (
            exported_alignment.Representation is not None
            and get_alignment_curve(exported_alignment) is not None
            and get_alignment_curve(exported_alignment).is_a()
            == expected_alignment["geometry_curve"]
            and all(
                segment.DesignParameters.PredefinedType == "LINE"
                and all(
                    math.isclose(observed, expected, abs_tol=1e-9)
                    for observed, expected in zip(
                        segment.DesignParameters.StartPoint.Coordinates,
                        point[:2],
                    )
                )
                for segment, point in zip(
                    horizontal_design_segments, expected_points
                )
            )
            and all(
                segment.DesignParameters.PredefinedType == "CONSTANTGRADIENT"
                and math.isclose(
                    segment.DesignParameters.StartHeight,
                    point[2],
                    abs_tol=1e-9,
                )
                for segment, point in zip(
                    vertical_design_segments, expected_points
                )
            )
            and math.isclose(
                observed_length,
                expected_alignment["total_horizontal_length_m"],
                abs_tol=1e-6,
            )
            and expected_alignment["cant_status"]
            == "not-modelled; accepted cant design unavailable"
            and expected_alignment["transition_status"]
            == "not-modelled; planning polyline has no accepted radii"
        )
    projected_crs = reopened.by_type("IfcProjectedCRS")
    map_conversions = reopened.by_type("IfcMapConversion")
    georeferencing = index["georeferencing"]
    georeferencing_matches = (
        len(projected_crs) == len(map_conversions) == 1
        and georeferencing["native_ifc_georeferencing"]
        and projected_crs[0].Name == georeferencing["crs_name"]
    ) or (
        not georeferencing["native_ifc_georeferencing"]
        and not projected_crs
        and not map_conversions
    )
    checks = [
        {"id": "ifc4x3-schema", "passed": reopened.schema == "IFC4X3", "observed": reopened.schema},
        {"id": "ifc-schema-conformance", "passed": not schema_issues, "observed": len(schema_issues)},
        {"id": "stable-assets", "passed": tagged == expected, "observed": len(tagged)},
        {
            "id": "native-object-types",
            "passed": exported_types == expected_types,
            "observed": len(exported_types),
        },
        {
            "id": "type-assignments",
            "passed": type_assignments_match,
            "observed": sum(
                bool(getattr(product, "IsTypedBy", None))
                for product in reopened.by_type("IfcElement")
            ),
        },
        {
            "id": "native-rolling-stock-vehicles",
            "passed": native_vehicle_semantics_match,
            "observed": len(reopened.by_type("IfcVehicle")),
        },
        {
            "id": "native-material-families",
            "passed": exported_materials == expected_materials and material_catalog_matches,
            "observed": len(exported_materials),
        },
        {
            "id": "material-inheritance",
            "passed": material_assignments_match,
            "observed": sum(
                row["material_id"] is not None for row in index["objects"]
            ),
        },
        {
            "id": "native-profile-catalog",
            "passed": profile_catalog_matches,
            "observed": len(exported_profile_definitions),
        },
        {
            "id": "profile-geometry-usage",
            "passed": profile_geometry_usage_matches,
            "observed": sum(row["profile_id"] is not None for row in index["objects"]),
        },
        {
            "id": "native-document-register",
            "passed": document_catalog_matches,
            "observed": len(document_information),
        },
        {
            "id": "document-source-associations",
            "passed": document_associations_match,
            "observed": sum(bool(row["document_ids"]) for row in index["objects"]),
        },
        {
            "id": "native-osr-classification",
            "passed": classification_catalog_matches,
            "observed": len(index["classification"]["references"]),
        },
        {
            "id": "classification-inheritance",
            "passed": classification_assignments_match,
            "observed": sum(
                bool(row["classification_code"]) for row in index["objects"]
            ),
        },
        {
            "id": "native-coordination-groups",
            "passed": group_catalog_matches,
            "observed": len(exported_groups),
        },
        {
            "id": "coordination-group-membership",
            "passed": group_memberships_match,
            "observed": sum(observed_asset_memberships.values()),
        },
        {
            "id": "native-functional-systems",
            "passed": system_catalog_matches,
            "observed": len(exported_systems),
        },
        {
            "id": "functional-system-membership",
            "passed": system_memberships_match,
            "observed": sum(observed_system_memberships.values()),
        },
        {
            "id": "specialized-functional-systems",
            "passed": specialized_systems_match,
            "observed": sum(
                system.is_a() == "IfcBuiltSystem"
                for system in exported_systems.values()
            ),
        },
        {
            "id": "functional-system-spatial-references",
            "passed": system_spatial_references_match,
            "observed": observed_system_spatial_references,
        },
        {
            "id": "native-presentation-layers",
            "passed": layer_catalog_matches,
            "observed": len(exported_layers),
        },
        {
            "id": "presentation-layer-assignments",
            "passed": layer_assignments_match,
            "observed": len(representation_layer_ids),
        },
        {
            "id": "native-interface-constraints",
            "passed": constraint_catalog_matches,
            "observed": len(exported_constraints),
        },
        {
            "id": "native-interface-metrics",
            "passed": metric_catalog_matches,
            "observed": len(exported_metrics),
        },
        {
            "id": "interface-constraint-associations",
            "passed": constraint_associations_match,
            "observed": len(reopened.by_type("IfcRelAssociatesConstraint")),
        },
        {
            "id": "constraint-source-document-links",
            "passed": constraint_source_documents_match,
            "observed": len(constraint_source_relationships),
        },
        {
            "id": "external-engineering-decision-register",
            "passed": external_decision_register_valid,
            "observed": len(external_decisions),
        },
        {
            "id": "custom-property-set-naming",
            "passed": not invalid_custom_pset_names,
            "observed": len(invalid_custom_pset_names),
        },
        {
            "id": "native-property-templates",
            "passed": property_template_catalog_matches,
            "observed": len(exported_templates),
        },
        {
            "id": "property-template-links",
            "passed": property_template_links_match,
            "observed": len(linked_definition_ids),
        },
        {
            "id": "property-template-project-declaration",
            "passed": property_template_declarations_match,
            "observed": len(template_declarations),
        },
        {
            "id": "native-planning-rate-schedule",
            "passed": planning_rate_schedule_matches,
            "observed": len(exported_cost_schedules),
        },
        {
            "id": "planning-rate-items",
            "passed": planning_rate_items_match,
            "observed": index["cost_schedule"]["item_count"],
        },
        {"id": "railway-spatial-root", "passed": len(reopened.by_type("IfcRailway")) == 1, "observed": len(reopened.by_type("IfcRailway"))},
        {"id": "railway-parts", "passed": len(reopened.by_type("IfcRailwayPart")) == 4, "observed": len(reopened.by_type("IfcRailwayPart"))},
        {
            "id": "native-alignment-layouts",
            "passed": native_alignment_structure_matches,
            "observed": (
                f"{index['alignment']['horizontal_segment_count']} horizontal / "
                f"{index['alignment']['vertical_segment_count']} vertical segments"
            ),
        },
        {
            "id": "native-alignment-geometry",
            "passed": native_alignment_geometry_matches,
            "observed": index["alignment"]["geometry_curve"],
        },
        {
            "id": "georeferencing-contract",
            "passed": georeferencing_matches,
            "observed": georeferencing["mode"],
        },
        {"id": "construction-schedule", "passed": len(reopened.by_type("IfcWorkSchedule")) == 1, "observed": len(reopened.by_type("IfcTask"))},
        {"id": "task-index-match", "passed": len(reopened.by_type("IfcTask")) == len(sequence["tasks"]), "observed": len(sequence["tasks"])},
        {"id": "all-interface-checks", "passed": all(item["passed"] for item in index["validation"]), "observed": len(index["validation"])},
        {"id": "ids-information-requirements", "passed": ids_report["status"], "observed": f"{ids_report['total_specifications_pass']}/{ids_report['total_specifications']} specifications"},
        {"id": "bcf3-coordination-topics", "passed": bcf_validation["version"] == "3.0" and bcf_validation["topic_count"] == bcf_index["topic_count"], "observed": bcf_validation["topic_count"]},
        {"id": "bcf-viewpoint-ifc-links", "passed": bcf_validation["all_selected_guids_resolve"], "observed": bcf_validation["selected_ifc_guids"]},
    ]
    return {
        "schema": "org.opensourcerail.bonsai-ifc-validation.v1",
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
        "ifc_sha256": sha256_bytes(ifc_path.read_bytes()),
        "ifc_size_bytes": ifc_path.stat().st_size,
        "artifact_sha256": {
            kind: sha256_bytes(paths[kind].read_bytes())
            for kind in ("ifc", "ids", "ids_report", "bcf", "bcf_index")
        },
        "ids": {
            "specifications": ids_report["total_specifications"],
            "requirements": ids_report["total_requirements"],
            "checks": ids_report["total_checks"],
        },
        "bcf": bcf_validation,
        "schema_validation": {
            "engine": f"IfcOpenShell {version('ifcopenshell')}",
            "express_rules": True,
            "issue_count": len(schema_issues),
            "issues": schema_issues,
        },
        "entity_count": sum(1 for _ in reopened),
    }


def write_outputs(out_dir: Path, *, alignment_path: Path | None, revision_id: str) -> dict[str, Path]:
    alignment_input = load_alignment(alignment_path)
    model, index, sequence = build_model(alignment_input=alignment_input, revision_id=revision_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "ifc": out_dir / "civil-coordination.ifc",
        "index": out_dir / "civil-coordination.index.json",
        "sequence": out_dir / "civil-construction-sequence.json",
        "ids": out_dir / "civil-information-requirements.ids",
        "ids_report": out_dir / "civil-information-requirements.report.json",
        "bcf": out_dir / "civil-coordination-issues.bcf",
        "bcf_index": out_dir / "civil-coordination-issues.index.json",
        "validation": out_dir / "civil-coordination.validation.json",
    }
    model.write(str(paths["ifc"]))
    ids_report = write_and_validate_ids(paths["ifc"], paths["ids"], paths["ids_report"], index)
    bcf_index = write_coordination_bcf(
        paths["ifc"], paths["bcf"], paths["bcf_index"], index, alignment_input
    )
    validation = validate_written(paths, index, sequence, ids_report, bcf_index)
    if not validation["passed"]:
        raise ValueError("written civil IFC failed validation")
    index["ifc_sha256"] = validation["ifc_sha256"]
    index["ifc_size_bytes"] = validation["ifc_size_bytes"]
    paths["index"].write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["sequence"].write_text(json.dumps(sequence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["validation"].write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--alignment-input", type=Path)
    parser.add_argument("--revision-id", default="working-tree")
    args = parser.parse_args(argv)
    paths = write_outputs(args.out_dir, alignment_path=args.alignment_input, revision_id=args.revision_id)
    for kind, path in paths.items():
        print(f"{kind}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

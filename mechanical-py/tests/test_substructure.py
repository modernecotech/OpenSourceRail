from __future__ import annotations

import pytest

from osr_mech.civil.substructure import (
    ABUTMENT_WIDTH_MM,
    ABUTMENT_ASSEMBLY_INSTRUCTIONS,
    GIRDER_CENTRE_SPACING_MM,
    PIER_CAP_Y_MM,
    PIER_ASSEMBLY_INSTRUCTIONS,
    WEB_BEARING_OFFSET_MM,
    abutment_bom,
    pier_bom,
    viaduct_abutment,
    viaduct_pier,
)
from osr_mech.civil.decked_pi import STEM_CENTRE_OFFSET_MM


@pytest.mark.parametrize("height_m", [5.0, 8.0, 12.0])
def test_pier_catalogue_envelope_and_bom(height_m: float) -> None:
    pier = viaduct_pier(height_m)
    assert pier.volume > 0
    assert sum(child.label == "Elastomeric/PTFE girder bearing" for child in pier.children) == 4
    assert sum("jacking shelf" in child.label for child in pier.children) == 4
    assert WEB_BEARING_OFFSET_MM == STEM_CENTRE_OFFSET_MM
    assert 6_500.0 <= PIER_CAP_Y_MM <= 7_500.0
    expected_y = sorted(
        girder_y + web_y
        for girder_y in (-GIRDER_CENTRE_SPACING_MM / 2.0, GIRDER_CENTRE_SPACING_MM / 2.0)
        for web_y in (-WEB_BEARING_OFFSET_MM, WEB_BEARING_OFFSET_MM)
    )
    actual_y = sorted(
        {
            (child.bounding_box().min.Y + child.bounding_box().max.Y) / 2.0
            for child in pier.children
            if child.label == "Elastomeric/PTFE girder bearing"
        }
    )
    assert actual_y == expected_y
    bom = {item.id: item for item in pier_bom(height_m)}
    assert bom["CIV-PIER-P020"].quantity == height_m
    assert bom["CIV-PIER-P040"].quantity == 4


def test_expansion_unit_boundary_keeps_two_bearing_lines() -> None:
    pier = viaduct_pier(8.0, continuity_role="expansion")
    assert sum(child.label == "Elastomeric/PTFE girder bearing" for child in pier.children) == 8
    assert pier_bom(8.0, continuity_role="expansion")[3].quantity == 8
    with pytest.raises(ValueError, match="continuity role"):
        viaduct_pier(8.0, continuity_role="unknown")


def test_pier_requires_actual_length_for_deep_foundation_geometry() -> None:
    interface = viaduct_pier(8.0)
    assert "interface-only" in interface.label
    assert any("depth intentionally not modelled" in child.label for child in interface.children)
    unresolved = viaduct_pier(8.0, foundation="bored-shaft")
    assert any("actual pile/shaft length required" in child.label for child in unresolved.children)
    released = viaduct_pier(8.0, foundation="bored-shaft", actual_foundation_length_m=18.0)
    shaft = next(child for child in released.children if "Bored-shaft" in child.label)
    assert shaft.bounding_box().min.Z == pytest.approx(-18_000.0)
    with pytest.raises(ValueError):
        viaduct_pier(8.0, foundation="unknown")  # type: ignore[arg-type]


def test_pier_rejects_non_catalogue_height() -> None:
    with pytest.raises(ValueError):
        viaduct_pier(4.9)
    with pytest.raises(ValueError):
        pier_bom(12.1)


def test_abutment_has_two_wings_four_bearings_and_expansion_joint() -> None:
    abutment = viaduct_abutment()
    labels = [child.label for child in abutment.children]
    assert abutment.volume > 0
    assert sum("wing wall" in label for label in labels) == 2
    assert labels.count("Elastomeric/PTFE girder bearing") == 4
    assert "Replaceable expansion-joint interface" in labels
    bom = {item.id: item for item in abutment_bom()}
    assert bom["CIV-ABT-P030"].quantity == 2
    assert bom["CIV-ABT-P040"].quantity == 4
    bearing_edges = [
        child.bounding_box()
        for child in abutment.children
        if child.label == "Elastomeric/PTFE girder bearing"
    ]
    assert max(box.max.Y for box in bearing_edges) <= ABUTMENT_WIDTH_MM / 2.0
    assert min(box.min.Y for box in bearing_edges) >= -ABUTMENT_WIDTH_MM / 2.0


def test_substructure_kits_publish_assembly_sequences() -> None:
    assert len(PIER_ASSEMBLY_INSTRUCTIONS) >= 5
    assert len(ABUTMENT_ASSEMBLY_INSTRUCTIONS) >= 4

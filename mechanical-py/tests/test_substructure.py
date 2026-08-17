from __future__ import annotations

import pytest

from osr_mech.civil.substructure import (
    ABUTMENT_ASSEMBLY_INSTRUCTIONS,
    PIER_ASSEMBLY_INSTRUCTIONS,
    abutment_bom,
    pier_bom,
    viaduct_abutment,
    viaduct_pier,
)


@pytest.mark.parametrize("height_m", [5.0, 8.0, 12.0])
def test_pier_catalogue_envelope_and_bom(height_m: float) -> None:
    pier = viaduct_pier(height_m)
    assert pier.volume > 0
    assert sum(child.label == "Elastomeric/PTFE girder bearing" for child in pier.children) == 8
    bom = {item.id: item for item in pier_bom(height_m)}
    assert bom["CIV-PIER-P020"].quantity == height_m
    assert bom["CIV-PIER-P040"].quantity == 8


def test_pier_supports_geotechnically_released_monopile_interface() -> None:
    pier = viaduct_pier(8.0, foundation="monopile")
    assert "monopile" in pier.label
    assert any("bored-shaft/monopile" in child.label for child in pier.children)
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


def test_substructure_kits_publish_assembly_sequences() -> None:
    assert len(PIER_ASSEMBLY_INSTRUCTIONS) >= 5
    assert len(ABUTMENT_ASSEMBLY_INSTRUCTIONS) >= 4

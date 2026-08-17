from __future__ import annotations

import pytest

from osr_mech.civil.segmental import segmental_u_envelope
from osr_mech.civil.special_span import special_span_envelope


def test_segmental_family_controls_match_cast_joint_planes() -> None:
    model = segmental_u_envelope(25.0, 2.5)
    labels = [child.label for child in model.children]
    assert labels.count("Match-cast epoxy joint and shear-key design plane") == 9
    assert any("Post-tensioning" in label for label in labels)
    with pytest.raises(ValueError):
        segmental_u_envelope(25.0, 4.0)


def test_special_span_is_separate_from_full_span_u_catalogue() -> None:
    model = special_span_envelope(40.0)
    assert model.label.startswith("OSR-SP")
    assert len(model.children) == 5
    with pytest.raises(ValueError):
        special_span_envelope(30.0)

from __future__ import annotations

from osr_mech.trainset_cots_candidates import load_and_validate, render_markdown


def test_every_bought_in_row_has_a_candidate() -> None:
    data = load_and_validate()
    coverage = data["coverage"]
    assert coverage["external_product_rows"] == 56
    assert coverage["covered_external_product_rows"] == 56
    assert coverage["uncovered_product_ids"] == []
    assert coverage["candidate_count"] >= 30


def test_register_preserves_release_boundary_and_integration_actions() -> None:
    data = load_and_validate()
    output = render_markdown(data)
    assert "does not prove LM3 fit" in data["release_boundary"]
    assert "Before freeze" in output
    assert "OSR-COTS-HV-SCHALTBAU-C360" in output
    assert "OSR-COTS-CONTROL-DUAGON-MH50C" in output

"""Non-FreeCAD checks for the generated FEA screening pipeline."""

from __future__ import annotations

from pathlib import Path

from osr_mech.freecad_fea import _markdown_link_path, all_studies
from osr_mech.freecad_screenshots import _refresh_latest_outputs


def test_freecad_fea_studies_cover_broadened_load_cases() -> None:
    studies = all_studies()
    slugs = {study.slug for study in studies}
    assert {
        "chassis-bogie-screen",
        "chassis-aw3-proof-screen",
        "chassis-track-twist-screen",
        "bogie-frame-screen",
        "bogie-brake-traction-screen",
        "full-body-frame-screen",
        "full-body-lateral-sway-screen",
    } <= slugs
    assert all(study.nodes for study in studies)
    assert all(study.elements for study in studies)
    assert all(study.loads for study in studies)


def test_fea_summary_result_links_are_local_to_catalog() -> None:
    link = _markdown_link_path(
        "mechanical-py/catalog/fea/chassis-bogie-screen/chassis-bogie-screen-result.png",
        Path("mechanical-py/catalog/fea").resolve(),
    )
    assert link == "chassis-bogie-screen/chassis-bogie-screen-result.png"


def test_freecad_screenshot_cleanup_preserves_solver_result_pngs(tmp_path) -> None:
    screenshot = tmp_path / "freecad-fea-screening-models.png"
    result = tmp_path / "freecad-fea-chassis-bogie-screen-result.png"
    screenshot.write_bytes(b"old screenshot")
    result.write_bytes(b"solver plot")

    _refresh_latest_outputs(tmp_path)

    assert not screenshot.exists()
    assert result.exists()

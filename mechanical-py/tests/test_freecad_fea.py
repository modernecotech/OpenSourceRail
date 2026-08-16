"""Non-FreeCAD checks for the generated FEA screening pipeline."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from osr_mech.freecad_fea import _ccx_deck_stem, _markdown_link_path, all_studies
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
        "full-set-longitudinal-buff-screen",
        "full-set-vertical-service-screen",
        "train-to-train-joint-vertical-screen",
        "train-to-train-joint-lateral-sway-screen",
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


def test_calculix_deck_stem_is_short_local_name() -> None:
    study = next(study for study in all_studies() if study.slug == "full-set-longitudinal-buff-screen")

    assert _ccx_deck_stem(study) == "full-set-longitudinal-buff-screen"
    assert "/" not in _ccx_deck_stem(study)


def test_generated_fea_screening_artifacts_are_solver_backed() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    summary_path = repo_root / "mechanical-py/catalog/fea/screening-summary.json"
    assert summary_path.exists(), "run scripts/freecad-generate.sh --fem to create FEA evidence"
    summary = json.loads(summary_path.read_text())
    assert summary["dependencies"]["freecad_importable"] is True
    expected_slugs = {study.slug for study in all_studies()}
    results = {result["slug"]: result for result in summary["results"]}
    missing_generated_slugs = expected_slugs - results.keys()
    pending_long_consist_slugs = {
        "full-set-longitudinal-buff-screen",
        "full-set-vertical-service-screen",
        "train-to-train-joint-vertical-screen",
        "train-to-train-joint-lateral-sway-screen",
    }
    if missing_generated_slugs:
        assert missing_generated_slugs <= pending_long_consist_slugs
        assert shutil.which("FreeCADCmd") is None and shutil.which("freecadcmd") is None

    for slug in expected_slugs & results.keys():
        result = results[slug]
        assert result["solver_ok"] is True, f"{slug} did not solve"
        assert result["nodes"] > 0
        assert result["elements"] > 0
        assert result["issue"] is None, f"{slug} has unresolved screening issue: {result['issue']}"
        assert result["max_displacement_mm"] <= result["deflection_limit_mm"]
        assert result["safety_factor_to_yield"] > 2.0
        assert (repo_root / result["result_png"]).exists(), f"{slug} missing catalog result PNG"
        assert (repo_root / result["docs_result_png"]).exists(), f"{slug} missing docs result PNG"


def test_freecad_screenshot_cleanup_preserves_solver_result_pngs(tmp_path) -> None:
    screenshot = tmp_path / "freecad-fea-screening-models.png"
    result = tmp_path / "freecad-fea-chassis-bogie-screen-result.png"
    screenshot.write_bytes(b"old screenshot")
    result.write_bytes(b"solver plot")

    _refresh_latest_outputs(tmp_path)

    assert not screenshot.exists()
    assert result.exists()

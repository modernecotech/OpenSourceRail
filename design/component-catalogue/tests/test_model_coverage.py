from __future__ import annotations

import json
from pathlib import Path

from engineering.model_coverage import LEVELS, build_register, write


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_model_coverage_matches_both_product_manifests() -> None:
    register = build_register()
    assert register["passed"]
    assert register["summary"]["lm3_products"] == 101
    assert register["summary"]["station_products"] == 45
    assert register["summary"]["station_variants"] == 7
    assert set(register["summary"]["geometry_level_counts"]) <= set(LEVELS)
    assert all(row["release_evidence"] for row in register["lm3_products"])
    assert all(row["analysis_ids"] for row in register["station_products"])


def test_model_coverage_outputs_are_deterministic(tmp_path: Path) -> None:
    first_json = tmp_path / "first.json"
    first_md = tmp_path / "first.md"
    second_json = tmp_path / "second.json"
    second_md = tmp_path / "second.md"
    write(first_json, first_md)
    write(second_json, second_md)
    assert first_json.read_bytes() == second_json.read_bytes()
    assert first_md.read_bytes() == second_md.read_bytes()
    assert json.loads(first_json.read_text())["passed"] is True


def test_public_model_handoffs_exist_for_every_covered_item() -> None:
    register = build_register()
    for row in register["lm3_products"]:
        assert (REPO_ROOT / row["freecad"]).is_file()
        assert (REPO_ROOT / row["ifc"]).is_file()
        if row["route"] == "MAKE":
            assert (REPO_ROOT / row["neutral_step"]).is_file()
            assert (REPO_ROOT / row["neutral_dxf"]).is_file()
            assert (REPO_ROOT / row["reference_drawing"]).is_file()
    for variant in register["station_variants"]:
        assert (REPO_ROOT / variant["freecad"]).is_file()
        assert (REPO_ROOT / variant["ifc"]).is_file()

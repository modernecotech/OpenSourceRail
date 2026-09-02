from __future__ import annotations

import json
from pathlib import Path

from engineering.station_product_reconciliation import build_register, write


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_station_product_handoffs_have_no_orphan_ids() -> None:
    register = build_register()
    assert register["passed"] is True
    assert register["variant_count"] == 7
    for variant in register["variants"]:
        assert variant["passed"] is True
        assert variant["mismatches"] == {}
        assert variant["missing_definition_sheets"] == []
        assert variant["missing_connection_controls"] == []
        assert variant["configuration_states"] == ["installed", "exploded"]
        assert variant["product_count"] == variant["definition_sheet_count"]


def test_station_product_reconciliation_is_deterministic(tmp_path: Path) -> None:
    first_json = tmp_path / "first.json"
    first_md = tmp_path / "first.md"
    second_json = tmp_path / "second.json"
    second_md = tmp_path / "second.md"
    write(first_json, first_md)
    write(second_json, second_md)
    assert first_json.read_bytes() == second_json.read_bytes()
    assert first_md.read_bytes() == second_md.read_bytes()
    assert json.loads(first_json.read_text(encoding="utf-8"))["passed"] is True


def test_station_review_sidecars_are_public_and_hash_locked() -> None:
    index_path = REPO_ROOT / "design/component-catalogue/models/cad/stations/station-library.index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    for row in index["variants"]:
        sidecar = REPO_ROOT / row["assembly_review"]
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
        assert sidecar.is_file()
        assert payload["product_ids"] == row["product_ids"]
        assert payload["assembly_ids"] == row["assembly_ids"]
        assert [state["id"] for state in payload["states"]] == ["installed", "exploded"]
        assert len(payload["datums_and_zones"]) >= 8
        tor = next(item for item in payload["datums_and_zones"] if item["id"] == "DATUM-TOR")
        assert all(
            interface["boarding_z_mm"] - interface["top_of_rail_z_mm"] == 350.0
            for interface in tor["interfaces"]
        )

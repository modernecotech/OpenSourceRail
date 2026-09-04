from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ElementTree
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_neutral_make_handoffs_are_complete_and_hash_locked() -> None:
    root = REPO_ROOT / "design/component-catalogue/models/manufacturing-reference"
    index = json.loads((root / "index.json").read_text(encoding="utf-8"))
    assert index["passed"] is True
    assert index["make_product_count"] == 62
    assert len(index["entries"]) == 62
    for row in index["entries"]:
        step = REPO_ROOT / row["step"]
        dxf = REPO_ROOT / row["dxf"]
        drawing = REPO_ROOT / row["drawing"]
        assert step.suffix == ".step"
        assert re.fullmatch(r"[0-9a-f]{64}", row["step_sha256"])
        # STEP exports are intentionally local-only because they are bulky and
        # require FreeCAD. Validate their content when the optional exports are
        # present; a clean checkout still validates the controlled hash record.
        if step.is_file():
            assert _sha256(step) == row["step_sha256"]
            assert "ISO-10303-21" in step.read_text(encoding="utf-8")[:100]
        assert _sha256(dxf) == row["dxf_sha256"]
        assert _sha256(drawing) == row["drawing_sha256"]
        assert "LWPOLYLINE" in dxf.read_text(encoding="ascii")
        assert ElementTree.parse(drawing).getroot().tag.endswith("svg")


def test_station_freecad_library_is_complete_and_hash_locked() -> None:
    root = REPO_ROOT / "design/component-catalogue/models/cad/stations"
    index = json.loads((root / "station-library.index.json").read_text(encoding="utf-8"))
    assert index["passed"] is True
    assert index["variant_count"] == 7
    assert {row["archetype"] for row in index["variants"]} == {
        "halt",
        "standard",
        "major",
        "interchange",
        "interchange-elevated",
        "terminal",
        "depot-terminal",
    }
    for row in index["variants"]:
        path = REPO_ROOT / row["file"]
        sidecar = REPO_ROOT / row["assembly_review"]
        assert path.stat().st_size == row["size_bytes"]
        assert _sha256(path) == row["sha256"]
        assert _sha256(sidecar) == row["assembly_review_sha256"]
        assert row["configuration_states"] == ["installed", "exploded"]
        assert row["native_shape_count"] == row["primitive_count"] * 2
        assert len(row["product_ids"]) == row["product_count"]
        assert len(row["assembly_ids"]) == row["assembly_count"]
        assert row["reopen_validated"] is True


def test_station_installed_and_exploded_review_images_are_public() -> None:
    screenshot_root = REPO_ROOT / "docs/screenshots/freecad"
    for name in (
        "freecad-station-standard-installed.png",
        "freecad-station-standard-exploded.png",
    ):
        path = screenshot_root / name
        assert path.is_file()
        assert path.stat().st_size > 10_000

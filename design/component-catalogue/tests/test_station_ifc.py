"""Determinism checks for the generated station IFC handoff."""

from __future__ import annotations

import json
import runpy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
EXPORTER = REPO_ROOT / "engineering/interchange/station_ifc.py"
MANIFEST = (
    REPO_ROOT
    / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
)


def test_station_ifc_is_byte_deterministic(tmp_path: Path) -> None:
    module = runpy.run_path(str(EXPORTER))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    standard = next(
        variant for variant in manifest["variants"] if variant["archetype"] == "standard"
    )
    first = tmp_path / "first.ifc"
    second = tmp_path / "second.ifc"

    first_report = module["export_variant"](standard, first)
    second_report = module["export_variant"](standard, second)

    assert first.read_bytes() == second.read_bytes()
    assert first_report["ifc_sha256"] == second_report["ifc_sha256"]
    assert module["FIXED_HEADER_TIMESTAMP"] in first.read_text(encoding="utf-8")

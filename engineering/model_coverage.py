#!/usr/bin/env python3
"""Generate the single CAD/IFC model-fidelity and release-evidence register."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MECHANICAL_SRC = REPO_ROOT / "design/component-catalogue/src"
if str(MECHANICAL_SRC) not in sys.path:
    sys.path.insert(0, str(MECHANICAL_SRC))

from osr_mech.rolling_stock.product_geometry import (  # noqa: E402
    flatten_geometry as flatten_lm3,
    geometry_level as lm3_geometry_level,
    geometry_specs as lm3_geometry_specs,
    product_geometry,
)
from osr_mech.station.product_geometry import (  # noqa: E402
    flatten_geometry as flatten_station,
    geometry_specs as station_geometry_specs,
    station_product_geometry,
)


LM3_MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
STATION_MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
DEFAULT_JSON = REPO_ROOT / "engineering/models/model-coverage.json"
DEFAULT_MD = REPO_ROOT / "engineering/models/model-coverage.md"
LEVELS = (
    "absent",
    "structure-only",
    "coordination-envelope",
    "manufacturing-envelope",
    "design-reference-detail",
    "interface-detailed",
    "fabrication-detailed",
    "released",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lm3_analysis_ids(product_id: str) -> list[str]:
    if product_id.startswith(("LM3-BDY", "LM3-CWL", "LM3-END")):
        return ["OSR-AN-RS-BODY-001", "OSR-AN-RS-FEA-SCREEN-001"]
    if product_id.startswith("LM3-BOG"):
        return ["OSR-AN-RS-TRAC-001", "OSR-AN-RS-FEA-SCREEN-001"]
    if product_id.startswith(("LM3-ART",)):
        return ["OSR-AN-RS-FEA-SCREEN-001"]
    if product_id.startswith(("LM3-HV", "LM3-TRC")):
        return ["OSR-AN-RS-HV-001", "OSR-AN-RS-TRAC-001"]
    return ["OSR-AN-IFC-LM3-MFG-001"]


def station_analysis_ids(product_id: str) -> list[str]:
    result = ["OSR-AN-IFC-STN-001"]
    if product_id.startswith(("STN-CNP", "STN-STR")):
        result.append("OSR-AN-STN-STR-001")
    if product_id.startswith(("STN-ACC", "STN-PAX")):
        result.append("OSR-AN-STN-PED-002")
    if product_id.startswith(("STN-CIV", "STN-CNP", "STN-DEP", "STN-TRK")):
        result.append("OSR-AN-STN-DRA-001")
    if product_id.startswith(("STN-CHG", "STN-MEP", "STN-CNP")):
        result.append("OSR-AN-ENE-CHG-001")
    if product_id.startswith(("STN-CHG", "STN-DEP", "STN-MEP")):
        result.extend(["OSR-AN-STN-THM-001", "OSR-AN-STN-FIR-001"])
    return result


def build_register() -> dict[str, Any]:
    lm3 = json.loads(LM3_MANIFEST.read_text(encoding="utf-8"))
    stations = json.loads(STATION_MANIFEST.read_text(encoding="utf-8"))
    lm3_specs = lm3_geometry_specs()
    lm3_ids = {str(item["id"]) for item in lm3["product_items"]}
    if lm3_ids != set(lm3_specs):
        raise ValueError("LM3 model coverage differs from the controlled product manifest")

    lm3_rows: list[dict[str, Any]] = []
    for item in lm3["product_items"]:
        product_id = str(item["id"])
        leaves = flatten_lm3(product_geometry(product_id, str(item["title"])))
        level = lm3_geometry_level(product_id, str(item["route"]), str(item["maturity"]))
        if level not in LEVELS:
            raise ValueError(f"unknown model level {level} for {product_id}")
        lm3_rows.append({
            "id": product_id,
            "title": item["title"],
            "route": item["route"],
            "product_maturity": item["maturity"],
            "geometry_level": level,
            "geometry_form": lm3_specs[product_id].form,
            "primitive_count": len(leaves),
            "freecad": f"design/component-catalogue/models/cad/lm3-parts/{product_id}.FCStd",
            "ifc": f"engineering/models/bim/reference/lm3-parts/{product_id}.ifc",
            "neutral_step": (
                f"design/component-catalogue/models/manufacturing-reference/step/{product_id}.step"
                if item["route"] == "MAKE" else None
            ),
            "neutral_dxf": (
                f"design/component-catalogue/models/manufacturing-reference/dxf-inspection-projections/{product_id}.dxf"
                if item["route"] == "MAKE" else None
            ),
            "reference_drawing": (
                f"design/component-catalogue/models/manufacturing-reference/drawing-references/{product_id}.svg"
                if item["route"] == "MAKE" else None
            ),
            "analysis_ids": lm3_analysis_ids(product_id),
            "release_evidence": item["acceptance"],
        })

    unique_station_items: dict[str, dict[str, Any]] = {}
    variant_coverage: list[dict[str, Any]] = []
    station_specs = station_geometry_specs()
    for variant in stations["variants"]:
        represented = []
        primitive_count = 0
        for item in variant["product_items"]:
            product_id = str(item["id"])
            unique_station_items.setdefault(product_id, item)
            leaves = flatten_station(station_product_geometry(item, variant["parameters"]))
            if not leaves or any(leaf.bounding_box().volume <= 0 for leaf in leaves):
                raise ValueError(f"invalid station geometry {variant['archetype']}/{product_id}")
            primitive_count += len(leaves)
            represented.append(product_id)
        variant_coverage.append({
            "archetype": variant["archetype"],
            "product_count": len(represented),
            "primitive_count": primitive_count,
            "freecad": f"design/component-catalogue/models/cad/stations/station-{variant['archetype']}.FCStd",
            "ifc": f"engineering/models/bim/reference/stations/station-{variant['archetype']}.ifc",
        })
    if set(unique_station_items) != set(station_specs):
        raise ValueError("station model coverage differs from the controlled product manifest")
    station_rows = [{
        "id": product_id,
        "title": item["title"],
        "route": item["route"],
        "product_maturity": item["maturity"],
        "geometry_level": station_specs[product_id].geometry_level,
        "ifc_class": station_specs[product_id].ifc_class,
        "analysis_ids": station_analysis_ids(product_id),
        "release_evidence": item["acceptance"],
    } for product_id, item in sorted(unique_station_items.items())]

    level_counts = Counter(row["geometry_level"] for row in [*lm3_rows, *station_rows])
    return {
        "schema": "org.opensourcerail.model-coverage.v1",
        "status": "design-reference-not-released",
        "levels": list(LEVELS),
        "release_boundary": "Geometry level records modelling fidelity, not engineering approval or construction release.",
        "sources": {
            "lm3_manifest": str(LM3_MANIFEST.relative_to(REPO_ROOT)),
            "lm3_manifest_sha256": sha256(LM3_MANIFEST),
            "station_manifest": str(STATION_MANIFEST.relative_to(REPO_ROOT)),
            "station_manifest_sha256": sha256(STATION_MANIFEST),
        },
        "summary": {
            "lm3_products": len(lm3_rows),
            "station_products": len(station_rows),
            "station_variants": len(variant_coverage),
            "geometry_level_counts": dict(sorted(level_counts.items())),
        },
        "lm3_products": lm3_rows,
        "station_products": station_rows,
        "station_variants": variant_coverage,
        "passed": len(lm3_rows) == 120 and len(station_rows) == 45 and len(variant_coverage) == 7,
    }


def render_markdown(register: dict[str, Any]) -> str:
    counts = register["summary"]["geometry_level_counts"]
    lines = [
        "# CAD and IFC model coverage",
        "",
        "This generated register is the concise fidelity view for the LM3 and station",
        "models. Product maturity, geometry fidelity and release approval are separate",
        "states; no row is a construction release merely because geometry exists.",
        "",
        "## Summary",
        "",
        f"- LM3 product models: {register['summary']['lm3_products']}",
        f"- Unique station product models: {register['summary']['station_products']}",
        f"- Complete station variant assemblies: {register['summary']['station_variants']}",
        "- Geometry levels: " + ", ".join(f"`{key}`={value}" for key, value in counts.items()),
        "",
        "## Meaning",
        "",
        "`coordination-envelope` controls space and interfaces for sourced equipment;",
        "`manufacturing-envelope` adds OSR manufacturing intent; `design-reference-detail`",
        "adds inspectable subcomponents; `interface-detailed`",
        "models repeatable datums, connections or service routes. `fabrication-detailed`",
        "and `released` require controlled drawings, tolerances and accepted evidence.",
        "",
        "The complete machine-readable per-product mapping, analysis IDs, evidence gates",
        "and FreeCAD/IFC/neutral-output paths are in",
        "[`model-coverage.json`](model-coverage.json).",
        "",
    ]
    return "\n".join(lines)


def write(json_path: Path = DEFAULT_JSON, markdown_path: Path = DEFAULT_MD) -> dict[str, Any]:
    register = build_register()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(register, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(register), encoding="utf-8")
    return register


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    register = write(args.json.resolve(), args.markdown.resolve())
    print(json.dumps(register["summary"], indent=2, sort_keys=True))
    return 0 if register["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Prove station product identities agree across every public handoff."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MECHANICAL_SRC = REPO_ROOT / "design/component-catalogue/src"
if str(MECHANICAL_SRC) not in sys.path:
    sys.path.insert(0, str(MECHANICAL_SRC))

from osr_mech.buildable_stations import (  # noqa: E402
    StationProductItem,
    StationVariant,
    product_connection_id,
    product_drawing_id,
)


MANIFEST = REPO_ROOT / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
CATALOGUE = MANIFEST.parent
BOM_ROOT = REPO_ROOT / "build/bom/stations"
FREECAD_ROOT = REPO_ROOT / "design/component-catalogue/models/cad/stations"
IFC_SUMMARY = REPO_ROOT / "engineering/models/bim/reference/stations/summary.json"
DEFAULT_JSON = CATALOGUE / "station-product-reconciliation.json"
DEFAULT_MARKDOWN = CATALOGUE / "station-product-reconciliation.md"
ID_PATTERN = re.compile(r"STN-[A-Z]+-(?:P|SA|A)\d{3}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ids_in_text(path: Path) -> set[str]:
    return set(ID_PATTERN.findall(path.read_text(encoding="utf-8")))


def _variant(value: dict[str, object]) -> StationVariant:
    products = tuple(StationProductItem(**row) for row in value["product_items"])
    # Only product helper functions need a StationVariant; keep assembly dictionaries
    # in the manifest as the authority for the hierarchy comparison.
    return StationVariant(
        archetype=str(value["archetype"]),
        consist=str(value["consist"]),
        parameters=dict(value["parameters"]),
        product_items=products,
        assemblies=(),
        baseline_exclusions=tuple(value["baseline_exclusions"]),
    )


def build_register() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    freecad_index = json.loads((FREECAD_ROOT / "station-library.index.json").read_text(encoding="utf-8"))
    ifc_summary = json.loads(IFC_SUMMARY.read_text(encoding="utf-8"))
    freecad_variants = {row["archetype"]: row for row in freecad_index["variants"]}
    ifc_variants = {row["archetype"]: row for row in ifc_summary["variants"]}
    results: list[dict[str, object]] = []

    for raw in manifest["variants"]:
        archetype = str(raw["archetype"])
        variant = _variant(raw)
        expected_products = {item.id for item in variant.product_items}
        expected_assemblies = {str(row["id"]) for row in raw["assemblies"]}
        expected_all = expected_products | expected_assemblies

        with (BOM_ROOT / f"{archetype}.csv").open(encoding="utf-8", newline="") as handle:
            bom_products = {str(row["engineering_id"]) for row in csv.DictReader(handle)}
        traveler_ids = _ids_in_text(CATALOGUE / "travelers" / f"{archetype}.md")
        definition = CATALOGUE / "variants" / f"{archetype}.md"
        definition_ids = _ids_in_text(definition)
        freecad = freecad_variants[archetype]
        sidecar_path = REPO_ROOT / str(freecad["assembly_review"])
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        ifc = ifc_variants[archetype]

        sources = {
            "bom_products": bom_products,
            "traveler_ids": traveler_ids,
            "definition_ids": definition_ids,
            "freecad_products": set(freecad["product_ids"]),
            "freecad_assemblies": set(freecad["assembly_ids"]),
            "state_map_products": set(sidecar["product_ids"]),
            "state_map_assemblies": set(sidecar["assembly_ids"]),
            "ifc_products": set(ifc["product_ids"]),
            "ifc_assemblies": set(ifc["assembly_ids"]),
        }
        expected_by_source = {
            "bom_products": expected_products,
            "traveler_ids": expected_all,
            "definition_ids": expected_all,
            "freecad_products": expected_products,
            "freecad_assemblies": expected_assemblies,
            "state_map_products": expected_products,
            "state_map_assemblies": expected_assemblies,
            "ifc_products": expected_products,
            "ifc_assemblies": expected_assemblies,
        }
        mismatches = {
            name: {
                "missing": sorted(expected_by_source[name] - values),
                "unexpected": sorted(values - expected_by_source[name]),
            }
            for name, values in sources.items()
            if values != expected_by_source[name]
        }
        missing_definition_sheets = sorted(
            product_drawing_id(variant, item)
            for item in variant.product_items
            if product_drawing_id(variant, item) not in definition.read_text(encoding="utf-8")
        )
        required_connections = sorted(
            control
            for item in variant.product_items
            if (control := product_connection_id(item)) != "not-applicable"
        )
        missing_connections = sorted(
            control for control in required_connections if control not in definition.read_text(encoding="utf-8")
        )
        state_ids = [str(row["id"]) for row in sidecar["states"]]
        state_ok = state_ids == ["installed", "exploded"]
        hashes_ok = (
            _sha256(MANIFEST) == sidecar["manifest_sha256"]
            and _sha256(sidecar_path) == freecad["assembly_review_sha256"]
        )
        passed = not mismatches and not missing_definition_sheets and not missing_connections and state_ok and hashes_ok
        results.append(
            {
                "archetype": archetype,
                "assembly_count": len(expected_assemblies),
                "product_count": len(expected_products),
                "definition_sheet_count": len(expected_products),
                "connection_control_count": len(required_connections),
                "configuration_states": state_ids,
                "mismatches": mismatches,
                "missing_definition_sheets": missing_definition_sheets,
                "missing_connection_controls": missing_connections,
                "hashes_ok": hashes_ok,
                "passed": passed,
            }
        )

    return {
        "schema": "org.opensourcerail.station-product-reconciliation.v1",
        "status": "design-reference-not-released",
        "scope": "bidirectional stable-ID closure across station manifest, BOM, traveler, definition register, FreeCAD states, and IFC4.3",
        "manifest": str(MANIFEST.relative_to(REPO_ROOT)),
        "manifest_sha256": _sha256(MANIFEST),
        "variant_count": len(results),
        "variants": results,
        "passed": len(results) == 7 and all(row["passed"] for row in results),
    }


def render_markdown(register: dict[str, object]) -> str:
    lines = [
        "# Station product reconciliation",
        "",
        "**Status:** " + ("PASS" if register["passed"] else "FAIL"),
        "",
        "This generated register proves stable identities in both directions across",
        "the station manifest, BOM, traveler, compact variant definition/drawing",
        "register, native FreeCAD installed/exploded states and IFC4.3 handoff.",
        "It proves configuration consistency, not construction readiness.",
        "",
        "| Variant | Products | Assemblies | Definition sheets | Connection controls | States | Result |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in register["variants"]:
        lines.append(
            f"| `{row['archetype']}` | {row['product_count']} | {row['assembly_count']} | "
            f"{row['definition_sheet_count']} | {row['connection_control_count']} | "
            f"{', '.join(row['configuration_states'])} | {'PASS' if row['passed'] else 'FAIL'} |"
        )
    lines.extend(
        [
            "",
            "A definition-sheet or connection-control identifier is a required",
            "deployment deliverable keyed to its product row. It is not evidence that",
            "a signed fabrication drawing, supplier data or site approval already exists.",
            "Those gates remain in the open-release register and each assembly traveler.",
            "",
        ]
    )
    return "\n".join(lines)


def write(json_path: Path = DEFAULT_JSON, markdown_path: Path = DEFAULT_MARKDOWN) -> dict[str, object]:
    register = build_register()
    json_path.write_text(json.dumps(register, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(register), encoding="utf-8")
    return register


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    register = write(args.json, args.markdown)
    print(json.dumps({"variant_count": register["variant_count"], "passed": register["passed"]}, indent=2))
    return 0 if register["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path

from osr_mech.buildable_stations import (
    DEFAULT_TEMPLATE,
    _template_archetypes,
    render_station_factory_release_packages,
    station_factory_release_payload,
    station_variant,
)
from osr_mech.common import StationArchetype
from osr_mech.station.factory_release import (
    render_station_release_readiness,
    station_product_release_path,
    station_release_packages,
    station_release_record_template,
)
from osr_mech.station.default_specifications import (
    default_product_specifications,
    default_specification_payload,
    reference_sources,
    render_default_specifications,
)


def _variants():
    configs = _template_archetypes(DEFAULT_TEMPLATE)
    return tuple(
        station_variant(archetype, configs[archetype.value])
        for archetype in StationArchetype
    )


def test_station_factory_packages_cover_every_unique_product_once() -> None:
    payload = station_factory_release_payload(_variants())
    assert payload["package_count"] == 9
    assert payload["controlled_product_count"] == 45
    assert payload["drawing_count"] == 18
    assert payload["release_path_counts"] == {
        "reusable-definition": 18,
        "supplier-configuration": 14,
        "deployment-specific": 13,
    }
    assert all(payload["validation"].values())
    assert all(package["product_rows"] for package in payload["packages"])
    assert sum(
        product["reference_default"].startswith("default-product-specifications.json::")
        for package in payload["packages"]
        for product in package["product_rows"]
    ) == 29


def test_release_paths_keep_site_and_supplier_authority_explicit() -> None:
    assert station_product_release_path("STN-CIV-P010") == "reusable-definition"
    assert station_product_release_path("STN-CNP-P030") == "supplier-configuration"
    assert station_product_release_path("STN-CNP-P070") == "deployment-specific"
    assert station_product_release_path("STN-DEP-P060") == "deployment-specific"
    boundaries = " ".join(package.release_boundary for package in station_release_packages()).lower()
    for required in ("does not release site", "utility", "structural approval", "do not authorize site works"):
        assert required in boundaries


def test_station_release_record_is_complete_but_unfilled() -> None:
    payload = station_factory_release_payload(_variants())
    record = station_release_record_template(payload)
    assert record["template_status"] == "unfilled-not-release-evidence"
    assert record["coverage"] == {
        "package_count": 9,
        "open_package_count": 9,
        "unique_drawing_count": 18,
        "controlled_product_count": 45,
        "unique_tooling_count": 22,
    }
    assert all(package["release_status"] == "open-unissued" for package in record["packages"])
    assert all(
        drawing["issue_status"] == "unissued" and not drawing["published_file_sha256"]
        for package in record["packages"]
        for drawing in package["drawing_records"]
    )
    assert all(
        verification["status"] == "not-performed"
        for package in record["packages"]
        for verification in package["verification_records"]
    )
    assert "Packages: **9**; open: **9**" in render_station_release_readiness(record)


def test_generated_station_factory_release_artifacts_are_current() -> None:
    variants = _variants()
    payload = station_factory_release_payload(variants)
    record = station_release_record_template(payload)
    root = Path(__file__).resolve().parents[1] / "catalog/buildable-stations"
    assert json.loads((root / "factory-release-work-packages.json").read_text()) == payload
    assert (root / "factory-release-work-packages.md").read_text() == render_station_factory_release_packages(variants)
    assert json.loads((root / "evidence/factory-release-record-template.json").read_text()) == record
    assert (root / "factory-release-readiness.md").read_text() == render_station_release_readiness(record)


def test_reference_defaults_cover_every_open_product_without_claiming_release() -> None:
    variants = _variants()
    products = {item.id: item for variant in variants for item in variant.product_items}
    open_ids = {product_id for product_id, item in products.items() if item.maturity != "release-candidate"}
    payload = default_specification_payload(open_ids)
    assert payload["default_count"] == 29
    assert set(open_ids) == {row.product_id for row in default_product_specifications()}
    assert all(payload["validation"].values())
    assert all(row.parameters and row.must_override_when for row in default_product_specifications())
    assert "not-procurement-or-construction-release" in payload["status"]
    assert set(reference_sources()) == {
        source
        for row in default_product_specifications()
        for source in row.source_ids
    }


def test_generated_reference_default_artifacts_are_current() -> None:
    variants = _variants()
    products = {item.id: item for variant in variants for item in variant.product_items}
    payload = default_specification_payload(
        {product_id for product_id, item in products.items() if item.maturity != "release-candidate"}
    )
    root = Path(__file__).resolve().parents[1] / "catalog/buildable-stations"
    assert json.loads((root / "default-product-specifications.json").read_text()) == payload
    assert (root / "default-product-specifications.md").read_text() == render_default_specifications(
        payload, {product_id: item.title for product_id, item in products.items()}
    )

from __future__ import annotations

import json
from pathlib import Path

from osr_mech.buildable_trainset import (
    buildable_trainset_design,
    factory_release_work_package_payload,
    render_factory_release_work_packages,
)
from osr_mech.common import ConsistFamily
from osr_mech.rolling_stock.factory_release import factory_release_packages


def test_factory_release_packages_cover_requested_dedicated_scope() -> None:
    packages = factory_release_packages()
    assert len(packages) == 10
    assert len({package.id for package in packages}) == len(packages)
    text = json.dumps([package.__dict__ for package in packages]).lower()
    for required in (
        "transverse structure",
        "one-metre exterior module",
        "front-glass carrier",
        "front-lamp cassette",
        "roof curb",
        "interior moulding",
        "service rail",
        "pre-cut exterior film",
        "radiative roof-coating",
        "field-rerailing",
    ):
        assert required in text


def test_factory_release_payload_is_bound_to_manifest_geometry_and_tooling() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    payload = factory_release_work_package_payload(design)
    assert payload["package_count"] == 10
    assert payload["controlled_product_count"] >= 50
    assert len(payload["tooling_ids"]) >= 20
    assert all(payload["validation"].values())
    assert all(package["product_rows"] for package in payload["packages"])
    assert all(
        len(row["design_reference_envelope_mm"]) == 3
        for package in payload["packages"]
        for row in package["product_rows"]
    )


def test_release_boundaries_preserve_safety_and_finish_fallbacks() -> None:
    boundaries = " ".join(package.release_boundary for package in factory_release_packages()).lower()
    assert "no steel cutting release" in boundaries
    assert "non-structural" in boundaries
    assert "photometric evidence remains mandatory" in boundaries
    assert "generic proof result cannot qualify every fixture" in boundaries
    assert "baseline qualified light roof finish remains available" in boundaries
    assert "automotive scissor jacks" in boundaries


def test_generated_factory_release_artifacts_are_current() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    root = Path(__file__).resolve().parents[1] / "catalog/buildable-trainset"
    payload = factory_release_work_package_payload(design)
    assert json.loads((root / "factory-release-work-packages.json").read_text(encoding="utf-8")) == payload
    assert (root / "factory-release-work-packages.md").read_text(encoding="utf-8") == render_factory_release_work_packages(design)


def test_first_article_rows_link_to_their_factory_drawing_packages() -> None:
    root = Path(__file__).resolve().parents[1] / "catalog/buildable-trainset"
    work = json.loads((root / "first-article-work-packages.json").read_text(encoding="utf-8"))
    assert work["schema_version"] == "1.2"
    assert work["factory_release_source"].endswith("factory-release-work-packages.json")
    rows = {row["engineering_id"]: row for row in work["work_packages"]}
    assert rows["LM3-FAS-P010"]["factory_release_package_ids"] == ["LM3-FRP-030"]
    assert rows["LM3-ROOF-P030"]["factory_release_package_ids"] == ["LM3-FRP-050", "LM3-FRP-090"]
    assert rows["LM3-FIN-P020"]["factory_release_package_ids"] == ["LM3-FRP-090"]
    assert rows["LM3-FIX-P030"]["factory_release_package_ids"] == ["LM3-FRP-070"]

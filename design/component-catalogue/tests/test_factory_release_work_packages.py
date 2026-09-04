from __future__ import annotations

import json
from pathlib import Path

from osr_mech.buildable_trainset import (
    buildable_trainset_design,
    factory_release_work_package_payload,
    render_factory_release_work_packages,
)
from osr_mech.common import ConsistFamily
from osr_mech.rolling_stock.factory_release import (
    factory_drawing_metadata,
    factory_drawing_seed_payloads,
    factory_release_packages,
    factory_release_record_template,
    render_factory_drawing_index,
    render_factory_drawing_seed,
    render_factory_release_readiness,
)


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


def test_factory_release_record_covers_every_package_without_claiming_release() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    work = factory_release_work_package_payload(design)
    record = factory_release_record_template(work)
    assert record["template_status"] == "unfilled-not-release-evidence"
    assert record["coverage"] == {
        "package_count": 10,
        "open_package_count": 10,
        "unique_drawing_count": 18,
        "controlled_product_count": 57,
        "unique_tooling_count": 23,
    }
    assert {row["package_id"] for row in record["packages"]} == {
        row["id"] for row in work["packages"]
    }
    assert {
        product["product_id"]
        for package in record["packages"]
        for product in package["product_configuration_records"]
    } == set(work["controlled_product_ids"])
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
    readiness = render_factory_release_readiness(record)
    assert "Packages: **10**; open: **10**" in readiness
    assert "unfilled" in readiness


def test_factory_drawing_seeds_bind_all_drawing_ids_products_and_shared_ownership() -> None:
    design = buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)
    work = factory_release_work_package_payload(design)
    seeds = factory_drawing_seed_payloads(work)
    assert len(seeds) == 18
    assert {seed["drawing_id"] for seed in seeds} == {
        row.id for row in factory_drawing_metadata()
    }
    assert {
        product["id"] for seed in seeds for product in seed["product_rows"]
    } == set(work["controlled_product_ids"])
    assert all(seed["issue_status"] == "definition-seed-not-issued" for seed in seeds)
    assert all(seed["required_views"] for seed in seeds)
    assert all(seed["mandatory_drawing_controls"] for seed in seeds)
    assert all(seed["product_rows"] for seed in seeds)

    by_id = {seed["drawing_id"]: seed for seed in seeds}
    assert by_id["LM3-BDY-100"]["package_ids"] == ["LM3-FRP-010", "LM3-FRP-100"]
    assert "LM3-BDY-P120" in {
        product["id"] for product in by_id["LM3-BDY-100"]["product_rows"]
    }
    assert "panoramic glass" in by_id["LM3-FAS-180"]["title"]
    assert "not a dimensioned production drawing" in by_id["LM3-REC-270"]["release_boundary"]
    assert "definition seeds; none issued" in render_factory_drawing_index(seeds)
    assert "## Controlled product scope" in render_factory_drawing_seed(by_id["LM3-HV-325"])


def test_first_article_rows_link_to_their_factory_drawing_packages() -> None:
    root = Path(__file__).resolve().parents[1] / "catalog/buildable-trainset"
    work = json.loads((root / "first-article-work-packages.json").read_text(encoding="utf-8"))
    assert work["schema_version"] == "1.3"
    assert work["factory_release_source"].endswith("factory-release-work-packages.json")
    assert work["mass_closure_source"].endswith("mass-closure-ledger.json")
    assert all(row["mass_responsibility_category"] for row in work["work_packages"])
    assert {row["mass_evidence_status"] for row in work["work_packages"]} <= {
        "unclosed-evidence-required",
        "inactive-option-not-weighed",
    }
    assert any(row["mass_evidence_status"] == "unclosed-evidence-required" for row in work["work_packages"])
    rows = {row["engineering_id"]: row for row in work["work_packages"]}
    assert rows["LM3-FAS-P010"]["factory_release_package_ids"] == ["LM3-FRP-030"]
    assert rows["LM3-ROOF-P030"]["factory_release_package_ids"] == ["LM3-FRP-050", "LM3-FRP-090"]
    assert rows["LM3-FIN-P020"]["factory_release_package_ids"] == ["LM3-FRP-090"]
    assert rows["LM3-FIX-P030"]["factory_release_package_ids"] == ["LM3-FRP-070"]

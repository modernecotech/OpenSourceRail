from __future__ import annotations

import json
from pathlib import Path

from osr_mech.buildable_trainset import (
    Route,
    buildable_trainset_design,
    factory_release_work_package_payload,
)
from osr_mech.common import ConsistFamily
from osr_mech.rolling_stock.default_specifications import (
    default_product_specifications,
    default_specification_payload,
    render_default_specifications,
)


def _design():
    return buildable_trainset_design(ConsistFamily.LIGHT_METRO_3CAR)


def test_reference_defaults_cover_every_bought_in_product_once() -> None:
    design = _design()
    expected = {item.id for item in design.product_items if item.route is not Route.MAKE}
    rows = default_product_specifications(design.product_items)
    payload = default_specification_payload(design.product_items)
    assert len(rows) == 58
    assert {row.product_id for row in rows} == expected
    assert payload["route_counts"] == {"BID": 34, "SOURCE": 24}
    assert payload["source_count"] == 41
    assert all(payload["validation"].values())
    assert all(row.public_parameters for row in rows)
    assert all(row.must_close_before_freeze and row.must_override_when for row in rows)
    assert all(len(row.design_reference_envelope_mm) == 3 for row in rows)


def test_defaults_preserve_safe_finish_and_charging_boundaries() -> None:
    rows = {row.product_id: row for row in default_product_specifications(_design().product_items)}
    assert rows["LM3-FIN-P020"].use_class == (
        "trial-only-reference-not-an-orderable-fleet-product"
    )
    assert "qualified light-colour base" in rows["LM3-FIN-P020"].default_name
    assert rows["LM3-TRC-P060"].use_class == "interface-rfq-default-not-selected"
    assert "supplier-neutral" in rows["LM3-TRC-P060"].default_name


def test_factory_packages_link_every_controlled_bought_in_row_to_defaults() -> None:
    payload = factory_release_work_package_payload(_design())
    assert payload["validation"]["all_controlled_bought_in_rows_link_reference_defaults"]
    bought_in = [
        row
        for package in payload["packages"]
        for row in package["product_rows"]
        if row["route"] != "MAKE"
    ]
    assert bought_in
    assert all(
        row["reference_default"]
        == f"default-product-specifications.json::{row['id']}"
        for row in bought_in
    )


def test_generated_trainset_reference_default_artifacts_are_current() -> None:
    design = _design()
    payload = default_specification_payload(design.product_items)
    root = Path(__file__).resolve().parents[1] / "catalog/buildable-trainset"
    assert json.loads((root / "default-product-specifications.json").read_text()) == payload
    assert (root / "default-product-specifications.md").read_text() == render_default_specifications(
        payload,
        {item.id: item.title for item in design.product_items},
    )

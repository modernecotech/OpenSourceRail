"""Whole-inventory coverage, stale imports and non-promotion of research results."""

from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile

import pytest

from engineering.generative_design import campaign, coverage, coupling, review


def test_every_authoritative_id_is_assigned_and_omissions_fail():
    scope = campaign.scope()
    result = coverage.audit(scope)
    assert result["work_package_count"] == 63
    assert any(
        i["collection"] == "product_items" and i["count"] == 120
        for i in result["inventories"]
    )
    inventory = next(
        i
        for i in scope["source_inventory"]
        if i["path"].endswith("buildable-trainset-manifest.json")
    )
    missing = next(
        c
        for c in inventory["inventory_collections"]
        if c["collection"] == "product_items"
    )["expected_ids"][0]
    for package in scope["work_packages"]:
        for source in package["authoritative_sources"]:
            if source["path"] == inventory["path"]:
                source["ids"] = [i for i in source["ids"] if i != missing]
    with pytest.raises(ValueError, match="unassigned source IDs"):
        coverage.audit(scope)


def test_dependency_cycles_and_release_flags_fail_scope_audit():
    scope = campaign.scope()
    scope["work_packages"][0]["dependencies"] = [scope["work_packages"][0]["id"]]
    with pytest.raises(ValueError, match="self-dependent"):
        coverage.audit(scope)
    scope = campaign.scope()
    scope["work_packages"][0]["physical_release"] = True
    with pytest.raises(ValueError, match="cannot grant"):
        coverage.audit(scope)


def test_representative_success_cannot_close_parent_system():
    scope = campaign.scope()
    lanes = {
        name: dict(selected_candidate_ids=["conditionally-passed-part"])
        for name in ("civil", "mechanical")
    }
    result = coverage.ledger(scope, lanes, {})
    assert len(result["work_packages"]) == 63
    assert result["completed_packages"] == 0
    assert result["all_systems_design_complete"] is False
    assert all(
        not p["design_complete"] and not p["manufacturing_release"]
        for p in result["work_packages"]
    )
    assert result["counts"]["requires-discipline-model"] > 0


def test_same_length_duplicate_or_replaced_ledger_ids_cannot_hide_work():
    value = campaign.scope()
    closure = coverage.ledger(value, {}, {})
    coverage.validate_ledger(value, closure)
    closure["work_packages"][1]["id"] = closure["work_packages"][0]["id"]
    with pytest.raises(ValueError, match="package IDs differ"):
        coverage.validate_ledger(value, closure)
    closure = coverage.ledger(value, {}, {})
    closure["work_packages"][0]["id"] = "UNINVENTORIED"
    with pytest.raises(ValueError, match="package IDs differ"):
        coverage.validate_ledger(value, closure)
    closure = coverage.ledger(value, {}, {})
    closure["work_packages"][0]["required_gates"]["manufacturing"] = []
    with pytest.raises(ValueError, match="changed mandatory"):
        coverage.validate_ledger(campaign.scope(), closure)


def test_variations_preserve_declared_function_and_vary_one_coordinate():
    from engineering.design_engine.registry import get
    from engineering.design_engine.contracts import variables

    charter = get("battery-installation")
    original = deepcopy(charter)
    rows = campaign.variations(charter)
    assert len(rows) == 4 and charter == original
    assert len({json.dumps(r, sort_keys=True) for r in rows}) == 4
    for row in rows:
        variables(charter, row)
        assert sum(row[k] != rows[0][k] for k in row) <= 1


def test_import_rejects_stale_sources_tools_and_altered_function():
    from engineering.design_engine.runtime import request
    from engineering.design_engine.contracts import identity, SCHEMA

    context = identity(
        dict(
            schema=SCHEMA,
            city="baghdad",
            project="baghdad",
            environment="simulation",
            configuration_revision="test",
            baseline_sha256=None,
            run_id=None,
            asset_id=None,
            part_id=None,
        )
    )
    req = request("mechanical-cleat", context)
    campaign.validate_common_request(req)
    for field in ("dependencies", "toolchain"):
        changed = deepcopy(req)
        changed[field] = {}
        with pytest.raises(ValueError, match="source/toolchain is stale"):
            campaign.validate_common_request(changed)
    changed = deepcopy(req)
    changed["problem"]["applicability"]["function"] += " altered"
    with pytest.raises(ValueError, match="function/charter differs"):
        campaign.validate_common_request(changed)


def test_raised_beam_force_propagates_to_both_return_rails_and_stays_unqualified():
    report = dict(
        selected_candidate_ids=["beam-A"],
        candidates=[dict(id="beam-A", metrics=dict(initial_bed_force_n=14.784e6))],
    )
    result = coupling.search(report)
    assert len(result["candidates"]) == 9
    assert all(
        r["per_rail_compression_n"] == pytest.approx(7.392e6)
        for r in result["candidates"]
    )
    assert any(
        r["checks"]["gross_elastic_stability"]["state"] == "failed"
        for r in result["candidates"]
    )
    assert any(
        r["checks"]["gross_elastic_stability"]["state"] == "passed"
        for r in result["candidates"]
    )
    assert all(
        r["accepted_rail_resistance_n"] is None and not r["complete_bed_qualified"]
        for r in result["candidates"]
    )
    for t in (0.016, 0.020, 0.025):
        factors = [
            r["minimum_elastic_eigenvalue_factor"]
            for r in result["candidates"]
            if r["variables"]["wall_m"] == t
        ]
        assert factors == sorted(factors)


@pytest.fixture
def small_campaign():
    folder = coverage.ROOT / "build/generative-tests"
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=folder) as parent:
        output = Path(parent) / "run"
        campaign.run(output, civil_budget=1, mechanical_budget=1, common="none")
        yield output


def test_complete_receipt_detects_extra_and_changed_artifacts(small_campaign):
    assert campaign.verify(small_campaign)["integrity_verified"]
    p = small_campaign / "foreign.json"
    p.write_text("{}")
    with pytest.raises(ValueError, match="membership differs"):
        campaign.verify(small_campaign)
    p.unlink()
    p = small_campaign / "civil/search.json"
    p.write_text("{}")
    with pytest.raises(ValueError, match="artifact changed"):
        campaign.verify(small_campaign)


def test_resealed_summary_cannot_promote_numerics_into_design_release(small_campaign):
    p = small_campaign / "summary.json"
    result = json.loads(p.read_text())
    result["all_systems_design_complete"] = True
    campaign.write(p, result)
    p = small_campaign / "receipt.json"
    receipt = json.loads(p.read_text())
    receipt["files_sha256"]["summary.json"] = coverage.sha(
        small_campaign / "summary.json"
    )
    campaign.write(p, receipt)
    with pytest.raises(ValueError, match="cannot grant"):
        campaign.verify(small_campaign)


def test_native_failure_is_retained_and_civil_model_records_are_normalized(monkeypatch):
    from engineering.factory_examples import native

    def failed(*args):
        raise RuntimeError("controlled native holdout failure")

    monkeypatch.setattr(native, "generate", failed)
    folder = coverage.ROOT / "build/generative-tests"
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=folder) as parent:
        output = Path(parent) / "run"
        result = campaign.run(
            output, civil_budget=128, mechanical_budget=128, native=True, common="none"
        )
        assert result["native_geometry_failed"] == 4
        assert result["native_geometry_passed"] == 0
        assert result["all_systems_design_complete"] is False
        assert all(
            r["status"] == "failed"
            for r in json.loads((output / "summary.json").read_text())[
                "native_geometry"
            ]
        )

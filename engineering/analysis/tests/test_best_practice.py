"""Research completeness must not hide new scope, stale evidence or acceptance gaps."""
from copy import deepcopy
import csv
from datetime import date
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from engineering.best_practice.register import (
    DATA, FIELDS, OUTPUTS, assurance_links, build, check, contained, inventory, load, validate,
)

AS_OF = date(2026, 10, 11)


@pytest.fixture(scope="module")
def baseline():
    sources = load(ROOT, DATA / "sources.json")
    practices = load(ROOT, DATA / "practices.json")
    scope = load(ROOT, DATA / "scope.json")
    return sources, practices, scope, inventory(ROOT, scope)


@pytest.fixture
def checkout(tmp_path):
    """Only named source inputs and public outputs; no caches or repo history."""
    paths = set(load(ROOT, OUTPUTS["coverage.json"])["source_sha256"])
    paths.update(str(path) for path in OUTPUTS.values())
    for relative in paths:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    return tmp_path


def test_all_catalogue_system_and_software_definitions_have_explicit_guidance(baseline):
    result = check(ROOT, AS_OF)
    assert result["inventory_count"] == result["mapped_count"] == 356
    assert result["inventory_by_kind"] == {
        "train-product": 120, "train-assembly": 26, "civil-type": 19,
        "station-product": 50, "station-assembly": 10, "station-system": 7,
        "software-package": 60, "subsystem-template": 64,
    }
    assert result["practice_count"] == 54 and result["source_count"] == 73
    assert result["documentation_coverage_complete"]
    assert not result["engineering_accepted"] and not result["production_released"]
    assert not result["physical_validation"] and not result["all_possible_rail_components_covered"]
    _, practices, assignments, overdue = validate(*baseline, AS_OF)
    assert not overdue
    assert all(set(ids) - set(baseline[1]["common_practices"]) for ids in assignments.values())
    assert set(assurance_links(ROOT, practices)["practice_control_ids"]) == set(practices)


def test_optional_configuration_and_all_station_variants_are_preserved(baseline):
    items = {item["id"]: item for item in baseline[3]}
    assert items["LM3-ART-P040"]["applicability"][0]["quantity"] == 0
    platform = items["STN-CIV-P010"]["applicability"]
    assert len(platform) == 7
    assert len({entry["title"] for entry in platform}) > 1
    assert all(entry["quantity"] > 0 and entry["unit"] for entry in platform)
    assert "not a structural product" in items["OSR-TYPE-239C28547990"]["title"]
    assert len([item for item in items.values() if item["kind"] == "software-package"]) == 60


def test_verification_is_allocated_but_unperformed_with_no_invented_limits():
    outputs = build(ROOT, AS_OF)
    plan = json.loads(outputs["verification-plan.json"])
    assert len(plan["task_definitions"]) == 108
    assert len(plan["allocations"]) == 356
    assert len(plan["research_backlog"]) == 54
    for task in plan["task_definitions"]:
        assert task["status"] == "open-unperformed"
        assert task["acceptance_criteria"] is task["procedure"] is task["result"] is None
        assert task["adopted_standard_clauses"] == task["evidence"] == []
        assert task["assurance_control_ids"]
    rows = list(csv.DictReader(io.StringIO(outputs["component-guidance.csv"])))
    assert {row["id"] for row in rows} == {row["item_id"] for row in plan["allocations"]}
    assert all(row["source_ids"] and row["assurance_control_ids"] for row in rows)
    assert all(row["evidence_status"] == "project-adoption-and-physical-evidence-open" for row in rows)
    assert build(ROOT, AS_OF) == outputs


def test_new_product_has_no_silent_family_or_keyword_fallback(baseline):
    inputs = deepcopy(baseline)
    inputs[3].append(dict(id="LM3-BOG-P999", kind="train-product", title="new bearing kit"))
    with pytest.raises(ValueError, match="unmapped=.*LM3-BOG-P999"):
        validate(*inputs, AS_OF)


def test_new_rust_package_requires_explicit_subsystem_guidance(checkout):
    workspace = checkout / "Cargo.toml"
    workspace.write_text(workspace.read_text().replace("members = [", 'members = [\n    "crates/new-controller",', 1))
    manifest = checkout / "crates/new-controller/Cargo.toml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text('[package]\nname = "new-controller"\nversion = "0.0.1"\n')
    with pytest.raises(ValueError, match="unmapped=.*software:new-controller"):
        build(checkout, AS_OF)


@pytest.mark.parametrize("change", ["new", "deleted", "both", "empty-reason"])
def test_template_scope_changes_cannot_hide_in_cost_or_configuration_files(checkout, change):
    scope_path = checkout / DATA / "scope.json"
    scope = json.loads(scope_path.read_text())
    if change == "new":
        (checkout / "lib/templates/new-pump.toml").write_text('purpose="new pump"\n')
    elif change == "deleted":
        (checkout / "lib/templates/track-geometry.toml").unlink()
    elif change == "both":
        scope["template_exclusions"]["rolling-stock.toml"] = "Excluded"
    else:
        scope["template_exclusions"]["capex-costs.toml"] = ""
    scope_path.write_text(json.dumps(scope))
    with pytest.raises(ValueError, match="template"):
        build(checkout, AS_OF)


@pytest.mark.parametrize("defect", ["stale-mapping", "unknown-practice", "only-common", "duplicate-practice", "empty"])
def test_product_mappings_must_be_current_specific_and_unambiguous(baseline, defect):
    inputs = deepcopy(baseline)
    assignments = inputs[2]["assignments"]
    if defect == "stale-mapping":
        assignments["retired-missing-product"] = ["carbody"]
    elif defect == "unknown-practice":
        assignments["LM3-BDY-P010"] = ["unknown"]
    elif defect == "only-common":
        assignments["LM3-BDY-P010"] = ["configuration"]
    elif defect == "duplicate-practice":
        assignments["LM3-BDY-P010"] = ["carbody", "carbody"]
    else:
        assignments["LM3-BDY-P010"] = []
    with pytest.raises(ValueError):
        validate(*inputs, AS_OF)


@pytest.mark.parametrize("field", [*FIELDS, "owner_role", "source_ids"])
def test_a_card_cannot_drop_a_lifecycle_stage_owner_or_source(baseline, field):
    inputs = deepcopy(baseline)
    inputs[1]["practices"][0][field] = [] if field != "owner_role" else ""
    with pytest.raises(ValueError, match="practice"):
        validate(*inputs, AS_OF)


@pytest.mark.parametrize("defect", ["unknown-source", "duplicate-source", "empty-limit", "bad-url", "bad-kind", "future-review", "clause-claim"])
def test_source_discovery_needs_provenance_limitations_and_honest_status(baseline, defect):
    inputs = deepcopy(baseline)
    source = inputs[0]["sources"][0]
    if defect == "unknown-source":
        inputs[1]["practices"][0]["source_ids"] = ["invented-source"]
    elif defect == "duplicate-source":
        inputs[0]["sources"].append(deepcopy(source))
    elif defect == "empty-limit":
        source["limitation"] = ""
    elif defect == "bad-url":
        source["url"] = "javascript:alert(1)"
    elif defect == "bad-kind":
        source["kind"] = "certification"
    elif defect == "future-review":
        source["reviewed_on"] = "2026-10-12"
    else:
        source["full_clause_review"] = True
    with pytest.raises(ValueError):
        validate(*inputs, AS_OF)


@pytest.mark.parametrize("flag", ["engineering_accepted", "physical_validation"])
def test_research_cannot_be_promoted_into_acceptance(baseline, flag):
    inputs = deepcopy(baseline)
    inputs[1][flag] = True
    with pytest.raises(ValueError, match=flag):
        validate(*inputs, AS_OF)


def test_source_expiry_is_visible_and_fails_a_current_review():
    later = date(2027, 1, 10)
    report = json.loads(build(ROOT, later)["coverage.json"])
    overdue = {row["source_id"] for row in report["source_refresh_required"]}
    assert "era-locpas" in overdue and "fta-safety" in overdue
    assert "iec-rams" not in overdue and "nasa-systems" not in overdue
    assert not report["research_refresh_current"]
    with pytest.raises(ValueError, match="source refresh required"):
        check(ROOT, later)


@pytest.mark.parametrize("change", ["catalogue-byte", "template-byte", "handbook-byte", "missing-output"])
def test_changed_sources_or_published_outputs_require_regeneration(checkout, change):
    check(checkout, AS_OF)
    if change == "catalogue-byte":
        path = checkout / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
        path.write_text(path.read_text() + "\n")
    elif change == "template-byte":
        path = checkout / "lib/templates/rolling-stock.toml"
        path.write_text(path.read_text() + "\n# reviewed input changed\n")
    elif change == "handbook-byte":
        path = checkout / OUTPUTS["handbook.md"]
        path.write_text(path.read_text() + "Unreviewed change.\n")
    else:
        (checkout / OUTPUTS["component-guidance.csv"]).unlink()
    with pytest.raises(ValueError, match="stale generated"):
        check(checkout, AS_OF)


def test_deleted_or_unknown_assurance_objective_cannot_break_the_existing_thread(checkout):
    path = checkout / DATA / "assurance-links.json"
    document = json.loads(path.read_text())
    document["practice_control_ids"]["braking"] = ["STD-CTRL-NOT-DEFINED"]
    path.write_text(json.dumps(document))
    with pytest.raises(ValueError, match="unknown existing assurance control"):
        build(checkout, AS_OF)


def test_paths_and_duplicate_json_keys_cannot_hide_source_ambiguity(tmp_path):
    for path in ("../other.json", str(tmp_path / "absolute.json")):
        with pytest.raises(ValueError, match="repository relative"):
            contained(tmp_path, path)
    (tmp_path / "duplicate.json").write_text('{"accepted":false,"accepted":true}')
    with pytest.raises(ValueError, match="duplicate JSON key"):
        load(tmp_path, "duplicate.json")


def test_cli_requires_an_explicit_assessment_date():
    tool = ROOT / "tools/automation/best-practice.py"
    missing = subprocess.run([sys.executable, str(tool), "check"], capture_output=True, text=True)
    assert missing.returncode != 0 and "--as-of" in missing.stderr
    valid = subprocess.run([sys.executable, str(tool), "check", "--as-of", AS_OF.isoformat()],
                           capture_output=True, text=True)
    assert valid.returncode == 0, valid.stderr
    assert json.loads(valid.stdout)["physical_validation"] is False


def test_current_source_review_does_not_rewrite_the_historical_publication():
    tool = ROOT / "tools/automation/best-practice.py"
    before = {name: (ROOT / path).read_bytes() for name, path in OUTPUTS.items()}
    valid = subprocess.run([sys.executable, str(tool), "review-sources", "--as-of", "2026-10-12"],
                           capture_output=True, text=True)
    assert valid.returncode == 0, valid.stderr
    assert json.loads(valid.stdout)["assessed_on"] == "2026-10-12"
    expired = subprocess.run([sys.executable, str(tool), "review-sources", "--as-of", "2027-01-10"],
                             capture_output=True, text=True)
    assert expired.returncode != 0 and "source refresh required" in expired.stderr
    assert {name: (ROOT / path).read_bytes() for name, path in OUTPUTS.items()} == before

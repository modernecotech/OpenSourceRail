"""CLI launch, local storage and bounded sourcing command contracts."""
import json
import gzip
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from engineering.sourcing import cli
from engineering.sourcing.model import identity, record


def test_default_database_is_under_xdg_state_and_outside_checkout(tmp_path):
    state = tmp_path / "state"
    path = cli.default_database_path({"XDG_STATE_HOME": str(state)}, home=tmp_path)
    assert path == state / "opensourcerail" / "sourcing" / "sourcing.sqlite3"
    assert not path.is_relative_to(cli.ROOT)


def test_default_database_falls_back_to_user_state(tmp_path):
    path = cli.default_database_path({}, home=tmp_path)
    assert path == tmp_path / ".local" / "state" / "opensourcerail" / "sourcing" / "sourcing.sqlite3"


def test_raw_feed_cache_defaults_to_outside_checkout_xdg_data(tmp_path):
    data = tmp_path / "xdg-data"
    path = cli.default_raw_cache_path({"XDG_DATA_HOME": str(data)}, home=tmp_path)
    assert path == data / "opensourcerail" / "sourcing" / "raw-feeds"
    assert not path.is_relative_to(cli.ROOT)


def test_parser_accepts_review_commands_and_bounded_run_inputs(tmp_path):
    run = cli._parser().parse_args([
        "--database", str(tmp_path / "records.sqlite3"), "run",
        "--input", str(tmp_path / "bom.json"), "--member", "inventory.json",
        "--as-of", "2026-10-29", "--output", str(tmp_path / "packet"),
        "--bindings", str(tmp_path / "bindings.json"), "--max-requirements", "12",
    ])
    assert run.command == "run"
    assert run.member == "inventory.json"
    assert run.max_requirements == 12
    assert run.database == tmp_path / "records.sqlite3"
    assert cli._parser().parse_args(["rfq", "export", "a" * 64, "--output", str(tmp_path / "draft.json")]).rfq_command == "export"
    packages = cli._parser().parse_args([
        "procurement-bom", "--input", str(tmp_path / "twin.tar.gz"),
        "--concrete-material-recipe", str(tmp_path / "concrete-material-recipe.json"),
        "--output", str(tmp_path / "procurement.json.gz"),
    ])
    assert packages.concrete_material_recipe == tmp_path / "concrete-material-recipe.json"
    refresh = cli._parser().parse_args(["refresh", "--cache-dir", str(tmp_path / "cache")])
    assert refresh.command == "refresh"
    assert refresh.cache_dir == tmp_path / "cache"
    study = cli._parser().parse_args(["study", "laminate", "--input", str(tmp_path / "twin.tar.gz"),
        "--member", "federated-bom.json.gz", "--as-of", "2026-10-29", "--output", str(tmp_path / "studies"),
        "--product-observation", "GURIT-CORECELL-M80=" + "c" * 64])
    assert study.command == "study" and study.study_command == "laminate"
    assert study.member == "federated-bom.json.gz"
    direct_study = cli._parser().parse_args(["study", "laminate", "--input", str(tmp_path / "twin.json.gz"),
                                             "--as-of", "2026-10-30", "--output", str(tmp_path / "studies")])
    assert direct_study.member is None
    assert cli._parse_product_observations(study.product_observation) == {"GURIT-CORECELL-M80": "c" * 64}
    for values in (["not-a-selection"], ["GURIT-CORECELL-M80=bad"],
                   ["GURIT-CORECELL-M80=" + "c" * 64, "GURIT-CORECELL-M80=" + "d" * 64]):
        with pytest.raises(ValueError):
            cli._parse_product_observations(values)


def test_repeated_category_budgets_are_distinct_positive_and_exclusive_with_total():
    assert cli._parse_category_budgets(["propulsion=12", "civil=7"]) == {"propulsion": 12, "civil": 7}
    for values, total in ((["civil=7", "civil=9"], None), (["body-materials=0"], None),
                          (["running-gear=-1"], None), (["not-a-budget"], None),
                          (["propulsion=2"], 10)):
        with pytest.raises(ValueError):
            cli._parse_category_budgets(values, total)


def test_init_uses_default_xdg_database_outside_checkout(tmp_path, monkeypatch, capsys):
    state = tmp_path / "xdg-state"
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    assert cli.main(["init"]) == 0
    result = json.loads(capsys.readouterr().out)
    path = Path(result["database"])
    assert result["initialized"] is True
    assert result["outside_checkout"] is True
    assert path.is_file()
    assert path.is_relative_to(state)


def test_status_on_missing_database_does_not_create_it(tmp_path, capsys):
    path = tmp_path / "missing" / "sourcing.sqlite3"
    assert cli.main(["--database", str(path), "status"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["recent_runs"] == []
    assert all(count == 0 for count in result["counts"].values())
    assert not path.exists()


def test_gfrp_regional_estimate_cli_needs_no_database_and_reports_all_scenarios(tmp_path, capsys):
    packet_root = cli.ROOT / "docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v18"
    output = tmp_path / "gfrp-regional.json"
    assert cli.main(["estimate", "gfrp-laminate", "--packet-root", str(packet_root),
                     "--output", str(output)]) == 0
    result = json.loads(capsys.readouterr().out)
    packet = json.loads(output.read_text())
    assert result["regional_scenarios"] == 135
    assert result["regional_governorate_count"] == 15
    assert packet["schema"] == "osr-iraq-gfrp-local-fabrication-cost-screens/2"
    assert packet["complete_fabrication_cost_iqd"] is None


def test_procurement_bom_cli_links_regional_2026_concrete_scenarios(tmp_path, capsys):
    source_input = cli.ROOT / "docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v6/input.json.gz"
    reference = cli.ROOT / "docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-july-v2/iraq-domestic-cost-reference-2026-07.json"
    output = tmp_path / "procurement-bom.json.gz"
    assert cli.main(["procurement-bom", "--input", str(source_input),
                     "--regional-cost-reference", str(reference), "--output", str(output)]) == 0
    result = json.loads(capsys.readouterr().out)
    packet = json.loads(gzip.decompress(output.read_bytes()))
    assert result["packages_with_domestic_cost_estimates"] == 81
    assert result["domestic_cost_estimate_scenario_count"] == 486
    assert result["complete_installed_bom"] is False
    concrete = [row for row in packet["packages"]
                if row["package_family"] == "civil-concrete-stock-package"]
    assert len(concrete) == 81
    assert all(len(row["domestic_cost_estimate_scenarios"]) == 6 for row in concrete)
    assert {scenario["region"] for row in concrete
            for scenario in row["domestic_cost_estimate_scenarios"]} == {"Baghdad", "Al-Muthanna"}


def test_procurement_bom_cli_attaches_ingredient_quantities_to_exact_september_span_packages(tmp_path, capsys):
    source_input = cli.ROOT / "docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v6/input.json.gz"
    reference = cli.ROOT / "docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-september-v6/iraq-domestic-cost-reference-2026-09.json"
    recipe = cli.ROOT / "docs/design-engine/sourcing/domestic-fabrication/takeoff-recipes/concrete-material-inputs-2026-09.json"
    output = tmp_path / "procurement-bom-with-concrete-material-inputs.json.gz"
    assert cli.main(["procurement-bom", "--input", str(source_input),
                     "--regional-cost-reference", str(reference),
                     "--concrete-material-recipe", str(recipe),
                     "--output", str(output)]) == 0
    result = json.loads(capsys.readouterr().out)
    packet = json.loads(gzip.decompress(output.read_bytes()))
    takeoff = packet["concrete_material_input_takeoff"]
    concrete = [row for row in packet["packages"]
                if row["package_family"] == "civil-concrete-stock-package"]

    assert result["concrete_material_input_takeoff_package_count"] == 81
    assert result["concrete_material_input_takeoff_line_count"] == 243
    assert packet["source_registry_record_count"] == 94
    assert takeoff["candidate_id"] == packet["candidate_id"]
    assert takeoff["source_input_id"] == packet["source_input_id"]
    assert takeoff["package_count"] == 81
    assert takeoff["manufacturing_group_count"] == 81
    assert takeoff["engineering_occurrence_count"] == 486
    assert float(takeoff["nominal_output_volume_m3"]) == pytest.approx(1804.8096, abs=1e-9)
    assert [float(row["total_recipe_input_quantity"]) for row in takeoff["material_inputs"]] == pytest.approx(
        [631.68336, 902.4048, 1443.84768], abs=1e-9)
    assert [float(row["material_extension_iqd"]) for row in takeoff["material_inputs"]] == pytest.approx(
        [83382203.52, 18950500.8, 34652344.32], abs=1e-6)
    assert sum(float(row["material_extension_iqd"]) for row in takeoff["material_inputs"]) == pytest.approx(136985048.64)
    assert takeoff["non_additive_to_output_concrete_stock"] is True
    assert takeoff["ingredient_quantities_are_commercial_order_quantities"] is False
    assert takeoff["conversion_yield_fraction"] is None
    assert takeoff["complete_process_cost"] is None
    assert takeoff["complete_installed_cost"] is None
    assert packet["located_stock_occurrence_count"] == 27216
    assert packet["unlocated_obligation_count"] == 4773
    assert len(packet["material_purchasing_lines"]) == 8
    assert all(len(row["manufacturing_input_takeoff"]["material_inputs"]) == 3
               for row in concrete)
    assert all(row["manufacturing_input_takeoff"]["material_cost_reconciles_to_existing_cost_scenarios"] is True
               for row in concrete)
    assert all(line["commercial_order_quantity"] is None
               and line["purchase_yield_fraction"] is None
               and line["supplier_product_match"] is False
               for row in concrete
               for line in row["manufacturing_input_takeoff"]["material_inputs"])
    concrete_line = next(row for row in packet["material_purchasing_lines"]
                         if row["system"] == "civil/concrete")
    assert {row["source_key"] for row in concrete_line["domestic_fabrication_lead_sources"]} >= {
        "iraq.regaasphalt.aggregate", "iraq.hewa.construction-materials"}
    assert concrete_line["domestic_fabrication_leads_are_supplier_matches"] is False


def test_run_verify_show_and_rfq_export_are_local_disabled_review_steps(tmp_path, capsys):
    candidate = "a" * 64
    requirement = record("requirement", candidate_id=candidate, input_id="b" * 64,
        namespace="fixture-vehicle", requirement_key="bogie-account",
        description="Unresolved complete-bogie account", category="running-gear",
        priority=4, quantity=None, quantity_unit=None, occurrence_ids=[],
        physical_scopes=[], procurement_scope="complete-bogie", identifiers={}, constraints=[])
    payload = dict(schema="osr-sourcing-declared-requirements/1", candidate_id=candidate,
                   requirements=[requirement])
    source = tmp_path / "bom.json"
    source.write_text(json.dumps(payload))
    database = tmp_path / "state" / "sourcing.sqlite3"
    packet = tmp_path / "packet"

    assert cli.main(["--database", str(database), "init"]) == 0
    capsys.readouterr()
    assert cli.main(["--database", str(database), "run", "--input", str(source),
                     "--as-of", "2026-10-29", "--output", str(packet),
                     "--max-requirements", "1"]) == 0
    run_output = json.loads(capsys.readouterr().out)
    run_id = run_output["manifest"]["run_id"]
    assert run_output["summary"]["summary"]["unknown_quantity_requirements"] == 1
    assert run_output["summary"]["complete_installed_cost"] is None
    assert run_output["vehicle_only_input_is_not_infrastructure_coverage"] is True

    assert cli.main(["verify", str(packet)]) == 0
    assert json.loads(capsys.readouterr().out)["semantic_replay_executed"] is True
    assert cli.main(["--database", str(database), "show", run_id]) == 0
    show = json.loads(capsys.readouterr().out)
    assert show["rfq_draft_status"]["enabled"] is False
    assert show["complete_whole_life_cost"] is None

    draft = tmp_path / "rfq-review.json"
    assert cli.main(["--database", str(database), "rfq", "export", run_id,
                     "--output", str(draft)]) == 0
    export = json.loads(capsys.readouterr().out)
    saved = json.loads(draft.read_text())
    assert export["draft_count"] == 1
    assert saved["send_supplier_emails"] is False
    assert saved["procurement_authorized"] is False
    assert saved["drafts"][0]["submission_allowed"] is False


def test_run_passes_category_budgets_to_the_evaluation_request(tmp_path, monkeypatch, capsys):
    import engineering.sourcing.publication as publication

    database = tmp_path / "state.sqlite3"
    source = tmp_path / "input.json"
    source.write_text(json.dumps({"schema": "fixture/1"}))
    captured = {}
    monkeypatch.setattr(publication, "execute", lambda store, twin, request, root: captured.update(request=request) or {"record_id": "x"})
    monkeypatch.setattr(publication, "publish", lambda store, result, twin, request, output, root: {"publication_id": "y"})
    monkeypatch.setattr(publication, "summary", lambda store, result: {"summary": {"requirement_count": 0}})
    result = cli.main(["--database", str(database), "run", "--input", str(source),
        "--as-of", "2026-10-29", "--output", str(tmp_path / "packet"),
        "--category-budget", "propulsion=2", "--category-budget", "civil=1"])
    assert result == 0
    capsys.readouterr()
    assert captured["request"]["max_requirements_by_category"] == {"propulsion": 2, "civil": 1}
    assert "max_requirements" not in captured["request"]


def test_explicit_feed_refresh_uses_the_outside_checkout_data_cache(tmp_path, monkeypatch, capsys):
    data = tmp_path / "xdg-data"
    monkeypatch.setenv("XDG_DATA_HOME", str(data))
    captured = {}

    def fake_refresh(store, *, cache_dir):
        captured["cache_dir"] = Path(cache_dir)
        return {"added_source_count": 0, "held_failure_count": 0}

    monkeypatch.setitem(sys.modules, "engineering.sourcing.refresh",
                        SimpleNamespace(refresh_public_feeds=fake_refresh))
    assert cli.main(["--database", str(tmp_path / "state.sqlite3"), "refresh"]) == 0
    result = json.loads(capsys.readouterr().out)
    expected = data / "opensourcerail" / "sourcing" / "raw-feeds"
    assert captured["cache_dir"] == expected
    assert result["network_refresh_was_explicit"] is True
    assert result["automatic_source_updates"] is False
    assert result["committed_raw_vendor_files"] is False

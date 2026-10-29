"""CLI launch, local storage and bounded sourcing command contracts."""
import json
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
    refresh = cli._parser().parse_args(["refresh", "--cache-dir", str(tmp_path / "cache")])
    assert refresh.command == "refresh"
    assert refresh.cache_dir == tmp_path / "cache"
    study = cli._parser().parse_args(["study", "laminate", "--input", str(tmp_path / "twin.tar.gz"),
        "--member", "federated-bom.json.gz", "--as-of", "2026-10-29", "--output", str(tmp_path / "studies"),
        "--product-observation", "GURIT-CORECELL-M80=" + "c" * 64])
    assert study.command == "study" and study.study_command == "laminate"
    assert study.member == "federated-bom.json.gz"
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

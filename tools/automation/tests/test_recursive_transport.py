"""CLI/HTTP transport tests; no worker or native solver is started here."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
from types import SimpleNamespace

import pytest

from engineering.design_engine import http
from engineering.analysis.tests.test_design_http import handler, identity


ROOT = Path(__file__).resolve().parents[3]
ACTOR = dict(username="planner", roles=["planner"], city_scopes=["samawah"])


def test_public_launcher_dispatches_iterate_to_the_common_engine():
    result = subprocess.run([str(ROOT / "osr"), "design", "iterate", "--help"],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert "--recursive-policy" in result.stdout and "--finite-exhaustive" in result.stdout


@pytest.fixture
def cli(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location("recursive_cli_transport", ROOT / "tools/automation/design-engine.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    captured = []
    module.request = lambda *args, **kwargs: captured.append((args, kwargs)) or kwargs
    final = dict(id="run-test", status="completed", phase="completed", error=None,
                 physical_release=False, active_attempt=1)
    service = SimpleNamespace(store=SimpleNamespace(root=tmp_path, get=lambda _: final),
                              start=lambda request: final)
    monkeypatch.setattr(module, "Manager", lambda _: service)
    report = dict(incumbent_id="verified-candidate", termination_reason="finite-space-exhausted",
                  finite_domain_complete=True, native_domain_complete=True,
                  best_verified_in_tested_domain_claimed=True,
                  best_verified_claim_scope="bounded tested numerical domain; physical qualification open",
                  decision_trace_sha256="a" * 64)
    monkeypatch.setattr(module, "comparison", lambda *args: {"recursive_search": report})
    return module, captured


def test_cli_iterate_json_tuning_explicit_flags_and_result_report(cli, tmp_path, monkeypatch, capsys):
    module, captured = cli
    tuning = tmp_path / "policy.json"
    tuning.write_text(json.dumps(dict(evaluations=18, iterations=7, confirmations=8, seed=42)))
    monkeypatch.setattr(sys, "argv", ["design-engine", "iterate", "--problem", "mechanical-cleat",
        "--city", "samawah", "--recursive-policy", str(tuning), "--proposals", "12", "--rounds", "4",
        "--confirmations", "6", "--finite-exhaustive", "--evaluations", "30"])
    assert module.main() == 0
    args, forwarded = captured[0]
    assert args[0] == "mechanical-cleat"
    assert forwarded["recursive"] == dict(evaluations=12, iterations=4, confirmations=6, seed=42, finite_exhaustive=True)
    assert forwarded["budget"] == {"evaluations": 30}
    assert forwarded["search"] is None
    text = capsys.readouterr().out
    result = json.loads(text[text.index("{"):])["recursive_search"]
    assert result["incumbent_id"] == "verified-candidate"
    assert result["decision_trace_sha256"] == "a" * 64
    assert Path(result["report_path"]) == tmp_path / "runs/run-test/attempt-0001/recursive-search.json"


def test_cli_json_evaluation_budget_is_not_overwritten_and_search_default_is_preserved(cli, tmp_path, monkeypatch):
    module, captured = cli
    tuning = tmp_path / "policy.json"
    tuning.write_text('{"evaluations":12,"confirmations":6}')
    monkeypatch.setattr(sys, "argv", ["design-engine", "iterate", "--problem", "mechanical-cleat",
        "--city", "samawah", "--recursive-policy", str(tuning)])
    assert module.main() == 0
    assert captured[-1][1]["recursive"] == dict(evaluations=12, confirmations=6)
    monkeypatch.setattr(sys, "argv", ["design-engine", "search", "--problem", "clipped-side-bay", "--city", "samawah"])
    assert module.main() == 0
    assert captured[-1][1]["search"] == dict(seeds=[11, 29, 47], evaluations=32)
    assert captured[-1][1]["recursive"] is None


def test_http_recursive_tuning_reaches_controlled_request_and_check_waivers_fail(tmp_path, monkeypatch):
    from engineering.design_engine import runtime
    # Tool inventory is not exercised by this boundary test; request validation is real.
    monkeypatch.setattr(runtime, "toolchain", lambda _: {"label": "transport-test-only"})
    received = []
    monkeypatch.setattr(http, "manager", lambda _: SimpleNamespace(store=None,
        start=lambda req: received.append(req) or {"id": "run-test"}))
    data = dict(identity=identity(), problem="mechanical-cleat", recursive=dict(evaluations=12, finite_exhaustive=True))
    call = handler(tmp_path, data, actor=ACTOR)
    http.post(call)
    assert call.response[0] == 200, call.response
    assert received[0]["recursive"]["evaluations"] == 12
    assert received[0]["refine"]
    assert "physical_correlation" in received[0]["recursive"]["physical_checks"]
    data["recursive"] = {"native_checks": []}
    call = handler(tmp_path, data, actor=ACTOR)
    http.post(call)
    assert call.response[0] == 400 and len(received) == 1


@pytest.mark.parametrize("explicit", ["inherited", None, {"evaluations": 4}])
def test_reviewed_child_inherits_only_tuning_or_explicit_override(tmp_path, monkeypatch, explicit):
    from engineering.design_engine import input_revisions
    parent_scope = identity()
    child_scope = {**parent_scope, "configuration_revision": "reviewed-2"}
    snapshot = dict(parent_job="parent-job", problem_id="mechanical-cleat", target_identity=child_scope)
    parent_policy = dict(evaluations=12, finite_exhaustive=True, screening_checks=["geometry"],
                         native_checks=["solver"], physical_checks=["independent_acceptance"])
    parent = {"request": {"recursive": parent_policy, "candidates": [{"thickness_m": .012, "topology": "solid-web"}]}}
    monkeypatch.setattr(input_revisions, "InputRevisions", lambda _: SimpleNamespace(
        get=lambda _: {"identity": parent_scope}, snapshot=lambda _: deepcopy(snapshot), validate_job=lambda req: None))
    received = []
    monkeypatch.setattr(http, "request", lambda *args, **kwargs: received.append((args, kwargs)) or {"accepted": True})
    monkeypatch.setattr(http, "manager", lambda _: SimpleNamespace(
        store=SimpleNamespace(verify_request=lambda _: parent), start=lambda req, **kwargs: {"id": "child-job"}))
    data = dict(identity=parent_scope, search=None, refine=True, budget={})
    if explicit != "inherited":
        data["recursive"] = explicit
    call = handler(tmp_path, data, actor=ACTOR)
    call.path = "/api/design/input-revisions/input-test/run"
    http.post(call)
    assert call.response[0] == 200, call.response
    args, forwarded = received[0]
    assert args[1] == child_scope and forwarded["reviewed_inputs"] == snapshot
    assert forwarded["recursive"] == (dict(evaluations=12, finite_exhaustive=True) if explicit == "inherited" else explicit)
    assert call.response[1]["child_identity"] == child_scope
    assert not call.response[1]["baseline_modified"] and not call.response[1]["physical_release"]
    assert parent["request"]["recursive"] == parent_policy


def test_problem_operation_inventory_includes_iterate_without_opening_worker(tmp_path, monkeypatch):
    monkeypatch.setattr(http, "manager", lambda _: SimpleNamespace(store=None))
    monkeypatch.setattr(http, "problems", lambda: {"fixture": {"id": "fixture"}})
    monkeypatch.setattr(http, "preflight", lambda charter, operation="screen": {"operation": operation})
    call = handler(tmp_path, {}, actor=ACTOR)
    call.path = "/api/design/problems?city=samawah&environment=simulation"
    http.get(call)
    assert call.response[0] == 200
    assert call.response[1]["operations"]["fixture"]["iterate"] == {"operation": "iterate"}

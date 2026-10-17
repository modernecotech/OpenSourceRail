"""Independent checks for durable scheduling and cross-discipline research evidence."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.continuous_design import tasks, worker, service
from engineering.twin_workflow import core


def test_seed_domains_cover_four_lanes_without_duplicate_designs():
    seeds = tasks.seeds()
    assert {tasks.validate(v) for v in seeds} == set(tasks.LANES)
    keys = [tasks.identity(v, "a" * 64) for v in seeds]
    assert len(keys) == len(set(keys))
    assert len(seeds) == 27


@pytest.mark.parametrize("source", ["__import__('os').system('true')", "facts.clear()", "(x for x in [])", "1", "unknown", "True if data_valid else False", "True\nimport os"])
def test_generated_policy_cannot_execute_calls_attributes_imports_or_unknown_facts(source):
    with pytest.raises((ValueError, SyntaxError)):
        tasks.expression(source)


def test_fixed_truth_table_and_temporal_ramp_distinguish_generated_policies():
    correct = worker.software(" and ".join(tasks.FACTS))
    weak = worker.software("voltage_ready")
    assert correct["study_pass"] and not weak["study_pass"]
    assert correct["metrics"] == dict(truth_table_cases=4096, temporal_cases=20, failed_temporal_cases=0)
    assert weak["counterexamples"]
    assert next(r for r in correct["replay"] if r["id"] == "normal-voltage-ramp-can-complete")["requests"] == [False, True]
    assert all(correct[k] is False for k in core.FLAGS)


def test_equivalent_software_expressions_do_not_create_repeat_experiments():
    a = tasks.task("software-logic", dict(expression=" and ".join(tasks.FACTS)))
    b = tasks.task("software-logic", dict(expression=" and ".join(reversed(tasks.FACTS))))
    assert tasks.identity(a, "baseline") == tasks.identity(b, "baseline")


def test_generated_source_is_executable_and_corresponds_to_tested_expression(tmp_path):
    value = tasks.task("software-logic", dict(expression=" and ".join(tasks.FACTS)))
    result = worker.evaluate(dict(task=value, key="a" * 64), tmp_path / "output")
    assert result["study_pass"]
    path = tmp_path / "output/generated-controller.py"
    spec = importlib.util.spec_from_file_location("tested_policy", path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    facts = {k: True for k in tasks.FACTS}
    assert module.closure_request(**facts)
    facts["hvil_closed"] = False
    assert not module.closure_request(**facts)


def test_durable_queue_deduplicates_and_recovers_only_interrupted_jobs(tmp_path):
    store = service.Store(tmp_path)
    value = tasks.task("software-logic", dict(expression="voltage_ready"))
    assert store.enqueue(value, "baseline")
    value["rationale"] = "A different name cannot generate repeat progress"
    assert not store.enqueue(value, "baseline")
    with store.db:
        store.db.execute("UPDATE jobs SET status='running',attempts=1")
    store.db.close()
    recovered = service.Store(tmp_path)
    recovered.recover()
    row = recovered.db.execute("SELECT * FROM jobs").fetchone()
    assert row["status"] == "queued" and row["attempts"] == 1
    with recovered.db:
        recovered.db.execute("UPDATE jobs SET status='running',attempts=2")
    recovered.recover()
    assert recovered.db.execute("SELECT status FROM jobs").fetchone()[0] == "error"


def test_provider_cannot_widen_lane_or_change_recipe_limits_and_import_is_atomic(tmp_path):
    store = service.Store(tmp_path)
    good = dict(kind="software-logic", parameters_json=json.dumps(dict(expression="voltage_ready")), rationale="negative control")
    bad = dict(kind="software-logic", parameters_json=json.dumps(dict(expression="True", timeout=999)), rationale="bypass")
    with pytest.raises(ValueError):
        service.import_proposals(store, "baseline", "software", dict(proposals=[good, bad], needs=[]))
    assert store.db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0
    with pytest.raises(ValueError, match="lane"):
        service.import_proposals(store, "baseline", "civil", dict(proposals=[good], needs=[]))
    assert service.import_proposals(store, "baseline", "software", dict(proposals=[good], needs=[dict(item_id="HIL", required="Identify target hardware and timing limits")])) == 1
    assert service.import_proposals(store, "baseline", "software", dict(proposals=[good], needs=[])) == 0


@pytest.mark.parametrize("patch", [dict(concurrency=4), dict(poll_seconds=0), dict(max_output_gib=float('nan')), dict(provider_enabled="yes")])
def test_resource_settings_are_bounded(patch):
    config = service.config_default(); config.update(patch)
    with pytest.raises(ValueError):
        service.validate_config(config)


def seal_child(tmp_path, value, baseline, result):
    key = tasks.identity(value, baseline)
    folder = tmp_path / key; folder.mkdir()
    core.write(folder / "result.json", result)
    receipt = dict(key=key, baseline_sha256=baseline, files_sha256={"result.json": core.sha(folder / "result.json")})
    core.write(folder / "receipt.json", receipt)
    return dict(key=key, task=value, folder=str(folder), receipt_sha256=core.sha(folder / "receipt.json"))


def test_actual_cross_lane_coupling_uses_exact_child_mass_and_preserves_rejections(tmp_path):
    baseline = "b" * 64
    values = tasks.seeds()
    mechanical = next(v for v in values if v["kind"] == "mechanical-detail")
    civil = next(v for v in values if v["kind"] == "civil-detail")
    software = tasks.task("software-logic", dict(expression=" and ".join(tasks.FACTS)))
    deps = []
    for index, value in enumerate((mechanical, civil, software)):
        result = worker.evaluate(dict(task=value, key=tasks.identity(value, baseline)), tmp_path / f"eval-{index}")
        deps.append(seal_child(tmp_path, value, baseline, result))
    result = worker.integration(dict(baseline_sha256=baseline, dependencies=deps))
    mass = core.read(Path(deps[0]["folder"]) / "result.json")["assessment"]["objectives"]["mass_kg"]
    assert result["metrics"]["gross_added_mass_kg"] == pytest.approx(3*mass)
    assert result["metrics"]["coupled_axle_force_n"] > result["metrics"]["baseline_axle_force_n"]
    assert not result["study_pass"] and not result["adopted"]
    child_path = Path(deps[0]["folder"]) / "result.json"
    child_path.write_text("{}")
    with pytest.raises(ValueError, match="artifact"):
        worker.integration(dict(baseline_sha256=baseline, dependencies=deps))


def test_integration_rejects_unavailable_child_ids(tmp_path):
    store = service.Store(tmp_path)
    with pytest.raises(ValueError, match="children"):
        store.enqueue(tasks.task("integration-coupling", dict(children=["a"*64,"b"*64,"c"*64])), "baseline")


def test_no_progress_ai_does_not_reserve_a_worker_slot_or_retry_identical_context(tmp_path, monkeypatch):
    store = service.Store(tmp_path)
    config = service.config_default(); config["provider_enabled"] = True
    monkeypatch.setattr(service, "provider_request", lambda *args: {"fixed": True})
    request_hash = core.digest({"fixed": True})
    with store.db:
        for lane in tasks.LANES:
            store.db.execute("INSERT INTO provider(baseline,lane,request_hash,context_hash,folder,status,created,finished) VALUES(?,?,?,?,?,?,?,?)",
                             ("baseline", lane, request_hash, request_hash, str(tmp_path), "no-progress", 1., 2.))
    assert service.next_provider(store, "baseline", config, 1e6) is None
    with store.db:
        store.db.execute("UPDATE provider SET status='error' WHERE lane='civil'")
    assert service.next_provider(store, "baseline", config, 1e6)[0] == "civil"


def test_real_systemd_parser_accepts_generated_unit(tmp_path):
    import subprocess
    spec = importlib.util.spec_from_file_location("continuous_cli", ROOT / "tools/automation/design-continuous.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    path = tmp_path / "osr-test-continuous.service"
    text = module.unit_text(tmp_path / "work space")
    assert 'WorkingDirectory="' not in text
    assert "Restart=on-failure" in text and "KillMode=control-group" in text
    path.write_text(text)
    result = subprocess.run(["systemd-analyze", "--user", "verify", str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("wall", [.006, .008, .010])
def test_interface_wall_change_updates_nut_clearance_and_bolt_grip(wall):
    model = tasks.interface(dict(carrier_wall_m=.004, sill_wall_m=wall))
    for part in model["parts"]:
        if part["id"].startswith("bolt-"):
            primitives = {p["id"]: p for p in part["manufacturing"]["primitives"]}
            nut, bolt = primitives["nut"], primitives["bolt"]
            assert nut["centre_m"][2] + nut["length_m"]/2 == pytest.approx(.14 - wall)
            assert bolt["centre_m"][2] - bolt["length_m"]/2 == pytest.approx(nut["centre_m"][2] - nut["length_m"]/2)
            assert not part["production_released"]


def test_account_model_override_reaches_only_the_proposer_command(tmp_path, monkeypatch):
    from engineering.continuous_design import proposer
    seen = []
    def command(argv, **kwargs):
        seen.extend(argv)
        core.write(tmp_path / "response.json", dict(proposals=[], needs=[]))
    monkeypatch.setattr(proposer.subprocess, "run", command)
    result = proposer.run({"lane": "software"}, tmp_path, "/usr/bin/codex", "account-model")
    assert seen[seen.index("--model")+1] == "account-model"
    assert "--sandbox" in seen and "read-only" in seen
    assert result == dict(proposal_count=0, need_count=0)

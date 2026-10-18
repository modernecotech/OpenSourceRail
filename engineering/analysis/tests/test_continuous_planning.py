"""Regressions for exhausted budgets, missed feasible couplings and feedback loss."""
import itertools

from engineering.continuous_design import planning, service, tasks, worker
from engineering.twin_workflow import core


FRAME = dict(bolster_depth_m=.65, bolt_diameter_m=.027, bolts_per_support=8,
    crossbearer_pitch_m=.6, diaphragm_thickness_m=.025, maximum_stock_piece_length_m=3.8,
    plate_thickness_m=.025, side_depth_m=.75, spine_wall_m=.025, web_thickness_m=.016, weld_throat_m=.008)


def complete(store, value, baseline, result):
    assert store.enqueue(value, baseline)
    key = tasks.identity(value, baseline)
    folder = store.workspace / "sealed" / key
    folder.mkdir(parents=True)
    core.write(folder / "result.json", result)
    core.write(folder / "receipt.json", dict(key=key, baseline_sha256=baseline,
        files_sha256={"result.json": core.sha(folder / "result.json")}))
    with store.db:
        store.db.execute("UPDATE jobs SET status='completed',folder=?,receipt_sha=?,finished=1 WHERE key=?",
            (str(folder), core.sha(folder / "receipt.json"), key))
    return dict(key=key, task=value, folder=str(folder), receipt_sha256=core.sha(folder / "receipt.json"))


def real_children(store, baseline, *, span="pi25", footing=5., beam_depth=None, stirrup_spacing=None):
    values = [tasks.task("mechanical-detail", dict(context_id="metro-6car-planning", variables=FRAME)),
        tasks.task("civil-detail", dict(context_id="planning-six-car-460800kg-cg0.5/" + span,
            variables=dict(beam_depth_m=beam_depth or (1.7 if span == "pi25" else 1.4), beam_stem_width_m=.36,
                footing_width_m=footing, pad_length_m=.5 if span == "pi25" else .35,
                stirrup_diameter_m=.012, stirrup_spacing_m=stirrup_spacing or (.1 if span == "pi25" else .2)))),
        tasks.task("software-logic", dict(expression=" and ".join(tasks.FACTS)))]
    deps = []
    for i, value in enumerate(values):
        result = worker.evaluate(dict(task=value, key=tasks.identity(value, baseline)), store.workspace / f"evaluate-{i}")
        deps.append(complete(store, value, baseline, result))
    return deps


def test_completed_256_no_longer_prevents_new_candidate_and_deferred_work_survives_restart(tmp_path, monkeypatch):
    store = service.Store(tmp_path)
    # The previous controller counted all these completed experiments as capacity.
    with store.db:
        for i in range(256):
            store.db.execute("INSERT INTO jobs(key,baseline,lane,task,status,created) VALUES(?,?,?,?,?,?)",
                (f"history-{i}", "baseline", "software", "{}", "completed", i))
    monkeypatch.setattr(service.Store, "MAX_PENDING_PER_LANE", 1)
    a, b = [v for v in tasks.seeds() if v["kind"] == "software-logic"][:2]
    assert store.enqueue(a, "baseline")
    assert store.enqueue(b, "baseline", priority=0)
    assert not store.enqueue(b, "baseline")
    assert store.db.execute("SELECT status FROM jobs WHERE key=?", (tasks.identity(b, "baseline"),)).fetchone()[0] == "deferred"
    store.db.close()
    store = service.Store(tmp_path)
    with store.db:
        store.db.execute("UPDATE jobs SET status='completed' WHERE key=?", (tasks.identity(a, "baseline"),))
    store.promote("baseline")
    assert store.db.execute("SELECT status FROM jobs WHERE key=?", (tasks.identity(b, "baseline"),)).fetchone()[0] == "queued"


def test_feasible_children_produce_actual_passing_coupling_and_fresh_history_evaluations(tmp_path):
    store = service.Store(tmp_path)
    deps = real_children(store, "a" * 64)
    assert store.integration_jobs("a" * 64) == 1
    assert store.integration_jobs("a" * 64) == 0
    row = store.db.execute("SELECT * FROM jobs WHERE lane='integration'").fetchone()
    result = worker.integration(dict(key=row["key"], baseline_sha256="a" * 64, dependencies=deps))
    assert result["study_pass"] and not result["failed_checks"]
    assert all(result[k] is False for k in core.FLAGS)
    records = planning.historical_inputs(store, "a" * 64, "b" * 64)
    assert len(records) == 3
    for record in records:
        fresh = store.db.execute("SELECT * FROM jobs WHERE key=?", (record["key"],)).fetchone()
        assert fresh["status"] == "queued" and fresh["folder"] is None and fresh["receipt_sha"] is None
        assert fresh["key"] != record["previous_key"] and not record["acceptance_reused"]
    # A bootstrap retry retains the nomination provenance without duplicate work.
    assert len(planning.historical_inputs(store, "a" * 64, "b" * 64)) == 3
    assert store.integration_jobs("b" * 64) == 0


def test_coupled_rejection_reports_exact_predicates_and_proposes_actual_footing_repair(tmp_path):
    store = service.Store(tmp_path)
    deps = real_children(store, "a" * 64, footing=4.5, beam_depth=1.55, stirrup_spacing=.2)
    from pathlib import Path
    assert all(core.read(Path(d["folder"]) / "result.json")["study_pass"] for d in deps)
    result = worker.integration(dict(baseline_sha256="a" * 64, dependencies=deps))
    assert not result["study_pass"]
    assert result["failed_checks"] == ["civil_response_recomputed"]
    assert "footing_pressure" in result["metrics"]["failed_civil_checks"]
    check = next(c for c in result["check_details"] if c["id"] == "footing_pressure")
    assert check["value"] > check["limit"] and not check["accepted_basis"]
    assert any(r["parameters"]["variables"]["footing_width_m"] == 5. for r in result["repairs"])
    assert all(r["parameters"]["context_id"] == "planning-six-car-460800kg-cg0.5/pi25" for r in result["repairs"])


def test_lm3_proven_family_bound_stops_identical_family_search_without_hiding_failures(tmp_path):
    value = next(v for v in tasks.seeds() if v["kind"] == "mechanical-detail" and v["parameters"]["context_id"] == "LM3")
    result = worker.evaluate(dict(task=value, key=tasks.identity(value, "baseline")), tmp_path / "evaluate")
    assert not result["study_pass"] and result["failed_checks"]
    assert result["search_blocked"]["research_family_screen_incompatible"]
    assert not result["repairs"]
    assert result["needs"][0]["item_id"] == "LM3-alternative-load-path-adapter"


def test_feasible_geometry_generates_material_saving_trials_with_same_context_and_limits(tmp_path):
    value = tasks.task("mechanical-detail", dict(context_id="metro-6car-planning", variables=FRAME))
    result = worker.evaluate(dict(task=value, key=tasks.identity(value, "baseline")), tmp_path / "evaluate")
    assert result["study_pass"] and result["repairs"]
    for trial in result["repairs"]:
        tasks.validate(trial)
        assert trial["parameters"]["context_id"] == value["parameters"]["context_id"]
        assert sum(trial["parameters"]["variables"][k] != FRAME[k] for k in FRAME) == 1


def test_catalogue_keeps_old_passing_children_after_many_later_rejections_and_feedback_is_explicit(tmp_path):
    store = service.Store(tmp_path)
    deps = real_children(store, "a" * 64)
    # More than the old latest-100 window, with valid distinct recipe identities.
    module, _ = tasks.contexts("mechanical-detail")
    domains = core.read(module.DATA)["bounds"]
    for choices in itertools.islice(itertools.product(domains["side_depth_m"], domains["plate_thickness_m"],
            domains["spine_wall_m"], domains["web_thickness_m"]), 105):
        variables = dict(FRAME, **dict(zip(("side_depth_m", "plate_thickness_m", "spine_wall_m", "web_thickness_m"), choices)))
        value = tasks.task("mechanical-detail", dict(context_id="metro-6car-planning", variables=variables))
        complete(store, value, "a" * 64, dict(study_pass=False, failed_checks=["example_failure"],
            checks=dict(example_failure=False), assessment=dict(configuration_id="metro-6car-planning"), **core.FLAGS))
    request = service.provider_request(store, "a" * 64, "integration")
    catalogue = request["available_children"]
    assert {d["key"] for d in deps} <= {r["key"] for r in catalogue}
    assert all(r["study_pass"] for r in catalogue[:3])
    assert store.integration_jobs("a" * 64) == 1
    mechanical_feedback = service.provider_request(store, "a" * 64, "mechanical")["feedback"]
    assert mechanical_feedback[0]["failed_checks"] == ["example_failure"]
    assert mechanical_feedback[0]["checks"] == dict(example_failure=False)


def test_provider_predicates_are_recovered_when_older_result_omits_failed_checks():
    result = dict(study_pass=False, checks=dict(a=True, b=False, c="fail", d="unknown"), children=[dict(key="child")])
    feedback = planning.feedback(dict(key="example", status="completed", error=None), {}, result)
    assert feedback["failed_checks"] == ["b", "c"]
    assert feedback["children"] == [dict(key="child")]


def test_integration_budget_covers_both_spans_before_many_frame_variants(monkeypatch):
    groups = {kind: [] for kind in planning.CHILD_KINDS}
    for i in range(10):
        groups["mechanical-detail"].append((dict(key=f"frame-{i}"), {}, dict(study_pass=True,
            assessment=dict(configuration_id="metro-6car-planning", objectives=dict(mass_kg=10+i)))))
    for span in (20, 25):
        groups["civil-detail"].append((dict(key=f"civil-{span}"), {}, dict(study_pass=True,
            assessment=dict(context_id=f"pi{span}", architecture_id="metro-6car-planning"))))
    groups["software-logic"].append((dict(key="software"), {}, dict(study_pass=True)))
    monkeypatch.setattr(planning, "children", lambda *_: groups)
    class Admissions:
        def __init__(self):
            self.tasks = []
        def enqueue(self, value, baseline, *, priority):
            self.tasks.append(value)
            return True
    store = Admissions()
    assert planning.integration_frontier(store, "baseline", admission_budget=2) == 2
    assert {v["parameters"]["children"][1] for v in store.tasks} == {"civil-20", "civil-25"}

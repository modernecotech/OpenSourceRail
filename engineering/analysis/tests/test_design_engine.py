"""Scope, immutable history, budgets and adverse-result regression boundaries."""

from copy import deepcopy
import json
import os
from pathlib import Path

import pytest

from engineering.design_engine import contracts as c
from engineering.design_engine.registry import get, problems
from engineering.design_engine.runtime import (
    request,
    Budget,
    BudgetExceeded,
    diverse_shortlist,
)
from engineering.design_engine.store import Store, write_new
from engineering.design_engine.publication import digest


def scope(city="samawah", environment="simulation"):
    return c.identity(
        dict(
            schema=c.SCHEMA,
            city=city,
            project=city,
            environment=environment,
            configuration_revision="research-1",
            baseline_sha256=None,
            run_id=None,
            asset_id=None,
            part_id=None,
        )
    )


def test_all_registered_problems_have_distinct_fixed_function_and_mandatory_matrix():
    for row in problems().values():
        assert c.problem(row) == row
    side = get("clipped-side-bay")
    roof = get("clipped-roof-bay")
    assert side["applicability"]["function"] != roof["applicability"]["function"]
    with pytest.raises(ValueError):
        c.comparable(
            dict(problem_sha256=c.fingerprint(side), identity=scope()),
            dict(problem_sha256=c.fingerprint(roof), identity=scope()),
        )


@pytest.mark.parametrize(
    "fault",
    [
        "unit",
        "nonfinite",
        "missing-scope",
        "environment",
        "duplicate-check",
        "integer-budget",
    ],
)
def test_units_revisions_scope_and_nonfinite_mutations_reject(fault):
    charter = get("clipped-side-bay")
    context = scope()
    if fault == "unit":
        charter["variables"]["core_m"]["unit"] = "mm pretending to be m"
    elif fault == "nonfinite":
        charter["variables"]["core_m"]["choices"] = [float("nan")]
    elif fault == "missing-scope":
        context.pop("project")
    elif fault == "environment":
        context["environment"] = "production-approved"
    elif fault == "duplicate-check":
        charter["applicability"]["mandatory_checks"].append("geometry")
    else:
        charter["budget"]["evaluations"] = True
    with pytest.raises(ValueError):
        c.problem(charter)
        c.identity(context)


def test_unknown_objectives_are_not_zero_and_incomplete_evidence_cannot_pass():
    assert (
        c.quantity(
            dict(value=None, unit="USD", state="unknown", basis="no supplier quote")
        )["value"]
        is None
    )
    with pytest.raises(ValueError):
        c.quantity(
            dict(value=0, unit="USD", state="unknown", basis="no supplier quote")
        )
    checks = {
        "nominal": dict(state="passed", basis="screen"),
        "fault": dict(state="not-run", basis="not executed"),
    }
    assert c.checks_status(checks, ["nominal", "fault"]) == "not-run"
    checks["fault"]["state"] = "failed"
    assert c.checks_status(checks, ["nominal", "fault"]) == "failed"
    with pytest.raises(ValueError):
        c.checks_status({"nominal": checks["nominal"]}, ["nominal", "fault"])


def test_native_json_numeric_roundtrip_preserves_declared_choice_type():
    charter = get("clipped-side-bay")
    values = dict(support_span_m=1, grade_density=80, core_m=0.0246, skin_m=0.0015)
    normalized = c.variables(charter, values)
    assert type(normalized["support_span_m"]) is float
    with pytest.raises(ValueError):
        c.variables(charter, {**values, "grade_density": True})


def test_workbench_crosswalk_never_imports_role_or_actor_as_authority():
    row = c.from_workbench(
        dict(
            schema_version=1,
            city="samawah",
            environment="simulation",
            actor="administrator",
            role="reviewer",
        ),
        project="samawah",
    )
    assert "actor" not in row and "role" not in row
    assert row["baseline_sha256"] is None


def test_changed_environment_and_city_cannot_be_compared():
    base = dict(problem_sha256="problem", identity=scope())
    for different in (scope("mosul"), scope(environment="physical")):
        with pytest.raises(ValueError):
            c.comparable(base, dict(problem_sha256="problem", identity=different))


def minimal_request():
    return dict(
        schema="osr-design-request/1",
        identity=scope(),
        problem=get("clipped-side-bay"),
        dependencies={"model.py": "current"},
        toolchain={"solver": "pinned"},
    )


def sealed_attempt(store, job, status="failed"):
    folder = store.begin(job["id"], os.getpid())
    write_new(folder / "result.json", dict(state=status, physical_release=False))
    manifest = dict(
        schema="osr-design-attempt/1",
        request_sha256=c.fingerprint(job["request"]),
        artifacts={"result.json": digest(folder / "result.json")},
        physical_release=False,
    )
    write_new(folder / "manifest.json", manifest)
    store.finish(job["id"], status, "original failed attempt", manifest)
    return folder, manifest


def test_failed_attempt_survives_restart_resume_and_cannot_be_rewritten(tmp_path):
    store = Store(tmp_path)
    job = store.create(minimal_request())
    folder, manifest = sealed_attempt(store, job)
    reopened = Store(tmp_path)
    assert reopened.verify_attempt(job["id"], 1) == manifest
    with pytest.raises(ValueError):
        reopened.finish(job["id"], "completed")
    reopened.resume(job["id"], {"model.py": "current"}, {"solver": "pinned"})
    second = reopened.begin(job["id"], os.getpid())
    assert second != folder
    assert (folder / "result.json").read_text().find("failed") >= 0
    assert reopened.get(job["id"])["attempts"][0]["status"] == "failed"


def test_stale_source_or_corrupted_artifact_cannot_resume(tmp_path):
    store = Store(tmp_path)
    job = store.create(minimal_request())
    folder, _ = sealed_attempt(store, job)
    with pytest.raises(ValueError, match="stale"):
        store.resume(job["id"], {"model.py": "changed"}, {"solver": "pinned"})
    (folder / "result.json").write_text("corrupt")
    with pytest.raises(ValueError, match="corrupt"):
        store.resume(job["id"], {"model.py": "current"}, {"solver": "pinned"})


def test_queued_cancellation_is_not_cleared_when_worker_claims_job(tmp_path):
    store = Store(tmp_path)
    job = store.create(minimal_request())
    store.cancel(job["id"])
    store.begin(job["id"], os.getpid())
    assert store.cancelled(job["id"])


def test_evaluation_budget_is_checked_before_running_work(tmp_path):
    store = Store(tmp_path)
    job = store.create(minimal_request())
    budget = Budget(store, job["id"], dict(evaluations=2, wall_seconds=100))
    budget.charge(2, "screen")
    with pytest.raises(BudgetExceeded):
        budget.charge(1, "unbudgeted-refinement")
    assert budget.spent == 2


def test_two_dispatchers_cannot_execute_the_same_queued_request(tmp_path):
    store=Store(tmp_path);job=store.create(minimal_request())
    assert store.claim_dispatch(job['id'])is True
    assert Store(tmp_path).claim_dispatch(job['id'])is False
    assert job['id']not in Store(tmp_path).pending()


def test_dead_worker_recovery_preserves_interrupted_attempt_and_request(tmp_path):
    store=Store(tmp_path);job=store.create(minimal_request());store.begin(job['id'],os.getpid())
    with store.connect()as con:con.execute('UPDATE jobs SET pid=?,process_start=? WHERE id=?',(99999999,'never-live',job['id']))
    Store(tmp_path).recover();row=store.get(job['id'])
    assert row['status']=='interrupted'and row['attempts'][0]['status']=='interrupted'
    assert store.verify_request(job['id'])['request']==job['request']


def test_shortlist_preserves_diversity_and_rejects_failed_or_outside_domain():
    def row(identifier, span, mass, state="passed"):
        return dict(
            id=identifier,
            variables=dict(support_span_m=span),
            metrics=dict(defined_mass_kg=mass),
            checks=dict(geometry=dict(state=state)),
        )

    values = [
        row("cheap", 1, 1),
        row("same", 1, 2),
        row("diverse", 0.2, 3),
        row("invalid", 0.5, 0.1, "outside-domain"),
        row("failed", 0.33, 0.2, "failed"),
    ]
    assert [r["id"] for r in diverse_shortlist(values, 2)] == ["cheap", "diverse"]


def test_real_compiler_keeps_function_adds_hardware_and_conserves_properties():
    from engineering.design_engine.adapters import compile_candidate

    base = dict(support_span_m=1, grade_density=80, core_m=0.0246, skin_m=0.0015)
    first = compile_candidate(get("clipped-side-bay"), scope(), base)
    tighter = compile_candidate(
        get("clipped-side-bay"), scope(), {**base, "support_span_m": 0.2}
    )
    assert tighter["metrics"]["defined_mass_kg"] > first["metrics"]["defined_mass_kg"]
    assert tighter["metrics"]["attachment_count"] > first["metrics"]["attachment_count"]
    assert (
        first["definition"]["contract"]["panel_parameters"]["height_m"]
        == tighter["definition"]["contract"]["panel_parameters"]["height_m"]
        == 3.45
    )
    assert (
        first["complete_installed_mass_kg"] is None and first["installed_cost"] is None
    )
    assert first["physical_release"] is False


def test_budgets_do_not_change_function_but_loads_do():
    base=get('clipped-side-bay');limited=deepcopy(base);limited['budget']['evaluations']=4
    assert c.problem_fingerprint(base)==c.problem_fingerprint(limited)
    limited['applicability']['loads'][0]['quantity']['value']=3000
    assert c.problem_fingerprint(base)!=c.problem_fingerprint(limited)


def test_extra_hvac_hardware_does_not_steal_mass_and_reaches_all_review_properties():
    from engineering.design_engine.subsystems import hvac
    first=hvac(dict(hvac_modules=4,carrier_thickness_m=.004))
    extra=hvac(dict(hvac_modules=5,carrier_thickness_m=.005))
    a,b=first['review'],extra['review']
    assert b['total_train_mass_kg']>a['total_train_mass_kg']+6*125
    assert abs(b['static_reaction_balance_n'])<1e-6
    assert b['carbody_dynamics'][0]['mass_kg']>a['carbody_dynamics'][0]['mass_kg']
    assert b['carbody_dynamics'][0]['inertia_kg_m2']!=a['carbody_dynamics'][0]['inertia_kg_m2']
    assert extra['verification']['configuration_sha256']==b['configuration_sha256']

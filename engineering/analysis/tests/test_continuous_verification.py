"""Evidence scopes, real native promotion, numerical benchmarks and shortlist changes."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from engineering.continuous_design import beam_confirmation,evidence,ledger,research,runtime,service,tasks,worker
from engineering.twin_workflow import core
from engineering.analysis.tests.test_continuous_planning import complete,real_children,FRAME


def test_independent_beam_benchmarks_conserve_force_and_match_closed_forms():
    assert all(r["passed"] for r in beam_confirmation.benchmarks())
    row=beam_confirmation.solve(4.,[0.,4.],4e6,points=[(2.,3000.)],divisions=16)
    assert row["midspan_deflection_m"]==pytest.approx(3000*4**3/(48*4e6),rel=1e-8)
    assert row["force_balance_relative_error"]<1e-8


def test_evidence_never_calls_analytical_frame_native_confirmed():
    result=evidence.label("mechanical-detail",dict(study_pass=True,checks=dict(analytical=True)))
    assert result["verification"]["evaluated_level"]=="analytical_screening"
    assert result["verification"]["levels"]["native_geometry"]["state"]=="not_run"
    assert result["verification"]["levels"]["physical_correlation"]["state"]=="not_run"
    assert not result["verification"]["independent_physics_rerun"]


def test_constraint_margins_preserve_unknowns_and_failed_limit_distance():
    rows=evidence.margins([dict(id="failed",state="fail",value=120.,limit=100.),
        dict(id="pass",state="pass",value=80.,limit=100.),dict(id="unknown",state="unknown",value=None,limit=None)])
    assert [r["id"] for r in rows]==["failed","pass"]
    assert rows[0]["signed_normalised_distance"]<0<rows[1]["signed_normalised_distance"]


def test_pareto_archive_retains_effort_tradeoff_and_champion_revisions(tmp_path):
    store=service.Store(tmp_path)
    for depth,mass,parts in ((.26,10.,5),(.45,11.,6),(.6,12.,3),(.75,9.,5)):
        value=tasks.task("mechanical-detail",dict(context_id="metro-6car-planning",variables=dict(FRAME,side_depth_m=depth)))
        result=evidence.label("mechanical-detail",dict(study_pass=True,checks=dict(screen=True),metrics=dict(mass_kg=mass),
            assessment=dict(configuration_id="metro-6car-planning",geometry=dict(parts=[{}]*parts)),**core.FLAGS))
        child=complete(store,value,"baseline",result)
        with ledger.transaction(store.db):research.observe(store,child["key"])
    frontier=list(store.db.execute("SELECT mass,effort FROM observations WHERE pareto=1 ORDER BY mass"))
    assert [tuple(r) for r in frontier]==[(9.,5.),(12.,3.)]
    champions=list(store.db.execute("SELECT * FROM champions ORDER BY id"))
    assert len(champions)==2 and champions[-1]["predecessor"]==champions[0]["key"]
    assert json.loads(store.db.execute("SELECT objectives FROM observations LIMIT 1").fetchone()[0])["quoted_cost"] is None


def test_duplicate_observation_cannot_fabricate_repeated_improvement(tmp_path):
    store=service.Store(tmp_path);deps=real_children(store,"a"*64)
    with ledger.transaction(store.db):
        research.observe(store,deps[0]["key"]);research.observe(store,deps[0]["key"])
    assert store.db.execute("SELECT COUNT(*) FROM champions").fetchone()[0]==1


def test_source_update_preserves_verified_nominations_from_unfinished_epoch(tmp_path):
    from engineering.continuous_design import planning
    store=service.Store(tmp_path);real_children(store,"a"*64)
    records=planning.historical_inputs(store,"a"*64,"b"*64)
    folder=tmp_path/"epochs"/("b"*64);folder.mkdir(parents=True)
    core.write(folder/"historical-inputs.json",dict(nominations=records,previous_baseline="a"*64))
    carried=planning.historical_inputs(store,"b"*64,"c"*64)
    assert len(carried)==3
    for record in carried:
        assert record["previous_baseline"]=="a"*64 and not record["acceptance_reused"]
        row=store.db.execute("SELECT * FROM jobs WHERE key=?",(record["key"],)).fetchone()
        assert row["status"]=="queued" and row["receipt_sha"] is None


def test_failed_parent_integration_cannot_replace_passing_research_champion(tmp_path):
    store=service.Store(tmp_path);baseline="a"*64;deps=real_children(store,baseline)
    good=tasks.task("integration-coupling",dict(children=[d["key"] for d in deps]))
    result=worker.integration(dict(baseline_sha256=baseline,dependencies=deps))
    sealed=complete(store,good,baseline,evidence.label("integration-coupling",result))
    with ledger.transaction(store.db):research.observe(store,sealed["key"])
    weak=tasks.task("software-logic",dict(expression="voltage_ready"))
    bad_software=complete(store,weak,baseline,worker.software("voltage_ready"))
    bad_deps=[deps[0],deps[1],bad_software]
    bad=tasks.task("integration-coupling",dict(children=[d["key"] for d in bad_deps]))
    rejected=worker.integration(dict(baseline_sha256=baseline,dependencies=bad_deps))
    assert not rejected["study_pass"]
    bad_child=complete(store,bad,baseline,evidence.label("integration-coupling",rejected))
    with ledger.transaction(store.db):research.observe(store,bad_child["key"])
    champions=list(store.db.execute("SELECT key FROM champions WHERE kind='integration-coupling'"))
    assert [r["key"] for r in champions]==[sealed["key"]]


def test_numerical_runtime_change_invalidates_current_verification(tmp_path,monkeypatch):
    store=service.Store(tmp_path);store.db.close()
    original=dict(version="same",binary_sha256="old");baseline=core.digest(dict(sources={},runtime=original))
    folder=tmp_path/"epoch";folder.mkdir()
    core.write(folder/"baseline.json",dict(source_sha256={},runtime_identity=original))
    core.write(tmp_path/"active.json",dict(baseline_sha256=baseline,epoch=str(folder)))
    monkeypatch.setattr(runtime,"capture",lambda:dict(version="same",binary_sha256="changed"))
    with pytest.raises(ValueError,match="runtime identity changed"):service.verify(tmp_path)
    assert service.verify(tmp_path,historical=True)["physics_rerun"] is False


def test_same_package_version_with_changed_module_bytes_changes_runtime_hash(tmp_path,monkeypatch):
    path=tmp_path/"numeric.py";path.write_text("value=1\n")
    class Distribution:
        version="1.0";files=["numeric.py"]
        def locate_file(self,member):return tmp_path/member
    monkeypatch.setattr(runtime.importlib.metadata,"distribution",lambda _:Distribution())
    monkeypatch.setattr(runtime,"actual_tools",lambda:{})
    old=runtime.digest(runtime.capture());path.write_text("value=2\n")
    assert old!=runtime.digest(runtime.capture())


def test_unregistered_receiver_is_not_advertised_or_admitted(tmp_path):
    from engineering.continuous_design import protocol_receiver
    store=service.Store(tmp_path)
    assert "software-receiver" not in service.registered_domains(store,"software")
    with pytest.raises(ValueError,match="registration"):store.enqueue(protocol_receiver.seeds()[0],"baseline")


def test_capability_registration_rejects_changed_installed_bytes(tmp_path):
    from engineering.continuous_design import capabilities
    store=service.Store(tmp_path);folder=tmp_path/"capabilities/example";folder.mkdir(parents=True)
    core.write(folder/"work-order.json",dict(item_id="example",limitations=["research only"]))
    core.write(folder/"benchmark-receipt.json",dict(passed=True,source_sha256={"engineering/continuous_design/protocol_receiver.py":"0"*64}))
    core.write(folder/"review.json",dict(decision="register-for-research",scope="research only",benchmark_receipt_sha256=core.sha(folder/"benchmark-receipt.json")))
    with pytest.raises(ValueError,match="installed repository bytes"):capabilities.register(store,"example")


@pytest.mark.parametrize("kind",["mechanical-detail","civil-detail"])
def test_automatic_shortlist_confirmation_runs_actual_native_geometry_and_independent_meshes(tmp_path,kind):
    if not shutil.which("FreeCADCmd") and not shutil.which("freecadcmd"):
        if not shutil.which("flatpak") or subprocess.run(["flatpak","info","org.freecad.FreeCAD"],capture_output=True).returncode:
            pytest.skip("actual native FreeCAD runtime unavailable")
    store=service.Store(tmp_path);baseline="a"*64;deps=real_children(store,baseline)
    child=next(d for d in deps if d["task"]["kind"]==kind)
    with ledger.transaction(store.db):research.observe(store,child["key"])
    promotion=store.db.execute("SELECT * FROM promotions WHERE child=?",(child["key"],)).fetchone()
    assert promotion is not None
    row=store.db.execute("SELECT * FROM jobs WHERE key=?",(promotion["task_key"],)).fetchone()
    result=worker.evaluate(dict(task=json.loads(row["task"]),key=row["key"],baseline_sha256=baseline,dependencies=[child]),tmp_path/"higher-fidelity")
    assert result["study_pass"],result.get("errors")
    levels=result["verification"]["levels"]
    assert levels["native_geometry"]["state"]==levels["numerical_confirmation"]["state"]=="passed"
    assert levels["physical_correlation"]["state"]=="not_run"
    assert (tmp_path/"higher-fidelity/cad/model.FCStd").is_file()
    assert (tmp_path/"higher-fidelity/cad/model.step").is_file()
    assert len(list((tmp_path/"higher-fidelity").glob("*-mesh-*.json")))>=2
    assert all(result[k] is False for k in core.FLAGS)
    # An integrated champion shares the civil context: it must not be mistaken
    # for another detail candidate when a confirmation frees promotion capacity.
    integration=tasks.task("integration-coupling",dict(children=[d["key"] for d in deps]))
    integrated=complete(store,integration,baseline,worker.integration(dict(baseline_sha256=baseline,dependencies=deps)))
    with ledger.transaction(store.db):research.observe(store,integrated["key"])
    folder=tmp_path/"higher-fidelity"
    receipt=dict(files_sha256={p.relative_to(folder).as_posix():core.sha(p) for p in folder.rglob("*") if p.is_file()})
    core.write(folder/"receipt.json",receipt)
    with store.db:
        store.db.execute("UPDATE jobs SET status='completed',folder=?,receipt_sha=?,finished=2 WHERE key=?",(str(folder),core.sha(folder/"receipt.json"),row["key"]))
    with ledger.transaction(store.db):research.observe(store,row["key"])
    assert store.db.execute("SELECT native_confirmed FROM observations WHERE key=?",(child["key"],)).fetchone()[0]==1

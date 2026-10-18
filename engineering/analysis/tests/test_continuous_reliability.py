"""Process-kill recovery, bounded long histories and persistent proposer fairness."""
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from engineering.continuous_design import ledger, proposals, service, tasks
from engineering.twin_workflow import core


def pending_completion(folder):
    store=service.Store(folder)
    parent=tasks.task("software-logic",dict(expression="voltage_ready"))
    repair=tasks.task("software-logic",dict(expression="voltage_ready and timeout_ok"))
    store.enqueue(parent,"baseline");key=tasks.identity(parent,"baseline")
    result=dict(study_pass=False,checks=dict(oracle=False),repairs=[repair],
        needs=[dict(item_id="required-followup",required="Retain the missing physical evidence request")],**core.FLAGS)
    output=folder/"sealed";output.mkdir()
    core.write(output/"result.json",result)
    core.write(output/"receipt.json",dict(files_sha256={"result.json":core.sha(output/"result.json")}))
    with store.db:
        store.db.execute("UPDATE jobs SET status='running',attempts=1,folder=? WHERE key=?",(str(output),key))
    store.db.close()
    return key,repair


@pytest.mark.parametrize("boundary",["inside-completion","after-completion","inside-dispatch"])
def test_kill_at_completion_boundaries_loses_neither_parent_nor_followups(tmp_path,boundary):
    key,repair=pending_completion(tmp_path)
    script="""
import os,sys
from pathlib import Path
from engineering.continuous_design import service,ledger
from engineering.twin_workflow import core
s=service.Store(Path(sys.argv[1]));key=sys.argv[2];boundary=sys.argv[3]
folder=Path(sys.argv[1])/'sealed';result=core.read(folder/'result.json')
if boundary=='inside-completion':
 original=ledger.add
 def crash(*a,**k):
  original(*a,**k);os._exit(72)
 ledger.add=crash
ledger.complete_job(s,key,core.sha(folder/'receipt.json'),result)
if boundary=='inside-dispatch':
 def crash(*a,**k):os._exit(72)
 s.record_needs=crash
 ledger.dispatch(s)
os._exit(72)
"""
    result=subprocess.run([sys.executable,"-c",script,str(tmp_path),key,boundary],cwd=core.ROOT)
    assert result.returncode==72
    store=service.Store(tmp_path);store.recover()
    parent=store.db.execute("SELECT * FROM jobs WHERE key=?",(key,)).fetchone()
    if boundary=="inside-completion":
        assert parent["status"]=="queued"
        ledger.complete_job(store,key,core.sha(tmp_path/"sealed/receipt.json"),core.read(tmp_path/"sealed/result.json"))
    ledger.dispatch(store);store.recover();ledger.dispatch(store)
    assert store.db.execute("SELECT COUNT(*) FROM jobs WHERE key=?",(tasks.identity(repair,"baseline"),)).fetchone()[0]==1
    assert store.db.execute("SELECT COUNT(*) FROM needs WHERE item_id='required-followup'").fetchone()[0]==1
    assert store.db.execute("SELECT state FROM outbox WHERE origin=?",("job:"+key,)).fetchone()[0]=="delivered"


def test_legacy_completed_parent_with_lost_children_is_repaired_by_migration(tmp_path):
    key,repair=pending_completion(tmp_path);store=service.Store(tmp_path)
    with store.db:
        store.db.execute("UPDATE jobs SET status='completed',receipt_sha=? WHERE key=?",(core.sha(tmp_path/"sealed/receipt.json"),key))
    store.recover();store.recover()
    assert store.db.execute("SELECT COUNT(*) FROM jobs WHERE key=?",(tasks.identity(repair,"baseline"),)).fetchone()[0]==1


def test_ai_import_commit_and_partial_dispatch_replay_atomically(tmp_path,monkeypatch):
    store=service.Store(tmp_path)
    with store.db:
        row=store.db.execute("INSERT INTO provider(baseline,lane,request_hash,context_hash,folder,status,created) VALUES('baseline','software','request','request',?,'running',1)",(str(tmp_path),))
    value=tasks.task("software-logic",dict(expression="voltage_ready"))
    ledger.complete_provider(store,row.lastrowid,[value],[dict(item_id="AI-need",required="Actual missing evidence")],"response-digest")
    original=store.record_needs
    monkeypatch.setattr(store,"record_needs",lambda *a: (_ for _ in ()).throw(RuntimeError("simulated process loss")))
    with pytest.raises(RuntimeError):ledger.dispatch(store)
    assert store.db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]==0
    assert store.db.execute("SELECT status FROM provider").fetchone()[0]=="import-pending"
    monkeypatch.setattr(store,"record_needs",original)
    ledger.dispatch(store);ledger.dispatch(store)
    assert store.db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]==1
    assert store.db.execute("SELECT COUNT(*) FROM needs").fetchone()[0]==1
    assert store.db.execute("SELECT status FROM provider").fetchone()[0]=="added"


def test_long_ai_calls_serve_every_eligible_lane_within_four_turns_across_restarts(tmp_path,monkeypatch):
    config=service.config_default();config.update(provider_enabled=True,provider_interval_seconds=120)
    sequence=[]
    for turn in range(8):
        store=service.Store(tmp_path)
        monkeypatch.setattr(service,"provider_request",lambda s,b,l:dict(lane=l,progress=turn))
        now=100000.+turn*301
        lane,request,digest,_=service.next_provider(store,"baseline",config,now)
        sequence.append(lane)
        with store.db:
            store.db.execute("INSERT INTO provider(baseline,lane,request_hash,context_hash,folder,status,created,finished) VALUES(?,?,?,?,?,'no-progress',?,?)",
                ("baseline",lane,digest,digest,str(tmp_path),now,now+300))
        store.db.close()
    assert sequence==list(tasks.LANES)*2


def test_4000_design_history_stays_bounded_and_pagination_does_not_lose_rows(tmp_path):
    store=service.Store(tmp_path)
    module,mapping=tasks.contexts("mechanical-detail")
    variables=module.seed(mapping["metro-6car-planning"])
    with store.db:
        for i in range(4000):
            value=tasks.task("mechanical-detail",dict(context_id="metro-6car-planning",variables=variables),rationale="example"+str(i))
            store.db.execute("INSERT INTO jobs(key,baseline,lane,task,status,created) VALUES(?,?,?,?,'queued',?)",
                (f"synthetic-history-{i}","baseline","mechanical",json.dumps(value),i))
    request=service.provider_request(store,"baseline","mechanical")
    assert len(core.encoded(request))<=proposals.MAX_REQUEST_BYTES
    assert len(request["existing_designs"])<=24
    assert not request["history_lookup"]["complete_history_included"]
    seen=[];cursor=0
    while True:
        page=proposals.history(store,"baseline","mechanical",after=cursor,limit=50)
        seen.extend(r["key"] for r in page["items"])
        if page["next_cursor"] is None:break
        cursor=page["next_cursor"]
    assert len(seen)==len(set(seen))==4000


def test_proposer_inputs_logs_and_outputs_have_separate_budgets(tmp_path):
    (tmp_path/"request.json").write_bytes(b"x"*(128*1024))
    (tmp_path/"prompt.txt").write_bytes(b"x"*1000)
    (tmp_path/"provider.log").write_bytes(b"x"*(4*1024**2-1))
    assert proposals.budget_error(tmp_path) is None
    (tmp_path/"response.json").write_bytes(b"x"*(proposals.MAX_RESPONSE_BYTES+1))
    assert proposals.budget_error(tmp_path)=="proposer response budget exceeded"


def test_sealed_worker_output_survives_crash_before_completion_database_commit(tmp_path):
    key,repair=pending_completion(tmp_path);store=service.Store(tmp_path)
    receipt=core.read(tmp_path/"sealed/receipt.json")
    receipt.update(key=key,baseline_sha256="baseline")
    core.write(tmp_path/"sealed/receipt.json",receipt)
    store.recover()
    assert store.db.execute("SELECT status FROM jobs WHERE key=?",(key,)).fetchone()[0]=="completed"
    assert store.db.execute("SELECT COUNT(*) FROM jobs WHERE key=?",(tasks.identity(repair,"baseline"),)).fetchone()[0]==1


def test_final_ai_response_survives_crash_before_controller_import(tmp_path):
    store=service.Store(tmp_path)
    with store.db:
        store.db.execute("INSERT INTO provider(baseline,lane,request_hash,context_hash,folder,status,created) VALUES('baseline','software','r','r',?,'running',1)",(str(tmp_path),))
    core.write(tmp_path/"response.json",dict(proposals=[dict(kind="software-logic",parameters_json=json.dumps(dict(expression="voltage_ready")),rationale="Retained proposal")],needs=[]))
    store.recover();store.recover()
    assert store.db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]==1
    assert store.db.execute("SELECT status FROM provider").fetchone()[0]=="added"


def test_input_preflight_rejects_oversized_context_before_starting_cli(tmp_path,monkeypatch):
    from engineering.continuous_design import proposer
    launched=[]
    monkeypatch.setattr(proposer.subprocess,"run",lambda *a,**k:launched.append(a))
    request=dict(available_children=[],feedback=[],existing_designs=[],package_scope=[],padding="x"*(proposals.MAX_REQUEST_BYTES+1))
    with pytest.raises(ValueError,match="input budget"):proposer.run(request,tmp_path,"codex")
    assert not launched

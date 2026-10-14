"""Actual draft solvers behind scoped HTTP; no baseline or acceptance mutation."""

from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from engineering.design_consistency.demonstrators import viaduct
from engineering.design_engine import http
from engineering.design_engine.contracts import SCHEMA, fingerprint
from engineering.design_engine.runtime import request
from engineering.design_engine.store import Store


def scope():
    return dict(schema=SCHEMA,city="samawah",project="samawah",environment="simulation",
                configuration_revision="research-1",baseline_sha256=None,run_id=None,asset_id=None,part_id=None)


@pytest.fixture
def case(tmp_path,monkeypatch):
    store=Store(tmp_path/"store")
    job=store.create(request("viaduct-bay",scope()))
    store.finish(job["id"],"completed")
    contract=viaduct()
    candidate=dict(id="candidate-test-only",definition=dict(contract=contract))
    monkeypatch.setattr(http,"manager",lambda handler:SimpleNamespace(store=store))
    monkeypatch.setattr(http,"comparison",lambda *args:dict(candidates=[candidate]))
    template=http.qualification_template("site",contract,scope())
    data=dict(identity=scope(),candidate=candidate["id"],contract_sha256=fingerprint(contract),kind="site",input_json=json.dumps(template))
    return store,job,candidate,data


def call(case,data=None,*,csrf=True,roles=None,origin=True,username="test-fixture-planner"):
    store,job,candidate,default=case
    data=deepcopy(default if data is None else data)
    actor=dict(username=username,roles=roles or ["planner"],city_scopes=["samawah"])
    handler=SimpleNamespace(path="/api/design/jobs/"+job["id"]+"/qualification-draft",
                            headers={"Content-Length":str(len(json.dumps(data).encode())),"Origin":"http://localhost:1234" if origin else "https://elsewhere.invalid","Host":"localhost:1234"},
                            project_twins=SimpleNamespace(_cities={"samawah":{}}),bootstrap={"city":"samawah"})
    handler._actor=lambda:actor
    handler._valid_csrf=lambda supplied:csrf
    handler._read_json=lambda:data
    handler._send_json=lambda status,payload:setattr(handler,"response",(status,payload))
    http.post(handler)
    return handler.response


def test_blank_scoped_draft_retains_unknowns_and_preserves_candidate(case):
    store,job,candidate,data=case
    before=deepcopy(candidate)
    code,payload=call(case)
    assert code==200
    assert payload["missing_fields"]
    assert set(payload["assessment"]["checks"].values())=={"unknown"}
    assert payload["physical_release"] is payload["baseline_modified"] is payload["source_files_verified"] is False
    assert candidate==before
    folder=store.root/"planning-drafts"/("qualification-"+payload["draft_sha256"])
    assert json.loads((folder/"request.json").read_text())==data
    assert call(case)[1]==payload
    assert store.get(job["id"])["status"]=="completed"


@pytest.mark.parametrize("fault,expected",[("revision",403),("asset",403),("inner-scope",403),("hash",400),("candidate",400),("extra",400),("unknown-nested",400),("duplicate",400),("nonfinite",400),("overflow",400),("source",400)])
def test_malformed_or_stale_inputs_do_not_create_drafts(case,monkeypatch,fault,expected):
    store,job,candidate,data=case
    data=deepcopy(data)
    if fault=="revision":data["identity"]["configuration_revision"]="another"
    elif fault=="asset":data["identity"]["asset_id"]="another"
    elif fault=="hash":data["contract_sha256"]="0"*64
    elif fault=="candidate":data["candidate"]="absent"
    elif fault=="extra":data["physical_release"]=True
    elif fault in {"inner-scope","unknown-nested","nonfinite","overflow"}:
        proposal=json.loads(data["input_json"])
        if fault=="inner-scope":proposal["identity"]["environment"]="physical"
        elif fault=="unknown-nested":proposal["survey"]["approve_site"]=True
        else:proposal["survey"]["horizontal_uncertainty"]["value"]=float("nan") if fault=="nonfinite" else float("inf")
        data["input_json"]=json.dumps(proposal).replace("Infinity","1e999") if fault=="overflow" else json.dumps(proposal)
    elif fault=="duplicate":data["input_json"]='{"schema":1,"schema":2}'
    elif fault=="source":monkeypatch.setattr(http,"dependencies",lambda adapter:{"changed":"0"*64})
    assert call(case,data)[0]==expected
    assert not (store.root/"planning-drafts").exists()


@pytest.mark.parametrize("kwargs",[{"csrf":False},{"roles":["inspector"]},{"origin":False}])
def test_qualification_needs_existing_role_same_origin_and_csrf(case,kwargs):
    assert call(case,**kwargs)[0]==403
    assert not (case[0].root/"planning-drafts").exists()


def test_partial_site_records_execute_only_the_complete_source_qualified_block(case):
    data=deepcopy(case[3]);proposal=json.loads(data["input_json"])
    source=dict(reference="Clearly labelled numerical test fixture",sha256="a"*64,basis="research-assumption")
    proposal["layers"]=[dict(top=dict(value=0.,unit="m",source=source),bottom=dict(value=1.,unit="m",source=source),description="test layer",source=source)]
    data["input_json"]=json.dumps(proposal)
    code,payload=call(case,data)
    assert code==200
    assert payload["assessment"]["checks"]["ground_depth_coverage"]=="failed"
    assert payload["assessment"]["checks"]["survey"]=="unknown"
    assert payload["assessment"]["site_qualified"] is False


def test_null_manufacturing_and_prestress_templates_are_retained_without_new_baseline(case):
    for kind in ("manufacturing","prestress"):
        data=deepcopy(case[3]);data["kind"]=kind
        data["input_json"]=json.dumps(http.qualification_template(kind,case[2]["definition"]["contract"],scope()))
        code,payload=call(case,data)
        assert code==200
        assert payload["missing_fields"]
        assert payload["physical_release"] is payload["baseline_modified"] is False
        if kind=="prestress":assert payload["assessment"]["gross_demands"]["service"]["effective_prestress_force_n"]==0
        else:assert all(n==0 for n in payload["assessment"]["supplied_rule_counts"].values())


def test_complete_entered_manufacturing_rule_retains_failure_without_baseline_change(case):
    data=deepcopy(case[3]);contract=case[2]["definition"]["contract"]
    original=fingerprint(contract)
    data["kind"]="manufacturing"
    proposal=http.qualification_template("manufacturing",contract,scope())
    proposal["part_rules"][0].update(stock_bounds_m=[.001,.001,.001],minimum_wall_m=.0001,
                                   basis_reference="Clearly labelled numerical test fixture")
    data["input_json"]=json.dumps(proposal)
    code,payload=call(case,data)
    assert code==200
    assert payload["assessment"]["state"]=="failed"
    assert payload["assessment"]["supplied_rule_counts"]["part_rules"]==1
    assert fingerprint(contract)==original


def test_same_inputs_from_distinct_accounts_have_separate_immutable_audit(case):
    a=call(case,username="fixture-planner-a")[1]
    b=call(case,username="fixture-planner-b")[1]
    assert a["draft_sha256"]!=b["draft_sha256"]
    assert a["actor"]=="fixture-planner-a"
    assert b["actor"]=="fixture-planner-b"
    assert a["input_sha256"]==b["input_sha256"]
    assert call(case,username="fixture-planner-a")[1]==a


def test_interrupted_draft_publication_leaves_no_half_record_and_retry_succeeds(case,monkeypatch):
    from engineering.design_engine import store as store_module
    original=store_module.write_new
    def fail_assessment(path,value):
        if path.name=="assessment.json":raise OSError("Injected test interruption before atomic publish")
        return original(path,value)
    monkeypatch.setattr(store_module,"write_new",fail_assessment)
    assert call(case)[0]==400
    assert list((case[0].root/"planning-drafts").iterdir())==[]
    monkeypatch.setattr(store_module,"write_new",original)
    assert call(case)[0]==200

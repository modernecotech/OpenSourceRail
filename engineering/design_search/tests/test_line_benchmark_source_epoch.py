from pathlib import Path
from copy import deepcopy
import json
import pytest
from engineering.station_rail.common import digest, identity

from engineering.design_search import line_benchmark_retained


ROOT = Path(__file__).resolve().parents[3]


def test_line30_benchmark_is_integrity_verified_under_its_historical_source_epoch():
    report = line_benchmark_retained.verify(ROOT)

    assert report["verified"] is True
    assert report["current_source_valid"] is False
    result=json.loads((ROOT/line_benchmark_retained.PACKAGE/"result.json").read_bytes())
    assert report["requirements_id"]==result["requirements_id"]
    assert report["requirements_id"]==identity(result["functional_requirements"])
    assert report["source_epoch"] == "historical"
    expected={line_benchmark_retained.SOURCE}
    if digest(ROOT/line_benchmark_retained.COST_SOURCE)!=line_benchmark_retained.COST_HASH:
        expected.add(line_benchmark_retained.COST_SOURCE)
    assert set(report["historical_source_paths"]) == expected
    assert report['retained_cost_receipt_id']==line_benchmark_retained.COST_RECEIPT_ID
    assert report["analytical_replay"] is False
    assert report["numerical_reexecuted"] is False
    assert report["native_solver_jobs"] == 0
    assert report["physical_accepted"] is False
    assert report["engineering_accepted"] is False
    assert report["current_evaluator_admission"] is False


def test_retained_requirement_identity_cannot_be_relabelled(monkeypatch):
    original=line_benchmark_retained.line_benchmark.validate_result
    def reject_changed_requirement(value,root,**kwargs):
        bad=deepcopy(value);bad['requirements_id']='0'*64
        bad['evaluation_id']=identity({k:v for k,v in bad.items() if k!='evaluation_id'})
        original(bad,root,**kwargs)
    monkeypatch.setattr(line_benchmark_retained.line_benchmark,'validate_result',reject_changed_requirement)
    with pytest.raises(ValueError,match='requirements identity differs'):line_benchmark_retained.verify(ROOT)


def test_explicit_retained_cli_does_not_claim_current_replay(capsys):
    line_benchmark_retained.main([])
    report=json.loads(capsys.readouterr().out)
    assert report['source_epoch']=='historical' and report['current_source_valid'] is False
    assert report['analytical_replay'] is False and report['native_solver_jobs']==0


def test_new_selected_cost_does_not_reprice_retained_line30(tmp_path, monkeypatch):
    old_file=line_benchmark_retained._file
    current=tmp_path/'new-selected-cost.json'
    current.write_text('{"new_selected_evaluation":true}\n')
    def changed_cost(root,relative,**kwargs):
        return current if relative==line_benchmark_retained.COST_SOURCE else old_file(root,relative,**kwargs)
    monkeypatch.setattr(line_benchmark_retained,'_file',changed_cost)
    report=line_benchmark_retained.verify(ROOT)
    assert set(report['historical_source_paths'])=={
        line_benchmark_retained.SOURCE,line_benchmark_retained.COST_SOURCE}
    benchmark=line_benchmark_retained.historical_baseline(ROOT)
    assert benchmark['evaluation_id']==line_benchmark_retained.EVALUATION_ID
    assert benchmark['vehicle_cost_estimate_id']==line_benchmark_retained.COST_ESTIMATE_ID
    assert report['current_evaluator_admission'] is False


@pytest.mark.parametrize('target',('receipt','source'))
def test_retained_selected_cost_archive_rejects_tampering(tmp_path,monkeypatch,target):
    old_file=line_benchmark_retained._file
    path=tmp_path/'tampered.json'
    named=(line_benchmark_retained.COST_RECEIPT if target=='receipt'
           else line_benchmark_retained.COST_ARTIFACT)
    if target=='receipt':
        receipt=json.loads((ROOT/named).read_bytes());receipt['source_commit']='0'*40
        path.write_text(json.dumps(receipt))
    else:
        path.write_bytes((ROOT/named).read_bytes()+b' ')
    def replaced(root,relative,**kwargs):
        return path if relative==named else old_file(root,relative,**kwargs)
    monkeypatch.setattr(line_benchmark_retained,'_file',replaced)
    with pytest.raises(ValueError,match='retained selected-cost'):
        line_benchmark_retained.verify(ROOT)

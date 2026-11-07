from copy import deepcopy
import json
import pytest
from engineering.design_search.craft_backends import viaduct_workflow as w,viaduct_replay as replay


def test_unknown_numerical_performance_is_never_a_zero_score(tmp_path):
    (tmp_path/'request.json').write_text(json.dumps(dict(evaluation_id='evaluation')))
    result=dict(result_id='result',evaluation_id='evaluation',levels=dict(coarse=dict(state='held'),fine=dict(state='held')),refinement=None)
    value=w.numerical_summary(result,tmp_path)
    assert value['numerical_screen_passed'] is False
    assert value['displacement_refinement_relative'] is None
    assert value['levels']['fine']['fieldcraft_midspan_uz_m'] is None


def test_resealed_evaluation_or_incomplete_mesh_coverage_is_rejected(tmp_path):
    (tmp_path/'request.json').write_text(json.dumps(dict(evaluation_id='expected')))
    result=dict(result_id='result',evaluation_id='other',levels=dict(coarse=dict(state='held'),fine=dict(state='held')),refinement=None)
    with pytest.raises(ValueError,match='evaluation identity'):w.numerical_summary(result,tmp_path)
    result['evaluation_id']='expected';result['levels'].pop('fine')
    with pytest.raises(ValueError,match='mesh-level coverage'):w.numerical_summary(result,tmp_path)


def test_process_accounting_recomputed_from_actual_inventory(tmp_path):
    folder=tmp_path/'worker';folder.mkdir();(folder/'execution.json').write_text('{}')
    value=dict(cad_source_path=str(tmp_path.parent/'external-cad'),fresh_native_invocations=1,imported_CAD_native_invocations=13)
    w.verify_process_counts(value,tmp_path,dict(native_processes=13))
    bad=deepcopy(value);bad['fresh_native_invocations']=0
    with pytest.raises(ValueError,match='execution accounting'):w.verify_process_counts(bad,tmp_path,dict(native_processes=13))


def test_replay_interpreter_entrypoint_is_preserved_not_resolved(monkeypatch):
    import subprocess
    observed=[]
    def run(args,**kw):
        observed.append(args)
        return subprocess.CompletedProcess(args,0,stdout='{"runtime":{},"verification":null}',stderr='')
    monkeypatch.setattr(replay.subprocess,'run',run)
    replay.invoke(python='/usr/bin/python3')
    assert observed[0][0]=='/usr/bin/python3'
    with pytest.raises(ValueError,match='supported numerical replay'):replay.invoke(python='/tmp/untrusted-python')

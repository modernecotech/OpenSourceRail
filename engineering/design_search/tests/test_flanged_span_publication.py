"""Small synthetic records; no actual candidate input or numerical run is touched."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from engineering.station_rail.common import encoded, identity
from engineering.design_search import flanged_span_publication as p


def seal(value, key):
    value[key] = identity(value)
    return value


@pytest.fixture
def experiment(tmp_path, monkeypatch):
    root = tmp_path / 'root'
    producer = root / p.PRODUCER
    producer.parent.mkdir(parents=True)
    shutil.copyfile(p.__file__, producer)
    state = tmp_path / 'state';state.mkdir()
    (state / 'run.py').write_bytes(b'# supplied worker source\n')
    (state / 'execution.log').write_bytes(b'supplied worker log\n')
    context = seal(dict(schema='test-context',source_sha256={'example.py':'a'*64},**p.FLAGS),'context_id')
    assumptions = {'schema':'test-spec'}
    expected = {}
    for i, name in enumerate(p.NAMES):
        folder = state / name;folder.mkdir()
        candidate = dict(gauge=name,candidate_id=str(i+1)*64,geometry_id=str(i+4)*64)
        q = seal(dict(candidate_id=candidate['candidate_id'],accounted_mass_kg_cases=dict(low=1.,base=2.,high=3.),
            complete_installed_mass_kg=None,**p.FLAGS),'evaluation_id')
        a = seal(dict(candidate_id=candidate['candidate_id'],quantity_evaluation_id=q['evaluation_id'],load_context_id=context['context_id'],
            EI_Nm2=42.,responses=[dict(response=dict(deflection_at_observation_m=[0.,.1])) for _ in range(81)],
            all_position_model_bounds=[dict(all_position_model_deflection_upper_m=.2) for _ in range(27)],
            engineering_screen='unresolved',integrated_selection=None,numerical_validity='test',holds=['physical test pending'],**p.FLAGS),'evaluation_id')
        c = seal(dict(candidate_id=candidate['candidate_id'],quantity_evaluation_id=q['evaluation_id'],whole_system_ranking_allowed=False,
            complete_installed_cost_iqd=None,lifecycle_cost_iqd=None,
            cases={k:dict(scoped_installed_iqd=100.,factory_labour_hours={'work':8.}) for k in ('low','base','high')},**p.FLAGS),'evaluation_id')
        request=seal(dict(schema='osr-flanged-span-stage1-request/1',candidate=candidate,context=context,assumptions=assumptions,
            runtime_budget=dict(address_space_bytes=1073741824,cpu_seconds=240,wall_seconds=300,workers=1),disposition=p.DISPOSITION),'request_id')
        result=seal(dict(schema='osr-flanged-span-stage1-result/1',request_id=request['request_id'],candidate_id=candidate['candidate_id'],
            quantities=q,analysis=a,cost=c,execution='completed'),'result_id')
        (folder/'request.json').write_bytes(encoded(request));(folder/'result.json').write_bytes(encoded(result))
        expected[name]=dict(request=request,result=result)
    def candidate_check(c):
        if c != expected[c['gauge']]['request']['candidate']:raise ValueError('candidate mismatch')
    def context_check(c, _root):
        if c != context:raise ValueError('context mismatch')
    monkeypatch.setattr(p.span,'_candidate',candidate_check)
    monkeypatch.setattr(p.span,'_context',context_check)
    monkeypatch.setattr(p.span,'_spec',lambda s:s)
    monkeypatch.setattr(p.span,'load_context',lambda _root:deepcopy(context))
    monkeypatch.setattr(p.span,'quantities',lambda c, s:deepcopy(expected[c['gauge']]['result']['quantities']))
    monkeypatch.setattr(p.span,'estimate',lambda c, q, s:deepcopy(expected[c['gauge']]['result']['cost']))
    monkeypatch.setattr(p.span,'evaluate',lambda c, x, s, root:deepcopy(expected[c['gauge']]['result']['analysis']))
    monkeypatch.setattr(subprocess,'Popen',lambda *_a,**_k:pytest.fail('native dispatch is forbidden'))
    return root,state,expected


def test_archive_preserves_original_and_replays_without_promoting(experiment,tmp_path):
    root,state,expected=experiment;out=tmp_path/'packet'
    manifest=p.publish(state,root=root,output=out);verified=p.verify(out,root=root)
    assert verified['verified'] and verified['completed']==3 and verified['native_solver_executed'] is False
    assert verified['physical_accepted'] is False and verified['integrated_selection'] is None
    assert (out/'original/baseline/result.json').read_bytes()==(state/'baseline/result.json').read_bytes()
    result=json.loads((out/'result.json').read_bytes());row=result['attempts'][0]
    assert row['analysis_evaluation_id']==expected['baseline']['result']['analysis']['evaluation_id']
    assert row['factory_person_hours']['base']==8. and row['engineering_screen']=='unresolved'
    assert manifest['source_sha256'][p.PRODUCER]
    with pytest.raises(ValueError,match='New publication'):p.publish(state,root=root,output=out)
    with pytest.raises(ValueError,match='separate'):p.publish(state,root=root,output=state/'nested')


def test_failure_and_unattempted_are_preserved_without_invention(experiment,tmp_path):
    root,state,_=experiment
    (state/'baseline/result.json').unlink();(state/'baseline/failure.txt').write_text('original failure\n')
    shutil.rmtree(state/'thick-web')
    out=tmp_path/'packet';p.publish(state,root=root,output=out)
    result=json.loads((out/'result.json').read_bytes())
    assert [v['execution'] for v in result['attempts']]==['recorded-failure','not-attempted','completed']
    assert (out/'original/baseline/failure.txt').read_text()=='original failure\n'
    assert result['attempts'][1]['candidate_id'] is None


@pytest.mark.parametrize('damage',['request','candidate','result','quantity','analysis','cost','promotion','coverage','both','budget','context'])
def test_resealed_bad_attempts_fail_semantic_gates(experiment,tmp_path,damage):
    root,state,_=experiment;folder=state/'baseline'
    request=json.loads((folder/'request.json').read_bytes());result=json.loads((folder/'result.json').read_bytes())
    if damage=='request':result['request_id']='0'*64
    elif damage=='candidate':result['candidate_id']='0'*64
    elif damage=='result':result['execution']='passed'
    elif damage=='quantity':result['quantities']['accounted_mass_kg_cases']['base']+=1;result['quantities'].pop('evaluation_id');seal(result['quantities'],'evaluation_id')
    elif damage=='analysis':result['analysis']['EI_Nm2']+=1;result['analysis'].pop('evaluation_id');seal(result['analysis'],'evaluation_id')
    elif damage=='cost':result['cost']['cases']['base']['scoped_installed_iqd']+=1;result['cost'].pop('evaluation_id');seal(result['cost'],'evaluation_id')
    elif damage=='promotion':result['analysis']['physical_accepted']=True;result['analysis'].pop('evaluation_id');seal(result['analysis'],'evaluation_id')
    elif damage=='coverage':result['analysis']['responses'].pop();result['analysis'].pop('evaluation_id');seal(result['analysis'],'evaluation_id')
    elif damage=='both':(folder/'failure.txt').write_text('failure too')
    elif damage=='budget':request['runtime_budget']['cpu_seconds']=500;request.pop('request_id');seal(request,'request_id');result['request_id']=request['request_id']
    else:request['context']['context_id']='0'*64;request.pop('request_id');seal(request,'request_id');result['request_id']=request['request_id']
    result.pop('result_id');seal(result,'result_id')
    (folder/'request.json').write_bytes(encoded(request));(folder/'result.json').write_bytes(encoded(result))
    with pytest.raises(ValueError):p.publish(state,root=root,output=tmp_path/'packet')


def test_modification_extra_file_and_symlink_rejected(experiment,tmp_path):
    root,state,_=experiment;out=tmp_path/'packet';p.publish(state,root=root,output=out)
    (out/'original/baseline/result.json').write_bytes(b'{}\n')
    with pytest.raises(ValueError):p.verify(out,root=root)
    (out/'original/baseline/result.json').write_bytes((state/'baseline/result.json').read_bytes())
    (out/'extra').write_text('unaudited')
    with pytest.raises(ValueError):p.verify(out,root=root)
    (out/'extra').unlink();(out/'original'/'manifest.json').write_text('unaudited')
    with pytest.raises(ValueError):p.verify(out,root=root)
    (out/'original'/'manifest.json').unlink();(out/'linked').symlink_to(out/'result.json')
    with pytest.raises(ValueError):p.verify(out,root=root)


def test_source_changed_and_mixed_context_rejected(experiment,tmp_path):
    root,state,_=experiment
    with (root/p.PRODUCER).open('a') as handle:handle.write('# changed\n')
    with pytest.raises(ValueError,match='publication source'):p.publish(state,root=root,output=tmp_path/'packet')

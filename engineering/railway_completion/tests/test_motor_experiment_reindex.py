"""Exact raw transport controls; disposable backend never executes a motor."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from engineering.railway_completion import experiments as e
from engineering.station_rail.common import identity,encoded,digest


def write(path,value):Path(path).write_bytes(encoded(value))
def read(path):return json.loads(Path(path).read_bytes())
def seal_index(path,value):
    value['experiment_id']=identity({k:v for k,v in value.items() if k not in ('new_runs','experiment_id')});write(path/'latest.json',value)


@pytest.fixture
def execution(tmp_path,monkeypatch):
    tool=dict(python='typed-python',python_sha256='a'*64,numpy='typed-numpy',scipy='typed-scipy',superlu_sha256='b'*64)
    old={'broad.py':'1'*64,e.PRODUCER:'2'*64};current={'broad.py':'3'*64,e.PRODUCER:'4'*64};narrow={'method.py':'c'*64};definitions=[];proofs=[]
    for i in range(8):
        request=dict(name='case-'+str(i),bundle_id='bundle-'+str(i),motor_component_id='motor-'+str(i),maximum_seconds=10.,memory_bytes=1024**3,method='same-method');request['request_id']=identity(request)
        definitions.append(dict(name=request['name'],request=request,purpose='method-control' if i<4 else 'candidate-screen'))
    def bound(request):return dict(passes_declared_sinusoidal_bound=request['name'] not in ('case-4','case-5'),basis='typed necessary bound')
    def held(request):
        value=dict(execution='held-necessary-bound',bundle_id=request['bundle_id'],motor_component_id=request['motor_component_id'],request_id=request['request_id'],state='typed hold',trace=[],electrical_bound=bound(request),**e.FLAGS);value['evaluation_id']=identity(value);return value
    def forbidden(*args,**kwargs):raise AssertionError('No solver may execute during reindex')
    monkeypatch.setattr(e,'cases',lambda root:deepcopy(definitions));monkeypatch.setattr(e,'source_epoch',lambda root:deepcopy(current));monkeypatch.setattr(e,'electrical_bound',bound);monkeypatch.setattr(e,'_held',held);monkeypatch.setattr(e.motor,'run',forbidden);monkeypatch.setattr(e.motor,'_tool',lambda request:deepcopy(tool))
    def verify(path,*,root,require_current_tool=True,replay=False):
        assert replay is False;path=Path(path);manifest=read(path/'manifest.json');data=read(path/'input.json');result=read(path/'result.json');recorded=read(path/'tool.json')
        if manifest['files']!={p.name:digest(p) for p in path.iterdir() if p.name!='manifest.json'}:raise ValueError('typed raw payload tampering')
        if read(path/'narrow.json')!=narrow:raise ValueError('typed narrow method/source mismatch')
        if require_current_tool and recorded!=tool:raise ValueError('typed tool mismatch')
        if data['request']['memory_bytes']!=1024**3:raise ValueError('typed resources mismatch')
        proof=dict(verified=True,recorded_tool_identity=recorded,current_tool_identity=tool,require_current_tool=require_current_tool,independent_execution_attempted=False,request_id=data['request']['request_id'],evaluation_id=result['evaluation_id'],execution=result['execution']);proofs.append(proof);return proof
    monkeypatch.setattr(e.motor,'verify',verify)
    state=tmp_path/'original';state.mkdir();rows=[]
    for i,definition in enumerate(definitions):
        request=definition['request'];key=identity(dict(request_id=request['request_id'],source_sha256=old,tool_identity=tool));output=state/'runs'/key;output.mkdir(parents=True)
        if i in (4,5):
            result=held(request);write(output/'input.json',dict(request=request,source_sha256=old))
        else:
            result=dict(execution='interrupted' if i>=6 else 'completed',bundle_id=request['bundle_id'],motor_component_id=request['motor_component_id'],request_id=request['request_id'],state='typed-no-numerical-evidence',trace=[],**e.FLAGS);result['evaluation_id']=identity(result)
            write(output/'input.json',dict(request=request,source_sha256=narrow));write(output/'tool.json',tool);write(output/'narrow.json',narrow);(output/'partial-trace.jsonl').write_bytes(b'opaque original partial bytes\x00\n')
        write(output/'result.json',result)
        if i not in (4,5):write(output/'manifest.json',dict(files={p.name:digest(p) for p in output.iterdir()}))
        rows.append(dict(output='runs/'+key,request=request,purpose=definition['purpose'],electrical_bound=bound(request),summary=e._summary(definition['name'],result)))
    index=dict(schema='osr-configured-motor-experiment/1',source_sha256=old,tool_identity=tool,rows=rows,pending=[],new_runs=8,integrated_selection=None,**e.FLAGS);seal_index(state,index)
    return dict(state=state,index=index,old=old,current=current,tool=tool,narrow=narrow,definitions=definitions,proofs=proofs,target=tmp_path/'new')


def test_reindex_preserves_completed_and_interrupted_raw_bytes_and_refreshes_holds(execution):
    x=execution;before=e._inventory(x['state']);value=e.reindex(x['state'],x['target'])
    assert value['new_runs']==0 and value['source_sha256']==x['current'] and value['pending']==[]
    assert e._inventory(x['state'])==before
    assert (x['target']/'origin-index.json').read_bytes()==(x['state']/'latest.json').read_bytes()
    assert [r['summary']['execution'] for r in value['rows']].count('interrupted')==2
    for old,new in zip(x['index']['rows'],value['rows']):
        assert old['output']!=new['output']
        if old['summary']['execution']=='held-necessary-bound':
            assert read(x['target']/new['output']/'input.json')['source_sha256']==x['current']
            assert read(x['state']/old['output']/'input.json')['source_sha256']==x['old']
        else:
            assert e._inventory(x['target']/new['output'])==e._inventory(x['state']/old['output'])
            assert old['summary']['evaluation_id']==new['summary']['evaluation_id']
    assert any(p['require_current_tool'] for p in x['proofs'])
    assert all(value[k] is False for k in e.FLAGS)
    assert e.verify_index(x['target'])['experiment_id']==value['experiment_id']


@pytest.mark.parametrize('mutation',['unsealed','duplicate','missing','request','method','resources','tool','path','source-path'])
def test_changed_original_index_or_request_contract_rejected(execution,mutation):
    x=execution;value=deepcopy(x['index'])
    if mutation=='unsealed':value['integrated_selection']='tampered'
    elif mutation=='duplicate':value['rows'][-1]=deepcopy(value['rows'][0])
    elif mutation=='missing':value['rows'].pop()
    elif mutation in ('request','method','resources'):
        key={'request':'request_id','method':'method','resources':'maximum_seconds'}[mutation];value['rows'][0]['request'][key]='different'
    elif mutation=='tool':value['tool_identity']['python']='different tool'
    elif mutation=='path':value['rows'][0]['output']='../escape'
    else:value['source_sha256']['../escaped.py']='d'*64
    if mutation=='unsealed':write(x['state']/'latest.json',value)
    else:seal_index(x['state'],value)
    with pytest.raises(ValueError):e.reindex(x['state'],x['target'])
    assert not (x['target']/'latest.json').exists()


@pytest.mark.parametrize('mutation',['method','tool','resources','indexed-request','raw-tamper'])
def test_narrow_source_tool_resources_and_actual_native_request_are_verified_before_reuse(execution,mutation):
    x=execution;path=x['state']/x['index']['rows'][0]['output']
    if mutation=='method':write(path/'narrow.json',{'method.py':'e'*64})
    elif mutation=='tool':write(path/'tool.json',dict(x['tool'],numpy='different'))
    elif mutation in ('resources','indexed-request'):
        data=read(path/'input.json');data['request']['memory_bytes' if mutation=='resources' else 'method']=2*1024**3 if mutation=='resources' else 'different';write(path/'input.json',data)
    else:(path/'partial-trace.jsonl').write_bytes(b'changed')
    if mutation!='raw-tamper':write(path/'manifest.json',dict(files={p.name:digest(p) for p in path.iterdir() if p.name!='manifest.json'}))
    with pytest.raises(ValueError):e.reindex(x['state'],x['target'])


def test_origin_index_and_raw_provenance_are_checked_after_publication(execution,tmp_path):
    x=execution;value=e.reindex(x['state'],x['target']);output=tmp_path/'publication';e.publish(x['target'],output)
    assert e.verify_publication(output)['verified']
    origin=read(x['target']/'origin-index.json');origin['rows'][0]['summary']['execution']='forged';write(x['target']/'origin-index.json',origin)
    with pytest.raises(ValueError):e.verify_index(x['target'])


def test_existing_output_and_linked_source_are_never_overwritten(execution,tmp_path):
    x=execution;x['target'].mkdir();(x['target']/'keep').write_text('user data')
    with pytest.raises(ValueError):e.reindex(x['state'],x['target'])
    assert (x['target']/'keep').read_text()=='user data'
    alias=tmp_path/'linked';alias.symlink_to(x['state'],target_is_directory=True)
    with pytest.raises(ValueError):e.reindex(alias,tmp_path/'other')


def test_generic_run_cannot_erase_reindex_provenance(execution):
    x=execution;e.reindex(x['state'],x['target']);before=(x['target']/'latest.json').read_bytes()
    with pytest.raises(ValueError,match='immutable'):e.run(x['target'],maximum_new_runs=0)
    assert (x['target']/'latest.json').read_bytes()==before


def test_partial_reindex_after_source_mutation_remains_unpublishable(execution,monkeypatch):
    x=execution;copy=e.shutil.copytree;changed=[]
    def copying(source,target,*args,**kwargs):
        result=copy(source,target,*args,**kwargs)
        if not changed and (Path(source)/'partial-trace.jsonl').exists():
            (Path(source)/'partial-trace.jsonl').write_bytes(b'concurrent source change');changed.append(True)
        return result
    monkeypatch.setattr(e.shutil,'copytree',copying)
    with pytest.raises(ValueError,match='changed during'):e.reindex(x['state'],x['target'])
    assert (x['target']/'reindex-failure.txt').exists()
    with pytest.raises(ValueError,match='partial reindex'):e.verify_index(x['target'])

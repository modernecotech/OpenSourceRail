import errno
import hashlib
import json
import os
from copy import deepcopy
from pathlib import Path

import pytest

from engineering.design_search import railway_campaign as campaign
from engineering.design_search import design_grammar as grammar
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded, identity


def legacy_semantic(value):
    def clean(node):
        if isinstance(node, dict):
            return {k: clean(v) for k, v in node.items() if k not in (
                'campaign_id', 'run_id', 'new_bundles', 'reused_bundles',
                'new_native_jobs', 'reused_native_jobs', 'requested_native_jobs', 'reused')}
        if isinstance(node, list):
            return [clean(v) for v in node]
        return node
    return identity(clean(value))


def sample():
    value = {'schema': 'test-campaign', 'rows': [
        {'case_context_id':'1'*64,'candidate_id': 'one', 'value': [1.2, -0.0, '🚆'], 'reused': True},
        {'case_context_id':'2'*64,'candidate_id': 'two', 'value': ({'reused': 'tuple remains untouched'},)},
    ], 'contract_id':'3'*64,'source_sha256':{'producer':'4'*64},'new_bundles': 1, 'reused_bundles': 1,
        'integrated_selection': None, 'selected_reference_changed': False,
        **campaign.FLAGS}
    for row in value['rows']:row['row_id']=identity(row)
    value['campaign_id'] = legacy_semantic(value)
    value['run_id'] = identity(value)
    return value


def test_canonical_hashes_equal_original_including_tuple_omissions():
    value = sample()
    assert campaign.semantic_id(value) == legacy_semantic(value)
    run_input = {k: v for k, v in value.items() if k != 'run_id'}
    assert campaign._aggregate_identity(run_input) == identity(run_input) == value['run_id']


def test_case_write_streams_exact_bytes_and_keeps_prior_on_failure(tmp_path, monkeypatch):
    path = tmp_path/'case.json'
    value = {'candidate_id': 'one', 'trace': list(range(5000)), 'unknown': None}
    campaign._write(path, value)
    assert path.read_bytes() == encoded(value)
    previous = path.read_bytes()
    def interrupted(value, output):
        output.write(b'incomplete')
        raise OSError(errno.ENOSPC, 'full')
    monkeypatch.setattr(campaign.canonical_stream, 'write_canonical', interrupted)
    with pytest.raises(OSError) as exc:
        campaign._write(path, {'candidate_id': 'two'})
    assert exc.value.errno == errno.ENOSPC
    assert path.read_bytes() == previous
    assert len(list(tmp_path.glob('.case.json.*.pending'))) == 1


def test_nonstring_keys_fail_closed_in_campaign_identity():
    value = {'nested': {1: 'one', 2: ['two', {'reused': True}]}}
    with pytest.raises(TypeError,match='built-in string object keys'):
        campaign.semantic_id(value)
    with pytest.raises(TypeError,match='built-in string object keys'):
        campaign._aggregate_identity(value)


def write_case_shards(folder,value):
    for row in value['rows']:
        path=campaign.case_node_store.path_for(folder/'cases',row['case_context_id'])
        campaign.case_node_store.write(path,row,'case')


def test_arrow_aggregate_streams_exact_bytes_without_json_clones(tmp_path):
    from io import BytesIO
    value=sample();write_case_shards(tmp_path,value)
    pointer=campaign._write_aggregate(tmp_path,value)
    snapshot,checked=campaign.current_aggregate(tmp_path,value['contract_id'])
    sink=BytesIO();manifest=campaign.aggregate_store.read(snapshot,tmp_path/'cases',sink)
    assert sink.getvalue()==encoded(value)
    assert checked==pointer and manifest['aggregate_sha256']==pointer['aggregate_sha256']
    assert not (tmp_path/'result.json').exists() and not (tmp_path/'invocations').exists()
    assert value['integrated_selection'] is None and all(value[k] is False for k in campaign.FLAGS)


def test_same_run_reuses_verified_immutable_aggregate(tmp_path):
    value=sample();write_case_shards(tmp_path,value)
    first=campaign._write_aggregate(tmp_path,value)
    snapshot,_=campaign.current_aggregate(tmp_path,value['contract_id'])
    before={p.name:p.stat().st_ino for p in snapshot.iterdir()}
    assert campaign._write_aggregate(tmp_path,value)==first
    assert before=={p.name:p.stat().st_ino for p in snapshot.iterdir()}


def test_corrupt_existing_aggregate_fails_without_advancing_pointer(tmp_path):
    value=sample();write_case_shards(tmp_path,value)
    campaign._write_aggregate(tmp_path,value)
    pointer=(tmp_path/'aggregate-current.json').read_bytes()
    snapshot,_=campaign.current_aggregate(tmp_path,value['contract_id'])
    core=snapshot/'core.parquet';core.write_bytes(core.read_bytes()[:12])
    with pytest.raises(ValueError,match='Parquet part hash'):
        campaign._write_aggregate(tmp_path,value)
    assert (tmp_path/'aggregate-current.json').read_bytes()==pointer


def test_interrupted_aggregate_retains_pending_evidence(tmp_path,monkeypatch):
    value=sample();write_case_shards(tmp_path,value)
    def interrupted(*args,**kwargs):raise OSError(errno.ENOSPC,'full')
    monkeypatch.setattr(campaign.aggregate_store,'_write_component',interrupted)
    with pytest.raises(OSError) as exc:campaign._write_aggregate(tmp_path,value)
    assert exc.value.errno==errno.ENOSPC
    assert not (tmp_path/'aggregate-current.json').exists()
    assert list((tmp_path/'aggregates').glob('.*.pending'))


def test_source_epoch_binds_stream_implementation_and_detects_change(tmp_path, monkeypatch):
    rust_name='crates/osr-design-search/src/case_nodes.rs'
    rust=tmp_path/rust_name;rust.parent.mkdir(parents=True);rust.write_text('rust implementation')
    def codec_sources(root):
        return {rust_name:hashlib.sha256((Path(root)/rust_name).read_bytes()).hexdigest()}
    monkeypatch.setattr(campaign.case_node_store,'codec_source_identity',codec_sources)
    names = []
    def collect(path):
        names.append(Path(path).relative_to(tmp_path).as_posix())
        return '0'*64
    real_digest=campaign.digest
    monkeypatch.setattr(campaign, 'digest', collect)
    first=campaign.source_epoch(tmp_path)
    assert 'engineering/design_search/canonical_stream.py' in names
    assert first[rust_name]==hashlib.sha256(rust.read_bytes()).hexdigest()
    for name in set(names):
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(name)
    monkeypatch.setattr(campaign, 'digest', real_digest)
    before=campaign.source_epoch(tmp_path)
    stream=tmp_path/'engineering/design_search/canonical_stream.py'
    stream.write_text('changed implementation')
    after=campaign.source_epoch(tmp_path)
    assert before[stream.relative_to(tmp_path).as_posix()] != after[stream.relative_to(tmp_path).as_posix()]
    assert identity(before) != identity(after)
    rust.write_text('changed rust implementation')
    assert campaign.source_epoch(tmp_path)[rust_name]!=after[rust_name]
    stream.unlink()
    with pytest.raises(FileNotFoundError):campaign.source_epoch(tmp_path)


def test_old_source_case_cannot_be_reused_even_at_explicit_state():
    epoch={'campaign.py':'a'*64};bundle={'definition_id':'b'*64};context='c'*64
    row={'case_context_id':context,'bundle_definition_id':bundle['definition_id'],
         'stages':[{'stage':name,'request':{'source_sha256':dict(epoch)}} for name in campaign.STAGES]}
    row['row_id']=identity(row)
    campaign._validate_cached_row(row,context,bundle,epoch)
    with pytest.raises(ValueError,match='source epoch'):
        campaign._validate_cached_row(row,context,bundle,{'campaign.py':'d'*64})
    row['stages'][0]['request'].pop('source_sha256')
    row['row_id']=identity({k:v for k,v in row.items() if k!='row_id'})
    with pytest.raises(ValueError,match='source epoch'):
        campaign._validate_cached_row(row,context,bundle,epoch)


def test_state_marker_rejects_foreign_contract_before_native_work(tmp_path,monkeypatch):
    from contextlib import nullcontext
    import engineering.performance as performance
    monkeypatch.setattr(performance,'disk_reservation',lambda *args,**kwargs:nullcontext(None))
    spec={'schema':'fixture','maximum_native_jobs':12,'maximum_bundle_cases':0};epoch={'producer':'a'*64}
    monkeypatch.setattr(campaign,'specification',lambda root:spec)
    monkeypatch.setattr(campaign,'source_epoch',lambda root:epoch)
    monkeypatch.setattr(campaign,'generate_bodies',lambda:pytest.fail('must reject before body/native work'))
    (tmp_path/'journal.json').write_bytes(encoded({'contract_id':'foreign'}))
    with pytest.raises(ValueError,match='journal contract'):
        campaign.run(root=tmp_path,state=tmp_path,native_jobs=0)
    assert not (tmp_path/'source-contract.json').exists()


def test_state_marker_preserves_same_source_interrupted_stages(tmp_path):
    epoch={'producer':'a'*64};contract='b'*64
    campaign._bind_state_source(tmp_path,contract,epoch)
    pending=tmp_path/'stages/pending.parquet.pending';pending.parent.mkdir();pending.write_bytes(b'partial')
    campaign._bind_state_source(tmp_path,contract,epoch)
    assert pending.read_bytes()==b'partial'
    with pytest.raises(ValueError,match='source contract'):
        campaign._bind_state_source(tmp_path,'c'*64,epoch)
    assert pending.read_bytes()==b'partial'


def test_unbound_existing_cache_is_preserved_and_rejected(tmp_path):
    cache=tmp_path/'native/jobs/existing';cache.parent.mkdir(parents=True);cache.write_bytes(b'old evidence')
    with pytest.raises(ValueError,match='unbound existing cache'):
        campaign._bind_state_source(tmp_path,'b'*64,{'producer':'a'*64})
    assert cache.read_bytes()==b'old evidence'
    assert not (tmp_path/'source-contract.json').exists()


@pytest.mark.parametrize('cache_name',['cases','stages','native'])
def test_matching_untrusted_journal_cannot_adopt_unbound_cache(tmp_path,cache_name):
    epoch={'producer':'a'*64};contract='b'*64
    journal=tmp_path/'journal.json';journal.write_bytes(encoded({'contract_id':contract}))
    saved_journal=journal.read_bytes()
    cache=tmp_path/cache_name/'existing';cache.parent.mkdir();cache.write_bytes(b'preserve old evidence')
    with pytest.raises(ValueError,match='unbound existing cache'):
        campaign._bind_state_source(tmp_path,contract,epoch)
    assert cache.read_bytes()==b'preserve old evidence'
    assert journal.read_bytes()==saved_journal
    assert not (tmp_path/'source-contract.json').exists()


def test_symlink_state_marker_is_rejected(tmp_path):
    external=tmp_path/'external';external.write_text('{}');(tmp_path/'source-contract.json').symlink_to(external)
    with pytest.raises(ValueError,match='ordinary file'):
        campaign._bind_state_source(tmp_path,'b'*64,{'producer':'a'*64})


@pytest.mark.parametrize('cache_name',['cases','stages','native'])
def test_marker_does_not_allow_symlinked_cache_directories(tmp_path,cache_name):
    epoch={'producer':'a'*64};contract='b'*64
    campaign._bind_state_source(tmp_path,contract,epoch)
    marker=(tmp_path/'source-contract.json').read_bytes()
    external=tmp_path/'external';external.mkdir();(external/'evidence').write_bytes(b'preserve')
    (tmp_path/cache_name).symlink_to(external,target_is_directory=True)
    with pytest.raises(ValueError,match='cache directories'):
        campaign._bind_state_source(tmp_path,contract,epoch)
    assert (tmp_path/'source-contract.json').read_bytes()==marker
    assert (external/'evidence').read_bytes()==b'preserve'


def test_state_and_ancestor_symlinks_are_rejected_before_creation(tmp_path):
    external=tmp_path/'external';external.mkdir();link=tmp_path/'link';link.symlink_to(external,target_is_directory=True)
    for path in (link,link/'state'):
        with pytest.raises(ValueError,match='state path and ancestors'):
            campaign._ordinary_state_path(path)
    assert not (external/'state').exists()
    with pytest.raises(ValueError,match='parent traversal'):
        campaign._ordinary_state_path(tmp_path/'subdir/../state')


def test_symlink_lock_rejected_before_open(tmp_path,monkeypatch):
    from contextlib import nullcontext
    import engineering.performance as performance
    monkeypatch.setattr(performance,'disk_reservation',lambda *args,**kwargs:nullcontext(None))
    spec={'schema':'fixture','maximum_native_jobs':12,'maximum_bundle_cases':0};epoch={'producer':'a'*64}
    monkeypatch.setattr(campaign,'specification',lambda root:spec)
    monkeypatch.setattr(campaign,'source_epoch',lambda root:epoch)
    external=tmp_path/'external';external.write_bytes(b'preserve');(tmp_path/'lock').symlink_to(external)
    with pytest.raises(ValueError,match='lock is not an ordinary'):
        campaign.run(root=tmp_path,state=tmp_path,native_jobs=0)
    assert external.read_bytes()==b'preserve'


def test_nonfinite_aggregate_core_fails_before_pointer(tmp_path):
    value=sample();write_case_shards(tmp_path,value)
    value['provisional_test']=float('nan')
    with pytest.raises(ValueError):campaign._write_aggregate(tmp_path,value)
    assert not (tmp_path/'aggregate-current.json').exists()


def test_compact_motion_preserves_legacy_bytes_without_mutating_input():
    value={'trace_index':{'old':'value'},'nested':[{'trace':[{'time':-0.0,'name':'🚆'},
           {'time':1.0,'unknown':None}], 'keep':{'measure':[1,2]}}],
           'trace':[{'step':1},{'step':2}], 'other':[1,{'trace':'not a list'}]}
    original=deepcopy(value)
    expected=deepcopy(value)
    def old_visit(node):
        if isinstance(node,dict):
            for key in list(node):
                if key=='trace' and isinstance(node[key],list):
                    rows=node.pop(key)
                    node['trace_index']={'rows':len(rows),'sha256':identity(rows)}
                else:old_visit(node[key])
        elif isinstance(node,list):
            for item in node:old_visit(item)
    old_visit(expected)
    actual=campaign._compact_motion(value)
    assert encoded(actual)==encoded(expected)
    assert value==original
    actual['nested'][0]['keep']['measure'].append(3)
    assert value==original


def test_one_bundle_active_stream_preserves_legacy_ids(tmp_path,monkeypatch):
    """Run one bounded real analytical bundle in a private state, no native."""
    from contextlib import nullcontext
    import engineering.performance as performance
    monkeypatch.setattr(performance,'disk_reservation',lambda *args,**kwargs:nullcontext(None))
    body=grammar.build(grammar.parameters());spec=campaign.specification();spec['families']=['P1']
    monkeypatch.setattr(campaign,'specification',lambda root=ROOT:deepcopy(spec))
    monkeypatch.setattr(campaign,'generate_bodies',lambda:([body],[]))
    context=dict(method_status='not-run',body_admission={},body_results=[],pending=[])
    monkeypatch.setattr(campaign,'_native_campaign',lambda *args,**kwargs:deepcopy(context))
    result=campaign.run(state=tmp_path/'active',maximum_new_bundles=1,native_jobs=0)
    assert result['campaign_id']==legacy_semantic(result)
    assert result['run_id']==identity({k:v for k,v in result.items() if k!='run_id'})
    assert result['new_bundles']==1 and result['integrated_selection'] is None
    assert all(result[name] is False for name in campaign.FLAGS)
    from io import BytesIO
    state=tmp_path/'active';snapshot,pointer=campaign.current_aggregate(state,result['contract_id'])
    sink=BytesIO();receipt=campaign.aggregate_store.read(snapshot,state/'cases',sink)
    assert sink.getvalue()==encoded(result)
    assert receipt['aggregate_sha256']==pointer['aggregate_sha256']
    assert not (state/'result.json').exists() and not (state/'invocations').exists()


def test_campaign_reserves_disk_before_creating_contract(tmp_path,monkeypatch):
    from engineering.performance import DiskReservationHeld
    monkeypatch.setattr(campaign,'specification',lambda root:{
        'maximum_native_jobs':12,'maximum_bundle_cases':128})
    with pytest.raises(DiskReservationHeld) as held:
        campaign.run(root=tmp_path,maximum_new_bundles=0,native_jobs=0)
    assert held.value.record['status']=='held'
    assert held.value.record['target']==str(tmp_path/'build/coupled-railway')
    assert not (tmp_path/'build/coupled-railway').exists()

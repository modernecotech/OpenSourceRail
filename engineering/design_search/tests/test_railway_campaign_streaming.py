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
        {'candidate_id': 'one', 'value': [1.2, -0.0, '🚆'], 'reused': True},
        {'candidate_id': 'two', 'value': ({'reused': 'tuple remains untouched'},)},
    ], 'new_bundles': 1, 'reused_bundles': 1,
        'integrated_selection': None, 'selected_reference_changed': False,
        **campaign.FLAGS}
    value['campaign_id'] = legacy_semantic(value)
    value['run_id'] = identity(value)
    return value


def test_canonical_hashes_equal_original_including_tuple_omissions():
    value = sample()
    assert campaign.semantic_id(value) == campaign.semantic_id(value,streaming=True) == legacy_semantic(value)
    run_input = {k: v for k, v in value.items() if k != 'run_id'}
    assert campaign._aggregate_identity(run_input) == identity(run_input) == value['run_id']


def test_original_json_domain_falls_back_for_nonstring_keys():
    value = {'nested': {1: 'one', 2: ['two', {'reused': True}]}}
    assert campaign.semantic_id(value) == campaign.semantic_id(value,streaming=True) == legacy_semantic(value)
    assert campaign._aggregate_identity(value) == identity(value)


def test_aggregate_pair_exact_bytes_and_no_hardlinks(tmp_path):
    value = sample()
    (tmp_path/'result.json').write_bytes(b'previous result')
    campaign._write_aggregate(tmp_path, value)
    invocation = tmp_path/'invocations'/(value['run_id']+'.json')
    result = tmp_path/'result.json'
    assert invocation.read_bytes() == result.read_bytes() == encoded(value)
    assert invocation.stat().st_ino != result.stat().st_ino
    assert invocation.stat().st_nlink == result.stat().st_nlink == 1
    assert value['integrated_selection'] is None
    assert all(value[k] is False for k in campaign.FLAGS)


def test_unsupported_clone_falls_back_to_bounded_copy(tmp_path, monkeypatch):
    def unsupported(*args):
        raise OSError(errno.EOPNOTSUPP, 'unsupported')
    monkeypatch.setattr(campaign.fcntl, 'ioctl', unsupported)
    value = sample()
    campaign._write_aggregate(tmp_path, value)
    invocation = tmp_path/'invocations'/(value['run_id']+'.json')
    assert invocation.read_bytes() == (tmp_path/'result.json').read_bytes() == encoded(value)
    assert invocation.stat().st_ino != (tmp_path/'result.json').stat().st_ino


def test_fatal_clone_error_preserves_previous_result(tmp_path, monkeypatch):
    def out_of_space(*args):
        raise OSError(errno.ENOSPC, 'full')
    monkeypatch.setattr(campaign.fcntl, 'ioctl', out_of_space)
    result = tmp_path/'result.json';result.write_bytes(b'previous result')
    value = sample()
    with pytest.raises(OSError) as exc:
        campaign._write_aggregate(tmp_path, value)
    assert exc.value.errno == errno.ENOSPC
    assert result.read_bytes() == b'previous result'
    assert (tmp_path/'invocations'/(value['run_id']+'.json')).read_bytes() == encoded(value)


def test_failed_fallback_copy_preserves_previous_result(tmp_path,monkeypatch):
    source=tmp_path/'source';source.write_bytes(b'valid source');target=tmp_path/'result';target.write_bytes(b'prior')
    expected=(hashlib.sha256(b'valid source').hexdigest(),len(b'valid source'))
    def unsupported(*args):raise OSError(errno.EOPNOTSUPP,'unsupported')
    monkeypatch.setattr(campaign.fcntl,'ioctl',unsupported)
    real_fdopen=campaign.os.fdopen
    class NoProgress:
        def __init__(self,stream):self.stream=stream
        def __enter__(self):return self
        def __exit__(self,*args):self.stream.close()
        def __getattr__(self,name):return getattr(self.stream,name)
        def write(self,data):return 0
    monkeypatch.setattr(campaign.os,'fdopen',lambda *a,**kw:NoProgress(real_fdopen(*a,**kw)))
    with pytest.raises(OSError,match='progress'):campaign._clone_result(source,target,expected)
    assert target.read_bytes()==b'prior' and source.read_bytes()==b'valid source'


def test_clone_rejects_changed_source_before_result_replacement(tmp_path):
    source=tmp_path/'source';source.write_bytes(b'changed')
    target=tmp_path/'result';target.write_bytes(b'prior')
    with pytest.raises(ValueError,match='changed before cloning'):
        campaign._clone_result(source,target,(hashlib.sha256(b'expected').hexdigest(),8))
    assert target.read_bytes()==b'prior'


def test_false_successful_clone_is_detected(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign.fcntl, 'ioctl', lambda *args: 0)
    result = tmp_path/'result.json';result.write_bytes(b'previous result')
    with pytest.raises(ValueError, match='clone or invocation bytes'):
        campaign._write_aggregate(tmp_path, sample())
    assert result.read_bytes() == b'previous result'


def test_short_writes_are_handled_and_no_progress_is_detected(tmp_path, monkeypatch):
    original = campaign._DigestWriter.write
    monkeypatch.setattr(campaign._DigestWriter, 'write', lambda self, data: original(self, data[:2]))
    value = sample()
    campaign._write_aggregate(tmp_path, value)
    assert (tmp_path/'result.json').read_bytes() == encoded(value)
    monkeypatch.setattr(campaign._DigestWriter, 'write', lambda self, data: 0)
    other = tmp_path/'other'
    with pytest.raises(OSError, match='progress'):
        campaign._stream_invocation(other, value)
    assert not other.exists()


def test_resealed_incorrect_existing_invocation_is_not_overwritten(tmp_path):
    value = sample();path=tmp_path/'invocations'/(value['run_id']+'.json')
    path.parent.mkdir();path.write_bytes(b'other evidence')
    with pytest.raises(ValueError, match='Existing invocation differs'):
        campaign._write_aggregate(tmp_path, value)
    assert path.read_bytes() == b'other evidence'
    assert not (tmp_path/'result.json').exists()


def test_hardlinked_or_mutated_invocation_rejected(tmp_path):
    source = tmp_path/'source';source.write_bytes(b'input')
    target = tmp_path/'result';target.write_bytes(b'previous')
    expected=(hashlib.sha256(b'input').hexdigest(), 5)
    os.link(source,tmp_path/'second-link')
    with pytest.raises(ValueError, match='single-link'):
        campaign._clone_result(source,target,expected)
    assert target.read_bytes() == b'previous'


def test_source_epoch_binds_stream_implementation_and_detects_change(tmp_path, monkeypatch):
    names = []
    def collect(path):
        names.append(Path(path).relative_to(tmp_path).as_posix())
        return '0'*64
    real_digest=campaign.digest
    monkeypatch.setattr(campaign, 'digest', collect)
    campaign.source_epoch(tmp_path)
    assert 'engineering/design_search/canonical_stream.py' in names
    for name in set(names):
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(name)
    monkeypatch.setattr(campaign, 'digest', real_digest)
    before=campaign.source_epoch(tmp_path)
    stream=tmp_path/'engineering/design_search/canonical_stream.py'
    stream.write_text('changed implementation')
    after=campaign.source_epoch(tmp_path)
    assert before[stream.relative_to(tmp_path).as_posix()] != after[stream.relative_to(tmp_path).as_posix()]
    assert identity(before) != identity(after)
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
    spec={'schema':'fixture','maximum_native_jobs':12};epoch={'producer':'a'*64}
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
    pending=tmp_path/'stages/pending';pending.parent.mkdir();pending.write_bytes(b'partial')
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


def test_symlink_state_marker_is_rejected(tmp_path):
    external=tmp_path/'external';external.write_text('{}');(tmp_path/'source-contract.json').symlink_to(external)
    with pytest.raises(ValueError,match='ordinary file'):
        campaign._bind_state_source(tmp_path,'b'*64,{'producer':'a'*64})


def test_unsupported_stream_values_fall_back_for_writes(tmp_path):
    value={'nested':{1:'one',2:'two'},'integrated_selection':None}
    value['campaign_id']=legacy_semantic(value);value['run_id']=identity(value)
    campaign._write_aggregate(tmp_path,value)
    assert (tmp_path/'result.json').read_bytes()==encoded(value)


def test_nonfinite_failure_preserves_existing_result(tmp_path):
    result=tmp_path/'result.json';result.write_bytes(b'prior')
    with pytest.raises(ValueError):
        campaign._write_aggregate(tmp_path,{'run_id':'a'*64,'value':float('nan')})
    assert result.read_bytes()==b'prior'


def test_one_bundle_default_and_opt_in_campaign_outputs_match(tmp_path,monkeypatch):
    """Run one bounded real analytical bundle per fresh private state, no native."""
    body=grammar.build(grammar.parameters());spec=campaign.specification();spec['families']=['P1']
    monkeypatch.setattr(campaign,'specification',lambda root=ROOT:deepcopy(spec))
    monkeypatch.setattr(campaign,'generate_bodies',lambda:([body],[]))
    context=dict(method_status='not-run',body_admission={},body_results=[],pending=[])
    monkeypatch.setattr(campaign,'_native_campaign',lambda *args,**kwargs:deepcopy(context))
    default=campaign.run(state=tmp_path/'default',maximum_new_bundles=1,native_jobs=0)
    streamed=campaign.run(state=tmp_path/'stream',maximum_new_bundles=1,native_jobs=0,stream_aggregate=True)
    assert default==streamed
    assert default['new_bundles']==1 and default['integrated_selection'] is None
    assert all(default[name] is False for name in campaign.FLAGS)
    assert (tmp_path/'default/result.json').read_bytes()==(tmp_path/'stream/result.json').read_bytes()
    assert (tmp_path/'stream/invocations'/(streamed['run_id']+'.json')).read_bytes()==encoded(default)

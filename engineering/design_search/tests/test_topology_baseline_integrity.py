"""Independent baseline pinning and semantic-replay controls."""
from copy import deepcopy
import gzip
import json

import pytest

from engineering.design_search import topology_baseline_integrity as guard
from engineering.station_rail.common import encoded, identity


def seal(value):
    value['baseline_id'] = identity(value)
    return value


def sample():
    return seal(dict(schema='osr-topology-system-baseline/1',
        load_context=dict(context_id='a'*64), load_context_id='a'*64,
        source_sha256={'producer.py':'b'*64},
        selected=dict(candidate_id='c'*64,vehicle_evaluation_id='d'*64,selection_id='e'*64),
        canonical_system_cost_estimate_id='f'*64,canonical_vehicle_cost_estimate_id='0'*64,
        tool_context=dict(python='3.13',numpy='2.3.5'),
        cases=dict(base=dict(cost=dict(foundation_iqd=2690073120.))), **guard.FLAGS))


def fake_replay(monkeypatch, original):
    def validate(value, root, *, require_current_tools):
        assert require_current_tools is False
        return value
    def rebuild(root, context):
        result=deepcopy(original);result.pop('baseline_id')
        result['tool_context']=dict(python='3.12',numpy='2.3.5')
        return seal(result)
    monkeypatch.setattr(guard.canonical, 'validate_baseline', validate)
    monkeypatch.setattr(guard.canonical, 'make_baseline', rebuild)


def test_exact_semantics_replay_with_distinct_runtime_preserves_original_identity(monkeypatch,tmp_path):
    original=sample();before=deepcopy(original);fake_replay(monkeypatch,original)
    out=guard.verify_record(original,expected_baseline_id=original['baseline_id'],root=tmp_path)
    assert out['verified'] is True and out['canonical_cost_fields_recomputed'] is True
    assert out['recorded_tool_context']!=out['replay_tool_context']
    assert out['native_evaluator_reuse'] is False and out['physical_accepted'] is False
    assert out['selected_vehicle_candidate_id']=='c'*64 and out['source_epoch_id']==identity(original['source_sha256'])
    assert original==before and out['replay_baseline_id']!=out['expected_baseline_id']


def test_resealed_halved_cost_rejected_against_external_pin_and_even_repinning(monkeypatch,tmp_path):
    original=sample();fake_replay(monkeypatch,original);forged=deepcopy(original)
    forged['cases']['base']['cost']['foundation_iqd']/=2
    forged.pop('baseline_id');seal(forged)
    with pytest.raises(ValueError,match='caller-pinned'):
        guard.verify_record(forged,expected_baseline_id=original['baseline_id'],root=tmp_path)
    with pytest.raises(ValueError,match='semantic replay differs: cases'):
        guard.verify_record(forged,expected_baseline_id=forged['baseline_id'],root=tmp_path)


def test_replay_rejects_boolean_substituted_for_numerically_equal_one(monkeypatch,tmp_path):
    original=sample();original.pop('baseline_id');original['cases']['base']['cost']['foundation_iqd']=1;seal(original)
    fake_replay(monkeypatch,original);forged=deepcopy(original);forged.pop('baseline_id')
    forged['cases']['base']['cost']['foundation_iqd']=True;seal(forged)
    with pytest.raises(ValueError,match='semantic replay differs: cases'):
        guard.verify_record(forged,expected_baseline_id=forged['baseline_id'],root=tmp_path)


@pytest.mark.parametrize('invalid',('',None,'g'*64,'0'*63,1))
def test_missing_or_malformed_external_pin_rejected(invalid,tmp_path):
    with pytest.raises(ValueError,match='Caller-pinned'):
        guard.verify_record(sample(),expected_baseline_id=invalid,root=tmp_path)


def test_changed_source_during_replay_rejected(monkeypatch,tmp_path):
    original=sample();fake_replay(monkeypatch,original);calls=[]
    def validate(value,root,*,require_current_tools):
        calls.append(1)
        if len(calls)==2:raise ValueError('source epoch changed')
    monkeypatch.setattr(guard.canonical,'validate_baseline',validate)
    with pytest.raises(ValueError,match='source epoch changed'):
        guard.verify_record(original,expected_baseline_id=original['baseline_id'],root=tmp_path)


def test_ordinary_file_bounded_json_and_symlink_controls(tmp_path):
    baseline=sample();path=tmp_path/'baseline.json.gz';raw=gzip.compress(encoded(baseline),mtime=0);path.write_bytes(raw)
    assert guard._snapshot(path)==(raw,baseline)
    link=tmp_path/'alias.gz';link.symlink_to(path)
    with pytest.raises(ValueError,match='Symlink'):guard._snapshot(link)
    path.write_bytes(gzip.compress(b'{"a":1,"a":2}',mtime=0))
    with pytest.raises(ValueError,match='Duplicate'):guard._snapshot(path)
    path.write_bytes(gzip.compress(b'{"a":NaN}',mtime=0))
    with pytest.raises(ValueError,match='Nonfinite'):guard._snapshot(path)

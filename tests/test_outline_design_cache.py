import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest

from engineering.outline import design_cache


def _fixture(root):
    state = dict(source_sha256={'source-a': 'a'*64},
        source_manifest_ids={'packet-a': 'b'*64},
        pricing_policy=dict(policy_id='policy-a'))
    calls = {'evaluate': 0, 'validate': 0}
    guard = threading.Lock()

    def evaluate(root, policy):
        with guard:
            calls['evaluate'] += 1
        time.sleep(.04)
        result = dict(source_sha256=dict(state['source_sha256']),
            source_manifest_ids=dict(state['source_manifest_ids']),
            pricing_policy=dict(policy), counts={'railway-bundle': 112},
            payload='deterministic design prices')
        return result, dict(elapsed_s=.04, native_solver_jobs=0, CAD_jobs=0,
            streamed_railway_records=112)

    def validate(value, root):
        calls['validate'] += 1
        assert value['source_sha256'] == state['source_sha256']
        assert value['source_manifest_ids'] == state['source_manifest_ids']
        assert value['pricing_policy']['policy_id'] == state['pricing_policy']['policy_id']
        return {'verified': True}

    module = SimpleNamespace(policy=lambda root: dict(state['pricing_policy']),
        _source_inputs=lambda root: (dict(state['source_sha256']),
            dict(state['source_manifest_ids'])), evaluate=evaluate, validate=validate)
    return module, state, calls


def test_design_cache_evaluates_once_and_validates_every_hit(tmp_path):
    module, _, calls = _fixture(tmp_path)
    first, first_timing = design_cache.evaluate_cached(tmp_path,
        design_completion_module=module)
    second, second_timing = design_cache.evaluate_cached(tmp_path,
        design_completion_module=module)

    assert first == second
    assert first_timing['cache_hit'] is False
    assert first_timing['design_evaluation_performed'] is True
    assert second_timing['cache_hit'] is True
    assert second_timing['design_evaluation_performed'] is False
    assert second_timing['cache_key'] == first_timing['cache_key']
    assert calls == {'evaluate': 1, 'validate': 2}


def test_source_or_policy_changes_create_a_new_cache_key(tmp_path):
    module, state, calls = _fixture(tmp_path)
    first, _ = design_cache.evaluate_cached(tmp_path, design_completion_module=module)
    state['source_sha256'] = {'source-a': 'c'*64}
    second, timing = design_cache.evaluate_cached(tmp_path, design_completion_module=module)
    assert first['source_sha256'] != second['source_sha256']
    assert timing['cache_hit'] is False and calls['evaluate'] == 2
    state['pricing_policy'] = dict(policy_id='policy-b')
    _, policy_timing = design_cache.evaluate_cached(tmp_path,
        design_completion_module=module)
    assert policy_timing['cache_hit'] is False and calls['evaluate'] == 3


def test_cache_prunes_oldest_reproducible_entries_to_its_retention_budget(tmp_path):
    module, state, calls = _fixture(tmp_path)
    first_key = None
    for index in range(design_cache.MAX_CACHE_ENTRIES + 1):
        state['pricing_policy'] = dict(policy_id=f'policy-{index}')
        _, timing = design_cache.evaluate_cached(tmp_path, design_completion_module=module)
        if index == 0:
            first_key = timing['cache_key']
    directory = tmp_path/'.cache/osr-engineering/design-completion'
    assert not (directory/(first_key+'.json')).exists()
    assert len(list(directory.glob('*.json'))) == design_cache.MAX_CACHE_ENTRIES
    assert timing['cache_entries'] == design_cache.MAX_CACHE_ENTRIES
    assert timing['cache_total_bytes'] <= design_cache.MAX_CACHE_BYTES
    assert timing['evicted_entries'] == 1
    assert calls['evaluate'] == design_cache.MAX_CACHE_ENTRIES + 1
    assert len(list(directory.glob('*.lock'))) <= 17


def test_concurrent_requests_share_one_immutable_evaluation(tmp_path):
    module, _, calls = _fixture(tmp_path)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: design_cache.evaluate_cached(
            tmp_path, design_completion_module=module), range(2)))
    assert results[0][0] == results[1][0]
    assert sorted(result[1]['cache_hit'] for result in results) == [False, True]
    assert calls['evaluate'] == 1


def test_corrupt_cache_is_retained_and_refused(tmp_path):
    module, _, calls = _fixture(tmp_path)
    _, timing = design_cache.evaluate_cached(tmp_path, design_completion_module=module)
    path = tmp_path/'.cache/osr-engineering/design-completion'/(timing['cache_key']+'.json')
    corrupt = b'{corrupt cache bytes\n'
    path.write_bytes(corrupt)
    with pytest.raises((ValueError, json.JSONDecodeError)):
        design_cache.evaluate_cached(tmp_path, design_completion_module=module)
    assert path.read_bytes() == corrupt
    assert calls['evaluate'] == 1


def test_symlinked_cache_root_is_rejected_before_evaluation(tmp_path):
    module, _, calls = _fixture(tmp_path)
    external = tmp_path/'external';external.mkdir()
    cache = tmp_path/'.cache';cache.symlink_to(external, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink'):
        design_cache.evaluate_cached(tmp_path, design_completion_module=module)
    assert calls['evaluate'] == 0

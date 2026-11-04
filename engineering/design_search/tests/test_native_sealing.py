"""Independent exact-format and campaign checks for opt-in Rust record sealing."""
from copy import deepcopy
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import random
import struct
from concurrent.futures import ThreadPoolExecutor

import pytest

from engineering.design_search import native_campaign as c, native_canonical as n
from engineering.station_rail import common

PYTHON_ENCODED = common.encoded


def oracle(value, key='evaluation_id'):
    """Independent Python spelling of the original fresh-record contract."""
    if (type(value) is not dict or not isinstance(key, str) or not key or key in value
            or any(type(k) is not str for k in value)):
        raise ValueError('Fresh string-keyed record and absent seal key required')
    seal = sha256(PYTHON_ENCODED(value)).hexdigest()
    result = dict(value)
    result[key] = seal
    return result, PYTHON_ENCODED(result), seal


@pytest.fixture(scope='module')
def native():
    if os.environ.get('OSR_TEST_NATIVE_CANONICAL') != '1':
        pytest.skip('Explicit current-ABI Rust encoder build required')
    return n.NativeCanonical()


def test_python_fallback_works_without_loading_rust_and_preserves_subclass_seal_key(monkeypatch):
    class SealKey(str): pass
    def forbidden(*args, **kwargs): raise AssertionError('Python fallback loaded Rust')
    monkeypatch.setattr(n, 'NativeCanonical', forbidden)
    value = {'existing': [1, None, -0.0]}
    expected, raw, _ = oracle(value, SealKey('id'))
    actual, actual_raw = c._sealed_record(value, SealKey('id'))
    assert actual == expected and actual_raw == raw
    assert value == {'existing': [1, None, -0.0]}


@pytest.mark.parametrize('invalid', [1, None, 'false'])
def test_record_sealing_policy_requires_explicit_boolean(invalid):
    with pytest.raises(ValueError, match='boolean'):
        with n.campaign_backend('python', record_sealing=invalid):
            pass


@pytest.mark.parametrize('key,value', [
    ('id', {}), ('a', {'b': 1, 'c': 2}), ('b', {'a': 1, 'c': 2}),
    ('z', {'a': 1, 'b': 2}), ('\ud800', {'\udfff': 1, '\U00010000': 2, '\ue000': 3}),
    ('\U00010000', {'\ud800\udc00': 1, 'é': 2, 'e\u0301': 3}),
    ('json\n\x00', {'🐈': [-0.0, 2**4096, 5e-324, 1e16, -1e-6]})])
def test_exact_sealed_bytes_hash_key_position_and_nonmutation(native, key, value):
    before = deepcopy(value)
    expected, expected_raw, seal = oracle(value, key)
    with native.session() as session:
        raw, actual_seal = session.sealed_record(value, key)
    assert (raw, actual_seal) == (expected_raw, seal)
    assert json.loads(raw) == json.loads(expected_raw)
    assert value == before and key not in value


def test_thousands_of_deterministic_nested_records_match_original_format(native):
    rng = random.Random(20261104)
    atoms = [None, True, False, 0, -1, 2**300, -0.0, 1e-7, 5e-324, '', 'é', '\ud800', '🐈']
    def item(depth):
        if depth == 0 or rng.randrange(3) == 0: return rng.choice(atoms)
        if rng.randrange(2): return [item(depth-1) for _ in range(rng.randrange(4))]
        return {f'{i}:{rng.choice(atoms[8:])}': item(depth-1) for i in range(rng.randrange(4))}
    with native.session() as session:
        for i in range(3000):
            value = {f'{j}:{i}': item(3) for j in range(rng.randrange(5))}
            _, expected, seal = oracle(value, 'seal')
            assert session.sealed_record(value, 'seal') == (expected, seal)


def test_randomized_multiplane_dictionary_key_order_and_sealing_match_python(native):
    rng = random.Random(20261106)
    # A surrogate pair remains two Python codepoints and is distinct from the
    # equivalent scalar, even when both have the same escaped JSON spelling.
    atoms = ['a', 'Z', '\x00', '\u007f', '\u0080', '\u07ff', '\u0800',
             '\ud7ff', '\ud800', '\udfff', '\ue000', '\ufffd', '\uffff',
             '\U00010000', '\ud800\udc00', '\U0001f680', '\U0010ffff',
             'é', 'e\u0301', '\u0301', 'العراق']
    with native.session() as session:
        for case in range(300):
            keys = set(atoms)
            for _ in range(rng.randrange(108)):
                keys.add(''.join(rng.choice(atoms) for _ in range(rng.randrange(1, 4))))
            keys = sorted(keys)[:128]
            shuffled = list(keys); rng.shuffle(shuffled)
            nested = {key: index for index, key in enumerate(reversed(shuffled))}
            record = {key: (nested if index == 0 else [case, index])
                      for index, key in enumerate(shuffled)}
            expected = PYTHON_ENCODED(record)
            assert session.encoded(record) == expected
            assert session.identity(record) == sha256(expected).hexdigest()
            _, sealed, seal = oracle(record, 'sealing-id')
            assert session.sealed_record(record, 'sealing-id') == (sealed, seal)


def test_extreme_finite_floats_match_python_format(native):
    rng = random.Random(20261105)
    values = []
    while len(values) < 2048:
        value = struct.unpack('>d', rng.getrandbits(64).to_bytes(8, 'big'))[0]
        if math.isfinite(value): values.append(value)
    record = {'values': values, 'negative_zero': -0.0}
    _, raw, seal = oracle(record, 'id')
    assert native.sealed_record(record, 'id') == (raw, seal)


def test_shared_aliases_remain_acyclic_and_input_is_not_mutated(native):
    shared = {'x': [1, -0.0, '\ud800']}
    value = {'a': [shared, shared], 'b': (shared,)}
    _, raw, seal = oracle(value, 'id')
    assert native.sealed_record(value, 'id') == (raw, seal)
    assert value['a'][0] is shared and value['a'][1] is shared and value['b'][0] is shared
    assert 'id' not in value


@pytest.mark.parametrize('kind', ['list-cycle', 'mapping-cycle', 'nonfinite', 'nested-nonstring-key'])
def test_cycles_and_values_outside_native_domain_are_rejected(native, kind):
    if kind == 'list-cycle':
        x = []; x.append(x); value = {'x': x}
    elif kind == 'mapping-cycle':
        value = {}; value['x'] = value
    elif kind == 'nonfinite': value = {'x': float('nan')}
    else: value = {'x': {1: 'not a string key'}}
    with pytest.raises((TypeError, ValueError, RecursionError)):
        native.sealed_record(value, 'id')


def test_invalid_top_level_key_collision_and_builtin_subclasses_are_rejected(native):
    class String(str): pass
    class Dict(dict): pass
    cases = [([], 'id'), (Dict(a=1), 'id'), ({'id': 1}, 'id'), ({}, ''),
             ({1: 'nonstring'}, 'id'), ({String('a'): 1}, 'id'), ({}, String('id'))]
    for value, key in cases:
        with pytest.raises((TypeError, ValueError)):
            native.sealed_record(value, key)


def test_sealed_size_and_depth_limits_are_enforced(native):
    value = {'a': [1, 'text']}
    _, raw, seal = oracle(value, 'id')
    assert native.sealed_record(value, 'id', max_bytes=len(raw)) == (raw, seal)
    with pytest.raises(ValueError): native.sealed_record(value, 'id', max_bytes=len(raw)-1)
    nested = 0
    for _ in range(20): nested = [nested]
    with pytest.raises((ValueError, RecursionError)):
        native.sealed_record({'nested': nested}, 'id', max_depth=8)
    _, expected, expected_seal = oracle({'nested': nested}, 'id')
    assert native.sealed_record({'nested': nested}, 'id', max_depth=32) == (expected, expected_seal)
    for limits in ({'max_bytes': True}, {'max_bytes': 0}, {'max_bytes': 64*1024**2+1},
                   {'max_depth': True}, {'max_depth': 0}, {'max_depth': 257}):
        with pytest.raises(ValueError): native.sealed_record({}, 'id', **limits)


def test_scoped_activation_and_exception_restore_python_aliases(native):
    assert n.active_sealed_record({'a': 1}, 'id') is None
    aliases = (common.encoded, common.identity, c.encoded, c.identity)
    with pytest.raises(RuntimeError, match='intentional'):
        with n.campaign_backend('rust', record_sealing=True):
            _, raw, seal = oracle({'a': 1}, 'id')
            assert n.active_sealed_record({'a': 1}, 'id') == (raw, seal)
            with ThreadPoolExecutor(max_workers=1) as pool:
                assert pool.submit(n.active_sealed_record, {'a': 1}, 'id').result(timeout=5) is None
            raise RuntimeError('intentional')
    assert n.active_sealed_record({'a': 1}, 'id') is None
    assert (common.encoded, common.identity, c.encoded, c.identity) == aliases
    with n.campaign_backend('rust', record_sealing=False):
        assert n.active_sealed_record({'a': 1}, 'id') is None


def test_nested_python_scope_is_rejected_without_changing_outer_rust_scope(native):
    assert n.active_sealed_record({'a': 1}, 'id') is None
    _, raw, seal = oracle({'a': 1}, 'id')
    with n.campaign_backend('rust', record_sealing=True):
        assert n.active_sealed_record({'a': 1}, 'id') == (raw, seal)
        with pytest.raises(RuntimeError):
            with n.campaign_backend('python', record_sealing=False):
                pytest.fail('Nested Python provenance cannot inherit an active Rust encoder')
        assert n.active_sealed_record({'a': 1}, 'id') == (raw, seal)
    assert n.active_sealed_record({'a': 1}, 'id') is None


def test_active_scope_seals_without_per_record_filesystem_or_subprocess(native, monkeypatch):
    _, raw, _ = oracle({'a': [-0.0, 5]}, 'id')
    def forbidden(*args, **kwargs): raise AssertionError('Per-record I/O attempted')
    with n.campaign_backend('rust', record_sealing=True):
        with monkeypatch.context() as patch:
            patch.setattr(n.native_search, '_read', forbidden)
            patch.setattr(n, '_sources', forbidden)
            patch.setattr(n.native_search, '_tools', forbidden)
            actual, actual_raw = c._sealed_record({'a': [-0.0, 5]}, 'id')
            assert actual_raw == raw and actual['id'] == sha256(PYTHON_ENCODED({'a': [-0.0, 5]})).hexdigest()


def test_enabled_native_error_propagates_without_silent_fallback(native, monkeypatch):
    value = {'a': [1, 2]}
    def failed(*args, **kwargs): raise RuntimeError('native sealing failure')
    with n.campaign_backend('rust', record_sealing=True):
        with monkeypatch.context() as patch:
            patch.setattr(n, 'active_sealed_record', failed)
            with pytest.raises(RuntimeError, match='native sealing failure'):
                c._sealed_record(value, 'id')
    assert value == {'a': [1, 2]}


def test_session_is_not_usable_after_context_exit(native):
    with native.session() as session:
        assert session.sealed_record({}, 'id')[0] == oracle({}, 'id')[1]
    with pytest.raises(RuntimeError, match='session has ended'):
        session.sealed_record({}, 'id')


@pytest.fixture
def small(monkeypatch):
    spec = c.specification(); spec.update(proposals_per_generation=4, evaluations_per_generation=2,
                                          detailed_finalists=0, seed_bracing=[False])
    monkeypatch.setattr(c, 'specification', lambda root=c.ROOT: deepcopy(spec))
    registry = c.shape_families.registry()
    recipes = {key: registry[key] for key in ('aluminium_spaceframe', 'modular_segments')}
    monkeypatch.setattr(c.shape_families, 'registry', lambda root=c.ROOT: deepcopy(recipes))


def test_enabled_and_disabled_native_sealing_preserve_campaign_and_resume(native, tmp_path, small):
    def run(state, sealing, budget):
        result = c.run(state=state, generations=1, maximum_new_evaluations=budget,
                       canonical_backend='rust', native_record_sealing=sealing,
                       native_jobs=0, frame_native_jobs=0, section_torsion_jobs=0)
        return json.loads(Path(result['output']).read_bytes())
    baseline = run(tmp_path / 'original', False, 2)
    fused = run(tmp_path / 'fused', True, 2)
    assert baseline['evaluations'] == fused['evaluations']
    assert baseline['archive'] == fused['archive']
    assert baseline['refinement'] == fused['refinement']
    fields = ('genes', 'generation', 'operator', 'parent_candidate_ids', 'parent_evaluations',
              'candidate_id', 'definition_id', 'evaluation_id', 'state')
    project = lambda run: [{key: attempt.get(key) for key in fields} for attempt in run['attempts']]
    assert project(baseline) == project(fused)
    assert fused['integrated_selection'] is None and fused['numerical_solver_dispatch_count'] == 0
    assert all(fused[key] is False for key in c.FLAGS)
    resumed = run(tmp_path / 'fused', True, 0)
    assert resumed['evaluations'] == fused['evaluations']
    assert resumed['generations'] == fused['generations']
    assert resumed['attempts'] == fused['attempts']

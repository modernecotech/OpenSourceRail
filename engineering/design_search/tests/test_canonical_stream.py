import io
import random

import pytest

from engineering.design_search import canonical_stream as streaming
from engineering.design_search import railway_campaign
from engineering.station_rail.common import encoded, identity


def reference_clean(value):
    if isinstance(value, dict):
        return {key: reference_clean(item) for key, item in value.items()
                if key not in streaming.SEMANTIC_OMISSIONS}
    if isinstance(value, list):
        return [reference_clean(item) for item in value]
    return value


@pytest.mark.parametrize('value', [
    None, True, False, 0, -123456789012345678901234567890, -0.0, 1e-7, 1e20,
    5e-324, 1.7976931348623157e308, '', 'Unicode: é 🚆 \ud800', '"\\\n\t\0',
    [], (), {}, {'z': 2, 'a': 1},
    {'run_id': 'drop', 'keep': [{'reused': True, 'nested': {'campaign_id': 'drop'}}]},
    {'inside_tuple': ({'run_id': 'keep', 'nested': [{'reused': 'keep'}]},)},
    {'nested': [{'inside_tuple': ({'run_id': 'keep'},), 'run_id': 'drop'}]},
])
def test_matches_existing_canonical_bytes_and_identities(value):
    original = encoded(value)
    for size in (1, 3, 16, 65536):
        chunks = list(streaming.iter_canonical_bytes(value, chunk_size=size))
        assert all(0 < len(chunk) <= size for chunk in chunks)
        assert b''.join(chunks) == original
        assert b''.join(streaming.iter_canonical_bytes(value, semantic=True, chunk_size=size)) == encoded(reference_clean(value))
        assert streaming.canonical_identity(value, chunk_size=size) == identity(value)
        assert streaming.canonical_identity(value, semantic=True, chunk_size=size) == railway_campaign.semantic_id(value)


def test_random_nested_trees_match_both_existing_identities():
    rng = random.Random(42817)
    leaves = [None, True, False, -0.0, 1e-7, 1e20, -42, '', 'é', '\udfff', '"\\\n']
    names = ['run_id', 'reused', 'campaign_id', 'new_bundles', 'x', 'é', '\ud800']

    def tree(depth):
        if not depth or rng.random() < .32:
            return rng.choice(leaves)
        choice = rng.randrange(3)
        if choice == 0:
            return [tree(depth - 1) for _ in range(rng.randrange(5))]
        if choice == 1:
            return tuple(tree(depth - 1) for _ in range(rng.randrange(5)))
        return {rng.choice(names): tree(depth - 1) for _ in range(rng.randrange(5))}

    for _ in range(500):
        value = tree(5)
        assert b''.join(streaming.iter_canonical_bytes(value, chunk_size=11)) == encoded(value)
        assert b''.join(streaming.iter_canonical_bytes(value, semantic=True, chunk_size=11)) == encoded(reference_clean(value))
        assert streaming.canonical_identity(value) == identity(value)
        assert streaming.canonical_identity(value, semantic=True) == railway_campaign.semantic_id(value)


def test_nested_aliases_are_not_mutated_or_mistaken_for_cycles():
    shared = {'run_id': 'drop', 'x': [1, 2]}
    value = {'a': shared, 'b': [shared, (shared,)]}
    before = encoded(value)
    assert streaming.canonical_identity(value, semantic=True) == railway_campaign.semantic_id(value)
    assert encoded(value) == before


@pytest.mark.parametrize('value', [float('nan'), float('inf'), float('-inf')])
def test_nonfinite_values_are_rejected(value):
    with pytest.raises(ValueError):
        encoded(value)
    with pytest.raises(ValueError):
        b''.join(streaming.iter_canonical_bytes(value))


def test_omitted_values_are_not_traversed():
    value = {'run_id': float('nan'), 'keep': 1}
    assert streaming.canonical_identity(value, semantic=True) == railway_campaign.semantic_id(value)
    with pytest.raises(ValueError):
        streaming.canonical_identity(value)
    cycle = []
    cycle.append(cycle)
    assert streaming.canonical_identity({'run_id': cycle}, semantic=True) == railway_campaign.semantic_id({'run_id': cycle})


def test_unsupported_values_and_object_keys_fail_closed():
    for value in ({1: 'json accepts this key, streaming intentionally does not'}, {1, 2}, b'bytes'):
        with pytest.raises(TypeError):
            b''.join(streaming.iter_canonical_bytes(value))
    cycle = []
    cycle.append(cycle)
    with pytest.raises(ValueError, match='Circular'):
        b''.join(streaming.iter_canonical_bytes(cycle))


def test_write_canonical_handles_partial_writes_and_detects_no_progress():
    class Partial(io.BytesIO):
        def write(self, data):
            return super().write(data[:2])

    output = Partial()
    value = {'a': ['é', 1, {'z': True}]}
    assert streaming.write_canonical(value, output, chunk_size=3) == len(encoded(value))
    assert output.getvalue() == encoded(value)

    class Stalled:
        def write(self, data):
            return 0

    with pytest.raises(OSError, match='progress'):
        streaming.write_canonical(value, Stalled())


@pytest.mark.parametrize('kwargs', [{'chunk_size': 0}, {'chunk_size': True}, {'semantic': 1}])
def test_invalid_stream_options_are_rejected(kwargs):
    with pytest.raises(ValueError):
        b''.join(streaming.iter_canonical_bytes({}, **kwargs))

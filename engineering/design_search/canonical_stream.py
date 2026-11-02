"""Opt-in bounded-buffer canonical JSON for research identities.

This standalone primitive does not modify campaign execution or admit any
candidate. It intentionally supports only the built-in JSON value types with
string object keys. Large individual string values still require an escaped
copy; buffering bounds the combined output, not the input object.
"""
from __future__ import annotations

from hashlib import sha256
import json.encoder
import math

SEMANTIC_OMISSIONS = frozenset((
    'campaign_id', 'run_id', 'new_bundles', 'reused_bundles',
    'new_native_jobs', 'reused_native_jobs', 'requested_native_jobs', 'reused',
))


def _tokens(value, semantic, active):
    """Yield ASCII JSON text; semantic follows railway_campaign.clean exactly."""
    kind = type(value)
    if kind is str:
        yield json.encoder.encode_basestring_ascii(value)
    elif kind is type(None):
        yield 'null'
    elif kind is bool:
        yield 'true' if value else 'false'
    elif kind is int:
        yield str(value)
    elif kind is float:
        if not math.isfinite(value):
            raise ValueError('Out of range float values are not JSON compliant')
        yield repr(value)
    elif kind in (dict, list, tuple):
        marker = id(value)
        if marker in active:
            raise ValueError('Circular reference detected')
        active.add(marker)
        try:
            if kind is dict:
                if any(type(key) is not str for key in value):
                    raise TypeError('Canonical streaming requires built-in string object keys')
                yield '{'
                first = True
                for key in sorted(value):
                    if semantic and key in SEMANTIC_OMISSIONS:
                        continue
                    if not first:
                        yield ','
                    first = False
                    yield json.encoder.encode_basestring_ascii(key)
                    yield ':'
                    yield from _tokens(value[key], semantic, active)
                yield '}'
            else:
                yield '['
                # The existing semantic cleaner traverses dicts/lists only.
                # A tuple is returned untouched, including its descendants.
                nested_semantic = semantic if kind is list else False
                for index, item in enumerate(value):
                    if index:
                        yield ','
                    yield from _tokens(item, nested_semantic, active)
                yield ']'
        finally:
            active.remove(marker)
    else:
        raise TypeError(f'Unsupported canonical streaming type: {kind.__name__}')


def iter_canonical_bytes(value, *, semantic=False, chunk_size=65536):
    """Yield sorted compact canonical JSON, with the required trailing newline.

    With ``semantic=True``, omit the same bookkeeping keys as
    ``railway_campaign.semantic_id``. No input objects are modified.
    """
    if type(semantic) is not bool or type(chunk_size) is not int or chunk_size < 1:
        raise ValueError('A boolean semantic mode and positive integer chunk size are required')
    buffer = bytearray()
    for token in _tokens(value, semantic, set()):
        data = token.encode('ascii')
        if len(data) < chunk_size - len(buffer):
            buffer.extend(data)
            continue
        view = memoryview(data)
        while view:
            count = min(chunk_size - len(buffer), len(view))
            buffer.extend(view[:count])
            view = view[count:]
            if len(buffer) == chunk_size:
                yield bytes(buffer)
                buffer.clear()
    buffer.extend(b'\n')
    yield bytes(buffer)


def canonical_identity(value, *, semantic=False, chunk_size=65536):
    """Return the SHA-256 of the exact canonical stream."""
    digest = sha256()
    for chunk in iter_canonical_bytes(value, semantic=semantic, chunk_size=chunk_size):
        digest.update(chunk)
    return digest.hexdigest()


def write_canonical(value, stream, *, semantic=False, chunk_size=65536):
    """Write to a binary stream; callers must handle atomicity and failures."""
    total = 0
    for chunk in iter_canonical_bytes(value, semantic=semantic, chunk_size=chunk_size):
        remaining = memoryview(chunk)
        while remaining:
            count = stream.write(remaining)
            if type(count) is not int or not 0 < count <= len(remaining):
                raise OSError('Canonical stream write made no valid progress')
            total += count
            remaining = remaining[count:]
    return total

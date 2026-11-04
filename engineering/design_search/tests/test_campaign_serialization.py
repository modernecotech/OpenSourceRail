"""Canonical sealing optimization retains exact reference bytes and identities."""
from copy import deepcopy
import gzip
import random

import pytest

from engineering.design_search import native_campaign as campaign
from engineering.station_rail.common import encoded, identity


def reference(value, key):
    value = deepcopy(value)
    value[key] = identity(value)
    return value, encoded(value)


def test_fragment_sealing_matches_independent_encoder_with_nested_data_and_all_positions():
    randomizer = random.Random(874)
    for _ in range(100):
        shared = [None, True, False, -0.0, 1e-100, 1e100, "\u03a9\\\n\"", randomizer.random()]
        value = {"a": {"nested": shared}, "z": [shared, tuple(shared)], "\u03a9": randomizer.randrange(10**30)}
        before = deepcopy(value)
        for key in ("0", "m", "zz", "\uffff"):
            sealed, raw = campaign._sealed_record(value, key)
            expected, expected_raw = reference(value, key)
            assert sealed == expected
            assert raw == expected_raw == encoded(sealed)
        assert value == before


def test_empty_record_and_checkpoint_wire_format_remain_identical(tmp_path):
    assert campaign._sealed_record({}, "id") == reference({}, "id")
    value = {"attempts": [{"mass": None, "accepted": False}], "pending": []}
    path = tmp_path / "checkpoint.json"
    campaign._checkpoint(path, value)
    assert path.read_bytes() == reference(value, "checkpoint_id")[1]
    assert "checkpoint_id" not in value


@pytest.mark.parametrize("value,key", [({"id": "old"}, "id"), ({1: "non-string"}, "id"), ({}, ""), ([], "id")])
def test_sealing_requires_a_fresh_explicit_record(value, key):
    with pytest.raises(ValueError):
        campaign._sealed_record(value, key)


@pytest.mark.parametrize("value", [{"x": float("nan")}, {"x": float("inf")}, {"x": object()}])
def test_authoritative_encoder_failures_are_preserved(value):
    with pytest.raises((ValueError, TypeError)):
        campaign._sealed_record(value)


def test_circular_values_are_not_silently_accepted():
    value = {"nested": []}
    value["nested"].append(value)
    with pytest.raises(ValueError, match="Circular"):
        campaign._sealed_record(value)


def test_geometry_compression_is_lossless_and_immutable_replay_still_checks_bytes(tmp_path):
    value = {"candidate": {"parts": [{"mass_kg": 3.0}]}, "materialisation_base": {"mass": None}}
    sealed, raw = campaign._sealed_record(value, "record_id")
    assert gzip.decompress(gzip.compress(raw, compresslevel=1, mtime=0)) == reference(value, "record_id")[1]
    path = tmp_path / "record.json"
    campaign._store_raw(path, raw)
    campaign._store(path, sealed)
    with pytest.raises(RuntimeError, match="Conflicting immutable"):
        campaign._store_raw(path, raw.replace(b"3.0", b"0.0"))


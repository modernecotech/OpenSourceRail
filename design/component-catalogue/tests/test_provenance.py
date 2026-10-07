"""Portable artifacts identify input contents rather than their containing commit."""
import gzip
import os
from pathlib import Path
import subprocess
import sys

from osr_mech.provenance import deterministic_gzip, input_revision


def test_revision_is_order_independent_and_changes_when_an_input_changes():
    assert input_revision({'a':'0'*64,'b':'1'*64})==input_revision({'b':'1'*64,'a':'0'*64})
    assert input_revision({'a':'0'*64})!=input_revision({'a':'1'*64})


def test_gzip_has_fixed_headers_and_roundtrips():
    raw=b'whole bays and beams\n'*1000
    compressed=deterministic_gzip(raw)
    assert compressed[4:8]==b'\0'*4
    assert compressed[9]==255
    assert gzip.decompress(compressed)==raw
    assert deterministic_gzip(raw)==compressed


def test_supported_python_runtimes_produce_the_same_schedule_bytes(tmp_path):
    other=Path('/usr/bin/python3.11')
    if not other.exists():
        return  # CI separately exercises its pinned 3.11 runtime.
    module_root=Path(__file__).resolve().parents[1]/'src'
    code="from osr_mech.provenance import deterministic_gzip;import sys;sys.stdout.buffer.write(deterministic_gzip(b'whole bays and beams\\n'*1000))"
    env={**os.environ,'PYTHONPATH':str(module_root)}
    current=subprocess.check_output([sys.executable,'-c',code],env=env)
    pinned=subprocess.check_output([str(other),'-c',code],env=env)
    assert current==pinned

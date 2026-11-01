"""Byte-identical gzip headers and payloads across supported Python runtimes."""
import gzip
import shutil
import subprocess
import sys
from pathlib import Path

from engineering.design_search import portable_gzip


def test_canonical_wrapper_has_no_filename_timestamp_or_host_os():
    payload=b"OpenSourceRail candidate\n"*32
    compressed=portable_gzip.compress(payload)
    assert compressed[:10]==bytes.fromhex("1f8b08000000000002ff")
    assert gzip.decompress(compressed)==payload
    assert portable_gzip.compress(payload)==compressed


def test_other_available_python_runtimes_reproduce_exact_bytes():
    command="from engineering.design_search.portable_gzip import compress; import sys; sys.stdout.buffer.write(compress(b'OpenSourceRail candidate\\n'*32))"
    expected=portable_gzip.compress(b"OpenSourceRail candidate\n"*32)
    for name in ("python3.11","python3.12","python3.13"):
        runtime=shutil.which(name)
        if runtime:
            assert subprocess.check_output([runtime,"-c",command],cwd=Path(__file__).resolve().parents[3])==expected

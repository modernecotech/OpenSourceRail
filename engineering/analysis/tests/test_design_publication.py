"""A killed producer must leave an entire old or new published closure."""

from pathlib import Path
import os
import subprocess
import sys

import pytest

from engineering.design_engine.publication import hashes, publish


def fixture(tmp_path):
    source = tmp_path / "source"
    source.write_text("input")
    target = tmp_path / "current"
    target.mkdir()
    (target / "one.json").write_bytes(b"old one")
    (target / "two.json").write_bytes(b"old two")
    (target / "historical.json").write_bytes(b"frozen historical record")
    return target, hashes(tmp_path, ["source"])


def test_publication_preserves_complete_prior_generation_and_history(tmp_path):
    target, sources = fixture(tmp_path)
    previous = publish(
        target,
        {"one.json": b"new one", "two.json": b"new two"},
        repository=tmp_path,
        sources=sources,
        history=tmp_path / "history",
    )
    assert (previous / "one.json").read_bytes() == b"old one"
    assert (previous / "two.json").read_bytes() == b"old two"
    assert (target / "one.json").read_bytes() == b"new one"
    assert (target / "two.json").read_bytes() == b"new two"
    assert (target / "historical.json").read_bytes() == b"frozen historical record"


def test_source_changed_during_staging_cannot_publish(tmp_path):
    target, sources = fixture(tmp_path)

    def changed(stage):
        (tmp_path / "source").write_text("changed")

    with pytest.raises(ValueError, match="source changed"):
        publish(
            target,
            {"one.json": b"new"},
            repository=tmp_path,
            sources=sources,
            history=tmp_path / "history",
            before_commit=changed,
        )
    assert (target / "one.json").read_bytes() == b"old one"


def test_hard_crash_before_commit_leaves_complete_current_generation(tmp_path):
    target, sources = fixture(tmp_path)
    code = """import os,sys
from pathlib import Path
from engineering.design_engine.publication import publish,hashes
root=Path(sys.argv[1])
publish(root/'current',{'one.json':b'new one','two.json':b'new two'},repository=root,sources=hashes(root,['source']),history=root/'history',before_commit=lambda stage:os._exit(66))
"""
    root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-c", code, str(tmp_path)],
        cwd=root,
        env={**os.environ, "PYTHONPATH": str(root)},
        timeout=20,
    )
    assert result.returncode == 66
    assert (target / "one.json").read_bytes() == b"old one"
    assert (target / "two.json").read_bytes() == b"old two"


def test_escaping_artifact_path_is_rejected(tmp_path):
    target, sources = fixture(tmp_path)
    with pytest.raises(ValueError):
        publish(
            target,
            {"../escaped": b"bad"},
            repository=tmp_path,
            sources=sources,
            history=tmp_path / "history",
        )
    assert not (tmp_path / "escaped").exists()

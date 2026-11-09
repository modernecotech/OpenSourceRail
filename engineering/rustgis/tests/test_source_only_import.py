"""Synthetic import-policy controls only: no GIS, server or project workload."""
import hashlib
import importlib
import importlib.util
import marshal
import os
from pathlib import Path
import struct
import sys
import types

import pytest


# Bootstrap by exact file location, without first importing engineering. The
# real guard must authenticate this bootstrap file before loading it.
SPEC = importlib.util.spec_from_file_location(
    "_osr_source_only_import_test", Path(__file__).parents[1] / "source_only_import.py")
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)
NS = "osr_source_contract_fixture"
sha = lambda raw: hashlib.sha256(raw).hexdigest()


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    finders = []

    def write(relative, raw):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return sha(raw)

    def install(sources, **kwargs):
        finder = policy.install(repo_root=root, source_sha256=sources,
                                namespaces=(NS,), **kwargs)
        finders.append(finder)
        return finder

    yield root, write, install
    for finder in finders:
        finder.close()
    for name in list(sys.modules):
        if name == NS or name.startswith(NS + "."):
            del sys.modules[name]


def test_verified_source_package_relative_import_and_exact_execution_records(project):
    root, write, install = project
    sources = {
        NS + "/__init__.py": write(NS + "/__init__.py", b"from .answer import VALUE\n"),
        NS + "/answer.py": write(NS + "/answer.py", b"VALUE = 42\n"),
    }
    finder = install(sources)
    module = importlib.import_module(NS)
    assert module.VALUE == 42
    assert module.__cached__ is None
    assert {r["path"]: r["sha256"] for r in finder.records} == sources
    assert all(r["execution"] == "completed" and r["kind"] == "source" for r in finder.records)
    assert all(r["bytes"] == (root / r["path"]).stat().st_size for r in finder.records)
    # Returning a copy keeps a consumer from altering the retained trace.
    finder.records[0]["sha256"] = "0" * 64
    assert finder.records[0]["sha256"] != "0" * 64
    assert not list(root.rglob("__pycache__"))


def test_conflicting_existing_bytecode_is_never_opened_or_modified(project, monkeypatch):
    root, write, install = project
    relative = NS + "/answer.py"
    expected = write(relative, b"VALUE = 'authenticated source'\n")
    src = root / relative
    # A valid timestamp-pyc header names the current source metadata, but its
    # code is deliberately different. Both modern and sourceless forms exist.
    code = compile("VALUE = 'conflicting bytecode'", str(src), "exec")
    header = importlib.util.MAGIC_NUMBER + struct.pack("<III", 0, int(src.stat().st_mtime), src.stat().st_size)
    pyc = header + marshal.dumps(code)
    cached = Path(importlib.util.cache_from_source(str(src)))
    cached.parent.mkdir()
    cached.write_bytes(pyc)
    legacy = src.with_suffix(".pyc")
    legacy.write_bytes(pyc)
    finder = install({relative: expected})
    original_open = os.open

    def no_bytecode_open(path, *args, **kwargs):
        value = os.fspath(path)
        assert "__pycache__" not in value and not value.endswith(".pyc")
        return original_open(path, *args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(os, "open", no_bytecode_open)
        module = importlib.import_module(NS + ".answer")
    assert module.VALUE == "authenticated source"
    assert cached.read_bytes() == legacy.read_bytes() == pyc
    assert module.__cached__ is None
    assert finder.records[-1]["sha256"] == expected
    assert finder.records[0]["kind"] == "closed-namespace"


def test_unlisted_and_sourceless_modules_cannot_fall_through_to_other_finders(project, monkeypatch):
    root, write, install = project
    listed = NS + "/known.py"
    expected = write(listed, b"VALUE = 'known'\n")
    write(NS + "/omitted.py", b"raise AssertionError('unlisted source executed')\n")
    (root / NS / "sourceless.pyc").write_bytes(
        importlib.util.MAGIC_NUMBER + struct.pack("<III", 0, 0, 0) +
        marshal.dumps(compile("raise AssertionError('bytecode executed')", "sourceless", "exec")))
    monkeypatch.syspath_prepend(str(root))
    install({listed: expected})
    importlib.import_module(NS + ".known")
    for name in ("omitted", "sourceless"):
        with pytest.raises(ModuleNotFoundError, match="Source-only allowlist refuses"):
            importlib.import_module(NS + "." + name)


def test_stale_source_digest_refuses_before_execution(project):
    _, write, install = project
    relative = NS + "/changed.py"
    write(relative, b"raise AssertionError('changed source executed')\n")
    finder = install({relative: sha(b"different reviewed bytes\n")})
    with pytest.raises(policy.SourceImportError, match="SHA256 differs"):
        importlib.import_module(NS + ".changed")
    assert all(r["kind"] == "closed-namespace" for r in finder.records)


def test_allowlisted_but_absent_source_is_refused(project):
    root, _, install = project
    (root / NS).mkdir()
    install({NS + "/missing.py": sha(b"")})
    with pytest.raises(policy.SourceImportError, match="Missing, symlinked or inaccessible"):
        importlib.import_module(NS + ".missing")


@pytest.mark.parametrize("directory_link", [False, True])
def test_symlinked_source_or_namespace_is_refused(project, tmp_path, directory_link):
    root, _, install = project
    outside = tmp_path / "outside"
    outside.mkdir()
    raw = b"VALUE = 'outside'\n"
    (outside / "item.py").write_bytes(raw)
    if directory_link:
        (root / NS).symlink_to(outside, target_is_directory=True)
    else:
        (root / NS).mkdir()
        (root / NS / "item.py").symlink_to(outside / "item.py")
    install({NS + "/item.py": sha(raw)})
    with pytest.raises(policy.SourceImportError, match="symlinked"):
        importlib.import_module(NS + ".item")


@pytest.mark.parametrize("relative", ["../outside.py", NS + "/../outside.py",
    "/tmp/outside.py", NS + "//item.py", NS + "/item.pyc",
    NS + "/__pycache__/item.py"])
def test_allowlist_path_escape_and_noncanonical_paths_refuse(project, relative):
    _, _, install = project
    with pytest.raises(ValueError, match="repository-relative"):
        install({relative: sha(b"")})


def test_symlink_repository_root_refuses(tmp_path):
    actual = tmp_path / "actual"
    actual.mkdir()
    link = tmp_path / "link"
    link.symlink_to(actual, target_is_directory=True)
    with pytest.raises(policy.SourceImportError, match="ordinary directories"):
        policy.install(repo_root=link, source_sha256={}, namespaces=(NS,))


@pytest.mark.parametrize("initializer", ["__init__.py", "__init__.pyc"])
def test_closed_namespace_does_not_skip_an_unlisted_initializer(project, initializer):
    _, write, install = project
    write(NS + "/" + initializer, b"raise AssertionError('unlisted initializer executed')\n")
    expected = write(NS + "/item.py", b"VALUE = 1\n")
    install({NS + "/item.py": expected})
    with pytest.raises(policy.SourceImportError, match="Unlisted package initializer"):
        importlib.import_module(NS + ".item")


def test_preloaded_namespace_is_not_silently_relabelled(project):
    _, write, install = project
    expected = write(NS + "/item.py", b"VALUE = 1\n")
    sys.modules[NS] = types.ModuleType(NS)
    with pytest.raises(policy.SourceImportError, match="before importing"):
        install({NS + "/item.py": expected})


def test_bytecode_generation_must_already_be_disabled(project, monkeypatch):
    _, _, install = project
    monkeypatch.setattr(sys, "dont_write_bytecode", False)
    with pytest.raises(policy.SourceImportError, match="generation must be disabled"):
        install({})


def test_failed_authenticated_execution_is_retained(project):
    _, write, install = project
    relative = NS + "/failure.py"
    expected = write(relative, b"raise RuntimeError('declared test failure')\n")
    finder = install({relative: expected})
    with pytest.raises(RuntimeError, match="declared test failure"):
        importlib.import_module(NS + ".failure")
    assert finder.records[-1] == dict(module=NS + ".failure", path=relative,
        sha256=expected, bytes=len(b"raise RuntimeError('declared test failure')\n"),
        kind="source", execution="failed")


def test_bounded_source_size_and_ambiguous_package_are_refused(project):
    _, write, install = project
    expected = write(NS + "/item.py", b"VALUE = 'too long'\n")
    install({NS + "/item.py": expected}, max_source_bytes=4)
    with pytest.raises(policy.SourceImportError, match="bounded source"):
        importlib.import_module(NS + ".item")
    with pytest.raises(ValueError, match="Ambiguous"):
        install({NS + ".py": sha(b""), NS + "/__init__.py": sha(b"")})

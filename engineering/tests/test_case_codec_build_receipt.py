"""A cached Rust case codec needs exact source, tool and executable bytes."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import subprocess

import pytest


HELPER = Path(__file__).resolve().parents[2] / 'tools/automation/case_codec_build_receipt.py'
SPEC = spec_from_file_location('case_codec_build_receipt', HELPER)
receipt = module_from_spec(SPEC)
SPEC.loader.exec_module(receipt)


@pytest.fixture
def built(tmp_path, monkeypatch):
    root = tmp_path
    binary = root / receipt.BIN
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b'compiled Rust codec')
    binary.chmod(0o755)
    for name in receipt.REQUIRED_DEPENDENCIES:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name)
    for name in receipt.BUILD_INPUTS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name)
    depfile = root / receipt.DEPFILE
    depfile.write_text(str(binary) + ': ' + ' '.join(str(root / name)
                       for name in sorted(receipt.REQUIRED_DEPENDENCIES)) + '\n')
    monkeypatch.setattr(receipt, '_tool', lambda name: {'name': name, 'version': 'test tool'})
    monkeypatch.setattr(receipt, '_build_environment', lambda: {'CARGO_TARGET_DIR': str(root / 'target')})
    receipt.seal(root)
    assert receipt.check(root)
    return root


@pytest.mark.parametrize('name', [
    'crates/osr-design-search/src/columnar.rs',
    'crates/osr-design-search/src/lib.rs',
    'crates/osr-design-search/src/scheduling.rs',
    'Cargo.toml', 'crates/osr-design-search/Cargo.toml',
    'Cargo.lock', 'rust-toolchain.toml', 'osr',
    'tools/automation/case_codec_build_receipt.py',
])
def test_changed_source_requires_build(built, name):
    path = built / name
    path.write_bytes(path.read_bytes() + b' changed')
    assert not receipt.check(built)


def test_changed_executable_depfile_and_flags_require_build(built, monkeypatch):
    binary = built / receipt.BIN
    binary.write_bytes(binary.read_bytes() + b' tampered')
    assert not receipt.check(built)
    binary.write_bytes(b'compiled Rust codec')
    assert receipt.check(built)
    depfile = built / receipt.DEPFILE
    depfile.write_bytes(depfile.read_bytes() + b' ')  # Same source set, different receipt bytes.
    assert not receipt.check(built)
    depfile.write_bytes(depfile.read_bytes().rstrip() + b'\n')
    assert receipt.check(built)
    monkeypatch.setattr(receipt, '_build_environment', lambda: {'RUSTFLAGS': '-C target-cpu=native'})
    assert not receipt.check(built)


def test_changed_tool_identity_or_missing_receipt_requires_build(built, monkeypatch):
    monkeypatch.setattr(receipt, '_tool', lambda name: {'name': name, 'version': 'other tool'})
    assert not receipt.check(built)
    monkeypatch.setattr(receipt, '_tool', lambda name: {'name': name, 'version': 'test tool'})
    assert receipt.check(built)
    (built / receipt.RECEIPT).unlink()
    assert not receipt.check(built)


def test_changed_cargo_configuration_requires_build(built, monkeypatch):
    local = built / '.cargo/config.toml'
    local.parent.mkdir()
    local.write_text('[build]\nrustflags = []\n')
    home = built / 'cargo-home'
    home.mkdir()
    global_config = home / 'config.toml'
    global_config.write_text('[net]\noffline = true\n')
    monkeypatch.setenv('CARGO_HOME', str(home))
    receipt.seal(built)
    assert receipt.check(built)
    local.write_text('[build]\nrustflags = ["-C", "target-cpu=native"]\n')
    assert not receipt.check(built)
    local.write_text('[build]\nrustflags = []\n')
    assert receipt.check(built)
    global_config.write_text('[net]\noffline = false\n')
    assert not receipt.check(built)


def test_new_implicit_cargo_build_script_requires_build(built):
    build_script=built/'crates/osr-design-search/build.rs'
    build_script.write_text('fn main() {}\n')
    assert not receipt.check(built)


def test_changed_rust_wrapper_bytes_require_build(built, monkeypatch):
    wrapper = built / 'wrapper'
    wrapper.write_text('#!/bin/sh\nexit 0\n')
    wrapper.chmod(0o755)
    monkeypatch.setenv('RUSTC_WRAPPER', str(wrapper))
    receipt.seal(built)
    assert receipt.check(built)
    wrapper.write_text('#!/bin/sh\nexit 1\n')
    assert not receipt.check(built)


@pytest.mark.parametrize('name', [receipt.BIN, receipt.DEPFILE, receipt.RECEIPT])
def test_symlink_is_never_reused(built, name):
    path = built / name
    safe = path.with_name(path.name + '.original')
    path.rename(safe)
    path.symlink_to(safe)
    assert not receipt.check(built)


def test_failed_build_does_not_seal_new_receipt(built, monkeypatch):
    (built / receipt.RECEIPT).unlink()
    def fail(*_args, **_kwargs):
        raise subprocess.CalledProcessError(1, receipt.BUILD_COMMAND)
    monkeypatch.setattr(receipt.subprocess, 'run', fail)
    with pytest.raises(subprocess.CalledProcessError):
        receipt.build(built)
    assert not (built / receipt.RECEIPT).exists()


def test_successful_build_replaces_binary_and_seals_receipt(built, monkeypatch):
    (built / receipt.RECEIPT).unlink()
    def compile_fake(command, *, cwd, check):
        assert tuple(command) == receipt.BUILD_COMMAND and cwd == built and check
        binary = built / receipt.BIN
        assert not binary.exists() and not (built / receipt.DEPFILE).exists()
        binary.write_bytes(b'fresh compiled Rust codec')
        binary.chmod(0o755)
        (built / receipt.DEPFILE).write_text(str(binary) + ': ' + ' '.join(str(built / name)
                            for name in sorted(receipt.REQUIRED_DEPENDENCIES)) + '\n')
        return subprocess.CompletedProcess(command, 0)
    monkeypatch.setattr(receipt.subprocess, 'run', compile_fake)
    receipt.build(built)
    assert receipt.check(built)
    assert (built / receipt.BIN).read_bytes() == b'fresh compiled Rust codec'


def test_receipt_tamper_and_missing_compiled_source_fail_closed(built):
    record = built / receipt.RECEIPT
    record.write_bytes(record.read_bytes() + b' ')
    assert not receipt.check(built)
    receipt.seal(built)
    depfile = built / receipt.DEPFILE
    depfile.write_text(str(built / receipt.BIN) + ': ' +
                       ' '.join(str(built / name) for name in sorted(receipt.REQUIRED_DEPENDENCIES)
                                if not name.endswith('/scheduling.rs')) + '\n')
    assert not receipt.check(built)

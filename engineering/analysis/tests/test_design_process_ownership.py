"""Process identity portability must never turn missing procfs into takeover."""

import os
import subprocess
import sys

import pytest

from engineering.design_engine import store as module
from engineering.analysis.tests.test_design_engine import minimal_request


def missing_proc(_pid):
    raise FileNotFoundError("procfs unavailable in this environment")


def test_missing_proc_keeps_exclusive_dispatch_across_store_instances(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "_process_stat", missing_proc)
    first = module.Store(tmp_path)
    job = first.create(minimal_request())
    assert first.claim_dispatch(job["id"])
    second = module.Store(tmp_path)
    assert not second.claim_dispatch(job["id"])
    assert job["id"] not in second.pending()
    assert module.process_start(os.getpid()).startswith("local:")
    first.begin(job["id"], os.getpid())
    second.recover()
    assert second.get(job["id"])["status"] == "running"


def test_unverifiable_live_foreign_owner_is_not_recovered_or_redispatched(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "_process_stat", missing_proc)
    # A real child proves that the zero signal checks existence without ending
    # it. This test owns and cleans up only its own child.
    with subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"]) as child:
        try:
            assert module.process_ownership(child.pid, "local:foreign") is None
            store = module.Store(tmp_path)
            job = store.create(minimal_request())
            with store.connect() as con:
                con.execute("INSERT INTO dispatches VALUES(?,?,?)", (job["id"], child.pid, "local:foreign"))
            assert not store.claim_dispatch(job["id"])
            assert job["id"] not in store.pending()
            store.begin(job["id"], child.pid)
            store.recover()
            assert store.get(job["id"])["status"] == "running"
        finally:
            child.terminate()
            child.wait(timeout=5)
    store.recover()
    assert store.get(job["id"])["status"] == "interrupted"


def test_missing_and_mismatched_identity_are_distinguished(monkeypatch):
    monkeypatch.setattr(module, "process_start", lambda pid: "101")
    assert module.process_ownership(os.getpid(), "101") is True
    assert module.process_ownership(os.getpid(), "100") is False
    assert module.process_ownership(os.getpid(), None) is None
    assert module.process_ownership(os.getpid(), "local:other-platform") is None


def test_different_local_fallback_tokens_do_not_prove_pid_reuse(monkeypatch):
    # Reloading the Python module can renew a token while its owner stays alive.
    monkeypatch.setattr(module, "process_start", lambda pid: "local:new-module")
    assert module.process_ownership(os.getpid(), "local:prior-module") is None


def test_zombie_is_dead_even_though_zero_signal_can_succeed(monkeypatch):
    monkeypatch.setattr(module, "_process_stat", lambda pid: ("Z", "101"))
    assert module.process_ownership(os.getpid(), "101") is False


@pytest.mark.parametrize("pid", [None, 0, -1, "1", True])
def test_invalid_owner_never_targets_a_process_group(pid):
    assert module.process_ownership(pid, "101") is False


def test_permission_failure_is_unverifiable_not_dead(monkeypatch):
    monkeypatch.setattr(module, "_process_stat", missing_proc)
    monkeypatch.setattr(module, "process_start", lambda pid: None)
    def forbidden(_pid, _signal):
        raise PermissionError("a different user owns this process")
    monkeypatch.setattr(module.os, "kill", forbidden)
    assert module.process_ownership(123, "101") is None


def test_non_posix_unknown_owner_is_never_signalled(monkeypatch):
    monkeypatch.setattr(module, "process_start", lambda pid: None)
    monkeypatch.setattr(module, "_process_stat", missing_proc)
    monkeypatch.setattr(module.os, "name", "nt")
    def unsafe(_pid, _signal):
        pytest.fail("unknown owner must never be signalled outside POSIX")
    monkeypatch.setattr(module.os, "kill", unsafe)
    assert module.process_ownership(123, "101") is None

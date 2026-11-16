"""Concurrent, filesystem-aware disk admission without allocating large payloads."""
from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import pytest

from engineering import performance as p


def test_live_reservations_are_serialized_and_release_without_erasing_receipts(tmp_path, monkeypatch):
    monkeypatch.setattr(p.shutil, "disk_usage", lambda _: shutil._ntuple_diskusage(8*p.GIB, 3*p.GIB, 5*p.GIB))
    target = tmp_path / "state"
    target.mkdir()
    with p.disk_reservation(tmp_path, target, "first", 3*p.GIB, minimum_free_gib=1) as first:
        assert first["status"] == "reserved"
        with pytest.raises(p.DiskReservationHeld) as held:
            with p.disk_reservation(tmp_path, target, "second", 2*p.GIB, minimum_free_gib=1):
                pass
        assert held.value.record["peer_projected_bytes"] == 3*p.GIB
        assert p.check_disk_reservation(first)["reserve_status"] == "met"
    receipt = json.loads(Path(first["receipt"]).read_text())
    assert receipt["status"] == "completed"
    with p.disk_reservation(tmp_path, target, "second", 2*p.GIB, minimum_free_gib=1) as second:
        assert second["peer_projected_bytes"] == 0


def test_enospc_failure_retains_receipt_and_reclaims_kernel_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(p.shutil, "disk_usage", lambda _: shutil._ntuple_diskusage(8*p.GIB, 3*p.GIB, 5*p.GIB))
    with pytest.raises(OSError) as error:
        with p.disk_reservation(tmp_path, tmp_path, "failed", p.GIB,
                                minimum_free_gib=1) as lease:
            raise OSError(errno.ENOSPC, "simulated full disk")
    assert error.value.errno == errno.ENOSPC
    assert json.loads(Path(lease["receipt"]).read_text())["status"] == "failed"
    with p.disk_reservation(tmp_path, tmp_path, "retry", p.GIB,
                            minimum_free_gib=1) as retry:
        assert retry["peer_projected_bytes"] == 0


def test_default_floor_refuses_small_target_filesystem(tmp_path):
    assert shutil.disk_usage(tmp_path).total < 20*p.GIB
    with pytest.raises(p.DiskReservationHeld) as held:
        with p.disk_reservation(tmp_path, tmp_path, "small-fs", 1):
            pass
    assert held.value.record["minimum_free_reserve_bytes"] == 20*p.GIB
    assert json.loads(Path(held.value.record["receipt"]).read_text())["status"] == "held"


def test_unlocked_interrupted_receipt_is_preserved_and_not_charged(tmp_path, monkeypatch):
    monkeypatch.setattr(p.shutil, "disk_usage", lambda _: shutil._ntuple_diskusage(8*p.GIB, 3*p.GIB, 5*p.GIB))
    store = p._reservation_store(tmp_path)
    stale = store / "old.json"
    stale.write_text(json.dumps(dict(schema="osr-disk-reservation/1",
        filesystem_device=tmp_path.stat().st_dev, status="reserved",
        projected_bytes=3*p.GIB)))
    with p.disk_reservation(tmp_path, tmp_path, "new", 2*p.GIB,
                            minimum_free_gib=1) as lease:
        assert lease["interrupted_receipts_observed"] == 1
        assert lease["peer_projected_bytes"] == 0
    assert stale.exists()


def test_torn_unlocked_receipt_does_not_block_safe_admission(tmp_path, monkeypatch):
    monkeypatch.setattr(p.shutil, "disk_usage", lambda _: shutil._ntuple_diskusage(8*p.GIB, 3*p.GIB, 5*p.GIB))
    stale = p._reservation_store(tmp_path) / "torn.json"
    stale.write_bytes(b'{"schema":')
    with p.disk_reservation(tmp_path, tmp_path, "after-torn", p.GIB,
                            minimum_free_gib=1) as lease:
        assert lease["interrupted_receipts_observed"] == 1
        assert lease["peer_projected_bytes"] == 0
    assert stale.read_bytes() == b'{"schema":'


def test_crashed_peer_lock_releases_without_erasing_interrupted_receipt(tmp_path, monkeypatch):
    """A real second process must block a competing admission until it exits."""
    usage = shutil.disk_usage(tmp_path)
    floor = 1
    peer = max(1, usage.free - p.GIB - 256*1024*1024)
    if peer > 1024*p.GIB:
        pytest.skip("test filesystem is larger than the reservation budget")
    marker = tmp_path / "ready"
    script = (
        "from engineering.performance import disk_reservation\n"
        "from pathlib import Path\nimport sys,time\n"
        "r,t,m,b=sys.argv[1:]\n"
        "with disk_reservation(Path(r),Path(t),'peer',int(b),minimum_free_gib=1):\n"
        " Path(m).write_text('ready');time.sleep(10)\n"
    )
    child = subprocess.Popen([sys.executable, "-c", script, str(tmp_path),
                              str(tmp_path), str(marker), str(peer)])
    try:
        deadline = time.monotonic() + 3
        while not marker.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(.01)
        assert marker.exists() and child.poll() is None
        with pytest.raises(p.DiskReservationHeld):
            with p.disk_reservation(tmp_path, tmp_path, "competitor", 512*1024*1024,
                                    minimum_free_gib=floor):
                pass
    finally:
        child.terminate()
        child.wait(timeout=3)
    with p.disk_reservation(tmp_path, tmp_path, "after-crash", 1,
                            minimum_free_gib=floor) as lease:
        assert lease["interrupted_receipts_observed"] >= 1


def test_reserved_child_exit_and_checkpoint_hold_are_recorded(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(p.shutil, "disk_usage", lambda _: shutil._ntuple_diskusage(8*p.GIB, 3*p.GIB, 5*p.GIB))
    report, code = p.run_reserved_command(tmp_path, tmp_path, "child", 1,
        [sys.executable, "-c", "raise SystemExit(7)"], minimum_free_gib=1)
    assert code == 7 and report["status"] == "failed"
    assert json.loads(Path(report["receipt"]).read_text())["status"] == "failed"
    with p.disk_reservation(tmp_path, tmp_path, "checkpoint", 1,
                            minimum_free_gib=1) as lease:
        monkeypatch.setattr(p.shutil, "disk_usage", lambda _: shutil._ntuple_diskusage(8*p.GIB, 8*p.GIB, 0))
        with pytest.raises(p.DiskReservationHeld, match="below"):
            p.check_disk_reservation(lease)
    monkeypatch.setattr(p.shutil, "disk_usage", lambda _: shutil._ntuple_diskusage(8*p.GIB, 3*p.GIB, 5*p.GIB))
    assert p.main(["reserve-run", "--target", str(tmp_path),
                   "--reservation-action", "columnar-index", "--projected-bytes", "1",
                   "--minimum-free-gib", "1", "--", sys.executable, "-c", "pass"],
                  root=tmp_path) == 0
    assert json.loads(capsys.readouterr().out)["execution"] == "completed"


def test_reserved_command_stops_process_group_when_floor_is_crossed(tmp_path, monkeypatch):
    marker = tmp_path / "child-ready"
    real_usage = shutil._ntuple_diskusage(8*p.GIB, 3*p.GIB, 5*p.GIB)
    exhausted = shutil._ntuple_diskusage(8*p.GIB, 8*p.GIB, 0)
    monkeypatch.setattr(p.shutil, "disk_usage",
                        lambda _: exhausted if marker.exists() else real_usage)
    report, code = p.run_reserved_command(tmp_path, tmp_path, "guarded-child", 1,
        [sys.executable, "-c",
         "from pathlib import Path;import time;Path(%r).write_text('ready');time.sleep(10)" % str(marker)],
        minimum_free_gib=1, monitor_interval_seconds=.05)
    assert marker.exists() and code == 3 and report["reason"].startswith("Target filesystem fell below")
    receipt = json.loads(Path(report["receipt"]).read_text())
    assert receipt["status"] == "held"
    assert receipt["reason"] == report["reason"]


def test_reserve_run_can_send_receipt_to_stderr_without_polluting_jsonl(tmp_path, monkeypatch, capfd):
    monkeypatch.setattr(p.shutil, "disk_usage", lambda _: shutil._ntuple_diskusage(8*p.GIB, 3*p.GIB, 5*p.GIB))
    command = ["reserve-run", "--target", str(tmp_path),
               "--reservation-action", "columnar-query", "--projected-bytes", "1",
               "--minimum-free-gib", "1", "--receipt-to-stderr", "--",
               sys.executable, "-c", "print('{\"candidate_id\":\"abc\"}')"]
    assert p.main(command, root=tmp_path) == 0
    output = capfd.readouterr()
    assert output.out == '{"candidate_id":"abc"}\n'
    assert json.loads(output.err)["execution"] == "completed"

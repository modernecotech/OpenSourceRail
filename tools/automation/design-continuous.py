#!/usr/bin/env python3
"""Persistent mechanical, civil, software and integration research design runner."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.twin_workflow import core
from engineering.continuous_design import service

UNIT = "osr-continuous-design.service"


def unit_text(workspace):
    # systemd argument quoting is distinct from shell quoting; no shell is used.
    def quote(value):
        return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"').replace("%", "%%") + '"'
    command = " ".join(quote(x) for x in (sys.executable, Path(__file__).resolve(), "run", "--workspace", Path(workspace).resolve()))
    return ("[Unit]\nDescription=OpenSourceRail continuous engineering research\nAfter=network-online.target\nWants=network-online.target\n\n"
        "[Service]\nType=simple\nWorkingDirectory=" + str(ROOT).replace("%", "%%") + "\nExecStart=" + command + "\n"
        "Restart=on-failure\nRestartSec=30\nTimeoutStopSec=30\nKillMode=control-group\n"
        "Nice=10\nCPUQuota=250%\nMemoryHigh=6G\nMemoryMax=8G\nTasksMax=512\nUMask=0077\n"
        "StandardOutput=journal\nStandardError=journal\n\n[Install]\nWantedBy=default.target\n")


def install(workspace):
    path = Path.home() / ".config/systemd/user" / UNIT
    if path.exists() and not path.read_text().startswith("[Unit]\nDescription=OpenSourceRail continuous engineering research\n"):
        raise ValueError("existing service unit has another owner; review it explicitly")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(unit_text(workspace))
    temporary.replace(path)
    subprocess.run(["systemd-analyze", "--user", "verify", str(path)], check=True)
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", UNIT], check=True)
    return dict(service=UNIT, unit=str(path), workspace=str(Path(workspace).resolve()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    for name in ("init", "run", "status", "submit", "install", "verify", "history", "dashboard", "capability-prepare", "capability-check", "capability-register", "replay"):
        p = actions.add_parser(name)
        p.add_argument("--workspace", type=Path, default=service.DEFAULT)
        if name == "init":
            p.add_argument("--with-ai", action="store_true", help="Use the existing authenticated local Codex CLI as read-only proposer")
        if name == "submit":
            p.add_argument("--tasks", type=Path, required=True)
        if name == "verify":
            p.add_argument("--historical", action="store_true")
        if name == "history":
            p.add_argument("--baseline")
            p.add_argument("--lane",choices=service.tasks.LANES,required=True)
            p.add_argument("--after",type=int,default=0)
            p.add_argument("--limit",type=int,default=20)
        if name.startswith("capability-"):
            p.add_argument("--need",required=True)
        if name=="dashboard":
            p.add_argument("--output",type=Path)
        if name=="replay":
            p.add_argument("--include-blocked",action="store_true")
    p = actions.add_parser("worker", help=argparse.SUPPRESS)
    p.add_argument("--task", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = actions.add_parser("propose", help=argparse.SUPPRESS)
    p.add_argument("--request", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--executable", required=True)
    p.add_argument("--model", default="")
    args = parser.parse_args()
    if args.action == "init":
        baseline, _ = service.prepare(args.workspace, provider=args.with_ai)
        result = dict(baseline_sha256=baseline, **core.FLAGS)
    elif args.action == "install":
        result = install(args.workspace)
    elif args.action == "run":
        service.run(args.workspace)
        return
    elif args.action == "status":
        result = service.status(args.workspace)
    elif args.action == "dashboard":
        from engineering.continuous_design import reporting
        report=reporting.dashboard(service.status(args.workspace))
        if args.output:
            args.output.write_text(report+"\n")
        print(report)
        return
    elif args.action == "history":
        from engineering.continuous_design import proposals
        store=service.Store(args.workspace)
        baseline=args.baseline or core.read(args.workspace/"active.json")["baseline_sha256"]
        result=proposals.history(store,baseline,args.lane,after=args.after,limit=args.limit)
        store.db.close()
    elif args.action.startswith("capability-"):
        from engineering.continuous_design import capabilities
        store=service.Store(args.workspace)
        result=getattr(capabilities,args.action.split("-")[1])(store,args.need)
        store.db.close()
    elif args.action=="replay":
        import fcntl
        from engineering.continuous_design import ledger
        with (args.workspace/".service.lock").open("a") as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            store=service.Store(args.workspace)
            if args.include_blocked:
                with store.db:store.db.execute("UPDATE outbox SET state='pending',error=NULL WHERE state='blocked'")
            ledger.backfill(store)
            result=dict(delivered=ledger.dispatch(store))
            store.db.close()
    elif args.action == "submit":
        store = service.Store(args.workspace)
        baseline = core.read(args.workspace / "active.json")["baseline_sha256"]
        values = core.read(args.tasks)
        if not isinstance(values, list) or len(values) > 32:
            raise ValueError("at most 32 typed tasks per submission")
        for value in values:
            service.tasks.validate(value)
            store.validate_children(value, baseline)
        result = dict(added=sum(store.enqueue(v, baseline) for v in values), **core.FLAGS)
        store.db.close()
    elif args.action == "verify":
        result = service.verify(args.workspace, historical=args.historical)
    elif args.action == "worker":
        from engineering.continuous_design.worker import evaluate
        result = evaluate(core.read(args.task, maximum=10_000_000), args.output)
        core.write(args.output.parent / "result.json", result, exclusive=True)
    else:
        from engineering.continuous_design.proposer import run
        result = run(core.read(args.request, maximum=10_000_000), args.output, args.executable, args.model)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

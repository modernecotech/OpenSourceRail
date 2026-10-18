"""Isolated Git worktrees and benchmark-gated research adapter registration.

Git isolation protects the running source tree, not the operating system. New
adapters require repository review and explicit controller registration; AI
proposal responses never import or execute arbitrary new adapter code.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from engineering.twin_workflow import core


def prepare(store,need_key):
    row=store.db.execute("SELECT * FROM needs WHERE key=?",(need_key,)).fetchone()
    if row is None:
        raise ValueError("choose an existing missing-capability need key")
    folder=store.workspace/"capabilities"/need_key
    if (folder/"work-order.json").exists():
        return core.read(folder/"work-order.json")
    folder.mkdir(parents=True,exist_ok=True)
    tree=folder/"worktree"
    subprocess.run(["git","worktree","add","--detach","--no-checkout",str(tree),"HEAD"],cwd=core.ROOT,check=True,capture_output=True,text=True,timeout=60)
    subprocess.run(["git","sparse-checkout","set","--cone","engineering","design/component-catalogue/src","tools/automation"],
        cwd=tree,check=True,capture_output=True,text=True,timeout=120)
    order=dict(schema="osr-capability-work-order/1",need_key=need_key,item_id=row["item_id"],
        required=row["required"],worktree=str(tree),source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=tree,text=True).strip(),
        stages=dict(scope="defined",implementation="open",independent_benchmarks="open",adverse_tests="open",review="open",registration="open"),
        benchmark_requirements=["Independent reference behaviour","Adverse and boundary cases","Bounded resource use","Explicit limitations"],
        modules=[],benchmarks=[],limitations=[],**core.FLAGS)
    core.write(folder/"work-order.json",order,exclusive=True)
    return order


def check(store,need_key):
    folder=store.workspace/"capabilities"/need_key;order=core.read(folder/"work-order.json")
    tree=Path(order["worktree"])
    if not order["modules"] or not order["benchmarks"] or not order["limitations"]:
        raise ValueError("define adapter modules, independent benchmarks and limitations first")
    paths=order["modules"]+order["benchmarks"]
    for path in paths:
        target=(tree/path).resolve()
        if not target.is_relative_to(tree.resolve()) or not target.is_file() or not path.endswith(".py"):
            raise ValueError("capability files must be Python sources inside its worktree")
    if any(not p.startswith("engineering/analysis/tests/test_") for p in order["benchmarks"]):
        raise ValueError("benchmark tests must be separate test modules")
    command=[sys.executable,"-m","pytest",*order["benchmarks"],"-q"]
    before={p:core.sha(tree/p) for p in paths}
    result=subprocess.run(command,cwd=tree,capture_output=True,text=True,timeout=300,
        env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
    (folder/"benchmark.log").write_text(result.stdout+result.stderr)
    after={p:core.sha(tree/p) for p in paths}
    record=dict(command=command,passed=result.returncode==0 and before==after,returncode=result.returncode,
        source_sha256=before,source_unchanged=before==after,tested_unix=time.time(),
        benchmark_log_sha256=core.sha(folder/"benchmark.log"),limitations=order["limitations"],**core.FLAGS)
    core.write(folder/"benchmark-receipt.json",record)
    order["stages"].update(implementation="proposed",independent_benchmarks="passed" if record["passed"] else "failed",adverse_tests="benchmarked",review="open",registration="open")
    core.write(folder/"work-order.json",order)
    return record


def register(store,need_key):
    folder=store.workspace/"capabilities"/need_key;order=core.read(folder/"work-order.json")
    receipt=core.read(folder/"benchmark-receipt.json");review=core.read(folder/"review.json")
    if not receipt["passed"] or review.get("decision")!="register-for-research" or review.get("benchmark_receipt_sha256")!=core.sha(folder/"benchmark-receipt.json"):
        raise ValueError("passing benchmarks and a review of the exact benchmark receipt are required")
    if any(not (core.ROOT/path).is_file() or core.sha(core.ROOT/path)!=digest for path,digest in receipt["source_sha256"].items()):
        raise ValueError("reviewed adapter and benchmarks must match installed repository bytes")
    registration=dict(item_id=order["item_id"],need_key=need_key,source_sha256=receipt["source_sha256"],
        review_sha256=core.sha(folder/"review.json"),registered_unix=time.time(),
        scope=review["scope"],limitations=order["limitations"],**core.FLAGS)
    core.write(folder/"registration.json",registration)
    order["stages"].update(review="reviewed-exact-benchmark-receipt",registration="research-only")
    core.write(folder/"work-order.json",order)
    with store.db:
        store.db.execute("UPDATE needs SET state='research-capability-registered' WHERE key=?",(need_key,))
    return registration


def registered(store,item_id):
    for path in (store.workspace/"capabilities").glob("*/registration.json"):
        value=core.read(path)
        if value["item_id"]==item_id and all((core.ROOT/p).is_file() and core.sha(core.ROOT/p)==h for p,h in value["source_sha256"].items()):
            return True
    return False

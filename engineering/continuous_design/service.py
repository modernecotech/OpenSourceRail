"""Durable, fair four-lane scheduler with bounded workers and an optional proposer.

Research rejection is a completed experiment. Worker crashes receive bounded
retries in new attempt directories. Neither state can confer engineering release.
"""
from collections import Counter
import fcntl
import json
import os
from pathlib import Path
import shutil
import signal
import sqlite3
import subprocess
import sys
import time

from engineering.twin_workflow import core
from . import tasks, planning, ledger, proposals, research, runtime, capabilities

ROOT = core.ROOT
ENTRY = ROOT / "tools/automation/design-continuous.py"
DEFAULT = Path.home() / ".local/state/opensourcerail/continuous-design"


def source_snapshot():
    sources = core.sources()
    for path in [*Path(__file__).parent.glob("*.py"), ENTRY]:
        sources[path.relative_to(ROOT).as_posix()] = core.sha(path)
    for name in ("engineering/factory_examples/native.py","engineering/factory_examples/models.py"):
        sources[name]=core.sha(ROOT/name)
    name="engineering/analysis/tests/test_protocol_receiver.py"
    sources[name]=core.sha(ROOT/name)
    return sources


def unchanged(sources):
    return all((ROOT / n).is_file() and core.sha(ROOT / n) == h for n, h in sources.items())


class Store:
    MAX_PENDING_PER_LANE = 64

    def __init__(self, workspace):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = sqlite3.connect(self.workspace / "queue.sqlite", timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=FULL;
            CREATE TABLE IF NOT EXISTS jobs (
                key TEXT PRIMARY KEY, baseline TEXT NOT NULL, lane TEXT NOT NULL,
                task TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'queued',
                attempts INTEGER NOT NULL DEFAULT 0, ready REAL NOT NULL DEFAULT 0,
                folder TEXT, receipt_sha TEXT, error TEXT, created REAL NOT NULL, finished REAL);
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY, at REAL NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS provider (
                id INTEGER PRIMARY KEY, baseline TEXT NOT NULL, lane TEXT NOT NULL,
                request_hash TEXT NOT NULL, folder TEXT NOT NULL,
                status TEXT NOT NULL, created REAL NOT NULL, finished REAL, error TEXT,
                context_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS needs (
                key TEXT PRIMARY KEY, baseline TEXT NOT NULL, lane TEXT NOT NULL,
                item_id TEXT NOT NULL, required TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'open');
        """)
        if "priority" not in {r[1] for r in self.db.execute("PRAGMA table_info(jobs)")}:
            self.db.execute("ALTER TABLE jobs ADD COLUMN priority INTEGER NOT NULL DEFAULT 10")
        self.db.execute("CREATE INDEX IF NOT EXISTS jobs_dispatch ON jobs(baseline,lane,status,priority,created)")
        self.db.commit()
        ledger.initialise(self)
        research.initialise(self)

    def event(self, kind, payload):
        with ledger.transaction(self.db):
            self.db.execute("INSERT INTO events(at,kind,payload) VALUES(?,?,?)", (time.time(), kind, json.dumps(payload)))

    def enqueue(self, value, baseline, *, priority=10):
        lane = tasks.validate(value)
        if value["kind"]=="software-receiver" and not capabilities.registered(self,"software-frame-receiver"):
            raise ValueError("receiver capability requires exact benchmark/review registration")
        key = tasks.identity(value, baseline)
        if self.db.execute("SELECT 1 FROM jobs WHERE key=?", (key,)).fetchone():
            return False
        self.validate_children(value, baseline)
        pending = self.db.execute("SELECT COUNT(*) FROM jobs WHERE baseline=? AND lane=? AND status IN ('queued','running')", (baseline, lane)).fetchone()[0]
        state = "deferred" if pending >= self.MAX_PENDING_PER_LANE else "queued"
        with ledger.transaction(self.db):
            cursor = self.db.execute("INSERT OR IGNORE INTO jobs(key,baseline,lane,task,status,priority,created) VALUES(?,?,?,?,?,?,?)",
                (key, baseline, lane, json.dumps(value, sort_keys=True), state, priority, time.time()))
        return bool(cursor.rowcount)

    def promote(self, baseline):
        for lane in tasks.LANES:
            pending = self.db.execute("SELECT COUNT(*) FROM jobs WHERE baseline=? AND lane=? AND status IN ('queued','running')", (baseline, lane)).fetchone()[0]
            with self.db:
                self.db.execute("UPDATE jobs SET status='queued' WHERE key IN (SELECT key FROM jobs WHERE baseline=? AND lane=? AND status='deferred' ORDER BY priority,created LIMIT ?)",
                    (baseline, lane, max(0, self.MAX_PENDING_PER_LANE - pending)))

    def record_needs(self, baseline, lane, rows):
        with ledger.transaction(self.db):
            for row in rows:
                key = core.digest(dict(baseline=baseline, lane=lane, **row))
                self.db.execute("INSERT OR IGNORE INTO needs(key,baseline,lane,item_id,required) VALUES(?,?,?,?,?)",
                    (key, baseline, lane, row["item_id"], row["required"]))

    def validate_children(self, value, baseline):
        if value["kind"].endswith("-confirmation"):
            row=self.db.execute("SELECT * FROM jobs WHERE key=? AND baseline=? AND status='completed'",(value["parameters"]["child"],baseline)).fetchone()
            if row is None or json.loads(row["task"])["kind"]!=value["kind"].replace("-confirmation","-detail"):
                raise ValueError("confirmation needs a completed exact detailed child")
            return
        if value["kind"] != "integration-coupling":
            return
        children = [self.db.execute("SELECT * FROM jobs WHERE key=? AND baseline=? AND status='completed'", (k, baseline)).fetchone()
                    for k in value["parameters"]["children"]]
        if any(r is None for r in children) or {json.loads(r["task"])["kind"] for r in children} != {
            "mechanical-detail", "civil-detail", "software-logic"}:
            raise ValueError("integration needs completed exact mechanical/civil/software children")
        parsed = {json.loads(r["task"])["kind"]: json.loads(r["task"])["parameters"] for r in children}
        _, mapping = tasks.contexts("civil-detail")
        civil = mapping[parsed["civil-detail"]["context_id"]]
        if civil["architecture_id"] != parsed["mechanical-detail"]["context_id"]:
            raise ValueError("integration children have different train configurations")

    def result(self, row):
        folder = Path(row["folder"])
        if core.sha(folder / "receipt.json") != row["receipt_sha"]:
            raise ValueError("changed queued child receipt: " + row["key"])
        receipt = core.read(folder / "receipt.json", maximum=10_000_000)
        for name, expected in receipt["files_sha256"].items():
            path = (folder / name).resolve()
            if not path.is_relative_to(folder.resolve()) or core.sha(path) != expected:
                raise ValueError("changed retained child artifact: " + name)
        return core.read(folder / "result.json", maximum=10_000_000)

    def recover(self):
        ledger.recover_outputs(self)
        with self.db:
            self.db.execute("UPDATE jobs SET status=CASE WHEN attempts<2 THEN 'queued' ELSE 'error' END, "
                "error='interrupted; partial attempt retained',ready=? WHERE status='running'", (time.time(),))
            self.db.execute("UPDATE provider SET status='interrupted',finished=? WHERE status='running'", (time.time(),))
        ledger.backfill(self)
        ledger.dispatch(self)

    def integration_jobs(self, baseline):
        return planning.integration_frontier(self, baseline)


def config_default():
    return dict(concurrency=3, poll_seconds=5, worker_timeout_seconds=900,
        max_output_gib=8, reserve_gib=10, max_attempt_mib=512,
        provider_enabled=False, provider_executable=shutil.which("codex") or "codex",
        provider_model="",
        provider_interval_seconds=600, provider_timeout_seconds=300,
        max_provider_calls_per_hour=8)


def validate_config(config):
    if set(config) != set(config_default()) or type(config["concurrency"]) is not int or not 1 <= config["concurrency"] <= 3:
        raise ValueError("exact runner configuration and concurrency 1..3 required")
    bounds = dict(poll_seconds=(.1, 60), worker_timeout_seconds=(1, 3600), max_output_gib=(.01, 50),
        reserve_gib=(.1, 100), max_attempt_mib=(1, 2048), provider_interval_seconds=(10, 86400),
        provider_timeout_seconds=(1, 900), max_provider_calls_per_hour=(1, 24))
    import math
    for key, (low, high) in bounds.items():
        value = config[key]
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError("invalid resource configuration: " + key)
    if type(config["provider_enabled"]) is not bool or not isinstance(config["provider_executable"], str):
        raise ValueError("invalid proposer configuration")
    import re
    if not isinstance(config["provider_model"], str) or (config["provider_model"] and not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}", config["provider_model"])):
        raise ValueError("invalid proposer model identifier")


def prepare(workspace, *, provider=False):
    workspace = Path(workspace).resolve()
    store = Store(workspace)
    path = workspace / "config.json"
    if not path.exists():
        config = config_default()
        config["provider_enabled"] = provider
        core.write(path, config, exclusive=True)
    validate_config(core.read(path))
    sources = source_snapshot()
    identity=runtime.capture()
    baseline = core.digest(dict(sources=sources,runtime=identity))
    epoch = workspace / "epochs" / baseline
    previous = core.read(workspace / "active.json")["baseline_sha256"] if (workspace / "active.json").is_file() else None
    if epoch.exists() and not (epoch / "baseline.json").is_file():
        epoch.rename(epoch.with_name(epoch.name + ".interrupted-" + str(time.time_ns())))
    if not epoch.exists():
        from engineering.generative_design import digital_thread
        digital_thread.verify(core.PACKET)
        core.initialise(epoch / "work-orders")
        core.write(epoch / "baseline.json", dict(baseline_sha256=baseline, source_sha256=sources,runtime_identity=identity, **core.FLAGS), exclusive=True)
        store.event("new-baseline", dict(baseline=baseline))
    if not (epoch / "historical-inputs.json").exists():
        nominations = planning.historical_inputs(store, previous, baseline) if previous and previous != baseline else []
        core.write(epoch / "historical-inputs.json", dict(previous_baseline=previous,
            nominations=nominations, acceptance_reused=False, **core.FLAGS), exclusive=True)
    for value in tasks.seeds():
        store.enqueue(value, baseline)
    if capabilities.registered(store,"software-frame-receiver"):
        from . import protocol_receiver
        for value in protocol_receiver.seeds():
            store.enqueue(value,baseline,priority=-15)
    core.write(workspace / "active.json", dict(baseline_sha256=baseline, epoch=str(epoch), **core.FLAGS))
    store.db.close()
    return baseline, sources


def status(workspace):
    workspace = Path(workspace).resolve()
    store = Store(workspace)
    active = core.read(workspace / "active.json")
    baseline = active["baseline_sha256"]
    lanes = {}
    for lane in tasks.LANES:
        counts = Counter(r["status"] for r in store.db.execute("SELECT status FROM jobs WHERE baseline=? AND lane=?", (baseline, lane)))
        lanes[lane] = {k: counts[k] for k in ("queued", "deferred", "running", "completed", "error")}
    runtime = core.read(workspace / "status.json") if (workspace / "status.json").exists() else {}
    result = dict(workspace=str(workspace), baseline_sha256=baseline, lanes=lanes,
        research=research.summary(store,baseline),
        outbox_states=dict(Counter(r[0] for r in store.db.execute("SELECT state FROM outbox WHERE baseline=?",(baseline,)))),
        oldest_waiting_unix=store.db.execute("SELECT MIN(created) FROM jobs WHERE baseline=? AND status IN ('queued','deferred')",(baseline,)).fetchone()[0],
        blocked_capabilities=[dict(r) for r in store.db.execute("SELECT lane,item_id,required,state FROM needs WHERE baseline=? AND state='open' LIMIT 30",(baseline,))],
        max_pending_per_lane=Store.MAX_PENDING_PER_LANE, lifetime_experiment_cap=None,
        heartbeat_age_seconds=max(0, time.time() - runtime.get("heartbeat_unix", 0)),
        runtime=runtime, provider_calls=store.db.execute("SELECT COUNT(*) FROM provider WHERE baseline=?", (baseline,)).fetchone()[0],
        provider_states=dict(Counter(r[0] for r in store.db.execute("SELECT status FROM provider WHERE baseline=?", (baseline,)))),
        open_provider_needs=store.db.execute("SELECT COUNT(*) FROM needs WHERE baseline=?", (baseline,)).fetchone()[0], **core.FLAGS)
    store.db.close()
    return result


def provider_request(store, baseline, lane):
    rows = list(store.db.execute("SELECT * FROM jobs WHERE baseline=? AND lane=? AND status IN ('completed','error') ORDER BY finished DESC,created DESC LIMIT 8", (baseline, lane)))
    rows += list(store.db.execute("SELECT * FROM jobs WHERE baseline=? AND lane=? AND status NOT IN ('completed','error') ORDER BY priority,created LIMIT 4", (baseline, lane)))
    feedback = []
    for row in rows:
        feedback.append(proposals.compact_feedback(planning.feedback(row, json.loads(row["task"]), store.result(row) if row["status"] == "completed" else None)))
    available = planning.child_catalogue(store, baseline, limit=24) if lane == "integration" else []
    orders_path = store.workspace / "epochs" / baseline / "work-orders/work-orders.json"
    package_scope = []
    if orders_path.is_file():
        orders = core.read(orders_path, maximum=10_000_000)
        for package in orders["packages"]:
            if lane in str(package.get("domain", "")):
                package_scope.append({k: package[k] for k in ("id", "title", "domain", "completion_artifacts") if k in package})
    return proposals.bounded(dict(schema="osr-continuous-proposal-request/2", lane=lane, baseline_sha256=baseline,
        domains=registered_domains(store,lane), feedback=feedback,
        available_children=available, package_scope=package_scope,
        progress_signature=research.progress_signature(store,baseline,lane),
        tradeoffs=research.tradeoffs(store,baseline,lane),
        coverage=research.coverage(store,baseline,lane),
        existing_designs=proposals.representatives(store, baseline, lane),
        history_lookup=dict(workspace=str(store.workspace), lane=lane,
            command="tools/automation/osr-python tools/automation/design-continuous.py history",
            arguments=dict(baseline=baseline, after=0, limit=20), complete_history_included=False),
        instructions="Propose up to three DISTINCT useful designs using supported domains and actual failures. "
        "Return parameters as JSON text in parameters_json. Do not change loads, limits, fixtures or source. "
        "Read-only proposal work only: no edits, commits, uploads, messages, deployment or additional agents. "
        "If adapters/evidence are missing, return precise needs instead of a fabricated pass. "
        "For integration use exact mechanical-detail/civil-detail/software-logic keys from the existing service data. "
        "Prioritize children with study_pass=true and matching architecture_id; civil context_id identifies each span. "
        "study_pass means only implemented offline checks pass: false release flags do not prevent a research study pass. "
        "Use declared provisional inputs; accepted physical evidence is not required to propose a research trial. "
        "A null family bound means no such bound is provided, not that context data is missing. "
        "Needs: item_id is a short capability identifier; required is the concrete missing work/evidence description, never a boolean. "
        "You may inspect engineering source and paginated history locally. No production release is available.", **core.FLAGS))


def registered_domains(store,lane):
    domains=tasks.domain_description(lane)
    if lane=="software" and not capabilities.registered(store,"software-frame-receiver"):
        domains.pop("software-receiver",None)
    return domains


def validated_proposals(store, baseline, lane, response):
    if not isinstance(response, dict) or set(response) != {"proposals", "needs"}:
        raise ValueError("exact provider response required")
    if not isinstance(response["proposals"], list) or len(response["proposals"]) > 3 or not isinstance(response["needs"], list) or len(response["needs"]) > 10:
        raise ValueError("provider response exceeds candidate/need bounds")
    # Validate the entire response before accepting any part of it.
    values = []
    for row in response["proposals"]:
        if not isinstance(row, dict) or set(row) != {"kind", "parameters_json", "rationale"} or not isinstance(row["parameters_json"], str):
            raise ValueError("typed proposal required")
        params = json.loads(row["parameters_json"], parse_constant=lambda v: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
        value = tasks.task(row["kind"], params, row["rationale"])
        if tasks.validate(value) != lane:
            raise ValueError("proposer cannot submit to another lane")
        store.validate_children(value, baseline)
        values.append(value)
    for row in response["needs"]:
        if not isinstance(row, dict) or set(row) != {"item_id", "required"} or any(
            not isinstance(row[k], str) or not 1 <= len(row[k]) <= 8000 for k in row):
            raise ValueError("typed missing-evidence need required")
        if len(row["item_id"])>200 or len(row["required"].strip())<12 or row["required"].strip().lower() in {"true","false","yes","no","required"}:
            raise ValueError("need requires a short identifier and concrete missing-work description")
    return values, response["needs"]


def import_proposals(store, baseline, lane, response):
    values, needs = validated_proposals(store, baseline, lane, response)
    with ledger.transaction(store.db):
        added = sum(store.enqueue(v, baseline) for v in values)
        store.record_needs(baseline, lane, needs)
    return added


def _stop(process):
    if process.poll() is None:
        from engineering.design_engine.generated_parts_native import _stop_owned_descendants
        _stop_owned_descendants(process)


def next_provider(store, baseline, config, now):
    if not config["provider_enabled"]:
        return None
    calls = store.db.execute("SELECT COUNT(*) FROM provider WHERE created>?", (now - 3600,)).fetchone()[0]
    if calls >= config["max_provider_calls_per_hour"]:
        return None
    served = {lane: store.db.execute("SELECT MAX(created) FROM provider WHERE lane=?", (lane,)).fetchone()[0] for lane in tasks.LANES}
    for lane in sorted(tasks.LANES, key=lambda lane: (served[lane] if served[lane] is not None else -1, tasks.LANES.index(lane))):
        if store.db.execute("SELECT COUNT(*) FROM jobs WHERE baseline=? AND lane=? AND status IN ('queued','running','deferred')", (baseline, lane)).fetchone()[0] >= Store.MAX_PENDING_PER_LANE:
            continue
        last = store.db.execute("SELECT MAX(COALESCE(finished,created)) FROM provider WHERE lane=?", (lane,)).fetchone()[0]
        if last is not None and now - last < config["provider_interval_seconds"]:
            continue
        request = provider_request(store, baseline, lane)
        request_hash = core.digest(request.get("progress_signature",request))
        previous = list(store.db.execute("SELECT * FROM provider WHERE baseline=? AND lane=? AND context_hash=? ORDER BY created", (baseline, lane, request_hash)))
        if previous:
            last_call = previous[-1]
            if last_call["status"] not in {"error", "interrupted"} or len(previous) >= 3 or now - (last_call["finished"] or last_call["created"]) < 1800:
                continue
        return lane, request, request_hash, len(previous)
    return None


def run(workspace, *, once=False):
    workspace = Path(workspace).resolve()
    lock = (workspace / ".service.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    baseline, sources = prepare(workspace)
    store = Store(workspace)
    store.recover()
    binding=core.read(workspace/"epochs"/baseline/"baseline.json")
    runtime_sha=runtime.digest(binding["runtime_identity"])
    runtime_ok,last_runtime_check=True,0.
    active, stopping, cursor, last_integrated_count = {}, False, 0, -1
    def stop_signal(_number, _frame):
        nonlocal stopping
        stopping = True
    if not once:
        signal.signal(signal.SIGTERM, stop_signal)
        signal.signal(signal.SIGINT, stop_signal)
    mode, last_size_check, used = "running", 0., 0
    try:
        while not stopping:
            config = core.read(workspace / "config.json")
            validate_config(config)
            now = time.time()
            if now-last_runtime_check>=60:
                runtime_ok=runtime.digest(runtime.capture())==runtime_sha
                last_runtime_check=now
            if now - last_size_check >= 15:
                used = core._size(workspace)
                last_size_check = now
            free = shutil.disk_usage(workspace).free
            source_ok = unchanged(sources) and runtime_ok
            capacity = used < config["max_output_gib"] * 1024**3 and free >= config["reserve_gib"] * 1024**3
            mode = "running" if source_ok and capacity else ("waiting_for_runtime_restart" if not runtime_ok else "waiting_for_source_restart" if not source_ok else "waiting_for_disk")
            for key, job in list(active.items()):
                process, folder = job["process"], job["folder"]
                reason = None
                limit = config["provider_timeout_seconds"] if job["provider"] else config["worker_timeout_seconds"]
                if now - job["started"] > limit:
                    reason = "worker timeout"
                if job["provider"]:
                    reason = proposals.budget_error(folder) or reason
                elif core._size(folder) > config["max_attempt_mib"] * 1024**2:
                    reason = "attempt output budget"
                if not capacity:
                    reason = "workspace disk budget"
                if reason:
                    _stop(process)
                if process.poll() is None:
                    continue
                for stream in job["streams"]:
                    stream.close()
                try:
                    if reason or process.returncode != 0 or not unchanged(sources) or runtime.digest(runtime.capture())!=runtime_sha:
                        raise ValueError(reason or "process failed or input sources changed; inspect retained logs")
                    if job["provider"]:
                        response = core.read(folder / "response.json",maximum=proposals.MAX_RESPONSE_BYTES)
                        values, needs = validated_proposals(store, baseline, job["lane"], response)
                        ledger.complete_provider(store, job["id"], values, needs, core.sha(folder / "response.json"))
                    else:
                        result = core.read(folder / "result.json", maximum=10_000_000)
                        if type(result.get("study_pass")) is not bool or any(result.get(k) is not False for k in core.FLAGS):
                            raise ValueError("worker result cannot confer acceptance")
                        receipt = dict(key=key, baseline_sha256=baseline, task=job["task"],
                            files_sha256={p.relative_to(folder).as_posix(): core.sha(p) for p in sorted(folder.rglob("*")) if p.is_file()}, **core.FLAGS)
                        core.write(folder / "receipt.json", receipt, exclusive=True)
                        ledger.complete_job(store, key, core.sha(folder / "receipt.json"), result, now=now)
                        store.event("completed", dict(key=key, lane=job["lane"], study_pass=result["study_pass"]))
                except (ValueError, OSError, TypeError, KeyError) as exc:
                    if job["provider"]:
                        with store.db:
                            store.db.execute("UPDATE provider SET status='error',error=?,finished=? WHERE id=?", (str(exc), now, job["id"]))
                    else:
                        with store.db:
                            store.db.execute("UPDATE jobs SET status=CASE WHEN attempts<2 THEN 'queued' ELSE 'error' END,error=?,ready=? WHERE key=?",
                                (str(exc), now + 30, key))
                    store.event("attempt-error", dict(key=key, reason=str(exc)))
                del active[key]
            ledger.dispatch(store)
            if mode == "running":
                store.promote(baseline)
                completed_count = store.db.execute("SELECT COUNT(*) FROM jobs WHERE baseline=? AND status='completed'", (baseline,)).fetchone()[0]
                if completed_count != last_integrated_count:
                    store.integration_jobs(baseline)
                    last_integrated_count = completed_count
                # Reserve one slot when the single AI proposer is due. Otherwise
                # continuously replenished numerical queues could starve it.
                pending_provider = None if any(j["provider"] for j in active.values()) else next_provider(store, baseline, config, now)
                worker_slots = config["concurrency"] - int(pending_provider is not None)
                for _ in tasks.LANES:
                    if len(active) >= worker_slots:
                        break
                    lane = tasks.LANES[cursor % len(tasks.LANES)]
                    cursor += 1
                    if any(j["lane"] == lane and not j["provider"] for j in active.values()):
                        continue
                    row = store.db.execute("SELECT * FROM jobs WHERE baseline=? AND lane=? AND status='queued' AND ready<=? ORDER BY priority,created LIMIT 1",
                        (baseline, lane, now)).fetchone()
                    if row is None:
                        continue
                    value = json.loads(row["task"])
                    folder = workspace / "epochs" / baseline / "attempts" / row["key"] / f"{row['attempts'] + 1:03d}"
                    with store.db:
                        store.db.execute("UPDATE jobs SET status='running',attempts=attempts+1,folder=? WHERE key=?", (str(folder), row["key"]))
                    folder.mkdir(parents=True, exist_ok=False)
                    dependencies = []
                    child_keys=value["parameters"].get("children", [])
                    if value["kind"].endswith("-confirmation"):
                        child_keys=[value["parameters"]["child"]]
                    for child in child_keys:
                        dep = store.db.execute("SELECT * FROM jobs WHERE key=? AND baseline=? AND status='completed'", (child, baseline)).fetchone()
                        if dep is None:
                            raise ValueError("integration child unavailable")
                        store.result(dep)
                        dependencies.append(dict(key=child, task=json.loads(dep["task"]), folder=dep["folder"], receipt_sha256=dep["receipt_sha"]))
                    envelope = dict(task=value, key=row["key"], baseline_sha256=baseline, dependencies=dependencies,
                        runtime_sha256=runtime_sha)
                    core.write(folder / "task.json", envelope, exclusive=True)
                    stdout, stderr = (folder / "worker.log").open("wb"), (folder / "worker.stderr.log").open("wb")
                    argv = [sys.executable, str(ENTRY), "worker", "--task", str(folder / "task.json"), "--output", str(folder / "output")]
                    process = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                        start_new_session=True, env={**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1"})
                    active[row["key"]] = dict(process=process, folder=folder, streams=(stdout, stderr), task=value, lane=lane, started=now, provider=False)
                if pending_provider is not None and len(active) < config["concurrency"]:
                    lane, request, request_hash, previous_count = pending_provider
                    folder = workspace / "epochs" / baseline / "provider" / f"{lane}-{time.time_ns()}"
                    folder.mkdir(parents=True)
                    core.write(folder / "request.json", request, exclusive=True)
                    stdout, stderr = (folder / "provider.log").open("wb"), (folder / "provider.stderr.log").open("wb")
                    argv = [sys.executable, str(ENTRY), "propose", "--request", str(folder / "request.json"), "--output", str(folder), "--executable", config["provider_executable"]]
                    if config["provider_model"]:
                        argv += ["--model", config["provider_model"]]
                    with store.db:
                        cur = store.db.execute("INSERT INTO provider(baseline,lane,request_hash,context_hash,folder,status,created) VALUES(?,?,?,?,?,?,?)",
                            (baseline, lane, core.digest([request_hash, previous_count]), request_hash, str(folder), "running", now))
                    process = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True)
                    key = "provider-" + str(cur.lastrowid)
                    active[key] = dict(process=process, folder=folder, streams=(stdout, stderr), lane=lane, started=now, provider=True, id=cur.lastrowid)
            if mode == "running" and not active:
                mode = "watching_for_new_work"
            if mode in {"waiting_for_source_restart","waiting_for_runtime_restart"} and not active:
                # A fresh interpreter binds new committed code; never attach new
                # hashes to old imported implementation. Dirty edits wait safely.
                clean = subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd=ROOT).returncode == 0
                if clean:
                    raise RuntimeError("committed sources changed; supervisor restart creates a fresh baseline")
            core.write(workspace / "status.json", dict(heartbeat_unix=now, pid=os.getpid(), state=mode,
                active=[dict(key=k, lane=j["lane"], provider=j["provider"], pid=j["process"].pid) for k, j in active.items()],
                used_bytes=used, disk_free_bytes=free, baseline_sha256=baseline, **core.FLAGS))
            if once:
                break
            time.sleep(config["poll_seconds"])
    finally:
        for job in active.values():
            _stop(job["process"])
            for stream in job["streams"]:
                stream.close()
        store.recover()
        core.write(workspace / "status.json", dict(heartbeat_unix=time.time(), pid=os.getpid(), state="stopped", active=[], **core.FLAGS))
        store.db.close()
        lock.close()


def verify(workspace, *, historical=False):
    workspace = Path(workspace).resolve()
    store = Store(workspace)
    active = core.read(workspace / "active.json")
    binding = core.read(Path(active["epoch"]) / "baseline.json")
    expected=core.digest(dict(sources=binding["source_sha256"],runtime=binding["runtime_identity"])) if "runtime_identity" in binding else core.digest(binding["source_sha256"])
    if expected != active["baseline_sha256"] or (
        not historical and not unchanged(binding["source_sha256"])):
        raise ValueError("baseline/source applicability failed")
    if not historical and "runtime_identity" in binding and runtime.digest(runtime.capture())!=runtime.digest(binding["runtime_identity"]):
        raise ValueError("numerical runtime identity changed")
    count = 0
    for row in store.db.execute("SELECT * FROM jobs WHERE baseline=? AND status='completed'", (active["baseline_sha256"],)):
        result = store.result(row)
        if tasks.identity(json.loads(row["task"]), row["baseline"]) != row["key"] or any(result.get(k) is not False for k in core.FLAGS):
            raise ValueError("task identity or acceptance flags changed")
        if "runtime_identity" in binding and result.get("runtime_sha256")!=runtime.digest(binding["runtime_identity"]):
            raise ValueError("completed worker is not bound to the epoch runtime")
        count += 1
    result = dict(verified_completed_experiments=count, current_sources_required=not historical,
                  source_and_artifact_integrity=True, physics_rerun=False,
                  runtime_identity_checked=not historical and "runtime_identity" in binding, **core.FLAGS)
    store.db.close()
    return result

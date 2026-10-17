"""Bounded proposal evaluation in disposable Git worktrees, using the common store.

Proposals are data from named agents. This controller runs declared tools, not an
LLM service. Worktrees isolate revisions; they are not a security sandbox.
Acceptance commands belong to the controller policy, never the proposal.
"""

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import re
import selectors
import signal
import subprocess
import threading
import time

from engineering.design_engine.contracts import fingerprint
from engineering.design_engine.store import Store, write_new

_GIT_LOCK = threading.Lock()


def _git(root, *argv):
    return (
        subprocess.check_output(
            ["git", "-C", str(root), *argv], stderr=subprocess.STDOUT
        )
        .decode()
        .strip()
    )


def _path(value):
    p = PurePosixPath(value)
    if not value or p.is_absolute() or ".." in p.parts or p.as_posix() != value:
        raise ValueError("repository-relative path required")
    return value


def _validate(proposals, policy, concurrency):
    if type(concurrency) is not int or not 1 <= concurrency <= 3:
        raise ValueError("worker concurrency must be 1..3")
    if set(policy) != {
        "checkout_paths",
        "commands",
        "timeout_seconds",
        "max_candidates",
        "allowed_paths",
        "acceptance_files",
        "toolchain",
        "max_log_bytes",
    }:
        raise ValueError("exact controller-owned execution policy required")
    if (
        type(policy["max_candidates"]) is not int
        or not 1 <= policy["max_candidates"] <= 32
    ):
        raise ValueError("candidate budget must be 1..32")
    if not 0 < len(proposals) <= policy["max_candidates"]:
        raise ValueError("candidate budget exceeded")
    if (
        type(policy["timeout_seconds"]) is not int
        or not 1 <= policy["timeout_seconds"] <= 300
    ):
        raise ValueError("wall budget must be 1..300 seconds per command")
    for key in ("checkout_paths", "allowed_paths"):
        if not policy[key] or len(set(policy[key])) != len(policy[key]):
            raise ValueError("distinct explicit " + key + " required")
        for value in policy[key]:
            _path(value)
    if not 1 <= len(policy["commands"]) <= 16 or any(
        not isinstance(argv, list)
        or not argv
        or any(
            not isinstance(value, str) or not value or "\0" in value for value in argv
        )
        for argv in policy["commands"]
    ):
        raise ValueError("explicit controller argv lists required")
    if not isinstance(policy["acceptance_files"], dict):
        raise ValueError("acceptance hashes required")
    if not isinstance(policy["toolchain"], dict) or not policy["toolchain"]:
        raise ValueError("recorded execution toolchain required")
    if (
        type(policy["max_log_bytes"]) is not int
        or not 1024 <= policy["max_log_bytes"] <= 16 * 1024 * 1024
    ):
        raise ValueError("log byte budget must be 1024..16777216")
    for path, digest in policy["acceptance_files"].items():
        if not Path(path).is_absolute() or not re.fullmatch(r"[a-f0-9]{64}", digest):
            raise ValueError("absolute acceptance file and SHA256 required")
    ids = set()
    for proposal in proposals:
        if set(proposal) != {"id", "role", "base_commit", "patch", "allowed_paths"}:
            raise ValueError("typed agent proposal required")
        if (
            not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", proposal["id"])
            or proposal["id"] in ids
        ):
            raise ValueError("distinct safe proposal IDs required")
        ids.add(proposal["id"])
        if not proposal["role"] or not re.fullmatch(
            r"[a-f0-9]{40}", proposal["base_commit"]
        ):
            raise ValueError("named agent and exact Git revision required")
        if (
            not isinstance(proposal["patch"], str)
            or len(proposal["patch"].encode()) > 1_000_000
        ):
            raise ValueError("bounded textual patch required")
        if set(proposal["allowed_paths"]) - set(policy["allowed_paths"]):
            raise ValueError("proposal cannot widen controlled changes")


def _acceptance(policy):
    for name, digest in policy["acceptance_files"].items():
        p = Path(name)
        if p.is_symlink() or sha256(p.read_bytes()).hexdigest() != digest:
            raise ValueError("controller acceptance file changed")


def _snapshot(workspace):
    extra = _git(workspace, "ls-files", "--others", "-z").split("\0")
    return dict(
        diff=_git(workspace, "diff", "--binary", "HEAD"),
        extra={
            name: (
                "symlink:" + os.readlink(workspace / name)
                if (workspace / name).is_symlink()
                else sha256((workspace / name).read_bytes()).hexdigest()
            )
            for name in extra
            if name
        },
    )


def _command(argv, workspace, folder, index, timeout, max_log_bytes):
    argv = [part.replace("{workspace}", str(workspace)) for part in argv]
    log = folder / f"tool-{index:03d}.log"
    env = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONPATH=os.pathsep.join(
            [str(workspace), str(workspace / "design/component-catalogue/src")]
        ),
    )
    # The trusted policy is responsible for a tool's own CPU/memory settings.
    # A process group ensures a timed-out test cannot leave child solvers running.
    with log.open("xb") as stream:
        process = subprocess.Popen(
            argv,
            cwd=workspace,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        deadline, size, state = time.monotonic() + timeout, 0, None
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    state = "inconclusive-timeout"
                    break
                if not selector.select(min(remaining, 0.1)):
                    continue
                data = os.read(process.stdout.fileno(), 65536)
                if not data:
                    break
                stream.write(data[: max_log_bytes - size])
                size += len(data)
                if size > max_log_bytes:
                    state = "inconclusive-output-limit"
                    break
        if state:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.stdout.close()
        try:
            code = process.wait(timeout=max(0.01, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            code = process.wait()
            state = state or "inconclusive-timeout"
        state = state or ("passed" if code == 0 else "failed")
    return dict(
        argv=argv,
        state=state,
        returncode=code,
        log=log.name,
        log_sha256=sha256(log.read_bytes()).hexdigest(),
        timeout_seconds=timeout,
        max_log_bytes=max_log_bytes,
    )


def execute_proposals(root, output, proposals, policy, *, concurrency=2):
    """Record actual tools and isolated revisions; make no adoption decision."""
    _validate(proposals, policy, concurrency)
    _acceptance(policy)
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("fresh execution output required")
    output.mkdir(parents=True)
    store = Store(output / "jobs")
    policy_hash = fingerprint(policy)
    write_new(output / "policy.json", policy)

    def worker(proposal):
        request = dict(
            identity=dict(
                schema="osr-design-identity/1",
                city="baghdad",
                project="hierarchical-design-pilot",
                environment="simulation",
                configuration_revision=proposal["base_commit"],
                baseline_sha256=fingerprint(proposal["base_commit"]),
                run_id=None,
                asset_id=proposal["id"],
                part_id=None,
            ),
            proposal=proposal,
            policy_sha256=policy_hash,
            dependencies=dict(source_commit=proposal["base_commit"]),
            toolchain=policy["toolchain"],
        )
        job = store.create(request)
        folder = store.begin(job["id"], os.getpid())
        write_new(folder / "proposal.json", proposal)
        patch = folder / "candidate.patch"
        patch.write_text(proposal["patch"])
        workspace = folder / "workspace"
        tools, state, error = [], "failed", None
        created = False
        changed = []
        try:
            with _GIT_LOCK:
                _git(
                    root,
                    "worktree",
                    "add",
                    "--detach",
                    "--no-checkout",
                    str(workspace),
                    proposal["base_commit"],
                )
                created = True
                # Sparse checkout retains a correct full index, unlike checking
                # selected files into an otherwise empty index.
                _git(workspace, "sparse-checkout", "init", "--no-cone")
                patterns = [
                    "/"
                    + p
                    + (
                        "/"
                        if _git(
                            root, "ls-tree", proposal["base_commit"], "--", p
                        ).startswith("040000")
                        else ""
                    )
                    for p in policy["checkout_paths"]
                ]
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(workspace),
                        "sparse-checkout",
                        "set",
                        "--no-cone",
                        "--stdin",
                    ],
                    input=("\n".join(patterns) + "\n").encode(),
                    check=True,
                    capture_output=True,
                )
                _git(workspace, "reset", "--hard", proposal["base_commit"])
            if proposal["patch"]:
                _git(workspace, "apply", "--index", "--check", str(patch))
                _git(workspace, "apply", "--index", str(patch))
            changed = _git(workspace, "diff", "--name-only", "HEAD").splitlines()
            if set(changed) - set(proposal["allowed_paths"]):
                raise ValueError("candidate changed protected files")
            if any((workspace / name).is_symlink() for name in changed):
                raise ValueError("candidate source cannot be a symbolic link")
            before = _snapshot(workspace)
            store.event(
                job["id"],
                dict(
                    kind="agent-proposal-evaluation",
                    role=proposal["role"],
                    patch_sha256=sha256(patch.read_bytes()).hexdigest(),
                    changed_paths=changed,
                ),
            )
            for index, argv in enumerate(policy["commands"]):
                _acceptance(policy)
                tool = _command(
                    argv,
                    workspace,
                    folder,
                    index,
                    policy["timeout_seconds"],
                    policy["max_log_bytes"],
                )
                tools.append(tool)
                store.event(job["id"], dict(kind="tool-completed", **tool))
                _acceptance(policy)
                if before != _snapshot(workspace):
                    raise ValueError(
                        "evaluation mutated candidate or acceptance source"
                    )
                if tool["state"] != "passed":
                    break
            if before != _snapshot(workspace):
                raise ValueError("evaluation mutated candidate or acceptance source")
            state = (
                "timeout"
                if any(t["state"] == "inconclusive-timeout" for t in tools)
                else (
                    "budget-exceeded"
                    if any(t["state"] == "inconclusive-output-limit" for t in tools)
                    else (
                        "completed"
                        if tools and all(t["state"] == "passed" for t in tools)
                        else "failed"
                    )
                )
            )
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        finally:
            if created:
                with _GIT_LOCK:
                    _git(root, "worktree", "remove", "--force", str(workspace))
        result = dict(
            schema="osr-agent-tool-evaluation/1",
            proposal_id=proposal["id"],
            job_id=job["id"],
            role=proposal["role"],
            base_commit=proposal["base_commit"],
            policy_sha256=policy_hash,
            proposal_sha256=fingerprint(proposal),
            execution_workspace=str(workspace),
            changed_paths=changed,
            tools=tools,
            status=state,
            error=error,
            llm_service_invoked=False,
            experimental_adoption=False,
            engineering_design_complete=False,
            manufacturing_release=False,
            physical_release=False,
        )
        write_new(folder / "evaluation.json", result)
        manifest = dict(
            request_sha256=fingerprint(request),
            artifacts={
                p.name: sha256(p.read_bytes()).hexdigest()
                for p in sorted(folder.iterdir())
                if p.is_file()
            },
        )
        write_new(folder / "manifest.json", manifest)
        store.finish(job["id"], state, error=error, manifest=manifest)
        result["artifact_directory"] = str(folder.relative_to(output))
        return result

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        results = list(executor.map(worker, proposals))
    report = dict(
        schema="osr-bounded-agent-execution/1",
        policy_sha256=policy_hash,
        concurrency=concurrency,
        results=results,
        physical_release=False,
    )
    write_new(output / "execution.json", report)
    return report


def verify_execution(output):
    """Verify common-store seals, typed proposals and the actual recorded tools."""
    output = Path(output).resolve()
    report = json.loads((output / "execution.json").read_text())
    policy = json.loads((output / "policy.json").read_text())
    if (
        report["policy_sha256"] != fingerprint(policy)
        or report["physical_release"] is not False
    ):
        raise ValueError("changed execution policy or release claim")
    store = Store(output / "jobs")
    proposals = []
    for result in report["results"]:
        job = store.verify_request(result["job_id"])
        store.verify_attempt(result["job_id"], 1)
        folder = output / result["artifact_directory"]
        if (
            folder.resolve()
            != (store.root / "runs" / result["job_id"] / "attempt-0001").resolve()
        ):
            raise ValueError("changed artifact directory")
        sealed = json.loads((folder / "evaluation.json").read_text())
        if sealed != {k: v for k, v in result.items() if k != "artifact_directory"}:
            raise ValueError("changed evaluation summary")
        proposal = job["request"]["proposal"]
        proposals.append(proposal)
        if result["proposal_sha256"] != fingerprint(proposal) or result[
            "policy_sha256"
        ] != fingerprint(policy):
            raise ValueError("changed proposal context")
        if (
            result["status"] != job["status"]
            or result["experimental_adoption"] is not False
        ):
            raise ValueError("changed outcome or adoption claim")
        if result["status"] == "completed" and len(result["tools"]) != len(
            policy["commands"]
        ):
            raise ValueError("completed result omitted required commands")
        for flag in (
            "engineering_design_complete",
            "manufacturing_release",
            "physical_release",
            "llm_service_invoked",
        ):
            if result[flag] is not False:
                raise ValueError("invalid execution authority claim")
        states = [t["state"] for t in result["tools"]]
        derived = (
            "failed"
            if result["error"]
            else (
                "timeout"
                if "inconclusive-timeout" in states
                else (
                    "budget-exceeded"
                    if "inconclusive-output-limit" in states
                    else (
                        "completed"
                        if states and all(s == "passed" for s in states)
                        else "failed"
                    )
                )
            )
        )
        if derived != result["status"]:
            raise ValueError("tool outcomes differ from terminal status")
        for index, tool in enumerate(result["tools"]):
            expected = [
                part.replace("{workspace}", result["execution_workspace"])
                for part in policy["commands"][index]
            ]
            if (
                tool["argv"] != expected
                or tool["log_sha256"]
                != sha256((folder / tool["log"]).read_bytes()).hexdigest()
            ):
                raise ValueError("changed tool invocation or log")
            if (
                tool["timeout_seconds"] != policy["timeout_seconds"]
                or tool["max_log_bytes"] != policy["max_log_bytes"]
                or (folder / tool["log"]).stat().st_size > policy["max_log_bytes"]
                or tool["state"]
                not in {
                    "passed",
                    "failed",
                    "inconclusive-timeout",
                    "inconclusive-output-limit",
                }
                or (tool["state"] == "passed" and tool["returncode"] != 0)
                or (tool["state"] == "failed" and tool["returncode"] == 0)
            ):
                raise ValueError("tool outcome or resource policy differs")
    _validate(proposals, policy, report["concurrency"])
    return dict(verified=True, jobs=len(proposals), physical_release=False)

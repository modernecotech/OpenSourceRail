"""Source-bound bridge to the opt-in Rust proposal and Pareto kernel.

Python retains canonical physical identities and engineering materializers. Rust
receives bounded numeric/categorical search records, never qualification powers.
Build receipts check cooperative source/tool/binary consistency; they are not a
signature, an OS sandbox, or physical evidence.
"""
from __future__ import annotations

import argparse
import fcntl
from hashlib import sha256
import json
from math import isfinite
import os
from pathlib import Path
import selectors
import stat
import subprocess
import tempfile
import time

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity

PRODUCER = "engineering/design_search/native_search.py"
CRATE = "crates/osr-design-search"
TARGET = "build/rust-search-target"
REQUEST_SCHEMA = "osr-search-kernel-request/1"
RESULT_SCHEMA = "osr-search-kernel-result/1"
RECEIPT_SCHEMA = "osr-rust-search-build/1"
MAX_BYTES = 64 * 1024**2
MAX_STDERR_BYTES = 1024**2
BUILD_COMMAND = ["cargo", "build", "--locked", "--release", "-p", "osr-design-search"]
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, manufacturing_release=False,
             operating_release=False, selected_reference_changed=False,
             native_engineering_solver_dispatched=False, integrated_selection=None)


def _regular(path):
    path = Path(path)
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("Regular non-symlink Rust source, receipt or binary required: " + str(path))
    return path


def _read(path, limit=MAX_BYTES):
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError as exc:
        raise ValueError("Regular non-symlink Rust source, receipt or binary required") from exc
    with os.fdopen(descriptor, "rb") as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise ValueError("Regular Rust record within reader size budget required")
        raw = handle.read(limit + 1)
        if len(raw) > limit:
            raise ValueError("Rust record exceeds reader size budget")
        return raw


def _pairs(items):
    value = {}
    for key, item in items:
        if key in value:
            raise ValueError("Duplicate JSON field in Rust search record")
        value[key] = item
    return value


def _parse(raw):
    def invalid(_):
        raise ValueError("Non-finite JSON value in Rust search record")
    return json.loads(raw, object_pairs_hook=_pairs, parse_constant=invalid)


def _sources(root):
    root = Path(root)
    names = ["Cargo.toml", "Cargo.lock"]
    names.extend(name for name in ("rust-toolchain", "rust-toolchain.toml") if (root / name).exists())
    names.extend(name for name in (".cargo/config", ".cargo/config.toml") if (root / name).exists())
    crate = root / CRATE
    if crate.is_symlink() or not crate.is_dir():
        raise ValueError("Rust search crate is unavailable")
    for directory, directories, files in os.walk(crate, followlinks=False):
        for name in directories:
            if (Path(directory) / name).is_symlink():
                raise ValueError("Symlinked Rust source directory is not permitted")
        for name in files:
            path = Path(directory) / name
            if path.suffix in (".rs", ".toml"):
                _regular(path)
                names.append(path.relative_to(root).as_posix())
    if not any(name.endswith("/src/main.rs") for name in names):
        raise ValueError("Rust search executable source is unavailable")
    return {name: sha256(_read(root / name)).hexdigest() for name in sorted(names)}


def _run(command, raw=b"", *, timeout=60, maximum_output=MAX_BYTES, cwd=None, env=None):
    """Bound both protocol pipes while writing input; no shell or solver dispatch."""
    if not isfinite(timeout) or timeout <= 0:
        raise ValueError("Positive finite subprocess timeout required")
    process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = bytearray(), bytearray()
    offset = 0
    deadline = time.monotonic() + timeout
    try:
        with selectors.DefaultSelector() as selector:
            for handle, label in ((process.stdout, "stdout"), (process.stderr, "stderr")):
                os.set_blocking(handle.fileno(), False)
                selector.register(handle, selectors.EVENT_READ, label)
            if raw:
                os.set_blocking(process.stdin.fileno(), False)
                selector.register(process.stdin, selectors.EVENT_WRITE, "stdin")
            else:
                process.stdin.close()
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Rust search subprocess exceeded its runtime budget")
                for key, _ in selector.select(min(remaining, 0.2)):
                    handle, label = key.fileobj, key.data
                    if label == "stdin":
                        try:
                            offset += os.write(handle.fileno(), raw[offset:offset + 65536])
                        except BrokenPipeError:
                            offset = len(raw)
                        if offset == len(raw):
                            selector.unregister(handle)
                            handle.close()
                        continue
                    chunk = os.read(handle.fileno(), 65536)
                    if not chunk:
                        selector.unregister(handle)
                        handle.close()
                        continue
                    buffer = output if label == "stdout" else error
                    buffer.extend(chunk)
                    limit = maximum_output if label == "stdout" else MAX_STDERR_BYTES
                    if len(buffer) > limit:
                        raise ValueError("Rust search subprocess exceeded its output size budget")
            returncode = process.wait(timeout=max(0.001, deadline - time.monotonic()))
        if returncode:
            message = (bytes(error) or bytes(output))[-4096:].decode("utf-8", "replace")
            raise RuntimeError("Rust search subprocess failed: " + message)
        return bytes(output)
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()
        for handle in (process.stdin, process.stdout, process.stderr):
            if not handle.closed:
                handle.close()


def _tools():
    return {name: _run([name, "--version"], timeout=15, maximum_output=65536).decode().strip()
            for name in ("cargo", "rustc")}


def _receipt_path(binary):
    return Path(binary).with_name(Path(binary).name + ".receipt.json")


def build_kernel(root=ROOT, target_dir=None):
    """Explicit release build; refuse stale sources and write a binary receipt."""
    root = Path(root).resolve()
    target = root / TARGET if target_dir is None else Path(target_dir).absolute()
    if target.is_symlink():
        raise ValueError("Regular Rust build target directory required")
    target.mkdir(parents=True, exist_ok=True)
    lock_path = target / "osr-design-search.build.lock"
    # Cooperative build coordination only; this is not source or OS isolation.
    if lock_path.exists():
        _regular(lock_path)
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        before = _sources(root)
        tools = _tools()
        environment = dict(os.environ, CARGO_TARGET_DIR=str(target), CARGO_BUILD_JOBS="2")
        _run(BUILD_COMMAND, timeout=180, cwd=root, env=environment)
        if _sources(root) != before or _tools() != tools:
            raise ValueError("Rust search sources or toolchain changed during build")
        binary = _regular(target / "release/osr-design-search")
        receipt = dict(schema=RECEIPT_SCHEMA, source_sha256=before, tool_versions=tools,
                       build_command=BUILD_COMMAND, binary_sha256=sha256(_read(binary)).hexdigest())
        receipt["receipt_id"] = identity(receipt)
        path = _receipt_path(binary)
        with tempfile.NamedTemporaryFile(prefix=".search-receipt-", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(encoded(receipt))
        try:
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
        return dict(binary=str(binary), **receipt)


def _hex(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


class NativeSearch:
    """Reuse one verified native engine; never build implicitly or change a candidate."""

    def __init__(self, root=ROOT, binary=None):
        self.root = Path(root).resolve()
        self.binary = self.root / TARGET / "release/osr-design-search" if binary is None else Path(binary).absolute()
        self.tools = _tools()
        self.receipt = _parse(_read(_receipt_path(self.binary)))
        if not isinstance(self.receipt, dict):
            raise ValueError("Explicit Rust search build receipt required")
        value = {key: item for key, item in self.receipt.items() if key != "receipt_id"}
        if (self.receipt.get("schema") != RECEIPT_SCHEMA
                or self.receipt.get("receipt_id") != identity(value)
                or self.receipt.get("build_command") != BUILD_COMMAND
                or self.receipt.get("tool_versions") != self.tools):
            raise ValueError("Rust search build receipt or toolchain differs; explicitly rebuild the kernel")
        self._current()

    def _current(self):
        _regular(self.binary)
        if (self.receipt["source_sha256"] != _sources(self.root)
                or self.receipt["binary_sha256"] != sha256(_read(self.binary)).hexdigest()
                or _parse(_read(_receipt_path(self.binary))) != self.receipt):
            raise ValueError("Rust search source, binary or receipt changed; explicitly rebuild the kernel")

    def request(self, request, *, timeout=60):
        if (not isinstance(request, dict) or request.get("schema") != REQUEST_SCHEMA
                or request.get("operation") not in ("pareto", "propose")):
            raise ValueError("Explicit versioned Rust search request required")
        raw = encoded(request)
        if len(raw) > MAX_BYTES:
            raise ValueError("Rust search request exceeds size budget")
        self._current()
        result_raw = _run([str(self.binary)], raw, timeout=timeout)
        self._current()
        result = _parse(result_raw)
        if (not isinstance(result, dict) or result.get("schema") != RESULT_SCHEMA
                or result.get("operation") != request["operation"] or "provenance" in result
                or any(key in result for key in FLAGS)):
            raise ValueError("Unexpected Rust search result schema or authority fields")
        provenance = dict(binary_sha256=self.receipt["binary_sha256"],
            build_receipt_id=self.receipt["receipt_id"], source_epoch_id=identity(self.receipt["source_sha256"]),
            bridge_source_sha256=digest(__file__), request_sha256=sha256(raw).hexdigest(),
            output_sha256=sha256(result_raw).hexdigest())
        provenance["request_id"] = identity(provenance)
        return dict(result, provenance=provenance, **FLAGS)

    def propose(self, **fields):
        return self.request(dict(schema=REQUEST_SCHEMA, operation="propose", **fields))

    def archive(self, rows, objectives, descriptor_keys, *, max_work=100_000_000):
        objectives, descriptor_keys = tuple(objectives), tuple(descriptor_keys)
        for values in (objectives, descriptor_keys):
            if not values or any(not isinstance(k, str) or not k for k in values) or len(set(values)) != len(values):
                raise ValueError("Unique explicit objective and descriptor names required")
        points, descriptors, seen = [], {}, set()
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("Explicit Rust archive candidate records required")
            cid = row.get("candidate_id")
            if not _hex(cid) or cid in seen:
                raise ValueError("Unique SHA-256 physical candidate identities required")
            seen.add(cid)
            descriptor = row.get("descriptor")
            if not isinstance(descriptor, dict) or set(descriptor_keys) - set(descriptor):
                raise ValueError("Complete explicit descriptor required")
            selected = {key: descriptor[key] for key in descriptor_keys}
            cell = identity(selected)
            descriptors[cell] = selected
            metrics = row.get("metrics", {})
            if not isinstance(metrics, dict):
                raise ValueError("Explicit objective metrics required")
            values = []
            for name in objectives:
                number = metrics.get(name)
                try:
                    valid = (type(number) in (int, float) and isfinite(number) and number >= 0
                             and (type(number) is not int or int(float(number)) == number))
                except (OverflowError, ValueError):
                    valid = False
                if not valid:
                    raise ValueError("Unknown, negative or inexact objective cannot enter search: " + name)
                values.append(float(number))
            points.append(dict(candidate_id=cid, cell_id=cell, values=values))
        result = self.request(dict(schema=REQUEST_SCHEMA, operation="pareto",
                                   points=sorted(points, key=lambda p: p["candidate_id"]), max_work=max_work))
        cells = result.get("cells")
        if not isinstance(cells, list) or {c["cell_id"] for c in cells} != set(descriptors):
            raise ValueError("Rust archive descriptor coverage differs")
        by_id = {p["candidate_id"]: p for p in points}
        retained = []
        for cell in cells:
            ids = cell.get("retained_candidate_ids")
            if (not isinstance(ids, list) or ids != sorted(set(ids)) or not ids
                    or any(cid not in by_id or by_id[cid]["cell_id"] != cell["cell_id"] for cid in ids)):
                raise ValueError("Rust archive candidate/cell identity differs")
            cell["descriptor"] = descriptors[cell["cell_id"]]
            retained.extend(ids)
        if result.get("retained_candidate_ids") != sorted(retained):
            raise ValueError("Rust archive retained union differs")
        front = result.get("global_front")
        if not isinstance(front, list) or front != sorted(set(front)) or set(front) - seen:
            raise ValueError("Rust global front identities differ")
        excluded = result.get("dominated")
        if (not isinstance(excluded, list) or len(excluded) != len(seen - set(retained))
                or {r["candidate_id"] for r in excluded} != seen - set(retained)):
            raise ValueError("Rust archive exclusion coverage differs")
        for row in excluded:
            left, right = by_id.get(row.get("dominated_by")), by_id.get(row.get("candidate_id"))
            if (left is None or right is None or row.get("cell_id") != right["cell_id"]
                    or left["cell_id"] != right["cell_id"]
                    or not all(a <= b for a, b in zip(left["values"], right["values"]))
                    or not (left["values"] != right["values"] or left["candidate_id"] < right["candidate_id"])):
                raise ValueError("Rust exclusion witness does not dominate its same-cell candidate")
        result.update(objectives=list(objectives), descriptor_keys=list(descriptor_keys),
            cross_cell_partial_quantity_pareto_candidate_ids=front,
            scope="Compact known-objective research archive; no installed-system selection or physical qualification")
        result["archive_id"] = identity(result)
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build",))
    parser.add_argument("--target-dir", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(build_kernel(target_dir=args.target_dir), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

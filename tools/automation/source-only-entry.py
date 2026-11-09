#!/usr/bin/env python3
"""Pinned, source-only Python bootstrap prototype; no GIS/server integration.

Run with ``python -I -B`` and externally pin this entrypoint and its command.
Required arguments: --loader, --loader-sha256, --manifest, --manifest-sha256,
--module, --function, --argv-json, --result (ordinary absolute paths for files).

The external SHA256-bound manifest has schema osr-source-only-entry-manifest/1
and exactly these fields: repo_root, namespaces, source_sha256, entrypoints
([{module, function}]), loader ({path, sha256}), and max_source_bytes.
The named function receives one list of strings and returns a bounded JSON value.
The exclusive result file is the authoritative record; stdout also receives it.
Hash pins require a separately trusted caller. This is not an OS sandbox and
cannot preserve a final report after SIGKILL, interpreter crash or storage loss.
"""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import types


MAX_LOADER_BYTES = 1024 * 1024
MAX_MANIFEST_BYTES = 4 * 1024 * 1024
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_ARGV_BYTES = MAX_RETURN_BYTES = 64 * 1024
BOOTSTRAP_NAME = "_osr_source_only_entry_loader"


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def hexsha(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def absolute(value):
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("Ordinary absolute file paths required")
    return path


def open_file(path, *, create=False):
    """No-follow descriptor walk; never resolve away symlinks or overwrite output."""
    path = absolute(path)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    parent = os.open(path.anchor, flags)
    try:
        for part in path.parts[1:-1]:
            nxt = os.open(part, flags, dir_fd=parent)
            os.close(parent)
            parent = nxt
        mode = os.O_WRONLY | os.O_CREAT | os.O_EXCL if create else os.O_RDONLY | os.O_NONBLOCK
        return os.open(path.name, mode | os.O_NOFOLLOW | os.O_CLOEXEC,
                       0o600, dir_fd=parent)
    finally:
        os.close(parent)


def read_pinned(path, expected, maximum, label, bindings):
    if not hexsha(expected):
        raise ValueError("Exact lowercase SHA256 required: " + label)
    fd = open_file(path)
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise ValueError("Ordinary bounded file required: " + label)
        raw = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
    bindings[label] = dict(path=str(absolute(path)), expected_sha256=expected,
                           sha256=sha(raw), bytes=len(raw))
    if len(raw) > maximum or (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_size, after.st_mtime_ns, after.st_ctime_ns):
        raise ValueError("Bounded stable file required: " + label)
    if sha(raw) != expected:
        raise ValueError("SHA256 differs: " + label)
    return raw


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(raw):
    def refuse(value):
        raise ValueError("Nonfinite JSON value refused: " + value)
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=refuse)


def manifest_contract(value, args):
    required = {"schema", "repo_root", "namespaces", "source_sha256", "entrypoints",
                "loader", "max_source_bytes"}
    if not isinstance(value, dict) or set(value) != required or value["schema"] != "osr-source-only-entry-manifest/1":
        raise ValueError("Closed source-only entry manifest schema required")
    root = absolute(value["repo_root"])
    ns = value["namespaces"]
    if (not isinstance(ns, list) or not 1 <= len(ns) <= 16 or len(set(ns)) != len(ns) or
            any(not isinstance(n, str) or not n.isidentifier() for n in ns)):
        raise ValueError("Distinct declared namespace identifiers required")
    sources = value["source_sha256"]
    if (not isinstance(sources, dict) or not 1 <= len(sources) <= 4096 or
            any(not isinstance(p, str) or len(p) > 1024 or not hexsha(h) for p, h in sources.items())):
        raise ValueError("Bounded explicit source SHA256 allowlist required")
    limit = value["max_source_bytes"]
    if type(limit) is not int or not 0 < limit <= MAX_SOURCE_BYTES:
        raise ValueError("Bounded source-file byte limit required")
    if value["loader"] != dict(path=str(absolute(args.loader)), sha256=args.loader_sha256):
        raise ValueError("Manifest loader binding differs from the pinned command")
    targets = value["entrypoints"]
    if not isinstance(targets, list) or not 1 <= len(targets) <= 16:
        raise ValueError("Bounded entrypoint allowlist required")
    pairs = []
    for item in targets:
        if (not isinstance(item, dict) or set(item) != {"module", "function"} or
                not isinstance(item["module"], str) or len(item["module"]) > 1024 or
                any(not part.isidentifier() for part in item["module"].split(".")) or
                not isinstance(item["function"], str) or not item["function"].isidentifier()):
            raise ValueError("Explicit module/function entrypoints required")
        module = item["module"]
        if module.split(".")[0] not in ns:
            raise ValueError("Entrypoint lies outside declared namespaces")
        path = module.replace(".", "/")
        if path + ".py" not in sources and path + "/__init__.py" not in sources:
            raise ValueError("Entrypoint module is absent from the source allowlist")
        pairs.append((module, item["function"]))
    if len(pairs) != len(set(pairs)) or (args.module, args.function) not in pairs:
        raise ValueError("Requested module/function is not allowlisted")
    return root


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("loader", "loader-sha256", "manifest", "manifest-sha256", "module",
                 "function", "argv-json", "result"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args(argv)
    finder, result_fd = None, None
    result_attempted, result_allowed = False, True
    report = dict(schema="osr-source-only-entry-result/1", execution="failed", phase="preflight",
        entrypoint=dict(module=args.module, function=args.function), bindings={}, imports=[],
        interpreter=dict(executable=sys.executable, isolated=sys.flags.isolated,
                         dont_write_bytecode=sys.dont_write_bytecode,
                         dont_write_bytecode_flag=sys.flags.dont_write_bytecode),
        return_value=None, error=None)
    try:
        if sys.flags.isolated != 1 or sys.flags.dont_write_bytecode != 1 or sys.dont_write_bytecode is not True:
            raise RuntimeError("Invoke the pinned entrypoint with python -I -B")
        if len(args.argv_json.encode()) > MAX_ARGV_BYTES:
            raise ValueError("Bounded JSON argv required")
        call_argv = read_json(args.argv_json)
        if (not isinstance(call_argv, list) or len(call_argv) > 256 or
                any(not isinstance(v, str) or len(v) > 4096 for v in call_argv)):
            raise ValueError("JSON argv must be a bounded list of strings")
        report["argv_sha256"] = sha(encoded(call_argv))
        report["phase"] = "authenticate-inputs"
        loader_raw = read_pinned(args.loader, args.loader_sha256, MAX_LOADER_BYTES,
                                 "loader", report["bindings"])
        manifest_raw = read_pinned(args.manifest, args.manifest_sha256, MAX_MANIFEST_BYTES,
                                   "source_manifest", report["bindings"])
        manifest = read_json(manifest_raw)
        root = manifest_contract(manifest, args)
        report["repo_root"] = str(root)
        if absolute(args.result).is_relative_to(root):
            result_allowed = False
            raise ValueError("Result must be outside the controlled source root")
        result_attempted = True
        result_fd = open_file(args.result, create=True)
        report["phase"] = "install-source-policy"
        if BOOTSTRAP_NAME in sys.modules:
            raise RuntimeError("Bootstrap loader module was already imported")
        loader = types.ModuleType(BOOTSTRAP_NAME)
        loader.__file__, loader.__package__ = str(absolute(args.loader)), ""
        sys.modules[BOOTSTRAP_NAME] = loader
        exec(compile(loader_raw, loader.__file__, "exec", dont_inherit=True, optimize=0), loader.__dict__)
        finder = loader.install(repo_root=root, source_sha256=manifest["source_sha256"],
                                namespaces=manifest["namespaces"],
                                max_source_bytes=manifest["max_source_bytes"])
        report["phase"] = "invoke-entrypoint"
        module = importlib.import_module(args.module)
        function = getattr(module, args.function)
        if not isinstance(function, types.FunctionType) or function.__globals__ is not module.__dict__:
            raise TypeError("Entrypoint must be a function defined in its authenticated module")
        returned = function(call_argv)
        if len(encoded(returned)) > MAX_RETURN_BYTES:
            raise ValueError("Entrypoint return value exceeds the JSON byte limit")
        report.update(return_value=returned, execution="completed", phase="completed")
    except BaseException as exc:
        report["error"] = dict(type=type(exc).__name__, message=str(exc)[:4096])
    finally:
        # Do not remove the finder or purge modules: it stays active until exit.
        if finder is not None:
            report["imports"] = list(finder.records)
        if not result_attempted and result_allowed:
            try:
                result_fd = open_file(args.result, create=True)
            except OSError as exc:
                report["result_write_error"] = dict(type=type(exc).__name__, message=str(exc)[:4096])
        report["evaluation_id"] = sha(encoded(report))
        raw = encoded(report)
        if result_fd is not None:
            try:
                with os.fdopen(result_fd, "wb") as stream:
                    stream.write(raw)
                    stream.flush()
                    os.fsync(stream.fileno())
            except OSError as exc:
                print("Source-only result write failed: " + str(exc), file=sys.stderr)
                return 2
        sys.stdout.write(raw.decode())
    return 0 if report["execution"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

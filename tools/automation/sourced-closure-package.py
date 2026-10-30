#!/usr/bin/env python3
"""Rebuild and replay the display package for a sourced engineering closure.

The closure report is computed from the exact saved run and retained native
packages. This tool only writes a report and a labelled display projection; it
cannot grant physical, engineering, manufacturing, or operating acceptance.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False)
MAX_ARCHIVE = 128 * 1024**2
MAX_MEMBER = 128 * 1024**2
MAX_TOTAL = 512 * 1024**2


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                        allow_nan=False) + "\n").encode()


def identity(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while block := stream.read(1024**2):
            h.update(block)
    return h.hexdigest()


def read_json(path, maximum=4 * 1024**2):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > maximum:
        raise ValueError("Bounded ordinary JSON file required: " + str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def archive_packages(folder, destination):
    """Extract and hash-check a retained methods package into a fresh directory."""
    folder = Path(folder)
    archive_path = folder / "structural-methods.tar.gz"
    if archive_path.is_symlink() or not archive_path.is_file() or archive_path.stat().st_size > MAX_ARCHIVE:
        raise ValueError("Bounded ordinary structural archive required")
    manifest = read_json(folder / "structural-methods.json")
    if (manifest.get("schema") != "osr-sourced-structural-methods/1" or
            manifest.get("publication_id") != identity({k: v for k, v in manifest.items()
                                                          if k != "publication_id"}) or
            any(manifest.get(key) is not False for key in FLAGS)):
        raise ValueError("Sealed unreleased structural methods manifest required")
    if manifest.get("files_sha256") != {"structural-methods.tar.gz": digest(archive_path)}:
        raise ValueError("Structural package archive digest differs")
    rows = manifest.get("packages")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 8 or len({r.get("name") for r in rows}) != len(rows):
        raise ValueError("Bounded structural package inventory required")
    expected = {}
    descriptors = []
    for row in rows:
        name = row.get("name")
        kind = row.get("kind")
        if not isinstance(name, str) or not name or "/" in name or name in (".", ".."):
            raise ValueError("Canonical structural package name required")
        if kind not in ("rejected-whole", "corrected-whole", "distributed-contact-whole"):
            raise ValueError("Unknown retained structural method kind")
        for relative, metadata in row.get("files_sha256", {}).items():
            path = PurePosixPath(relative)
            if (not path.parts or path.is_absolute() or ".." in path.parts or
                    path.as_posix() != relative or not isinstance(metadata, str) or len(metadata) != 64):
                raise ValueError("Canonical bounded structural member required")
            expected[name + "/" + relative] = (metadata, destination / name / relative)
        descriptor_kind = "distributed-contact-whole" if kind == "distributed-contact-whole" else "whole-body"
        descriptors.append(dict(kind=descriptor_kind, path=str(destination / name)))
    destination.mkdir(parents=True, exist_ok=True)
    seen = set()
    total = 0
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        if len(members) > 100:
            raise ValueError("Structural archive member budget exceeded")
        for member in members:
            name = member.name
            path = PurePosixPath(name)
            total += member.size
            if (name not in expected or name in seen or not member.isfile() or
                    path.is_absolute() or ".." in path.parts or path.as_posix() != name or
                    member.size < 0 or member.size > MAX_MEMBER or total > MAX_TOTAL):
                raise ValueError("Unexpected, linked, duplicate, or oversized structural member")
            seen.add(name)
            source = archive.extractfile(member)
            target = expected[name][1]
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = source.read(MAX_MEMBER + 1)
            if len(raw) != member.size or hashlib.sha256(raw).hexdigest() != expected[name][0]:
                raise ValueError("Structural member bytes differ: " + name)
            target.write_bytes(raw)
    if seen != set(expected):
        raise ValueError("Structural archive inventory is incomplete")
    return descriptors


def descriptors(root, scratch):
    result = []
    for index, relative in enumerate((
            "docs/design-engine/sourced-case",
            "docs/design-engine/sourced-bolster")):
        folder = Path(root) / relative
        result.extend(archive_packages(folder, Path(scratch) / ("native-" + str(index))))
    return result


def projection(report, report_sha256):
    value = dict(schema="osr-sourced-closure-display/1",
                 source_report_file="closure.json.gz", source_report_sha256=report_sha256,
                 source_report_evaluation_id=report["evaluation_id"], run_id=report["run_id"],
                 display_projection=True, counts=report["counts"], vehicles=report["vehicles"],
                 phases=report["phases"], work_packages=report["work_packages"],
                 required_test_inputs=report["required_test_inputs"], **FLAGS)
    value["summary_id"] = identity(value)
    return value


def report_bytes(report):
    raw = encoded(report)
    import io
    stream = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as compressed:
        compressed.write(raw)
    return stream.getvalue()


def rebuild(state, *, root=ROOT, native_folders=None):
    from engineering.sourced_case import closure
    native_folders = native_folders or []
    return closure.build(state, native=native_folders, root=root)


def publish(state, output, *, root=ROOT, methods_folders=None):
    output = Path(output)
    if output.is_symlink() or output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("Fresh or empty closure output directory required")
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="osr-sourced-closure-") as scratch:
        native = descriptors(root, Path(scratch)) if methods_folders is None else methods_folders
        report = rebuild(state, root=root, native_folders=native)
        if report.get("source_epoch_current") is not True or report.get("current_plan_coverage_verified") is not True:
            raise ValueError("Current complete source-bound closure required")
        if any(report.get(key) is not False for key in FLAGS):
            raise ValueError("Closure report cannot issue release or acceptance")
        raw = report_bytes(report)
        (output / "closure.json.gz").write_bytes(raw)
        summary = projection(report, hashlib.sha256(raw).hexdigest())
        (output / "closure-summary.json").write_bytes(json.dumps(
            summary, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False).encode() + b"\n")
    return summary


def verify(state, output, *, root=ROOT, methods_folders=None):
    output = Path(output)
    if output.is_symlink() or not output.is_dir():
        raise ValueError("Ordinary closure output directory required")
    raw_path = output / "closure.json.gz"
    if raw_path.is_symlink() or not raw_path.is_file() or raw_path.stat().st_size > MAX_ARCHIVE:
        raise ValueError("Bounded ordinary closure report required")
    with gzip.open(raw_path, "rb") as stream:
        raw = stream.read(MAX_TOTAL + 1)
    if len(raw) > MAX_TOTAL:
        raise ValueError("Closure report expansion budget exceeded")
    report = json.loads(raw)
    if report.get("evaluation_id") != identity({k: v for k, v in report.items() if k != "evaluation_id"}):
        raise ValueError("Closure report seal differs")
    summary = read_json(output / "closure-summary.json")
    if summary != projection(report, digest(raw_path)):
        raise ValueError("Closure display projection differs from source report")
    with tempfile.TemporaryDirectory(prefix="osr-sourced-closure-verify-") as scratch:
        native = descriptors(root, Path(scratch)) if methods_folders is None else methods_folders
        actual = rebuild(state, root=root, native_folders=native)
    if encoded(actual) != encoded(report):
        raise ValueError("Current closure reconstruction differs from published report")
    return dict(verified=True, run_id=report["run_id"], evaluation_id=report["evaluation_id"],
                current_plan_coverage_verified=True, physical_accepted=False,
                engineering_accepted=False, manufacturing_release=False,
                operating_release=False, selected_reference_changed=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("publish", "verify"):
        command = sub.add_parser(action)
        command.add_argument("state", type=Path)
        command.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = (publish(args.state, args.output) if args.action == "publish"
                  else verify(args.state, args.output))
    except (ValueError, OSError, EOFError, tarfile.TarError) as error:
        parser.exit(2, str(error) + "\n")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

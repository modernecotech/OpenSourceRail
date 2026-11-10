#!/usr/bin/env python3
"""Validate and deterministically archive one Baghdad route-study attempt."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import tarfile
from pathlib import Path


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def identity(record: dict, field: str) -> str:
    unsigned = {key: value for key, value in record.items() if key != field}
    raw = (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    return sha(raw)


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def validate(root: Path) -> tuple[dict, list[Path]]:
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("attempt root manifest is missing")
    root_manifest = load(manifest_path)
    if root_manifest.get("manifest_id") != identity(root_manifest, "manifest_id"):
        raise ValueError("attempt root manifest identity mismatch")
    payloads = sorted(path for path in root.rglob("*") if path.is_file() and path.name != "manifest.json")
    payload_hashes = {path.relative_to(root).as_posix(): sha(path.read_bytes()) for path in payloads}
    if payload_hashes != root_manifest.get("files_sha256"):
        raise ValueError("attempt payloads do not match root manifest")
    if root_manifest.get("file_count") != len(payloads):
        raise ValueError("attempt root payload count differs from manifest")

    nested = sorted(path for path in root.rglob("manifest.json") if path != manifest_path)
    if len(nested) != 4:
        raise ValueError(f"expected four nested study/business manifests, found {len(nested)}")
    nested_records = {path.relative_to(root).as_posix(): load(path) for path in nested}
    for relative, record in nested_records.items():
        if record.get("manifest_id") != identity(record, "manifest_id"):
            raise ValueError(f"nested manifest identity mismatch: {relative}")
        if "/business/" in relative:
            study_prefix = relative.split("/business/", 1)[0]
            parent = nested_records.get(study_prefix + "/manifest.json")
            if parent is None or parent.get("files_sha256", {}).get("business/manifest.json") != sha((root / relative).read_bytes()):
                raise ValueError(f"study manifest does not bind business manifest: {relative}")
            business_root = root / study_prefix / "business"
            actual = {path.relative_to(business_root).as_posix(): sha(path.read_bytes())
                      for path in business_root.rglob("*") if path.is_file() and path.name != "manifest.json"}
            if actual != record.get("files_sha256"):
                raise ValueError(f"business payload mismatch: {relative}")
        elif not relative.startswith("studies/"):
            raise ValueError(f"unexpected nested manifest path: {relative}")
        else:
            study_prefix = relative.removesuffix("/manifest.json")
            for child, expected_hash in record.get("files_sha256", {}).items():
                archive_relative = study_prefix + "/" + child
                actual_hash = payload_hashes.get(archive_relative)
                if child.endswith("manifest.json") and archive_relative in nested_records:
                    actual_hash = sha((root / archive_relative).read_bytes())
                if actual_hash != expected_hash:
                    raise ValueError(f"study manifest payload mismatch: {archive_relative}")

    return root_manifest, sorted(path for path in root.rglob("*") if path.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-dir", type=Path, required=True)
    parser.add_argument("--attempt-name", required=True, help="Archive prefix, for example attempt-05")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.attempt_name.startswith("attempt-") or "/" in args.attempt_name:
        raise SystemExit("attempt name must be a simple attempt-NN path component")
    root = args.attempt_dir.resolve()
    manifest, files = validate(root)
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite an existing archive: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    try:
        with temporary.open("wb") as raw:
            with gzip.GzipFile(fileobj=raw, mode="wb", filename=output.name, mtime=0, compresslevel=6) as gz:
                with tarfile.open(fileobj=gz, mode="w") as archive:
                    for path in files:
                        relative = path.relative_to(root).as_posix()
                        info = tarfile.TarInfo(f"{args.attempt_name}/{relative}")
                        info.size = path.stat().st_size
                        info.mode = 0o644
                        info.mtime = 0
                        info.uid = 0
                        info.gid = 0
                        info.uname = ""
                        info.gname = ""
                        with path.open("rb") as stream:
                            archive.addfile(info, stream)
        temporary.replace(output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    data = output.read_bytes()
    print(json.dumps({
        "attempt_manifest_id": manifest["manifest_id"],
        "archive": output.as_posix(),
        "archive_sha256": sha(data),
        "size_bytes": len(data),
        "member_count": len(files),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

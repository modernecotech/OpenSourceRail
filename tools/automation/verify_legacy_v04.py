#!/usr/bin/env python3
"""Verify the source-pinned v0.4 application workspace inventory."""
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "legacy/v0.4"
EXPECTED_COMMIT = "205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e"


def main():
    manifest = json.loads((WORKSPACE / "source-manifest.json").read_text(encoding="utf-8"))
    supplied_id = manifest.pop("manifest_id", None)
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    if (manifest.get("schema") != "osr-historical-workspace-source-manifest/1"
            or manifest.get("source_commit") != EXPECTED_COMMIT
            or manifest.get("workspace") != "legacy/v0.4"
            or not isinstance(supplied_id, str)
            or hashlib.sha256(canonical).hexdigest() != supplied_id):
        raise SystemExit("v0.4 source manifest identity or release pin differs")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != manifest.get("file_count"):
        raise SystemExit("v0.4 source manifest file list differs")
    expected = set()
    for row in files:
        rel = PurePosixPath(row.get("path", ""))
        if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.as_posix() in expected:
            raise SystemExit("unsafe or duplicate path in v0.4 source manifest")
        expected.add(rel.as_posix())
        path = WORKSPACE.joinpath(*rel.parts)
        if path.is_symlink() or not path.is_file():
            raise SystemExit("missing or non-regular v0.4 source file: " + rel.as_posix())
        raw = path.read_bytes()
        if len(raw) != row.get("bytes") or hashlib.sha256(raw).hexdigest() != row.get("sha256"):
            raise SystemExit("v0.4 source file hash differs: " + rel.as_posix())
    actual = {p.relative_to(WORKSPACE).as_posix() for p in WORKSPACE.rglob("*")
              if p.is_file() and p.relative_to(WORKSPACE).as_posix() not in {"README.md", "source-manifest.json"}}
    if actual != expected:
        raise SystemExit("v0.4 workspace file inventory differs")
    print(f"verified {len(expected)} files pinned to v0.4.0 {EXPECTED_COMMIT}")


if __name__ == "__main__":
    main()

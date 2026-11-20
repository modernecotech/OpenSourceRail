#!/usr/bin/env python3
"""Check local links in maintained Markdown; retained snapshots stay immutable."""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[2]
RETAINED_SNAPSHOT_PREFIXES = ("docs/archives/",)
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_TARGET = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)")
TITLE_SUFFIX = re.compile(r"^(.*?)\s+[\"'].*[\"']$")
EXTERNAL_PREFIXES = (
    "#",
    "data:",
    "http://",
    "https://",
    "javascript:",
    "mailto:",
)


@dataclass(frozen=True)
class BrokenLink:
    source: Path
    line: int
    target: str


def markdown_files() -> list[Path]:
    tracked = subprocess.check_output(
        ["git", "ls-files", "*.md"], cwd=REPO_ROOT, text=True
    ).splitlines()
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "*.md"],
        cwd=REPO_ROOT,
        text=True,
    ).splitlines()
    return sorted(
        Path(path)
        for path in set(tracked + untracked)
        if path == "docs/archives/README.md" or not Path(path).as_posix().startswith(RETAINED_SNAPSHOT_PREFIXES)
    )


def normalized_candidates(raw: str) -> list[str]:
    target = raw.strip().strip("<>")
    if not target or target.lower().startswith(EXTERNAL_PREFIXES):
        return []
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not target:
        return []
    candidates = [target]
    if match := TITLE_SUFFIX.match(target):
        candidates.append(match.group(1))
    return candidates


AUDIT = Path("docs/design-engine/v06-design-closure/all-city-baseline-audit")


def historical_sources(root: Path) -> dict[Path, tuple[str, Path]]:
    """Only these byte-preserved readers use their original relative locations."""
    maglev = json.loads((root / "docs/archives/pre-comfort-default/manifest.json").read_bytes())
    audit = json.loads((root / AUDIT / "manifest.json").read_bytes())
    gate = Path("docs/design-engine/v06-design-closure/README.md")
    copied = Path("reviewed-working-gate") / gate
    if hashlib.sha256((root / AUDIT / copied).read_bytes()).hexdigest() != audit["files"][copied.as_posix()]["sha256"]:
        raise ValueError("The archived city audit reader differs from its manifest")
    sources = {Path(name): (maglev["source_revision"], Path(name)) for name in (
        "engineering/ferrite_maglev/city-index.md",
        "docs/design-engine/ferrite-maglev/research-closure/readme-coverage.md")}
    sources[AUDIT / copied] = (audit["source_commit"], gate)
    return sources


def epoch_trees(root: Path, epochs: set[str]) -> dict[str, dict[str, str]]:
    """Read commit trees once. Shallow clones can fetch the two pinned commits in one request."""
    if not all(re.fullmatch(r"[0-9a-f]{40}", commit) for commit in epochs):
        raise ValueError("Invalid archive revision")
    missing = [commit for commit in sorted(epochs) if subprocess.run(
        ["git", "cat-file", "-e", commit + "^{tree}"], cwd=root, stderr=subprocess.DEVNULL).returncode]
    if missing:
        subprocess.run(["git", "fetch", "--no-tags", "--no-write-fetch-head", "--depth=1",
                        "--filter=blob:none", "origin", *missing], cwd=root, check=True)
    trees = {}
    for commit in sorted(epochs):
        listing = subprocess.check_output(["git", "ls-tree", "-r", "-t", "-z", "--full-tree",
                                          "--format=%(objectname)%x09%(path)", commit], cwd=root)
        tree = {}
        for record in listing.split(b"\0"):
            if record:
                oid, name = record.split(b"\t", 1)
                tree[name.decode("utf-8", errors="surrogateescape")] = oid.decode("ascii")
        trees[commit] = tree
    return trees


def historical_target_exists(source: Path, candidate: str, tree: dict[str, str]) -> bool:
    relative = posixpath.normpath(posixpath.join(source.parent.as_posix(), candidate))
    return relative == "." or relative in tree


def check() -> list[BrokenLink]:
    broken: list[BrokenLink] = []
    historical = historical_sources(REPO_ROOT)
    trees = epoch_trees(REPO_ROOT, {commit for commit, _ in historical.values()})
    for relative in markdown_files():
        source = REPO_ROOT / relative
        if not source.exists():
            continue
        history = historical.get(relative)
        if history:
            commit, original = history
            tree = trees[commit]
            contents = source.read_bytes()
            oid = hashlib.sha1(b"blob " + str(len(contents)).encode() + b"\0" + contents).hexdigest()
            if tree.get(original.as_posix()) != oid:
                raise ValueError(f"{relative} differs from {commit}:{original}")
        for line_no, line in enumerate(source.read_text(errors="replace").splitlines(), 1):
            targets = INLINE_LINK.findall(line)
            if reference := REFERENCE_TARGET.match(line):
                targets.append(reference.group(1))
            for raw in targets:
                candidates = normalized_candidates(raw)
                if not candidates:
                    continue
                if history:
                    exists = any(historical_target_exists(original, candidate, tree) for candidate in candidates)
                else:
                    exists = any((source.parent / candidate).resolve().exists() for candidate in candidates)
                if not exists:
                    broken.append(BrokenLink(relative, line_no, raw))
    return broken


def main() -> int:
    broken = check()
    for finding in broken:
        print(f"{finding.source}:{finding.line}: missing local link {finding.target!r}")
    if broken:
        print(f"{len(broken)} broken local Markdown link(s)", file=sys.stderr)
        return 1
    print(
        "local Markdown links: ok (three historical readers verified in their original Git trees; archived payloads preserved)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check that local links in tracked Markdown resolve inside the repository."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[1]
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
    return sorted({Path(path) for path in tracked + untracked})


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


def check() -> list[BrokenLink]:
    broken: list[BrokenLink] = []
    for relative in markdown_files():
        source = REPO_ROOT / relative
        if not source.exists():
            continue
        for line_no, line in enumerate(source.read_text(errors="replace").splitlines(), 1):
            targets = INLINE_LINK.findall(line)
            if reference := REFERENCE_TARGET.match(line):
                targets.append(reference.group(1))
            for raw in targets:
                candidates = normalized_candidates(raw)
                if not candidates:
                    continue
                if not any((source.parent / candidate).resolve().exists() for candidate in candidates):
                    broken.append(BrokenLink(relative, line_no, raw))
    return broken


def main() -> int:
    broken = check()
    for finding in broken:
        print(f"{finding.source}:{finding.line}: missing local link {finding.target!r}")
    if broken:
        print(f"{len(broken)} broken local Markdown link(s)", file=sys.stderr)
        return 1
    print("local Markdown links: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

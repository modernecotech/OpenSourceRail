#!/usr/bin/env python3
"""Check the maintained and generated README corpus as one documentation set."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def tracked_readmes() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "*README.md"], cwd=REPO_ROOT, text=True
    )
    return [REPO_ROOT / relative for relative in output.splitlines() if relative]


def normalized(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true", help="remove trailing whitespace and add final newlines")
    args = parser.parse_args()
    findings: list[str] = []
    paths = tracked_readmes()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        expected = normalized(text)
        if args.fix and text != expected:
            path.write_text(expected, encoding="utf-8")
            text = expected
        relative = path.relative_to(REPO_ROOT)
        if not text.startswith("# "):
            findings.append(f"{relative}: README must start with one H1 title")
        if text != normalized(text):
            findings.append(f"{relative}: trailing whitespace or missing final newline")
        if (path.parent / "design.toml").is_file():
            if "Auto-planned by the OpenSourceRail design pipeline" not in text:
                findings.append(f"{relative}: generated city README lacks provenance marker")
    if findings:
        print(f"README check: {len(findings)} finding(s)")
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print(f"README check: ok ({len(paths)} tracked README files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

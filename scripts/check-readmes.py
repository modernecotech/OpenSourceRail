#!/usr/bin/env python3
"""Check the maintained and generated README corpus as one documentation set."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def tracked_readmes() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "*README.md", "*NATIONAL-BRIEF.md"],
        cwd=REPO_ROOT,
        text=True,
    )
    # ``git ls-files`` includes paths deleted from the working tree until their
    # removal is staged.  Content checks should still work while generators are
    # reconciling tracked outputs in a dirty worktree.
    return [
        REPO_ROOT / relative
        for relative in output.splitlines()
        if relative and (REPO_ROOT / relative).is_file()
    ]


def normalized(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true", help="remove trailing whitespace and add final newlines")
    args = parser.parse_args()
    findings: list[str] = []
    paths = tracked_readmes()
    root_readme = REPO_ROOT / "README.md"
    docs_readme = REPO_ROOT / "docs/README.md"
    if not root_readme.is_file():
        findings.append("README.md: missing repository front door")
    else:
        root_text = root_readme.read_text(encoding="utf-8")
        if len(root_text.splitlines()) > 220:
            findings.append("README.md: front door exceeds 220 lines")
        for heading in ("## Find Your Way", "## Source Of Truth"):
            if heading not in root_text:
                findings.append(f"README.md: missing front-door section {heading!r}")
    if not docs_readme.is_file():
        findings.append("docs/README.md: missing documentation pointer")
    else:
        docs_text = docs_readme.read_text(encoding="utf-8")
        if len(docs_text.splitlines()) > 30:
            findings.append("docs/README.md: duplicates navigation instead of linking to root")
        if "only human-facing\nnavigation page" not in docs_text:
            findings.append("docs/README.md: does not identify the root README as the front door")

    tracked_markdown = subprocess.check_output(
        ["git", "ls-files", "*.md"], cwd=REPO_ROOT, text=True
    ).splitlines()
    setup_sources = [
        relative
        for relative in tracked_markdown
        if (REPO_ROOT / relative).is_file()
        and "./install.sh" in (REPO_ROOT / relative).read_text(encoding="utf-8")
    ]
    if setup_sources != ["README.md"]:
        findings.append(
            "common setup command must live only in README.md; found "
            + ", ".join(setup_sources)
        )
    common_reference = REPO_ROOT / "docs/deployment-planning-reference.md"
    if not common_reference.is_file():
        findings.append("docs/deployment-planning-reference.md: missing common deployment page")
    else:
        common_text = common_reference.read_text(encoding="utf-8")
        for heading in (
            "## Network And Station Planning",
            "## Service, Fleet And Capacity",
            "## Energy Method",
            "## Civil And Cost Method",
            "## Capital And Finance Method",
            "## QA, Maintenance And Assurance",
            "## Local Evidence Contract",
        ):
            if heading not in common_text:
                findings.append(
                    f"docs/deployment-planning-reference.md: missing shared section {heading!r}"
                )
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
            if "[deployment planning reference]" not in text:
                findings.append(f"{relative}: generated city README lacks common-method link")
            if len(text.splitlines()) > 120:
                findings.append(f"{relative}: generated city README exceeds 120-line local-summary limit")
            for duplicated_heading in (
                "## Construction QA system",
                "## Maintenance schedule system",
                "## Broad economic benefits (planning proxy)",
                "## Turnaround inspection and recharge",
                "## Distributed overnight stabling",
            ):
                if duplicated_heading in text:
                    findings.append(
                        f"{relative}: shared section belongs in deployment-planning-reference.md: "
                        f"{duplicated_heading!r}"
                    )
        if path.name == "NATIONAL-BRIEF.md":
            if "[deployment planning reference]" not in text:
                findings.append(f"{relative}: national brief lacks common-method link")
            if len(text.splitlines()) > 100:
                findings.append(f"{relative}: national brief exceeds 100-line local-summary limit")
    if findings:
        print(f"README check: {len(findings)} finding(s)")
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print(f"README check: ok ({len(paths)} tracked README/brief files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

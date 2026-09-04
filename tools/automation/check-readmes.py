#!/usr/bin/env python3
"""Check the maintained and generated README corpus as one documentation set."""

from __future__ import annotations

import argparse
import json
import subprocess
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_REGIONS = {
    "central-africa",
    "east-africa",
    "latin-america",
    "north-africa",
    "south-africa",
    "south-asia",
    "southeast-asia",
    "west-africa",
    "west-asia",
}


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
        if "[complete PDF book](OpenSourceRail-Book.pdf)" not in root_text:
            findings.append("README.md: missing root PDF-book link")
        if "./osr build" not in root_text:
            findings.append("README.md: missing one-command complete build")
        design_paths = sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml"))
        public_paths = [
            path
            for path in design_paths
            if path.relative_to(REPO_ROOT / "cities/catalogue").parts[0] in PUBLIC_REGIONS
        ]
        countries = {
            path.relative_to(REPO_ROOT / "cities/catalogue").parts[1]
            for path in public_paths
        }
        expected_scope = (
            f"**{len(public_paths)} cities in {len(countries)} developing countries**"
        )
        if expected_scope not in root_text:
            findings.append(
                f"README.md: public evidence count is stale; expected {expected_scope}"
            )
    if not (REPO_ROOT / "OpenSourceRail-Book.pdf").is_file():
        findings.append("OpenSourceRail-Book.pdf: missing published reader book")
    elif subprocess.run(
        ["git", "ls-files", "--error-unmatch", "OpenSourceRail-Book.pdf"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode:
        findings.append("OpenSourceRail-Book.pdf: book exists locally but is not tracked")
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
    untracked_markdown = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "*.md"],
        cwd=REPO_ROOT,
        text=True,
    ).splitlines()
    inventory_path = REPO_ROOT / "docs/INDEX.md"
    if inventory_path.is_file():
        inventory_text = inventory_path.read_text(encoding="utf-8")
        for relative in sorted(set(tracked_markdown + untracked_markdown) - {"docs/INDEX.md"}):
            if (REPO_ROOT / relative).is_file() and f"`{relative}`" not in inventory_text:
                findings.append(f"docs/INDEX.md: missing Markdown inventory entry for {relative}")

    trainset_root = REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset"
    contract_paths = {
        "manifest": trainset_root / "buildable-trainset-manifest.json",
        "mass": trainset_root / "mass-closure-ledger.json",
        "factory": trainset_root / "factory-release-work-packages.json",
        "methods": trainset_root / "manufacturing-methods.json",
        "cots": trainset_root / "cots-candidates.json",
        "evidence": REPO_ROOT / "lib/templates/lm3-first-article-evidence.toml",
        "evidence_status": trainset_root / "first-article-evidence-status.json",
    }
    if all(path.is_file() for path in contract_paths.values()):
        manifest = json.loads(contract_paths["manifest"].read_text(encoding="utf-8"))
        mass = json.loads(contract_paths["mass"].read_text(encoding="utf-8"))
        factory = json.loads(contract_paths["factory"].read_text(encoding="utf-8"))
        methods = json.loads(contract_paths["methods"].read_text(encoding="utf-8"))
        cots = json.loads(contract_paths["cots"].read_text(encoding="utf-8"))
        evidence = tomllib.loads(contract_paths["evidence"].read_text(encoding="utf-8"))
        evidence_status = json.loads(contract_paths["evidence_status"].read_text(encoding="utf-8"))
        products = len(manifest["product_items"])
        assemblies = len(manifest["assemblies"])
        make_rows = sum(row["route"] == "MAKE" for row in manifest["product_items"])
        bought_rows = int(cots["coverage"]["external_product_rows"])
        active_rows = int(mass["coverage"]["active_product_rows"])
        mapped_rows = int(mass["coverage"]["mapped_product_rows"])
        closed_rows = int(mass["coverage"]["closed_active_product_rows"])
        factory_packages = int(factory["package_count"])
        method_count = int(methods["coverage"]["method_count"])
        tooling_count = int(methods["coverage"]["tooling_count"])
        candidate_count = int(cots["coverage"]["candidate_count"])
        evidence_count = len(evidence["evidence_package"])
        open_evidence_count = int(evidence_status["open_count"])

        current_contracts = {
            REPO_ROOT / "README.md": (
                f"controls {products} product rows and {assemblies} assembly nodes",
                f"The {make_rows} locally made rows",
                "exterior-finish-system.md",
                "factory-release-work-packages.md",
                "mass-closure-ledger.md",
            ),
            REPO_ROOT / "docs/ROADMAP.md": (
                f"{products}-product-row/{assemblies}-assembly",
                f"{candidate_count} manufacturer/research candidates covering all {bought_rows} bought-in rows",
                f"{factory_packages} factory drawing/interface packages",
                f"{evidence_count}-gate first-article route",
                f"maps {mapped_rows}/{products} rows",
                f"{closed_rows}/{active_rows} active rows mass-closed",
                "all 10 drawing packages open",
                "factory-release-readiness.md",
            ),
            REPO_ROOT / "design/component-catalogue/README.md": (
                "mass-budget.md",
                "mass-closure-ledger.md",
                "factory-release-work-packages.md",
                "factory-release-readiness.md",
                "first-article-evidence-status.md",
            ),
            trainset_root / "README.md": (
                f"all {evidence_count} evidence gates",
                f"{open_evidence_count} still-open",
                f"all {products} product links, {method_count} timed methods, {tooling_count} tooling families",
                "open-release-gaps.md",
                "factory-release-readiness.md",
                "exterior-finish-system.md",
                "mass-closure-ledger.md",
            ),
            REPO_ROOT / "design/component-catalogue/catalog/buildable-stations/README.md": (
                "station-product-reconciliation.md",
            ),
        }
        for path, snippets in current_contracts.items():
            text = path.read_text(encoding="utf-8")
            for snippet in snippets:
                if snippet not in text:
                    findings.append(
                        f"{path.relative_to(REPO_ROOT)}: current engineering contract missing {snippet!r}"
                    )

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
            region = path.relative_to(REPO_ROOT / "cities/catalogue").parts[0]
            if region not in PUBLIC_REGIONS:
                findings.append(
                    f"{relative}: comparison-only region must not publish a national brief"
                )
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

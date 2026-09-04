#!/usr/bin/env python3
"""Freeze the LM3 first-article design baseline and export open work packages."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tomllib


REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset"
MANIFEST = CATALOGUE / "buildable-trainset-manifest.json"
STATE = CATALOGUE / "first-article-work-package-state.toml"
EVIDENCE = REPO_ROOT / "lib/templates/lm3-first-article-evidence.toml"
COTS = CATALOGUE / "cots-candidates.json"
FACTORY_RELEASE = CATALOGUE / "factory-release-work-packages.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owner_role(row: dict) -> str:
    if row["route"] == "MAKE":
        return "local manufacturing engineer + design authority"
    if row["route"] == "BID":
        return "subsystem engineer + procurement lead"
    return "materials/component engineer + procurement lead"


def matching_evidence_ids(engineering_id: str, packages: list[dict]) -> list[str]:
    return [
        package["id"]
        for package in packages
        if any(engineering_id.startswith(prefix) for prefix in package["applies_to_prefixes"])
    ]


def write_markdown(package: dict, path: Path) -> None:
    counts = package["status_counts"]
    rows = [
        "# LM3 First-Article Public Work Packages",
        "",
        "Generated from the controlled LM3 manifest and closure-state overrides. An issue may close only after its required evidence is reviewed; repository generation never converts a planned test into performed evidence.",
        "",
        f"**Baseline:** `{package['first_article_id']}` · **Open:** {package['open_count']} · **Accepted:** {counts.get('accepted', 0)}",
        "",
        "| Work package | Status | Owner | Candidate / evidence route | Issue |",
        "|---|---|---|---|---|",
    ]
    for row in package["work_packages"]:
        issue = f"[#{row['github_issue_number']}]({row['github_issue_url']})" if row.get("github_issue_url") else "ready to publish"
        routes = [
            *row.get("candidate_ids", []),
            *row.get("factory_release_package_ids", []),
            *row["evidence_package_ids"],
        ]
        evidence = ", ".join(f"`{value}`" for value in routes) or "product-row acceptance"
        rows.append(
            f"| `{row['id']}` — {row['title'].split(' — ', 1)[-1]} | {row['status']} | {row.get('owner') or row['owner_role']} | {evidence} | {issue} |"
        )
    rows.extend(["", "Machine-readable authority: [`first-article-work-packages.json`](first-article-work-packages.json).", ""])
    path.write_text("\n".join(rows), encoding="utf-8")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    state = tomllib.loads(STATE.read_text(encoding="utf-8"))
    evidence_packages = tomllib.loads(EVIDENCE.read_text(encoding="utf-8"))["evidence_package"]
    cots = json.loads(COTS.read_text(encoding="utf-8"))
    factory_release = json.loads(FACTORY_RELEASE.read_text(encoding="utf-8"))
    product_to_candidates = cots["product_to_candidates"]
    product_to_factory_release = {
        product_id: [
            package["id"]
            for package in factory_release["packages"]
            if product_id in package["product_ids"]
        ]
        for product_id in (row["id"] for row in manifest["product_items"])
    }
    overrides = {row["id"]: row for row in state.get("override", [])}
    open_rows = [
        row for row in manifest["product_items"]
        if row["maturity"] != "release-candidate"
    ]
    work_packages = []
    for row in open_rows:
        work_id = f'WP-{row["id"]}'
        override = overrides.get(work_id, {})
        status = override.get("status", "open")
        if status not in {"open", "in-progress", "evidence-submitted", "accepted", "blocked"}:
            raise SystemExit(f"invalid closure state for {work_id}: {status}")
        if status == "accepted" and not (override.get("evidence_refs") and override.get("reviewed_by")):
            raise SystemExit(f"accepted package {work_id} requires evidence_refs and reviewed_by")
        issue_title = f'{row["id"]} — freeze {row["title"]}'
        evidence_text = "; ".join(row.get("acceptance", []))
        candidate_ids = product_to_candidates.get(row["id"], [])
        factory_release_package_ids = product_to_factory_release.get(row["id"], [])
        work_packages.append({
            "id": work_id,
            "status": status,
            "engineering_id": row["id"],
            "title": issue_title,
            "route": row["route"],
            "maturity": row["maturity"],
            "parent_assembly": row["parent"],
            "owner_role": owner_role(row),
            "owner": override.get("owner", ""),
            "evidence_required": row.get("acceptance", []),
            "evidence_package_ids": matching_evidence_ids(row["id"], evidence_packages),
            "candidate_ids": candidate_ids,
            "factory_release_package_ids": factory_release_package_ids,
            "evidence_refs": override.get("evidence_refs", []),
            "reviewed_by": override.get("reviewed_by", ""),
            "github_issue_number": override.get("github_issue_number"),
            "github_issue_url": override.get("github_issue_url", ""),
            "source_refs": row.get("source_refs", []),
            "github_issue": {
                "title": issue_title,
                "labels": ["first-article", "LM3", row["route"].lower()],
                "body": (
                    f'<!-- osr-work-package: {work_id} -->\n\n'
                    f'Authoritative row: `{row["id"]}` in the LM3 buildable '
                    f'trainset manifest.\n\nParent: `{row["parent"]}`\n\n'
                    f'Closure evidence: {evidence_text}.\n\n'
                    f"Candidate sources: {', '.join(f'`{value}`' for value in candidate_ids) or 'locally manufactured item; no bought-in candidate'}.\n\n"
                    f"Factory drawing/interface packages: {', '.join(f'`{value}`' for value in factory_release_package_ids) or 'no dedicated factory-release package; use product definition and traveler'}.\n\n"
                    'Do not mark complete without '
                    "reviewed supplier/drawing/test evidence committed or linked "
                    "from the authoritative register."
                ),
            },
        })

    package = {
        "schema_version": "1.2",
        "first_article_id": "LM3-FA-001",
        "source_manifest": str(MANIFEST.relative_to(REPO_ROOT)),
        "source_manifest_sha256": digest(MANIFEST),
        "open_count": sum(row["status"] != "accepted" for row in work_packages),
        "status_counts": {
            status: sum(row["status"] == status for row in work_packages)
            for status in ("open", "in-progress", "evidence-submitted", "accepted", "blocked")
        },
        "closure_state_source": str(STATE.relative_to(REPO_ROOT)),
        "evidence_plan_source": str(EVIDENCE.relative_to(REPO_ROOT)),
        "candidate_register_source": str(COTS.relative_to(REPO_ROOT)),
        "candidate_register_sha256": digest(COTS),
        "factory_release_source": str(FACTORY_RELEASE.relative_to(REPO_ROOT)),
        "factory_release_sha256": digest(FACTORY_RELEASE),
        "work_packages": work_packages,
        "publication_note": (
            "Issue-ready export only. Publishing GitHub issues is an explicit "
            "maintainer action; this generator does not access the network."
        ),
    }
    work_path = CATALOGUE / "first-article-work-packages.json"
    work_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    write_markdown(package, CATALOGUE / "first-article-work-packages.md")

    baseline = {
        "schema_version": "1.0",
        "id": "LM3-FA-001",
        "status": "controlled-design-baseline-release-evidence-open",
        "configuration": manifest["target_candidate"],
        "candidate_id": manifest["candidate"]["id"],
        "candidate_metrics": manifest["candidate"]["metrics"],
        "product_rows": len(manifest["product_items"]),
        "assembly_nodes": len(manifest["assemblies"]),
        "open_work_packages": package["open_count"],
        "work_package_register": str(work_path.relative_to(REPO_ROOT)),
        "source_manifest": str(MANIFEST.relative_to(REPO_ROOT)),
        "source_manifest_sha256": digest(MANIFEST),
        "change_control": (
            "Change target configuration only through reviewed source changes, "
            "regeneration and updated CAD/IFC/simulation evidence."
        ),
        "release_boundary": (
            "This freezes the repository design candidate, not supplier SKUs, "
            "production drawings, manufacturing approval or vehicle acceptance."
        ),
    }
    baseline_path = CATALOGUE / "first-article-baseline.json"
    baseline_path.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    print(
        f"wrote {baseline_path.relative_to(REPO_ROOT)} and "
        f"{work_path.relative_to(REPO_ROOT)} ({len(work_packages)} open packages)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

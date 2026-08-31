#!/usr/bin/env python3
"""Freeze the LM3 first-article design baseline and export open work packages."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = REPO_ROOT / "design/component-catalogue/catalog/buildable-trainset"
MANIFEST = CATALOGUE / "buildable-trainset-manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owner_role(row: dict) -> str:
    if row["route"] == "MAKE":
        return "local manufacturing engineer + design authority"
    if row["route"] == "BID":
        return "subsystem engineer + procurement lead"
    return "materials/component engineer + procurement lead"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    open_rows = [
        row for row in manifest["product_items"]
        if row["maturity"] != "release-candidate"
    ]
    work_packages = []
    for row in open_rows:
        issue_title = f'{row["id"]} — freeze {row["title"]}'
        evidence = "; ".join(row.get("acceptance", []))
        work_packages.append({
            "id": f'WP-{row["id"]}',
            "status": "open",
            "engineering_id": row["id"],
            "title": issue_title,
            "route": row["route"],
            "maturity": row["maturity"],
            "parent_assembly": row["parent"],
            "owner_role": owner_role(row),
            "evidence_required": row.get("acceptance", []),
            "source_refs": row.get("source_refs", []),
            "github_issue": {
                "title": issue_title,
                "labels": ["first-article", "LM3", row["route"].lower()],
                "body": (
                    f'Authoritative row: `{row["id"]}` in the LM3 buildable '
                    f'trainset manifest.\n\nParent: `{row["parent"]}`\n\n'
                    f'Closure evidence: {evidence}.\n\nDo not mark complete without '
                    "reviewed supplier/drawing/test evidence committed or linked "
                    "from the authoritative register."
                ),
            },
        })

    package = {
        "schema_version": "1.0",
        "first_article_id": "LM3-FA-001",
        "source_manifest": str(MANIFEST.relative_to(REPO_ROOT)),
        "source_manifest_sha256": digest(MANIFEST),
        "open_count": len(work_packages),
        "work_packages": work_packages,
        "publication_note": (
            "Issue-ready export only. Publishing GitHub issues is an explicit "
            "maintainer action; this generator does not access the network."
        ),
    }
    work_path = CATALOGUE / "first-article-work-packages.json"
    work_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")

    baseline = {
        "schema_version": "1.0",
        "id": "LM3-FA-001",
        "status": "controlled-design-baseline-release-evidence-open",
        "configuration": manifest["target_candidate"],
        "candidate_id": manifest["candidate"]["id"],
        "candidate_metrics": manifest["candidate"]["metrics"],
        "product_rows": len(manifest["product_items"]),
        "assembly_nodes": len(manifest["assemblies"]),
        "open_work_packages": len(work_packages),
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

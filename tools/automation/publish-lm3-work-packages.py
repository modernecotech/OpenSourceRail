#!/usr/bin/env python3
"""Idempotently publish LM3 first-article work packages as GitHub issues."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "design/component-catalogue/catalog/buildable-trainset/first-article-work-packages.json"


def gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="create/update public issues; default is a read-only plan")
    args = parser.parse_args()
    package = json.loads(REGISTER.read_text(encoding="utf-8"))
    rows = [row for row in package["work_packages"] if row["status"] != "accepted"]
    if not args.apply:
        print(f"would reconcile {len(rows)} public LM3 work-package issues; rerun with --apply after reviewing the generated register")
        return 0
    gh("auth", "status")
    for label, color, description in [
        ("first-article", "1d76db", "LM3 first-article release work"),
        ("LM3", "5319e7", "LM3 rolling-stock baseline"),
        ("make", "0e8a16", "Local make route"),
        ("bid", "fbca04", "Competitive bid route"),
        ("source", "d93f0b", "Supplier/material source route"),
    ]:
        subprocess.run(["gh", "label", "create", label, "--color", color, "--description", description, "--force"], cwd=ROOT, check=True)
    existing = json.loads(gh("issue", "list", "--state", "all", "--limit", "1000", "--json", "number,title,body,url,state"))
    by_marker = {}
    for issue in existing:
        for line in str(issue.get("body", "")).splitlines():
            if line.startswith("<!-- osr-work-package: "):
                by_marker[line.strip()] = issue
                break
    published = []
    for row in rows:
        issue = row["github_issue"]
        marker = f"<!-- osr-work-package: {row['id']} -->"
        labels = ",".join(issue["labels"])
        current = by_marker.get(marker)
        if current:
            gh("issue", "edit", str(current["number"]), "--title", issue["title"], "--body", issue["body"], "--add-label", labels)
            published.append({"id": row["id"], "number": current["number"], "url": current["url"], "action": "updated"})
        else:
            url = gh("issue", "create", "--title", issue["title"], "--body", issue["body"], "--label", labels)
            published.append({"id": row["id"], "url": url, "action": "created"})
    output = ROOT / "build/lm3-first-article-github-issues.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"first_article_id": package["first_article_id"], "issues": published}, indent=2) + "\n", encoding="utf-8")
    print(f"reconciled {len(published)} GitHub issues; mapping: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

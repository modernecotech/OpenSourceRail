#!/usr/bin/env python3
"""Validate LM3 first-article engineering evidence without inventing test results."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "lib/templates/lm3-first-article-evidence.toml"
CATALOGUE = ROOT / "design/component-catalogue/catalog/buildable-trainset"
SUBMISSIONS = CATALOGUE / "evidence/submissions"
STATUS_JSON = CATALOGUE / "first-article-evidence-status.json"
STATUS_MD = CATALOGUE / "first-article-evidence-status.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_submission(path: Path, package_id: str) -> tuple[bool, list[str], dict]:
    errors: list[str] = []
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"invalid JSON: {exc}"], {}
    required = ["evidence_package_id", "status", "performed_at", "performed_by", "reviewed_by", "configuration_id", "procedure_revision", "equipment", "artifacts"]
    for field in required:
        if not row.get(field):
            errors.append(f"missing {field}")
    if row.get("evidence_package_id") != package_id:
        errors.append("evidence_package_id mismatch")
    if row.get("status") not in {"evidence-received", "independently-accepted"}:
        errors.append("status must be evidence-received or independently-accepted")
    if not isinstance(row.get("equipment"), list) or not all(item.get("id") and item.get("calibration_due") for item in row.get("equipment", [])):
        errors.append("every equipment row requires id and calibration_due")
    for artifact in row.get("artifacts", []):
        relative = Path(str(artifact.get("path", "")))
        try:
            target = (ROOT / relative).resolve()
            target.relative_to(ROOT)
        except ValueError:
            errors.append(f"artifact outside repository: {relative}")
            continue
        if not target.is_file():
            errors.append(f"missing artifact: {relative}")
        elif artifact.get("sha256") != digest(target):
            errors.append(f"checksum mismatch: {relative}")
    return not errors, errors, row


def build_status() -> dict:
    plan = tomllib.loads(PLAN.read_text(encoding="utf-8"))
    rows = []
    for package in plan["evidence_package"]:
        missing = [path for path in package.get("existing_artifacts", []) if not (ROOT / path).exists()]
        submission_paths = sorted(SUBMISSIONS.glob(f"{package['id']}*.json")) if SUBMISSIONS.exists() else []
        valid_submissions = []
        submission_errors = []
        for path in submission_paths:
            valid, errors, submission = validate_submission(path, package["id"])
            if valid:
                valid_submissions.append({"path": str(path.relative_to(ROOT)), "status": submission["status"], "sha256": digest(path)})
            else:
                submission_errors.append({"path": str(path.relative_to(ROOT)), "errors": errors})
        accepted = any(row["status"] == "independently-accepted" for row in valid_submissions)
        rows.append({
            **package,
            "existing_artifacts_complete": not missing,
            "missing_existing_artifacts": missing,
            "valid_submissions": valid_submissions,
            "submission_errors": submission_errors,
            "release_gate": "accepted" if accepted else "open",
        })
    return {
        "schema_version": "1.0",
        "first_article_id": plan["first_article_id"],
        "release_ready": all(row["release_gate"] == "accepted" for row in rows),
        "accepted_count": sum(row["release_gate"] == "accepted" for row in rows),
        "open_count": sum(row["release_gate"] != "accepted" for row in rows),
        "packages": rows,
        "interpretation": "Solver-backed screening is useful design evidence but does not close a physical or supplier release gate.",
    }


def write_status(status: dict) -> None:
    STATUS_JSON.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# LM3 First-Article Evidence Status",
        "",
        "This register distinguishes existing solver-backed screening from supplier, laboratory and independently accepted release evidence. Planned protocols are not represented as performed tests.",
        "",
        f"**Release ready:** {'yes' if status['release_ready'] else 'no'} · **Accepted:** {status['accepted_count']} · **Open:** {status['open_count']}",
        "",
        "| Evidence package | Repository status | Release gate | Existing artifacts |",
        "|---|---|---|---|",
    ]
    for row in status["packages"]:
        artifact_status = "present" if row["existing_artifacts_complete"] else f"missing {len(row['missing_existing_artifacts'])}"
        lines.append(f"| `{row['id']}` — {row['title']} | {row['status']} | {row['release_gate']} | {artifact_status} |")
    lines.extend([
        "",
        "A gate becomes accepted only through a submission under `evidence/submissions/` containing accountable people, configuration/procedure revisions, calibrated equipment, raw/review artifacts and verified SHA-256 values.",
        "",
    ])
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when generated status files drift")
    args = parser.parse_args()
    status = build_status()
    json_text = json.dumps(status, indent=2) + "\n"
    if args.check:
        if not STATUS_JSON.exists() or STATUS_JSON.read_text(encoding="utf-8") != json_text:
            raise SystemExit("LM3 evidence status is stale; run validate-lm3-first-article-evidence.py")
    else:
        write_status(status)
    if any(row["submission_errors"] for row in status["packages"]):
        raise SystemExit("one or more LM3 evidence submissions are invalid")
    print(f"LM3 evidence: {status['accepted_count']} accepted, {status['open_count']} open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate the tracked engineering analysis register and evidence hygiene."""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path


REVIEWED = {"calibrated", "independently-checked", "accepted"}
FORBIDDEN_EVIDENCE = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".webp"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("register", type=Path, nargs="?", default=Path("engineering/analysis-register.toml"))
    args = parser.parse_args()
    root = Path.cwd()
    data = tomllib.loads(args.register.read_text(encoding="utf-8"))
    allowed = set(data["statuses"])
    errors: list[str] = []
    seen: set[str] = set()
    for index, analysis in enumerate(data.get("analysis", []), start=1):
        prefix = f"analysis[{index}]"
        analysis_id = str(analysis.get("id", ""))
        if not analysis_id or analysis_id in seen:
            errors.append(f"{prefix}: ID is missing or duplicated: {analysis_id!r}")
        seen.add(analysis_id)
        status = analysis.get("status")
        if status not in allowed:
            errors.append(f"{analysis_id}: invalid status {status!r}")
        for field in ("title", "tool", "acceptance_criterion", "limitations"):
            if not str(analysis.get(field, "")).strip():
                errors.append(f"{analysis_id}: missing {field}")
        for path_text in analysis.get("input_paths", []):
            path = root / path_text
            if not path.is_file():
                errors.append(f"{analysis_id}: missing tracked input {path_text}")
        result_path = str(analysis.get("result_path", ""))
        if Path(result_path).suffix.lower() in FORBIDDEN_EVIDENCE:
            errors.append(f"{analysis_id}: screenshot/image cannot be the result artifact")
        if status != "planned" and not analysis.get("converged", False):
            errors.append(f"{analysis_id}: non-planned analysis is not marked converged")
        if status in REVIEWED:
            for field in ("reviewer", "review_date", "evidence_revision"):
                if not str(analysis.get(field, "")).strip():
                    errors.append(f"{analysis_id}: reviewed status requires {field}")
            if not result_path:
                errors.append(f"{analysis_id}: reviewed status requires a result artifact")
    if errors:
        for error in errors:
            print(f"analysis-register: {error}")
        return 1
    print(f"analysis-register: ok ({len(seen)} analyses; {len(allowed)} statuses)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

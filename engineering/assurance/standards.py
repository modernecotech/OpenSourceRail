"""Compile the OSR standards crosswalk and detect changes in its digital evidence."""

import argparse
from datetime import date
from hashlib import file_digest
import json
from pathlib import Path
import sys
import tomllib
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = Path("docs/certification")
REGISTER = DIRECTORY / "standards.toml"
REPORT = DIRECTORY / "digital-assurance-report.json"
MATRIX = DIRECTORY / "compliance-matrix.md"


def _evidence(root, names):
    digests = {}
    for name in names:
        path = root / name
        if (Path(name).is_absolute() or Path(name).as_posix() != name
                or ".." in Path(name).parts or not path.resolve().is_relative_to(root)):
            raise ValueError(f"Evidence path must stay in the checkout: {name}")
        if not path.is_file():
            raise ValueError(f"Missing evidence file: {name}")
        with path.open("rb") as stream:
            digests[name] = file_digest(stream, "sha256").hexdigest()
    return digests


def compile_register(root=ROOT, today=None):
    """Record exactly the source bytes available for each open control."""
    root = Path(root).resolve()
    with (root / REGISTER).open("rb") as source:
        data = tomllib.load(source)

    reviewed, due = data["reviewed"], data["review_due"]
    today = date.today() if today is None else today
    if data["schema"] != 1 or not reviewed <= today <= due or reviewed >= due:
        raise ValueError("Review the publisher records and applicable editions before updating the register")

    standards = data["standards"]
    for name, url in standards.items():
        link = urlsplit(url)
        if not name.strip() or link.scheme != "https" or not link.netloc:
            raise ValueError(f"Invalid publisher reference: {name}")

    controls = {}
    used_standards = set()
    fields = ("id", "subject", "scope", "risk", "objective", "match", "maturity", "owner", "gap")
    for row in data["control"]:
        for field in fields:
            value = row[field]
            if not isinstance(value, str) or not value.strip() or "|" in value or "\n" in value:
                raise ValueError(f"Invalid control field: {field}")
        control = row["id"]
        if control in controls:
            raise ValueError(f"Duplicate control: {control}")
        references = row["standards"]
        evidence = row["evidence"]
        if (not isinstance(references, list) or not references
                or len(set(references)) != len(references) or set(references) - standards.keys()):
            raise ValueError(f"{control} requires unique registered standards")
        if not isinstance(evidence, list) or not evidence or len(set(evidence)) != len(evidence):
            raise ValueError(f"{control} requires unique evidence paths")
        used_standards.update(references)
        controls[control] = {
            **{key: row[key] for key in fields if key != "id"},
            "standards": references,
            "evidence_sha256": _evidence(root, evidence),
            "deployment_applicability": "open",
            "acceptance": "open",
        }
    if not controls or used_standards != standards.keys():
        raise ValueError("Every registered standard needs a mapped control")
    return {
        "schema": "osr-standards-crosswalk/1",
        "publisher_reviewed": reviewed.isoformat(),
        "publisher_review_due": due.isoformat(),
        "standards": standards,
        "controls": controls,
    }


def change_impact(previous, current):
    """Report affected controls, including added/removed mappings and changed publishers."""
    changed = {}
    old, new = previous["controls"], current["controls"]
    for key in sorted(old.keys() | new.keys()):
        before, after = old.get(key), new.get(key)
        if before is None or after is None:
            changed[key] = {"mapping": "added" if before is None else "removed"}
            continue
        old_files, new_files = before["evidence_sha256"], after["evidence_sha256"]
        paths = sorted(name for name in old_files.keys() | new_files.keys()
                       if old_files.get(name) != new_files.get(name))
        old_fields = {field: value for field, value in before.items() if field != "evidence_sha256"}
        new_fields = {field: value for field, value in after.items() if field != "evidence_sha256"}
        publishers = sorted(name for name in set(before["standards"] + after["standards"])
                            if previous["standards"].get(name) != current["standards"].get(name))
        if paths or old_fields != new_fields or publishers:
            changed[key] = {
                "mapping_changed": old_fields != new_fields,
                "changed_publishers": publishers,
                "changed_evidence": paths,
                "review": "required",
            }
    return changed


def render_matrix(report):
    lines = [
        "# Standards and evidence crosswalk", "",
        "Generated from [the source register](standards.toml). Each row records a project question, "
        "the evidence available in OpenSourceRail and the work required for deployment review.", "",
        f"Publisher metadata reviewed **{report['publisher_reviewed']}**. "
        f"Next review due **{report['publisher_review_due']}**.", "",
    ]
    for identity, row in report["controls"].items():
        standards = " · ".join(f"[{name}]({report['standards'][name]})" for name in row["standards"])
        paths = " · ".join(f"[{Path(name).name}](../../{name})" for name in row["evidence_sha256"])
        lines.extend([
            f"## {identity} · {row['subject']}", "",
            f"{row['scope']}. {standards}", "",
            f"**Risk.** {row['risk']}", "",
            f"**Control objective.** {row['objective']}", "",
            f"**OSR evidence ({row['maturity']}).** {row['match']} {paths}", "",
            f"**Open work for the {row['owner'].lower()}.** {row['gap']}", "",
        ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify both published files")
    mode.add_argument("--write", action="store_true", help="refresh the evidence report and matrix")
    mode.add_argument("--impact", action="store_true", help="compare the checkout to the published report")
    args = parser.parse_args()
    try:
        current = compile_register()
        report = json.dumps(current, indent=2, sort_keys=True) + "\n"
        if args.impact:
            previous = json.loads((ROOT / REPORT).read_text(encoding="utf-8"))
            print(json.dumps(change_impact(previous, current), indent=2))
            return 0
        outputs = {REPORT: report, MATRIX: render_matrix(current)}
        if args.write:
            for path, content in outputs.items():
                (ROOT / path).write_text(content, encoding="utf-8")
        elif args.check:
            for path, content in outputs.items():
                if (ROOT / path).read_text(encoding="utf-8") != content:
                    raise ValueError(f"Stale {path}. Run --impact and review the affected controls before --write")
            print(f"{len(current['controls'])} standards controls verified against the checkout")
        else:
            print(render_matrix(current), end="")
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(f"Standards crosswalk: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

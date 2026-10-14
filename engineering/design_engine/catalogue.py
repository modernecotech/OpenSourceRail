"""Incremental city artifact inventory without deleting or replacing payloads."""

from __future__ import annotations
import json
from pathlib import Path
import subprocess
import tomllib

from .registry import ROOT
from .publication import digest
from .contracts import canonical, fingerprint


def cities():
    result = {}
    for path in sorted((ROOT / "cities/catalogue").glob("*/*/*/design.toml")):
        value = tomllib.loads(path.read_text())
        slug = value["city"].get("slug", path.parent.name.lower())
        if slug in result:
            raise ValueError("duplicate catalogue city identity")
        result[slug] = path.parent
    return result


def index():
    tracked = (
        subprocess.check_output(["git", "ls-files", "-z", "cities/catalogue"], cwd=ROOT)
        .decode()
        .split("\0")
    )
    by_root = {
        folder.relative_to(ROOT).as_posix(): slug for slug, folder in cities().items()
    }
    rows = {s: [] for s in by_root.values()}
    for name in sorted(filter(None, tracked)):
        path = ROOT / name
        if not path.is_file():
            continue
        parts = Path(name).parts
        if len(parts) < 6:
            continue
        root = "/".join(parts[:5])
        slug = by_root.get(root)
        if slug is None:
            continue
        rows[slug].append(
            dict(
                path=name,
                sha256=digest(path),
                bytes=path.stat().st_size,
                retrieval="git:" + name,
                retained=True,
                licence="repository and original-source mapping; OSM attribution retained",
            )
        )
    return dict(
        schema="osr-city-artifact-index/1",
        cities={
            slug: dict(
                core=[
                    r
                    for r in files
                    if r["path"].endswith(
                        ("/design.toml", "/" + slug + ".toml", "/README.md")
                    )
                ],
                artifacts=files,
                content_sha256=fingerprint(files),
                retention="payloads retained at original paths",
            )
            for slug, files in sorted(rows.items())
        },
        total_retained_files=sum(map(len, rows.values())),
        physical_release=False,
        payloads_deleted=False,
    )


def selected_plan(slugs):
    known = cities()
    if not slugs or any(s not in known for s in slugs):
        raise ValueError("choose existing catalogue cities")
    return dict(
        schema="osr-selected-city-generation/1",
        selected=slugs,
        commands=[["tools/automation/regenerate-city.sh", s] for s in slugs],
        unselected_unchanged_required=True,
        baseline_adoption_permitted=False,
        execution_location="local",
    )


def snapshot_unselected(selected):
    roots = [
        str(folder.relative_to(ROOT))
        for slug, folder in cities().items()
        if slug not in selected
    ]
    names = (
        subprocess.check_output(["git", "ls-files", "-z", "--", *roots], cwd=ROOT)
        .decode()
        .split("\0")
    )
    return {
        name: digest(ROOT / name) for name in names if name and (ROOT / name).is_file()
    }


def run_selected(slugs):
    plan = selected_plan(slugs)
    before = snapshot_unselected(slugs)
    for command in plan["commands"]:
        subprocess.run(command, cwd=ROOT, check=True)
    if before != snapshot_unselected(slugs):
        raise ValueError(
            "selected-city build changed an unselected city; review required"
        )
    return plan

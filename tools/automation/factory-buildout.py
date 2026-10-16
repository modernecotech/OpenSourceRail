#!/usr/bin/env python3
"""Publish/check the mechanical and civil development handover; no physics runs."""

from __future__ import annotations
import argparse
import csv
import html
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.design_engine.publication import digest
from engineering.design_engine.factory_review import verify_snapshot

BASIS = ROOT / "engineering/design_engine/data/factory-delivery.json"


def safe(relative):
    p = ROOT / relative
    if (
        Path(relative).is_absolute()
        or ".." in Path(relative).parts
        or p.is_symlink()
        or not p.is_file()
        or not p.resolve().is_relative_to(ROOT)
    ):
        raise ValueError("missing or unsafe handover artifact: " + relative)
    return p


def evidence(current):
    basis = json.loads(BASIS.read_text())
    if (
        basis["schema"] != "osr-factory-development-delivery/1"
        or basis["physical_release"] is not False
        or [r["id"] for r in basis["stages"]] != [1, 2, 3, 4, 5]
        or len(basis["open_work"]) != 7
    ):
        raise ValueError("development scope or required open engineering gates differ")
    snapshots = {
        name: verify_snapshot(
            ROOT / "docs/design-engine" / name,
            current=current and name == "factory-whole-bed",
        )
        for name in ["factory-support", "factory-stages", "factory-whole-bed"]
    }
    native = json.loads(
        (ROOT / "docs/design-engine/factory-whole-bed/native-cad.json").read_text()
    )
    if (
        native["part_count"] != 376
        or native["fcstd_reopened"] is not True
        or native["step_reopened"] is not True
    ):
        raise ValueError("complete nominal whole-bed native evidence required")
    original = ROOT / "engineering/factory_examples/examples"
    original_seal = json.loads((original / "reproduction.json").read_text())
    for name, sha in original_seal["retained_files_sha256"].items():
        p = original / name
        if (
            not p.resolve().is_relative_to(original)
            or p.is_symlink()
            or digest(p) != sha
        ):
            raise ValueError("original factory evidence differs: " + name)
    names = sorted(set(p for stage in basis["stages"] for p in stage["files"]))
    hashes = {p: digest(safe(p)) for p in names}
    with safe(
        "docs/commercial/baghdad-uk-factory-suppliers-2026-10-15.csv"
    ).open() as stream:
        cases = list(csv.DictReader(stream))
    if len(cases) != 37 or any(
        c["contacted"] != "false" or c["compatibility_accepted"] != "false"
        for c in cases
    ):
        raise ValueError(
            "supplier investigation boundary changed; review handover scope"
        )
    return dict(
        schema="osr-factory-buildout-handover/1",
        scope=basis["scope"],
        development_review_package_complete=True,
        engineering_design_complete=False,
        stage_6_qualification_complete=False,
        physical_release=False,
        independent_acceptance=False,
        stages=basis["stages"],
        open_work=basis["open_work"],
        broad_supplier_cases=len(cases),
        original_native_models=9,
        whole_bed_native_objects=376,
        evidence_sha256=hashes,
        snapshots=snapshots,
        publisher_sources_sha256={
            p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__), BASIS]
        },
        numerical_recomputation_performed=False,
    )


def publish(folder):
    folder = Path(folder)
    if folder.exists():
        raise ValueError("handover snapshots are immutable; use a fresh output")
    record = evidence(True)
    folder.mkdir(parents=True)
    e = html.escape

    def link(name, label=None):
        return (
            '<a href="'
            + e(os.path.relpath(ROOT / name, folder))
            + '">'
            + e(label or name)
            + "</a>"
        )

    stages = "".join(
        "<section><h2>"
        + e(str(s["id"]) + ". " + s["title"])
        + "</h2><p>Development artifacts complete for review.</p><ul>"
        + "".join("<li>" + link(p) + "</li>" for p in s["files"])
        + "</ul></section>"
        for s in record["stages"]
    )
    gates = "".join(
        "<tr><td>"
        + e(r["id"])
        + "</td><td>"
        + e(r["kind"])
        + "</td><td>"
        + e(r["required"])
        + "</td></tr>"
        for r in record["open_work"]
    )
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Baghdad mechanical and civil factory buildout</title><style>body{font:16px/1.55 system-ui;max-width:1120px;margin:auto;padding:24px;background:#f4f7f7;color:#173d47}h1{line-height:1.15}a{color:#086071;overflow-wrap:anywhere}section{background:white;padding:18px;margin:16px 0;border-left:4px solid #246f71}table{width:100%;border-collapse:collapse}td,th{vertical-align:top;text-align:left;padding:10px;border-bottom:1px solid #bccccc;overflow-wrap:anywhere}.table{overflow:auto}.intro{font-size:1.15em}</style><h1>Baghdad mechanical and civil factory buildout</h1><p class="intro">Stages 1–5 of the representative development package are complete for review. Engineering design and stage 6 qualification remain open. No manufacturing, construction or production release is granted.</p><p>'
        + link(
            "docs/design-engine/factory-whole-bed/index.html",
            "Whole-bed CAD and engineering review",
        )
        + " · "
        + link(
            "engineering/factory_examples/examples/index.html",
            "Both factory layouts and original tooling",
        )
        + " · "
        + link(
            "docs/commercial/baghdad-uk-factory-suppliers-2026-10-15.md",
            "37 British-priority supplier cases",
        )
        + "</p>"
        + stages
        + '<h2>Required engineering and external evidence</h2><p>These seven work groups remain open. Some require further engineering analysis; others require owner, supplier, site, laboratory or independent reviewer evidence. They are not software passes.</p><div class="table"><table><thead><tr><th>Work group</th><th>Required participation</th><th>Remaining work</th></tr></thead><tbody>'
        + gates
        + "</tbody></table></div><p>"
        + link(
            "docs/design-engine/factory-completion-2026-10-16.md",
            "Delivery and qualification record",
        )
        + ' · <a href="handover.json">Integrity and scope record</a></p></html>\n'
    )
    (folder / "index.html").write_text(page)
    record["index_sha256"] = digest(folder / "index.html")
    (folder / "handover.json").write_text(json.dumps(record, indent=2) + "\n")
    return verify(folder, current=True)


def verify(folder, *, current=False):
    folder = Path(folder)
    record = json.loads((folder / "handover.json").read_text())
    if {p.name for p in folder.iterdir()} != {"handover.json", "index.html"} or any(
        p.is_symlink() for p in folder.iterdir()
    ):
        raise ValueError("handover artifact membership differs")
    if (
        record.get("schema") != "osr-factory-buildout-handover/1"
        or record.get("development_review_package_complete") is not True
        or any(
            record.get(k) is not False
            for k in [
                "engineering_design_complete",
                "stage_6_qualification_complete",
                "physical_release",
                "independent_acceptance",
            ]
        )
    ):
        raise ValueError("handover cannot grant engineering or physical acceptance")
    if digest(folder / "index.html") != record["index_sha256"]:
        raise ValueError("handover index integrity differs")
    for name, sha in record["evidence_sha256"].items():
        if digest(safe(name)) != sha:
            raise ValueError("handover evidence integrity differs: " + name)
    if current:
        now = evidence(True)
        if {k: v for k, v in record.items() if k != "index_sha256"} != now:
            raise ValueError("handover sources/scope no longer current")
    return dict(
        integrity_verified=True,
        current_sources_checked=current,
        development_review_package_complete=True,
        engineering_design_complete=False,
        physical_release=False,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--check", action="store_true")
    p.add_argument("--current", action="store_true")
    args = p.parse_args()
    print(
        json.dumps(
            (
                verify(args.output, current=args.current)
                if args.check
                else publish(args.output)
            ),
            indent=2,
        )
    )

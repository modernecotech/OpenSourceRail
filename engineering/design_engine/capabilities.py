"""Capability/source inventory and migration parity for retained entry points."""

from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tomllib

from .registry import ROOT, problems
from .contracts import fingerprint


def _tests(path, test_paths):
    stem = path.stem.replace("-", "_").replace("check_", "").replace("verify_", "")
    return [name for name in test_paths if Path(name).name.startswith("test_" + stem)]


def build():
    tracked = set(
        subprocess.check_output(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT,
        )
        .decode()
        .split("\0")
    )
    test_paths = sorted(
        name
        for name in tracked
        if Path(name).name.startswith("test_") and name.endswith(".py")
    )
    ledger = []

    def add(
        identifier,
        kind,
        owner,
        source,
        entry,
        contract,
        tests,
        example,
        *,
        status="implemented",
        boundary=None,
    ):
        ledger.append(
            dict(
                id=identifier,
                kind=kind,
                owner_role=owner,
                appointed_person=None,
                source=source,
                entry=entry,
                contract=contract,
                tests=tests,
                example=example,
                status=status,
                authority_boundary=boundary
                or "owner scope retained; numerical and physical acceptance remain separate",
            )
        )

    modules = json.loads((ROOT / "docs/workbench/modules.json").read_text())
    for row in modules["modules"]:
        add(
            "ui:" + row["id"],
            "workbench-route",
            row["service"] + " interface maintainer",
            "docs/workbench/modules.json",
            row["path"],
            "docs/workbench/context-contract.schema.json",
            ["tests/frontend"],
            row["path"],
            boundary="navigation context cannot grant native authentication, engineering acceptance or railway command",
        )
    cargo = tomllib.loads((ROOT / "Cargo.toml").read_text())
    for member in cargo["workspace"]["members"]:
        manifest = ROOT / member / "Cargo.toml"
        if not manifest.is_file():
            continue
        data = tomllib.loads(manifest.read_text())
        name = data["package"]["name"]
        source = member + "/src"
        add(
            "rust:" + name,
            "rust-crate",
            "railway domain maintainer",
            member + "/Cargo.toml",
            "cargo test -p " + name,
            source,
            ["cargo test -p " + name],
            (
                member + "/README.md"
                if (ROOT / member / "README.md").is_file()
                else source
            ),
        )
    for name in sorted(tracked):
        path = ROOT / name
        if (
            not name.startswith("tools/automation/")
            or path.parent != ROOT / "tools/automation"
            or not path.is_file()
            or path.suffix not in {".py", ".sh", ".mjs"}
        ):
            continue
        text = path.read_text()
        doc = ""
        public = []
        cli = path.suffix != ".py"
        if path.suffix == ".py":
            try:
                tree = ast.parse(text)
                doc = ast.get_docstring(tree) or ""
                public = [
                    n.name
                    for n in tree.body
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                    and not n.name.startswith("_")
                ]
                cli = "ArgumentParser" in text or any(n == "main" for n in public)
            except SyntaxError:
                doc = "unparsed source; review required"
        add(
            "tool:" + path.name,
            "local-cli" if cli else "python-library",
            "automation/domain maintainer",
            name,
            (
                "tools/automation/osr-python " + name + " --help"
                if "ArgumentParser" in text and path.suffix == ".py"
                else name
            ),
            dict(public_symbols=public, description=doc),
            _tests(path, test_paths),
            name,
            status=(
                "implemented; focused test mapping pending"
                if not _tests(path, test_paths)
                else "implemented"
            ),
        )
    for identifier, charter in problems().items():
        add(
            "design:" + identifier,
            "design-adapter",
            "design and discipline maintainer",
            "engineering/design_engine/registry.py",
            "./osr design run --problem " + identifier + " --city samawah",
            charter,
            ["engineering/analysis/tests/test_design_engine.py"],
            "engineering/design_engine/README.md",
        )
    for name in ("erpnext", "supervision", "example-city"):
        add(
            "service:" + name,
            "deployment-service",
            name + " maintainer",
            "deployment/" + name + "/README.md",
            "./osr " + ("erp" if name == "erpnext" else "example-city legacy" if name == "example-city" else name),
            "deployment/" + name + "/README.md",
            ["deployment/" + name + "/tests"],
            "deployment/" + name + "/README.md",
            boundary="native record ownership and authentication remain separate",
        )
    previous = json.loads(
        subprocess.check_output(
            ["git", "show", "17e168fe5c:docs/workbench/modules.json"], cwd=ROOT
        )
    )
    old = {m["id"]: m for m in previous["modules"]}
    new = {m["id"]: m for m in modules["modules"]}
    missing = sorted(old.keys() - new.keys())
    changed = [
        identifier
        for identifier, row in old.items()
        if identifier in new
        and any(row[k] != new[identifier][k] for k in ("path", "service"))
    ]
    if missing or changed:
        raise ValueError("unexplained capability/route loss: " + str(missing + changed))
    source_index = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in sorted(tracked)
        if name
        and (ROOT / name).is_file()
        and not name.startswith("cities/")
        and name.endswith((".py", ".rs", ".toml", ".js", ".mjs", ".sh"))
    }
    return dict(
        schema="osr-capability-ledger/1",
        capabilities=ledger,
        inventory=dict(
            rust_crates=sum(r["kind"] == "rust-crate" for r in ledger),
            automation_entries=sum(
                r["kind"] in {"local-cli", "python-library"} for r in ledger
            ),
            workbench_routes=len(modules["modules"]),
            retained_prior_routes=len(old),
            task_areas=modules["task_areas"],
        ),
        migration=dict(
            baseline="17e168fe5c",
            missing=[],
            changed_native_or_deep_link_paths=[],
            no_unexplained_route_loss=True,
            test_mapping_is_not_a_full_functional_acceptance=True,
        ),
        source_index=source_index,
        source_index_sha256=fingerprint(source_index),
        physical_release=False,
    )


def render(data):
    lines = [
        "# Capability and source directory",
        "",
        "Generated by `./osr capabilities`; owner roles are responsibilities, not invented appointments.",
        "",
        "All 25 previous Workbench routes are retained under six task areas. Native authentication and record ownership remain separate.",
        "",
        "A source inventory proves retained entry points, not coverage or physical acceptance. Unmapped focused tests remain visible.",
        "",
        "| Capability | Owner role | Source / contract | Entry | Status |",
        "|---|---|---|---|---|",
    ]
    for row in data["capabilities"]:
        lines.append(
            "| "
            + row["id"]
            + " | "
            + row["owner_role"]
            + " | `"
            + row["source"]
            + "` | `"
            + row["entry"]
            + "` | "
            + row["status"]
            + " |"
        )
    return "\n".join(lines) + "\n"

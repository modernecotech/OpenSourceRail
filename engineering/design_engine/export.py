"""Source-bound offline review, BOM, RFQ and verification packages."""

from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from .contracts import canonical
from .publication import digest
from .registry import ROOT, dependencies
from .runtime import comparison, toolchain


def export(store, identifier, destination, *, native=False):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("review exports are immutable; use a fresh output directory")
    job = store.verify_request(identifier)
    req = job["request"]
    adapter = req["problem"]["adapter"]
    if req["dependencies"] != dependencies(adapter) or req["toolchain"] != toolchain(
        adapter
    ):
        raise ValueError("stale candidate cannot be exported as current")
    report = comparison(store, identifier)
    attempt = store.root / "runs" / identifier / f'attempt-{job["active_attempt"]:04d}'
    destination.mkdir(parents=True)
    shutil.copytree(attempt, destination / "executed-attempt")
    (destination / "request.json").write_bytes(canonical(req) + b"\n")
    source_root = destination / "sources"
    for name, expected in req["dependencies"].items():
        source = ROOT / name
        if digest(source) != expected:
            raise ValueError("source changed during review export")
        target = source_root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    package_sources = {}
    for source in [
        Path(__file__),
        Path(__file__).with_name("native_cad.py"),
        Path(__file__).with_name("delivery.py"),
    ]:
        name = source.relative_to(ROOT).as_posix()
        package_sources[name] = digest(source)
        target = source_root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    names = [
        "LICENSE.md",
        *[
            p.relative_to(ROOT).as_posix()
            for p in (ROOT / "LICENSES").rglob("*")
            if p.is_file()
        ],
    ]
    for name in names:
        source = ROOT / name
        if source.is_file():
            target = source_root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    with (destination / "bill-of-materials.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "candidate",
                "part_id",
                "material",
                "revision",
                "defined_mass_kg",
                "installed_kit_complete",
                "production_released",
            ]
        )
        for candidate in report["candidates"]:
            for part in (
                candidate.get("definition", {}).get("contract", {}).get("parts", [])
            ):
                writer.writerow(
                    [
                        candidate["id"],
                        part["id"],
                        part["material"],
                        part["revision"],
                        part["properties"]["mass_kg"],
                        "false",
                        "false",
                    ]
                )
    with (destination / "verification-matrix.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["candidate", "check", "state", "basis", "observables"])
        for candidate in report["candidates"]:
            for name, row in candidate["checks"].items():
                writer.writerow(
                    [
                        candidate["id"],
                        name,
                        row["state"],
                        row["basis"],
                        json.dumps(
                            {
                                k: v
                                for k, v in row.items()
                                if k not in {"state", "basis"}
                            },
                            sort_keys=True,
                        ),
                    ]
                )
    (destination / "supplier-rfq.json").write_bytes(
        canonical(
            dict(
                schema="osr-design-rfq/1",
                job=identifier,
                identity=req["identity"],
                candidate_ids=[r["id"] for r in report["candidates"]],
                required_scopes=[
                    "material/grade/batch",
                    "complete supports/joints/retention/seals",
                    "tooling",
                    "inspection/rejects",
                    "transport/lift/site installation",
                    "replacement/spares/maintenance",
                    "rights/local supply",
                ],
                quotations=[],
                binding_commitment=False,
                physical_release=False,
            )
        )
        + b"\n"
    )
    (destination / "README.md").write_text(
        "# Design review package\n\n"
        "Execution "
        + identifier
        + ". Scope: "
        + req["problem"]["applicability"]["function"]
        + ".\n\n"
        "Original failed/unknown/not-run checks remain in the verification matrix. Defined component mass does not close the installed kit. "
        "The RFQ has no assumed price or supplier commitment. Drawings are unissued; physical tests and independent decisions remain separate.\n\n"
        "Original attempt and source bytes are retained for offline review. Native solver histories keep their original domain schema.\n"
    )
    native_results = []
    if native:
        from .native_cad import generate

        selected = set(report["conditional_shortlist"])
        if len(report["candidates"]) == 1:
            selected = {report["candidates"][0]["id"]}
        for candidate in report["candidates"]:
            if candidate["id"] not in selected:
                native_results.append(
                    dict(
                        candidate=candidate["id"],
                        state="not-run",
                        basis="outside the bounded confirmation shortlist",
                    )
                )
                continue
            contract = candidate.get("definition", {}).get("contract")
            if not contract:
                native_results.append(
                    dict(
                        candidate=candidate["id"],
                        state="not-run",
                        basis="no manufacturing representation contract in this adapter",
                    )
                )
                continue
            inputs = destination / "native-inputs" / (candidate["id"] + ".json")
            inputs.parent.mkdir(parents=True, exist_ok=True)
            inputs.write_bytes(canonical(contract) + b"\n")
            try:
                result = generate(inputs, destination / "cad" / candidate["id"], ROOT)
                record = dict(
                    candidate=candidate["id"],
                    state="numerically-verified",
                    native_correspondence=result,
                    drawing_issued=False,
                )
                if any(p["id"] == "deck" for p in contract["parts"]):
                    from engineering.design_consistency.ifc import export as export_ifc

                    record["bim_correspondence"] = export_ifc(
                        contract,
                        destination / "cad" / candidate["id"] / "candidate.ifc",
                    )
                native_results.append(record)
            except (
                ValueError,
                RuntimeError,
                OSError,
                subprocess.SubprocessError,
            ) as error:
                native_results.append(
                    dict(
                        candidate=candidate["id"],
                        state="failed",
                        basis=str(error),
                        physical_release=False,
                    )
                )
        (destination / "native-export.json").write_bytes(
            canonical(
                dict(
                    schema="osr-native-review-exports/1",
                    results=native_results,
                    physical_release=False,
                )
            )
            + b"\n"
        )
    if req["dependencies"] != dependencies(adapter) or req["toolchain"] != toolchain(
        adapter
    ):
        raise ValueError(
            "source/toolchain changed during review export; unsealed output retained"
        )
    if any(
        digest(ROOT / name) != expected for name, expected in package_sources.items()
    ):
        raise ValueError(
            "package generator changed during export; unsealed output retained"
        )
    files = {
        p.relative_to(destination).as_posix(): digest(p)
        for p in sorted(destination.rglob("*"))
        if p.is_file()
    }
    manifest = dict(
        schema="osr-design-export/1",
        job=identifier,
        identity=req["identity"],
        files=files,
        licence_source="sources/LICENSE.md",
        baseline_overwrite_permitted=False,
        physical_release=False,
        independently_accepted=False,
        native_exports=native_results,
        package_source_sha256=package_sources,
    )
    (destination / "manifest.json").write_bytes(canonical(manifest) + b"\n")
    return manifest


def verify_export(folder):
    folder = Path(folder).resolve()
    manifest = json.loads((folder / "manifest.json").read_text())
    if (
        manifest.get("schema") != "osr-design-export/1"
        or manifest.get("physical_release") is not False
    ):
        raise ValueError("invalid review package")
    for name, expected in manifest["files"].items():
        path = folder / name
        if (
            path.is_symlink()
            or ".." in Path(name).parts
            or not path.resolve().is_relative_to(folder)
            or digest(path) != expected
        ):
            raise ValueError("unsafe or changed review export: " + name)
    actual = {
        p.relative_to(folder).as_posix()
        for p in folder.rglob("*")
        if p.is_file() and p != folder / "manifest.json"
    }
    if actual != set(manifest["files"]):
        raise ValueError("review export membership changed")
    return manifest

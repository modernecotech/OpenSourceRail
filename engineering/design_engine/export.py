"""Source-bound offline review, BOM, RFQ and verification packages."""

from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from .contracts import canonical
from .bom import review_bill
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
    bills = [
        review_bill(candidate, adapter=adapter) for candidate in report["candidates"]
    ]
    attempt = store.root / "runs" / identifier / f'attempt-{job["active_attempt"]:04d}'
    destination.mkdir(parents=True)
    shutil.copytree(attempt, destination / "executed-attempt")
    (destination / "request.json").write_bytes(canonical(req) + b"\n")
    reviewed_input_sources = []
    input_source_checks = []
    if req.get("reviewed_inputs"):
        from .input_revisions import InputRevisions

        input_revisions = InputRevisions(store)
        for folder in input_revisions.source_directories(req):
            source_files = {}
            for path in sorted(folder.rglob("*")):
                if path.is_symlink() or not path.resolve().is_relative_to(
                    folder.resolve()
                ):
                    raise ValueError("unsafe reviewed input source export")
                if path.is_file():
                    source_files[path.relative_to(folder).as_posix()] = digest(path)
            target = destination / "reviewed-inputs" / folder.name
            shutil.copytree(folder, target)
            if any(
                digest(target / name) != expected
                for name, expected in source_files.items()
            ):
                raise ValueError("reviewed input sources changed during export")
            input_source_checks.append((folder, source_files))
            reviewed_input_sources.append(
                dict(
                    input_revision=folder.name,
                    path=target.relative_to(destination).as_posix(),
                    files=source_files,
                )
            )
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
        Path(__file__).with_name("bom.py"),
        Path(__file__).with_name("native_cad.py"),
        Path(__file__).with_name("delivery.py"),
        Path(__file__).with_name("panel_assembly.py"),
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
                "physical_id",
                "part_id",
                "quantity",
                "unit",
                "material",
                "revision",
                "defined_mass_kg",
                "cg_m",
                "inertia_tensor_kg_m2",
                "property_frame",
                "property_units",
                "inertia_reference",
                "placement",
                "installed_kit_complete",
                "production_released",
            ]
        )
        for bill in bills:
            for part in bill["parts"]:
                writer.writerow(
                    [
                        bill["candidate"],
                        part["physical_id"],
                        part["part_id"],
                        part["quantity"],
                        part["unit"],
                        part["material"],
                        part["revision"],
                        part["defined_mass_kg"],
                        json.dumps(part["cg_m"]),
                        json.dumps(part["inertia_tensor_kg_m2"]),
                        part["property_frame"],
                        json.dumps(part["property_units"], sort_keys=True),
                        part["inertia_reference"],
                        json.dumps(part["placement"], sort_keys=True),
                        "false",
                        "false",
                    ]
                )
    (destination / "bill-of-materials.json").write_bytes(
        canonical(
            dict(schema="osr-design-bill/1", candidates=bills, physical_release=False)
        )
        + b"\n"
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
        "Original failed/unknown/not-run checks remain in the verification matrix. The BOM uses reconciled per-instance installed-register quantities; its JSON retains unknown values, catalogue counts and unresolved allocations for each candidate. Defined component mass does not close the installed kit. "
        "The RFQ has no assumed price or supplier commitment. Drawings are unissued; physical tests and independent decisions remain separate.\n\n"
        "Original attempt and source bytes are retained for offline review. Native solver histories keep their original domain schema.\n"
    )
    native_results = []
    if adapter == "panel":
        from .panel_assembly import write_packet

        for candidate in report["candidates"]:
            if candidate.get("definition", {}).get("contract"):
                write_packet(candidate, destination / "panel-assemblies" / candidate["id"])
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
            generated = candidate.get("definition", {}).get("native_confirmation")
            if adapter in {"mechanical-cleat", "civil-steel-beam"} and generated:
                native_results.append(dict(
                    candidate=candidate["id"], state="retained-native-execution",
                    basis="Original CAD, meshes and solver results retained in executed-attempt; no export-time solve",
                    native_correspondence=generated,
                    drawing_issued=False, physical_release=False))
                continue
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
    if req.get("reviewed_inputs"):
        current_folders = input_revisions.source_directories(req)
        if current_folders != [folder for folder, _ in input_source_checks]:
            raise ValueError("reviewed input ancestry changed during export")
        for folder, expected in input_source_checks:
            paths = list(folder.rglob("*"))
            if (
                any(path.is_symlink() for path in paths)
                or {
                    path.relative_to(folder).as_posix(): digest(path)
                    for path in paths
                    if path.is_file()
                }
                != expected
            ):
                raise ValueError(
                    "reviewed input sources changed during export; unsealed output retained"
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
        reviewed_input_sources=reviewed_input_sources,
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

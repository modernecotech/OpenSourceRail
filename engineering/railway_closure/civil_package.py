"""Build compact, source-bound civil proof archives from final-trial runs."""
from __future__ import annotations

import argparse
import gzip
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
import tempfile

from engineering.station_rail.common import digest, encoded, identity
from engineering.pilot_civil.design import validate_train
from engineering.pilot_civil.native_trial import source_context

from . import ROOT, civil_reference


FLAGS = dict(
    physical_accepted=False,
    engineering_accepted=False,
    manufacturing_release=False,
    operating_release=False,
    selected_reference_changed=False,
    movement_authority=False,
)


def _sealed(value, key="evaluation_id"):
    if value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError(f"Civil trial record seal differs: {key}")
    return value


def _sha(path: Path) -> str:
    return digest(path)


def _omission_reason(name: str) -> str | None:
    p = PurePosixPath(name)
    parts = p.parts
    if "__pycache__" in parts or p.suffix == ".pyc":
        return "Interpreter cache; source and measured outputs are retained."
    if len(parts) >= 3 and parts[0].startswith("case-") and parts[1] == "fieldcraft":
        if p.name.startswith("rolling-") or p.suffix == ".bak" or p.suffix == ".fieldcraft":
            return "Replaceable rolling FieldCraft checkpoint; final commands and results are retained."
    if len(parts) == 3 and parts[0].startswith("case-") and parts[1] == "mesh-native" and p.name in ("imported.json", "imported.msh"):
        return "Intermediate mesh export; the sealed canonical mesh.json is retained."
    if len(parts) == 2 and parts[0].startswith("case-") and p.name == "input.step":
        return "Duplicate of the hash-bound gross-beam CAD STEP retained once."
    return None


def _load_trial(run: Path, root: Path):
    run = run.resolve()
    root = root.resolve()
    if not run.is_dir() or run.is_symlink():
        raise ValueError("Ordinary completed final-trial directory required")
    run_manifest = _sealed(json.loads((run / "manifest.json").read_bytes()))
    for name, spec in run_manifest["files"].items():
        path = run / name
        if not path.is_file() or path.is_symlink() or path.stat().st_size != spec["bytes"] or _sha(path) != spec["sha256"]:
            raise ValueError("Final-trial member differs from its manifest: " + name)
    train = _sealed(json.loads((run / "axle-input.json").read_bytes()))
    validate_train(train, root)
    civil = _sealed(json.loads((run / "civil.json").read_bytes()))
    native = _sealed(json.loads((run / "native-input.json").read_bytes()), "input_id")
    report = _sealed(json.loads((run / "report.json").read_bytes()))
    before = json.loads((run / "source-before.json").read_bytes())
    after = json.loads((run / "source-after.json").read_bytes())
    upstream_after = json.loads((run / "upstream-source-after.json").read_bytes())
    if before != after or before != source_context(root):
        raise ValueError("Numerical source epoch differs from the current checkout")
    if train["source_sha256"] != upstream_after:
        raise ValueError("Upstream source changed during the final trial")
    if not report["source_unchanged"] or not report["upstream_source_unchanged"]:
        raise ValueError("Final trial reports source drift")
    if not report["refinement_screen_passed"] or len(report["results"]) != 3:
        raise ValueError("A passing three-mesh refinement result is required")
    if any(report.get(flag) is not False for flag in FLAGS):
        raise ValueError("Civil numerical evidence cannot grant release or acceptance")
    if not (report["system_candidate_id"] == train["candidate_id"] == civil["system_candidate_id"] == native["system_candidate_id"]):
        raise ValueError("Mixed civil system candidate IDs")
    if not (report["civil_evaluation_id"] == civil["evaluation_id"] and report["input_load_evaluation_id"] == train["evaluation_id"] == native["input_load_evaluation_id"] == civil["input_load_evaluation_id"]):
        raise ValueError("Mixed civil or load evaluation IDs")
    if report["native_input_id"] != native["input_id"]:
        raise ValueError("Native input identity differs")
    return run, root, run_manifest, train, civil, native, report, before


def _archive_sources(root: Path, before: dict, upstream: dict):
    values = {}
    for group, mapping in (("numerical", before), ("upstream", upstream)):
        for name, wanted in sorted(mapping.items()):
            rel = PurePosixPath(name)
            if rel.is_absolute() or ".." in rel.parts:
                raise ValueError("Source manifest contains an unsafe relative path")
            path = root.joinpath(*rel.parts)
            if not path.is_file() or path.is_symlink() or _sha(path) != wanted:
                raise ValueError("Source file differs from its run identity: " + name)
            values[f"source/{group}/{name}"] = path
    return values


def _stable_tar(archive_path: Path, members: dict[str, Path]):
    tmp = archive_path.with_name(archive_path.name + ".partial")
    if tmp.exists() or archive_path.exists():
        raise ValueError("Immutable archive destination already exists")
    try:
        with tmp.open("xb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=6) as zipped:
            with tarfile.open(fileobj=zipped, mode="w|", format=tarfile.PAX_FORMAT) as tar:
                for name in sorted(members):
                    path = members[name]
                    info = tarfile.TarInfo(name)
                    info.size = path.stat().st_size
                    info.mode = 0o644
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = 0
                    with path.open("rb") as stream:
                        tar.addfile(info, stream)
        os.replace(tmp, archive_path)
    except BaseException:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise


def package_trial(run, output, *, root=ROOT, manifest_name=None, archive_name=None):
    """Package a passing final trial without changing its immutable source run."""
    run, root, run_manifest, train, civil, native, report, before = _load_trial(Path(run), Path(root))
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    report_id = report["evaluation_id"]
    stem = f"civil-native-current-{report_id[:12]}"
    manifest_name = manifest_name or f"{stem}.json"
    archive_name = archive_name or f"{stem}.tar.gz"
    if Path(manifest_name).name != manifest_name or Path(archive_name).name != archive_name:
        raise ValueError("Ordinary archive and manifest names required")

    with tempfile.TemporaryDirectory(prefix="osr-civil-package-") as temp:
        generated = Path(temp)
        source_members = _archive_sources(root, before, train["source_sha256"])
        members: dict[str, Path] = {}
        omissions = []
        for path in sorted(run.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(run).as_posix()
            if rel == "manifest.json":
                target = generated / "full-private-manifest.json"
                target.write_bytes(path.read_bytes())
                members["full-private-manifest.json"] = target
                continue
            reason = _omission_reason(rel)
            if reason:
                omissions.append(dict(path=rel, bytes=path.stat().st_size, sha256=_sha(path), reason=reason))
                continue
            members[rel] = path
        members.update(source_members)
        members["package-builder.py"] = Path(__file__).resolve()

        omissions_path = generated / "omissions.json"
        omissions_path.write_bytes(encoded(dict(schema="osr-civil-proof-omissions/1", entries=omissions)))
        members["omissions.json"] = omissions_path

        prior_path = root / civil_reference.FOLDER / civil_reference.MANIFEST
        prior_id = None
        if prior_path.is_file():
            prior = json.loads(prior_path.read_bytes())
            prior_id = prior.get("report_evaluation_id")
        readme = (
            "OpenSourceRail source-bound final-load civil comparison\n\n"
            "Run `python verify.py` after extracting this archive into a fresh directory. "
            "The verifier checks member hashes, candidate and load identities, source snapshots, "
            "CAD volume, solver equilibrium, support-line reactions, resource records and mesh refinement.\n\n"
            "This is a gross elastic numerical comparison for one normal-base load pose. It does not "
            "qualify bearing contact or compliance, joints, reinforcement, prestress, cracking, fatigue, "
            "soil, construction, or physical acceptance. All release and acceptance flags remain false.\n\n"
            "Replaceable rolling checkpoints, intermediate mesh exports, bytecode and duplicate STEP "
            "copies are listed with hashes in omissions.json. The full private-run manifest is retained.\n"
        )
        readme_path = generated / "proof-readme.txt"
        readme_path.write_text(readme)
        members["proof-readme.txt"] = readme_path

        # Preserve the independent, standard-library audit that accompanied the
        # earlier proof; its paths and checks are candidate agnostic.
        with tarfile.open(root / civil_reference.FOLDER / civil_reference.MANIFEST.replace(".json", ".tar.gz"), "r:gz") as old:
            verify_member = old.extractfile("verify.py")
            if verify_member is None:
                raise ValueError("Prior proof's independent verifier is missing")
            verifier_path = generated / "verify.py"
            verifier_path.write_bytes(verify_member.read())
        members["verify.py"] = verifier_path

        compact = {}
        for name, path in sorted(members.items()):
            compact[name] = dict(bytes=path.stat().st_size, sha256=_sha(path))
        compact_path = generated / "compact-members.json"
        compact_value = dict(schema="osr-civil-proof-members/1", members=compact)
        compact_value["evaluation_id"] = identity(compact_value)
        compact_path.write_bytes(encoded(compact_value))
        members["compact-members.json"] = compact_path

        archive_path = output / archive_name
        _stable_tar(archive_path, members)
        outer_members = {name: dict(bytes=path.stat().st_size, sha256=_sha(path)) for name, path in members.items()}
        manifest = dict(
            schema="osr-pilot-civil-native-proof/1",
            archive_file=archive_name,
            archive_bytes=archive_path.stat().st_size,
            archive_sha256=_sha(archive_path),
            members=outer_members,
            system_candidate_id=train["candidate_id"],
            vehicle_candidate_id=train["vehicle_candidate_id"],
            mass_evaluation_id=train["mass_evaluation_id"],
            civil_candidate_id=civil["civil_candidate_id"],
            civil_evaluation_id=civil["evaluation_id"],
            input_load_evaluation_id=train["evaluation_id"],
            native_input_id=native["input_id"],
            report_file="report.json",
            report_evaluation_id=report_id,
            native_source_epoch_id=identity(before),
            source_commits=[subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()],
            prior_incompatible_report_id=prior_id,
            correction="Current source-bound axle and mass evaluation; explicit 1.435 m inner-face gauge, 70 mm nominal railheads and ±0.7525 m contact centres.",
            **FLAGS,
        )
        manifest["evaluation_id"] = identity(manifest)
        manifest_path = output / manifest_name
        if manifest_path.exists():
            raise ValueError("Immutable proof manifest destination already exists")
        manifest_path.write_bytes(encoded(manifest))

    civil_reference.verify(output, root=root, manifest_name=manifest_name)
    return dict(manifest_file=manifest_name, archive_file=archive_name,
                manifest_id=manifest["evaluation_id"], archive_bytes=manifest["archive_bytes"],
                report_id=report_id, verified=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(package_trial(args.run, args.output, root=args.root), indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exercise the compact Airport source installation exported from a named Git commit."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cities.Baghdad.airport_integration import same_packet
from engineering.performance import run_reserved_command

# These sources reproduce the Airport dossier and the independent v0.7 reference.
PATHS = (
    "VERSION", "LICENSE.md", "LICENSES", "osr", "Cargo.toml", "Cargo.lock", "rust-toolchain.toml",
    "package.json", "package-lock.json", "crates", "control-electronics", "cities/Baghdad",
    "cities/catalogue/west-asia/Iraq/Baghdad/map-context.json.gz", "docs/reference-v07",
    "docs/operator-review/delivery/calculate.py", "docs/operator-review/delivery/quantities.json",
    "docs/operator-review/finance", "docs/releases/v0.7.2", "docs/RELEASE-v0.7.md",
    "engineering/design_search/frame_analysis.py", "engineering/outline", "engineering/performance.py",
    "engineering/station_rail/__init__.py", "engineering/v07_reference_journey.py",
    "tools/automation/osr-python", "tools/automation/toolchain-release.sh",
)
MAX_SOURCE_BYTES = 96 * 1024**2


def verify(revision, output):
    directory = Path(tempfile.mkdtemp(prefix="v072-airport-", dir=output))
    listing = subprocess.check_output(["git", "ls-tree", "-rlz", revision, "--", *PATHS], cwd=ROOT)
    entries = [row for row in listing.split(b"\0") if row]
    size = sum(int(row.split(b"\t", 1)[0].split()[3]) for row in entries)
    if size > MAX_SOURCE_BYTES:
        raise ValueError("Airport source selection exceeds the compact installation budget")
    archive = directory / "OpenSourceRail-v0.7.2-Airport.tar.gz"
    name = "OpenSourceRail-v0.7.2-Airport"
    subprocess.run(["git", "archive", "--format=tar.gz", "--prefix=" + name + "/",
                    "-o", str(archive), revision, "--", *PATHS], cwd=ROOT, check=True)
    with tarfile.open(archive, "r:gz") as contents:
        for member in contents:
            if (not member.isfile() and not member.isdir()) or Path(member.name).parts[0] != name:
                raise ValueError("Unexpected source archive member")
        contents.extractall(directory, filter="data")
    source = directory / name
    if (source / "VERSION").read_text().strip() != "0.7.2":
        raise ValueError("Expected v0.7.2 source metadata")
    env = {**os.environ, "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
           "GIT_CEILING_DIRECTORIES": str(directory)}
    for var in ("VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME", "GIT_DIR", "GIT_WORK_TREE"):
        env.pop(var, None)
    commands = [
        [sys.executable, "-I", "-m", "venv", "--without-pip", ".venv"],
        ["./osr", "design", "railway", "airport", "--check"],
        ["./osr", "design", "railway", "airport", "--packet", "build/airport-supplier.zip"],
        ["./osr", "reference", "v07"],
        [".venv/bin/python", "-m", "cities.Baghdad.phased_finance", "--check"],
    ]
    for i, command in enumerate(commands):
        with (directory / f"command-{i+1}.log").open("wb") as log:
            run = subprocess.run(command, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT)
        if run.returncode:
            raise RuntimeError(f"Clean installation exited {run.returncode} at {command}. See {log.name}")
    dossier = source / "build/airport-supplier.zip"
    with ZipFile(dossier) as package:
        if not package.namelist() or package.testzip() is not None:
            raise ValueError("Invalid Airport dossier after installation")
        dossier_files = sorted(package.namelist())
        manifest = json.loads(package.read("manifest.json"))
        selection = json.loads(package.read("selection.json"))
        checksums = manifest["sha256"]
        if (set(checksums) != set(dossier_files) - {"manifest.json"}
                or any(sha256(package.read(item)).hexdigest() != expected for item, expected in checksums.items())
                or selection["selection_id"] != manifest["selection_id"]
                or selection["physical_candidate_id"] != manifest["candidate_id"]
                or selection["planning_configuration"] is not True or selection["physical_accepted"] is not False):
            raise ValueError("Dossier bytes, planning selection or physical evidence status differ")
        selected_id = selection["selection_id"]
        if (directory / "command-2.log").read_text().strip() != selected_id:
            raise ValueError("Exported dossier differs from the checked operating and cost sheets")
    published = source / "cities/Baghdad/airport-dossier.zip"
    if not same_packet(published, dossier):
        raise ValueError("Installed dossier differs from the committed downloadable packet")
    receipt = {"commit": revision, "source_bytes": size, "source_file_count": len(entries),
               "archive": archive.name, "archive_sha256": sha256(archive.read_bytes()).hexdigest(),
               "archive_bytes": archive.stat().st_size, "selection_id": selected_id,
               "dossier_sha256": sha256(published.read_bytes()).hexdigest(),
               "rebuilt_dossier_sha256": sha256(dossier.read_bytes()).hexdigest(), "dossier_files": dossier_files,
               "python": sys.version, "commands": commands}
    (directory / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(directory / "verification.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", default="HEAD")
    args = parser.parse_args()
    revision = subprocess.check_output(["git", "rev-parse", "--verify", "--end-of-options",
                                        args.revision + "^{commit}"], cwd=ROOT, text=True).strip()
    output = ROOT / "build"
    output.mkdir(exist_ok=True)
    # Keep the entire export, installation and packet run under the existing
    # disk monitor, including subprocesses started by the installation.
    child = [sys.executable, "-B", "-c",
             "import runpy,sys; m=runpy.run_path(sys.argv[1]); m['verify'](sys.argv[2],m['ROOT']/'build')",
             str(Path(__file__).resolve()), revision]
    receipt, code = run_reserved_command(ROOT, output, "v0.7.2 Airport clean source installation", 384 * 1024**2,
                                          child)
    print(receipt["receipt"])
    raise SystemExit(code)


if __name__ == "__main__":
    main()

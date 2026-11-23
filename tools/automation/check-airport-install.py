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
    "engineering/station_rail/__init__.py", "engineering/station_rail/common.py",
    "engineering/station_rail/vehicle.py", "engineering/station_rail/braking.py", "engineering/station_rail/civil.py",
    "engineering/station_rail/station_motor.py", "engineering/station_rail/long_motor.py",
    "engineering/design_search/requirement_policy.py", "engineering/design_search/remit.py",
    "engineering/design_search/design_grammar.py", "engineering/design_search/capabilities.py",
    "engineering/design_search/railway_architecture.py", "engineering/design_search/wheel_motor.py",
    "engineering/design_search/railway_bundle.py", "engineering/design_search/test_readiness.py",
    "engineering/railway_completion/__init__.py", "engineering/railway_completion/evidence.py",
    "engineering/v07_reference_journey.py",
    "tools/automation/osr-python", "tools/automation/toolchain-release.sh",
)
MAX_SOURCE_BYTES = 96 * 1024**2


def verify(revision, output):
    directory = Path(tempfile.mkdtemp(prefix="v072-airport-", dir=output))
    # Keep validating older release commits that predate the buyer workflow.
    has_sourcing = subprocess.run(
        ["git", "cat-file", "-e", revision + ":cities/Baghdad/engineering/prototype/sourcing.py"],
        cwd=ROOT, stderr=subprocess.DEVNULL,
    ).returncode == 0
    paths = list(PATHS)
    if has_sourcing:
        paths.extend(("deployment/erpnext/apps/osr_erpnext/osr_erpnext/sourcing_comparison.py",
                      "engineering/development-baseline.toml"))
    has_enquiries = subprocess.run(
        ["git", "cat-file", "-e", revision + ":cities/Baghdad/engineering/prototype/enquiries.py"],
        cwd=ROOT, stderr=subprocess.DEVNULL,
    ).returncode == 0
    if has_enquiries:
        paths.extend("docs/operator-review/delivery/" + name for name in
                     ("README.md", "precast-yard.svg", "vehicle-works.svg", "workforce.png"))
    listing = subprocess.check_output(["git", "ls-tree", "-rlz", revision, "--", *paths], cwd=ROOT)
    entries = [row for row in listing.split(b"\0") if row]
    size = sum(int(row.split(b"\t", 1)[0].split()[3]) for row in entries)
    if size > MAX_SOURCE_BYTES:
        raise ValueError("Airport source selection exceeds the compact installation budget")
    has_prototype = any(row.endswith(b"\tcities/Baghdad/engineering/prototype/review.py") for row in entries)
    name = "OpenSourceRail-Airport-" + revision[:12] if has_prototype else "OpenSourceRail-v0.7.2-Airport"
    archive = directory / (name + ".tar.gz")
    subprocess.run(["git", "archive", "--format=tar.gz", "--prefix=" + name + "/",
                    "-o", str(archive), revision, "--", *paths], cwd=ROOT, check=True)
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
    if has_prototype:
        commands.extend([
            ["./osr", "design", "railway", "prototype", "--check"],
            [".venv/bin/python", "-m", "cities.Baghdad.citywide_service", "--check"],
        ])
    workshop = "cities/Baghdad/engineering/prototype"
    if (source / workshop / "shop_costs.py").is_file():
        commands.extend([
            [".venv/bin/python", "-m", "cities.Baghdad.engineering.prototype.shop_costs", "--check"],
            [".venv/bin/python", workshop + "/cam/build.py", "--check"],
            [".venv/bin/python", "-m", "cities.Baghdad.engineering.prototype.infrastructure.bar_stock",
             "--stock-mm", "14000"],
        ])
    if has_sourcing:
        commands.extend([
            ["./osr", "design", "railway", "sourcing", "--check"],
            ["./osr", "design", "railway", "sourcing", "--demo"],
        ])
    if has_enquiries:
        commands.extend([
            ["./osr", "design", "railway", "sourcing", "--issue", "build/airport-enquiries.zip"],
            [".venv/bin/python", "cities/Baghdad/engineering/prototype/vehicle-factory/installed_ga.py", "--check"],
            [".venv/bin/python", "cities/Baghdad/engineering/prototype/vehicle-factory/body_bogie.py", "--check"],
            [".venv/bin/python", "cities/Baghdad/engineering/prototype/infrastructure/platform_sweep.py", "--check"],
        ])
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
    if has_enquiries:
        buyer_issue = source / "cities/Baghdad/engineering/prototype/airport-enquiries.zip"
        if not same_packet(buyer_issue, source / "build/airport-enquiries.zip"):
            raise ValueError("Installed first-article schedules differ from the downloadable buyer issue")
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

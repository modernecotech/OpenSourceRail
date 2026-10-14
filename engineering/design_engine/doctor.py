"""Named, read-only local toolchain preflight and dependency receipts."""

from __future__ import annotations
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys

from .contracts import canonical, fingerprint
from .registry import ROOT

PROFILES = {
    "minimal": dict(
        python=["pytest", "numpy", "scipy", "PyYAML"], commands=[["git", "--version"]]
    ),
    "browser": dict(
        python=["pytest"],
        commands=[
            ["node", "--version"],
            ["npx", "--no-install", "playwright", "--version"],
            ["cargo", "--version"],
            ["trunk", "--version"],
        ],
    ),
    "panel": dict(python=["numpy", "scipy", "matplotlib"], commands=[["ccx", "-v"]]),
    "civil": dict(
        python=["numpy", "scipy", "openseespy"],
        commands=[["ccx", "-v"], ["gmsh", "--version"]],
    ),
    "cad-bim": dict(
        python=["numpy", "ifcopenshell"],
        commands=[["flatpak", "info", "org.freecad.FreeCAD"]],
    ),
    "formal": dict(
        python=[], commands=[["cargo-kani", "--version"], ["java", "-version"]]
    ),
    "stack": dict(
        python=["pytest"],
        commands=[
            ["docker", "compose", "version"],
            ["node", "--version"],
            ["cargo", "--version"],
        ],
    ),
}


def inspect(profile):
    if profile not in PROFILES:
        raise ValueError("unknown named toolchain profile")
    policy = PROFILES[profile]
    rows = []
    for name in policy["python"]:
        try:
            version = importlib.metadata.version(name)
            state = "available"
        except importlib.metadata.PackageNotFoundError:
            version = None
            state = "unavailable"
        rows.append(
            dict(kind="python-package", name=name, state=state, version=version)
        )
    for command in policy["commands"]:
        binary = shutil.which(command[0])
        code = None
        text = "executable not found"
        if binary:
            try:
                result = subprocess.run(
                    command,
                    cwd=ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=20,
                )
                code = result.returncode
                text = result.stdout.strip()[:2000]
            except subprocess.TimeoutExpired:
                text = "native probe timed out"
            except OSError as error:
                text = str(error)
        state = "available" if code == 0 else "unavailable"
        # CalculiX's version-only mode uses 201 even for a valid installation.
        # Native solve jobs independently require zero exit and complete output.
        if (
            command[0] == "ccx"
            and code in (0, 201)
            and text.strip() == "This is Version 2.23"
        ):
            state = "available"
        if command[0] == "cargo-kani" and text != "cargo-kani 0.67.0":
            state = "unavailable"
        if command[0] == "node" and code == 0:
            try:
                if int(text.lstrip("v").split(".")[0]) < 22:
                    state = "unavailable"
            except ValueError:
                state = "unavailable"
        rows.append(
            dict(
                kind="native-tool",
                name=command[0],
                command=command,
                state=state,
                exit_code=code,
                version_or_diagnostic=text,
                binary_sha256=(
                    hashlib.sha256(Path(binary).read_bytes()).hexdigest()
                    if binary
                    else None
                ),
            )
        )
    if profile == "civil":
        command = [
            sys.executable,
            "-c",
            "import openseespy.opensees as ops; print(ops.version())",
        ]
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=20,
            )
            rows.append(
                dict(
                    kind="native-import",
                    name="OpenSees",
                    state="available" if result.returncode == 0 else "unavailable",
                    diagnostic=result.stdout[:2000],
                )
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            rows.append(
                dict(
                    kind="native-import",
                    name="OpenSees",
                    state="unavailable",
                    diagnostic=str(error),
                )
            )
    distributions = sorted(
        (d.metadata["Name"], d.version)
        for d in importlib.metadata.distributions()
        if d.metadata["Name"]
    )
    return dict(
        schema="osr-local-toolchain/1",
        profile=profile,
        python=sys.version.split()[0],
        checks=rows,
        available=all(r["state"] == "available" for r in rows),
        locked_python_environment=dict(distributions),
        profile_sha256=fingerprint(policy),
        physical_release=False,
        installation_performed=False,
    )


def write_receipt(profile, output):
    result = inspect(profile)
    output = Path(output)
    if output.exists():
        raise ValueError("toolchain receipts are immutable; choose a fresh directory")
    output.mkdir(parents=True)
    (output / "toolchain.json").write_bytes(canonical(result) + b"\n")
    (output / "python-lock.txt").write_text(
        "".join(
            name + "==" + version + "\n"
            for name, version in sorted(result["locked_python_environment"].items())
        )
    )
    return result

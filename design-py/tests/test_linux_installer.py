"""Keep the cross-distribution Linux entry point deterministic and discoverable."""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPO_ROOT / "install.sh"
LAUNCHER = REPO_ROOT / "scripts" / "osr"


def run_dry(family: str, *arguments: str) -> str:
    environment = os.environ.copy()
    environment["OSR_INSTALL_FAMILY"] = family
    environment["OSR_INSTALL_ARCH"] = "x86_64"
    result = subprocess.run(
        [str(INSTALLER), "--dry-run", "--no-build", *arguments],
        cwd=REPO_ROOT,
        env=environment,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "no changes were made" in result.stdout
    return result.stdout


def test_install_entry_points_are_executable_and_valid_bash() -> None:
    for path in (INSTALLER, LAUNCHER):
        assert path.stat().st_mode & stat.S_IXUSR
        subprocess.run(["bash", "-n", str(path)], check=True)


def test_debian_core_dry_run_is_complete() -> None:
    output = run_dry("debian")
    assert "apt-get update" in output
    assert "apt-get install" in output
    assert "Node.js 22.23.2" in output
    assert "Rust 1.88.0" in output
    assert "Python design environment" in output
    assert "npm ci" in output
    assert "playwright install --with-deps chromium" in output
    assert "flatpak install" not in output


def test_redhat_engineering_dry_run_includes_desktop_tools() -> None:
    output = run_dry("redhat", "--engineering")
    assert "dnf install" in output
    assert "playwright install chromium" in output
    for identifier in (
        "org.freecad.FreeCAD",
        "org.blender.Blender",
        "org.qgis.qgis",
        "org.cloudcompare.CloudCompare",
        "org.eclipse.sumo",
        "bonsai",
        "python-requirements.txt",
    ):
        assert identifier in output


def test_aarch64_uses_native_archives() -> None:
    environment = os.environ.copy()
    environment["OSR_INSTALL_FAMILY"] = "debian"
    environment["OSR_INSTALL_ARCH"] = "aarch64"
    result = subprocess.run(
        [str(INSTALLER), "--dry-run", "--no-build"],
        cwd=REPO_ROOT,
        env=environment,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "node-v22.23.2-linux-arm64.tar.xz" in result.stdout
    assert "uv-aarch64-unknown-linux-gnu.tar.gz" in result.stdout
    assert "trunk-aarch64-unknown-linux-gnu.tar.gz" in result.stdout


def test_installer_and_launcher_pin_the_same_node_release() -> None:
    installer = INSTALLER.read_text(encoding="utf-8")
    launcher = LAUNCHER.read_text(encoding="utf-8")
    assert 'NODE_VERSION="22.23.2"' in installer
    assert 'NODE_VERSION="22.23.2"' in launcher


def test_root_readme_exposes_one_command_setup_and_launcher() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "./install.sh" in readme
    assert "./install.sh --engineering" in readme
    assert "./scripts/osr workbench" in readme

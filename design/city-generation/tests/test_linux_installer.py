"""Keep Linux installation simple, safe, and discoverable."""

from __future__ import annotations

import stat
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
INSTALLER = REPO_ROOT / "install.sh"
LAUNCHER = REPO_ROOT / "osr"


def test_install_entry_points_are_executable_and_valid_bash() -> None:
    for path in (INSTALLER, LAUNCHER):
        assert path.stat().st_mode & stat.S_IXUSR
        subprocess.run(["bash", "-n", str(path)], check=True)


def test_single_command_can_check_without_changing_the_machine() -> None:
    result = subprocess.run(
        [str(INSTALLER)],
        cwd=REPO_ROOT,
        input="no\n",
        check=True,
        text=True,
        capture_output=True,
    )
    assert "Current installation" in result.stdout
    assert "No changes were made" in result.stdout


def test_installer_rejects_command_line_options() -> None:
    result = subprocess.run(
        [str(INSTALLER), "--anything"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 1
    assert "without options" in result.stderr


def test_installation_is_user_local_and_has_no_configuration_interface() -> None:
    installer = INSTALLER.read_text(encoding="utf-8")
    launcher = LAUNCHER.read_text(encoding="utf-8")
    assert ".local/share/opensource-rail/toolchains" in installer
    assert 'NODE_VERSION="22.23.2"' in installer
    assert 'NODE_VERSION="22.23.2"' in launcher
    for removed_interface in (
        "OSR_INSTALL_",
        "--engineering",
        "--dry-run",
        "--no-build",
    ):
        assert removed_interface not in installer
    assert "--check)" not in installer


def test_installer_checks_before_installing_and_offers_optional_tools() -> None:
    installer = INSTALLER.read_text(encoding="utf-8")
    assert "show_core_status" in installer
    assert "Install or refresh the core platform?" in installer
    assert "Also install the large CAD, BIM, GIS, and SUMO applications?" in installer
    assert "Start the Workbench now?" in installer
    for identifier in (
        "org.freecad.FreeCAD",
        "org.blender.Blender",
        "org.qgis.qgis",
        "org.cloudcompare.CloudCompare",
        "org.eclipse.sumo",
        "bonsai",
    ):
        assert identifier in installer


def test_root_readme_exposes_only_the_simple_setup_path() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "./install.sh" in readme
    assert "./osr" in readme
    assert "./install.sh --" not in readme
    assert "osr doctor" not in readme


def test_launcher_builds_the_book_in_the_managed_python_environment() -> None:
    launcher = LAUNCHER.read_text(encoding="utf-8")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "book [arguments]" in launcher
    assert 'exec python3 tools/automation/build-doc-book.py "$@"' in launcher
    assert "./osr book" in readme

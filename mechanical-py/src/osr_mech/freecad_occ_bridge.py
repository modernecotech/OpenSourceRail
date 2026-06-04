"""Move parametric source geometry into FreeCAD documents.

FreeCAD and the Python CAD source both sit on OpenCascade, so the bridge
uses a temporary BREP handoff during document generation. The only
persistent review artifacts are the saved FreeCAD documents.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceGeometry:
    key: str


def safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in name).strip("_")


def _source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _export_source_brep_in_process(source: SourceGeometry, brep_path: Path) -> None:
    from osr_mech.freecad_sources import export_source_brep

    export_source_brep(source.key, brep_path)


def _host_python_prefix() -> list[str]:
    requested_python = os.environ.get("OSR_HOST_PYTHON") or os.environ.get("PYTHON") or "python3"
    if Path("/.flatpak-info").exists() and shutil.which("flatpak-spawn"):
        return ["flatpak-spawn", "--host", requested_python]
    return [requested_python if requested_python else sys.executable]


def _export_source_brep_with_host_python(source: SourceGeometry, brep_path: Path) -> None:
    code = (
        "import sys; "
        "sys.path.insert(0, sys.argv[3]); "
        "from osr_mech.freecad_sources import export_source_brep; "
        "export_source_brep(sys.argv[1], sys.argv[2])"
    )
    cmd = _host_python_prefix() + [
        "-c",
        code,
        source.key,
        str(brep_path),
        str(_source_root()),
    ]
    proc = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"host Python could not build source geometry {source.key!r}:\n{proc.stdout}"
        )


def _export_source_brep(source: SourceGeometry, brep_path: Path) -> None:
    try:
        _export_source_brep_in_process(source, brep_path)
    except ModuleNotFoundError:
        _export_source_brep_with_host_python(source, brep_path)


def freecad_shape_from_source(
    source: SourceGeometry,
    *,
    part_module,
    cache: dict[str, object],
    temp_dir: Path,
):
    cached = cache.get(source.key)
    if cached is None:
        temp_dir.mkdir(parents=True, exist_ok=True)
        brep_path = temp_dir / f"{safe_name(source.key)}.brep"
        _export_source_brep(source, brep_path)

        shape = part_module.Shape()
        import_brep = getattr(shape, "importBrep", None)
        if callable(import_brep):
            import_brep(str(brep_path))
        else:
            shape.read(str(brep_path))
        cached = shape
        cache[source.key] = cached

    copy_shape = getattr(cached, "copy", None)
    return copy_shape() if callable(copy_shape) else cached

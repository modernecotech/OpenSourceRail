"""Move parametric source geometry into FreeCAD documents.

The Python catalogue source emits native FreeCAD ``Part`` shapes when it
runs under ``FreeCADCmd``. The only persistent review artifacts are the
saved FreeCAD documents.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceGeometry:
    key: str


def safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in name).strip("_")


def freecad_shape_from_source(
    source: SourceGeometry,
    *,
    part_module,
    cache: dict[str, object],
    temp_dir: Path,
):
    del part_module, temp_dir
    cached = cache.get(source.key)
    if cached is None:
        from osr_mech.freecad_sources import source_shape

        cached = source_shape(source.key)
        cache[source.key] = cached

    copy_shape = getattr(cached, "copy", None)
    return copy_shape() if callable(copy_shape) else cached

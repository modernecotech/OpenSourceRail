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
    car_length_mm: float | None = None


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
    cache_key = source.key if source.car_length_mm is None else (source.key, source.car_length_mm)
    cached = cache.get(cache_key)
    if cached is None:
        from osr_mech.freecad_sources import source_shape

        cached = source_shape(source.key) if source.car_length_mm is None else source_shape(source.key, car_length_mm=source.car_length_mm)
        cache[cache_key] = cached

    copy_shape = getattr(cached, "copy", None)
    return copy_shape() if callable(copy_shape) else cached

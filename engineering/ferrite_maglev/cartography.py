"""Offline city-context map of the current retained/proposed geography."""
from engineering.city_maps.render import render, _simplify as simplify


def source_paths():
    from engineering.city_maps import render as renderer
    from pathlib import Path
    return [Path(__file__), *renderer.source_paths()]

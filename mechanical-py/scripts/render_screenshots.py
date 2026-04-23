"""Render README screenshots for the parametric catalogue.

Walks a handful of published Compounds (canopy, trainset, fit-out car
body), tessellates every solid in each, and rasterises an isometric
matplotlib 3D view per drawing. Outputs under ``docs/screenshots/``.

The rendering is deliberately simple — a single pass with
``Poly3DCollection``, per-solid face colour taken from the build123d
``.color`` attribute where present, default off-white otherwise. No
camera setup, no raytracing; this is the CAD-sanity view, not a
marketing render.

Run from the repo root::

    python3 -m mechanical_py_scripts.render_screenshots

or directly::

    python3 mechanical-py/scripts/render_screenshots.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from build123d import Compound, Part
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageChops

from osr_mech.common import ConsistFamily, StationArchetype
from osr_mech.rolling_stock.car_body import CarDimensions
from osr_mech.rolling_stock.cots_equipment import fit_out_car_body
from osr_mech.rolling_stock.trainset import trainset
from osr_mech.station.canopy import station_canopy


DEFAULT_COLOR = (0.82, 0.82, 0.85, 1.0)


def _edge_from_face(rgba: tuple) -> tuple:
    """Darken the face colour for a subtle edge pass. Keeps the fill
    dominant — avoids the 'dense triangulation diagonal' look."""
    r, g, b = rgba[:3]
    alpha = rgba[3] if len(rgba) == 4 else 1.0
    return (r * 0.55, g * 0.55, b * 0.55, alpha * 0.35)


def _leaf_solids(node) -> list:
    """Flatten a build123d tree to its solid leaves. Compound children
    may themselves be Compounds (e.g. `station_canopy`, `trainset`); we
    recurse, and collect every `Part` / `Solid` we find.
    """
    out: list = []
    if hasattr(node, "children") and node.children:
        for c in node.children:
            out.extend(_leaf_solids(c))
        return out
    return [node]


def _color_tuple(node) -> tuple[float, float, float, float]:
    c = getattr(node, "color", None)
    if c is None:
        return DEFAULT_COLOR
    try:
        rgba = tuple(c)
        return (float(rgba[0]), float(rgba[1]), float(rgba[2]), float(rgba[3]))
    except Exception:
        return DEFAULT_COLOR


def _tessellate_collection(
    root,
    tolerance_mm: float,
    alpha_override: dict[str, float] | None = None,
) -> list[tuple[np.ndarray, tuple]]:
    """Return a list of `(triangles, rgba)` per leaf solid.

    `alpha_override` maps a substring-of-label to an alpha value —
    used e.g. to make the car-body shell translucent so interior
    envelopes show through."""
    collections: list[tuple[np.ndarray, tuple]] = []
    for leaf in _leaf_solids(root):
        try:
            verts, tris = leaf.tessellate(tolerance_mm)
        except Exception:
            continue
        if not verts or not tris:
            continue
        V = np.array([[v.X, v.Y, v.Z] for v in verts])
        T = np.array(tris, dtype=int)
        rgba = _color_tuple(leaf)
        if alpha_override:
            label = getattr(leaf, "label", "") or ""
            for needle, a in alpha_override.items():
                if needle in label:
                    rgba = (rgba[0], rgba[1], rgba[2], a)
                    break
        collections.append((V[T], rgba))
    # Draw opaque first, then translucent, so alpha-blending shows
    # interior objects through the shell.
    collections.sort(key=lambda g: g[1][3], reverse=True)
    return collections


def _render(
    compound: Compound,
    out_path: Path,
    *,
    tolerance_mm: float = 30.0,
    elev: float = 22.0,
    azim: float = -60.0,
    figsize: tuple[float, float] = (10.0, 5.0),
    dpi: int = 140,
    edge_linewidth: float = 0.15,
    background: str = "#f4f4f6",
    title: str | None = None,
    alpha_override: dict[str, float] | None = None,
) -> None:
    """Render `compound` to `out_path`. Tolerance controls triangle
    count — 30 mm is fine for a wide shot, 5 mm for close work. One
    big tessellation per solid; no adaptive refinement."""

    groups = _tessellate_collection(compound, tolerance_mm, alpha_override)
    if not groups:
        raise ValueError(f"no tessellatable leaves under {compound!r}")

    fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=background)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(background)

    all_pts: list[np.ndarray] = []
    lightsource = matplotlib.colors.LightSource(azdeg=225, altdeg=35)
    for tris, rgba in groups:
        # shade=True requires per-face facecolors; tile the solid's
        # RGBA over its triangle count.
        face_colors = np.tile(np.array(rgba)[None, :], (len(tris), 1))
        edge_colors = np.tile(
            np.array(_edge_from_face(rgba))[None, :], (len(tris), 1)
        )
        coll = Poly3DCollection(
            tris,
            facecolors=face_colors,
            edgecolors=edge_colors,
            linewidths=edge_linewidth,
            shade=True,
            lightsource=lightsource,
        )
        ax.add_collection3d(coll)
        all_pts.append(tris.reshape(-1, 3))

    pts = np.concatenate(all_pts, axis=0)
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    ctr = (lo + hi) / 2.0
    ranges = (hi - lo).astype(float)
    # Small pad so edges don't touch the plot box.
    pad = ranges * 0.02
    ax.set_xlim(lo[0] - pad[0], hi[0] + pad[0])
    ax.set_ylim(lo[1] - pad[1], hi[1] + pad[1])
    ax.set_zlim(lo[2] - pad[2], hi[2] + pad[2])
    # Use the actual geometry proportions — long skinny objects get a
    # long skinny 3D box instead of being lost inside a cube.
    ax.set_box_aspect(tuple(np.maximum(ranges, 1.0)))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()

    # Compact the figure: matplotlib 3D leaves wide margins by default;
    # we want the geometry to fill the frame. These are the knobs that
    # actually eat whitespace on a 3D axes.
    ax.margins(0)
    try:
        ax.set_position([0, 0, 1, 0.95 if title else 1.0])
    except Exception:
        pass
    if title:
        fig.suptitle(title, fontsize=11, color="#222", y=0.98)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        out_path,
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0.02,
        facecolor=background,
    )
    plt.close(fig)

    # Post-crop: matplotlib 3D always reserves a cubic bounding box in
    # screen space even when the geometry is thin. Trim whitespace to
    # actual drawn pixels, then re-pad a few px.
    _autocrop(out_path, background=background, pad_px=12)
    print(f"wrote {out_path}  ({out_path.stat().st_size // 1024} KB)")


def _autocrop(path: Path, *, background: str, pad_px: int) -> None:
    img = Image.open(path).convert("RGB")
    # Build a reference image the same size filled with `background`.
    from matplotlib.colors import to_rgb

    bg_rgb = tuple(int(round(c * 255)) for c in to_rgb(background))
    ref = Image.new("RGB", img.size, bg_rgb)
    diff = ImageChops.difference(img, ref)
    bbox = diff.getbbox()
    if bbox is None:
        return
    l, t, r, b = bbox
    W, H = img.size
    l = max(0, l - pad_px)
    t = max(0, t - pad_px)
    r = min(W, r + pad_px)
    b = min(H, b + pad_px)
    img.crop((l, t, r, b)).save(path)


def render_all(out_root: Path) -> None:
    # Titles live in the README caption, not the PNG — keeps the
    # rendered frame uncluttered.

    # 1. Reference station canopy — standard archetype, light-metro 3-car.
    canopy = station_canopy(
        archetype=StationArchetype.STANDARD,
        consist=ConsistFamily.LIGHT_METRO_3CAR,
    )
    _render(
        canopy,
        out_root / "station-canopy.png",
        tolerance_mm=20.0,
        elev=22,
        azim=-55,
        figsize=(12, 3.2),
    )

    # 2. Reference trainset — light-metro 3-car, cabless symmetric.
    ts = trainset(family=ConsistFamily.LIGHT_METRO_3CAR)
    _render(
        ts,
        out_root / "trainset-light-metro-3car.png",
        tolerance_mm=30.0,
        elev=18,
        azim=-55,
        figsize=(12, 3.0),
    )

    # 3. Fit-out car body — structural shell + all COTS envelopes in
    # their catalogue colours. The shell is drawn translucent so the
    # coloured interior envelopes read through it.
    fit = fit_out_car_body(CarDimensions())
    _render(
        fit,
        out_root / "trainset-interior-fit-out.png",
        tolerance_mm=15.0,
        elev=24,
        azim=-60,
        figsize=(12, 4.4),
        alpha_override={"Car body": 0.12},
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    out_root = repo_root / "docs" / "screenshots"
    render_all(out_root)


if __name__ == "__main__":
    main()

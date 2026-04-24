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
from osr_mech.rolling_stock.car_body import CarDimensions, car_body
from osr_mech.rolling_stock.cots_equipment import fit_out_car_body
from osr_mech.rolling_stock.trainset import trainset
from osr_mech.station.canopy import station_canopy


DEFAULT_COLOR = (0.82, 0.82, 0.85, 1.0)


def _apply_location(V: np.ndarray, loc) -> np.ndarray:
    """Apply a build123d Location to an (N, 3) vertex array.

    build123d Locations wrap an OCP TopLoc_Location whose underlying
    gp_Trsf is a 3×4 matrix (rotation + translation). We pull the
    values out one cell at a time and apply `v' = R·v + t`."""
    try:
        tr = loc.wrapped.Transformation()
        R = np.array(
            [[tr.Value(r + 1, c + 1) for c in range(3)] for r in range(3)]
        )
        t = np.array([tr.Value(r + 1, 4) for r in range(3)])
        return V @ R.T + t
    except Exception:
        try:
            p = loc.position
            return V + np.array([p.X, p.Y, p.Z])
        except Exception:
            return V


def _apply_soft_shading(
    tris: np.ndarray,
    face_colors: np.ndarray,
    lightsource: "matplotlib.colors.LightSource",
) -> np.ndarray:
    """Shade per-triangle by Lambert with a floor so shadow-side
    faces don't go black. Returns RGBA array, one row per triangle.

    `tris` has shape (N, 3, 3). Face normal = cross of two edges;
    we dot with the lightsource direction, clamp into [floor, 1.0]
    and multiply the RGB components.
    """
    # Face normals.
    e1 = tris[:, 1] - tris[:, 0]
    e2 = tris[:, 2] - tris[:, 0]
    n = np.cross(e1, e2)
    norm = np.linalg.norm(n, axis=1, keepdims=True)
    norm = np.where(norm < 1e-6, 1.0, norm)
    n = n / norm

    # Lightsource direction (azdeg measured ccw from +X in XY plane).
    az = np.radians(lightsource.azdeg)
    al = np.radians(lightsource.altdeg)
    L = np.array(
        [np.cos(al) * np.cos(az), np.cos(al) * np.sin(az), np.sin(al)]
    )

    # Use |dot| so triangles with flipped winding (some tessellators
    # alternate on adjacent triangles) don't produce a diagonal
    # checkerboard across coplanar faces.
    dot = np.abs(n @ L)
    # Floor + gain: 0.55 ambient (shadow side) → 1.0 (fully lit).
    shade = 0.55 + 0.45 * np.clip(dot, 0.0, 1.0)
    shade = shade[:, None]  # (N, 1)

    # Scale RGB; keep alpha untouched.
    out = face_colors.copy()
    out[:, :3] = np.clip(face_colors[:, :3] * shade, 0.0, 1.0)
    return out


def _leaf_solids(node) -> list:
    """Flatten a build123d tree to leaf shapes in world space.

    build123d's `.children` is an anytree view that can diverge from
    the OCP TopoDS tree once `.translate()` is called on a nested
    Compound. We walk the TopoDS tree for the authoritative world-
    space geometry, then pair each Solid with the nearest anytree
    leaf's label + colour by matching centroid locations.
    """
    # Anytree leaves → (label, color, centroid).
    anytree_meta = _collect_anytree_meta(node)

    # Walk TopoDS for the authoritative solid list.
    from build123d import Solid
    from OCP.TopoDS import TopoDS_Iterator
    from OCP.TopAbs import TopAbs_SOLID

    solids: list = []

    def rec(topods):
        if topods.ShapeType() == TopAbs_SOLID:
            leaf = Solid(topods)
            _assign_metadata(leaf, anytree_meta)
            solids.append(leaf)
            return
        it = TopoDS_Iterator(topods)
        while it.More():
            rec(it.Value())
            it.Next()

    rec(node.wrapped)
    return solids


def _collect_anytree_meta(root) -> list:
    """Return per-anytree-leaf (label, color, dims_sorted) tuples.
    `dims_sorted` is the sorted bbox-side-length tuple — a rotation-
    and-position-invariant fingerprint we can match against TopoDS
    solids discovered through a separate traversal."""
    out: list = []

    def rec(node):
        if hasattr(node, "children") and node.children:
            for c in node.children:
                rec(c)
            return
        try:
            bb = node.bounding_box()
            dims = tuple(
                sorted(
                    (
                        bb.max.X - bb.min.X,
                        bb.max.Y - bb.min.Y,
                        bb.max.Z - bb.min.Z,
                    )
                )
            )
        except Exception:
            dims = (0.0, 0.0, 0.0)
        out.append(
            (
                getattr(node, "label", "") or "",
                getattr(node, "color", None),
                dims,
            )
        )

    rec(root)
    return out


def _assign_metadata(solid, anytree_meta) -> None:
    """Tag a TopoDS-walked Solid with the anytree leaf whose bbox
    fingerprint matches. Dims are in mm; we allow 5 mm slop."""
    bb = solid.bounding_box()
    dims = tuple(
        sorted(
            (bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z)
        )
    )
    best_label = ""
    best_color = None
    best_score = float("inf")
    for label, color, mdims in anytree_meta:
        score = sum(abs(a - b) for a, b in zip(dims, mdims))
        if score < best_score:
            best_score = score
            best_label = label
            best_color = color
    if best_score > 50.0:  # no good match — keep defaults
        return
    if best_label:
        solid.label = best_label
    if best_color is not None:
        solid.color = best_color


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
    collections: list[tuple[np.ndarray, tuple, str]] = []
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
        label = getattr(leaf, "label", "") or ""
        if alpha_override:
            for needle, a in alpha_override.items():
                if needle in label:
                    rgba = (rgba[0], rgba[1], rgba[2], a)
                    break
        collections.append((V[T], rgba, label))
    # Painter's order: body shell first (drawn at the back), then
    # applied features (livery, doors, skirt), then rooftop equipment,
    # then translucent items last so alpha-blending shows interior
    # objects through the shell.
    def _order_key(group):
        rgba = group[1]
        label = group[2] if len(group) > 2 else ""
        alpha = rgba[3]
        priority = 1  # default (middle)
        lower = label.lower() if label else ""
        if "shell" in lower:
            priority = 0
        elif "livery" in lower:
            priority = 2
        elif "door leaf" in lower:
            priority = 3
        elif "glazing" in lower:
            priority = 4
        elif "hvac" in lower or "roof" in lower or "sensor" in lower or "headlight" in lower:
            priority = 5
        if alpha < 0.95:
            priority = 9  # translucent on top
        return priority
    collections.sort(key=_order_key)
    # Strip the label after sorting; downstream code expects (tris, rgba).
    return [(t, c) for (t, c, *_rest) in collections]


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
    # Honour our explicit zorder — matplotlib's auto depth-sort on 3D
    # axes otherwise reorders collections by average-Z and hides
    # thin surfaces (the livery band) behind the shell.
    try:
        ax.set_computed_zorder(False)
    except AttributeError:
        pass

    lightsource = matplotlib.colors.LightSource(azdeg=315, altdeg=55)

    # Merge every leaf's triangles into ONE Poly3DCollection with
    # per-face colours. matplotlib's per-face z-sort then handles
    # occlusion correctly — far-and-away better than per-collection
    # average-Z sort, which hides thin features (livery band) behind
    # the shell regardless of the explicit zorder we set.
    opaque_tris: list[np.ndarray] = []
    opaque_colors: list[np.ndarray] = []
    translucent_tris: list[np.ndarray] = []
    translucent_colors: list[np.ndarray] = []
    for tris, rgba in groups:
        face_colors = np.tile(np.array(rgba)[None, :], (len(tris), 1))
        shaded = _apply_soft_shading(tris, face_colors, lightsource)
        if rgba[3] >= 0.95:
            opaque_tris.append(tris)
            opaque_colors.append(shaded)
        else:
            translucent_tris.append(tris)
            translucent_colors.append(shaded)

    all_pts: list[np.ndarray] = []
    if opaque_tris:
        T = np.concatenate(opaque_tris, axis=0)
        C = np.concatenate(opaque_colors, axis=0)
        coll = Poly3DCollection(T, facecolors=C, linewidths=0)
        coll.set_zorder(1)
        ax.add_collection3d(coll)
        all_pts.append(T.reshape(-1, 3))
    if translucent_tris:
        T = np.concatenate(translucent_tris, axis=0)
        C = np.concatenate(translucent_colors, axis=0)
        coll = Poly3DCollection(T, facecolors=C, linewidths=0)
        coll.set_zorder(2)
        ax.add_collection3d(coll)
        all_pts.append(T.reshape(-1, 3))

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
        tolerance_mm=10.0,
        elev=22,
        azim=-55,
        figsize=(12, 3.4),
        dpi=160,
    )

    # 2. Reference trainset — light-metro 3-car, cabless symmetric.
    # Near-head-on side elevation (same as the single car) so the
    # three-car arrangement + nose cowls read cleanly without self-
    # occlusion from isometric overlap.
    ts = trainset(family=ConsistFamily.LIGHT_METRO_3CAR)
    _render(
        ts,
        out_root / "trainset-light-metro-3car.png",
        tolerance_mm=6.0,
        elev=3,
        azim=-90.1,
        figsize=(16, 3.2),
        dpi=180,
    )

    # 3. A single car — near head-on side view so the design details
    # (rounded corners, livery, doors, windows, roof HVAC, skirt)
    # all read clearly without self-occlusion. Tight tessellation for
    # the filleted corners.
    car = car_body(CarDimensions())
    _render(
        car,
        out_root / "trainset-car-detail.png",
        tolerance_mm=2.0,
        elev=3,
        azim=-90.1,  # -90 exactly is a degenerate case; nudge slightly
        figsize=(14, 3.2),
        dpi=200,
    )

    # 4. Fit-out car body — structural shell + all COTS envelopes in
    # their catalogue colours. The shell is drawn translucent so the
    # coloured interior envelopes read through it.
    fit = fit_out_car_body(CarDimensions())
    _render(
        fit,
        out_root / "trainset-interior-fit-out.png",
        tolerance_mm=10.0,
        elev=20,
        azim=-55,
        figsize=(12, 4.6),
        dpi=160,
        alpha_override={"shell": 0.12, "livery": 0.0, "skirt": 0.0, "Roof auxiliary": 0.25, "HVAC roof unit": 0.25},
    )

    # 5. Motor bogie — detailed component + assembly CAD (RFC 0022).
    from osr_mech.rolling_stock.bogie import motor_bogie, trailer_bogie
    _render(
        motor_bogie(),
        out_root / "bogie-motor.png",
        tolerance_mm=8.0,
        elev=18,
        azim=-45,
        figsize=(12, 6),
        dpi=180,
    )
    _render(
        trailer_bogie(),
        out_root / "bogie-trailer.png",
        tolerance_mm=8.0,
        elev=18,
        azim=-45,
        figsize=(12, 6),
        dpi=180,
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    out_root = repo_root / "docs" / "screenshots"
    render_all(out_root)


if __name__ == "__main__":
    main()

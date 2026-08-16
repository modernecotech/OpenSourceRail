"""Render README screenshots for the parametric catalogue.

Walks a handful of published Compounds (canopy, trainset, fit-out car
body), tessellates every solid in each, and rasterises an isometric
matplotlib 3D view per drawing. Outputs under ``docs/screenshots/``.

The rendering is deliberately simple — a single pass with
``Poly3DCollection``, per-solid face colour taken from the CAD object's
``.color`` attribute where present, default off-white otherwise. No
camera setup, no raytracing; this is the CAD-sanity view, not a
marketing render.

Run from the repo root::

    python3 -m mechanical_py_scripts.render_screenshots

or directly::

    python3 mechanical-py/scripts/render_screenshots.py
"""

from __future__ import annotations

from collections.abc import Iterable
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from osr_mech.cad import Compound, Part
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageChops

from osr_mech.common import ConsistFamily, StationArchetype
from osr_mech.rolling_stock.car_body import (
    CarDimensions,
    car_body,
    car_body_exterior,
    car_body_interior,
    car_body_services,
    car_body_structure,
)
from osr_mech.rolling_stock.bogie import WHEELBASE_MM, motor_bogie, trailer_bogie
from osr_mech.rolling_stock.cots_equipment import fit_out_car_body
from osr_mech.rolling_stock.mechanical_interfaces import INTERFACE_BUILDERS
from osr_mech.rolling_stock.sensor_cowl import sensor_cowl
from osr_mech.rolling_stock.trainset import trainset
from osr_mech.station.canopy import station_canopy


DEFAULT_COLOR = (0.82, 0.82, 0.85, 1.0)

ROOT_SCREENSHOT_PATTERNS = (
    "station-canopy.png",
    "end-glass-cowl*.png",
    "trainset-*.png",
    "bogie-*.png",
)

FACTORY_COLORS = {
    "steel": "#8b949e",
    "weld": "#6b7280",
    "composite": "#58a55c",
    "paint": "#d8a03d",
    "bogie": "#2f3437",
    "interior": "#4f83cc",
    "final": "#3f6ea8",
    "support": "#c5ccd3",
    "yard": "#d8e6d2",
    "track": "#333842",
    "machine": "#f0c05a",
}


def _remove_generated(paths: Iterable[Path]) -> None:
    for path in paths:
        if not path.is_file():
            continue
        path.unlink()
        print(f"removed old generated screenshot {path}")


def _refresh_latest_outputs(out_root: Path) -> None:
    """Clear screenshots owned by this renderer before writing new ones.

    The docs reference stable filenames. Removing the renderer-owned
    targets first keeps those filenames as "latest" views and prevents
    stale images from surviving after a screenshot is renamed or removed.
    """
    for pattern in ROOT_SCREENSHOT_PATTERNS:
        _remove_generated(out_root.glob(pattern))
    interface_out = out_root / "rolling-stock" / "interfaces"
    _remove_generated(interface_out.glob("*.png"))


def _apply_location(V: np.ndarray, loc) -> np.ndarray:
    """Apply a CAD Location to an (N, 3) vertex array.

    Locations wrap an OCP TopLoc_Location whose underlying
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
    """Flatten a CAD tree to leaf shapes in world space.

    The `.children` view can diverge from
    the OCP TopoDS tree once `.translate()` is called on a nested
    Compound. We walk the TopoDS tree for the authoritative world-
    space geometry, then pair each Solid with the nearest anytree
    leaf's label + colour by matching centroid locations.
    """
    if getattr(node, "wrapped", None) is None:
        solids: list = []

        def rec_anytree(n):
            children = getattr(n, "children", None)
            if children:
                for child in children:
                    rec_anytree(child)
                return
            solids.append(n)

        rec_anytree(node)
        return solids

    # Anytree leaves → (label, color, centroid).
    anytree_meta = _collect_anytree_meta(node)

    # Walk TopoDS for the authoritative solid list.
    from osr_mech.cad import Solid
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


def _save_2d(fig, out_path: Path, *, background: str = "#f4f4f6") -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180, bbox_inches="tight", pad_inches=0.08, facecolor=background)
    plt.close(fig)
    _autocrop(out_path, background=background, pad_px=14)
    print(f"wrote {out_path}  ({out_path.stat().st_size // 1024} KB)")


def _box2d(ax, x, y, w, h, *, color, label="", edge="#20242a", alpha=1.0, lw=1.2, hatch=None):
    patch = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor=edge, linewidth=lw, alpha=alpha, hatch=hatch)
    ax.add_patch(patch)
    if label:
        ax.text(
            x + w / 2,
            y + h / 2,
            label,
            ha="center",
            va="center",
            fontsize=7.5,
            color="#111827",
            wrap=True,
        )
    return patch


def _factory_plan_path(out_root: Path) -> Path:
    return out_root.parents[1] / "mechanical-py" / "catalog" / "buildable-trainset" / "factory-plan.json"


def _critical_path_path(out_root: Path) -> Path:
    return out_root.parents[1] / "mechanical-py" / "catalog" / "buildable-trainset" / "critical-path.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _render_factory_layout(factory: dict, out_path: Path) -> None:
    size = factory["factory_size"]
    fig, ax = plt.subplots(figsize=(14, 8), facecolor="#f4f4f6")
    ax.set_facecolor("#f4f4f6")
    ax.set_aspect("equal")
    ax.axis("off")

    # Scaled 72 x 52 m envelope ~= 3,744 m2, leaving visual edge space
    # around the 3,515 m2 recommended minimum.
    _box2d(ax, 0, 0, 72, 52, color="#edf0f3", edge="#1f2937", lw=1.8)
    ax.text(0, 57, "LM3 pilot factory - enclosed 3,515 m2 / 37,835 ft2", fontsize=13, weight="bold", color="#111827")
    ax.text(0, 54.6, "One 55 m final bay; chassis, bogies, GFRP modules, and interiors run off-line in parallel", fontsize=9, color="#374151")

    # Main process cells, arranged like a plausible leased industrial bay.
    _box2d(ax, 2, 30, 18, 10, color="#d6d9de", label="Steel prep\n18 x 10 m")
    _box2d(ax, 22, 22, 32, 20, color="#c7cbd1", label="Chassis weld + body-frame fixtures\n32 x 20 m")
    _box2d(ax, 2, 14, 22, 12, color="#cde8cc", label="")
    ax.text(13, 15.1, "Composite mould / cure / trim\n22 x 12 m", ha="center", va="bottom", fontsize=7.5, color="#111827")
    _box2d(ax, 26, 6, 28, 12, color="#efd7a3", label="")
    ax.text(47, 13.2, "Paint + corrosion bay\n28 x 12 m", ha="center", va="center", fontsize=7.5, color="#111827")
    _box2d(ax, 56, 28, 14, 14, color="#c3c7cc", label="Stores / QA /\ntoolroom / offices")
    _box2d(ax, 2, 2, 20, 10, color="#c6cbd0", label="")
    ax.text(12, 9.6, "Bogie assembly + test\n20 x 12 m", ha="center", va="center", fontsize=7.5, color="#111827")
    _box2d(ax, 24, 2, 16, 10, color="#bdd3f1", label="Interior + HVAC duct\nkit bench")
    _box2d(ax, 8, -13, 55, 10, color="#d8e6d2", edge="#6a7c65", label="Outside yard / apron 2,200 m2\nstaging + short test access", alpha=0.95)

    # Final bay drawn as the dominant train-length process lane.
    _box2d(ax, 6, 42.0, 60, 7.2, color="#b7cce7", label="")
    ax.plot([8, 64], [44.6, 44.6], color=FACTORY_COLORS["track"], linewidth=3)
    ax.plot([8, 64], [46.4, 46.4], color=FACTORY_COLORS["track"], linewidth=3)
    for x in np.linspace(11, 61, 9):
        ax.plot([x, x], [44.1, 46.9], color="#6b7280", linewidth=1.1)
    _box2d(ax, 10, 43.3, 49.5, 2.4, color="#f8fafc", edge="#2563eb", label="3-car LM3 on final assembly / static-test track", lw=1.4)
    _box2d(ax, 13, 47.2, 11, 1.0, color="#f0c05a", label="roof access", lw=0.8)
    _box2d(ax, 44, 47.2, 11, 1.0, color="#f0c05a", label="HV lockout", lw=0.8)

    # Realistic fixture/machine hints.
    for x in (25, 39):
        _box2d(ax, x, 34, 16.5, 2.4, color="#9ca3af", label="underframe rotator", lw=0.8)
    for x in (25, 39):
        _box2d(ax, x, 25, 13, 2.0, color="#aeb4bc", label="side/roof fixture", lw=0.8)
    ax.text(13, 23.2, "1 m modular moulds", ha="center", va="center", fontsize=7.2, color="#111827")
    for i, x in enumerate((5, 10, 15, 20)):
        _box2d(ax, x, 20, 3.2, 2.5, color="#9fd39c", label=f"M{i+1}", lw=0.7)
    _box2d(ax, 17.5, 15.2, 4.8, 2.2, color="#f0c05a", label="CNC trim", lw=0.7)
    for x in (6, 12, 18):
        _box2d(ax, x, 4.0, 4, 1.6, color="#1f2937", label="", edge="#111827", lw=0.7)
        ax.text(x + 2, 4.8, "bogie", ha="center", va="center", fontsize=7.0, color="#f9fafb")
    _box2d(ax, 58, 22, 8, 4, color="#f4d182", label="forklift / carts", lw=0.7)

    ax.text(2, -16.5, f"Dynamic test track: {size['dynamic_test_track']}", fontsize=8.5, color="#374151")
    ax.set_xlim(-1, 73)
    ax.set_ylim(-18, 58)
    _save_2d(fig, out_path)


def _render_assembly_timeline(factory: dict, critical: dict, out_path: Path) -> None:
    tasks = {task["id"]: task for task in critical["tasks"]}
    fig, ax = plt.subplots(figsize=(15, 7), facecolor="#f4f4f6")
    ax.set_facecolor("#f4f4f6")
    ax.axis("off")
    ax.set_xlim(-4, 36)
    ax.set_ylim(-0.6, 8.5)
    ax.text(0, 8.1, "LM3 first-article assembly method - parallel work streams", fontsize=13, weight="bold", color="#111827")
    ax.text(0, 7.75, "35 working days total; off-line cells feed one controlled 55 m final bay", fontsize=9, color="#374151")

    streams = [
        ("Chassis/body frame", ("CP-020", "CP-030", "CP-040", "CP-070"), FACTORY_COLORS["weld"]),
        ("GFRP moulding + body clip", ("CP-060", "CP-080"), FACTORY_COLORS["composite"]),
        ("Bogies + marriage", ("CP-050", "CP-120"), FACTORY_COLORS["bogie"]),
        ("Interior kits + install", ("CP-065", "CP-110"), FACTORY_COLORS["interior"]),
        ("Doors/windows/roof", ("CP-090",), FACTORY_COLORS["final"]),
        ("HV/electrical install", ("CP-100",), "#3f6ea8"),
        ("Articulation + static", ("CP-130", "CP-140"), "#5479a6"),
        ("Dynamic release", ("CP-150",), "#7c3aed"),
    ]
    for row_idx, (label, task_ids, color) in enumerate(streams):
        y = 7.0 - row_idx
        ax.text(-3.8, y + 0.18, label, ha="left", va="center", fontsize=8.5, color="#111827")
        for task_id in task_ids:
            task = tasks[task_id]
            x = float(task["early_start_day"])
            w = float(task["early_finish_day"]) - x
            _box2d(
                ax,
                x,
                y - 0.2,
                w,
                0.42,
                color=color,
                label=task_id,
                edge="#111827",
                lw=0.8,
                alpha=0.92,
            )
            ax.text(x + w / 2, y - 0.47, f"{w:.0f}d / {float(task['labor_hours']):.0f}h", ha="center", fontsize=6.5, color="#374151")
    for day in range(0, 36, 5):
        ax.plot([day, day], [-0.1, 7.4], color="#d1d5db", linewidth=0.8, zorder=0)
        ax.text(day, -0.35, f"d{day}", ha="center", fontsize=8, color="#4b5563")
    ax.plot([0, 35], [-0.05, -0.05], color="#6b7280", linewidth=1.2)
    _save_2d(fig, out_path)


def _render_bogie_marriage_method(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 6), facecolor="#f4f4f6")
    ax.set_facecolor("#f4f4f6")
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0, 9.2, "Bogie-to-carbody marriage method", fontsize=13, weight="bold", color="#111827")
    ax.text(0, 8.55, "Released bogies enter late; chassis is lifted on mobile columns, then lowered to centre-pivot and air-spring datums", fontsize=9, color="#374151")

    ax.plot([0.5, 22.5], [1.0, 1.0], color=FACTORY_COLORS["track"], linewidth=4)
    ax.plot([0.5, 22.5], [2.0, 2.0], color=FACTORY_COLORS["track"], linewidth=4)
    for x in np.linspace(1.5, 21.5, 11):
        ax.plot([x, x], [0.5, 2.5], color="#6b7280", linewidth=1)

    # Carbody/chassis above bogies, with jack columns.
    _box2d(ax, 2.2, 5.3, 18.5, 1.1, color="#d8dde3", edge="#374151", label="painted carbody / chassis datum", lw=1.5)
    _box2d(ax, 3.0, 6.45, 3.2, 0.55, color="#b7cce7", label="roof/HVAC", lw=0.7)
    _box2d(ax, 16.6, 6.45, 3.2, 0.55, color="#b7cce7", label="roof/HVAC", lw=0.7)
    for x in (4.2, 9.0, 14.0, 18.8):
        _box2d(ax, x, 2.4, 0.45, 3.0, color="#f0c05a", label="", lw=0.8)
        _box2d(ax, x - 0.55, 2.15, 1.55, 0.35, color="#f0c05a", label="", lw=0.8)
    for x, label in ((5.0, "motor bogie"), (18.0, "trailer bogie")):
        _box2d(ax, x - 2.0, 1.25, 4.0, 1.05, color="#252a30", edge="#111827", label="", lw=1.1)
        ax.text(x, 1.77, label, ha="center", va="center", fontsize=7.5, color="#f9fafb")
        for wx in (x - 1.25, x + 1.25):
            circle = plt.Circle((wx, 1.05), 0.45, color="#111827")
            ax.add_patch(circle)
            ax.add_patch(plt.Circle((wx, 1.05), 0.24, color="#6b7280"))
        _box2d(ax, x - 0.25, 2.55, 0.5, 2.15, color="#ef4444", label="", lw=0.7)
        ax.annotate("", xy=(x, 2.55), xytext=(x, 4.75), arrowprops=dict(arrowstyle="<->", color="#ef4444", lw=1.4))
    ax.text(0.5, 7.55, "Hold points: bogie certificates -> centre-pivot socket survey -> air-spring shim record -> brake/static checks", fontsize=8, color="#374151")
    ax.set_xlim(-0.5, 23.5)
    ax.set_ylim(0, 10)
    _save_2d(fig, out_path)


def _render_gfrp_moulding_method(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 6), facecolor="#f4f4f6")
    ax.set_facecolor("#f4f4f6")
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0, 9.2, "One-metre GFRP module moulding and clip-on body method", fontsize=13, weight="bold", color="#111827")
    ax.text(0, 8.55, "Four short moulds feed CNC trim, edge sealing, insert/clip fit, master-frame dry fit, then one-shift body installation", fontsize=9, color="#374151")

    stages = [
        ("1. mould / cure", 0.5, FACTORY_COLORS["composite"]),
        ("2. demould / trim", 5.2, "#a7d7a4"),
        ("3. inserts / seals", 9.9, "#bdd7b9"),
        ("4. master-frame dry fit", 14.6, "#d1e9cf"),
        ("5. clip to carbody", 19.3, "#b7cce7"),
    ]
    for label, x, color in stages:
        _box2d(ax, x, 6.7, 3.6, 1.1, color=color, label=label, lw=1.0)
    for x in (4.3, 9.0, 13.7, 18.4):
        ax.annotate("", xy=(x + 0.6, 7.25), xytext=(x, 7.25), arrowprops=dict(arrowstyle="->", color="#374151", lw=1.3))

    for i, x in enumerate((0.6, 1.6, 2.6, 3.6), start=1):
        _box2d(ax, x, 4.0, 0.8, 1.9, color="#8dcf86", label=f"M{i}", lw=0.7)
    _box2d(ax, 5.25, 4.25, 3.4, 1.3, color="#f0c05a", label="CNC trim / drill", lw=0.8)
    for x in (10.1, 11.2, 12.3):
        _box2d(ax, x, 4.25, 0.85, 1.3, color="#e5e7eb", label="clip\nseal", lw=0.7)
    _box2d(ax, 14.8, 3.8, 3.4, 2.0, color="#e5e7eb", label="master frame\nfit gauge", lw=0.9)
    _box2d(ax, 19.2, 3.25, 4.8, 2.7, color="#d8dde3", label="painted carbody\nclip rails", lw=1.0)
    for x in np.linspace(19.6, 23.2, 6):
        _box2d(ax, x, 5.0, 0.45, 0.55, color="#8dcf86", label="", lw=0.5)
        _box2d(ax, x, 3.65, 0.45, 0.55, color="#8dcf86", label="", lw=0.5)
    ax.text(0.5, 1.6, "Evidence: mould release record, resin/fibre batch, cure log, witness coupon, CNC trim report, insert pull-out, edge seal, dry-fit map", fontsize=8, color="#374151")
    ax.text(0.5, 0.85, "Assembly rule: dry EPDM seals + keyed hooks + captive clips + anti-lift retainers; no full-length body mould and no production adhesive cure hold", fontsize=8, color="#374151")
    ax.set_xlim(-0.2, 24.5)
    ax.set_ylim(0, 10)
    _save_2d(fig, out_path)


def _render_factory_method_screenshots(out_root: Path) -> None:
    factory = _load_json(_factory_plan_path(out_root))
    critical = _load_json(_critical_path_path(out_root))
    _render_factory_layout(factory, out_root / "trainset-factory-layout.png")
    _render_assembly_timeline(factory, critical, out_root / "trainset-assembly-method-flow.png")
    _render_bogie_marriage_method(out_root / "trainset-bogie-marriage-method.png")
    _render_gfrp_moulding_method(out_root / "trainset-gfrp-moulding-method.png")


def render_all(out_root: Path) -> None:
    _refresh_latest_outputs(out_root)

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

    # 2. Driverless end cowl close-up — a compact view where the
    # single panoramic glass face is legible before the full consist view.
    _render(
        sensor_cowl(),
        out_root / "end-glass-cowl.png",
        tolerance_mm=5.0,
        elev=3,
        azim=0,
        figsize=(8, 5),
        dpi=180,
        alpha_override={"aerodynamic envelope": 0.18},
    )

    # 3. Reference trainset — light-metro 3-car, cabless symmetric.
    # Near-head-on side elevation (same as the single car) so the
    # three-car arrangement + nose cowls read cleanly without self-
    # occlusion from isometric overlap.
    ts = trainset(family=ConsistFamily.LIGHT_METRO_3CAR)
    _render(
        ts,
        out_root / "trainset-light-metro-3car.png",
        tolerance_mm=18.0,
        elev=3,
        azim=-90.1,
        figsize=(16, 3.2),
        dpi=150,
    )

    # 4. A single car — near head-on side view so the design details
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

    # 4a. Layered body subassemblies. These are intentionally separate
    # from the final car render so the current CAD hierarchy is
    # visible in docs without opening a CAD viewer.
    _render(
        car_body_structure(CarDimensions()),
        out_root / "trainset-car-body-structure.png",
        tolerance_mm=5.0,
        elev=22,
        azim=-48,
        figsize=(15, 5.2),
        dpi=200,
        alpha_override={"shell": 0.08},
    )
    dims = CarDimensions()
    bogie_offset_x = dims.body_length_mm / 2.0 - WHEELBASE_MM
    structure_with_bogies = Compound(
        label="Car body structure with standard bogies subassembly",
        children=[
            car_body_structure(dims),
            motor_bogie().translate((-bogie_offset_x, 0.0, 0.0)),
            trailer_bogie().translate((bogie_offset_x, 0.0, 0.0)),
        ],
    )
    _render(
        structure_with_bogies,
        out_root / "trainset-car-body-bogie-subassembly.png",
        tolerance_mm=6.0,
        elev=16,
        azim=-55,
        figsize=(15, 5.6),
        dpi=190,
        alpha_override={"shell": 0.08},
    )
    _render(
        car_body_exterior(CarDimensions()),
        out_root / "trainset-car-body-exterior.png",
        tolerance_mm=4.0,
        elev=8,
        azim=-80,
        figsize=(13, 4),
        dpi=180,
    )
    _render(
        car_body_interior(CarDimensions()),
        out_root / "trainset-car-body-interior.png",
        tolerance_mm=5.0,
        elev=18,
        azim=-55,
        figsize=(13, 4.5),
        dpi=180,
    )
    _render(
        car_body_services(CarDimensions()),
        out_root / "trainset-car-body-services.png",
        tolerance_mm=4.0,
        elev=18,
        azim=-55,
        figsize=(13, 4.5),
        dpi=180,
    )

    # 5. Fit-out car body — structural shell + all COTS envelopes in
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

    from osr_mech.cad_templates import body_sheet_metal_kit

    _render(
        body_sheet_metal_kit(),
        out_root / "trainset-body-sheet-metal-kit.png",
        tolerance_mm=12.0,
        elev=16,
        azim=-55,
        figsize=(13, 5),
        dpi=170,
    )

    # 6. Motor bogie — detailed component + assembly CAD (RFC 0022).
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

    # 7. Train-level systems now represented in the final trainset:
    # couplers, inter-car articulation, battery modules, doors,
    # electronics, charging contacts, accessibility, and T-OBS sensors.
    from osr_mech.rolling_stock.systems import (
        battery_pack_set,
        car_systems,
        door_system_pair,
        electronics_cabinet,
        end_coupler,
        inter_car_articulation,
        roof_solar_system,
        tobs_sensor_pack,
    )

    _render(
        car_systems(CarDimensions()),
        out_root / "trainset-car-systems.png",
        tolerance_mm=8.0,
        elev=18,
        azim=-55,
        figsize=(13, 5.5),
        dpi=170,
    )
    _render(
        battery_pack_set(CarDimensions()),
        out_root / "trainset-battery-pack.png",
        tolerance_mm=4.0,
        elev=22,
        azim=-40,
        figsize=(11, 4.5),
        dpi=180,
    )
    _render(
        roof_solar_system(CarDimensions()),
        out_root / "trainset-roof-solar-system.png",
        tolerance_mm=6.0,
        elev=22,
        azim=-55,
        figsize=(12, 5),
        dpi=180,
    )
    _render(
        door_system_pair(),
        out_root / "trainset-door-system.png",
        tolerance_mm=3.0,
        elev=10,
        azim=-65,
        figsize=(8, 5),
        dpi=180,
    )
    _render(
        electronics_cabinet(),
        out_root / "trainset-electronics-cabinet.png",
        tolerance_mm=3.0,
        elev=18,
        azim=-45,
        figsize=(8, 5),
        dpi=180,
    )
    _render(
        end_coupler(),
        out_root / "trainset-end-coupler.png",
        tolerance_mm=3.0,
        elev=18,
        azim=-45,
        figsize=(8, 4.5),
        dpi=180,
    )
    _render(
        inter_car_articulation(),
        out_root / "trainset-inter-car-articulation.png",
        tolerance_mm=8.0,
        elev=18,
        azim=-125,
        figsize=(8, 6),
        dpi=180,
    )
    _render(
        tobs_sensor_pack(),
        out_root / "trainset-tobs-sensor-pack.png",
        tolerance_mm=3.0,
        elev=15,
        azim=-45,
        figsize=(8, 5),
        dpi=180,
    )

    # 8. Mechanical interface and installation packages. These are the
    # explicit bracket/rail/mount/torsion-box details added for the
    # FreeCAD assembly and FEA review loop.
    interface_out = out_root / "rolling-stock" / "interfaces"
    for slug, builder in INTERFACE_BUILDERS.items():
        model = builder()
        if slug == "mechanical-interface-package":
            figsize = (16, 7)
            dpi = 170
            tolerance = 12.0
        elif slug in {"low-floor-chassis", "side-body-frame-attachments", "composite-body-roof-attachments"}:
            figsize = (14, 5.2)
            dpi = 180
            tolerance = 7.0
        else:
            figsize = (10, 5.5)
            dpi = 180
            tolerance = 5.0
        _render(
            model,
            interface_out / f"{slug}.png",
            tolerance_mm=tolerance,
            elev=18,
            azim=-55,
            figsize=figsize,
            dpi=dpi,
        )

    # 9. More realistic manufacturing/assembly-method screenshots
    # generated from the current factory and critical-path artifacts.
    _render_factory_method_screenshots(out_root)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    out_root = repo_root / "docs" / "screenshots"
    render_all(out_root)


if __name__ == "__main__":
    main()

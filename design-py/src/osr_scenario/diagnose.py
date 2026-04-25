"""Coverage / spacing / cluster diagnostics for a city design.

Produces `{slug}-diagnose.png` next to the design.toml — a 4-panel plot:

1. Coverage heatmap: demand raster with cells coloured by distance to
   nearest station (green ≤ 500 m, yellow ≤ 1000 m, red > 1000 m,
   demand-weighted so unserved farmland is invisible).
2. Per-line demand profile: demand sampled along each line vs s_m,
   with vertical bars at station positions. Lets you see "stops in
   the middle of nowhere" (station on a low-demand stretch) and
   "missed neighbourhoods" (high-demand peaks with no nearby station).
3. Interchange cluster size: each junction_group plotted at its
   centroid, marker scaled by line count. Lets you see "clusters and
   overlaps" where 3+ stations clump within a few hundred metres.
4. Summary stats: total km, station count, covered-fraction,
   uncovered-high-demand bbox so you know roughly where to look.

Reads:
  * design.toml — for stations and lines
  * {slug}.corridor.geojson — for line geometry (cells via lat/lon)
  * {slug}.grid.json + .demand.npy from the raster cache
  * {slug}.stations.json — for junction_group + s_m fields

Usage:
    python -m osr_scenario.diagnose --design <design.toml> \
        --raster-dir <.cache/osr-pipeline/rasters>
"""

from __future__ import annotations

import argparse
import json
import math
import tomllib
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class GridRef:
    h: int
    w: int
    cell_m: float
    lat0: float
    bbox_south: float
    bbox_west: float
    m_per_deg_lat: float
    m_per_deg_lon: float

    @classmethod
    def load(cls, path: Path) -> "GridRef":
        d = json.loads(path.read_text())["grid"]
        return cls(
            h=d["height"], w=d["width"], cell_m=d["cell_m"],
            lat0=d["lat0"], bbox_south=d["bbox_south"], bbox_west=d["bbox_west"],
            m_per_deg_lat=d["m_per_deg_lat"], m_per_deg_lon=d["m_per_deg_lon"],
        )

    def latlon_to_rc(self, lat: float, lon: float) -> tuple[int, int]:
        # Mirrors osr_routing::raster::GridRef::latlon_to_rc — origin at
        # the SW corner, rows count north from south.
        y = (lat - self.bbox_south) * self.m_per_deg_lat
        x = (lon - self.bbox_west) * self.m_per_deg_lon
        c = int(round(x / self.cell_m))
        r = self.h - 1 - int(round(y / self.cell_m))
        return r, c


def diagnose(design_path: Path, raster_dir: Path, out_path: Path | None = None) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    doc = tomllib.loads(design_path.read_text())
    slug = (
        doc.get("design", {}).get("id")
        or doc.get("city", {}).get("slug")
        or "city"
    ).rsplit("/", 1)[-1].lower()

    grid_path = raster_dir / f"{slug}.grid.json"
    demand_path = raster_dir / f"{slug}.demand.npy"
    if not grid_path.exists():
        raise FileNotFoundError(f"missing {grid_path}")
    grid = GridRef.load(grid_path)
    demand = np.fromfile(demand_path, dtype=np.float32).reshape(grid.h, grid.w)

    stations_json = json.loads(
        (design_path.parent / f"{slug}.stations.json").read_text()
    )
    stations = stations_json if isinstance(stations_json, list) else stations_json.get("stations", [])

    corridor_path = design_path.parent / f"{slug}.corridor.geojson"
    sidecar = json.loads(corridor_path.read_text()) if corridor_path.exists() else {"features": []}

    # ---- Panel 1: coverage heatmap --------------------------------------
    # Distance² (in cells) to nearest station, computed cheaply by
    # rasterising station markers and using SciPy's EDT — falls back to
    # a brute O(n_stations × bin_pixels) loop on small grids without
    # SciPy. We only need rough rings, not exact distances.
    station_cells: list[tuple[int, int]] = []
    for s in stations:
        r, c = grid.latlon_to_rc(float(s["lat"]), float(s["lon"]))
        if 0 <= r < grid.h and 0 <= c < grid.w:
            station_cells.append((r, c))

    # Downsample for plotting speed — 4× decimation keeps Baghdad's
    # 2668×2976 grid plottable as ~667×744 pixels.
    decim = max(1, max(grid.h, grid.w) // 800)
    h_d, w_d = grid.h // decim, grid.w // decim
    demand_d = demand[: h_d * decim, : w_d * decim].reshape(h_d, decim, w_d, decim).max(axis=(1, 3))

    # For each downsampled cell, compute distance to nearest station (m).
    # A vectorised "for each station, update min distance" loop is
    # plenty fast for a few hundred stations × a few hundred-thousand
    # cells.
    rr, cc = np.meshgrid(np.arange(h_d), np.arange(w_d), indexing="ij")
    rr = rr.astype(np.float32) * decim
    cc = cc.astype(np.float32) * decim
    dist_m = np.full((h_d, w_d), np.inf, dtype=np.float32)
    for sr, sc in station_cells:
        d = np.sqrt((rr - sr) ** 2 + (cc - sc) ** 2) * grid.cell_m
        np.minimum(dist_m, d, out=dist_m)

    # Coverage classification (only matters where demand is non-trivial).
    HIGH_DEMAND_THR = 0.30
    COVERED_M = 600.0
    NEAR_M = 1200.0

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    ax = axes[0, 0]
    # Demand grayscale background.
    ax.imshow(demand_d, cmap="Greys", vmin=0.0, vmax=1.0, origin="upper")
    # Coverage overlay: only on high-demand cells. Green ≤ 600 m,
    # yellow ≤ 1200 m, red beyond.
    high = demand_d >= HIGH_DEMAND_THR
    overlay = np.zeros((h_d, w_d, 4), dtype=np.float32)
    covered = high & (dist_m <= COVERED_M)
    near = high & (dist_m > COVERED_M) & (dist_m <= NEAR_M)
    far = high & (dist_m > NEAR_M)
    overlay[covered] = (0.0, 0.7, 0.0, 0.55)
    overlay[near] = (1.0, 0.85, 0.0, 0.55)
    overlay[far] = (0.85, 0.0, 0.0, 0.65)
    ax.imshow(overlay, origin="upper")
    # Station markers.
    for sr, sc in station_cells:
        ax.plot(sc / decim, sr / decim, "o", markersize=2.5, color="#0033cc",
                markeredgecolor="white", markeredgewidth=0.4)
    n_high = int(high.sum())
    n_covered = int(covered.sum())
    n_near = int(near.sum())
    n_far = int(far.sum())
    cov_frac = n_covered / max(n_high, 1)
    ax.set_title(
        f"Coverage heatmap (slug={slug})\n"
        f"high-demand cells: {n_high:,} | covered ≤ {COVERED_M:.0f} m: "
        f"{n_covered:,} ({100 * cov_frac:.1f} %) | "
        f"near ≤ {NEAR_M:.0f} m: {n_near:,} | far: {n_far:,}"
    )
    ax.set_xticks([])
    ax.set_yticks([])

    # ---- Panel 2: per-line demand profile ------------------------------
    ax = axes[0, 1]
    # For each line in sidecar, sample demand at every cell along the
    # routed corridor, plot demand vs cumulative-m, overlay station
    # marks.
    line_features = [
        ft for ft in sidecar.get("features", [])
        if (ft.get("properties") or {}).get("kind") == "line"
    ]
    colour_cycle = ["#0033cc", "#cc0000", "#006600", "#663399", "#ff6600", "#009999"]
    for i, ft in enumerate(line_features):
        props = ft.get("properties", {}) or {}
        name = props.get("name") or props.get("id") or f"line-{i}"
        coords = ft.get("geometry", {}).get("coordinates") or []
        if len(coords) < 2:
            continue
        s_m = [0.0]
        demand_along = []
        prev_lat, prev_lon = coords[0][1], coords[0][0]
        r, c = grid.latlon_to_rc(prev_lat, prev_lon)
        demand_along.append(demand[max(0, min(grid.h - 1, r)), max(0, min(grid.w - 1, c))])
        for lon, lat in coords[1:]:
            # Cumulative metres using the grid's m-per-deg constants —
            # consistent with how the rust solver counts s_m.
            dlat_m = (lat - prev_lat) * grid.m_per_deg_lat
            dlon_m = (lon - prev_lon) * grid.m_per_deg_lon
            s_m.append(s_m[-1] + math.hypot(dlat_m, dlon_m))
            r, c = grid.latlon_to_rc(lat, lon)
            r = max(0, min(grid.h - 1, r))
            c = max(0, min(grid.w - 1, c))
            demand_along.append(demand[r, c])
            prev_lat, prev_lon = lat, lon
        colour = colour_cycle[i % len(colour_cycle)]
        ax.plot(np.array(s_m) / 1000.0, demand_along, color=colour, alpha=0.7, label=name, linewidth=1.2)
        # Station marks for this line.
        line_stations = [s for s in stations if s.get("line_name") == name]
        for s in line_stations:
            ax.axvline(float(s.get("s_m", 0.0)) / 1000.0, color=colour, alpha=0.35, linewidth=0.5)
    ax.set_xlabel("along-line distance (km)")
    ax.set_ylabel("demand")
    ax.set_title("Per-line demand profile (vertical = station). Stops on flat low-demand stretches = stops in nowhere.")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)

    # ---- Panel 3: interchange clusters --------------------------------
    ax = axes[1, 0]
    ax.imshow(demand_d, cmap="Greys", vmin=0.0, vmax=1.0, origin="upper")
    # Group stations by junction_group; non-grouped get group=None.
    groups: dict[int, list[dict]] = {}
    singletons: list[dict] = []
    for s in stations:
        jg = s.get("junction_group")
        if jg is None:
            singletons.append(s)
        else:
            groups.setdefault(int(jg), []).append(s)
    # Plot singletons small.
    for s in singletons:
        r, c = grid.latlon_to_rc(float(s["lat"]), float(s["lon"]))
        ax.plot(c / decim, r / decim, "o", markersize=2, color="#3366aa", alpha=0.6)
    # Plot groups: marker size scales with member count.
    for jg, members in sorted(groups.items()):
        # Centroid in grid coords.
        rs, cs = [], []
        for s in members:
            r, c = grid.latlon_to_rc(float(s["lat"]), float(s["lon"]))
            rs.append(r)
            cs.append(c)
        rc, cc_ = np.mean(rs), np.mean(cs)
        size = 4 + 4 * len(members)
        ax.plot(cc_ / decim, rc / decim, "o", markersize=size,
                color="#cc6600", markeredgecolor="black", markeredgewidth=0.8, alpha=0.85)
        ax.text(cc_ / decim + 4, rc / decim, f"{len(members)}", fontsize=7, color="black")
    n_groups = len(groups)
    largest = max((len(v) for v in groups.values()), default=0)
    ax.set_title(
        f"Interchange clusters: {n_groups} groups, largest = {largest} platforms.\n"
        f"Big amber dots = many lines meeting; clusters of small dots = unmerged near-misses."
    )
    ax.set_xticks([])
    ax.set_yticks([])

    # ---- Panel 4: summary text ----------------------------------------
    ax = axes[1, 1]
    ax.axis("off")
    total_km = sum(
        # Compute approximate route km from lines (sum of segment metres).
        sum(
            math.hypot(
                (coords[k + 1][1] - coords[k][1]) * grid.m_per_deg_lat,
                (coords[k + 1][0] - coords[k][0]) * grid.m_per_deg_lon,
            )
            for k in range(len(coords) - 1)
        )
        / 1000.0
        for ft in line_features
        for coords in [ft.get("geometry", {}).get("coordinates") or []]
        if len(coords) >= 2
    )
    text = [
        f"slug:           {slug}",
        f"lines:          {len(line_features)}",
        f"stations:       {len(stations)}",
        f"singleton stns: {len(singletons)}",
        f"junction grps:  {n_groups}",
        f"largest junction (platforms): {largest}",
        f"total route km: {total_km:.1f}",
        f"high-demand cells (decim): {n_high:,}",
        f"  covered (≤{COVERED_M:.0f} m): {100 * cov_frac:.1f} %",
        f"  near    (≤{NEAR_M:.0f} m):    {100 * n_near / max(n_high,1):.1f} %",
        f"  far     (>{NEAR_M:.0f} m):    {100 * n_far / max(n_high,1):.1f} %",
        "",
        "How to read:",
        "  Top-left  → are high-demand cells reached?",
        "  Top-right → does each line stop where the demand is?",
        "  Bot-left  → do lines actually meet at clean interchanges?",
    ]
    ax.text(0.0, 1.0, "\n".join(text), family="monospace", fontsize=11,
            verticalalignment="top", transform=ax.transAxes)

    fig.suptitle(f"OSR design diagnostic — {slug}", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out_path = out_path or design_path.parent / f"{slug}-diagnose.png"
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    return out_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="osr_scenario.diagnose")
    ap.add_argument("--design", type=Path, required=True, help="path to design.toml")
    ap.add_argument(
        "--raster-dir",
        type=Path,
        default=Path("/home/hayder/Documents/OpenSourceRail/.cache/osr-pipeline/rasters"),
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    out = diagnose(args.design, args.raster_dir, args.out)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

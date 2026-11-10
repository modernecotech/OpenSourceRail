#!/usr/bin/env python3
"""Render a route-only Baghdad comparison from the sealed study archive."""

from __future__ import annotations

import json
import math
import tarfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "results" / "equal-propulsion-attempt-05.tar.gz"
OUTPUT = ROOT / "route-comparison.svg"


def read_geojson(tf: tarfile.TarFile, relative: str) -> dict:
    member = tf.extractfile("attempt-05/" + relative)
    if member is None:
        raise SystemExit(f"missing route artifact: {relative}")
    return json.load(member)


def xy(point: list[float], lon0: float, lat0: float) -> tuple[float, float]:
    lon, lat = point
    return ((lon-lon0)*111_320*math.cos(math.radians(lat0)), (lat-lat0)*111_320)


def features(data: dict):
    lines = {feature["properties"]["line_id"]: feature for feature in data["features"]
             if feature.get("geometry", {}).get("type") == "LineString"}
    stations = [feature for feature in data["features"]
                if feature.get("geometry", {}).get("type") == "Point"
                and feature.get("properties", {}).get("role") == "operational-shared-station-complex"]
    return lines, stations


def main() -> None:
    with tarfile.open(ARCHIVE, "r:gz") as tf:
        baseline_label = "baseline-published-anchor-preserving-chord-research-powered-axle"
        revised_label = "simplified-radials-from-published-baseline"
        baseline = read_geojson(tf, f"studies/{baseline_label}/alignments.geojson")
        revised = read_geojson(tf, f"studies/{revised_label}/alignments.geojson")
        baseline_plan = json.load(tf.extractfile(f"attempt-05/studies/{baseline_label}/planning.json"))
        revised_plan = json.load(tf.extractfile(f"attempt-05/studies/{revised_label}/planning.json"))
    line_sets = [features(data) for data in (baseline, revised)]
    if set(line_sets[0][0]) != set(line_sets[1][0]) or len(line_sets[0][0]) != 14:
        raise SystemExit("route cases must retain the same fourteen lines")
    station_identity = lambda row: (row["properties"]["stop_id"], tuple(row["geometry"]["coordinates"]))
    baseline_stations = {station_identity(row) for row in line_sets[0][1]}
    revised_stations = {station_identity(row) for row in line_sets[1][1]}
    if baseline_stations != revised_stations or len(baseline_stations) != 157:
        raise SystemExit("operational stop identities/coordinates differ or count is unexpected")
    if line_sets[0][0]["line-9"]["geometry"]["coordinates"] != line_sets[1][0]["line-9"]["geometry"]["coordinates"]:
        raise SystemExit("ring line 9 changed in a radial-only route comparison")
    baseline_km = sum(row["length_m"] for row in baseline_plan["lines"])/1000
    revised_km = sum(row["length_m"] for row in revised_plan["lines"])/1000
    change_pct = (revised_km/baseline_km-1)*100
    all_points = [point for lines, _ in line_sets for feature in lines.values()
                  for point in feature["geometry"]["coordinates"]]
    lon0 = sum(p[0] for p in all_points)/len(all_points)
    lat0 = sum(p[1] for p in all_points)/len(all_points)
    palette = plt.get_cmap("tab20")
    line_ids = sorted(line_sets[0][0], key=lambda value: int(value.split("-")[1]))
    colors = {line_id: palette(index/20) for index, line_id in enumerate(line_ids)}

    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    fig, axes = plt.subplots(1, 2, figsize=(15.2, 8.4), facecolor="#f5f7f6")
    fig.subplots_adjust(left=.05, right=.95, top=.69, bottom=.20, wspace=.12)
    fig.text(.05, .94, "BAGHDAD  /  ROUTE SENSITIVITY", fontsize=10, weight="bold", color="#637177")
    fig.text(.05, .875, "Published radial routes simplified; ring unchanged", fontsize=22, weight="bold", color="#142c36")
    fig.text(.05, .82, f"14 lines · {len(baseline_stations)} operational stop coordinates · common powered-axle research overlay",
             fontsize=10.2, color="#52656d")
    panel_titles = ("CURRENT PUBLISHED GEOMETRY", "RADIAL SENSITIVITY")
    panel_lengths = (f"{baseline_km:.3f} km total", f"{revised_km:.3f} km total  ·  {change_pct:+.2f}%")
    for ax, (lines, stations), title, length in zip(axes, line_sets,
            panel_titles, panel_lengths):
        ax.set_facecolor("#f5f7f6")
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_axis_off()
        ax.text(.01, 1.065, title, transform=ax.transAxes, fontsize=10, weight="bold", color="#1d3945")
        ax.text(.01, 1.015, length, transform=ax.transAxes, fontsize=9, color="#65777d")
        for line_id in line_ids:
            feature = lines[line_id]
            points = [xy(p, lon0, lat0) for p in feature["geometry"]["coordinates"]]
            xs, ys = zip(*points)
            ax.plot(xs, ys, color=colors[line_id], linewidth=1.55, alpha=.94,
                    solid_capstyle="round", zorder=2)
        for feature in stations:
            point = xy(feature["geometry"]["coordinates"], lon0, lat0)
            ax.scatter([point[0]], [point[1]], s=8, c="#f5f7f6", edgecolors="#2c4149",
                       linewidths=.45, zorder=4)
        ax.margins(x=.055, y=.085)

    handles = [plt.Line2D([0], [0], color=colors[line_id], lw=2,
                           label=f"Line {line_id.split('-')[1]}") for line_id in line_ids]
    handles.append(plt.Line2D([0], [0], marker="o", color="none", markerfacecolor="#f5f7f6",
                              markeredgecolor="#2c4149", markersize=4, label="Station marker"))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .105), ncol=8,
               frameon=False, fontsize=8.3, handlelength=1.5, columnspacing=1.4)
    fig.text(.05, .025,
             "13 radial lines use 5 m bidirectional samples and a 20 m deviation sensitivity; the 26-stop ring line 9 is unchanged.\n"
             "Route-only drawing, not a basemap or survey. No additional stop merging, access, obstacle, utility or clearance review is included.",
             fontsize=8, color="#52656d", va="bottom", linespacing=1.4)
    fig.savefig(OUTPUT, format="svg", facecolor=fig.get_facecolor(),
                metadata={"Title": "Baghdad route geometry sensitivity"})
    print(OUTPUT)


if __name__ == "__main__":
    main()

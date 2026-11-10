#!/usr/bin/env python3
"""Render a compact route-only SVG comparison from the sealed study archive."""

from __future__ import annotations

import json
import math
import tarfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "results" / "equal-propulsion-attempt-02.tar.gz"
OUTPUT = ROOT / "route-comparison.svg"
COLORS = ("#246b85", "#cb5a46", "#54896d", "#8c6ca8", "#bc8a27")


def read_geojson(tf: tarfile.TarFile, relative: str) -> dict:
    member = tf.extractfile("attempt-02/" + relative)
    if member is None:
        raise SystemExit(f"missing route artifact: {relative}")
    return json.load(member)


def xy(point: list[float], lon0: float, lat0: float) -> tuple[float, float]:
    lon, lat = point
    return ((lon - lon0) * 111_320 * math.cos(math.radians(lat0)),
            (lat - lat0) * 111_320)


def main() -> None:
    with tarfile.open(ARCHIVE, "r:gz") as tf:
        baseline = read_geojson(tf, "studies/baseline-fixed-powered-axle/alignments.geojson")
        revised = read_geojson(tf, "studies/simplified-route-fixed-powered-axle/alignments.geojson")

    datasets = (baseline, revised)
    line_features = [
        {f["properties"]["line_id"]: f for f in data["features"]
         if f.get("geometry", {}).get("type") == "LineString"}
        for data in datasets
    ]
    station_features = [
        [f for f in data["features"]
         if f.get("geometry", {}).get("type") == "Point"
         and f.get("properties", {}).get("role") == "operational-shared-station-complex"]
        for data in datasets
    ]
    all_coords = [coord for routes in line_features for feature in routes.values()
                  for coord in feature["geometry"]["coordinates"]]
    lon0 = sum(point[0] for point in all_coords) / len(all_coords)
    lat0 = sum(point[1] for point in all_coords) / len(all_coords)

    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 7.2), facecolor="#f5f7f6")
    fig.subplots_adjust(left=.045, right=.955, top=.70, bottom=.16, wspace=.13)
    fig.text(.05, .94, "SAMAWAH  /  ROUTE SENSITIVITY", fontsize=10, weight="bold", color="#637177")
    fig.text(.05, .875, "Shorter paths, same station markers", fontsize=25, weight="bold", color="#142c36")
    fig.text(.05, .825, "Five lines · common propulsion and planning inputs · route geometry and downstream service recalculated",
             fontsize=10.5, color="#52656d")

    titles = ("PUBLISHED OUTLINE", "SAMPLED STRAIGHTENING")
    lengths = ("57.873 km total", "54.608 km total  ·  −5.64%")
    for panel, (ax, routes, stations, title, length) in enumerate(zip(axes, line_features, station_features, titles, lengths)):
        ax.set_facecolor("#f5f7f6")
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_axis_off()
        ax.text(.01, 1.065, title, transform=ax.transAxes, fontsize=10, weight="bold", color="#1d3945")
        ax.text(.01, 1.015, length, transform=ax.transAxes, fontsize=9, color="#65777d")
        for index, line_id in enumerate(sorted(routes)):
            feature = routes[line_id]
            points = [xy(p, lon0, lat0) for p in feature["geometry"]["coordinates"]]
            xs, ys = zip(*points)
            ax.plot(xs, ys, color=COLORS[index], linewidth=2.45, solid_capstyle="round", zorder=2,
                    label=f"Line {index + 1}")
            if panel == 1:
                ax.text(xs[-1], ys[-1], f"  L{index + 1}", fontsize=7.5, color=COLORS[index],
                        weight="bold", va="center", zorder=5)
        for feature in stations:
            point = xy(feature["geometry"]["coordinates"], lon0, lat0)
            ax.scatter([point[0]], [point[1]], s=18, c="#f5f7f6", edgecolors="#1d3945",
                       linewidths=.9, zorder=4)
        ax.margins(x=.09, y=.12)

    # One compact legend, separated from the geographic strokes.
    handles = [plt.Line2D([0], [0], color=COLORS[i], lw=2.5, label=f"Line {i + 1}") for i in range(5)]
    handles.append(plt.Line2D([0], [0], marker="o", color="none", markerfacecolor="#f5f7f6",
                              markeredgecolor="#1d3945", markersize=5, label="Station marker"))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .075), ncol=6,
               frameon=False, fontsize=8.5, handlelength=1.7, columnspacing=1.8)
    fig.text(.05, .025,
             "Station markers are retained. 20 m sampled deviation screen (maximum observed: 19.345 m).\n"
             "Route-only drawing; no surveyed basemap, right-of-way, obstacle, utility or accessibility validation. Not a selected alignment.",
             fontsize=8, color="#52656d", va="bottom", linespacing=1.45)
    fig.savefig(OUTPUT, format="svg", facecolor=fig.get_facecolor(), metadata={"Title": "Samawah route geometry sensitivity"})
    print(OUTPUT)


if __name__ == "__main__":
    main()

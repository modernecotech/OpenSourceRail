#!/usr/bin/env python3
"""Render current QGIS-layer and SUMO-result evidence for a city README."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import tomllib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


REPO_ROOT = Path(__file__).resolve().parents[1]
COLORS = ["#00a6a6", "#ffb000", "#ef476f", "#7b61ff", "#2a9d8f", "#e76f51", "#457b9d"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def features(path: Path) -> list[dict]:
    return load_json(path).get("features", [])


def coordinates(feature: dict) -> tuple[list[float], list[float]]:
    value = feature["geometry"]["coordinates"]
    if feature["geometry"]["type"] == "Point":
        return [value[0]], [value[1]]
    return [point[0] for point in value], [point[1] for point in value]


def validate_sources(design_path: Path) -> tuple[str, Path, dict, dict, dict]:
    design = tomllib.loads(design_path.read_text(encoding="utf-8"))
    slug = str(design["city"]["slug"])
    city_dir = design_path.parent
    scenario_path = city_dir / f"{slug}.toml"
    corridor_path = city_dir / f"{slug}.corridor.geojson"
    engineering = city_dir / "engineering"
    sumo = load_json(engineering / "sumo/summary.json")
    gis = load_json(engineering / "gis/summary.json")
    energy = load_json(engineering / "energy/summary.json")
    expected = {
        "design_sha256": sha256(design_path),
        "corridor_sha256": sha256(corridor_path),
        "scenario_sha256": sha256(scenario_path),
    }
    errors: list[str] = []
    if not sumo.get("simulation_passed") or sumo.get("design_sha256") != expected["design_sha256"] or sumo.get("corridor_sha256") != expected["corridor_sha256"]:
        errors.append("SUMO result is failed or stale")
    if not gis.get("generation_passed") or any(gis.get(key) != value for key, value in expected.items()):
        errors.append("QGIS/GDAL result is failed or stale")
    if not energy.get("solver_passed") or energy.get("design_sha256") != expected["design_sha256"] or energy.get("scenario_sha256") != expected["scenario_sha256"]:
        errors.append("energy result is failed or stale")
    if errors:
        raise RuntimeError(f"{slug}: " + "; ".join(errors))
    return slug, scenario_path, sumo, gis, energy


def render_qgis(city_dir: Path, slug: str, gis: dict, output: Path) -> None:
    layers = city_dir / "engineering/gis/layers"
    corridors = features(layers / "corridors.geojson")
    civil = features(layers / "civil_segments.geojson")
    stations = features(layers / "stations.geojson")
    interchange_path = layers / "interchanges.geojson"
    interchanges = features(interchange_path) if interchange_path.is_file() else []
    depots = features(layers / "depots.geojson")
    sites = features(layers / "energy_sites.geojson")

    fig, ax = plt.subplots(figsize=(14, 9), dpi=150, facecolor="#07131f")
    ax.set_facecolor("#0b1f2f")
    line_ids = sorted(
        {
            str(
                f.get("properties", {}).get("line")
                or f.get("properties", {}).get("name")
                or ""
            )
            for f in corridors
        }
    )
    palette = {line: COLORS[i % len(COLORS)] for i, line in enumerate(line_ids)}
    for feature in civil:
        xs, ys = coordinates(feature)
        props = feature.get("properties", {})
        style = str(
            props.get("civil_class", props.get("civil_type", props.get("classification", "at-grade")))
        )
        linestyle = "--" if "elev" in style or "bridge" in style else "-"
        ax.plot(xs, ys, color=palette.get(str(props.get("line", "")), "#8da9bd"), linewidth=3.2, linestyle=linestyle, alpha=0.88, zorder=2)
    if not civil:
        for feature in corridors:
            xs, ys = coordinates(feature)
            props = feature.get("properties", {})
            line = str(props.get("line") or props.get("name") or "")
            ax.plot(xs, ys, color=palette.get(line, "#8da9bd"), linewidth=3.2, zorder=2)
    for feature in stations:
        if feature.get("properties", {}).get("junction_group") is not None:
            continue
        xs, ys = coordinates(feature)
        ax.scatter(xs, ys, s=18, facecolor="#f4f7f9", edgecolor="#07131f", linewidth=0.5, zorder=4)
    for feature in interchanges:
        xs, ys = coordinates(feature)
        ax.scatter(xs, ys, s=92, marker="D", facecolor="#a66cff", edgecolor="white", linewidth=1.1, zorder=7)
    for feature in sites:
        xs, ys = coordinates(feature)
        ax.scatter(xs, ys, s=28, marker="^", facecolor="#ffd166", edgecolor="#07131f", linewidth=0.6, alpha=0.9, zorder=5)
    for feature in depots:
        xs, ys = coordinates(feature)
        ax.scatter(xs, ys, s=72, marker="s", facecolor="#ef476f", edgecolor="white", linewidth=0.8, zorder=6)

    all_x = [x for f in corridors for x in coordinates(f)[0]]
    all_y = [y for f in corridors for y in coordinates(f)[1]]
    if all_x and all_y:
        ax.set_aspect(1 / max(0.2, abs(__import__("math").cos(__import__("math").radians(sum(all_y) / len(all_y))))))
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors="#8da9bd", labelsize=8)
    ax.grid(color="#27485e", linewidth=0.5, alpha=0.45)
    ax.set_xlabel("Longitude · EPSG:4326", color="#8da9bd")
    ax.set_ylabel("Latitude", color="#8da9bd")
    ax.set_title(f"{slug.replace('-', ' ').title()} · QGIS-validated engineering layers", loc="left", color="white", fontsize=20, fontweight="bold", pad=18)
    ax.text(0, 1.01, f"{gis['layers'].get('corridors', 0)} corridors · {gis['layers'].get('stations', 0)} line platforms · {gis['layers'].get('interchanges', 0)} interchange complexes · {gis['layers'].get('civil_segments', 0)} civil segments · GeoPackage PASS", transform=ax.transAxes, color="#9fc3d5", fontsize=10)
    handles = [Line2D([0], [0], color=palette[line], lw=4, label=line) for line in line_ids]
    handles += [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white", label="Station"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor="#a66cff", markeredgecolor="white", label="Interchange complex"),
        Line2D([0], [0], marker="^", color="none", markerfacecolor="#ffd166", label="Energy site"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="#ef476f", label="Depot"),
    ]
    legend = ax.legend(handles=handles, loc="best", frameon=True, facecolor="#0b1f2f", edgecolor="#36586d", fontsize=8)
    for text in legend.get_texts():
        text.set_color("white")
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def render_sumo(slug: str, sumo: dict, energy: dict, output: Path) -> None:
    lines = sumo.get("lines", [])
    names = [str(line["line"]) for line in lines]
    durations = [float(line.get("mean_trip_duration_s", 0)) / 60 for line in lines]
    lengths = [float(line.get("modeled_length_m", 0)) / 1000 for line in lines]
    colors = [COLORS[i % len(COLORS)] for i in range(len(lines))]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), dpi=150, facecolor="#07131f", gridspec_kw={"width_ratios": [1.45, 1]})
    for ax in (ax1, ax2):
        ax.set_facecolor("#0b1f2f")
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(colors="#aec6d4")
        ax.grid(axis="x", color="#27485e", linewidth=0.6, alpha=0.55)
    y = list(range(len(lines)))
    ax1.barh(y, durations, color=colors, height=0.62)
    ax1.set_yticks(y, names, color="white")
    ax1.invert_yaxis()
    ax1.set_xlabel("Mean end-to-end journey (minutes)", color="#aec6d4")
    for index, (duration, length) in enumerate(zip(durations, lengths)):
        ax1.text(duration + max(durations or [1]) * 0.015, index, f"{duration:.1f} min · {length:.1f} km", va="center", color="white", fontsize=8)
    cases = energy.get("cases", {})
    labels = ["Services arrived", "Input checks clear", "Grid-only loading", "Coordinated loading"]
    values = [
        100 * float(sumo.get("arrived_services", 0)) / max(1, float(sumo.get("scheduled_services", 0))),
        100.0 if not sumo.get("input_issues") else 0.0,
        float(cases.get("peak_charge_grid_only", {}).get("maximum_transformer_loading_percent", 0)),
        float(cases.get("coordinated_daylight", {}).get("maximum_transformer_loading_percent", 0)),
    ]
    status_colors = ["#06d6a0" if value <= 100 else "#ef476f" for value in values]
    ax2.barh(range(4), values, color=status_colors, height=0.58)
    ax2.set_yticks(range(4), labels, color="white")
    ax2.invert_yaxis()
    ax2.set_xlim(0, max(110, max(values) * 1.15))
    ax2.set_xlabel("Percent", color="#aec6d4")
    for index, value in enumerate(values):
        ax2.text(value + 2, index, f"{value:.1f}%", va="center", color="white", fontsize=9)
    fig.suptitle(f"{slug.replace('-', ' ').title()} · SUMO executed timetable validation", x=0.04, ha="left", color="white", fontsize=20, fontweight="bold")
    fig.text(0.04, 0.91, f"{sumo.get('arrived_services', 0)}/{sumo.get('scheduled_services', 0)} services arrived · {len(lines)} lines · {sumo.get('station_count', 0)} stations · status {sumo.get('simulation_status', 'unknown').upper()}", color="#9fc3d5", fontsize=10)
    fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.88))
    fig.savefig(output, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    args = parser.parse_args()
    design_path = args.design.resolve()
    slug, scenario_path, sumo, gis, energy = validate_sources(design_path)
    city_dir = design_path.parent
    output_dir = city_dir / "engineering/screenshots"
    output_dir.mkdir(parents=True, exist_ok=True)
    qgis_path = output_dir / f"{slug}-qgis-engineering-map.png"
    sumo_path = output_dir / f"{slug}-sumo-validation.png"
    render_qgis(city_dir, slug, gis, qgis_path)
    render_sumo(slug, sumo, energy, sumo_path)
    sources = {
        "design_sha256": sha256(design_path),
        "scenario_sha256": sha256(scenario_path),
        "sumo_summary_sha256": sha256(city_dir / "engineering/sumo/summary.json"),
        "gis_summary_sha256": sha256(city_dir / "engineering/gis/summary.json"),
        "energy_summary_sha256": sha256(city_dir / "engineering/energy/summary.json"),
    }
    atomic_json(output_dir / "manifest.json", {
        "city": slug,
        "generator": str(Path(__file__).relative_to(REPO_ROOT)),
        "generator_sha256": sha256(Path(__file__)),
        "passed": True,
        "sources": sources,
        "screenshots": {
            "qgis_engineering_map": {"path": qgis_path.name, "sha256": sha256(qgis_path)},
            "sumo_validation": {"path": sumo_path.name, "sha256": sha256(sumo_path)},
        },
    })
    print(f"rendered {qgis_path}")
    print(f"rendered {sumo_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

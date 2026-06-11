#!/usr/bin/env python3
"""Generate current simulator screenshots for the README and PDF book."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIO = REPO_ROOT / "designs/west-asia/Iraq/Samawah/samawah.toml"
DEFAULT_OUT_DIR = REPO_ROOT / "docs/screenshots/simulation"
BUILD_DIR = REPO_ROOT / "build/sim-screenshots"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def chrome_bin() -> str:
    for name in ("google-chrome", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError("headless Chrome/Chromium is required to capture the visualizer PNG")


def capture_visualizer(scenario: Path, out_dir: Path) -> Path:
    html_path = BUILD_DIR / "samawah-network-visualizer.html"
    png_path = out_dir / "samawah-network-visualizer.png"
    run(
        [
            "cargo",
            "run",
            "-p",
            "osr-sim",
            "--bin",
            "osr-vis",
            "--",
            "--config",
            str(scenario),
            "--out",
            str(html_path),
        ]
    )
    run(
        [
            chrome_bin(),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--window-size=1600,1000",
            f"--screenshot={png_path}",
            html_path.resolve().as_uri(),
        ]
    )
    return png_path


def run_sim_trace(scenario: Path, duration_s: int) -> tuple[Path, Path]:
    csv_path = BUILD_DIR / "samawah-sim.csv"
    json_path = BUILD_DIR / "samawah-sim.json"
    run(
        [
            "cargo",
            "run",
            "-p",
            "osr-sim",
            "--bin",
            "osr-sim",
            "--",
            "--config",
            str(scenario),
            "--duration",
            str(duration_s),
            "--status-every",
            "0",
            "--csv-out",
            str(csv_path),
            "--csv-every",
            "60",
            "--json-out",
            str(json_path),
            "--ma-check-every",
            "0",
        ]
    )
    return csv_path, json_path


def plot_dashboard(csv_path: Path, json_path: Path, out_dir: Path) -> Path:
    png_path = out_dir / "samawah-simulation-dashboard.png"
    frame = pd.read_csv(csv_path)
    frame["time_h"] = frame["sim_time_s"] / 3600.0
    grouped = frame.groupby("time_h")

    energy = grouped[
        ["energy_consumed_kwh", "energy_charged_kwh", "roof_pv_charged_kwh"]
    ].sum()
    soc = grouped["soc"].agg(["min", "median", "max"])
    power = grouped[
        [
            "battery_draw_power_kw",
            "station_charge_power_kw",
        ]
    ].sum()
    roof_power = grouped[["roof_pv_kw", "roof_pv_cleaner_power_kw"]].sum()
    motion_frame = frame[frame["section_speed_mps"] > 0.05]
    motion = motion_frame.groupby("time_h").agg(
        mean_speed_kmh=("section_speed_mps", lambda s: (s * 3.6).mean()),
        max_speed_kmh=("section_speed_mps", lambda s: (s * 3.6).max()),
        max_accel_mps2=("section_accel_mps2", "max"),
        min_accel_mps2=("section_accel_mps2", "min"),
    )
    motion = motion.reindex(energy.index).ffill().fillna(0.0)

    with json_path.open() as fh:
        summary = json.load(fh)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig = plt.figure(figsize=(16, 12), dpi=120)
    grid = fig.add_gridspec(3, 2, hspace=0.34, wspace=0.2)
    ax_energy = fig.add_subplot(grid[0, 0])
    ax_soc = fig.add_subplot(grid[0, 1])
    ax_power = fig.add_subplot(grid[1, 0])
    ax_roof = fig.add_subplot(grid[1, 1])
    ax_motion = fig.add_subplot(grid[2, :])

    ax_energy.plot(
        energy.index,
        energy["energy_consumed_kwh"],
        label="Fleet energy used",
        color="#2f3a8f",
        linewidth=2.4,
    )
    ax_energy.plot(
        energy.index,
        energy["energy_charged_kwh"],
        label="All charging credited",
        color="#1b8a5a",
        linewidth=2.4,
    )
    ax_energy.plot(
        energy.index,
        energy["roof_pv_charged_kwh"],
        label="Roof PV credited",
        color="#d99000",
        linewidth=2.4,
    )
    ax_energy.set_title("Cumulative Energy")
    ax_energy.set_xlabel("Simulation time (h)")
    ax_energy.set_ylabel("kWh")
    ax_energy.legend(loc="upper left")

    ax_soc.fill_between(
        soc.index,
        soc["min"],
        soc["max"],
        color="#a9c9ff",
        alpha=0.35,
        label="min-max",
    )
    ax_soc.plot(
        soc.index,
        soc["median"],
        color="#2451a6",
        linewidth=2.4,
        label="median",
    )
    ax_soc.plot(
        soc.index,
        soc["min"],
        color="#be3a34",
        linewidth=1.8,
        label="minimum",
    )
    ax_soc.set_title("Fleet Battery State Of Charge")
    ax_soc.set_xlabel("Simulation time (h)")
    ax_soc.set_ylabel("SoC fraction")
    ax_soc.set_ylim(0, 1.02)
    ax_soc.legend(loc="lower left")

    ax_power.plot(
        power.index,
        power["battery_draw_power_kw"],
        label="Battery draw",
        color="#6b3fa0",
        linewidth=2.0,
    )
    ax_power.plot(
        power.index,
        power["station_charge_power_kw"],
        label="Platform charging",
        color="#1b8a5a",
        linewidth=2.0,
    )
    ax_power.set_title("Fleet Traction And Charging Power")
    ax_power.set_xlabel("Simulation time (h)")
    ax_power.set_ylabel("kW")
    ax_power.legend(loc="upper left")

    ax_roof.plot(
        roof_power.index,
        roof_power["roof_pv_kw"],
        label="Net roof PV",
        color="#d99000",
        linewidth=2.2,
    )
    ax_roof.plot(
        roof_power.index,
        roof_power["roof_pv_cleaner_power_kw"],
        label="PV cleaner load",
        color="#60656f",
        linewidth=2.0,
    )
    ax_roof.set_title("Roof Solar And Air Cleaner")
    ax_roof.set_xlabel("Simulation time (h)")
    ax_roof.set_ylabel("kW")
    ax_roof.legend(loc="upper left")

    ax_motion.plot(
        motion.index,
        motion["max_speed_kmh"],
        label="max train speed",
        color="#2451a6",
        linewidth=2.2,
    )
    ax_motion.plot(
        motion.index,
        motion["mean_speed_kmh"],
        label="mean moving speed",
        color="#1b8a5a",
        linewidth=2.0,
    )
    ax_motion.set_title("Motion Profile")
    ax_motion.set_xlabel("Simulation time (h)")
    ax_motion.set_ylabel("km/h")
    ax_motion_accel = ax_motion.twinx()
    ax_motion_accel.plot(
        motion.index,
        motion["max_accel_mps2"],
        label="max acceleration",
        color="#d99000",
        linewidth=1.6,
        alpha=0.9,
    )
    ax_motion_accel.plot(
        motion.index,
        motion["min_accel_mps2"],
        label="max braking",
        color="#be3a34",
        linewidth=1.6,
        alpha=0.9,
    )
    ax_motion_accel.set_ylabel("m/s2")
    motion_lines, motion_labels = ax_motion.get_legend_handles_labels()
    accel_lines, accel_labels = ax_motion_accel.get_legend_handles_labels()
    ax_motion.legend(
        motion_lines + accel_lines,
        motion_labels + accel_labels,
        loc="upper right",
        ncol=4,
    )

    duration = max(frame["sim_time_s"]) / 3600.0
    title = (
        "Samawah simulation trace: motion, dwell, charging, roof PV, "
        "and battery state"
    )
    subtitle = (
        f"{duration:.1f} h run, {frame['train_id'].nunique()} trainsets, "
        f"{summary.get('total_train_km', 0.0):.1f} train-km, "
        f"{summary.get('total_energy_consumed_kwh', 0.0):.1f} kWh consumed"
    )
    fig.suptitle(title, fontsize=18, fontweight="bold", x=0.04, ha="left")
    fig.text(0.04, 0.925, subtitle, fontsize=11, color="#4b5563")
    fig.text(
        0.04,
        0.035,
        "Generated by scripts/render-sim-screenshots.py from osr-sim CSV output.",
        fontsize=9,
        color="#6b7280",
    )
    fig.savefig(png_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return png_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, default=DEFAULT_SCENARIO)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--duration", type=int, default=7200)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    visualizer = capture_visualizer(args.scenario, args.out_dir)
    csv_path, json_path = run_sim_trace(args.scenario, args.duration)
    dashboard = plot_dashboard(csv_path, json_path, args.out_dir)
    print(visualizer.relative_to(REPO_ROOT))
    print(dashboard.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

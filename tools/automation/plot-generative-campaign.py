#!/usr/bin/env python3
"""Plot actual campaign variations without implying complete design acceptance."""

import argparse
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.generative_design.campaign import verify, write
from engineering.generative_design.coverage import sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    verify(args.campaign)
    if args.output.exists() or args.output.with_suffix(".json").exists():
        raise ValueError("figure publication needs fresh output paths")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def read(name):
        return json.loads((args.campaign / name).read_text())

    civil, mechanical = read("civil/search.json"), read("mechanical/search.json")
    coupled, ledger = read("bed-coupling.json"), read("closure-ledger.json")
    plt.rcParams["svg.hashsalt"] = "osr-generative-campaign-1"
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), layout="constrained")
    colours = {True: "#247878", False: "#bb6553"}
    for feasible in (False, True):
        rows = [r for r in civil["candidates"] if r["conditional_feasible"] == feasible]
        axes[0, 0].scatter(
            [r["metrics"]["initial_bed_force_n"] / 1e6 for r in rows],
            [r["metrics"]["minimum_service_compression_pa"] / 1e6 for r in rows],
            s=14,
            alpha=0.5,
            color=colours[feasible],
            label=(
                "Local research screens passed"
                if feasible
                else "One or more local screens failed"
            ),
        )
        rows = [
            r
            for r in mechanical["candidates"]
            if r["conditional_screen_feasible"] == feasible
        ]
        axes[0, 1].scatter(
            [r["metrics"]["gross_blank_and_component_mass_kg"] for r in rows],
            [r["metrics"]["nominal_strip_deflection_m"] * 1e6 for r in rows],
            s=14,
            alpha=0.5,
            color=colours[feasible],
        )
    for report, ax, x, y, xscale, yscale in (
        (
            civil,
            axes[0, 0],
            "initial_bed_force_n",
            "minimum_service_compression_pa",
            1e-6,
            1e-6,
        ),
        (
            mechanical,
            axes[0, 1],
            "gross_blank_and_component_mass_kg",
            "nominal_strip_deflection_m",
            1,
            1e6,
        ),
    ):
        rows = [
            r
            for r in report["candidates"]
            if r["id"] in report["selected_candidate_ids"]
        ]
        ax.scatter(
            [r["metrics"][x] * xscale for r in rows],
            [r["metrics"][y] * yscale for r in rows],
            marker="D",
            facecolors="none",
            edgecolors="#142737",
            s=100,
            linewidths=1.5,
            label="Selected for native geometry",
        )
    axes[0, 0].axhline(0, color="#333333", linestyle="--", linewidth=1)
    axes[0, 0].set(
        title=f'Civil: {len(civil["candidates"])} declared combinations',
        xlabel="Initial stressing-bed force [MN]",
        ylabel="Minimum sampled service compression [MPa]",
    )
    axes[0, 0].legend(fontsize=8)
    axes[0, 1].set(
        title=f'Mechanical: {len(mechanical["candidates"])} feedback candidates',
        xlabel="Gross blank and component mass [kg]",
        ylabel="Ideal strip deflection [µm]",
        yscale="log",
    )
    axes[0, 1].axhline(
        10, color="#333333", linestyle="--", linewidth=1, label="10 µm research target"
    )
    axes[0, 1].legend(fontsize=8)
    beam = (
        coupled["candidates"][0]["variables"]["beam"] if coupled["candidates"] else None
    )
    for spring in (1e5, 1e6, 1e7):
        rows = [
            r
            for r in coupled["candidates"]
            if r["variables"]["beam"] == beam
            and r["variables"]["hypothetical_spring_n_m"] == spring
        ]
        axes[1, 0].plot(
            [r["variables"]["wall_m"] * 1000 for r in rows],
            [r["minimum_elastic_eigenvalue_factor"] for r in rows],
            marker="o",
            label=f"{spring/1e6:g} MN/m hypothetical springs",
        )
    axes[1, 0].axhline(
        1, color="#bb6553", linestyle="--", label="Numerical stability boundary"
    )
    force = (
        coupled["candidates"][0]["initial_bed_force_n"] / 1e6
        if coupled["candidates"]
        else None
    )
    axes[1, 0].set(
        title=(
            f"{force:g} MN beam force → two axial return rails"
            if force is not None
            else "No civil selection for bed coupling"
        ),
        xlabel="Proposed return-rail wall [mm]",
        ylabel="Smallest elastic eigenvalue factor",
    )
    axes[1, 0].legend(fontsize=8)
    labels = [
        "Representative exploration",
        "Needs discipline model",
        "Manufacturing release",
    ]
    values = [
        ledger["counts"].get("representative-partial", 0),
        ledger["counts"].get("requires-discipline-model", 0),
        ledger["completed_packages"],
    ]
    bars = axes[1, 1].barh(labels, values, color=["#247878", "#b58a48", "#142737"])
    axes[1, 1].bar_label(bars, padding=4)
    axes[1, 1].set(
        title=f'{len(ledger["work_packages"])} work packages: inventory covered, closure open',
        xlabel="Work packages",
        xlim=(0, max(1, len(ledger["work_packages"]))),
    )
    for ax in axes.flat:
        ax.grid(alpha=0.2)
        ax.set_axisbelow(True)
    fig.suptitle(
        "Multi-agent generative design · research variations and explicit open manufacturing gates"
    )
    out = io.StringIO()
    fig.savefig(
        out,
        format="svg",
        metadata={"Date": None, "Creator": "OpenSourceRail generative campaign"},
    )
    plt.close(fig)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(line.rstrip() for line in out.getvalue().splitlines()) + "\n"
    )
    write(
        args.output.with_suffix(".json"),
        dict(
            schema="osr-generative-figure/1",
            parent_campaign_receipt_sha256=sha(args.campaign / "receipt.json"),
            plotter_sha256=sha(__file__),
            figure_sha256=sha(args.output),
            matplotlib=matplotlib.__version__,
            inputs_sha256={
                name: sha(args.campaign / name)
                for name in (
                    "civil/search.json",
                    "mechanical/search.json",
                    "bed-coupling.json",
                    "closure-ledger.json",
                )
            },
            physical_release=False,
        ),
    )
    print(args.output)


if __name__ == "__main__":
    main()

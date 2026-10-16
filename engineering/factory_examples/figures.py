"""Deterministic standalone engineering figures for the factory development."""

from __future__ import annotations

import io


def development_svg(report):
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    with matplotlib.rc_context(
        {"svg.hashsalt": "osr-factory-development-2", "font.size": 9}
    ):
        fig, axes = plt.subplots(2, 2, figsize=(12, 7.5), layout="constrained")
        fig.suptitle(
            "Baghdad factory development — numerical research screens", fontsize=15
        )
        prestress = report["prestress"]
        colours = {
            "low-40": "#a34d37",
            "balanced-40": "#5f6e83",
            "balanced-48": "#14715e",
        }
        for alt in prestress["alternatives"]:
            s = next(s for s in alt["scenarios"] if s["span_m"] == 25)
            stations = s["stations"]
            for fiber, style in (("top_pa", "-"), ("soffit_pa", "--")):
                axes[0, 0].plot(
                    [v["x_m"] for v in stations],
                    [v["transfer"][fiber] / 1e6 for v in stations],
                    style,
                    color=colours[alt["id"]],
                    label=alt["id"] + " " + fiber.removesuffix("_pa"),
                )
        axes[0, 0].axhline(0, color="black", linewidth=0.7)
        axes[0, 0].set(
            title="Pi25 transfer, full-force gross-section idealisation",
            xlabel="Station along span [m]",
            ylabel="Compression-positive stress [MPa]",
        )
        axes[0, 0].legend(fontsize=7, ncol=2)
        names = []
        values = []
        barcol = []
        for alt in prestress["alternatives"]:
            for s in alt["scenarios"]:
                names.append(alt["id"] + "\n" + str(int(s["span_m"])) + " m")
                values.append(
                    s["minimum_compression_pa_by_stage"]["service_dead_only"] / 1e6
                )
                barcol.append(colours[alt["id"]])
        axes[0, 1].bar(names, values, color=barcol)
        axes[0, 1].axhline(0, color="black", linewidth=0.7)
        axes[0, 1].set(
            title="Minimum stress after assumed loss, dead load only",
            ylabel="Compression-positive stress [MPa]",
        )
        bed = report["bed"]["cases"]
        axes[1, 0].plot(
            range(len(bed)),
            [r["elastic_load_factor"] for r in bed],
            "o-",
            color="#164c68",
        )
        axes[1, 0].axhline(
            1,
            color="#a34d37",
            linestyle="--",
            label="Elastic critical load = applied axial force",
        )
        axes[1, 0].set_xticks(
            range(len(bed)), [f"{r['spring_n_m']/1e6:g}" for r in bed]
        )
        axes[1, 0].set(
            title="Bed buckling sensitivity; ground stiffness unmeasured",
            xlabel="Spring at each ground restraint [MN/m]",
            ylabel="Elastic critical / applied force",
        )
        axes[1, 0].legend(fontsize=7)
        r = report["runway"]
        axes[1, 1].bar(
            ["Near wheel", "Far wheel"],
            [r["near_wheel_n"] / 1000, r["far_wheel_n"] / 1000],
            color=["#164c68", "#6b9ba8"],
        )
        axes[1, 1].set(
            title="125 t rated-crane interface scenario; 2 wheels per rail",
            ylabel="Vertical action per wheel [kN]",
        )
        for ax in axes.flat:
            ax.grid(axis="y", alpha=0.2)
            ax.set_axisbelow(True)
        fig.supxlabel(
            "Full-force end extension is diagnostic. Transfer/bond, concrete limits, railway loads, restraint, crane configuration and site resistance remain unqualified.",
            fontsize=8,
        )
        stream = io.StringIO()
        fig.savefig(
            stream,
            format="svg",
            metadata={"Date": None, "Creator": "OpenSourceRail factory development"},
        )
        plt.close(fig)
        return (
            "\n".join(line.rstrip() for line in stream.getvalue().splitlines()) + "\n"
        )

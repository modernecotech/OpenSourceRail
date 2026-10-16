"""Deterministic standalone engineering figures for the factory development."""

from __future__ import annotations

import io


def connections_svg(report):
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    from matplotlib.colors import ListedColormap

    s = report["strongback"]
    with matplotlib.rc_context(
        {"svg.hashsalt": "osr-factory-connections-3", "font.size": 9}
    ):
        fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
        fig.suptitle(
            "Factory fabrication interfaces — preliminary geometry and demand",
            fontsize=15,
        )
        ax = axes[0, 0]
        for point in s["points"]:
            for sign in (-1, 1):
                ax.add_patch(
                    Circle(
                        (sign * point["y_m"], point["z_m"]),
                        0.025,
                        facecolor="#dcebe5",
                        edgecolor="#14715e",
                        linewidth=1,
                    )
                )
                ax.add_patch(
                    Circle(
                        (sign * point["y_m"], point["z_m"]),
                        0.011,
                        facecolor="white",
                        edgecolor="#214756",
                        linewidth=0.5,
                    )
                )
        ax.set(
            xlim=(-1, 1),
            ylim=(0.55, 2),
            xlabel="Transverse position y [m]",
            ylabel="Height z [m]",
            title="Central 2 m of grip field: 60 mm pitch, 50 mm bodies",
        )
        ax.set_aspect("equal")
        ax = axes[0, 1]
        for name, colour in (("lower_first", "#a34d37"), ("balanced_pairs", "#14715e")):
            sequence = s["sequences"][name]["stages"]
            ax.plot(
                [0] + [v["stage"] for v in sequence],
                [0] + [v["end_vertical_couple_nm"] / 1e6 for v in sequence],
                color=colour,
                label=name.replace("_", " "),
            )
        ax.axhline(0, color="black", linewidth=0.6)
        ax.set(
            title="Aligned return axis; every individual strand step",
            xlabel="Strands stressed",
            ylabel="End vertical couple [MNm]",
        )
        ax.legend(fontsize=8)
        ax = axes[1, 0]

        def box(x, z, w, h, colour):
            ax.add_patch(
                Rectangle(
                    (x, z), w, h, facecolor=colour, edgecolor="#214756", linewidth=0.6
                )
            )

        box(-25, 700, 50, 100, "#9db7c2")
        box(-20, 705, 40, 90, "white")
        box(-4.5, 795, 9, 5, "white")
        box(-11, 700, 22, 5, "white")
        box(-90, 800, 180, 20, "#dcebe5")
        box(-10, 800, 20, 20, "white")
        box(-9.995, 800, 19.99, 20, "#8faaa0")
        box(-16, 820, 32, 20, "#8faaa0")
        box(-3.4, 800, 6.8, 16, "white")
        box(-8, 793, 16, 2, "#ba9358")
        box(-6.5, 785, 13, 8, "#ba9358")
        box(-4, 793, 8, 20, "#ddc89f")
        ax.annotate(
            "22 mm access",
            xy=(0, 702),
            xytext=(38, 720),
            arrowprops=dict(arrowstyle="->"),
            fontsize=8,
        )
        ax.annotate(
            "Contact datum 840 mm",
            xy=(0, 840),
            xytext=(-95, 860),
            arrowprops=dict(arrowstyle="->"),
            fontsize=8,
        )
        ax.set(
            xlim=(-105, 105),
            ylim=(690, 870),
            xlabel="x [mm]",
            ylabel="z [mm]",
            title="Locator coupon section; thread envelopes only",
        )
        ax.set_aspect("equal")
        ax = axes[1, 1]
        names = [
            "runway-baseplate",
            "strongback-box",
            "strongback-end-steel",
            "runway-girder",
        ]
        suppliers = ["promil-starcut260", "responsive-horizontal"]
        data = [
            [
                int(
                    next(
                        v
                        for v in report["manufacturing"]["cases"]
                        if v["part"] == name and v["supplier_case"] == supplier
                    )["geometric_range_screen"]
                )
                for supplier in suppliers
            ]
            for name in names
        ]
        ax.imshow(
            data,
            cmap=ListedColormap(["#cf9278", "#b8d9cb"]),
            vmin=0,
            vmax=1,
            aspect="auto",
        )
        for row in range(len(names)):
            for col in range(2):
                ax.text(
                    col,
                    row,
                    "within range" if data[row][col] else "outside range",
                    ha="center",
                    va="center",
                    fontsize=8,
                )
        ax.set_xticks([0, 1], ["Pro-Mil Starcut", "Responsive horizontal"])
        ax.set_yticks(range(len(names)), names)
        ax.set_title("Setup range only; payload and tool access unaccepted")
        fig.supxlabel(
            "Unissued concepts. Grip/jack compatibility, local strength, material/threads/welds, stressing procedure, ground restraint and actual supplier offers remain open.",
            fontsize=8,
        )
        output = io.StringIO()
        fig.savefig(
            output,
            format="svg",
            metadata={"Date": None, "Creator": "OpenSourceRail factory fabrication"},
        )
        plt.close(fig)
        return (
            "\n".join(line.rstrip() for line in output.getvalue().splitlines()) + "\n"
        )


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

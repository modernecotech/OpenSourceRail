"""Factory engineering views inside the common immutable review export."""

from __future__ import annotations

import csv
import html
import io
import json
from pathlib import Path

from .contracts import canonical


def csv_file(path, rows):
    if not rows:
        path.write_text("state,basis\nnot-run,selected ideal rail case is unstable\n")
        return
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def figure(data):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    support, schedule = data["restraint"], data["production_schedule"]
    plt.rcParams["svg.hashsalt"] = "osr-factory-restraint-schedule-v1"
    fig = plt.figure(figsize=(13, 10), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=(1, 1.4))
    ax = fig.add_subplot(grid[0, 0])
    if support["cases"]:
        worst = max(
            support["cases"], key=lambda r: max(r["baseplate"]["anchor_tensions_n"])
        )
        plate = worst["baseplate"]
        cfg = support["basis"]
        y = np.linspace(-cfg["baseplate_m"][1] / 2, cfg["baseplate_m"][1] / 2, 401)
        q = cfg["grout_normal_spring_per_area_n_m3"] * np.maximum(
            plate["downward_translation_m"] + plate["rotation_rad"] * y, 0
        )
        ax.plot(y * 1000, q / 1e6, color="#15725a")
        ax.fill_between(y * 1000, q / 1e6, color="#15725a", alpha=0.15)
        ax.set_title(f"Rigid baseplate contact · station {worst['global_x_m']:g} m")
        ax.text(
            0.03,
            0.96,
            f"Largest anchor tension {max(plate['anchor_tensions_n'])/1000:.2f} kN\nNominal zero-preload spring model",
            transform=ax.transAxes,
            va="top",
            fontsize=9,
        )
    else:
        ax.text(
            0.1,
            0.5,
            "Selected ideal return rail is unstable;\nno post-force/contact demand is reported",
            transform=ax.transAxes,
        )
    ax.set_xlabel("Transverse plate coordinate [mm]")
    ax.set_ylabel("Compression-only grout demand [MPa]")
    ax.grid(alpha=0.2)
    ax = fig.add_subplot(grid[0, 1])
    rows = support["interface_cases"][1:]
    xs = np.arange(len(rows))
    for offset, field, label, color in (
        (-0.18, "effective_lateral_n_m", "Lateral", "#225b85"),
        (0.18, "effective_vertical_n_m", "Vertical", "#b67537"),
    ):
        vals = [r[field] / 1e6 if r[field] is not None else 0 for r in rows]
        ax.bar(xs + offset, vals, width=0.32, label=label, color=color)
    ax.axhline(
        support["selected_lateral_requirement_n_m"] / 1e6,
        color="#225b85",
        linestyle="--",
        linewidth=1,
    )
    ax.axhline(
        support["selected_vertical_requirement_n_m"] / 1e6,
        color="#b67537",
        linestyle=":",
        linewidth=1,
    )
    ax.set_xticks(xs, [r["id"].replace("-hypothesis", "") for r in rows])
    ax.set_ylabel("Effective stiffness [MN/m]")
    ax.set_title("Series interface hypotheses · actual stiffness unknown")
    if any(r["effective_lateral_n_m"] for r in rows):
        ax.set_yscale("log")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.2)
    ax = fig.add_subplot(grid[1, :])
    bed_units = sorted(
        {r["unit"] for r in schedule["reservations"] if r["resource"] == "bed"}
    )[:8]
    lanes = [("crane", i) for i in range(schedule["basis"]["resources"]["crane"])] + [
        ("bed", i) for i in bed_units
    ]
    colors = dict(
        cage_lift="#8b66a0",
        casting="#2a718e",
        release_demould="#c97c36",
        dispatch="#397d55",
        hold="#aebac3",
        maintenance="#b73c45",
    )
    for lane, (resource, unit) in enumerate(lanes):
        for row in schedule["reservations"]:
            if row["resource"] != resource or row["unit"] != unit:
                continue
            phase = row["task"].split("/")[-1]
            ax.barh(
                lane,
                (row["end_h"] - row["start_h"]) / 24,
                left=row["start_h"] / 24,
                height=0.7,
                color=colors.get(phase, "#aebac3"),
                edgecolor="white",
                linewidth=0.35,
            )
    ax.axvline(
        schedule["horizon_h"] / 24,
        color="#ab2833",
        linestyle="--",
        label="Campaign deadline",
    )
    ax.set_yticks(range(len(lanes)), [f"{key} {unit+1}" for key, unit in lanes])
    ax.invert_yaxis()
    ax.set_xlabel("Elapsed calendar days; work occupies the declared daily window")
    ax.set_title(
        f"Finite planning campaign: {schedule['dispatched_within_horizon']}/{schedule['beam_count']} dispatched by day {schedule['horizon_h']/24:g}; grey = bed held through curing/release"
    )
    from matplotlib.patches import Patch

    ax.legend(
        handles=[Patch(color=c, label=k.replace("_", " ")) for k, c in colors.items()],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=6,
        fontsize=8,
    )
    ax.grid(axis="x", alpha=0.2)
    fig.suptitle(
        "Factory support and resource studies · unissued research hypotheses",
        fontsize=14,
    )
    out = io.StringIO()
    fig.savefig(
        out,
        format="svg",
        metadata={"Date": None, "Creator": "OpenSourceRail common factory review"},
    )
    plt.close(fig)
    return "\n".join(line.rstrip() for line in out.getvalue().splitlines()) + "\n"


def write_packet(candidate, folder):
    data = candidate.get("definition", {})
    if "restraint" not in data:
        return
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    study = {
        key: data[key]
        for key in ("restraint", "production_schedule", "interface_supplier_enquiries")
    }
    if "staged_loads" in data:
        study["staged_loads"] = data["staged_loads"]
    if "spatial_frame" in data:
        study["spatial_frame"] = data["spatial_frame"]
        study["spatial_confirmation"] = data.get("spatial_confirmation")
    if "beam_demands" in data:
        study["beam_demands"] = data["beam_demands"]
    study.update(
        schema="osr-common-factory-studies/1",
        candidate=candidate["id"],
        identity=candidate["identity"],
        physical_release=False,
    )
    (folder / "study.json").write_bytes(canonical(study) + b"\n")
    support = data["restraint"]
    rows = []
    for case in support["cases"]:
        plate = case["baseplate"]
        rows.append(
            dict(
                station_m=case["global_x_m"],
                lateral_sign=case["lateral_sign"],
                vertical_sign=case["vertical_sign"],
                lateral_force_n=case["lateral_force_n"],
                vertical_upward_force_n=case["vertical_upward_force_n"],
                post_downward_force_n=case["post_downward_force_n"],
                base_moment_nm=case["post_base_moment_nm"],
                maximum_anchor_tension_n=max(plate["anchor_tensions_n"]),
                maximum_contact_pressure_pa=plate[
                    "maximum_sampled_contact_pressure_pa"
                ],
                nominal_weld_combined_demand_pa=case["post_base_weld"][
                    "nominal_combined_demand_pa"
                ],
                contact_fraction=plate["contact_area_fraction"],
                pad_maximum_pressure_pa=case["pad"]["maximum_pressure_pa"],
                force_residual_n=plate["force_residual_n"],
                moment_residual_nm=plate["moment_residual_nm"],
                physical_release=False,
            )
        )
    csv_file(folder / "support-demands.csv", rows)
    if "beam_demands" in data:
        beam = data["beam_demands"]
        csv_file(folder / "beam-service-demands.csv", beam["railway"]["stations"])
        csv_file(folder / "beam-handling-moments.csv", beam["handling"]["diagram"])
        (folder / "beam-demands.svg").write_text(beam_figure(beam))
    if "spatial_frame" in data:
        spatial = data["spatial_frame"]
        csv_file(
            folder / "spatial-base-demands.csv",
            [
                dict(
                    stage=row["index"],
                    phase=row["phase"],
                    node=base["node"],
                    **dict(
                        zip(
                            ["x_m", "y_m", "z_m"],
                            spatial["model"]["nodes_m"][base["node"]],
                        )
                    ),
                    **dict(
                        zip(
                            ["fx_n", "fy_n", "fz_n", "mx_nm", "my_nm", "mz_nm"],
                            [-v for v in base["wrench_on_structure"]],
                        )
                    ),
                    physical_release=False,
                )
                for row in spatial["stages"]
                for base in row["reactions"]
            ],
        )
        (folder / "spatial-frame.svg").write_text(frame_figure(spatial))
    if "staged_loads" in data:
        staged = data["staged_loads"]
        csv_file(
            folder / "static-stages.csv",
            [
                {
                    k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
                    for k, v in row.items()
                    if k != "pin_cases"
                }
                for row in staged["stages"]
            ],
        )
        csv_file(
            folder / "end-pin-demands.csv",
            [
                dict(
                    stage=row["index"],
                    phase=row["phase"],
                    side=pin["side"],
                    vertical_sign=pin["vertical_sign"],
                    x_m=x,
                    force_on_foundation_n=force,
                    physical_release=False,
                )
                for row in staged["stages"]
                for pin in row["pin_cases"]
                for x, force in zip(
                    pin["x_m"], pin["force_on_foundation_n"], strict=True
                )
            ],
        )
        (folder / "static-stages.svg").write_text(stage_figure(staged))
    csv_file(
        folder / "resource-reservations.csv",
        data["production_schedule"]["reservations"],
    )
    csv_file(
        folder / "process-tasks.csv",
        [
            dict(
                **{k: v for k, v in row.items() if k != "resources"},
                resources=json.dumps(row["resources"]),
            )
            for row in data["production_schedule"]["tasks"]
        ],
    )
    csv_file(
        folder / "interface-rfq.csv",
        [
            dict(
                id=r["id"],
                supplier=r["supplier"],
                model=r["model"],
                origin=r["origin"],
                request=r["enquiry"],
                sources="; ".join(r["sources"]),
                price_gbp="",
                supplier_contacted=False,
                contract_accepted=False,
            )
            for r in data["interface_supplier_enquiries"]["cases"]
        ],
    )
    (folder / "review.svg").write_text(figure(data))
    import importlib.metadata

    (folder / "view-metadata.json").write_bytes(
        canonical(
            dict(
                schema="osr-factory-study-view/1",
                matplotlib=importlib.metadata.version("matplotlib"),
                scope="Presentation of retained job results; no new solver execution or pixel-equivalence claim",
                physical_release=False,
            )
        )
        + b"\n"
    )
    escaped = html.escape

    def table(headers, rows):
        return (
            "<table><thead><tr>"
            + "".join("<th>" + escaped(h) + "</th>" for h in headers)
            + "</tr></thead><tbody>"
            + "".join(
                "<tr>"
                + "".join("<td>" + escaped(str(cell)) + "</td>" for cell in row)
                + "</tr>"
                for row in rows
            )
            + "</tbody></table>"
        )

    interfaces = table(
        ["Interface case", "Lateral MN/m", "Vertical MN/m", "Lateral load factor"],
        [
            [
                r["id"],
                (
                    "unknown"
                    if r["effective_lateral_n_m"] is None
                    else f"{r['effective_lateral_n_m']/1e6:.4f}"
                ),
                (
                    "unknown"
                    if r["effective_vertical_n_m"] is None
                    else f"{r['effective_vertical_n_m']/1e6:.4f}"
                ),
                (
                    "unknown"
                    if r["lateral_elastic_load_factor"] is None
                    else f"{r['lateral_elastic_load_factor']:.3f}"
                ),
            ]
            for r in support["interface_cases"]
        ],
    )
    machining = table(
        ["Plate width", "Fixed-hole edge", "CV5 diameter screen"],
        [
            [
                f"{r['width_m']*1000:g} mm",
                f"{r['fixed_anchor_hole_edge_clearance_m']*1000:.1f} mm",
                r["pilot_cv5_diameter_screen"],
            ]
            for r in support["baseplate_machining_cases"]
        ],
    )
    suppliers = "".join(
        "<h3>"
        + escaped(r["supplier"])
        + " · "
        + escaped(r["model"])
        + "</h3><p>"
        + escaped(r["origin"])
        + "</p><p>"
        + escaped(r["enquiry"])
        + "</p><p>"
        + " · ".join(
            f'<a href="{escaped(s,quote=True)}">Official source {i+1}</a>'
            for i, s in enumerate(r["sources"])
        )
        + "</p>"
        for r in data["interface_supplier_enquiries"]["cases"]
    )
    native = folder.parent.parent / "executed-attempt" / candidate["id"]
    cad_links = " · ".join(
        f'<a href="../../executed-attempt/{candidate["id"]}/{name}">{label}</a>'
        for name, label in (("model.FCStd", "FreeCAD"), ("model.step", "STEP"))
        if (native / name).is_file()
    )
    plan = data["production_schedule"]
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Factory support and scheduling review</title><style>body{font:16px/1.5 system-ui;max-width:1100px;margin:auto;padding:22px;color:#163746;background:#f5f8f8}img{width:100%;height:auto}table{width:100%;border-collapse:collapse;margin:20px 0}th,td{padding:9px;border-bottom:1px solid #b6c8cd;text-align:left;overflow-wrap:anywhere}h2{margin-top:32px}a{color:#075e74}code{overflow-wrap:anywhere}</style>'
    page += (
        "<h1>Factory support and resource studies</h1><p>Unissued research hypotheses. Original factory examples are retained separately. This packet comes from a common design job; it is not a fabrication, lift or production release.</p><p>"
        + cad_links
        + '</p><img src="review.svg" alt="Baseplate contact, interface stiffness and finite crane/bed calendar"><h2>Support interfaces</h2>'
        + interfaces
        + machining
    )
    page += (
        f'<p>{len(support["cases"])} final-force, matching-station/sign cases per nominal return rail. Anchor springs use gross bar area; post/plate/weld, thread/embedment, grout and site resistance remain unqualified. Ideal end-pin grounding and staged stressing/release torsion remain unresolved.</p><h2>Finite resource campaign</h2><p>'
        + f'{plan["dispatched_within_horizon"]} of {plan["beam_count"]} beams dispatched within {plan["horizon_h"]/24:g} calendar days; {plan["backlog_at_horizon"]} remain at the deadline. The accepted-equivalent planning value is {plan["planning_accepted_equivalent"]:g}, using an unmeasured yield hypothesis. Each Pi{candidate["variables"]["span_m"]:g} pour uses {plan["batches_per_beam"]} assumed batches and reserves mixer/crane/crew for {plan["casting_block_h"]:.2f} hours. These are finite policy results, not steady-state capacity or supplier performance.'
        + "</p><h2>Unsent supplier enquiries</h2>"
        + suppliers
    )
    page += '<h2>Review data</h2><p><a href="study.json">Full study</a> · <a href="support-demands.csv">Support demands</a> · <a href="resource-reservations.csv">Resource reservations</a> · <a href="process-tasks.csv">Tasks</a> · <a href="interface-rfq.csv">Unsent RFQs</a></p></html>\n'
    if "staged_loads" in data:
        staged = data["staged_loads"]
        addition = f'<h2>Static stressing and unloading hypotheses</h2><p>{staged["stage_count"]} force states and {staged["contact_cases_solved"]} support-contact cases. Order: {escaped(staged["stressing_order"])}; unloading: {escaped(staged["release_order"])}. Rail gravity is included. Load allocation, mirrored end operation, ideal grounding and static unloading remain hypotheses; concrete transfer, dynamics, local resistance and an approved release procedure remain unresolved.</p><img src="static-stages.svg" alt="Staged rail force and eccentric couple, anchor and ideal end-pin demand histories"><p><a href="static-stages.csv">Static states</a> · <a href="end-pin-demands.csv">Signed end-pin demands</a></p>'
        page = page.replace("<h2>Review data</h2>", addition + "<h2>Review data</h2>")
    if "beam_demands" in data:
        beam = data["beam_demands"]
        lift = beam["handling"]
        addition = f'<h2>Pi-beam railway and handling demands</h2><p>The railway diagnostic uses the retained three-car, twelve-axle planning reference. Six-car Baghdad axle loading remains unknown. Peak total moment {beam["railway"]["continuous_peak"]["moment_nm"]/1e6:.3f} MNm; minimum sampled service compression {beam["minimum_sampled_service_compression_pa"]/1e6:.3f} MPa (negative is tension). No concrete stress limits or railway resistance are accepted.</p><img src="beam-demands.svg" alt="Diagnostic moving-load moment and sampled service stresses, handling overhang moment and lower-leg tensions"><p>Lift stations at {lift["support_x_m"][0]:g} and {lift["support_x_m"][1]:g} m give {lift["longitudinal_rig_span_m"]:g} m longitudinal spreader span. The {lift["upper_sling_angle_from_vertical_deg"]:g} degree upper-sling hypothesis needs {lift["geometric_headroom_above_longitudinal_end_units_m"]:.2f} m above its end units. Complete rig mass, inserts, equalization, transverse distributors, supplier span/angle capacity and the site lift plan remain unresolved.</p><p><a href="beam-service-demands.csv">Section diagnostic demands</a> · <a href="beam-handling-moments.csv">Handling moments</a></p>'
        page = page.replace("<h2>Review data</h2>", addition + "<h2>Review data</h2>")
    if "spatial_frame" in data:
        spatial = data["spatial_frame"]
        addition = f'<h2>Connected whole-bed spatial model</h2><p>376 native objects; two strongbacks, full return rails and all sixteen nominal support details. {len(spatial["model"]["nodes_m"])} frame nodes and {len(spatial["model"]["members"])} gross members. Six-axis base springs replace ideal end pins in this separate first-order model. Actual stiffness, biaxial/torsional connection resistance, local effects and interaction with second-order response remain unqualified. The earlier ideal-pin studies above retain their original assumptions.</p><img src="spatial-frame.svg" alt="Whole-bed spatial frame and finite-base force history"><p><a href="spatial-base-demands.csv">Signed six-axis forces and moments on base foundations</a></p>'
        page = page.replace("<h2>Review data</h2>", addition + "<h2>Review data</h2>")
    (folder / "index.html").write_text(page)


def stage_figure(study):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["svg.hashsalt"] = "osr-static-stages-v1"
    rows = study["stages"]
    x = [r["index"] for r in rows]
    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True, layout="constrained")
    for side in (0, 1):
        axes[0].plot(
            x, [r["axial_n"][side] / 1e6 for r in rows], label=f"Rail {side+1}"
        )
        axes[1].plot(
            x, [r["end_couple_nm"][side] / 1000 for r in rows], label=f"Rail {side+1}"
        )
    axes[2].plot(
        x,
        [
            (
                None
                if r["maximum_anchor_tension_n"] is None
                else r["maximum_anchor_tension_n"] / 1000
            )
            for r in rows
        ],
        label="Largest anchor tension",
    )
    axes[2].plot(
        x,
        [
            (
                None
                if r["maximum_vertical_pin_force_n"] is None
                else r["maximum_vertical_pin_force_n"] / 1000
            )
            for r in rows
        ],
        label="Largest ideal end-pin force",
    )
    boundary = next(r["index"] for r in rows if r["phase"] == "unloading")
    for ax, label in zip(
        axes,
        [
            "Rail compression [MN]",
            "Allocated end couple [kNm]",
            "Demand magnitude [kN]",
        ],
        strict=True,
    ):
        ax.axvline(boundary, linestyle="--", color="#9d5252", linewidth=1)
        ax.set_ylabel(label)
        ax.grid(alpha=0.2)
        ax.legend(fontsize=9)
    axes[-1].set_xlabel(
        "Static state index; dashed line = start of hypothetical unloading"
    )
    axes[0].set_title(
        "Staged bed hypotheses · rail gravity included · no physical release"
    )
    out = io.StringIO()
    fig.savefig(
        out,
        format="svg",
        metadata={"Date": None, "Creator": "OpenSourceRail common factory review"},
    )
    plt.close(fig)
    return "\n".join(line.rstrip() for line in out.getvalue().splitlines()) + "\n"


def beam_figure(study):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["svg.hashsalt"] = "osr-beam-demands-v1"
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    rows = study["railway"]["stations"]
    xs = [r["x_m"] for r in rows]
    axes[0, 0].plot(xs, [r["dead_moment_nm"] / 1e6 for r in rows], label="Dead load")
    axes[0, 0].plot(
        xs,
        [r["maximum_total_moment_nm"] / 1e6 for r in rows],
        label="Dead + diagnostic train",
    )
    peak = study["railway"]["continuous_peak"]
    axes[0, 0].scatter(
        [peak["x_m"]],
        [peak["moment_nm"] / 1e6],
        color="#ad493f",
        label="Continuous moment peak",
    )
    axes[0, 0].set(
        title="Legacy three-car diagnostic; six-car loading unknown",
        ylabel="Moment [MNm]",
    )
    axes[0, 0].legend(fontsize=8)
    for key, label in [
        ("top_compression_pa", "Top minimum (train off span)"),
        ("top_maximum_compression_pa", "Top maximum"),
        ("soffit_compression_pa", "Soffit minimum"),
    ]:
        axes[0, 1].plot(xs, [r[key] / 1e6 for r in rows], label=label)
    axes[0, 1].axhline(0, color="#ad493f", linestyle="--")
    axes[0, 1].set(
        title="Sampled gross service fibres; no accepted limits",
        ylabel="Compression [MPa]; tension negative",
    )
    axes[0, 1].legend(fontsize=8)
    lift = study["handling"]
    axes[1, 0].plot(
        [r["x_m"] for r in lift["diagram"]],
        [r["moment_nm"] / 1e6 for r in lift["diagram"]],
        color="#276f76",
    )
    for x in lift["support_x_m"]:
        axes[1, 0].axvline(x, color="#b97b3b", linestyle="--")
    axes[1, 0].set(
        title="Factored beam-only handling; dashed = lift stations",
        ylabel="Moment [MNm]",
    )
    axes[1, 1].bar(
        ["4 equalized legs", "2 effective legs"],
        [
            lift["nominal_equalized_leg_tension_n"] / 1000,
            lift["two_effective_leg_tension_n"] / 1000,
        ],
        color=["#276f76", "#b97b3b"],
    )
    axes[1, 1].set(
        title=f'Lower-leg hypotheses at {lift["lower_sling_angle_from_vertical_deg"]:g}° from vertical',
        ylabel="Tension per effective leg [kN]",
    )
    for ax in axes.flat:
        ax.grid(alpha=0.2)
    for ax in [axes[0, 0], axes[0, 1], axes[1, 0]]:
        ax.set_xlabel("Beam station [m]")
    fig.suptitle(
        f'Pi{study["span_m"]:g} · {study["prestress_id"]} · diagnostic/handling demands only'
    )
    out = io.StringIO()
    fig.savefig(
        out,
        format="svg",
        metadata={"Date": None, "Creator": "OpenSourceRail common factory review"},
    )
    plt.close(fig)
    return "\n".join(line.rstrip() for line in out.getvalue().splitlines()) + "\n"


def frame_figure(study):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    plt.rcParams["svg.hashsalt"] = "osr-spatial-frame-v1"
    fig = plt.figure(figsize=(12, 8), layout="constrained")
    ax = fig.add_subplot(211, projection="3d")
    model = study["model"]
    for m in model["members"]:
        points = np.array(
            [
                np.array(model["nodes_m"][m[k]]) + m[o]
                for k, o in (("i", "offset_i_m"), ("j", "offset_j_m"))
            ]
        )
        ax.plot(*points.T, color="#176477", linewidth=1.5)
    bases = np.array([model["nodes_m"][s["node"]] for s in model["springs"]])
    ax.scatter(*bases.T, color="#bc7836", s=16)
    ax.set_box_aspect([26, 4, 3])
    ax.set(xlabel="x [m]", ylabel="y [m]", zlabel="z [m]")
    ax.set_title(
        "Connected gross spatial bed; six-axis finite base springs; no ideal end pins"
    )
    ax = fig.add_subplot(212)
    ax.plot(
        [r["index"] for r in study["stages"]],
        [r["maximum_base_force_resultant_n"] / 1000 for r in study["stages"]],
        color="#176477",
    )
    ax.set(
        xlabel="Static force state",
        ylabel="Largest base force resultant [kN]",
        title="First-order reaction demand; no resistance or physical acceptance",
    )
    ax.grid(alpha=0.2)
    out = io.StringIO()
    fig.savefig(
        out,
        format="svg",
        metadata={"Date": None, "Creator": "OpenSourceRail common factory review"},
    )
    plt.close(fig)
    return "\n".join(line.rstrip() for line in out.getvalue().splitlines()) + "\n"


def publish_snapshot(source, destination):
    """Retain a compact documentation projection of one verified common export."""
    import shutil
    from .export import verify_export
    from .publication import digest
    from .registry import dependencies

    source, destination = Path(source), Path(destination)
    manifest = verify_export(source)
    request = json.loads((source / "request.json").read_text())
    if request["problem"]["adapter"] != "factory-precast" or request[
        "dependencies"
    ] != dependencies("factory-precast"):
        raise ValueError("current common precast export required for publication")
    studies = list((source / "factory-studies").glob("*/study.json"))
    if len(studies) != 1:
        raise ValueError("snapshot requires exactly one common factory study")
    study = json.loads(studies[0].read_text())
    identifier = study["candidate"]
    native = source / "executed-attempt" / identifier
    if not (native / "model.FCStd").is_file():
        raise ValueError("snapshot requires an executed native confirmation")
    if destination.exists():
        raise ValueError("factory snapshots are immutable; use a fresh destination")
    destination.mkdir(parents=True)
    parent_files = {}
    for path in [
        *studies[0].parent.iterdir(),
        *(
            native / name
            for name in (
                "model.json",
                "model.FCStd",
                "native-cad.json",
                "spatial-input.json",
                "spatial-native.json",
            )
        ),
        source / "request.json",
    ]:
        if not path.is_file():
            continue
        shutil.copyfile(path, destination / path.name)
        parent_files[path.relative_to(source).as_posix()] = digest(path)
    page = (destination / "index.html").read_text()
    page = page.replace(
        f"../../executed-attempt/{identifier}/model.FCStd", "model.FCStd"
    )
    page = page.replace(
        f' · <a href="../../executed-attempt/{identifier}/model.step">STEP</a>', ""
    )
    (destination / "index.html").write_text(page)
    record = dict(
        schema="osr-common-factory-snapshot/1",
        job=manifest["job"],
        candidate=identifier,
        parent_export_manifest_sha256=digest(source / "manifest.json"),
        parent_files_sha256=parent_files,
        files_sha256={
            p.name: digest(p) for p in sorted(destination.iterdir()) if p.is_file()
        },
        presentation_change="Native link localized; local-only STEP link removed. All numerical/CAD bytes copied unchanged from common export.",
        physical_release=False,
    )
    (destination / "snapshot.json").write_bytes(canonical(record) + b"\n")
    return verify_snapshot(destination, current=True)


def verify_snapshot(folder, *, current=False):
    from .publication import digest
    from .registry import dependencies

    folder = Path(folder)
    record = json.loads((folder / "snapshot.json").read_text())
    if (
        record.get("schema") != "osr-common-factory-snapshot/1"
        or record.get("physical_release") is not False
    ):
        raise ValueError("controlled unissued factory snapshot required")
    actual = {
        p.name for p in folder.iterdir() if p.is_file() and p.name != "snapshot.json"
    }
    if actual != set(record["files_sha256"]):
        raise ValueError("factory snapshot artifact membership differs")
    for name, sha in record["files_sha256"].items():
        path = folder / name
        if Path(name).name != name or path.is_symlink() or digest(path) != sha:
            raise ValueError("factory snapshot artifact integrity differs: " + name)
    receipt = json.loads((folder / "native-cad.json").read_text())
    if (
        receipt["input_sha256"] != digest(folder / "model.json")
        or receipt["files_sha256"]["model.FCStd"] != digest(folder / "model.FCStd")
        or not receipt["fcstd_reopened"]
        or not receipt["step_reopened"]
    ):
        raise ValueError("factory snapshot native correspondence differs")
    request = json.loads((folder / "request.json").read_text())
    if (folder / "spatial-native.json").exists():
        proof = json.loads((folder / "spatial-native.json").read_text())
        if (
            proof["input_sha256"] != digest(folder / "spatial-input.json")
            or proof["numerical_comparison_passed"] is not True
            or proof["case_count"] != 2
            or proof["physical_release"] is not False
        ):
            raise ValueError("factory snapshot spatial correspondence differs")
    if current and request["dependencies"] != dependencies("factory-precast"):
        raise ValueError("factory snapshot belongs to an earlier source revision")
    return dict(
        schema="osr-factory-snapshot-verification/1",
        integrity_verified=True,
        current_sources_checked=current,
        numerical_recomputation_performed=False,
        job=record["job"],
        physical_release=False,
    )

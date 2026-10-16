"""Common design adapters over the retained factory solvers and CAD exporter.

Plant capacity scenarios are not additional issued layouts. Model inventories
represent a fixture or one strongback end, with every missing allocation named.
"""

from __future__ import annotations

from copy import deepcopy
import json
import hashlib
import math
from pathlib import Path
import shutil
import subprocess

from .registry import ROOT

PACKAGE = ROOT / "engineering/factory_examples"
ADAPTERS = {"factory-fixture", "factory-precast"}
PRODUCTION_RESOURCES = {
    "reinforcement",
    "stressing_release",
    "batching_casting",
    "crane_handling",
    "storage_dispatch",
    "haulage",
    "labour",
    "maintenance",
}
COMMON_CHECKS = [
    "geometry",
    "native_geometry",
    "mass_inertia",
    "local_resistance",
    "foundation_connections",
    "complete_installed_inventory",
    "supplier_configuration",
    "physical_correlation",
    "independent_acceptance",
]


def toolchain():
    from engineering.factory_examples.native import digest

    binary = shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
    result = dict(
        available=False,
        missing=["FreeCAD"],
        executable_sha256=None,
        flatpak_commit=None,
        flatpak_runtime=None,
        flatpak_runtime_commit=None,
    )
    if binary:
        result.update(available=True, missing=[], executable_sha256=digest(binary))
    elif shutil.which("flatpak"):
        try:

            def info(option, app):
                return subprocess.check_output(
                    ["flatpak", "info", option, app],
                    text=True,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                ).strip()

            commit = info("--show-commit", "org.freecad.FreeCAD")
            runtime = info("--show-runtime", "org.freecad.FreeCAD")
            runtime_commit = info("--show-commit", runtime)
            if commit and runtime and runtime_commit:
                result.update(
                    available=True,
                    missing=[],
                    flatpak_commit=commit,
                    flatpak_runtime=runtime,
                    flatpak_runtime_commit=runtime_commit,
                )
        except (OSError, subprocess.SubprocessError):
            pass
    return result


def charters():
    from .registry import charter, choice

    rows = [
        charter(
            "factory-fixture",
            "factory-fixture",
            "Fixed 1.6 × 1.0 m datum fixture with three candidate clamps; payload/preload research cases",
            dict(
                payload_kg=choice("kg", 500, 250, 750),
                clamp_preload_n=choice("N", 500, 250, 1000),
            ),
            checks=COMMON_CHECKS + ["vertical_contact"],
            domain=[
                "Declared tool/CG and clamp-preload scenarios; idealised stock geometry; measured preload, lateral locator, weld, anchor, fatigue and datum repeatability acceptance remain open"
            ],
        ),
        charter(
            "factory-precast",
            "factory-precast",
            "Fixed Pi20/Pi25 section and 26 m return bed; coupled beam, strongback, two-plane restraint, handling and capacity scenarios",
            dict(
                span_m=choice("m", 25, 20),
                prestress_id=choice("1", "balanced-48", "balanced-40", "low-40"),
                lateral_spring_n_m=choice("N/m", 1000000, 0, 100000, 10000000),
                vertical_spring_n_m=choice("N/m", 1000000, 0, 100000, 10000000),
                casting_positions=choice("ea", 4, 16, 134),
                rated_lift_kg=choice("kg", 125000, 100000),
            ),
            checks=COMMON_CHECKS
            + [
                "dead_load_prestress",
                "lateral_stability",
                "vertical_stability",
                "grip_fit",
                "handling_lower_bound",
                "production_flow",
            ],
            domain=[
                "Dead-load prismatic elastic beam and ideal pinned return rails with hypothetical independent ground springs in each plane; handling lower bound and resource upper bounds only. Railway live loads, compression/transmission/shear/fatigue, local connections, ground, complete process scheduling and installed costs remain unknown. Position count is a capacity scenario, not a factory layout."
            ],
        ),
    ]
    for row in rows:
        row["applicability"]["environment"] = ["simulation", "training"]
    return rows


def inputs():
    def read(name):
        return json.loads((PACKAGE / "data" / name).read_text())

    return (
        read("basis.json")["assumptions"],
        read("development.json"),
        read("connections.json"),
        {e["id"]: e for e in read("equipment.json")["equipment"]},
        read("production.json"),
    )


def physical_model(native_model, density, missing):
    """Per-instance nominal mass; no mass is assigned to reserved envelopes."""
    from engineering.factory_examples import models

    parts = []
    for original in native_model["parts"]:
        p = deepcopy(original)
        volume = models.volume(p)
        if volume <= 0:
            raise ValueError("positive factory solid volume required")
        envelope = any(word in p["role"] for word in ("envelope", "reservation"))
        p.update(
            revision="research-1",
            material="unknown-supplier" if envelope else "nominal-steel-unqualified",
            properties=dict(
                mass_kg=None if envelope else volume * density,
                cg_m=None,
                inertia_tensor_kg_m2=None,
            ),
            manufacturing=dict(
                schema="osr-factory-primitive/1",
                units="m",
                definition=deepcopy(original),
            ),
        )
        parts.append(p)
    return dict(
        schema="osr-factory-definition/1",
        id=native_model["id"],
        parts=parts,
        unresolved_part_allocations=missing,
        physical_release=False,
    )


def production(a, positions, inputs):
    """Necessary resource upper bounds, never a promised end-to-end rate."""
    from engineering.factory_examples import models

    a = {**a, "bed_positions": positions}
    bed = models.capacity(a)
    required = a["programme_beams_per_working_day"]
    rows = [
        dict(
            id="casting_curing_positions",
            accepted_upper_bound_per_day=bed["planning_accepted_beams_per_working_day"],
            measured=False,
        )
    ]
    resource_ids = {r["id"] for r in inputs["resources"]}
    if (
        len(resource_ids) != len(inputs["resources"])
        or resource_ids != PRODUCTION_RESOURCES
    ):
        raise ValueError("complete unique production resource IDs required")
    for resource in inputs["resources"]:
        count, cycle, availability = (
            resource[k] for k in ("units", "working_days_per_attempt", "availability")
        )
        for key, value in (
            ("units", count),
            ("working_days_per_attempt", cycle),
            ("availability", availability),
        ):
            if value is not None:
                models.positive(value, key)
        if count is not None and (type(count) is not int):
            raise ValueError("integer production resource count required")
        if availability is not None and availability > 1:
            raise ValueError("resource availability <= 1 required")
        capacity = (
            None
            if any(v is None for v in (count, cycle, availability))
            else count / cycle * availability * a["accepted_beam_yield"]
        )
        rows.append(
            dict(
                id=resource["id"],
                accepted_upper_bound_per_day=capacity,
                measured=False,
                units_required_at_programme=(
                    None
                    if cycle is None or availability is None
                    else math.ceil(
                        required * cycle / availability / a["accepted_beam_yield"]
                    )
                ),
            )
        )
    known = [
        r["accepted_upper_bound_per_day"]
        for r in rows
        if r["accepted_upper_bound_per_day"] is not None
    ]
    unknown = [r["id"] for r in rows if r["accepted_upper_bound_per_day"] is None]
    return dict(
        resources=rows,
        known_resource_upper_bound_per_day=min(known),
        all_resource_upper_bound_per_day=None if unknown else min(known),
        programme_target_per_day=required,
        unresolved_resources=unknown,
        demonstrated_accepted_output_per_day=None,
        scheduling_validated=False,
        installed_cost=None,
        measured=False,
        scope=inputs["scope"],
    )


def compile_definition(kind, values):
    from engineering.factory_examples import models, development, connections

    a, dev, cfg, equipment, prod = inputs()
    if kind == "factory-fixture":
        a["fixture_payload_kg"] = values["payload_kg"]
        dev["fixture"]["requested_clamp_preload_n_each"] = values["clamp_preload_n"]
        fix = models.fixture(a)
        response = development.workholding(
            a, dev["fixture"], fix, equipment[dev["fixture"]["clamp_model"]]
        )
        native = dict(
            id="OSR-FIX-500-WORKHOLDING",
            parts=development.workholding_parts(fix, dev["fixture"]),
        )
        data = dict(
            native_model=native,
            response=response,
            model=physical_model(
                native,
                a["steel_density_kg_m3"],
                [dict(id="anchors_welds_supplier_retention", state="unknown")],
            ),
        )
        metrics = dict(
            payload_demand_n=fix["payload_demand_n"],
            minimum_contact_reaction_n=response["minimum_contact_reaction_n"],
        )
    else:
        civil = models.civil(a)
        prestress = development.prestress_alternatives(
            a, dev["prestress"], civil["section"]
        )
        candidate = next(
            r for r in prestress["alternatives"] if r["id"] == values["prestress_id"]
        )
        beam = next(
            r for r in candidate["scenarios"] if r["span_m"] == values["span_m"]
        )
        sb = connections.strongback(
            a, cfg["strongback"], candidate, equipment["ccl-sla15"]
        )
        native = dict(
            id="OSR-ALIGNED-STRONGBACK-END",
            parts=connections.strongback_parts(cfg["strongback"], sb),
            interference_roles=["strongback-steel", "return-rail-steel", "post-steel"],
        )
        bed = dev["bed"]
        stations = [x - bed["origin_x_m"] for x in bed["brace_stations_m"]]
        H, B, t = [v / 1000 for v in civil["bed_screen"]["side_box_mm"]]
        strong_I = (B * H**3 - (B - 2 * t) * (H - 2 * t) ** 3) / 12
        stability = {}
        for plane, inertia in (
            ("lateral", civil["bed_screen"]["weak_inertia_m4"]),
            ("vertical", strong_I),
        ):
            stiffness = values[plane + "_spring_n_m"]
            critical = development.column_buckling(
                bed["active_length_m"],
                a["steel_elastic_modulus_pa"],
                inertia,
                bed["elements"],
                [(x, stiffness) for x in stations],
            )
            response = development.imperfect_column(
                bed["active_length_m"],
                a["steel_elastic_modulus_pa"],
                inertia,
                bed["elements"],
                [(x, stiffness) for x in stations],
                candidate["initial_force_n"] / 2,
                bed["initial_sway_m"],
            )
            stability[plane] = dict(
                critical_force_per_side_n=critical,
                elastic_load_factor=critical / (candidate["initial_force_n"] / 2),
                spring_n_m=stiffness,
                imperfect_response=response,
                measured=False,
            )
        runway_inputs = {**dev["runway"], "rated_lift_kg": values["rated_lift_kg"]}
        flow = production(a, values["casting_positions"], prod)
        data = dict(
            native_model=native,
            beam=beam,
            strongback=sb,
            stability=stability,
            runway=development.runway(a, runway_inputs),
            production=flow,
            model=physical_model(
                native,
                a["steel_density_kg_m3"],
                [
                    dict(
                        id="remaining_bed_beam_reinforcement_crane_foundations_factory",
                        state="unknown",
                    )
                ],
            ),
        )
        metrics = dict(
            beam_mass_lower_bound_kg=beam["known_concrete_plus_strand_mass_kg"],
            handling_equivalent_lower_bound_kg=beam[
                "handling_equivalent_kg_lower_bound"
            ],
            initial_bed_force_n=candidate["initial_force_n"],
            lateral_elastic_load_factor=stability["lateral"]["elastic_load_factor"],
            vertical_elastic_load_factor=stability["vertical"]["elastic_load_factor"],
            known_resource_upper_bound_per_day=flow[
                "known_resource_upper_bound_per_day"
            ],
            maximum_stage_end_couple_nm=sb["sequences"]["balanced_pairs"][
                "maximum_abs_end_couple_nm"
            ],
        )
    masses = [p["properties"]["mass_kg"] for p in data["model"]["parts"]]
    metrics.update(
        defined_mass_kg=None if any(m is None for m in masses) else sum(masses),
        represented_steel_mass_kg=sum(m for m in masses if m is not None),
    )
    return data, metrics


def screen(kind, result, set_check):
    data = result["definition"]
    for name in result["checks"]:
        if name != "geometry":
            set_check(
                result,
                name,
                "unknown",
                "No supplier, material, site, first-article or independent acceptance evidence; research demands only",
            )
    set_check(
        result,
        "native_geometry",
        "not-run",
        "Requires fresh installed FreeCAD export/reopen confirmation",
    )
    if kind == "factory-fixture":
        set_check(
            result,
            "vertical_contact",
            (
                "passed"
                if data["response"]["all_cases_vertical_contact_screen"]
                else "failed"
            ),
            "Declared payload/CG/tool/preload alternatives; measured clamp force and lateral contact unqualified",
            value=data["response"]["minimum_contact_reaction_n"],
            limit=0,
            unit="N",
        )
    else:
        set_check(
            result,
            "dead_load_prestress",
            "passed" if data["beam"]["no_tension_research_screen"] else "failed",
            "Prismatic transfer/dead-load zero-tension screen only; compression limits, live loads and transmission/end zones unknown",
            value=min(data["beam"]["minimum_compression_pa_by_stage"].values()),
            limit=0,
            unit="Pa",
        )
        for plane in ("lateral", "vertical"):
            set_check(
                result,
                plane + "_stability",
                (
                    "passed"
                    if data["stability"][plane]["elastic_load_factor"] > 1
                    else "failed"
                ),
                "Elastic eigenvalue with assumed springs; not measured ground stiffness or structural resistance",
                value=data["stability"][plane]["elastic_load_factor"],
                limit=1,
                unit="1",
            )
        sb = data["strongback"]
        fit = (
            sb["revised_grip_fit"]["geometric_clearance_screen"]
            and sb["revised_plate_grip_edge_clearance_m"] >= 0
        )
        set_check(
            result,
            "grip_fit",
            "passed" if fit else "failed",
            "Grip-body and plate-edge envelopes only; exact strand/grip and jack nose compatibility unknown",
        )
        # Rigging and amplification are already included in this legacy quantity.
        demand = data["beam"]["handling_equivalent_kg_lower_bound"]
        rated = result["variables"]["rated_lift_kg"]
        set_check(
            result,
            "handling_lower_bound",
            "failed" if demand > rated else "unknown",
            "Demand includes known concrete/strand, rigging and research multiplier; missing reinforcement/attachments prevents a passing complete lift check",
            lower_bound_kg=demand,
            scenario_rating_kg=rated,
            value=demand,
            limit=rated,
            unit="kg",
        )
        flow = data["production"]
        set_check(
            result,
            "production_flow",
            (
                "failed"
                if flow["known_resource_upper_bound_per_day"]
                < flow["programme_target_per_day"]
                else "unknown"
            ),
            "Known resource upper bounds reject impossible targets; unknown stages, queues, shared resources and measurements prevent throughput acceptance",
            value=flow["known_resource_upper_bound_per_day"],
            limit=flow["programme_target_per_day"],
            unit="accepted beams/working day",
        )


def confirm(result, charge, folder, remaining_seconds):
    """Supervise the existing native exporter within the common job budget."""
    from .runtime import BudgetExceeded
    from .generated_parts_native import _run, _Time

    charge(1, "factory-native-geometry")
    seconds = remaining_seconds() if remaining_seconds else 600
    if seconds <= 0:
        raise BudgetExceeded("factory native budget exhausted")
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    model = folder / "model.json"
    model.write_text(
        json.dumps(result["definition"]["native_model"], indent=2, sort_keys=True)
        + "\n"
    )
    script = folder / "generate.py"
    script.write_text(
        "import sys\nfrom pathlib import Path\nsys.path[:0]="
        + repr([str(ROOT), str(ROOT / "design/component-catalogue/src")])
        + "\nfrom engineering.factory_examples.native import export_native\nexport_native("
        + repr(str(model.resolve()))
        + ","
        + repr(str(folder.resolve()))
        + ")\n"
    )
    binary = shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
    command = (
        [binary]
        if binary
        else [
            "flatpak",
            "run",
            "--filesystem=" + str(ROOT),
            "--filesystem=" + str(folder.resolve()),
            "--command=FreeCADCmd",
            "org.freecad.FreeCAD",
        ]
    )
    try:
        _run(
            [*command, str(script.resolve())],
            ROOT,
            folder / "native-runner.log",
            _Time(remaining_seconds or seconds),
            maximum=600,
        )
    except TimeoutError as error:
        raise BudgetExceeded(
            "factory native geometry exceeded remaining wall budget"
        ) from error
    charge(0, "factory-native-completed")
    receipt = json.loads((folder / "native-cad.json").read_text())
    if (
        receipt["input_sha256"] != hashlib.sha256(model.read_bytes()).hexdigest()
        or not receipt["fcstd_reopened"]
        or not receipt["step_reopened"]
    ):
        raise ValueError("factory native identity or round-trip failure")
    result["definition"]["native_confirmation"] = receipt
    result["checks"]["native_geometry"] = dict(
        state="passed",
        basis="Fresh FreeCAD solids, volumes/bounds and FCStd/STEP reopen; steel subset collision screen where declared; no resistance qualification",
    )

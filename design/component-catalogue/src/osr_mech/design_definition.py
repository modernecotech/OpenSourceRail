"""Top-down / bottom-up mechanical design definition and optimizer.

This module is intentionally lightweight: it can run in ordinary Python
without FreeCAD, CalculiX, NumPy, or supplier CAD. It defines the design
tree that sits above the parametric geometry:

- top-level requirements and objectives;
- external bought-in components;
- fabricated parts owned by OSR;
- subassemblies that combine bought-in and fabricated items;
- final assemblies and candidate configurations;
- a deterministic design-space iterator that picks the best feasible
  candidate inside the declared options.

The generated JSON/Markdown outputs are planning artefacts. When a
candidate is promoted, the existing FreeCAD/FEM launchers regenerate the
geometry and screening evidence from the same parametric source.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from osr_mech.common import ConsistFamily, consist_platform_length_m


@dataclass(frozen=True)
class Requirement:
    id: str
    description: str
    unit: str
    target: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    weight: float = 1.0


@dataclass(frozen=True)
class ExternalComponent:
    id: str
    role: str
    selection_class: str
    mass_kg: float
    base_cost_usd: float
    continuous_power_kw: float = 0.0
    usable_energy_kwh: float = 0.0
    thermal_capacity_kw: float = 0.0
    maturity: str = "supplier-neutral envelope"
    interface_owner: str = "OSR owns envelope/datum; supplier owns internals"


@dataclass(frozen=True)
class FabricatedPart:
    id: str
    role: str
    material: str
    process: str
    mass_kg: float
    base_cost_usd: float
    design_owner: str = "OSR"


@dataclass(frozen=True)
class Subassembly:
    id: str
    role: str
    children: tuple[str, ...]
    acceptance_checks: tuple[str, ...]


@dataclass(frozen=True)
class FinalAssembly:
    id: str
    role: str
    children: tuple[str, ...]
    release_gates: tuple[str, ...]


@dataclass(frozen=True)
class CandidateParameters:
    family: ConsistFamily
    car_length_m: float
    structure_gauge: str
    bogie_frame_gauge: str
    motor_id: str
    battery_id: str
    hvac_id: str
    pv_modules_per_car: int


@dataclass(frozen=True)
class DesignCandidate:
    id: str
    parameters: CandidateParameters
    feasible: bool
    score: float
    violations: tuple[str, ...]
    metrics: dict[str, float]
    mass_breakdown_kg: dict[str, float]


@dataclass(frozen=True)
class DesignRun:
    requirements: tuple[Requirement, ...]
    external_components: tuple[ExternalComponent, ...]
    fabricated_parts: tuple[FabricatedPart, ...]
    subassemblies: tuple[Subassembly, ...]
    final_assemblies: tuple[FinalAssembly, ...]
    iterations: int
    optimum: DesignCandidate
    trace: tuple[DesignCandidate, ...]


CAR_COUNT: dict[ConsistFamily, int] = {
    ConsistFamily.URBAN_SHUTTLE_1CAR: 1,
    ConsistFamily.TRAM_2CAR: 2,
    ConsistFamily.LIGHT_METRO_3CAR: 3,
    ConsistFamily.METRO_4CAR: 4,
    ConsistFamily.METRO_6CAR: 6,
}


REQUIREMENTS: tuple[Requirement, ...] = (
    Requirement(
        id="RS-TOP-001",
        description="Fit the chosen consist inside the RFC platform envelope with stopping margin.",
        unit="m",
        minimum=1.0,
        weight=1.5,
    ),
    Requirement(
        id="RS-TOP-002",
        description="Keep planning axle load inside light-metro civil envelope.",
        unit="kg/axle",
        maximum=11_000.0,
        weight=1.4,
    ),
    Requirement(
        id="RS-TOP-003",
        description="Deliver useful off-wire range for resilient/depot operation.",
        unit="km",
        minimum=50.0,
        weight=1.2,
    ),
    Requirement(
        id="RS-TOP-004",
        description="Provide continuous traction power margin for urban acceleration.",
        unit="ratio",
        minimum=1.0,
        weight=1.2,
    ),
    Requirement(
        id="RS-TOP-005",
        description="Provide hot-climate HVAC capacity margin.",
        unit="ratio",
        minimum=1.0,
        weight=0.9,
    ),
    Requirement(
        id="RS-TOP-006",
        description="Minimise direct material and supplier-module cost.",
        unit="USD",
        target=650_000.0,
        weight=1.0,
    ),
    Requirement(
        id="RS-TOP-007",
        description="Minimise fleet mass to reduce civil, energy, and brake loads.",
        unit="t",
        target=75.0,
        weight=1.1,
    ),
)


EXTERNAL_COMPONENTS: tuple[ExternalComponent, ...] = (
    ExternalComponent(
        id="motor-350kw-hm47-class",
        role="traction motor",
        selection_class="350 kW peak heavy-vehicle PMSM, HM47-class qualified reference envelope",
        mass_kg=340.0,
        base_cost_usd=5_500.0,
        continuous_power_kw=250.0,
        maturity="RFQ reference; continuous duty, rail vibration, gearing, EMC, and 50 C thermal evidence open",
    ),
    ExternalComponent(
        id="battery-225kwh-lfp-800v",
        role="traction battery pack per car",
        selection_class="225 kWh gross / 180 kWh usable liquid-cooled LFP, 650–700 V nominal",
        mass_kg=1_450.0,
        base_cost_usd=25_000.0,
        usable_energy_kwh=180.0,
        maturity="EVE-class RFQ reference; IEC 62928, vibration, propagation, venting, and custom-pack evidence open",
    ),
    ExternalComponent(
        id="hvac-24kw-direct-hv-dc",
        role="roof HVAC per car",
        selection_class="24 kW direct 650–700 V DC packaged roof HVAC for high ambient",
        mass_kg=510.0,
        base_cost_usd=5_750.0,
        thermal_capacity_kw=24.0,
        maturity="Longertek-class RFQ reference; 50 C curve, rail vibration, EMC, and service evidence open",
    ),
)


FABRICATED_PARTS: tuple[FabricatedPart, ...] = (
    FabricatedPart(
        id="fab-carbody-primary-shell",
        role="primary car body shell, side frames, floor pan, roof bows",
        material="S355 steel + FR composite cladding",
        process="CNC cut, press-brake, MIG/MAG weld, adhesive bond",
        mass_kg=8_800.0,
        base_cost_usd=46_000.0,
    ),
    FabricatedPart(
        id="fab-bogie-frame-powered",
        role="powered bogie frame and motor cradle weldment",
        material="S355/S460 welded steel",
        process="cut plate, fixture weld, machine pivot/air-spring datums",
        mass_kg=1_450.0,
        base_cost_usd=7_000.0,
    ),
    FabricatedPart(
        id="fab-bogie-frame-trailer",
        role="trailer bogie frame weldment",
        material="S355/S460 welded steel",
        process="cut plate, fixture weld, machine pivot/air-spring datums",
        mass_kg=1_180.0,
        base_cost_usd=5_200.0,
    ),
    FabricatedPart(
        id="fab-cowl-and-interface-kit",
        role="fiberglass end cowl casts, crash ring, backing ring, lamp/sensor hatches",
        material="fire-rated FRP + steel ring",
        process="low-volume moulding, trim/drill jig, adhesive bond",
        mass_kg=620.0,
        base_cost_usd=9_000.0,
    ),
    FabricatedPart(
        id="fab-articulation-adapter-kit",
        role="inter-car adapter frames, anti-lift keepers, service-loop brackets",
        material="S355 machined/welded steel",
        process="cut, weld, machine shims and datum faces",
        mass_kg=900.0,
        base_cost_usd=9_000.0,
    ),
)


SUBASSEMBLIES: tuple[Subassembly, ...] = (
    Subassembly(
        id="sub-car-module",
        role="one repeated 16.5 m car module",
        children=(
            "fab-carbody-primary-shell",
            "traction battery pack per car",
            "roof HVAC per car",
            "door/window/interior COTS interfaces",
            "one powered bogie",
            "one trailer bogie",
        ),
        acceptance_checks=(
            "body datum survey",
            "door cassette gauge",
            "battery vent and service-lid gauge",
            "roof HVAC/PV clearance",
        ),
    ),
    Subassembly(
        id="sub-powered-bogie",
        role="powered bogie with motor, gearbox, brakes, wheelsets, and suspension",
        children=(
            "fab-bogie-frame-powered",
            "traction motor",
            "gearbox",
            "wheelsets",
            "brake/suspension COTS",
        ),
        acceptance_checks=("weld records", "wheelbase/gauge survey", "motor cradle load proof"),
    ),
    Subassembly(
        id="sub-final-trainset",
        role="complete cabless consist assembled from repeated cars",
        children=("sub-car-module × N", "fab-cowl-and-interface-kit × 2", "fab-articulation-adapter-kit × N-1"),
        acceptance_checks=("trainset envelope", "mass budget", "traction/brake thermal budget", "FEM screening"),
    ),
)


FINAL_ASSEMBLIES: tuple[FinalAssembly, ...] = (
    FinalAssembly(
        id="final-light-metro-trainset",
        role="repeated-car driverless light-metro trainset",
        children=("sub-final-trainset",),
        release_gates=(
            "requirements scorecard feasible",
            "FreeCAD review assemblies regenerated",
            "FEM screening summary green/accepted",
            "BOM and supplier evidence frozen",
        ),
    ),
)


def _component(component_id: str) -> ExternalComponent:
    for item in EXTERNAL_COMPONENTS:
        if item.id == component_id:
            return item
    raise KeyError(component_id)


def _fabricated(part_id: str) -> FabricatedPart:
    for item in FABRICATED_PARTS:
        if item.id == part_id:
            return item
    raise KeyError(part_id)


def candidate_id(params: CandidateParameters) -> str:
    return (
        f"{params.family.value}__{params.car_length_m:.1f}m"
        f"__{params.structure_gauge}-body__{params.bogie_frame_gauge}-bogie"
        f"__{params.motor_id}__{params.battery_id}__{params.hvac_id}"
        f"__pv{params.pv_modules_per_car}"
    ).replace(".", "p")


def evaluate_candidate(params: CandidateParameters) -> DesignCandidate:
    cars = CAR_COUNT[params.family]
    platform_m = consist_platform_length_m(params.family)
    trainset_length_m = cars * params.car_length_m
    platform_margin_m = platform_m - trainset_length_m

    motor = _component(params.motor_id)
    battery = _component(params.battery_id)
    hvac = _component(params.hvac_id)

    body = _fabricated("fab-carbody-primary-shell")
    powered_bogie = _fabricated("fab-bogie-frame-powered")
    trailer_bogie = _fabricated("fab-bogie-frame-trailer")
    cowl = _fabricated("fab-cowl-and-interface-kit")
    articulation = _fabricated("fab-articulation-adapter-kit")

    structure_factor = {"light": 0.94, "reference": 1.0, "heavy": 1.10}[params.structure_gauge]
    bogie_factor = {"light": 0.95, "reference": 1.0, "heavy": 1.12}[params.bogie_frame_gauge]
    length_factor = params.car_length_m / 17.0

    pv_mass_per_module_kg = 24.0
    pv_cost_per_module_usd = 240.0
    pv_kw_per_module = 0.42
    common_cots_mass_per_car_kg = 5_450.0
    common_cots_cost_per_car_usd = 70_000.0
    wheel_brake_suspension_mass_per_bogie_kg = 2_050.0
    wheel_brake_suspension_cost_per_bogie_usd = 15_500.0
    gearbox_mass_per_powered_bogie_kg = 380.0
    gearbox_cost_per_powered_bogie_usd = 5_000.0
    inverter_mass_per_powered_bogie_kg = 60.0  # two ~30 kg controllers
    inverter_cost_per_powered_bogie_usd = 8_000.0

    body_mass_total = cars * body.mass_kg * structure_factor * length_factor
    body_cost_total = cars * body.base_cost_usd * (0.85 + 0.15 * structure_factor) * length_factor

    powered_bogies = cars
    trailer_bogies = cars
    bogie_mass_total = (
        powered_bogies * powered_bogie.mass_kg * bogie_factor
        + trailer_bogies * trailer_bogie.mass_kg * bogie_factor
        + (powered_bogies + trailer_bogies) * wheel_brake_suspension_mass_per_bogie_kg
    )
    bogie_cost_total = (
        powered_bogies * powered_bogie.base_cost_usd * bogie_factor
        + trailer_bogies * trailer_bogie.base_cost_usd * bogie_factor
        + (powered_bogies + trailer_bogies) * wheel_brake_suspension_cost_per_bogie_usd
    )

    motors_per_powered_bogie = 2
    motor_count = powered_bogies * motors_per_powered_bogie
    traction_mass_total = motor_count * motor.mass_kg + powered_bogies * (
        gearbox_mass_per_powered_bogie_kg + inverter_mass_per_powered_bogie_kg
    )
    traction_cost_total = motor_count * motor.base_cost_usd + powered_bogies * (
        gearbox_cost_per_powered_bogie_usd + inverter_cost_per_powered_bogie_usd
    )

    battery_mass_total = cars * battery.mass_kg
    battery_cost_total = cars * battery.base_cost_usd
    hvac_mass_total = cars * hvac.mass_kg
    hvac_cost_total = cars * hvac.base_cost_usd
    pv_mass_total = cars * params.pv_modules_per_car * pv_mass_per_module_kg
    pv_cost_total = cars * params.pv_modules_per_car * pv_cost_per_module_usd
    common_mass_total = cars * common_cots_mass_per_car_kg
    common_cost_total = cars * common_cots_cost_per_car_usd
    cowl_mass_total = 2 * cowl.mass_kg
    cowl_cost_total = 2 * cowl.base_cost_usd
    articulation_mass_total = max(0, cars - 1) * articulation.mass_kg
    articulation_cost_total = max(0, cars - 1) * articulation.base_cost_usd

    mass_breakdown_kg = {
        "carbody primary structure": body_mass_total,
        "bogie frames, wheelsets, brakes, and suspension": bogie_mass_total,
        "traction motors, gearboxes, and controllers": traction_mass_total,
        "traction batteries": battery_mass_total,
        "roof HVAC": hvac_mass_total,
        "roof PV": pv_mass_total,
        "doors, glazing, interior, and auxiliaries": common_mass_total,
        "end cowls and interfaces": cowl_mass_total,
        "inter-car articulation": articulation_mass_total,
    }
    mass_kg = sum(mass_breakdown_kg.values())
    cost_usd = (
        body_cost_total
        + bogie_cost_total
        + traction_cost_total
        + battery_cost_total
        + hvac_cost_total
        + pv_cost_total
        + common_cost_total
        + cowl_cost_total
        + articulation_cost_total
    )

    mass_t = mass_kg / 1000.0
    axle_count = cars * 4
    axle_load_kg = mass_kg / axle_count
    installed_continuous_kw = motor_count * motor.continuous_power_kw
    traction_required_kw = mass_t * 7.0
    traction_margin = installed_continuous_kw / traction_required_kw
    battery_usable_kwh = cars * battery.usable_energy_kwh
    pv_peak_kw = cars * params.pv_modules_per_car * pv_kw_per_module
    energy_kwh_per_km = 5.2 + 0.035 * mass_t
    offwire_range_km = battery_usable_kwh / energy_kwh_per_km
    hvac_margin = (cars * hvac.thermal_capacity_kw) / (cars * 20.0)
    manufacturing_complexity = (
        1.0
        + {"light": 0.05, "reference": 0.0, "heavy": 0.12}[params.structure_gauge]
        + {"light": 0.04, "reference": 0.0, "heavy": 0.10}[params.bogie_frame_gauge]
        + max(0, params.pv_modules_per_car - 16) * 0.01
    )

    metrics = {
        "cars": float(cars),
        "trainset_length_m": round(trainset_length_m, 3),
        "platform_margin_m": round(platform_margin_m, 3),
        "mass_t": round(mass_t, 3),
        "cost_usd": round(cost_usd, 2),
        "axle_load_kg": round(axle_load_kg, 2),
        "installed_continuous_kw": round(installed_continuous_kw, 2),
        "traction_margin": round(traction_margin, 3),
        "battery_usable_kwh": round(battery_usable_kwh, 2),
        "offwire_range_km": round(offwire_range_km, 3),
        "hvac_margin": round(hvac_margin, 3),
        "pv_peak_kw": round(pv_peak_kw, 3),
        "manufacturing_complexity_index": round(manufacturing_complexity, 3),
    }

    violations: list[str] = []
    if platform_margin_m < 1.0:
        violations.append("platform margin below 1.0 m")
    if axle_load_kg > 11_000.0:
        violations.append("axle load above 11,000 kg")
    if offwire_range_km < 50.0:
        violations.append("off-wire range below 50 km")
    if traction_margin < 1.0:
        violations.append("traction power margin below 1.0")
    if hvac_margin < 1.0:
        violations.append("HVAC thermal margin below 1.0")

    feasible = not violations
    score = score_candidate(metrics, feasible)
    return DesignCandidate(
        id=candidate_id(params),
        parameters=params,
        feasible=feasible,
        score=round(score, 3),
        violations=tuple(violations),
        metrics=metrics,
        mass_breakdown_kg={key: round(value, 2) for key, value in mass_breakdown_kg.items()},
    )


def _benefit(value: float, minimum: float, excellent: float) -> float:
    if value <= minimum:
        return 0.0
    if value >= excellent:
        return 1.0
    return (value - minimum) / (excellent - minimum)


def _cost_benefit(value: float, target: float, unacceptable: float) -> float:
    if value <= target:
        return 1.0
    if value >= unacceptable:
        return 0.0
    return 1.0 - (value - target) / (unacceptable - target)


def score_candidate(metrics: dict[str, float], feasible: bool) -> float:
    score = 0.0
    score += 15.0 * _benefit(metrics["platform_margin_m"], 1.0, 10.0)
    score += 15.0 * _benefit(11_000.0 - metrics["axle_load_kg"], 0.0, 4_000.0)
    score += 14.0 * _benefit(metrics["offwire_range_km"], 50.0, 80.0)
    score += 12.0 * _benefit(metrics["traction_margin"], 1.0, 2.8)
    score += 8.0 * _benefit(metrics["hvac_margin"], 1.0, 1.2)
    score += 16.0 * _cost_benefit(metrics["cost_usd"], 650_000.0, 900_000.0)
    score += 12.0 * _cost_benefit(metrics["mass_t"], 75.0, 105.0)
    score += 8.0 * _cost_benefit(metrics["manufacturing_complexity_index"], 1.0, 1.35)
    if not feasible:
        score *= 0.35
    return score


def parameter_space(family: ConsistFamily) -> Iterable[CandidateParameters]:
    car_lengths = (16.5, 17.0, 17.5)
    structure_gauges = ("light", "reference", "heavy")
    bogie_frame_gauges = ("light", "reference", "heavy")
    motor_ids = tuple(c.id for c in EXTERNAL_COMPONENTS if c.role == "traction motor")
    battery_ids = tuple(c.id for c in EXTERNAL_COMPONENTS if c.role == "traction battery pack per car")
    hvac_ids = tuple(c.id for c in EXTERNAL_COMPONENTS if c.role == "roof HVAC per car")
    pv_modules = (12, 16, 20)

    for values in itertools.product(
        car_lengths,
        structure_gauges,
        bogie_frame_gauges,
        motor_ids,
        battery_ids,
        hvac_ids,
        pv_modules,
    ):
        car_length_m, structure_gauge, bogie_frame_gauge, motor_id, battery_id, hvac_id, pv = values
        yield CandidateParameters(
            family=family,
            car_length_m=car_length_m,
            structure_gauge=structure_gauge,
            bogie_frame_gauge=bogie_frame_gauge,
            motor_id=motor_id,
            battery_id=battery_id,
            hvac_id=hvac_id,
            pv_modules_per_car=pv,
        )


def iterate_design_space(
    family: ConsistFamily = ConsistFamily.LIGHT_METRO_3CAR,
    *,
    max_iterations: int | None = None,
) -> DesignRun:
    trace: list[DesignCandidate] = []
    optimum: DesignCandidate | None = None
    for index, params in enumerate(parameter_space(family), start=1):
        if max_iterations is not None and index > max_iterations:
            break
        candidate = evaluate_candidate(params)
        trace.append(candidate)
        if optimum is None:
            optimum = candidate
        elif (candidate.feasible, candidate.score) > (optimum.feasible, optimum.score):
            optimum = candidate

    if optimum is None:
        raise ValueError("empty design space")

    return DesignRun(
        requirements=REQUIREMENTS,
        external_components=EXTERNAL_COMPONENTS,
        fabricated_parts=FABRICATED_PARTS,
        subassemblies=SUBASSEMBLIES,
        final_assemblies=FINAL_ASSEMBLIES,
        iterations=len(trace),
        optimum=optimum,
        trace=tuple(trace),
    )


def _serialise(value):
    if isinstance(value, ConsistFamily):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    raise TypeError(f"cannot serialise {type(value)!r}")


def write_outputs(run: DesignRun, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "design-iteration.json"
    md_path = out_dir / "design-iteration-summary.md"
    feasible = sorted((c for c in run.trace if c.feasible), key=lambda c: c.score, reverse=True)
    infeasible = sorted((c for c in run.trace if not c.feasible), key=lambda c: c.score, reverse=True)
    payload = {
        "requirements": run.requirements,
        "external_components": run.external_components,
        "fabricated_parts": run.fabricated_parts,
        "subassemblies": run.subassemblies,
        "final_assemblies": run.final_assemblies,
        "iterations": run.iterations,
        "feasible_candidates": len(feasible),
        "infeasible_candidates": len(infeasible),
        "optimum": run.optimum,
        "top_feasible": feasible[:25],
        "top_infeasible": infeasible[:10],
        "trace_note": (
            "The optimizer evaluated the full declared discrete design space in memory; "
            "this generated JSON stores ranked shortlists to keep the repository compact."
        ),
    }
    json_path.write_text(
        json.dumps(payload, default=_serialise, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(render_markdown(run), encoding="utf-8")
    return json_path, md_path


def render_markdown(run: DesignRun) -> str:
    top = run.optimum
    lines = [
        "# Rolling-stock design iteration summary",
        "",
        "This file is generated by `tools/automation/design-iterate.sh`. It records the best",
        "candidate inside the declared discrete design space; it is not a supplier",
        "freeze or homologated drawing release.",
        "",
        f"- Iterations evaluated: {run.iterations}",
        f"- Best candidate: `{top.id}`",
        f"- Feasible: `{str(top.feasible).lower()}`",
        f"- Score: `{top.score:.3f}`",
        "",
        "## Best-candidate metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in top.metrics.items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Best-candidate modeled mass breakdown",
            "",
            "This is the optimizer subtotal before the promoted engineering reserve.",
            "",
            "| Category | Mass (kg) |",
            "|---|---:|",
        ]
    )
    for category, mass_kg in top.mass_breakdown_kg.items():
        lines.append(f"| {category} | {mass_kg:.2f} |")
    lines.append(f"| **Modeled subtotal** | **{sum(top.mass_breakdown_kg.values()):.2f}** |")
    if top.violations:
        lines.extend(["", "## Violations", ""])
        for violation in top.violations:
            lines.append(f"- {violation}")
    lines.extend(
        [
            "",
            "## Best-candidate parameters",
            "",
            "| Parameter | Value |",
            "|---|---|",
            f"| family | `{top.parameters.family.value}` |",
            f"| car length | `{top.parameters.car_length_m:.1f} m` |",
            f"| body structure gauge | `{top.parameters.structure_gauge}` |",
            f"| bogie frame gauge | `{top.parameters.bogie_frame_gauge}` |",
            f"| motor | `{top.parameters.motor_id}` |",
            f"| battery | `{top.parameters.battery_id}` |",
            f"| HVAC | `{top.parameters.hvac_id}` |",
            f"| PV modules per car | `{top.parameters.pv_modules_per_car}` |",
            "",
            "## Design hierarchy",
            "",
            "### External components",
            "",
            "| ID | Role | Selection class |",
            "|---|---|---|",
        ]
    )
    for item in run.external_components:
        lines.append(f"| `{item.id}` | {item.role} | {item.selection_class} |")
    lines.extend(["", "### Fabricated parts", "", "| ID | Role | Process |", "|---|---|---|"])
    for item in run.fabricated_parts:
        lines.append(f"| `{item.id}` | {item.role} | {item.process} |")
    lines.extend(["", "### Subassemblies", "", "| ID | Role | Acceptance checks |", "|---|---|---|"])
    for item in run.subassemblies:
        checks = "<br>".join(item.acceptance_checks)
        lines.append(f"| `{item.id}` | {item.role} | {checks} |")
    lines.extend(
        [
            "",
            "## Top ten feasible candidates",
            "",
            "| Rank | Candidate | Score | Mass t | Cost USD | Range km | Traction margin |",
            "|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    feasible = sorted((c for c in run.trace if c.feasible), key=lambda c: c.score, reverse=True)
    for rank, candidate in enumerate(feasible[:10], start=1):
        lines.append(
            f"| {rank} | `{candidate.id}` | {candidate.score:.3f} | "
            f"{candidate.metrics['mass_t']} | {candidate.metrics['cost_usd']:.0f} | "
            f"{candidate.metrics['offwire_range_km']} | {candidate.metrics['traction_margin']} |"
        )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Define and iterate the OSR top-down/bottom-up mechanical design space."
    )
    parser.add_argument(
        "--family",
        choices=[family.value for family in ConsistFamily],
        default=ConsistFamily.LIGHT_METRO_3CAR.value,
        help="Consist family to optimise.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=0,
        help="Maximum candidates to evaluate; 0 means exhaust the declared discrete design space.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "catalog" / "design-system",
        help="Output directory for generated JSON and Markdown summaries.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    max_iterations = None if args.max_iterations == 0 else args.max_iterations
    run = iterate_design_space(ConsistFamily(args.family), max_iterations=max_iterations)
    json_path, md_path = write_outputs(run, args.out)
    print(f"evaluated {run.iterations} candidates")
    print(f"best candidate: {run.optimum.id}")
    print(f"score: {run.optimum.score:.3f}; feasible: {str(run.optimum.feasible).lower()}")
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()

"""One-metre clip-on fiberglass exterior body modules.

The welded steel underframe and spaceframe remain the certified load path.
These modules provide the weather skin, finish, and replaceable local damage
zone.  A 16.5 m car carries sixteen 1 m longitudinal cladding bays between
250 mm steel end-ring transitions; no full-length body mould is required.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from osr_mech.cad import Box, Color, Compound, Location, Part


MODULE_WIDTH_MM = 1_000.0
MODULE_JOINT_GAP_MM = 6.0
MODULE_DEPTH_MM = 28.0
END_RING_TRANSITION_MM = 250.0
CLIPS_PER_MODULE = 4
SIDE_MODULES_PER_CAR = 32
ROOF_MODULES_PER_CAR = 16
MODULES_PER_CAR = SIDE_MODULES_PER_CAR + ROOF_MODULES_PER_CAR

COLOR_FIBERGLASS = Color(0.91, 0.91, 0.88)
COLOR_ROOF_FIBERGLASS = Color(0.82, 0.84, 0.84)
COLOR_CLIP = Color(0.66, 0.68, 0.70)
COLOR_GASKET = Color(0.04, 0.04, 0.045)


@dataclass(frozen=True)
class CladdingBay:
    index: int
    x_center_mm: float
    width_mm: float = MODULE_WIDTH_MM


@dataclass(frozen=True)
class AssemblyPhase:
    sequence: int
    activity: str
    elapsed_hours: float
    parallel_crews: int
    release_check: str


def cladding_bays(body_length_mm: float) -> tuple[CladdingBay, ...]:
    """Return the repeated 1 m bays centred between steel end transitions."""

    usable_length = body_length_mm - 2.0 * END_RING_TRANSITION_MM
    count = int(round(usable_length / MODULE_WIDTH_MM))
    if abs(usable_length - count * MODULE_WIDTH_MM) > 1e-6:
        raise ValueError(
            "body length must leave an integer number of 1 m cladding bays "
            f"after two {END_RING_TRANSITION_MM:.0f} mm end transitions"
        )
    first_center = -usable_length / 2.0 + MODULE_WIDTH_MM / 2.0
    return tuple(
        CladdingBay(index=index + 1, x_center_mm=first_center + index * MODULE_WIDTH_MM)
        for index in range(count)
    )


def _overlap(
    bay: CladdingBay,
    aperture_center_mm: float,
    aperture_width_mm: float,
) -> tuple[float, float] | None:
    bay_left = bay.x_center_mm - bay.width_mm / 2.0
    bay_right = bay.x_center_mm + bay.width_mm / 2.0
    aperture_left = aperture_center_mm - aperture_width_mm / 2.0
    aperture_right = aperture_center_mm + aperture_width_mm / 2.0
    left = max(bay_left, aperture_left)
    right = min(bay_right, aperture_right)
    if right <= left:
        return None
    return ((left + right) / 2.0, right - left)


def _side_module(
    bay: CladdingBay,
    side: str,
    body_width_mm: float,
    body_height_mm: float,
    door_centres_mm: tuple[float, ...],
    door_width_mm: float,
    door_sill_mm: float,
    door_height_mm: float,
    window_zones: tuple[tuple[float, float], ...],
    window_sill_mm: float,
    window_height_mm: float,
) -> Part:
    y_sign = -1.0 if side == "left" else 1.0
    panel_width = bay.width_mm - MODULE_JOINT_GAP_MM
    panel = Box(panel_width, MODULE_DEPTH_MM, body_height_mm).locate(
        Location(
            (
                bay.x_center_mm,
                y_sign * (body_width_mm / 2.0 + MODULE_DEPTH_MM / 2.0),
                body_height_mm / 2.0,
            )
        )
    )
    panel.color = COLOR_FIBERGLASS
    panel.label = f"1 m clip-on fiberglass side module {side} bay {bay.index:02d}"

    for center in door_centres_mm:
        overlap = _overlap(bay, center, door_width_mm)
        if overlap is None:
            continue
        cut_center, cut_width = overlap
        panel = panel - Box(
            cut_width + MODULE_JOINT_GAP_MM,
            MODULE_DEPTH_MM + 20.0,
            door_height_mm,
        ).locate(Location((cut_center, y_sign * body_width_mm / 2.0, door_sill_mm + door_height_mm / 2.0)))

    for center, width in window_zones:
        overlap = _overlap(bay, center, width)
        if overlap is None:
            continue
        cut_center, cut_width = overlap
        panel = panel - Box(
            cut_width + MODULE_JOINT_GAP_MM,
            MODULE_DEPTH_MM + 20.0,
            window_height_mm,
        ).locate(Location((cut_center, y_sign * body_width_mm / 2.0, window_sill_mm + window_height_mm / 2.0)))

    panel.color = COLOR_FIBERGLASS
    panel.label = f"1 m clip-on fiberglass side module {side} bay {bay.index:02d}"
    return panel


def _roof_module(bay: CladdingBay, body_width_mm: float, body_height_mm: float) -> Part:
    module = Box(
        bay.width_mm - MODULE_JOINT_GAP_MM,
        body_width_mm - 2.0 * END_RING_TRANSITION_MM,
        MODULE_DEPTH_MM,
    ).locate(Location((bay.x_center_mm, 0.0, body_height_mm + MODULE_DEPTH_MM / 2.0)))
    module.color = COLOR_ROOF_FIBERGLASS
    module.label = f"1 m clip-on fiberglass roof module bay {bay.index:02d}"
    return module


def _module_clips(
    bay: CladdingBay,
    body_width_mm: float,
    body_height_mm: float,
) -> list[Part]:
    clips: list[Part] = []
    for y_sign, side in ((-1.0, "left"), (1.0, "right")):
        for x_offset, z in ((-310.0, 620.0), (310.0, 620.0), (-310.0, 2_850.0), (310.0, 2_850.0)):
            clip = Box(80.0, 34.0, 55.0).locate(
                Location((bay.x_center_mm + x_offset, y_sign * (body_width_mm / 2.0 - 3.0), z))
            )
            clip.color = COLOR_CLIP
            clip.label = f"Captive keyed over-centre clip {side} bay {bay.index:02d}"
            clips.append(clip)
    for y_offset in (-720.0, 720.0):
        for x_offset in (-310.0, 310.0):
            clip = Box(80.0, 55.0, 34.0).locate(
                Location((bay.x_center_mm + x_offset, y_offset, body_height_mm - 3.0))
            )
            clip.color = COLOR_CLIP
            clip.label = f"Captive keyed roof clip bay {bay.index:02d}"
            clips.append(clip)
    return clips


def fiberglass_cladding_system(
    *,
    body_length_mm: float,
    body_width_mm: float,
    body_height_mm: float,
    door_centres_mm: tuple[float, ...],
    door_width_mm: float,
    door_sill_mm: float,
    door_height_mm: float,
    window_zones: tuple[tuple[float, float], ...],
    window_sill_mm: float,
    window_height_mm: float,
) -> Compound:
    """Build the complete removable fiberglass weather skin for one car."""

    bays = cladding_bays(body_length_mm)
    side_modules = [
        _side_module(
            bay,
            side,
            body_width_mm,
            body_height_mm,
            door_centres_mm,
            door_width_mm,
            door_sill_mm,
            door_height_mm,
            window_zones,
            window_sill_mm,
            window_height_mm,
        )
        for bay in bays
        for side in ("left", "right")
    ]
    roof_modules = [_roof_module(bay, body_width_mm, body_height_mm) for bay in bays]
    clips = [clip for bay in bays for clip in _module_clips(bay, body_width_mm, body_height_mm)]
    gaskets: list[Part] = []
    for boundary in range(1, len(bays)):
        x = bays[0].x_center_mm - MODULE_WIDTH_MM / 2.0 + boundary * MODULE_WIDTH_MM
        for y_sign in (-1.0, 1.0):
            gasket = Box(MODULE_JOINT_GAP_MM, 12.0, body_height_mm - 160.0).locate(
                Location((x, y_sign * body_width_mm / 2.0, body_height_mm / 2.0))
            )
            gasket.color = COLOR_GASKET
            gasket.label = "Replaceable EPDM vertical module-joint gasket"
            gaskets.append(gasket)

    return Compound(
        label="One-metre clip-on fiberglass body cladding system",
        children=[
            Compound(label="Clip-on fiberglass side modules", children=side_modules),
            Compound(label="Clip-on fiberglass roof modules", children=roof_modules),
            Compound(label="Captive mechanical clips and anti-lift retainers", children=clips),
            Compound(label="Dry EPDM compression seals and drain joints", children=gaskets),
        ],
    )


def one_day_trainset_assembly_plan() -> tuple[AssemblyPhase, ...]:
    """One-shift exterior-body route for three released 16.5 m frames."""

    return (
        AssemblyPhase(10, "Receive three released frames and verify clip-rail datums", 0.5, 3, "frame and kit revision match"),
        AssemblyPhase(20, "Fit dry EPDM seals and inspect keyed clip receptacles", 1.0, 6, "continuous seal and open drains"),
        AssemblyPhase(30, "Hang and latch left/right 1 m side modules", 3.0, 6, "every captive witness mark visible"),
        AssemblyPhase(40, "Hang and latch 1 m roof modules from mobile access stands", 1.5, 6, "anti-lift retainers closed"),
        AssemblyPhase(50, "Fit corner closures, skirts, labels, and earth bonds", 1.0, 6, "bond continuity and service access"),
        AssemblyPhase(60, "Water test, rattle check, snag closeout, and QA release", 1.0, 3, "dry interior and signed module map"),
    )


def design_manifest() -> dict[str, object]:
    plan = one_day_trainset_assembly_plan()
    return {
        "design_id": "LM3-BDY-160",
        "description": "one-metre clip-on non-structural fiberglass body modules",
        "module_width_mm": MODULE_WIDTH_MM,
        "car_body_length_mm": 16_500.0,
        "steel_end_transition_mm_each": END_RING_TRANSITION_MM,
        "bays_per_car": 16,
        "side_modules_per_car": SIDE_MODULES_PER_CAR,
        "roof_modules_per_car": ROOF_MODULES_PER_CAR,
        "modules_per_car": MODULES_PER_CAR,
        "modules_per_three_car_trainset": MODULES_PER_CAR * 3,
        "clips_per_module": CLIPS_PER_MODULE,
        "retention": "keyed hook plus captive over-centre clip and independent anti-lift retainer",
        "seal": "replaceable dry EPDM compression gasket; no production adhesive cure",
        "structural_role": "non-structural weather skin; steel frame remains the certified load path",
        "assembly_elapsed_hours": sum(phase.elapsed_hours for phase in plan),
        "assembly_crews": 6,
        "assembly_plan": [asdict(phase) for phase in plan],
    }


def write_design_pack(out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = design_manifest()
    plan = one_day_trainset_assembly_plan()
    json_path = out_dir / "modular-fiberglass-body-manifest.json"
    md_path = out_dir / "README.md"
    json_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# One-metre clip-on fiberglass body design",
        "",
        "Generated from `osr_mech.rolling_stock.modular_fiberglass_body`.",
        "The panels are a non-structural weather skin over the welded steel frame.",
        "",
        "| Parameter | Value |",
        "|---|---:|",
        f"| Longitudinal module pitch | {MODULE_WIDTH_MM:,.0f} mm |",
        f"| Bays per car | {manifest['bays_per_car']} |",
        f"| Modules per car | {MODULES_PER_CAR} |",
        f"| Modules per 3-car trainset | {MODULES_PER_CAR * 3} |",
        f"| Exterior-body assembly elapsed time | {manifest['assembly_elapsed_hours']:.1f} h |",
        "",
        "## One-shift route",
        "",
        "| Seq | Activity | Elapsed | Parallel crews | Release check |",
        "|---:|---|---:|---:|---|",
    ]
    for phase in plan:
        lines.append(
            f"| {phase.sequence} | {phase.activity} | {phase.elapsed_hours:.1f} h | "
            f"{phase.parallel_crews} | {phase.release_check} |"
        )
    lines.extend(
        [
            "",
            "The eight-hour claim applies to installation and release of the exterior body modules on three completed, painted, dimensionally accepted frames. Doors, glazing, traction equipment, bogies, commissioning, and homologation remain separate controlled work.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


if __name__ == "__main__":
    write_design_pack(Path("mechanical-py/catalog/modular-fiberglass-body"))

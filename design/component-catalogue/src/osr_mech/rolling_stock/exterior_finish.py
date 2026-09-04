"""Controlled LM3 exterior-finish zoning and design-review geometry.

Decorative film is deliberately separated from corrosion protection, composite
surface protection and fire qualification.  The calcium-carbonate coating is a
research-led candidate and remains behind coupon and vehicle-trial gates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from osr_mech.cad import Box, Color, Compound, Location


WHITE_BASE = Color(0.90, 0.91, 0.90)
LIVERY = Color(0.10, 0.62, 0.32)
COOL_ROOF = Color(0.97, 0.97, 0.94)
KEEP_OUT = Color(0.16, 0.18, 0.20)


@dataclass(frozen=True)
class FinishZone:
    id: str
    substrate: str
    mandatory_base_system: str
    simplified_finish: str
    replaceable: bool
    prohibited_coverage: tuple[str, ...]
    release_evidence: tuple[str, ...]


@dataclass(frozen=True)
class FinishProcessStep:
    sequence: int
    operation: str
    hold_point: str


def finish_zones() -> tuple[FinishZone, ...]:
    return (
        FinishZone(
            "LM3-FIN-Z01",
            "S355 primary and secondary steel",
            "qualified blast/clean, corrosion primer, stripe coat, topcoat and cavity protection",
            "single light neutral topcoat; optional livery film only after full cure",
            False,
            ("weld inspection lands until released", "earth studs", "machined datums", "drains", "labels"),
            ("surface-preparation record", "coating batch", "dry-film thickness", "holiday/visual inspection", "adhesion/cure release"),
        ),
        FinishZone(
            "LM3-FIN-Z02",
            "clip-on GFRP side modules and end-cowl casts",
            "fire/UV-qualified in-mould white gelcoat or compatible primer/base topcoat with sealed cut edges",
            "pre-cut rail-use graphic film for coloured livery bands, logos and replaceable local graphics",
            True,
            ("EPDM seals", "drains", "retained fasteners", "service labels", "glass/lamp edges", "bond/seal lands"),
            ("substrate cure/cleanliness", "film-system certificate", "adhesion coupon", "edge/overlap map", "removal/repair trial"),
        ),
        FinishZone(
            "LM3-FIN-Z03",
            "exposed GFRP roof skins and removable HVAC/PV fairings",
            "fire/UV-qualified in-mould white gelcoat or compatible rail coating",
            "CaCO3-acrylic radiative coating candidate only after coupon and one-car qualification",
            True,
            (
                "PV active area and clamps",
                "HVAC intake/exhaust and heat exchangers",
                "antennas and sensor apertures",
                "walkways and anti-slip pads",
                "lifting/jacking covers",
                "earth bonds",
                "glands, drains, seals, labels and service lands",
            ),
            (
                "fire/chemical compatibility",
                "GFRP adhesion/flexibility",
                "UV/abrasion/wash ageing",
                "new and aged solar reflectance/emittance",
                "glare/visibility review",
                "one-car thermal and maintenance trial",
            ),
        ),
    )


def finish_process() -> tuple[FinishProcessStep, ...]:
    return (
        FinishProcessStep(10, "release corrosion, fire and composite base finish before decorative work", "base finish records accepted"),
        FinishProcessStep(20, "survey, repair, fully cure and clean each film/coating substrate", "signed pre-installation inspection"),
        FinishProcessStep(30, "cut film by module/bay and make film plus roof-coating witness coupons", "coupon adhesion and appearance accepted"),
        FinishProcessStep(40, "dry-apply livery film; mask roof keep-outs and apply qualified candidate coating", "edges, overlaps, mask map and wet/dry film record accepted"),
        FinishProcessStep(50, "inspect, water/wash test, retain coupons and complete removal/repair demonstration", "new-build release or trial-only disposition signed"),
        FinishProcessStep(60, "age coupons and one-car trial through UV, wash, abrasion and service exposure", "aged optical/adhesion and maintenance evidence reviewed"),
    )


def finish_process_payload() -> dict[str, object]:
    return {
        "design_id": "LM3-FIN-260",
        "status": "design-reference; CaCO3 roof route is trial-only",
        "principle": "film simplifies livery but never replaces corrosion, composite-surface or fire protection",
        "film_product_boundary": "rail-application product selected by current supplier bulletin and project fire/adhesion evidence",
        "radiative_research_targets": {
            "initial_solar_reflectance": 0.955,
            "initial_sky_window_emissivity": 0.94,
            "use": "research screening targets only; measure the selected LM3 system new and aged",
        },
        "zones": [asdict(zone) for zone in finish_zones()],
        "process": [asdict(step) for step in finish_process()],
    }


def exterior_finish_review_assembly() -> Compound:
    """Show side-film and roof-coating zones with explicit equipment keep-outs."""

    parts = []
    for side in (-1, 1):
        parts.append(
            Box(16_000, 8, 3_050).locate(Location((0, side * 1_425, 1_525)))
        )
        parts[-1].label = "white in-mould/base finish"
        parts[-1].color = WHITE_BASE
        parts.append(
            Box(16_000, 10, 420).locate(Location((0, side * 1_431, 1_420)))
        )
        parts[-1].label = "replaceable pre-cut livery film band"
        parts[-1].color = LIVERY
    roof = Box(16_000, 2_700, 8).locate(Location((0, 0, 3_454)))
    roof.label = "candidate CaCO3 radiative finish on exposed roof only"
    roof.color = COOL_ROOF
    parts.append(roof)
    for x, width, label in ((-5_200, 2_800, "HVAC keep-out"), (0, 5_600, "PV keep-out"), (5_800, 1_200, "antenna/service keep-out")):
        keep_out = Box(width, 1_900, 16).locate(Location((x, 0, 3_458)))
        keep_out.label = label
        keep_out.color = KEEP_OUT
        parts.append(keep_out)
    return Compound(label="LM3 exterior finish zoning review", children=parts)


__all__ = [
    "FinishProcessStep",
    "FinishZone",
    "exterior_finish_review_assembly",
    "finish_process",
    "finish_process_payload",
    "finish_zones",
]

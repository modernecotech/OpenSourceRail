"""OSR-ALN validator — RFC 0009 v3 / format-spec §"Validator semantics".

Reads an OSR-ALN TOML file and enforces the eight hard gates +
three soft gates from the format spec. Hard-gate failures make
the validator exit nonzero so a CI pipeline can reject bad
alignments before the simulator or interlocking ever sees them.

Stdlib-only: uses `tomllib` (Python 3.11+).

# Preset parameters

The validator carries its own copy of the RFC 0009 §1 preset
table. This must stay in sync with the preset definitions
implemented in the Rust `osr-core` / `osr-design` crates; the
unit tests cover the preset table against a handful of named
RFC values.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class PresetLimits:
    """RFC 0009 §1 preset envelope the validator enforces."""

    name: str
    min_curve_radius_m: float
    max_gradient_per_mille: float
    max_cant_mm: float
    compatible_consists: frozenset[str]


# Preset table mirrored from RFC 0009 §1. Keep in sync with
# `lib/templates/track-geometry.toml`.
PRESETS: dict[str, PresetLimits] = {
    "standard-urban": PresetLimits(
        name="standard-urban",
        min_curve_radius_m=90.0,
        max_gradient_per_mille=50.0,
        max_cant_mm=150.0,
        compatible_consists=frozenset(
            {"tram-2car", "light-metro-3car"}
        ),
    ),
    "standard-metro": PresetLimits(
        name="standard-metro",
        min_curve_radius_m=200.0,
        max_gradient_per_mille=35.0,
        max_cant_mm=160.0,
        compatible_consists=frozenset(
            {"light-metro-3car", "metro-4car", "metro-6car"}
        ),
    ),
    "mainline-mixed": PresetLimits(
        name="mainline-mixed",
        min_curve_radius_m=400.0,
        max_gradient_per_mille=25.0,
        max_cant_mm=180.0,
        compatible_consists=frozenset(
            {"metro-4car", "metro-6car"}
        ),
    ),
}

ALLOWED_CIVIL_CLASSES = frozenset({"at-grade", "elevated", "bridge"})


@dataclass
class ValidationReport:
    """Structured report of all findings from one validation pass."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True iff no hard-gate errors. Warnings do not fail."""
        return not self.errors

    def format_text(self) -> str:
        lines = []
        if self.errors:
            lines.append(f"{len(self.errors)} HARD-GATE FAILURE(S):")
            for e in self.errors:
                lines.append(f"  ✗ {e}")
        if self.warnings:
            lines.append(f"{len(self.warnings)} soft-gate warning(s):")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        if not self.errors and not self.warnings:
            lines.append("✓ all gates clear")
        return "\n".join(lines)


def validate(
    doc: dict,
    known_station_ids: set[str] | None = None,
    known_line_ids: set[str] | None = None,
) -> ValidationReport:
    """Run every hard + soft gate on the parsed OSR-ALN document.

    Parameters
    ----------
    doc:
        The tomllib-parsed OSR-ALN document.
    known_station_ids:
        Set of station ids from the deployment's design.toml. If
        provided, gate H5 checks each `[[station]].id` against it.
        If `None`, H5 is skipped with a warning.
    known_line_ids:
        Set of line ids from the deployment's design.toml. If provided,
        gate H5 also checks `meta.line_id` against it.
    """

    report = ValidationReport()

    # -- H1: preset is recognised --------------------------------------
    meta = doc.get("meta", {})
    preset_name = meta.get("preset")
    if preset_name not in PRESETS:
        report.errors.append(
            f"H1: meta.preset={preset_name!r} is not one of "
            f"{sorted(PRESETS)}"
        )
        # Without a preset we can't evaluate H2/H6/H7/H8 meaningfully.
        return report
    preset = PRESETS[preset_name]

    # -- H2: consist is in the preset's compatible set ----------------
    consist = meta.get("consist")
    if consist not in preset.compatible_consists:
        report.errors.append(
            f"H2: meta.consist={consist!r} is not compatible with preset "
            f"{preset.name!r}; allowed: {sorted(preset.compatible_consists)}"
        )

    horizontal = doc.get("horizontal", [])

    # -- H3 + H4: civil spans contiguous + no tunnels -----------------
    civil = doc.get("civil", [])
    if not civil:
        report.errors.append("H3: no [[civil]] spans declared")
    else:
        # H4 first so we don't confuse H3 with a tunnel-class entry.
        for i, span in enumerate(civil):
            cls = span.get("class")
            if cls not in ALLOWED_CIVIL_CLASSES:
                report.errors.append(
                    f"H4: [[civil]] #{i}.class={cls!r} — only "
                    f"{sorted(ALLOWED_CIVIL_CLASSES)} allowed "
                    "(no tunnels per RFC 0011)"
                )
        # H3: contiguous, sorted, cover [0, max).
        sorted_spans = sorted(civil, key=lambda s: s.get("from_station_m", 0.0))
        expected_from = 0.0
        for i, span in enumerate(sorted_spans):
            f = span.get("from_station_m")
            t = span.get("to_station_m")
            if f is None or t is None:
                report.errors.append(
                    f"H3: [[civil]] #{i} missing from_station_m / to_station_m"
                )
                break
            if f != expected_from:
                report.errors.append(
                    f"H3: [[civil]] gap/overlap — expected from_station_m="
                    f"{expected_from:.3f}, got {f:.3f} at span #{i}"
                )
                break
            if t <= f:
                report.errors.append(
                    f"H3: [[civil]] #{i} has to_station_m={t:.3f} "
                    f"≤ from_station_m={f:.3f}"
                )
                break
            expected_from = t
        alignment_end = max(
            (point.get("station_m", 0.0) for point in horizontal),
            default=0.0,
        )
        if abs(expected_from - alignment_end) > 1e-6:
            report.errors.append(
                f"H3: [[civil]] coverage ends at {expected_from:.3f}, "
                f"horizontal alignment ends at {alignment_end:.3f}"
            )

    # -- H5: every station id resolves in design.toml -----------------
    stations = doc.get("station", [])
    if known_line_ids is not None and meta.get("line_id") not in known_line_ids:
        report.errors.append(
            f"H5: meta.line_id={meta.get('line_id')!r} not found in design.toml"
        )
    if known_station_ids is None:
        if stations:
            report.warnings.append(
                "H5 skipped: no design.toml station ids provided to the "
                "validator (run with --design-toml to enable)"
            )
    else:
        for i, st in enumerate(stations):
            sid = st.get("id")
            if sid not in known_station_ids:
                report.errors.append(
                    f"H5: [[station]] #{i}.id={sid!r} not found in design.toml"
                )

    # -- H6: every curve radius ≥ preset minimum ----------------------
    for i, h in enumerate(horizontal):
        r = h.get("curve_radius_m", 0.0)
        if r > 0.0 and r < preset.min_curve_radius_m:
            report.errors.append(
                f"H6: [[horizontal]] #{i}.curve_radius_m={r:.1f} < "
                f"preset minimum {preset.min_curve_radius_m:.0f}"
            )
        # Soft gate S2: radius ≤ 2× preset minimum flags a speed restriction.
        elif r > 0.0 and r <= 2 * preset.min_curve_radius_m:
            report.warnings.append(
                f"S2: [[horizontal]] #{i}.curve_radius_m={r:.0f} within 2× of "
                f"preset minimum {preset.min_curve_radius_m:.0f} — candidate for "
                "speed restriction per RFC 0013 S4"
            )

    # -- H7: every grade ≤ preset maximum -----------------------------
    vertical = doc.get("vertical", [])
    for i in range(len(vertical) - 1):
        a = vertical[i]
        b = vertical[i + 1]
        dz = b.get("elevation_m", 0.0) - a.get("elevation_m", 0.0)
        dx = b.get("station_m", 0.0) - a.get("station_m", 0.0)
        if dx <= 0:
            continue
        grade_per_mille = abs(dz) / dx * 1000.0
        if grade_per_mille > preset.max_gradient_per_mille:
            report.errors.append(
                f"H7: grade between [[vertical]] #{i} and #{i+1} is "
                f"{grade_per_mille:.2f} ‰ > preset maximum "
                f"{preset.max_gradient_per_mille:.1f} ‰"
            )
        elif grade_per_mille > 0.8 * preset.max_gradient_per_mille:
            report.warnings.append(
                f"S3: grade between [[vertical]] #{i} and #{i+1} is "
                f"{grade_per_mille:.2f} ‰ — within 80 % of preset maximum "
                f"{preset.max_gradient_per_mille:.1f} ‰, flag for review"
            )

    # -- H8: every cant ≤ preset maximum ------------------------------
    for i, c in enumerate(doc.get("cant", [])):
        max_cant = c.get("max_cant_mm", 0.0)
        if max_cant > preset.max_cant_mm:
            report.errors.append(
                f"H8: [[cant]] #{i}.max_cant_mm={max_cant:.0f} > preset "
                f"maximum {preset.max_cant_mm:.0f}"
            )

    # -- S1: elevated share > 30 % (soft) -----------------------------
    total_length = sum(
        span.get("to_station_m", 0.0) - span.get("from_station_m", 0.0)
        for span in civil
    )
    if total_length > 0:
        elevated_length = sum(
            span.get("to_station_m", 0.0) - span.get("from_station_m", 0.0)
            for span in civil
            if span.get("class") == "elevated"
        )
        elevated_share = elevated_length / total_length
        if elevated_share > 0.30:
            report.warnings.append(
                f"S1: elevated share = {elevated_share * 100:.1f} % > 30 % "
                "— review per RFC 0011 §8 cost-soft-gate"
            )

    return report


def validate_file(
    path: Path,
    known_station_ids: set[str] | None = None,
    known_line_ids: set[str] | None = None,
) -> ValidationReport:
    with path.open("rb") as f:
        doc = tomllib.load(f)
    return validate(
        doc,
        known_station_ids=known_station_ids,
        known_line_ids=known_line_ids,
    )


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="osr-aln-validate",
        description=(
            "Validate an OSR-ALN TOML alignment against the RFC 0009 §1 "
            "preset table and the format-spec hard/soft gates."
        ),
    )
    ap.add_argument("aln", type=Path, help="Path to the .aln.toml file.")
    ap.add_argument(
        "--design-toml",
        type=Path,
        help=(
            "Optional design.toml for H5 station-id cross-check. If "
            "omitted the validator skips H5 with a warning."
        ),
    )
    args = ap.parse_args(list(argv) if argv is not None else None)

    known_ids: set[str] | None = None
    known_line_ids: set[str] | None = None
    if args.design_toml is not None:
        with args.design_toml.open("rb") as f:
            design = tomllib.load(f)
        known_ids = {
            s.get("id") for s in design.get("stations", []) if s.get("id")
        }
        known_line_ids = {
            line.get("name") for line in design.get("lines", []) if line.get("name")
        }

    report = validate_file(
        args.aln,
        known_station_ids=known_ids,
        known_line_ids=known_line_ids,
    )
    sys.stdout.write(report.format_text() + "\n")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())

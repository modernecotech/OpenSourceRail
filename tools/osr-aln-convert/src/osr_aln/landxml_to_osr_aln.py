"""LandXML → OSR-ALN converter.

Reads a LandXML 1.2 (or subset-compatible) alignment export from
Autodesk Civil 3D, Bentley OpenRail, Trimble Business Center, or
QGIS + rail-path plugins, and emits an OSR-ALN TOML document per
`docs/civil/osr-aln-format.md`.

Design notes:

- **Stdlib only.** XML parsing is ElementTree; TOML emission is a
  hand-rolled serialiser (a reviewer can read every byte). No
  third-party deps.
- **Deterministic output.** The same LandXML input produces
  byte-identical TOML output — the golden test in
  `tests/test_round_trip.py` asserts this.
- **Conservative.** Fields the LandXML does not carry (civil
  class, cant, station ids) are emitted as commented
  placeholders for the deployment engineer to fill in, not
  silently omitted.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

LANDXML_NS = "{http://www.landxml.org/schema/LandXML-1.2}"


@dataclass
class HorizontalPoint:
    station_m: float
    easting_m: float
    northing_m: float
    bearing_in_deg: float
    bearing_out_deg: float
    curve_radius_m: float
    transition_length_m: float


@dataclass
class VerticalPoint:
    station_m: float
    elevation_m: float
    vc_radius_m: float


@dataclass
class StationRef:
    """Placeholder station row — LandXML names go here; the
    deployment engineer maps to a `station_id` from `design.toml`."""

    placeholder_id: str
    station_m: float
    platform_length_m: float


DEFAULT_PLATFORM_LENGTH_M: dict[str, float] = {
    "urban-shuttle-1car": 31.0,
    "tram-2car": 49.0,
    "light-metro-3car": 61.0,
    "metro-4car": 85.0,
    "metro-6car": 121.0,
}


@dataclass
class Alignment:
    name: str
    length_m: float
    horizontal: list[HorizontalPoint] = field(default_factory=list)
    vertical: list[VerticalPoint] = field(default_factory=list)
    stations: list[StationRef] = field(default_factory=list)


# ---------------------------------------------------------------------------
# LandXML parsing
# ---------------------------------------------------------------------------


def _tag(name: str) -> str:
    return f"{LANDXML_NS}{name}"


def _parse_alignment(el: ET.Element) -> Alignment:
    """Parse one <Alignment> element into our internal representation."""

    name = el.get("name", "alignment")
    length_m = float(el.get("length", "0"))
    aln = Alignment(name=name, length_m=length_m)

    # -- Horizontal geometry -------------------------------------------
    coord_geom = el.find(_tag("CoordGeom"))
    if coord_geom is not None:
        for child in coord_geom:
            kind = child.tag.replace(LANDXML_NS, "")
            if kind == "Line":
                _parse_line(child, aln)
            elif kind == "Curve":
                _parse_curve(child, aln)
            elif kind == "Spiral":
                _parse_spiral(child, aln)

    # -- Vertical profile ---------------------------------------------
    profile = el.find(_tag("Profile"))
    if profile is not None:
        prof_align = profile.find(_tag("ProfAlign"))
        if prof_align is not None:
            for child in prof_align:
                kind = child.tag.replace(LANDXML_NS, "")
                if kind in ("PVI", "ProfileLine"):
                    _parse_pvi(child, aln)
                elif kind in ("CircCurve", "ParaCurve"):
                    _parse_vc(child, aln)

    # -- Stations ------------------------------------------------------
    for sta_el in el.findall(_tag("Station")):
        sta_name = sta_el.get("name") or sta_el.get("desc") or "unknown"
        station_m = float(sta_el.get("staAhead", sta_el.get("station", "0")))
        aln.stations.append(
            StationRef(
                placeholder_id=sta_name,
                station_m=station_m,
                # Filled after parsing from the selected consist family.
                platform_length_m=0.0,
            )
        )

    return aln


def _parse_line(el: ET.Element, aln: Alignment) -> None:
    """A straight segment. Start + end points and a bearing."""
    start = el.find(_tag("Start"))
    end = el.find(_tag("End"))
    if start is None or end is None or start.text is None or end.text is None:
        return
    sx, sy = _parse_coord(start.text)
    ex, ey = _parse_coord(end.text)
    station_start = float(el.get("staStart", "0"))
    length = float(el.get("length", "0"))
    bearing = _bearing_deg(sx, sy, ex, ey)
    aln.horizontal.append(
        HorizontalPoint(
            station_m=station_start,
            easting_m=sx,
            northing_m=sy,
            bearing_in_deg=bearing,
            bearing_out_deg=bearing,
            curve_radius_m=0.0,
            transition_length_m=0.0,
        )
    )
    # End-of-line anchor (tangent).
    aln.horizontal.append(
        HorizontalPoint(
            station_m=station_start + length,
            easting_m=ex,
            northing_m=ey,
            bearing_in_deg=bearing,
            bearing_out_deg=bearing,
            curve_radius_m=0.0,
            transition_length_m=0.0,
        )
    )


def _parse_curve(el: ET.Element, aln: Alignment) -> None:
    """A circular curve. Carries radius + start/end bearing."""
    start = el.find(_tag("Start"))
    end = el.find(_tag("End"))
    if start is None or end is None or start.text is None or end.text is None:
        return
    sx, sy = _parse_coord(start.text)
    ex, ey = _parse_coord(end.text)
    station_start = float(el.get("staStart", "0"))
    radius = float(el.get("radius", "0"))
    direction = el.get("rot", "cw")  # "cw" or "ccw"
    chord = math.hypot(ex - sx, ey - sy)
    chord_bearing = _bearing_deg(sx, sy, ex, ey)
    # Central angle (radians) = 2 * asin(chord / (2 * radius)).
    if radius > 0 and chord <= 2 * radius:
        half = math.degrees(math.asin(chord / (2 * radius)))
    else:
        half = 0.0
    sign = -1.0 if direction == "cw" else 1.0
    bearing_in = (chord_bearing - sign * half) % 360.0
    bearing_out = (chord_bearing + sign * half) % 360.0
    aln.horizontal.append(
        HorizontalPoint(
            station_m=station_start,
            easting_m=sx,
            northing_m=sy,
            bearing_in_deg=bearing_in,
            bearing_out_deg=bearing_out,
            curve_radius_m=radius,
            transition_length_m=0.0,
        )
    )


def _parse_spiral(el: ET.Element, aln: Alignment) -> None:
    """A transition spiral — clothoid. Carries transition length."""
    start = el.find(_tag("Start"))
    if start is None or start.text is None:
        return
    sx, sy = _parse_coord(start.text)
    station_start = float(el.get("staStart", "0"))
    length = float(el.get("length", "0"))
    radius_end = float(el.get("radiusEnd", "0"))
    if radius_end <= 0:
        # "Infinite" radius sentinel in some LandXML exports.
        radius_end = 0.0
    bearing = 0.0
    aln.horizontal.append(
        HorizontalPoint(
            station_m=station_start,
            easting_m=sx,
            northing_m=sy,
            bearing_in_deg=bearing,
            bearing_out_deg=bearing,
            curve_radius_m=radius_end,
            transition_length_m=length,
        )
    )


def _parse_pvi(el: ET.Element, aln: Alignment) -> None:
    """A Point of Vertical Intersection — a (station, elevation) pair."""
    txt = el.text
    if txt is None:
        return
    parts = txt.strip().split()
    if len(parts) < 2:
        return
    station_m = float(parts[0])
    elevation_m = float(parts[1])
    aln.vertical.append(
        VerticalPoint(
            station_m=station_m,
            elevation_m=elevation_m,
            vc_radius_m=0.0,
        )
    )


def _parse_vc(el: ET.Element, aln: Alignment) -> None:
    """A vertical curve at a grade-change PVI. Carries a radius."""
    radius = float(el.get("radius", "0"))
    station = float(el.get("staStart", "0"))
    # Attach the radius to the closest existing vertical point; if
    # none exists yet, emit a fresh record.
    if aln.vertical and abs(aln.vertical[-1].station_m - station) < 0.5:
        aln.vertical[-1].vc_radius_m = radius
        return
    # Otherwise record a placeholder; elevation filled later from a
    # subsequent PVI.
    aln.vertical.append(
        VerticalPoint(
            station_m=station,
            elevation_m=aln.vertical[-1].elevation_m if aln.vertical else 0.0,
            vc_radius_m=radius,
        )
    )


def _parse_coord(text: str) -> tuple[float, float]:
    """LandXML coordinate: 'northing easting [elevation]' per the
    namespace convention. We return (easting, northing)."""
    parts = text.strip().split()
    if len(parts) < 2:
        return (0.0, 0.0)
    northing = float(parts[0])
    easting = float(parts[1])
    return (easting, northing)


def _bearing_deg(x1: float, y1: float, x2: float, y2: float) -> float:
    """Compass bearing (0° = north, 90° = east) from (x1, y1) to
    (x2, y2)."""
    dx = x2 - x1
    dy = y2 - y1
    theta = math.degrees(math.atan2(dx, dy))  # compass convention
    return theta % 360.0


# ---------------------------------------------------------------------------
# OSR-ALN TOML emission
# ---------------------------------------------------------------------------


@dataclass
class Meta:
    line_id: str
    preset: str
    consist: str
    crs: str
    surveyor: str
    design_date: str
    is_ring: bool = False
    schema_version: str = "1.0"
    units: str = "metric"


def emit_toml(aln: Alignment, meta: Meta) -> str:
    """Serialise an Alignment + Meta to OSR-ALN TOML."""
    out: list[str] = []
    out.append("# OSR-ALN v1.0 — generated by landxml-to-osr-aln.")
    out.append("# Source: LandXML alignment export.")
    out.append(f"# Alignment name: {aln.name}")
    out.append(f"# Total length: {aln.length_m:.2f} m")
    out.append("")
    out.append("[meta]")
    out.append(f'schema_version = "{meta.schema_version}"')
    out.append(f'line_id        = "{meta.line_id}"')
    out.append(f'design_date    = "{meta.design_date}"')
    out.append(f'surveyor       = "{meta.surveyor}"')
    out.append(f'preset         = "{meta.preset}"')
    out.append(f'consist        = "{meta.consist}"')
    out.append(f'crs            = "{meta.crs}"')
    out.append(f'units          = "{meta.units}"')
    out.append(f"is_ring        = {str(meta.is_ring).lower()}")
    out.append("")
    out.append("# ----------------------------------------------------------")
    out.append("# Horizontal alignment — sourced from LandXML <CoordGeom>.")
    out.append("# ----------------------------------------------------------")
    for h in aln.horizontal:
        out.append("")
        out.append("[[horizontal]]")
        out.append(f"station_m           = {h.station_m:.3f}")
        out.append(f"easting_m           = {h.easting_m:.3f}")
        out.append(f"northing_m          = {h.northing_m:.3f}")
        out.append(f"bearing_in_deg      = {h.bearing_in_deg:.3f}")
        out.append(f"bearing_out_deg     = {h.bearing_out_deg:.3f}")
        out.append(f"curve_radius_m      = {h.curve_radius_m:.3f}")
        out.append(f"transition_length_m = {h.transition_length_m:.3f}")
    out.append("")
    out.append("# ----------------------------------------------------------")
    out.append("# Vertical alignment — sourced from LandXML <ProfAlign>.")
    out.append("# ----------------------------------------------------------")
    for v in aln.vertical:
        out.append("")
        out.append("[[vertical]]")
        out.append(f"station_m   = {v.station_m:.3f}")
        out.append(f"elevation_m = {v.elevation_m:.3f}")
        out.append(f"vc_radius_m = {v.vc_radius_m:.3f}")
    out.append("")
    out.append("# ----------------------------------------------------------")
    out.append("# Civil class — LandXML does not carry this. The converter")
    out.append("# emits an at-grade placeholder covering the full length;")
    out.append("# the deployment engineer splits per RFC 0011 classes.")
    out.append("# ----------------------------------------------------------")
    out.append("")
    out.append("[[civil]]")
    out.append("from_station_m = 0.0")
    out.append(f"to_station_m   = {aln.length_m:.3f}")
    out.append('class          = "at-grade"   # TODO: split per RFC 0011')
    out.append("")
    out.append("# ----------------------------------------------------------")
    out.append("# Stations — LandXML names kept as placeholder_id; the")
    out.append("# deployment engineer maps each to the id in design.toml.")
    out.append("# ----------------------------------------------------------")
    for s in aln.stations:
        out.append("")
        out.append("[[station]]")
        out.append(f'id                = "{s.placeholder_id}"   # TODO: match design.toml')
        out.append(f"station_m         = {s.station_m:.3f}")
        out.append(f"platform_length_m = {s.platform_length_m:.3f}")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def convert(
    xml_path: Path,
    meta: Meta,
    platform_length_default_m: float | None = None,
) -> str:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    alignments_el = root.find(_tag("Alignments"))
    if alignments_el is None:
        raise SystemExit(f"no <Alignments> element found in {xml_path}")

    # Pick the first alignment. A LandXML file may carry many; for v1
    # the CLI caller converts one at a time (per line).
    aln_el = alignments_el.find(_tag("Alignment"))
    if aln_el is None:
        raise SystemExit(f"no <Alignment> element found in {xml_path}")

    aln = _parse_alignment(aln_el)
    platform_length_m = (
        platform_length_default_m
        if platform_length_default_m is not None
        else DEFAULT_PLATFORM_LENGTH_M.get(meta.consist, 61.0)
    )
    for station in aln.stations:
        station.platform_length_m = platform_length_m
    return emit_toml(aln, meta)


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="landxml-to-osr-aln",
        description="Convert a LandXML 1.2 alignment to OSR-ALN TOML (RFC 0009 v3).",
    )
    ap.add_argument("--input", required=True, type=Path, help="Input LandXML file.")
    ap.add_argument(
        "--output",
        type=Path,
        help="Output .aln.toml file; omit to print to stdout.",
    )
    ap.add_argument("--line-id", required=True, help="Line id, e.g. samawah-line1.")
    ap.add_argument("--preset", required=True, help="RFC 0009 §1 preset key.")
    ap.add_argument("--consist", required=True, help="RFC 0008 §1 consist family.")
    ap.add_argument("--crs", required=True, help="EPSG CRS, e.g. EPSG:32638.")
    ap.add_argument(
        "--surveyor",
        default="unknown",
        help="Name of the civil firm producing the alignment.",
    )
    ap.add_argument(
        "--design-date",
        default="1970-01-01",
        help="ISO 8601 date the alignment was designed.",
    )
    ap.add_argument(
        "--is-ring",
        action="store_true",
        help="Set meta.is_ring = true (for ring lines).",
    )
    ap.add_argument(
        "--platform-length-default",
        type=float,
        default=None,
        help=(
            "Placeholder station platform length in metres; default derives "
            "from --consist using RFC 0008/0010."
        ),
    )
    args = ap.parse_args(list(argv) if argv is not None else None)

    meta = Meta(
        line_id=args.line_id,
        preset=args.preset,
        consist=args.consist,
        crs=args.crs,
        surveyor=args.surveyor,
        design_date=args.design_date,
        is_ring=args.is_ring,
    )

    text = convert(args.input, meta, platform_length_default_m=args.platform_length_default)

    if args.output:
        args.output.write_text(text)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())

# Samawah civil alignment — v1 deliverable of RFC 0009

Worked civil-alignment envelope for the Samawah reference
deployment's Line 1 (Nahrain) and Line 2 (Halqa), against the
[RFC 0009](../../rfcs/0009-track-design-standard.md)
`standard-urban` preset.

## What this is

A **per-segment alignment table** for every track segment
between adjacent stations, computed from the station
coordinates in [`designs/west-asia/Iraq/Samawah/design.toml`](../../../designs/west-asia/Iraq/Samawah/design.toml),
validated against the `standard-urban` preset's limits (min
curve radius 90 m, max grade 50 ‰, max cant 150 mm, nominal
speed 22 m/s).

## What this is NOT

- A surveyed alignment. Station lat/lons are planning-grade
  RFC 0003 numbers. A real deployment substitutes GNSS-surveyed
  coordinates.
- A final civil-engineering design. This table is the envelope a
  civil engineering firm bids against.
- A structural design for the viaducts / bridges. Those are
  RFC 0011 work, summarised per-segment in
  [`civil-class-summary.md`](civil-class-summary.md).

## Contents

| File | Scope |
|---|---|
| [`line1-segments.md`](line1-segments.md) | Line 1 (12 stations, 11 segments, radial) per-segment table |
| [`line2-segments.md`](line2-segments.md) | Line 2 (10 stations, 10 segments + ring wrap) per-segment table |
| [`civil-class-summary.md`](civil-class-summary.md) | At-grade / elevated / bridge breakdown per-line and consolidated |
| [`compliance-report.md`](compliance-report.md) | Per-segment pass/fail against the `standard-urban` preset's §§5–6 limits |
| [`../../../designs/west-asia/Iraq/Samawah/samawah-line1.aln.toml`](../../../designs/west-asia/Iraq/Samawah/samawah-line1.aln.toml) | **Machine-readable OSR-ALN v1.0 alignment for Line 1** (13 km, 12 stations, passes `osr-aln-validate`) |
| [`../../../designs/west-asia/Iraq/Samawah/samawah-line2.aln.toml`](../../../designs/west-asia/Iraq/Samawah/samawah-line2.aln.toml) | **Machine-readable OSR-ALN v1.0 alignment for Line 2** (16 km ring, 10 stations, 4 cant sections, passes `osr-aln-validate`) |

## How to execute

1. Civil engineering firm reads [`line1-segments.md`](line1-segments.md)
   + [`line2-segments.md`](line2-segments.md). Each row is a
   buildable segment.
2. Firm runs their in-house alignment tool (Civil 3D, Bentley
   OpenRail, Trimble etc.) against each row's start/end
   coordinates + length target + civil class.
3. Firm produces the detailed alignment (horizontal + vertical
   geometry, cross-sections, stationing) that matches the v1
   envelope.
4. Per-segment structural design follows RFC 0011 §§4–6 for
   at-grade / elevated / bridge respectively.

## Licensing

CC-BY-SA 4.0 for this v1 specification. Detailed alignment
drawings under CERN-OHL-S v2 once v2 is produced.

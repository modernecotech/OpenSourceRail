# LM3-FAS-185 — reversible front-lamp cassette and aiming interface

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Owner: vehicle integration + lamp supplier
- Factory package: `LM3-FRP-040`
- Source: `docs/rolling-stock/light-metro-3car/end-cowl.md`, `docs/rolling-stock/light-metro-3car/dedicated-parts-and-moulds.md`
- Coordinate basis: vehicle X longitudinal from car centre, Y lateral from vehicle centreline, Z vertical from top of rail; drawing-specific fabrication datums must be released and related back to this basis

## Controlled product scope

| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |
|---|---|---:|---:|---|
| `LM3-CWL-P014` — CWL-FRP-04 lower apron and anti-climber cover fiberglass cast | `MAKE` / `buildable-after-supplier-freeze` | 2 ea | 1000 × 2650 × 760 | lower apron and anti-climber cover cast |
| `LM3-CWL-P015` — CWL-FRP-05 lamp, washer, and service-hatch fiberglass cast set | `MAKE` / `buildable-after-supplier-freeze` | 4 hatch | 650 × 520 × 420 | lamp/washer/service-hatch cast set |
| `LM3-END-P050` — sealed headlight, tail/marker light, threshold-warning, and end-lamp harness kit | `SOURCE` / `buildable-after-supplier-freeze` | 2 end kit | 1600 × 900 × 280 | head/tail/marker/threshold lamps and harness |
| `LM3-FAS-P020` — reversible front-lamp cassette tray, aiming adjusters, and retained service bracket | `MAKE` / `buildable-after-supplier-freeze` | 2 end set | 1850 × 720 × 420 | reversible lamp cassette tray and aiming adjusters |

## Required views

- A/B cassette installation views
- optical-axis and adjuster datum diagram
- harness, earth, drip-loop and service-clearance details

## Unresolved inputs

- selected lamp photometric, thermal, EMC, IP and connector data
- A/B end configuration and cowl service-hatch envelope
- released lamp reaction, aiming and retention requirements

## Required outputs

- common reversible tray, adjuster and retained service-bracket drawing
- lamp optical-axis datum and adjustment-limit schedule
- harness, earth, drip-loop and connector-access route
- A/B interchange and lamp-cassette configuration record

## Required verification

- tray and optical-axis datum gauge
- aim range, lock and vibration-retention test
- thermal/IP/functional evidence review
- service-hatch and cassette removal demonstration

## Mandatory drawing controls

- drawing number, title, sheet, scale, units, projection, revision and issue status
- named design, checking, manufacturing, quality and approval responsibilities
- material/grade, finish/protection, mass and applicable process specification
- functional datums, geometric tolerances, fits, clearances and inspection characteristics
- part/assembly IDs, quantities, configuration applicability and revision-compatible BOM
- joining method, weld/adhesive/fastener authority and special-process hold points
- supplier-controlled dimensions and keep-outs identified rather than assumed
- tooling/gauge references, inspection method, acceptance criteria and evidence route

## Tooling and issue record

Tooling: `LM3-TOOL-COWL-MOULD`, `LM3-TOOL-LAMP-AIM`.

The machine-readable JSON beside this page contains the deliberately blank
native/published file references, checksum, sheet/scale and approval fields.

Boundary: This seed aggregates controlled scope and design-reference envelopes. It is not a dimensioned production drawing, released tool surface, NC definition, signed calculation or authority to manufacture.

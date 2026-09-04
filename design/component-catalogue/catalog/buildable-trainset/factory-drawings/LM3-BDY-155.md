# LM3-BDY-155 — identical A/B-end GFRP cowl cast kit

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Owner: composites engineering + vehicle integration
- Factory package: `LM3-FRP-030`, `LM3-FRP-040`
- Source: `docs/rolling-stock/light-metro-3car/end-cowl.md`, `docs/rolling-stock/light-metro-3car/dedicated-parts-and-moulds.md`
- Coordinate basis: vehicle X longitudinal from car centre, Y lateral from vehicle centreline, Z vertical from top of rail; drawing-specific fabrication datums must be released and related back to this basis

## Controlled product scope

| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |
|---|---|---:|---:|---|
| `LM3-CWL-P014` — CWL-FRP-04 lower apron and anti-climber cover fiberglass cast | `MAKE` / `buildable-after-supplier-freeze` | 2 ea | 1000 × 2650 × 760 | lower apron and anti-climber cover cast |
| `LM3-CWL-P015` — CWL-FRP-05 lamp, washer, and service-hatch fiberglass cast set | `MAKE` / `buildable-after-supplier-freeze` | 4 hatch | 650 × 520 × 420 | lamp/washer/service-hatch cast set |
| `LM3-CWL-P016` — CWL-FRP-06 backing-ring flange fiberglass cast set | `MAKE` / `buildable-after-supplier-freeze` | 8 flange section | 720 × 120 × 720 | backing-ring flange cast |
| `LM3-END-P050` — sealed headlight, tail/marker light, threshold-warning, and end-lamp harness kit | `SOURCE` / `buildable-after-supplier-freeze` | 2 end kit | 1600 × 900 × 280 | head/tail/marker/threshold lamps and harness |
| `LM3-EXT-P030` — single panoramic heated end-glass assembly | `BID` / `buildable-after-supplier-freeze` | 2 ea | 2300 × 110 × 1450 | heated panoramic end glazing |
| `LM3-FAS-P010` — panoramic front-glass carrier ring, setting-block pockets, and secondary-retention frame | `MAKE` / `buildable-after-supplier-freeze` | 2 end set | 2300 × 260 × 1780 | panoramic glass carrier, setting blocks and secondary retention |
| `LM3-FAS-P020` — reversible front-lamp cassette tray, aiming adjusters, and retained service bracket | `MAKE` / `buildable-after-supplier-freeze` | 2 end set | 1850 × 720 × 420 | reversible lamp cassette tray and aiming adjusters |
| `LM3-FAS-P030` — front glazing/lamp EPDM seal, drain rail, washer sleeve, and edge-closeout kit | `SOURCE` / `buildable-after-supplier-freeze` | 2 end kit | 2500 × 420 × 1950 | glazing/lamp seals, drains, washer sleeves and closeouts |

## Required views

- front, side and plan exterior surfaces
- six-piece split, flange and trim scheme
- glass, lamp, sensor, drain and service-access sections

## Unresolved inputs

- supplier glass construction, edge, mass, heater and retention loads
- accepted glazing adhesive/gasket and EPDM compatibility data
- released steel backing-ring and cowl flange datums
- selected lamp photometric, thermal, EMC, IP and connector data
- A/B end configuration and cowl service-hatch envelope
- released lamp reaction, aiming and retention requirements

## Required outputs

- carrier segments, corner joints, setting blocks and secondary-retention drawing
- glass-edge clearance and seal-compression characteristic map
- drain rail, washer sleeve, earth and heater-service route
- protected removal path and lifting-tool access drawing
- common reversible tray, adjuster and retained service-bracket drawing
- lamp optical-axis datum and adjustment-limit schedule
- harness, earth, drip-loop and connector-access route
- A/B interchange and lamp-cassette configuration record

## Required verification

- carrier and backing-ring datum survey
- retention calculation and representative proof
- compression/drain map and controlled spray test
- heated-pane service isolation and timed removal/refit trial
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

Tooling: `LM3-TOOL-COWL-MOULD`, `LM3-TOOL-GLASS-CARRIER-NEST`, `LM3-TOOL-WATER-TEST`, `LM3-TOOL-LAMP-AIM`.

The machine-readable JSON beside this page contains the deliberately blank
native/published file references, checksum, sheet/scale and approval fields.

Boundary: This seed aggregates controlled scope and design-reference envelopes. It is not a dimensioned production drawing, released tool surface, NC definition, signed calculation or authority to manufacture.

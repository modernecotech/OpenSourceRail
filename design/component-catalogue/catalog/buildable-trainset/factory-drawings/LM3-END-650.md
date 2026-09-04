# LM3-END-650 — configurable panoramic or open-mid train-end interface

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Owner: vehicle structures + train-end integration
- Factory package: `LM3-FRP-120`
- Source: `docs/rolling-stock/light-metro-3car/articulation.md`, `docs/rolling-stock/light-metro-3car/end-cowl.md`, `docs/rolling-stock/light-metro-3car/interfaces.md`
- Coordinate basis: vehicle X longitudinal from car centre, Y lateral from vehicle centreline, Z vertical from top of rail; drawing-specific fabrication datums must be released and related back to this basis

## Controlled product scope

| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |
|---|---|---:|---:|---|
| `LM3-END-P030` — cowl service hatch, sensor backing bracket, washer-tube, and heater-cable clip kit | `MAKE` / `release-candidate` | 2 end kit | 900 × 700 × 420 | service hatch, backing bracket and clipped services |
| `LM3-END-P060` — common reversible end-interface carrier ring, option bolt grid, and sealing datum kit | `MAKE` / `release-candidate` | 2 end position | 2650 × 280 × 2650 | reversible end carrier and option bolt grid |
| `LM3-END-P061` — panoramic-end option shim, cowl/glass carrier, and sensor datum closeout kit | `MAKE` / `release-candidate` | 2 option kit | 1250 × 2650 × 2650 | panoramic closeout, glass carrier and sensor datums |
| `LM3-END-P062` — mid open-connection option portal trim, bellows clamp, threshold bridge, and drain kit | `MAKE` / `release-candidate` | 0 option kit | 1300 × 2100 × 2350 | open portal, clamp, threshold and drain option |

## Required views

- common carrier ring and option bolt-grid elevation
- panoramic closeout and open-mid portal configuration sections
- seal, drain, threshold, sensor/service-hatch and option-record details

## Unresolved inputs

- released crash, articulation, anti-lift, gangway and end-equipment load cases
- frozen panoramic-end and open-mid supplier interface envelopes
- selected-end configuration, seal, drain, threshold and service-access requirements

## Required outputs

- common end ring, option bolt grid and articulation-adapter production drawings
- panoramic and open-mid shim/closeout configuration drawings
- anti-lift, service-hatch, sensor-backing, drain and threshold details
- serialized end-position option and interchangeability record

## Required verification

- independent structural, fatigue and full-motion calculation review
- end-ring/bolt-grid datum survey and A/B interchange gauge
- articulation sweep plus keeper/pin-retention inspection
- configured-end water, drain, threshold and service-removal trials

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

Tooling: `LM3-TOOL-STEEL-FIXTURE`, `LM3-TOOL-DATUM-GAUGE`, `LM3-TOOL-COWL-MOULD`, `LM3-TOOL-WATER-TEST`.

The machine-readable JSON beside this page contains the deliberately blank
native/published file references, checksum, sheet/scale and approval fields.

Boundary: This seed aggregates controlled scope and design-reference envelopes. It is not a dimensioned production drawing, released tool surface, NC definition, signed calculation or authority to manufacture.

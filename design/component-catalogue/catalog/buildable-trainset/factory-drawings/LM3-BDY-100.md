# LM3-BDY-100 — carbody primary steel and recovery load-path assembly

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Owner: vehicle structures + fabricator
- Factory package: `LM3-FRP-010`, `LM3-FRP-100`
- Source: `docs/rolling-stock/light-metro-3car/body.md`, `docs/rolling-stock/light-metro-3car/field-rerailing-concept.md`
- Coordinate basis: vehicle X longitudinal from car centre, Y lateral from vehicle centreline, Z vertical from top of rail; drawing-specific fabrication datums must be released and related back to this basis

## Controlled product scope

| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |
|---|---|---:|---:|---|
| `LM3-BDY-P010` — laser-cut side sill beam, LH/RH | `MAKE` / `release-candidate` | 6 ea | 16000 × 180 × 260 | one side-sill member with end datum faces |
| `LM3-BDY-P020` — underframe centre spine and longitudinal load-path kit | `MAKE` / `release-candidate` | 3 kit | 15800 × 2650 × 380 | centre spine and repeated cross-bearers |
| `LM3-BDY-P021` — underframe cross-bearer, door-bay outrigger, and equipment-bracket pack | `MAKE` / `release-candidate` | 3 car pack | 15200 × 2650 × 320 | stationed cross-bearers, door outriggers and equipment brackets |
| `LM3-BDY-P030` — bolster box, air-spring pad, and centre-pivot insert set | `MAKE` / `release-candidate` | 6 set | 1700 × 2650 × 420 | bolster box, spring pads and pivot land |
| `LM3-BDY-P060` — low-floor centre pan and removable service-floor support set | `MAKE` / `release-candidate` | 3 set | 15600 × 2650 × 460 | low-floor pan and raised bogie-end decks |
| `LM3-BDY-P061` — raised bogie-end deck, transition ramp, and removable hatch-frame set | `MAKE` / `release-candidate` | 3 car set | 5200 × 2650 × 460 | raised end decks, transition ramps and removable hatch frames |
| `LM3-BDY-P070` — side-wall post, door portal, waist rail, and cant rail kit | `MAKE` / `release-candidate` | 6 side | 15800 × 180 × 2850 | posts, door portals, waist and cant rails |
| `LM3-BDY-P080` — roof bow, HVAC rail, PV rail, and cable-tray bracket kit | `MAKE` / `release-candidate` | 3 kit | 15600 × 2500 × 360 | roof bows and equipment/cable rails |
| `LM3-BDY-P120` — jacking pad, lifting eye, towing lug, and recovery-label kit | `MAKE` / `release-candidate` | 3 car kit | 1600 × 900 × 280 | jacking, lifting and towing interface kit |

## Required views

- carbody plan, side and end elevations
- primary datum and support-point scheme
- welded load-path and recovery-interface details

## Unresolved inputs

- released structural load cases and material grades
- door, window, bogie, battery, coupler and roof interface reactions
- weld-class, distortion and corrosion-process requirements
- individual-car mass and centre-of-gravity envelopes
- released underframe, articulation, bogie-retention and coupler load cases
- selected depot and portable recovery equipment interfaces

## Required outputs

- member and plate drawings with datums, tolerances and material callouts
- cut, bend, machining and weld maps with heat/part trace fields
- fixture loading sequence and dimensional inspection characteristic list
- mass-properties contribution and controlled centre-of-gravity ledger rows
- J1--J4 pad, lifting eye, tow/rerailing lug and keyed-adapter drawings
- permitted support combinations, reactions, stop conditions and labels
- vehicle isolation, brake release, bogie retention and recovery diagrams
- proof-load, inspection, NDT, maintenance and damage-rejection schedule

## Required verification

- independent calculation review
- fixture and tack survey
- post-weld datum/straightness survey
- weld/NDT and corrosion hold-point records
- structural and weld/NDT calculation review
- four-point datum/interchange gauge
- representative proof and asymmetric/loss-of-pressure trials
- timed depot lift and field rerailing demonstration by trained crews

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

Tooling: `LM3-TOOL-STEEL-FIXTURE`, `LM3-TOOL-DATUM-GAUGE`, `LM3-TOOL-LIFT-COLUMNS`.

The machine-readable JSON beside this page contains the deliberately blank
native/published file references, checksum, sheet/scale and approval fields.

Boundary: This seed aggregates controlled scope and design-reference envelopes. It is not a dimensioned production drawing, released tool surface, NC definition, signed calculation or authority to manufacture.

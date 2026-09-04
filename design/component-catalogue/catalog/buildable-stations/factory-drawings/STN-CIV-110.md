# STN-CIV-110 — site set-out, levelling, drainage and closure coordination

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Scope type: `deployment-interface-definition`
- Owner: deployment civil engineer
- Release package: `STN-FRP-010`
- Source: `docs/stations/standard-archetype/envelope.md`, `docs/stations/standard-archetype/services.md`
- Coordinate basis: catalogue station X is along track from platform centre, Y is lateral from track/station centreline and Z is vertical in the local station frame; deployment drawings must transform this frame to accepted survey control while preserving the 350 mm platform-to-top-of-rail interface

## Controlled product scope

| Product | Route / maturity | Release path | Variants | Reference default |
|---|---|---|---:|---|
| `STN-CIV-P020` — platform sub-base, levelling pad, grout, and closure-pour kit | `MAKE` / `release-candidate` | `reusable-definition` | 7 | not required |
| `STN-CIV-P030` — platform and track drainage channel, pipe, catch-pit, and outlet kit | `MAKE` / `release-candidate` | `reusable-definition` | 7 | not required |
| `STN-CIV-P040` — 3 m at-grade guideway-channel edge beam, coping/tactile carrier, and drained service trough | `MAKE` / `release-candidate` | `reusable-definition` | 6 | not required |

## Required views

- survey-control and set-out plan
- longitudinal/crossfall and drainage profiles
- levelling, grout, closure-pour and outfall details

## Unresolved inputs

- accepted survey control, track alignment and platform stepping/gap envelope
- site geotechnical, drainage/outfall and foundation design
- released concrete, reinforcement, tactile and joint/seal systems

## Required outputs

- repeatable precast mould, reinforcement, insert and lifting drawings
- site set-out, levelling, drainage and closure-pour schedule
- platform-edge datum, tolerance and interface-control plan

## Required verification

- mould and first-article dimensional survey
- concrete, reinforcement and lifting-insert records
- installed track/platform gap-step and drainage survey

## Mandatory drawing controls

- drawing number, title, sheet, scale, units, projection, revision and issue status
- named catalogue, deployment, supplier, checking, quality and approval responsibilities
- survey coordinate reference system, horizontal/vertical datums and controlled transformation
- material/grade, protection, durability life and applicable process specification
- functional datums, tolerances, fits, clearances and measurable inspection characteristics
- product/assembly IDs, configuration applicability, quantities and revision-compatible BOM
- supplier-controlled dimensions, reactions, access zones and utility interfaces identified rather than assumed
- temporary works, lifting/erection sequence, hold points and safe access where applicable
- tool/gauge references, inspection method, acceptance criteria and evidence route
- reusable definition and deployment-specific construction release shown as separate statuses

## Tooling and issue record

Tools/gauges: `STN-TOOL-PRECAST-MOULD`, `STN-TOOL-EDGE-GAUGE`, `STN-TOOL-LIFTING-GAUGE`.

The JSON beside this page retains deliberately blank native/published file,
checksum, survey/supplier, calculation and named approval fields.

Boundary: This is a drafting/checking brief built from catalogue products, reference defaults and open inputs. It is not a dimensioned fabrication or construction drawing, supplier selection, signed calculation, survey, permit or authority to manufacture, build, energise or operate.

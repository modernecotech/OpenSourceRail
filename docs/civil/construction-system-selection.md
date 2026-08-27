# Civil Construction-System Selection

Status: deterministic planning rules; every selected product remains subject
to project structural, geotechnical, rail-system and construction release.

The machine-readable source is
[`lib/templates/civil-construction-systems.toml`](../../lib/templates/civil-construction-systems.toml).
It changes the method used to construct the existing civil product family; it
does not lower the canonical 3 M USD/km at-grade, 12 M USD/km elevated or
18 M USD/km bridge planning floors.

| Zone condition | Default selected method | Deterministic exception |
|---|---|---|
| Long open at-grade run | Continuous slipformed twin-track slab | ST6 single-track panels in tagged utility, street, flood, transition or short-possession zones |
| Normal 20/25 m viaduct | Four-span semi-continuous Pi-beam unit | Five spans may be assessed inside the 80–125 m movement range; special products remain separate |
| Viaduct approach up to 4.5 m | Reinforced-soil retained embankment | Reject for flood/scour, severe settlement, insufficient ROW or failed cyclic deformation check |
| Soft ground beneath formation/embankment | Zone-selected rigid inclusions, deep mixing, stone columns, lightweight fill or stabilisation | Full project-specific solution where catalogue applicability fails |
| Ordinary pier with clear piling access | Driven pile bent without a buried pile cap | Integral bored shaft in vibration-restricted ground; pile group for high lateral/seismic/scour cases |
| Major road conflict | Compare road over/under/relocation and short rail bridge with long rail elevation | Discard infeasible options; score direct cost plus construction penalties |

## Semi-continuous reference kilometre

`semi_continuous_unit_plan(1000)` resolves 40 Pi25 spans into ten four-span
units. Thirty internal joints become reinforced link slabs or diaphragms; ten
deck gaps remain. One bearing line at an internal unit support gives four
bearings; a unit boundary keeps two independent lines and eight bearings. The
complete reference kilometre therefore has 200 bearings. No kilometre-long
continuity is implied.

Release requires continuous-welded-rail interaction, braking/traction,
temperature/shrinkage, seismic displacement, foundation-flexibility and
connection fatigue/waterproofing analyses. Fully integral internal piers are a
future option, not the default.

## Geotechnical-zone record

Every zone chooses either a foundation product for a support or a ground-
improvement product for ground-supported construction. Quantities are stored
as actual pile/shaft length and count, treated area/volume and column geometry,
installation time, verification result and installed cost. The model never
converts route length into a generic volume of foundation concrete.

## Manufacturing controls

The production target is a 24-hour reusable-mould cycle using self-
consolidating concrete, maturity-based release, standard welded cages,
controlled inserts and serialised component travellers. The schedule retains
the validated 48-hour planning cycle until a mix, sensor, mould and first-
article trial releases the target. Small closure pours and grouted sockets are
preferred; rare 3D-printed formwork and exotic materials are not standard
primary members.

## Cost validation

The combined method changes carry a preliminary 15–30% civil-cost reduction
target only. OSR retains the existing cost baseline until rail-specific
prototypes, the project foundation schedule, installation trials and supplier
quotations support a revision in Git. Each accepted revision should include
its changed assumptions, source evidence, quantity diff and test outputs.

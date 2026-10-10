# Complete viaduct system exploration

The workbench now investigates complete packages rather than varying one hollow
beam/pier with a fixed foundation. It extends the original
[Word action plan](../../OpenSourceRail_Civil_Exploration_Plan.docx) and preserves
the [C01–C14 acceptance audit](design-exploration.md). The root
[README](../../README.md#complete-viaduct-design-exploration) exposes the choices,
executed comparison and model limits.

## Scope and choices

The common comparison uses 300 m of double track, allowing whole 20, 25 and
30 m bays with consistent end supports. This is a research segment, separate
from the initial 100 m reference milestone and the complete Baghdad inventory.
Existing Pi20/Pi25 shapes remain controls. Ten beam families, six pier families,
nine foundation layouts and three connection schemes are registered before
search. Each carries allowed parameters/materials, ownership and uncovered
failure modes. More families are not silently treated as qualified catalogue
products.

Normal/HPC/lightweight concrete selection changes the deck's density and
stiffness. It does not automatically lighten piers or foundations. Separate
support and foundation material records govern those quantities. Targeted UHPC,
structural steel and GFRP/CFRP occupy disjoint actual material regions. FRP is
orthotropic; neither its matrix nor its shell is credited as a replacement for
required seismic reinforcement. All initial property sets are explicitly
synthetic hypotheses, with no supplier mix, laminate or measured strength adopted.

Foundation geometry includes solid circular shafts/piles, square precast piles,
annular precast piles and zero-pile spread footings. Net voids survive CAD and
IFC export. Pile diameter/length and cap dimensions are sampled with the beam
and pier. Diameter changes update cap plan size proportionally to the declared
layout; this preserves its unqualified spacing ratio rather than inventing a
site spacing acceptance. Exact capacity and cap reinforcement remain open.

The native pile model calculates three cap unit-load responses with elastic
Timoshenko piles, axial/lateral soil springs, toe springs and a rigid cap.
Reciprocity, positive energy and at least three discretisations are checked before
condensation. Horizontal–rotation coupling is retained in the system model.
Refinement continues from 16 to 32/64 elements per pile when the declared
stiffness convergence check needs more resolution; unresolved cases retain a
numerical-failure status. Both longitudinal and transverse axes are checked.
Separate longitudinal/transverse condensed responses drive the 3D model.
Shallow support springs use the declared rectangular footing and soil bed.
Installation methods receive **no automatic soil improvement credit**.
These are declared linear research soil laws, not Baghdad stratigraphy or a
substitute for calibrated nonlinear group, cyclic or liquefaction response.

## Loading and numerical confirmation

The six-car infrastructure planning allowance is divided by the retained train
length to create a **uniform static stiffness sensitivity**. Axle concentration,
train dynamics and combinations are not inferred from this average. The static
profile contains no LM3 or invented Baghdad axle array. Actual six-car axle
positions/forces remain blocked in the [qualification workflow](baghdad-qualification.md).

Reduced native screening includes gravity, uniform service and the declared
braking sensitivity, finite bearings, material-region stiffness, piers and
foundation compliance. Provisional response/lifting/nominal soil-resistance
limits are tagged research constraints. They do not establish concrete capacity,
prestress, fatigue, site foundation resistance or adopted railway limits.
Failures remain distinguishable from missing evidence and from solver failures.

The diverse shortlist receives three actual C3D20R solid meshes with common
gravity/service pressure, source-bound native displacement/stress fields and
an explicit displacement convergence criterion. The 3D shear-flexible frame
uses separate tracks, flexible hollow transverse caps, column/cap offsets,
finite bearing translations/roll and coupled foundation stiffness. Both-track,
single-track and braking sensitivities run at three meshes in both soil cases.
Vertical/horizontal force and moment equilibrium are checked independently.
Saint-Venant rectangular torsion and closed-cell Bredt torsion are explicitly
bounded formulations; open-section warping/distortion remain uncovered.

A two-layer composite diagnostic adds distributed shear-slip energy to axial
and bending behaviour. Independent no-bond and strong-connector analytical
limits verify it. Unmeasured connector stiffness sweeps show possible loss of
the perfect-bond advantage; they cannot establish connector resistance or
debonding/fatigue/fire behaviour. Existing nonlinear fibre, pile, P-delta,
friction, orthotropic and coupled-vehicle component benchmarks are rerun.
Shortlisted piers also receive a native P-delta diagnostic using the minimum
effective section and worst reduced axial/shear actions. Its independently
checked prismatic cantilever domain does not establish full flexible-base
stability, taper/joint/cyclic capacity or accepted candidate resistance.

## Construction and complete cost

Each method has actual shipping/lifting units derived from canonical regions:
full members, beam segments, empty structural shells, pier segments/shells,
caps and precast pile segments. Rebar/tendon/inserts remain declared quantity
allowances, not fabricated bar/tendon geometry or accepted rigging weights.
Completed service mass is distinct from empty transport mass. Driven piles
include production, curing, delivery, handling/splice time and installation.
Site concrete delivery is separate from material supply.

The existing `project_twin.apply_resource_cpm` engine schedules whole-hour slots
with finite rigs, beds, curing yard, transport, erection, site crews and QA.
Procurement, foundation tests, production, support readiness, infill, joints,
curing and final inspection have explicit dependencies. External gates remain
unresolved, with no assumed zero-duration acceptance. Reported working time
starts conditionally after those gates and uses conservative whole-hour
rounding; it is not an adopted Baghdad calendar or delivery commitment.

Every package has complete material-separated quantities and rows for material,
reinforcement/tendons/inserts, bearings/joints, piling plant, delivered concrete,
precast transport, crane plant/mobilisation, temporary works, labour,
bed/curing/QA/tooling, track/walkway/drainage interfaces, reinstatement and site
overhead. Synthetic annual maintenance and bearing/joint replacement scenarios
give discounted whole-life sensitivities. Actual rates/charts/availability and
maintenance intervals remain open.

Three **synthetic** price/productivity cases expose ranking reversals. They are
not Baghdad market estimates. Hypothetical crane tiers expose step changes but
are not accepted crane charts. Actual supplier-price totals remain null when
any applicable cost row is missing. The cheapest source-priced qualified design
remains unresolved. Carbon totals remain unknown without controlled EPD factors.

## Search, records and review

Random and Pareto-evolution searches use equal attempt budgets and multiple seeds.
Every registered beam family has engineering seeds and early coverage. Evolution
changes bounded dimensions, materials, pier/foundation choice and construction
method within compatible families. Cost, installed mass and working time remain
separate objectives; installed/whole-life/lifting tradeoffs remain reviewable.
The best found choices are bounded by the declared search, not a proof of global
optimality. Reduced leaders and converged-shortlist leaders are reported separately.

Candidate IDs bind geometry/material/foundation data. Package IDs also bind
assembly/construction choices; input snapshots bind loads, scenarios, code and
native binaries. Modification events retain parent packages and reasons.
Checkpoints verify all saved results, raw schedules, costs and source bytes.
Failed native/refinement attempts retain their logs. The full shortlist is packed
in immutable sub-50-MiB archive parts and restored with member hash verification.
A sealed change proposal names the existing change/release workflows while
keeping acceptance false; it never promotes itself into the catalogue.

```sh
tools/automation/osr-python tools/automation/civil-study.py system-study \
  --output build/engineering/civil-studies/baghdad-complete-systems-v2
tools/automation/osr-python tools/automation/civil-study.py system-verify \
  build/engineering/civil-studies/baghdad-complete-systems-v2
tools/automation/osr-python tools/automation/export-civil-system-review.py \
  build/engineering/civil-studies/baghdad-complete-systems-v2 --update-readme
```

`--resume` requires matching configuration, dependencies, native environment and
all checkpoint hashes. `--skip-detail` explicitly creates reduced evidence only
and cannot be exported as the retained confirmed review. Use `--seeds`,
`--evaluations-per-method` and `--shortlist` for bounded pilots. Configurations
and quote sources must be retained repository files.

The compact [retained comparison](../../engineering/civil_exploration/examples/complete-system-review.md)
and JSON have a named regression consumer. The scratch `report.html` is a
self-contained filter/sort viewer with quantities, failures and evidence gaps;
`comparison.csv`, material-section SVG and Pareto SVG support external review.

## What cannot be completed from software alone

The C01–C14 software/evidence audit is generated with every comparison.
Project/supplier load records, adopted requirements, measured mix/laminate/bond
properties, reinforcement/tendon/anchorage designs, support-zone ground/survey,
installation/equipment trials, quoted cost/productivity, physical instrumented
tests and independent authority acceptance remain actual dependencies.
V/Y support systems, site ground-improvement load transfer, haunched members
and novel recycled primary structures remain purpose-specific model/adoption
work, with explicit owners/data needs. The current search does not count them
as implemented or qualified families. Engineering acceptance of all document
items therefore remains incomplete.

## Research sources and limits

FHWA's [lightweight concrete primer](https://www.fhwa.dot.gov/bridge/concrete/hif19067_Nov2021.pdf)
supports investigating density and stiffness together; its highway bridge
guidance does not qualify a local metro mix. FHWA's
[UHPC waffle-deck work](https://www.fhwa.dot.gov/hfl/partnerships/uhpc/hif13032/chap01.cfm)
includes connection and field studies; the targeted-rib option here is a distinct
research geometry, not that tested bridge product.

MxV Rail's [hybrid-beam service observations](https://www.mxvrail.com/technology-digest/hybrid-composite-beam-spans-revenue-service-results/)
show why connection deterioration and inspection access need explicit evidence.
The straight shell/I options here do not reproduce the tested concrete-arch HCB.
FHWA's [CFA/displacement-pile guidance](https://www.fhwa.dot.gov/engineering/geotech/pubs/gec8/gec8.pdf)
identifies installation-dependent behaviour and limitations; no automatic
capacity benefit or constructability acceptance is adopted from it.
The [OpenSees 3D Timoshenko interface](https://openseespydoc.readthedocs.io/en/latest/src/ElasticTimoshenkoBeam.html)
defines the native shear-flexible formulation used; equation checks and solver
agreement provide numerical verification, not physical validation.

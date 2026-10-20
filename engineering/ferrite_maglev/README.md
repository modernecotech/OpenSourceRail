# OpenSourceRail v0.5 primary infrastructure adapter

The selected architecture is ferrite PM-biased active maglev, with onboard
windings/electronics, passive guidebeams, local manufacturing and Rust controls
on off-the-shelf SBCs. The [migration decision](../../docs/rfcs/0035-v05-primary-ferrite-maglev.md)
separates the selected architecture from engineering acceptance. **Accepted
engineering and physical releases remain zero.**

```bash
./osr                         # primary architecture and migration status
./osr build                   # build Rust examples and publish the study
./osr design run              # regenerate bounded calculations and review images
./osr design check            # independently regenerate and compare publication outputs
./osr design verify           # verify current publication source/file checksums
./osr design release-check    # exits 3 while acceptance remains open
./osr city baghdad            # separate provisional maglev planning package
./osr sim baghdad --cycles 2  # representative-train offline SOC/charging replay
cargo test -p osr-maglev-control --all-targets
cargo run -p osr-maglev-control --release --example multimodule_replay
cargo build -p osr-maglev-control --release --example coupled_bridge
tools/automation/osr-python -m engineering.ferrite_maglev.coupled --duration-s 3
```

[Open the generated report](../../docs/design-engine/ferrite-maglev/reference/index.html).
The scalar study retains 4 mass variants, 12 cost configurations, 2 additional
local-manufacture budget targets, 16 normal/hot load-duty cases, 3 additional
no-regen/90 km/h cases and 27 guidebeam geometry/span combinations. The 5% hot
uphill steady power envelope is a separate calculation. These use declared
assumptions; actual magnetic force/loss data remain open.

## Implementation and closure status

| Capability | Implemented scope | Evidence still needed |
|---|---|---|
| [Transition register](transition.py) and [explicit decisions](data/transition-plan.json) | 345 canonical identities plus 69 additional Baghdad records: 202 redesign, 17 replace, 151 retain shared with interface revalidation, 44 retire wheel-specific; all 63 old packages and 72 requirements map to 11 primary packages | Accepted exact-configuration outputs for every allocated item; legacy geometry/tests do not transfer |
| [Native geometry](geometry.py) | Default 624-solid partial 17 m frame/24-cartridge lift interface, plus a two-direction 25 m civil bay; actual FreeCAD solid export, FCStd/STEP reopening, identities and selected interference checks | Full body/propulsion/capture definition, qualified joints/retainers, structural calculations, materials and production drawings; export receipts identify the exact checked variant |
| [2D field solver](field.py) | Variable-reluctivity finite-difference A_z equation, manufactured sine-solution second-order controls, artificial nonlinear iron law, air Maxwell contours and gap/temperature/current coupon studies | Coupon force remains unconverged under mesh refinement; actual B-H/recoil curves, 3D ends/windings, force/loss/demagnetisation maps and physical rig correlation |
| [Rust module array](../../crates/osr-maglev-control/README.md) | 24-module force allocation, virtual plant/replay, I/O contracts and support-aware fault logic | Actual force/current/thermal plant, isolated physical I/O, independent protection/power domains and measured SBC deadlines |
| [Two-way beam/control replay](coupled.py) | Rust module forces load a 50-element, six-vertical-mode beam; resulting local displacement changes subsequent controller gaps; three-second virtual demonstrator and independent static beam controls | Flexible body, torsion/lateral/soil/joint/moving-load dynamics, qualified magnetic actuator maps, physical timing and instrumented stability/ride/fault evidence |
| [City compiler](cities.py) and [catalogue index](city-index.md) | 266 cities / 1,565 lines with retained geography/demand, matched AW2/AW3 formations, recalculated duty/fleet/charging/depot quantities and partial low/base/high costs | Located terminal loops/ring closure, coupling/platform/egress fit, real route/charging/berth/dispatch/recovery duty and complete programme cost |

The native interface is a partial material model. Its recessed-retainer variant
models 8 mm nominal fastener-head clearance; the earlier 576-solid flat-retainer
variant has only 2 mm. Ground ferrite edge recesses, low-profile fasteners,
retention after crack/debond, force area and the complete manufacturing/control/
thermal gap budget remain unqualified. Neither nominal clearance nor successful
CAD reopening establishes physical fit or a released vehicle.

The two-way replay uses a stationary rigid car and synthetic instantaneous force
channels. It exchanges forces and beam displacements in both directions, but its
1 ms step is virtual time. It does not demonstrate physical I/O timing or a
validated six-degree-of-freedom vehicle/guideway system. PDE residuals and the
manufactured equation's refinement order likewise do not establish coupon force
convergence or actual lift capacity.

City packages remain separate from the retained wheel/rail city outputs.
Formation preserves both passenger loading cases; old train counts, turnouts and
cost totals are not adopted. Fixed terminal loops remain unlocated allowances,
charging and berth layouts require validation, and complete city programme costs
remain unknown. Partial fleet/ordinary-elevated allowances are not project bids
or achieved savings. The [Baghdad package](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/README.md)
shows these assumptions and open gates for the six-car comparison.

## Manufacturing and acceptance

The register includes 23 planned EBOM objects, 437 industrial obligations,
ERP/lifecycle and observation-only FUXA interface plans, unanswered supplier
questions, and G0–G5 procedures with traveller prerequisites. Its 27 unresolved
quantitative thresholds must be derived and approved before testing. No material
certificate, priced origin-traced MBOM, actual equipment/process qualification,
installed serial, physical result or acceptance signature is invented. Supplier
questions distinguish UK manufacture from UK distribution/supply; local
assembly does not establish input origin or local value-added percentage.

`workbook.py` imports literal cells with source addresses and a workbook hash;
it does not execute spreadsheet code or trust cached formula outputs. `model.py`
recalculates the supplied budgets and physical screens. `delivery.py` binds
source, input, runtime and output hashes. Checksum verification establishes
integrity; `check` repeats its declared calculations. Native exports and physical
tests require their own configuration-specific receipts and evidence.

Old physical generators remain accessible through explicit `legacy` launcher
paths. Their city/CAD/book outputs are comparator evidence; new models and
qualified physical tests must establish the maglev design.

## Predominantly elevated and simpler by design

The primary policy now targets 99% elevated mainline coverage and proposes all
ordinary running sections on viaducts. Existing at-grade planning lengths enter
the new ordinary viaduct allowance; bridges and other special crossings retain
separate quantities and unpriced scope. Existing routes are retained geography,
not newly approved straight alignments. Rings and terminal loops still curve.
Housing demolition, road conflicts, wildlife effects, utilities, station/egress
access, temporary works and pier/foundation placement require their own evidence.
An elevated line does not establish zero impact or eliminate air-rights needs.

[optimisation.py](optimisation.py) runs a bounded joint search controlled by
[optimisation.toml](optimisation.toml). Section dimensions, span/support count,
transport, lift count/mass and candidate vehicle tare enter the same comparison.
The Pareto objectives include indexed civil cost, counted concrete mass, bare
lift mass, car tare, train allowance and the number of unqualified vehicle target changes.
Gross uncracked stiffness and bare lifting-mass screens are numerical filters;
relative magnetic gap, strength, actual crane capacity and site acceptance stay open.

Costs are indexed from the supplied workbook: structural volume, support count,
transport mass and handling affect their declared rows. Passive rails, walkway
brackets, temporary works, installation, night work, QA, relocation and traffic
receive no automatic deletion credit. A cheaper fully manufactured and erected
system needs evidence for actual unit rates, connections, tooling, yield,
production throughput, access and maintenance. Complete city totals stay unknown.

Vehicle targets retain equal passenger loads, storage, ferrite, capture/braking
and growth reserve. Reduced frame/equipment mass does not automatically reduce
procurement cost. The existing USD90,000/USD60,000 magnetic hardware targets are
unquoted budget sensitivities; removed wheel/gear costs are credited only once.
Doors, HVAC fans/pumps as required, cooling, sensors, support drives and independent
protection remain. Imported-input cost and local value-added remain unknown until
origin-traced records exist; zero normal-running-gear moving parts is an objective,
not a count of every mechanism on the train.

Source context: [FTA aerial fixed-guideway planning](https://www.transit.dot.gov/sites/fta.dot.gov/files/2025-01/Project-and-Construction-Management-Guidelines-January-2025.pdf)
identifies ROW, adjacent-building, utility and station-access considerations.
[FHWA prefabrication guidance](https://www.fhwa.dot.gov/bridge/prefab/index.cfm)
supports offsite assembly and reduced onsite disruption; its
[decision framework](https://www.fhwa.dot.gov/bridge/prefab/framework.cfm) retains
connections, erection equipment and local production capability as feasibility
issues. These references do not validate OSR pricing or railway acceptance.

The initial expanded grid also explores 80 mm walls and deeper narrow sections.
These require separate reinforcement/cover, prestress, local-load, durability,
torsion and production assessment. The new screens count the retained wide iron
faces from native material quantities (about 300 kg/m per direction), rather than
substituting the older 100 kg/m allowance. This does not close bracket/anchor mass.
Analytical alternatives are separate configurations from the retained native CAD
and the earlier flexible-beam replay; those receipts do not validate the new minima.

## Integrated guidebeam and onboard evacuation target

The new target is one integrated structural guidebeam per direction without a
continuous external walkway. The 54-part beam-only bay removes 20 walkway
cassettes and 14,940 kg of modelled material from the retained 25 m reference.
Iron reaction faces are necessary for the current attraction circuit; plain
concrete is not its magnetic reaction material. Supports, foundations, joints,
mounts, drainage and emergency/maintenance access still need engineering.

[evacuation.py](evacuation.py) and [evacuation.toml](evacuation.toml) define a
preferred vertical controlled-descent chute concept (internal spiral or cell
variants), an inclined-slide comparator and counterexamples. Four chute-height
envelopes (8/12/20/30 m) assume a 1.2 m diameter, 1 m stand-off and ±0.5 m
lateral displacement. These are geometric sensitivities, not supplier dimensions,
a wind-response model or approved operating heights. An illustrative
8 m height at 30 degrees requires a 16 m straight slide, 13.86 m horizontal run
and additional landing clearance. Live roads, roofs, water, obstructed land and
insufficient clearance reject that landing path. Safe geometry alone stays on
hold: fire/smoke, adjacent trains, wind/heat/dust, support immobilisation, disabled
and assisted evacuation, crew/responder access, inflation/reliability and the
applicable authority's acceptance are unproved. No real deployment is commanded.

For a non-fire breakdown with a tenable train, the initial strategy is recovery
to a station or qualified rescue transfer. Emergency chutes/slides are not assumed to
be the universal sole escape route. Historical FTA guidance and aviation/marine
analogies inform research; their test criteria or equipment approvals do not
transfer to this railway. The current full rail standard and deployment-specific
acceptance basis require independent review. CIV-004 already retains the reference
walkway until an approved egress design replaces it; that acceptance remains open.

Another 432 no-walkway research cases are held outside reference champion and
city-price selection. Gross avoided civil allowances are reported separately
from net system savings. A provisional three doors per side would mean six
evacuation packs per car; installed mass, mounting, lost cabin space, inspection,
repacking/replacement and lifetime costs require actual supplier data. The 25/50/
100 kg pack values are mass sensitivities, not selected equipment. British supply
and service leads are distinct from confirmed British manufacture.

Run `./osr design evacuation-native` to export/reopen the candidate native solids
and render their retained geometry. The [primary report](../../docs/design-engine/ferrite-maglev/reference/index.html)
links the CAD, counterexamples, quantities and clearance diagram. No evacuation,
manufacturing or physical release is claimed.

A further geometric counterexample tests an inward-facing door against the
retained adjacent beam: the straight slide centreline intersects the adjacent
beam's web. An outward path clear of those modelled boxes still has no approved
landing or evacuation. Door equipment count therefore cannot be used as the count
of simultaneously usable exits. Both cases are retained in the structured study.

The chute research compares [Axel Thoms](https://escape-chute.net/en/stationary-escape-chute/)
(vertical internal spiral), [Survitec MarinArk 2](https://survitecgroup.com/marine-evacuation-systems/marin-ark-2)
(enclosed helical marine path) and [VIKING Basic EVAC](https://www.viking-life.com/products/evacuation-systems/offshore-evacuation-systems/chute-systems/viking-basic-evac-evacuation-system/)
(offshore chute, published installation heights up to 35 m). These applications
have different supports, stabilisation and receiving areas from an onboard train
system. [Safelincs](https://www.safelincs.co.uk/product/fire-evacuation-chute-for-escape-out-of-windows-and-from-roofs)
lists a 4–120 m building spiral and up to 15 persons/minute: UK supply of a
German-made product, not confirmed British manufacture or railway qualification.
The manufacturer states that each installation is designed for its location.

At that unverified building flow claim, 960 passengers and 18 usable chutes give
an ideal queue bound of 243 seconds including an assumed 30-second deployment;
with nine usable chutes it is 457 seconds. These are optimistic arithmetic bounds,
not evacuation simulations: cabin distribution, descent, assistance, entry/exit
queues and blocked outlets still require evaluation. No rail time limit is adopted.
A vertical swept-envelope check also retains adjacent-beam clashes where assumed
sway reaches the other guidebeam. Ground anchors, variable length at arbitrary
stop positions, outlet control, local fire/smoke, packed volume and door/body
reaction loads remain design work; no civil or lifecycle saving is accepted yet.

## Implementation roadmap

This roadmap reconciles the initial v0.5 review with the current elevated,
integrated-beam and spiral-chute direction. The older request for mandatory
walkways is a comparator; an approved alternative is still required before removal.
Architecture objectives are implemented; complete design and manufacture remain open.

| Workstream | Current executable comparison | Required next evidence |
|---|---|---|
| Elevated, direct alignments | All ordinary retained sections proposed elevated; original class lengths and conversion budgets retained; radial path length / first-to-last chord reported from cell geometry | Located alternatives, standard straight-span fraction, horizontal/vertical radii, buildings/utilities, station walking catchments and interchange access; rings need their own defined corridor endpoints |
| Complete installed viaduct | Candidate-specific indexed ordinary allowances, counted concrete, bare lifts, support counts; separate lowest-allowance/lowest-counted-mass observations and Pareto set | Actual foundations/ground, prestress/reinforcement, joints, lifting accessories/crane radius, tolerances, interfaces, full installed quantities and supplier prices |
| Production and erection | Quantities and indexed transport/handling sensitivities | A maglev-specific finite-resource factory, curing, connection and erection schedule; fastest-construction candidate remains null until this exists |
| Complete rolling stock | Matched payload/storage/reserve/ferrite, mass-allocation alternatives, fixed running-gear objective, required passenger/protection equipment retained | Part-level EBOM/MBOM, carriers/interfaces, unique and moving assembly counts, wear tasks, measured module replacement and failed-train recovery times |
| Vehicle/civil/energy feedback | Candidate AW3 mass changes beam demand and the same hot, no-regeneration, straight/level duty/charger screen | Qualified force/loss/thermal maps, candidate-specific actuator layout/control and coupled dynamics; bidirectional complete-system optimisation is not yet implemented |
| Local manufacture and cost | Workbook-indexed allowances; removed conventional scope credited once; local-integration budget targets separate | Origin-traced supplier-priced MBOM, factory-gate scope, complete installed cost, labour, tooling/yield, specialist dependencies and lifecycle repair/renewal costs |
| Beam-only evacuation | Conditional CAD, slide/chute clearance and unsafe-landing counterexamples; no-walkway cases excluded from reference promotion | Selected device/mount/entry design, additional mass, every-stop landing/alternative, descent/flow, accessibility, wind/fire/rescue, cost and independent acceptance |

Every search candidate has a `system_scorecard` in the complete retained
`optimisation-study.json.gz`. Values identify their units and arithmetic scope;
missing quantities are null. Cost and mass extrema refer to indexed ordinary
allowances and counted concrete, not complete installed price or mass. All
no-walkway scorecards hold energy/charging because extra chute mass is unknown.
The profile-level baseline duty remains a comparator. Supplier-priced cost,
imported value, labour and repair times are not inferred from a lighter mass target.
The separate legacy civil schedule is not promoted into a maglev winner.

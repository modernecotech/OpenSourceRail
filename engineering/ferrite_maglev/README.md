# OpenSourceRail v0.5 ferrite-maglev engineering

The current design uses ferrite PM-biased active-attraction support, fixed onboard windings and electronics, passive reaction iron and compact concrete guidebeams. Rust control packages run offline models for eventual off-the-shelf SBC implementation. Powered linear propulsion, cooling, sensing, independent protection, braking, capture, parking and recovery remain necessary. **Accepted engineering and physical releases: zero.**

## Run and inspect

```bash
./osr build
./osr design run
./osr design iterate
./osr design check
./osr design verify
./osr city baghdad
./osr sim baghdad --cycles 2
./osr workbench
./osr test
./osr book
cargo test --locked -p osr-maglev-control --all-targets
```

[Generated report](../../docs/design-engine/ferrite-maglev/reference/index.html) · [Workbench](../../docs/workbench/maglev/index.html) · [city directory](city-index.md) · [architecture](../../docs/ARCHITECTURE.md).

`./osr capabilities` publishes executable sources and their scope. `./osr catalogue plan --city baghdad` resolves a selected regeneration, and `./osr catalogue run --city baghdad` rebuilds that city. `./osr readiness` reports current-source gates. `./osr design release-check` remains held while acceptance is open.

The [dependency runner](workflow.py) verifies implemented native, numerical, control, city and publication prerequisites in order. It rebuilds stale evidence and holds dependent outputs after failures. An interprocess lock excludes concurrent timer/manual builds. Runtime progress is stored under `build/maglev-workflow/latest.json`. This is a finite reproducible build of implemented evaluators; missing physical tests and engineering decisions require additional work.

The [adaptive search](iteration.py), configured in [iteration.toml](iteration.toml), generates new section/span, vehicle-mass allocation and actual Rust-gain proposals from preceding results. Each viable proposal faces three coupled load/disturbance cases and replay/excess-gap controls. Shortlisted exact revisions face two separate confirmation scenarios. Failed confirmations remove recommendation eligibility while preserving analytical history. The seeded campaign has explicit evaluation and stagnation budgets; exact-source cache receipts support restart. A timer resumes stale campaigns, then idles once current.

[Published campaign](../../docs/design-engine/ferrite-maglev/iterative/README.md) includes ancestry, traces, progress and the research recommendation. Preference weights and screening bounds are provisional. Scaled body/equipment mass and inertia assumptions do not replace complete manufactured geometry, magnetic measurements or qualified dynamics. The recommendation is kept separate from the reference configuration and city costing.

## Current inputs and design records

| Concern | Source |
|---|---|
| Architecture | [Infrastructure policy](../../lib/templates/infrastructure.toml) |
| Vehicle and civil configuration | [Reference configuration](reference-configuration.toml), [configuration reader](configuration.py), [study assumptions](../../ferrite-maglev-study.toml) |
| Requirements and work allocation | [Requirements data](data/requirements.json), [current systems register](transition.py) |
| Cost quantities and manufacturing | [Process model](manufacturing.py), [planning rates](data/cost-rates.json) |
| Magnetic/native geometry | [Geometry](geometry.py), [field equations](field.py), [native export](../factory_examples/native.py) |
| City service and geography | Each city's `city.json`; [compiler](cities.py) |
| Control | [Rust maglev package](../../crates/osr-maglev-control/README.md), [offline SBC profile](../../deployment/maglev.toml) |

Baghdad uses six 17 m bodies with shared coupling, platform, magnetic-arm and boarding-gap assumptions. The partial station model includes floor frames, guidebeams, island platform and a centred flush lift floor. It omits complete vehicle and station equipment; the boarding gap requires a qualified bridge plate. Native exports identify the exact modeled revision.

## Implementation and closure status

| Capability | Implemented scope | Outstanding evidence |
|---|---|---|
| Systems register | Current system items, requirement relationships, work packages, manufacturing and test obligations | Approved quantitative criteria and accepted exact-configuration evidence |
| Native geometry | Partial magnetic interface, civil bay, beam-only variant, evacuation entry, support envelopes and Baghdad station; FreeCAD/STEP exports, reopening checks, images and short visibility videos | Full production geometry, qualified materials, joints, loads, tolerance chains and manufacturing drawings |
| Magnetic field | 2D variable-reluctivity equation, manufactured-solution controls and explicit nonlinear material hypotheses | Coupon force convergence, measured material data, 3D force/loss maps and physical rig correlation |
| Rust control | Module allocation, five-mode virtual replay, protection interfaces, support-preserving stops and advisory evacuation | Actual actuator/sensor model, isolated physical I/O, independent protection and measured timing |
| Coupled replay | Two-way exchange of Rust module forces and flexible vertical-beam deflections | Flexible vehicle, lateral/torsional/joint/soil dynamics, moving loads and correlated stability/ride/fault measurements |
| Adaptive design | Result-guided vehicle/beam/gain variation, actual Rust coupling, protection controls, Pareto observations and separate confirmation | Full production geometry, qualified criteria, measured plant, whole-train dynamics and independent acceptance |
| City planning | Capacity-matched formations, duty, fleet, charging, guideway quantities, provisional costs and manufacturing process needs | Located terminal loops, route/ground/utility surveys, recovery, full duty and complete programme economics |
| Industrialisation | Current material quantities and explicit process/rate assumptions | Configured suppliers, qualified processes, origin-traced MBOM, production capacity, logistics and installed scope |

Assembly videos show final-position visibility sequences. They do not simulate motion, collision-free erection, crane operation or chute deployment. CAD export integrity does not establish strength or manufacturing readiness. Virtual replay steps do not demonstrate physical deadlines. Equation residuals do not establish real lift capacity.

## Manufacturing and costs

Cost estimates start from current maglev quantities and fabrication operations. The reference formation is six cars. Per-car equipment, shared train equipment, beam/support quantities, station and factory scope must be kept distinct. [Planning rates](data/cost-rates.json) are explicit assumptions, rather than supplier quotations. A missing first-pilot/NRE total stays unpriced. Project scope, contingency, lifecycle and finance require their own evidence.

City `engineering/maglev/manufacturing.json` records the materials, processing, equipment needs and construction approaches behind its estimate. Candidate processes include controlled precast casting/curing and inspection, reinforcement/prestress work, reaction-iron fabrication and fitting, structural cutting/joining, coil winding, cartridge assembly, wiring, software integration and factory testing. Transport, temporary works, crane radius/capacity, joints and site acceptance remain part of installed delivery.

Prefer verified British manufacture when considering UK suppliers. A UK distributor or integrator does not establish UK manufacturing origin. Likewise domestic assembly does not change imported cell, semiconductor, sensor or raw-material origin. Complete local-content percentage remains unknown until the complete bill and origin evidence exist.

## Evacuation and compact civil works

The research target is one integrated beam per direction without a continuous external walkway. Necessary reaction iron, supports, foundations and connections remain. A vertical spiral controlled-descent chute is the preferred unqualified onboard candidate. The [evacuation study](evacuation.py) tracks variable height, anchorage, ground landing, assistance, fire/weather, partial failure, rescue, lifecycle and driverless operation. Walkway removal is conditional on accepted route and onboard alternatives at every permitted stopping location.

## Implementation roadmap

The [closure queue](../../docs/ROADMAP.md#primary-maglev-closure-queue) covers complete mechanical/civil geometry, magnetic qualification, dynamics, physical controls, origin-traced industrialisation, city site evidence and demonstrator acceptance. Requirements allocation and successful digital checks define progress within their scope; neither constitutes a manufacturing or operating release.

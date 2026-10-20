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

The register includes 22 planned EBOM objects, 436 industrial obligations,
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

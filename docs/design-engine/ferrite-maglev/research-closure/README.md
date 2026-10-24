# Design completion and optimisation execution plan

OpenSourceRail pursues simple locally buildable urban transport, low construction
and operating cost, affordable debt and high useful passenger throughput. Fixed
station motors launch and receive trains; onboard support and services remain
independent through the coast. Passengers transfer between fixed lines.
[Project introduction and ethos](../../../../README.md).

Reviewed baseline: `d875faec18` (24 October 2026). Canonical candidate:
`a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd`. Repository checks and bounded
research are executed; **the train design remains incomplete and unaccepted**.

This plan retains **all 576 qualification tasks**, covering
179 requirements, 53 system IDs,
8 workstreams, 15 protocols and G0–G5.
No task is dropped because a simulation fails. Physical/site/supplier measurements,
approved limits and independent decisions remain required. Owner roles below
are proposed responsibilities, not appointments or reviewer approvals.

## Completed repository work

| Work | Executed result | Scope |
|---|---|---|
| [Magnetic archive audit](magnetics.md) | 225 original records independently checked | Four original static passes; fifteen conditional topology passes; zero combined guidance passes |
| [Additional magnetic optimisation](magnetic-optimisation.json) | 240 new paired-topology winding cases; 0 joint survivors | Counted mass feedback and unchanged current, fill, field and thermal limits |
| [Propulsion follow-up](propulsion.md) | Four scalar electrical fixtures; 28 current/duty variants, 17 conditional coupon passes | All remain ineligible for system adoption; local peak convergence unresolved |
| [Dynamics and curve optimisation](dynamics.md) | 14 retained cases audited; 0 motion cases; 0 continued post-fault cases | Attempted initial currents distinguished from executed currents; analytical curve fitting only |
| Full qualification inventory | 576 dependency-ordered tasks retained | Zero accepted requirements or physical gates |

Digital ERP/FUXA screens remain separate from physical engineering acceptance.
The 240 new magnetic cases are additional records; the sealed 225-record archive
is unchanged. No replacement configuration is adopted. A conditional propulsion
coupon does not cure the canonical support deficit or provide an installed mass.

## Next optimisation and design work

1. Build independent nonlinear spatial flux models for paired original/sensitivity geometries; establish mesh/domain and energy/force consistency before interpreting gains.
2. Design and count revised guidance windings and heat paths, including insulation, cooling/protection and support mass; rerun simultaneous AW3 lift/lateral/current/thermal screens.
3. Resolve propulsion local peaks with independent longitudinal/depth refinement and retain refused meshes; count the changed installed propulsion geometry.
4. Develop shorter or articulated magnetic mounting candidates for curves; count mechanisms and verify gap, capture, brake and structural load paths.
5. Bind one surviving revision to actual current control, repeated duty, initial equilibrium and fault trajectories before the four-stop electromechanical run.
6. Execute all physical, supplier, site and independent-review tasks using the existing typed qualification procedures and approved limits.

The magnetic search found no simultaneous survivor. Its best original-topology
case requires about 139 W/K guidance cooling against the assumed 18 W/K; the
unvalidated sensitivity needs about 50 W/K. Adding cooling changes mass and lift
demand, so neither figure is a completed heat-path design. Propulsion ranking
selects a next fixed-pose coupon using force-times-duty, not route performance.
Recentring the existing rigid array reduces the necessary curve radius from
about 2,521 m to 1,250 m; the 300 m and 50 m cases still fail. Shorter/articulated
mounts require a new geometry, mass, tolerance and structural definition.

### Prepared next magnetic comparisons

The independent spatial/thermal experiments below are **planned and unexecuted**.
Each pair holds dimensions, conductor area and pack size fixed while changing
the flux-allocation hypothesis. This separates topology from winding/mass changes.
The original and sensitivity winners use different pack sizes, so comparing only
those two winners would confound the experiment. Exact hypothesis digests and
paired case IDs are retained in the machine-readable plan.

| Seed | Flux hypothesis | Pole width mm | Core scale | Guide turns | Guide conductor mm² | Pack |
|---|---|---:|---:|---:|---:|---|
| closure-072 | original-branch-flux | 22.5 | 2.4 | 140 | 16.617 | standard |
| closure-073 | useful-only-poles-sensitivity | 22.5 | 2.4 | 140 | 16.617 | standard |
| closure-074 | original-branch-flux | 22.5 | 2.4 | 140 | 19.252 | wide |
| closure-075 | useful-only-poles-sensitivity | 22.5 | 2.4 | 140 | 19.252 | wide |

The next model must derive the physical flux split from the same spatial
geometry, rather than impose either reluctance-network hypothesis as truth.
Cooling requirements remain fixed-load lower bounds; redesigned hardware still
needs its own mass and support calculation before an operating comparison.

## Complete work allocation

The [machine-readable plan](execution-plan.json.gz) contains every original task,
deliverable, prerequisite, hold rule and topological order. The original
[qualification procedures](../qualification/README.md) remain the authority for
typed physical evidence. All 576 tasks remain on hold there.

| Responsible role | Design deliverable | Missing evidence / evaluator |
|---|---|---|
| Vehicle structures and equipment | Sized sandwich/rib/stringer and local hardpoint drawings, service joint geometry, exclusive interface BOM and complete equipment mass closure | Qualified hot/aged orthotropic laminate/core/adhesive properties; Full body buckling/fatigue/crash/coupler/peel and insert tests; Complete equipment, joint, mass/CG/inertia and repair drawings |
| Magnetic assemblies and maps | Grade-controlled cartridge/coil/steel/phase geometry and converged shared support-thrust force/flux/R/L/loss/thermal maps | Nonlinear 3D finite-array/steel/coil circuit and magnetic stiffness; Demagnetisation, retention, control authority and full-scale force/loss rig correlation |
| Station propulsion and receiving brakes | Station and located booster cassette/section/bridge/phase/rail-beam interface drawings, grouped converter BOM, normal/thrust reactions and independently available receiving brake | Measured force constants, normal-force coupling, R/L/voltage/current and repeated thermal duty; Concrete anchors, isolation, protection, phase handover and receiving redundancy; Supplier-priced converter/winding configurations and complete station MEP |
| Civil design and construction | Prestress/rebar/cover/end-block/bearing/anchor schedules, temporary restraint and lifting plans, ground-selected foundations and emergency load paths | Shear/torsion/end-zone/transfer/cracking/creep and moving train-gap interaction; Ground/utility/settlement/water/seismic/wind and anchor capacities; Load-tested bearings, handling points, restraints and serial survey acceptance |
| Services, storage and charging | Power/thermal single-lines, battery/BMS/charger and services duty, independent support reserve, qualified HVAC/cooling hardware | Measured hot-weather HVAC/door duty, repeated charging/ageing and containment; Isolated protection, support-loss reserve, connector and power/thermal tests |
| Controls, target hardware and protection | Versioned support/phase/reservation/complete-consist sensing and independent protection interfaces, fault containment and physical timing tests | Authenticated independent sensing/clearance, common-cause and power-loss tests; Real current/position control and measured MCU/SBC deadlines; System hazards, configuration authentication and independent acceptance |
| Stations, access and evacuation | Passenger-transfer hubs between independent fixed lines with accessible platform/vertical paths, route egress, assisted evacuation and located recovery provisions; no train-routing switch | All-stop landing/height/wind/fire/obstruction and assisted evacuation tests; Full station structure, access, canopy/services and emergency transfers; Qualified device stowage/deployment mass, anchors, inspection and renewal |
| Manufacturing, economics and independent assurance | Instance-bound MBOM/routings, factory/mould/crew/crane/transport plans, depot/terminal/recovery layout, origin/price records and demonstrator acceptance | Configured machines, controlled processes, measured yield/cure/output and supplier offers; Access-qualified terminal/depot and rescue/winch/tow arrangements and recovery exercises; Independent requirements/hazards/site/operator approval and serial material/test evidence |

City rollout, factory output, hardware timing, surveyed routes and whole-life
economics remain in these workstreams. Planning assumptions and synthetic demand
must retain their labels. Software tests do not resolve measured demand, price,
site, material or hardware gaps.

## Simplicity, cost and passenger-capacity design round

The [versioned research specification](../../../../engineering/maglev_research/design-intent.toml)
allows lower speed, different stop spacing, dwell and repeated-car formations.
It preserves the normal **14,400 passengers/hour/direction** comparison floor,
full-tail protection, passenger loads and magnetic/current/thermal screens.
These are proposed study inputs, not approved operating or city specifications.

| Executed workstream | Result |
|---|---|
| [Counted support architectures](support-architecture.md) | 256 shared-circuit cases; 32 nominal passes; **0** combined reserve/fit survivors |
| Separate guidance contract | 18 material-bound cases; proposed 30 support modules plus 6 guide units/car, **54.469 t AW3/car minimum** |
| [Service at canonical comparison mass](service-envelope.md) | 1044 service variants; 107 meet the normal capacity comparison floor conditionally |
| Service at the support material-mass floor | 1710 variants; 45 meet that floor conditionally |
| [Finite-stock carriers and terminal curves](carrier-geometry.md) | 160 cases; 0 yaw-only survivors; installed joints/guidance/cooling fit remains open |

The separate-guide contract is a **stationary spatial-model/rig proposal**.
Its gap field and steel flux, turns, conductor, bobbin, fluid, cooling and mass
are explicit. Airgap-only MMF still omits steel/leakage/control margin; it is
not a demonstrated guidance circuit. The counted mass excludes unweighed carrier
mechanisms and remaining installed interfaces. Its nominal support power fits
the inherited suspension allocation conditionally, while the static 1.3-load
subtotal exceeds it; repeated duty and fault reserve remain unqualified.

The same lower-bound mass is used for the heavier service study; the lighter
canonical mass supplies no free performance credit. Its ranking selects a
**research comparison** with 12 cars,
209.5 m overall,
1 km stop spacing,
28.8 km/h speed cap,
45 s dwell and approximately
14,796 normal passengers/hour/direction.
The full comparison includes station, platform, winding and charging quantities.
All service cases retain failed/open thermal, support, grade and protection gates.
The existing 5% grade comparison is still unmet; no unproved lower-grade route
is substituted. Longer trains and high charging ratings do not establish low
total cost.

Carrier geometry includes full stock envelopes, tolerance reserve, collisions,
body offset and actual lateral travel. Multiple yaw pivots on one rigid body
cannot independently follow the curve without the declared lateral mechanism.
Larger terminal radii and a 3.0 m underbody clearance are explicit research
changes; the 2.65 m body and current city layouts are not silently widened.
Guide units, capture/brakes, coolers, bearings and slides must fit and be weighed
before repeating the support and service calculations.

**Integrated specification decision: hold.** No one configuration yet combines
validated lift/guidance, complete installed mass, carriers, repeated thermal duty,
protection, route geometry and cost at the desired normal passenger capacity.
The existing catalogue defaults remain preserved, and the next work is defined
by exact research contracts rather than automatic promotion of separate wins.



## README introductions

The [README context register](readme-coverage.md) audits every repository README,
maintains concise introductions at the thirteen manual entrypoints and preserves
source-bound city, numerical and archived evidence wording. Each audited README
has a route to the current system introduction, either through its own navigation
or directly from that register. The [coverage receipt](readme-coverage.json)
records individual file digests and checks original evidence bindings.

## Admission order for integrated operation

1. **candidate-definition** — One revised configuration digest with the selected car formation, support/guide channel counts, complete installed mass/CG/inertia, tolerances and protection equipment counted once.
2. **maps-and-initial-equilibrium** — Same-revision finite-geometry lift/guidance maps over actual gaps/current/temperature and within-drive current/thermal/material limits; solve the actual support and guidance channel counts across the selected formation and prove static guideway equilibrium. The canonical 144-module/six-car inverse remains a separate preserved reference.
3. **curve-and-contact-fit** — Same-revision rigid or articulated module, capture and brake geometry fits urban/terminal curves with tolerance and load paths; count added mechanisms/mass.
4. **propulsion-and-electrical-transients** — Same-revision converged useful-field map, located group phase/R/L/flux, voltage/current limits, thermal repeated duty, receiver braking and support/reserve independence.
5. **continued-fault-motion** — Current-based motion of the complete selected formation, actual revised channel allocation and post-injection trajectories under all named faults, with nonzero frames, energy balance and verified supported/captured stop outcomes; no inherited six-car credit for longer formations.
6. **four-stop-electromechanical** — Actual front/tail authority and complete selected-formation poses through four stops, receiving braking, dwell, services/charging, terminal return and repeated dispatch at the exact revised installed mass/maps/channel counts.
7. **physical-qualification** — Calibrated rigs, actual target timing/protection, serial-specific hardware and independent G0–G5 dispositions. Numerical screening gives no release authority.

The complete four-stop electromechanical journey remains unexecuted. Known
initial refusals are preserved; rerunning them is not useful motion evidence.

## Reproduce and maintain

```bash
tools/automation/osr-python -m engineering.maglev_research.research_closure publish
tools/automation/osr-python -m engineering.maglev_research.research_closure check
tools/automation/osr-python -m engineering.maglev_research.magnetic_research_closure --optimise build/magnetic-followup-new.json
bash tools/automation/test-maglev-research.sh
tools/automation/osr-python -m engineering.maglev_research.readme_context --check
./osr test
```

`publish` refreshes audits, electrical coupons, curve bounds and the full plan.
It verifies the retained magnetic optimisation; it does not rerun that search.
`check` recomputes the publication and rejects changed sources or payloads.
Optimisation requires a new output path, preserving previous runs. New results
must be reviewed against the joint constraints before changing this plan.

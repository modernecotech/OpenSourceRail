# Roadmap

OpenSourceRail v0.5 uses one ferrite-maglev architecture across mechanical, civil, software, manufacturing and city planning. [Implemented work and commands](../engineering/ferrite_maglev/README.md) and the [current report](design-engine/ferrite-maglev/reference/index.html) identify the tested digital scope. Accepted engineering and physical releases remain zero.

## Primary maglev closure queue

| Package | Evidence required for closure |
|---|---|
| Requirements and configuration | Approved loads, service envelope, tolerances and quantitative acceptance criteria for exact revisions |
| Magnetic assemblies | Complete support/guidance/propulsion/capture assemblies, connections and dimensional chains |
| Magnetic force and loss | Converged force calculations, qualified material curves, 3D winding/end effects, thermal maps and correlated rig measurements |
| Vehicle | Complete body, doors, interiors, storage, cooling, controls and evacuation; mass, centre of gravity, inertia and structural qualification |
| Civil kit | Beams, reaction iron, connections, supports, foundations, stations, services and all handling/construction stages |
| Control and protection | Qualified plant model, independent protection, loss-of-power behavior, braking, capture and recovery interfaces |
| Coupled dynamics | Moving trains, flexible bodies, lateral/torsional modes, joints and soil with calibrated models |
| SBC hardware | Isolated I/O, power stages, measured deadlines, watchdogs and independent protection on selected equipment |
| City delivery | Located routes, terminal loops, platforms, charging, storage/recovery, all-stop evacuation and site investigations |
| Manufacturing and economics | Complete origin-traced MBOM, process routes, machine/tooling options, throughput, transport, erection, maintenance and financing |
| Demonstrator | Traceable manufactured units, independent inspections and physical acceptance on identified serials and revisions |

The adaptive designer now varies vehicle mass allocations, beam geometry/spans and actual Rust controller gains using previous measured results. It retains ancestry and traces, applies separate holdout scenarios and disqualifies failed confirmations. Its preferred candidate is a bounded research result; it does not close production geometry, qualified magnetic maps, physical timing or whole-train acceptance.

The automated runner can regenerate the implemented studies and hold downstream evidence after failures. Missing evaluators, measurements and approvals remain open work, even after every current automated check passes.

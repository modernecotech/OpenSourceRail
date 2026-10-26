# Development roadmap

OpenSourceRail aims for simple, low-cost, locally maintainable urban transport with frequent comfortable service. The current default is the six-car comfort/NdFeB development design in [the authoritative selector](../engineering/development-baseline.toml). All PMs and support controls remain on the train; ordinary guideway is concrete and passive steel.

## Current digital baseline

- Six 17 m cars, 44 seats plus two wheelchair places/car, zero planned standing and two doors on one side.
- Aluminium extrusion frame, lightweight sandwich floor/roof, counted bench stock and retained glazing references.
- 120-second target, 8,280 normal passengers/hour/direction and a 72 km/h retained-stop network proposal.
- Candidate-bound mass, service, civil-interface, control, manufacturing and procurement records; all city planning uses the same default.
- Native material CAD/STEP and source-bound Rust protection-method fixtures, with clear scope limits.

The [current dossier](design-engine/current/README.md), [city index](design-engine/current/cities.json) and [Workbench](workbench/current/index.html) share one selection. The [historical programme](archives/pre-comfort-default/README.md) remains evidence of earlier work rather than the current default.

## Work required for physical completion

| Work package | Completion evidence |
|---|---|
| Suspension and control | Converged installed 3D force/moment/current/temperature maps; stable equilibrium, lateral/rotational control and fault reserve |
| Complete vehicle | Located installed stock, full CG/inertia; structural, fatigue, buckling, modal and passenger-load confirmation |
| Capture and braking | Counted revised hardware; force/energy and retention tests; demonstrated stopping and holding across relevant conditions |
| Thermal and HVAC | Roof/core temperature within material limits; qualified 50 C cooling capacity, ventilation, redundancy and essential-energy duty |
| Station drive | Current/voltage/force/thermal envelopes for actual winding groups; phase handoff and overlapping station resources |
| Coupled journey | Empty, capped-load, crowd-control and fault cases from verified hover through launch, coast and controlled arrival |
| Civil and construction | Counted facing supports/anchors, beam prestress/rebar, piers, foundations, survey tolerances and erection stages |
| Operations | Protected 120-second operation with dwell variation, receiving failures, evacuation, accessibility and realistic transfers |
| Whole-system economics | Same-candidate priced vehicle/civil/station stock, factory labour, energy, renewals, fleet, crews and finance |
| Prototype correlation | Authenticated measured force, temperature, geometry, mass and structural data linked to the selected parts |

Capture energy and unshaded hot-roof-core cases presently fail; remaining physical gates are unknown. A development selection does not waive these results. The 46-person cap needs enforceable admission and compatible stations; it does not eliminate accidental or crowd loads. Glass and electropermanent magnets remain comparisons until their complete evidence supports selection.

## Execution discipline

Fix bounded failures, keep unsuccessful trials, run independent confirmation and regenerate affected current outputs. Specialist agents develop evaluators and design alternatives; deterministic workers evaluate numerical samples. Preserve historical receipts against their original source revision. Publish physical acceptance only through the qualification process with measured evidence and review.

```bash
./osr status
./osr build
./osr verify
./osr test
./osr legacy verify
```

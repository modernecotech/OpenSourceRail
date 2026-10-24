# Magnetic research closure and bounded optimisation

The canonical `a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd`
configuration remains unchanged and disqualified. Its retained 3,064 N lift is
below the module's own 4,275 N weight and the 15,371 N allocated AW3 support.
The [original archive](../../../../engineering/assurance/v053-pole-return-research/archive/README.md)
remains intact. The additional executed search below does not supersede those
225 historical case records.

The [closure auditor](../../../../engineering/maglev_research/magnetic_research_closure.py)
first verifies every retained archive byte, then independently checks reported
case counts, mass feedback, winding fill, achieved simultaneous forces, current
density and the constant-current copper heat balance. The derived results retain
four original static passes, fifteen conditional topology-sensitive 1.3 AW3
passes, and zero joint guidance/current-density/thermal passes. Same-network
energy and reciprocity checks do not validate the physical flux allocation.

For the best fitting archived guidance case, at its archived force and mass:

| Requirement | Derived minimum | Existing value |
|---|---:|---:|
| Guidance conductor area at 3.75 A/mm² | 16.744 mm² | 13.4 mm² |
| Guidance pack copper fill at that area | 68.21% | 55% maximum |
| Guidance heat conductance to balance at 120°C | 49.882 W/K | 18 W/K |

These are fixed-load sizing bounds. They omit new copper, winding, cooling,
protection and support mass. They are not a completed redesign or thermal rating;
each physical change requires new accounting and a fresh joint-force solution.

## Additional executed search

The [240-case receipt](magnetic-optimisation.json) records a finite deterministic
search over six pole widths (20–35 mm), five core scales (1.5–2.4), two guidance
turn counts (140/200), two retained pack envelopes, and two flux allocations.
Copper area is derived at 54.9% pack fill, inside the unchanged 55% ceiling.
Every case recounts the complete module and all 24 modules' AW3 mass before
solving simultaneous 1.0 AW3 lift plus 0.1 AW3 lateral force. A separate
1.3 AW3 lift plus 0.1 AW3 lateral point is also retained.

The exact archived model and drivers are reconstructed in a temporary tree.
Original branch-flux and useful-only-pole sensitivity cases are paired, without
editing the canonical source or borrowing the sensitivity's force map for the
original topology. All 240 cases satisfy nominal AABB/fill checks; **zero pass
the combined nominal force/current/field/current-density/thermal screen**.

Ranking minimises the largest normalised nominal constraint ratio, then counted
AW3 mass. Thermal violation uses the heat conductance required at 120°C divided
by the unchanged available conductance, so divergent heat balances still have a
finite, interpretable comparison. The best-ranked cases remain failures:

| Flux allocation | AW3/car | Guide J | Guide cooling needed | Largest violation |
|---|---:|---:|---:|---:|
| Original branch flux | 50.247 t | 7.799 A/mm² | 138.960 W/K | 7.720× |
| Useful-only-pole sensitivity | 49.861 t | 5.201 A/mm² | 49.566 W/K | 2.754× |

This ranking is a research triage result. It does not make the sensitivity's
flux path physically correct, establish real-turn winding clearance or improve
the installed railway. Both examples retain failed adverse-load points.

## Dependency-ordered next work

1. Resolve the leakage/useful flux allocation using an independent nonlinear
   spatial model with counted steel, permanent magnets, four gaps and both
   circuits; retain mesh/domain convergence and force/linkage comparisons.
2. Specify a new guidance pack/heat path from the quantified deficits. Count
   actual conductor routing, enamel, bobbins, manifolds, cooling hardware and
   power, protection and mounting stock before recomputing AW3 demand.
3. Repeat simultaneous lift/lateral sweeps, tolerance/gap/temperature extrema and
   fault reserve. Retain rejected cases and the original-topology controls.
4. Establish R/L/bus voltage, transient control and repeated duty, including core,
   PWM and cooling losses. Correlate physical force and thermal coupons.
5. Bind one surviving exact mass/configuration revision to the dynamics and
   propulsion maps. Adoption and every engineering/physical release gate remain
   open until their own evidence and independent dispositions exist.

## Reproduce

```bash
tools/automation/osr-python -m engineering.maglev_research.magnetic_research_closure
tools/automation/osr-python -m engineering.maglev_research.magnetic_research_closure --optimise build/magnetic-research-followup.json
tools/automation/osr-python -m pytest -q engineering/maglev_research/tests/test_magnetic_research_closure.py
```

The output path must be new to preserve prior executions. Audit does not rerun
the model. Optimisation uses a 180-second subprocess limit, fixed 240-case grid
and frozen archived sources. Its receipt binds the archive manifest, auditor,
worker and exact original model sources. No physical acceptance is asserted.

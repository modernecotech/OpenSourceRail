# Six-car admission and curve optimisation

The [machine-readable audit](dynamics.json) checks the bytes of the retained
current-based six-car packet and all 66 original source files, then extracts the
actual pre-motion blockers. It performs an additional analytical curve-fit
optimisation. It does not rerun the fourteen simulations, revise canonical
configuration `a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd`,
or supply physical acceptance.

## What blocks motion

Twelve cases fail initial support/current/field checks; two fail initial curve or
gap geometry. All fourteen execute zero mechanical steps and earn zero continued
post-fault trajectories. The four-stop authority/current-kernel attempt remains
an executed refusal, with no completed trip.

An important diagnostic distinction is now explicit: the initial inverse solver
attempts up to **270 A**, against the dynamics drive limit of **120 A** (2.25 times
the limit). The reported executed-current peak remains **0 A**, because the plant
never reaches a mechanical/current frame. An attempted, invalid inverse solution
cannot be interpreted as operating performance.

At the dynamics model's 9.81 m/s² gravity, the counted 37,618.592 kg AW3 car needs
**15,376.599 N average support per module**. The retained nominal sample is
**3,041.849 N at 108 A**, leaving **12,334.750 N per module** and a required/sample
ratio of **5.055**. That sample itself fails the current/material map; it is not an
available support rating. These targets differ slightly from the magnetic study,
which uses its own declared gravity and sample current. No proportional-current
or force extrapolation is adopted.

## Bounded geometry optimisation

The source-bound module centres run from −5.5 m to +5.5 m. On a circular guideway,
the exact lateral chord offset at longitudinal position x is
`x² / (R + sqrt(R² − x²))`. With an 8 mm nominal gap and 2–30 mm permitted gaps,
both opposing guide poles require the lateral mismatch to stay within **6 mm**.

For a symmetric rigid array, the best lateral translation lies halfway between
the smallest and largest chord offsets. A yaw term cannot improve this symmetric
minimax fit. The audit searches the exact minimum feasible radius and retains
both the original and optimally translated results.

| Clearance-only result | Original placement | Best lateral recentering |
|---|---:|---:|
| Minimum radius at module centres | 2,520.836 m | 1,250.006 m |
| Maximum mismatch at 300 m radius | 50.421 mm | 25.002 mm |
| Maximum mismatch at 50 m radius | 303.421 mm | 150.460 mm |

Recentring improves the analytical fit, but neither operating curve fits the
6 mm allowance. Increasing current or reducing speed cannot remove this
geometric interference. The next geometry study must compare a larger route
radius against counted articulated/independently steered magnetic mounts or
shorter rigid bands.

For a continuous rigid segment with optimised lateral recentering, the exact
chord-only maximum span is `4 sqrt(R δ − δ²)`, where δ is the 6 mm allowance:
**5.367 m at 300 m radius** and **2.191 m at 50 m radius**. These are theoretical
upper bounds before module length, rotation, tolerance, guideway deformation,
actuator travel, wiring, load-path and capture/brake clearances. They do not
specify an accepted segmentation design or grant free articulation/mass.

## Admission order

The audit publishes a dependency graph so optimisation can stop known failures
before an expensive full-line rerun:

1. Define a revised configuration with complete installed mass, CG, inertia,
   tolerances and protection equipment counted once.
2. Prove same-revision support/guidance maps and actual 144-module static
   equilibrium within current, material and thermal limits. Resolve topology
   and numerical convergence first.
3. Fit magnetic arrays, capture and brakes to route curves, including counted
   mechanisms and structural load paths.
4. Supply same-revision useful propulsion fields, located group phase/R/L/flux,
   electrical transients, receiving braking, repeated thermal duty and
   independently supported reserve operation.
5. Execute current-based continued six-car fault motion with real frame counts,
   energy balances and supported/captured stop outcomes.
6. Compose actual authority/poses through four stops, braking, dwell, charging,
   terminal return and repeated dispatch at the same installed mass and maps.
7. Close measured hardware, target timing, rig and independent G0–G5 dispositions.

The existing [576-task qualification programme](../qualification/README.md)
remains the physical acceptance register. Older ideal-force moving-train results,
zero duties after refusal and independent traffic simulations cannot satisfy the
current-based admission sequence. All engineering/manufacturing/physical release
flags remain false.

## Reproduce

```bash
tools/automation/osr-python -m engineering.maglev_research.dynamics_readiness \
  --output docs/design-engine/ferrite-maglev/research-closure/dynamics.json
tools/automation/osr-python -m pytest -q \
  engineering/maglev_research/tests/test_dynamics_readiness.py
```

The regression suite rejects legacy ideal-force packets, mixed candidate IDs,
promoted initial refusals, out-of-limit initial equilibria, invented completed
trips, missing cases, counterfeit post-fault frames, nonfinite current attempts,
modified retained payloads, original-source drift and incomplete original source
inventories. Fault-current frames and fault ticks require an actual fault
injection; an initial hold cannot earn an executed frame. Current microsteps
must be positive integers, and screen values must be booleans. It also checks the exact
curve bounds and minimax translation against independent chord calculations.

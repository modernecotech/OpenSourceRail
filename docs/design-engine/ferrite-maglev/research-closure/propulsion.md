# Propulsion research closure workstream

This workstream follows the 24 October 2026 review of `d875faec18`. The parent
candidate remains `a79a21a0…`; the separate 8 mm chamfer hypothesis remains
`2ccec6df…`. No archived coupon, current guard, production configuration or
adoption flag is changed.

## Executed repository work

The new [research module](../../../../engineering/maglev_research/propulsion_research.py)
first runs the retained propulsion archive verifier with current-source checks.
It retains all 21 executed coupons and both refused mesh requests, then executes
four electrical fixtures and a bounded 28-case current/duty comparison. Reproduce:

```bash
tools/automation/osr-python -m engineering.maglev_research.propulsion_research --output build/research-closure/propulsion.json
tools/automation/osr-python -m pytest -q engineering/maglev_research/tests/test_propulsion_research.py
```

The electrical fixture solves the phase-amplitude RL equation using each group's
retained resistance, inductance and EMF magnitude. Implicit midpoint integration
balances terminal energy against copper heat, external EMF work and inductive
storage. A 0.2 s, 1,349 A command followed by 0.1 s at zero command uses ideal
model feedforward and proportional current feedback. All four fixtures track the
command without clipping; their absolute energy residuals are below `1e-6 J`.
A voltage-starvation control retains waveform and current-limit failures.

This is a constant-coefficient electrical fixture, with a scalar EMF energy sink.
It does not implement a rotating dq plant, switching inverter, sensor delays,
the Rust current controller, moving overlap or an actual motor transient.
Those engineering acceptance gates remain open.

The comparison searches seven current requests and four pulse lengths. Current
requests of 1,350 A retain the archived exact-limit phasor refusal; 1,400 A is
over-limit. The other cases use the retained linear fixed-field force relation,
the full four-group finite-overlap force, and a steady `EMF + RI + omega LI`
triangle voltage bound. No extra overlap is assigned to the end groups.

For each case, forty pulses repeat every 180 s. The copper-only thermal fixture
solves the declared linear resistance-versus-temperature ODE analytically with
zero cooling, starting at 40°C and stopping at the provisional 120°C screen.
It retains failed cases and never extrapolates beyond the screen. Heat transfer
from magnets, steel, converter and surroundings is unmodelled. Passing this
fixture supplies neither thermal equilibrium nor measured cooling evidence.

Seventeen of the 28 variants pass these conditional coupon screens. Every
variant retains `system_eligible = false`. The ranking is for selecting the
next research coupon; its force-times-duty proxy is not average route thrust.

| Current / pulse | Conditional fixed-pose force | Force-times-duty proxy | Copper temperature after 40 pulses |
|---|---:|---:|---:|
| 675 A / 10 s | 5.050 kN | 280.53 N | 76.32°C |
| 1,349 A / 5 s | 10.092 kN | 280.32 N | 117.32°C |
| 1,200 A / 5 s | 8.977 kN | 249.36 N | 99.56°C |

The lower-current, longer-pulse fixture ranks slightly above the maximum
interior-current fixture on that declared proxy while producing much less
instantaneous thrust. It is not a selected operating design. Actual powered
length, speed and arrival requirements must determine any useful pulse length.

Using the existing canonical comparison mass and inherited resistance proxy,
the 1,349 A sample gives 0.26826 m/s² before resistance and 0.22254 m/s² after
resistance. At the route's 0.2 m/s² request, its residual ideal uphill-grade
allowance is only about 0.230%. This is one-pose necessary-force arithmetic.
The changed hypothesis has no reconciled installed vehicle mass, and the
calculation supplies no route-grade or launch acceptance.

## Dependency-ordered open tasks

| Task | Dependency | Required completion evidence |
|---|---|---|
| P1 — resolve local peaks | Preserve physical 8 mm corners; establish a bounded finer-grid implementation | Independent longitudinal/depth/boundary refinement, asymptotic error evidence and retained failures; a stable fundamental alone is insufficient |
| P2 — qualify field/material domain | P1 and approved material measurements | Full declared temperature/current/gap/phase domain, 3D/end/interacting-iron studies and measured force/loss/demagnetisation correlation |
| P3 — reconcile installed geometry | Exact revised native geometry | Machined PM volumes, retention, tolerances, clearances, support interfaces, weighed mass, CG and inertia |
| P4 — execute actual current control | P2, approved winding topology and changing-overlap map | Actual inverter/RL/controller coupling, current/voltage protection, phase transitions, faults, measured timing and energy closure |
| P5 — execute repeated duty | P3/P4, loss maps and measured cooling | Worst repeated launch/receive duty with all heat sources, thermal equilibrium or bounded mission temperatures, insulation and reserve limits |
| P6 — integrate supported service | Magnetic lift/guidance closure plus P2–P5 | Shared six-car powered-group allocation and the complete four-stop supported electromechanical journey, including receiving/fault cases |
| P7 — independent disposition | P1–P6 and required physical tests | Reviewed exact configuration, manufacturing and operating evidence; no automatic adoption from passing coupons |

The mesh diagnostic currently finds two applicable meshes per sampled temperature.
The cold margin falls by 13.153 kA/m between them; the warm margin falls by
12.239 kA/m. Both remain positive, but longitudinal and depth resolution change
together. An observed asymptotic convergence order is unavailable. Both legacy
`256 × 64` refusals remain in the archive; this work does not relax the existing
mesh-size guard to create an apparent convergence result.

The new tests cover the RL closed-form response and energy identity, voltage
starvation, bounded inputs, resistance-dependent repeated heating, temperature
truncation, retained mesh failures and refused requests. The canonical support
failure continues to block system-level integration regardless of these coupons.

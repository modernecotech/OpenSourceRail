# Station energy-recovery first screen

[Project purpose](../../README.md) · [Research plan](../../docs/design-engine/station-regenerative-launch/README.md)

This deterministic Rust library and bounded JSON executable calculate **ideal
requirements and energy envelopes** for one capture/store/release/coast/boost
event. They do not model physical contact, spring release dynamics, passenger
jerk, coupler loads, storage power, thermal duty or qualified independent brakes.
No speed, train mass, efficiency, headway or installed equipment is selected by
the kernel. The active reference is never changed.

`cargo run --locked --release -p osr-station-energy --bin osr-station-energy` reads one JSON request from
standard input and writes one JSON result. Requests are limited to 8 MiB and
1–10,000 independently identified cases. Unknown fields, duplicate case IDs,
invalid units/domains, nonfinite values and derived overflows reject the request.
Failed physical screens remain completed result rows with explicit reasons.

The wire request is `{"schema":"osr-station-energy-request/1","cases":[...]}`;
the result uses `osr-station-energy-result/1`. `Case` in `src/lib.rs` is the exact,
strict field schema. Every numerical field declares its SI unit. All numerical
inputs are required except the five nullable equipment/braking limits; missing
limits mean unknown capacity. They never mean zero or unlimited proven capacity.

## Model and accounting

- Effective inertial mass includes rotating-equivalent inertia **once**. Physical
  mass separately determines gravity: `m_physical * 9.80665 * sin(atan(grade))`.
  The declared constant resistance and grade apply to capture and departure.
- Controlled capture uses the declared **net** deceleration, `s=v²/(2a)` and
  `t=v/a`. Recoverable brake work is the kinetic-energy drop minus resistance and
  grade work over that distance. Uphill gravity therefore reduces recovery;
  downhill gravity can increase it. A demanded deceleration requiring positive
  drive fails this capture model and receives no recovery credit.
- The unpreloaded linear spring screen is supported only at zero grade and zero
  resistance. Its minimum stroke is `v²/a_peak`, twice the controlled-constant
  distance at the same maximum deceleration. Its capture time is the corresponding
  harmonic quarter period. Outside that domain, the work remains explicitly
  unresolved and no recovered work is credited. No real spring or fatigue life
  is designed. A forward transfer mechanism remains necessary.
- Known insufficient capture stroke or force diverts capture work to the explicit
  unrecovered-braking account. Full storage produces an explicit overflow/dump
  account. Neither case proves independent stopping or a safe dump installation.
- Capture, store and release efficiencies are separate. Conversion, overflow,
  standing and release losses are individually counted. Standing loss is clipped
  at the energy actually present. Reserve energy is protected against release;
  a reserve already lost during dwell is reported as a failed bound.
- `launch_request_j` is **train-side** requested work. Available storage limits
  delivery; insufficient energy creates a shortfall rather than external energy.
  Missing forward transfer or zero release duration blocks positive launch work.
  Initial stored energy is tagged separately from newly captured energy, using
  FIFO attribution of standing loss and release. This is accounting attribution,
  not a claim that mixed energy has physically separate compartments.
- `storage.end_j` is the remaining state for a later event. Reusing the original
  initial state in two rows does not model a shared sequential store. To simulate
  two sequential departures, pass the first ending state into the second input.
  The kernel does not automatically schedule shared storage or other trains.
- `energy_residual_j` balances the **capture plus storage** accounts, including
  explicitly unresolved capture work. It does not combine an assumed successful
  booster with a physically failed event. Coast and booster requirements are
  separately reported. A zero residual is not evidence of physical feasibility.
- `motion.ideal_launch_speed_m_s = sqrt(2*delivered_work/effective_mass)` is a
  **lossless release-energy upper bound**. Finite release duration is used only
  for exclusive-resource occupancy. Release distance, force, jerk and losses
  along a real launch trajectory must be analysed before selecting hardware.
- `booster_offset_m` is an unpowered coast distance; `booster_length_m` is the
  subsequent active **acceleration distance**, not installed motor/winding length.
  A coast that exhausts its energy before the booster fails reachability, and
  booster force/power remain null. Downhill gravity is accounted with its sign.
- A reached booster uses constant net acceleration. Required drive force includes
  resistance and physical-mass gravity. Mechanical power is `F*v`; source power
  and energy additionally divide by declared booster efficiency. These are
  demands, never an available motor-force map. Negative required drive means
  regeneration/braking outside this booster model, not a free energy credit.
- Exclusive resource occupation is assumed to be required capture time + dwell
  + release duration + reset. A negative headway margin fails this single-resource
  assumption. Parallel berths, independent mechanisms and shared-store dispatch
  require a separate resource model.
- Optional independent net braking deceleration produces an **assumed** stopping
  distance for failed capture. This neither sizes all brake hardware nor verifies
  degraded stopping, gradients, reaction time, adhesion, evacuation or recovery.

`necessary_bounds="fail"` reports a known violated bound. Otherwise this first
screen reports `"unknown"` while relevant engineering evidence remains unresolved;
it never treats a missing hardware capability as a passed bound. Every result
separately lists unknown engineering evidence and
keeps `physical_accepted`, `engineering_accepted`, `operating_release` and
`selected_reference_changed` false. Constant-acceleration phase boundaries cannot
establish a finite jerk limit. No result grants native solver admission.

## Independent control

For 160,000 kg effective/physical mass, capture from 5 m/s, level track without
resistance, capture/store/release efficiencies `1,0.7,1`, an initially empty
adequately sized store and a 1.4 MJ launch request, the envelope returns:

- 2 MJ kinetic capture input and 1.4 MJ train-side launch work;
- 4.183300133 m/s ideal recovered launch speed;
- 0.95625 m/s², 153 kN and 3.06 MW **mechanical** peak requirement to reach 20 m/s
  over a 200 m active acceleration distance; traversal time 16.54034 seconds.

20 m/s is one test input, not a requirement. Tests also vary 40, 50, 60 and 72 km/h.
A 200 m **offset** on level track instead adds 47.80914 seconds of ideal coasting
at that recovered launch speed. An already available 1.4 MJ on a 2% uphill coast
is exhausted after approximately 44.62 m, before any rolling/drag resistance.
Capturing on that same uphill also reduces recovery and must not be conflated
with the already-stored-energy control.

Run `cargo test --locked -p osr-station-energy`,
`cargo fmt --package osr-station-energy -- --check`, and
`cargo clippy --locked -p osr-station-energy --all-targets -- -D warnings`.

## Staged arrestor and storage research

The additional `osr-arrestor` binary implements the [G research family](../../docs/design-engine/station-regenerative-launch/README.md).
It uses a separate strict `osr-multistage-arrestor-request/1` contract: bounded
jerk profiles, aggregate or independently pulsed capture, useful storage-energy
windows, rear/front/distributed nominal launch loads and required booster motion.
It does not change the first-screen wire contract above.

Run `cargo run --locked --release -p osr-station-energy --bin osr-arrestor` with
an explicit request on standard input, or use
`python -m engineering.station_energy arrestor-build`, `arrestor-examples`,
`arrestor-run`, `arrestor-verify` and `arrestor-reprice`.
The Python study carries event streams until usable storage state closes or its
eight-solver-event budget expires. Identical positive-gain warm-up arrivals can
be summed analytically with a complete energy ledger and separate event count;
the next Rust event must independently confirm the periodic state. It keeps motion and monetary identities separate;
repricing exact-source cached physics does not execute Rust again. Independent
verification replays the events before publishing.

Store sizing returns active spring/rim material or a declared vessel mass
estimate. Full installed mass remains false. Flat track and zero running
resistance are the staged model's explicit domain; other inputs retain an
unsupported-model result with unresolved energy. Phase coordinates describe a
reference point, not a complete train or safe swept envelope. Required contact,
force, thermal, fatigue, containment, braking, reset and control capability remain
unverified; all release and movement-authority flags stay false.

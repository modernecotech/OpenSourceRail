# osr-maglev-control

Portable fixed-zone ferrite-maglev study core, using Rust `no_std`, no heap
and no external dependencies. It targets simulation and off-the-shelf SBC replay.
Station and located-booster LSM demand is separate from onboard active PM support and guidance. Every computed
output has `physical_output_authorised = false`; the I/O boundary records study
outputs and supplies no current, gate-drive or PWM operation.

`drives` adds a separate local-loop software layer: bipolar support-current PI,
three-phase Clarke/Park transforms and bounded dq current regulation for station
LSM converters. It checks dual current acquisition, phase uncertainty, deadlines,
temperature, DC voltage, protected authority and receiver/resistor readiness.
Faults latch; reset requires fresh healthy zero-demand stopped/secured evidence.
An unavailable support command requests external local fallback; a wayside fault
never requests onboard support shutdown. None of these outputs operates hardware.

The proposed division is SBC supervision/allocation, local MCU current and gap
loops, and independent hardware protection plus support power. The 20 kHz target
is an input, not a measured deadline. `cargo test --locked -p osr-maglev-control
--test drives` runs nine regression tests. `cargo run --locked -p
osr-maglev-control --example winding_replay` emits three actual 4000-frame RL/FOC
coupon replays and fourteen adverse controls. The independent plant uses a
standard-library trigonometric oracle. The 40 A coupon does not qualify a
multi-kA launch converter or close the ideal-force moving-train model.

See the [construction design and counted BOM](../../docs/design-engine/ferrite-maglev/drive-construction/README.md)
for support-coil packages, winding/phase schedules, power-electronics families,
sensing, connections, supplier references and the remaining magnetic/hardware
acceptance gates. No PCB, ADC/PWM adapter, gate-drive or installed timing is released.

The existing `evaluate(previous, inputs, now_ns, params)` API remains a
single-module integer current hypothesis. Its polarity, damping, envelope,
time/replay, stop/reset and support-power tests remain compatible. Increasing an
upward-attraction gap asks for increasing support. The controller cannot be
reused unchanged for shaped-pole passive vertical support.

## 24-module force and moment study

`array::evaluate_array` adds coupled heave, roll, pitch, lateral displacement and
yaw feedback and `array::allocate` distributes requested forces and moments over
24 support stations. This is one rigid car; the complete moving six-car Baghdad
train and a validated six-degree-of-freedom suspension remain open. The array
model has no longitudinal actuator; nonzero longitudinal demand appears as an
unachieved residual. The separate station module supplies an offline LSM demand
screen, without closing physical propulsion/braking, traction/support coupling,
flexible vehicle/beam modes, finite-angle dynamics or contact behavior.

Coordinates use x forward, y left and z up, with the assumed car centre of mass
as origin. Station positions and gaps are metres, force is newtons, moments are
newton-metres, small angles are radians and timestamps are monotonic nanoseconds.
Upward force is positive attraction. Lateral force is positive left. Each moment
is the sum of `position cross force`. The explicit seed geometry is 12 paired
stations at x = -5.5, -4.5, …, 5.5 m and y = ±0.88 m, z = 0 m; this matches the
candidate 12 m magnetic strips. Actual centre of mass, attachment heights,
lever arms, tolerances and dynamic mass properties need physical closure.

Each station has a bounded upward channel and a signed lateral channel. The
illustrative limits are 0–20 kN upward, ±4 kN lateral and 2 MN/s slew per channel.
These numbers are hypothetical force envelopes, **not measured magnetic maps,
current/voltage/thermal limits or proved simultaneous lift/guidance capability**.
A real PM-biased module can retain force after drive loss: a failed station takes
an explicit specified residual force. Zero in the example is an ideal failure
assumption. Unknown failed-channel forces require a separate bounded uncertainty
and protection model before hardware use.

The allocator uses at most 256 bounded coordinate sweeps to minimise squared
force residuals and moment residuals scaled by a declared 6 m lever arm. It
reports the independently reconstructed resultant, residual wrench, constraint
limits and feasibility tolerances. A solver iteration count establishes no
physical deadline. Infeasible requests remain visible; no six-axis success is
inferred from solver completion. Slew limits apply against a prior force frame;
without one the first study allocation has no force history and applies only
static limits. This is not a physical startup or touchdown procedure.

The mode estimator fits a small-angle rigid plane to 24 dual-gap samples and
fits lateral displacement/yaw to 24 dual lateral samples. Every individual gap
and lateral sample is checked before averaging; disagreement, nonfinite values
and degenerate geometry fail. This fit is not a flexible-body observer. Sensor
channels share one supplied acquisition timestamp; per-channel skew, physical
independence, common-cause failure and calibration are not established.
Derivatives use acquisition time. Host time/sequence checks reject stale,
future, replayed, regressing and late frames.

A stop request preserves fresh bounded support. A station failure, active bound or infeasible
allocation latches a traction stop while available ideal support remains active.
Missing valid sensing or power requests external local fallback, never frozen
study forces. A prior fault inhibits traction until a fresh healthy frame,
reported stopped/secured conditions and reset coincide. Capture, fallback,
independent protection energy and secure-condition verification need separate
engineering; they are not supplied by these Boolean reports.

## Reproducible offline checks

Run:

```sh
cargo test -p osr-maglev-control
cargo clippy -p osr-maglev-control --all-targets -- -D warnings
cargo run -p osr-maglev-control --example sbc_replay
cargo run -p osr-maglev-control --example multimodule_replay
```

The array replay integrates ten seconds of virtual 1 ms frames, prints CSV at
500 ms intervals and asserts feasibility and a final small five-mode error. Its
27,750 kg AW2 mass is a retained numerical comparison: 18,750 kg tare plus
120 × 75 kg passengers. The current station-powered design instead targets
14,200 kg tare; this retained control case is not the new vehicle mass closure. Gains, diagonal inertias, force limits and instantaneous actuator
response are synthetic. It starts with coupled displacement/tilt, commands a
stop at 0.5 s and loses station 0 at 1 s under a specified zero-residual failure
hypothesis. It keeps fresh support and the stop latch active. This trajectory
is a numerical example, not a closed-loop stability or ride-quality proof.

`ideal::IdealPlant` integrates a constant wrench exactly within each small-angle
step. Tests independently check uniform equilibrium (272,227.5 N weight), moment
signs, force/moment reconstruction, five-component demand, failed-force
redistribution, capacity and slew infeasibility, all-failed residuals, sensor and
time rejection, support-preserving stops and secure reset. Mechanical interface
power agrees with resultant wrench power, and one-step work agrees with change
in kinetic plus gravitational energy. These conservation checks validate the
ideal mechanics arithmetic, not actual magnet energy or electrical losses.

`io::StudyIo`, `host_tick` and `ReplayIo` define an acquisition/record boundary
without owning an OS clock or hardware. Recording/acquisition failures return
to the host; the host must engineer its local fallback. Repeated single-frame
stub reads are rejected as replay. No scheduler, GPIO, ADC or network transport
is validated, and this example measures neither SBC timing nor I/O latency.

Physical gates remain open: calibrated nonlinear magnetic force/loss maps over
gap/current/temperature and shared flux, identified electrical/thermal and
mechanical dynamics, actuator failure residuals, independent sensors/protection,
measured end-to-end target timing, multi-module rigs, flexible guideway and loaded
vehicle tests, braking/capture and train/route acceptance. No operational or
manufacturing authority is inherited from the numerical study.

## Flexible guideway numerical demonstrator

`coupled_bridge` connects this exact array core to the separately labelled Python
beam demonstrator in `engineering/ferrite_maglev/coupled.py`. From the repository
root, run:

```sh
cargo build -p osr-maglev-control --release --example coupled_bridge
.venv/bin/python -m engineering.ferrite_maglev.coupled --duration-s 3
.venv/bin/python -m pytest -q engineering/analysis/tests/test_ferrite_maglev_coupled.py
```

The Python host sends all 24 **local relative gaps** each virtual millisecond.
Rust returns bounded support forces, which load a 25 m simply supported
Euler–Bernoulli beam; its local displacement feeds the next sensor frame. This
is two-way offline coupling, with no physical output. The beam assumes
the current configured section and native quantity-derived line mass, with 2% modal damping, retaining
six vertical modes of a 50-element consistent-mass model. Independent point-load
closed forms check static response; analytical pinned-beam frequencies and
virtual-work/undamped-energy checks control the numerical implementation.

The model can show global beam displacement exceeding 8 mm while the car follows
that displacement and the **relative** gaps remain inside the example's study
envelope. This establishes neither a gap requirement nor structural acceptance.
It omits dead-load camber, torsion/corbel flexibility, moving/train loads,
flexible car structure, soil, joints, fatigue, real magnetic/electrical dynamics
and independent protection. The line protocol accepts at most 20,000 frames,
8 KiB per frame, and measures no hardware timing. The three-mode car motion and
vertical beam coupling do not provide a six-degree-of-freedom stability proof.


## Offline evacuation sequencing

`egress::evaluate` adds allocation-free doorway sequencing with an exact declared
candidate/door context, fresh monotonic frames, explicit readiness/assistance
prerequisites, latched contradiction/context/deadline faults, and secured/stowed
reset. It reports study traction inhibition and continued-support obligations;
it supplies no door, restraint, chute or support output adapter. Input assertions
are unauthenticated study facts, not verified independent sensor or safety evidence.

`cargo run -p osr-maglev-control --release --example egress_replay -- REVISION PATH_CLEAR HEIGHT_COVERED`
prints a bounded nine-frame synthetic sequence. The linked Python study supplies
its candidate tag and calculated hypothetical path/height gates, and retains
negative controls. Loss of prerequisites after deployment begins holds the
sequence; no automatic retraction is commanded. The egress/support composition
test preserves fresh support control while inhibiting traction. Physical timing,
independent protection, accessible passenger evacuation and railway approval remain open.


## Station launch and receiving study

`station` evaluates bounded offline launch, coast, receive and secured modes.
It checks exact configuration/zone identity, fresh monotonic frames, phase
uncertainty, reservation assertions, magnetic-band overlap and assumed current,
voltage and thermal limits. Coast demands zero station thrust. Receiving braking
requires the declared brake resistor to be ready. Receiver loss after commitment
requires independent stopping/recovery; clearing a Boolean drive demand does not
stop an already coasting train.

```sh
cargo run --locked -p osr-maglev-control --example station_replay
./osr design protocol
```

The scalar force/current relation, winding R/L/flux and voltage/loss calculations
are explicit hypotheses. They are not measured motor maps, three-phase hardware
commutation, shared support/thrust qualification or a six-car electromagnetic
simulation. An external `launch_committed` assertion is not an authenticated
interlocking or detector record. Persistent corridor/berth ownership is exercised
separately in `osr-interlocking`; permission expiry cannot release a committed
train, and full-consist clearance is required. No physical output adapter or
railway operating authority is supplied.

The longer-corridor study (`./osr design corridor`) separately evaluates urban
2 km and suburban 5 km profiles, finite station/booster overlap and electrical
rating alternatives. A booster is a nonpassenger powered asset; junctions are
passenger transfers between independent fixed lines. The 1 km station replay
remains a component benchmark. Its passing result cannot clear longer-profile
voltage, service-energy, recovery, section-handover or exclusive-reservation
capacity holds.

## Adaptive research tuning

`./osr design iterate` varies bounded proportional and damping gains alongside
vehicle mass allocations and guidebeam sections/spans. The bridge accepts mass
and gain scales as optional command arguments; nonfinite or out-of-bound scales
are rejected before processing frames. Exact revisions face separate confirmation
scenarios and replay/excess-gap negative controls. This offline tuning establishes
neither measured magnetic response nor stability over the full operating envelope.

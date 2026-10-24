# Delayed-map normal-wrench Rust research prototype

<!-- osr-system-context:start -->
OpenSourceRail develops an open, locally buildable urban railway with fixed linear motors at stations and, where needed, located boosters. Trains coast between powered zones while onboard ferrite support, guidance and passenger services remain independently powered; passengers transfer between fixed lines at junctions. Simple vehicles, repeated civil works and repairable local production aim for high useful passenger throughput and affordable construction, operation and debt repayment. Current studies and digital workflows support development; an accepted physical railway has not been established.

[Project introduction](../../../README.md) · [Engineering approach and current status](../README.md)
<!-- osr-system-context:end -->

This standalone Rust package computes an offline candidate normal-force correction
for the six-car station-powered ferrite-maglev research model. It ports the Python
normal-wrench observer and minimum-norm module allocation. It has its own workspace
and lockfile, no dependencies, and no hardware, network or device commands. Its
outputs always carry `physical_output_authorised = 0`.

The library and tests do **not** establish an integrated full-journey result,
physical calibration, safety certification or real-time performance. The current
campaign's source identity changes only when its owner deliberately incorporates
this package and reruns that campaign. This package itself changes neither the
primary Rust workspace nor the product configuration.

## Calculation and scope

Each powered group supplies six flux-linkage amplitudes ψ (Wb), phases θ (rad),
world overlap positions (m), and an accepted alpha/beta current pair (A). The
previous accepted car speeds and centres are used. For car c and group g:

```
angle = theta[g,c] + k * previous_speed[c] * 0.001
local_real_current = I_alpha[g]*cos(angle) + I_beta[g]*sin(angle)
normal_force[g,c] = 1.5*k*psi[g,c]*local_real_current
wrench[c] = [sum(normal_force), 0,
             -sum(normal_force*(overlap_position-previous_car_centre))]
scaled_wrench = estimator_scale*wrench
correction = -M.T * inverse(M*M.T) * scaled_wrench
```

`M` has rows `[1, y, -x]` for 24 modules, at x = −5.5…5.5 m in 1 m steps and
y = ±0.88 m. Symmetry makes the Gram matrix diagonal: `[24, 18.5856, 286]`.
Roll disturbance is zero in this model; the allocator is separately tested with
nonzero roll. The returned request is `desired_support + correction`. It must
remain within the research screen 0…20,000 N for every module. No clipping or
direct force application occurs. The subsequent inverse-NI, voltage/current
controller and RL/mechanical plant are outside this package.

The observer is unfiltered. Its virtual field map uses the same phase/gap model
as the research plant; that calibration is unqualified. This is a previous-frame
estimate, not an independent physical sensor. The ±10% scale cases (0.9, 1.0,
1.1) are supported, but all three full journeys still need to be run in the
integrating campaign. A virtual 1 ms age check does not qualify actual sensing,
communication latency, worst-case execution time or clock synchronisation.

## Refusal and state contract

`observe(&ObserverInput)` is a safe, side-effect-free Rust API.
`osr_research_normal_wrench_v1(ObserverInput)` is the by-value C ABI, with the
matching header under `include/` and a stdlib `ctypes` binding under `python/`.
No raw pointers or unsafe memory operations are used. The only narrowly allowed
unsafe attribute exports the unique C symbol; numeric code retains the deny lint.

The caller supplies a nonzero 32-byte configuration SHA256, exact group count
(1…200), positive finite k, one of the three scales and a 1,000,000 ns step. The
first frame has sequence 1 and no observation; it produces a zero estimate.
Subsequent frames require monotonically consecutive sequences and exact virtual
time increments, an observation from the immediately previous accepted sequence
and timestamp, and the exact configuration identity and group count. Changing
any configuration field midway requires a fresh explicit state/context.

All active field/current/speed/position channels must be finite, even where ψ is
zero. Negative ψ, overflow, stale/future/missing samples, malformed shape, replay,
clock inconsistency and invalid support requests cause a hold. A refusal returns
nonzero status, unchanged state and zero numeric output. The Python binding also
rejects integer wrapping and incorrect shapes before crossing the ABI. It raises
`ObserverRefusal` and advances its stored state only on success.

The hash comparison is a consistency check. This library cannot authenticate the
caller, its configuration or its claims about accepted sensor/current samples.
It cannot prevent a caller deliberately resetting state. Those responsibilities
belong to the enclosing controlled test or future qualified runtime.

## Reproduction

From the repository root:

```sh
cargo fmt --manifest-path engineering/ferrite_maglev/observer-prototype/Cargo.toml -- --check
cargo clippy --locked --manifest-path engineering/ferrite_maglev/observer-prototype/Cargo.toml --all-targets -- -D warnings
cargo test --locked --manifest-path engineering/ferrite_maglev/observer-prototype/Cargo.toml --all-targets
python3 engineering/ferrite_maglev/observer-prototype/tests/differential.py
```

The differential test builds the release cdylib and compares the retained Python
fixture plus 64 seeded finite/adverse vectors at all three scales. Its independent
stdlib oracle uses complex rotation and general pivoted 3×3 elimination, rather
than the Rust allocation's closed form. It checks every wrench, module correction,
support request and force/torque balance. The retained fixture has an explicit
historical source/function digest; it is virtual research evidence, never an
accepted physical measurement. Rust unit tests cover analytical controls and
refusal/no-state-advance paths. C/ctypes layout checks bind the by-value ABI.

`OSR_OBSERVER_TARGET_DIR` optionally places differential-test build products in
another directory. Nested `target/` is ignored. A normal Cargo build has no
default features or dependencies to disable.

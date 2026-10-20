# osr-maglev-control

Portable v0.5 maglev study core, using Rust `no_std`, integer units and no heap or
external dependencies. It targets simulation and off-the-shelf SBC replay first.
There is no physical output adapter or qualified deployment controller.

`evaluate(previous, inputs, now_ns, params)` produces a hypothetical single-module
current command, traction permission and a support response. Larger upward-
attraction gaps demand greater current. Gains and bias are synthetic in the
example; a selected magnetic circuit and identified plant must determine them.
This model cannot be reused unchanged for shaped-pole passive vertical support.

The tests cover polarity, damping sign, bounds/saturation, independent checks of
both sensor envelopes, stale/future/replayed frames, missed ticks, faulty sensors,
support-power loss, drive faults and stopped/secured reset. A traction stop keeps
fresh support control active. Missing valid sensing requests local fallback; no
stale current is latched as a supposed safe suspension controller. The independent
fallback, power architecture and capture response remain engineering work.

Run `cargo run -p osr-maglev-control --example sbc_replay`. It uses a virtual
sequence of timestamps and reports physical-output permission as false on every
tick. It measures neither SBC scheduling nor I/O timing. The crate is not connected
to wheel-based traction or braking evaluators and inherits no acceptance from them.

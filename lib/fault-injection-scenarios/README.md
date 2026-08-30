# Fault-injection scenarios

Reference simulation scenarios that stage specific failure modes for exercising the safety-critical subsystems. Each file is a **complete scenario** (currently built on top of the Samawah network in `cities/catalogue/west-asia/Iraq/Samawah/samawah.toml`) with an additional `[[faults]]` / event-schedule section that the sim replays against the network.

| File | RFC | What it exercises |
|---|---|---|
| [`dust-storm.toml`](dust-storm.toml) | [RFC 0002](../../docs/rfcs/0002-energy-sizing.md) §5.4 + [RFC 0001](../../docs/rfcs/0001-track-state-consensus.md) §8 | AM-peak dust storm with PV derating + late-afternoon depot grid outage — tests degraded-mode energy operation. |
| [`obstacle-fault.toml`](obstacle-fault.toml) | [RFC 0015](../../docs/rfcs/0015-driverless-operation.md) | Staged onboard sensor failures — LIDAR offline, ultrasonic stale, peer 2oo2 disagreement, LIDAR+radar offline at mainline speed. Validates the five O-series SIL-4 properties of `osr-obstacle-detect`. |
| [`wayside-intrusion.toml`](wayside-intrusion.toml) | [RFC 0016](../../docs/rfcs/0016-wayside-track-intrusion.md) | Three staged section-intrusion events (Present, Unknown, Present) on Samawah Line 1 — validates the interlocking's gate (d) `section_intrusion_permits` check prevents MA issuance on non-Clear sections. |

## Current status

These scenarios are **Samawah-based full scenarios** — they replicate the whole Samawah network in-file, then append the fault schedule. A future refactor should decompose each into a small overlay (just the `[[faults]]` + schedule sections) that can be merged on top of any city's base scenario, so the same fault fixtures exercise e.g. the Baghdad network. Until then, re-running the fault scenarios against a different city means copying the base scenario's content in.

## Running

```
cargo run --release --bin osr-sim -- \
    --config lib/fault-injection-scenarios/dust-storm.toml \
    --duration 54000 --status-every 3600
```

End-of-run summary prints per-fault tick counts under the scenario's safety-subsystem monitors.

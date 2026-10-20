# Rust Workspace

The `crates/` tree is the OpenSourceRail software stack. It contains
the simulator, safety evaluators, onboard and wayside services,
operator GUIs, design synthesis tools, and evidence generators.

The primary v0.5 control implementation is [`osr-maglev-control`](osr-maglev-control/README.md), with fixed magnetic modules, linear electromagnetic propulsion and offline SBC replays. [deployment/maglev.toml](../deployment/maglev.toml) defines its development profile; no old host image or wheel/rail control result is inherited.

## Primary Commands

```bash
cargo test --locked -p osr-maglev-control --all-targets
cargo check --locked -p osr-maglev-control --no-default-features
cargo run --locked -p osr-maglev-control --example multimodule_replay
./osr test
```

The remaining crates provide shared platform functions and retained wheel/rail references. Use `./osr sim legacy`, `./osr design legacy` and `./osr test legacy` for explicit comparator workflows. Wheel-specific traction, braking, odometry, axle and points logic requires replacement or interface revalidation.

## Shared and Retained Groups

| Area | Crates |
|---|---|
| Shared foundations | `osr-core`, `osr-proto`, `osr-crypto`, `osr-secbus`, `osr-supervision-contract`, `osr-lifecycle-identity` |
| Signalling and wayside safety | `osr-consensus`, `osr-interlocking`, `osr-wayside-points`, `osr-level-crossing`, `osr-intrusion-detect`, `osr-hot-axle-wayside` |
| Reference process hosts | `osr-runtime` (development target; qualification pending) |
| Onboard safety | `osr-atp`, `osr-onboard-routing`, `osr-odometry`, `osr-brake`, `osr-bms`, `osr-door-control`, `osr-fire-safety`, `osr-derailment`, `osr-obstacle-detect` |
| Train systems | `osr-tcms`, `osr-ato`, `osr-traction`, `osr-aux-power`, `osr-hvac`, `osr-lighting`, `osr-regen`, `osr-tcn`, `osr-t2g`, `osr-event-recorder`, `osr-cbm-onboard` |
| Stations and passengers | `osr-afc`, `osr-afc-backoffice`, `osr-pis-onboard`, `osr-pis-station`, `osr-psd`, `osr-station-scada` |
| Simulation and design | `osr-sim`, `osr-design`, `osr-alignment`, `osr-routing`, `osr-analytics`, `osr-energy-site`, `osr-balise`, `osr-tvm` |
| Operator tooling | `osr-gui-shared`, `osr-sim-gui`, `osr-occ-gui`, `osr-occ`, `osr-historian` |
| Evidence and images | `osr-safety-case`, `osr-selftest`, `osr-trainset-image`, `osr-cbm-backend` |

The architecture rationale is in
[`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md), with the crate-level
software map in
[`docs/rfcs/0005-sbc-software-architecture.md`](../docs/rfcs/0005-sbc-software-architecture.md).
The evidence-backed maturity review and executed integration plan are in
[`docs/rust-codebase-review-and-integration-plan.md`](../docs/rust-codebase-review-and-integration-plan.md).

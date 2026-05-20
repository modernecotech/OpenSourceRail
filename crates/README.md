# Rust Workspace

The `crates/` tree is the OpenSourceRail software stack. It contains
the simulator, safety evaluators, onboard and wayside services,
operator GUIs, design synthesis tools, and evidence generators.

## Common Commands

```bash
cargo test --workspace
cargo run --release --bin osr-sim -- --duration 3600 --status-every 300
cargo run --release --bin osr-design -- --help
```

## Main Groups

| Area | Crates |
|---|---|
| Shared foundations | `osr-core`, `osr-proto`, `osr-crypto`, `osr-secbus` |
| Signalling and wayside safety | `osr-consensus`, `osr-interlocking`, `osr-wayside-points`, `osr-level-crossing`, `osr-intrusion-detect`, `osr-hot-axle-wayside` |
| Onboard safety | `osr-atp`, `osr-odometry`, `osr-brake`, `osr-bms`, `osr-door-control`, `osr-fire-safety`, `osr-derailment`, `osr-obstacle-detect`, `osr-vigilance` |
| Train systems | `osr-tcms`, `osr-ato`, `osr-traction`, `osr-aux-power`, `osr-hvac`, `osr-lighting`, `osr-regen`, `osr-tcn`, `osr-t2g`, `osr-event-recorder`, `osr-cbm-onboard` |
| Stations and passengers | `osr-afc`, `osr-afc-backoffice`, `osr-pis-onboard`, `osr-pis-station`, `osr-psd`, `osr-station-scada`, `osr-dmi` |
| Simulation and design | `osr-sim`, `osr-design`, `osr-alignment`, `osr-routing`, `osr-analytics`, `osr-energy-site`, `osr-balise`, `osr-tvm` |
| Operator tooling | `osr-gui-shared`, `osr-sim-gui`, `osr-occ-gui`, `osr-occ`, `osr-historian` |
| Evidence and images | `osr-safety-case`, `osr-selftest`, `osr-trainset-image`, `osr-cbm-backend` |

The architecture rationale is in
[`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md), with the crate-level
software map in
[`docs/rfcs/0005-sbc-software-architecture.md`](../docs/rfcs/0005-sbc-software-architecture.md).


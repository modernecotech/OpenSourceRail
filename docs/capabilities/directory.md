# Primary maglev capability directory

Implemented digital capabilities for v0.5. Every engineering/physical acceptance gate remains open.

| Capability | Entry | Implemented scope |
|---|---|---|
| [city-planning](../../engineering/ferrite_maglev/cities.py) | `./osr city baghdad` | Separate maglev formation, fleet, duty, charging and partial cost planning; no route acceptance. |
| [system-search](../../engineering/ferrite_maglev/optimisation.py) | `./osr design run` | Vehicle/beam/span sensitivities and indexed allowances; complete costs and full coupling remain open. |
| [native-geometry](../../engineering/ferrite_maglev/geometry.py) | `./osr design native` | Partial magnetic interface and civil-bay native solids; not complete production geometry. |
| [beam-only-egress](../../engineering/ferrite_maglev/evacuation.py) | `./osr design evacuation-native` | Beam-only geometry and chute envelope/height screens; no evacuation approval. |
| [field-equations](../../engineering/ferrite_maglev/field.py) | `./osr design run` | 2D field equation controls; coupon force convergence and qualified force/loss maps remain open. |
| [rust-control](../../crates/osr-maglev-control/Cargo.toml) | `cargo test --locked -p osr-maglev-control --all-targets` | Fixed-module Rust control and advisory egress logic; no physical output authority. |
| [coupled-replay](../../engineering/ferrite_maglev/coupled.py) | `./osr design coupled` | Two-way virtual Rust/vertical-beam replay; no qualified vehicle dynamics. |
| [linked-development](../../engineering/ferrite_maglev/system_development.py) | `./osr design system` | Partial entry/support geometry, stage demands and geometry-bound software replays. |
| [dependency-runner](../../engineering/ferrite_maglev/workflow.py) | `./osr build` | Restartable build of implemented studies; missing evaluators and acceptance remain open. |
| [primary-ui](../../tools/automation/maglev-workbench.py) | `./osr workbench` | Read-only primary design UI, city plans, images and visibility videos; no hardware commands. |
| [development-host](../../deployment/maglev.toml) | `tools/automation/osr-python tools/automation/validate-host-manifests.py` | Offline SBC development profile; no deployed host image or physical timing qualification. |

Selected city rebuild: `./osr catalogue run --city <slug>`.

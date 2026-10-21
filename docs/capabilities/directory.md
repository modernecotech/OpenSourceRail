# Primary maglev capability directory

Implemented digital capabilities for v0.5. Every engineering/physical acceptance gate remains open.

| Capability | Entry | Implemented scope |
|---|---|---|
| [city-planning](../../engineering/ferrite_maglev/cities.py) | `./osr city baghdad` | Separate maglev formation, fleet, duty, charging and partial cost planning; no route acceptance. |
| [system-search](../../engineering/ferrite_maglev/optimisation.py) | `./osr design run` | Vehicle/beam/span sensitivities and indexed allowances; complete costs and full coupling remain open. |
| [adaptive-search](../../engineering/ferrite_maglev/iteration.py) | `./osr design iterate` | Result-guided vehicle/beam/Rust gain variants and separate holdout confirmation; research recommendation only. |
| [station-propulsion](../../engineering/ferrite_maglev/station.py) | `./osr design station` | Jerk-limited launch/coast/receive, actual-band overlap, headway and corrected services charging; no qualified motor map. |
| [gfrp-civil-product](../../engineering/ferrite_maglev/station_structure.py) | `./osr design structure` | Panel/civil quantity, finite-dipole reference and production-target studies; no manufactured release. |
| [station-protocol](../../engineering/ferrite_maglev/station_protocol.py) | `./osr design protocol` | Executed Rust station replay and durable atomic launch tests; local offline domain only. |
| [moving-six-car](../../engineering/ferrite_maglev/moving_train.py) | `./osr design moving` | Moving six-car ideal-force Rust/beam/coupler studies, refinement and motion animation; physical qualification open. |
| [integrated-station](../../engineering/ferrite_maglev/system_campaign.py) | `./osr design campaign` | Actual local interlocking-to-station control, full-tail ownership, fault cases and independent recovery sizing. |
| [fixed-powered-corridors](../../engineering/ferrite_maglev/corridor.py) | `./osr design corridor` | Finite station/booster urban/suburban trajectories, actual offline Rust control and moving confirmations; electrical, reserve and capacity holds remain explicit. |
| [interchange-hubs](../../engineering/ferrite_maglev/interchange_hubs.py) | `./osr design interchange-hubs` | Bounded Baghdad hub, accessible connector and realignment alternatives; unchanged default and unqualified costs, capacity and sites remain explicit. |
| [booster-recovery-kit](../../engineering/ferrite_maglev/booster_kit.py) | `./osr design booster-kit` | Counted powered-zone mounts and independently equipped recovery alternatives with foundations, energy, mass and unquoted costs. |
| [booster-recovery-native](../../engineering/ferrite_maglev/booster_native.py) | `./osr design booster-native` | Reopened partial booster/rescue stock solids, native mesh, image and visibility video; not a qualified assembled installation. |
| [manufactured-dossier](../../engineering/ferrite_maglev/closure.py) | `./osr design dossier` | Counted frame/connection/handling/prestress/bearing/brake/foundation candidates and all-obligation evidence map; no release. |
| [manufactured-native](../../engineering/ferrite_maglev/manufactured_native.py) | `./osr build` | Reopened native frame cut-stock and connection details with quantities and visibility media. |
| [station-native](../../engineering/ferrite_maglev/station_native.py) | `./osr build` | Actual FreeCAD/STEP, PNG and visibility video for partial GFRP/civil material stock. |
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

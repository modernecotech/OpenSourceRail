# Pilot development assurance profiles

Exact development execution; engineering, delivery and formal profiles are separate. No SIL, hardware, site or operational acceptance.

| Profile | Digital execution | Commands |
|---|---|---:|
| engineering | hold | 0 |
| delivery-lifecycle | executed-current | 3 |
| control-formal | executed-current | 5 |

Run an explicit profile with `./osr assurance run <profile>`.
Opening/verifying this packet only checks retained evidence. Failed or stale runs cannot become a current pass. Build current design packets before an engineering profile; its pending hold is published before readiness tests. Run `./osr build` after successful profiles to refresh their completed presentation.

The project assurance graph traces current engineering, delivery and control claims to source. Source traceability, executed verification and independent acceptance are separate gates.

Physical gates: measured magnetic maps, target timing and EMI, site/ground and utilities, fire and evacuation, supplier qualifications, independent engineering and authority acceptance.

Compile the whole pilot evidence graph with `cargo run --locked -p osr-safety-case -- engineering/ferrite_maglev/data --evidence-root . --results docs/design-engine/ferrite-maglev/assurance-profiles/results.toml`. The physical-protocol branch remains unverified and every independent acceptance remains open.

[Kani usage and harness selection](https://model-checking.github.io/kani/usage.html) · [Loop bounds and unwinding assertions](https://model-checking.github.io/kani/tutorial-loop-unwinding.html).

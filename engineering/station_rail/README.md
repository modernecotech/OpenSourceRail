# v0.6 station-powered freewheeling rail

This package develops the [selected v0.6 research candidate](../development-baseline.toml): six comfort cars, passive two-axle bogies, conventional rail/concrete guideway, station LIM primaries and onboard passive aluminium secondaries. No traction motor, traction battery or suspension magnet is fitted. Independent service energy, brakes, ATP and recovery remain necessary.

`brief.toml` owns requirements and declared hypotheses. `vehicle` counts retained and revised assemblies; `civil` compares three structural families; `operations` solves required longitudinal forces and finite station geometry; `electrical` assesses service charge and secondary heat. `evaluation` composes readiness; `exports`, `publication` and `reader` compile consistent research records. `controls` executes the actual Rust wheel-interface predicates and inherited ATP regressions. `cities` preserves geographic inputs and holds numerical city regeneration.

A reachable analytical profile is not available motor thrust or a qualified journey. Missing source data, equipment location, structural qualification, thermal performance and prices remain explicit. [Current results](../../docs/design-engine/current/README.md) · [Project introduction](../../README.md) · [Roadmap](../../docs/ROADMAP.md).

The [native follow-up](../../docs/design-engine/v06-physical-closure/README.md) uses `station_motor` and `long_motor` for actual current-excited primary geometry, `braking` for reduced force-driven Chrono cases and counted rotor inertia, and `body_frame`, `body_solid_frame` and `body_floor_fit` for connectivity, benchmarked frame calculations and actual floor cutouts. `motor_review` keeps necessary winding arithmetic separate from circuit validation. `closure_artifacts` indexes omitted raw fields; `closure_round` publishes failed/unknown results without changing the default geometry.

```bash
.venv/bin/python -m engineering.station_rail.closure_round --verify
```

Native workers require a fresh output directory, the pinned GetDP/Chrono environments, Gmsh, CalculiX and FreeCAD. Call `station_motor.run(output)` and `long_motor.run(output)` from the project Python; call `braking.native_run(output, vehicle.build(), dt_s=.005)` from the Chrono Python. `body_solid_frame.run(output, vehicle.build())` and `body_floor_fit.run(output, vehicle.build())` execute the native structural and fit-up experiments. Raw package verifiers check original sources; compact archive verification only checks its declared retained bytes.

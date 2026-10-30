# OpenSourceRail v0.4 application workspace

This is a source-pinned restoration of the v0.4.0 City Studio, time-stepped simulator, Sim GUI, OCC GUI, component libraries, and their Samawah example project. The application and component sources come from commit `205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e`; the nested `Cargo.toml` and `Cargo.lock` retain their v0.4 workspace identity. The [source manifest](source-manifest.json) records blob IDs, sizes and SHA-256 hashes for all 468 restored source/data files; one RFC has a documented trailing-whitespace-only cleanup. `python tools/automation/verify_legacy_v04.py` checks the copy and manifest. The current v0.6 workspace does not depend on this directory.

These tools preserve the earlier maglev-era physical and software models. They are available for historical project editing and reproduction; their vehicle, propulsion, service, costs, and simulation outcomes do not transfer to the selected v0.6 wheel/LIM candidate. They do not provide operating authority or physical qualification.

Run from this directory so project and data paths resolve to the retained Samawah fixture:

```bash
cargo run -p osr-city-studio -- validate
cargo run -p osr-city-studio -- serve
cargo run -p osr-sim-gui
cargo run -p osr-occ-gui -- --auto-attach
```

The OCC application is a read-only historical simulator console; its controls are rehearsal stubs as documented in the original crate. `cargo test --locked -p osr-city-studio --all-targets` checks the city compiler and review workflow. `cargo test --locked -p osr-sim -p osr-sim-gui -p osr-occ-gui --lib` checks the simulator and GUI contracts. The main CI runs both targeted checks independently from the current v0.6 Rust workspace.

The full v0.4 source remains available at its original pinned [release commit](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e); this restoration retains the application workspace and Samawah fixtures needed to run these tools without checking out that historical revision.

# osr-sim-gui — simulator GUI (RFC 0018)

Pure-Rust egui front-end for `osr-sim`. Loads a scenario, runs the
sim once to completion, builds a 1 Hz [`SimTimeline`](../osr-sim/src/timeline.rs),
then animates the run at arbitrary playback speed.

## Features (v1)

- Scenario selection via `--scenario <path>` flag (or the Samawah
  built-in default).
- Play / pause / reset + 0.5× / 1× / 10× / 60× speed controls.
- Timeline scrubber (drag to any second).
- Network schematic with trains coloured by phase (traveling /
  dwelling / charging / SoC-warning).
- Click-to-inspect sidebar with line, phase, `station_m`, SoC, and
  last-event details.
- Event log with per-kind filter checkboxes (dispatched, arrive,
  depart, charging, turnaround, SoC warning).
- Fault-active badges for every `[[faults]]` entry that's firing at
  the current playback time.
- Embedded evidence for TCMS trip movement holds, event recording, CBM,
  hot-axle, and T2G primary/backup/offline operation.
- IEEE 1588 acquisition and lock evidence for the shared simulation clock.
- Station and wayside evidence for PSD, PIS, SCADA, and intrusion detection.
- Physical HABD passage, trip, latched-stop, and inspected-reset evidence.
- Depot evidence for radio-delivered CBM, history, analytics, and work orders.

## Run (native)

```bash
cargo run --release -p osr-sim-gui
# or with a specific scenario
cargo run --release -p osr-sim-gui -- --scenario designs/west-asia/Iraq/Samawah/samawah.toml
```

## Run (WebAssembly)

The same code ships as a WASM app. Build + serve with
[trunk](https://trunkrs.dev):

```bash
rustup target add wasm32-unknown-unknown
trunk --version # must report trunk 0.21.8
cd crates/osr-sim-gui
trunk serve web/index.html --open
```

The HTML file at [`web/index.html`](web/index.html) pulls the
crate's library target, builds it to WASM with `wasm-bindgen`,
loads it into the `<canvas id="osr_sim_canvas">`, and the same
`SimApp` runs inside a browser tab.

From the repository root, `npm run test:frontend` builds this release bundle
and verifies it in pinned Playwright Chromium.

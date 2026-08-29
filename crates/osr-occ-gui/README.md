# osr-occ-gui — operations-control dispatcher console (RFC 0018)

Pure-Rust egui front-end for the OCC. v1 ships as a read-only
console that attaches to a pre-recorded sim run for demonstration;
v3 (per RFC 0018 §9) wires live consensus + RFC 0017 signed action
emission.

## Features (v1)

- Live-style playback (speed controls 1× / 10× / 60×) against a
  pre-recorded sim run.
- Network schematic with per-section intrusion overlays (Present /
  Unknown colour-coded per RFC 0016).
- Train panel listing every in-service trainset with phase + SoC.
- Embedded telemetry roll-up from the attached deterministic recording:
  TCMS trip movement holds, CBM service flags, and T2G channel/transmission
  counts.
- IEEE 1588 acquisition and lock evidence from the same recording.
- Station/wayside roll-up for PSD states, controller ticks, and intrusion
  verdict transitions.
- Physical HABD passage, warning restriction, trip, active-stop, and
  inspected-reset evidence.
- Balise registry, accepted odometry fixes, and sighting-audit findings.
- Depot roll-up for received CBM payloads, historian samples, analytics, and
  maintenance work orders.
- Alert feed (info / warn / crit) with category filter checkboxes,
  pre-seeded with SoC-warning alerts harvested from the recorded
  run and dispatcher-action entries.
- Dispatcher-action modals with **input validation**:
  - **S2.1 Issue route grant** — requires `T<number>` train id +
    comma-separated numeric section ids.
  - **S5.1 Commit MaintenanceOverride** — requires numeric
    section id, non-empty crew id, and expiry 15..=240 min (per
    RFC 0013 S5.4).
  - **Release inspected HABD stop** — requires a train, named qualified
    authority, inspection reference, and explicit examination/line-clear
    confirmation.
  - **Declare degraded mode** — selector for Normal / M1 Manual-
    on-MA / M2 Restricted / M3 Evacuation per RFC 0013 §5.
- Test-mode intrusion injection buttons so a dispatcher can
  rehearse Present / Clear transitions on SEC1001.

## Run (native)

```bash
cargo run --release -p osr-occ-gui -- --operator "dispatcher-alpha"
```

Click **Attach recording** in the left sidebar to run an hour of
the Samawah scenario and stream it into the UI.

## Run (WebAssembly)

Same toolchain as `osr-sim-gui`:

```bash
rustup target add wasm32-unknown-unknown
trunk --version # must report trunk 0.21.8
cd crates/osr-occ-gui
trunk serve web/index.html --open
```

From the repository root, `npm run test:frontend` builds this release bundle
and verifies it in pinned Playwright Chromium.

## Security note

v1 is **read-only** — every dispatcher action emits a stub log line
instead of a signed RFC 0017 envelope. A visible "READ-ONLY v1"
watermark sits in the bottom-right of the map. v3 wires the
operator's signing key from their ATECC608B-backed login and every
committed action reaches the consensus cluster as a `SignedBytes`
envelope that the interlocking verifies before applying.

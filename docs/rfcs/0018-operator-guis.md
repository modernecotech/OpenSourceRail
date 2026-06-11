# RFC 0018 — Operator GUIs: simulator + operations control

**Status:** accepted · 2026-04-23.
**Authors:** OSR project.
**Complements:** [RFC 0003](0003-samawah-reference-deployment.md)
(sim scenarios), [RFC 0013](0013-operations-rulebook.md) (OCC
procedures), [RFC 0017](0017-cybersecurity-message-authentication.md)
(entry authentication).

## 1. Purpose

Two human-facing GUIs that have been implicit in the project
but not built:

- **Simulator GUI (`osr-sim-gui`)** — runs `osr-sim` against a
  scenario TOML, renders the network + trains + MAs + faults
  live, and lets a designer inspect any entity by click-through.
  The audience is the deployment engineer validating their
  design.toml before commissioning, and the OSR developer
  verifying new scenarios.

- **Operations-control GUI (`osr-occ-gui`)** — the dispatcher
  console that RFC 0013 §4.2 has always assumed exists. Renders
  the live network state (from the consensus log), shows every
  RFC 0013 alert (S3 incident categories, S4 weather overlays,
  S7 intrusion verdicts), and exposes the specific actions the
  rulebook allows a dispatcher to take (route grant,
  MaintenanceOverride, degraded-mode transition).

## 2. Non-goals

- **Passenger-facing displays.** PIS rendering is `osr-pis-onboard`
  + `osr-pis-station` — separate codepath, separate build.
- **Maintenance workbench GUI.** CBM dashboards are a v2 scope
  of `osr-cbm-backend`, not this RFC.
- **Mobile apps.** Neither GUI needs to run on a phone.
- **3D rendering.** 2D network schematic is sufficient — legacy
  metros have proved that.
- **Legacy CBTC operator-console emulation.** OSR operates its
  own consensus log; there's no back-compat requirement.

## 3. Technology stack

**egui (+ eframe)** in pure Rust.

Why:

- **Type-consistent with the rest of the workspace.** One language
  from SIL-4 kernel to dispatcher console; fits the project's
  ethos of no-JavaScript-stack, no-proprietary-SCADA.
- **Immediate-mode rendering** matches the per-tick update cadence
  of the sim + consensus log — redraw cheaply, don't reason about
  widget state machines.
- **Works natively + WebAssembly.** A deployment partner can host
  the OCC GUI as a web app for remote supervision without
  rewriting it.
- **Conduction-cooled SBC friendly.** egui renders at 10 Hz on a
  400 MHz single-core ARM — not that we need that, but it
  guarantees the OCC GUI runs on any reasonable workstation.
- **No Electron.** An Electron OCC app would pull in 200 MB of
  Chromium; egui's eframe binary is ~30 MB static-linked.

Rejected alternatives:

- **React/Vue + Tauri** — excellent for complex UIs, but adds a
  full JavaScript toolchain to the build + another set of
  security primitives to audit. Tauri remains a fallback if
  egui runs into a specific limitation.
- **Iced / Slint** — also pure Rust, but egui's immediate-mode
  model is a better fit for the "redraw the whole network each
  tick" workload than retained-mode widget trees.
- **GTK / Qt** — C/C++ deps outside the project's sandbox.

## 4. Architecture

Three new crates:

- **`osr-gui-shared`** — library. Network-layout + drawing
  primitives + colour palette. Consumed by both GUI binaries so
  the two have a consistent look. Not intended for direct use
  outside the GUIs.

- **`osr-sim-gui`** — binary. Wraps `osr-sim` + `osr-gui-shared`.
  Loads a scenario TOML, runs the sim per-tick in the same
  thread as the UI, renders the state each frame.

- **`osr-occ-gui`** — binary. Wraps `osr-occ` + `osr-gui-shared`.
  Reads from a consensus-log source (either a `SimulatedLog`
  file replay or a live `ConsensusBackend`), renders the latest
  derived state, exposes dispatcher actions via modal dialogs
  that emit signed consensus entries (RFC 0017).

```
             ┌────────────────────────────────┐
             │       osr-gui-shared           │
             │  Network layout + drawing      │
             │  Colour palette                │
             │  Click-hit helpers             │
             └────────────────────────────────┘
                       ▲              ▲
                       │              │
       ┌───────────────┘              └────────────────┐
       │                                                │
  ┌──────────────┐                              ┌──────────────┐
  │ osr-sim-gui  │                              │ osr-occ-gui  │
  │              │                              │              │
  │  scenario →  │                              │  live log →  │
  │  osr-sim →   │                              │  osr-occ →   │
  │  egui draw   │                              │  egui draw + │
  │              │                              │  action pane │
  └──────────────┘                              └──────────────┘
      │                                                │
      ▼                                                ▼
   designer workstation                        OCC dispatcher
```

## 5. Shared rendering — `osr-gui-shared`

Scope:

- **`NetworkLayout`** — per-line horizontal strip, stations
  placed along the strip by cumulative distance. Same layout
  strategy as the existing HTML `osr-vis`, reused so dispatchers
  + designers see an identical schematic.
- **`draw_network` / `draw_train` / `draw_section_state`** —
  egui paint helpers that take a `Painter`, a `NetworkLayout`,
  and the current state to render.
- **`Palette`** — colours for every train phase, section
  state, intrusion verdict, obstacle verdict, fault state.

## 6. `osr-sim-gui`

Minimum viable feature set:

- **Scenario loader.** Filebrowser → pick a `scenarios/*.toml`
  → load.
- **Playback controls.** Play / pause / step / speed (1×, 10×,
  100×).
- **Network render.** Samawah two-line schematic with every
  train drawn as a dot at its current `station_m`, colour-coded
  by phase.
- **Inspector pane.** Click a train → sidebar shows ATP verdict,
  brake cmd, SoC, obstacle-detect verdict.
- **Event log.** Scrolling list of `EventKind` emissions —
  Dispatched, ArriveStation, DepartStation, etc.
- **Fault indicators.** Active faults from the scenario's
  `[[faults]]` section render as coloured badges on the
  affected station / section / train.

Post-v1 (deferred):

- Timeline scrubber for replay
- Record / export runs
- Differential compare of two scenarios side-by-side
- Remote-monitor mode (read the sim from another host)

## 7. `osr-occ-gui`

Minimum viable feature set for v1:

- **Log-source selector.** Pick a file replay (for exercises)
  or connect to a live `ConsensusBackend`.
- **Network render.** Same layout as the sim GUI.
- **Section-state panel.** `SectionIntrusion` verdicts from
  RFC 0016, colour-coded; click a section to see the latest
  `MaintenanceOverride`, `RouteGrant`, or `SectionIntrusion`
  on that section.
- **Train panel.** List of every train under the dispatcher's
  control, with the same colour coding as the sim GUI.
- **Alert feed.** Intercom presses, EB events, weather
  overlays, CBM red alerts.
- **Action modal stubs.** The four dispatcher actions from
  RFC 0013 §4.2 (issue route grant S2.1, commit
  `MaintenanceOverride` S5.1, extend dwell S2.3, declare
  degraded mode) exist as modal dialogs that validate the
  input but emit no-ops for v1.

Post-v1 (deferred):

- Live command emission to the consensus cluster with RFC 0017
  signed envelopes
- Multi-operator role partitioning (dispatcher vs supervisor vs
  engineer-on-call) with per-role action gates
- Full audit-log display
- Video feed from station CCTV + cabin CCTV (RFC 0015 §5.5)

## 8. Security model

The OCC GUI is a privileged actor. Its action emissions must
be signed by the logged-in dispatcher's personal key (RFC 0013
S1.1, RFC 0017). v2 of this RFC wires the signing key → OCC
UI login flow; v1 is read-only so the security model is
trivially "read-only view of committed log."

## 9. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | `osr-gui-shared` network renderer + `osr-sim-gui` + `osr-occ-gui` scaffolded; both compile cleanly in the workspace, open an egui window, render the Samawah network, and expose the v1 minimum feature set listed above. | v0 |
| **v2** | `osr-sim-gui` full sim integration (live tick stream, click-to-inspect) | v1, RFC 0003 |
| **v3** | `osr-occ-gui` live consensus integration (read + write via RFC 0017 signed envelopes) | v1, RFC 0017 v2 |
| **v4** | WebAssembly builds for remote access to both GUIs | v2, v3 |
| **v5** | First OSR deployment instance uses `osr-occ-gui` in revenue service | v3 |

## 10. What this RFC does NOT include

- **PIS (passenger-facing) displays.** Separate `osr-pis-*` crates.
- **CBM / maintenance dashboards.** Separate `osr-cbm-backend` UI.
- **Electron / web-framework-native versions.** egui's WASM
  target covers the "browser access" use case.
- **3D rendering.** Schematic 2D is explicitly the goal.
- **Mobile apps.** Not a target deployment form factor for
  either audience.

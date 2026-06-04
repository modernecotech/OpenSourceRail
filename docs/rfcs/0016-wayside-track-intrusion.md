# RFC 0016 — Wayside track-intrusion detection

**Status:** accepted · 2026-04-23.
**Authors:** OSR project.
**Complements:** [RFC 0015](0015-driverless-operation.md) (onboard
obstacle detection). **Amends:** RFC 0005 (crate map), RFC 0007
(hardware palette adds one SKU variant), RFC 0001 (interlocking
consumes intrusion state).

## 1. Purpose

Driverless trains (RFC 0015) detect obstacles in their own path
with the onboard `osr-obstacle-detect` evaluator. This RFC
complements that with **wayside track-intrusion detection** —
fence-line + ROW-mounted sensors that detect people, animals,
debris, or vehicles entering the track envelope **before a train
arrives**.

The goal is not redundancy with the onboard detector. The two
systems serve different safety arguments:

- **Onboard detector** sees what's in front of the moving train,
  *reactively* — once something enters the current envelope,
  brake hard.
- **Wayside detector** sees what's in the ROW at any time,
  *proactively* — if the section is not clear, the interlocking
  withholds Movement Authority and the train never arrives at
  the obstacle.

Wayside detection is what lets the interlocking say "this
section is safe" rather than "this section was safe the last
time a train passed through." In GoA 4 operation, with no
driver to see irregularities between trains, this is a
necessary safety property — not a nice-to-have.

## 2. Why now, not in RFC 0015

RFC 0015 §13 explicitly listed "automated track-intrusion
detection at wayside" as a future RFC candidate. The two RFCs
partition cleanly:

- **RFC 0015** owns the onboard sensor suite, the T-OBS ECU,
  and the driverless rolling-stock profile.
- **RFC 0016** owns the wayside sensor suite, a new
  `osr-intrusion-detect` evaluator on the W-SBC host class,
  and the feed into `osr-interlocking` that withholds MA on
  intrusion-flagged sections.

Splitting keeps each RFC focused on one SIL-4 evaluator + one
host class, matching the RFC-per-crate-family pattern of the
project.

## 3. Scope

**In scope:**

- Wayside sensor-suite spec (fence contact, ROW LIDAR, ROW radar,
  CCTV AI).
- `osr-intrusion-detect` evaluator: per-section `IntrusionVerdict`
  (Clear / Unknown / Present), with fail-restrictive on Unknown.
- Integration with `osr-interlocking`: intrusion state is a new
  gating input alongside switch-position and block-occupancy.
- Operations amendments: how the dispatcher handles a section
  under active intrusion.

**Out of scope:**

- Fencing construction (deployment-partner civil scope).
- Video-analytics AI model training (training data is deployment-
  specific; the classifier runs as a black box per §5.3).
- Long-range perimeter surveillance outside the ROW (deployment
  partner's security concern, not rail safety).

## 4. What the wayside sensor suite looks like

Per-section sensor pack (one pack per `[SEC]` id in the
interlocking). Installed at ROW junction boxes; each junction
box feeds a W-SBC running `osr-intrusion-detect`.

| Sensor | Role | Typical unit | Unit price (2026) | Why |
|---|---|---|---|---|
| **Fence-line contact** | Perimeter breach | Vibration + cut-wire sensor (e.g., Senstar FlexZone) | $325–550 / 100 m | Instant alarm on fence cut or climb; mature tech, low false-positive rate |
| **ROW LIDAR** (pole-mount, every ~200 m) | 3D silhouette in ROW | Livox Mid-360 (360° FoV, 70 m range) or equivalent | $875–1 300 | 3D presence detection, day/night, IP67 industrial — same supply-chain story as RFC 0015 §5.1 |
| **ROW radar** (pole-mount, every ~500 m) | All-weather presence | TI AWR1843 or eq. 77 GHz | ~$550 | Penetrates fog/dust that degrades LIDAR; redundant physics |
| **CCTV with AI classifier** | Classification + human oversight | Commodity 4 K IP camera + edge TPU (Google Coral or eq.) | $435–875 per camera | Per-station already required by RFC 0010; AI classification reuses existing cameras |

**Sensor spacing** is driven by section length (RFC 0001):

- `at-grade` sections: LIDAR every 200 m, radar every 500 m,
  fence-line continuous.
- `elevated` sections: LIDAR every 200 m; fence-line not
  applicable (viaduct edge is the barrier); radar optional.
- `bridge` sections: LIDAR at each end + mid-span; no fence-line
  applicable.

A typical `standard-urban` 1 km `at-grade` section carries:
5 LIDAR + 2 radar + 1 CCTV + 1 km fence-line. Total hardware
cost ≈ $7 600 per section — small fraction of the $850 000 per
km civil cost.

## 5. The `osr-intrusion-detect` evaluator

### 5.1 Pure-function API

```rust
pub fn evaluate(
    frame: &WaysideSensorFrame,
    now_ns: u64,
    params: &IntrusionParams,
) -> IntrusionOutcome;
```

Inputs:

- `WaysideSensorFrame` — one tick of sensor data per section:
  fence-line state, LIDAR detection list (range + lateral),
  radar detection list, camera classification + confidence.
- `now_ns` — sim / system time for staleness checks.
- `IntrusionParams` — per-deployment thresholds (lateral rail-
  profile width, freshness timeout, classifier confidence floor).

Output:

- `IntrusionVerdict` — `Clear` / `Unknown` / `Present`.
- `TriggerReason` — which sensor + which class, for logging.

### 5.2 The three verdicts

- **`Clear`** — the section has no detected intrusion. MA may
  cross this section.
- **`Unknown`** — at least one safety-primary sensor is stale
  or offline, and no `Present` detection is confirmed. MA **is
  withheld** (fail-restrictive). This is the crucial property:
  a broken sensor does not imply safe track.
- **`Present`** — an intrusion is confirmed by at least one
  sensor of sufficient confidence. MA is withheld; dispatcher
  is alerted.

### 5.3 Safety properties (I1–I5)

Paralleling the O-series from RFC 0015:

| Property | Claim |
|---|---|
| **I1** | Any LIDAR detection inside the ±1500 mm rail profile → `Present`. |
| **I2** | Any sensor frame stale beyond `MAX_SENSOR_STALE_MS` → `Unknown` (not `Clear`). |
| **I3** | Fence-line breach → `Present` regardless of other sensor state. |
| **I4** | Camera classifier alone (no LIDAR / radar corroboration) cannot emit `Clear` — the safety-primary physics must be alive. |
| **I5** | Refreshing a sensor never moves the verdict in a less-restrictive direction (monotone under freshness). |

Each property anchors a Kani harness + a proptest — same pattern
as the O-series.

### 5.4 Integration with `osr-interlocking`

A new `SectionIntrusion` entry on the consensus log carries the
verdict per section. `osr-interlocking::section_available_to`
reads this alongside the existing gates (block occupancy, switch
position) and refuses to grant MA across a section whose latest
`SectionIntrusion` is not `Clear`.

This is a v2 deliverable of this RFC; v1 scaffolds the
evaluator and a first Kani suite.

## 6. Hardware implications

`osr-intrusion-detect` runs on the W-SBC (Radxa CM5 RK3588S)
per RFC 0007. No new host class — the W-SBC already hosts
`osr-interlocking` and `osr-wayside-points`, so adding
intrusion-detect is a same-crate-family deployment.

Baseboard additions per junction box:

- 8× fence-line contact inputs (optically isolated).
- 2× CAN-FD (radar + spare).
- 1× 1000BASE-T to LIDAR.
- 1× MIPI-CSI to CCTV edge-TPU (or Ethernet if the TPU is
  separate).

No change to the T-ECU/S or T-OBS boards — this is purely a
wayside addition.

## 7. Operations implications

### 7.1 Dispatcher (S rulebook amendment)

A new rule group S7 — Intrusion response:

- **S7.1** On first `Present` verdict, the dispatcher holds the
  section and dispatches track-patrol within 10 min.
- **S7.2** On `Unknown` verdict persisting > 5 min, the dispatcher
  treats it as a functional failure of wayside equipment and
  opens a work ticket; trains are held or diverted.
- **S7.3** A section cleared by track-patrol and returned to
  `Clear` may re-enter revenue service.

### 7.2 Maintenance (M rulebook amendment)

- **M7** Wayside sensor maintenance: 30-day walk-through
  inspecting each LIDAR/radar housing, cable runs, fence
  contacts. Same cadence as M3 track inspection.

Rulebook text added when RFC 0016 v2 lands.

## 8. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | `osr-intrusion-detect` crate at [`crates/osr-intrusion-detect/`](../../crates/osr-intrusion-detect/) — pure-function evaluator with 5 Kani harnesses + proptest properties I1–I5. GSN safety-case file at [`docs/safety-case/gsn/70-intrusion-detect.toml`](../safety-case/gsn/70-intrusion-detect.toml) closes against real evidence (done 2026-04-23). | v0 |
| **v2** ✅ | Integration with `osr-interlocking`: new `EntryPayload::SectionIntrusion` consensus log entry + `IntrusionState` enum (`Clear`/`Unknown`/`Present`); `DerivedState.section_intrusions` folds the latest verdict per section; `section_available_to` gate (d) consults the verdict — `Present`/`Unknown` withhold MA, `Clear` permits, missing entry = "not instrumented" (backwards-compatible). 5 unit tests exercise every path including "latest verdict wins". (done 2026-04-23) | v1, RFC 0001 |
| **v3** ✅ | Sim integration: new `FaultKind::WaysideIntrusion { section, state }` in `osr-sim::fault`; the sim tick emits one `SectionIntrusion` consensus entry per active fault through `MaLogBackend::emit_intrusion` (both `SimulatedLog` and `ConsensusBackend` backends). A demonstrator scenario stages Present / Unknown / Present events across three sections during AM peak; run completes with zero invariant violations — the interlocking's gate (d) held MA back without any train entering the flagged sections. (done 2026-04-23) | v2 |
| **v4** ✅ | Rulebook amendments — dispatcher S7 at [`docs/operations/dispatcher/s7-intrusion-response.md`](../operations/dispatcher/s7-intrusion-response.md) (5 rules: S7.1 track-patrol, S7.2 sustained-Unknown, S7.3 return-to-service, S7.4 multi-section escalation, S7.5 no-override) and maintenance M7 at [`docs/operations/maintenance/m7-wayside-sensor-maintenance.md`](../operations/maintenance/m7-wayside-sensor-maintenance.md) (5 rules: M7.1 30-day walk, M7.2 post-weather, M7.3 sustained-Unknown ticket, M7.4 replacement calibration, M7.5 fence continuity test). RFC 0013 §4.2 and §4.4 indices updated. (done 2026-04-23) | v2 |
| **v5** | Deployment at Samawah: first-article sensor packs at 3 sections on Line 1 | RFC 0003, v2 |

## 9. Relationship to existing RFCs

- **RFC 0001** (consensus) — adds `SectionIntrusion` log entry.
- **RFC 0005** (software architecture) — adds `osr-intrusion-detect`
  to the W-SBC crate map.
- **RFC 0007** (hardware) — junction-box baseboard adds sensor
  headers; no new host class.
- **RFC 0013** (operations) — S7 + M7 rule groups (v2+).
- **RFC 0015** (driverless) — complements onboard obstacle-
  detect; the two-layer defence (wayside proactive, onboard
  reactive) is the full GoA 4 safety-envelope story.

## 10. What this RFC does NOT include

- Passive fence line without contact-sensor instrumentation —
  standard civil scope.
- Personnel-identification against a whitelist (crew vs. intruder)
  — handled by CCTV + human review at the OCC, not automated in
  this RFC.
- Anti-climb / anti-cut physical deterrents on the fence — civil
  scope per deployment-partner security spec.
- Section-level live-radar tracking of authorised track workers
  (under a `MaintenanceOverride`, RFC 0013 S5 rules apply; the
  intrusion-detect evaluator flags `Present` and the dispatcher
  cross-references against the active work-block manifest).

# Safety requirements specification

Functional safety requirements (SR-01 … SR-24) derived from
EN 62267 §6 (functional requirements for GoA 4 operation) and
cross-referenced to OSR artefacts (crates, RFCs, rulebook
sections). Requirements are grouped by the EN 62267 function.

Each requirement states **what** the system must do and names
the **evidence** that it does so. Detailed evidence lives in
[evidence-register.md](evidence-register.md).

## 1. Train separation (EN 62267 §6.1)

### SR-01 — Safe separation between trains

The system shall at all times prevent two trains from occupying
the same track section.

- **Implementation:** `osr-interlocking::section_available_to`
  gate (a) refuses MA into any section whose `section_occupancy`
  record names a different train.
- **Evidence:** GSN G1 (via `docs/safety-case/gsn/10-non-overlap.toml`);
  property P2 proptest at `crates/osr-interlocking/tests/proptest_ma.rs`;
  Kani harness `kani_a5_head_past_ma_end_trips_same_section`.

### SR-02 — MA validity window

Every movement authority issued to a train shall carry an
absolute expiry time and shall not be extended without a fresh
position report.

- **Implementation:** `MA_VALIDITY_WINDOW_NS` bound on every
  MA; ATP property A2 trips on expiry.
- **Evidence:** Kani `kani_a2_expired_ma_trips`; property P5
  proptest.

### SR-03 — MA conservatism under uncertainty

Widening any sensor-uncertainty or shortening any MA input shall
never move the ATP verdict toward a less-restrictive brake
command.

- **Implementation:** ATP property A7.
- **Evidence:** Kani `kani_a7_uncertainty_widening_is_conservative`;
  property A7 proptest.

## 2. Train protection (EN 62267 §6.2)

### SR-04 — Stopping before obstacle (GoA 4 substitution for driver)

The system shall detect obstacles inside the current stopping-
distance envelope and command Emergency Brake within the ATP
tick.

- **Implementation:** `osr-obstacle-detect::evaluate` property O1;
  any LIDAR / radar / ultrasonic detection inside the envelope
  forces `ObstacleVerdict::EmergencyBrake`, which flows into
  `BrakeInputs::obstacle_emergency`.
- **Evidence:** Kani `o1_ultrasonic_return_forces_eb`; proptest
  `o1_ultrasonic_return_forces_eb`; sim built-in obstacle-fault
  fault-injection fixture.

### SR-05 — Fail-restrictive on sensor failure

If any safety-primary obstacle-detect sensor is stale beyond
100 ms, the verdict shall be at least `RestrictedSpeed` (O4b)
and never `Clear`.

- **Implementation:** O2 + O4b in `osr-obstacle-detect`.
- **Evidence:** Kani `o2_stale_ultrasonic_forces_eb`,
  `o4b_lidar_offline_with_radar_healthy_restricts_speed`.

### SR-06 — 2oo2 cross-check on obstacle detection

The two redundant obstacle-detect channels (RP2350 A + B on the
T-OBS board) shall both agree on `Clear` before the trainset
may proceed at full MA-permitted speed.

- **Implementation:** O3 property; any peer disagreement → EB.
- **Evidence:** Kani `o3_peer_disagreement_forces_eb`.

### SR-07 — Wayside intrusion gate

The system shall withhold MA on any track section whose latest
wayside intrusion verdict is not `Clear`.

- **Implementation:** `osr-interlocking::section_available_to`
  gate (d) introduced by RFC 0016 v2.
- **Evidence:** `intrusion_present_blocks_section`,
  `intrusion_unknown_is_fail_restrictive`,
  `latest_intrusion_verdict_wins` unit tests in
  `crates/osr-interlocking/src/ma.rs`.

## 3. Door operation (EN 62267 §6.3)

### SR-08 — Door closed above threshold speed

The system shall interlock door opening so that a door cannot
be commanded open while `speed ≥ 5 km/h`.

- **Implementation:** `osr-door-control` closing interlock
  (SIL-4 per RFC 0005 §4.2).
- **Evidence:** `osr-door-control` proptests.

### SR-09 — Door obstruction detection

The system shall detect door obstructions via motor current +
dedicated sensor and reopen the affected door on detection.

- **Implementation:** `osr-door-control` obstruction
  handler.
- **Evidence:** `osr-door-control` integration tests.

### SR-10 — Platform-side alignment at standstill

Door opening shall be enabled only when the train is at
standstill (`speed < threshold`) and reporting position within
± 0.5 m of the platform reference mark.

- **Implementation:** Door-enable gate uses `osr-odometry`
  position + `osr-ato` stop-detection; PSD interlock adds a
  second layer at PSD-equipped stations.
- **Evidence:** `osr-ato` stop-tolerance tests; RFC 0010 §7
  platform geometry.

## 4. Obstacle and derailment detection (EN 62267 §6.4)

### SR-11 — Derailment detection

Lateral g-forces + axle-rotation asymmetry monitored in 2oo2
shall trip Emergency Brake on any indication of derailment.

- **Implementation:** `osr-derailment::derailment_evaluate`;
  feeds `BrakeInputs::derailment_emergency`.
- **Evidence:** `osr-derailment` proptests.

### SR-12 — Onboard fire detection

Smoke + temperature in battery / traction / HVAC bays shall
trigger suppression + EB.

- **Implementation:** `osr-fire-safety::fire_evaluate`;
  feeds `BrakeInputs::fire_emergency`.
- **Evidence:** `osr-fire-safety` proptests.

### SR-13 — Hot-axle box detection

Axle bearing temperature above threshold shall produce an
advisory event; OCC triages per RFC 0013 S3.

- **Implementation:** `osr-hot-axle` (onboard, SIL-2) +
  `osr-hot-axle-wayside` (wayside, SIL-4).
- **Evidence:** `osr-hot-axle-wayside` proptests.

## 5. Emergency detection and management (EN 62267 §6.5)

### SR-14 — Passenger emergency intercom

Passengers shall be able to trigger a controlled brake + open
an audio + video channel to OCC by pressing an emergency
intercom; the brake shall bring the train to a safe stop at
the next station (not immediate EB, to avoid stranding).

- **Implementation:** RFC 0015 §5.3 intercom path; feeds
  `BrakeInputs::driver_emergency` (legacy name, covers
  passenger-intercom route in GoA 4).
- **Evidence:** RFC 0013 rulebook cross-refs; current simulator
  coverage is a stub. Release closure requires the live intercom
  path and incident workflow evidence tracked in
  [release-gap-register.md](release-gap-register.md).

### SR-15 — EB dominates all other brake commands

Emergency Brake shall not be reducible by any other input;
service-brake or release commands during an EB shall be
ignored until EB is explicitly released.

- **Implementation:** `osr-brake::brake_evaluate` B2 property.
- **Evidence:** Kani `kani_b2_emergency_union`,
  `kani_b3_emergency_completeness`.

### SR-16 — Passenger fire-evacuation on EB + fire

If EB is driven by a fire trip, the train shall continue to
the next station platform where safe, then open doors +
announce evacuation.

- **Implementation:** `osr-ato` fire-response mode;
  `osr-fire-safety` coordinates with `osr-brake`; RFC 0013 S3.6
  rulebook procedure.
- **Evidence:** Rulebook; deployment-specific simulator and
  first-article evacuation evidence are release gaps.

## 6. Operations supervision (EN 62267 §6.6)

### SR-17 — Dispatcher accountability

Every MA grant, MaintenanceOverride, and degraded-mode
transition shall be attributable to a named dispatcher via
their OCC login.

- **Implementation:** RFC 0013 S1.1 rule (personal credential);
  `osr-occ` console logs.
- **Evidence:** Rulebook; audit-log structure in `osr-historian`.

### SR-18 — Remote-assist for passenger incidents

OCC shall maintain an audio + video channel to any trainset
under remote-assist; dispatcher may hold the train, request
medical, or release to continue.

- **Implementation:** RFC 0015 §5.3; RFC 0013 C2 communications.
- **Evidence:** Rulebook cross-refs; live-comms hardware and
  integration evidence are release gaps.

## 7. Fault management (EN 62267 §6.7)

### SR-19 — Fail-restrictive default

Every SIL-4 evaluator shall fail in the restrictive direction —
on any uncertainty, ambiguity, or missing input the verdict is
at least the second-most-severe (usually a brake, sometimes a
speed cap).

- **Implementation:** All O-series (obstacle-detect), I-series
  (intrusion-detect), A-series (ATP), P-series (interlocking),
  V-series (vigilance), O-odom, B-brake properties carry fail-
  restrictive clauses.
- **Evidence:** 8 Kani harness modules across the SIL-4 crates;
  GSN G1–G24 closure.

### SR-20 — 2oo2 hardware voting at output stage

Every brake command to the actuator shall pass through a 2oo2
AND-gate relay driven by both RP2350 channels of the T-ECU/S.

- **Implementation:** Hardware AND-gate relay stage per
  `hardware/t-ecu-s/schematics/v2-spec/safety-nets.md`.
- **Evidence:** Safety-nets spec; DRC pass at board production
  (deployment-specific).

### SR-21 — Watchdog-driven reset

Loss of heartbeat from either RP2350 shall drive the TPS3701
supervisor to reset that channel; concurrent loss of both
heartbeats shall drop the EB relay directly (bypassing the
AND gate).

- **Implementation:** `hardware/t-ecu-s/schematics/v2-spec/safety-nets.md`
  watchdog rules.
- **Evidence:** Safety-nets spec.

## 8. Cybersecurity (EN 62267 §6.8, complementary IEC 62443-4-2)

### SR-22 — Consensus entry authenticity

Every entry committed to the track-state consensus log shall
be signed by its originating entity and verified by every
consumer before it affects derived state.

- **Implementation:** `osr-secbus::verify_signed` (RFC 0017);
  S1/S2/S3 properties.
- **Evidence:** `osr-secbus` Kani + proptest; GSN G25–G27.
  **Status:** library in tree; wiring into the live consensus
  wire layer is RFC 0017 v2 (open).

### SR-23 — Fare-token authenticity

Every fare transaction token shall carry an HMAC-SHA256 MAC
keyed to a per-deployment secret that is rotatable without
re-issuing existing tokens.

- **Implementation:** `osr-crypto::hmac_sha256_verify`; used by
  `osr-afc`.
- **Evidence:** `osr-crypto` proptests; `osr-afc` integration.

## 9. Passenger interaction (EN 62267 §6.9)

### SR-24 — Platform screen door mandatory at GoA 4

Every passenger boarding platform in a GoA 4 deployment shall
be equipped with platform screen doors (PSDs) per RFC 0010
§6 + RFC 0015 §5.4.

- **Implementation:** RFC 0010 station-design standard with PSD
  in every non-`halt` archetype; RFC 0015 §5.4 tightens the
  default to PSD-mandatory for every boarding platform
  (except depot-terminal, where access is staff-only).
- **Evidence:** RFC 0010, RFC 0015; deployment-specific design
  report.

## Requirement summary table

| ID | Summary | SIL | Evidence kind |
|---|---|---|---|
| SR-01 | Section-occupancy gate | 4 | Kani + proptest + GSN G1 |
| SR-02 | MA validity window | 4 | Kani + proptest |
| SR-03 | MA conservatism | 4 | Kani + proptest |
| SR-04 | Obstacle detection in envelope | 4 | Kani + proptest + sim |
| SR-05 | Fail-restrictive on sensor failure | 4 | Kani + proptest |
| SR-06 | 2oo2 obstacle-detect cross-check | 4 | Kani |
| SR-07 | Wayside intrusion gate | 4 | Unit test + GSN G20–G24 |
| SR-08 | Door-interlock above threshold | 4 | Proptest |
| SR-09 | Door-obstruction reopen | 4 | Integration test |
| SR-10 | Platform-alignment gate | 4 | ATO tests + RFC 0010 |
| SR-11 | Derailment detection | 4 | Proptest |
| SR-12 | Onboard fire detection | 4 | Proptest |
| SR-13 | Hot-axle-box detection | 4 (wayside) / 2 (onboard) | Proptest |
| SR-14 | Passenger emergency intercom | 2 | Rulebook + sim stub |
| SR-15 | EB dominates | 4 | Kani |
| SR-16 | Evacuation on fire-EB | 2 | Rulebook + sim pending |
| SR-17 | Dispatcher accountability | — | Rulebook S1.1 |
| SR-18 | Remote-assist channel | — | Rulebook C2 + HW stub |
| SR-19 | Fail-restrictive default | 4 | 8 Kani modules + GSN G1–G24 |
| SR-20 | 2oo2 hardware voting | 4 | Safety-nets spec |
| SR-21 | Watchdog + reset | 4 | Safety-nets spec |
| SR-22 | Consensus entry auth | 2 | Kani + proptest + GSN G25–G27 |
| SR-23 | Fare-token auth | 2 | Proptest |
| SR-24 | PSDs at every boarding platform | — | RFC 0010 + RFC 0015 §5.4 |

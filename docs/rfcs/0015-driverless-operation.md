# RFC 0015 — Driverless operation (GoA 4) as the default

**Status:** accepted · 2026-04-22.
**Authors:** OSR project.
**Superseded:** nothing (new). **Supersedes for GoA 4 deployments:**
RFC 0013 §4.1 (Driver rulebook D1–D8). **Amends:** RFC 0008 (cab),
RFC 0007 (hardware), RFC 0005 (crate map), RFC 0013 (operations).

## 1. Purpose

Every OpenSourceRail deployment ships as a **GoA 4 (Unattended
Train Operation, UTO) system from day one**. The default rolling
stock has no driver cab. The default operations model has no
driver role.

This RFC sets the safety, hardware, and operations envelope for
that default — specifically, the onboard obstacle-detection
sensor suite + ECU that lets a trainset run without a driver's
eyes in the loop.

## 2. Why driverless by default

Three non-novelty reasons:

1. **Lower total cost.** A cab costs ~$270k per trainset when
   wiring, DMI, HVAC, controls, and emergency exits are summed.
   Over a 40-trainset fleet that is ~$11 M of capex. Drivers cost
   ~$110 k/year fully loaded; a 50-driver roster for round-the-
   clock operation is ~$5.5 M/year in wages alone.

2. **Simpler trainset.** Removing the cab takes out roughly
   40 kg of wiring, four HMIs (DMI, mirror monitors, rear-view,
   comms), the master controller + dead-man handle, cab HVAC,
   cab door + exit, and all the diagnostic plumbing that
   terminates in the cab. The nose becomes a sensor cowl plus a
   coupler; the floor plan becomes full passenger capacity
   end-to-end. **~5 % more seats per trainset.**

3. **Simpler operations.** The driver rulebook (RFC 0013 §4.1
   D1–D8) was already the densest and safest-critical section.
   In GoA 4 it evaporates: about 40 % of driver tasks transfer
   to OCC (dispatcher + remote-assist), about 50 % transfer to
   station staff (dwell supervision, boarding assistance), and
   the remaining 10 % are automated by the onboard stack.

The tradeoff is concentrated in the obstacle-detection problem:
what a driver's eyes used to do, a sensor suite must now do. The
rest of this RFC is mostly about that.

## 3. Scope

**In scope of this RFC:**

- Obstacle-detection sensor suite (ultrasonic + radar + camera,
  LIDAR optional) and the onboard ECU that fuses them.
- Deprecation of cab-only software (`osr-dmi`, `osr-vigilance`)
  for the GoA 4 default.
- New operations primitives: remote assist, platform staff role
  expansion, passenger emergency intercom.
- Amendments to RFC 0008, 0007, 0005, 0013.

**Out of scope:**

- Cab-retained variants (GoA 2). These remain *possible* — `osr-
  vigilance` and `osr-dmi` stay in tree, marked "GoA 2 only" —
  but they are not the shipped default.
- Passenger-facing accessibility (covered by RFC 0010 §7 and not
  changed by driverless).
- Cybersecurity of the obstacle-detect data path (covered by the
  pending `osr-secbus` RFC).

## 4. What goes away

| Removed | Reason | Replacement (if any) |
|---|---|---|
| Driver cab + windscreen | No driver | Nose-cone sensor cowl |
| DMI touchscreen | No driver | Remote-assist web console (OCC) |
| Master controller + dead-man | No driver | ATO + emergency plunger (intercom-triggered) |
| Cab HVAC + cab door | No driver | — |
| Cab-to-ground radio handset | Voice comms are now OCC-mediated | Cabin PA + passenger emergency intercom |
| Driver rulebook D1–D8 | No driver | Dispatcher S1–S6 + Station-staff T1–T5 absorb |
| `osr-vigilance` (from SIL-4 critical path) | No driver to vigil | — |
| `osr-dmi` (from default build) | No driver to display to | Passenger PIS already exists |

## 5. What becomes required

### 5.1 Obstacle-detection sensor suite

**Two identical sensor packs per trainset — one behind each
nose panel.** The trainset has no permanent "leading end" —
either end can lead on the current run. The active pack is
always the one facing the direction of travel; the trailing
pack self-tests continuously and stands ready for the return
trip.

Each pack contains:

| Sensor | Role | Range | Update rate | Unit price (2026) | Why |
|---|---|---|---|---|---|
| **4 × ultrasonic** (Murata MA40H1S-R or equivalent, 40 kHz) | Close-range safety belt | 0.2 – 20 m | 20 Hz | ~$25 each | Platform gap, depot yard, emergency crawl — cheap, solid-state, unaffected by darkness, failure mode self-detectable from echo pattern |
| **1 × solid-state LIDAR** (Livox HAP / Tele-series / RoboSense M1 / Leishen CH-series — all Chinese OEMs now in the $550–2,200 bracket) | Mid-range 3D primary | 5 – 200 m | 10 Hz | $550 – $2,200 | 3D point cloud, day/night, 150–300 m published range, IP67 industrial variants available |
| **1 × mmWave radar** (TI AWR1843 or eq., 77 GHz) | All-weather validation | 5 – 200 m | 20 Hz | ~$550 | Penetrates dust, fog, and the sandstorms the LIDAR point cloud degrades under — independent physics for a true disagreement vote |
| **1 × stereo camera pair** | Object classification | 0 – 100 m | 30 Hz | ~$325 | Distinguishes human / animal / debris; informs verdict severity, not primary safety |

The suite is **multi-sensor by design** — obstacle detection
is too consequential to rest on a single physics. A
sensor-disagreement verdict is explicit in the evaluator
(§10.1) and fail-restrictive.

### 5.1.1 Degraded-sensor speed policy

The evaluator exposes a dedicated `RestrictedSpeed` verdict so
that partial sensor failures produce a *smooth speed reduction*
instead of an EB:

| Configuration | Verdict (no obstacles detected) | Effect |
|---|---|---|
| Ultrasonic + LIDAR + radar all healthy | `Clear` | Full MA-permitted speed |
| LIDAR offline / stale · radar healthy | **`RestrictedSpeed`** | **ATO caps at 40 km/h** (the ultrasonic-safe envelope) |
| LIDAR healthy · radar offline | `Clear` | Full speed — radar is a validation channel, not primary |
| Both long-range offline · train ≤ 40 km/h | `RestrictedSpeed` | ATO holds ≤ 40 km/h |
| Both long-range offline · train > 40 km/h | `EmergencyBrake` | No coverage beyond ultrasonic band at this speed — full EB |
| Any ultrasonic channel stale / faulted | `EmergencyBrake` | Ultrasonic is always required (close-range safety belt) |
| Peer 2oo2 channel disagrees | `EmergencyBrake` | Fail-restrictive |

The policy is asymmetric on purpose: **LIDAR is the primary
long-range channel; radar is its all-weather validator**. Losing
LIDAR restricts speed; losing radar (while LIDAR still sees
3D at 5–200 m) does not. Both gone → EB if speed would outrun
the ultrasonic envelope.

**Why LIDAR failing caps at 40 km/h rather than EB.** At 40 km/h
the stopping distance is ≈ 18 m, inside the ultrasonic reliable
band. The trainset keeps moving (avoiding a stranded-passengers
incident) but at a speed that ultrasonic can safely cover if
radar also fails in the next tick. Braking smoothly with the
service brake to 40 km/h from mainline speed is a passenger-
comfort decision that costs no safety — the remaining sensors
still cover the revised stopping distance.

**Why ultrasonic is primary for the close-range envelope.**
Ultrasonic transducers are the cheapest, simplest, and most
failure-predictable sensor in the suite. A quadrant (four
transducers with overlapping cones) costs ~€100, draws <
1 W, and has a failure mode that is detectable from its own
echo pattern. For the platform-approach envelope (< 40 km/h,
< 20 m stopping distance) it is sufficient on its own — which
is why RFC 0015 makes it the *primary safety belt* for that
speed band. Depot and workshop movements run permanently
inside the ultrasonic band.

**Why LIDAR is primary mid-range, not optional.** The 2025–
2026 market shift in Chinese solid-state LIDAR put the
Livox-class unit (150–300 m range, IP67, automotive-grade)
into the $550–2 200 bracket — an order of magnitude below
where it was three years ago. At that price, LIDAR becomes
*the cheapest way* to cover the 20 m – 200 m obstacle
envelope with full 3D range data; it displaces radar as the
primary mid-range sensor and pushes radar into the
all-weather-validation role. Any target-region dust-storm
event (see RFC 0013 S4.1) degrades LIDAR point density,
which is exactly when the radar's mmWave penetration
matters.

**Why radar stays in the suite even with LIDAR promoted.**
The point of the multi-sensor architecture is that each
sensor fails under a different physics. LIDAR fails in
heavy dust or direct sun; radar fails on small stationary
objects; ultrasonic fails at speed; cameras fail at night.
A 2oo2-style safety vote across independent physics is
stronger than any one sensor's specified SIL rating.

**Why cameras are classifier-only.** Cameras inform the
*severity* of a detection (human vs. animal vs. debris)
which feeds the verdict severity (`CrawlOnly` for a paper
bag, `EmergencyBrake` for a person). They are not the
safety-primary channel for detection — detection comes from
ultrasonic / LIDAR / radar. Cameras are included at cheap
cost ($325/stereo pair) because classifier data improves
operational availability (fewer spurious EBs on windblown
debris).

### 5.2 The T-OBS ECU

A new onboard host class: **T-OBS (Train Obstacle-Detection
ECU)**. Architecture mirrors T-ECU/S:

- **2 × Raspberry Pi RP2350** in a 2oo2 composite fail-safe
  voting arrangement, each running identical `no_std` Rust
  obstacle-detection code.
- **1 × Raspberry Pi CM5** app processor for sensor fusion
  and classifier inference (non-safety path).
- Inputs: 4 × ultrasonic (analog-in per channel), radar
  (CAN-FD), stereo camera (MIPI-CSI to CM5), LIDAR (Ethernet,
  optional).
- Outputs: a single `ObstacleVerdict` bus message published
  every 50 ms, evaluated into the main T-ECU/S 2oo2 chain as
  a *brake-demand* input. Verdict `Emergency` → EB via the
  same 2oo2 AND-gate relay stage as the ATP.

Two T-OBS modules per trainset, one at each end. Only the
leading end's verdict is active; the trailing module
self-tests and publishes an `Inactive` status.

Detailed hardware spec lives at
[`hardware/t-obs/schematics/v2-spec/`](../../hardware/t-obs/schematics/v2-spec/)
(scaffold only; v3 KiCad capture per RFC 0007 v3 rollout).

### 5.3 Passenger emergency intercom

Every car carries at least 4 passenger emergency intercoms
(one per car end, both doors). Pressing an intercom:

1. Triggers an immediate brake application to 50 % braking
   effort (not EB) — the trainset slows to a controlled stop
   at the next station.
2. Opens an audio + video channel to OCC remote-assist.
3. Logs the event to `osr-event-recorder` with timestamp,
   car id, and intercom id.

OCC can release the hold and resume normal operation remotely,
or escalate to full EB if the situation warrants.

**Why braking to the next station, not EB:** unplanned EB in
a driverless trainset with no driver to manage the aftermath
strands the passengers between stations — a self-inflicted
mass-incident risk. Braking controlled to the next station
puts the passengers where they can be helped.

### 5.4 Platform screen doors upgraded to mandatory

In the GoA 2 model, PSDs were optional for `halt` archetype.
In the GoA 4 default, **PSDs are mandatory at every station
with passenger boarding** — no driver means no human last-line-
of-defence between a passenger and the track. RFC 0010 v2.1
will reflect this.

**Exception:** `depot-terminal` platforms accessible only by
staff do not require PSDs; staff training (M1) substitutes.

### 5.5 Enhanced CCTV coverage

Every car carries at least 4 cabin cameras, live to OCC.
Platform cameras already exist per RFC 0010; coverage is now
contiguous end-to-end so OCC can see any point in the system
on demand.

## 6. Safety case

### 6.1 Equivalence claim

The driverless trainset achieves **safety equivalence to GoA 2
operation with a trained driver** through:

- **SIL-4 obstacle detection** replacing driver's-eye
  detection, with a lower false-negative rate on rail-relevant
  obstacle classes (validated against a 10 000-object test set
  during type certification).
- **Lower reaction latency** (radar-to-brake ~50 ms vs typical
  driver reaction of 1.5 s).
- **No fatigue, no distraction, no panic.** Driverless trains
  don't miss red signals because they were texting. The
  statistical argument is well-established in global metro
  operations (DLR, Copenhagen, Singapore NSL all GoA 4 with
  better safety records than GoA 2 fleets).

### 6.2 New SIL-4 claims for the safety case

RFC 0015 adds five safety goals to the `osr-safety-case` GSN
tree:

| Goal | Claim | Evidence |
|---|---|---|
| **G15** | `osr-obstacle-detect` produces `Emergency` verdict when any sensor reports an obstacle inside the current stopping-distance envelope | O1 Kani harness + 500-case proptest |
| **G16** | Sensor disagreement between the 2oo2 channels produces `Emergency` (fail-restrictive) | O3 Kani harness |
| **G17** | Stale sensor data (> 100 ms since last update) produces `Emergency` | O2 Kani harness |
| **G18a** | With every long-range sensor offline above 40 km/h, the verdict is `EmergencyBrake` | O4a Kani harness |
| **G18b** | With LIDAR offline (radar healthy), the verdict is at least `RestrictedSpeed` and never `EmergencyBrake` from the O4 branch alone | O4b Kani harness |
| **G19** | Passenger-intercom-triggered stop is delivered within 3 s of press | O5 integration test against `osr-sim` |

### 6.3 Residual risks explicit

Driverless operation carries residual risks that GoA 2 mitigates
via the driver. Each one is explicitly acknowledged:

- **Obscured obstacle above sensor plane** (e.g., a person
  standing upright but only the torso is visible above the
  platform edge): mitigated by PSD mandatory (§5.4) +
  ultrasonic under-body sweep at platform approach.
- **Suicide on track**: the most common rail-fatality mode in
  the industry, driverless or not. Not uniquely worsened by
  driverless; PSDs eliminate the station-platform variant
  entirely.
- **Slipping rail, wheelspin**: detected by `osr-odometry`
  slip-flag, triggers EB. No driver judgement involved.
- **Terrorism / sabotage on track**: track-intrusion detection
  at wayside (out of RFC 0015 scope; RFC 0016 candidate).
- **Passenger medical emergency mid-journey**: intercom to OCC,
  OCC dispatches medical at next station. GoA 2 driver would
  radio the same dispatcher.

### 6.4 Certification pathway

Type certification to EN 62267 (UGTMS — Urban Guided Transport
Management + Command/Control Systems) at GoA 4 is the target.
Each deployment additionally certifies to the local regulator
(NRSA equivalent).

The certification package draws from the existing safety-case
tree plus the five new goals in §6.2.

## 7. Operations implications

### 7.1 Driver rulebook (RFC 0013 §4.1) → deprecated for GoA 4

Every rule in D1–D8 is either:

- Automated (depot power-on D1.1 → onboard sequence), or
- Transferred to OCC (emergency plunger D7.1 → intercom to OCC
  via §5.3), or
- Transferred to station staff (dwell supervision D4.4 → T2.3).

RFC 0013 is amended to mark D1–D8 as "GoA 2 historical reference;
retain for mixed-fleet operations only."

### 7.2 OCC role expands

The OCC gains two new staff roles (amendment to RFC 0013 §4.5
C1):

- **Remote-assist operator.** Handles passenger intercom calls,
  takes manual override of a stopped trainset if needed, and
  coordinates with emergency services for on-board medical
  events. One operator per 5–10 trainsets in service.
- **Fleet-health supervisor.** Monitors the live CCTV + sensor
  feeds for trainset anomalies (smoke, unusual passenger
  behaviour, unattended items) that a driver would previously
  have noticed.

### 7.3 Station staff role expands

Station-staff T2 (Passenger boarding) gains two additional
responsibilities:

- **Platform dispatch ready-check.** Staff confirm PSD closed +
  platform clear before the dispatch signal is released. This
  substitutes for the driver's final platform check (D4.5).
- **Boarding assistance.** Staff are now the sole human presence
  during boarding; wheelchair assist, passenger inquiries, and
  boarding-rate management all sit at platform level.

### 7.4 No loss of safety personnel — they move where risk is

The driverless pivot does not reduce safety staffing. The
heads-per-hour shifted from driver-in-cab to OCC + platform:
same people, different posts, generally safer posts.

## 8. Rolling-stock implications (amends RFC 0008)

### 8.1 Cab eliminated

- Front wall: just a nose cone with the §5.1 sensor cowl + a
  coupler interface.
- No windscreen, no DMI, no master controller, no cab door,
  no cab HVAC, no rear-view mirror.
- Both ends of the trainset are symmetric — no leading / trailing
  distinction at the rolling-stock level.

### 8.2 Recovery-mode lockable cabinet

Every trainset retains a **recovery-mode keyswitch cabinet** —
a steel-locked enclosure behind the nose, accessible only with
a physical key held by depot recovery crew. Inside:

- A wired pendant with: forward / reverse select, 0–15 km/h
  throttle, emergency stop.
- The keyswitch enables a slow-speed (≤ 15 km/h) manual move
  that ignores ATO / ATP — used only to push a stuck trainset
  off a block for rescue-coupling (D7 / M6).

This is the only manual-control path. It is physical, locked,
slow-speed, and single-purpose. No full cab required.

### 8.3 Floor plan extends to both ends

Passenger seating extends to the full car length. The additional
~3 m × 2.4 m of floor at each end of the lead + rear cars =
about 14 extra seats per trainset on the `light-metro-3car`
family.

### 8.4 Mass + capex savings (per trainset)

Rough figures for the `light-metro-3car` reference:

| Item | Saved mass (kg) | Saved capex (USD) |
|---|---|---|
| Cab structure (front wall, door, windscreen) | ~800 | ~$33 000 |
| Cab controls + DMI + wiring | ~150 | ~$87 000 |
| Cab HVAC | ~120 | ~$16 000 |
| Cab seat + interior trim | ~80 | ~$9 000 |
| Mirror / wiper / horn package | ~40 | ~$4 000 |
| Cab lighting + accessories | ~20 | ~$3 000 |
| **Total** | **~1 210 kg / cab × 2 cabs** | **~$150 k × 2** |
| **Added (T-OBS + sensors + intercoms)** | ~60 kg × 2 ends | ~$27 k × 2 |
| **Net** | **~2 300 kg saved** | **~$250 k saved** |

## 9. Hardware implications (amends RFC 0007)

A new host class **T-OBS** joins the palette:

| Class | SoC | Role |
|---|---|---|
| T-ECU/S | 2× RP2350 + RPi CM5 | Train safety kernel (ATP, brake, etc.) |
| T-ECU/A | RPi CM5 | Train application (TCMS, PIS, TCN) |
| **T-OBS** | **2× RP2350 + RPi CM5** | **Obstacle detection + sensor fusion** |
| W-SBC | Radxa CM5 | Wayside |
| S-SBC | RPi CM5 | Station |

T-OBS is two modules per trainset (one at each end). Architecture
and PCB family are re-used from T-ECU/S; only the carrier board
(sensor breakouts, CAN-FD transceiver, analog-in front-end,
MIPI-CSI camera headers) differs.

## 10. Software implications (amends RFC 0005)

### 10.1 New crate

**`osr-obstacle-detect`** — pure-function SIL-4 evaluator. Runs
on T-OBS. Takes a `SensorFrame` (ultrasonic ranges × 4, LIDAR
return list, radar return list, camera classifier output),
current train speed, current Movement Authority end, and the
peer-channel clear bit, and returns an `ObstacleVerdict`:

```rust
enum ObstacleVerdict {
    Clear,
    RestrictedSpeed,   // ATO caps at 40 km/h (LIDAR degraded)
    CrawlOnly,         // ATO caps at 15 km/h (soft obstacle)
    EmergencyBrake,
}
```

Verdicts are strictly ordered by severity: `Clear <
RestrictedSpeed < CrawlOnly < EmergencyBrake`. A detection
inside the envelope can only escalate severity; a clearer
sensor frame can only de-escalate.

Five SIL-4 safety properties (O1, O2, O3, O4a+O4b, O5) mapped
to Kani harnesses; proptest coverage across the same properties.

### 10.2 Crates demoted to "GoA 2 only"

- **`osr-vigilance`** — kept in tree, marked optional.
- **`osr-dmi`** — kept in tree, marked optional. Passenger
  display functions already split out to `osr-pis-onboard` so
  this crate is truly cab-only.

A workspace feature flag `goa2-cab` (additive, opt-in) is the
canonical switch for legacy fleets. The new
[`osr-trainset-image`](../../crates/osr-trainset-image/) integrator
crate is the single entry point: it re-exports the always-on
onboard stack (ATP, ATO, brake, derailment, door-control, fire-
safety, obstacle-detect, odometry, TCMS) and gates
[`osr-dmi`] + [`osr-vigilance`] behind `--features goa2-cab`.
`cab_profile()` returns `CabProfile::Unattended` in the default
build and `CabProfile::Cabbed` when the flag is enabled — a
compile-time witness for the RFC 0015 "GoA 4 by default" claim.

## 11. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | `osr-obstacle-detect` crate at [`crates/osr-obstacle-detect/`](../../crates/osr-obstacle-detect/) — SIL-4 pure-function evaluator with O1/O2/O3/O4a/O4b/O5 Kani harnesses + 8 proptests (26 tests total); GSN safety-case goals G15–G19 at [`docs/safety-case/gsn/60-obstacle-detect.toml`](../safety-case/gsn/60-obstacle-detect.toml) close against real Kani + proptest evidence (done 2026-04-22). | v0 |
| **v2** ✅ | `osr-sim` shadow onboard stack now calls `osr_obstacle_detect::evaluate` at every tick: each `OnboardShadow` carries an `obstacle_out` field, feeds an all-clear synthetic `SensorFrame` into the evaluator, and threads `ObstacleVerdict::EmergencyBrake` through `BrakeInputs::obstacle_emergency` into the existing emergency-source union. Per-verdict tick counters roll up in `OnboardSummary::total_obstacle_{restricted,crawl,emergency}_ticks`; the simulator summary prints them under "Onboard shadow stack". `BrakeInputs`, `EmergencySources` (in both `osr-brake` and `osr-tcms`), and the brake evaluator carry `obstacle_emergency` end-to-end. **v2.1 (2026-04-23):** scenario-driven sensor-fault injection — four new `FaultKind` variants (`LidarOffline`, `RadarOffline`, `UltrasonicChannelStale`, `ObstaclePeerDisagreement`) with per-train + fleet-wide scope; parser in `scenario_file.rs`; a demonstrator fault-injection scenario exercises every O-series path through the shadow stack. Run confirms RestrictedSpeed / EmergencyBrake verdicts fire and flow through the emergency-source union without invariant violations. (done 2026-04-23) | v1 |
| **v3** ✅ | T-OBS v2 schematic specification at [`hardware/t-obs/schematics/v2-spec/`](../../hardware/t-obs/schematics/v2-spec/) — block diagram + per-rail power budget + safety-nets with 2oo2 AND-gate design + RP2350 A/B pinouts + 12-entry M12 connector table (done 2026-04-22). KiCad capture is v3.1, deferred alongside the RFC 0007 hardware KiCad rollout. | v0 |
| **v4** ✅ (v1) | Type-certification pre-submission pack at [`docs/certification/`](../certification/) — README + system-description + safety-requirements (SR-01..SR-24) + hazard-log (17 hazards, 7 classes) + evidence-register + EN 62267 clause-by-clause compliance-matrix. Every SR cross-referenced to a Kani harness / proptest / GSN goal / rulebook rule. Remaining for v4.1 (open): residual-risk narrative, per-clause compliance prose for §5–§9, and independent-assessor review (deployment-partner scope). (done 2026-04-23) | v2, v3 |
| **v5** | First driverless revenue service on an OSR deployment instance | v4 |

## 12. Relationship to existing RFCs

- **RFC 0003 (Samawah worked instance)** — shows how one city can
  instantiate the GoA 4 operating model.
- **RFC 0005 (SBC software architecture)** — crate map amended
  in §10.
- **RFC 0007 (hardware reference designs)** — new T-OBS class in
  §9.
- **RFC 0008 (rolling stock)** — cab elimination in §8.
- **RFC 0010 (station design standard)** — PSDs become
  mandatory (§5.4); v2.1 amendment.
- **RFC 0013 (operations rulebook)** — driver section deprecated,
  OCC and station staff absorb (§7).

## 13. What this RFC does NOT include

- Automated track-intrusion detection at wayside — covered by
  [RFC 0016](0016-wayside-track-intrusion.md).
- Autonomous platform-side boarding (still a human station-staff
  function; automation would require RFC 0015.1).
- Retrofit path for legacy cabbed trainsets — if an operator
  already has GoA 2 fleet, the retrofit cost is likely higher
  than just running it out to end-of-life alongside a new
  GoA 4 fleet.
- Autonomous depot shunting under GoA 4 (treated as a separate
  RFC scope because the obstacle-detection envelope at depot
  speeds is different).

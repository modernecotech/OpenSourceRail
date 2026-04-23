# Hazard log

GoA 4 Unattended Train Operation hazards identified against the
system boundary in [system-description.md](system-description.md).
Organised by hazard class: collision, runaway, derailment,
passenger-boarding, fire, sabotage, data-integrity.

Each row carries:

- **Severity** — using the EN 50126 scale: Catastrophic (multiple
  fatalities) / Critical (single fatality or multiple serious
  injuries) / Marginal (single serious injury or multiple minor)
  / Insignificant.
- **Frequency without controls** — order-of-magnitude estimate for
  how often the hazard would occur absent any mitigation.
- **Residual frequency** — the frequency that remains once the
  listed controls are in place; the residual-risk narrative
  in [residual-risk.md](residual-risk.md) argues the residual is
  tolerable.
- **Mitigating controls** — cross-referenced to requirements and
  artefacts.

Frequencies are expressed on a qualitative EN 50126 scale:
**Frequent** (≥ 1/yr) / **Probable** (1/10 yr) / **Occasional**
(1/100 yr) / **Remote** (1/1 000 yr) / **Improbable** (1/10 000 yr)
/ **Incredible** (< 1/10 000 yr).

## H-CO — Collision hazards

### H-CO-01 — Rear-end collision between two trains

| Field | Value |
|---|---|
| Description | Two trains occupy the same block; the following train collides with the leading. |
| Severity | Catastrophic |
| Frequency without controls | Frequent |
| Controls | SR-01 section-occupancy gate; SR-02 MA validity window; SR-03 MA conservatism; 2oo2 AND-gate at brake actuator (SR-20). |
| Residual frequency | Incredible |

### H-CO-02 — Head-on collision through mis-set switch

| Field | Value |
|---|---|
| Description | Switch commanded Normal but observed Reverse (or Unknown); train enters a conflicting route. |
| Severity | Catastrophic |
| Frequency without controls | Probable |
| Controls | `osr-wayside-points` 2oo2 sensor fusion; `osr-interlocking::section_available_to` checks switch state before MA grant; fail-restrictive `Unknown` classification. |
| Residual frequency | Incredible |

### H-CO-03 — Collision with obstacle on track (debris, vehicle, person)

| Field | Value |
|---|---|
| Description | A person, animal, car, or large debris enters the track envelope between trains; next train hits it. |
| Severity | Critical to Catastrophic |
| Frequency without controls | Occasional (target climate: dust storms deposit debris; urban ROW crossings possible) |
| Controls | SR-07 wayside intrusion gate (proactive — RFC 0016); SR-04 onboard obstacle detection (reactive — RFC 0015); SR-24 PSDs at every boarding platform; physical fence (deployment civil scope). |
| Residual frequency | Remote |

### H-CO-04 — Collision with a track worker under MaintenanceOverride

| Field | Value |
|---|---|
| Description | Track worker on foot under an active `MaintenanceOverride`; train enters the blocked section. |
| Severity | Critical |
| Frequency without controls | Probable |
| Controls | SR-01 section-occupancy gate refuses MA on any section carrying an active override; protection signals (RFC 0013 S5.3); physical trap point (site-specific); 30-minute block-renewal cadence (S5.4) catches silent over-runs. |
| Residual frequency | Incredible |

## H-RA — Runaway hazards

### H-RA-01 — Runaway on grade after brake release

| Field | Value |
|---|---|
| Description | Train parked on a grade; parking brake fails or is released in error. |
| Severity | Catastrophic |
| Frequency without controls | Occasional |
| Controls | Parking-brake engagement below `park_brake_max_speed_mmps` (SR-20 `osr-brake` B5 property); EB latches on any monitor trip; both SIL-4 channels required to release. |
| Residual frequency | Improbable |

### H-RA-02 — Overspeed through brake failure

| Field | Value |
|---|---|
| Description | Train exceeds the civil-speed envelope due to a regen/friction-blend failure. |
| Severity | Critical |
| Frequency without controls | Occasional |
| Controls | ATP overspeed trip (SR-03); regen-shortfall falls back to friction; WSP subtractive-only (B4). |
| Residual frequency | Remote |

## H-DE — Derailment hazards

### H-DE-01 — Derailment through undetected switch Unknown

| Field | Value |
|---|---|
| Description | Switch observation fails or reads `Unknown`; train enters the switch without MA. |
| Severity | Catastrophic |
| Frequency without controls | Probable |
| Controls | Switch observation fail-restrictive (`Unknown` rejects MA); `osr-wayside-points` 2oo2 sensor fusion; RFC 0013 M4 30-day switch inspection. |
| Residual frequency | Incredible |

### H-DE-02 — Derailment through lateral forces

| Field | Value |
|---|---|
| Description | Excessive lateral acceleration (track-twist, excessive speed into curve) causes derailment. |
| Severity | Catastrophic |
| Frequency without controls | Occasional |
| Controls | SR-11 onboard derailment monitor (`osr-derailment`); RFC 0013 M3 track-geometry inspection cadence (90/60/45 days per preset); RFC 0009 preset-bounded curve radius + cant. |
| Residual frequency | Improbable |

## H-PB — Passenger-boarding hazards

### H-PB-01 — Passenger struck by closing doors

| Field | Value |
|---|---|
| Description | Door closes on a passenger limb / bag. |
| Severity | Marginal (rare Critical) |
| Frequency without controls | Frequent |
| Controls | SR-09 door-obstruction motor-current + sensor; reopen on detection; SR-08 closing-interlock above 5 km/h. |
| Residual frequency | Remote |

### H-PB-02 — Passenger falls between platform and train

| Field | Value |
|---|---|
| Description | Passenger falls into the platform gap during boarding. |
| Severity | Critical |
| Frequency without controls | Frequent (legacy no-PSD metros) |
| Controls | SR-24 PSDs at every boarding platform; RFC 0010 platform-gap design; station-staff T2 supervision. |
| Residual frequency | Improbable |

### H-PB-03 — Train departs with passenger caught in door

| Field | Value |
|---|---|
| Description | Passenger's limb / bag remains trapped in closed door; train begins to move. |
| Severity | Critical |
| Frequency without controls | Probable |
| Controls | SR-09 door-sensor + SR-08 interlock; station-staff T2.5 platform-clear confirmation at non-PSD stations; PSD interlock at PSD stations (SR-24). |
| Residual frequency | Improbable |

## H-FI — Fire hazards

### H-FI-01 — Battery thermal runaway

| Field | Value |
|---|---|
| Description | Cell thermal runaway propagates to adjacent cells; fire on-board. |
| Severity | Critical |
| Frequency without controls | Occasional |
| Controls | SR-12 onboard fire detection + suppression; BMS thermal cutoff + cell-out derating; Na-ion chemistry has lower runaway risk than LFP and significantly lower than NMC. |
| Residual frequency | Remote |

### H-FI-02 — Electrical fire in traction inverter

| Field | Value |
|---|---|
| Description | Short or arc in the SiC inverter; fire. |
| Severity | Critical |
| Frequency without controls | Occasional |
| Controls | SR-12; `osr-traction` isolation on fault; RFC 0008 §3 EN 45545 HL2 R1 material compliance. |
| Residual frequency | Remote |

## H-SA — Sabotage + intrusion hazards

### H-SA-01 — Deliberate obstacle placement on track

| Field | Value |
|---|---|
| Description | Attacker places a large obstacle on the ROW between trains. |
| Severity | Critical to Catastrophic |
| Frequency without controls | Occasional |
| Controls | SR-07 wayside intrusion gate (proactive, detects placement); SR-04 onboard obstacle detection (reactive); fence-line contact detection (RFC 0016 fence sensor); CCTV coverage. |
| Residual frequency | Remote |

### H-SA-02 — Station-platform intrusion

| Field | Value |
|---|---|
| Description | Attacker gains access to the trackside from a platform. |
| Severity | Critical |
| Frequency without controls | Probable (stations are public) |
| Controls | SR-24 PSDs block direct platform → trackside access; station-staff T2.1 platform walk; CCTV. |
| Residual frequency | Remote |

## H-DI — Data-integrity hazards

### H-DI-01 — Forged consensus entry

| Field | Value |
|---|---|
| Description | Attacker with network access injects a forged `SectionIntrusion::Clear` or `RouteGrant`. |
| Severity | Critical to Catastrophic (depends on forged content) |
| Frequency without controls | Remote (requires network access + cryptographic sophistication) |
| Controls | SR-22 consensus entry authenticity (RFC 0017 — library in tree, v2 wiring open); physical network isolation (deployment scope); IEC 62443-4-2 component-level controls. |
| Residual frequency | Improbable (after SR-22 v2) / Remote (today, pending SR-22 wire integration) |

### H-DI-02 — Replay of a valid entry

| Field | Value |
|---|---|
| Description | Attacker replays an old `RouteRelease` or `MaintenanceOverride` at an inconvenient time. |
| Severity | Critical |
| Frequency without controls | Remote |
| Controls | Derived-state fold is idempotent in `entry_id` (RFC 0017 §3.4); 60 s freshness window on timestamp_ns; Raft already rejects duplicate entry_ids. |
| Residual frequency | Improbable |

## Hazard summary

| Class | Count | Worst-case severity | After controls |
|---|---|---|---|
| Collision | 4 | Catastrophic | Incredible–Remote |
| Runaway | 2 | Catastrophic | Improbable–Remote |
| Derailment | 2 | Catastrophic | Incredible–Improbable |
| Passenger-boarding | 3 | Critical | Improbable–Remote |
| Fire | 2 | Critical | Remote |
| Sabotage / intrusion | 2 | Catastrophic | Remote |
| Data integrity | 2 | Catastrophic | Improbable |
| **Total** | **17** | | |

Every hazard carries ≥ 2 independent controls. No single
control failure produces a single-fault hazard of residual
frequency worse than **Remote**.

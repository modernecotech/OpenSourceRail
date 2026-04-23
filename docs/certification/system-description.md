# System description

## 1. What OSR is

OpenSourceRail is an open-source urban-rail technology stack —
software + hardware reference designs + operational rules — sized
for GoA 4 (Unattended Train Operation) light-metro and metro
deployments. The Samawah reference ([RFC 0003](../rfcs/0003-samawah-reference-deployment.md))
instantiates the stack against a 30 km two-line network
(12 km radial + 16 km ring + 2 interchanges, 22 stations, 10
trainsets) built for a mid-size city in a hot-arid climate.

The stack is the entirety of a modern metro:

- **Rolling stock** — cabless (RFC 0015), four consist families
  (tram-2car through metro-6car) per RFC 0008.
- **Track** — four geometry presets per RFC 0009 covering gauge
  1435 mm, radius, grade, cant, and rail profile.
- **Civil** — at-grade + elevated + bridge only per RFC 0011; no
  tunnels.
- **Stations** — six archetypes per RFC 0010, prefab steel-
  portal + solar-canopy with no station building.
- **Signalling** — distributed consensus-based interlocking per
  RFC 0001, no central CBTC zone controller.
- **Energy** — catenary-free; onboard Na-ion/LFP batteries +
  station/depot PV per RFC 0002.
- **Operations** — one shared ≤ 60-page rulebook across four
  role families per RFC 0013.

For the safety claim of this pack, the relevant subset is the
SIL-4 + SIL-2 code running on four onboard + wayside host
classes:

- **T-ECU/S** — onboard safety kernel (2× RP2350 + RPi CM5 in
  2oo2), runs `osr-atp`, `osr-brake`, `osr-derailment`,
  `osr-door-control`, `osr-fire-safety`, `osr-odometry`.
- **T-ECU/A** — onboard application tier (RPi CM5), runs
  `osr-ato`, `osr-tcms`, `osr-event-recorder`, `osr-tcn`.
- **T-OBS** — onboard obstacle detector (RFC 0015), runs
  `osr-obstacle-detect`.
- **W-SBC** — wayside SBC (Radxa CM5 industrial), runs
  `osr-interlocking`, `osr-consensus`, `osr-wayside-points`,
  `osr-intrusion-detect` (RFC 0016).

## 2. System boundary

### 2.1 In scope for this certification

The OSR safety claim covers:

- **Onboard safety chain** — from sensor-fusion position through
  ATP envelope computation to brake command actuation.
- **Wayside safety chain** — from track-occupancy + switch-
  observation + intrusion detection through MA computation to
  MA delivery to the train.
- **Distributed signalling consensus** — the Raft-derived
  consensus protocol that keeps the wayside state machines
  coherent across nodes.
- **Obstacle detection + intrusion detection** — the RFC 0015
  onboard sensor fusion and RFC 0016 wayside sensor fusion that
  together substitute for a driver's-eye detection.
- **Operational rules** — the RFC 0013 rulebook that binds the
  safety-case solutions to human procedures (dispatcher,
  station staff, maintenance, OCC).

### 2.2 Out of scope for this certification

- **Crashworthiness** — EN 15227 certification is the rolling-
  stock builder's scope (RFC 0008 §3).
- **Fire-protection material performance** — EN 45545 is
  material-certification scope.
- **Civil structure** — structural engineering of elevated
  viaducts and at-grade formation is the deployment partner's
  civil scope (RFC 0011).
- **Electrical supply** — MV/LV distribution from the grid
  connection to the rectifier substation is the deployment
  partner's electrical scope.
- **Cybersecurity above SIL-2** — IEC 62443-4-2 message
  authentication is in tree at SIL-2 (RFC 0017) and integrates
  as complementary evidence; component-level cybersecurity
  certification is tracked separately from EN 62267.

## 3. Operational envelope

- **Maximum civil speed:** 80 km/h (22 m/s) at `standard-urban`
  preset; 100 km/h on `mainline-mixed`.
- **Minimum curve radius:** preset-dependent per RFC 0009 §1.
- **Maximum gradient:** preset-dependent per RFC 0009 §1.
- **Climate envelope:** −10 °C to +55 °C ambient per RFC 0003
  §4.5 (deployment-adaptable).
- **Crashworthiness envelope:** EN 15227 Cat C-II up to 25 km/h
  metro-to-obstacle collision.
- **Communication envelope:** 5G primary + LoRa backup for TRG;
  Cat 6a + TSN for wayside back-office (RFC 0005 §5).

Operation outside any of these envelopes triggers a degraded-
mode response per RFC 0013 §5 — the deployment continues safely
at reduced performance; no passenger is carried under a
violated envelope.

## 4. Interfaces to the external world

- **Passengers** — at station platforms (PSDs per RFC 0010) and
  inside the trainset (seats, doors, emergency intercoms per
  RFC 0015 §5.3).
- **Track workers** — via `MaintenanceOverride` grants issued
  from OCC per RFC 0013 S5; physical protection signals per
  RFC 0013 S5.3.
- **Emergency services** — via OCC radio liaison per RFC 0013
  C2.4; passenger emergency intercom direct to OCC per
  RFC 0015 §5.3.
- **National safety authority** — via the OCC incident-
  notification path per RFC 0013 S3.5 (I5 within 2 h, I6
  immediately).
- **Power grid** — at each rectifier substation, bidirectional
  per RFC 0002 §6.
- **OSM + Civil 3D / OpenRail / Trimble** — design-time only,
  via the OSR-ALN alignment interchange format (RFC 0009 v2).

## 5. Non-interfaces

OSR does not interface with:

- **Third-party CBTC zone controllers** — RFC 0001 replaces
  them with distributed consensus.
- **Legacy MVB/WTB trainbus** — RFC 0006 replaces with TCN-E
  (TSN Ethernet).
- **Magnetic smartcard fare systems** — RFC 0013 and
  `osr-afc` use account-based mobile money + QR.
- **GSM-R radio** — RFC 0007 uses 5G + LoRa.
- **Catenary power distribution** — RFC 0002 is onboard-
  battery-only.

A deployment that must interface with any of the above forks
the repository — no upstream compatibility is offered.

## 6. Quantitative footprint

| Metric | Value |
|---|---|
| Rust crates in the safety-relevant workspace | 51 |
| Total Rust tests, current workspace | 705 |
| SIL-4 evaluators with Kani harnesses | 8 (`osr-atp`, `osr-brake`, `osr-vigilance`, `osr-odometry`, `osr-wayside-points`, `osr-interlocking`, `osr-obstacle-detect`, `osr-intrusion-detect`) |
| GSN goals currently closed against evidence | G1–G27 across 8 TOML files under `docs/safety-case/gsn/` |
| Operations rulebook page count (target) | ≤ 60 |
| Operations rulebook role families | 5 (driver GoA 2 legacy; dispatcher, station-staff, maintenance, control-centre in GoA 4 default) |

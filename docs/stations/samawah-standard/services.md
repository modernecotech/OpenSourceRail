# Station services — Samawah `standard` archetype

HVAC, lighting, fire, drainage, signage — the MEP (mechanical /
electrical / plumbing) envelope for the station.

Per RFC 0010 §11 an outdoor Samawah station is passively cooled
by the canopy. Only enclosed spaces (ticket hall, lift rooms,
services cabinet) get mechanical HVAC.

## HVAC (ticket hall only)

- **System:** split-type air conditioner, 12 kW cooling (covers
  120 m² ticket hall + lift rooms at design ambient 50 °C).
- **Refrigerant:** R-32 (commodity).
- **Fresh-air intake:** 10 % OA per ASHRAE 62.1.
- **Heating:** none — Samawah sees ≥ 5 °C ambient year-round;
  if used, reverse-cycle heat pump on the same unit.
- **Filters:** MERV 8 standard; MERV 14 for heavy-dust days per
  operator discretion.
- **Drain:** to condensate pipe → station storm drain.
- **Control:** `osr-station-scada` with operator override.

## Platform ventilation

**None.** Platform is open-air under the canopy. Natural
cross-ventilation works year-round; on haboob days, platform
shelter behind the canopy plus fare-gate doors to the enclosed
ticket hall (which has the AC).

## Lighting

Per EN 12464-2:

| Area | Illuminance | Colour temp | Control |
|---|---|---|---|
| Platform (night) | 100 lx | 4 000 K | Dusk-dawn sensor + schedule |
| Ticket hall | 300 lx | 4 000 K | Time schedule + occupancy |
| Platform (day) | canopy ambient | daylight | none |
| Stair + ramp | 100 lx | 4 000 K | Dusk-dawn + motion |
| Lift interior | 200 lx | 4 000 K | Always on when door is open |
| Emergency egress | 20 lx (1 h battery) | 4 000 K | EN 1838 self-test |
| Exterior approach | 50 lx | 4 000 K | Dusk-dawn |
| Services cabinet room | 500 lx | 4 000 K | Maintenance switch |

All LED, EN 61000-6-3 EMC class B. Total connected load per
station: ~4 kW.

## Fire + life safety

Per NFPA 130 + Iraqi national fire code (whichever is stricter):

- **Smoke detection:** aspirating detector in ticket hall + per
  lift room. Ceiling smoke detectors in services cabinet.
- **Heat detection:** per lift room (rate-of-rise).
- **Passive protection:** all materials per EN 45545 HL1 (one
  step below HL2 rolling stock since the station is outdoor).
- **Fire extinguishers:** 2× CO₂ at ticket hall, 1× water
  per platform end.
- **Fire alarm signal:** goes directly to the OCC via
  `osr-station-scada`; cannot be silenced without OCC OK.
- **Emergency power:** 1-hour UPS (60 kWh Li-ion battery in
  services cabinet) keeps PIS + emergency lighting + OCC comms
  alive.
- **Evacuation:** platform end stairs are the emergency path
  (per `envelope.md` §egress).

## Drainage

- **Platform:** 2 % transverse fall to centre trough drain;
  longitudinal 0.5 % fall to the low end.
- **Track drain:** centre trough between the two tracks, 300 mm
  wide, 400 mm deep, to perforated pipe below the ballast.
- **Canopy runoff:** gutter + downspout at each column base,
  discharges to station storm drain.
- **Ticket hall:** floor drain in the centre.
- **Capacity:** sized for 50 mm/h 10-year return storm. Samawah
  rarely hits this, but when a sandstorm is followed by rain,
  the first event of the year can overload the drain — catch
  pit at storm drain connection.

## Signage

- **External:** station name + route-map + OSR brand panel at
  each entrance.
- **Internal:** wayfinding per ISO 7001 pictograms; bilingual
  (Arabic + English) text. Signs at 2.5 m height (overhead)
  + 1.2 m height (lateral, for accessibility).
- **Line / route diagram:** strip map of Line 1 + Line 2 at
  every platform-edge support column.
- **Real-time information:** `osr-pis-station` drives the LED
  + LCD displays.
- **Emergency exit signs:** EN 1838 photo-luminescent + battery
  backup.

## Utilities

### Electrical

- Mains: 3-phase 400 V AC at 50 Hz from the municipal
  connection (or from the nearest `osr-energy-site` if in
  island mode).
- Connected load at peak: HVAC 12 kW + lighting 4 kW +
  services + fare equipment + PIS + lift ~10 kW = **~26 kW
  total**.
- Design demand: 30 kW + 50 % future-growth headroom = 45 kW
  incoming supply.
- Distribution: MCB board in the services cabinet, RCD-
  protected sub-circuits.

### Water + waste

- **Water:** town water for ticket-hall cleaning + condensate
  make-up; no drinking fountain at `standard` archetype.
- **Waste:** municipal connection for storm + sanitary
  (if the operator adds a future toilet).

### Communications

- Ethernet from the station's S-SBC to the OCC (primary + LoRa
  backup).
- CCTV camera feeds bonded to the station SCADA, then
  backhauled to OCC.

## Environmental

- Noise: platform ambient target ≤ 70 dB(A) day, ≤ 55 dB(A)
  night during no-train condition. Train pass-by peak
  ≤ 80 dB(A) per ISO 3095.
- Visual impact: canopy form factor + lighting strategy
  follow the operator's urban-design guidelines.

## v2 deliverables (not in v1)

- Detailed MEP drawings (plans + sections).
- Load schedule per sub-circuit.
- Fire-detection zone plan with alarm-panel layout.
- Lift-room machinery spec.
- PA loudspeaker aiming + acoustic coverage plots.

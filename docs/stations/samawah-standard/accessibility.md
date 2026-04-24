# Accessibility — Samawah `standard` archetype

Per RFC 0010 §7 + [`lib/templates/accessibility.toml`](../../../lib/templates/accessibility.toml).
Designed against EN 16586 (PRM — Persons with Reduced Mobility)
and the corresponding Iraqi accessibility overlay.

## Step-free path — requirements

Every passenger, including wheelchair users, must have a
step-free path from street to any door on any train:

1. **Street → Ticket hall:** ramp at max 1:12, with 1.5 m×1.5 m
   landings every 9 m. Samawah: typical site has ≤ 400 mm
   elevation delta between street and ticket-hall entrance →
   one 5 m ramp suffices.
2. **Ticket hall → Paid zone:** wide fare gate (min 900 mm
   clear, per RFC 0010 §8). One per direction on this archetype.
3. **Paid zone → Platform:** ramp or elevator. `standard`
   archetype has both (redundant path).
4. **Platform → Train:** 350 mm platform level = consist floor
   level (level boarding per RFC 0008 §3.3). 75 mm horizontal
   gap max with the retractable skirt on the consist. Wheelchair
   spaces in the train at door-2 of every car.

## Tactile paving

Per ISO 23599 / Iraqi national code:

- **Warning tactile:** 600 mm deep along the full platform edge.
  Bright-colour contrast against the platform deck for vision-
  impaired users.
- **Directional tactile:** 300 mm wide strips guiding from
  ticket hall to platform access points.
- **Landing tactile:** 1 500 × 1 500 mm at the top / bottom of
  ramps + stairs.
- **Lift approach:** tactile strip at lift-call button height.

## Audio + visual information

Per RFC 0010 §7:

- **Visual:** next-train display (dot-matrix LED + color LCD)
  on each platform at 2 m height, 3 units per platform at
  25 m intervals. Driven by `osr-pis-station`.
- **Audio:** PA speakers at 10 m intervals on each platform,
  weatherproof (IP65), driven by `osr-pis-station`. Volume
  capped at 85 dB(A) at 1 m to protect hearing.
- **Audio-visual synchronisation:** PA + visual announce the
  same next-train at the same time (tested in `osr-pis-station`'s
  proptest suite).

## Wheelchair spaces

- **On platform:** 1 marked wheelchair waiting area per 30 m of
  platform length. For 75 m platform: **2 marked areas per
  platform × 2 platforms = 4 per station**.
- **On train:** 2 wheelchair spaces per car × 3 cars = 6 per
  consist (per RFC 0008 §3.3).

Waiting area location: colocated with door 2 of the nearest
car when the train stops — so a wheelchair user doesn't have
to travel along the platform to reach the wheelchair-spaced
door.

## Lift per platform

Per RFC 0010 §5 — every archetype except `halt` gets one lift
per platform. Samawah `standard`:

- Type: Otis Gen3 (or local equivalent), MRL (machine-room-less).
- Car size: 1 100 × 1 400 mm, 630 kg rating.
- Doors: 900 mm clear, automatic open/close with wheelchair-
  button override.
- Height of controls: 900 mm from floor for accessibility.
- Voice announcement: floor-arrival and door-status.
- Braille on all buttons.

## Seating on platform

Per RFC 0010 §7 accessibility (only `halt` archetype omits):

- 3 × 2-seat benches per platform, anchored to the platform
  back wall (under the canopy).
- Armrest on aisle side to aid stand-up.
- No fixed leg-rests — interferes with wheelchair approach.

## Baggage + mobility aid storage

Not provided at `standard` archetype — passengers carry with
them. `major` and `interchange` archetypes add storage lockers
(v2 doc).

## Companion-animal policy

Service dogs unrestricted; other pets per operator policy
(Iraq typical: service dogs only). No rule in the archetype.

## Accessible toilet

Not at `standard` archetype (per-operator choice). `major` and
`terminal` archetypes have accessible toilets (v2).

## Emergency communication

- **Help buttons** on each platform at 2 m height, 25 m
  intervals — directly connected to the OCC via the station
  SCADA. Wheelchair-user reach height max 1 200 mm.
- **Help buttons in lifts** — voice intercom + visual status.
- **Audio-induction loop** at ticket-gate staff position for
  hearing-aid users.

## Compliance checklist (pre-opening)

| Item | Status at v1 |
|---|---|
| Step-free path from street to platform | ✓ specified |
| Platform-edge tactile paving 600 mm | ✓ |
| Directional tactile to platform | ✓ |
| Lift ≥ 1 100 × 1 400 mm | ✓ |
| Audio + visual PIS | ✓ |
| 2 wheelchair waiting areas per platform | ✓ |
| Wide fare gate ≥ 900 mm | ✓ |
| Accessible seating on platform | ✓ |
| Accessible help buttons | ✓ |
| Braille + raised-character signage | ✓ specified |
| Accessible toilet | n/a at `standard` archetype |
| Changing Places toilet | n/a at `standard` archetype (only at `major` / `terminal`) |
| Audio-induction loop at staffed position | ✓ specified |

## v2 deliverables (not in v1)

- Room data-sheet per staff position (reception, security).
- Signage typography + wayfinding ISO 7001 pictogram set.
- Accessibility-focused acceptance test with a local
  disability-rights advocacy group.

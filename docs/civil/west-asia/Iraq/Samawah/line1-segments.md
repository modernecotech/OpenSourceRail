# Samawah Line 1 — per-segment alignment table

Line 1 (Nahrain) is a 12-station radial line, west to east.
Every segment is `standard-urban` preset per RFC 0009 §1.
Direction of travel in this table is eastbound (forward).
Reverse-direction segments use a paired parallel track (double-
track per RFC 0009 §7.2).

**Station coordinates:** from [`design.toml`](../../../designs/west-asia/Iraq/Samawah/design.toml).
Bearings computed from great-circle deltas; horizontal radii at
waypoints computed from inter-segment bearing change
`R ≈ (L1 + L2) / (2 · tan(θ/2))`. Planning-grade numbers — a
surveyed alignment substitutes GNSS coordinates at v2.

## Segment table

| # | From → To | L (m) | Civil | Bearing (°) | Entry R (m) | Max grade (‰) | Max cant (mm) | Design speed (m/s) | Notes |
|---|---|---|---|---|---|---|---|---|---|
| L1-01 | samawah-rws → north-gate | 1 000 | at-grade | 128.7 | line start | 0 | 0 | 22 | From intercity RWS; at-grade boulevard running parallel to Mosul St. |
| L1-02 | north-gate → old-souq | 1 300 | elevated | 123.7 | 26 300 | 0 | 30 | 22 | Enters dense-souq block; viaduct per RFC 0011 §5. |
| L1-03 | old-souq → samawah-central | 1 100 | elevated | 115.8 | 17 400 | 0 | 30 | 22 | Elevated through commercial core. |
| L1-04 | samawah-central → riverside | 900 | at-grade | 106.9 | 12 900 | 0 | 0 | 22 | Re-enters at-grade after ramp down from old-souq viaduct. |
| L1-05 | riverside → eastern-bridge | 1 200 | bridge | 103.2 | 32 500 | 0 | 30 | 22 | Euphrates crossing — reference viaduct over water per RFC 0011 §6. |
| L1-06 | eastern-bridge → al-salam | 1 400 | at-grade | 105.1 | 78 000 | 0 | 0 | 22 | East bank, dedicated ROW parallel to the highway. |
| L1-07 | al-salam → governorate-hospital | 1 300 | at-grade | 105.2 | > 1 000 000 | 0 | 0 | 22 | Straight. |
| L1-08 | governorate-hospital → new-german-hospital | 1 500 | at-grade | 104.9 | > 1 000 000 | 0 | 0 | 22 | Straight. |
| L1-09 | new-german-hospital → engineering-quarter | 1 300 | at-grade | 103.9 | > 1 000 000 | 0 | 0 | 22 | Straight. |
| L1-10 | engineering-quarter → al-muthanna-university | 1 400 | at-grade | 106.3 | > 1 000 000 | 0 | 0 | 22 | Straight. |
| L1-11 | al-muthanna-university → east-depot | 600 | at-grade | 102.0 | 68 000 | 0 | 0 | 22 | Depot throat + buffer zone. |

**Total L1 length:** 13 000 m (matches design.toml). Civil mix:
**9 500 m at-grade (73 %) + 2 400 m elevated (18 %) + 1 200 m
bridge (9 %)**.

## Waypoints (curve apex details)

All curves on Line 1 are at radius > 12 000 m — well above the
`standard-urban` preset's 90 m minimum. Cant is 0 mm on the
straight-running at-grade segments (no lateral acceleration to
compensate). On the three viaduct segments (L1-02, L1-03, L1-05)
30 mm cant is specified at the transition curves to smooth
ride quality; this is well under the 150 mm preset maximum.

## Vertical alignment

Samawah sits on the Euphrates alluvial plain — elevation 6–10 m
above sea level across the full alignment. Grade assumed 0 ‰
everywhere; v2 surveyed alignment will refine with actual
elevation data. The only vertical feature is the viaduct ramp-
up / ramp-down at L1-02 and L1-05 entries and exits:

- L1-02 entry ramp (north-gate → viaduct): 0 ‰ at-grade → 35 ‰
  ramp over 150 m → level deck at 10 m ToR.
- L1-03 exit ramp (viaduct → samawah-central): level deck →
  35 ‰ descent over 150 m → at-grade.
- L1-04 exit / L1-05 entry (riverside → bridge): 10 ‰ approach
  grade, bridge deck level at 12 m ToR clearance over river.
- L1-05 exit (bridge → at-grade on east bank): 10 ‰ descent
  over 200 m.

All ramp grades ≤ 50 ‰ (preset max), with vertical-curve radii
≥ 0.4 · v² m = 194 m per RFC 0009 §6.

## Earthworks estimate

At-grade segments sit in very flat terrain. Preliminary cut /
fill volume budget:

- Samawah-rws → eastern-bridge: minor cut (≤ 1 m) for drainage.
- eastern-bridge → east-depot: minor fill (≤ 1 m) for ROW
  levelling.
- Viaduct segments: no earthworks (piers on pile foundations).

## Stopping distance check (sanity)

The `osr-atp` envelope per `light-metro-3car` emergency-brake
curve + EN 14363 headroom:

- From 22 m/s: stopping distance ≤ 175 m on level track.
- L1-11 (600 m, from 22 m/s into `depot-terminal`): plenty of
  brake distance. ✓
- Every inter-station segment ≥ 600 m: all allow a full-speed
  start + full-speed stop with margin. ✓

## Compliance summary (vs `standard-urban`)

Every segment passes the preset's constraints:

- **Min curve radius 90 m:** all Line 1 curves ≥ 12 000 m ✓
- **Max grade 50 ‰:** ramp grades ≤ 35 ‰ ✓
- **Max cant 150 mm:** max used 30 mm ✓
- **Design speed 22 m/s:** ✓ all segments

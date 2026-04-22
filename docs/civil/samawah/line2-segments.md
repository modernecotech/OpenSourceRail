# Samawah Line 2 — per-segment alignment table

Line 2 (Halqa) is a 10-station **ring** line,
counterclockwise from Eastern Bridge. Every segment is
`standard-urban` preset per RFC 0009. Two interchange points
with Line 1: `eastern-bridge` and `al-muthanna-university`.

**Station coordinates:** from [`design.toml`](../../../designs/middle-east/iraq/samawah/design.toml).

## Segment table

Ring sequence: eastern-bridge → northern-suburbs-a →
northern-suburbs-b → northwest-junction → industrial-west →
western-residential → south-west-residential → southern-markets
→ south-east-residential → al-muthanna-university → (ring
wrap) → eastern-bridge.

| # | From → To | L (m) | Civil | Bearing (°) | Entry R (m) | Max grade (‰) | Max cant (mm) | Design speed (m/s) | Notes |
|---|---|---|---|---|---|---|---|---|---|
| L2-01 | eastern-bridge → northern-suburbs-a | 1 800 | at-grade | 28 | ring start | 0 | 0 | 22 | Northbound from L1 interchange. |
| L2-02 | northern-suburbs-a → northern-suburbs-b | 1 500 | at-grade | 324 | 9 500 | 0 | 0 | 22 | Bearing swings NW — the first ring-curve apex. |
| L2-03 | northern-suburbs-b → northwest-junction | 1 700 | at-grade | 297 | 12 000 | 0 | 0 | 22 | Continues NW, reaches `northwest-junction` layup-minimal. |
| L2-04 | northwest-junction → industrial-west | 1 600 | at-grade | 240 | 4 300 | 0 | 20 | 22 | Ring apex — tightest curve; 4.3 km radius is still > 47× preset min. |
| L2-05 | industrial-west → western-residential | 1 500 | at-grade | 198 | 10 200 | 0 | 0 | 22 | Southbound. |
| L2-06 | western-residential → south-west-residential | 1 800 | at-grade | 180 | 15 000 | 0 | 0 | 22 | Due south. |
| L2-07 | south-west-residential → southern-markets | 1 400 | at-grade | 108 | 5 800 | 0 | 20 | 22 | Turns east. |
| L2-08 | southern-markets → south-east-residential | 1 600 | at-grade | 90 | 10 500 | 0 | 0 | 22 | Due east. |
| L2-09 | south-east-residential → al-muthanna-university | 1 500 | elevated | 36 | 5 900 | 0 | 20 | 22 | Approach to L1/L2 interchange; elevated over the engineering-quarter block. Per RFC 0010 §7 interchange = at-grade (L1) + elevated (L2). |
| L2-10 | (ring wrap) al-muthanna-university → eastern-bridge | 1 600 | at-grade | 286 | 7 800 | 0 | 0 | 22 | Closes the ring. Dedicated ROW returns at-grade. |

**Total L2 length:** 16 000 m (matches design.toml). Civil mix:
**14 500 m at-grade (91 %) + 1 500 m elevated (9 %) + 0 m
bridge**.

## Waypoints (curve apex details)

Line 2 has tighter curves than Line 1 because the ring
geometry forces direction reversals. The tightest is L2-04 at
4 300 m radius — still 47× the preset 90 m minimum. At 22 m/s
through a 4 300 m curve, centripetal acceleration is 0.11 m/s²
— imperceptible. A 20 mm cant at the tightest curves is a
ride-quality nicety, not a speed-safety requirement.

## Vertical alignment

Same assumption as Line 1: level terrain, grade 0 ‰ on all
at-grade segments. Ring-apex curves might need sub-1 ‰ drainage
slope; v2 surveyed alignment refines.

L2-09 (elevated to the interchange): 35 ‰ ramp up over 150 m
at the approach, level 10 m ToR deck at the al-muthanna-
university platform, 35 ‰ ramp down on the far side back to
at-grade for the ring wrap.

## Interchange compliance (L1/L2 at `eastern-bridge` + `al-muthanna-university`)

Per RFC 0010 §7 the interchange archetype is stacked
at-grade (L1) + elevated (L2):

- `eastern-bridge`: Line 1 crosses at **bridge** (over the
  Euphrates) at +12 m ToR. Line 2 approaches at at-grade.
  Interchange vertical circulation handles the ~12 m height
  delta (ramp + stair + escalator + lift, per RFC 0010 §5).
- `al-muthanna-university`: Line 1 at-grade at +0 m ToR; Line 2
  at elevated +10 m ToR. Interchange has the same vertical-
  circulation kit.

Both are RFC 0011 §7 compliant (never two elevated levels).

## Stopping distance check

Same envelope as Line 1. Every L2 segment ≥ 1 400 m is plenty
for the 175 m emergency-brake distance from 22 m/s.

## Compliance summary (vs `standard-urban`)

- **Min curve radius 90 m:** all Line 2 curves ≥ 4 300 m ✓
- **Max grade 50 ‰:** ramp grades ≤ 35 ‰ ✓
- **Max cant 150 mm:** max used 20 mm ✓
- **Design speed 22 m/s:** ✓

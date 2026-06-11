# `standard` archetype — envelope

Plan + section geometry of a Samawah `standard` station. Every
number here is a buildable dimension.

## Plan

```
    ROW:  ──────────── 12.5 m wide ────────────
                                                     (north)
           street           ┌───────────────────┐         ↑
    ════════════════════════╡   side platform 1 ├══════   │
                            │   (northbound)    │         │
                            └───────────────────┘         │
                        ═══════════════════════════════ track 1
                                                              ←── 75 m ──→
                        ═══════════════════════════════ track 2
                            ┌───────────────────┐
    ════════════════════════╡   side platform 2 ├══════
                            │   (southbound)    │
                            └───────────────────┘
    fare gates + TVMs on low plinths: west end of both platforms
                                                            (south)
```

- **Configuration:** two side platforms, double-track.
- **Platform length:** 75 m safeguarded Samawah build allowance.
  The generic `light-metro-3car` standard is 61 m (51 m consist
  + 10 m clearance); this package deliberately reserves more civil
  length for local clearance and later fleet growth.
- **Platform width:** 3.5 m each (per RFC 0010 §4.3).
- **Track centres:** 4.0 m (standard double-track with centre
  drain).
- **Total station ROW width:** 3.5 + 4.0 + 3.5 = 11.0 m;
  +1.5 m buffer for drainage + ROW-line clearance = **12.5 m**.
- **Pedestrian datum:** platform walking surfaces are flat with
  the adjacent footpath/forecourt. The rail datum drops through the
  station bay; passengers do not climb onto a raised platform.

## Section through platform

```
    ┌───────┐   canopy 2.2 m high above platform    ┌───────┐
    │       │                                         │       │
    │       │                                         │       │
    ▼       ▼                                         ▼       ▼
  ════════════════════════════════════════════════════════════
  pedestrian-grade platform / footpath slab (flat walking surface)
  platform edge  |←── 2 400 mm ──→| drainage | |←── 2 400 mm ──→|
       ToR 350 mm below slab       |   track 1       |   track 2       |
                 |                 |           |                 |
                 ═══════════ 1 435 mm gauge ═══════════
                    ↑                                 ↑
              rail profile UIC60                 rail profile UIC60
```

- Platform walking surface: flush with adjacent pedestrian pavement.
  Top-of-rail (ToR) sits 350 mm below that surface inside the drained
  guideway channel, matching the `light-metro-3car` low-floor height
  for level boarding without raising the platform above street level.
- Platform-to-track horizontal gap at door: ≤ 75 mm (UIC 741).
- Canopy clearance: 2 200 mm minimum height over the platform
  deck. Roof is at 3 800 mm above ToR (matches the consist's
  max height envelope).

## Sub-areas

| Area | Location | Size (m²) | Function |
|---|---|---|---|
| Platform 1 (northbound) | 75 m × 3.5 m | 263 | Passenger wait + board |
| Platform 2 (southbound) | 75 m × 3.5 m | 263 | Passenger wait + board |
| Cross-platform canopy | 85 m × 22 m | 1 870 | Solar canopy + rain shelter (incl. edges) |
| Fare/TVM plinths (west end) | 2 × 10 m × 2 m | 40 | Fare gates + TVMs + validator line |
| Services cabinet room | 4 m × 3 m | 12 | Station SCADA + sub-MSB + UPS |

**Total gross floor area:** ~530 m² open platform + ~50 m² compact
fare/services footprint. No default ticket hall, lift room, or stair
well is included for an at-grade `standard` station.

## Access modes (per RFC 0010 §5)

Each side platform has:

1. **Direct paved access** from the adjacent footpath/forecourt to
   the platform slab. Gradient is governed by the surrounding street,
   not by the station kit.
2. **Fare line / validator plinth** at the west end, with a wide
   gate and bypass gate for PRM users.
3. **Secondary direct egress** at the east end. If the station sits
   between roads, the crossing is protected and interlocked rather
   than grade-separated.

No lift, stair, escalator, or overbridge is part of the at-grade
`standard` archetype. Those are local overrides for elevated/stacked
stations or unavoidable road-barrier sites.

## Egress (per RFC 0010 §6 and NFPA 130 4-minute rule)

Platform occupancy sizing:

- Planning-grade peak: 150 passengers × 2 platforms = 300.
- NFPA 130 egress: must reach a "safe point" within 4 minutes.

Egress paths (per platform):

- Primary: direct west-end paved exit to the footpath/forecourt
  (≤ 11 m travel from the fare line).
- Secondary: direct east-end paved exit to the footpath/forecourt.

Effective egress width:
- West exit 2.0 m + east exit 2.0 m.
- **Total effective width: ≥ 4.0 m per platform.**

At 300 pax per platform and NFPA 130 flow 1.3 pax/m/s:
- Clearance time = 300 / (4.0 m × 1.3 pax/m/s) ≈ 58 s.
  Well under the 4 min target. ✓

## Fare paid / unpaid zones

- **Unpaid zone:** footpath/forecourt, TVMs, outside fare gates.
- **Paid zone:** everything platform-side of the fare gates.

`standard` archetype gets 2 fare-gate lanes per direction per
RFC 0010 §8 (so 4 total — 2 in, 2 out; 1 wide-gate for
wheelchairs). TVMs: 1 per direction (2 total).

## Property-line setbacks (for operator adaptation)

- ROW centreline to property line: ≥ 3 m both sides (municipal
  code typical).
- Ticket hall at west end can extend into unused ROW corners;
  operator adapts per parcel.
- If a constrained site can only accept one public entrance, keep the
  opposite platform end as a normally closed emergency gate. A
  `standard` archetype still requires at least 2 independent egress
  directions per platform.

## Site footprint

Total approximate footprint a `standard` station occupies on
the ground:

- Platform envelope: 75 × 12.5 = **940 m²** main rectangle.
- Fare/TVM west plinths: 40 m² inside the main rectangle.
- Service cabinet: 12 m² west-end addition if it cannot sit under
  the canopy.
- Canopy shadow (extends slightly beyond platform): 85 × 22 =
  1 870 m² — but this is the roof, not ground footprint.

**Usable ground footprint: ~950-1 000 m² per station.**

## Interface with the simulator

`osr-sim` consumes these archetype numbers via the
`lib/templates/stations.toml` schema. The v1 envelope does
not require any sim change; all parametric sizing already
lives in templates.

## What this doesn't commit to

- Façade finish (brick, stucco, aluminium panel — operator
  choice).
- Signage typeface / bilingual arrangement (operator choice).
- Paid-zone toilets or vending (operator discretion, not an
  archetype feature).
- Retail concessions (excluded from `standard`; see `major`
  archetype at v2).

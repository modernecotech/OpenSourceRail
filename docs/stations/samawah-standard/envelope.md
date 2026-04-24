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
    ticket hall + fare gates + TVMs: west end of both platforms
                                                            (south)
```

- **Configuration:** two side platforms, double-track.
- **Platform length:** 75 m (65 m consist + 10 m clearance).
- **Platform width:** 3.5 m each (per RFC 0010 §4.3).
- **Track centres:** 4.0 m (standard double-track with centre
  drain).
- **Total station ROW width:** 3.5 + 4.0 + 3.5 = 11.0 m;
  +1.5 m buffer for drainage + ROW-line clearance = **12.5 m**.

## Section through platform

```
    ┌───────┐   canopy 2.2 m high above platform    ┌───────┐
    │       │                                         │       │
    │       │                                         │       │
    ▼       ▼                                         ▼       ▼
  ════════════════════════════════════════════════════════════
  platform edge  |←── 2 400 mm ──→| drainage | |←── 2 400 mm ──→|
  350 mm ToR     |   track 1       |  centre   |   track 2       |
                 |                 |           |                 |
                 ═══════════ 1 435 mm gauge ═══════════
                    ↑                                 ↑
              rail profile UIC60                 rail profile UIC60
```

- Platform top: 350 mm above top-of-rail (ToR) — matches the
  `light-metro-3car`'s low-floor height exactly. Level boarding.
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
| Ticket hall (west end) | 15 m × 8 m | 120 | Fare gates + TVMs + SSBC cabinet |
| Lift rooms (per platform) | 2 × 2 m × 2 m | 8 | Wheelchair-accessible lift per side |
| Stair wells (per platform) | 2 × 4 m × 2.5 m | 20 | From ticket hall to platform |
| Services cabinet room | 4 m × 3 m | 12 | Station SCADA + sub-MSB + UPS |

**Total gross floor area:** ~700 m² indoor + 600 m² canopied
outdoor platform.

## Access modes (per RFC 0010 §5)

Each side platform has:

1. **Ramp + stair** from the ticket hall at platform level.
   Ramp max 1:12 per accessibility; length ~8 m (rises from
   grade level to platform + 350 mm to ToR = 350 mm rise = 4.2 m
   ramp; plus 300 mm for floor thickness and drain). Use a
   dog-leg ramp that folds into 8 m × 1.5 m.
2. **Stair** alongside the ramp for capacity: 2 × 1.5 m wide
   straight runs.
3. **Elevator** from ticket hall to platform: 1 100 × 1 400 mm
   car, 630 kg rating.

No escalator at `standard` archetype (per RFC 0010 §5 — only
`major` / `interchange` / `terminal` / `depot-terminal` get
escalators).

## Egress (per RFC 0010 §6 and NFPA 130 4-minute rule)

Platform occupancy sizing:

- Planning-grade peak: 150 passengers × 2 platforms = 300.
- NFPA 130 egress: must reach a "safe point" within 4 minutes.

Egress paths (per platform):

- Primary: ramp + stair to ticket hall (11 m travel).
- Secondary: at the opposite (east) end of the platform, a
  direct stair down to street level (8 m vertical travel).

Effective egress width:
- Ramp 1.5 m + stair 1.5 m → 3 m aggregate (≥ the RFC 0010 §6
  `standard` minimum of 2 m aggregate).
- Secondary stair 1.5 m.
- **Total effective width: ≥ 4.5 m per platform.**

At 300 pax per platform and NFPA 130 flow 1.3 pax/m/s:
- Clearance time = 300 / (4.5 m × 1.3 pax/m/s) ≈ 52 s.
  Well under the 4 min target. ✓

## Fare paid / unpaid zones

- **Unpaid zone:** ticket hall, TVMs, outside fare gates.
- **Paid zone:** everything platform-side of the fare gates.

`standard` archetype gets 2 fare-gate lanes per direction per
RFC 0010 §8 (so 4 total — 2 in, 2 out; 1 wide-gate for
wheelchairs). TVMs: 1 per direction (2 total).

## Property-line setbacks (for operator adaptation)

- ROW centreline to property line: ≥ 3 m both sides (municipal
  code typical).
- Ticket hall at west end can extend into unused ROW corners;
  operator adapts per parcel.
- If the ticket hall must go on only one side (single-access
  station due to constrained site), drop to one platform access
  at the west end + keep the secondary east-end emergency
  stair. **`standard` archetype requires at least 2 independent
  egress directions per platform**, so single-access is out.

## Site footprint

Total approximate footprint a `standard` station occupies on
the ground:

- Platform envelope: 75 × 12.5 = **940 m²** main rectangle.
- Ticket hall west: 120 m² west-end addition.
- Service cabinet + lifts: 30 m² west-end addition.
- Canopy shadow (extends slightly beyond platform): 85 × 22 =
  1 870 m² — but this is the roof, not ground footprint.

**Usable ground footprint: ~1 100 m² per station.**

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

# DIY assembly — tools + materials

## Required tools

| Tool | Purpose | Typical source |
|---|---|---|
| **PH1 + PH2 Phillips screwdriver** | Enclosure + terminal-block + DIN-rail screws | Any hardware store |
| **2.5 mm flat-head screwdriver** | Small terminal block screws | Any hardware store |
| **Wire cutter / stripper** for 0.5 – 2.5 mm² stranded | Field wiring + terminal-block jumpers | Any electronics supplier |
| **Ferrule crimper** for 0.5 – 2.5 mm² ferrules | Stranded-wire termination into terminal blocks (do not tin with solder) | Knipex / generic |
| **Micro-HDMI → HDMI cable** | First-boot commissioning via CM5's micro-HDMI + a monitor | Generic |
| **Keyboard** (USB) | First-boot commissioning | Generic |

That is the entire tool list. No soldering iron, no hot-air
station, no benchtop power supply, no logic analyser, no
oscilloscope. The safety-case argument (RFC 0019 §7) does not
require per-unit scope capture — the Pico 2's own self-test
plus `osr-selftest` provides the verification.

## Optional but recommended

| Tool | Purpose |
|---|---|
| Multimeter | Spot-check 24 V power continuity at the DIN-rail terminal |
| ESD wrist strap | Good practice around the CM5 module; not strictly required once it's seated in the IO Board |
| Labelmaker | Cable labels per the wiring map; saves hours at commissioning |
| Torque screwdriver (0.5 Nm preset) | For enclosure screws on shock-rated field units (EN 50155 OT4) |

## Consumables (per host class)

| Consumable | Spec | Qty per unit |
|---|---|---|
| Ferrules | 0.5 / 0.75 / 1.5 mm² insulated colour-coded | ~50 |
| Cable ties | Nylon 2.5 mm × 100 mm | ~20 |
| Heat-shrink sleeve | Ø 3 mm + Ø 6 mm, any colour | ~5 pieces |
| Labels | Adhesive printable | ~30 |

## Hygiene rules

1. **Never power up with the CM5 not fully seated.** The
   SO-DIMM pins will short on a partial insertion.
2. **Strip to the ferrule's depth, no more.** Over-strip
   = exposed copper outside the terminal = creepage
   violation.
3. **Separate safety-critical wiring.** The 2oo2 A-channel and
   B-channel wiring must route through different cable trays
   / different bundles. A common single-point cable-bundle
   damage incident defeats the 2oo2 safety argument. Use
   different insulation colours (A = black, B = brown, per
   RFC 0007 §safety-nets convention).
4. **Label everything at assembly time.** `A-CROSS-CHECK-IN`,
   `A-CROSS-CHECK-OUT`, `B-CROSS-CHECK-IN`, `B-CROSS-CHECK-OUT`
   — at 3 AM during a field incident nobody can guess.
5. **Terminal-block torque is 0.5 Nm.** Factor applies to
   every screw terminal in every host class.

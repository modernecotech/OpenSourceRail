# RFC 0025 — DIY Switch and Point-Machine Production

**Status:** Draft — extends [RFC 0012 §4](0012-switches-and-crossings.md)
**Date:** 2026-04-26
**Depends on:** [RFC 0012 Switches & Crossings](0012-switches-and-crossings.md), [RFC 0007 Hardware Reference Designs](0007-hardware-reference-designs.md)

## 1. Summary

[RFC 0012 §4](0012-switches-and-crossings.md#4-switch-architecture)
already commits a **non-proprietary switch architecture** — flexible
machined switch blade, cast-manganese frog, electro-mechanical BLDC +
planetary-gearbox + crank point machine, 2oo2 detection. What it does
not commit is a **production path** for that architecture in target
regions, nor specific commodity SKUs for the actuator. The result in
practice: deployments still buy $120 k turnouts from VAE / Vossloh /
Schwihag because RFC 0012 is silent on the make-vs-buy decision.

This RFC commits a **regional switch-shop bootstrap** as the primary
production path, with vendor procurement as the alternate for
deployments that don't have the volume to justify the shop.

For a 100 km deployment with ~80 switches, the procurement-vs-DIY
delta is **~$8–10 M USD**, the largest single affordability lever in
any OSR civil build.

## 2. Non-goals

- **Not a re-spec of RFC 0012 geometry.** The three turnout tangents
  (1:9 / 1:14 / 1:18.5) and the switch architecture remain canonical.
- **Not a re-spec of `osr-wayside-points`.** The detection,
  observation, and consensus path stay in
  [`osr-wayside-points`](../../crates/osr-wayside-points/).
- **Not a re-spec of the safety case.** A DIY switch and a vendor
  switch carry the **same** SIL-4 safety case — the SIL-4 logic
  lives in software (`osr-wayside-points` + `osr-interlocking`), not
  in the actuator. The mechanical part is below SIL.

## 3. Switch-shop bootstrap (primary path)

### 3.1 Tooling and capex

| Equipment | Spec | New | Used |
|---|---|---|---|
| CNC milling machine | 4 m × 1.5 m × 1 m bed, 3-axis minimum | $200 k | $80 k |
| Plate-cutting (plasma or fibre laser) | 4 m × 8 m bed | $80 k | $30 k |
| Forge press | 200 t hydraulic | $80 k | $35 k |
| Heat-treatment furnace | 2 m × 1 m, 1 200 °C | $60 k | $25 k |
| Welding bay | MAG/MIG to EN 15085 CP-C2 | $30 k | $15 k |
| Inspection table + CMM | 4 m × 2 m granite + portable CMM | $50 k | $25 k |
| Misc tooling, jigs, fixtures | — | $80 k | $30 k |
| **Total switch-shop CAPEX** | | **~$580 k** | **~$240 k** |

### 3.2 Output and unit economics

- Production rate: ~2 switches/week steady-state, ~100/year.
- Per-switch BOM (1:9 turnout):
  - Switch blades (machined from rail blank): $1 800
  - Stock rails: $1 200
  - Stretcher bars (forged): $400
  - Frog (cast manganese, sub-contracted to regional foundry): $1 500
  - Check rails: $300
  - Switch sleepers (per RFC 0009): $2 000
  - Point machine assembly (per §4): $2 200
  - Heating + cabinet + harness: $800
  - **Total BOM:** ~**$10 200**
- Vendor 1:9 reference: $120 k (matches
  [`lib/templates/switches.toml`](../../lib/templates/switches.toml)
  `kits.no-9-mainline` `cost_usd`).
- DIY savings per 1:9: ~$110 k.
- 80 switches: ~$8.8 M saved, vs ~$580 k shop CAPEX → ~15 × payback.

### 3.3 Reference designs

Switch-blade and frog geometry are **public** at AREMA standard or
UIC 60E1 equivalent. Drawings circulate in the public domain and
cover every tangent in RFC 0012.

## 4. Point machine — commodity actuator

The RFC 0012 §4.2 architecture (BLDC + planetary + crank, 6 kN
nominal / 12 kN peak, ≤ 3 s throw) is satisfied by commodity
industrial linear actuators with no rail-specific silicon:

| SKU class | Vendor | Stroke | Force | List | Notes |
|---|---|---|---|---|---|
| PC-Series | Thomson Linear | 200 mm | 5–10 kN | $1 800 | IP67, BLDC+planetary, regional distributor everywhere |
| EPCO | Festo | 150–300 mm | 5–8 kN | $2 000 | Same |
| CASM-100 | SKF | 200 mm | 8 kN | $1 600 | Same |
| LinMot P10 | LinMot AG | 240 mm | 5 kN | $2 200 | Direct-drive linear (no gearbox) — alternate |
| Regional copies | Various Chinese / Indian | 200 mm | 5–10 kN | $700 | Need qualification testing — see §6 |

Vendor-branded rail point machines (Siemens M3, Alstom M58 EBI Switch,
Schwihag): **$25 k–$45 k each.**

Per OSR switch: ~$1 800 vs $25 k → **$23 k saved per switch on the
actuator alone.**

## 5. Detection and integration

Unchanged from [RFC 0012 §5](0012-switches-and-crossings.md#5-position-detection--integration)
and [`osr-wayside-points`](../../crates/osr-wayside-points/). The
DIY switch reports position over the same 2oo2 channel as a vendor
switch; the W-SBC ([RFC 0007 §6](0007-hardware-reference-designs.md))
sees no difference.

## 6. Qualification and safety

The DIY-switch SIL-4 case is **the same as the vendor-switch case**
because:

- Position sense, locking confirmation, and FPS observation are all
  in `osr-wayside-points` (already SIL-4 qualified).
- The mechanical interlock is via the front stretcher bar, identical
  to the vendor architecture.
- The actuator below the lock has no SIL claim — it is "best effort"
  with the SIL-4 verdict coming from sensed position, not commanded
  position.

What **does** need a per-design qualification:

1. **Throw force margin** — proof test to 12 kN peak with a 1.5 ×
   safety factor (18 kN ultimate).
2. **Throw time** — measured throw time ≤ 3 s from rest to locked
   per RFC 0012 §4.2.
3. **Endurance** — 10⁶ cycles at full force without lock failure
   (industry standard for points: ~3-month bench test).
4. **Environmental** — IP67, −25 °C to +55 °C operation.

These are mechanical qualifications, not safety-case qualifications.
A regional university mechanical engineering department can run
them in 6 months.

## 7. Procurement alternate

For deployments with < 20 switches/year volume, vendor procurement
remains the right answer. Alternate suppliers in priority order:

| Supplier | Region | Notes |
|---|---|---|
| Voestalpine VAE | Austria / Brazil / India | reference, premium pricing, MENA distribution |
| Vossloh Cogifer | France / Germany | reference |
| AnaSteel / Texmaco Rail | India | mid-tier, good for South Asia + East Africa |
| CRRC Yangtze | China | volume, ~50 % of European pricing |
| Voestalpine VAE Brasil | Brazil | regional Latin America |

## 8. Open questions

1. Manganese-steel frog foundry — does the project source a
   regional foundry per deployment, or maintain a small list of
   qualified foundries?
2. Switch-blade-stock supply — head-hardened 60E1 rail blanks need
   to come from one of the rail mills in [RFC 0009](0009-track-design-standard.md).
3. Whether the actuator qualification (per §6) is a per-deployment
   activity or a one-time project-level activity.

## 9. Revision history

| Date | Version | Change |
|---|---|---|
| 2026-04-26 | v0 | Stub. Switch-shop CAPEX model, commodity actuator SKUs, DIY-vs-vendor unit economics, qualification frame. |

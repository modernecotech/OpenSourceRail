# RFC 0024 — Battery Thermal Management at High Ambient

**Status:** Draft — extends [RFC 0021 §7](0021-battery-traction.md#7-thermal-management)
**Date:** 2026-04-26
**Depends on:** [RFC 0021 Battery Traction](0021-battery-traction.md), [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md)

## 1. Summary

[RFC 0021 §7](0021-battery-traction.md#7-thermal-management) already commits
the **baseline** thermal architecture: 2.5 kW refrigerant coil per strake
fed from the HVAC condenser loop, per-module cell-temperature sense, BMS
charge-derating above 50 °C cell, sealed-strake runaway containment with
weak-point lateral vent. This RFC does **not** replace that architecture —
it extends it for deployments at the upper end of the +50 °C envelope
where the shared-condenser baseline leaves insufficient margin against
cycle-life degradation.

The two extensions:

1. **PCM thermal mass** in the strake — passive buffer for station-dwell
   and acceleration peaks.
2. **Dedicated chiller alternative** to the shared HVAC condenser — for
   deployments where the HVAC duty cycle alone cannot cover sustained
   high-ambient charging.

## 2. Non-goals

- **Not a re-spec of RFC 0021 §7.** The baseline shared-condenser
  architecture remains the default. This RFC adds two **alternates**
  and a selection rule.
- **Not a chemistry-change RFC.** Sodium-ion remains primary, LFP
  remains alternate per [RFC 0021 §3](0021-battery-traction.md).

## 3. Why extend the baseline

At +50 °C ambient with the strake skin shaded by the longitudinal bench
(per RFC 0021 §7), measured strake-air rises to ~+58 °C under sustained
load. With 2.5 kW per strake of refrigerant coil drawn from the HVAC
condenser, the coil has to share its budget with cabin cooling — which
is itself peaking at 50 °C ambient. Under the worst case (full-crush
cabin + 2 C charge accept after a depot-terminal turnback), the
shared-condenser path can lose its derate margin and the BMS cuts
charge current to 0.5 C. That is *safe* but it stretches turnback
dwell and degrades the energy-sizing calculations in
[RFC 0002 §4](0002-energy-sizing.md).

## 4. Extension A — PCM thermal mass

| Aspect | Choice |
|---|---|
| Location | 30 mm phase-change-material layer between cell stack and outer strake skin |
| PCM | Paraffin-wax composite (RGEES TH-58 / PCM Products A55), latent heat ~210 kJ/kg, melt point 50–55 °C |
| Mass | ~12 kg PCM per strake, ~72 kg per `light-metro-3car` car |
| Maintenance | Zero — sealed inside the strake enclosure, lifetime-of-pack |
| Cost | ~$2/kg → ~$140 per car PCM-only; encapsulation adds ~$200/car |

PCM absorbs the heat-of-fusion through the cell-skin temperature
range, smoothing the chiller load across station-dwell and
acceleration peaks. The chiller still does the steady-state
work; PCM removes the spikes.

## 5. Extension B — Dedicated vapour-compression chiller

| Aspect | Choice |
|---|---|
| Location | One chiller per car, mounted on the underframe plenum (per RFC 0008 §3.1) |
| Capacity | ~3 kW thermal per 100 kWh pack (≈ 12 kW per `light-metro-3car`) |
| Refrigerant | R-1234yf (default) or R-744 / CO₂ (deployments with regional supply) — both Kigali-compliant |
| Cold plate | CNC-milled aluminium + brazed copper tubing per strake — any HVAC shop |
| Power source | 400 V aux bus (`osr-aux-power`) |
| Cost | ~$5 k chiller + $2 k cold-plate set per car |

Use the dedicated chiller when:

- Ambient > 45 °C **continuous** (Samawah summer, Khartoum, Riyadh,
  Karachi).
- Charge profile is 2 C sustained at depot-terminals on short
  turnback dwells.
- HVAC duty-cycle modelling shows < 0.7 reserve on the condenser at
  AW3 + +50 °C.

## 6. Selection rule

```text
   ambient envelope          charge profile          architecture
   ─────────────────         ─────────────────       ──────────────────────
   ≤ 40 °C continuous        ≤ 1 C sustained         RFC 0021 §7 baseline
   40–45 °C continuous       ≤ 1 C sustained         baseline + Ext. A (PCM)
   ≤ 50 °C continuous        ≤ 2 C sustained         Ext. A + Ext. B (chiller)
   > 50 °C continuous        any                     Ext. A + Ext. B + uprated coil
```

The auto-gen pipeline picks the architecture per deployment from the
ambient envelope and charge-profile inputs.

## 7. Charge-rate enforcement (BMS)

[`osr-bms`](../../crates/osr-bms/) already has the cell-temperature
derating function per RFC 0021 §7. This RFC adds an explicit
**charge-rate cap table**:

| Cell temperature | Charge rate cap |
|---|---|
| ≤ 35 °C | 2 C (nameplate) |
| 35–45 °C | 1 C |
| 45–50 °C | 0.5 C |
| 50–55 °C | 0.2 C |
| > 55 °C | 0 (charge inhibit), report fault |

Discharge derating is per RFC 0021 §7; this table applies on the
charge side only.

## 8. Cost impact (USD OECD-base)

| Architecture | Per-`light-metro-3car` add | Per-fleet (16 trainsets) add |
|---|---|---|
| Baseline (RFC 0021 §7) | — | — |
| + Extension A (PCM) | ~$1 k | ~$16 k |
| + Extensions A+B | ~$22 k | ~$350 k |

Compare an unmitigated pack-replacement event at year 5 (baseline
warranty assumed year 12): ~$80 k per consist for OSR-discipline cells
(360 kWh × ~$90/kWh integrated + commissioning) plus ~2 weeks of revenue
loss while strake is removed. **Extensions A+B is not optional for
Samawah-class envelopes.**

## 9. Open questions

1. PCM lifecycle vs cell-fault venting — whether wax leak after a
   thermal event creates a secondary fire hazard.
2. R-744 vs R-1234yf — supply-chain analysis per target region.
3. Whether to fold this RFC back into RFC 0021 §7 as v2 of that
   section, or keep it separate.

## 10. Revision history

| Date | Version | Change |
|---|---|---|
| 2026-04-26 | v0 | Stub. PCM + dedicated-chiller extensions on top of RFC 0021 §7 baseline; selection rule by ambient + charge profile. |

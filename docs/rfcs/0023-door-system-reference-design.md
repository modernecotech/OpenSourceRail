# RFC 0023 — Door System Reference Design

**Status:** Draft — stub, awaiting elaboration
**Date:** 2026-04-26
**Depends on:** [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0015 Driverless Operation](0015-driverless-operation.md), [RFC 0007 Hardware Reference Designs](0007-hardware-reference-designs.md)

## 1. Summary

[RFC 0008 §3.3](0008-rolling-stock-reference-design.md#3-unified-architecture--every-family)
commits each car side to "2 × 1 300 mm plug doors" and a 1 250 mm × 2 000 mm
clear opening, but does not specify the **door operator** — the
electromechanical actuator that opens, closes, locks, and senses
obstruction. This is a meaningful omission. Door operators are a top-three
reliability and operating-cost item on every metro, and the rail-certified
vendor market (IFE / Knorr-Bremse, Faiveley / Wabtec, Nabtesco) prices a
single operator at $20 k–$40 k per door at OECD list — $320 k–$640 k per
`light-metro-3car` consist (16 doors), of which 60–70 % is certification
margin re-billed to each operator.

This RFC commits an **electric linear-actuator** door operator built from
commodity industrial silicon, certified once at the project level under
EN 14752, and integrated with [`osr-door-control`](../../crates/osr-door-control/).

## 2. Non-goals

- **Not a pneumatic door system.** Pneumatic plug doors (the legacy
  default) require a compressor + air-treatment loop; the rolling-stock
  design ([RFC 0008 §3.2](0008-rolling-stock-reference-design.md))
  has already removed pneumatics from the brake system, and adding them
  back for doors would re-introduce the maintenance line item we
  eliminated. Electric only.
- **Not a sliding-pocket-door design.** OSR commits to plug doors per
  RFC 0008 — this RFC covers the operator, not the door geometry.
- **Not a platform-screen-door (PSD) interface spec.** PSD coupling
  protocol stays in [`osr-psd`](../../crates/osr-psd/).

## 3. Architecture

| Aspect | Choice | Rationale |
|---|---|---|
| Actuator | 24 V DC brushless linear actuator, 1 200 mm stroke, 5 kN continuous | Commodity industrial silicon (Thomson PC-series, Festo EPCO, SKF CASM, regional copies). Single-vendor risk avoided by spec'ing to interchangeable form factor. |
| Drive | Cog-belt + slide-rail, no pneumatic | Same architecture as Bombardier MOVIA / Siemens Inspiro at the mechanical level; the complexity is in EN 14752 certification, not in the parts. |
| Controller | BLDC servo controller, CAN-FD interface to `osr-door-control` | Roboteq / RoboClaw class for pilot; in-house RFC 0007-class board for production. |
| Obstruction detection | Light-curtain across opening (Banner / SICK rail-grade) + pinch-current sensing in actuator | Two independent detection paths; either alone halts the close. |
| Lock | Mechanical hook lock at full-close, monitored by independent micro-switch | EN 14752 mandates positive-locked status sense. |
| Emergency egress | Manual unlock handle inside + outside, mechanical override of lock | EN 14752 + UIC 560. |
| Position sense | Linear encoder on actuator + redundant Hall on the lock cam | Dual-channel agreement to `osr-door-control` over CAN-FD. |

## 4. Certification

**EN 14752 (Bodyside doors for rail vehicles)** is the governing standard.
The certification surface is real but is a **one-time engineering item**:
the project absorbs it once and amortises across every deployment, in
contrast to the current commercial-vendor model where every operator
re-pays the certification load embedded in the per-door price.

Certification artefacts land under
`docs/certification/door-system/` once the v1 elaboration completes.

## 5. Cost model (indicative, 2026, USD OECD-base)

| Component | DIY-path BOM | Vendor reference |
|---|---|---|
| Linear actuator | $400 | (bundled) |
| BLDC servo controller | $250 | (bundled) |
| Slide rail + cog belt + carrier | $300 | (bundled) |
| Light curtain | $400 | (bundled) |
| Lock + position-sense + harness | $400 | (bundled) |
| Integration + harness + commissioning | $250 | (bundled) |
| **Per-door total** | **~$2 000** | **$20 k–$40 k** |

`light-metro-3car` consist (16 doors): **~$32 k DIY** vs **$320 k–$640 k
vendor**. Country-cost multipliers from
[`lib/templates/country-costs.toml`](../../lib/templates/country-costs.toml)
apply to the labour share downstream.

## 6. Open questions

1. EN 14752 certification path — UK / EU notified-body engagement vs
   self-certification by the project consortium.
2. PSD interfacing — does the actuator need to expose a hardline
   interlock to the platform PSD, or is the CAN-FD bridge through
   `osr-psd` sufficient?
3. Cold-climate variant — at the ≤ −25 °C end of the rolling-stock
   envelope ([RFC 0008 §3.5](0008-rolling-stock-reference-design.md)),
   actuator grease and light-curtain fogging are open issues.
4. Recovery path on actuator failure — whether the door reverts to
   manual-only or whether a redundant secondary actuator is mandated.

## 7. Revision history

| Date | Version | Change |
|---|---|---|
| 2026-04-26 | v0 | Stub. Architecture sketch, BOM model, certification frame. Detailed elaboration pending. |

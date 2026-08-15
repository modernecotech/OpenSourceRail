# RFC 0023 — Door System Reference Design

**Status:** Current — v2A architecture, certification evidence open
**Date:** 2026-04-26
**Depends on:** [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0015 Driverless Operation](0015-driverless-operation.md), [RFC 0007 Hardware Reference Designs](0007-hardware-reference-designs.md)

## 1. Summary

[RFC 0008 §3.3](0008-rolling-stock-reference-design.md#3-unified-architecture--every-family)
commits each 16.5 m car to two large double-leaf plug-door cassettes
per side: twelve exterior cassettes, twenty-four leaves, and a
nominal 1 500 mm clear opening per cassette on the `light-metro-3car`
consist. It did not previously specify the **door operator** — the
electromechanical actuator that opens, closes, locks, and senses
obstruction. This was a meaningful omission. Door operators are a
top-three reliability and operating-cost item on every metro, and the
rail-certified vendor market (IFE / Knorr-Bremse, Faiveley / Wabtec,
Nabtesco) prices a single operator at $20 k–$40 k per cassette at OECD
list — $120 k–$240 k per `light-metro-3car` consist, of which 60–70 %
is certification margin re-billed to each operator.

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
| Actuator | 24 V DC brushless linear actuator, 900-1 200 mm stroke, 3-5 kN continuous | Commodity industrial silicon (Thomson PC-series, Festo EPCO, SKF CASM, regional copies). Single-vendor risk avoided by spec'ing to interchangeable form factor. |
| Drive | Cog-belt + slide-rail, no pneumatic | Same architecture as modern electric metro plug doors at the mechanical level; the complexity is in EN 14752 certification, not in the parts. |
| Controller | BLDC servo controller, CAN-FD interface to `osr-door-control`, hardwired closed-and-locked loop to T-ECU/S | Roboteq / RoboClaw class for pilot; in-house RFC 0007-class board for production. Safety output does not depend on CAN alone. |
| Obstruction detection | Light-curtain across opening (Banner / SICK rail-grade) + pinch-current sensing in actuator | Two independent detection paths; either alone halts the close. |
| Lock | Mechanical hook lock at full-close, monitored by independent micro-switch | EN 14752 mandates positive-locked status sense. |
| Emergency egress | Manual unlock handle inside + outside, mechanical override of lock | EN 14752 + UIC 560. |
| Position sense | Linear encoder on actuator + redundant Hall on the lock cam | Dual-channel agreement to `osr-door-control` over CAN-FD. |

## 4. Interface Contract

| Interface | Requirement |
|---|---|
| Structural aperture | Door cassette installs into the side-frame portal defined by `LM3-DOOR-200`; supplier changes may not move primary steel datums |
| Power | 24 V DC control power plus protected motor feed from the car auxiliary cabinet |
| Data | CAN-FD command/status to `osr-door-control`; diagnostic Ethernet optional |
| Safety loop | Independent hardwired closed-and-locked contact per cassette, wired into the train safety chain |
| Drainage | Threshold tray drains outside the saloon; drain path must remain inspectable after interior trim installation |
| Emergency release | Interior release at the doorway and exterior release behind a tamper-evident cover |
| Gap filler | Door-sill flap/skirt permissive is interlocked with door-open command and platform-side selection |

## 5. Certification

**EN 14752 (Bodyside doors for rail vehicles)** is the governing standard.
The certification surface is real but is a **one-time engineering item**:
the project absorbs it once and amortises across every deployment, in
contrast to the current commercial-vendor model where every operator
re-pays the certification load embedded in the per-door price.

Certification artefacts land under `docs/certification/door-system/`.
The release gap is tracked in
[`docs/certification/release-gap-register.md`](../certification/release-gap-register.md).

## 6. Cost model (indicative, 2026, USD OECD-base)

| Component | DIY-path BOM | Vendor reference |
|---|---|---|
| Linear actuator | $400 | (bundled) |
| BLDC servo controller | $250 | (bundled) |
| Slide rail + cog belt + carrier | $300 | (bundled) |
| Light curtain | $400 | (bundled) |
| Lock + position-sense + harness | $400 | (bundled) |
| Integration + harness + commissioning | $250 | (bundled) |
| **Per-door total** | **~$2 000** | **$20 k–$40 k** |

`light-metro-3car` consist (12 exterior cassettes): **~$24 k DIY
operator BOM** vs **$240 k–$480 k vendor** before certification and
qualification overhead. Country-cost multipliers from
[`lib/templates/country-costs.toml`](../../lib/templates/country-costs.toml)
apply to the labour share downstream.

## 7. Release Checklist

| Gate | Closure artifact |
|---|---|
| Door envelope freeze | Supplier drawing proving the cassette fits `LM3-DOOR-200` without primary steel changes |
| EN 14752 plan | Notified-body or assessor route, test plan, acceptance criteria, and sample count |
| Lock-loop validation | Tests proving a false closed-and-locked status cannot be produced by one sensor fault |
| Obstruction validation | Light-curtain, current-sense, reopen timing, force limit, and degraded-mode tests |
| Emergency release | Interior/exterior release force, tamper evidence, reset procedure, and signage |
| PSD/platform interface | Door-side select, platform-screen-door interlock, gap-filler permissive, and failure states |
| Environmental tests | Heat, dust, rain ingress, washer/cleaning chemical compatibility, and low-temperature grease variant |

## 8. Open questions

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

## 9. Revision history

| Date | Version | Change |
|---|---|---|
| 2026-04-26 | v0 | Stub. Architecture sketch, BOM model, certification frame. Detailed elaboration pending. |
| 2026-05-20 | v1 | Added interface contract and release checklist. |
| 2026-08-14 | v2 | Aligned the RFC with the promoted 16.5 m car and twelve-cassette trainset layout. |

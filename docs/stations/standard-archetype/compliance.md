# Compliance Matrix - `standard` Archetype Worked Example

Standards the envelope is designed against. Per-deployment
NRSA / NRCA (national-rail + national-construction authority)
approvals overlay — those are per-country and not repeated here.

## Structural + fire

| Standard | Scope | Evidence status (v1 → v2) |
|---|---|---|
| **EN 1990 / EN 1991** | Basis of structural design; loads on structures | Load cases enumerated in [`canopy.md`](canopy.md) (v1) → full FEA (v2) |
| **EN 1993** | Design of steel structures | First-pass column + truss check in [`canopy.md`](canopy.md) (v1) → EN 1993 stamped calc (v2) |
| **EN 1997** | Geotechnical design | Planning-grade bearing capacity (v1) → site-specific geotech (v2) |
| **EN 1998** | Seismic design of structures | Iraq PGA 0.1 g baseline (v1) → site-specific seismic microzonation (v2) |
| **NFPA 130** | Fixed guideway transit + passenger rail systems | Egress 4-minute rule checked in [`envelope.md`](envelope.md) + [`services.md`](services.md) (v1) |
| **EN 45545** (parts 2 + 3) | Fire behaviour of railway vehicles + stations | Materials flagged HL1 for outdoor station in [`services.md`](services.md) (v1) → per-material test reports (v2) |
| **EN 1838** | Emergency lighting | Spec'd in [`services.md`](services.md) (v1) → product selection + test (v2) |

## Accessibility

| Standard | Scope | Evidence status |
|---|---|---|
| **EN 16586** | PRM (Persons with Reduced Mobility) | [`accessibility.md`](accessibility.md) (v1 ✓) |
| **ISO 23599** | Tactile walking-surface indicators | Applied throughout [`accessibility.md`](accessibility.md) |
| **ISO 7001** | Public-information pictograms | Applied in [`services.md`](services.md) signage |
| **ISO 21542** | Building construction — accessibility | Flat pedestrian-grade access; local ramps only where site grading requires them |
| **EN 81-70** | Lifts accessible to persons with disabilities | n/a for flat at-grade `standard`; applies to elevated/stacked overrides |

## Electrical + MEP

| Standard | Scope | Evidence status |
|---|---|---|
| **EN 60439** | Low-voltage switchgear assemblies | Ticket-hall MCB board (v2 product spec) |
| **EN 61000-6-3** | EMC — emission standard for residential, commercial, light-industrial | LED lighting + PIS equipment class-B compliant |
| **EN 12464-2** | Light and lighting — outdoor workplaces | Illuminance targets in [`services.md`](services.md) (v1 ✓) |
| **IEC 60947-5-1** | Auxiliary contacts for emergency-stop circuits | Used on emergency help buttons |
| **ISO 14644** | Cleanrooms / contamination control | n/a for transit station — not specified |

## Environmental

| Standard | Scope | Evidence status |
|---|---|---|
| **ISO 3095** | Acoustics — railway applications, noise emitted | Pass-by noise target 80 dB(A) at platform (v1) |
| **WHO community-noise guidelines** | Night-time outdoor noise | Target 45 dB(A) at façade (RFC 0011 §5.1 acoustic screens on elevated) |
| **EN 12101** (parts 1–9) | Smoke + heat control systems | n/a — open-air platform |
| **NFPA 110** | Emergency + standby power systems | UPS in services cabinet — spec level 1 |

## Cybersecurity + physical security

| Standard | Scope | Evidence status |
|---|---|---|
| **IEC 62443** (parts 2-4 + 4-2) | Industrial automation + control systems cybersecurity | `osr-station-scada` designed per `osr-crypto` discipline |
| **EN 50159** | Railway applications — communications, signalling, processing systems | `osr-station-scada` interfaces conform |

## National overlays (Iraq — per-deployment)

- Iraqi Electrical Code (based on NEC) — deployment electrical
  contractor scope.
- Iraqi Fire Code — applied via the national fire directorate's
  approval process.
- Iraqi Accessibility Act — overlays EN 16586 with Arabic-
  specific signage requirements.

**Upstream (this doc) provides the EN-standard base.** Per-
deployment overlays are the operator's compliance-team scope.

## Acceptance-test outline (pre-opening)

A `standard` station's pre-opening sign-off checklist:

1. **Structural:** inspector visual walk-through + spot-check
   on column anchorage, truss welds.
2. **Accessibility:** actual wheelchair user rides from street
   to train door on both platforms — no step, no gap > spec.
3. **Emergency lighting:** simulate mains-fail; confirm 1-hour
   battery operation of exit signs + egress lighting.
4. **Fire alarm:** test services-cabinet detector → OCC alarm
   ≤ 30 s latency.
5. **PIS:** next-train information updates correctly from the
   OCC's mock schedule.
6. **Fare gates:** open on valid QR + NFC; deny on invalid;
   emergency-release works.
7. **Platform-screen-door coordination:** (if fitted at this
   station — not `standard` default but per operator choice)
   door command / confirmation round-trip within `osr-psd`'s
   FSM.
8. **CCTV:** OCC receives all cameras at nominal resolution +
   frame rate.
9. **Drainage:** pour 1 m³ of water into the low end; confirm
   it drains to the municipal connection in ≤ 5 min.
10. **Noise:** train pass-by at design speed ≤ 80 dB(A) at
    platform (confirm by sound-level meter at the waiting
    area).

Checklist lands with actual pass/fail values in the deployment's
`acceptance/` tree.

## What v1 doesn't commit to

- Stamped structural calculations (v2).
- Product-specific equipment selections (operator discretion).
- Specific lift-service contracts (only for elevated/stacked overrides).
- National approval-body sign-off procedure (per-deployment).

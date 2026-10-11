# Compliance Matrix - `standard` Archetype Worked Example

Candidate standards and verification routes for the planning envelope. No
configuration-specific conformity or authority approval is established here.
The [Digital Standards Thread](../../certification/digital-standards-adherence.md)
governs deployment applicability, current adopted editions/clauses, evidence and
independent decisions. National construction, fire, access and railway
requirements remain project-specific inputs.

## Structural + fire

| Standard | Scope | Evidence status (v1 → v2) |
|---|---|---|
| **EN 1990 / EN 1991** | Basis of structural design; loads on structures | Load cases enumerated in [`canopy.md`](canopy.md) (v1) → full FEA (v2) |
| **EN 1993** | Design of steel structures | First-pass column + truss check in [`canopy.md`](canopy.md) (v1) → EN 1993 stamped calc (v2) |
| **EN 1997** | Geotechnical design | Planning-grade bearing capacity (v1) → site-specific geotech (v2) |
| **EN 1998** | Seismic design of structures | Iraq PGA 0.1 g baseline (v1) → site-specific seismic microzonation (v2) |
| **NFPA 130** | Candidate fixed-guideway transit fire/egress route where adopted | Simple planning checks in [`envelope.md`](envelope.md) do not establish interacting crowd, fire or disruption-case compliance; adopted clauses and fire-engineer assessment open |
| **EN 45545** (parts 2 + 3) | Railway-vehicle materials and fire barriers | Vehicle interface only where applicable. Outdoor stations have no automatic HL1 classification; building/station fire rules, installed material build-ups and test evidence require separate adoption |
| **EN 1838** | Emergency lighting | Spec'd in [`services.md`](services.md) (v1) → product selection + test (v2) |

## Accessibility

| Standard | Scope | Evidence status |
|---|---|---|
| **EN 16586** | Vehicle PRM boarding interface candidate; applicability review required | Planning intentions in [`accessibility.md`](accessibility.md); actual vehicle/platform compatibility and physical access tests open |
| **ISO 23599** | Tactile walking-surface indicators | Candidate tactile layout in [`accessibility.md`](accessibility.md); installed assessment open |
| **ISO 7001** | Public-information pictograms | Candidate signage basis in [`services.md`](services.md); user and installed evidence open |
| **ISO 21542** | Building construction — accessibility | Flat pedestrian-grade access; local ramps only where site grading requires them |
| **EN 81-70** | Lifts accessible to persons with disabilities | n/a for flat at-grade `standard`; applies to elevated/stacked overrides |

## Electrical + MEP

| Standard | Scope | Evidence status |
|---|---|---|
| **IEC/EN 61439 series** | Low-voltage switchgear/controlgear assemblies; select the relevant product part with Part 1 | Exact assembly, adopted edition, design/routine verification and installation evidence open; IEC 60439-1 is replaced |
| **EN 61000-6-3** | Candidate generic EMC emission scope; railway/system applicability review required | LED/PIS compliance and installed compatibility unassessed |
| **EN 12464-2** | Candidate outdoor workplace lighting scope | Planning illuminance targets in [`services.md`](services.md); adopted values and installed measurements open |
| **IEC 60947-5-1** | Auxiliary contacts for emergency-stop circuits | Used on emergency help buttons |
| **ISO 14644** | Cleanrooms / contamination control | n/a for transit station — not specified |

## Environmental

| Standard | Scope | Evidence status |
|---|---|---|
| **ISO 3095** | Acoustics — railway applications, noise emitted | Pass-by noise target 80 dB(A) at platform (v1) |
| **WHO community-noise guidelines** | Night-time outdoor noise | Target 45 dB(A) at façade (RFC 0011 §5.1 acoustic screens on elevated) |
| **EN 12101** (applicable parts) | Smoke/heat control candidate | Open-air configuration does not automatically exempt cabinets, enclosed approaches or future variants; applicability assessment open |
| **Applicable UPS and emergency-power requirements** | Station backup power, battery/fire protection and load endurance | UPS specification, critical-load allocation, product scope, installed runtime and authority decisions open; no NFPA 110 classification claimed |

## Cybersecurity + physical security

| Standard | Scope | Evidence status |
|---|---|---|
| **IEC 62443** (parts 2-4 + 4-2) | Industrial automation + control systems cybersecurity | `osr-station-scada` designed per `osr-crypto` discipline |
| **EN 50159** | Safety-related railway communications candidate | `osr-station-scada` design intent; channel classification, adopted clauses, configuration-specific tests and acceptance open |

## National overlays (Iraq — per-deployment)

Confirm the actual national/local electrical, fire, accessibility and railway
rules, identifiers, editions, competent authorities and approval route. This
planning document does not establish their current legal status or adoption.
Arabic signage and representative user needs belong in the project access plan.

Publisher scope review: [BSI EN 45545-1](https://knowledge.bsigroup.com/products/railway-applications-fire-protection-on-railway-vehicles-general)
concerns onboard vehicle fire protection. [IEC 60439-1](https://webstore.iec.ch/en/publication/16182)
is replaced; [IEC 61439-1:2020](https://webstore.iec.ch/en/publication/32338)
is a general assembly scope used with the applicable product part. These public
records do not establish full-clause conformity.

## Acceptance-test outline (pre-opening)

Unperformed candidate test outline. Adopt configuration-specific procedures,
limits, calibration, representative scenarios and independent acceptance before
using any entry as a pre-opening sign-off:

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

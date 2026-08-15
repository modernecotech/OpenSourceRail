# Compliance matrix — `light-metro-3car`

Standards the consist is designed against. Every row is a type-
approval campaign the operator runs pre-revenue. Upstream
provides the design envelope; each deployment owns its own
test-house relationship.

## Structural + mechanical

| Standard | Scope | Evidence for v1 → v2 |
|---|---|---|
| **EN 15227** Cat C-II | Crashworthiness at 25 km/h metro scenario | FEA simulation report (v2) |
| **EN 12663** Cat P-III | Static + fatigue body loading | FEA report (v2) |
| **EN 14363** | Dynamic behaviour + safety against derailment | On-track test campaign (v3) |
| **EN 13749** | Bogie frame fatigue + structural | FEA + test-rig (v2/v3) |
| **EN 15085** CL1–CL4 | Weld quality per assembly | Per-welder EN ISO 9606 certificates (v2) |
| **UIC 510-2** | Wheel profile + wear limits | Monobloc certificate from supplier (v1 source) |
| **UIC 505-1** | Structure gauge | General-arrangement compliance shown (v1 ✓) |

## Fire + materials

| Standard | Scope | Evidence |
|---|---|---|
| **EN 45545-2 HL2** | Fire behaviour of materials | Per-material test reports from an accredited lab (v2 campaign) |
| Applied to: body, seats, flooring, cabling, insulation, door rubbers | | |

## Electrical + electronic

| Standard | Scope | Evidence |
|---|---|---|
| **EN 50155** OT4 | On-board electronic equipment ambient class | Per-PCB compliance (RFC 0007 v1 bring-up) |
| **EN 50121-3-2** | Rolling-stock EMC | Pre-compliance sweep on test car (v3) |
| **EN 50126** | RAMS lifecycle | SIL-4 safety case — links into `docs/safety-case/` |
| **EN 50128** | Software for railway control — SIL-4 | Coding standard per RFC 0005 §7; evidence per crate |
| **EN 50129** | Safety-related electronic systems — SIL-4 | Composite fail-safe argument for T-ECU/S (RFC 0007 §4.1) |

## Passenger experience + accessibility

| Standard | Scope | Evidence |
|---|---|---|
| **EN 12299** | Ride-comfort indices | Dynamic-ride test (v3) |
| **ISO 3095** | External + internal noise | Acoustic measurement (v3) |
| **UIC 741** | Platform-to-train gap | General arrangement + gap-filler flap spec (v1 ✓) |
| **EN 14752** | Door systems | IFE type-4 door or equiv. (v1 source-identified) |
| **EN 16586** | Accessibility PRM | Wheelchair-space layout and COTS fit-out envelopes (v1 — see COTS catalogue) |
| **EN 15152** | Windows | Laminated safety glass (v1 source-identified) |

## Onboard safety systems

| Standard | Scope | Evidence |
|---|---|---|
| **EN 50126** / **EN 50128** / **EN 50129** as above for SIL-4 | Every onboard SIL-4 crate has proptest + Kani evidence | Per-crate solution nodes in the GSN safety case |
| **EN 14033** | Rail infrastructure works — applies to self-propelled work consists (n/a for revenue service) | n/a |

## Target-region overlays (per-deployment)

Each country's NRSA (or equivalent) has its own approval
process. Common overlays:

- Iraq (RFC 0003 Samawah): Iraqi Railways directorate approval.
- GCC region: GCC rail-authorities common spec.
- Sub-Saharan Africa: per-country; AU railways coordination
  underway.

v1 does NOT enumerate overlays — that is the operator's
NRSA-liaison scope. Upstream provides the EN-standard base.

## Test-campaign ordering

A typical sequence from design freeze to revenue:

1. **v2 CAD release:** FEA reports (EN 15227, EN 12663, EN 13749).
2. **v2A drawing register release:** controlled drawings, supplier
   installation documents, and evidence gates issued per
   [`drawing-register.md`](drawing-register.md).
3. **First-article prototype:** EN 45545 material test campaigns.
4. **Static test on bogie rig:** EN 13749 frame fatigue.
5. **Dynamic test (pilot deployment):** EN 14363 derailment
   safety; EN 12299 ride comfort; ISO 3095 noise;
   EN 50121-3-2 EMC.
6. **Safety-case sign-off:** EN 50126 lifecycle file complete.
7. **NRSA approval.**
8. **Revenue service.**

Steps 1–5 are fabricator + accredited-test-house scope.
Steps 6–7 are operator + project-safety-team scope.

## What v1 commits to

- Source-identified parts where such parts exist (Scharfenberg
  coupler, IFE door, PZ pantograph, EN 45545 materials).
- BID scope clearly delimited (motor, inverter, battery pack).
- MAKE scope matched to local fabricator capability (cut/bend/weld
  body frame, bogie frames, brackets, wiring harness).
- No proprietary/closed interfaces anywhere in the consist.

## What v1 does NOT commit to

- Specific test-house accreditation (per-country choice).
- Specific national-regulatory overlay fitments (flag signage,
  emergency PA language, fare-gate integration — all
  per-deployment).
- Second-source data for BID parts (v2).

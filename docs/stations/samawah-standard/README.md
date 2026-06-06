# Samawah `standard` archetype — architectural envelope v1

**Scope:** architectural envelope + canopy first-pass structural
calc for the Samawah reference deployment's standard-archetype
station, serving as the buildable spec an architect-of-record
can tender against. Applicable to every `standard`-archetype
station on Samawah Line 1 + Line 2 — that's 12 of the 22
stations in the deployment.

**Reference consist:** `light-metro-3car` per RFC 0008.
**Platform clearance:** 10 m per RFC 0010 §4.1.
**Generic platform length:** 51 + 10 = **61 m**.
**Samawah build allowance:** **75 m** safeguarded civil length for
local clearance and later fleet growth.

## Contents

| File | Scope |
|---|---|
| [`envelope.md`](envelope.md) | Plan + section geometry, ground-level access, egress |
| [`canopy.md`](canopy.md) | Solar canopy structural envelope + PV sizing + first-pass load calc |
| [`accessibility.md`](accessibility.md) | Step-free path, tactile paving, wheelchair zones, audio+visual per EN 16586 |
| [`services.md`](services.md) | Lighting, fire, drainage, small service cabinet, signage |
| [`compliance.md`](compliance.md) | Standards matrix (NFPA 130 egress, EN 12464-2 lighting, etc.) |

## Why this is repeatable

The whole point of RFC 0010's 6-archetype catalogue is to avoid
bespoke station design per deployment. This envelope is applied
**unchanged** at every `standard`-archetype station on Samawah
— 12 stations out of 22. The operator's architect-of-record
adapts it only for:

- Site-specific property-line constraints.
- Cardinal orientation (to aim the canopy PV south/north of
  equator for Samawah: south-facing).
- Pedestrian-connection geometry to the surrounding street
  network.
- Local material availability for façade finishes (all
  structural choices stay fixed).

## Site list — where this applies (Line 1 + Line 2)

From [`design.toml`](../../../designs/west-asia/Iraq/Samawah/design.toml):

### Line 1 (5 `standard` stations)

- north-gate
- old-souq *(note: override sets `canopy_type = shelter-only`;
  this arch envelope applies with canopy removed — §canopy.md
  covers the rain-shelter alternate)*
- riverside
- al-salam
- engineering-quarter

### Line 2 (7 `standard` stations)

- northern-suburbs-a
- northern-suburbs-b
- industrial-west
- western-residential
- south-west-residential
- south-east-residential

Other archetypes (`major`, `interchange`, `terminal`,
`depot-terminal`) have their own envelope docs (v2 scope —
not in this session).

## Licensing

v1 specification: CC-BY-SA 4.0.
v2 architectural drawings: CERN-OHL-S v2.

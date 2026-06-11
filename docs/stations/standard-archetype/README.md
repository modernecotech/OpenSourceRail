# Standard Station Archetype Worked Example

**Scope:** architectural envelope + canopy first-pass structural
calc for the shared `standard` station archetype. The worked dimensions
use a 75 m safeguarded platform and hot-climate assumptions; each
deployment overrides climate, orientation, and parcel interfaces through
the generated city model and local survey package.

**Reference consist:** `light-metro-3car` per RFC 0008.
**Platform clearance:** 10 m per RFC 0010 §4.1.
**Generic platform length:** 51 + 10 = **61 m**.
**Instance build allowance:** **75 m** safeguarded civil length for
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
unchanged wherever the generated design selects the `standard`
archetype. The operator's architect-of-record adapts it only for:

- Site-specific property-line constraints.
- Cardinal orientation (to aim the canopy PV south/north of
  equator; south-facing in the Iraq worked climate case).
- Pedestrian-connection geometry to the surrounding street
  network.
- Local material availability for façade finishes (all
  structural choices stay fixed).

## Licensing

v1 specification: CC-BY-SA 4.0.
v2 architectural drawings: CERN-OHL-S v2.

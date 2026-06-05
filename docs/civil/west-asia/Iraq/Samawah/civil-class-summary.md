# Samawah civil-class summary

Consolidated from [`line1-segments.md`](line1-segments.md) and
[`line2-segments.md`](line2-segments.md). Per-line and total
civil-class shares, against RFC 0011's at-grade dominance
target (≥ 70 %).

## Per-line shares

### Line 1 (Nahrain, 13 km)

| Class | Length (m) | Share |
|---|---|---|
| at-grade | 9 500 | 73 % |
| elevated | 2 400 | 18 % |
| bridge | 1 200 | 9 % |
| tunnel | 0 | 0 % (invariant per RFC 0011) |

### Line 2 (Halqa, 16 km ring)

| Class | Length (m) | Share |
|---|---|---|
| at-grade | 14 500 | 91 % |
| elevated | 1 500 | 9 % |
| bridge | 0 | 0 % |
| tunnel | 0 | 0 % |

### Consolidated (29 km total)

| Class | Length (m) | Share |
|---|---|---|
| at-grade | 24 000 | 83 % |
| elevated | 3 900 | 13 % |
| bridge | 1 200 | 4 % |
| tunnel | 0 | 0 % |

**Passes RFC 0011's ≥ 70 % at-grade target** by a comfortable
margin. No soft-gate trip for `elevated_le_0.30` per the
emitter's quality YAML.

## Costing

This file deliberately does not carry a separate Samawah cost model.
Generated CAPEX lives in
[`designs/west-asia/Iraq/Samawah/design.toml`](../../../../../designs/west-asia/Iraq/Samawah/design.toml)
and the generated city report at
[`designs/west-asia/Iraq/Samawah/README.md`](../../../../../designs/west-asia/Iraq/Samawah/README.md).
Those artefacts read the canonical rates from
[`lib/templates/capex-costs.toml`](../../../../../lib/templates/capex-costs.toml).

The civil package here is only the worked alignment envelope: line
lengths, civil class shares, land take, and constructability risks.

## Land acquisition

29 km of double-track ROW at 10.5 m width:
- At-grade: 24 km × 10.5 m = 25.2 ha.
- Elevated: 3.9 km × 6 m footprint (piers + walkway) = 2.3 ha.
- Bridge: 1.2 km × 6 m = 0.7 ha.
- Stations + depots: ~3 ha.

**Total land acquisition: ~31 ha.**

For Samawah context (urban core population ~250 k, municipal
area ~50 km²), this is a small fraction of urban land — ≈ 0.06 %.
Several segments follow the existing Mosul Street corridor +
the highway east of the river; those use existing public ROW
with minimal acquisition.

## Risk register (civil-side)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Euphrates flood level rise | Medium | High | Bridge design 100-year flood +2 m (RFC 0011 §6). |
| Land-acquisition objections | Medium | Medium | Route follows existing ROW where possible; per-parcel negotiation. |
| Local fabricator capacity for precast U-girder | Low | Medium | One yard serves the whole project; 18-month production at 20 forms. |
| Dust-storm effect on construction schedule | High | Low | Pad ROW + prefab bay weather enclosure. |
| Groundwater depth variability at pier foundations | Medium | Medium | Geotech survey before each pier; foundation depth per-site. |

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

## Cost estimate (per RFC 0011 §9 rates)

Planning-grade USD/km direct-procurement floor × civil mix:

| Class | USD/km | Length | Subtotal (USD) |
|---|---|---|---|
| at-grade | 1 200 000 | 24 km | 28 800 000 |
| elevated | 5 500 000 | 3.9 km | 21 450 000 |
| bridge | 8 000 000 | 1.2 km | 9 600 000 |
| **Civil total** | | | **$59 850 000** |

Generated city `design.toml` files keep EUR mirrors at 0.92 USD->EUR
for schema compatibility, but the procurement basis is USD. Country
cost factors for Iraq can still be applied downstream (from
[`lib/templates/country-costs.toml`](../../../../../lib/templates/country-costs.toml)):
- Labour discount: ~0.4 × OECD.
- Materials: ~0.95 × OECD.
- Effective factor: ~0.65.

**Samawah two-line civil CAPEX floor: ~$60 M before local factor; ~$39 M
if the full Iraq factor is applied.**

Note: this is **civil only** — track + viaducts + bridges. It
excludes:

- Rolling stock (~$0.800 M × 16 three-car trainsets = ~$13 M,
  using the current marketplace-BOM floor for the 3-car RFC 0008 basis).
- Stations (~$0.450 M per `standard`, with majors/terminals/interchanges
  scaled from the station archetype table
  + interchanges).
- Depots (~$7.5 M for the `main-heavy` east depot + ~$0.9 M
  for the `layup-minimal`).
- Residual train-control wayside + radio/OCC integration (~$0.4 M;
  train protection is primarily onboard driverless sensing).
- Procurement, engineering, contingency (~20 %).

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

## Comparison to legacy equivalents

A 29 km light-metro project in the Middle East at legacy-vendor
pricing (CAPEX-only, civil + signalling + rolling stock) is
typically quoted at **$1–3 billion** in 2026-era bids.

The OSR Samawah deployment budgets around **$120–185 M** all-in under
the direct-procurement floor; the current auto-generated larger network
lands near **$165 M** after the 2026 rail/station-rate refresh.
This is the catenary-free + local-manufacturability +
simple-civil bet playing out in practice. The largest single
savings:

- No continuous catenary: saves ~$60 M.
- No tunnelling (vs the typical 20 % tunnelled urban alignment):
  saves ~$500–800 M.
- Onboard-first driverless protection instead of a proprietary CBTC
  vendor stack: saves ~$30–80 M over 30 years.
- Commodity rolling stock vs bespoke: saves ~$75–95 M over a
  fleet of 16 trainsets at the marketplace-BOM floor.

The residual difference is OpenSourceRail's structural CAPEX
target. A real deployment may come in higher — ~$250 M is a
realistic upper bound for contingency + land + overheads — but
not an order of magnitude higher like legacy bids.

## Risk register (civil-side)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Euphrates flood level rise | Medium | High | Bridge design 100-year flood +2 m (RFC 0011 §6). |
| Land-acquisition objections | Medium | Medium | Route follows existing ROW where possible; per-parcel negotiation. |
| Local fabricator capacity for precast U-girder | Low | Medium | One yard serves the whole project; 18-month production at 20 forms. |
| Dust-storm effect on construction schedule | High | Low | Pad ROW + prefab bay weather enclosure. |
| Groundwater depth variability at pier foundations | Medium | Medium | Geotech survey before each pier; foundation depth per-site. |

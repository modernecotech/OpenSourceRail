# Davao — Urban Rail Network

**Country:** PH · **Population:** 1,827,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Davao-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.43 bn (86.4%) of external capital** and **$4.21 bn of external interest**. Capital plus saved interest totals **$7.64 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Davao rail network on OpenStreetMap](davao-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 99 / 10 |
| Route length | 280.2 km double track |
| Coverage / transfer reachability | 39.2% / 33% |
| Estimated station catchment | 716,184 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 329 × 4-car `metro-4car` trainsets (296 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 47.2 km | 17 | 72 | NE Outer ↔ SW Outer |
| line-2 | 40.4 km | 15 | 62 | NW Outer ↔ SE Mid |
| line-3 | 36.4 km | 12 | 54 | E Outer ↔ W Mid |
| line-4 | 36.9 km | 14 | 58 | W Mid ↔ E Outer |
| line-5 | 32.1 km | 11 | 49 | NW Outer ↔ SE Mid |
| line-6 | 87.3 km | 30 | 34 | NW Mid ↔ NW Mid |
| **Total** | **280.2 km** | **99 unique** | **329** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 109,997 train-km/day |
| Annual traction demand | 693.8 GWh |
| Station/depot PV / storage | 32.3 MW / 176.5 MWh |
| Aggregate charging power | 138.0 MW |
| Dedicated solar plant | 418.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 11.0 km / 110 kWh |
| Lowest traversal charging margin | line-5: 236 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $859 M |
| Stations | $468 M |
| Depots | $8.0 M |
| Rolling stock | $368 M |
| Dedicated solar plant | $335 M |
| Residual train control | $14 M |
| Charging microgrids | $30 M |
| EPC / project services | $122 M |
| **Total city programme** | **$2.20 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $541 M (24.6%) |
| Domestic / local capital | $1.66 bn (75.4%) |
| Annual public construction commitment | $173 M / yr for 5 years |
| Annual post-grace debt service | $125 M / yr |
| External capital saved vs default turnkey sensitivity | $3.43 bn |
| Capital + lifetime external interest saved | $7.64 bn |
| Annual OPEX | $54 M / yr |

## Local Evidence

**Evidence refresh required.** Retained passing results below are unverified.
The strict README generator rejected the evidence: engineering/simulation/validation-summary.json describes scenario SHA-256 d31fdaac322b583878411327c7c7be22474ca52f8a60853ff8eaec2750358c13, but davao.toml is fe309a8cab5a540d117570b09d84df3d85d34213aef0e60fc36011c5d8eb95c0; rerun and update the validation evidence. This audit view does not accept or replace the retained solver results.

| Package | Current status | Evidence |
|---|---|---|
| Finance | unverified | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | unverified | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | unverified | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | missing/fail; junction/authority gate open | not generated |
| GIS package | unverified | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | unverified; 0 findings; 58 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 878 assets / 3,808 tasks | [`davao-operations-manifest.json`](operations/davao-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`davao.toml`](davao.toml) | Expanded simulator scenario |
| [`davao.corridor.geojson`](davao.corridor.geojson) | GIS corridor and stations |
| [`davao.design-quality.yaml`](davao.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh davao
```

# Garoua — Urban Rail Network

**Country:** CM · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Garoua-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$502 M (87.5%) of external capital** and **$629 M of external interest**. Capital plus saved interest totals **$1.13 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Garoua rail network on OpenStreetMap](garoua-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 1 |
| Route length | 33.0 km double track |
| Coverage / transfer reachability | 66.4% / 33% |
| Estimated station catchment | 398,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 73 × 3-car `light-metro-3car` trainsets (65 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.2 km | 6 | 31 | SW Outer ↔ NE Outer |
| line-2 | 10.9 km | 4 | 24 | S Mid ↔ N Outer |
| line-3 |  7.8 km | 4 | 18 | W Outer ↔ N Mid |
| **Total** | **33.0 km** | **14 unique** | **73** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 15,334 train-km/day |
| Annual traction demand | 72.5 GWh |
| Station/depot PV / storage | 8.9 MW / 46.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 24.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.1 km / 51 kWh |
| Lowest traversal charging margin | line-3: 26 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $140 M |
| Stations | $62 M |
| Depots | $8.0 M |
| Rolling stock | $66 M |
| Dedicated solar plant | $20 M |
| Residual train control | $1.6 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $20 M |
| **Total city programme** | **$319 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $72 M (22.5%) |
| Domestic / local capital | $247 M (77.5%) |
| Annual public construction commitment | $27 M / yr for 7 years |
| Annual post-grace debt service | $22 M / yr |
| External capital saved vs default turnkey sensitivity | $502 M |
| Capital + lifetime external interest saved | $1.13 bn |
| Annual OPEX | $8.0 M / yr |

## Local Evidence

**Evidence refresh required.** Retained passing results below are unverified.
The strict README generator rejected the evidence: engineering/simulation/validation-summary.json describes scenario SHA-256 8f5075db3ac979e01b9c928a313b084e92395359c87e054513a39c7c70a8240d, but garoua.toml is c1028d679f64f1e2dc7960558ccffa06626edd8cccce1cdc2ee3454d67bac646; rerun and update the validation evidence. This audit view does not accept or replace the retained solver results.

| Package | Current status | Evidence |
|---|---|---|
| Finance | unverified | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | unverified | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | unverified | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | unverified; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | unverified | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | unverified; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 157 assets / 909 tasks | [`garoua-operations-manifest.json`](operations/garoua-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`garoua.toml`](garoua.toml) | Expanded simulator scenario |
| [`garoua.corridor.geojson`](garoua.corridor.geojson) | GIS corridor and stations |
| [`garoua.design-quality.yaml`](garoua.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh garoua
```

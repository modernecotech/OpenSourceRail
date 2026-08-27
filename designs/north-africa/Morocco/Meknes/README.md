# Meknes — Urban Rail Network

**Country:** MA · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Meknes-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$535 M (86.6%) of external capital** and **$658 M of external interest**. Capital plus saved interest totals **$1.19 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Meknes rail network on OpenStreetMap](meknes-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 39.4 km double track |
| Coverage / transfer reachability | 58.0% / 100% |
| Estimated station catchment | 406,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 89 × 3-car `light-metro-3car` trainsets (79 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.7 km | 6 | 35 | NE Outer ↔ SW Outer |
| line-2 | 12.2 km | 5 | 27 | N Outer ↔ S Mid |
| line-3 | 11.4 km | 6 | 27 | S Mid ↔ NW Mid |
| **Total** | **39.4 km** | **17 unique** | **89** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 18,302 train-km/day |
| Annual traction demand | 86.6 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 38.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 4.7 km / 34 kWh |
| Lowest traversal charging margin | line-2: 46 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $115 M |
| Stations | $86 M |
| Depots | $8.0 M |
| Rolling stock | $80 M |
| Dedicated solar plant | $31 M |
| Residual train control | $2.0 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $20 M |
| **Total city programme** | **$343 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $83 M (24.2%) |
| Domestic / local capital | $260 M (75.8%) |
| Annual public construction commitment | $24 M / yr for 5 years |
| Annual post-grace debt service | $17 M / yr |
| External capital saved vs default turnkey sensitivity | $535 M |
| Capital + lifetime external interest saved | $1.19 bn |
| Annual OPEX | $9.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 192 assets / 885 tasks | [`meknes-operations-manifest.json`](operations/meknes-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`meknes.toml`](meknes.toml) | Expanded simulator scenario |
| [`meknes.corridor.geojson`](meknes.corridor.geojson) | GIS corridor and stations |
| [`meknes.design-quality.yaml`](meknes.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh meknes
```

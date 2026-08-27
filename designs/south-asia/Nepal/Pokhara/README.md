# Pokhara — Urban Rail Network

**Country:** NP · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Pokhara-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$994 M (86.6%) of external capital** and **$1.25 bn of external interest**. Capital plus saved interest totals **$2.24 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Pokhara rail network on OpenStreetMap](pokhara-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 25 / 2 |
| Route length | 81.2 km double track |
| Coverage / transfer reachability | 40.8% / 100% |
| Estimated station catchment | 244,799 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 172 × 3-car `light-metro-3car` trainsets (155 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.9 km | 9 | 63 | SE Outer ↔ NW Outer |
| line-2 | 23.8 km | 8 | 51 | NW Mid ↔ SE Outer |
| line-3 | 27.4 km | 8 | 58 | NW Outer ↔ SE Outer |
| **Total** | **81.2 km** | **25 unique** | **172** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 37,758 train-km/day |
| Annual traction demand | 178.6 GWh |
| Station/depot PV / storage | 11.9 MW / 51.5 MWh |
| Aggregate charging power | 12.0 MW |
| Dedicated solar plant | 77.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 11.6 km / 84 kWh |
| Lowest traversal charging margin | line-2: 105 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $243 M |
| Stations | $127 M |
| Depots | $8.0 M |
| Rolling stock | $155 M |
| Dedicated solar plant | $62 M |
| Residual train control | $4.1 M |
| Charging microgrids | $2.7 M |
| EPC / project services | $38 M |
| **Total city programme** | **$638 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $154 M (24.2%) |
| Domestic / local capital | $484 M (75.8%) |
| Annual public construction commitment | $50 M / yr for 7 years |
| Annual post-grace debt service | $41 M / yr |
| External capital saved vs default turnkey sensitivity | $994 M |
| Capital + lifetime external interest saved | $2.24 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 327 assets / 1,596 tasks | [`pokhara-operations-manifest.json`](operations/pokhara-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`pokhara.toml`](pokhara.toml) | Expanded simulator scenario |
| [`pokhara.corridor.geojson`](pokhara.corridor.geojson) | GIS corridor and stations |
| [`pokhara.design-quality.yaml`](pokhara.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh pokhara
```

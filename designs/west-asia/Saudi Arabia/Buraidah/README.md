# Buraidah — Urban Rail Network

**Country:** SA · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Buraidah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$844 M (86.5%) of external capital** and **$1.04 bn of external interest**. Capital plus saved interest totals **$1.88 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Buraidah rail network on OpenStreetMap](buraidah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 27 / 1 |
| Route length | 69.2 km double track |
| Coverage / transfer reachability | 46.1% / 100% |
| Estimated station catchment | 322,700 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 146 × 3-car `light-metro-3car` trainsets (131 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.3 km | 9 | 60 | SE Outer ↔ NW Outer |
| line-2 | 20.9 km | 9 | 46 | NW Mid ↔ SE Mid |
| line-3 | 19.0 km | 9 | 40 | S Mid ↔ N Mid |
| **Total** | **69.2 km** | **27 unique** | **146** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 32,199 train-km/day |
| Annual traction demand | 152.3 GWh |
| Station/depot PV / storage | 12.8 MW / 53.0 MWh |
| Aggregate charging power | 13.5 MW |
| Dedicated solar plant | 65.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 6.9 km / 55 kWh |
| Lowest traversal charging margin | line-3: 52 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $193 M |
| Stations | $118 M |
| Depots | $8.0 M |
| Rolling stock | $131 M |
| Dedicated solar plant | $52 M |
| Residual train control | $3.5 M |
| Charging microgrids | $2.9 M |
| EPC / project services | $32 M |
| **Total city programme** | **$542 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $132 M (24.3%) |
| Domestic / local capital | $410 M (75.7%) |
| Annual public construction commitment | $37 M / yr for 5 years |
| Annual post-grace debt service | $26 M / yr |
| External capital saved vs default turnkey sensitivity | $844 M |
| Capital + lifetime external interest saved | $1.88 bn |
| Annual OPEX | $24 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 307 assets / 1,442 tasks | [`buraidah-operations-manifest.json`](operations/buraidah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`buraidah.toml`](buraidah.toml) | Expanded simulator scenario |
| [`buraidah.corridor.geojson`](buraidah.corridor.geojson) | GIS corridor and stations |
| [`buraidah.design-quality.yaml`](buraidah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh buraidah
```

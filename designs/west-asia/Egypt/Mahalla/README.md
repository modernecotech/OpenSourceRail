# Mahalla — Urban Rail Network

**Country:** EG · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mahalla-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$523 M (86.8%) of external capital** and **$643 M of external interest**. Capital plus saved interest totals **$1.17 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mahalla rail network on OpenStreetMap](mahalla-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 16 / 2 |
| Route length | 38.3 km double track |
| Coverage / transfer reachability | 68.2% / 33% |
| Estimated station catchment | 409,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 84 × 3-car `light-metro-3car` trainsets (75 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.3 km | 5 | 27 | W Inner ↔ E Outer |
| line-2 | 18.6 km | 7 | 41 | SW Outer ↔ NE Mid |
| line-3 |  7.4 km | 4 | 16 | NW Inner ↔ NE Mid |
| **Total** | **38.3 km** | **16 unique** | **84** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 17,802 train-km/day |
| Annual traction demand | 84.2 GWh |
| Station/depot PV / storage | 8.9 MW / 46.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 34.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.8 km / 87 kWh |
| Lowest traversal charging margin | line-3: 24 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $123 M |
| Stations | $77 M |
| Depots | $8.0 M |
| Rolling stock | $76 M |
| Dedicated solar plant | $27 M |
| Residual train control | $1.9 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $20 M |
| **Total city programme** | **$335 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $79 M (23.7%) |
| Domestic / local capital | $255 M (76.3%) |
| Annual public construction commitment | $35 M / yr for 5 years |
| Annual post-grace debt service | $27 M / yr |
| External capital saved vs default turnkey sensitivity | $523 M |
| Capital + lifetime external interest saved | $1.17 bn |
| Annual OPEX | $8.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 180 assets / 829 tasks | [`mahalla-operations-manifest.json`](operations/mahalla-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mahalla.toml`](mahalla.toml) | Expanded simulator scenario |
| [`mahalla.corridor.geojson`](mahalla.corridor.geojson) | GIS corridor and stations |
| [`mahalla.design-quality.yaml`](mahalla.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh mahalla
```

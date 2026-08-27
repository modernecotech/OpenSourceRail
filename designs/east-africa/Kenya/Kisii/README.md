# Kisii — Urban Rail Network

**Country:** KE · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kisii-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$324 M (87.9%) of external capital** and **$407 M of external interest**. Capital plus saved interest totals **$731 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kisii rail network on OpenStreetMap](kisii-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 12 / 1 |
| Route length | 24.3 km double track |
| Coverage / transfer reachability | 89.8% / 33% |
| Estimated station catchment | 269,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 52 × 2-car `tram-2car` trainsets (46 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.1 km | 4 | 16 | SE Mid ↔ W Mid |
| line-2 |  6.3 km | 4 | 15 | NW Mid ↔ SW Inner |
| line-3 | 10.9 km | 4 | 21 | N Outer ↔ SE Mid |
| **Total** | **24.3 km** | **12 unique** | **52** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 11,290 train-km/day |
| Annual traction demand | 35.6 GWh |
| Station/depot PV / storage | 8.3 MW / 45.5 MWh |
| Aggregate charging power | 6.0 MW |
| Dedicated solar plant | 13.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.3 km / 32 kWh |
| Lowest traversal charging margin | line-3: 38 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $76 M |
| Stations | $66 M |
| Depots | $8.0 M |
| Rolling stock | $29 M |
| Dedicated solar plant | $11 M |
| Residual train control | $1.2 M |
| Charging microgrids | $1.4 M |
| EPC / project services | $13 M |
| **Total city programme** | **$205 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $45 M (21.8%) |
| Domestic / local capital | $160 M (78.2%) |
| Annual public construction commitment | $21 M / yr for 7 years |
| Annual post-grace debt service | $18 M / yr |
| External capital saved vs default turnkey sensitivity | $324 M |
| Capital + lifetime external interest saved | $731 M |
| Annual OPEX | $5.2 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 124 assets / 545 tasks | [`kisii-operations-manifest.json`](operations/kisii-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kisii.toml`](kisii.toml) | Expanded simulator scenario |
| [`kisii.corridor.geojson`](kisii.corridor.geojson) | GIS corridor and stations |
| [`kisii.design-quality.yaml`](kisii.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh kisii
```

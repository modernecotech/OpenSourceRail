# Waw — Urban Rail Network

**Country:** SD · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Waw-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$248 M (88.3%) of external capital** and **$320 M of external interest**. Capital plus saved interest totals **$568 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Waw rail network on OpenStreetMap](waw-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 9 / 2 |
| Route length | 18.3 km double track |
| Coverage / transfer reachability | 75.2% / 100% |
| Estimated station catchment | 225,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 41 × 2-car `tram-2car` trainsets (35 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.1 km | 4 | 17 | NW Mid ↔ S Outer |
| line-2 |  7.9 km | 3 | 16 | N Outer ↔ S Inner |
| line-3 |  2.2 km | 2 | 8 | SE Inner ↔ W Inner |
| **Total** | **18.3 km** | **9 unique** | **41** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 8,495 train-km/day |
| Annual traction demand | 26.8 GWh |
| Station/depot PV / storage | 7.4 MW / 44.0 MWh |
| Aggregate charging power | 4.5 MW |
| Dedicated solar plant | 4.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 4.4 km / 24 kWh |
| Lowest traversal charging margin | line-2: 21 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $60 M |
| Stations | $50 M |
| Depots | $8.0 M |
| Rolling stock | $23 M |
| Dedicated solar plant | $3.6 M |
| Residual train control | $913 k |
| Charging microgrids | $1.1 M |
| EPC / project services | $10.0 M |
| **Total city programme** | **$156 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $33 M (21.1%) |
| Domestic / local capital | $123 M (78.9%) |
| Annual public construction commitment | $19 M / yr for 10 years |
| Annual post-grace debt service | $17 M / yr |
| External capital saved vs default turnkey sensitivity | $248 M |
| Capital + lifetime external interest saved | $568 M |
| Annual OPEX | $3.7 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 97 assets / 422 tasks | [`waw-operations-manifest.json`](operations/waw-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`waw.toml`](waw.toml) | Expanded simulator scenario |
| [`waw.corridor.geojson`](waw.corridor.geojson) | GIS corridor and stations |
| [`waw.design-quality.yaml`](waw.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh waw
```

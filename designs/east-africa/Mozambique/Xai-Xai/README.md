# Xai-Xai — Urban Rail Network

**Country:** MZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Xai-Xai-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$261 M (87.6%) of external capital** and **$337 M of external interest**. Capital plus saved interest totals **$598 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Xai-Xai rail network on OpenStreetMap](xai-xai-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 1 |
| Route length | 22.2 km double track |
| Coverage / transfer reachability | 56.5% / 33% |
| Estimated station catchment | 141,250 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 47 × 2-car `tram-2car` trainsets (41 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.4 km | 5 | 20 | S Outer ↔ NE Mid |
| line-2 |  8.4 km | 4 | 17 | E Outer ↔ NW Outer |
| line-3 |  4.4 km | 2 | 10 | S Mid ↔ NE Outer |
| **Total** | **22.2 km** | **11 unique** | **47** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 10,336 train-km/day |
| Annual traction demand | 32.6 GWh |
| Station/depot PV / storage | 8.0 MW / 45.0 MWh |
| Aggregate charging power | 5.5 MW |
| Dedicated solar plant | 12.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 4.4 km / 22 kWh |
| Lowest traversal charging margin | line-3: 25 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $58 M |
| Stations | $51 M |
| Depots | $8.0 M |
| Rolling stock | $26 M |
| Dedicated solar plant | $9.8 M |
| Residual train control | $1.1 M |
| Charging microgrids | $1.2 M |
| EPC / project services | $10 M |
| **Total city programme** | **$166 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $37 M (22.4%) |
| Domestic / local capital | $129 M (77.6%) |
| Annual public construction commitment | $18 M / yr for 10 years |
| Annual post-grace debt service | $16 M / yr |
| External capital saved vs default turnkey sensitivity | $261 M |
| Capital + lifetime external interest saved | $598 M |
| Annual OPEX | $4.0 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 113 assets / 494 tasks | [`xai-xai-operations-manifest.json`](operations/xai-xai-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`xai-xai.toml`](xai-xai.toml) | Expanded simulator scenario |
| [`xai-xai.corridor.geojson`](xai-xai.corridor.geojson) | GIS corridor and stations |
| [`xai-xai.design-quality.yaml`](xai-xai.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh xai-xai
```

# Shinyanga — Urban Rail Network

**Country:** TZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Shinyanga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$393 M (87.8%) of external capital** and **$492 M of external interest**. Capital plus saved interest totals **$885 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Shinyanga rail network on OpenStreetMap](shinyanga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 1 |
| Route length | 36.8 km double track |
| Coverage / transfer reachability | 83.2% / 100% |
| Estimated station catchment | 208,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 76 × 2-car `tram-2car` trainsets (68 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.9 km | 6 | 32 | NE Outer ↔ SW Mid |
| line-2 |  9.6 km | 4 | 20 | W Mid ↔ S Inner |
| line-3 | 11.3 km | 4 | 24 | SE Inner ↔ S Outer |
| **Total** | **36.8 km** | **14 unique** | **76** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 17,104 train-km/day |
| Annual traction demand | 53.9 GWh |
| Station/depot PV / storage | 8.6 MW / 46.0 MWh |
| Aggregate charging power | 6.5 MW |
| Dedicated solar plant | 16.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.0 km / 39 kWh |
| Lowest traversal charging margin | line-3: 29 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $104 M |
| Stations | $62 M |
| Depots | $8.0 M |
| Rolling stock | $43 M |
| Dedicated solar plant | $13 M |
| Residual train control | $1.8 M |
| Charging microgrids | $1.4 M |
| EPC / project services | $15 M |
| **Total city programme** | **$249 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $55 M (22.0%) |
| Domestic / local capital | $194 M (78.0%) |
| Annual public construction commitment | $23 M / yr for 7 years |
| Annual post-grace debt service | $19 M / yr |
| External capital saved vs default turnkey sensitivity | $393 M |
| Capital + lifetime external interest saved | $885 M |
| Annual OPEX | $6.2 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 160 assets / 743 tasks | [`shinyanga-operations-manifest.json`](operations/shinyanga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`shinyanga.toml`](shinyanga.toml) | Expanded simulator scenario |
| [`shinyanga.corridor.geojson`](shinyanga.corridor.geojson) | GIS corridor and stations |
| [`shinyanga.design-quality.yaml`](shinyanga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh shinyanga
```

# Naivasha — Urban Rail Network

**Country:** KE · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Naivasha-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$434 M (87.9%) of external capital** and **$544 M of external interest**. Capital plus saved interest totals **$978 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Naivasha rail network on OpenStreetMap](naivasha-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 1 |
| Route length | 39.0 km double track |
| Coverage / transfer reachability | 81.9% / 100% |
| Estimated station catchment | 204,750 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 79 × 2-car `tram-2car` trainsets (71 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.2 km | 5 | 29 | NW Outer ↔ S Outer |
| line-2 | 10.0 km | 4 | 20 | S Outer ↔ NE Inner |
| line-3 | 14.9 km | 5 | 30 | SE Outer ↔ NW Outer |
| **Total** | **39.0 km** | **14 unique** | **79** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 18,128 train-km/day |
| Annual traction demand | 57.2 GWh |
| Station/depot PV / storage | 8.6 MW / 46.0 MWh |
| Aggregate charging power | 6.5 MW |
| Dedicated solar plant | 17.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 8.3 km / 46 kWh |
| Lowest traversal charging margin | line-1: 28 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $113 M |
| Stations | $74 M |
| Depots | $8.0 M |
| Rolling stock | $44 M |
| Dedicated solar plant | $14 M |
| Residual train control | $1.9 M |
| Charging microgrids | $1.5 M |
| EPC / project services | $17 M |
| **Total city programme** | **$274 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $60 M (21.8%) |
| Domestic / local capital | $215 M (78.2%) |
| Annual public construction commitment | $29 M / yr for 7 years |
| Annual post-grace debt service | $24 M / yr |
| External capital saved vs default turnkey sensitivity | $434 M |
| Capital + lifetime external interest saved | $978 M |
| Annual OPEX | $7.0 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 164 assets / 765 tasks | [`naivasha-operations-manifest.json`](operations/naivasha-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`naivasha.toml`](naivasha.toml) | Expanded simulator scenario |
| [`naivasha.corridor.geojson`](naivasha.corridor.geojson) | GIS corridor and stations |
| [`naivasha.design-quality.yaml`](naivasha.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh naivasha
```

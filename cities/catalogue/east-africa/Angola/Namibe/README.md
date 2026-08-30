# Namibe — Urban Rail Network

**Country:** AO · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Namibe-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$451 M (87.8%) of external capital** and **$554 M of external interest**. Capital plus saved interest totals **$1.00 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Namibe rail network on OpenStreetMap](namibe-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 1 |
| Route length | 40.8 km double track |
| Coverage / transfer reachability | 63.6% / 100% |
| Estimated station catchment | 190,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 84 × 2-car `tram-2car` trainsets (75 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.0 km | 6 | 30 | SW Outer ↔ E Outer |
| line-2 | 12.1 km | 6 | 25 | NE Outer ↔ S Mid |
| line-3 | 13.8 km | 7 | 29 | NE Outer ↔ SW Outer |
| **Total** | **40.8 km** | **19 unique** | **84** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 18,973 train-km/day |
| Annual traction demand | 59.8 GWh |
| Station/depot PV / storage | 10.4 MW / 49.0 MWh |
| Aggregate charging power | 9.5 MW |
| Dedicated solar plant | 17.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 3.6 km / 20 kWh |
| Lowest traversal charging margin | line-2: 40 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $110 M |
| Stations | $84 M |
| Depots | $8.0 M |
| Rolling stock | $47 M |
| Dedicated solar plant | $14 M |
| Residual train control | $2.0 M |
| Charging microgrids | $2.0 M |
| EPC / project services | $18 M |
| **Total city programme** | **$285 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $63 M (21.9%) |
| Domestic / local capital | $223 M (78.1%) |
| Annual public construction commitment | $32 M / yr for 5 years |
| Annual post-grace debt service | $25 M / yr |
| External capital saved vs default turnkey sensitivity | $451 M |
| Capital + lifetime external interest saved | $1.00 bn |
| Annual OPEX | $7.4 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 195 assets / 878 tasks | [`namibe-operations-manifest.json`](operations/namibe-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`namibe.toml`](namibe.toml) | Expanded simulator scenario |
| [`namibe.corridor.geojson`](namibe.corridor.geojson) | GIS corridor and stations |
| [`namibe.design-quality.yaml`](namibe.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh namibe
```

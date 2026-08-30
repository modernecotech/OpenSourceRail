# Kakamega — Urban Rail Network

**Country:** KE · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kakamega-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$493 M (87.6%) of external capital** and **$618 M of external interest**. Capital plus saved interest totals **$1.11 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kakamega rail network on OpenStreetMap](kakamega-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 42.2 km double track |
| Coverage / transfer reachability | 77.2% / 100% |
| Estimated station catchment | 231,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 83 × 2-car `tram-2car` trainsets (74 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.6 km | 5 | 27 | W Mid ↔ SE Mid |
| line-2 | 15.4 km | 7 | 30 | NE Outer ↔ SW Mid |
| line-3 | 13.1 km | 5 | 26 | NW Mid ↔ S Outer |
| **Total** | **42.2 km** | **17 unique** | **83** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,606 train-km/day |
| Annual traction demand | 61.8 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 29.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 5.5 km / 27 kWh |
| Lowest traversal charging margin | line-1: 36 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $126 M |
| Stations | $86 M |
| Depots | $8.0 M |
| Rolling stock | $46 M |
| Dedicated solar plant | $23 M |
| Residual train control | $2.1 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $19 M |
| **Total city programme** | **$312 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $69 M (22.2%) |
| Domestic / local capital | $243 M (77.8%) |
| Annual public construction commitment | $32 M / yr for 7 years |
| Annual post-grace debt service | $27 M / yr |
| External capital saved vs default turnkey sensitivity | $493 M |
| Capital + lifetime external interest saved | $1.11 bn |
| Annual OPEX | $7.8 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 185 assets / 842 tasks | [`kakamega-operations-manifest.json`](operations/kakamega-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kakamega.toml`](kakamega.toml) | Expanded simulator scenario |
| [`kakamega.corridor.geojson`](kakamega.corridor.geojson) | GIS corridor and stations |
| [`kakamega.design-quality.yaml`](kakamega.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kakamega
```

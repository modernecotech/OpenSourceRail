# Sidon — Urban Rail Network

**Country:** LB · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sidon-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$447 M (87.8%) of external capital** and **$566 M of external interest**. Capital plus saved interest totals **$1.01 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Sidon rail network on OpenStreetMap](sidon-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 16 / 1 |
| Route length | 37.8 km double track |
| Coverage / transfer reachability | 85.1% / 100% |
| Estimated station catchment | 255,300 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 79 × 2-car `tram-2car` trainsets (71 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.0 km | 6 | 31 | S Mid ↔ N Outer |
| line-2 |  9.8 km | 5 | 21 | SW Mid ↔ S Mid |
| line-3 | 12.9 km | 5 | 27 | SE Inner ↔ NE Outer |
| **Total** | **37.8 km** | **16 unique** | **79** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 17,558 train-km/day |
| Annual traction demand | 55.4 GWh |
| Station/depot PV / storage | 8.9 MW / 46.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 21.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 8.3 km / 40 kWh |
| Lowest traversal charging margin | line-3: 30 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $111 M |
| Stations | $81 M |
| Depots | $8.0 M |
| Rolling stock | $44 M |
| Dedicated solar plant | $17 M |
| Residual train control | $1.9 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $17 M |
| **Total city programme** | **$283 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $62 M (22.0%) |
| Domestic / local capital | $221 M (78.0%) |
| Annual public construction commitment | $52 M / yr for 8 years |
| Annual post-grace debt service | $48 M / yr |
| External capital saved vs default turnkey sensitivity | $447 M |
| Capital + lifetime external interest saved | $1.01 bn |
| Annual OPEX | $7.4 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 173 assets / 792 tasks | [`sidon-operations-manifest.json`](operations/sidon-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sidon.toml`](sidon.toml) | Expanded simulator scenario |
| [`sidon.corridor.geojson`](sidon.corridor.geojson) | GIS corridor and stations |
| [`sidon.design-quality.yaml`](sidon.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sidon
```

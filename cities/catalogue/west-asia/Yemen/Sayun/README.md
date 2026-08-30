# Sayun — Urban Rail Network

**Country:** YE · **Population:** 200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sayun-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$328 M (88.1%) of external capital** and **$423 M of external interest**. Capital plus saved interest totals **$751 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Sayun rail network on OpenStreetMap](sayun-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 1 |
| Route length | 24.4 km double track |
| Coverage / transfer reachability | 79.3% / 100% |
| Estimated station catchment | 158,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 54 × 2-car `tram-2car` trainsets (47 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.2 km | 5 | 29 | E Outer ↔ W Outer |
| line-2 |  5.4 km | 3 | 13 | SW Inner ↔ NW Inner |
| line-3 |  4.9 km | 3 | 12 | SE Inner ↔ N Mid |
| **Total** | **24.4 km** | **11 unique** | **54** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 11,346 train-km/day |
| Annual traction demand | 35.8 GWh |
| Station/depot PV / storage | 8.0 MW / 45.0 MWh |
| Aggregate charging power | 5.5 MW |
| Dedicated solar plant | 9.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 6.1 km / 33 kWh |
| Lowest traversal charging margin | line-2: 34 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $77 M |
| Stations | $68 M |
| Depots | $8.0 M |
| Rolling stock | $30 M |
| Dedicated solar plant | $7.7 M |
| Residual train control | $1.2 M |
| Charging microgrids | $1.3 M |
| EPC / project services | $13 M |
| **Total city programme** | **$207 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $44 M (21.5%) |
| Domestic / local capital | $162 M (78.5%) |
| Annual public construction commitment | $29 M / yr for 10 years |
| Annual post-grace debt service | $26 M / yr |
| External capital saved vs default turnkey sensitivity | $328 M |
| Capital + lifetime external interest saved | $751 M |
| Annual OPEX | $4.7 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 122 assets / 545 tasks | [`sayun-operations-manifest.json`](operations/sayun-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sayun.toml`](sayun.toml) | Expanded simulator scenario |
| [`sayun.corridor.geojson`](sayun.corridor.geojson) | GIS corridor and stations |
| [`sayun.design-quality.yaml`](sayun.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sayun
```

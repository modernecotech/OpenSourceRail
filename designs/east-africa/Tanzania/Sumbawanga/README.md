# Sumbawanga — Urban Rail Network

**Country:** TZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sumbawanga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$217 M (88.0%) of external capital** and **$272 M of external interest**. Capital plus saved interest totals **$490 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Sumbawanga rail network on OpenStreetMap](sumbawanga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 10 / 1 |
| Route length | 15.7 km double track |
| Coverage / transfer reachability | 77.2% / 100% |
| Estimated station catchment | 193,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 40 × 2-car `tram-2car` trainsets (34 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  6.6 km | 4 | 16 | E Mid ↔ NW Outer |
| line-2 |  5.7 km | 3 | 13 | S Outer ↔ NE Mid |
| line-3 |  3.3 km | 3 | 11 | N Mid ↔ S Mid |
| **Total** | **15.7 km** | **10 unique** | **40** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 7,285 train-km/day |
| Annual traction demand | 23.0 GWh |
| Station/depot PV / storage | 7.7 MW / 44.5 MWh |
| Aggregate charging power | 5.0 MW |
| Dedicated solar plant | 2.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 3.4 km / 19 kWh |
| Lowest traversal charging margin | line-2: 30 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $42 M |
| Stations | $52 M |
| Depots | $8.0 M |
| Rolling stock | $22 M |
| Dedicated solar plant | $1.8 M |
| Residual train control | $783 k |
| Charging microgrids | $1.1 M |
| EPC / project services | $8.9 M |
| **Total city programme** | **$137 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $30 M (21.6%) |
| Domestic / local capital | $108 M (78.4%) |
| Annual public construction commitment | $13 M / yr for 7 years |
| Annual post-grace debt service | $10 M / yr |
| External capital saved vs default turnkey sensitivity | $217 M |
| Capital + lifetime external interest saved | $490 M |
| Annual OPEX | $3.5 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 99 assets / 428 tasks | [`sumbawanga-operations-manifest.json`](operations/sumbawanga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sumbawanga.toml`](sumbawanga.toml) | Expanded simulator scenario |
| [`sumbawanga.corridor.geojson`](sumbawanga.corridor.geojson) | GIS corridor and stations |
| [`sumbawanga.design-quality.yaml`](sumbawanga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh sumbawanga
```

# Samawah — Urban Rail Network

**Country:** IQ · **Population:** 373,770 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Samawah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$648 M (86.6%) of external capital** and **$796 M of external interest**. Capital plus saved interest totals **$1.44 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Samawah rail network on OpenStreetMap](samawah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 1 |
| Route length | 50.4 km double track |
| Coverage / transfer reachability | 58.9% / 100% |
| Estimated station catchment | 220,150 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 108 × 3-car `light-metro-3car` trainsets (97 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.6 km | 9 | 53 | N Mid ↔ SW Outer |
| line-2 | 12.8 km | 6 | 28 | SE Mid ↔ N Mid |
| line-3 | 12.0 km | 6 | 27 | E Mid ↔ W Inner |
| **Total** | **50.4 km** | **21 unique** | **108** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,447 train-km/day |
| Annual traction demand | 110.9 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 45.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 9.8 km / 79 kWh |
| Lowest traversal charging margin | line-2: 33 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $144 M |
| Stations | $100 M |
| Depots | $8.0 M |
| Rolling stock | $97 M |
| Dedicated solar plant | $37 M |
| Residual train control | $2.5 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $25 M |
| **Total city programme** | **$415 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $100 M (24.1%) |
| Domestic / local capital | $315 M (75.9%) |
| Annual public construction commitment | $39 M / yr for 5 years |
| Annual post-grace debt service | $28 M / yr |
| External capital saved vs default turnkey sensitivity | $648 M |
| Capital + lifetime external interest saved | $1.44 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 236 assets / 1,087 tasks | [`samawah-operations-manifest.json`](operations/samawah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`samawah.toml`](samawah.toml) | Expanded simulator scenario |
| [`samawah.corridor.geojson`](samawah.corridor.geojson) | GIS corridor and stations |
| [`samawah.design-quality.yaml`](samawah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh samawah
```

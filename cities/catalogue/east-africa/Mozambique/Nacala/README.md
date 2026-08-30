# Nacala — Urban Rail Network

**Country:** MZ · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nacala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$474 M (87.6%) of external capital** and **$612 M of external interest**. Capital plus saved interest totals **$1.09 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Nacala rail network on OpenStreetMap](nacala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 39.0 km double track |
| Coverage / transfer reachability | 80.0% / 100% |
| Estimated station catchment | 240,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 81 × 2-car `tram-2car` trainsets (72 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.5 km | 6 | 30 | S Mid ↔ NE Outer |
| line-2 | 12.1 km | 6 | 25 | SE Mid ↔ W Outer |
| line-3 | 12.4 km | 5 | 26 | NE Mid ↔ S Outer |
| **Total** | **39.0 km** | **17 unique** | **81** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 18,120 train-km/day |
| Annual traction demand | 57.1 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 26.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 4.7 km / 23 kWh |
| Lowest traversal charging margin | line-3: 42 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $115 M |
| Stations | $90 M |
| Depots | $8.0 M |
| Rolling stock | $45 M |
| Dedicated solar plant | $21 M |
| Residual train control | $1.9 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $18 M |
| **Total city programme** | **$301 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $67 M (22.3%) |
| Domestic / local capital | $234 M (77.7%) |
| Annual public construction commitment | $33 M / yr for 10 years |
| Annual post-grace debt service | $30 M / yr |
| External capital saved vs default turnkey sensitivity | $474 M |
| Capital + lifetime external interest saved | $1.09 bn |
| Annual OPEX | $7.1 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 183 assets / 828 tasks | [`nacala-operations-manifest.json`](operations/nacala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nacala.toml`](nacala.toml) | Expanded simulator scenario |
| [`nacala.corridor.geojson`](nacala.corridor.geojson) | GIS corridor and stations |
| [`nacala.design-quality.yaml`](nacala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh nacala
```

# Latakia — Urban Rail Network

**Country:** SY · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Latakia-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$536 M (86.3%) of external capital** and **$692 M of external interest**. Capital plus saved interest totals **$1.23 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Latakia rail network on OpenStreetMap](latakia-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 2 |
| Route length | 42.8 km double track |
| Coverage / transfer reachability | 57.2% / 100% |
| Estimated station catchment | 400,399 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 93 × 3-car `light-metro-3car` trainsets (83 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.2 km | 6 | 39 | SW Mid ↔ E Outer |
| line-2 | 11.5 km | 5 | 26 | NW Mid ↔ NE Mid |
| line-3 | 13.1 km | 6 | 28 | SW Mid ↔ NW Outer |
| **Total** | **42.8 km** | **17 unique** | **93** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,922 train-km/day |
| Annual traction demand | 94.2 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 42.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 5.4 km / 39 kWh |
| Lowest traversal charging margin | line-3: 43 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $112 M |
| Stations | $82 M |
| Depots | $8.0 M |
| Rolling stock | $84 M |
| Dedicated solar plant | $34 M |
| Residual train control | $2.1 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $20 M |
| **Total city programme** | **$345 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $85 M (24.6%) |
| Domestic / local capital | $260 M (75.4%) |
| Annual public construction commitment | $51 M / yr for 10 years |
| Annual post-grace debt service | $47 M / yr |
| External capital saved vs default turnkey sensitivity | $536 M |
| Capital + lifetime external interest saved | $1.23 bn |
| Annual OPEX | $8.4 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 195 assets / 912 tasks | [`latakia-operations-manifest.json`](operations/latakia-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`latakia.toml`](latakia.toml) | Expanded simulator scenario |
| [`latakia.corridor.geojson`](latakia.corridor.geojson) | GIS corridor and stations |
| [`latakia.design-quality.yaml`](latakia.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh latakia
```

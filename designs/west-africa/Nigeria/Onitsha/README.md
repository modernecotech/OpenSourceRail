# Onitsha — Urban Rail Network

**Country:** NG · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Onitsha-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.34 bn (86.8%) of external capital** and **$2.94 bn of external interest**. Capital plus saved interest totals **$5.28 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Onitsha rail network on OpenStreetMap](onitsha-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 63 / 8 |
| Route length | 188.6 km double track |
| Coverage / transfer reachability | 79.2% / 70% |
| Estimated station catchment | 1,188,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 198 × 4-car `metro-4car` trainsets (177 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.3 km | 8 | 34 | W Mid ↔ E Mid |
| line-2 | 32.4 km | 10 | 50 | NW Outer ↔ SE Outer |
| line-3 | 32.8 km | 10 | 51 | SW Outer ↔ NE Outer |
| line-4 | 16.9 km | 7 | 28 | SE Outer ↔ SW Inner |
| line-5 | 86.2 km | 28 | 35 | NW Outer ↔ W Outer |
| **Total** | **188.6 km** | **63 unique** | **198** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 67,665 train-km/day |
| Annual traction demand | 426.8 GWh |
| Station/depot PV / storage | 18.8 MW / 109.0 MWh |
| Aggregate charging power | 70.5 MW |
| Dedicated solar plant | 258.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 28.0 km / 280 kWh |
| Lowest traversal charging margin | line-4: 158 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $639 M |
| Stations | $315 M |
| Depots | $8.0 M |
| Rolling stock | $222 M |
| Dedicated solar plant | $207 M |
| Residual train control | $9.4 M |
| Charging microgrids | $16 M |
| EPC / project services | $85 M |
| **Total city programme** | **$1.50 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $355 M (23.7%) |
| Domestic / local capital | $1.14 bn (76.3%) |
| Annual public construction commitment | $172 M / yr for 7 years |
| Annual post-grace debt service | $146 M / yr |
| External capital saved vs default turnkey sensitivity | $2.34 bn |
| Capital + lifetime external interest saved | $5.28 bn |
| Annual OPEX | $34 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 536 assets / 2,305 tasks | [`onitsha-operations-manifest.json`](operations/onitsha-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`onitsha.toml`](onitsha.toml) | Expanded simulator scenario |
| [`onitsha.corridor.geojson`](onitsha.corridor.geojson) | GIS corridor and stations |
| [`onitsha.design-quality.yaml`](onitsha.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh onitsha
```

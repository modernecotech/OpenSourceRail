# Baqubah — Urban Rail Network

**Country:** IQ · **Population:** 470,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Baqubah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$746 M (86.5%) of external capital** and **$917 M of external interest**. Capital plus saved interest totals **$1.66 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Baqubah rail network on OpenStreetMap](baqubah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 1 |
| Route length | 60.9 km double track |
| Coverage / transfer reachability | 59.9% / 100% |
| Estimated station catchment | 281,530 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 130 × 3-car `light-metro-3car` trainsets (116 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.6 km | 5 | 34 | S Mid ↔ NW Mid |
| line-2 | 21.9 km | 7 | 46 | SW Mid ↔ NE Outer |
| line-3 | 23.4 km | 10 | 50 | N Outer ↔ SW Outer |
| **Total** | **60.9 km** | **22 unique** | **130** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 28,306 train-km/day |
| Annual traction demand | 133.9 GWh |
| Station/depot PV / storage | 10.4 MW / 49.0 MWh |
| Aggregate charging power | 9.5 MW |
| Dedicated solar plant | 58.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 9.9 km / 80 kWh |
| Lowest traversal charging margin | line-1: 46 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $180 M |
| Stations | $94 M |
| Depots | $8.0 M |
| Rolling stock | $117 M |
| Dedicated solar plant | $47 M |
| Residual train control | $3.0 M |
| Charging microgrids | $2.1 M |
| EPC / project services | $28 M |
| **Total city programme** | **$479 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $116 M (24.3%) |
| Domestic / local capital | $363 M (75.7%) |
| Annual public construction commitment | $44 M / yr for 5 years |
| Annual post-grace debt service | $33 M / yr |
| External capital saved vs default turnkey sensitivity | $746 M |
| Capital + lifetime external interest saved | $1.66 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 261 assets / 1,244 tasks | [`baqubah-operations-manifest.json`](operations/baqubah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`baqubah.toml`](baqubah.toml) | Expanded simulator scenario |
| [`baqubah.corridor.geojson`](baqubah.corridor.geojson) | GIS corridor and stations |
| [`baqubah.design-quality.yaml`](baqubah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh baqubah
```

# Amarah — Urban Rail Network

**Country:** IQ · **Population:** 660,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Amarah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$680 M (87.2%) of external capital** and **$836 M of external interest**. Capital plus saved interest totals **$1.52 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Amarah rail network on OpenStreetMap](amarah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 1 |
| Route length | 46.6 km double track |
| Coverage / transfer reachability | 57.5% / 100% |
| Estimated station catchment | 379,499 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 101 × 3-car `light-metro-3car` trainsets (90 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.6 km | 8 | 47 | NW Mid ↔ SE Outer |
| line-2 | 13.0 km | 6 | 28 | SW Mid ↔ N Mid |
| line-3 | 12.0 km | 4 | 26 | SE Inner ↔ W Mid |
| **Total** | **46.6 km** | **18 unique** | **101** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 21,668 train-km/day |
| Annual traction demand | 102.5 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 42.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 9.5 km / 77 kWh |
| Lowest traversal charging margin | line-2: 32 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $190 M |
| Stations | $80 M |
| Depots | $8.0 M |
| Rolling stock | $91 M |
| Dedicated solar plant | $34 M |
| Residual train control | $2.3 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $26 M |
| **Total city programme** | **$433 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $99 M (23.0%) |
| Domestic / local capital | $334 M (77.0%) |
| Annual public construction commitment | $41 M / yr for 5 years |
| Annual post-grace debt service | $30 M / yr |
| External capital saved vs default turnkey sensitivity | $680 M |
| Capital + lifetime external interest saved | $1.52 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 209 assets / 982 tasks | [`amarah-operations-manifest.json`](operations/amarah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`amarah.toml`](amarah.toml) | Expanded simulator scenario |
| [`amarah.corridor.geojson`](amarah.corridor.geojson) | GIS corridor and stations |
| [`amarah.design-quality.yaml`](amarah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh amarah
```

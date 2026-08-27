# Aba-Ng — Urban Rail Network

**Country:** NG · **Population:** 900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Aba-Ng-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$440 M (86.5%) of external capital** and **$552 M of external interest**. Capital plus saved interest totals **$992 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Aba-Ng rail network on OpenStreetMap](aba-ng-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 13 / 1 |
| Route length | 31.9 km double track |
| Coverage / transfer reachability | 68.4% / 33% |
| Estimated station catchment | 615,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 70 × 3-car `light-metro-3car` trainsets (62 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.4 km | 5 | 27 | E Outer ↔ W Outer |
| line-2 |  8.1 km | 4 | 18 | W Mid ↔ E Inner |
| line-3 | 11.5 km | 4 | 25 | SW Outer ↔ NE Mid |
| **Total** | **31.9 km** | **13 unique** | **70** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 14,853 train-km/day |
| Annual traction demand | 70.3 GWh |
| Station/depot PV / storage | 8.6 MW / 46.0 MWh |
| Aggregate charging power | 6.5 MW |
| Dedicated solar plant | 36.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 6.3 km / 47 kWh |
| Lowest traversal charging margin | line-2: 32 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $97 M |
| Stations | $66 M |
| Depots | $8.0 M |
| Rolling stock | $63 M |
| Dedicated solar plant | $29 M |
| Residual train control | $1.6 M |
| Charging microgrids | $1.5 M |
| EPC / project services | $17 M |
| **Total city programme** | **$283 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $69 M (24.3%) |
| Domestic / local capital | $214 M (75.7%) |
| Annual public construction commitment | $32 M / yr for 7 years |
| Annual post-grace debt service | $28 M / yr |
| External capital saved vs default turnkey sensitivity | $440 M |
| Capital + lifetime external interest saved | $992 M |
| Annual OPEX | $7.2 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 150 assets / 689 tasks | [`aba-ng-operations-manifest.json`](operations/aba-ng-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`aba-ng.toml`](aba-ng.toml) | Expanded simulator scenario |
| [`aba-ng.corridor.geojson`](aba-ng.corridor.geojson) | GIS corridor and stations |
| [`aba-ng.design-quality.yaml`](aba-ng.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh aba-ng
```

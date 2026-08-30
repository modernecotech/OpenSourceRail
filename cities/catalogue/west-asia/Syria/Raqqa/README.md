# Raqqa — Urban Rail Network

**Country:** SY · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Raqqa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$621 M (86.6%) of external capital** and **$802 M of external interest**. Capital plus saved interest totals **$1.42 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Raqqa rail network on OpenStreetMap](raqqa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 1 |
| Route length | 48.7 km double track |
| Coverage / transfer reachability | 86.1% / 100% |
| Estimated station catchment | 301,350 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 105 × 3-car `light-metro-3car` trainsets (94 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 16.0 km | 6 | 35 | W Outer ↔ E Inner |
| line-2 | 14.4 km | 5 | 30 | SW Mid ↔ NE Outer |
| line-3 | 18.3 km | 7 | 40 | E Outer ↔ W Mid |
| **Total** | **48.7 km** | **18 unique** | **105** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 22,663 train-km/day |
| Annual traction demand | 107.2 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 45.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 57 kWh |
| Lowest traversal charging margin | line-2: 35 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $147 M |
| Stations | $84 M |
| Depots | $8.0 M |
| Rolling stock | $94 M |
| Dedicated solar plant | $36 M |
| Residual train control | $2.4 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $24 M |
| **Total city programme** | **$398 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $96 M (24.1%) |
| Domestic / local capital | $302 M (75.9%) |
| Annual public construction commitment | $59 M / yr for 10 years |
| Annual post-grace debt service | $54 M / yr |
| External capital saved vs default turnkey sensitivity | $621 M |
| Capital + lifetime external interest saved | $1.42 bn |
| Annual OPEX | $9.6 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 214 assets / 1,011 tasks | [`raqqa-operations-manifest.json`](operations/raqqa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`raqqa.toml`](raqqa.toml) | Expanded simulator scenario |
| [`raqqa.corridor.geojson`](raqqa.corridor.geojson) | GIS corridor and stations |
| [`raqqa.design-quality.yaml`](raqqa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh raqqa
```

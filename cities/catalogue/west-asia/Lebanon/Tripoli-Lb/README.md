# Tripoli-Lb — Urban Rail Network

**Country:** LB · **Population:** 730,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tripoli-Lb-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$604 M (86.6%) of external capital** and **$765 M of external interest**. Capital plus saved interest totals **$1.37 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tripoli-Lb rail network on OpenStreetMap](tripoli-lb-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 20 / 1 |
| Route length | 45.6 km double track |
| Coverage / transfer reachability | 57.5% / 100% |
| Estimated station catchment | 419,749 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 99 × 3-car `light-metro-3car` trainsets (89 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.6 km | 6 | 27 | NW Mid ↔ SE Mid |
| line-2 | 18.8 km | 8 | 41 | NE Outer ↔ SW Mid |
| line-3 | 14.2 km | 6 | 31 | W Mid ↔ SE Outer |
| **Total** | **45.6 km** | **20 unique** | **99** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 21,210 train-km/day |
| Annual traction demand | 100.3 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 45.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 5.9 km / 42 kWh |
| Lowest traversal charging margin | line-1: 47 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $132 M |
| Stations | $95 M |
| Depots | $8.0 M |
| Rolling stock | $89 M |
| Dedicated solar plant | $36 M |
| Residual train control | $2.3 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $23 M |
| **Total city programme** | **$388 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $94 M (24.2%) |
| Domestic / local capital | $294 M (75.8%) |
| Annual public construction commitment | $70 M / yr for 8 years |
| Annual post-grace debt service | $64 M / yr |
| External capital saved vs default turnkey sensitivity | $604 M |
| Capital + lifetime external interest saved | $1.37 bn |
| Annual OPEX | $10 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 218 assets / 1,001 tasks | [`tripoli-lb-operations-manifest.json`](operations/tripoli-lb-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tripoli-lb.toml`](tripoli-lb.toml) | Expanded simulator scenario |
| [`tripoli-lb.corridor.geojson`](tripoli-lb.corridor.geojson) | GIS corridor and stations |
| [`tripoli-lb.design-quality.yaml`](tripoli-lb.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tripoli-lb
```

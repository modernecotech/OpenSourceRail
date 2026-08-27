# Bloemfontein — Urban Rail Network

**Country:** ZA · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bloemfontein-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$955 M (86.1%) of external capital** and **$1.17 bn of external interest**. Capital plus saved interest totals **$2.13 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Bloemfontein rail network on OpenStreetMap](bloemfontein-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 26 / 2 |
| Route length | 72.1 km double track |
| Coverage / transfer reachability | 34.7% / 100% |
| Estimated station catchment | 208,199 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 151 × 3-car `light-metro-3car` trainsets (136 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.3 km | 10 | 58 | SE Outer ↔ N Mid |
| line-2 | 25.9 km | 9 | 53 | NW Outer ↔ S Mid |
| line-3 | 18.9 km | 7 | 40 | NE Mid ↔ SW Mid |
| **Total** | **72.1 km** | **26 unique** | **151** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 33,526 train-km/day |
| Annual traction demand | 158.6 GWh |
| Station/depot PV / storage | 12.5 MW / 52.5 MWh |
| Aggregate charging power | 13.0 MW |
| Dedicated solar plant | 104.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.8 km / 49 kWh |
| Lowest traversal charging margin | line-3: 79 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $212 M |
| Stations | $135 M |
| Depots | $8.0 M |
| Rolling stock | $136 M |
| Dedicated solar plant | $84 M |
| Residual train control | $3.6 M |
| Charging microgrids | $2.9 M |
| EPC / project services | $35 M |
| **Total city programme** | **$616 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $154 M (25.0%) |
| Domestic / local capital | $462 M (75.0%) |
| Annual public construction commitment | $64 M / yr for 5 years |
| Annual post-grace debt service | $49 M / yr |
| External capital saved vs default turnkey sensitivity | $955 M |
| Capital + lifetime external interest saved | $2.13 bn |
| Annual OPEX | $17 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 309 assets / 1,464 tasks | [`bloemfontein-operations-manifest.json`](operations/bloemfontein-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bloemfontein.toml`](bloemfontein.toml) | Expanded simulator scenario |
| [`bloemfontein.corridor.geojson`](bloemfontein.corridor.geojson) | GIS corridor and stations |
| [`bloemfontein.design-quality.yaml`](bloemfontein.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh bloemfontein
```

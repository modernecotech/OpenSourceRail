# Al-Kharj — Urban Rail Network

**Country:** SA · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Al-Kharj-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$816 M (86.4%) of external capital** and **$1.00 bn of external interest**. Capital plus saved interest totals **$1.82 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Al-Kharj rail network on OpenStreetMap](al-kharj-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 27 / 1 |
| Route length | 67.7 km double track |
| Coverage / transfer reachability | 70.3% / 100% |
| Estimated station catchment | 281,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 143 × 3-car `light-metro-3car` trainsets (128 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.3 km | 9 | 48 | E Outer ↔ W Outer |
| line-2 | 23.1 km | 10 | 49 | NE Outer ↔ S Mid |
| line-3 | 21.4 km | 8 | 46 | W Outer ↔ E Outer |
| **Total** | **67.7 km** | **27 unique** | **143** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 31,497 train-km/day |
| Annual traction demand | 149.0 GWh |
| Station/depot PV / storage | 12.5 MW / 52.5 MWh |
| Aggregate charging power | 13.0 MW |
| Dedicated solar plant | 63.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 56 kWh |
| Lowest traversal charging margin | line-2: 52 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $189 M |
| Stations | $111 M |
| Depots | $8.0 M |
| Rolling stock | $129 M |
| Dedicated solar plant | $51 M |
| Residual train control | $3.4 M |
| Charging microgrids | $2.8 M |
| EPC / project services | $31 M |
| **Total city programme** | **$525 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $128 M (24.4%) |
| Domestic / local capital | $397 M (75.6%) |
| Annual public construction commitment | $36 M / yr for 5 years |
| Annual post-grace debt service | $26 M / yr |
| External capital saved vs default turnkey sensitivity | $816 M |
| Capital + lifetime external interest saved | $1.82 bn |
| Annual OPEX | $23 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 303 assets / 1,418 tasks | [`al-kharj-operations-manifest.json`](operations/al-kharj-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`al-kharj.toml`](al-kharj.toml) | Expanded simulator scenario |
| [`al-kharj.corridor.geojson`](al-kharj.corridor.geojson) | GIS corridor and stations |
| [`al-kharj.design-quality.yaml`](al-kharj.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh al-kharj
```

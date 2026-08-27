# Diwaniyah — Urban Rail Network

**Country:** IQ · **Population:** 440,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Diwaniyah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$681 M (87.0%) of external capital** and **$837 M of external interest**. Capital plus saved interest totals **$1.52 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Diwaniyah rail network on OpenStreetMap](diwaniyah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 1 |
| Route length | 49.8 km double track |
| Coverage / transfer reachability | 50.5% / 33% |
| Estimated station catchment | 222,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 106 × 3-car `light-metro-3car` trainsets (95 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.7 km | 9 | 43 | E Outer ↔ W Mid |
| line-2 | 12.7 km | 5 | 27 | N Mid ↔ SW Inner |
| line-3 | 16.4 km | 5 | 36 | SE Inner ↔ SW Outer |
| **Total** | **49.8 km** | **19 unique** | **106** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,180 train-km/day |
| Annual traction demand | 109.6 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 46.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 8.5 km / 68 kWh |
| Lowest traversal charging margin | line-2: 30 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $184 M |
| Stations | $79 M |
| Depots | $8.0 M |
| Rolling stock | $95 M |
| Dedicated solar plant | $37 M |
| Residual train control | $2.5 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $26 M |
| **Total city programme** | **$435 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $101 M (23.4%) |
| Domestic / local capital | $333 M (76.6%) |
| Annual public construction commitment | $41 M / yr for 5 years |
| Annual post-grace debt service | $30 M / yr |
| External capital saved vs default turnkey sensitivity | $681 M |
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
| Operations, QA and maintenance | 219 assets / 1,030 tasks | [`diwaniyah-operations-manifest.json`](operations/diwaniyah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`diwaniyah.toml`](diwaniyah.toml) | Expanded simulator scenario |
| [`diwaniyah.corridor.geojson`](diwaniyah.corridor.geojson) | GIS corridor and stations |
| [`diwaniyah.design-quality.yaml`](diwaniyah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh diwaniyah
```

# Multan — Urban Rail Network

**Country:** PK · **Population:** 2,197,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Multan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.85 bn (87.6%) of external capital** and **$2.32 bn of external interest**. Capital plus saved interest totals **$4.17 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Multan rail network on OpenStreetMap](multan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 48 / 12 |
| Route length | 118.6 km double track |
| Coverage / transfer reachability | 69.2% / 40% |
| Estimated station catchment | 1,520,324 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 149 × 4-car `metro-4car` trainsets (133 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.2 km | 9 | 35 | NE Outer ↔ SW Outer |
| line-2 | 20.0 km | 9 | 36 | NE Outer ↔ SW Outer |
| line-3 | 18.8 km | 7 | 30 | S Mid ↔ N Outer |
| line-4 | 19.7 km | 7 | 31 | W Mid ↔ E Outer |
| line-5 | 41.9 km | 16 | 17 | NE Outer ↔ N Outer |
| **Total** | **118.6 km** | **48 unique** | **149** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 45,378 train-km/day |
| Annual traction demand | 286.2 GWh |
| Station/depot PV / storage | 18.8 MW / 109.0 MWh |
| Aggregate charging power | 70.5 MW |
| Dedicated solar plant | 117.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 7.9 km / 88 kWh |
| Lowest traversal charging margin | line-4: 151 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $456 M |
| Stations | $358 M |
| Depots | $8.0 M |
| Rolling stock | $167 M |
| Dedicated solar plant | $94 M |
| Residual train control | $5.9 M |
| Charging microgrids | $16 M |
| EPC / project services | $71 M |
| **Total city programme** | **$1.17 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $263 M (22.3%) |
| Domestic / local capital | $912 M (77.7%) |
| Annual public construction commitment | $158 M / yr for 7 years |
| Annual post-grace debt service | $137 M / yr |
| External capital saved vs default turnkey sensitivity | $1.85 bn |
| Capital + lifetime external interest saved | $4.17 bn |
| Annual OPEX | $27 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 424 assets / 1,779 tasks | [`multan-operations-manifest.json`](operations/multan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`multan.toml`](multan.toml) | Expanded simulator scenario |
| [`multan.corridor.geojson`](multan.corridor.geojson) | GIS corridor and stations |
| [`multan.design-quality.yaml`](multan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh multan
```

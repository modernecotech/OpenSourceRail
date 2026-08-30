# Kenitra — Urban Rail Network

**Country:** MA · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kenitra-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$716 M (86.2%) of external capital** and **$881 M of external interest**. Capital plus saved interest totals **$1.60 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kenitra rail network on OpenStreetMap](kenitra-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 24 / 1 |
| Route length | 60.1 km double track |
| Coverage / transfer reachability | 66.2% / 100% |
| Estimated station catchment | 331,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 130 × 3-car `light-metro-3car` trainsets (116 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.7 km | 9 | 39 | E Mid ↔ W Mid |
| line-2 | 21.2 km | 8 | 46 | SE Mid ↔ W Outer |
| line-3 | 21.2 km | 7 | 45 | SW Mid ↔ NE Outer |
| **Total** | **60.1 km** | **24 unique** | **130** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 27,930 train-km/day |
| Annual traction demand | 132.1 GWh |
| Station/depot PV / storage | 11.6 MW / 51.0 MWh |
| Aggregate charging power | 11.5 MW |
| Dedicated solar plant | 62.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 11.4 km / 82 kWh |
| Lowest traversal charging margin | line-3: 77 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $157 M |
| Stations | $97 M |
| Depots | $8.0 M |
| Rolling stock | $117 M |
| Dedicated solar plant | $50 M |
| Residual train control | $3.0 M |
| Charging microgrids | $2.5 M |
| EPC / project services | $27 M |
| **Total city programme** | **$462 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $115 M (24.9%) |
| Domestic / local capital | $347 M (75.1%) |
| Annual public construction commitment | $32 M / yr for 5 years |
| Annual post-grace debt service | $22 M / yr |
| External capital saved vs default turnkey sensitivity | $716 M |
| Capital + lifetime external interest saved | $1.60 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 272 assets / 1,279 tasks | [`kenitra-operations-manifest.json`](operations/kenitra-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kenitra.toml`](kenitra.toml) | Expanded simulator scenario |
| [`kenitra.corridor.geojson`](kenitra.corridor.geojson) | GIS corridor and stations |
| [`kenitra.design-quality.yaml`](kenitra.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kenitra
```

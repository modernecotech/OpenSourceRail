# Bandung — Urban Rail Network

**Country:** ID · **Population:** 2,615,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bandung-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.53 bn (86.8%) of external capital** and **$4.34 bn of external interest**. Capital plus saved interest totals **$7.87 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Bandung rail network on OpenStreetMap](bandung-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 89 / 14 |
| Route length | 245.6 km double track |
| Coverage / transfer reachability | 60.1% / 87% |
| Estimated station catchment | 1,571,615 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 312 × 4-car `metro-4car` trainsets (281 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 39.6 km | 16 | 63 | E Mid ↔ W Outer |
| line-2 | 44.5 km | 15 | 71 | SE Outer ↔ NW Outer |
| line-3 | 24.0 km | 10 | 41 | SW Mid ↔ NE Inner |
| line-4 | 34.2 km | 14 | 57 | S Mid ↔ N Outer |
| line-5 | 31.5 km | 12 | 51 | SE Mid ↔ N Mid |
| line-6 | 71.8 km | 22 | 29 | W Mid ↔ W Mid |
| **Total** | **245.6 km** | **89 unique** | **312** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 97,518 train-km/day |
| Annual traction demand | 615.1 GWh |
| Station/depot PV / storage | 28.1 MW / 155.5 MWh |
| Aggregate charging power | 117.0 MW |
| Dedicated solar plant | 371.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 14.3 km / 143 kWh |
| Lowest traversal charging margin | line-3: 276 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $903 M |
| Stations | $534 M |
| Depots | $8.0 M |
| Rolling stock | $349 M |
| Dedicated solar plant | $297 M |
| Residual train control | $12 M |
| Charging microgrids | $26 M |
| EPC / project services | $128 M |
| **Total city programme** | **$2.26 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $536 M (23.7%) |
| Domestic / local capital | $1.72 bn (76.3%) |
| Annual public construction commitment | $185 M / yr for 5 years |
| Annual post-grace debt service | $134 M / yr |
| External capital saved vs default turnkey sensitivity | $3.53 bn |
| Capital + lifetime external interest saved | $7.87 bn |
| Annual OPEX | $54 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 808 assets / 3,528 tasks | [`bandung-operations-manifest.json`](operations/bandung-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bandung.toml`](bandung.toml) | Expanded simulator scenario |
| [`bandung.corridor.geojson`](bandung.corridor.geojson) | GIS corridor and stations |
| [`bandung.design-quality.yaml`](bandung.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh bandung
```

# Ismailia — Urban Rail Network

**Country:** EG · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Ismailia-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$658 M (86.5%) of external capital** and **$808 M of external interest**. Capital plus saved interest totals **$1.47 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Ismailia rail network on OpenStreetMap](ismailia-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 1 |
| Route length | 47.7 km double track |
| Coverage / transfer reachability | 63.0% / 100% |
| Estimated station catchment | 441,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 119 × 3-car `light-metro-3car` trainsets (106 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.5 km | 7 | 37 | E Mid ↔ NW Mid |
| line-2 | 22.5 km | 11 | 58 | NE Outer ↔ SW Mid |
| line-3 |  9.6 km | 4 | 24 | S Mid ↔ NW Inner |
| **Total** | **47.7 km** | **22 unique** | **119** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 22,180 train-km/day |
| Annual traction demand | 104.9 GWh |
| Station/depot PV / storage | 11.0 MW / 50.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 42.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 57 kWh |
| Lowest traversal charging margin | line-3: 29 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $137 M |
| Stations | $106 M |
| Depots | $8.0 M |
| Rolling stock | $107 M |
| Dedicated solar plant | $34 M |
| Residual train control | $2.4 M |
| Charging microgrids | $2.3 M |
| EPC / project services | $25 M |
| **Total city programme** | **$422 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $102 M (24.3%) |
| Domestic / local capital | $320 M (75.7%) |
| Annual public construction commitment | $44 M / yr for 5 years |
| Annual post-grace debt service | $34 M / yr |
| External capital saved vs default turnkey sensitivity | $658 M |
| Capital + lifetime external interest saved | $1.47 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 250 assets / 1,171 tasks | [`ismailia-operations-manifest.json`](operations/ismailia-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`ismailia.toml`](ismailia.toml) | Expanded simulator scenario |
| [`ismailia.corridor.geojson`](ismailia.corridor.geojson) | GIS corridor and stations |
| [`ismailia.design-quality.yaml`](ismailia.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh ismailia
```

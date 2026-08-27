# Basra — Urban Rail Network

**Country:** IQ · **Population:** 3,955,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Basra-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.81 bn (85.8%) of external capital** and **$5.92 bn of external interest**. Capital plus saved interest totals **$10.73 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Basra rail network on OpenStreetMap](basra-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 92 / 12 |
| Route length | 305.4 km double track |
| Coverage / transfer reachability | 82.3% / 38% |
| Estimated station catchment | 3,254,965 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 450 × 6-car `metro-6car` trainsets (407 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 45.2 km | 13 | 83 | S Inner ↔ N Outer |
| line-2 | 20.2 km | 8 | 39 | SE Inner ↔ N Mid |
| line-3 | 46.1 km | 13 | 87 | E Outer ↔ NW Mid |
| line-4 | 37.3 km | 12 | 72 | NW Mid ↔ E Outer |
| line-5 | 39.9 km | 13 | 76 | SW Outer ↔ NE Inner |
| line-6 | 29.8 km | 9 | 54 | NW Inner ↔ SW Mid |
| line-7 | 86.9 km | 24 | 39 | N Mid ↔ N Mid |
| **Total** | **305.4 km** | **92 unique** | **450** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,022 one-way journeys / 121,804 train-km/day |
| Annual traction demand | 1,152.4 GWh |
| Station/depot PV / storage | 28.1 MW / 194.0 MWh |
| Aggregate charging power | 156.0 MW |
| Dedicated solar plant | 572.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 15.2 km / 244 kWh |
| Lowest traversal charging margin | line-2: 229 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.21 bn |
| Stations | $458 M |
| Depots | $8.0 M |
| Rolling stock | $756 M |
| Dedicated solar plant | $458 M |
| Residual train control | $15 M |
| Charging microgrids | $34 M |
| EPC / project services | $174 M |
| **Total city programme** | **$3.11 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $793 M (25.5%) |
| Domestic / local capital | $2.32 bn (74.5%) |
| Annual public construction commitment | $286 M / yr for 5 years |
| Annual post-grace debt service | $213 M / yr |
| External capital saved vs default turnkey sensitivity | $4.81 bn |
| Capital + lifetime external interest saved | $10.73 bn |
| Annual OPEX | $80 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 977 assets / 4,546 tasks | [`basra-operations-manifest.json`](operations/basra-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`basra.toml`](basra.toml) | Expanded simulator scenario |
| [`basra.corridor.geojson`](basra.corridor.geojson) | GIS corridor and stations |
| [`basra.design-quality.yaml`](basra.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh basra
```

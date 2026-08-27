# Sialkot — Urban Rail Network

**Country:** PK · **Population:** 750,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sialkot-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.11 bn (88.1%) of external capital** and **$1.39 bn of external interest**. Capital plus saved interest totals **$2.50 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Sialkot rail network on OpenStreetMap](sialkot-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 2 |
| Route length | 55.4 km double track |
| Coverage / transfer reachability | 45.6% / 100% |
| Estimated station catchment | 342,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 134 × 3-car `light-metro-3car` trainsets (120 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.7 km | 7 | 46 | N Mid ↔ SW Outer |
| line-2 | 22.6 km | 8 | 53 | SE Outer ↔ NW Outer |
| line-3 | 14.1 km | 6 | 35 | NE Mid ↔ W Outer |
| **Total** | **55.4 km** | **21 unique** | **134** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 25,762 train-km/day |
| Annual traction demand | 121.9 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 51.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 57 kWh |
| Lowest traversal charging margin | line-3: 46 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $372 M |
| Stations | $111 M |
| Depots | $8.0 M |
| Rolling stock | $121 M |
| Dedicated solar plant | $41 M |
| Residual train control | $2.8 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $43 M |
| **Total city programme** | **$700 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $149 M (21.3%) |
| Domestic / local capital | $551 M (78.7%) |
| Annual public construction commitment | $95 M / yr for 7 years |
| Annual post-grace debt service | $82 M / yr |
| External capital saved vs default turnkey sensitivity | $1.11 bn |
| Capital + lifetime external interest saved | $2.50 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 263 assets / 1,264 tasks | [`sialkot-operations-manifest.json`](operations/sialkot-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sialkot.toml`](sialkot.toml) | Expanded simulator scenario |
| [`sialkot.corridor.geojson`](sialkot.corridor.geojson) | GIS corridor and stations |
| [`sialkot.design-quality.yaml`](sialkot.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh sialkot
```

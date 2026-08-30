# Sylhet — Urban Rail Network

**Country:** BD · **Population:** 900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sylhet-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$634 M (86.2%) of external capital** and **$795 M of external interest**. Capital plus saved interest totals **$1.43 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Sylhet rail network on OpenStreetMap](sylhet-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 1 |
| Route length | 49.6 km double track |
| Coverage / transfer reachability | 75.4% / 100% |
| Estimated station catchment | 678,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 109 × 3-car `light-metro-3car` trainsets (98 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.2 km | 7 | 31 | E Mid ↔ NW Mid |
| line-2 | 24.1 km | 9 | 52 | SW Outer ↔ N Mid |
| line-3 | 11.3 km | 5 | 26 | SE Mid ↔ NW Mid |
| **Total** | **49.6 km** | **21 unique** | **109** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,087 train-km/day |
| Annual traction demand | 109.2 GWh |
| Station/depot PV / storage | 10.4 MW / 49.0 MWh |
| Aggregate charging power | 9.5 MW |
| Dedicated solar plant | 59.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 11.4 km / 86 kWh |
| Lowest traversal charging margin | line-3: 50 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $147 M |
| Stations | $80 M |
| Depots | $8.0 M |
| Rolling stock | $98 M |
| Dedicated solar plant | $48 M |
| Residual train control | $2.5 M |
| Charging microgrids | $2.0 M |
| EPC / project services | $24 M |
| **Total city programme** | **$409 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $101 M (24.8%) |
| Domestic / local capital | $307 M (75.2%) |
| Annual public construction commitment | $34 M / yr for 7 years |
| Annual post-grace debt service | $28 M / yr |
| External capital saved vs default turnkey sensitivity | $634 M |
| Capital + lifetime external interest saved | $1.43 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 232 assets / 1,081 tasks | [`sylhet-operations-manifest.json`](operations/sylhet-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sylhet.toml`](sylhet.toml) | Expanded simulator scenario |
| [`sylhet.corridor.geojson`](sylhet.corridor.geojson) | GIS corridor and stations |
| [`sylhet.design-quality.yaml`](sylhet.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sylhet
```

# Hodeidah — Urban Rail Network

**Country:** YE · **Population:** 750,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hodeidah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$456 M (86.9%) of external capital** and **$589 M of external interest**. Capital plus saved interest totals **$1.04 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Hodeidah rail network on OpenStreetMap](hodeidah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 1 |
| Route length | 30.7 km double track |
| Coverage / transfer reachability | 65.7% / 100% |
| Estimated station catchment | 492,750 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 71 × 3-car `light-metro-3car` trainsets (63 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.7 km | 5 | 23 | NE Mid ↔ S Outer |
| line-2 | 11.6 km | 6 | 27 | SE Mid ↔ NW Outer |
| line-3 |  9.4 km | 4 | 21 | E Outer ↔ NW Mid |
| **Total** | **30.7 km** | **15 unique** | **71** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 14,262 train-km/day |
| Annual traction demand | 67.5 GWh |
| Station/depot PV / storage | 9.2 MW / 47.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 24.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 3.6 km / 29 kWh |
| Lowest traversal charging margin | line-3: 31 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $92 M |
| Stations | $86 M |
| Depots | $8.0 M |
| Rolling stock | $64 M |
| Dedicated solar plant | $20 M |
| Residual train control | $1.5 M |
| Charging microgrids | $1.7 M |
| EPC / project services | $18 M |
| **Total city programme** | **$291 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $69 M (23.5%) |
| Domestic / local capital | $223 M (76.5%) |
| Annual public construction commitment | $40 M / yr for 10 years |
| Annual post-grace debt service | $37 M / yr |
| External capital saved vs default turnkey sensitivity | $456 M |
| Capital + lifetime external interest saved | $1.04 bn |
| Annual OPEX | $7.0 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 161 assets / 726 tasks | [`hodeidah-operations-manifest.json`](operations/hodeidah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hodeidah.toml`](hodeidah.toml) | Expanded simulator scenario |
| [`hodeidah.corridor.geojson`](hodeidah.corridor.geojson) | GIS corridor and stations |
| [`hodeidah.design-quality.yaml`](hodeidah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hodeidah
```

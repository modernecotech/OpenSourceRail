# Bertoua — Urban Rail Network

**Country:** CM · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bertoua-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$421 M (86.6%) of external capital** and **$528 M of external interest**. Capital plus saved interest totals **$950 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Bertoua rail network on OpenStreetMap](bertoua-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 12 / 1 |
| Route length | 29.4 km double track |
| Coverage / transfer reachability | 78.2% / 100% |
| Estimated station catchment | 273,700 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 63 × 3-car `light-metro-3car` trainsets (57 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.4 km | 4 | 21 | W Mid ↔ SE Mid |
| line-2 | 10.3 km | 4 | 21 | NW Mid ↔ NE Outer |
| line-3 |  9.6 km | 4 | 21 | S Outer ↔ NW Mid |
| **Total** | **29.4 km** | **12 unique** | **63** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 13,649 train-km/day |
| Annual traction demand | 64.6 GWh |
| Station/depot PV / storage | 8.3 MW / 45.5 MWh |
| Aggregate charging power | 6.0 MW |
| Dedicated solar plant | 32.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 5.7 km / 43 kWh |
| Lowest traversal charging margin | line-2: 33 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $89 M |
| Stations | $71 M |
| Depots | $8.0 M |
| Rolling stock | $57 M |
| Dedicated solar plant | $26 M |
| Residual train control | $1.5 M |
| Charging microgrids | $1.4 M |
| EPC / project services | $16 M |
| **Total city programme** | **$270 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $65 M (24.0%) |
| Domestic / local capital | $205 M (76.0%) |
| Annual public construction commitment | $23 M / yr for 7 years |
| Annual post-grace debt service | $19 M / yr |
| External capital saved vs default turnkey sensitivity | $421 M |
| Capital + lifetime external interest saved | $950 M |
| Annual OPEX | $6.8 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 137 assets / 624 tasks | [`bertoua-operations-manifest.json`](operations/bertoua-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bertoua.toml`](bertoua.toml) | Expanded simulator scenario |
| [`bertoua.corridor.geojson`](bertoua.corridor.geojson) | GIS corridor and stations |
| [`bertoua.design-quality.yaml`](bertoua.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bertoua
```

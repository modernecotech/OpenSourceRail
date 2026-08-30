# Tete — Urban Rail Network

**Country:** MZ · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tete-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$596 M (87.8%) of external capital** and **$769 M of external interest**. Capital plus saved interest totals **$1.37 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tete rail network on OpenStreetMap](tete-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 13 / 1 |
| Route length | 37.9 km double track |
| Coverage / transfer reachability | 76.9% / 33% |
| Estimated station catchment | 269,150 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 81 × 3-car `light-metro-3car` trainsets (72 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.5 km | 5 | 30 | NW Outer ↔ S Outer |
| line-2 | 12.6 km | 4 | 27 | SE Outer ↔ NW Mid |
| line-3 | 10.8 km | 4 | 24 | SW Inner ↔ NE Outer |
| **Total** | **37.9 km** | **13 unique** | **81** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 17,608 train-km/day |
| Annual traction demand | 83.3 GWh |
| Station/depot PV / storage | 8.3 MW / 45.5 MWh |
| Aggregate charging power | 6.0 MW |
| Dedicated solar plant | 30.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.2 km / 61 kWh |
| Lowest traversal charging margin | line-3: 24 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $191 M |
| Stations | $54 M |
| Depots | $8.0 M |
| Rolling stock | $73 M |
| Dedicated solar plant | $25 M |
| Residual train control | $1.9 M |
| Charging microgrids | $1.4 M |
| EPC / project services | $23 M |
| **Total city programme** | **$377 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $83 M (22.0%) |
| Domestic / local capital | $294 M (78.0%) |
| Annual public construction commitment | $41 M / yr for 10 years |
| Annual post-grace debt service | $38 M / yr |
| External capital saved vs default turnkey sensitivity | $596 M |
| Capital + lifetime external interest saved | $1.37 bn |
| Annual OPEX | $9.0 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 161 assets / 764 tasks | [`tete-operations-manifest.json`](operations/tete-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tete.toml`](tete.toml) | Expanded simulator scenario |
| [`tete.corridor.geojson`](tete.corridor.geojson) | GIS corridor and stations |
| [`tete.design-quality.yaml`](tete.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tete
```

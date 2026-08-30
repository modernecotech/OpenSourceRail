# Fort-Portal — Urban Rail Network

**Country:** UG · **Population:** 200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Fort-Portal-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$443 M (87.6%) of external capital** and **$555 M of external interest**. Capital plus saved interest totals **$998 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Fort-Portal rail network on OpenStreetMap](fort-portal-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 1 |
| Route length | 36.3 km double track |
| Coverage / transfer reachability | 83.8% / 100% |
| Estimated station catchment | 167,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 76 × 2-car `tram-2car` trainsets (68 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.2 km | 5 | 26 | SE Mid ↔ NW Outer |
| line-2 |  9.2 km | 5 | 20 | NE Inner ↔ SW Mid |
| line-3 | 14.9 km | 5 | 30 | E Outer ↔ W Mid |
| **Total** | **36.3 km** | **15 unique** | **76** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 16,874 train-km/day |
| Annual traction demand | 53.2 GWh |
| Station/depot PV / storage | 9.2 MW / 47.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 24.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.8 km / 34 kWh |
| Lowest traversal charging margin | line-1: 43 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $108 M |
| Stations | $82 M |
| Depots | $8.0 M |
| Rolling stock | $43 M |
| Dedicated solar plant | $19 M |
| Residual train control | $1.8 M |
| Charging microgrids | $1.7 M |
| EPC / project services | $17 M |
| **Total city programme** | **$281 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $62 M (22.2%) |
| Domestic / local capital | $218 M (77.8%) |
| Annual public construction commitment | $34 M / yr for 7 years |
| Annual post-grace debt service | $28 M / yr |
| External capital saved vs default turnkey sensitivity | $443 M |
| Capital + lifetime external interest saved | $998 M |
| Annual OPEX | $6.7 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 167 assets / 762 tasks | [`fort-portal-operations-manifest.json`](operations/fort-portal-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`fort-portal.toml`](fort-portal.toml) | Expanded simulator scenario |
| [`fort-portal.corridor.geojson`](fort-portal.corridor.geojson) | GIS corridor and stations |
| [`fort-portal.design-quality.yaml`](fort-portal.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh fort-portal
```

# Arua — Urban Rail Network

**Country:** UG · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Arua-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$456 M (87.7%) of external capital** and **$571 M of external interest**. Capital plus saved interest totals **$1.03 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Arua rail network on OpenStreetMap](arua-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 16 / 1 |
| Route length | 37.7 km double track |
| Coverage / transfer reachability | 78.9% / 100% |
| Estimated station catchment | 197,250 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 77 × 2-car `tram-2car` trainsets (69 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.9 km | 5 | 21 | NW Mid ↔ SE Mid |
| line-2 | 15.0 km | 5 | 30 | E Outer ↔ W Outer |
| line-3 | 12.8 km | 6 | 26 | NE Outer ↔ S Mid |
| **Total** | **37.7 km** | **16 unique** | **77** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 17,545 train-km/day |
| Annual traction demand | 55.3 GWh |
| Station/depot PV / storage | 9.5 MW / 47.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 25.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.4 km / 32 kWh |
| Lowest traversal charging margin | line-1: 44 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $111 M |
| Stations | $85 M |
| Depots | $8.0 M |
| Rolling stock | $43 M |
| Dedicated solar plant | $20 M |
| Residual train control | $1.9 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $18 M |
| **Total city programme** | **$289 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $64 M (22.2%) |
| Domestic / local capital | $225 M (77.8%) |
| Annual public construction commitment | $34 M / yr for 7 years |
| Annual post-grace debt service | $29 M / yr |
| External capital saved vs default turnkey sensitivity | $456 M |
| Capital + lifetime external interest saved | $1.03 bn |
| Annual OPEX | $6.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 173 assets / 784 tasks | [`arua-operations-manifest.json`](operations/arua-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`arua.toml`](arua.toml) | Expanded simulator scenario |
| [`arua.corridor.geojson`](arua.corridor.geojson) | GIS corridor and stations |
| [`arua.design-quality.yaml`](arua.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh arua
```

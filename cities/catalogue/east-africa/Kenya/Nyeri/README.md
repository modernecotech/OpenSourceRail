# Nyeri — Urban Rail Network

**Country:** KE · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nyeri-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$599 M (88.6%) of external capital** and **$751 M of external interest**. Capital plus saved interest totals **$1.35 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Nyeri rail network on OpenStreetMap](nyeri-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 16 / 3 |
| Route length | 36.7 km double track |
| Coverage / transfer reachability | 62.3% / 100% |
| Estimated station catchment | 155,750 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 76 × 2-car `tram-2car` trainsets (68 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.4 km | 5 | 21 | SE Outer ↔ W Mid |
| line-2 | 15.1 km | 6 | 30 | NE Outer ↔ S Outer |
| line-3 | 11.2 km | 5 | 25 | SW Outer ↔ N Mid |
| **Total** | **36.7 km** | **16 unique** | **76** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 17,056 train-km/day |
| Annual traction demand | 53.8 GWh |
| Station/depot PV / storage | 9.5 MW / 47.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 24.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.0 km / 30 kWh |
| Lowest traversal charging margin | line-1: 41 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $191 M |
| Stations | $88 M |
| Depots | $8.0 M |
| Rolling stock | $43 M |
| Dedicated solar plant | $20 M |
| Residual train control | $1.8 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $23 M |
| **Total city programme** | **$376 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $77 M (20.5%) |
| Domestic / local capital | $299 M (79.5%) |
| Annual public construction commitment | $39 M / yr for 7 years |
| Annual post-grace debt service | $33 M / yr |
| External capital saved vs default turnkey sensitivity | $599 M |
| Capital + lifetime external interest saved | $1.35 bn |
| Annual OPEX | $8.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 171 assets / 776 tasks | [`nyeri-operations-manifest.json`](operations/nyeri-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nyeri.toml`](nyeri.toml) | Expanded simulator scenario |
| [`nyeri.corridor.geojson`](nyeri.corridor.geojson) | GIS corridor and stations |
| [`nyeri.design-quality.yaml`](nyeri.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh nyeri
```

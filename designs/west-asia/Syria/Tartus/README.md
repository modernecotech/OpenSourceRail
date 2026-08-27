# Tartus — Urban Rail Network

**Country:** SY · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tartus-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$368 M (88.0%) of external capital** and **$476 M of external interest**. Capital plus saved interest totals **$844 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tartus rail network on OpenStreetMap](tartus-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 13 / 1 |
| Route length | 27.8 km double track |
| Coverage / transfer reachability | 83.2% / 100% |
| Estimated station catchment | 208,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 60 × 2-car `tram-2car` trainsets (53 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.2 km | 5 | 26 | S Outer ↔ NW Mid |
| line-2 | 10.7 km | 5 | 21 | SE Outer ↔ N Mid |
| line-3 |  5.0 km | 3 | 13 | N Mid ↔ W Inner |
| **Total** | **27.8 km** | **13 unique** | **60** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 12,939 train-km/day |
| Annual traction demand | 40.8 GWh |
| Station/depot PV / storage | 8.6 MW / 46.0 MWh |
| Aggregate charging power | 6.5 MW |
| Dedicated solar plant | 13.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 4.4 km / 21 kWh |
| Lowest traversal charging margin | line-3: 39 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $87 M |
| Stations | $76 M |
| Depots | $8.0 M |
| Rolling stock | $34 M |
| Dedicated solar plant | $11 M |
| Residual train control | $1.4 M |
| Charging microgrids | $1.5 M |
| EPC / project services | $15 M |
| **Total city programme** | **$233 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $50 M (21.6%) |
| Domestic / local capital | $182 M (78.4%) |
| Annual public construction commitment | $35 M / yr for 10 years |
| Annual post-grace debt service | $32 M / yr |
| External capital saved vs default turnkey sensitivity | $368 M |
| Capital + lifetime external interest saved | $844 M |
| Annual OPEX | $5.3 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 138 assets / 617 tasks | [`tartus-operations-manifest.json`](operations/tartus-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tartus.toml`](tartus.toml) | Expanded simulator scenario |
| [`tartus.corridor.geojson`](tartus.corridor.geojson) | GIS corridor and stations |
| [`tartus.design-quality.yaml`](tartus.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh tartus
```

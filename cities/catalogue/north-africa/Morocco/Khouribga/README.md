# Khouribga — Urban Rail Network

**Country:** MA · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Khouribga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$289 M (88.2%) of external capital** and **$355 M of external interest**. Capital plus saved interest totals **$644 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Khouribga rail network on OpenStreetMap](khouribga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 1 |
| Route length | 18.8 km double track |
| Coverage / transfer reachability | 82.0% / 100% |
| Estimated station catchment | 205,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 46 × 2-car `tram-2car` trainsets (40 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.9 km | 4 | 19 | S Outer ↔ E Outer |
| line-2 |  5.7 km | 4 | 15 | N Mid ↔ SW Outer |
| line-3 |  4.2 km | 3 | 12 | NW Mid ↔ S Inner |
| **Total** | **18.8 km** | **11 unique** | **46** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 8,729 train-km/day |
| Annual traction demand | 27.5 GWh |
| Station/depot PV / storage | 8.0 MW / 45.0 MWh |
| Aggregate charging power | 5.5 MW |
| Dedicated solar plant | 5.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 4.0 km / 21 kWh |
| Lowest traversal charging margin | line-3: 41 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $61 M |
| Stations | $68 M |
| Depots | $8.0 M |
| Rolling stock | $26 M |
| Dedicated solar plant | $4.2 M |
| Residual train control | $939 k |
| Charging microgrids | $1.3 M |
| EPC / project services | $12 M |
| **Total city programme** | **$182 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $39 M (21.2%) |
| Domestic / local capital | $143 M (78.8%) |
| Annual public construction commitment | $13 M / yr for 5 years |
| Annual post-grace debt service | $8.8 M / yr |
| External capital saved vs default turnkey sensitivity | $289 M |
| Capital + lifetime external interest saved | $644 M |
| Annual OPEX | $5.3 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 112 assets / 487 tasks | [`khouribga-operations-manifest.json`](operations/khouribga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`khouribga.toml`](khouribga.toml) | Expanded simulator scenario |
| [`khouribga.corridor.geojson`](khouribga.corridor.geojson) | GIS corridor and stations |
| [`khouribga.design-quality.yaml`](khouribga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh khouribga
```

# Soyo — Urban Rail Network

**Country:** AO · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Soyo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$469 M (88.2%) of external capital** and **$577 M of external interest**. Capital plus saved interest totals **$1.05 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Soyo rail network on OpenStreetMap](soyo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 3 |
| Route length | 29.4 km double track |
| Coverage / transfer reachability | 81.2% / 100% |
| Estimated station catchment | 203,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 63 × 2-car `tram-2car` trainsets (56 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.4 km | 5 | 20 | NW Outer ↔ S Inner |
| line-2 |  8.5 km | 4 | 18 | S Mid ↔ E Mid |
| line-3 | 11.5 km | 5 | 25 | NW Mid ↔ S Outer |
| **Total** | **29.4 km** | **14 unique** | **63** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 13,679 train-km/day |
| Annual traction demand | 43.1 GWh |
| Station/depot PV / storage | 8.9 MW / 46.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 18.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 5.3 km / 27 kWh |
| Lowest traversal charging margin | line-2: 35 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $112 M |
| Stations | $104 M |
| Depots | $8.0 M |
| Rolling stock | $35 M |
| Dedicated solar plant | $14 M |
| Residual train control | $1.5 M |
| Charging microgrids | $1.7 M |
| EPC / project services | $18 M |
| **Total city programme** | **$295 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $63 M (21.2%) |
| Domestic / local capital | $233 M (78.8%) |
| Annual public construction commitment | $34 M / yr for 5 years |
| Annual post-grace debt service | $25 M / yr |
| External capital saved vs default turnkey sensitivity | $469 M |
| Capital + lifetime external interest saved | $1.05 bn |
| Annual OPEX | $7.2 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 149 assets / 656 tasks | [`soyo-operations-manifest.json`](operations/soyo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`soyo.toml`](soyo.toml) | Expanded simulator scenario |
| [`soyo.corridor.geojson`](soyo.corridor.geojson) | GIS corridor and stations |
| [`soyo.design-quality.yaml`](soyo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh soyo
```

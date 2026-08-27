# Nador — Urban Rail Network

**Country:** MA · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nador-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$422 M (87.8%) of external capital** and **$518 M of external interest**. Capital plus saved interest totals **$940 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Nador rail network on OpenStreetMap](nador-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 16 / 1 |
| Route length | 34.3 km double track |
| Coverage / transfer reachability | 69.6% / 100% |
| Estimated station catchment | 174,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 72 × 2-car `tram-2car` trainsets (65 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.0 km | 5 | 21 | E Inner ↔ W Outer |
| line-2 | 15.4 km | 7 | 32 | NW Outer ↔ SE Mid |
| line-3 |  9.0 km | 4 | 19 | SE Outer ↔ NW Inner |
| **Total** | **34.3 km** | **16 unique** | **72** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 15,971 train-km/day |
| Annual traction demand | 50.4 GWh |
| Station/depot PV / storage | 9.2 MW / 47.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 18.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 34 kWh |
| Lowest traversal charging margin | line-3: 42 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $103 M |
| Stations | $81 M |
| Depots | $8.0 M |
| Rolling stock | $40 M |
| Dedicated solar plant | $15 M |
| Residual train control | $1.7 M |
| Charging microgrids | $1.7 M |
| EPC / project services | $16 M |
| **Total city programme** | **$267 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $58 M (21.9%) |
| Domestic / local capital | $208 M (78.1%) |
| Annual public construction commitment | $18 M / yr for 5 years |
| Annual post-grace debt service | $13 M / yr |
| External capital saved vs default turnkey sensitivity | $422 M |
| Capital + lifetime external interest saved | $940 M |
| Annual OPEX | $7.5 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 166 assets / 745 tasks | [`nador-operations-manifest.json`](operations/nador-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nador.toml`](nador.toml) | Expanded simulator scenario |
| [`nador.corridor.geojson`](nador.corridor.geojson) | GIS corridor and stations |
| [`nador.design-quality.yaml`](nador.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh nador
```

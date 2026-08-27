# Fez — Urban Rail Network

**Country:** MA · **Population:** 1,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Fez-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.64 bn (87.4%) of external capital** and **$2.01 bn of external interest**. Capital plus saved interest totals **$3.65 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Fez rail network on OpenStreetMap](fez-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 45 / 9 |
| Route length | 114.4 km double track |
| Coverage / transfer reachability | 73.1% / 83% |
| Estimated station catchment | 950,300 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 128 × 4-car `metro-4car` trainsets (115 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 22.3 km | 10 | 40 | NE Mid ↔ SW Outer |
| line-2 | 20.3 km | 9 | 36 | W Outer ↔ SE Mid |
| line-3 | 19.8 km | 8 | 32 | E Outer ↔ NW Mid |
| line-4 | 52.0 km | 18 | 20 | NW Mid ↔ W Mid |
| **Total** | **114.4 km** | **45 unique** | **128** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,628 one-way journeys / 41,121 train-km/day |
| Annual traction demand | 259.4 GWh |
| Station/depot PV / storage | 17.9 MW / 104.5 MWh |
| Aggregate charging power | 66.0 MW |
| Dedicated solar plant | 128.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 67 kWh |
| Lowest traversal charging margin | line-3: 183 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $416 M |
| Stations | $289 M |
| Depots | $8.0 M |
| Rolling stock | $143 M |
| Dedicated solar plant | $102 M |
| Residual train control | $5.7 M |
| Charging microgrids | $15 M |
| EPC / project services | $61 M |
| **Total city programme** | **$1.04 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $236 M (22.7%) |
| Domestic / local capital | $804 M (77.3%) |
| Annual public construction commitment | $72 M / yr for 5 years |
| Annual post-grace debt service | $50 M / yr |
| External capital saved vs default turnkey sensitivity | $1.64 bn |
| Capital + lifetime external interest saved | $3.65 bn |
| Annual OPEX | $26 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 382 assets / 1,584 tasks | [`fez-operations-manifest.json`](operations/fez-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`fez.toml`](fez.toml) | Expanded simulator scenario |
| [`fez.corridor.geojson`](fez.corridor.geojson) | GIS corridor and stations |
| [`fez.design-quality.yaml`](fez.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh fez
```

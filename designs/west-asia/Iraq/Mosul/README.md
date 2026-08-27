# Mosul — Urban Rail Network

**Country:** IQ · **Population:** 1,940,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mosul-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.04 bn (87.6%) of external capital** and **$3.73 bn of external interest**. Capital plus saved interest totals **$6.77 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mosul rail network on OpenStreetMap](mosul-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 69 / 12 |
| Route length | 207.3 km double track |
| Coverage / transfer reachability | 61.7% / 80% |
| Estimated station catchment | 1,196,980 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 256 × 4-car `metro-4car` trainsets (229 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 34.5 km | 11 | 56 | SE Mid ↔ NW Outer |
| line-2 | 31.1 km | 11 | 51 | S Mid ↔ NE Outer |
| line-3 | 29.4 km | 10 | 45 | SE Mid ↔ W Outer |
| line-4 | 25.4 km | 10 | 40 | E Outer ↔ SW Mid |
| line-5 | 23.9 km | 10 | 40 | S Mid ↔ NW Mid |
| line-6 | 63.0 km | 17 | 24 | N Inner ↔ NW Inner |
| **Total** | **207.3 km** | **69 unique** | **256** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 81,756 train-km/day |
| Annual traction demand | 515.7 GWh |
| Station/depot PV / storage | 22.4 MW / 127.0 MWh |
| Aggregate charging power | 88.5 MW |
| Dedicated solar plant | 245.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 16.0 km / 172 kWh |
| Lowest traversal charging margin | line-4: 140 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $949 M |
| Stations | $344 M |
| Depots | $8.0 M |
| Rolling stock | $287 M |
| Dedicated solar plant | $196 M |
| Residual train control | $10 M |
| Charging microgrids | $19 M |
| EPC / project services | $113 M |
| **Total city programme** | **$1.93 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $432 M (22.4%) |
| Domestic / local capital | $1.50 bn (77.6%) |
| Annual public construction commitment | $181 M / yr for 5 years |
| Annual post-grace debt service | $133 M / yr |
| External capital saved vs default turnkey sensitivity | $3.04 bn |
| Capital + lifetime external interest saved | $6.77 bn |
| Annual OPEX | $47 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 638 assets / 2,824 tasks | [`mosul-operations-manifest.json`](operations/mosul-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mosul.toml`](mosul.toml) | Expanded simulator scenario |
| [`mosul.corridor.geojson`](mosul.corridor.geojson) | GIS corridor and stations |
| [`mosul.design-quality.yaml`](mosul.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh mosul
```

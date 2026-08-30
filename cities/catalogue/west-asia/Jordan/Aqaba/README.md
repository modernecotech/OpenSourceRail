# Aqaba — Urban Rail Network

**Country:** JO · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Aqaba-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$478 M (88.2%) of external capital** and **$588 M of external interest**. Capital plus saved interest totals **$1.07 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Aqaba rail network on OpenStreetMap](aqaba-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 16 / 2 |
| Route length | 34.6 km double track |
| Coverage / transfer reachability | 62.8% / 100% |
| Estimated station catchment | 157,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 71 × 2-car `tram-2car` trainsets (64 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.0 km | 6 | 30 | W Outer ↔ E Outer |
| line-2 |  9.6 km | 5 | 20 | S Mid ↔ NE Outer |
| line-3 | 10.0 km | 5 | 21 | SE Mid ↔ W Outer |
| **Total** | **34.6 km** | **16 unique** | **71** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 16,098 train-km/day |
| Annual traction demand | 50.8 GWh |
| Station/depot PV / storage | 9.5 MW / 47.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 15.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 3.6 km / 19 kWh |
| Lowest traversal charging margin | line-3: 39 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $116 M |
| Stations | $102 M |
| Depots | $8.0 M |
| Rolling stock | $40 M |
| Dedicated solar plant | $13 M |
| Residual train control | $1.7 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $19 M |
| **Total city programme** | **$301 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $64 M (21.2%) |
| Domestic / local capital | $237 M (78.8%) |
| Annual public construction commitment | $27 M / yr for 5 years |
| Annual post-grace debt service | $19 M / yr |
| External capital saved vs default turnkey sensitivity | $478 M |
| Capital + lifetime external interest saved | $1.07 bn |
| Annual OPEX | $9.0 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 167 assets / 742 tasks | [`aqaba-operations-manifest.json`](operations/aqaba-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`aqaba.toml`](aqaba.toml) | Expanded simulator scenario |
| [`aqaba.corridor.geojson`](aqaba.corridor.geojson) | GIS corridor and stations |
| [`aqaba.design-quality.yaml`](aqaba.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh aqaba
```

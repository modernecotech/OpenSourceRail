# Quelimane — Urban Rail Network

**Country:** MZ · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Quelimane-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$140 M (86.6%) of external capital** and **$181 M of external interest**. Capital plus saved interest totals **$321 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Quelimane rail network on OpenStreetMap](quelimane-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 1 / 5 / 0 |
| Route length | 10.3 km double track |
| Coverage / transfer reachability | 47.6% / 100% |
| Estimated station catchment | 166,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 23 × 3-car `light-metro-3car` trainsets (20 peak revenue) |
| Peak network throughput | 14,400 passengers/hour |
| Practical service capacity | 133,920 passenger-trips/day |
| Annual paid-trip planning range | 24.4–39.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.3 km | 5 | 23 | NE Outer ↔ W Outer |
| **Total** | **10.3 km** | **5 unique** | **23** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 465 one-way journeys / 4,774 train-km/day |
| Annual traction demand | 22.6 GWh |
| Station/depot PV / storage | 6.2 MW / 42.0 MWh |
| Aggregate charging power | 2.5 MW |
| Dedicated solar plant | 7.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 3.1 km / 23 kWh |
| Lowest traversal charging margin | line-1: 46 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $27 M |
| Stations | $21 M |
| Depots | $8.0 M |
| Rolling stock | $21 M |
| Dedicated solar plant | $6.2 M |
| Residual train control | $513 k |
| Charging microgrids | $650 k |
| EPC / project services | $5.5 M |
| **Total city programme** | **$90 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $22 M (24.1%) |
| Domestic / local capital | $68 M (75.9%) |
| Annual public construction commitment | $9.7 M / yr for 10 years |
| Annual post-grace debt service | $8.9 M / yr |
| External capital saved vs default turnkey sensitivity | $140 M |
| Capital + lifetime external interest saved | $321 M |
| Annual OPEX | $2.3 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 55 assets / 238 tasks | [`quelimane-operations-manifest.json`](operations/quelimane-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`quelimane.toml`](quelimane.toml) | Expanded simulator scenario |
| [`quelimane.corridor.geojson`](quelimane.corridor.geojson) | GIS corridor and stations |
| [`quelimane.design-quality.yaml`](quelimane.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh quelimane
```

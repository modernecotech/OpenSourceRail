# Antananarivo — Urban Rail Network

**Country:** MG · **Population:** 3,058,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Antananarivo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.24 bn (85.1%) of external capital** and **$6.76 bn of external interest**. Capital plus saved interest totals **$12.00 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Antananarivo rail network on OpenStreetMap](antananarivo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 101 / 13 |
| Route length | 324.5 km double track |
| Coverage / transfer reachability | 82.2% / 58% |
| Estimated station catchment | 2,513,676 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 504 × 6-car `metro-6car` trainsets (454 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 35.4 km | 11 | 65 | S Mid ↔ NE Outer |
| line-2 | 29.4 km | 10 | 56 | SE Mid ↔ NW Outer |
| line-3 | 34.2 km | 13 | 68 | W Outer ↔ E Mid |
| line-4 | 25.7 km | 8 | 48 | E Mid ↔ SW Mid |
| line-5 | 29.2 km | 9 | 52 | N Inner ↔ S Outer |
| line-6 | 35.5 km | 10 | 65 | E Outer ↔ W Outer |
| line-7 | 32.3 km | 10 | 61 | W Mid ↔ NE Outer |
| line-8 | 29.5 km | 9 | 53 | SE Mid ↔ NW Outer |
| line-9 | 73.4 km | 21 | 36 | NW Mid ↔ NW Mid |
| **Total** | **324.5 km** | **101 unique** | **504** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 133,853 train-km/day |
| Annual traction demand | 1,266.4 GWh |
| Station/depot PV / storage | 31.1 MW / 214.0 MWh |
| Aggregate charging power | 176.0 MW |
| Dedicated solar plant | 795.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 14.0 km / 210 kWh |
| Lowest traversal charging margin | line-8: 200 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.17 bn |
| Stations | $522 M |
| Depots | $8.0 M |
| Rolling stock | $847 M |
| Dedicated solar plant | $636 M |
| Residual train control | $16 M |
| Charging microgrids | $38 M |
| EPC / project services | $182 M |
| **Total city programme** | **$3.42 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $915 M (26.8%) |
| Domestic / local capital | $2.50 bn (73.2%) |
| Annual public construction commitment | $311 M / yr for 10 years |
| Annual post-grace debt service | $286 M / yr |
| External capital saved vs default turnkey sensitivity | $5.24 bn |
| Capital + lifetime external interest saved | $12.00 bn |
| Annual OPEX | $81 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,083 assets / 5,062 tasks | [`antananarivo-operations-manifest.json`](operations/antananarivo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`antananarivo.toml`](antananarivo.toml) | Expanded simulator scenario |
| [`antananarivo.corridor.geojson`](antananarivo.corridor.geojson) | GIS corridor and stations |
| [`antananarivo.design-quality.yaml`](antananarivo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh antananarivo
```

# Huye — Urban Rail Network

**Country:** RW · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Huye-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$462 M (87.2%) of external capital** and **$579 M of external interest**. Capital plus saved interest totals **$1.04 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Huye rail network on OpenStreetMap](huye-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 44.6 km double track |
| Coverage / transfer reachability | 67.7% / 100% |
| Estimated station catchment | 169,250 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 92 × 2-car `tram-2car` trainsets (83 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.9 km | 6 | 32 | SW Mid ↔ NE Outer |
| line-2 | 14.0 km | 5 | 29 | SE Outer ↔ W Mid |
| line-3 | 14.8 km | 6 | 31 | N Outer ↔ W Mid |
| **Total** | **44.6 km** | **17 unique** | **92** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 20,762 train-km/day |
| Annual traction demand | 65.5 GWh |
| Station/depot PV / storage | 8.9 MW / 46.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 32.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 9.0 km / 45 kWh |
| Lowest traversal charging margin | line-2: 37 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $119 M |
| Stations | $68 M |
| Depots | $8.0 M |
| Rolling stock | $52 M |
| Dedicated solar plant | $26 M |
| Residual train control | $2.2 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $18 M |
| **Total city programme** | **$294 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $68 M (23.0%) |
| Domestic / local capital | $227 M (77.0%) |
| Annual public construction commitment | $25 M / yr for 7 years |
| Annual post-grace debt service | $21 M / yr |
| External capital saved vs default turnkey sensitivity | $462 M |
| Capital + lifetime external interest saved | $1.04 bn |
| Annual OPEX | $7.1 M / yr |

## Local Evidence

**Evidence refresh required.** Retained passing results below are unverified.
The strict README generator rejected the evidence: engineering/simulation/validation-summary.json describes scenario SHA-256 b6b703c821747fbb9f8d55d4010c0ed6e4c4174ad92ac08209363088f0fe7a07, but huye.toml is 40f674920063fcafeda0f055ffdbdc4339973f58e5886f80b6d45a3f0541cfbe; rerun and update the validation evidence. This audit view does not accept or replace the retained solver results.

| Package | Current status | Evidence |
|---|---|---|
| Finance | unverified | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | unverified | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | unverified | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | unverified; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | unverified | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | unverified; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 191 assets / 896 tasks | [`huye-operations-manifest.json`](operations/huye-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`huye.toml`](huye.toml) | Expanded simulator scenario |
| [`huye.corridor.geojson`](huye.corridor.geojson) | GIS corridor and stations |
| [`huye.design-quality.yaml`](huye.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh huye
```

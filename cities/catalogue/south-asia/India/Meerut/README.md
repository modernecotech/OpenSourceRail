# Meerut — Urban Rail Network

**Country:** IN · **Population:** 1,600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Meerut-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.85 bn (87.2%) of external capital** and **$2.27 bn of external interest**. Capital plus saved interest totals **$4.12 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Meerut rail network on OpenStreetMap](meerut-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 47 / 8 |
| Route length | 145.4 km double track |
| Coverage / transfer reachability | 68.6% / 67% |
| Estimated station catchment | 1,097,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 158 × 4-car `metro-4car` trainsets (141 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 24.7 km | 10 | 40 | NW Outer ↔ E Mid |
| line-2 | 31.4 km | 10 | 48 | N Outer ↔ S Outer |
| line-3 | 31.2 km | 9 | 47 | SW Outer ↔ NE Mid |
| line-4 | 58.2 km | 18 | 23 | N Mid ↔ N Mid |
| **Total** | **145.4 km** | **47 unique** | **158** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,628 one-way journeys / 54,099 train-km/day |
| Annual traction demand | 341.2 GWh |
| Station/depot PV / storage | 16.7 MW / 98.5 MWh |
| Aggregate charging power | 60.0 MW |
| Dedicated solar plant | 160.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 11.5 km / 123 kWh |
| Lowest traversal charging margin | line-3: 146 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $503 M |
| Stations | $271 M |
| Depots | $8.0 M |
| Rolling stock | $177 M |
| Dedicated solar plant | $128 M |
| Residual train control | $7.3 M |
| Charging microgrids | $14 M |
| EPC / project services | $69 M |
| **Total city programme** | **$1.18 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $271 M (23.0%) |
| Domestic / local capital | $906 M (77.0%) |
| Annual public construction commitment | $101 M / yr for 5 years |
| Annual post-grace debt service | $73 M / yr |
| External capital saved vs default turnkey sensitivity | $1.85 bn |
| Capital + lifetime external interest saved | $4.12 bn |
| Annual OPEX | $27 M / yr |

## Local Evidence

**Evidence refresh required.** Retained passing results below are unverified.
The strict README generator rejected the evidence: engineering/simulation/validation-summary.json describes scenario SHA-256 ea5f67a5ccaabfbc3dbf8a9bbbb6783b205c4b4a5355955ed24814cb2af53235, but meerut.toml is 6f003ebb474b094e3db17836df3054eb605e98fde963a825082dd5573f64ab95; rerun and update the validation evidence. This audit view does not accept or replace the retained solver results.

| Package | Current status | Evidence |
|---|---|---|
| Finance | unverified | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | unverified | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | unverified | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | unverified; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | unverified | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | unverified; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 419 assets / 1,809 tasks | [`meerut-operations-manifest.json`](operations/meerut-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`meerut.toml`](meerut.toml) | Expanded simulator scenario |
| [`meerut.corridor.geojson`](meerut.corridor.geojson) | GIS corridor and stations |
| [`meerut.design-quality.yaml`](meerut.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh meerut
```

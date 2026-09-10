# Khamis-Mushait — Urban Rail Network

**Country:** SA · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Khamis-Mushait-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$983 M (85.9%) of external capital** and **$1.21 bn of external interest**. Capital plus saved interest totals **$2.19 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Khamis-Mushait rail network on OpenStreetMap](khamis-mushait-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 26 / 1 |
| Route length | 81.2 km double track |
| Coverage / transfer reachability | 44.9% / 33% |
| Estimated station catchment | 269,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 217 × 3-car `light-metro-3car` trainsets (195 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.1 km | 9 | 78 | SE Outer ↔ NW Outer |
| line-2 | 25.5 km | 8 | 69 | SE Mid ↔ NW Outer |
| line-3 | 26.5 km | 9 | 70 | N Outer ↔ SE Outer |
| **Total** | **81.2 km** | **26 unique** | **217** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 37,742 train-km/day |
| Annual traction demand | 178.5 GWh |
| Station/depot PV / storage | 12.2 MW / 52.0 MWh |
| Aggregate charging power | 12.5 MW |
| Dedicated solar plant | 79.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 8.6 km / 69 kWh |
| Lowest traversal charging margin | line-3: 59 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $230 M |
| Stations | $95 M |
| Depots | $8.0 M |
| Rolling stock | $195 M |
| Dedicated solar plant | $64 M |
| Residual train control | $4.1 M |
| Charging microgrids | $2.6 M |
| EPC / project services | $37 M |
| **Total city programme** | **$636 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $161 M (25.3%) |
| Domestic / local capital | $475 M (74.7%) |
| Annual public construction commitment | $43 M / yr for 5 years |
| Annual post-grace debt service | $31 M / yr |
| External capital saved vs default turnkey sensitivity | $983 M |
| Capital + lifetime external interest saved | $2.19 bn |
| Annual OPEX | $29 M / yr |

## Local Evidence

**Evidence refresh required.** Retained passing results below are unverified.
The strict README generator rejected the evidence: engineering/simulation/validation-summary.json describes scenario SHA-256 40569e91d9f53abb967dad26d7c886373c1113520c8bad2b59e87e6bed35bcd0, but khamis-mushait.toml is 49f402eda5acd8934694a85e84aee9dc88e9f38e94189db41c62659908bb438f; rerun and update the validation evidence. This audit view does not accept or replace the retained solver results.

| Package | Current status | Evidence |
|---|---|---|
| Finance | unverified | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | unverified | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | unverified | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | unverified; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | unverified | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | unverified; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 382 assets / 2,439 tasks | [`khamis-mushait-operations-manifest.json`](operations/khamis-mushait-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`khamis-mushait.toml`](khamis-mushait.toml) | Expanded simulator scenario |
| [`khamis-mushait.corridor.geojson`](khamis-mushait.corridor.geojson) | GIS corridor and stations |
| [`khamis-mushait.design-quality.yaml`](khamis-mushait.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh khamis-mushait
```

# Kassala — Urban Rail Network

**Country:** SD · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kassala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$435 M (88.1%) of external capital** and **$562 M of external interest**. Capital plus saved interest totals **$997 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kassala rail network on OpenStreetMap](kassala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 1 |
| Route length | 23.5 km double track |
| Coverage / transfer reachability | 80.7% / 100% |
| Estimated station catchment | 403,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 52 × 3-car `light-metro-3car` trainsets (46 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.3 km | 4 | 21 | N Outer ↔ SW Outer |
| line-2 |  6.1 km | 4 | 15 | E Mid ↔ W Mid |
| line-3 |  7.1 km | 3 | 16 | NE Mid ↔ SW Outer |
| **Total** | **23.5 km** | **11 unique** | **52** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 10,949 train-km/day |
| Annual traction demand | 51.8 GWh |
| Station/depot PV / storage | 8.0 MW / 45.0 MWh |
| Aggregate charging power | 5.5 MW |
| Dedicated solar plant | 18.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 5.3 km / 43 kWh |
| Lowest traversal charging margin | line-3: 23 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $133 M |
| Stations | $53 M |
| Depots | $8.0 M |
| Rolling stock | $47 M |
| Dedicated solar plant | $14 M |
| Residual train control | $1.2 M |
| Charging microgrids | $1.2 M |
| EPC / project services | $17 M |
| **Total city programme** | **$274 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $59 M (21.5%) |
| Domestic / local capital | $215 M (78.5%) |
| Annual public construction commitment | $33 M / yr for 10 years |
| Annual post-grace debt service | $30 M / yr |
| External capital saved vs default turnkey sensitivity | $435 M |
| Capital + lifetime external interest saved | $997 M |
| Annual OPEX | $6.4 M / yr |

## Local Evidence

**Evidence refresh required.** Retained passing results below are unverified.
The strict README generator rejected the evidence: engineering/simulation/validation-summary.json describes scenario SHA-256 01057c0ecf7defc57193067b83dfbbf3588bdc52f23dd048e1dccb71afb9a39d, but kassala.toml is bf09d1b3ae0b31926cc777ced840a08d0d3df8b4874677bdf16e3c273e5f9053; rerun and update the validation evidence. This audit view does not accept or replace the retained solver results.

| Package | Current status | Evidence |
|---|---|---|
| Finance | unverified | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | unverified | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | unverified | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | unverified; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | unverified | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | unverified; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 118 assets / 663 tasks | [`kassala-operations-manifest.json`](operations/kassala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kassala.toml`](kassala.toml) | Expanded simulator scenario |
| [`kassala.corridor.geojson`](kassala.corridor.geojson) | GIS corridor and stations |
| [`kassala.design-quality.yaml`](kassala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kassala
```

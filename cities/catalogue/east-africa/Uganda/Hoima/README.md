# Hoima — Urban Rail Network

**Country:** UG · **Population:** 200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hoima-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$318 M (87.4%) of external capital** and **$399 M of external interest**. Capital plus saved interest totals **$717 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Hoima rail network on OpenStreetMap](hoima-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 1 |
| Route length | 29.1 km double track |
| Coverage / transfer reachability | 80.8% / 33% |
| Estimated station catchment | 161,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 61 × 2-car `tram-2car` trainsets (54 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.3 km | 4 | 24 | S Inner ↔ NW Outer |
| line-2 | 10.7 km | 4 | 21 | SE Outer ↔ NW Inner |
| line-3 |  7.1 km | 3 | 16 | SW Inner ↔ E Mid |
| **Total** | **29.1 km** | **11 unique** | **61** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 13,539 train-km/day |
| Annual traction demand | 42.7 GWh |
| Station/depot PV / storage | 8.0 MW / 45.0 MWh |
| Aggregate charging power | 5.5 MW |
| Dedicated solar plant | 18.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 6.7 km / 33 kWh |
| Lowest traversal charging margin | line-3: 30 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $79 M |
| Stations | $51 M |
| Depots | $8.0 M |
| Rolling stock | $34 M |
| Dedicated solar plant | $15 M |
| Residual train control | $1.5 M |
| Charging microgrids | $1.2 M |
| EPC / project services | $12 M |
| **Total city programme** | **$202 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $46 M (22.7%) |
| Domestic / local capital | $156 M (77.3%) |
| Annual public construction commitment | $24 M / yr for 7 years |
| Annual post-grace debt service | $20 M / yr |
| External capital saved vs default turnkey sensitivity | $318 M |
| Capital + lifetime external interest saved | $717 M |
| Annual OPEX | $5.0 M / yr |

## Local Evidence

**Evidence refresh required.** Retained passing results below are unverified.
The strict README generator rejected the evidence: engineering/simulation/validation-summary.json describes scenario SHA-256 82432fa734dcb1c9883647588950d36a9aaa38d08c172616da21d8c58431ef0b, but hoima.toml is 971835d2d76792912796bf6a50d6cf0dc7721fcfb7ccf7b876b290b1c124725f; rerun and update the validation evidence. This audit view does not accept or replace the retained solver results.

| Package | Current status | Evidence |
|---|---|---|
| Finance | unverified | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | unverified | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | unverified | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | missing/fail; junction/authority gate open | not generated |
| GIS package | unverified | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | unverified; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 129 assets / 594 tasks | [`hoima-operations-manifest.json`](operations/hoima-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hoima.toml`](hoima.toml) | Expanded simulator scenario |
| [`hoima.corridor.geojson`](hoima.corridor.geojson) | GIS corridor and stations |
| [`hoima.design-quality.yaml`](hoima.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hoima
```

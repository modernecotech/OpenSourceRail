# Iringa — Urban Rail Network

**Country:** TZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Iringa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$335 M (88.1%) of external capital** and **$420 M of external interest**. Capital plus saved interest totals **$756 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Iringa rail network on OpenStreetMap](iringa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 1 |
| Route length | 27.1 km double track |
| Coverage / transfer reachability | 73.2% / 100% |
| Estimated station catchment | 183,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 58 × 2-car `tram-2car` trainsets (51 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.3 km | 6 | 25 | NE Outer ↔ SW Outer |
| line-2 |  9.7 km | 5 | 20 | S Outer ↔ W Outer |
| line-3 |  6.0 km | 3 | 13 | NW Mid ↔ E Mid |
| **Total** | **27.1 km** | **14 unique** | **58** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 12,591 train-km/day |
| Annual traction demand | 39.7 GWh |
| Station/depot PV / storage | 8.9 MW / 46.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 9.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 3.4 km / 19 kWh |
| Lowest traversal charging margin | line-3: 28 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $80 M |
| Stations | $68 M |
| Depots | $8.0 M |
| Rolling stock | $32 M |
| Dedicated solar plant | $7.2 M |
| Residual train control | $1.4 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $13 M |
| **Total city programme** | **$212 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $45 M (21.5%) |
| Domestic / local capital | $166 M (78.5%) |
| Annual public construction commitment | $19 M / yr for 7 years |
| Annual post-grace debt service | $16 M / yr |
| External capital saved vs default turnkey sensitivity | $335 M |
| Capital + lifetime external interest saved | $756 M |
| Annual OPEX | $5.2 M / yr |

## Local Evidence

**Evidence refresh required.** Retained passing results below are unverified.
The strict README generator rejected the evidence: engineering/simulation/validation-summary.json describes scenario SHA-256 abefa41f85b49d04a2bda48c10d5f608d3a109c053c319bd7e3f385b52614af0, but iringa.toml is e159d7ffa1ed2e1aadda0621d6b7b3a6d77822fe35725bdf8315142ffebe609c; rerun and update the validation evidence. This audit view does not accept or replace the retained solver results.

| Package | Current status | Evidence |
|---|---|---|
| Finance | unverified | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | unverified | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | unverified | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | unverified; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | unverified | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | unverified; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 140 assets / 772 tasks | [`iringa-operations-manifest.json`](operations/iringa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`iringa.toml`](iringa.toml) | Expanded simulator scenario |
| [`iringa.corridor.geojson`](iringa.corridor.geojson) | GIS corridor and stations |
| [`iringa.design-quality.yaml`](iringa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh iringa
```

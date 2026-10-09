# Jodhpur — Urban Rail Network

**Country:** IN · **Population:** 1,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jodhpur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.32 bn (89.4%) of external capital** and **$5.31 bn of external interest**. Capital plus saved interest totals **$9.62 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **5 lines**, including **0 additional residential lines**. Native population-count evidence is unavailable; resident coverage and population-led additional lines are not invented. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **123.531 km to 113.653 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **65 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **191 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **191 metro-4car trainsets / 764 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Jodhpur rail network on OpenStreetMap](jodhpur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 65 / 10 |
| Route length | 136.9 km double track |
| Direct transfers / reachable line pairs | 90.0% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 191 × 4-car `metro-4car` trainsets (172 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 24.7 km | 12 | 48 | S Outer ↔ N Outer |
| line-2 | 20.3 km | 11 | 41 | W Mid ↔ NE Outer |
| line-3 | 19.6 km | 11 | 40 | S Outer ↔ NW Inner |
| line-4 | 24.8 km | 10 | 41 | SE Outer ↔ NW Mid |
| line-5 | 47.6 km | 21 | 21 | NW Inner ↔ NW Inner |
| **Total** | **136.9 km** | **65 unique** | **191** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 52,623 train-km/day |
| Annual traction demand | 331.9 GWh |
| Station/depot PV / storage | 41.8 MW / 284.0 MWh |
| Aggregate charging power | 91.5 MW |
| Dedicated solar plant | 126.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 13.9 km / 149 kWh |
| Lowest traversal charging margin | line-4: 172 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.71 bn |
| Stations | $370 M |
| Depots | $94 M |
| Rolling stock | $214 M |
| Dedicated solar plant | $101 M |
| Residual train control | $6.8 M |
| Charging microgrids | $19 M |
| EPC / project services | $169 M |
| **Total city programme** | **$2.68 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $510 M (19.0%) |
| Domestic / local capital | $2.17 bn (81.0%) |
| Annual public construction commitment | $235 M / yr for 5 years |
| Annual post-grace debt service | $166 M / yr |
| External capital saved vs default turnkey sensitivity | $4.32 bn |
| Capital + lifetime external interest saved | $9.62 bn |
| Annual OPEX | $62 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 550 assets / 2,885 tasks | [`jodhpur-operations-manifest.json`](operations/jodhpur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jodhpur.toml`](jodhpur.toml) | Expanded simulator scenario |
| [`jodhpur.corridor.geojson`](jodhpur.corridor.geojson) | GIS corridor and stations |
| [`jodhpur.design-quality.yaml`](jodhpur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jodhpur
```

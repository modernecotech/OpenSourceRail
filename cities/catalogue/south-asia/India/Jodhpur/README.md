# Jodhpur — Urban Rail Network

**Country:** IN · **Population:** 1,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jodhpur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.44 bn (89.3%) of external capital** and **$5.46 bn of external interest**. Capital plus saved interest totals **$9.90 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **5 lines**, including **0 additional residential lines**. Native population-count evidence is unavailable; resident coverage and population-led additional lines are not invented. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **123.531 km to 129.346 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **66 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **211 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **211 metro-4car trainsets / 844 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Jodhpur rail network on OpenStreetMap](jodhpur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 66 / 11 |
| Route length | 151.2 km double track |
| Direct transfers / reachable line pairs | 90.0% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 211 × 4-car `metro-4car` trainsets (189 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.1 km | 11 | 48 | S Outer ↔ N Mid |
| line-2 | 23.7 km | 11 | 45 | SW Mid ↔ NE Mid |
| line-3 | 22.2 km | 13 | 47 | S Outer ↔ NW Inner |
| line-4 | 28.2 km | 14 | 52 | SE Outer ↔ W Inner |
| line-5 | 49.0 km | 17 | 19 | NW Inner ↔ NW Inner |
| **Total** | **151.2 km** | **66 unique** | **211** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 58,905 train-km/day |
| Annual traction demand | 371.5 GWh |
| Station/depot PV / storage | 41.8 MW / 284.0 MWh |
| Aggregate charging power | 91.5 MW |
| Dedicated solar plant | 147.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 10.5 km / 113 kWh |
| Lowest traversal charging margin | line-5: 156 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.71 bn |
| Stations | $396 M |
| Depots | $99 M |
| Rolling stock | $236 M |
| Dedicated solar plant | $118 M |
| Residual train control | $7.6 M |
| Charging microgrids | $19 M |
| EPC / project services | $173 M |
| **Total city programme** | **$2.76 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $534 M (19.3%) |
| Domestic / local capital | $2.23 bn (80.7%) |
| Annual public construction commitment | $242 M / yr for 5 years |
| Annual post-grace debt service | $171 M / yr |
| External capital saved vs default turnkey sensitivity | $4.44 bn |
| Capital + lifetime external interest saved | $9.90 bn |
| Annual OPEX | $64 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 577 assets / 3,082 tasks | [`jodhpur-operations-manifest.json`](operations/jodhpur-operations-manifest.json) |

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

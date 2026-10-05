# Baghdad — Urban Rail Network

**Country:** IQ · **Population:** 9,780,429 · [Original national catalogue](../NATIONAL-BRIEF.md)

**Current planning basis: 2026-10-04 [programme recalculation](engineering/programme-recalculation/README.md), `local_positive` conditional local-production case.** The main route is the reworked city-centre elevated planning alignment; service remains a capacity-led assumption. Revised scope is unquoted and uncommitted; this is not a construction design or an operating release.

Programme capital is **USD 15.233bn**, including line-local depots, final assembly and selected upstream component plants. The model requires **IQD 27.330tn unsourced support** in addition to assumed facilities, and the case retains **IQD 13.000tn terminal debt**. Older catalogue financial passes establish arithmetic for their own assumptions, not viability of this revised scope.

## Network

![Baghdad rail network on OpenStreetMap](baghdad-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 186 / 36 |
| Route length | 479.0 km double track |
| Coverage / transfer reachability | 39.4% / 81% |
| Estimated station catchment | 3,853,489 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 772 × 6-car `metro-6car` trainsets (697 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 49.1 km | 20 | 94 | S Outer ↔ N Outer |
| line-2 | 52.9 km | 20 | 96 | SE Outer ↔ NW Outer |
| line-3 | 49.5 km | 20 | 92 | S Outer ↔ NE Outer |
| line-4 | 41.9 km | 16 | 83 | NW Outer ↔ E Mid |
| line-5 | 47.3 km | 20 | 90 | W Mid ↔ E Outer |
| line-6 | 52.5 km | 21 | 104 | SW Outer ↔ NE Mid |
| line-7 | 40.0 km | 16 | 74 | E Outer ↔ SW Mid |
| line-8 | 48.1 km | 18 | 92 | SE Outer ↔ NW Mid |
| line-9 | 97.7 km | 35 | 47 | NW Mid ↔ NW Mid |
| **Total** | **479.0 km** | **186 unique** | **772** | |

Coverage is an anchor-weighted planning proxy, not measured pedestrian access. Straighter core routes change station catchments; OD counts, walk/feeder access and property clearance require review.

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 200,020 train-km/day |
| Annual traction demand | 1,892.3 GWh |
| Station/depot PV / storage | 53.9 MW / 366.0 MWh |
| Aggregate charging power | 328.0 MW |
| Dedicated solar plant | 931.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 17.7 km / 285 kWh |
| Lowest traversal charging margin | line-7: 271 kWh |
These energy quantities describe the current regenerated scenario. Zero annual residual grid import is an accounting balance, not accepted hourly autonomy. Depot charging/grid upgrades, duty and launch conflicts remain open.

## Current capital and operating people

| Revised capital scope | USD equivalent million |
| --- | --- |
| Civil and bearing allowance | 10,230.401 |
| Stations and core elevated access | 1,345.880 |
| Rolling stock | 1,205.976 |
| Final assembly and component plants | 411.941 |
| Line-local depots | 253.456 |
| Solar and charging | 813.671 |
| Signalling and programme overhead | 971.744 |
| **Total programme** | **15,233.069** |

There are **9 depots**, one per line, with **772 storage slots** for all 111 m six-car trains plus clearance. Depot reference capital is **USD 253.456m**, replacing the old USD 8m once. Workshop bays are sized separately by workload. The current case gives no capacity credit to station stabling. Actual land, foundations, connected access, installed charging and morning launch acceptance remain open. [Depot quantities](engineering/programme-recalculation/depots.json) · [Items](engineering/programme-recalculation/depot-items.csv).

The operating establishment is **3,716 FTE**, including **1,840 station-cover FTE**. Two staff per station and two normal eight-hour shifts give 744 daily shift assignments; retained 20.5-hour service also funds late cover and weekly/leave/training/sickness relief. Loaded annual payroll is **IQD 86.303bn**, with subsequent OPEX inflation. General pay starts at **IQD 1,175,455/month**, 50% above the historical employee median indexed to 2026. Technical/supervisor/senior/director grades are separate; this is not a newly measured median. [Roles and wages](engineering/programme-recalculation/workforce.csv).
Final assembly has 1294 production and 195 support FTE; selected upstream plants add 229 production and 35 support FTE. Their 55 paid production months are separate from permanent railway jobs. [Construction crew screen](engineering/programme-recalculation/construction-workforce.json) is incomplete; contractor labour is already inside contract rates.

## Iraqi manufacture and USD capital exposure

| Product | Network quantity | Current case |
| --- | --- | --- |
| bogie | 9264 | Local process option |
| motor-inverter-set | 9264 | Bought component |
| battery-225kwh-pack | 4632 | Local process option |
| door-cassette | 18528 | Local process option |
| window-cassette | 27792 | Bought component |

Imported process machinery supports the selected Iraqi fabrication and assembly options shown above. Cells/BMS, wheels/axles/bearings, inverters and other critical inputs retain imports. Products with negative Baghdad-only whole-order margins remain bought in this case. Plant readiness/qualification within 18 months is assumed, not demonstrated. [Make/buy appraisal](engineering/programme-recalculation/component-make-buy.csv).

Compared with the matched bought-component case, capital changes from USD 15.341bn to USD 15.233bn; imported invoice exposure changes from USD 3.287bn (21.43%) to USD 3.021bn (**19.83%**). The historical 148 km / USD 18bn proposal has a different scope and assumed all-USD funding; it is not a matched tender saving.

## Current funding and cashflows

Government capital is exactly **25%**. Imports use **50% government USD cash / 50% proposed Chinese USD credit**. Only Chinese debt is USD; the rest of government cash, bonds, bank/gap credit and mezzanine is IQD. Government invoice downpayments are scheduled within the total 25% contribution. FX is the historical planning anchor of IQD 1,300/USD.

| Capital-only source | Currency | Native amount |
| --- | --- | --- |
| Government import cash | USD | 1,510,440,238 |
| Government local cash | IQD | 2,987,175,216,330 |
| Chinese capital credit | USD | 1,510,440,238 |
| Ordinary capital bonds | IQD | 8,588,305,488,245 |
| Green capital bonds | IQD | 1,053,822,212,230 |
| Senior bank capital credit | IQD | 3,214,042,566,825 |
| Conditional climate grant | IQD | 32,500,000,000 |

Interest/fees, reserve cash, OPEX and gap facilities are additional cashflows, not capital added twice. Fares, kiosks, advertising, additional receipts and fare/OPEX indexation are included. Green/grant/rights terms and concessional gap credit remain uncommitted. Conditional first/full line revenue is month **40 / 77**; physical and financing gates are open.

The tested IQD mezzanine leaves 79 defaulted draw vintages and increases terminal debt to IQD 29.090tn. It does not cure the operating deficit. [Monthly cashflow](engineering/programme-recalculation/local_positive-monthly.csv) · [Six-month bond/loan placements](engineering/programme-recalculation/local_positive-semiannual.csv) · [All twelve cases](engineering/programme-recalculation/README.md).

## City-centre elevated alignment

The main design uses straight core radial tangents and broad curved ring connections where the retained water evidence permits them, inside the explicit 33.22–33.42°N / 44.28–44.53°E study area. Shoreline detours retain their separate curve and structure review gates. Land sections there are elevated; water crossings remain bridges. The final water-constrained core routes change from **301.670 km to 264.321 km**. The main network is **479.012 route km**, with **55.26% elevated** across the whole system. Maps, station placement, fleet, civil quantities, staff and finance use that reworked design. [Analytical controls and limitations](engineering/alignment/core-realignment.json).

![Earlier corridors and current central alignment](engineering/alignment/core-alignment-comparison.png)

Property/air rights, obstacles, protected sites, surveyed heights, utilities, piers, foundations, transition curves and vertical alignment remain open. Existing outer approaches retain street/raster bends; exceptional geometry still requires realignment or special products. Additional outer grade-separation sensitivities add 7.178 km and retain current dates; they are not the adopted core geometry or an achieved routing-penalty saving.

## Evidence, original references and regeneration

[Complete proposal PDF](Baghdad-Proposal.pdf) · [Editable proposal](BAGHDAD-PROPOSAL.md) · [Supporting data](Baghdad-Proposal-Supporting-Data.zip) · [Planning-only ERP drafts](engineering/programme-recalculation/erp-planning-drafts.json) · [Original catalogue finance](engineering/finance/FUNDING-MODEL.md) · [Original depot/stabling screen](engineering/depot-scope/README.md). Simulation, energy and asset evidence uses the current reworked geometry; the new staffing/depot/factory plans do not create accepted sites, appointed employees or operational assets.

Auto-planned by the OpenSourceRail design pipeline. Shared assumptions are in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md). Inputs: [design](design.toml), [scenario](baghdad.toml), [map](baghdad-network-map.png), [package evidence](package-manifest.json). City-local [simulation](engineering/simulation/validation-summary.json), [energy](engineering/energy/summary.json), [GIS](engineering/gis/summary.json), [operations](operations/acceptance-evidence-report.md) and [delivery](engineering/delivery/README.md) retain their recorded planning/release gates.

For presentation-only updates, run `.venv/bin/python tools/automation/publish-city-summary.py`; add `--check` to detect drift. The city regeneration pipeline uses this publisher. A stale scope study stops publication rather than silently restoring the original cost headline. Publication provenance is in [publication-manifest.json](publication-manifest.json).

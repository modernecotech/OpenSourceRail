# Nepal national OpenSourceRail strategy

Nepal should implement OpenSourceRail as one national industrial and financing programme covering the 3 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 3 |
| Served population represented | 2,342,000 |
| Trainsets across city plans | 483 |
| Vehicle/car modules to manufacture | 1,626 |
| City infrastructure + fleet CAPEX | $3.18 B |
| One shared national trainset factory | $58.6 M |
| National factory sizing basis | 976 modules: largest single-city programme (Kathmandu) |
| **Total national programme CAPEX** | **$3.24 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **43.5%** | **$1.41 B** | **$201.2 M / yr** |
| **Local capital for domestic value** | **56.5%** | **$1.83 B** | **$261.8 M / yr** |
| planned local-currency bond issuance | 45.2% of total | $1.47 B | $209.5 M / yr |
| local public equity / other domestic funding | 11.3% of total | $366.6 M | $52.4 M / yr |
| **Total capital programme** | **100.0%** | **$3.24 B** | **$463.0 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $82.7 M for external import finance plus $121.1 M for local bonds, or **$203.8 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$225.7 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $1.50 B | 35% | $523.9 M | $973.0 M |
| Stations | $612.2 M | 40% | $244.9 M | $367.3 M |
| Depots | $24.0 M | 40% | $9.6 M | $14.4 M |
| Rolling stock | $465.6 M | 55% | $256.1 M | $209.5 M |
| Dedicated solar plants | $354.5 M | 70% | $248.2 M | $106.4 M |
| Residual signalling / train control | $15.5 M | 80% | $12.4 M | $3.1 M |
| Charging microgrids | $25.0 M | 55% | $13.8 M | $11.2 M |
| EPC / project services | $188.9 M | 45% | $85.0 M | $103.9 M |
| Shared national trainset factory | $58.6 M | 25% | $14.6 M | $43.9 M |
| **Total** | **$3.24 B** | **43.5%** | **$1.41 B** | **$1.83 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Kathmandu](Kathmandu/README.md) | 1,442,000 | 244 | $2.00 B | 44.6% | $891.9 M | $1.11 B |
| [Pokhara](Pokhara/README.md) | 600,000 | 172 | $680.7 M | 44.6% | $303.9 M | $376.8 M |
| [Biratnagar](Biratnagar/README.md) | 300,000 | 67 | $500.1 M | 39.2% | $196.1 M | $303.9 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `NP`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

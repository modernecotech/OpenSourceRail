# Tunisia national OpenSourceRail strategy

Tunisia should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 2,900,000 |
| Trainsets across city plans | 255 |
| Vehicle/car modules to manufacture | 1,020 |
| City infrastructure + fleet CAPEX | $1.91 B |
| One shared national trainset factory | $61.2 M |
| National factory sizing basis | 1,020 modules: largest single-city programme (Tunis) |
| **Total national programme CAPEX** | **$1.98 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **43.6%** | **$862.2 M** | **$172.4 M / yr** |
| **Local capital for domestic value** | **56.4%** | **$1.11 B** | **$222.8 M / yr** |
| planned local-currency bond issuance | 45.1% of total | $891.3 M | $178.3 M / yr |
| local public equity / other domestic funding | 11.3% of total | $222.8 M | $44.6 M / yr |
| **Total capital programme** | **100.0%** | **$1.98 B** | **$395.3 M / yr** |

The annual construction draw is spread evenly over 5 planning years. Post-grace annual debt service is $49.4 M for external import finance plus $84.4 M for local bonds, or **$133.7 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$163.6 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $845.8 M | 35% | $296.0 M | $549.8 M |
| Stations | $404.9 M | 40% | $162.0 M | $242.9 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $285.6 M | 55% | $157.1 M | $128.5 M |
| Dedicated solar plants | $222.3 M | 70% | $155.6 M | $66.7 M |
| Residual signalling / train control | $11.1 M | 80% | $8.8 M | $2.2 M |
| Charging microgrids | $22.7 M | 55% | $12.5 M | $10.2 M |
| EPC / project services | $114.7 M | 45% | $51.6 M | $63.1 M |
| Shared national trainset factory | $61.2 M | 25% | $15.3 M | $45.9 M |
| **Total** | **$1.98 B** | **43.6%** | **$862.2 M** | **$1.11 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Tunis](Tunis/README.md) | 2,900,000 | 255 | $1.91 B | 44.2% | $844.9 M | $1.07 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `TN`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

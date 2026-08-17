# Philippines national OpenSourceRail strategy

Philippines should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 1,827,000 |
| Trainsets across city plans | 329 |
| Vehicle/car modules to manufacture | 1,316 |
| City infrastructure + fleet CAPEX | $2.35 B |
| One shared national trainset factory | $79.0 M |
| National factory sizing basis | 1,316 modules: largest single-city programme (Davao) |
| **Total national programme CAPEX** | **$2.44 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **44.5%** | **$1.09 B** | **$217.1 M / yr** |
| **Local capital for domestic value** | **55.5%** | **$1.35 B** | **$270.3 M / yr** |
| planned local-currency bond issuance | 44.4% of total | $1.08 B | $216.2 M / yr |
| local public equity / other domestic funding | 11.1% of total | $270.3 M | $54.1 M / yr |
| **Total capital programme** | **100.0%** | **$2.44 B** | **$487.4 M / yr** |

The annual construction draw is spread evenly over 5 planning years. Post-grace annual debt service is $62.2 M for external import finance plus $76.3 M for local bonds, or **$138.5 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$169.9 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $998.2 M | 35% | $349.4 M | $648.8 M |
| Stations | $467.7 M | 40% | $187.1 M | $280.6 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $368.5 M | 55% | $202.7 M | $165.8 M |
| Dedicated solar plants | $334.6 M | 70% | $234.2 M | $100.4 M |
| Residual signalling / train control | $14.0 M | 80% | $11.2 M | $2.8 M |
| Charging microgrids | $29.7 M | 55% | $16.3 M | $13.4 M |
| EPC / project services | $137.6 M | 45% | $61.9 M | $75.7 M |
| Shared national trainset factory | $79.0 M | 25% | $19.7 M | $59.2 M |
| **Total** | **$2.44 B** | **44.5%** | **$1.09 B** | **$1.35 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Davao](Davao/README.md) | 1,827,000 | 329 | $2.35 B | 45.2% | $1.06 B | $1.29 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `PH`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

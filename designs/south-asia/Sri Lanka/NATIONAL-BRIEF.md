# Sri Lanka national OpenSourceRail strategy

Sri Lanka should implement OpenSourceRail as one national industrial and financing programme covering the 4 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 4 |
| Served population represented | 7,398,000 |
| Trainsets across city plans | 983 |
| Vehicle/car modules to manufacture | 4,440 |
| City infrastructure + fleet CAPEX | $5.57 B |
| One shared national trainset factory | $178.9 M |
| National factory sizing basis | 2,982 modules: largest single-city programme (Colombo) |
| **Total national programme CAPEX** | **$5.76 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **45.9%** | **$2.64 B** | **$377.8 M / yr** |
| **Local capital for domestic value** | **54.1%** | **$3.12 B** | **$445.5 M / yr** |
| planned local-currency bond issuance | 43.3% of total | $2.49 B | $356.4 M / yr |
| local public equity / other domestic funding | 10.8% of total | $623.6 M | $89.1 M / yr |
| **Total capital programme** | **100.0%** | **$5.76 B** | **$823.3 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $155.4 M for external import finance plus $342.0 M for local bonds, or **$497.4 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$544.9 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $2.08 B | 35% | $726.4 M | $1.35 B |
| Stations | $986.0 M | 40% | $394.4 M | $591.6 M |
| Depots | $32.0 M | 40% | $12.8 M | $19.2 M |
| Rolling stock | $1.27 B | 55% | $699.8 M | $572.6 M |
| Dedicated solar plants | $816.7 M | 70% | $571.7 M | $245.0 M |
| Residual signalling / train control | $25.7 M | 80% | $20.5 M | $5.1 M |
| Charging microgrids | $52.4 M | 55% | $28.8 M | $23.6 M |
| EPC / project services | $323.6 M | 45% | $145.6 M | $178.0 M |
| Shared national trainset factory | $178.9 M | 25% | $44.7 M | $134.2 M |
| **Total** | **$5.76 B** | **45.9%** | **$2.64 B** | **$3.12 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Colombo](Colombo/README.md) | 5,648,000 | 497 | $3.81 B | 47.0% | $1.79 B | $2.02 B |
| [Kandy](Kandy/README.md) | 650,000 | 178 | $703.9 M | 45.0% | $316.9 M | $387.1 M |
| [Jaffna](Jaffna/README.md) | 600,000 | 131 | $483.1 M | 45.7% | $220.5 M | $262.5 M |
| [Galle](Galle/README.md) | 500,000 | 177 | $577.7 M | 46.2% | $266.7 M | $311.0 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `LK`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

# Cambodia national OpenSourceRail strategy

Cambodia should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 2,281,000 |
| Trainsets across city plans | 293 |
| Vehicle/car modules to manufacture | 1,172 |
| City infrastructure + fleet CAPEX | $2.53 B |
| One shared national trainset factory | $70.3 M |
| National factory sizing basis | 1,172 modules: largest single-city programme (Phnom Penh) |
| **Total national programme CAPEX** | **$2.61 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **43.0%** | **$1.12 B** | **$160.1 M / yr** |
| **Local capital for domestic value** | **57.0%** | **$1.49 B** | **$212.3 M / yr** |
| planned local-currency bond issuance | 45.6% of total | $1.19 B | $169.8 M / yr |
| local public equity / other domestic funding | 11.4% of total | $297.2 M | $42.5 M / yr |
| **Total capital programme** | **100.0%** | **$2.61 B** | **$372.3 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $65.8 M for external import finance plus $103.2 M for local bonds, or **$169.1 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$188.0 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $1.27 B | 35% | $442.8 M | $822.3 M |
| Stations | $459.3 M | 40% | $183.7 M | $275.6 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $328.2 M | 55% | $180.5 M | $147.7 M |
| Dedicated solar plants | $289.8 M | 70% | $202.9 M | $87.0 M |
| Residual signalling / train control | $11.9 M | 80% | $9.5 M | $2.4 M |
| Charging microgrids | $22.3 M | 55% | $12.3 M | $10.0 M |
| EPC / project services | $151.5 M | 45% | $68.2 M | $83.4 M |
| Shared national trainset factory | $70.3 M | 25% | $17.6 M | $52.7 M |
| **Total** | **$2.61 B** | **43.0%** | **$1.12 B** | **$1.49 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Phnom Penh](Phnom-Penh/README.md) | 2,281,000 | 293 | $2.53 B | 43.5% | $1.10 B | $1.43 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `KH`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

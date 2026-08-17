# El Salvador national OpenSourceRail strategy

El Salvador should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 1,800,000 |
| Trainsets across city plans | 308 |
| Vehicle/car modules to manufacture | 1,232 |
| City infrastructure + fleet CAPEX | $2.26 B |
| One shared national trainset factory | $73.9 M |
| National factory sizing basis | 1,232 modules: largest single-city programme (San Salvador) |
| **Total national programme CAPEX** | **$2.34 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **44.3%** | **$1.04 B** | **$207.4 M / yr** |
| **Local capital for domestic value** | **55.7%** | **$1.30 B** | **$260.4 M / yr** |
| planned local-currency bond issuance | 44.5% of total | $1.04 B | $208.3 M / yr |
| local public equity / other domestic funding | 11.1% of total | $260.4 M | $52.1 M / yr |
| **Total capital programme** | **100.0%** | **$2.34 B** | **$467.8 M / yr** |

The annual construction draw is spread evenly over 5 planning years. Post-grace annual debt service is $59.4 M for external import finance plus $122.5 M for local bonds, or **$181.9 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$218.5 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $966.8 M | 35% | $338.4 M | $628.4 M |
| Stations | $464.0 M | 40% | $185.6 M | $278.4 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $345.0 M | 55% | $189.7 M | $155.2 M |
| Dedicated solar plants | $312.4 M | 70% | $218.7 M | $93.7 M |
| Residual signalling / train control | $12.8 M | 80% | $10.3 M | $2.6 M |
| Charging microgrids | $23.6 M | 55% | $13.0 M | $10.6 M |
| EPC / project services | $132.6 M | 45% | $59.7 M | $72.9 M |
| Shared national trainset factory | $73.9 M | 25% | $18.5 M | $55.4 M |
| **Total** | **$2.34 B** | **44.3%** | **$1.04 B** | **$1.30 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [San Salvador](San-Salvador/README.md) | 1,800,000 | 308 | $2.26 B | 45.0% | $1.02 B | $1.24 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `SV`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

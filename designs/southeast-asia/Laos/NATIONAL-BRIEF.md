# Laos national OpenSourceRail strategy

Laos should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 948,000 |
| Trainsets across city plans | 155 |
| Vehicle/car modules to manufacture | 465 |
| City infrastructure + fleet CAPEX | $621.9 M |
| One shared national trainset factory | $27.9 M |
| National factory sizing basis | 465 modules: largest single-city programme (Vientiane) |
| **Total national programme CAPEX** | **$651.7 M** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **44.7%** | **$291.3 M** | **$41.6 M / yr** |
| **Local capital for domestic value** | **55.3%** | **$360.4 M** | **$51.5 M / yr** |
| planned local-currency bond issuance | 44.2% of total | $288.3 M | $41.2 M / yr |
| local public equity / other domestic funding | 11.1% of total | $72.1 M | $10.3 M / yr |
| **Total capital programme** | **100.0%** | **$651.7 M** | **$93.1 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $17.1 M for external import finance plus $31.4 M for local bonds, or **$48.6 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$53.7 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $245.0 M | 35% | $85.7 M | $159.2 M |
| Stations | $112.6 M | 40% | $45.0 M | $67.6 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $139.5 M | 55% | $76.7 M | $62.8 M |
| Dedicated solar plants | $74.4 M | 70% | $52.1 M | $22.3 M |
| Residual signalling / train control | $3.7 M | 80% | $3.0 M | $744 k |
| Charging microgrids | $2.8 M | 55% | $1.6 M | $1.3 M |
| EPC / project services | $37.8 M | 45% | $17.0 M | $20.8 M |
| Shared national trainset factory | $27.9 M | 25% | $7.0 M | $20.9 M |
| **Total** | **$651.7 M** | **44.7%** | **$291.3 M** | **$360.4 M** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Vientiane](Vientiane/README.md) | 948,000 | 155 | $621.9 M | 45.6% | $283.5 M | $338.4 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `LA`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

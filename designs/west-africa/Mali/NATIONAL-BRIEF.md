# Mali national OpenSourceRail strategy

Mali should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 2,929,000 |
| Trainsets across city plans | 255 |
| Vehicle/car modules to manufacture | 1,020 |
| City infrastructure + fleet CAPEX | $2.39 B |
| One shared national trainset factory | $61.2 M |
| National factory sizing basis | 1,020 modules: largest single-city programme (Bamako) |
| **Total national programme CAPEX** | **$2.45 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **41.4%** | **$1.01 B** | **$101.4 M / yr** |
| **Local capital for domestic value** | **58.6%** | **$1.44 B** | **$143.7 M / yr** |
| planned local-currency bond issuance | 46.9% of total | $1.15 B | $115.0 M / yr |
| local public equity / other domestic funding | 11.7% of total | $287.5 M | $28.7 M / yr |
| **Total capital programme** | **100.0%** | **$2.45 B** | **$245.1 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $62.2 M for external import finance plus $116.9 M for local bonds, or **$179.1 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$183.6 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $1.39 B | 35% | $488.0 M | $906.2 M |
| Stations | $341.1 M | 40% | $136.4 M | $204.7 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $285.6 M | 55% | $157.1 M | $128.5 M |
| Dedicated solar plants | $181.7 M | 70% | $127.2 M | $54.5 M |
| Residual signalling / train control | $10.6 M | 80% | $8.5 M | $2.1 M |
| Charging microgrids | $20.1 M | 55% | $11.1 M | $9.0 M |
| EPC / project services | $148.5 M | 45% | $66.8 M | $81.7 M |
| Shared national trainset factory | $61.2 M | 25% | $15.3 M | $45.9 M |
| **Total** | **$2.45 B** | **41.4%** | **$1.01 B** | **$1.44 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Bamako](Bamako/README.md) | 2,929,000 | 255 | $2.39 B | 41.8% | $996.3 M | $1.39 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `ML`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

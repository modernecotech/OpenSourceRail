# Myanmar national OpenSourceRail strategy

Myanmar should implement OpenSourceRail as one national industrial and financing programme covering the 2 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 2 |
| Served population represented | 6,926,000 |
| Trainsets across city plans | 937 |
| Vehicle/car modules to manufacture | 5,070 |
| City infrastructure + fleet CAPEX | $6.76 B |
| One shared national trainset factory | $238.0 M |
| National factory sizing basis | 3,966 modules: largest single-city programme (Yangon) |
| **Total national programme CAPEX** | **$7.01 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **45.6%** | **$3.20 B** | **$320.1 M / yr** |
| **Local capital for domestic value** | **54.4%** | **$3.81 B** | **$381.1 M / yr** |
| planned local-currency bond issuance | 43.5% of total | $3.05 B | $304.9 M / yr |
| local public equity / other domestic funding | 10.9% of total | $762.2 M | $76.2 M / yr |
| **Total capital programme** | **100.0%** | **$7.01 B** | **$701.1 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $196.5 M for external import finance plus $406.7 M for local bonds, or **$603.2 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$616.6 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $2.67 B | 35% | $932.8 M | $1.73 B |
| Stations | $1.15 B | 40% | $458.6 M | $687.9 M |
| Depots | $16.0 M | 40% | $6.4 M | $9.6 M |
| Rolling stock | $1.42 B | 55% | $780.8 M | $638.8 M |
| Dedicated solar plants | $1.03 B | 70% | $719.9 M | $308.5 M |
| Residual signalling / train control | $32.0 M | 80% | $25.6 M | $6.4 M |
| Charging microgrids | $74.5 M | 55% | $41.0 M | $33.5 M |
| EPC / project services | $391.4 M | 45% | $176.1 M | $215.3 M |
| Shared national trainset factory | $238.0 M | 25% | $59.5 M | $178.5 M |
| **Total** | **$7.01 B** | **45.6%** | **$3.20 B** | **$3.81 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Yangon](Yangon/README.md) | 5,200,000 | 661 | $4.66 B | 47.8% | $2.22 B | $2.43 B |
| [Mandalay](Mandalay/README.md) | 1,726,000 | 276 | $2.10 B | 43.3% | $909.5 M | $1.19 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `MM`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

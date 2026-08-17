# Yemen national OpenSourceRail strategy

Yemen should implement OpenSourceRail as one national industrial and financing programme covering the 9 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 9 |
| Served population represented | 8,337,500 |
| Trainsets across city plans | 1,054 |
| Vehicle/car modules to manufacture | 4,060 |
| City infrastructure + fleet CAPEX | $5.03 B |
| One shared national trainset factory | $128.9 M |
| National factory sizing basis | 2,148 modules: largest single-city programme (Sanaa) |
| **Total national programme CAPEX** | **$5.17 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **44.9%** | **$2.32 B** | **$232.2 M / yr** |
| **Local capital for domestic value** | **55.1%** | **$2.85 B** | **$284.7 M / yr** |
| planned local-currency bond issuance | 44.1% of total | $2.28 B | $227.7 M / yr |
| local public equity / other domestic funding | 11.0% of total | $569.3 M | $56.9 M / yr |
| **Total capital programme** | **100.0%** | **$5.17 B** | **$516.9 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $142.6 M for external import finance plus $412.8 M for local bonds, or **$555.4 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$571.3 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $1.88 B | 35% | $659.6 M | $1.22 B |
| Stations | $1.01 B | 40% | $403.4 M | $605.0 M |
| Depots | $72.0 M | 40% | $28.8 M | $43.2 M |
| Rolling stock | $1.17 B | 55% | $642.4 M | $525.6 M |
| Dedicated solar plants | $535.6 M | 70% | $374.9 M | $160.7 M |
| Residual signalling / train control | $27.3 M | 80% | $21.9 M | $5.5 M |
| Charging microgrids | $40.9 M | 55% | $22.5 M | $18.4 M |
| EPC / project services | $303.1 M | 45% | $136.4 M | $166.7 M |
| Shared national trainset factory | $128.9 M | 25% | $32.2 M | $96.7 M |
| **Total** | **$5.17 B** | **44.9%** | **$2.32 B** | **$2.85 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Sanaa](Sanaa/README.md) | 3,937,500 | 358 | $2.27 B | 47.4% | $1.08 B | $1.19 B |
| [Aden](Aden/README.md) | 985,000 | 97 | $400.2 M | 44.4% | $177.8 M | $222.4 M |
| [Hodeidah](Hodeidah/README.md) | 750,000 | 71 | $307.2 M | 43.9% | $134.9 M | $172.3 M |
| [Ibb](Ibb/README.md) | 750,000 | 106 | $435.0 M | 44.4% | $193.1 M | $241.9 M |
| [Taiz](Taiz/README.md) | 615,000 | 94 | $380.4 M | 44.4% | $168.7 M | $211.6 M |
| [Mukalla](Mukalla/README.md) | 550,000 | 152 | $490.8 M | 45.8% | $224.6 M | $266.1 M |
| [Dhamar](Dhamar/README.md) | 300,000 | 63 | $218.3 M | 42.4% | $92.6 M | $125.7 M |
| [Lahij](Lahij/README.md) | 250,000 | 59 | $308.2 M | 41.0% | $126.4 M | $181.8 M |
| [Sayun](Sayun/README.md) | 200,000 | 54 | $220.0 M | 41.7% | $91.7 M | $128.2 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `YE`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

# Sudan national OpenSourceRail strategy

Sudan should implement OpenSourceRail as one national industrial and financing programme covering the 7 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 7 |
| Served population represented | 11,029,000 |
| Trainsets across city plans | 1,319 |
| Vehicle/car modules to manufacture | 6,139 |
| City infrastructure + fleet CAPEX | $8.33 B |
| One shared national trainset factory | $229.3 M |
| National factory sizing basis | 3,822 modules: largest single-city programme (Khartoum) |
| **Total national programme CAPEX** | **$8.58 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **44.8%** | **$3.84 B** | **$384.2 M / yr** |
| **Local capital for domestic value** | **55.2%** | **$4.74 B** | **$473.8 M / yr** |
| planned local-currency bond issuance | 44.2% of total | $3.79 B | $379.1 M / yr |
| local public equity / other domestic funding | 11.0% of total | $947.7 M | $94.8 M / yr |
| **Total capital programme** | **100.0%** | **$8.58 B** | **$858.0 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $235.8 M for external import finance plus $577.3 M for local bonds, or **$813.2 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$836.2 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $3.35 B | 35% | $1.17 B | $2.18 B |
| Stations | $1.59 B | 40% | $637.0 M | $955.4 M |
| Depots | $56.0 M | 40% | $22.4 M | $33.6 M |
| Rolling stock | $1.74 B | 55% | $956.3 M | $782.4 M |
| Dedicated solar plants | $984.7 M | 70% | $689.3 M | $295.4 M |
| Residual signalling / train control | $42.1 M | 80% | $33.7 M | $8.4 M |
| Charging microgrids | $90.4 M | 55% | $49.7 M | $40.7 M |
| EPC / project services | $496.9 M | 45% | $223.6 M | $273.3 M |
| Shared national trainset factory | $229.3 M | 25% | $57.3 M | $172.0 M |
| **Total** | **$8.58 B** | **44.8%** | **$3.84 B** | **$4.74 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Khartoum](Khartoum/README.md) | 5,829,000 | 637 | $4.35 B | 46.9% | $2.04 B | $2.31 B |
| [Omdurman](Omdurman/README.md) | 2,800,000 | 312 | $2.30 B | 43.9% | $1.01 B | $1.29 B |
| [Nyala](Nyala/README.md) | 600,000 | 99 | $466.0 M | 43.2% | $201.2 M | $264.8 M |
| [El Obeid](El-Obeid/README.md) | 500,000 | 102 | $409.8 M | 44.4% | $182.0 M | $227.8 M |
| [Kassala](Kassala/README.md) | 500,000 | 52 | $304.6 M | 41.6% | $126.8 M | $177.9 M |
| [Port Sudan](Port-Sudan/README.md) | 500,000 | 76 | $339.3 M | 43.8% | $148.5 M | $190.8 M |
| [Waw](Waw/README.md) | 300,000 | 41 | $166.3 M | 41.3% | $68.7 M | $97.7 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `SD`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

# Afghanistan national OpenSourceRail strategy

Afghanistan should implement OpenSourceRail as one national industrial and financing programme covering the 5 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 5 |
| Served population represented | 7,051,000 |
| Trainsets across city plans | 822 |
| Vehicle/car modules to manufacture | 3,516 |
| City infrastructure + fleet CAPEX | $4.31 B |
| One shared national trainset factory | $126.0 M |
| National factory sizing basis | 2,100 modules: largest single-city programme (Kabul) |
| **Total national programme CAPEX** | **$4.45 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **45.0%** | **$2.00 B** | **$200.4 M / yr** |
| **Local capital for domestic value** | **55.0%** | **$2.45 B** | **$244.6 M / yr** |
| planned local-currency bond issuance | 44.0% of total | $1.96 B | $195.7 M / yr |
| local public equity / other domestic funding | 11.0% of total | $489.2 M | $48.9 M / yr |
| **Total capital programme** | **100.0%** | **$4.45 B** | **$445.0 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $123.0 M for external import finance plus $354.7 M for local bonds, or **$477.7 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$491.3 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $1.65 B | 35% | $577.4 M | $1.07 B |
| Stations | $813.7 M | 40% | $325.5 M | $488.2 M |
| Depots | $40.0 M | 40% | $16.0 M | $24.0 M |
| Rolling stock | $1.01 B | 55% | $557.0 M | $455.8 M |
| Dedicated solar plants | $483.8 M | 70% | $338.6 M | $145.1 M |
| Residual signalling / train control | $22.1 M | 80% | $17.7 M | $4.4 M |
| Charging microgrids | $42.2 M | 55% | $23.2 M | $19.0 M |
| EPC / project services | $259.4 M | 45% | $116.8 M | $142.7 M |
| Shared national trainset factory | $126.0 M | 25% | $31.5 M | $94.5 M |
| **Total** | **$4.45 B** | **45.0%** | **$2.00 B** | **$2.45 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Kabul](Kabul/README.md) | 4,601,000 | 350 | $2.48 B | 46.3% | $1.15 B | $1.33 B |
| [Herat](Herat/README.md) | 800,000 | 108 | $459.9 M | 44.0% | $202.5 M | $257.4 M |
| [Kandahar](Kandahar/README.md) | 700,000 | 113 | $466.2 M | 44.5% | $207.5 M | $258.8 M |
| [Mazar E Sharif](Mazar-E-Sharif/README.md) | 600,000 | 139 | $521.2 M | 44.9% | $234.0 M | $287.1 M |
| [Jalalabad Af](Jalalabad-Af/README.md) | 350,000 | 112 | $391.3 M | 45.1% | $176.6 M | $214.8 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `AF`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

# Uganda national OpenSourceRail strategy

Uganda should implement OpenSourceRail as one national industrial and financing programme covering the 12 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 12 |
| Served population represented | 4,925,000 |
| Trainsets across city plans | 1,160 |
| Vehicle/car modules to manufacture | 3,120 |
| City infrastructure + fleet CAPEX | $5.38 B |
| One shared national trainset factory | $65.8 M |
| National factory sizing basis | 1,096 modules: largest single-city programme (Kampala) |
| **Total national programme CAPEX** | **$5.45 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **43.8%** | **$2.39 B** | **$340.8 M / yr** |
| **Local capital for domestic value** | **56.2%** | **$3.06 B** | **$437.2 M / yr** |
| planned local-currency bond issuance | 45.0% of total | $2.45 B | $349.8 M / yr |
| local public equity / other domestic funding | 11.2% of total | $612.1 M | $87.4 M / yr |
| **Total capital programme** | **100.0%** | **$5.45 B** | **$778.1 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $140.2 M for external import finance plus $347.4 M for local bonds, or **$487.5 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$537.6 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $2.28 B | 35% | $797.0 M | $1.48 B |
| Stations | $1.18 B | 40% | $473.3 M | $710.0 M |
| Depots | $96.0 M | 40% | $38.4 M | $57.6 M |
| Rolling stock | $888.7 M | 55% | $488.8 M | $399.9 M |
| Dedicated solar plants | $543.0 M | 70% | $380.1 M | $162.9 M |
| Residual signalling / train control | $31.9 M | 80% | $25.5 M | $6.4 M |
| Charging microgrids | $39.8 M | 55% | $21.9 M | $17.9 M |
| EPC / project services | $320.8 M | 45% | $144.4 M | $176.4 M |
| Shared national trainset factory | $65.8 M | 25% | $16.4 M | $49.3 M |
| **Total** | **$5.45 B** | **43.8%** | **$2.39 B** | **$3.06 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Kampala](Kampala/README.md) | 1,875,000 | 274 | $1.95 B | 45.0% | $877.7 M | $1.07 B |
| [Mbarara](Mbarara/README.md) | 500,000 | 113 | $483.5 M | 45.0% | $217.6 M | $265.9 M |
| [Gulu](Gulu/README.md) | 350,000 | 139 | $470.5 M | 46.6% | $219.2 M | $251.3 M |
| [Jinja](Jinja/README.md) | 300,000 | 87 | $333.9 M | 42.8% | $142.9 M | $191.0 M |
| [Mbale](Mbale/README.md) | 300,000 | 71 | $274.0 M | 42.3% | $115.9 M | $158.2 M |
| [Arua](Arua/README.md) | 250,000 | 77 | $308.2 M | 42.6% | $131.3 M | $176.8 M |
| [Entebbe](Entebbe/README.md) | 250,000 | 78 | $317.2 M | 42.6% | $135.2 M | $182.0 M |
| [Lira](Lira/README.md) | 250,000 | 92 | $343.8 M | 43.0% | $147.8 M | $196.0 M |
| [Masaka](Masaka/README.md) | 250,000 | 69 | $276.9 M | 42.5% | $117.6 M | $159.3 M |
| [Fort Portal](Fort-Portal/README.md) | 200,000 | 76 | $299.5 M | 42.6% | $127.7 M | $171.9 M |
| [Hoima](Hoima/README.md) | 200,000 | 61 | $216.1 M | 43.0% | $92.9 M | $123.2 M |
| [Soroti](Soroti/README.md) | 200,000 | 23 | $102.4 M | 40.6% | $41.6 M | $60.8 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `UG`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

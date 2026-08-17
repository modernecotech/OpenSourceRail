# Lebanon national OpenSourceRail strategy

Lebanon should implement OpenSourceRail as one national industrial and financing programme covering the 3 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 3 |
| Served population represented | 3,230,000 |
| Trainsets across city plans | 367 |
| Vehicle/car modules to manufacture | 1,211 |
| City infrastructure + fleet CAPEX | $2.13 B |
| One shared national trainset factory | $45.4 M |
| National factory sizing basis | 756 modules: largest single-city programme (Beirut) |
| **Total national programme CAPEX** | **$2.18 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **43.5%** | **$950.5 M** | **$118.8 M / yr** |
| **Local capital for domestic value** | **56.5%** | **$1.23 B** | **$154.1 M / yr** |
| planned local-currency bond issuance | 45.2% of total | $986.0 M | $123.2 M / yr |
| local public equity / other domestic funding | 11.3% of total | $246.5 M | $30.8 M / yr |
| **Total capital programme** | **100.0%** | **$2.18 B** | **$272.9 M / yr** |

The annual construction draw is spread evenly over 8 planning years. Post-grace annual debt service is $56.6 M for external import finance plus $246.7 M for local bonds, or **$303.3 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$320.1 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $851.6 M | 35% | $298.0 M | $553.5 M |
| Stations | $552.9 M | 40% | $221.2 M | $331.7 M |
| Depots | $24.0 M | 40% | $9.6 M | $14.4 M |
| Rolling stock | $345.0 M | 55% | $189.8 M | $155.3 M |
| Dedicated solar plants | $202.9 M | 70% | $142.0 M | $60.9 M |
| Residual signalling / train control | $11.3 M | 80% | $9.0 M | $2.3 M |
| Charging microgrids | $20.4 M | 55% | $11.2 M | $9.2 M |
| EPC / project services | $129.5 M | 45% | $58.3 M | $71.2 M |
| Shared national trainset factory | $45.4 M | 25% | $11.3 M | $34.0 M |
| **Total** | **$2.18 B** | **43.5%** | **$950.5 M** | **$1.23 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Beirut](Beirut/README.md) | 2,200,000 | 189 | $1.42 B | 44.1% | $626.2 M | $795.1 M |
| [Tripoli Lb](Tripoli-Lb/README.md) | 730,000 | 99 | $410.8 M | 44.6% | $183.3 M | $227.5 M |
| [Sidon](Sidon/README.md) | 300,000 | 79 | $302.4 M | 42.4% | $128.2 M | $174.2 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `LB`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

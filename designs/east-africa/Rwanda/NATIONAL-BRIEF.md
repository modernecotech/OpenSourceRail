# Rwanda national OpenSourceRail strategy

Rwanda should implement OpenSourceRail as one national industrial and financing programme covering the 3 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 3 |
| Served population represented | 1,708,000 |
| Trainsets across city plans | 410 |
| Vehicle/car modules to manufacture | 1,274 |
| City infrastructure + fleet CAPEX | $2.50 B |
| One shared national trainset factory | $54.5 M |
| National factory sizing basis | 908 modules: largest single-city programme (Kigali) |
| **Total national programme CAPEX** | **$2.56 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **43.5%** | **$1.12 B** | **$159.3 M / yr** |
| **Local capital for domestic value** | **56.5%** | **$1.45 B** | **$206.7 M / yr** |
| planned local-currency bond issuance | 45.2% of total | $1.16 B | $165.4 M / yr |
| local public equity / other domestic funding | 11.3% of total | $289.4 M | $41.3 M / yr |
| **Total capital programme** | **100.0%** | **$2.56 B** | **$366.0 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $65.5 M for external import finance plus $105.5 M for local bonds, or **$171.1 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$189.9 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $1.03 B | 35% | $360.5 M | $669.5 M |
| Stations | $641.6 M | 40% | $256.6 M | $385.0 M |
| Depots | $24.0 M | 40% | $9.6 M | $14.4 M |
| Rolling stock | $356.7 M | 55% | $196.2 M | $160.5 M |
| Dedicated solar plants | $265.7 M | 70% | $186.0 M | $79.7 M |
| Residual signalling / train control | $13.7 M | 80% | $11.0 M | $2.7 M |
| Charging microgrids | $25.9 M | 55% | $14.2 M | $11.6 M |
| EPC / project services | $150.2 M | 45% | $67.6 M | $82.6 M |
| Shared national trainset factory | $54.5 M | 25% | $13.6 M | $40.9 M |
| **Total** | **$2.56 B** | **43.5%** | **$1.12 B** | **$1.45 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Kigali](Kigali/README.md) | 1,208,000 | 227 | $1.85 B | 44.2% | $818.0 M | $1.03 B |
| [Huye](Huye/README.md) | 250,000 | 92 | $315.3 M | 43.4% | $136.8 M | $178.5 M |
| [Rubavu](Rubavu/README.md) | 250,000 | 91 | $336.7 M | 43.1% | $145.2 M | $191.5 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `RW`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

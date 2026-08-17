# France national OpenSourceRail strategy

France should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 1,436,354 |
| Trainsets across city plans | 347 |
| Vehicle/car modules to manufacture | 1,388 |
| City infrastructure + fleet CAPEX | $2.39 B |
| One shared national trainset factory | $83.3 M |
| National factory sizing basis | 1,388 modules: largest single-city programme (Lyon) |
| **Total national programme CAPEX** | **$2.48 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **45.1%** | **$1.12 B** | **$372.9 M / yr** |
| **Local capital for domestic value** | **54.9%** | **$1.36 B** | **$453.9 M / yr** |
| planned local-currency bond issuance | 43.9% of total | $1.09 B | $363.1 M / yr |
| local public equity / other domestic funding | 11.0% of total | $272.4 M | $90.8 M / yr |
| **Total capital programme** | **100.0%** | **$2.48 B** | **$826.9 M / yr** |

The annual construction draw is spread evenly over 3 planning years. Post-grace annual debt service is $62.6 M for external import finance plus $49.1 M for local bonds, or **$111.8 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$173.8 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $1.03 B | 35% | $358.9 M | $666.5 M |
| Stations | $413.7 M | 40% | $165.5 M | $248.2 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $388.6 M | 55% | $213.8 M | $174.9 M |
| Dedicated solar plants | $387.3 M | 70% | $271.1 M | $116.2 M |
| Residual signalling / train control | $13.5 M | 80% | $10.8 M | $2.7 M |
| Charging microgrids | $23.8 M | 55% | $13.1 M | $10.7 M |
| EPC / project services | $136.9 M | 45% | $61.6 M | $75.3 M |
| Shared national trainset factory | $83.3 M | 25% | $20.8 M | $62.5 M |
| **Total** | **$2.48 B** | **45.1%** | **$1.12 B** | **$1.36 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Lyon](Lyon/README.md) | 1,436,354 | 347 | $2.39 B | 45.8% | $1.10 B | $1.30 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `FR`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

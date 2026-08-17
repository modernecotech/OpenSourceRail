# Philippines national OpenSourceRail strategy

Philippines should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 1,827,000 |
| Trainsets across city plans | 329 |
| Vehicle/car modules to manufacture | 1,316 |
| City infrastructure + fleet CAPEX | $2.35 B |
| One shared national trainset factory | $79.0 M |
| National factory sizing basis | 1,316 modules: largest single-city programme (Davao) |
| **Total national programme CAPEX** | **$2.44 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **23.8%** | **$580.1 M** | **$116.0 M / yr** |
| **Local capital for domestic value** | **76.2%** | **$1.86 B** | **$371.4 M / yr** |
| planned local-currency bond issuance | 61.0% of total | $1.49 B | $297.1 M / yr |
| local public equity / other domestic funding | 15.2% of total | $371.4 M | $74.3 M / yr |
| **Total capital programme** | **100.0%** | **$2.44 B** | **$487.4 M / yr** |

The annual construction draw is spread evenly over 5 planning years. Post-grace annual debt service is $33.2 M for external import finance plus $104.9 M for local bonds, or **$138.1 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$192.5 M per year**.

## Foreign-company turnkey comparison

This controlled comparison is an editable sensitivity, not a supplier quotation. It uses the same national network, fleet, service, and energy scope, with 90% of a foreign contractor's price assumed to require foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price.

| Case | Cost multiplier vs OSR | Foreign-company total CAPEX | Foreign-company external capital | OSR external capital saved | Annual external capital saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $3.66 B | $3.29 B | $2.71 B (82.4%) | $542.0 M / yr |
| **Default** | 2.00× | $4.87 B | $4.39 B | $3.81 B (86.8%) | $761.4 M / yr |
| High | 3.00× | $7.31 B | $6.58 B | $6.00 B (91.2%) | $1.20 B / yr |

At the default 2.00× case, the OSR programme reduces external capital from $4.39 B to $580.1 M, a saving of **$3.81 B (86.8%)**. Total programme CAPEX is 50.0% below the comparator. Replace both variables with scope-normalized bids before investment approval.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $998.2 M | 15% | $149.7 M | $848.5 M |
| Stations | $467.7 M | 20% | $93.5 M | $374.2 M |
| Depots | $8.0 M | 25% | $2.0 M | $6.0 M |
| Rolling stock | $368.5 M | 35% | $129.0 M | $239.5 M |
| Dedicated solar plants | $334.6 M | 45% | $150.6 M | $184.0 M |
| Residual signalling / train control | $14.0 M | 50% | $7.0 M | $7.0 M |
| Charging microgrids | $29.7 M | 40% | $11.9 M | $17.8 M |
| EPC / project services | $137.6 M | 15% | $20.6 M | $116.9 M |
| Shared national trainset factory | $79.0 M | 20% | $15.8 M | $63.2 M |
| **Total** | **$2.44 B** | **23.8%** | **$580.1 M** | **$1.86 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | OSR external capital | Foreign-turnkey external capital (default) | External capital saved | Local capital |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Davao](Davao/README.md) | 1,827,000 | 329 | $2.35 B | 24.0% | $563.5 M | $4.23 B | $3.67 B | $1.79 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The foreign-turnkey multiplier and external share are illustrative variables, not received bids or named-vendor prices. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `PH`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

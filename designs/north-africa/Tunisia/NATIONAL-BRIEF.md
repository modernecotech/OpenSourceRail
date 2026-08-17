# Tunisia national OpenSourceRail strategy

Tunisia should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 2,900,000 |
| Trainsets across city plans | 255 |
| Vehicle/car modules to manufacture | 1,020 |
| City infrastructure + fleet CAPEX | $1.91 B |
| One shared national trainset factory | $61.2 M |
| National factory sizing basis | 1,020 modules: largest single-city programme (Tunis) |
| **Total national programme CAPEX** | **$1.98 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **23.0%** | **$453.9 M** | **$90.8 M / yr** |
| **Local capital for domestic value** | **77.0%** | **$1.52 B** | **$304.5 M / yr** |
| planned local-currency bond issuance | 61.6% of total | $1.22 B | $243.6 M / yr |
| local public equity / other domestic funding | 15.4% of total | $304.5 M | $60.9 M / yr |
| **Total capital programme** | **100.0%** | **$1.98 B** | **$395.3 M / yr** |

The annual construction draw is spread evenly over 5 planning years. Post-grace annual debt service is $26.0 M for external import finance plus $115.3 M for local bonds, or **$141.3 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$190.9 M per year**.

## Foreign-company turnkey comparison

This controlled comparison is an editable sensitivity, not a supplier quotation. It uses the same national network, fleet, service, and energy scope, with 90% of a foreign contractor's price assumed to require foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price.

| Case | Cost multiplier vs OSR | Foreign-company total CAPEX | Foreign-company external capital | OSR external capital saved | Annual external capital saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $2.96 B | $2.67 B | $2.21 B (83.0%) | $442.8 M / yr |
| **Default** | 2.00× | $3.95 B | $3.56 B | $3.10 B (87.2%) | $620.7 M / yr |
| High | 3.00× | $5.93 B | $5.34 B | $4.88 B (91.5%) | $976.4 M / yr |

At the default 2.00× case, the OSR programme reduces external capital from $3.56 B to $453.9 M, a saving of **$3.10 B (87.2%)**. Total programme CAPEX is 50.0% below the comparator. Replace both variables with scope-normalized bids before investment approval.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $845.8 M | 15% | $126.9 M | $718.9 M |
| Stations | $404.9 M | 20% | $81.0 M | $323.9 M |
| Depots | $8.0 M | 25% | $2.0 M | $6.0 M |
| Rolling stock | $285.6 M | 35% | $100.0 M | $185.6 M |
| Dedicated solar plants | $222.3 M | 45% | $100.0 M | $122.3 M |
| Residual signalling / train control | $11.1 M | 50% | $5.5 M | $5.5 M |
| Charging microgrids | $22.7 M | 40% | $9.1 M | $13.6 M |
| EPC / project services | $114.7 M | 15% | $17.2 M | $97.5 M |
| Shared national trainset factory | $61.2 M | 20% | $12.2 M | $49.0 M |
| **Total** | **$1.98 B** | **23.0%** | **$453.9 M** | **$1.52 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | OSR external capital | Foreign-turnkey external capital (default) | External capital saved | Local capital |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Tunis](Tunis/README.md) | 2,900,000 | 255 | $1.91 B | 23.1% | $441.0 M | $3.44 B | $3.00 B | $1.47 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The foreign-turnkey multiplier and external share are illustrative variables, not received bids or named-vendor prices. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `TN`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

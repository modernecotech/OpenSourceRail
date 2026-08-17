# Niger national OpenSourceRail strategy

Niger should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 1,407,635 |
| Trainsets across city plans | 186 |
| Vehicle/car modules to manufacture | 744 |
| City infrastructure + fleet CAPEX | $1.43 B |
| One shared national trainset factory | $44.6 M |
| National factory sizing basis | 744 modules: largest single-city programme (Niamey) |
| **Total national programme CAPEX** | **$1.48 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **22.3%** | **$328.5 M** | **$32.8 M / yr** |
| **Local capital for domestic value** | **77.7%** | **$1.15 B** | **$114.7 M / yr** |
| planned local-currency bond issuance | 62.2% of total | $917.6 M | $91.8 M / yr |
| local public equity / other domestic funding | 15.5% of total | $229.4 M | $22.9 M / yr |
| **Total capital programme** | **100.0%** | **$1.48 B** | **$147.6 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $20.2 M for external import finance plus $89.3 M for local bonds, or **$109.5 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$120.3 M per year**.

## Foreign-company turnkey comparison

This controlled comparison is an editable sensitivity, not a supplier quotation. It uses the same national network, fleet, service, and energy scope, with 90% of a foreign contractor's price assumed to require foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price.

| Case | Cost multiplier vs OSR | Foreign-company total CAPEX | Foreign-company external capital | OSR external capital saved | Annual external capital saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $2.21 B | $1.99 B | $1.66 B (83.5%) | $166.3 M / yr |
| **Default** | 2.00× | $2.95 B | $2.66 B | $2.33 B (87.6%) | $232.7 M / yr |
| High | 3.00× | $4.43 B | $3.98 B | $3.66 B (91.8%) | $365.5 M / yr |

At the default 2.00× case, the OSR programme reduces external capital from $2.66 B to $328.5 M, a saving of **$2.33 B (87.6%)**. Total programme CAPEX is 50.0% below the comparator. Replace both variables with scope-normalized bids before investment approval.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $644.1 M | 15% | $96.6 M | $547.5 M |
| Stations | $327.0 M | 20% | $65.4 M | $261.6 M |
| Depots | $8.0 M | 25% | $2.0 M | $6.0 M |
| Rolling stock | $208.3 M | 35% | $72.9 M | $135.4 M |
| Dedicated solar plants | $129.6 M | 45% | $58.3 M | $71.3 M |
| Residual signalling / train control | $7.9 M | 50% | $3.9 M | $3.9 M |
| Charging microgrids | $17.9 M | 40% | $7.2 M | $10.8 M |
| EPC / project services | $88.1 M | 15% | $13.2 M | $74.8 M |
| Shared national trainset factory | $44.6 M | 20% | $8.9 M | $35.7 M |
| **Total** | **$1.48 B** | **22.3%** | **$328.5 M** | **$1.15 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | OSR external capital | Foreign-turnkey external capital (default) | External capital saved | Local capital |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Niamey](Niamey/README.md) | 1,407,635 | 186 | $1.43 B | 22.3% | $319.1 M | $2.57 B | $2.25 B | $1.11 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The foreign-turnkey multiplier and external share are illustrative variables, not received bids or named-vendor prices. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `NE`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

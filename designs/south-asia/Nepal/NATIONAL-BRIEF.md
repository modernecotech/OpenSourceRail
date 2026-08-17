# Nepal national OpenSourceRail strategy

Nepal should implement OpenSourceRail as one national industrial and financing programme covering the 3 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 3 |
| Served population represented | 2,342,000 |
| Trainsets across city plans | 483 |
| Vehicle/car modules to manufacture | 1,626 |
| City infrastructure + fleet CAPEX | $3.18 B |
| One shared national trainset factory | $58.6 M |
| National factory sizing basis | 976 modules: largest single-city programme (Kathmandu) |
| **Total national programme CAPEX** | **$3.24 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **22.6%** | **$733.3 M** | **$104.8 M / yr** |
| **Local capital for domestic value** | **77.4%** | **$2.51 B** | **$358.3 M / yr** |
| planned local-currency bond issuance | 61.9% of total | $2.01 B | $286.6 M / yr |
| local public equity / other domestic funding | 15.5% of total | $501.6 M | $71.7 M / yr |
| **Total capital programme** | **100.0%** | **$3.24 B** | **$463.0 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $43.1 M for external import finance plus $165.7 M for local bonds, or **$208.8 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$255.1 M per year**.

## Foreign-company turnkey comparison

This controlled comparison is an editable sensitivity, not a supplier quotation. It uses the same national network, fleet, service, and energy scope, with 90% of a foreign contractor's price assumed to require foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price.

| Case | Cost multiplier vs OSR | Foreign-company total CAPEX | Foreign-company external capital | OSR external capital saved | Annual external capital saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $4.86 B | $4.38 B | $3.64 B (83.2%) | $520.3 M / yr |
| **Default** | 2.00× | $6.48 B | $5.83 B | $5.10 B (87.4%) | $728.7 M / yr |
| High | 3.00× | $9.72 B | $8.75 B | $8.02 B (91.6%) | $1.15 B / yr |

At the default 2.00× case, the OSR programme reduces external capital from $5.83 B to $733.3 M, a saving of **$5.10 B (87.4%)**. Total programme CAPEX is 50.0% below the comparator. Replace both variables with scope-normalized bids before investment approval.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $1.50 B | 15% | $224.5 M | $1.27 B |
| Stations | $612.2 M | 20% | $122.4 M | $489.8 M |
| Depots | $24.0 M | 25% | $6.0 M | $18.0 M |
| Rolling stock | $465.6 M | 35% | $163.0 M | $302.6 M |
| Dedicated solar plants | $354.5 M | 45% | $159.5 M | $195.0 M |
| Residual signalling / train control | $15.5 M | 50% | $7.8 M | $7.8 M |
| Charging microgrids | $25.0 M | 40% | $10.0 M | $15.0 M |
| EPC / project services | $188.9 M | 15% | $28.3 M | $160.5 M |
| Shared national trainset factory | $58.6 M | 20% | $11.7 M | $46.8 M |
| **Total** | **$3.24 B** | **22.6%** | **$733.3 M** | **$2.51 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | OSR external capital | Foreign-turnkey external capital (default) | External capital saved | Local capital |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Kathmandu](Kathmandu/README.md) | 1,442,000 | 244 | $2.00 B | 23.4% | $467.7 M | $3.60 B | $3.13 B | $1.53 B |
| [Pokhara](Pokhara/README.md) | 600,000 | 172 | $680.7 M | 23.6% | $160.8 M | $1.23 B | $1.06 B | $519.9 M |
| [Biratnagar](Biratnagar/README.md) | 300,000 | 67 | $500.1 M | 18.5% | $92.5 M | $900.1 M | $807.6 M | $407.6 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The foreign-turnkey multiplier and external share are illustrative variables, not received bids or named-vendor prices. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `NP`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

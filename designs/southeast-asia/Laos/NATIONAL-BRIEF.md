# Laos national OpenSourceRail strategy

Laos should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 948,000 |
| Trainsets across city plans | 155 |
| Vehicle/car modules to manufacture | 465 |
| City infrastructure + fleet CAPEX | $621.9 M |
| One shared national trainset factory | $27.9 M |
| National factory sizing basis | 465 modules: largest single-city programme (Vientiane) |
| **Total national programme CAPEX** | **$651.7 M** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **24.2%** | **$157.8 M** | **$22.5 M / yr** |
| **Local capital for domestic value** | **75.8%** | **$493.9 M** | **$70.6 M / yr** |
| planned local-currency bond issuance | 60.6% of total | $395.1 M | $56.4 M / yr |
| local public equity / other domestic funding | 15.2% of total | $98.8 M | $14.1 M / yr |
| **Total capital programme** | **100.0%** | **$651.7 M** | **$93.1 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $9.3 M for external import finance plus $43.1 M for local bonds, or **$52.4 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$62.7 M per year**.

## Foreign-company turnkey comparison

This controlled comparison is an editable sensitivity, not a supplier quotation. It uses the same national network, fleet, service, and energy scope, with 90% of a foreign contractor's price assumed to require foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price.

| Case | Cost multiplier vs OSR | Foreign-company total CAPEX | Foreign-company external capital | OSR external capital saved | Annual external capital saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $977.6 M | $879.9 M | $722.0 M (82.1%) | $103.1 M / yr |
| **Default** | 2.00× | $1.30 B | $1.17 B | $1.02 B (86.5%) | $145.0 M / yr |
| High | 3.00× | $1.96 B | $1.76 B | $1.60 B (91.0%) | $228.8 M / yr |

At the default 2.00× case, the OSR programme reduces external capital from $1.17 B to $157.8 M, a saving of **$1.02 B (86.5%)**. Total programme CAPEX is 50.0% below the comparator. Replace both variables with scope-normalized bids before investment approval.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $245.0 M | 15% | $36.7 M | $208.2 M |
| Stations | $112.6 M | 20% | $22.5 M | $90.1 M |
| Depots | $8.0 M | 25% | $2.0 M | $6.0 M |
| Rolling stock | $139.5 M | 35% | $48.8 M | $90.7 M |
| Dedicated solar plants | $74.4 M | 45% | $33.5 M | $40.9 M |
| Residual signalling / train control | $3.7 M | 50% | $1.9 M | $1.9 M |
| Charging microgrids | $2.8 M | 40% | $1.1 M | $1.7 M |
| EPC / project services | $37.8 M | 15% | $5.7 M | $32.1 M |
| Shared national trainset factory | $27.9 M | 20% | $5.6 M | $22.3 M |
| **Total** | **$651.7 M** | **24.2%** | **$157.8 M** | **$493.9 M** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | OSR external capital | Foreign-turnkey external capital (default) | External capital saved | Local capital |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Vientiane](Vientiane/README.md) | 948,000 | 155 | $621.9 M | 24.4% | $152.0 M | $1.12 B | $967.4 M | $469.9 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The foreign-turnkey multiplier and external share are illustrative variables, not received bids or named-vendor prices. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `LA`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

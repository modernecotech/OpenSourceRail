# Myanmar national OpenSourceRail strategy

Myanmar should implement OpenSourceRail as one national industrial and financing programme covering the 2 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 2 |
| Served population represented | 6,926,000 |
| Trainsets across city plans | 937 |
| Vehicle/car modules to manufacture | 5,070 |
| City infrastructure + fleet CAPEX | $6.76 B |
| One shared national trainset factory | $238.0 M |
| National factory sizing basis | 3,966 modules: largest single-city programme (Yangon) |
| **Total national programme CAPEX** | **$7.01 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **24.9%** | **$1.74 B** | **$174.5 M / yr** |
| **Local capital for domestic value** | **75.1%** | **$5.27 B** | **$526.7 M / yr** |
| planned local-currency bond issuance | 60.1% of total | $4.21 B | $421.3 M / yr |
| local public equity / other domestic funding | 15.0% of total | $1.05 B | $105.3 M / yr |
| **Total capital programme** | **100.0%** | **$7.01 B** | **$701.1 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $107.1 M for external import finance plus $562.1 M for local bonds, or **$669.2 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$731.6 M per year**.

## Foreign-company turnkey comparison

This controlled comparison is an editable sensitivity, not a supplier quotation. It uses the same national network, fleet, service, and energy scope, with 90% of a foreign contractor's price assumed to require foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price.

| Case | Cost multiplier vs OSR | Foreign-company total CAPEX | Foreign-company external capital | OSR external capital saved | Annual external capital saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $10.52 B | $9.47 B | $7.72 B (81.6%) | $772.1 M / yr |
| **Default** | 2.00× | $14.02 B | $12.62 B | $10.88 B (86.2%) | $1.09 B / yr |
| High | 3.00× | $21.03 B | $18.93 B | $17.19 B (90.8%) | $1.72 B / yr |

At the default 2.00× case, the OSR programme reduces external capital from $12.62 B to $1.74 B, a saving of **$10.88 B (86.2%)**. Total programme CAPEX is 50.0% below the comparator. Replace both variables with scope-normalized bids before investment approval.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $2.67 B | 15% | $399.8 M | $2.27 B |
| Stations | $1.15 B | 20% | $229.3 M | $917.2 M |
| Depots | $16.0 M | 25% | $4.0 M | $12.0 M |
| Rolling stock | $1.42 B | 35% | $496.9 M | $922.7 M |
| Dedicated solar plants | $1.03 B | 45% | $462.8 M | $565.6 M |
| Residual signalling / train control | $32.0 M | 50% | $16.0 M | $16.0 M |
| Charging microgrids | $74.5 M | 40% | $29.8 M | $44.7 M |
| EPC / project services | $391.4 M | 15% | $58.7 M | $332.7 M |
| Shared national trainset factory | $238.0 M | 20% | $47.6 M | $190.4 M |
| **Total** | **$7.01 B** | **24.9%** | **$1.74 B** | **$5.27 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | OSR external capital | Foreign-turnkey external capital (default) | External capital saved | Local capital |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Yangon](Yangon/README.md) | 5,200,000 | 661 | $4.66 B | 26.4% | $1.23 B | $8.38 B | $7.15 B | $3.43 B |
| [Mandalay](Mandalay/README.md) | 1,726,000 | 276 | $2.10 B | 22.3% | $467.4 M | $3.78 B | $3.31 B | $1.63 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The foreign-turnkey multiplier and external share are illustrative variables, not received bids or named-vendor prices. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `MM`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

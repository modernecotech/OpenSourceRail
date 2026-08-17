# Ecuador national OpenSourceRail strategy

Ecuador should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 817,100 |
| Trainsets across city plans | 169 |
| Vehicle/car modules to manufacture | 507 |
| City infrastructure + fleet CAPEX | $586.4 M |
| One shared national trainset factory | $30.4 M |
| National factory sizing basis | 507 modules: largest single-city programme (Cuenca) |
| **Total national programme CAPEX** | **$618.9 M** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **24.8%** | **$153.2 M** | **$30.6 M / yr** |
| **Local capital for domestic value** | **75.2%** | **$465.7 M** | **$93.1 M / yr** |
| planned local-currency bond issuance | 60.2% of total | $372.5 M | $74.5 M / yr |
| local public equity / other domestic funding | 15.0% of total | $93.1 M | $18.6 M / yr |
| **Total capital programme** | **100.0%** | **$618.9 M** | **$123.8 M / yr** |

The annual construction draw is spread evenly over 5 planning years. Post-grace annual debt service is $8.8 M for external import finance plus $36.9 M for local bonds, or **$45.7 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$60.9 M per year**.

## Foreign-company turnkey comparison

This controlled comparison is an editable sensitivity, not a supplier quotation. It uses the same national network, fleet, service, and energy scope, with 90% of a foreign contractor's price assumed to require foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price.

| Case | Cost multiplier vs OSR | Foreign-company total CAPEX | Foreign-company external capital | OSR external capital saved | Annual external capital saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $928.4 M | $835.5 M | $682.3 M (81.7%) | $136.5 M / yr |
| **Default** | 2.00× | $1.24 B | $1.11 B | $960.8 M (86.2%) | $192.2 M / yr |
| High | 3.00× | $1.86 B | $1.67 B | $1.52 B (90.8%) | $303.6 M / yr |

At the default 2.00× case, the OSR programme reduces external capital from $1.11 B to $153.2 M, a saving of **$960.8 M (86.2%)**. Total programme CAPEX is 50.0% below the comparator. Replace both variables with scope-normalized bids before investment approval.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $229.5 M | 15% | $34.4 M | $195.1 M |
| Stations | $85.4 M | 20% | $17.1 M | $68.3 M |
| Depots | $8.0 M | 25% | $2.0 M | $6.0 M |
| Rolling stock | $152.1 M | 35% | $53.2 M | $98.9 M |
| Dedicated solar plants | $72.0 M | 45% | $32.4 M | $39.6 M |
| Residual signalling / train control | $3.5 M | 50% | $1.8 M | $1.8 M |
| Charging microgrids | $2.1 M | 40% | $860 k | $1.3 M |
| EPC / project services | $35.8 M | 15% | $5.4 M | $30.4 M |
| Shared national trainset factory | $30.4 M | 20% | $6.1 M | $24.3 M |
| **Total** | **$618.9 M** | **24.8%** | **$153.2 M** | **$465.7 M** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | OSR external capital | Foreign-turnkey external capital (default) | External capital saved | Local capital |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Cuenca](Cuenca/README.md) | 817,100 | 169 | $586.4 M | 25.0% | $146.8 M | $1.06 B | $908.6 M | $439.5 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The foreign-turnkey multiplier and external share are illustrative variables, not received bids or named-vendor prices. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `EC`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

# Senegal national OpenSourceRail strategy

Senegal should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 4,030,000 |
| Trainsets across city plans | 330 |
| Vehicle/car modules to manufacture | 1,980 |
| City infrastructure + fleet CAPEX | $2.30 B |
| One shared national trainset factory | $118.8 M |
| National factory sizing basis | 1,980 modules: largest single-city programme (Dakar) |
| **Total national programme CAPEX** | **$2.42 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **24.9%** | **$603.8 M** | **$86.3 M / yr** |
| **Local capital for domestic value** | **75.1%** | **$1.82 B** | **$259.8 M / yr** |
| planned local-currency bond issuance | 60.1% of total | $1.46 B | $207.9 M / yr |
| local public equity / other domestic funding | 15.0% of total | $363.8 M | $52.0 M / yr |
| **Total capital programme** | **100.0%** | **$2.42 B** | **$346.1 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $35.5 M for external import finance plus $132.7 M for local bonds, or **$168.1 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$202.8 M per year**.

## Foreign-company turnkey comparison

This controlled comparison is an editable sensitivity, not a supplier quotation. It uses the same national network, fleet, service, and energy scope, with 90% of a foreign contractor's price assumed to require foreign currency or international capital. Illustrative variable benchmark for an equivalent foreign-company turnkey delivery. It excludes tunnels, land, tax/duty, utility relocation, financing fees, and escalation on both sides; it does not represent a received bid or named vendor price.

| Case | Cost multiplier vs OSR | Foreign-company total CAPEX | Foreign-company external capital | OSR external capital saved | Annual external capital saved |
|---|---:|---:|---:|---:|---:|
| Low | 1.50× | $3.63 B | $3.27 B | $2.67 B (81.5%) | $381.0 M / yr |
| **Default** | 2.00× | $4.85 B | $4.36 B | $3.76 B (86.2%) | $536.7 M / yr |
| High | 3.00× | $7.27 B | $6.54 B | $5.94 B (90.8%) | $848.2 M / yr |

At the default 2.00× case, the OSR programme reduces external capital from $4.36 B to $603.8 M, a saving of **$3.76 B (86.2%)**. Total programme CAPEX is 50.0% below the comparator. Replace both variables with scope-normalized bids before investment approval.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $834.7 M | 15% | $125.2 M | $709.5 M |
| Stations | $425.4 M | 20% | $85.1 M | $340.3 M |
| Depots | $8.0 M | 25% | $2.0 M | $6.0 M |
| Rolling stock | $554.4 M | 35% | $194.0 M | $360.4 M |
| Dedicated solar plants | $297.2 M | 45% | $133.7 M | $163.5 M |
| Residual signalling / train control | $11.1 M | 50% | $5.6 M | $5.6 M |
| Charging microgrids | $33.9 M | 40% | $13.6 M | $20.3 M |
| EPC / project services | $139.0 M | 15% | $20.9 M | $118.2 M |
| Shared national trainset factory | $118.8 M | 20% | $23.8 M | $95.0 M |
| **Total** | **$2.42 B** | **24.9%** | **$603.8 M** | **$1.82 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | OSR external capital | Foreign-turnkey external capital (default) | External capital saved | Local capital |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Dakar](Dakar/README.md) | 4,030,000 | 330 | $2.30 B | 25.2% | $578.8 M | $4.13 B | $3.55 B | $1.72 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The foreign-turnkey multiplier and external share are illustrative variables, not received bids or named-vendor prices. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `SN`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

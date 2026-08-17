# Guinea national OpenSourceRail strategy

Guinea should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 2,010,000 |
| Trainsets across city plans | 84 |
| Vehicle/car modules to manufacture | 336 |
| City infrastructure + fleet CAPEX | $635.0 M |
| One shared national trainset factory | $20.2 M |
| National factory sizing basis | 336 modules: largest single-city programme (Conakry) |
| **Total national programme CAPEX** | **$656.5 M** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **44.3%** | **$290.6 M** | **$29.1 M / yr** |
| **Local capital for domestic value** | **55.7%** | **$365.9 M** | **$36.6 M / yr** |
| planned local-currency bond issuance | 44.6% of total | $292.7 M | $29.3 M / yr |
| local public equity / other domestic funding | 11.1% of total | $73.2 M | $7.3 M / yr |
| **Total capital programme** | **100.0%** | **$656.5 M** | **$65.7 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $17.8 M for external import finance plus $31.1 M for local bonds, or **$48.9 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$49.7 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $283.3 M | 35% | $99.2 M | $184.1 M |
| Stations | $113.5 M | 40% | $45.4 M | $68.1 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $94.1 M | 55% | $51.7 M | $42.3 M |
| Dedicated solar plants | $87.6 M | 70% | $61.3 M | $26.3 M |
| Residual signalling / train control | $4.1 M | 80% | $3.3 M | $820 k |
| Charging microgrids | $8.6 M | 55% | $4.7 M | $3.8 M |
| EPC / project services | $37.2 M | 45% | $16.7 M | $20.5 M |
| Shared national trainset factory | $20.2 M | 25% | $5.0 M | $15.1 M |
| **Total** | **$656.5 M** | **44.3%** | **$290.6 M** | **$365.9 M** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Conakry](Conakry/README.md) | 2,010,000 | 84 | $635.0 M | 44.9% | $284.9 M | $350.0 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `GN`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

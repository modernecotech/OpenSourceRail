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
| **External capital for imports** | **42.8%** | **$631.7 M** | **$63.2 M / yr** |
| **Local capital for domestic value** | **57.2%** | **$843.8 M** | **$84.4 M / yr** |
| planned local-currency bond issuance | 45.8% of total | $675.1 M | $67.5 M / yr |
| local public equity / other domestic funding | 11.4% of total | $168.8 M | $16.9 M / yr |
| **Total capital programme** | **100.0%** | **$1.48 B** | **$147.6 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $38.8 M for external import finance plus $65.7 M for local bonds, or **$104.5 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$106.1 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $644.1 M | 35% | $225.4 M | $418.7 M |
| Stations | $327.0 M | 40% | $130.8 M | $196.2 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $208.3 M | 55% | $114.6 M | $93.7 M |
| Dedicated solar plants | $129.6 M | 70% | $90.7 M | $38.9 M |
| Residual signalling / train control | $7.9 M | 80% | $6.3 M | $1.6 M |
| Charging microgrids | $17.9 M | 55% | $9.9 M | $8.1 M |
| EPC / project services | $88.1 M | 45% | $39.6 M | $48.4 M |
| Shared national trainset factory | $44.6 M | 25% | $11.2 M | $33.5 M |
| **Total** | **$1.48 B** | **42.8%** | **$631.7 M** | **$843.8 M** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Niamey](Niamey/README.md) | 1,407,635 | 186 | $1.43 B | 43.4% | $619.1 M | $808.6 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `NE`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

# Zambia national OpenSourceRail strategy

Zambia should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 3,037,000 |
| Trainsets across city plans | 418 |
| Vehicle/car modules to manufacture | 2,508 |
| City infrastructure + fleet CAPEX | $3.00 B |
| One shared national trainset factory | $150.5 M |
| National factory sizing basis | 2,508 modules: largest single-city programme (Lusaka) |
| **Total national programme CAPEX** | **$3.16 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **46.6%** | **$1.47 B** | **$210.6 M / yr** |
| **Local capital for domestic value** | **53.4%** | **$1.69 B** | **$240.9 M / yr** |
| planned local-currency bond issuance | 42.7% of total | $1.35 B | $192.7 M / yr |
| local public equity / other domestic funding | 10.7% of total | $337.3 M | $48.2 M / yr |
| **Total capital programme** | **100.0%** | **$3.16 B** | **$451.5 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $86.6 M for external import finance plus $224.1 M for local bonds, or **$310.7 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$337.2 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $1.05 B | 35% | $366.1 M | $679.8 M |
| Stations | $498.3 M | 40% | $199.3 M | $299.0 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $702.2 M | 55% | $386.2 M | $316.0 M |
| Dedicated solar plants | $532.0 M | 70% | $372.4 M | $159.6 M |
| Residual signalling / train control | $14.0 M | 80% | $11.2 M | $2.8 M |
| Charging microgrids | $37.9 M | 55% | $20.8 M | $17.1 M |
| EPC / project services | $172.0 M | 45% | $77.4 M | $94.6 M |
| Shared national trainset factory | $150.5 M | 25% | $37.6 M | $112.9 M |
| **Total** | **$3.16 B** | **46.6%** | **$1.47 B** | **$1.69 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Lusaka](Lusaka/README.md) | 3,037,000 | 418 | $3.00 B | 47.7% | $1.43 B | $1.57 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `ZM`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

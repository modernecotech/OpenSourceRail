# Burkina Faso national OpenSourceRail strategy

Burkina Faso should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 2,531,000 |
| Trainsets across city plans | 271 |
| Vehicle/car modules to manufacture | 1,084 |
| City infrastructure + fleet CAPEX | $1.85 B |
| One shared national trainset factory | $65.0 M |
| National factory sizing basis | 1,084 modules: largest single-city programme (Ouagadougou) |
| **Total national programme CAPEX** | **$1.92 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **43.5%** | **$832.6 M** | **$83.3 M / yr** |
| **Local capital for domestic value** | **56.5%** | **$1.08 B** | **$108.3 M / yr** |
| planned local-currency bond issuance | 45.2% of total | $866.6 M | $86.7 M / yr |
| local public equity / other domestic funding | 11.3% of total | $216.6 M | $21.7 M / yr |
| **Total capital programme** | **100.0%** | **$1.92 B** | **$191.6 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $51.1 M for external import finance plus $88.1 M for local bonds, or **$139.2 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$141.5 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $803.4 M | 35% | $281.2 M | $522.2 M |
| Stations | $397.8 M | 40% | $159.1 M | $238.7 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $303.5 M | 55% | $166.9 M | $136.6 M |
| Dedicated solar plants | $190.0 M | 70% | $133.0 M | $57.0 M |
| Residual signalling / train control | $11.1 M | 80% | $8.9 M | $2.2 M |
| Charging microgrids | $24.1 M | 55% | $13.2 M | $10.8 M |
| EPC / project services | $112.9 M | 45% | $50.8 M | $62.1 M |
| Shared national trainset factory | $65.0 M | 25% | $16.3 M | $48.8 M |
| **Total** | **$1.92 B** | **43.5%** | **$832.6 M** | **$1.08 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Ouagadougou](Ouagadougou/README.md) | 2,531,000 | 271 | $1.85 B | 44.1% | $814.3 M | $1.03 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `BF`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

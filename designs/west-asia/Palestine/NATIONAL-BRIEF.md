# Palestine national OpenSourceRail strategy

Palestine should implement OpenSourceRail as one national industrial and financing programme covering the 3 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 3 |
| Served population represented | 1,850,000 |
| Trainsets across city plans | 385 |
| Vehicle/car modules to manufacture | 1,155 |
| City infrastructure + fleet CAPEX | $1.45 B |
| One shared national trainset factory | $31.3 M |
| National factory sizing basis | 522 modules: largest single-city programme (Nablus) |
| **Total national programme CAPEX** | **$1.49 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **44.8%** | **$665.0 M** | **$95.0 M / yr** |
| **Local capital for domestic value** | **55.2%** | **$820.5 M** | **$117.2 M / yr** |
| planned local-currency bond issuance | 44.2% of total | $656.4 M | $93.8 M / yr |
| local public equity / other domestic funding | 11.0% of total | $164.1 M | $23.4 M / yr |
| **Total capital programme** | **100.0%** | **$1.49 B** | **$212.2 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $39.1 M for external import finance plus $59.8 M for local bonds, or **$98.9 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$109.2 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $572.0 M | 35% | $200.2 M | $371.8 M |
| Stations | $264.8 M | 40% | $105.9 M | $158.9 M |
| Depots | $24.0 M | 40% | $9.6 M | $14.4 M |
| Rolling stock | $346.5 M | 55% | $190.6 M | $155.9 M |
| Dedicated solar plants | $144.7 M | 70% | $101.3 M | $43.4 M |
| Residual signalling / train control | $8.5 M | 80% | $6.8 M | $1.7 M |
| Charging microgrids | $6.0 M | 55% | $3.3 M | $2.7 M |
| EPC / project services | $87.7 M | 45% | $39.5 M | $48.2 M |
| Shared national trainset factory | $31.3 M | 25% | $7.8 M | $23.5 M |
| **Total** | **$1.49 B** | **44.8%** | **$665.0 M** | **$820.5 M** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Hebron](Hebron/README.md) | 800,000 | 127 | $507.4 M | 45.0% | $228.5 M | $278.9 M |
| [Gaza City](Gaza-City/README.md) | 600,000 | 84 | $353.7 M | 44.4% | $157.0 M | $196.7 M |
| [Nablus](Nablus/README.md) | 450,000 | 174 | $590.9 M | 45.8% | $270.6 M | $320.3 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `PS`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

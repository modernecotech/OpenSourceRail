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
| **External capital for imports** | **45.3%** | **$1.10 B** | **$156.9 M / yr** |
| **Local capital for domestic value** | **54.7%** | **$1.32 B** | **$189.2 M / yr** |
| planned local-currency bond issuance | 43.7% of total | $1.06 B | $151.4 M / yr |
| local public equity / other domestic funding | 10.9% of total | $264.9 M | $37.8 M / yr |
| **Total capital programme** | **100.0%** | **$2.42 B** | **$346.1 M / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $64.5 M for external import finance plus $96.6 M for local bonds, or **$161.1 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$177.3 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $834.7 M | 35% | $292.2 M | $542.6 M |
| Stations | $425.4 M | 40% | $170.2 M | $255.2 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $554.4 M | 55% | $304.9 M | $249.5 M |
| Dedicated solar plants | $297.2 M | 70% | $208.1 M | $89.2 M |
| Residual signalling / train control | $11.1 M | 80% | $8.9 M | $2.2 M |
| Charging microgrids | $33.9 M | 55% | $18.6 M | $15.3 M |
| EPC / project services | $139.0 M | 45% | $62.6 M | $76.5 M |
| Shared national trainset factory | $118.8 M | 25% | $29.7 M | $89.1 M |
| **Total** | **$2.42 B** | **45.3%** | **$1.10 B** | **$1.32 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Dakar](Dakar/README.md) | 4,030,000 | 330 | $2.30 B | 46.4% | $1.06 B | $1.23 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `SN`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

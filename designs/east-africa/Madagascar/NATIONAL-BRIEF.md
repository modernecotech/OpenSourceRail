# Madagascar national OpenSourceRail strategy

Madagascar should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 3,058,000 |
| Trainsets across city plans | 504 |
| Vehicle/car modules to manufacture | 3,024 |
| City infrastructure + fleet CAPEX | $3.64 B |
| One shared national trainset factory | $181.4 M |
| National factory sizing basis | 3,024 modules: largest single-city programme (Antananarivo) |
| **Total national programme CAPEX** | **$3.83 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **46.4%** | **$1.78 B** | **$177.8 M / yr** |
| **Local capital for domestic value** | **53.6%** | **$2.06 B** | **$205.5 M / yr** |
| planned local-currency bond issuance | 42.9% of total | $1.64 B | $164.4 M / yr |
| local public equity / other domestic funding | 10.7% of total | $411.1 M | $41.1 M / yr |
| **Total capital programme** | **100.0%** | **$3.83 B** | **$383.3 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $109.1 M for external import finance plus $189.1 M for local bonds, or **$298.3 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$302.0 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $1.38 B | 35% | $481.5 M | $894.2 M |
| Stations | $521.8 M | 40% | $208.7 M | $313.1 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $846.7 M | 55% | $465.7 M | $381.0 M |
| Dedicated solar plants | $636.4 M | 70% | $445.5 M | $190.9 M |
| Residual signalling / train control | $16.2 M | 80% | $13.0 M | $3.2 M |
| Charging microgrids | $37.7 M | 55% | $20.7 M | $17.0 M |
| EPC / project services | $209.1 M | 45% | $94.1 M | $115.0 M |
| Shared national trainset factory | $181.4 M | 25% | $45.4 M | $136.1 M |
| **Total** | **$3.83 B** | **46.4%** | **$1.78 B** | **$2.06 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Antananarivo](Antananarivo/README.md) | 3,058,000 | 504 | $3.64 B | 47.4% | $1.73 B | $1.91 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `MG`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

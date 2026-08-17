# Mozambique national OpenSourceRail strategy

Mozambique should implement OpenSourceRail as one national industrial and financing programme covering the 10 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 10 |
| Served population represented | 5,015,000 |
| Trainsets across city plans | 849 |
| Vehicle/car modules to manufacture | 2,530 |
| City infrastructure + fleet CAPEX | $4.20 B |
| One shared national trainset factory | $51.4 M |
| National factory sizing basis | 856 modules: largest single-city programme (Maputo) |
| **Total national programme CAPEX** | **$4.25 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **43.9%** | **$1.87 B** | **$186.6 M / yr** |
| **Local capital for domestic value** | **56.1%** | **$2.39 B** | **$238.7 M / yr** |
| planned local-currency bond issuance | 44.9% of total | $1.91 B | $191.0 M / yr |
| local public equity / other domestic funding | 11.2% of total | $477.5 M | $47.7 M / yr |
| **Total capital programme** | **100.0%** | **$4.25 B** | **$425.4 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $114.6 M for external import finance plus $263.8 M for local bonds, or **$378.3 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$389.6 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $1.76 B | 35% | $614.9 M | $1.14 B |
| Stations | $913.0 M | 40% | $365.2 M | $547.8 M |
| Depots | $80.0 M | 40% | $32.0 M | $48.0 M |
| Rolling stock | $732.6 M | 55% | $403.0 M | $329.7 M |
| Dedicated solar plants | $411.8 M | 70% | $288.3 M | $123.5 M |
| Residual signalling / train control | $23.1 M | 80% | $18.5 M | $4.6 M |
| Charging microgrids | $33.5 M | 55% | $18.4 M | $15.1 M |
| EPC / project services | $251.3 M | 45% | $113.1 M | $138.2 M |
| Shared national trainset factory | $51.4 M | 25% | $12.8 M | $38.5 M |
| **Total** | **$4.25 B** | **43.9%** | **$1.87 B** | **$2.39 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Maputo](Maputo/README.md) | 1,530,000 | 214 | $1.58 B | 44.7% | $708.2 M | $875.1 M |
| [Nampula](Nampula/README.md) | 800,000 | 122 | $447.4 M | 45.7% | $204.6 M | $242.8 M |
| [Beira](Beira/README.md) | 535,000 | 96 | $396.4 M | 45.2% | $179.0 M | $217.3 M |
| [Chimoio](Chimoio/README.md) | 400,000 | 82 | $309.7 M | 45.3% | $140.4 M | $169.3 M |
| [Quelimane](Quelimane/README.md) | 350,000 | 23 | $94.5 M | 44.2% | $41.8 M | $52.8 M |
| [Tete](Tete/README.md) | 350,000 | 81 | $419.5 M | 42.2% | $176.8 M | $242.6 M |
| [Nacala](Nacala/README.md) | 300,000 | 81 | $320.5 M | 42.6% | $136.7 M | $183.8 M |
| [Lichinga](Lichinga/README.md) | 250,000 | 34 | $160.7 M | 41.4% | $66.5 M | $94.2 M |
| [Pemba Mz](Pemba-Mz/README.md) | 250,000 | 69 | $291.0 M | 42.2% | $122.7 M | $168.3 M |
| [Xai Xai](Xai-Xai/README.md) | 250,000 | 47 | $175.7 M | 42.7% | $75.0 M | $100.8 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `MZ`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

# Jordan national OpenSourceRail strategy

Jordan should implement OpenSourceRail as one national industrial and financing programme covering the 4 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 4 |
| Served population represented | 5,557,000 |
| Trainsets across city plans | 960 |
| Vehicle/car modules to manufacture | 4,474 |
| City infrastructure + fleet CAPEX | $5.52 B |
| One shared national trainset factory | $199.8 M |
| National factory sizing basis | 3,330 modules: largest single-city programme (Amman) |
| **Total national programme CAPEX** | **$5.73 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **45.0%** | **$2.58 B** | **$515.6 M / yr** |
| **Local capital for domestic value** | **55.0%** | **$3.15 B** | **$630.4 M / yr** |
| planned local-currency bond issuance | 44.0% of total | $2.52 B | $504.3 M / yr |
| local public equity / other domestic funding | 11.0% of total | $630.4 M | $126.1 M / yr |
| **Total capital programme** | **100.0%** | **$5.73 B** | **$1.15 B / yr** |

The annual construction draw is spread evenly over 5 planning years. Post-grace annual debt service is $147.6 M for external import finance plus $205.5 M for local bonds, or **$353.1 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$431.2 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $2.16 B | 35% | $756.8 M | $1.41 B |
| Stations | $990.2 M | 40% | $396.1 M | $594.1 M |
| Depots | $32.0 M | 40% | $12.8 M | $19.2 M |
| Rolling stock | $1.27 B | 55% | $700.0 M | $572.7 M |
| Dedicated solar plants | $659.9 M | 70% | $461.9 M | $198.0 M |
| Residual signalling / train control | $25.7 M | 80% | $20.6 M | $5.1 M |
| Charging microgrids | $55.8 M | 55% | $30.7 M | $25.1 M |
| EPC / project services | $331.7 M | 45% | $149.3 M | $182.4 M |
| Shared national trainset factory | $199.8 M | 25% | $50.0 M | $149.8 M |
| **Total** | **$5.73 B** | **45.0%** | **$2.58 B** | **$3.15 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Amman](Amman/README.md) | 4,007,000 | 555 | $4.01 B | 46.4% | $1.86 B | $2.15 B |
| [Zarqa](Zarqa/README.md) | 700,000 | 227 | $783.8 M | 44.3% | $347.2 M | $436.6 M |
| [Irbid](Irbid/README.md) | 600,000 | 107 | $402.6 M | 45.3% | $182.3 M | $220.3 M |
| [Aqaba](Aqaba/README.md) | 250,000 | 71 | $321.4 M | 41.5% | $133.5 M | $187.9 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `JO`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

# DR Congo national OpenSourceRail strategy

DR Congo should implement OpenSourceRail as one national industrial and financing programme covering the 7 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 7 |
| Served population represented | 27,007,000 |
| Trainsets across city plans | 1,280 |
| Vehicle/car modules to manufacture | 6,151 |
| City infrastructure + fleet CAPEX | $8.62 B |
| One shared national trainset factory | $231.5 M |
| National factory sizing basis | 3,858 modules: largest single-city programme (Kinshasa) |
| **Total national programme CAPEX** | **$8.87 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **45.7%** | **$4.05 B** | **$405.1 M / yr** |
| **Local capital for domestic value** | **54.3%** | **$4.82 B** | **$481.8 M / yr** |
| planned local-currency bond issuance | 43.5% of total | $3.85 B | $385.4 M / yr |
| local public equity / other domestic funding | 10.9% of total | $963.6 M | $96.4 M / yr |
| **Total capital programme** | **100.0%** | **$8.87 B** | **$886.9 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $248.7 M for external import finance plus $514.2 M for local bonds, or **$762.9 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$779.7 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $3.25 B | 35% | $1.14 B | $2.11 B |
| Stations | $1.68 B | 40% | $673.2 M | $1.01 B |
| Depots | $56.0 M | 40% | $22.4 M | $33.6 M |
| Rolling stock | $1.74 B | 55% | $955.7 M | $781.9 M |
| Dedicated solar plants | $1.27 B | 70% | $892.5 M | $382.5 M |
| Residual signalling / train control | $42.9 M | 80% | $34.3 M | $8.6 M |
| Charging microgrids | $100.4 M | 55% | $55.2 M | $45.2 M |
| EPC / project services | $496.8 M | 45% | $223.6 M | $273.2 M |
| Shared national trainset factory | $231.5 M | 25% | $57.9 M | $173.6 M |
| **Total** | **$8.87 B** | **45.7%** | **$4.05 B** | **$4.82 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Kinshasa](Kinshasa/README.md) | 17,178,000 | 643 | $4.61 B | 47.6% | $2.19 B | $2.42 B |
| [Lubumbashi](Lubumbashi/README.md) | 2,829,000 | 161 | $1.08 B | 45.2% | $490.2 M | $594.7 M |
| [Mbuji Mayi](Mbuji-Mayi/README.md) | 2,500,000 | 135 | $1.14 B | 44.1% | $502.8 M | $638.1 M |
| [Kisangani](Kisangani/README.md) | 1,300,000 | 50 | $432.6 M | 43.9% | $189.8 M | $242.8 M |
| [Kananga](Kananga/README.md) | 1,200,000 | 36 | $319.7 M | 43.6% | $139.2 M | $180.4 M |
| [Bukavu](Bukavu/README.md) | 1,000,000 | 130 | $505.3 M | 45.7% | $231.0 M | $274.3 M |
| [Goma](Goma/README.md) | 1,000,000 | 125 | $529.5 M | 45.2% | $239.4 M | $290.1 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `CD`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

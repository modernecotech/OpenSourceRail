# Nigeria national OpenSourceRail strategy

Nigeria should implement OpenSourceRail as one national industrial and financing programme covering the 10 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 10 |
| Served population represented | 19,200,000 |
| Trainsets across city plans | 2,078 |
| Vehicle/car modules to manufacture | 9,756 |
| City infrastructure + fleet CAPEX | $14.32 B |
| One shared national trainset factory | $247.0 M |
| National factory sizing basis | 4,116 modules: largest single-city programme (Kano) |
| **Total national programme CAPEX** | **$14.58 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **44.8%** | **$6.53 B** | **$932.3 M / yr** |
| **Local capital for domestic value** | **55.2%** | **$8.05 B** | **$1.15 B / yr** |
| planned local-currency bond issuance | 44.2% of total | $6.44 B | $920.5 M / yr |
| local public equity / other domestic funding | 11.0% of total | $1.61 B | $230.1 M / yr |
| **Total capital programme** | **100.0%** | **$14.58 B** | **$2.08 B / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $383.4 M for external import finance plus $883.4 M for local bonds, or **$1.27 B per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$1.39 B per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $5.99 B | 35% | $2.09 B | $3.89 B |
| Stations | $2.70 B | 40% | $1.08 B | $1.62 B |
| Depots | $80.0 M | 40% | $32.0 M | $48.0 M |
| Rolling stock | $2.75 B | 55% | $1.51 B | $1.24 B |
| Dedicated solar plants | $1.74 B | 70% | $1.22 B | $523.4 M |
| Residual signalling / train control | $70.6 M | 80% | $56.5 M | $14.1 M |
| Charging microgrids | $155.0 M | 55% | $85.3 M | $69.8 M |
| EPC / project services | $839.7 M | 45% | $377.9 M | $461.8 M |
| Shared national trainset factory | $247.0 M | 25% | $61.7 M | $185.2 M |
| **Total** | **$14.58 B** | **44.8%** | **$6.53 B** | **$8.05 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Kano](Kano/README.md) | 4,200,000 | 686 | $4.71 B | 46.3% | $2.18 B | $2.53 B |
| [Ibadan](Ibadan/README.md) | 3,900,000 | 222 | $1.67 B | 46.8% | $782.9 M | $889.4 M |
| [Port Harcourt](Port-Harcourt/README.md) | 3,000,000 | 232 | $1.83 B | 44.3% | $809.9 M | $1.02 B |
| [Benin City](Benin-City/README.md) | 1,800,000 | 171 | $1.27 B | 44.4% | $562.4 M | $704.5 M |
| [Onitsha](Onitsha/README.md) | 1,500,000 | 198 | $1.62 B | 44.3% | $714.8 M | $900.3 M |
| [Maiduguri](Maiduguri/README.md) | 1,200,000 | 197 | $1.63 B | 42.7% | $697.5 M | $937.0 M |
| [Ilorin](Ilorin/README.md) | 1,000,000 | 124 | $535.4 M | 44.8% | $239.6 M | $295.8 M |
| [Aba Ng](Aba-Ng/README.md) | 900,000 | 70 | $299.8 M | 44.8% | $134.2 M | $165.6 M |
| [Jos](Jos/README.md) | 900,000 | 102 | $417.8 M | 43.9% | $183.4 M | $234.4 M |
| [Uyo](Uyo/README.md) | 800,000 | 76 | $334.6 M | 44.5% | $149.0 M | $185.7 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `NG`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

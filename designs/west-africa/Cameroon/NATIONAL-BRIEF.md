# Cameroon national OpenSourceRail strategy

Cameroon should implement OpenSourceRail as one national industrial and financing programme covering the 10 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 10 |
| Served population represented | 11,650,000 |
| Trainsets across city plans | 1,326 |
| Vehicle/car modules to manufacture | 5,860 |
| City infrastructure + fleet CAPEX | $7.66 B |
| One shared national trainset factory | $115.9 M |
| National factory sizing basis | 1,932 modules: largest single-city programme (Douala) |
| **Total national programme CAPEX** | **$7.79 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **45.8%** | **$3.57 B** | **$510.0 M / yr** |
| **Local capital for domestic value** | **54.2%** | **$4.22 B** | **$602.5 M / yr** |
| planned local-currency bond issuance | 43.3% of total | $3.37 B | $482.0 M / yr |
| local public equity / other domestic funding | 10.8% of total | $843.5 M | $120.5 M / yr |
| **Total capital programme** | **100.0%** | **$7.79 B** | **$1.11 B / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $209.7 M for external import finance plus $307.6 M for local bonds, or **$517.3 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$567.9 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $2.94 B | 35% | $1.03 B | $1.91 B |
| Stations | $1.36 B | 40% | $543.0 M | $814.6 M |
| Depots | $80.0 M | 40% | $32.0 M | $48.0 M |
| Rolling stock | $1.68 B | 55% | $924.6 M | $756.5 M |
| Dedicated solar plants | $1.06 B | 70% | $745.2 M | $319.4 M |
| Residual signalling / train control | $37.5 M | 80% | $30.0 M | $7.5 M |
| Charging microgrids | $71.5 M | 55% | $39.3 M | $32.2 M |
| EPC / project services | $439.8 M | 45% | $197.9 M | $241.9 M |
| Shared national trainset factory | $115.9 M | 25% | $29.0 M | $86.9 M |
| **Total** | **$7.79 B** | **45.8%** | **$3.57 B** | **$4.22 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Yaounde](Yaounde/README.md) | 4,100,000 | 312 | $2.26 B | 47.7% | $1.08 B | $1.18 B |
| [Douala](Douala/README.md) | 3,900,000 | 322 | $2.54 B | 46.6% | $1.18 B | $1.36 B |
| [Bafoussam](Bafoussam/README.md) | 600,000 | 158 | $580.5 M | 46.2% | $268.0 M | $312.5 M |
| [Bamenda](Bamenda/README.md) | 600,000 | 111 | $428.9 M | 45.8% | $196.4 M | $232.5 M |
| [Garoua](Garoua/README.md) | 600,000 | 73 | $348.5 M | 42.7% | $148.8 M | $199.7 M |
| [Maroua](Maroua/README.md) | 500,000 | 113 | $488.4 M | 43.7% | $213.3 M | $275.1 M |
| [Kumba](Kumba/README.md) | 400,000 | 90 | $356.2 M | 45.6% | $162.5 M | $193.7 M |
| [Bertoua](Bertoua/README.md) | 350,000 | 63 | $285.8 M | 44.5% | $127.2 M | $158.6 M |
| [Ngaoundere](Ngaoundere/README.md) | 350,000 | 64 | $300.4 M | 43.2% | $129.7 M | $170.6 M |
| [Edea](Edea/README.md) | 250,000 | 20 | $77.5 M | 41.6% | $32.3 M | $45.3 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `CM`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

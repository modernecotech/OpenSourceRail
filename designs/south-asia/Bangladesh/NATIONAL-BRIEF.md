# Bangladesh national OpenSourceRail strategy

Bangladesh should implement OpenSourceRail as one national industrial and financing programme covering the 10 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 10 |
| Served population represented | 13,550,000 |
| Trainsets across city plans | 1,901 |
| Vehicle/car modules to manufacture | 7,844 |
| City infrastructure + fleet CAPEX | $11.72 B |
| One shared national trainset factory | $186.1 M |
| National factory sizing basis | 3,102 modules: largest single-city programme (Chittagong) |
| **Total national programme CAPEX** | **$11.91 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **45.1%** | **$5.37 B** | **$767.4 M / yr** |
| **Local capital for domestic value** | **54.9%** | **$6.54 B** | **$934.6 M / yr** |
| planned local-currency bond issuance | 43.9% of total | $5.23 B | $747.7 M / yr |
| local public equity / other domestic funding | 11.0% of total | $1.31 B | $186.9 M / yr |
| **Total capital programme** | **100.0%** | **$11.91 B** | **$1.70 B / yr** |

The annual construction draw is spread evenly over 7 planning years. Post-grace annual debt service is $315.6 M for external import finance plus $477.2 M for local bonds, or **$792.8 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$873.5 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $4.90 B | 35% | $1.72 B | $3.19 B |
| Stations | $2.10 B | 40% | $839.8 M | $1.26 B |
| Depots | $80.0 M | 40% | $32.0 M | $48.0 M |
| Rolling stock | $2.24 B | 55% | $1.23 B | $1.01 B |
| Dedicated solar plants | $1.57 B | 70% | $1.10 B | $470.4 M |
| Residual signalling / train control | $57.9 M | 80% | $46.3 M | $11.6 M |
| Charging microgrids | $101.1 M | 55% | $55.6 M | $45.5 M |
| EPC / project services | $676.9 M | 45% | $304.6 M | $372.3 M |
| Shared national trainset factory | $186.1 M | 25% | $46.5 M | $139.6 M |
| **Total** | **$11.91 B** | **45.1%** | **$5.37 B** | **$6.54 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Chittagong](Chittagong/README.md) | 5,200,000 | 517 | $3.72 B | 47.4% | $1.76 B | $1.96 B |
| [Khulna](Khulna/README.md) | 1,500,000 | 252 | $1.95 B | 44.2% | $863.1 M | $1.09 B |
| [Gazipur](Gazipur/README.md) | 1,400,000 | 338 | $2.48 B | 44.8% | $1.11 B | $1.37 B |
| [Narayanganj](Narayanganj/README.md) | 950,000 | 157 | $711.3 M | 44.4% | $316.1 M | $395.2 M |
| [Rajshahi](Rajshahi/README.md) | 950,000 | 93 | $437.2 M | 44.2% | $193.3 M | $243.8 M |
| [Sylhet](Sylhet/README.md) | 900,000 | 109 | $436.0 M | 45.3% | $197.4 M | $238.6 M |
| [Rangpur](Rangpur/README.md) | 800,000 | 99 | $411.9 M | 45.1% | $185.9 M | $225.9 M |
| [Mymensingh](Mymensingh/README.md) | 700,000 | 92 | $510.1 M | 42.6% | $217.5 M | $292.6 M |
| [Comilla](Comilla/README.md) | 600,000 | 114 | $472.7 M | 45.3% | $214.3 M | $258.4 M |
| [Barisal](Barisal/README.md) | 550,000 | 130 | $579.3 M | 44.5% | $257.5 M | $321.8 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `BD`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

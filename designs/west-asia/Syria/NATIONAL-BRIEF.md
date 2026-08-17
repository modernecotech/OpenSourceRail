# Syria national OpenSourceRail strategy

Syria should implement OpenSourceRail as one national industrial and financing programme covering the 9 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 9 |
| Served population represented | 7,617,000 |
| Trainsets across city plans | 1,124 |
| Vehicle/car modules to manufacture | 3,700 |
| City infrastructure + fleet CAPEX | $6.07 B |
| One shared national trainset factory | $56.6 M |
| National factory sizing basis | 944 modules: largest single-city programme (Damascus) |
| **Total national programme CAPEX** | **$6.13 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **43.8%** | **$2.69 B** | **$268.8 M / yr** |
| **Local capital for domestic value** | **56.2%** | **$3.44 B** | **$344.4 M / yr** |
| planned local-currency bond issuance | 44.9% of total | $2.76 B | $275.5 M / yr |
| local public equity / other domestic funding | 11.2% of total | $688.8 M | $68.9 M / yr |
| **Total capital programme** | **100.0%** | **$6.13 B** | **$613.2 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $165.0 M for external import finance plus $553.4 M for local bonds, or **$718.4 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$740.9 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $2.56 B | 35% | $895.6 M | $1.66 B |
| Stations | $1.35 B | 40% | $541.4 M | $812.0 M |
| Depots | $72.0 M | 40% | $28.8 M | $43.2 M |
| Rolling stock | $1.07 B | 55% | $587.7 M | $480.8 M |
| Dedicated solar plants | $572.5 M | 70% | $400.8 M | $171.8 M |
| Residual signalling / train control | $33.8 M | 80% | $27.0 M | $6.8 M |
| Charging microgrids | $52.5 M | 55% | $28.9 M | $23.6 M |
| EPC / project services | $363.7 M | 45% | $163.7 M | $200.0 M |
| Shared national trainset factory | $56.6 M | 25% | $14.2 M | $42.5 M |
| **Total** | **$6.13 B** | **43.8%** | **$2.69 B** | **$3.44 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Damascus](Damascus/README.md) | 2,503,000 | 236 | $1.76 B | 43.9% | $771.3 M | $987.5 M |
| [Aleppo](Aleppo/README.md) | 1,639,000 | 219 | $1.68 B | 44.1% | $739.7 M | $938.4 M |
| [Homs](Homs/README.md) | 775,000 | 87 | $380.1 M | 44.2% | $168.0 M | $212.1 M |
| [Latakia](Latakia/README.md) | 700,000 | 93 | $364.1 M | 45.1% | $164.2 M | $200.0 M |
| [Hama](Hama/README.md) | 600,000 | 114 | $433.2 M | 44.8% | $194.1 M | $239.1 M |
| [Deir Ez Zor](Deir-Ez-Zor/README.md) | 500,000 | 143 | $524.8 M | 44.3% | $232.3 M | $292.5 M |
| [Raqqa](Raqqa/README.md) | 350,000 | 105 | $424.4 M | 44.5% | $188.7 M | $235.7 M |
| [Idlib](Idlib/README.md) | 300,000 | 67 | $259.7 M | 42.3% | $109.8 M | $149.9 M |
| [Tartus](Tartus/README.md) | 250,000 | 60 | $247.9 M | 41.9% | $103.9 M | $144.0 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `SY`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

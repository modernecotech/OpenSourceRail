# Angola national OpenSourceRail strategy

Angola should implement OpenSourceRail as one national industrial and financing programme covering the 9 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 9 |
| Served population represented | 13,135,000 |
| Trainsets across city plans | 1,254 |
| Vehicle/car modules to manufacture | 5,481 |
| City infrastructure + fleet CAPEX | $6.81 B |
| One shared national trainset factory | $223.9 M |
| National factory sizing basis | 3,732 modules: largest single-city programme (Luanda) |
| **Total national programme CAPEX** | **$7.05 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **45.8%** | **$3.23 B** | **$645.8 M / yr** |
| **Local capital for domestic value** | **54.2%** | **$3.82 B** | **$764.0 M / yr** |
| planned local-currency bond issuance | 43.4% of total | $3.06 B | $611.2 M / yr |
| local public equity / other domestic funding | 10.8% of total | $764.0 M | $152.8 M / yr |
| **Total capital programme** | **100.0%** | **$7.05 B** | **$1.41 B / yr** |

The annual construction draw is spread evenly over 5 planning years. Post-grace annual debt service is $184.9 M for external import finance plus $359.4 M for local bonds, or **$544.3 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$649.5 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $2.41 B | 35% | $843.8 M | $1.57 B |
| Stations | $1.33 B | 40% | $531.9 M | $797.9 M |
| Depots | $72.0 M | 40% | $28.8 M | $43.2 M |
| Rolling stock | $1.56 B | 55% | $860.1 M | $703.7 M |
| Dedicated solar plants | $952.7 M | 70% | $666.9 M | $285.8 M |
| Residual signalling / train control | $34.1 M | 80% | $27.3 M | $6.8 M |
| Charging microgrids | $63.0 M | 55% | $34.6 M | $28.4 M |
| EPC / project services | $398.8 M | 45% | $179.5 M | $219.3 M |
| Shared national trainset factory | $223.9 M | 25% | $56.0 M | $167.9 M |
| **Total** | **$7.05 B** | **45.8%** | **$3.23 B** | **$3.82 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Luanda](Luanda/README.md) | 9,085,000 | 622 | $4.27 B | 48.1% | $2.05 B | $2.22 B |
| [Huambo](Huambo/README.md) | 800,000 | 112 | $436.9 M | 44.4% | $194.2 M | $242.7 M |
| [Lubango](Lubango/README.md) | 700,000 | 119 | $469.7 M | 44.4% | $208.4 M | $261.3 M |
| [Benguela](Benguela/README.md) | 600,000 | 110 | $419.1 M | 44.5% | $186.7 M | $232.5 M |
| [Lobito](Lobito/README.md) | 500,000 | 83 | $316.8 M | 44.6% | $141.3 M | $175.6 M |
| [Malanje](Malanje/README.md) | 500,000 | 34 | $172.3 M | 43.4% | $74.7 M | $97.6 M |
| [Uige](Uige/README.md) | 400,000 | 27 | $103.4 M | 44.7% | $46.2 M | $57.1 M |
| [Namibe](Namibe/README.md) | 300,000 | 84 | $304.4 M | 42.2% | $128.6 M | $175.9 M |
| [Soyo](Soyo/README.md) | 250,000 | 63 | $314.5 M | 41.6% | $130.8 M | $183.7 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `AO`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

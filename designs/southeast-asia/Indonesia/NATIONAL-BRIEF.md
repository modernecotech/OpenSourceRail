# Indonesia national OpenSourceRail strategy

Indonesia should implement OpenSourceRail as one national industrial and financing programme covering the 2 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 2 |
| Served population represented | 5,624,000 |
| Trainsets across city plans | 782 |
| Vehicle/car modules to manufacture | 4,068 |
| City infrastructure + fleet CAPEX | $6.05 B |
| One shared national trainset factory | $169.2 M |
| National factory sizing basis | 2,820 modules: largest single-city programme (Surabaya) |
| **Total national programme CAPEX** | **$6.23 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **45.3%** | **$2.82 B** | **$563.9 M / yr** |
| **Local capital for domestic value** | **54.7%** | **$3.41 B** | **$682.2 M / yr** |
| planned local-currency bond issuance | 43.8% of total | $2.73 B | $545.7 M / yr |
| local public equity / other domestic funding | 10.9% of total | $682.2 M | $136.4 M / yr |
| **Total capital programme** | **100.0%** | **$6.23 B** | **$1.25 B / yr** |

The annual construction draw is spread evenly over 5 planning years. Post-grace annual debt service is $161.5 M for external import finance plus $203.9 M for local bonds, or **$365.4 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$446.1 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $2.39 B | 35% | $837.3 M | $1.55 B |
| Stations | $1.19 B | 40% | $476.8 M | $715.1 M |
| Depots | $16.0 M | 40% | $6.4 M | $9.6 M |
| Rolling stock | $1.14 B | 55% | $626.5 M | $512.6 M |
| Dedicated solar plants | $876.7 M | 70% | $613.7 M | $263.0 M |
| Residual signalling / train control | $27.0 M | 80% | $21.6 M | $5.4 M |
| Charging microgrids | $68.3 M | 55% | $37.6 M | $30.8 M |
| EPC / project services | $350.3 M | 45% | $157.6 M | $192.6 M |
| Shared national trainset factory | $169.2 M | 25% | $42.3 M | $126.9 M |
| **Total** | **$6.23 B** | **45.3%** | **$2.82 B** | **$3.41 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Surabaya](Surabaya/README.md) | 3,009,000 | 470 | $3.63 B | 46.8% | $1.70 B | $1.93 B |
| [Bandung](Bandung/README.md) | 2,615,000 | 312 | $2.42 B | 44.3% | $1.07 B | $1.35 B |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `ID`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

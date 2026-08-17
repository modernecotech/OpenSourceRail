# Somalia national OpenSourceRail strategy

Somalia should implement OpenSourceRail as one national industrial and financing programme covering the 1 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 1 |
| Served population represented | 2,610,000 |
| Trainsets across city plans | 149 |
| Vehicle/car modules to manufacture | 596 |
| City infrastructure + fleet CAPEX | $1.13 B |
| One shared national trainset factory | $35.8 M |
| National factory sizing basis | 596 modules: largest single-city programme (Mogadishu) |
| **Total national programme CAPEX** | **$1.17 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **43.1%** | **$505.5 M** | **$50.6 M / yr** |
| **Local capital for domestic value** | **56.9%** | **$667.3 M** | **$66.7 M / yr** |
| planned local-currency bond issuance | 45.5% of total | $533.9 M | $53.4 M / yr |
| local public equity / other domestic funding | 11.4% of total | $133.5 M | $13.3 M / yr |
| **Total capital programme** | **100.0%** | **$1.17 B** | **$117.3 M / yr** |

The annual construction draw is spread evenly over 10 planning years. Post-grace annual debt service is $31.0 M for external import finance plus $81.3 M for local bonds, or **$112.3 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$116.2 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $467.1 M | 35% | $163.5 M | $303.6 M |
| Stations | $297.9 M | 40% | $119.2 M | $178.7 M |
| Depots | $8.0 M | 40% | $3.2 M | $4.8 M |
| Rolling stock | $166.9 M | 55% | $91.8 M | $75.1 M |
| Dedicated solar plants | $106.4 M | 70% | $74.5 M | $31.9 M |
| Residual signalling / train control | $6.0 M | 80% | $4.8 M | $1.2 M |
| Charging microgrids | $15.0 M | 55% | $8.3 M | $6.7 M |
| EPC / project services | $69.8 M | 45% | $31.4 M | $38.4 M |
| Shared national trainset factory | $35.8 M | 25% | $8.9 M | $26.8 M |
| **Total** | **$1.17 B** | **43.1%** | **$505.5 M** | **$667.3 M** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Mogadishu](Mogadishu/README.md) | 2,610,000 | 149 | $1.13 B | 43.7% | $495.4 M | $639.1 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `SO`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

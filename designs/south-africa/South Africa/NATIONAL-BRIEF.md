# South Africa national OpenSourceRail strategy

South Africa should implement OpenSourceRail as one national industrial and financing programme covering the 5 catalogue cities below, rather than as disconnected city projects. One centrally governed trainset factory builds the shared modular fleet in phases; city and regional contractors fabricate and install rails, viaducts, stations, depots, and local civil works. This concentrates scarce imported machinery, specialist tooling, engineering support, and foreign currency in one reusable national asset while maximizing domestic labour, materials, fabrication, and local-currency financing.

## National programme at a glance

| Measure | National planning value |
|---|---:|
| Cities in catalogue | 5 |
| Served population represented | 6,200,000 |
| Trainsets across city plans | 1,096 |
| Vehicle/car modules to manufacture | 5,056 |
| City infrastructure + fleet CAPEX | $6.72 B |
| One shared national trainset factory | $221.8 M |
| National factory sizing basis | 3,696 modules: largest single-city programme (Durban) |
| **Total national programme CAPEX** | **$6.96 B** |

The factory is sized to the largest single-city fleet programme and reused through a phased national rollout. This avoids duplicating factory buildings, moulds, welding fixtures, metrology, commissioning equipment, and imported machinery in every city. Final factory siting requires a national freight, power, workforce, land, and test-track study; this brief does not preselect a city.

## External versus local capital

Imported content is the minimum foreign-currency or international-capital requirement. Local content is the domestic funding envelope and can be raised through local-currency infrastructure bonds, public equity, pension/insurance capital, land-value capture, or other domestic sources.

| Capital boundary | Share | Total | Annual draw during construction |
|---|---:|---:|---:|
| **External capital for imports** | **45.8%** | **$3.18 B** | **$636.8 M / yr** |
| **Local capital for domestic value** | **54.2%** | **$3.78 B** | **$755.0 M / yr** |
| planned local-currency bond issuance | 43.4% of total | $3.02 B | $604.0 M / yr |
| local public equity / other domestic funding | 10.8% of total | $755.0 M | $151.0 M / yr |
| **Total capital programme** | **100.0%** | **$6.96 B** | **$1.39 B / yr** |

The annual construction draw is spread evenly over 5 planning years. Post-grace annual debt service is $182.4 M for external import finance plus $327.0 M for local bonds, or **$509.4 M per year** before railway operating cash flow. During construction, interest plus the local public-equity draw is **$611.4 M per year**.

## Procurement-origin composition

| CAPEX bucket | Total | Imported share | External capital | Local value |
|---|---:|---:|---:|---:|
| Civil works | $2.47 B | 35% | $865.9 M | $1.61 B |
| Stations | $1.30 B | 40% | $519.3 M | $779.0 M |
| Depots | $40.0 M | 40% | $16.0 M | $24.0 M |
| Rolling stock | $1.44 B | 55% | $791.8 M | $647.9 M |
| Dedicated solar plants | $999.1 M | 70% | $699.4 M | $299.7 M |
| Residual signalling / train control | $31.5 M | 80% | $25.2 M | $6.3 M |
| Charging microgrids | $64.8 M | 55% | $35.6 M | $29.2 M |
| EPC / project services | $389.9 M | 45% | $175.5 M | $214.5 M |
| Shared national trainset factory | $221.8 M | 25% | $55.4 M | $166.3 M |
| **Total** | **$6.96 B** | **45.8%** | **$3.18 B** | **$3.78 B** |

## City programme

Each city CAPEX below excludes the national factory. Its imported share varies with the local mix of civil structures, rolling stock, stations, charging, signalling, and solar infrastructure.

| City | Population | Fleet | City CAPEX | Imported % | External capital | Local capital |
|---|---:|---:|---:|---:|---:|---:|
| [Durban](Durban/README.md) | 3,900,000 | 616 | $4.77 B | 47.0% | $2.24 B | $2.53 B |
| [East London Za](East-London-Za/README.md) | 800,000 | 139 | $577.5 M | 45.8% | $264.5 M | $313.0 M |
| [Bloemfontein](Bloemfontein/README.md) | 600,000 | 151 | $653.0 M | 45.6% | $298.1 M | $354.9 M |
| [Polokwane](Polokwane/README.md) | 600,000 | 110 | $406.6 M | 44.9% | $182.6 M | $224.0 M |
| [Nelspruit](Nelspruit/README.md) | 300,000 | 80 | $312.4 M | 42.7% | $133.4 M | $179.0 M |

## National implementation sequence

1. Establish one national programme authority, common technical baseline, procurement-origin register, and local-content verification method.
2. Procure the shared trainset-factory machinery and first-article imported kits once; qualify domestic steel, composites, wiring, interiors, and assembly.
3. Launch city civil packages in parallel where local contractor capacity allows, using standardized rail, viaduct, station, depot, and charging interfaces.
4. Sequence trainset production through the national factory by opening date, reusing fixtures and commissioning capability between cities.
5. Issue local-currency bonds against the domestic-value programme and reserve international borrowing or foreign exchange for the imported-value schedule.
6. Update these planning shares with supplier quotations, customs/tax treatment, country capability audits, and a signed financing plan before procurement.

## Basis and limitations

This is a planning strategy, not a financing commitment or supplier-origin audit. Imported shares come from `lib/templates/capex-costs.toml`; city geometry, fleet, and cost data come from each generated `design.toml` and scenario. The model excludes tax/duty, FX paths, land acquisition, utility relocation, and country-specific supplier qualification until controlled evidence exists.

Generated by `scripts/generate-national-briefs.py` for `ZA`. Controlled imported-share keys: charging_microgrid, civil, depots, epc_overhead, production_plant, rolling_stock, signalling, solar_plant, stations.

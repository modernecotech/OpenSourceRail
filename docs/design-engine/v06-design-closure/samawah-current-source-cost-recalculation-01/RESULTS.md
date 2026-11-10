# Samawah current-source route and cost comparison

**Result packet:** `current-source-attempt-08`
**Packet ID:** `ea483225f960922029c9db56399e55c113d7297d4c1566bb1e99afa91d71b5ec`
**Cost/model source epoch:** `897e36510812966bcef0e04fddebdd98bedee4af`
**Vehicle candidate/body:** `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3` / `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`

This is a current-source **Samawah planning comparison**, not a completed repricing of Iraq's other 265 city studies. Four city studies were replay-verified: the published route and a new 20 m simplification, each under the local project make/buy case and the repository's internal `china-bulk-buy` case. Every study has the same 14 whole-life cost scopes, each with low/base/high values. None changes the selected vehicle or grants engineering, procurement, manufacturing or operating approval.

## Calculated city totals

Amounts are USD millions. CAPEX is installed capital; NPV is the modeled 30-year whole-life total. These are wide Class C planning estimates, not bids.

| Route and price case | Route km | Trainsets | CAPEX low / base / high | 30-year NPV low / base / high | Base CAPEX per route-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| Published route — project make/buy | 57.873 | 81 | 314.6 / 1,141.5 / 6,857.7 | 629.5 / 2,258.4 / 13,160.5 | $19.72m |
| Published route — China benchmark / forced-purchase sensitivity | 57.873 | 81 | 316.2 / 1,147.3 / 6,881.1 | 632.0 / 2,268.9 / 13,211.5 | $19.82m |
| Simplified route (20 m deviation limit) — project make/buy | 54.608 | 83 | 347.7 / 1,298.7 / 7,878.5 | 655.8 / 2,410.1 / 14,241.4 | $23.78m |
| Simplified route (20 m deviation limit) — China benchmark / forced-purchase sensitivity | 54.608 | 83 | 349.3 / 1,304.7 / 7,902.8 | 658.4 / 2,420.9 / 14,293.9 | $23.89m |

The China case raises base CAPEX by $5.78m (0.51%) on the published route and $5.96m (0.46%) on the simplified route. It is not cheaper under the current inputs.

## Route simplification result

“20 m” is the maximum permitted sampled lateral deviation from the source alignment; it is not the route length. The new geometry was generated from the exact current canonical plan. The prior merged-route packet contributed tolerance context only; its midpoint station, 28.3 m from the current canonical stop, was not copied. All 25 current operational station coordinates remain fixed as route vertices.

The 20 m screen reduced mapped length from 57.873 km to 54.608 km, a 3.265 km (5.64%) decrease, and reduced stored route vertices from 2,633 to 138. The maximum 5 m sampled two-way deviation was 19.345 m in a local spherical azimuthal-equidistant projection.

| Line | Source km | Proposed km | Change km | Vertices, source → proposed | Maximum sampled deviation |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 26.603 | 24.280 | −2.323 | 1,216 → 58 | 19.345 m |
| 2 | 12.753 | 12.135 | −0.618 | 546 → 42 | 19.323 m |
| 3 | 8.789 | 8.585 | −0.204 | 431 → 6 | 18.671 m |
| 4 | 5.444 | 5.360 | −0.084 | 253 → 23 | 18.513 m |
| 5 | 4.284 | 4.248 | −0.035 | 187 → 9 | 19.073 m |

This is an unsurveyed line simplification, not a route selection. It does not test property boundaries, roads, bridges, waterways, utilities, gradient, curve radius, geotechnical conditions, access or construction staging.

## Base-case cost scopes

USD millions; all 14 scope totals are shown so the main cost shifts are visible. The packet's `summary.json` contains exact low/base/high values for every scope and case.

| Scope | Published, make/buy | Published, China sensitivity | 20 m route, make/buy | 20 m route, China sensitivity |
| --- | ---: | ---: | ---: | ---: |
| Construction | 511.57 | 513.07 | 646.43 | 647.98 |
| Disposal | 10.56 | 10.61 | 12.01 | 12.07 |
| Energy | 471.62 | 471.62 | 439.92 | 439.92 |
| Factory/tooling | 10.88 | 9.88 | 10.61 | 9.62 |
| Fleet | 21.47 | 21.77 | 20.46 | 20.77 |
| Guideway | 78.62 | 78.62 | 75.07 | 75.07 |
| Land, utilities and depot | 65.45 | 65.40 | 64.04 | 63.99 |
| Maintenance | 306.56 | 309.14 | 318.84 | 321.48 |
| Operations | 42.22 | 42.22 | 42.22 | 42.22 |
| Recovery | 13.49 | 13.49 | 13.49 | 13.49 |
| Reliability | 19.59 | 19.59 | 18.49 | 18.49 |
| Renewals | 259.52 | 261.62 | 273.02 | 275.18 |
| Rolling stock | 223.65 | 228.68 | 203.55 | 208.70 |
| Stations and power | 223.23 | 223.23 | 271.95 | 271.95 |

This is a joint route-and-service recalculation, not an isolated geometry experiment. Along with the route edit, the study's planning revision changes line 1's propulsion mode from `powered-axle-continuous-research` to `station-launch-reference`; its resulting service calculation changes line 1 from 28 to 33 trainsets. The physical vehicle candidate is held constant, but this configuration change means the route cost delta cannot be attributed to straightening alone.

On the local make/buy basis, the simplified-route scenario increases base CAPEX by $157.25m (13.78%) and base NPV by $151.67m (6.72%); modeled fleet rises by two trainsets overall. The city cost adapter adds a $97.93m base reserve for changed corridor access, right-of-way and unverified crossings because the geometry has no site evidence. The old civil classes are also transferred by route-length proportion and marked for reassessment.

The service calculation itself changes materially: line 1 grows from 28 to 33 total trainsets, while lines 2–3 shrink by six combined. Its final leg has a 589 s modeled run under the simplified route case versus a 332 s conditional run on the published route. The published route's corresponding coast screen says the train stops short of the receiving zone. Neither result has an available-force map or physical journey evidence, so this is a useful warning about the coupled service model, not an operating timetable.

## How to read the China price case

`china-bulk-buy` is the internal adapter name. The defensible description is **China benchmark / forced-purchase sensitivity**:

- China-origin benchmark inputs and assumed landing costs price selected manufactured stock.
- Some civil purchase routes use local-contractor proxies; the scenario is not all-China sourcing.
- The main item groups do not select project-quantity purchase tiers. No negotiated or blanket volume discount is applied.
- The project make/buy case does model city quantities and allocates shared setup/tooling, but it is not a local factory quotation.
- No multi-city order aggregation, signed quote, Incoterm, freight contract, customs quote, or supplier capacity is represented.

So this run corrects the cost totals under the repository's current assumptions, but it does **not** establish the deep volume discounts the project may secure. Those need sourced quantity tiers or an explicitly labeled discount sensitivity, not an assumed saving.

## Reproduction and evidence

- [Sealed comparison packet archive](results/current-source-attempt-08.tar.gz)
- [Packet extraction and verification instructions](results/README.md)
- [Method and reproduction instructions](README.md)

The archive contains the sealed packet and its four complete source-bound city studies. Its root manifest lists 83 files and each city-study manifest lists 20 artifacts. All four studies were replay-verified against source epoch `897e36510812966bcef0e04fddebdd98bedee4af`; exact cached results were reused in the packaging invocation and replayed again. No GIS/CAD/FEM solver or external transaction ran. The source mirror was not OS-sandboxed. The route and price scenarios remain unselected; physical, engineering, manufacturing and operating acceptance flags are false.

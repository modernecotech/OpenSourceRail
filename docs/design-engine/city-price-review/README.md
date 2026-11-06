# City price review — 6 November 2026

All 266 v0.6 city networks have been recalculated. These are complete, internally reconciled outline estimates under declared assumptions. They are not verified local construction budgets or qualified railway designs.

The corrected energy account includes reserve-fleet auxiliaries and charging losses. The accounting horizon and discount rate now follow the declared city policy, including short horizons with an explicitly empty renewal schedule. Named local operating tariff and paid-hour wage estimates can replace their individual accounts without discounting imported equipment or construction.

| City | Route km | Headline capital US$m | 30-year NPV US$m | Separate civil alternative US$m | Interface holds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baghdad | 494.43 | 8,354.56 | 16,025.92 | 7,628.84 | 32 |
| Kut | 53.05 | 1,456.99 | 2,375.37 | 909.47 | 0 |
| Samawah | 57.87 | 1,141.49 | 2,258.43 | 1,071.99 | 1 |

The headline retains the mapped civil classes. The alternative traverses actual selected route coordinates through authenticated historical WorldCover/OSM water masks. Dry legacy bridge allowances become elevated construction plus a nonzero obstruction reserve. Wet at-grade or unsupported interfaces remain explicit holds. Roads, utilities, flooding, soil and clearance requirements are not resolved by a water mask. These figures therefore compare hypotheses; they do not establish savings that can be banked.

Each city page now exposes the price basis, largest capital allowances, electricity scenarios and annual reserve-fleet energy. Its `energy_budget.csv` and `local_cost_inputs.csv` are downloadable. Factory/make-buy, civil, staffing, delivery, fare/funding and geographic outputs remain linked in the city dossier.

The estimates retain the declared China-origin material/finished-supply and calculated local-production routes. Wholesale observations are not finished rail-grade quotations. No additional unsupported bulk discount has been applied. Outside Iraq, transferred rate scenarios remain explicit until scoped local inputs are supplied. Generic 4,000 peak passengers/hour/direction is a planning assumption, not a city demand forecast. Powered-axle research fallbacks are identified separately from the passive station-powered reference.

Reproduce with:

```sh
python -m engineering.outline complete --workers 3 --output /path/to/fresh-run
python -m engineering.outline complete-verify --replay --output /path/to/fresh-run
python tools/automation/report-city-price-review.py --state /path/to/fresh-run --output docs/design-engine/city-price-review
```

[Per-city audit and exact identities](results.json) · [Calculated outline methods](../outline-completion/README.md) · [City dossiers](../city-dossiers/index.json)

Execution manifest: `a79258063c31bd623366a2db2ebe558b0fbe5d190ddc27c6c1acb415a26320ff`. Audit: `e1f114311ee374ead0030fd9afbf833d727f3bb621fdedfc3e4f6b9211631003`. Control: `bf3373473583092fd1a701037b91c3ec79a37cd0`. Full numerical runs, historical source masks and interrupted trials are retained outside the published compact packet; their execution manifests and hashes identify the exact evidence.

Independent verification checked the complete 266-city execution and exactly replayed Baghdad, Kut and Lyon from a fresh evidence cache. The [verification receipt](independent-verification.json) records timing, source hashes and read-only host execution. Across the separate civil alternatives, 949 water/civil interface holds remain open in 112 cities; these do not invalidate their completed planning outlines or qualify the proposed structures.

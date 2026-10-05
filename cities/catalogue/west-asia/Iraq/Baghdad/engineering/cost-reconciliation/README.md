# Baghdad same-alignment cost reconciliation

**Base planning allowance; complete installed price and financing remain unresolved.**

This compares the reviewed `d4cd3db2cd` baseline with the corrected monetary model, on identical controlled routes, stations, fleets and depots. Civil construction-method boundaries now follow local geometry. Route-search scores are excluded from prices.

| Measure | Reviewed baseline | Corrected base case |
|---|---:|---:|
| Programme allowance, USD bn | 15.233 | 8.312 |
| Unfunded support, IQD tn | 27.330 | 0.033 |
| Terminal debt, IQD tn | 13.000 | 11.162 |
| Operating FTE | 3716 | 3716 |
| Loaded annual payroll, IQD bn | 86.303 | 86.303 |

The allowance correction is not a supplier saving, accepted alternative or complete delivery budget. Special/segmental increments, actual foundations, installed grid/charging upgrades, land, utilities and other closure items remain unpriced. Maintenance follows the corrected capital-percentage allowance; physical inspection, replacement and access workloads still require independent quantities and prices. The correction grants no lower staffing, traction duty or surveyed demand requirement.

The original baseline bytes are retained in [the source snapshot](baseline-sources.json.gz), so a fresh shallow checkout can reproduce this comparison offline. Month 101 comparisons in the [source-bound reconciliation](summary.json) annualise one nominal model month, rather than predicting a calendar year. Paid journeys remain capacity-led; no population-to-fare uplift is adopted. The [demand handoff](../demand-bridge/README.md), [energy closure](../delivery-closure/SITE-ENERGY.md), [clearance screen](../clearance/README.md) and [current programme ledger](../programme-recalculation/README.md) retain their separate acceptance gates.

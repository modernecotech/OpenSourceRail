# Baghdad cost correction and subsequent alignment reconciliation

**Base planning allowance; complete installed price and financing remain unresolved.**

The original `d4cd3db2cd` monetary correction is verified against the retained same-alignment `a1a14f6d29` reference. The current design subsequently changed controlled fields lines, stations, fleets, depots. The latest values below therefore include separately recorded alignment effects; they are not all attributed to a same-geometry price correction. Route-search scores remain excluded from prices.

| Measure | Reviewed baseline | Corrected base case |
|---|---:|---:|
| Programme allowance, USD bn | 15.233 | 19.407 |
| Unfunded support, IQD tn | 27.330 | 0.000 |
| Terminal debt, IQD tn | 13.000 | 0.000 |
| Operating FTE | 3716 | 11459 |
| Loaded annual payroll, IQD bn | 86.303 | 264.730 |

The allowance correction is not a supplier saving, accepted alternative or complete delivery budget. Special/segmental increments, actual foundations, installed grid/charging upgrades, land, utilities and other closure items remain unpriced. Maintenance follows the corrected capital-percentage allowance; physical inspection, replacement and access workloads still require independent quantities and prices. The correction grants no lower staffing, traction duty or surveyed demand requirement.

The same-alignment corrected reference capital is USD 8.312371bn; the current alignment changes it by USD 11,094,282,084.15 in the unquoted model. The current route is 863.9238 km against 479.0124 km in that reference. [The retained corrected snapshot](../../../../../../../engineering/network-planning/baghdad/corrected-alignment-sources.json.gz) preserves the original stage when an alignment revision exists; its bytes are also in the companion planning archive.

The original baseline bytes are retained in [the source snapshot](baseline-sources.json.gz), so a fresh shallow checkout can reproduce this comparison offline. Month 101 comparisons in the [source-bound reconciliation](summary.json) annualise one nominal model month, rather than predicting a calendar year. Paid journeys remain capacity-led; no population-to-fare uplift is adopted. The [demand handoff](../demand-bridge/README.md), [energy closure](../delivery-closure/SITE-ENERGY.md), [clearance screen](../clearance/README.md) and [current programme ledger](../programme-recalculation/README.md) retain their separate acceptance gates.

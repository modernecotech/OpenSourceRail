# Baghdad delivery estimate and scope reconciliation

The published **USD 17.430462bn equivalent** is a base planning estimate, not a complete delivery budget. City subtotal is USD 16.634253bn and the one Baghdad factory including its EPC is USD 796.208m. [Scope register](scope-register.csv) retains quantity, implied rate, currency/source quality, inclusions, exclusions, estimator role and uncertainty. Every actual price date, quotation and named estimator remains unknown. Category implied rates reconcile the baseline; they are not surveyed rates.

| Baseline WBS | Quantity | USD m equivalent | Evidence |
| --- | --- | --- | --- |
| civil | 863.924 | 6,963.165 | category-planning-estimate |
| stations | 600.000 | 3,574.100 | category-planning-estimate |
| depots | 1.000 | 8.000 | category-planning-estimate |
| rolling_stock | 2,067.000 | 3,472.560 | category-planning-estimate |
| solar_plant | 1,695,026.537 | 1,356.021 | category-planning-estimate |
| signalling | 863.924 | 43.196 | category-planning-estimate |
| charging_microgrid | 1.000 | 217.700 | category-planning-estimate |
| epc_overhead | 1.000 | 999.510 | category-planning-estimate |
| factory-direct | 1.000 | 744.120 | factory-sizing-allowance |
| factory-epc | 1.000 | 52.088 | factory-sizing-allowance |

12 additional scope records retain **null costs**, not zero: land/title, utility diversions, duties/tax, owner costs, pre-opening people, six-car qualification, installed control/HIL, initial spares, working capital, civil/station investigations, task-derived maintenance and cyber deployment. Each requires a signed inclusion/quotation decision before financing is recalculated. Surveyed grade separation, foundations, standard spans, temporary works/erection, passenger access/evacuation, road interfaces and station functions must be investigated by corridor; civil and station standards alone do not resolve them.

EPC has [identified delivery obligations](epc-obligations.json), with individual priced contracts still null. Their sum cannot be asserted from the existing percentage. Factory contingency **USD 39.971m**, factory design/training/qualification **USD 20.0m**, routine train QA/labour/logistics and factory EPC are already embedded and must not be added twice. Initial stock, battery renewal cash dates, labour/maintenance contracts and working-capital reserves need account-level reconciliation.

| Depot alternative | Gross priced reference USD m | Provisional replacement total USD bn |
| --- | --- | --- |
| retained_declared_bays | 440.376 | 17.862837 |
| workload_bays | 438.382 | 17.860843 |

Replacement illustrations subtract the old depot allowance once, then add the gross quantity-based reference. They remain incomplete: charging/PV/EPC overlaps and unpriced work are unresolved. No alternative is adopted into the published funding programme; government/import shares, loans and opening dates remain conditional on the original scope. Retained property additions remain their existing separate scenarios, not automatically added to this base.

The seeded [correlated cost-and-delay sensitivity](cost-schedule-risk.json) combines a shared risk quantile with idiosyncratic cost events and delay escalation. Illustrative known-scope P50 is USD 21.616bn and P80 USD 23.253bn. **These are uncalibrated distributions, not an approved probabilistic budget.** Unpriced scope is excluded rather than priced at zero; existing contingencies remain embedded; stress outputs are alternatives and cannot be added to the base. Calibrate from investigations, contract evidence, event-level dependencies and actual invoice dates. [GAO estimating guidance](https://www.gao.gov/products/gao-20-195g) supports technical baseline, WBS, data, alternatives, risk analysis and updates; it does not validate OSR's rates. Reference checked 4 October 2026.

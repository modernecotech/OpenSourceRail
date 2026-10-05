# Baghdad factory sized to the city programme

<!-- OSR CURRENT SCOPE CONTEXT -->
> **Original catalogue or earlier scope reference.** The figures and policies below retain their original assumptions; they are not the latest Baghdad staffing, depot, procurement or funding basis. See the [current Baghdad recalculation](../programme-recalculation/README.md) and [current city summary](../../README.md). National/portfolio totals have not been repriced with that conditional Baghdad option.
<!-- END OSR CURRENT SCOPE CONTEXT -->

One factory is sized for **772 complete six-car trainsets / 4,632 cars**, with physical cells, crews and test paths. Facility readiness is **18 months from notice to proceed (working day 390)**, replacing the old 24-month assumption. Financial close precedes NTP by 30 working days; these are conditional offsets, not dated construction commitments.

The unchanged infrastructure resource model finishes on working day **1552**. The sized flow accepts the final train on day **1549**, 3 working days earlier. Full-network commissioning therefore follows infrastructure completion, rather than waiting decades for four generic train-production slots. All **772** trains remain in the planned scope; there is no smaller opening-fleet substitution.

## Flow and physical capacity

Cycles explicitly represent a **whole six-car trainset**, with structural, electrical and fit-out allowances doubled from the old generic cycle. One eight-hour shift and 85% productive availability are assumed. Occupation is ceil(productive cycle / availability); availability is not deducted again from that output. The first complete train belongs to the 772 and carries an additional 60-working-day qualification allowance. Every remaining material-kit task depends on that first-article acceptance; no series release is assumed before day 556.

| Stage | Productive days | Occupied days | Cells/bays | Direct crew |
| --- | --- | --- | --- | --- |
| Baghdad trainset kitting | 3 | 4 | 4 | 12 |
| Baghdad six-car structural assembly | 24 | 29 | 26 | 468 |
| Baghdad six-car composite kits | 10 | 12 | 11 | 88 |
| Baghdad six-car body installation | 2 | 3 | 3 | 36 |
| Baghdad six-car electrical integration | 20 | 24 | 21 | 252 |
| Baghdad six-car fitout and static test | 16 | 19 | 17 | 204 |
| Baghdad trainset acceptance bays | 12 | 15 | 13 | 52 |

The limiting steady capacity is **225.3 trainsets / 1352 cars per working year**. The resource scheduler simulates each train's linked stages, finite lanes and first-article gate. Cells are calculated from the city's fleet and the remaining infrastructure window, then increased to the first feasible balanced allocation; this is a reproducible capacity design, not a proof of minimum land or minimum cost.

Production bays use a 135 m by 6.5 m envelope for the 111 m consist, not a released building module. Composite and kitting cells have separate floor assumptions. Process and support space totals **113,940 m²**. The site screen is **43.5 hectares**, including circulation/storage and **3 independently segregated 2.0 km test paths**. These are site-reservation assumptions pending geometry, braking, fire, access, geotechnical and safe-operation design. Dynamic acceptance bays are not independent running tracks: the separate path calculation permits only **331.5 trainsets/year**, based on 16 exclusive track-hours/train and 85% path availability. A shared route cannot be counted twice. The test-path margin above limiting production is only 47.12%; the final fleet has only 3 working days of schedule margin. See the [frozen-resource disruption, costed second-shift recovery and civil acceleration study](../delivery-risk/README.md). Those stresses preserve the selected cells rather than resizing them to hide delay.

Direct cell staffing totals **1,112 positions per staffed shift** before management, stores, maintenance, relief and shift coverage. It is a proposed resource requirement, not measured job creation. Manufacturing labour and materials are already in train procurement CAPEX; they are not added again to plant CAPEX or railway OPEX.

## Line handover and the early-line constraint

| Line | Full fleet | Infrastructure day | Fleet day | Opening month |
| --- | --- | --- | --- | --- |
| line-1 | 94 | 676 | 766 | 40 |
| line-2 | 96 | 787 | 877 | 45 |
| line-3 | 92 | 893 | 983 | 50 |
| line-4 | 83 | 989 | 1079 | 55 |
| line-5 | 90 | 1093 | 1183 | 59 |
| line-6 | 104 | 1213 | 1303 | 65 |
| line-7 | 74 | 1298 | 1388 | 69 |
| line-8 | 92 | 1405 | 1495 | 74 |
| line-9 | 47 | 1552 | 1549 | 77 |

The factory completes alongside the **overall city civil programme**. Full-fleet openings are retained. Noncritical infrastructure now moves within its existing crew lanes and dependency graph towards fleet handover, with a 90-working-day target buffer; critical infrastructure retains its original completion dates. Line 1's infrastructure completion moves from day 225 to day 676, reducing the idle interval before its fleet from 541 to 90 working days. No rolling-stock date, task duration, resource count or opening date changes. This is a conditional investment-timing proposal: surveys, land, utilities, permits and contract dates require approval before deferring site work. [Original and rephased line reconciliation](civil-rephasing.csv) preserves both sets of dates. Line priority follows the original infrastructure requirements, with actual asset identifiers preserved.

The opening calculation retains the separate three-month integrated commissioning allowance after line infrastructure, the full fleet and shared depot/control work. The 60-day first-article allowance and three-month line allowance cover different activities. Required approvals, surveys, physical tests and independent acceptance remain open; neither allowance constitutes accepted safety evidence or an approved construction calendar.

## Eighteen-month facility construction sequence

| Activity | Working days | Accountable role |
| --- | --- | --- |
| Land/access, survey, design and approvals | 60 | Sponsor and owner engineer |
| Mobilisation, earthworks, foundations and underground services | 70 | Local civil contractor |
| Factory shell, lifting structure and utility backbone | 70 | Local structural and MEP contractors |
| Production cells, moulds, cranes and test-track construction | 80 | Production engineer and equipment suppliers |
| Equipment installation, calibration, staffing and training | 70 | Factory operator and quality manager |
| Factory process proving, safe-work and facility acceptance | 40 | Owner engineer and independent inspectors |

These six sequential planning packages total 390 working days. Long-lead tooling, cranes, battery handling equipment and imported systems must be ordered early enough to install and prove within that window. Land/access and financing availability are required at NTP. A delay to those gates changes the programme; the schedule is not a contractor-backed promise.

## Factory capital and cashflow

| Physical budget allocation | USD million |
| --- | --- |
| buildings | 79.758 |
| serviced site | 15.220 |
| stage tooling | 104.450 |
| test tracks | 18.000 |
| shared utilities stores labs logistics | 35.000 |
| design training qualification | 20.000 |
| contingency | 54.486 |

The physical envelope is **USD 326.913 million direct**, compared with the old module allowance of USD 277.920 million. The programme budgets the larger amount, **USD 326.913 million plus USD 22.884 million EPC**, counted once. The resulting capital increase is **USD 52.423 million**; added bays are not treated as free capacity. Rates and quantities are engineering allocations requiring Iraqi contractor/vendor quotations, not market-verified prices. Actual equipment origin must also reconcile to the programme's imported/local allowances.

Factory payments are re-timed to the 390-day facility programme and city train payments follow the new production tasks. Baghdad's monthly debt, interest, 5% fare/OPEX indexing, liquidity gaps, surplus repayments and six-month bond/loan requirements are recalculated from those dates. Government remains 25% of capital; import cash and Chinese credit retain the 50:50 USD split, with remaining funding in IQD. The existing aggregate plant import allowance remains 20% of direct plant capital, allocated within tooling/test equipment rather than buildings; supplier origin and the actual equipment mix require RFQs and eligibility checks. EPC retains its separate procurement-origin allowance. Future national cities do not enter this plant's production load or Baghdad cashflow.

## Procurement and qualification requirements

Before release, obtain measured six-car labour routes and prototype cycle times; trainset-level supplier delivery schedules; released mould/fixture drawings and duplication plans; lifting/handling and HV/battery fire segregation; stores, quarantine and rework capacity; inspection/calibration capacity; crew recruitment and training; both independent test-path designs; utility availability; and a land/industrial permit package. Composite cells cannot be mistaken for the number of panel moulds: the final panel design and cure/release conditions determine mould duplication. The hypothetical whole-kit cycle must be validated against that tooling count. Existing civil precast/slab yards retain their own production resources and are not assigned to train bays.

The 85% factor is a deterministic allowance for non-productive time, not a quantified programme contingency. Supplier disruption, multi-month qualification, redesign and civil delays need risk scenarios before investment decisions. Expansion beyond Baghdad needs a new demand and capacity assessment; a national module budget is not a promise of parallel national production.

[Cell and tooling register](cells.csv) · [772 planned trainset acceptances](deliveries.csv) · [Line handover reconciliation](line-completion.csv) · [Machine-readable calculation](summary.json) · [Factory capacity inputs](../../../../../../../lib/templates/baghdad-factory.toml)

Regenerate after operations with `.venv/bin/python tools/automation/generate-factory-plan.py`; validate the same command with `--check`. Status: reference planning engineering, no construction or manufacturing release.

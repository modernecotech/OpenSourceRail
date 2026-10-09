# Baghdad factory sized to the city programme

One factory is sized for **2,067 complete six-car trainsets / 12,402 cars**, with physical cells, crews and test paths. Facility readiness is **18 months from notice to proceed (working day 390)**, replacing the old 24-month assumption. Financial close precedes NTP by 30 working days; these are conditional offsets, not dated construction commitments.

The unchanged infrastructure resource model finishes on working day **4217**. The sized flow accepts the final train on day **4201**, 16 working days earlier. Full-network commissioning therefore follows infrastructure completion, rather than waiting decades for four generic train-production slots. All **2067** trains remain in the planned scope; there is no smaller opening-fleet substitution.

## Flow and physical capacity

Cycles explicitly represent a **whole six-car trainset**, with structural, electrical and fit-out allowances doubled from the old generic cycle. One eight-hour shift and 85% productive availability are assumed. Occupation is ceil(productive cycle / availability); availability is not deducted again from that output. The first complete train belongs to the 2067 and carries an additional 60-working-day qualification allowance. Every remaining material-kit task depends on that first-article acceptance; no series release is assumed before day 556.

| Stage | Productive days | Occupied days | Cells/bays | Direct crew |
| --- | --- | --- | --- | --- |
| Baghdad trainset kitting | 3 | 4 | 3 | 9 |
| Baghdad six-car structural assembly | 24 | 29 | 17 | 306 |
| Baghdad six-car composite kits | 10 | 12 | 7 | 56 |
| Baghdad six-car body installation | 2 | 3 | 2 | 24 |
| Baghdad six-car electrical integration | 20 | 24 | 14 | 168 |
| Baghdad six-car fitout and static test | 16 | 19 | 12 | 144 |
| Baghdad trainset acceptance bays | 12 | 15 | 9 | 36 |

The limiting steady capacity is **151.7 trainsets / 910 cars per working year**. The resource scheduler simulates each train's linked stages, finite lanes and first-article gate. Cells are calculated from the city's fleet and the remaining infrastructure window, then increased to the first feasible balanced allocation; this is a reproducible capacity design, not a proof of minimum land or minimum cost.

Production bays use a 135 m by 6.5 m envelope for the 111 m consist, not a released building module. Composite and kitting cells have separate floor assumptions. Process and support space totals **76,322 m²**. The site screen is **29.1 hectares**, including circulation/storage and **2 independently segregated 2.0 km test paths**. These are site-reservation assumptions pending geometry, braking, fire, access, geotechnical and safe-operation design. Dynamic acceptance bays are not independent running tracks: the separate path calculation permits only **221.0 trainsets/year**, based on 16 exclusive track-hours/train and 85% path availability. A shared route cannot be counted twice. The test-path margin above limiting production is only 45.71%; the final fleet has only 16 working days of schedule margin. See the [frozen-resource disruption, costed second-shift recovery and civil acceleration study](../delivery-risk/README.md). Those stresses preserve the selected cells rather than resizing them to hide delay.

Direct cell staffing totals **743 positions per staffed shift** before management, stores, maintenance, relief and shift coverage. It is a proposed resource requirement, not measured job creation. Manufacturing labour and materials are already in train procurement CAPEX; they are not added again to plant CAPEX or railway OPEX.

## Line handover and the early-line constraint

| Line | Full fleet | Infrastructure day | Fleet day | Opening month |
| --- | --- | --- | --- | --- |
| line-1 | 126 | 783 | 873 | 45 |
| line-10 | 17 | 812 | 902 | 47 |
| line-11 | 25 | 855 | 945 | 49 |
| line-12 | 23 | 895 | 985 | 50 |
| line-13 | 20 | 929 | 1019 | 52 |
| line-14 | 19 | 961 | 1051 | 53 |
| line-15 | 30 | 1013 | 1103 | 56 |
| line-16 | 23 | 1052 | 1142 | 58 |
| line-17 | 20 | 1087 | 1177 | 59 |
| line-18 | 21 | 1123 | 1213 | 61 |
| line-19 | 19 | 1155 | 1245 | 62 |
| line-2 | 123 | 1515 | 1456 | 75 |
| line-20 | 20 | 1524 | 1490 | 75 |
| line-21 | 28 | 1533 | 1538 | 76 |
| line-22 | 17 | 1542 | 1567 | 77 |
| line-23 | 27 | 1551 | 1614 | 79 |
| line-24 | 31 | 1577 | 1667 | 82 |
| line-25 | 21 | 1613 | 1703 | 83 |
| line-26 | 19 | 1645 | 1735 | 85 |
| line-27 | 41 | 1716 | 1806 | 88 |
| line-28 | 25 | 1759 | 1849 | 90 |
| line-29 | 29 | 1808 | 1898 | 92 |
| line-3 | 113 | 2002 | 2092 | 101 |
| line-30 | 24 | 2043 | 2133 | 103 |
| line-31 | 32 | 2098 | 2188 | 106 |
| line-32 | 25 | 2141 | 2231 | 108 |
| line-33 | 25 | 2184 | 2274 | 110 |
| line-34 | 23 | 2223 | 2313 | 112 |
| line-35 | 24 | 2264 | 2354 | 114 |
| line-36 | 25 | 2307 | 2397 | 116 |
| line-37 | 37 | 2371 | 2461 | 118 |
| line-38 | 19 | 2403 | 2493 | 120 |
| line-39 | 19 | 2436 | 2526 | 121 |
| line-4 | 97 | 2602 | 2692 | 129 |
| line-40 | 20 | 2636 | 2726 | 131 |
| line-41 | 20 | 2671 | 2761 | 132 |
| line-42 | 16 | 2698 | 2788 | 134 |
| line-43 | 35 | 2758 | 2848 | 136 |
| line-44 | 32 | 2813 | 2903 | 139 |
| line-45 | 20 | 2847 | 2937 | 140 |
| line-46 | 25 | 2890 | 2980 | 142 |
| line-47 | 34 | 2948 | 3038 | 145 |
| line-48 | 17 | 2977 | 3067 | 146 |
| line-49 | 28 | 3025 | 3115 | 149 |
| line-5 | 116 | 3224 | 3314 | 158 |
| line-50 | 38 | 3289 | 3379 | 161 |
| line-51 | 21 | 3325 | 3415 | 163 |
| line-52 | 29 | 3375 | 3465 | 165 |
| line-53 | 37 | 3439 | 3529 | 168 |
| line-54 | 27 | 3485 | 3575 | 170 |
| line-6 | 119 | 3689 | 3779 | 179 |
| line-7 | 86 | 3836 | 3926 | 186 |
| line-8 | 102 | 4011 | 4101 | 194 |
| line-9 | 58 | 4217 | 4201 | 200 |

The factory completes alongside the **overall city civil programme**. Full-fleet openings are retained. Noncritical infrastructure now moves within its existing crew lanes and dependency graph towards fleet handover, with a 90-working-day target buffer; critical infrastructure retains its original completion dates. Line 1's infrastructure completion moves from day 671 to day 783, reducing the idle interval before its fleet from 202 to 90 working days. No rolling-stock date, task duration, resource count or opening date changes. This is a conditional investment-timing proposal: surveys, land, utilities, permits and contract dates require approval before deferring site work. [Original and rephased line reconciliation](civil-rephasing.csv) preserves both sets of dates. Line priority follows the original infrastructure requirements, with actual asset identifiers preserved.

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
| buildings | 53.426 |
| serviced site | 10.178 |
| stage tooling | 69.250 |
| test tracks | 12.000 |
| shared utilities stores labs logistics | 35.000 |
| design training qualification | 20.000 |
| contingency | 39.971 |

The physical envelope is **USD 239.825 million direct**, compared with the old module allowance of USD 744.120 million. The programme budgets the larger amount, **USD 744.120 million plus USD 52.088 million EPC**, counted once. The resulting capital increase is **USD 0.000 million**; added bays are not treated as free capacity. Rates and quantities are engineering allocations requiring Iraqi contractor/vendor quotations, not market-verified prices. Actual equipment origin must also reconcile to the programme's imported/local allowances.

Factory payments are re-timed to the 390-day facility programme and city train payments follow the new production tasks. Baghdad's monthly debt, interest, 5% fare/OPEX indexing, liquidity gaps, surplus repayments and six-month bond/loan requirements are recalculated from those dates. Government remains 25% of capital; import cash and Chinese credit retain the 50:50 USD split, with remaining funding in IQD. The existing aggregate plant import allowance remains 20% of direct plant capital, allocated within tooling/test equipment rather than buildings; supplier origin and the actual equipment mix require RFQs and eligibility checks. EPC retains its separate procurement-origin allowance. Future national cities do not enter this plant's production load or Baghdad cashflow.

## Procurement and qualification requirements

Before release, obtain measured six-car labour routes and prototype cycle times; trainset-level supplier delivery schedules; released mould/fixture drawings and duplication plans; lifting/handling and HV/battery fire segregation; stores, quarantine and rework capacity; inspection/calibration capacity; crew recruitment and training; both independent test-path designs; utility availability; and a land/industrial permit package. Composite cells cannot be mistaken for the number of panel moulds: the final panel design and cure/release conditions determine mould duplication. The hypothetical whole-kit cycle must be validated against that tooling count. Existing civil precast/slab yards retain their own production resources and are not assigned to train bays.

The 85% factor is a deterministic allowance for non-productive time, not a quantified programme contingency. Supplier disruption, multi-month qualification, redesign and civil delays need risk scenarios before investment decisions. Expansion beyond Baghdad needs a new demand and capacity assessment; a national module budget is not a promise of parallel national production.

[Cell and tooling register](cells.csv) · [2067 planned trainset acceptances](deliveries.csv) · [Line handover reconciliation](line-completion.csv) · [Machine-readable calculation](summary.json) · [Factory capacity inputs](../../../../../../../lib/templates/baghdad-factory.toml)

Regenerate after operations with `.venv/bin/python tools/automation/generate-factory-plan.py`; validate the same command with `--check`. Status: reference planning engineering, no construction or manufacturing release.

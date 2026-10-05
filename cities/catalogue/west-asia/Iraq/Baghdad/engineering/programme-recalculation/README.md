# Baghdad programme recalculation

Controlled planning basis, 2026-10-04; unquoted and uncommitted. This is the latest staffing/depot/local-production review. Existing cost and financing cases remain historical comparators; no survey, manufacturing qualification or lender commitment is created.

## Operating people and wages

The 186 stations require two concurrent staff during two normal eight-hour shifts: **744 daily shift assignments**, not a headcount of people working every day. Retaining 20.5 service hours also requires 4.5 hours of separately funded late cover per station. Weekly cover, leave, training, sickness and handovers give **1840 station-cover FTE**, within **3716 permanent operating FTE**. Full-operation loaded payroll is **IQD 86.303bn/year** (USD 66.387m equivalent), indexed thereafter with OPEX.

The employee median is IQD 614,000 from the 2021 Labour Force Survey, cited in the [IMF 2023 report](https://www.imf.org/-/media/files/publications/cr/2023/english/1irqea2023002.pdf). Applying an assumed 5% annual index to 2026 gives IQD 783,637; the general-worker floor is **IQD 1,175,455/month**, 50% higher. Technical, supervisor, senior and director roles use 2.25/3/4/5 times that indexed proxy. This is a historical observation plus an editable index, not a measured current national median. Employer costs and overtime are priced separately. [Roles](workforce.csv) and [recruitment/cohorts](workforce.json) retain appointment and competence gates.

[ERP planning drafts](erp-planning-drafts.json) map the revised Staffing Plan, depot Project/Asset budgets and factory Workstations to native business records; they create no Employee, appointment, transaction or approval.

Construction workers, factory production/support workers and permanent operators are separate populations. [Construction](construction-workforce.json) applies explicit trade-crew allowances to actual work-package resource lanes/dates, counting overlapping use of the same lane once; its peak is 466 FTE. It is not a measured complete contractor crew schedule; revised depot and upstream factory construction crews still require their own work-package schedules. Construction labour is already inside contract rates; its unknown payroll-content overlap remains unpriced, preventing a duplicate charge. A separate wage-content stress increases assumed labour content (20% of affected contracts) by 50%, with incremental EPC once; it is an overlap sensitivity, not proof of contractor wage contents. Existing assembly wages are replaced using an explicitly assumed embedded payroll credit; component process labour is inside component unit prices. Paid production capacity above those productive hours is added separately, never charged twice.

The final-assembly establishment is 1294 production FTE plus 195 support FTE. The scheduled order requires 55 paid months from month 18 through month 72; payroll follows this calendar, rather than dividing the order by a theoretical steady-state rate and losing ramp-up/idle months. Each upstream plant also funds its whole production establishment for that period, with the productive labour already in unit prices deducted once. These jobs are additional to permanent railway operations; no national order or permanent post-order subsidy is assumed.

## One depot per line, full-size trains and fleet

There are **9 line-local depots**, providing **772 storage slots** for all six-car revenue/spare/reserve trains. Slots use the actual 111 m train plus 10 m clearance. Workshop bays follow annual bay-hour demand and usable bay capacity; parking slots are not maintenance bays. Station storage is an option without any capacity credit in this case. Full overnight-to-morning launch and throat conflicts remain unvalidated.

| Line | Trainsets/storage slots | Tracks | Workshop bays | Land envelope ha | Reference USD m |
| --- | --- | --- | --- | --- | --- |
| line-1 | 94 | 32 | 13 | 12.60 | 29.039 |
| line-2 | 96 | 32 | 14 | 12.72 | 36.858 |
| line-3 | 92 | 31 | 13 | 12.27 | 28.814 |
| line-4 | 83 | 28 | 12 | 11.17 | 26.790 |
| line-5 | 90 | 30 | 13 | 11.94 | 28.589 |
| line-6 | 104 | 35 | 15 | 13.82 | 32.352 |
| line-7 | 74 | 25 | 11 | 10.07 | 24.766 |
| line-8 | 92 | 31 | 13 | 12.27 | 28.814 |
| line-9 | 47 | 16 | 7 | 6.64 | 17.435 |

Total depot reference: **USD 253.456m**, replacing the original USD 8m exactly once. Storage, workshop and access tracks, points, drainage/access, workshop shell/equipment/services, yard lighting/fire services, wash plant, wheel lathe, offices/stores and rescue/quarantine are visible. Access-track length is an editable allowance, not a connected site alignment. Existing depot PV/BESS is retained once. Land/title, utility relocation, actual soil/foundations, installed charger/grid upgrades and tax/duties remain unpriced. [Item register](depot-items.csv).

## Core elevated stations

The reworked core has 112 station platforms with raised-structure/access scope. The register replaces their catalogue allowance with a separately stated elevated reference, adding **USD 332.680m direct**, with incremental EPC and operating maintenance once. Elevated interchange allowances are already present where catalogued; they receive no duplicate uplift. Other core stations use a 30% structure allowance plus USD 1m for vertical access. These are unquoted allowances, not released multi-level junction or station designs. [Core station register](core-elevated-stations.json).

## Iraqi component manufacture

| Product | Network quantity | Required units/year | Cells | Production/support FTE | Factory capital USD m | Unit make/buy USD | Whole-order margin USD m |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bogie | 9264 | 2704 | 31 | 145/22 | 43.487 | 15156/25000 | 36.616 |
| motor-inverter-set | 9264 | 2704 | 21 | 74/12 | 29.965 | 11078/15000 | -0.371 |
| battery-225kwh-pack | 4632 | 1352 | 8 | 38/6 | 25.577 | 29828/45000 | 40.016 |
| door-cassette | 18528 | 5408 | 13 | 46/7 | 15.964 | 2023/3333 | 4.352 |
| window-cassette | 27792 | 8112 | 10 | 35/6 | 23.658 | 687/1111 | -16.293 |

[Make/buy inputs](component-make-buy.csv) price imported process machinery, Iraqi buildings/site work, qualification, residual imported inputs, local materials, graded labour, process overhead, fixed support and plant maintenance. Cells are sized to the existing train factory's required production rate, not a small demonstration line. The order is 1.042 GWh of gross onboard packs. Battery **pack assembly** is evaluated; imported cells/BMS remain. Bogie wheels/axles/bearings, motor inverters/magnets, door safety electronics and glazing feedstock also retain imports. Local manufacture does not mean zero USD input.

The buy case itemises these five imported completed products; the old blanket vehicle import percentage is retained only for other parent scope. This prevents replacing already-local scope with a second import credit. The all-product and positive-margin selections are separate unquoted cases. Whole-order margins are before finance/tax/risk; vendor prices, license, QA, process yield, supply commitments and first articles must validate them. No future national order pays Baghdad debt or makes an uneconomic line look profitable. Serial component qualification is assumed within the 18-month readiness target, not proven. A six-month supplier delay shifts rolling-stock invoices and opening/service cash, extends the full operating horizon and prices idle production payroll. A 25% raw-input price stress preserves the same selected facilities. Rejected/reworked product still needs a measured production replay. Existing final assembly tooling remains priced; upstream machinery is added without an unproven overlap credit.

## More elevation and fewer bends

The current main design adopts the straight central elevated alignment. The screening policy allows up to 65% elevated and at least 25% at grade, subject to site/design acceptance. Baghdad currently has 55.26% elevated. Investigation windows around all 18 exceptional segments add 7.178 km of candidate at-grade conversion, reaching 56.76%; overlapping intervals are merged and existing viaduct/bridge lengths excluded. Approach length is at least 300.0 m from assumed height/gradient.

**Elevation alone removes no horizontal bend.** Wider-radius geometry, station moves, ROW, vertical alignment, ramps, egress, ground/utility evidence, crossings and whole-life costs must be designed together. The finance cases separately test no routing-penalty removal and hypothetical 25%/50% removal; these percentages are unverified counterfactuals, not achieved savings. The added standard civil allowance uses the conservative simple-span bearing index. [Candidate intervals](alignment-candidates.csv).

## Funding and mezzanine comparison

Government capital remains exactly 25% of the scenario total. Imported invoices receive 50% government USD cash / 50% Chinese USD credit. Remaining government cash, bonds, senior bank/gap credit and mezzanine are IQD. Government USD payment dates follow machinery/input invoices; the remaining appropriation is allocated proportionally to local invoices, so a machinery-heavy month need not be falsely limited to 25% government cash. Chinese supplier origin and export-credit eligibility are assumptions requiring vendor/lender confirmation. China Exim describes buyer credit for Chinese products, technologies and services; machinery eligibility is not a loan commitment ([official product description](https://english.eximbank.gov.cn/Business/CreditB/SupportingFT/201810/t20181016_6965.html)).

The positive-margin local-production senior case's **capital-only** sources are shown below. They sum to its capital uses; gap credit, interest/fees, reserve funding and operating receipts are additional cashflows in its [monthly ledger](local_positive-monthly.csv) and [six-month placement schedule](local_positive-semiannual.csv). Ordinary and green bonds are separate placements, never added again to a combined bond figure. Bond face units are IQD 1m; rounded placement envelopes are not additional cash raised.

| Capital source | Currency | Native amount | USD equivalent m |
| --- | --- | --- | --- |
| Government import cash | USD | 1,510,440,238 | 1510.440 |
| Government local cash | IQD | 2,987,175,216,330 | 2297.827 |
| Chinese capital credit | USD | 1,510,440,238 | 1510.440 |
| Ordinary capital bonds | IQD | 8,588,305,488,245 | 6606.389 |
| Green capital bonds | IQD | 1,053,822,212,230 | 810.632 |
| Senior bank capital credit | IQD | 3,214,042,566,825 | 2472.340 |
| Conditional climate capital grant | IQD | 32,500,000,000 | 25.000 |

Mezzanine replaces 10% of domestic residual capital borrowing; it is not extra capital on top of the uses. The IQD case has 6% cash coupon, 4% PIK, 2% arrangement fee and a 15-year balloon from each draw. Deferred cash coupon and PIK increase outstanding debt until maturity. Thereafter the overdue principal is retained with separately disclosed simple 10% contractual-interest sensitivity; arrears are not compounded and the balloon is not silently extended. Cash junior payments require senior DSCR of 1.20, funded reserves and actual residual cash; new gap draws/unfunded support cannot pay junior debt. No conversion, fresh equity or automatic refinancing is invented. Unpaid maturity balances/defaults remain visible. Mezzanine is structurally junior to senior debt and senior to equity, as described by [UNCITRAL](https://digitallibrary.un.org/record/272622/files/A_CN.9_458_Add.1-EN.pdf); the rates here are project sensitivities.

| Matched case / six-month placement schedule | CAPEX USD bn | USD capital intensity | Peak IQD gap tn | Terminal all debt IQD tn | Unfunded IQD tn | Junior defaulted vintages |
| --- | --- | --- | --- | --- | --- | --- |
| [revised_scope_buy](revised_scope_buy-semiannual.csv) | 15.341 | 21.43% | 13.000 | 13.000 | 27.482 | 0 |
| [local_all](local_all-semiannual.csv) | 15.239 | 19.40% | 13.000 | 13.000 | 27.359 | 0 |
| [local_positive](local_positive-semiannual.csv) | 15.233 | 19.83% | 13.000 | 13.000 | 27.330 | 0 |
| [local_positive_mezzanine](local_positive_mezzanine-semiannual.csv) | 15.233 | 19.83% | 13.000 | 29.090 | 25.016 | 79 |
| [local_positive_commercial_gap](local_positive_commercial_gap-semiannual.csv) | 15.233 | 19.83% | 13.000 | 13.000 | 51.331 | 0 |
| [local_positive_mezzanine_stress](local_positive_mezzanine_stress-semiannual.csv) | 15.233 | 19.83% | 13.000 | 67.444 | 48.845 | 79 |
| [grade-separation-penalty-0pct](grade-separation-penalty-0pct-semiannual.csv) | 15.292 | 19.81% | 13.000 | 13.000 | 27.433 | 0 |
| [grade-separation-penalty-25pct](grade-separation-penalty-25pct-semiannual.csv) | 13.555 | 20.48% | 13.000 | 13.000 | 24.364 | 0 |
| [grade-separation-penalty-50pct](grade-separation-penalty-50pct-semiannual.csv) | 11.818 | 21.29% | 13.000 | 13.000 | 21.267 | 0 |
| [local_positive_raw_price_stress](local_positive_raw_price_stress-semiannual.csv) | 15.307 | 20.04% | 13.000 | 13.000 | 27.453 | 0 |
| [local_positive_supplier_delay](local_positive_supplier_delay-semiannual.csv) | 15.233 | 19.83% | 13.000 | 13.000 | 27.652 | 0 |
| [construction_wage_content_stress](construction_wage_content_stress-semiannual.csv) | 16.499 | 19.44% | 13.000 | 13.000 | 29.555 | 0 |

The 3 positive-margin process options reduce capital from USD 15.341bn to USD 15.233bn, and imported invoice exposure from USD 3.287bn to USD 3.021bn. Half of that exposure is government USD cash and half Chinese USD credit; all other capital funding is IQD. The historical 148 km / USD 18bn third-party benchmark has a different scope and assumed full foreign-currency financing; this is a planning comparison, not a like-for-like tender saving. The reworked 479.0 km network's 39.4% population-access proxy is not surveyed pedestrian coverage.

**Current financial conclusion:** the positive-margin senior case records IQD 27.330tn of residual unsourced support after assumed facilities and retains IQD 13.000tn of debt at the horizon. Its company NPV before finance is USD -10.591bn at the assumed nominal discount rate. Adding mezzanine does not change the underlying operating return: it leaves IQD 29.090tn of total debt and 79 unpaid junior vintages. It is not recommended as a cure for the funding deficit. Fare and OPEX indexation, kiosks/advertising and inherited additional receipts are already included; new verified capital, affordable revenue or accepted scope savings are still needed.

All cases use the same revised staff, depot and indexed fare/OPEX assumptions. Six months of scheduled senior service are reserved from the first draw; three months of OPEX plus explicit industrial working capital are restricted. This revised reserve policy differs from older reference cases, so compare matched cases in this table when judging mezzanine. Concessional 2% gap funding, grants/rights/additional income and enhanced green coupons are uncommitted; the 8% gap and high mezzanine-rate case expose that dependence. There are zero dividends. Cash/principal/PIK identities, maturity risk, monthly draws and six-month bond denominations are retained for every case.

Regenerate with `.venv/bin/python tools/automation/baghdad_programme_recalculation.py`; verify with `--check`. Complete installed scope, construction wage-content adjustment, local-pay survey, validated demand/timetable and supplier/lender agreements remain open.

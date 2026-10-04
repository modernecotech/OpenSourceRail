# Baghdad programme recalculation

Controlled planning basis, 2026-10-04; unquoted and uncommitted. This is the latest staffing/depot/local-production review. Existing cost and financing cases remain historical comparators; no survey, manufacturing qualification or lender commitment is created.

## Operating people and wages

The 182 stations require two concurrent staff during two normal eight-hour shifts: **728 daily shift assignments**, not 728 people working every day. Retaining 20.5 service hours also requires 4.5 hours of separately funded late cover per station. Weekly cover, leave, training, sickness and handovers give **1800 station-cover FTE**, within **3762 permanent operating FTE**. Full-operation loaded payroll is **IQD 87.808bn/year** (USD 67.544m equivalent), indexed thereafter with OPEX.

The employee median is IQD 614,000 from the 2021 Labour Force Survey, cited in the [IMF 2023 report](https://www.imf.org/-/media/files/publications/cr/2023/english/1irqea2023002.pdf). Applying an assumed 5% annual index to 2026 gives IQD 783,637; the general-worker floor is **IQD 1,175,455/month**, 50% higher. Technical, supervisor, senior and director roles use 2.25/3/4/5 times that indexed proxy. This is a historical observation plus an editable index, not a measured current national median. Employer costs and overtime are priced separately. [Roles](workforce.csv) and [recruitment/cohorts](workforce.json) retain appointment and competence gates.

[ERP planning drafts](erp-planning-drafts.json) map the revised Staffing Plan, depot Project/Asset budgets and factory Workstations to native business records; they create no Employee, appointment, transaction or approval.

Construction workers, factory production/support workers and permanent operators are separate populations. [Construction](construction-workforce.json) applies explicit trade-crew allowances to actual work-package resource lanes/dates, counting overlapping use of the same lane once; its peak is 464 FTE. It is not a measured complete contractor crew schedule; revised depot and upstream factory construction crews still require their own work-package schedules. Construction labour is already inside contract rates; its unknown payroll-content overlap remains unpriced, preventing a duplicate charge. A separate wage-content stress increases assumed labour content (20% of affected contracts) by 50%, with incremental EPC once; it is an overlap sensitivity, not proof of contractor wage contents. Existing assembly wages are replaced using an explicitly assumed embedded payroll credit; component process labour is inside component unit prices. Paid production capacity above those productive hours is added separately, never charged twice.

The final-assembly establishment is 1215 production FTE plus 183 support FTE. The scheduled order requires 60 paid months from month 18 through month 77; payroll follows this calendar, rather than dividing the order by a theoretical steady-state rate and losing ramp-up/idle months. Each upstream plant also funds its whole production establishment for that period, with the productive labour already in unit prices deducted once. These jobs are additional to permanent railway operations; no national order or permanent post-order subsidy is assumed.

## One depot per line, full-size trains and fleet

There are **9 line-local depots**, providing **831 storage slots** for all six-car revenue/spare/reserve trains. Slots use the actual 111 m train plus 10 m clearance. Workshop bays follow annual bay-hour demand and usable bay capacity; parking slots are not maintenance bays. Station storage is an option without any capacity credit in this case. Full overnight-to-morning launch and throat conflicts remain unvalidated.

| Line | Trainsets/storage slots | Tracks | Workshop bays | Land envelope ha | Reference USD m |
| --- | --- | --- | --- | --- | --- |
| line-1 | 95 | 32 | 14 | 12.72 | 30.328 |
| line-2 | 103 | 35 | 15 | 13.82 | 32.322 |
| line-3 | 108 | 36 | 15 | 14.15 | 32.637 |
| line-4 | 85 | 29 | 12 | 11.50 | 27.015 |
| line-5 | 98 | 33 | 14 | 13.05 | 30.583 |
| line-6 | 111 | 37 | 16 | 14.59 | 40.651 |
| line-7 | 84 | 28 | 12 | 11.17 | 26.820 |
| line-8 | 100 | 34 | 14 | 13.37 | 30.808 |
| line-9 | 47 | 16 | 7 | 6.64 | 17.435 |

Total depot reference: **USD 268.598m**, replacing the original USD 8m exactly once. Storage, workshop and access tracks, points, drainage/access, workshop shell/equipment/services, yard lighting/fire services, wash plant, wheel lathe, offices/stores and rescue/quarantine are visible. Access-track length is an editable allowance, not a connected site alignment. Existing depot PV/BESS is retained once. Land/title, utility relocation, actual soil/foundations, installed charger/grid upgrades and tax/duties remain unpriced. [Item register](depot-items.csv).

## Iraqi component manufacture

| Product | Network quantity | Required units/year | Cells | Production/support FTE | Factory capital USD m | Unit make/buy USD | Whole-order margin USD m |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bogie | 9972 | 2582 | 30 | 140/21 | 42.568 | 15156/25000 | 44.115 |
| motor-inverter-set | 9972 | 2582 | 20 | 70/11 | 29.253 | 11078/15000 | 3.066 |
| battery-225kwh-pack | 4986 | 1291 | 8 | 38/6 | 25.577 | 29828/45000 | 44.922 |
| door-cassette | 19944 | 5164 | 12 | 42/7 | 15.351 | 2023/3333 | 6.930 |
| window-cassette | 29916 | 7746 | 9 | 32/5 | 22.392 | 687/1111 | -13.965 |

[Make/buy inputs](component-make-buy.csv) price imported process machinery, Iraqi buildings/site work, qualification, residual imported inputs, local materials, graded labour, process overhead, fixed support and plant maintenance. Cells are sized to the existing train factory's required production rate, not a small demonstration line. The order is 1.122 GWh of gross onboard packs. Battery **pack assembly** is evaluated; imported cells/BMS remain. Bogie wheels/axles/bearings, motor inverters/magnets, door safety electronics and glazing feedstock also retain imports. Local manufacture does not mean zero USD input.

The buy case itemises these five imported completed products; the old blanket vehicle import percentage is retained only for other parent scope. This prevents replacing already-local scope with a second import credit. The all-product and positive-margin selections are separate unquoted cases. Whole-order margins are before finance/tax/risk; vendor prices, license, QA, process yield, supply commitments and first articles must validate them. No future national order pays Baghdad debt or makes an uneconomic line look profitable. Serial component qualification is assumed within the 18-month readiness target, not proven. A six-month supplier delay shifts rolling-stock invoices and opening/service cash, extends the full operating horizon and prices idle production payroll. A 25% raw-input price stress preserves the same selected facilities. Rejected/reworked product still needs a measured production replay. Existing final assembly tooling remains priced; upstream machinery is added without an unproven overlap credit.

## More elevation and fewer bends

The study allows up to 40% elevated and at least 55% at grade, subject to site/design acceptance. Baghdad currently has 14.68% elevated. Investigation windows around all 65 exceptional segments add 29.148 km of candidate at-grade conversion, reaching 20.32%; overlapping intervals are merged and existing viaduct/bridge lengths excluded. Approach length is at least 300.0 m from assumed height/gradient.

**Elevation alone removes no horizontal bend.** Wider-radius geometry, station moves, ROW, vertical alignment, ramps, egress, ground/utility evidence, crossings and whole-life costs must be designed together. The finance cases separately test no routing-penalty removal and hypothetical 25%/50% removal; these percentages are unverified counterfactuals, not achieved savings. The added standard civil allowance uses the conservative simple-span bearing index. [Candidate intervals](alignment-candidates.csv).

## Funding and mezzanine comparison

Government capital remains exactly 25% of the scenario total. Imported invoices receive 50% government USD cash / 50% Chinese USD credit. Remaining government cash, bonds, senior bank/gap credit and mezzanine are IQD. Government USD payment dates follow machinery/input invoices; the remaining appropriation is allocated proportionally to local invoices, so a machinery-heavy month need not be falsely limited to 25% government cash. Chinese supplier origin and export-credit eligibility are assumptions requiring vendor/lender confirmation. China Exim describes buyer credit for Chinese products, technologies and services; machinery eligibility is not a loan commitment ([official product description](https://english.eximbank.gov.cn/Business/CreditB/SupportingFT/201810/t20181016_6965.html)).

The four-process senior case's **capital-only** sources are shown below. They sum to its capital uses; gap credit, interest/fees, reserve funding and operating receipts are additional cashflows in its [monthly ledger](local_positive-monthly.csv) and [six-month placement schedule](local_positive-semiannual.csv). Ordinary and green bonds are separate placements, never added again to a combined bond figure. Bond face units are IQD 1m; rounded placement envelopes are not additional cash raised.

| Capital source | Currency | Native amount | USD equivalent m |
| --- | --- | --- | --- |
| Government import cash | USD | 981,925,190 | 981.925 |
| Government local cash | IQD | 1,369,355,612,384 | 1053.350 |
| Chinese capital credit | USD | 981,925,190 | 981.925 |
| Ordinary capital bonds | IQD | 3,801,789,702,761 | 2924.454 |
| Green capital bonds | IQD | 1,169,639,545,510 | 899.723 |
| Senior bank capital credit | IQD | 1,657,143,082,757 | 1274.725 |
| Conditional climate capital grant | IQD | 32,500,000,000 | 25.000 |

Mezzanine replaces 10% of domestic residual capital borrowing; it is not extra capital on top of the uses. The IQD case has 6% cash coupon, 4% PIK, 2% arrangement fee and a 15-year balloon from each draw. Deferred cash coupon and PIK increase outstanding debt until maturity. Thereafter the overdue principal is retained with separately disclosed simple 10% contractual-interest sensitivity; arrears are not compounded and the balloon is not silently extended. Cash junior payments require senior DSCR of 1.20, funded reserves and actual residual cash; new gap draws/unfunded support cannot pay junior debt. No conversion, fresh equity or automatic refinancing is invented. Unpaid maturity balances/defaults remain visible. Mezzanine is structurally junior to senior debt and senior to equity, as described by [UNCITRAL](https://digitallibrary.un.org/record/272622/files/A_CN.9_458_Add.1-EN.pdf); the rates here are project sensitivities.

| Matched case / six-month placement schedule | CAPEX USD bn | USD capital intensity | Peak IQD gap tn | Terminal all debt IQD tn | Unfunded IQD tn | Junior defaulted vintages |
| --- | --- | --- | --- | --- | --- | --- |
| [revised_scope_buy](revised_scope_buy-semiannual.csv) | 8.276 | 28.00% | 13.000 | 11.781 | 0.984 | 0 |
| [local_all](local_all-semiannual.csv) | 8.151 | 23.96% | 13.000 | 11.781 | 0.804 | 0 |
| [local_positive](local_positive-semiannual.csv) | 8.141 | 24.12% | 13.000 | 11.781 | 0.772 | 0 |
| [local_positive_mezzanine](local_positive_mezzanine-semiannual.csv) | 8.141 | 24.12% | 12.971 | 19.019 | 0.000 | 85 |
| [local_positive_commercial_gap](local_positive_commercial_gap-semiannual.csv) | 8.141 | 24.12% | 13.000 | 13.000 | 22.151 | 0 |
| [local_positive_mezzanine_stress](local_positive_mezzanine_stress-semiannual.csv) | 8.141 | 24.12% | 13.000 | 41.317 | 20.451 | 85 |
| [grade-separation-penalty-0pct](grade-separation-penalty-0pct-semiannual.csv) | 8.379 | 23.84% | 13.000 | 11.781 | 1.269 | 0 |
| [grade-separation-penalty-25pct](grade-separation-penalty-25pct-semiannual.csv) | 7.913 | 24.41% | 13.000 | 11.781 | 0.277 | 0 |
| [grade-separation-penalty-50pct](grade-separation-penalty-50pct-semiannual.csv) | 7.447 | 25.01% | 12.136 | 10.774 | 0.000 | 0 |
| [local_positive_raw_price_stress](local_positive_raw_price_stress-semiannual.csv) | 8.248 | 24.63% | 13.000 | 11.781 | 0.976 | 0 |
| [local_positive_supplier_delay](local_positive_supplier_delay-semiannual.csv) | 8.141 | 24.12% | 13.000 | 11.734 | 0.853 | 0 |
| [construction_wage_content_stress](construction_wage_content_stress-semiannual.csv) | 8.696 | 23.60% | 13.000 | 11.781 | 1.912 | 0 |

The four positive-margin process options reduce capital from USD 8.276bn to USD 8.141bn, and imported invoice exposure from USD 2.317bn to USD 1.964bn. Half of that exposure is government USD cash and half Chinese USD credit; all other capital funding is IQD. The historical 148 km / USD 18bn third-party benchmark has a different scope and assumed full foreign-currency financing; this is a planning comparison, not a like-for-like tender saving. The 516.5 km catalogue's 46.4% population-access proxy is unchanged and is not surveyed pedestrian coverage.

**Current financial conclusion:** the four-process senior case still needs IQD 0.772tn of unsourced support and retains IQD 11.781tn of debt at the horizon. Its company NPV before finance is USD -4.734bn at the assumed nominal discount rate. Adding mezzanine does not change the underlying operating return: it leaves IQD 19.019tn of total debt and 85 unpaid junior vintages. It is not recommended as a cure for the funding deficit. Fare and OPEX indexation, kiosks/advertising and inherited additional receipts are already included; new verified capital, affordable revenue or accepted scope savings are still needed.

All cases use the same revised staff, depot and indexed fare/OPEX assumptions. Six months of scheduled senior service are reserved from the first draw; three months of OPEX plus explicit industrial working capital are restricted. This revised reserve policy differs from older reference cases, so compare matched cases in this table when judging mezzanine. Concessional 2% gap funding, grants/rights/additional income and enhanced green coupons are uncommitted; the 8% gap and high mezzanine-rate case expose that dependence. There are zero dividends. Cash/principal/PIK identities, maturity risk, monthly draws and six-month bond denominations are retained for every case.

Regenerate with `.venv/bin/python tools/automation/baghdad_programme_recalculation.py`; verify with `--check`. Complete installed scope, construction wage-content adjustment, local-pay survey, validated demand/timetable and supplier/lender agreements remain open.

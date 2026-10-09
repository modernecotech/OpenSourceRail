# Baghdad programme recalculation

Controlled planning basis, 2026-10-04; unquoted and uncommitted. This is the latest staffing/depot/local-production review. Existing cost and financing cases remain historical comparators; no survey, manufacturing qualification or lender commitment is created.

## Operating people and wages

The 600 stations require two concurrent staff during two normal eight-hour shifts: **2400 daily shift assignments**, not a headcount of people working every day. Retaining 20.5 service hours also requires 4.5 hours of separately funded late cover per station. Weekly cover, leave, training, sickness and handovers give **5964 station-cover FTE**, within **11459 permanent operating FTE**. Full-operation loaded payroll is **IQD 264.730bn/year** (USD 203.639m equivalent), indexed thereafter with OPEX.

The employee median is IQD 614,000 from the 2021 Labour Force Survey, cited in the [IMF 2023 report](https://www.imf.org/-/media/files/publications/cr/2023/english/1irqea2023002.pdf). Applying an assumed 5% annual index to 2026 gives IQD 783,637; the general-worker floor is **IQD 1,175,455/month**, 50% higher. Technical, supervisor, senior and director roles use 2.25/3/4/5 times that indexed proxy. This is a historical observation plus an editable index, not a measured current national median. Employer costs and overtime are priced separately. [Roles](workforce.csv) and [recruitment/cohorts](workforce.json) retain appointment and competence gates.

[ERP planning drafts](erp-planning-drafts.json) map the revised Staffing Plan, depot Project/Asset budgets and factory Workstations to native business records; they create no Employee, appointment, transaction or approval.

Construction workers, factory production/support workers and permanent operators are separate populations. [Construction](construction-workforce.json) applies explicit trade-crew allowances to actual work-package resource lanes/dates, counting overlapping use of the same lane once; its peak is 434 FTE. It is not a measured complete contractor crew schedule; revised depot and upstream factory construction crews still require their own work-package schedules. Construction labour is already inside contract rates; its unknown payroll-content overlap remains unpriced, preventing a duplicate charge. A separate wage-content stress increases assumed labour content (20% of affected contracts) by 50%, with incremental EPC once; it is an overlap sensitivity, not proof of contractor wage contents. Existing assembly wages are replaced using an explicitly assumed embedded payroll credit; component process labour is inside component unit prices. Paid production capacity above those productive hours is added separately, never charged twice.

The final-assembly establishment is 865 production FTE plus 130 support FTE. The scheduled order requires 177 paid months from month 18 through month 194; payroll follows this calendar, rather than dividing the order by a theoretical steady-state rate and losing ramp-up/idle months. Each upstream plant also funds its whole production establishment for that period, with the productive labour already in unit prices deducted once. These jobs are additional to permanent railway operations; no national order or permanent post-order subsidy is assumed.

## One depot per line, full-size trains and fleet

There are **54 line-local depots**, providing **2067 storage slots** for all six-car revenue/spare/reserve trains. Slots use the actual 111 m train plus 10 m clearance. Workshop bays follow annual bay-hour demand and usable bay capacity; parking slots are not maintenance bays. Station storage is an option without any capacity credit in this case. Full overnight-to-morning launch and throat conflicts remain unvalidated.

| Line | Trainsets/storage slots | Tracks | Workshop bays | Land envelope ha | Reference USD m |
| --- | --- | --- | --- | --- | --- |
| line-1 | 126 | 42 | 18 | 16.47 | 37.944 |
| line-2 | 123 | 41 | 17 | 16.02 | 42.930 |
| line-3 | 113 | 38 | 16 | 14.92 | 34.376 |
| line-4 | 97 | 33 | 14 | 13.05 | 30.553 |
| line-5 | 116 | 39 | 16 | 15.25 | 34.631 |
| line-6 | 119 | 40 | 17 | 15.70 | 36.145 |
| line-7 | 86 | 29 | 12 | 11.50 | 27.045 |
| line-8 | 102 | 34 | 15 | 13.49 | 32.127 |
| line-9 | 58 | 20 | 8 | 8.07 | 19.684 |
| line-10 | 17 | 6 | 3 | 2.89 | 9.849 |
| line-11 | 25 | 9 | 4 | 3.99 | 11.843 |
| line-12 | 23 | 8 | 4 | 3.67 | 11.618 |
| line-13 | 20 | 7 | 3 | 3.22 | 10.104 |
| line-14 | 19 | 7 | 3 | 3.22 | 10.074 |
| line-15 | 30 | 10 | 5 | 4.44 | 13.417 |
| line-16 | 23 | 8 | 4 | 3.67 | 11.618 |
| line-17 | 20 | 7 | 3 | 3.22 | 10.104 |
| line-18 | 21 | 7 | 3 | 3.22 | 10.134 |
| line-19 | 19 | 7 | 3 | 3.22 | 10.074 |
| line-20 | 20 | 7 | 3 | 3.22 | 10.104 |
| line-21 | 28 | 10 | 4 | 4.32 | 12.098 |
| line-22 | 17 | 6 | 3 | 2.89 | 9.849 |
| line-23 | 27 | 9 | 4 | 3.99 | 11.903 |
| line-24 | 31 | 11 | 5 | 4.77 | 13.612 |
| line-25 | 21 | 7 | 3 | 3.22 | 10.134 |
| line-26 | 19 | 7 | 3 | 3.22 | 10.074 |
| line-27 | 41 | 14 | 6 | 5.87 | 15.666 |
| line-28 | 25 | 9 | 4 | 3.99 | 11.843 |
| line-29 | 29 | 10 | 4 | 4.32 | 12.128 |
| line-30 | 24 | 8 | 4 | 3.67 | 11.648 |
| line-31 | 32 | 11 | 5 | 4.77 | 13.642 |
| line-32 | 25 | 9 | 4 | 3.99 | 11.843 |
| line-33 | 25 | 9 | 4 | 3.99 | 11.843 |
| line-34 | 23 | 8 | 4 | 3.67 | 11.618 |
| line-35 | 24 | 8 | 4 | 3.67 | 11.648 |
| line-36 | 25 | 9 | 4 | 3.99 | 11.843 |
| line-37 | 37 | 13 | 6 | 5.54 | 15.381 |
| line-38 | 19 | 7 | 3 | 3.22 | 10.074 |
| line-39 | 19 | 7 | 3 | 3.22 | 10.074 |
| line-40 | 20 | 7 | 3 | 3.22 | 10.104 |
| line-41 | 20 | 7 | 3 | 3.22 | 10.104 |
| line-42 | 16 | 6 | 3 | 2.89 | 9.819 |
| line-43 | 35 | 12 | 5 | 5.10 | 13.897 |
| line-44 | 32 | 11 | 5 | 4.77 | 13.642 |
| line-45 | 20 | 7 | 3 | 3.22 | 10.104 |
| line-46 | 25 | 9 | 4 | 3.99 | 11.843 |
| line-47 | 34 | 12 | 5 | 5.10 | 13.867 |
| line-48 | 17 | 6 | 3 | 2.89 | 9.849 |
| line-49 | 28 | 10 | 4 | 4.32 | 12.098 |
| line-50 | 38 | 13 | 6 | 5.54 | 15.411 |
| line-51 | 21 | 7 | 3 | 3.22 | 10.134 |
| line-52 | 29 | 10 | 4 | 4.32 | 12.128 |
| line-53 | 37 | 13 | 6 | 5.54 | 15.381 |
| line-54 | 27 | 9 | 4 | 3.99 | 11.903 |

Total depot reference: **USD 821.580m**, replacing the original USD 8m exactly once. Storage, workshop and access tracks, points, drainage/access, workshop shell/equipment/services, yard lighting/fire services, wash plant, wheel lathe, offices/stores and rescue/quarantine are visible. Access-track length is an editable allowance, not a connected site alignment. Existing depot PV/BESS is retained once. Land/title, utility relocation, actual soil/foundations, installed charger/grid upgrades and tax/duties remain unpriced. [Item register](depot-items.csv).

## Core elevated stations

The reworked core has 345 station platforms with raised-structure/access scope. The register replaces their catalogue allowance with a separately stated elevated reference, adding **USD 1147.980m direct**, with incremental EPC and operating maintenance once. Elevated interchange allowances are already present where catalogued; they receive no duplicate uplift. Other core stations use a 30% structure allowance plus USD 1m for vertical access. These are unquoted allowances, not released multi-level junction or station designs. [Core station register](core-elevated-stations.json).

## Iraqi component manufacture

| Product | Network quantity | Required units/year | Cells | Production/support FTE | Factory capital USD m | Unit make/buy USD | Whole-order margin USD m |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bogie | 24804 | 1820 | 21 | 98/15 | 34.298 | 15156/25000 | 189.277 |
| motor-inverter-set | 24804 | 1820 | 14 | 49/8 | 24.977 | 11078/15000 | 58.958 |
| battery-225kwh-pack | 12402 | 910 | 6 | 28/5 | 22.433 | 29828/45000 | 153.932 |
| door-cassette | 49608 | 3640 | 9 | 32/5 | 13.514 | 2023/3333 | 43.097 |
| window-cassette | 74412 | 5460 | 7 | 25/4 | 19.860 | 687/1111 | 1.450 |

[Make/buy inputs](component-make-buy.csv) price imported process machinery, Iraqi buildings/site work, qualification, residual imported inputs, local materials, graded labour, process overhead, fixed support and plant maintenance. Cells are sized to the existing train factory's required production rate, not a small demonstration line. The order is 2.790 GWh of gross onboard packs. Battery **pack assembly** is evaluated; imported cells/BMS remain. Bogie wheels/axles/bearings, motor inverters/magnets, door safety electronics and glazing feedstock also retain imports. Local manufacture does not mean zero USD input.

The buy case itemises these five imported completed products; the old blanket vehicle import percentage is retained only for other parent scope. This prevents replacing already-local scope with a second import credit. The all-product and positive-margin selections are separate unquoted cases. Whole-order margins are before finance/tax/risk; vendor prices, license, QA, process yield, supply commitments and first articles must validate them. No future national order pays Baghdad debt or makes an uneconomic line look profitable. Serial component qualification is assumed within the 18-month readiness target, not proven. A six-month supplier delay shifts rolling-stock invoices and opening/service cash, extends the full operating horizon and prices idle production payroll. A 25% raw-input price stress preserves the same selected facilities. Rejected/reworked product still needs a measured production replay. Existing final assembly tooling remains priced; upstream machinery is added without an unproven overlap credit.

## Paid journeys and transfers

Revenue remains a capacity-led sensitivity rather than a surveyed OD forecast. The reference uses one boarding per paid journey, a zero-transfer upper-bound assumption. Integrated-fare sensitivities use 1.25, 1.5 and 2 boardings per journey: only fare receipts are divided; kiosk/rental/advertising receipts, service, staffing and energy are retained. These are uncalibrated factors, not estimates of Baghdad travel. Physical access and surveyed OD/section loads must qualify any adopted demand forecast. [Demand handoff](../demand-bridge/README.md).

## More elevation and fewer bends

The current main design adopts the straight central elevated alignment. The screening policy allows up to 65% elevated and at least 25% at grade, subject to site/design acceptance. Baghdad currently has 63.19% elevated. Investigation windows around all 159 exceptional segments add 10.412 km of candidate at-grade conversion, reaching 64.39%; overlapping intervals are merged and existing viaduct/bridge lengths excluded. Approach length is at least 300.0 m from assumed height/gradient.

**Elevation alone removes no horizontal bend.** Wider-radius geometry, station moves, ROW, vertical alignment, ramps, egress, ground/utility evidence, crossings and whole-life costs must be designed together. The additional-elevation case includes only its base allowance; routing scores are excluded from money and the old 25%/50% penalty-removal cases are retired. Special designs and consequential installed costs remain unknown. The added standard civil allowance uses the conservative simple-span bearing index. [Candidate intervals](alignment-candidates.csv).

## Funding and mezzanine comparison

Government capital remains exactly 25% of the scenario total. Imported invoices receive 50% government USD cash / 50% Chinese USD credit. Remaining government cash, bonds, senior bank/gap credit and mezzanine are IQD. Government USD payment dates follow machinery/input invoices; the remaining appropriation is allocated proportionally to local invoices, so a machinery-heavy month need not be falsely limited to 25% government cash. Chinese supplier origin and export-credit eligibility are assumptions requiring vendor/lender confirmation. China Exim describes buyer credit for Chinese products, technologies and services; machinery eligibility is not a loan commitment ([official product description](https://english.eximbank.gov.cn/Business/CreditB/SupportingFT/201810/t20181016_6965.html)).

The positive-margin local-production senior case's **capital-only** sources are shown below. They sum to its capital uses; gap credit, interest/fees, reserve funding and operating receipts are additional cashflows in its [monthly ledger](local_positive-monthly.csv) and [six-month placement schedule](local_positive-semiannual.csv). Ordinary and green bonds are separate placements, never added again to a combined bond figure. Bond face units are IQD 1m; rounded placement envelopes are not additional cash raised.

| Capital source | Currency | Native amount | USD equivalent m |
| --- | --- | --- | --- |
| Government import cash | USD | 2,224,124,693 | 2224.125 |
| Government local cash | IQD | 3,415,800,252,172 | 2627.539 |
| Chinese capital credit | USD | 2,224,124,693 | 2224.125 |
| Ordinary capital bonds | IQD | 9,449,661,777,729 | 7268.971 |
| Green capital bonds | IQD | 2,548,556,941,307 | 1960.428 |
| Senior bank capital credit | IQD | 3,999,406,239,679 | 3076.466 |
| Conditional climate capital grant | IQD | 32,500,000,000 | 25.000 |

Mezzanine replaces 10% of domestic residual capital borrowing; it is not extra capital on top of the uses. The IQD case has 6% cash coupon, 4% PIK, 2% arrangement fee and a 15-year balloon from each draw. Deferred cash coupon and PIK increase outstanding debt until maturity. Thereafter the overdue principal is retained with separately disclosed simple 10% contractual-interest sensitivity; arrears are not compounded and the balloon is not silently extended. Cash junior payments require senior DSCR of 1.20, funded reserves and actual residual cash; new gap draws/unfunded support cannot pay junior debt. No conversion, fresh equity or automatic refinancing is invented. Unpaid maturity balances/defaults remain visible. Mezzanine is structurally junior to senior debt and senior to equity, as described by [UNCITRAL](https://digitallibrary.un.org/record/272622/files/A_CN.9_458_Add.1-EN.pdf); the rates here are project sensitivities.

| Matched case / six-month placement schedule | CAPEX USD bn | USD capital intensity | Peak IQD gap tn | Terminal all debt IQD tn | Unfunded IQD tn | Junior defaulted vintages |
| --- | --- | --- | --- | --- | --- | --- |
| [revised_scope_buy](revised_scope_buy-semiannual.csv) | 19.954 | 27.47% | 3.873 | 0.000 | 0.000 | 0 |
| [local_all](local_all-semiannual.csv) | 19.407 | 22.92% | 3.882 | 0.000 | 0.000 | 0 |
| [local_positive](local_positive-semiannual.csv) | 19.407 | 22.92% | 3.882 | 0.000 | 0.000 | 0 |
| [local_positive_mezzanine](local_positive_mezzanine-semiannual.csv) | 19.407 | 22.92% | 3.353 | 0.000 | 0.000 | 0 |
| [local_positive_commercial_gap](local_positive_commercial_gap-semiannual.csv) | 19.407 | 22.92% | 5.343 | 0.000 | 0.000 | 0 |
| [local_positive_mezzanine_stress](local_positive_mezzanine_stress-semiannual.csv) | 19.407 | 22.92% | 4.489 | 0.000 | 0.000 | 0 |
| [additional_elevation_base_allowance](additional_elevation_base_allowance-semiannual.csv) | 19.491 | 22.88% | 3.915 | 0.000 | 0.000 | 0 |
| [local_positive_raw_price_stress](local_positive_raw_price_stress-semiannual.csv) | 19.682 | 23.49% | 3.950 | 0.000 | 0.000 | 0 |
| [local_positive_supplier_delay](local_positive_supplier_delay-semiannual.csv) | 19.407 | 22.92% | 4.412 | 0.000 | 0.000 | 0 |
| [construction_wage_content_stress](construction_wage_content_stress-semiannual.csv) | 20.757 | 22.44% | 4.395 | 0.000 | 0.000 | 0 |
| [integrated_fare_1_25_boardings](integrated_fare_1_25_boardings-semiannual.csv) | 19.407 | 22.92% | 5.468 | 0.000 | 0.000 | 0 |
| [integrated_fare_1_5_boardings](integrated_fare_1_5_boardings-semiannual.csv) | 19.407 | 22.92% | 7.896 | 0.000 | 0.000 | 0 |
| [integrated_fare_2_boardings](integrated_fare_2_boardings-semiannual.csv) | 19.407 | 22.92% | 13.000 | 0.000 | 2.177 | 0 |

The 5 positive-margin process options reduce capital from USD 19.954bn to USD 19.407bn, and imported invoice exposure from USD 5.481bn to USD 4.448bn. Half of that exposure is government USD cash and half Chinese USD credit; all other capital funding is IQD. The historical 148 km / USD 18bn third-party benchmark has a different scope and assumed full foreign-currency financing; this is a planning comparison, not a like-for-like tender saving. The reworked 863.9 km network's 66.4% legacy routing-demand cell fraction is not population access. Its former resident multiplication is retired; see the [native population and transfer audit](../access/README.md).

**Current financial conclusion:** the positive-margin senior case records IQD 0.000tn of residual unsourced support after assumed facilities and retains IQD 0.000tn of debt at the horizon. Its company NPV before finance is USD 1.574bn at the assumed nominal discount rate. Adding mezzanine does not change the underlying operating return: it leaves IQD 0.000tn of total debt and 0 unpaid junior vintages. It is not recommended as a cure for the funding deficit. Fare and OPEX indexation, kiosks/advertising and inherited additional receipts are already included; new verified capital, affordable revenue or accepted scope savings are still needed.

All cases use the same revised staff, depot and indexed fare/OPEX assumptions. Six months of scheduled senior service are reserved from the first draw; three months of OPEX plus explicit industrial working capital are restricted. This revised reserve policy differs from older reference cases, so compare matched cases in this table when judging mezzanine. Concessional 2% gap funding, grants/rights/additional income and enhanced green coupons are uncommitted; the 8% gap and high mezzanine-rate case expose that dependence. There are zero dividends. Cash/principal/PIK identities, maturity risk, monthly draws and six-month bond denominations are retained for every case.

Regenerate with `.venv/bin/python tools/automation/baghdad_programme_recalculation.py`; verify with `--check`. Complete installed scope, construction wage-content adjustment, local-pay survey, validated demand/timetable and supplier/lender agreements remain open.

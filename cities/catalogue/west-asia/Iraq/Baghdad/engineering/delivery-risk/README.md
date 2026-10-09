# Baghdad frozen-resource delivery and funding study

These are deterministic disturbances, not P80/P90 dates or measured failure rates. All planned six-car trains must pass acceptance before their line opens. Selected stage cells, civil crew lanes and dispatch order remain fixed in every stress. No stress calls the capacity-sizing search.

The explicit segregated-path calendar books 16 exclusive running hours per train at the case availability, inside acceptance-bay occupation, with setup and clearance. This adds a conservative calendar audit to the published average-throughput check. Baseline lane order is preserved; a replanned optimal dispatch might recover some delay. Financial-close months include 30 pre-NTP working days and three commissioning months.

| Case | First/full month | Peak IQD gap debt, tn | Interest/fees USD eq, bn | Debt cleared month |
|---|---:|---:|---:|---:|
| calendar_baseline | 45/200 | 2.141 | 3.989 | 224 |
| factory_delay_6months | 51/205 | 2.419 | 4.180 | 229 |
| supplier_shortage_6months | 51/204 | 2.434 | 4.182 | 228 |
| half_staff_late_12months | 49/203 | 2.347 | 4.141 | 227 |
| rework_10pct | 46/206 | 2.220 | 4.119 | 230 |
| one_test_path_outage_6months | 45/200 | 2.177 | 4.000 | 224 |
| civil_access_6months | 47/206 | 2.147 | 3.990 | 230 |
| availability_75pct | 48/227 | 2.453 | 4.387 | 251 |
| availability_65pct | 51/256 | 2.866 | 4.813 | 280 |
| combined | 59/242 | 3.161 | 4.869 | 267 |
| combined_second_test_shift | 59/242 | 3.162 | 4.872 | 267 |
| availability_75pct_second_test_shift | 48/227 | 2.461 | 4.391 | 251 |
| civil_cycles_20pct_faster | 45/200 | 2.143 | 3.991 | 224 |
| civil_earliest_unchanged_cycles | 45/200 | 3.388 | 5.413 | 224 |
| civil_earliest_20pct_faster | 45/199 | 4.045 | 6.036 | 223 |
| availability_75pct_costed | 48/227 | 2.453 | 4.387 | 251 |
| availability_75pct_test_shift_costed | 48/227 | 2.461 | 4.391 | 251 |
| hiring_ramp_costed | 49/203 | 2.347 | 4.141 | 227 |
| supplier_shortage_costed | 51/204 | 2.434 | 4.182 | 228 |
| availability_75pct_structural_shift | 47/227 | 2.476 | 4.405 | 251 |
| availability_75pct_electrical_shift | 47/226 | 2.441 | 4.367 | 251 |
| availability_75pct_composite_shift | 47/223 | 2.407 | 4.337 | 248 |
| availability_75pct_all_stage_shifts | 45/200 | 2.210 | 4.029 | 224 |
| recruitment_training_recovery | 45/200 | 2.144 | 3.993 | 224 |
| supplier_expedite_recovery | 48/201 | 2.343 | 4.010 | 225 |
| temporary_first_article | 41/200 | 2.020 | 3.905 | 224 |
| combined_delay_costs | 59/242 | 3.167 | 4.871 | 267 |
| combined_lower_demand | 59/242 | 4.894 | 6.797 | 267 |
| combined_escalation | 59/242 | 4.238 | 8.622 | 267 |
| combined_finance_downside | 59/242 | 4.000 | 10.047 | Unfunded |
| joint_downside | 59/242 | 4.000 | 21.584 | Unfunded |
| domestic_placement_interrupted_recovered | 51/206 | 2.365 | 4.011 | 230 |
| export_credit_delayed_recovered | 51/206 | 2.115 | 3.932 | 230 |

## Separate productivity from investment timing

The corrected civil_cycles_20pct_faster case retains every rephased start floor and changes only civil occupation durations. A 1.0 multiplier is tested as an exact schedule identity, including running-path reservations and line openings. Civil_earliest_unchanged_cycles removes the spending delays at original durations; civil_earliest_20pct_faster changes both. Their costs must not be attributed to productivity alone. Earlier completion may still advance completion/retention invoices even when mobilisation timing is retained. These are diagnostic cycle assumptions with no added crews or accepted acceleration price.

## Recovery comparisons and priced assumptions

Factory cells and dispatch lane order remain fixed. Fixed curing, bonding, inspection and test holds are listed in baghdad-delivery-risk.toml as unqualified working-calendar equivalents. Shift compression applies only to the remaining staffed occupation; the additional 60-day first-article qualification is unchanged. At one shift the original schedule is preserved exactly. Cure elapsed hours and batch/test evidence must replace these assumed splits before adoption. The test-only option uses the same selected segregated paths with a second eight-hour test shift: 26 incremental staff and USD 0.75m direct lighting/training per selected path plus 7% EPC, and indexed payroll before and after fares. It does not repair upstream stage throughput. The single structural, electrical and composite options add four staffed hours/day to the named stage at unchanged bay count; the coordinated option applies this to all seven stages and funds the second test shift. Incremental production FTE is half each selected stage crew, paid at a 25% premium, with nonlabour shift costs equal to 25% of added payroll. Each stage adds a USD 1m installation/training allowance and USD 10,000 per added FTE plus EPC. These assumed shift efficiencies, relief and wage premiums need qualification.

Use availability_75pct_costed, hiring_ramp_costed and supplier_shortage_costed as matching delay-cost baselines for their respective recovery options. Recruitment recovery funds USD 10,000 per delayed half of the 1044 production positions plus EPC and tests a six-month rather than twelve-month staffing ramp. Supplier recovery charges an assumed IQD local logistics fee of 2% of city imported invoice value, indexed to payment, and tests a shortage cut from 130 to 65 working days; this is a causal scenario assumption, not a guaranteed delivery improvement. Foreign-currency freight reimbursement and invoice eligibility need quotations. Neither purchases another train nor credits an unspecified subsidy.

The temporary first-article option adds USD 35m direct facility/tooling and 7% EPC, ready at day 260 (12 planning months from NTP), plus 60 incremental support FTE until the permanent plant is ready. Only the already-planned prototype assembles there. Acceptance still waits for permanent bays and running paths at day 390, and series still waits for first-article qualification. All line fleets remain complete at opening. The temporary site and staff must have their own RFQs and acceptance; no shorter passenger section is folded into this option.

## Delay costs and combined financial downside

Original delivery-only cases remain lower-bound comparisons. Combined_delay_costs additionally prices extended direct production staffing plus 100 support FTE at the existing Iraqi labour proxy; it compares staffed span lengths so a pure start delay does not buy the same crew-months twice. Plant storage/insurance/utilities carrying uses 1% of direct plant capital per extra/idle year excluding wages. Civil prolongation adds 150 supervision FTE and nonlabour site overhead at 0.5% of city capital per year beyond baseline civil completion. All these incremental operating costs are charged monthly at 5% annual indexing; baseline train labour/materials already inside procurement are not repeated. Rework prices 83 affected trains at USD 25,000 each. Monthly incremental-cost files reconcile each allowance to the case OPEX ledger. Contingency, tax and contractor claims remain unquoted; these are not a funded risk reserve.

The downside ladder isolates 30% fewer paid trips plus 25% lower existing retail/advertising receipts, 5% annual capital escalation applied to each invoice at actual payment month from financial close, and weaker financing. Weaker financing removes assumed green enhancement, climate grants, development rights and additional net income, increases core coupons two percentage points, and replaces the 2%/IQD 13tn gap sensitivity with 8% credit at a 1% draw fee and IQD 4tn maximum outstanding. Chinese credit and government import cash remain USD, all domestic credit/bonds/cash IQD; government remains 25% of escalated capital. Separately, domestic_placement_interrupted_recovered and export_credit_delayed_recovered stop procurement/construction/production for 130 working days and price local remobilisation plus prolongation; repayment is conditional on subsequently placing the refused debt. Permanent refusal has no opening or repayment date: see the [funding gates and evidence execution package](../qualification/README.md), including denied amounts, escrow requirements and six-month placement shortfalls. No gap facility is used to conceal a refused core source.

Lower demand with combined delays leaves IQD 0.000tn terminal gap debt. Joint_downside applies all of those assumptions together and 7% rail OPEX inflation: IQD 14.916tn cumulative uncovered cash and IQD 0.000tn terminal gap debt. Uncovered support is a balancing requirement, not an extra government appropriation, loan or cash source. Its presence blocks any unconditional repayment claim even if the simulated debt eventually amortizes. Interest totals in such cases also assume the missing cash is supplied; they do not establish an executable financed programme.

Base fare and OPEX sensitivities remain 5% from financial close, with existing kiosks/advertising, separate receipts and each line revenue ramp included. No tickets are sold before opening. Capital escalation is absent from reference cases and explicit in the named escalation cases. Green/grant/rights and all financing availability remain uncommitted. No future national city cashflow supports Baghdad debt.

## Evidence needed before adopting a recovery plan

The [qualification register](qualification-register.csv) assigns owners, required measurements/RFQs and acceptance rules for production, suppliers, recruitment, civil quantities, depot/site fit, demand, funding and operation. Every row remains not demonstrated. No measurements or quotations were obtained by running this model. The baseline fleet and test-path margins follow the current [factory sizing](../factory/summary.json); they require measured cycles and acceptance trials. Shorter passenger sections require a separate route, turnback, charging, depot, fleet duty and safety/operating acceptance study; the present comparisons retain full fleets and existing operating scope.

Regenerate after the city controls, factory plan and Baghdad funding programme are current with `.venv/bin/python tools/automation/baghdad_delivery_stress.py`, then regenerate the proposal. Verify source/output bindings with `--check`.

[Scenario comparison](scenario-comparison.csv) · [Machine-readable assumptions/results](summary.json) · [Baseline half-year funding](calendar_baseline-six-month-finance.csv) · [Combined stress half-year funding](combined-six-month-finance.csv) · [Joint downside half-year funding](joint_downside-six-month-finance.csv)

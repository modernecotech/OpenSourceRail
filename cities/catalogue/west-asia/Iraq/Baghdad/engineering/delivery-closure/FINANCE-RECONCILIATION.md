# Delivery-cost financial reconciliation

These executable sensitivities preserve the original reference, then replace the original depot allowance once and replace labour/solar OPEX once. Incremental EPC is an explicit 7% allowance; qualification credit against the existing factory allowance is explicit. Paid training/assessment/supervised experience and additional commissioning specialists are separate pre-opening cash; no factory production wages are duplicated. Battery top-ups add only the shortfall above reserve contributions already in maintenance. Land, duties, utility diversions, spare inclusion, actual owner insurance and grid/charger upgrade capital remain unpriced.

| Case | Capital USD bn | Government USD bn equivalent | Peak gap debt IQD tn | Unfunded support IQD tn | Debt clear without unfunded cash month | Company before-finance cash NPV USD bn |
| --- | --- | --- | --- | --- | --- | --- |
| reference | 17.430 | 4.358 | 2.141 | 0.000 | 224 | 4.376 |
| reconciled_full_fleet | 17.891 | 4.473 | 2.854 | 0.000 | 226 | 2.760 |
| reconciled_fixed_original_government | 17.891 | 4.358 | 2.897 | 0.000 | 226 | 2.760 |
| reconciled_without_uncommitted_income | 17.891 | 4.473 | 3.587 | 0.000 | 226 | 2.760 |
| opening_fleet_supply_scaled | 16.330 | 4.083 | 5.398 | 0.000 | 261 | -2.405 |
| contracted_solar | 16.535 | 4.134 | 3.052 | 0.000 | 226 | 2.543 |
| installed_energy_supply_bound | 17.891 | 4.473 | 2.860 | 0.000 | 226 | 2.623 |
| simple_span_bearing_index | 18.128 | 4.532 | 2.931 | 0.000 | 226 | 2.656 |

The fixed-government case retains the original absolute government contribution and reallocates its USD downpayment within that ceiling. Other cases use 25% of their own capital; increased appropriation is not committed. In every case imports are funded 50% government USD/50% proposed Chinese USD credit; ordinary/green bonds, bank and gap credit remain IQD. All debt/reserve/buffer/principal/cash residuals reconcile. **Six-month bond units are placement requirements, not subscriptions.** Climate/rights/additional local income remain uncommitted in conditional cases; the dedicated case removes all these targets and green pricing benefits.

Opening-fleet procurement follows the selected supply case and its extra spare. Factory cost/capacity is retained, and opening dates follow the later of civil readiness and replayed fleet acceptance; paid receipts scale with reduced timetable supply and ramps. Future expansion dates and funding remain null. Contracted solar removes city-owned plant CAPEX but keeps provider plant resources visible and charges generation; a private provider, rights, prices and firm deliverability are not established. Company cash NPVs are not like-for-like complete resource NPVs.

[Summary and source-bound cases](finance-summary.json) include full monthly native-currency ledgers, six-month bond/loan sale and repayment schedules, fees, grace, early principal, buffers and terminal debt/cash. Only genuine surplus after all obligations and buffers can fund contractual voluntary repayment; uncovered support cannot fund it. No new public subsidy or tariff adoption is claimed. Baseline fares and OPEX retain 5% growth and the existing elasticity/income assumptions.

[Opening factory replay](opening-factory-replay.json) manufactures exactly 1138 planned trains, including the extra line-9 spare, with rebuilt finite factory queues. Dropped orders are removed from manufacturing and invoice cash; original expansion-capable factory CAPEX is retained. Openings are the later of civil readiness and replayed fleet acceptance; later dates flow through receipts, payroll, reserves and the operating horizon. Depots retain full eventual-network capacity; staffing, maintenance, reserve and site energy follow the lower supply. All sensitivities retain zero modelled dividends; retained cash is not distributable profit without taxes, covenants and approvals.

The `simple_span_bearing_index` sensitivity removes the bearing reduction only from existing standard Pi25 length, then adds the declared incremental EPC once. It inherits original civil invoice dates and procurement-origin proportions as assumptions, keeps government at 25%, splits assumed imports 50% USD government cash / 50% Chinese USD credit, and retains all other funding in IQD. Monthly/six-month ledgers, interest, fees, reserves and early repayment are recalculated. This is an unquoted index counterfactual, not a bearing supplier offer; finite end effects, connection costs, actual import eligibility and consequential foundations remain unpriced. OSR-US and special segments do not inherit Pi25 bearing quantities.


## Fare/demand/affordability sensitivities

| Base fare IQD | Paid-demand multiplier | 44-trip income share | Debt-clear month | Terminal gap IQD tn | Before-finance cash NPV USD bn |
| --- | --- | --- | --- | --- | --- |
| 1500 | 0.962 | 13.4% | 226 | 0.000 | 4.138 |
| 1750 | 0.918 | 15.6% | 226 | 0.000 | 5.947 |
| 2000 | 0.882 | 17.8% | 226 | 0.000 | 7.682 |
| 2500 | 0.825 | 22.3% | 226 | 0.000 | 10.971 |
| 3000 | 0.781 | 26.7% | 226 | 0.000 | 14.069 |

[Full results](fare-sensitivities.json) change the base fare once, retain existing peak/off-peak pricing and 5% annual fare/OPEX/income growth, reduce paid trips with the existing uncalibrated elasticity, and scale existing station commercial receipts with demand. Debt clearance and cash NPV are different tests. Conditional green/grant/rights/local-income targets and cheap IQD gap credit remain uncommitted. An assumed higher fare is not a sustainable tariff until OD, distributional affordability and actual service/credit conditions are accepted. The 44-trip share uses the historical income proxy and base fare before variable-price weighting, not measured disposable income.

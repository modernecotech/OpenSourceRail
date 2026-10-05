# Delivery-cost financial reconciliation

<!-- OSR CURRENT SCOPE CONTEXT -->
> **Original catalogue or earlier scope reference.** The figures and policies below retain their original assumptions; they are not the latest Baghdad staffing, depot, procurement or funding basis. See the [current Baghdad recalculation](../programme-recalculation/README.md) and [current city summary](../../README.md). National/portfolio totals have not been repriced with that conditional Baghdad option.
<!-- END OSR CURRENT SCOPE CONTEXT -->

These executable sensitivities preserve the original reference, then replace the original depot allowance once and replace labour/solar OPEX once. Incremental EPC is an explicit 7% allowance; qualification credit against the existing factory allowance is explicit. Paid training/assessment/supervised experience and additional commissioning specialists are separate pre-opening cash; no factory production wages are duplicated. Battery top-ups add only the shortfall above reserve contributions already in maintenance. Land, duties, utility diversions, spare inclusion, actual owner insurance and grid/charger upgrade capital remain unpriced.

| Case | Capital USD bn | Government USD bn equivalent | Peak gap debt IQD tn | Unfunded support IQD tn | Debt clear without unfunded cash month | Company before-finance cash NPV USD bn |
| --- | --- | --- | --- | --- | --- | --- |
| reference | 14.527 | 3.632 | 13.000 | 10.196 | None | -9.087 |
| reconciled_full_fleet | 14.692 | 3.673 | 13.000 | 21.696 | None | -10.197 |
| reconciled_fixed_original_government | 14.692 | 3.632 | 13.000 | 21.793 | None | -10.197 |
| reconciled_without_uncommitted_income | 14.692 | 3.673 | 13.000 | 23.480 | None | -10.197 |
| opening_fleet_supply_scaled | 14.109 | 3.527 | 13.000 | 33.348 | None | -10.595 |
| contracted_solar | 13.947 | 3.487 | 13.000 | 28.080 | None | -10.230 |
| installed_energy_supply_bound | 14.692 | 3.673 | 13.000 | 27.153 | None | -10.537 |
| simple_span_bearing_index | 14.786 | 3.696 | 13.000 | 21.863 | None | -10.265 |

The fixed-government case retains the original absolute government contribution and reallocates its USD downpayment within that ceiling. Other cases use 25% of their own capital; increased appropriation is not committed. In every case imports are funded 50% government USD/50% proposed Chinese USD credit; ordinary/green bonds, bank and gap credit remain IQD. All debt/reserve/buffer/principal/cash residuals reconcile. **Six-month bond units are placement requirements, not subscriptions.** Climate/rights/additional local income remain uncommitted in conditional cases; the dedicated case removes all these targets and green pricing benefits.

Opening-fleet procurement follows the selected supply case and its extra spare. Factory cost/capacity is retained, and opening dates follow the later of civil readiness and replayed fleet acceptance; paid receipts scale with reduced timetable supply and ramps. Future expansion dates and funding remain null. Contracted solar removes city-owned plant CAPEX but keeps provider plant resources visible and charges generation; a private provider, rights, prices and firm deliverability are not established. Company cash NPVs are not like-for-like complete resource NPVs.

[Summary and source-bound cases](finance-summary.json) include full monthly native-currency ledgers, six-month bond/loan sale and repayment schedules, fees, grace, early principal, buffers and terminal debt/cash. Only genuine surplus after all obligations and buffers can fund contractual voluntary repayment; uncovered support cannot fund it. No new public subsidy or tariff adoption is claimed. Baseline fares and OPEX retain 5% growth and the existing elasticity/income assumptions.

[Opening factory replay](opening-factory-replay.json) manufactures exactly 425 planned trains, including the extra line-9 spare, with rebuilt finite factory queues. Dropped orders are removed from manufacturing and invoice cash; original expansion-capable factory CAPEX is retained. Openings are the later of civil readiness and replayed fleet acceptance; later dates flow through receipts, payroll, reserves and the operating horizon. Depots retain full eventual-network capacity; staffing, maintenance, reserve and site energy follow the lower supply. All sensitivities retain zero modelled dividends; retained cash is not distributable profit without taxes, covenants and approvals.

The `simple_span_bearing_index` sensitivity removes the bearing reduction only from existing standard Pi25 length, then adds the declared incremental EPC once. It inherits original civil invoice dates and procurement-origin proportions as assumptions, keeps government at 25%, splits assumed imports 50% USD government cash / 50% Chinese USD credit, and retains all other funding in IQD. Monthly/six-month ledgers, interest, fees, reserves and early repayment are recalculated. This is an unquoted index counterfactual, not a bearing supplier offer; finite end effects, connection costs, actual import eligibility and consequential foundations remain unpriced. OSR-US and special segments do not inherit Pi25 bearing quantities.


## Fare/demand/affordability sensitivities

| Base fare IQD | Paid-demand multiplier | 44-trip income share | Debt-clear month | Terminal gap IQD tn | Before-finance cash NPV USD bn |
| --- | --- | --- | --- | --- | --- |
| 1500 | 0.962 | 13.4% | None | 13.000 | -9.899 |
| 1750 | 0.918 | 15.6% | None | 11.223 | -9.507 |
| 2000 | 0.882 | 17.8% | None | 7.066 | -9.131 |
| 2500 | 0.825 | 22.3% | None | 0.000 | -8.417 |
| 3000 | 0.781 | 26.7% | None | 0.000 | -7.744 |

[Full results](fare-sensitivities.json) change the base fare once, retain existing peak/off-peak pricing and 5% annual fare/OPEX/income growth, reduce paid trips with the existing uncalibrated elasticity, and scale existing station commercial receipts with demand. Debt clearance and cash NPV are different tests. Conditional green/grant/rights/local-income targets and cheap IQD gap credit remain uncommitted. An assumed higher fare is not a sustainable tariff until OD, distributional affordability and actual service/credit conditions are accepted. The 44-trip share uses the historical income proxy and base fare before variable-price weighting, not measured disposable income.

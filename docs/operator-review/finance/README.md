# Funding the railway and testing fare receipts

Use **Funding and fares** in the offline workshop kit or local Workbench. Select the railway, choose a funding term, then expand **Annual sources and uses in US$ millions**. A city finance team can use this table to identify its largest construction-year contribution, the first full year of debt payments and the years when renewals fall due. All amounts use constant 2026 US dollars. [Open the calculator](index.html) · [Download and use the workshop kit](../README.md)

## What the buyer needs in the first full year of service

| Railway and assumed opening | All capital paid by public budget | 50% borrowed at 4% real for 20 years | 50% borrowed at 7% real for 12 years |
|---|---:|---:|---:|
| Core 30 km, relative Year 5 | $30.5m | $68.2m | $95.0m |
| Baghdad seven corridors, 2032 scenario | $197.0m | $486.4m | $692.1m |
| Independent Baghdad citywide, 2036 scenario | $780.5m | $1,921.7m | $2,733.1m |

Each number is one year's buyer cash before fare receipts. The public-budget column assumes the buyer paid the capital during construction. The borrowing columns include scheduled principal and interest alongside that year's operations. Baghdad also has an illustrative export-credit case for a limited share of the equipment scope. Eligibility, guarantees and actual terms require a lender and a qualifying contract. [Baghdad annual cash schedules](../../../cities/Baghdad/financing-scenarios.json)

The [staffing calculator](../delivery/index.html) can pass a reconciled annual operating budget to this screen. In that case the annual table and opening-year cash use the replacement budget for the selected railway in every full service year. Construction draws, debt and renewals keep their published schedules. Select **Use published budget** to restore the comparison above. Use a recurring staffing case for long-term affordability. A commissioning crew needs a separately timed budget for its period of deployment.

## A worked Baghdad fare example

1. Select **Baghdad · seven corridors** and **50% debt · 4% · 20 years**. The opening year shows $197.0m of operations and $289.4m of annual debt service, giving $486.4m before receipts.
2. Enter **100** under **Annual paid journeys, millions** and **1** under **Net receipt per paid journey, US$**. In this illustration the operator collects $100m and needs another **$386.4m** to cover the opening year. Use local passenger counts, transfer rules, concessions and collection costs to replace these two assumptions.
3. Keep those fare inputs and switch to **50% debt · 7% · 12 years**. Opening-year buyer cash rises to $692.1m, leaving **$592.1m** to fund after the same receipts. Ask bidders for a separate cash price so the cost of financing can be compared at the same delivered scope.
4. Expand the annual table and read across a construction year, the first full service year and a renewal year. During construction, the buyer pays the part of capital it funds directly plus interest on debt drawn. Through operation, it pays running costs, scheduled renewals and debt service. The closing debt column records the unpaid principal.

The fare fields affect the opening-year comparison. The chart and annual table continue to show gross buyer cash before receipts. Filling the fields does not generate a 30-year demand forecast. [Illustrated funding screen](baghdad-funding.png)

## Inputs to replace before seeking funding

| Owner | Evidence for a proposal |
|---|---|
| Operator and fare authority | Paid journeys per year, expected receipts per paying journey, treatment of transfers and concessions, public-service payments and the cost of collection. |
| Project delivery team | Surveyed opening scope, capital milestones, partial openings, land and utility agreements, taxes, delivery risk and timings of grid and depot readiness. |
| Commercial and finance leads | Supplier cash and financed prices, lender draw and repayment schedules, rates, fees, currencies and guarantees. Record who pays and when, including any renewal funding obligation. |
| Maintainer | Renewal timing, equipment life, spare holdings and the quoted overhaul cost under the service and local repair terms being offered. |

The core illustration spreads expenditure across its 43-month construction programme and starts full operations in relative Year 5. Baghdad uses the planned annual draws in each network's own schedule. The model assumes midyear borrowing during construction, interest paid by the buyer, and repayment after opening. The timing and prices can change when suppliers, lenders and the authority agree an opening package. [Core estimate and renewals](../../reference-v07/cost/README.md) · [Baghdad delivery and cost basis](../../../cities/Baghdad/COST-AND-DELIVERY.md) · [Matched bids and Iraqi value added](../../../cities/Baghdad/BUYER-COMPARISON.md)

The published schedules can be checked from the repository root with `python3 docs/operator-review/finance/build.py --check`.

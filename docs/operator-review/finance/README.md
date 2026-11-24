# Funding the railway and testing fare receipts

Use **Funding and fares** in the offline workshop kit or local Workbench. Select the railway, choose a funding term, then expand **Annual sources and uses in US$ millions**. A city finance team can use this table to identify its largest construction-year contribution, the first full year of debt payments and the years when renewals fall due. All amounts use constant 2026 US dollars. [Open the calculator](index.html) · [Download and use the workshop kit](../README.md)

## What the buyer needs in the first full year of service

| Railway and assumed opening | All capital paid by public budget | 50% borrowed at 4% real for 20 years | 50% borrowed at 7% real for 12 years |
|---|---:|---:|---:|
| Core 30 km, relative Year 5 | $30.5m | $68.2m | $95.0m |
| Baghdad seven corridors, 2032 scenario | $197.0m | $486.4m | $692.1m |
| Independent Baghdad citywide, 2036 scenario | $780.5m | $1,921.7m | $2,733.1m |

Select **Original construction and operating allowances / own fares** to reproduce the Baghdad values above. Each number is one year's buyer cash before fare receipts. The public-budget column assumes the buyer paid the capital during construction. The borrowing columns include scheduled principal and interest alongside that year's operations. Baghdad also has an illustrative export-credit case for a limited share of the equipment scope. Eligibility, guarantees and actual terms require a lender and a qualifying contract. [Baghdad annual cash schedules](../../../cities/Baghdad/financing-scenarios.json)

The [staffing calculator](../delivery/index.html) can pass a reconciled annual operating budget to this screen. In that case the annual table and opening-year cash use the replacement budget for the selected railway in every full service year. Construction draws, debt and renewals keep their published schedules. Select **Use service allowance** to restore the comparison above. Use a recurring staffing case for long-term affordability. A commissioning crew needs a separately timed budget for its period of deployment.

## A worked Baghdad fare example

1. Open **Baghdad · seven corridors** with the central Iraqi case. Annual operations are **$185.7m**, including **$12.3m** payroll and **$50.1m** electricity.
2. The central case assumes **188.4m paid journeys** and a posted **IQD 750** flat ticket. The operator collects IQD 637.5 per paid journey, or **$79.5m/year** in total. Edit either field to price a different ridership or fare.
3. At 50% borrowing and 4% real over 20 years the city needs **$414.1m** after receipts in its first full service year. The higher-cost, lower-income case needs **$640.8m**. Changing the loan to 7% over 12 years with the central assumptions raises the annual requirement after fares to **$633.1m**.
4. Select **Baghdad · citywide** to compare the full budgeted operation with the 14 main routes. The calculator follows the service mileage for payroll, energy and receipts and retains the same construction debt. Expand the annual table for construction draws, renewals, principal and interest. [Iraq price and demand assumptions](../../../cities/Baghdad/IRAQ-ESTIMATES.md)

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

## Supplier pricing

For the Airport, use the corrected 17.46 km budgetary enquiry and retain each quoted lot scope ID. The pricing worksheet covers first articles for the core railway and seven-corridor references. Use it to compare cash terms and documented local value against the issued drawings. [Corrected Airport enquiry](../../../cities/Baghdad/engineering/simulation/audited-enquiry.zip) · [First-article worksheet](purchasing.html)

Use [Price a railway package](purchasing.html) to issue matching drawings, collect separate cash and financing terms, and compare first-article price with documented local value. The core railway and Baghdad use different equipment and source revisions. The downloadable enquiries record the issued drawing hashes. Start the screen from the [offline kit](../README.md#taking-drawings-to-a-supplier). Check the issued scopes with `python3 docs/operator-review/finance/enquiries.py --check` and exercise file import, comparison and export with `node docs/operator-review/finance/check-purchasing.mjs`.

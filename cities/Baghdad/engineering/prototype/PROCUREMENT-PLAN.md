# Baghdad Airport estimates and competitive quotations

This estimate and ERPNext workflow reproduce the earlier Airport opening. The historical priced configuration uses 12 route-km, 24 track-km, 30 traction supply sites and six six-car sets. Three sets run the service and three cover spare and maintenance needs. For new quotes, issue the exact drawing revision, quantities, delivery boundary and operating period for each revised layout. [Earlier Airport design and drawings](README.md)

Generate candidate-specific scopes from the [corrected 17.46 km Airport study](../simulation/ASSUMPTION-AUDIT.md) with `./osr design railway audit --packet build/baghdad-airport-paired6-enquiries.zip --layout paired6`. The estimate and ERPNext instructions below apply to the historical 12 km lot edition. Match returns for the corrected layout to its own scope IDs.

## Planning position at 23 November 2026

The 22 opening construction scopes reconcile to **$1,069.75m low, $1,124.32m central and $1,237.55m high**. Four first-full-year operations lines reconcile to $10.45m, $13.09m and $17.53m per year. Six named renewal events add to $233.85m undiscounted across the 30-year schedule. The register contains 54 enquiry or comparison lines. Fifty-three carry a planning price. Customs and tax treatment require the buyer's import and contract facts. [Download the buyer estimate (JSON)](sourcing-estimate.json)

| Where to seek competing offers | Price already available for planning | Decision a return can resolve |
|---|---|---|
| Trains and workshops | Six sets $50.88m. The first car is $1.70m–$3.39m. | Reconcile the first article, local assembly, spares, repair access and warranty with the fleet contract. The first car overlaps the repeat-series enquiry. |
| Guideway, stations and surveys | 2,400 elevated spans $107.94m. Six stations $78m. Ground investigation $0.65m–$3.73m. | Confirm installation and possession terms and which survey costs the design contract includes. |
| Power and controls | 30 source groups $348.47m. Six-site alternatives including estimated utility tie-ins are $106.05m–$200.22m single-path and $132.18m–$247.91m paired-path. | Seek a scope-matched radial offer and a separate offer for each alternative. Compare conductor paths, AC connections, outages, upkeep and renewals. |
| Opening and operations | Six-stop demand study $0.14m–$0.56m. Traction and controls trials $0.81m–$4.67m. Procurement assurance $0.32m–$1.49m. | Obtain fieldwork, test and owner-service prices and review the results separately. Match these enquiries against the parent design or testing allowance before adding them. |
| Owner, lender and statutory scope | Exceptional works and approval sensitivity $0.17m–$10.81m. Lender fees $1.34m–$6.19m. | Confirm authority, utility and lender terms. Tax and duties remain open. Public allocations need documentary evidence. |

The source record identifies published allowances, Iraqi market inputs, external procurement comparators and model-based allocations separately. For example, the demand-study benchmark uses Solano Transportation Authority's $280,000 study ceiling. The alignment-survey benchmark transfers a £400,000 Network Rail award with an explicit conversion and scope range. Each row records the applicable multiplier and exclusions. [Solano Transportation Authority board packet](https://www.sta.ca.gov/wp-content/uploads/2022/09/STA-Board-Packet_04-12-2023.pdf) · [Network Rail award notice](https://www.find-tender.service.gov.uk/Notice/002326-2026/PDF)

## Compare machinery and service returns

For the earlier schematic, open the [historical buyer issue](airport-enquiries.zip) and give each supplier a copy of `machine-offer.csv`. The [shop estimate](SHOP-COSTS.md) gives the quoted unit for every line, including retained machines, occupied hours and booked shifts. Suppliers may leave whole lines blank. Use one file per ERPNext Supplier Quotation. On a priced line enter the supplier and quotation identifiers, the positive unit price in USD, delivery terms and exclusions, and a reference to the signed evidence. Enter `matches` for the issued scope or `deviation` and explain the difference. Keep the original currency and agreed conversion basis with the ERP quotation.

Save the returns separately under the ignored build directory. Compare two or more with the command below. The output preserves each offered rate, extends it for the issued quantity where known, and shows the unit variance from the planning rate for matching scope. For a known subset, the extension covers only that subset. For an open quantity, compare unit rates and obtain the missing schedule before extending a total.

```sh
python3 -m cities.Baghdad.engineering.prototype.shop_offers build/supplier-a.csv build/supplier-b.csv > build/machine-comparison.json
```

Inside an extracted issue the same comparison runs with `python3 shop_offers.py supplier-a.csv supplier-b.csv`. The issue supplies the matching estimate.

Attach the comparison and each signed return to the corresponding ERP quotation under the parent lot. Reconcile overlaps, annual upkeep, acceptance support and taxes in the lot comparison before changing the budget. The attachment command runs locally and creates no purchase commitments.

## Use the buyer estimate

Run these commands from the repository root. The first displays each extended lot price in constant 2026 USD. The second produces the estimate for ERP import. The third displays the quantities, price sources and work included in the fleet enquiry. The example compares three invented offers and can be rerun without ERPNext.

```sh
mkdir -p build/airport-sourcing
./osr design railway sourcing
./osr design railway sourcing --json > build/airport-sourcing/estimate.json
./osr design railway sourcing --lot fleet --json
./osr design railway sourcing --demo
./osr design railway sourcing --check
```

Use each row's period, inclusion group, overlap and exclusions before budgeting. An extended price already covers the quantity shown. A contract for all station sites can contain platform interfaces that are also available as first-article enquiries. Price capital, annual operation and scheduled renewals in their own columns. A supplier must describe where testing, freight, installation, duties, warranty, maintenance and spares are included. A missing price stays open for a return.

The physical identity binds the RFQ to the Airport configuration. The opening evaluation identifies the original pricing and service inputs. A separate estimate edition binds the exact benchmark, quantities and lot definitions. Another feeder geometry, train formation or route requires a new physical candidate. A revised allowance on the same geometry requires a new price edition. The citywide network has its own selection. [Feeder configurations and cost boundaries](feeder-cash-guide.md)

A buyer without the CLI can download the JSON above. A maintainer can regenerate the canonical file with `./osr design railway sourcing --publish`. Publication reserves 2 MiB in the shared Git disk budget and checks the 20 GiB free-space floor before replacing the file.

## Run a competition in ERPNext

1. In the configured ERPNext site open **/airport-sourcing**. The pilot project is **Baghdad Airport opening procurement** in company **OpenSourceRail Evaluation**. Buyers can select another permitted Project by its ERPNext ID. The local project already contains the estimate, 54 non-stock lot Items and 159 buying Item Prices across the low, central and high USD lists. The buying team can also open the native Item Price list in Desk and filter on the relevant price list.
2. To load a new edition, choose **Load a buyer estimate into ERPNext**, select the canonical JSON, enter an existing leaf Item Group and save. The existing company buying price list stays the default. For local works whose scenario quantities change, the ERP unit price is the extended scenario cost divided by that scenario's own quantity. The comparison also shows how those rates extend at the RFQ quantity.
3. Select the estimate edition and lot. Enter one or more distinct Supplier master IDs, a required delivery date and the round number. **Create draft RFQ** opens the native Request for Quotation for buyer review. Each supplier's enabled website account needs the Supplier role and a single link on its own Supplier master under Portal Users. The buyer can review and submit the RFQ in Desk. Use a new round for changes to the supplier list. A price spread requires two comparable offers in the same round. Supplier email flags are disabled on these managed RFQs. Arrange access with the actual parties through the buyer's authorised channel.
4. An invited supplier signs in to **/airport-sourcing**, opens the issued enquiry and enters its quotation reference, unit rate, expiry, delivery days, warranty, exclusions, upkeep and renewal schedule. **Submit supplier quotation** creates the supplier's own native draft Supplier Quotation and returns its receipt. An identical retry preserves the first submission. For changed terms, the buyer opens another numbered round and retains the old round for audit.
5. The buyer opens **Project competitions** and chooses a round. Inspect each supplier's dated scope and native quotation. The comparison shows amount, difference from the central benchmark, scope exceptions, 30-year present value and the spreads for comparable offers. Expired, cancelled and unverified receipts remain outside the live comparison. Review lead time and warranty when judging otherwise similar prices.
6. For an attributed, current quotation covering an opening-direct lot, choose **Model replacement**. The buyer sees the original and revised central opening price. A selected quote credits its exact lot once. The cash calculation reapplies 8% design, 2.5% testing and 20% project allowance on the revised direct-plus-design-and-test base. Nested test lines, first articles, alternative feeders, annual operating budgets and scheduled renewals stay in their respective comparisons. The scenario is read-only. Signed contract and funding decisions remain with the buyer.

## Assign and run the work

Astra manages the dependencies and checks the combined result. Bounded research and implementation go to lower-cost agents. Site owners and authorised purchasing staff control release of tenders, supplier accounts, contract terms and award. An ordinary repository checkout is shared by the workers. Check output hashes and use database rollback for trial records.

| Work and owner | Inputs and dependency | Deliverable and completion check | Trial budget |
|---|---|---|---|
| Estimate, quantity surveyor using GPT-6.2 Sol | Published Airport dossier, current lot definitions and traceable price evidence | Give each lot a procurement unit, quantity, evidence date, central amount or explicit gap, price period, exclusions and supplier deliverables. Reconcile totals to the opening model and exercise invalid inputs. | 20 minutes initially, 8 MiB, focused tests under 3 minutes |
| Competitive procurement, ERP developer using GPT-6.2 Sol | Agreed estimate schema, existing Frappe v15 supplier identities, test-only buyer and suppliers | Stage one edition. Open an RFQ with at least two eligible suppliers. Capture independent returns. Check identity, retry, changed terms, confidentiality, validity and database rollback. | 25 minutes initially, 10 MiB, focused tests under 5 minutes |
| Comparison, Astra | Exact edition plus eligible native quotation lines and supplier declarations | Calculate direct and discounted differences. Show scope exceptions, missing annual costs and missing renewals. The fixture exercises a lower upfront price with higher operating cost and a cheap incomplete offer. | One deterministic pass per lot, 30 operating years |
| Buyer staging and independent verification, coordinator | Returned estimate and ERP adapter | Rebuild the estimate, stage and reread the lot prices in the evaluation company, repeat safely, check native records and business state, verify a second quotation case. | One local site and two passes. Reserve publication writes and observe the 20 GiB free-space floor. |
| Commercial follow-up, buyer and bounded pricing agent | Exact lot edition, authenticated supplier returns, signed scope clarifications | For each comparably priced lot, record delivered scope, exceptions, lead time, warranty, local support, currency and renewal years. Return any unmatched scope to the bidder for clarification. | One lot and one current submission per supplier per review. Reopen the edition if the common scope changes. |
| Opening cash and verification, finance and technical owners | Buyer-reviewed replacement, receipt and original documents | Replace the matched allowance once. Map overlaps across lots, phase payments, recalculate the 33-year public cash schedule and identify the remaining owner funding. Record separately which required inspections, measurements and approvals have arrived. | One documented finance return and one replay per revision |

Workers may edit their assigned scope and run focused fixtures. If a planning price has weak evidence, assign a short supplier enquiry or a bounded comparable-price search with the same location, specification and price period. If an engineering property requires a test, obtain competing prices for its test method, article, instrument, witnessing and report. The technical owner reviews the measured value against the approved limit after delivery. The plan keeps the vehicle, boarding, braking, electrical protection, site and evacuation obligations open through that review.

## Evaluate like-for-like offers

The buyer compares two prices. The first covers the exact lot quantity and period. The second adds operation and renewals over 30 years at a real annual discount rate of 4%. Keep all amounts in constant 2026 USD. Resolve any currency conversion, duties, freight, quote validity, escalation and scope deviations with the bidder. A quote with a scope exception stays visible with its amount and hold reason.

For a one-time lot, the calculator adds the direct price at year zero, the annual maintenance price at the end of each operating year and the scheduled renewals in their stated operating years. For an annual service lot, its price covers a year of the service. Enter zero for additional annual upkeep when all upkeep is included. For a scheduled lot, give the complete year-by-year renewal allocation adding to the direct quotation and zero separate upkeep. An empty renewal schedule is an explicit declaration that there are no priced renewal events. A missing schedule or annual amount keeps the present value open. Lot comparisons show how the spread changes between bidders without authorising an award.

Only a documented, buyer-reviewed offer covering a matching opening allowance can enter the public cash calculation. Map all other scopes to individual site rows or hold them for a revised budget model. Retain the signed originals and exact article, lot, supplier, document revision and attachment hashes. A submitted quote prices an obligation. The qualification record carries the measured results, approved limits and independent acceptance. [Finance returns and annual cash](commercial-guide.md) · [Commissioning procedures](../commissioning/COMMISSIONING.md)

## Executed run and reproduction

An Astra manager assigned price estimation and ERP implementation to two GPT-6.2 Sol workers. The workers returned the dated estimate and native RFQ/quotation adapter. The estimator then implemented the credit-once opening scenario. The manager integrated the CLI, browser forms, comparison and budget handoff. The following identifiers bind this run.

| Record | Identity |
|---|---|
| Airport physical candidate | `b38d4bd348cc57d8f3fab9696df06e5b35ba51380670aa8e566b7f89d9c5da01` |
| Opening evaluation | `6a0580105823dbd30dadde4e44f7d9032aee7a4b210e229950d17673a7231e87` |
| Independent citywide service selection | `d514564801b2df2cd8b2a06e59619b5aff6e0ec425256117120047a937c9aeaf` |
| Airport prototype ZIP SHA-256 | `55c5faf416d11dd32d71e0a6f51bcc1c3234abd2d32cdf4a8f6b8c587ae3c909` |
| Sourcing estimate edition | `83de4f2c3023521a1b9a9b02c436b10ffa9c24a67763d700da624e53036ad095` |
| Canonical estimate JSON SHA-256 | `acb39a064991388a813526db776bb85c49b446387b50ef31193599af48378870` |
| ERP rollback fixture comparison | `bd7757a3d02550ee98200cefa83f7f599264f87b593cb9b9953f34cf50ef50f3` |
| ERP rollback fixture budget scenario | `b52a8b7e6025481ed064c1fd78c1e4bce976fdd187ae71dd7fdd79990ffb9bea` |
| ERP rollback fixture receipt SHA-256 | `93ebef748159b264c23f254057e4f3b13465e91167f54763a9cfb1df38408efb` |

The recorded ERPNext trial identifies the estimate and quote comparison used to verify the buyer workflow. A replay creates fresh test record identities. [Recorded ERPNext trial](sourcing-verification.json)

Fourteen package tests checked the quote comparison, same-quantity pricing, opening reconciliation, alternative holds, mixed identities and double counting. ERPNext 15.121.2 with Frappe 15.120.1 recorded two software-fixture fleet offers for $108m and $120m from independent test supplier accounts. Substituting the $108m offer credited $50.88m, increased direct cost by $57.12m and raised the central opening to **$1,200.06m**. A third supplier's access was denied. Expiry removed both offers from the later comparison. The database transaction rolled back the RFQ, quotations and test suppliers. No invitation email entered the queue. The buyer estimate remains in the pilot database.

The mobile form check used Chromium 151 at 390 px and exercised submission to a test receiver. The native rollback exercised Frappe's supplier page rendering, authenticated supplier methods, buyer comparison and opening scenario. Simultaneous submissions, externally hosted accounts, supplier identity verification, market price validity and physical trials remain outside those checks. A separate one-supplier round accepted its offer and left the competitive spread open.

```sh
python3 -m unittest -v \
  cities.Baghdad.engineering.prototype.test_sourcing_estimates \
  cities.Baghdad.engineering.prototype.test_sourcing_comparison \
  cities.Baghdad.engineering.prototype.test_sourcing_scenario
./osr design railway sourcing --check
python3 - <<'PYTEST'
from pathlib import Path
import subprocess
fixture = Path("deployment/erpnext/tests/verify-sourcing.py").read_text()
with Path("cities/Baghdad/engineering/prototype/sourcing-estimate.json").open("rb") as source:
    subprocess.run(["docker", "exec", "-i", "osr-maglev-pilot-backend-1",
                    "./env/bin/python", "-c", fixture], stdin=source, check=True)
PYTEST
```

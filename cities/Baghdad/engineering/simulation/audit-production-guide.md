# Airport workshop and partial owner cash

The workshop plan takes its train count and annual energy, mileage and fare assumptions from the normal moving-service day for the audited alignment. Cash follows completed passenger journeys. The model applies the matching demand record's aggregate paying share and the published net receipt per paid journey. The operator needs actual paying journeys and net fare data. Where a replay ends with incomplete workings, the annual mileage, energy and fare results scale the service completed in that day for cost sensitivity. Booked and operated kilometres cover passenger, positioning and yard movements. The receipt breaks down the booked total and reports completed trip counts. Operated distance includes any partial workings. [Moving-service model](motion_power.py) · [Demand and alignment](ALIGNMENT-DEMAND.md)

The fixed girder cost replaces the historic span allowance and standard haul proxy. The modeled works count full standard beams, bearings and foundations, their reinforcement allowances and their casting, transport and erection units. A partial end bay requires its own design, price and schedule. Exceptional ground, crossings, haul distance, yard access, and the remaining tooling allocation await returns. Civil inspections are disclosed outside programme cash while the buyer reconciles overlap with the historical maintenance provision. Standard bearing renewal enters operating year 20. The revised feeder package and recurring upkeep require a matched layout offer. The archive rates following the historical track, fleet, station and service quantities remain estimates. [High-load civil model and rate basis](../mechanical/civil/README.md) · [Historic procurement lots](../prototype/sourcing-estimate.json)

The schedule runs normal releases, a 30-workday material delay, 75% workcell availability, and rejection plus remake of the first vehicle article. A separate 48-hour mould-dwell sensitivity uses the same eight beam positions as the 24-hour source route; it does not assume a purchased capacity increase or qualified cure. It reuses the released factory workcell hours, crew capacities and archived stock patterns. Larger girder hours use the existing workload sensitivity. Workcells can resequence under delayed releases. Site setup, temporary works, closure bays, delivery constraints and actual availability can change these dates. Alloy or hybrid manufacturing requires its own material-specific CAM and workcell returns. The factory completion workday maps to a service opening year using 250 effective workdays per year and the inherited year-four opening floor. Each scenario carries its material release, availability, article gate and mould assumptions, beam position occupancy and peak (including curing and associated holds), and opening slip. Current modeled completions are about 449 normal, 490 delayed material, 772 reduced capacity, 501 rejected article and 601 extended mould-dwell workdays. Only reduced capacity moves opening from year four to year five. The other delays stay within the year-four opening floor and leave priced cash timing unchanged. [Factory planning method](production-guide.md)

Low, base and high price cases use constant 2026 USD. Partial cash uses 30 operating years and 4% real discounting, with historical opening design, testing and contingency factors. Scenario phasing moves those same priced opening, operating and renewal amounts in calendar time; its present-value difference from normal is a timing comparison, not an additional cost line. A scenario opening in the same year points to `cash.profiles`; a later opening carries complete low, base and high annual ledgers in `price_profiles`. The disruption increment remains unknown, and the timing difference must not be added to the already rephased present value. The 256 seeded stress draws describe the selected rate ranges, correlated changes, opening slips and a demand residual; they are a separate sensitivity and must not be summed with factory scenario ledgers. Return freight, utilities, taxes, finance, extra approval work, disruption claims and supplier performance remain owner exposures. Statistical confidence remains open pending calibrated inputs.

The cash receipt lists unpriced lots by opening, annual operation and renewal alongside its priced subtotals. The archived feeder estimates cover different electrical duties and layouts. The audit ledger shows any buyer-referenced opening or annual upkeep price separately. Without an owner replacement plan, feeder renewal remains an untimed exposure. The closure bay and other owner exposures also remain outside priced cash until their quantities, scope and prices can be established.

## Source-bound feeder replacements

Use `--renewals` for an owner-authored replacement plan tied to an issued alignment and physical feeder. The JSON schema is `baghdad-airport-feeder-renewals/1`; its `layouts` object may contain `paired6` and/or `radial30`. Each layout needs `alignment_id`, `feeder_physical_id`, an ISO `basis_date`, an adjacent `source_document`, its SHA-256, and nonempty `lots`. Each lot states a unique name, equipment class, replacement quantity, operating year 1–30, `price_usd` as low/base/high complete-lot prices in constant 2026 USD **or `null` when unknown**, and nonempty exclusions. Unknown prices remain open in cash but still receive a complete buyer quotation and ERPNext scope. The model checks that the quantity does not exceed its topology population and that lots of one class in one year do not cumulatively exceed that population. Counts of source groups, circuits, ties and test points must be whole integers; protected track-km may be fractional. `dc_source_groups` equals the source-site count; `protected_track_km` equals two times route length; `outgoing_circuits` and `midpoint_ties` follow the modeled section counts; `branch_disconnect_and_test_points` exists for the paired path layout. These are **modeled equipment populations**, not a verified installed bill of materials. The owner must reconcile them with an installed equipment register before treating replacement coverage as complete.

This is the exact JSON shape for a **synthetic example**. Replace both IDs, the source filename and digest, quantities and prices with reviewed project values. The source file must sit beside the JSON.

```json
{
  "schema": "baghdad-airport-feeder-renewals/1",
  "layouts": {
    "paired6": {
      "alignment_id": "COPY_THE_ALIGNMENT_ID_FROM_THE_AUDIT",
      "feeder_physical_id": "COPY_THE_PAIRED6_FEEDER_PHYSICAL_ID",
      "source_document": "owner-feeder-schedule.txt",
      "source_sha256": "COPY_THE_SHA256_OF_OWNER_FEEDER_SCHEDULE",
      "basis_date": "2026-11-24",
      "lots": [
        {
          "lot_id": "source-electronics-year-12",
          "equipment_class": "dc_source_groups",
          "replace_quantity": 2,
          "operating_year": 12,
          "price_usd": {"low": 400000, "base": 500000, "high": 600000},
          "exclusions": ["source civil works", "annual maintenance"]
        },
        {
          "lot_id": "test-points-year-22",
          "equipment_class": "branch_disconnect_and_test_points",
          "replace_quantity": 2,
          "operating_year": 22,
          "price_usd": null,
          "exclusions": ["annual inspection", "new feeder cable"]
        }
      ]
    }
  }
}
```

```sh
python3 -m cities.Baghdad.engineering.simulation.assumption_audit --json > build/airport-baseline.json
sha256sum build/owner-feeder-schedule.txt
python3 -m cities.Baghdad.engineering.simulation.assumption_audit \
  --renewals build/feeder-renewals.json --json > build/airport-with-renewals.json
```

Read the IDs from `alignment.alignment_id` and `power_days` for the matching topology in the baseline JSON. For an owner plan, the audit excludes the four archived feeder renewal allowances from that layout's priced cash and records each excluded historical allowance, source price and year under `feeder_scope.renewal_scope.displaced_archived_allowances`. The named replacement enters its actual operating year. `feeder-renewals` remains unpriced for unlisted equipment or later replacement events; a purchaser risk line cannot substitute that whole residual over named lots. It must identify a narrower, nonoverlapping exposure. A comparison of feeders with different named renewal scopes cannot claim a price parity or saving.

Each named lot receives its own `scope_id` in `production.<layout>.pricings`. The buyer can collect competing returns in the ordinary `--offers` file and award one complete matching scope. A verified enquiry containing that lot can be converted with `audit_erpnext` into a scheduled ERPNext estimate Item whose `operating_year`, complete quantity and scope ID match the audit. Retain the owner source document with the return; the priced estimate and ERP quotation do not authenticate its equipment population or replacement interval.

## Itemised owner risk sensitivity

The optional `risk_return` argument to `audit_production.evaluate` accepts a JSON-compatible purchaser return bound to the audit vehicle `candidate_id`, `alignment_id`, feeder physical ID, civil audit row ID and exact `cash_basis_id`. First evaluate the ordinary ledger, then copy `cash.owner_risk_sensitivity.cash_basis_id` into the return. The ID covers the demand and working-day context, scoped priced and unpriced lots, any accepted offer substitutions, nominal cash profiles, discount rate and opening year. A changed offer, demand or timetable needs a fresh baseline and risk review. This is an **uncalibrated digital sensitivity**: no local observed loss distribution, supplier claim series or approved owner risk allowance is available. The ordinary `cash.profiles` retain the historical 20% opening contingency after the 8% design and 2.5% test factors as the nominal comparator. A risk line has its own ID, description, documented evidence basis, exclusions, period, low/base/high cost bounds in constant 2026 USD and ISO basis date. `opening-direct` and `first-full-year-operations` use `operating_year: null`; a `renewal-schedule` line must name operating year 1–30.

Use `cash_treatment: "exposure-only"` while scope or overlap is unresolved. These lines stay in the itemised record and never enter priced cash. A line may enter `cash.owner_risk_sensitivity.revised_profiles` only with `cash_treatment: "substitute-unpriced-lot"`, one matching unpriced lot ID, and a documented low/base/high allocation of any overlap with the inherited opening contingency. The calculation deducts that allocation from the line's gross range and limits total opening allocations to the historical contingency pool. Annual and renewal lines cannot draw against opening contingency. The resulting net increment is added once in the last pre-opening year, each of 30 operating years, or the declared renewal year; no design, test or contingency multiplier is added again. The nominal ledger, unpriced-lot list and factory-disruption ledgers stay intact. The revised cash is illustrative and does not qualify a price, award or reserve. An overlap assertion is a purchaser input requiring independent review, not a measured fact.

For example, a returned line for `revised-feeder-package` can identify a low/base/high installed range, list excluded feeder upkeep and renewals, and disclose a separately evidenced opening-contingency allocation. Without that allocation and its basis, keep the line exposure-only. The return schema requires `candidate_id`, `alignment_id`, `feeder_physical_id`, `civil_row_id`, `cash_basis_id`, `currency`, `basis_date`, `calibration: "uncalibrated"` and `lines`. The feeder ID is the digest of the matching alignment ID and physical feeder layout; the civil ID is the selected `audit_row_id`. Each line requires `risk_id`, `description`, `evidence_basis`, `cost_exclusions`, `period`, `operating_year`, `range_usd`, `cash_treatment`, `substitutes_unpriced_lot_id`, `historical_contingency_overlap_usd` and `overlap_basis`. The three amount dictionaries have `low`, `base` and `high` keys. Exposure-only lines set the last three substitution/overlap fields to `null`. The buyer-side CLI adapter must validate and pass the return through the evaluation before a revised packet is issued.

The budgetary packet carries a separate rail-side feeder planning sensitivity in `engineering/feeder.json`. It applies the 23 November 2026 rate basis to the issued site count, two-track length, breakers, midpoint ties and paired disconnect or test points. The converter allowance applies the archived base site cost and marginal MW rate to a proxy from the largest source current in valid normal, abnormal and matching high-mass replays. Conductor costs use the archived split between shared structure and resistance-sensitive paths. Current and resistance provide rate inputs. Equipment nameplate, conductor cross-section, hot-circuit and fault ratings, utility works, site installation details and renewals still require returns.

For the 17.461 km paired six-site working alignment, the rail-side direct allowances are **$139.0m, $176.7m and $225.8m** in the low, base and high cases, in constant 2026 USD. At base, paths account for $121.0m, supply sites for $52.8m and switches and branch points for $2.9m. Annual rail-side upkeep varies from **$0.69m to $4.52m**, with a **$1.77m** base. The radial layouts use fixed published opening rates at the reference resistance with varied upkeep fractions. These figures stay outside posted cash and direct comparison of prices requires matched service and complete scopes. A comparison may show the difference between priced present-value subtotals. Price parity requires matching ordinary mileage and journeys, passing operating screens and comparable trips and passenger volumes in every specified outage and high-mass case. The priced civil scope, unpriced lots, currency, real discount rate and service opening year must also match. The default radial and paired layouts deliver different outage service, so their priced subtotals do not establish a break-even feeder price. [Dated price register](../prototype/sourcing-estimate.json) · [Rate settings](../../system.toml)

Each supplier enquiry binds its complete lot, quantities, timing, physical geometry, working day, rate basis, feeder and currency under a scope ID. The priced signal, wayside braking and land allowances count route-km. Track lots count each track separately. Renewal scope records the number of trainsets, bearings or kilometres covered by the event. A buyer-referenced complete offer replaces the matching line in the cash ledger and retains its displaced price. Addressable training, local labour and shop work are recorded within parent lots. An offer's domestic-value declaration requires itemized material and service origin plus invoice and production evidence before the buyer can report verified Iraqi participation.

## Use the corrected enquiry in ERPNext

With a verified budgetary packet, generate an estimate edition for the existing buyer upload in `/airport-sourcing`. Use the buyer's edition date in place of the example date. The corrected edition retains its own audit, packet and candidate IDs. Each ERPNext Item prices a single complete lot. The description, engineering files and scope ID retain the exact physical quantity and unit, including kilometres beyond ERPNext quotation precision. Unknown prices generate no Item Price. The buyer can review and create a draft RFQ through the existing workflow. [ERPNext sourcing workflow](../../../../deployment/erpnext/README.md)

The example uses the six-site enquiry. For the 30-site layout, substitute `audited-enquiry-radial30.zip`. Each published packet has its own trusted issue, evaluation, candidate and layout pins. To use a separately issued packet, supply its path and pass `--issue-id` with the ID obtained independently from the buyer's issue record. Use the same trusted ID for staging and quotation replay. Give invited suppliers the issued packet through the buyer's document channel before they quote. The supplier portal shows the packet issue, lot scope ID and physical quantity to match against `pricing/production.json`. [Published six-site enquiry](audited-enquiry.zip)

Issue the supplier ZIP from the audit before entering offers, awards, erection quotations, vehicle evidence or feeder evidence. Review any survey and observed-demand source references included with a custom engineering scope before sharing it. Use `--json` for buyer-side audit results with returns and retain them with the original documents in the buyer's workspace.

```sh
python3 -m cities.Baghdad.engineering.simulation.audit_erpnext \
  cities/Baghdad/engineering/simulation/audited-enquiry.zip \
  2026-11-24 build/airport-erp-estimate.json
```

For a corrected RFQ, save **Comparison JSON for the corrected Airport audit** from the buyer portal as `build/erp-comparison.json`. In `build/erp-buyer-reviews.json`, provide a JSON list with `quotation`, `buyer_review_reference` and `quotation_document` for each reviewed complete offer. The document path is relative to the working directory unless absolute. Add `buyer_award_reference` only to the offer the buyer explicitly selected for that lot. The adapter hashes the original quotation document and retains the native project, RFQ, lot, supplier, quotation, comparison IDs and dates alongside the review reference. It requires a unique supplier trace for a submitted RFQ, with the comparison date between quotation receipt and expiry. It carries the complete quoted amount for the matched estimate edition, lot and period. Additional upkeep and renewal terms need their own matched cash scope. Historical opening estimates continue to use their own opening-budget comparison in the portal.

```sh
python3 -m cities.Baghdad.engineering.simulation.audit_erpnext \
  cities/Baghdad/engineering/simulation/audited-enquiry.zip \
  2026-11-24 build/buyer-offers.json \
  --comparison build/erp-comparison.json --reviews build/erp-buyer-reviews.json
```

The generated buyer-offers JSON covers one RFQ. Combine the offer and award lists under their existing layout keys when reviewing several lots together, then replay the original audit with `--offers build/buyer-offers.json`. Retain the comparison directly from the authorised buyer session and a readable, nonempty copy of the original quotation. The recorded digests identify the captured bytes and comparison data. The buyer verifies supplier authorship and checks the document against the native quotation. Native draft creation, supplier submission and purchase decisions remain with the authorised ERPNext users.

The Airport assumption audit includes the civil and service child identities and the workshop scope ledger. Reproduce the targeted checks from the repository root.

```sh
python3 -m unittest cities.Baghdad.engineering.simulation.test_audit_production \
  cities.Baghdad.engineering.simulation.test_audit_packet
```

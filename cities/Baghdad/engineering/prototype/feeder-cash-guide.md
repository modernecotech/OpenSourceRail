# Compare two feeder bids against the Airport cash schedule

Use this calculation when suppliers return prices for the 30-site radial proposal and one six-site option. The result shows how much more or less the buyer would draw, borrow and pay in each of the 33 programme years if the prices covered equivalent work. A negative number means the six-site design costs less for the compared scope. The opening price for the six-site railway remains unresolved.

## Prepare the returns

Start with `returns/priced_radial-feeder.json` and either `returns/six_site_parallel-feeder.json` or `returns/six_site_quotation-feeder.json` from the **same** Airport prototype dossier. Preserve each topology, chainage, design and evaluation identity. The radial option covers 30 rectifier sites, 116 outgoing circuits and 58 midpoint ties. Each six-site enquiry covers six rectifier sites, 20 circuits and 10 ties. Both alternatives serve the same 24 track-km. The paired-circuit version needs both positive and return branches priced.

In each return enter `record_kind`, `document_revision` and `coverage`. Use the supplier's installed prices in constant 2026 USD for all four direct scopes. Include annual upkeep and renewal prices by operating year 1–30. An explicit zero records a quoted zero, and an empty renewal object records an explicit schedule with no expenditure. A null amount keeps cash comparison pending. Retain the original signed bid, the technical exclusions and any utility offer. Mark an internal trial as `engineering-sensitivity`.

Run from the repository root with the paths to the two completed files.

```sh
.venv/bin/python -m cities.Baghdad.engineering.prototype.feeder_cash \
  --radial radial.json --alternative six-site.json > cash-difference.json
```

Check both supplier scopes for utility connections. Generate the optional local scope review with the exact same bid files.

```sh
.venv/bin/python -m cities.Baghdad.engineering.prototype.feeder_cash \
  --radial radial.json --alternative six-site.json --scope-template > scope-review.json
```

Enter the two bid filenames under `bid_document`, the reviewer's supporting filename under `scope_review_document`, and a `documents` entry containing each original file's `issuer`, ISO calendar `date` and lowercase hex `sha256`. Preserve the generated return IDs. Set `offsite_boundary` to `included in both bids` with `separate_installed_offsite_usd` null, or to `excluded from both bids` with a complete `{"radial": ..., "alternative": ...}` pair in 2026 USD. Verify in the source records that any associated recurring offsite service and renewal is included in each complete upkeep and renewal schedule. Resolve mixed boundaries with the suppliers. With no review the model holds separate offsite costs constant and marks the boundary unconfirmed. Hash checks establish file custody. The buyer authenticates the issuer and reviews what each price covers.

```sh
.venv/bin/python -m cities.Baghdad.engineering.prototype.feeder_cash \
  --radial radial.json --alternative six-site.json \
  --scope-review scope-review.json --documents originals > cash-difference.json
```

An optional `--finance-return finance.json` supplies other documented opening inputs using the same originals directory. Remove overlapping commercial line-power lots and separate offsite replacement rows from that return before comparing these two bids.

## Read the annual difference

The model subtracts the radial amount from the six-site amount separately for each direct scope, upkeep and each renewal year. The two bids themselves provide the displaced prices. Any separate reviewed offsite difference enters the direct sum once. The model spreads the direct difference over 20%, 45% and 35% construction draws, finances 50% at 4% real over 20 years and applies upkeep for 30 operating years. The third and final programme years each have half a year of operation. Renewal year 1 maps to programme year 4 under the opening's financing convention. The whole-life difference discounts operating costs at 4% real and treats capital as an upfront cost. The annual cash rows show construction interest and repayment separately.

The radial opening budget includes procurement, offsite, overhead and commissioning allowances with potentially overlapping boundaries. Adding two full priced offers to that budget or deducting the generic 30-site allowance from a six-site offer would mix price bases. Use the annual differences as a sensitivity pending a reconciled scope ledger. Owner overhead and contingency, energy losses, protection redesign, access rights and exceptional utility works can change the buyer's eventual cost. Funding decisions and electrical qualification require their own evidence.

# Airport field returns and buyer cash

Use the finance form from the prototype packet whose car and feeder you are pricing. A return updates the central planning estimate and the 33-year buyer cash table. The first three years include construction draws. Passenger service starts halfway through year three, with 30 years of service across the schedule.

## Prepare a return

Extract `returns/finance.json` from `airport-prototype.zip` to a working directory. Put each original attachment in that same directory. Keep the candidate, opening evaluation, price basis and supplier-form identities from the exported file. If the supplier prices a different train, request its matching form.

| Field | What to enter |
|---|---|
| `documents` | A mapping from local filename to an object with `sha256`, `issuer` and `date`. Use a full SHA-256 hex digest, the source organisation or person, and an ISO calendar date such as `2026-11-23`. |
| `site_replacements` | Use an exact local works row name. Its object takes `document`, `unit`, `quantity` and `unit_usd`. Use the original unit, the full replacement quantity and a positive direct price per unit in constant 2026 USD. A documented quantity of zero removes that row's direct allowance. Count forecourts, turnouts, sites and crossings in whole units. |
| `supplier_prices.lots` | Use one of `trainsets`, `line_power`, `civil` or `stations`. Its object takes `review_reference` (attachment filename), `direct_price_usd_m` (full direct replacement in millions of USD), `annual_maintenance_change_usd_m` (signed change in annual upkeep) and `renewal_changes_usd_m` (signed changes by operating year from 1 to 30, with string year keys). Leave unreturned lots null. |
| `demand_survey` | Enter `document`, `sample_date_from`, `sample_date_to`, `observed_days`, `od` and `net_usd_per_paid_journey`. Each origin–destination row takes `from`, `to`, `all` and `paying`. Use the six stop IDs `Airport-00` through `Airport-05`. Enter each direction separately and each pair only once. |
| `public_allocations_usd_m` | Map each funded **construction-relative** year from `"1"` to `"33"` to `{"document":"budget.pdf","amount":12.5}`. Amounts are millions of constant 2026 USD. An omitted year retains an unknown allocation and gap. A documented zero shows the entire positive cash requirement as uncovered. |

The local works rows cover land and utility conflicts, turnout premiums, extra depot lead and refuge track, terminal forecourt, offsite distribution feeders, additional foundation shafts, exceptional road crossings, temporary yard access and extra beam haul. Use the exact names and units from `opening.json → iraq_site_estimate → scenarios → base → items` in the prototype packet. Map every supplier exclusion before combining returns. For example, the line-power lot covers railway-side equipment and the named local site row covers offsite tie-ins. The software credits the matched allowance once. The buyer must identify overlapping scope inside a supplier's document.

## Try the calculation with a labelled fixture

Run from the full repository root. This example uses invented counts to exercise the software. It creates an isolated return under the ignored build directory.

```sh
mkdir -p build/airport-field-example
python3 - <<'PY'
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

folder = Path("build/airport-field-example")
with ZipFile("cities/Baghdad/engineering/prototype/airport-prototype.zip") as packet:
    form = json.loads(packet.read("returns/finance.json"))
attachment = folder / "example-counts.txt"
attachment.write_text("Synthetic software exercise. Two days, 25 journeys, 20 paying.")
form["documents"][attachment.name] = {
    "issuer": "Software fixture", "date": "2026-11-23",
    "sha256": hashlib.sha256(attachment.read_bytes()).hexdigest(),
}
form["demand_survey"] = {
    "document": attachment.name,
    "sample_date_from": "2026-11-20", "sample_date_to": "2026-11-21",
    "observed_days": 2, "net_usd_per_paid_journey": 0.50,
    "od": [{"from": "Airport-00", "to": "Airport-05", "all": 25, "paying": 20}],
}
(folder / "finance.json").write_text(json.dumps(form, indent=2))
PY
python3 -m cities.Baghdad.engineering.prototype.review \
  --financial-return build/airport-field-example/finance.json \
  --packet build/airport-field-example/review.zip
```

The example extrapolates ten paid journeys per day across 365 service days and yields $1,825 in annual net fares. It also yields 54,750 passenger-km per year across the 12 km corridor. Check how representative the survey period, passenger population, coverage and net fare are before using the result for investment. Missing OD pairs contribute no counted journeys to the supplied sample.

## Review the result

A site quantity and unit price replace the original direct row. The buyer schedule then reapplies the existing design, test and project allowances to the difference. The model spreads revised capital across the same three draw years and recalculates borrowing, interest and principal. Survey fares and recurring costs follow the operating fraction in each year. For a documented allocation, the uncovered amount is the positive balance after fares and the allocation. An excess in one year carries no automatic credit into another year.

Keep the submitted JSON and original attachments together. The returned result identifies the source filenames, issuers, dates and hashes. The verifier checks local file contents and rejects missing, changed or symbolic-link attachments. The issuer, signer authority, market scope, observation method and any funding conditions require independent review. A revised estimate leaves the complete funded capital and opening date open.

# Return installed Airport weights

Use the first-article packet’s `returns/weights.json` to connect a particular six-car load case to the traction supply, civil load screen and buyer’s cash flow. Keep an untouched copy of the published packet. Work in a separate directory containing the form and its supporting documents.

## Record the train and load

1. Retain the candidate, opening evaluation, frame revision and printed axle names. Identify the six car serials, end orientation, equipment fitted, operating fluid levels and passenger or ballast distribution in the supporting documents.
2. Return kilograms for the **whole six-car set** in each of seven groups. Use the six tare groups for finished frames, running gear, drive and brakes, body fitout, power and controls, and residual equipment. Enter payload separately. Account for fluids, seals, harness loops and joint hardware once. A documented zero is available for residual tare. Leave unknown fields null.
3. Put each original supporting file alongside the form. Under `documents`, give its local filename, issuer, calendar date and SHA-256 digest. Enter the filename in the corresponding group’s `evidence` field. Preserve the scale calibration, serial numbers, loading sheet and witness records with the originals.
4. For the moving beam screen, record tare and loaded kilograms **at each of the 24 axles**. Use the printed car and axle order. Supply the tare, loaded and balance-limit document names and the permitted discrepancy in kilograms between the summed axle readings and the grouped totals. Obtain that limit from the documented weighing procedure. A train with only grouped weights has no axle-specific result. Once an axle return is started, all readings and references must be complete before dependent calculations run.

To identify the origin explicitly, wrap the filled form in an object with fields `record_kind` and `weights`. Set `weights` to the complete form object and choose `supplier-declaration`, `physical-measurement` or `synthetic-fixture`. An unwrapped form retains origin `unclassified`. A physical label records the submitter’s claim. A matching file hash verifies the attachment bytes. Independent authentication, interface inspection and sign-off remain separate.

## Recalculate and request updated prices

From the repository root, capture the assessment and extract the child forms. Both financial and electrical returns must belong to the newly identified opening.

```sh
./osr design railway prototype --assess-weights build/returns/weights.json > build/weight-review.json
```

Inspect `result` and `weights.missing` before sending forms. A partial return retains null electrical, commercial and template fields. If the feeder search cannot price the new train load, `weights.engineering_hold` explains the failure. Both outcomes preserve submitted dependent form identities and withhold their evaluations.

For a complete case, the following example extracts the finance and priced radial circuit forms for issue. Place the suppliers’ supporting documents beside their respective forms.

```sh
python3 - <<'PY'
import json
from pathlib import Path

review = json.loads(Path("build/weight-review.json").read_text())
forms = review["templates"]
if forms is None:
    raise SystemExit(review["result"])
for name, form in (("finance", forms["finance"]), ("radial", forms["feeder"]["priced_radial"])):
    target = Path("build/returns") / ("updated-" + name + ".json")
    target.write_text(json.dumps(form, indent=2) + "\n")
PY

./osr design railway prototype --assess-weights build/returns/weights.json \
  --financial-return build/returns/updated-finance.json \
  --feeder-return build/returns/updated-radial.json > build/weight-review-with-returns.json
```

The complete output contains the revised train mass, traction demand, supply sites and cost estimate under `weights.opening`. The per-axle case, when supplied, reports the global moving moment, reaction and controlling train location under `weights.axle_civil`. `electrical` evaluates restored feeds and circuit sensitivities. `commercial` gives the buyer’s annual cash schedule and any documented allocations. The priced opening carries its radial supply scope. A station-sited supplier quotation has its own circuit and cost scope under the electrical return. Combining an alternative circuit with the opening budget requires pricing the displaced scope and adopting that design.

Blank hot-circuit trial forms are under `templates.hot_test`, keyed by topology. Use the commissioning guide with the revised opening and its matching form. Review the declared load distribution, wheel-side split, fatigue, foundations and installed equipment before choosing a physical design. Funding, purchase, energisation and operation require their own decisions.

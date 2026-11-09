# v0.6 candidate business lifecycle audit

## Result

**HOLD: the audited inputs contain no sealed candidate-matched delivery
proposal, review pack, or native lifecycle packet for the compact-drive
candidate.** The available sealed railway study and 668-part delivery proposal
are bound to the original body candidate. The bounded
`engineering.compact_drive.design.build()` result has a different physical
candidate and evaluation. The proposal compiler correctly rejects the mixed
pair before creating a delivery proposal. No candidate-specific controlled
documents, review pack, native ERPNext transaction, or lifecycle evidence were
generated for the compact-drive candidate.

The repository already has the needed software path in principle: the pure
proposal compiler preserves source-part quantities and direct prices;
`review.compile_review_pack` accepts exact source-priced-workpiece conversions
only when paired with real drawing, inspection, and routing payload bytes; and
the candidate delivery ERPNext adapter requires administrator-bound project
context plus a distinct authenticated review before draft Items/BOM/routes may
be created. Its native v2 disposable lifecycle fixture is documented but has
not been run. This demonstrates software capability, not candidate closure or
physical/manufacturing acceptance.

## Exact inputs and identities

Source checkout: branch `codex/v06-design-closure-20261108`, starting commit
`ac61d15bf38571e676026b70b9e59d8e5ddc1e10`.

The existing sealed body and railway inputs are:

- `docs/design-engine/reconciled-pilot-bogie-detail/delivery/inputs/body.json.gz`
  SHA-256 `111077d3fd5f4ab1008089f362f7f777bdf547cc8369b2444acf070bf5499493`;
  physical body candidate `9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba`,
  evaluation `dfb48ca3fac6ee9b702ae13b2e5e4e0c112d734263750deefb25ad5718fdb272`.
- `docs/design-engine/reconciled-pilot-bogie-detail/delivery/inputs/study.json.gz`
  SHA-256 `613a51585b1f0f061459921f41ce0594118a0bd77b15d018ff02cab087c76c52`;
  study `abc42ebe77496d5c16fe30622ade179b02141bde5feacadd7497abe0b83cc710`.
- The existing sealed proposal is
  `docs/design-engine/reconciled-pilot-bogie-detail/delivery/proposal.json.gz`,
  SHA-256 `1b091c4875b2945cc344edcd11932d265514f193fbce2ef6d5429e76d392d90c`,
  proposal `7b88d05f9e0a16ada127d60e51d8ebfdc23b0dcb90ba0c906b2050d4e65a5775`,
  with 668 source items. Its research candidate identity is
  `cde8e4595d365b31d169cf452d1efc1b9f0c96225ca3bbccf8bf51b5a2480c7f`,
  under the body candidate and study above. Its service evaluation is
  `830ee18500b3c4c192f74fb61a9f8079adc1ef7eb3e3f3a9db96cdee8bf4a4c2`.

The current compact-drive build (default config `compact-737-h100`) produced:

- Physical candidate `75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797`.
- Evaluation `fdac4907a6a867f0b4f27e0876a772d1b54d526ec323beb3b6d9a155e0e00b21`.
- Exact ancestry requirement: body candidate `9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba`,
  body evaluation `dfb48ca3fac6ee9b702ae13b2e5e4e0c112d734263750deefb25ad5718fdb272`.

The design output declares `installed_mass_complete=false`, an interface screen
of `HOLD`, structural comparison invalidated, and selection purpose unselected.
The identity refusal below confirms fail-closed candidate handling; it does not
establish that this candidate is viable.

Attempting to combine that build with the available study and service evaluation
raised `ValueError: Mixed body candidate or engineering revision`. This is the
expected fail-closed result: the old service/cost/civil bundle cannot be relabelled
as the compact-drive candidate. The compact-drive revision first needs its own
canonical installed inventory and downstream railway study/service/cost bundle.

## Verification and execution boundary

Commands run from this checkout:

```sh
python3 -u - <<'PY'
from engineering.compact_drive.design import build
body = build()
print(body['candidate_id'], body['evaluation_id'])
PY
```

Completed in 17.8 seconds. A second bounded call attempted
`compile_proposal(study, body, '830ee18500b3c4c192f74fb61a9f8079adc1ef7eb3e3f3a9db96cdee8bf4a4c2')`
and returned the mixed-body hold above (22.1 seconds including build).

```sh
python3 -m pytest tests/test_pilot_delivery_review.py -q
```

Result: **15 passed in 16.57 seconds**. These are synthetic payload/contract
tests over the older sealed 9f6d proposal. They do not produce controlled
candidate documents or ERP evidence for the compact-drive candidate.

Native execution was not attempted. The existing review protocol states the v2
fixture has not been executed and the retained full-stack runner has no aggregate
CPU/RAM budget enforcement. Its documented preflight also requires a real
candidate-matched review pack. Neither prerequisite is present for this new
candidate; running the fixture would exceed the assigned evidence/resource
conditions. The exact hold is therefore missing canonical downstream candidate
bundle, missing compact-drive controlled research document set, and missing
resource-reviewed native run plan. No supplier, QA, or physical acceptance
reference was invented. Physical acceptance, manufacturing release, operating
release, and movement authority remain false.

Report SHA-256 is recorded by the producing commit once integrated; this report
is an audit note, not a sealed business or qualification receipt.

The command results and 15-test pass above are producer-reported in this note.
This audit directory does not include an immutable execution transcript or a
complete hash manifest for the compact-drive sources and test runner.

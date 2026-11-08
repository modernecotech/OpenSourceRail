# Pilot manufacturing and delivery proposals

This compiler turns one sealed railway-closure study, its exact installed-body
packet and an explicit nominal service evaluation into a local review draft.
It accepts the same input schemas for later physical revisions; the published
recovery and no-store pilots are controls, not hard-coded selections.

```sh
PYTHONPATH=. .venv/bin/python -m engineering.pilot_delivery compile \
  --study docs/design-engine/reconciled-pilot/study.json.gz \
  --body docs/design-engine/reconciled-pilot/vehicle/installation.json.gz \
  --service-id ffae6d3af1e44a940fab370a8dadd2b28e742f6ece8222cb4fef428b535d6f38 \
  --output /absolute/path/to/a/new/private-run
PYTHONPATH=. .venv/bin/python -m engineering.pilot_delivery verify \
  --output /absolute/path/to/a/new/private-run
```

Commit the compiler sources before a fresh export. Existing output directories
are refused. Results retain original input bytes, exact source hashes, Git
source commit, command, identities, failures and measured usage. Verification
checks those bytes and sources and repeats the inexpensive deterministic model.
No CAD/FEM process or external service is launched.

`model.compile_proposal(study, body, service_id, root=...)` returns a deterministic
sealed proposal. `export.compile_run(...)` writes the immutable review package;
`export.verify_run(...)` verifies it. The root coordinator can expose these
functions in the Workbench without changing their admission or release rules.

The draft contains:

- Actual body part/stock/material requirements, counted occurrence patterns,
  per-train and whole-fleet quantities, direct-cost references and make/buy routes.
- Source assembly operations, tools, fixture/workstation proposals, interfaces,
  removal sequences, inspection holds and lot/serial planning rules.
- External motor, gearbox, electrical and recovery ownership; DC/DC partitions
  and body-owned BOP stock are reconciled against the existing allowance once.
- Running beam and shared-bent quantities, source erection sequence, temporary
  works and lifting assumptions, with terminal/site detail held separately.
- Existing fourteen-scope cost views and source identities, without adding the
  decomposition or process-hour proxies to existing prices again.
- A generic engineering-evidence package and an intentionally held execution
  mapping for the existing integration adapter. Actual ERP Item, drawing,
  inspection and review references remain unassigned.

Physical candidate, component candidate, engineering revision/evaluation,
planning selection, component definition, occurrence and serial identities are
separate. Source component identities remain provenance; they are not relabelled
as the new whole-railway candidate. No serial number, accepted installation,
qualified process or approved business transaction is invented.

The time ranges in `policy.json` are Class A capacity hypotheses. Validated
process times, actual crew sizes, external-package/civil hours, calendars and
critical paths remain unknown. Two 8-hour production shifts describe equivalent
resource capacity, not one employee working two shifts. These estimates do not
add a second labour price to the catalogue's direct material/process allowance.

Source routes are reconciled against the actual current `assembly_id` on every
part. Removed definitions remain source provenance and receive route-revision
holds; they are excluded from current executable-part references and quantities.
New current parts receive their own recorded process proposals, with controlled
assembly detail and unprovided tooling held. Historical battery-route gaps and
new running-frame replacements use the same rule.

The source category `make` maps explicitly to a local-fabrication planning
proposal. `bounded-purchased-or-processed` remains unresolved: process hours and
the complete vehicle-hour total stay unknown, while the known-hour subtotal is
reported separately. Neither category implies a qualified production method.

The current body subtotal includes its installation reserve and excludes the
separately owned drive/BOP/recovery additions. It is never reported as complete
integrated train tare. Unlocated reserves remain positive and visible.

For a child with body-owned BOP stock, every counted `BOP_partition` must match an
explicit external reserve reconciliation containing
`previous_external_reserve_kg`, `explicit_parts_already_in_body_kg` and
`remaining_unknown_external_reserve_kg`. Inventory may retain the gross or the
residual `mass_hypothesis_kg` when that ownership is explicit; subtraction is
performed once. Ambiguous partition ownership is rejected.

All proposals remain DRAFT. The existing `engineering.execution_proposal`
contract rejects the mapping until actual review and native item/drawing/
inspection references exist. No ERPNext, FUXA, gateway, purchasing or movement
command is sent. Review, business transactions and release remain with their
responsible systems and people.

Regression command:

```sh
PYTHONPATH=. .venv/bin/python -m unittest tests.test_pilot_delivery -v
```

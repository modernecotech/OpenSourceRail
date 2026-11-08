# Candidate-linked research delivery review

`review.compile_review_pack(proposal, documents, conversions, artifact_root=..., city=...)`
is a pure compiler. It checks the original sealed proposal and current source
bytes, then the actual controlled drawing, inspection and routing payloads.
`review.export_review_pack(pack, artifact_root, output)` copies their verified
dependency closure into a new directory. Neither function contacts ERP.

The original proposal schema and CLI are unchanged. The additional CLI is:

```sh
.venv/bin/python -m engineering.pilot_delivery.review \
  --proposal /absolute/proposal.json.gz --documents /absolute/documents.json \
  --conversions /absolute/conversions.json --artifact-root /absolute/drawings \
  --city baghdad --output /absolute/fresh-review-pack
```

The producer supplies this document index. These are schematic paths; executable
inputs require real files, hashes and the **complete exact** proposal identities.

```json
{
  "schema": "osr-controlled-research-documents/1",
  "identities": {"all thirteen proposal identity fields": "exact source values"},
  "components": [{
    "part_id": "exact proposal.items[].id",
    "drawing": "part/drawing-metadata.json",
    "inspection": "part/inspection-metadata.json",
    "routing": "part/routing-metadata.json"
  }]
}
```

Each sidecar follows [controlled-document.schema.json](controlled-document.schema.json).
The semantic validator is `candidate_delivery_contract.validate_document`.
The common sidecar fields are:

```json
{
  "schema": "osr-controlled-research-document/1",
  "document_type": "drawing",
  "identities": {"all thirteen proposal identity fields": "exact source values"},
  "part_id": "exact proposal item id",
  "component_definition_id": "exact source component identity",
  "source_part_sha256": "common.identity(the exact proposal item)",
  "revision": "RESEARCH-1",
  "maturity": "controlled-research-draft",
  "research_holds": ["Explicit unresolved tolerances, interfaces and qualification"],
  "payloads": [{"path": "part/drawing.svg", "sha256": "actual byte hash", "bytes": 1234, "media_type": "image/svg+xml"}],
  "physical_accepted": false, "engineering_accepted": false,
  "manufacturing_release": false, "operating_release": false,
  "movement_authority": false, "physical_evidence": false
}
```

Inspection sidecars add `characteristics`: `id`, `name`, `unit`, `minimum`,
`maximum`, `method`, `evidence_maturity="calculated-research-limit"`. At least one
finite limit is required. Their JSON payload has schema
`osr-controlled-research-inspection/1`, exact identities, `part_id`, and the same
characteristics. Routing sidecars add ordered `operations`: `sequence`,
`operation`, `workstation`, nonempty `tools`, `setup_minutes`,
`run_minutes_per_unit`, `time_basis`, and `inspection_ids` referring to those
characteristics. Their JSON payload uses schema
`osr-controlled-research-route/1`, identities, `part_id`, and the same operations.

Drawing payloads must contain nonempty SVG geometry, a complete PDF, or a
complete STEP file. An arbitrary review-reference string cannot substitute for
a file. Symlinks, path escapes, missing bytes, changed hashes, empty geometry,
mixed candidates, invented parts and dangling inspection references are refused.

The conversion map is keyed by the exact part ID. The first permitted mode is
`source-priced-workpiece`: `source_part_sha256`, `valuation_mode`,
`stock_inputs=[]`, `direct_process_allowance_usd=null`. It retains the exact
source part's positive direct parts/process unit price, quantity and UOM. It is
a counted priced workpiece, not a claim to have recovered its raw-stock route.
It never assigns a USD 1 synthetic kit rate. Native route times are non-additive
resource information because the source price already includes processes.

The second mode, `quantified-source-stock`, requires explicit stock rows with
`id`, `uom`, `net_quantity`, `gross_quantity`, `waste_fraction`,
`unit_rate_usd`, `source_sha256`, `basis`, and a nonnegative
`direct_process_allowance_usd`. Net/gross/yield must balance, and raw stock plus
process allowance must reproduce the source unit price. Exact engineering
values survive separately from conservatively rounded native quantities and
six-decimal native rates. The process allowance is allocated through declared
route time; it is not added twice to the source project ledger.

Only documented components enter a pack. All source part IDs, covered IDs and
uncovered IDs remain explicit. Partial document coverage never becomes a whole
train manufacturing-completion claim.

## Native application boundary

An administrator explicitly provisions one immutable simulation project context
compiled from the original proposal. It binds all candidate identities, proposal
hash, source-part hashes and counted occurrence patterns. A different source
revision requires a separate reviewed project. Public APIs cannot choose the
authoritative source by supplying a browser context.

`osr_erpnext.candidate_delivery` registers actual private Files attached to the
exact Project; native content, attachment, modification and permissions are
rechecked. A Manufacturing Manager proposes the conversion. A different
authenticated Projects Manager reviews current prerequisites in a native Task.
Only that review permits draft Items, source-priced BOMs, routes, operations and
workstations. The adapter never submits purchasing, production or release.

Installation readback requires an exact counted pattern/ordinal/train index,
source BOM, submitted Work Order and Manufacture/Material Issue serial custody.
Replacement also requires a completed native condition repair and an inward
return of the exact old serial. Condition events on these explicitly bound
projects check revision, source documents, installed position and current native
serial custody before any Issue is created. Retained projects use their existing
ingress unchanged.

Handback uses actual chronological latest native inspection, including newer
draft, failed or cancelled inspections. It reads the native repair, custody and
authenticated inspector. Independent review creates a native Task and a sealed
software-business record. A later inspection or changed native evidence holds
the review again. Physical acceptance and physical handback remain outstanding.

## Disposable acceptance fixture

`tools/automation/v06-platform-native.py` retains v1 unchanged by default. Supply
all three options to use the separate v2 fixture:

```sh
.venv/bin/python tools/automation/v06-platform-native.py preflight \
  --proposal /absolute/proposal.json.gz --review-pack /absolute/review-pack \
  --component-id 'exact part id'
```

Preflight is read-only. `run` creates only a fresh labelled namespace and a new
private checkout `build/` directory. The v2 fixture is bounded to twelve
documented components and 64 MiB of controlled artifacts; its lifecycle follows
one explicit discrete source part. It tests native revision review → BOM → work
order → incoming QA hold/rework → serial installation → simulated observation →
defect → repair/serial replacement → latest-QA hold → independent handback.
Gateway outage/replay, native permissions, wrong revision/serial/project with no
provisional Issue, FUXA observation and absence of movement commands are checked.
Its public receipt excludes secrets, site databases and private state, and is
published only after labelled containers/volumes/networks have been removed and
cleanup verified. Failed executions remain private diagnostic records.

The new v2 fixture has **not been executed natively** by this change. Offline
tests and an in-memory Frappe double establish contract behavior only. Native
execution needs a frozen source review, actual generated research documents and
a separately reviewed resource plan. The retained full-stack runner does not
enforce an aggregate RAM/CPU budget; per-container CPU quotas depend on host
Docker support and do not imply overall isolation. The coordinator must resolve
that resource hold before running this fixture.

Pinned schema checks used the primary ERPNext v15.121.2 definitions for
[Workstation](https://github.com/frappe/erpnext/blob/v15.121.2/erpnext/manufacturing/doctype/workstation/workstation.json),
[Operation](https://github.com/frappe/erpnext/blob/v15.121.2/erpnext/manufacturing/doctype/operation/operation.json),
[Routing](https://github.com/frappe/erpnext/blob/v15.121.2/erpnext/manufacturing/doctype/routing/routing.json),
and [inspection readings](https://github.com/frappe/erpnext/blob/v15.121.2/erpnext/stock/doctype/quality_inspection_reading/quality_inspection_reading.json).
The live adapter also rejects unsupported required native fields before writing.

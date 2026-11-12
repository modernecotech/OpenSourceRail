# Counted research assembly software custody

The existing candidate-delivery protocol supports optional typed assembly
installation, replacement, condition-event resolution and business handback.
`register_assembly_installation` accepts an authoritative `assembly_id`, a
counted `assembly_patterns` occurrence, and exact native child provenance.
The existing part installation API and its historical outputs remain valid.

This is a software contract. The new API has synthetic in-memory regression
evidence. The retained native v2 fixture still admits one documented part; its
success cannot qualify the assembly API or the 694-piece door.

## Required source and documents

`compile_review_pack` accepts optional `documents.assemblies` entries containing
`assembly_id` and drawing/inspection/routing sidecar paths. Sidecars use
`osr-controlled-research-assembly-document/1`, with `assembly_id`,
`assembly_definition_id`, `source_assembly_sha256` and the existing explicit
research maturity, real payloads, calculated inspection limits and route
controls. Inspection/routing JSON payloads carry `assembly_id`.

A trusted administrator calls `source_context(..., assembly_groups=...,
assembly_documents=pack['assembly_documents'])` with verified compiler output.
The provisioned context pins each complete document-set hash independently of
client proposals. Private attached File bytes, revisions and native mapping are
rechecked before lifecycle operations. Parent assembly documents and QA are
required in addition to every applicable child document and QA. Grouped draft
packs without their own documents remain usable for draft review; lifecycle is
held.

## Admitted custody domain

This first assembly route admits made, individually serialized discrete children
only. Purchased, unresolved buy/process or lot-only custody is refused. A real
purchase receipt or lot contract must be implemented before those children can
enter this route. A missing Work Order is never replaced with a fabricated one.

`child_provenance` is a bounded list of `{kind, id, units}` entries matching every
source child edge and exact count. Each unit contains `serial`, `work_order`,
`manufacture_stock` and `children` (empty for a part). The native parent
Manufacture Stock Entry must consume exactly those child serials and quantities.
Each child must have its own submitted reviewed BOM, submitted Work Order and
manufacture entry, and latest submitted accepted inspection. Nested assemblies
repeat these checks within the existing depth and work bounds.

The parent serial must match manufacture and outward installation custody.
Replacement requires a completed condition repair and inward removal of the
exact prior serial. Source revision, child provenance and native serial custody
are read again for condition events and handback. Later pending, cancelled or
failed inspection and changed review Tasks invalidate business handback. Serial
position and child-consumption indices prevent silent duplicate allocation.

No API submits a draft BOM or grants physical manufacturing, installation,
operating or movement authority. Assembly process cost remains unknown;
zero native operation rates are conversion placeholders, not a zero engineering
process estimate. Actual door lifecycle execution remains held until matching
source identities, assembly/child documents and admitted custody inputs exist.

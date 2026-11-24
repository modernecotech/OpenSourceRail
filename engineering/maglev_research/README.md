# Retained maglev research inputs

`infrastructure-policy-v05.toml` is the byte-identical v0.5 policy formerly
stored at `lib/templates/infrastructure.toml`. It belongs to the ferrite maglev
research family, not to the v0.6 wheel-supported development default. The
offline maglev host validator and retained ferrite model read this copy.

Historical source receipts continue to name the original path and SHA-256
`0bebf8fbfd6b4dd05e53394171caadcc90b5d28154e31a8aa61794a57c898d12`.
Reproduce those records from the pinned source revision in
`docs/archives/v0.5-maglev/manifest.json`; relocating this working-tree input
does not rewrite an executed receipt or confer physical acceptance.

The four original study inputs now live in `inputs/`, with their bytes unchanged:

| Input | SHA-256 |
| --- | --- |
| `ferrite-maglev-study.toml` | `a1effd80c4a5390b3c615b5833258e88ed1e687cfad065c65260b8149ae50839` |
| `OpenSourceRail_Station_Powered_Maglev_Design_Specification.docx` | `ddadab05460950f13f99f8134fafb5303f0103a6e914aa57181917008d092b9a` |
| `OpenSourceRail maglev station concept.png` | `0f795d8c20890279ec6ef1075a882e61827f26db26c02c14f375948ed5275d37` |
| `Vertical spiral escape chute concept.png` | `b784a542c1fec9d2172f07ca917df7f6a2f5d9b48bf0a7aa4e7ac89e9e4c91b5` |

The controlled specification record keeps its original source name and digest.
Its reader resolves that name to `inputs/` in the current checkout. Historical
receipts and source keys retain their original values and are verified from the
pinned v0.5 checkout (`92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164`).
Current research readers accept an original path only when its recorded digest
matches the scoped copy exactly. A changed copy requires a new source epoch.
Published comfort and trip research packets remain bound to their executed
source epochs; their existing manifests are not revised by this file move.

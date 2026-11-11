# Reconciled pilot refresh and exact native reuse

**Recorded 11 November 2026.** The standard, no-store, and bogie-detail railway
pilot packets were regenerated from the current source at commit
`6836dcd719`. Each packet reuses native calculations only when its canonical
request bytes, solver source, tool versions, product, protocol, binary hash,
resource limits, and execution environment match. All 59 requested native
batches were reused; none of the Rust solver executables ran during these three
refreshes.

## Refreshed packets

| Variant | Candidate ID | Study ID | Publication manifest | Source publication manifest | Native batches reused |
|---|---|---|---|---|---:|
| Standard | `f9aa3afa47a297da855b2741c9e0fde0d77ad3e3211df500f32f901cfadb1877` | `1957d34bae126b086ba29ca94c6934a189ee86f3e259ab51079d4b3be277a5c7` | `63186aec244e73a68b77d2c71990e61ef3ec464c2445cf1a4a740c85ef8d62e0` | `36ba5761bd861645be2a2fd6277d674b27da153b36356343a8a722c8424fba14` | 21/21 |
| No-store | `7c916d9828baa5b694bf8f7e416be4fa8c7f196148174df4aa0474441479026d` | `58e8397978a88d13f6d6cf0851fe398e04834b9d14ad49b1fefda9069446315e` | `00305d984f89edd7103f01fb7e89aa5929e894771dcc08e450a2c67b63873741` | `209c1635780a118ac040fe27726bee8ae5edc3c24ddc37de4936bee5d5bbdf7e` | 18/18 |
| Bogie detail | `cde8e4595d365b31d169cf452d1efc1b9f0c96225ca3bbccf8bf51b5a2480c7f` | `5721158a4c0fac4175ab4d62795e2f8a8ae0f89052b6496acd182966575fa60b` | `685cb05df5d6c4b85f372be0176b2938df15f43d56cf802869ec63db6345c11e` | `4510eeab6487ed4f07b187e6835e8f6c8e4c2ae28d102ae65da60c16c8ecd9ae` | 20/20 |

The source manifests are the three packets committed in `fc01362edc`. That
commit keeps the exact origin receipts and files in Git history. Each new
receipt records the origin manifest, origin receipt, origin binary, and both
native bridge hashes. A bridge revision may reuse a result only after the exact
serialized request and all solver and runtime identities match; the bridge
hash difference remains explicit in the provenance.

## Measured resource use

| Variant | Wall time | Coordinator peak RSS | Run bytes before manifest | Native batch wall time in source receipts |
|---|---:|---:|---:|---:|
| Standard | 124.84 s | 534,424 KiB | 144,601,677 | 2.72 s |
| No-store | 116.88 s | 449,244 KiB | 127,223,269 | 2.19 s |
| Bogie detail | 131.46 s | 519,816 KiB | 133,378,542 | 2.58 s |

The whole coordinator still spends about 17–27 seconds each on body and civil
work, before service exploration, request preparation, serialization, and
verification. Reusing these pilot batches therefore removes 59 process launches
and about 7.49 seconds of recorded native solver time across all three studies;
it does not establish the proposed 30% cold-run or 70–90% warm-run speed
targets. The small full-run wall-time differences between earlier and refreshed
packets are not attributed to the cache. Function-level profiling of the body,
civil, and service stages is the next useful performance measurement. The
native solver was already Rust-backed, and these runs do not justify broad
vectorization or a Python rewrite.

## Active packet storage

The three current pilot directories occupy 114,008,363 bytes (108.72 MiB),
down from 193,328,058 bytes (184.37 MiB) at commit `9d35e27ba6`. This is a
79,319,695-byte (75.65 MiB, 41.0%) reduction in their active file trees. The
refresh keeps only native batches cited by each current study; it does not
delete old Git objects or rewrite history. The origin packets remain available
at `fc01362edc`.

The storage inventory still finds ignored build and research data in other
worktrees. Its cleanup proposal held all 12 candidates for ownership review and
deleted nothing. Temporary worktrees and staging created for this refresh were
removed after verification; unrelated worktrees and ignored research data
remain untouched.

## Validation and engineering limits

The exact reuse tests, railway closure integration tests, and gzip publication
tests passed: **17 passed**. Each refreshed packet passed
`python -m engineering.railway_closure verify --output <packet-directory>`.
The v0.6 closure ledger still reports **0 of 7 gates closed**. These packets
remain conditional engineering research: physical acceptance, manufacturing
release, operating release, movement authority, and selected-reference changes
are all false.

This change adds source-bound reuse to the railway closure campaign. It does
not yet provide a general performance profiler, shared disk quotas, a resource-
aware campaign scheduler, incremental all-city dependency calculation, or a
managed external artifact store. Those work packages still need measured
baselines and source-bound migration plans.

Resealing the global `docs/design-engine/current` publication after a README
coverage refresh was blocked by the existing `RetiredReferenceHold` for the
`coupled-railway` file inventory: that directory contains additional files
outside the fixed pre-comfort inventory. No historical pin or receipt was
edited, and the existing current coverage and manifest were left unchanged.
Reconciling that inventory is a separate publication task.

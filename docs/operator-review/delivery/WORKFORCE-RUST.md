# Rust efficiency review for workforce and delivery planning

| Path | Finding | Change or boundary |
|---|---|---|
| Workforce preparation | Assigning repeated shifts at the individual-worker and individual-day level would greatly enlarge input and replay. | The Python source adapter selects a published scope and creates compact role and shift patterns. Rust evaluates the minutes, costs and stress case. |
| Workforce simulation | Labour accounting, input validation and file export change for different reasons. | The dedicated Rust crate separates the data contract, capacity/cost kernel and export path. Arrow/Parquet dependencies compile with this tool in its own workspace. The main railway control workspace and the delivery scheduler use their existing default build features. |
| Campaign index queries | The previous query downcast columns and created owned strings for each row before testing the candidate. | The reader borrows typed columns once per batch and materialises rows only for matches. It still validates the schema and the ordinal sequence of all rows, and checks the source hash of every returned case. At a full 128-row all-miss batch, downcasts fall from 1,537 to 13 and 1,024 owned strings are avoided. Parquet decoding still runs. |
| Delivery dependencies and resource pools | The native scheduler repeatedly scans ready work and sorts resource pools before placement. | Keep its sequence and behaviour for now. Profile a representative large delivery graph before changing the scheduler. A ready queue and a bounded allocation structure are plausible improvements. Tests must protect tie breaks, repeated resource requests, invalid input and numerical work budgets. |
| Full campaign publication | The publication reader builds a full JSON value and clones case bytes to validate identifiers and check canonical evidence. | Evaluate a borrowing reader with a small identity projection as a separate exact-byte change. Keep canonical checksums and malformed input tests before promoting it. |

The workforce model operates on bounded column batches and uses compact
repeated-shift inputs. This design reduces unnecessary work and lets consumers
select only the columns they need. Explicit SIMD speedup would need measurement.
The index count is a comparison of work on the affected code path and excludes
Parquet decoding, disk access and case verification time.

A local check used a 16,384-row Parquet index with one match. The old and new
readers ran in the same unoptimised Rust process on the same data, with 20
interleaved warm repetitions and equal returned records. Median lookup fell
from 132.5 ms to 96.4 ms in this fixture. The result applies to this sparse
lookup and does not establish a release-build or full-publication speedup.

A release-build run processed 100,000 repeated source-derived work patterns
from a 54 MB JSON input in 0.48–0.50 s on the development machine, with about
125 MiB peak resident memory. That measurement includes parsing, applying the
availability scenario, writing CSV and Parquet, and generating the JSON
summary. The 39 MB CSV and roughly 492 KB Parquet reflect repeated values in
this fixture. The sample measures throughput under repetition. A plan with
unique names, roles and rates will compress differently.

```sh
cargo test --locked --manifest-path crates/osr-workforce/Cargo.toml
cargo test --locked -p osr-design-search --features columnar --test columnar
```

# Direct delivery compilation

Python remains the default scheduler. Compile a current verified mapped-city study directory through the supported uncached CLI:

```sh
./osr outline delivery --request /external/current-city-study --output /external/new-python-run
./osr outline delivery --request /external/current-city-study --output /external/new-rust-run --scheduler rust --scheduler-binary /external/target/release/osr-delivery-schedule
```

The existing `city_workflow.verify` checker validates the complete packet before and after compilation; raw self-sealed records are refused. The compiler extracts its `city_outline` member. Its candidate, geometry/service/cost identities and all declared source hashes must match. Historical records are refused as stale. The output directory must be fresh and outside the source checkout; input is bounded to32 MiB and plan JSON to64 MiB. Failed compilation retains the upstream manifest snapshot where available, any extracted input and a failure record. Successful receipts bind the upstream manifest identity and bytes.

Build explicitly using `engineering.outline.native_schedule.build(root, external_target)` in a separate admitted operation. It uses offline, locked Cargo, two build threads, a180-second limit, a768-MiB observed target cap and a20.75-GiB disk preflight. Scheduling never builds, downloads or falls back. A mismatched source, tool or executable receipt is an error.

`delivery_plan.evaluate(record, root=root, scheduler_backend='rust', scheduler_binary=binary)` is the corresponding API. Each complete Rust compilation requests three serial helper jobs, one per low/base/high case. Each helper has30 CPU seconds,45 wall seconds,512 MiB address space and32 MiB per output file; request JSON is limited to16 MiB. The96-MiB temporary aggregate budget is observed after each process, alongside the per-file limit; it is not an aggregate quota. Temporary request/output files are external; successful attempts are removed and failures retained. Disk admission is not an aggregate quota. Tool-version probes are separate metadata processes with10-second timeouts.

Plans record backend source hashes, tool versions, executable SHA-256 and helper limits in evaluation metadata. Physical candidate/configuration identities are unchanged. Python/Rust plan identities differ because evaluator provenance differs. This direct CLI has no persistent cache. Existing city-study workers and their caches still use Python, with zero Rust helper jobs; the new flags are rejected for other outline actions. No CAD, FEA or GIS solver is launched and every engineering/release flag remains false.

Direct-run receipts report wall and own/child CPU deltas. Separate self/children RSS figures are cumulative process-lifetime high-water marks, not per-invocation peaks or simultaneous aggregate memory. They include tool-version probes where applicable.

# Safety evidence: traceability, results and acceptance

The default `osr-safety-case` command checks the GSN graph and evidence paths.
It reports **traceability complete**, not safety-case acceptance. A source file
containing a proof harness is not a proof result.

Two additional, conservative gates assess every declared solution:

```bash
cargo run -q --bin osr-safety-case -- docs/safety-case/gsn \
  --results build/assurance/results.toml --require-verified
cargo run -q --bin osr-safety-case -- docs/safety-case/gsn \
  --results build/assurance/results.toml --require-accepted
```

Missing results fail these gates. The repository does not manufacture passing
records from its existing source pointers. Each supplied record must identify
its solution, kind, source and exact anchor; for Kani the named function must
exist in that source. It must also contain a successful execution status and
zero exit code, tool/version, reviewed bounds, runner identity, source/input
hashes and a separate report whose bytes match the recorded SHA-256.
Changed source inputs or report bytes invalidate the result. Bounds must describe
the actual run, including unwind limits, assumptions and tool configuration.

A trusted runner exports the following TOML contract (values below are explanatory
placeholders and intentionally do not constitute usable evidence):

```toml
schema = "osr-evidence-results/1"

[[result]]
solution = "E1.1a"
kind = "kani"
path = "crates/osr-interlocking/src/kani_proofs.rs"
anchor = "kani_p2_non_overlap_two_trains"
tool = "kani"
tool_version = "record the actual version"
bounds = "record exact unwind, assumptions and command"
executed_by = "controlled-runner-identity"
status = "passed"
exit_code = 0
report = "build/assurance/p2-report.txt"
report_sha256 = "sha256 of actual report bytes"
[result.inputs]
"crates/osr-interlocking/src/kani_proofs.rs" = "sha256 of actual source"
# Include implementation, manifests, lockfiles and all reviewed dependencies.

[result.acceptance]
status = "accepted"
reviewer = "independent-reviewer-identity"
reference = "controlled acceptance record"
result_sha256 = "ResultRecord::fingerprint() from the reviewed result"
```

Acceptance binds the entire result record through a deterministic fingerprint,
including input hashes, tool version and bounds; it cannot survive a changed
execution record. The reviewer must differ from the executing identity.
A passing result without this acceptance is reported separately.

This validates **recorded evidence**, not proof mathematics or reviewer identity.
It does not parse arbitrary vendor reports, invoke proof tools, establish that
an input list is complete, authenticate a runner, or grant railway release.
Controlled runner exports, dependency-scope review and authenticated independent
acceptance remain required. Citation solutions also need a reviewed result and
local input/report artifacts. The strict gate requires all solutions rather
than allowing one passing alternative to conceal missing declared evidence.

Inventory counts are generated from GSN TOML by
`python3 tools/automation/safety-case-summary.py`; CI runs it with `--check`.
The [release-gap register](../certification/release-gap-register.md) remains the
place to track physical and deployment acceptance work.

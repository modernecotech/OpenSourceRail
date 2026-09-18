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

## Controlled execution and signed acceptance

`tools/automation/assurance-evidence.py run` discovers the 41 declared Kani
solutions from GSN, invokes each exact harness with Kani 0.67.0, and exports
`results.toml`, per-harness logs and `execution.json`. A nonzero exit, timeout or
missing successful verification summary remains failed. Inputs include workspace
Rust (including untracked local source), manifests, lockfiles, GSN, runner and CI
workflow. Changed inputs during execution invalidate the run. CI runs all eight
packages and uploads diagnostics even on failure.

```sh
PATH="$HOME/.cargo/bin:$PATH" tools/automation/osr-python \
  tools/automation/assurance-evidence.py run \
  --output build/assurance/review --timeout 300
```

Local runs identify themselves as `local-unattested`. A GitHub run reference is
recorded as a declared executor, **not authenticated by environment variables**.
`runner_authenticated` remains false: verifying the actual CI run, toolchain,
dependency provenance and operating separation remains an independent task.

The separate `verify-acceptance` command authenticates an authorized reviewer's
Ed25519 signature over exact JSON envelope bytes, checks the result/report/input
hashes and current conservative dependency scope, rejects failed results, duplicate
solutions and mismatched declared harnesses, and rejects an executor/reviewer
identity match. It does not create a signature or decide that a review occurred.

A separately controlled policy supplies `reviewers`, keyed by reviewer identity,
with `enabled`, `public_key` (relative to the policy file) and
`public_key_sha256`. Keep that trust policy outside the contributor-controlled
checkout. The signed envelope contains:

```json
{
  "schema": "osr-independent-acceptance/1",
  "status": "accepted",
  "reviewer": "authorized-independent-reviewer",
  "reference": "controlled-review-record",
  "results_sha256": "hash-of-exact-reviewed-results.toml",
  "solutions": ["exact-reviewed-solution-identifiers"],
  "dependency_scope_reviewed": true
}
```

These are explanatory placeholders, not an acceptance record. The reviewer must
review actual runner provenance and independence; different text labels alone do
not establish different people. After an authorized reviewer supplies the envelope
and detached signature:

```sh
tools/automation/osr-python tools/automation/assurance-evidence.py verify-acceptance \
  --results build/assurance/review/results.toml \
  --envelope /controlled/review/acceptance.json \
  --signature /controlled/review/acceptance.sig \
  --policy /controlled/trust/reviewers.json
```

Successful signature verification covers only the listed execution records. It does
not satisfy the complete GSN case, authenticate physical evidence, or grant railway
release. Other evidence kinds and the existing complete-case validator retain their
own requirements. No independent acceptance was produced by the demonstration.

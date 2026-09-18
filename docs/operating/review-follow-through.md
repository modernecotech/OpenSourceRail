# Integration review follow-through — 18 September 2026

This follows the review of `ec7a2023`. It distinguishes implemented controls,
executed software tests and work that still requires evidence. **The complete
railway programme is not accepted or complete.** Published v0.4.0 remains immutable.

## Recommendations and disposition

| Review recommendation | Implemented response | Remaining closure |
|---|---|---|
| Make complete-city testing a release gate | `example-city` runs on push, PR and manual dispatch. Release packaging requires four successful workflows on the exact commit and validates the downloaded city's report hashes and clean scenario-start commit. Missing, failed, empty and altered reports are rejected. | A candidate needs its own successful CI runs; older local reports cannot qualify. |
| Unmocked disposition UI | Nine browser assertions use real ERP responses and three native users, through proposal, endorsement, native stop, independent verification and stale detection after resume. Self-review and premature verification are rejected. | Other action types retain native transactional tests; every browser/action/concurrency permutation is not covered. |
| Controlled proof evidence and independent acceptance | The runner executes every declared Kani harness, records actual exit codes/logs and conservative dependency hashes, and rejects source changes during execution. CI covers eight packages and all 41 declared harnesses. Ed25519 verification binds an independent authorized reviewer to exact result bytes, scope and reports. | Timeouts remain unproved. Runner provenance and reviewer key ownership require external trust review. No independent acceptance has been issued. Citation, property-test and other safety-case results remain separate. |
| Cross-domain engineering changes | Workbench binds the proposed package to city/company/project ERP observations and linked artifact hashes. Missing, ambiguous, older-than-five-minute, future-dated or revision-mismatched observations and changed artifacts are flagged; the context checksum changes with business observations. | This is a point-in-time review, not a cross-service transaction. Complete CAD dependency discovery, solver reruns, accepted rework and formal-evidence supersession remain open. Supervisory apply does not close these gates. |
| Broader operating validation | A resource-bounded, resumable runner supports selected cities or the full catalogue, nominal or degraded full-window runs, and generated candidates. Catalogue CI partitions the workload and rejects missing, duplicate, failed, stale or altered city artifacts. | Canonical full-service, continuous stabling, morning fleet, site-energy and physical acceptance need their own qualifying evidence; generated candidates do not promote canonical packages. |
| Manufacturing and production deployment | Existing supplier, factory, inspection, HIL and operating-release gates remain fail-closed. No nominal calculation or simulated ERP transaction is relabelled as performed evidence. | Approved supplier configurations, site surveys, inspected first articles, measured mass, HIL, production identity/TLS and independently accepted restore/recovery evidence are required. |

## Defects found by the expanded execution

- Complete-city browser execution exposed a document-navigation race while reading
  the native Task filter. Polling now retries only destroyed/detached document
  contexts, as the simulator/OCC readiness check already did; the authenticated
  user and exact city Project assertions still have to pass.
- Complete-city CI exposed a simulator command race: a local disable arriving
  during telemetry/polling could be missed by command execution. The simulator
  now rereads local enable/disconnect inputs immediately before each command;
  deterministic regression cases reproduce the old acceptance and verify rejection.
  The city test checks this independently of its shortened command-expiry probe.
- ERPNext's native reorder scheduler omitted the city Project from generated
  Material Request lines. The OSR hook now derives it from the exact Item/warehouse
  rule, preserves explicit values, and rejects ambiguous or stale scope. The
  reproducible ERP image is `osr/erpnext:15.121.2-hr15.64.0-osr13`.
- The point-machine controller could clear a persistent drive fault when its
  cooldown expired. Active over-temperature/drive faults now refresh the latch
  and inhibit motor movement, including clock saturation. Regression tests and
  all seven declared points harnesses passed after the correction.
- Signed `abs()` in brake, odometry and intrusion proof assumptions could itself
  overflow before the input constraint applied. Guards now use `unsigned_abs()`.
  Two intrusion harnesses needed unwind 10 to traverse the eight-slot LIDAR array;
  unwinding assertions remain enabled. All five intrusion and five brake harnesses
  passed in targeted execution. Full dependency-bound results are generated by the
  final broader sweep; these targeted checks alone do not close the safety case.
- Production obstacle/intrusion LIDAR and radar comparisons also used signed
  `abs()`. A regression test reproduced a panic at `i32::MIN`; unsigned magnitude
  comparisons now handle both signed extremes consistently with the off-profile
  rule. The updated five-crate unit/property suites pass. Superseded source-bound
  proof runs cannot qualify as evidence for these revised evaluators.
- ATP's same-section overrun harness and odometry's zero-wheel balise harness
  constructed topology their evaluated paths never read. Removing that fixture
  work, and bounding unreachable ATP loops with unwinding assertions enabled,
  allowed both proofs to finish with their original input ranges and assertions.
  The overspeed/conservatism harnesses also exposed insufficient square-root
  unwind bounds; these are increased to 32, with unresolved executions still
  treated as unproved. Graph-dependent harnesses keep their topology fixtures.
- Kisumu and Najaf's checked-in scenarios lacked the current train-system fields.
  Regeneration also exposes their explicit point-machine identities. Their original
  nominal runs failed the configuration contract even though operational checks ran.
  The batch runner can test regenerated candidates without overwriting their
  canonical city package or falsely promoting dependent evidence.

## Executed results and limits

- [Catalogue CI 35344461975](https://github.com/modernecotech/OpenSourceRail/actions/runs/35344461975)
  passed all **266 generated candidates**, each over 90,000 simulated seconds,
  at `7b744e124`. The downloaded reports, source hashes and aggregate were verified
  locally. These are nominal runs; canonical packages were not promoted.
- Two further generated candidates were selected from that result by their lowest
  service-completion and battery-charge margins. **Hofuf passed all eight degraded
  cases; Nampula passed seven of eight.** Nampula's combined 80% aged battery and
  maximum HVAC case completed **89.68%** of scheduled service, failing the 90%
  requirement even with the existing 0.2 percentage-point numerical tolerance.
  Its controller invariant count was zero. This is an open capacity/timetable
  validation finding, not a reason to lower the acceptance threshold. Full local
  records are generated under `build/city-validation/review-margin-resilience/`.
- [Broader Kani CI 35346889940](https://github.com/modernecotech/OpenSourceRail/actions/runs/35346889940)
  executed all **41** declared harnesses at `7b22b981e`: **30 passed and 11 timed
  out** at 300 seconds each. Their manifest, report and source hashes were verified
  locally. Timeouts do not establish the properties, and no independent acceptance
  has been issued. The required release workflow therefore remains unsuccessful.

These are results for the recorded inputs and commits, not approval of a later
candidate. Complete-city release artifacts must still pass their exact-commit gate.

## Repeatable commands

```sh
./osr example-city business-check
./osr example-city disposition-check
./osr example-city coverage
# Only after a full scenario started on the same clean candidate commit:
./osr example-city release-evidence

PATH="$HOME/.cargo/bin:$PATH" tools/automation/osr-python \
  tools/automation/assurance-evidence.py run \
  --output build/assurance/review --timeout 300

# All cities, including degraded full-window scenarios; bounded parallelism.
tools/automation/osr-python tools/automation/validate-city-batch.py \
  --all --jobs 2 --timeout 1800 --resume
# Examine current-generator candidates separately from canonical packages.
tools/automation/osr-python tools/automation/validate-city-batch.py \
  --city kisumu --city najaf --nominal-only --regenerate \
  --output build/city-validation/candidates

# Optional catalogue CI: 16 disjoint partitions, at most eight jobs at once.
gh workflow run city-catalogue.yml --ref YOUR_CANDIDATE_REF \
  -f basis=generator-candidate -f resilience=false
```

The catalogue workflow also runs on explicitly pushed `validation/cities/**`
branches. Each partition uses two workers; its collector verifies every current
catalogue city, commit, dependency scope and report/scenario/design hashes. It
publishes failed diagnostics as well as successes. This optional modelling check
is separate from the four required integrated software-release workflows.

Timeouts and failed runs retain diagnostics and exit unsuccessfully. `--resume`
never reuses failed results or results for changed inputs. `--nominal-only` excludes
resilience and is recorded in the evidence; it cannot satisfy a resilience run.

## Integration coverage and evidence still needed

The [coverage register](../../deployment/example-city/coverage-register.md) records
515 integration entries: **36 scenario, 64 varied, 135 partial and 280 gaps**.
The additional business scenario has 24 native outcome/rollback checks; the browser
scenario has nine unmocked disposition checks. Neither count represents all ERPNext
functions or all possible variable combinations.

Payroll posting, jurisdiction-specific tax, capitalization/depreciation, SLA
calendars/escalation, independent competence decisions, desktop regeneration,
concurrent load and fresh-volume backup restoration retain explicit gaps. Physical
and manufacturing closure still needs approved evidence and independent reviewers.
The tracked deployment summary retains its city-level gates until qualifying
canonical evidence is generated and reviewed.

The stale RFC release label, “unbounded” property-testing wording and operations
stabling description have been corrected. Samawah's adopted planning allocation is
**40 station-held plus 68 depot/terminal-held trains**, with physical fit separate.

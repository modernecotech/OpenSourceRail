# v0.6 software-release readiness

The v0.6.0 software release has its own versioned contract in
[`campaigns/v06-software-release.toml`](../../../campaigns/v06-software-release.toml)
and a machine-readable status in [status.json](status.json). Run:

```sh
./osr release software readiness
./osr release software readiness --require-ready
```

The first command reports verified proof-record integrity and the outstanding
software gates. The second returns a failing exit status until every gate has
source-bound passing proof and an independent release review. The readiness
report derives its result; the status file cannot set `software_release_ready`.

| Gate | Required evidence |
|---|---|
| SR-01 — Source and artifact integrity | Publication hashes, manifest replay and tamper rejection |
| SR-02 — Core tests | Required Python, Rust, frontend and release-lane checks on one frozen commit |
| SR-03 — Representative journeys | Editable Samawah, Baghdad comparison and candidate research demonstrations |
| SR-04 — Workbench usability | City selection/edit or comparison through calculation, same-candidate cost and export |
| SR-05 — Install and resource contract | Clean setup, disk admission, bounded outputs, warm replay and low-space refusal |
| SR-06 — Release communication | README, quickstart, release notes, maturity table, demo outputs and known limits |

All proof records must be ordinary in-tree files with SHA-256 identities. A
passing record must bind the exact candidate source commit, contract hash, gate
ID and required evidence kind. A changed source commit invalidates that record.
The final independent review is also source-bound.

## Current result

The six software gates are pending, so software-release readiness is false. The
`release_commit` is not pinned. Current browser and source-publication checks
are useful evidence, but they do not yet prove all three packaged journeys or
the clean-install resource contract.

Engineering closure is evaluated separately by
[`docs/design-engine/v06-design-closure/status.json`](../v06-design-closure/status.json).
Its six open gates and partial Workbench gate remain unchanged. The software
report keeps `engineering_accepted`, `physical_accepted`,
`manufacturing_release`, `movement_authority` and `operating_release` false.
Software proof integrity is not engineering-semantic review or physical
qualification. A software release therefore cannot authorize a vehicle,
manufacturing, construction, or railway operation.

The evidence-record format protects integrity and identities; reviewers still
must judge whether test results and demonstrations satisfy their stated
acceptance criteria. The evaluator does not execute the journeys or query a
remote CI service. CI receipts must first be retained as source-bound proof
files and then reviewed for the exact frozen commit.

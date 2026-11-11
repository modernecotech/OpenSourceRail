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

Passing proofs are kept outside the source checkout so they can attest to an
immutable release candidate without changing its commit. After freezing a
candidate and generating the evidence bundle, inspect it with:

```sh
./osr release software readiness \
  --attestation-bundle /path/to/v0.6.0-attestation \
  --expected-repository modernecotech/OpenSourceRail \
  --trusted-reviewer <reviewer-name-confirmed-out-of-band> \
  --trusted-reviewer-key-sha256 <fingerprint-confirmed-out-of-band>
./osr release software readiness --require-ready \
  --attestation-bundle /path/to/v0.6.0-attestation \
  --expected-repository modernecotech/OpenSourceRail \
  --trusted-reviewer <reviewer-name-confirmed-out-of-band> \
  --trusted-reviewer-key-sha256 <fingerprint-confirmed-out-of-band>
```

The bundle directory contains `attestation.json` and its referenced proof
files. The evaluator requires a clean Git checkout, matches both the full
commit and tree identities, checks the contract hash, and verifies every
required proof hash and identity. An accepted release review includes an
Ed25519 signature over a review record that binds the repository, exact
source commit/tree, contract and attestation identity. The verifier compares
that signing key with the SHA-256 fingerprint, reviewer identity and canonical
repository supplied out of band; obtain those values through an independently
authenticated channel. The reviewer must also be independent of the release
author/operator and must inspect the CI runs and proof semantics. The SR-02
proof names all three required Actions workflow files, run IDs, check names,
attempts, conclusions and tested commit; the signed reviewer must verify those
run references on GitHub. The checker validates their structure but does not
contact GitHub or evaluate whether the human review was adequate. OpenSSL 3 is
required to verify the Ed25519 signature.

The committed status remains a truthful pending dashboard; readiness is
derived only while inspecting the external bundle. `--source-commit`, when
supplied, is an expected value and must match the actual Git `HEAD`.

| Gate | Required evidence |
|---|---|
| SR-01 — Source and artifact integrity | Publication hashes, manifest replay and tamper rejection |
| SR-02 — Core tests | Required Python, Rust, frontend and release-lane checks on one frozen commit |
| SR-03 — Representative journeys | Editable Samawah, Baghdad comparison and candidate research demonstrations |
| SR-04 — Workbench usability | City selection/edit or comparison through calculation, same-candidate cost and export |
| SR-05 — Install and resource contract | Clean setup, disk admission, bounded outputs, warm replay and low-space refusal |
| SR-06 — Release communication | README, quickstart, release notes, maturity table, demo outputs and known limits |

Evidence files in an external bundle must be ordinary files with SHA-256
identities. A passing record binds the exact candidate commit, its Git tree,
contract hash, gate ID and required evidence kind. The detached reviewer
signature binds the complete gate-proof set to the same source identity and
canonical repository name. Attach the bundle to the frozen candidate's release
artifacts; do not commit passing proofs or change the pending dashboard.

## Current result

The committed dashboard remains pending and `release_commit` is not pinned.
Without a valid external bundle, software-release readiness is false. Current
browser and source-publication checks are useful evidence, but they do not yet
prove a fresh Samawah journey, the source-pinned Baghdad and candidate examples,
or the clean-install resource contract.

Engineering closure is evaluated separately by
[`docs/design-engine/v06-design-closure/status.json`](../v06-design-closure/status.json).
Its six open gates and partial Workbench gate remain unchanged. The software
report keeps `engineering_accepted`, `physical_accepted`,
`manufacturing_release`, `movement_authority` and `operating_release` false.
Software proof integrity is not engineering-semantic review or physical
qualification. A software release therefore cannot authorize a vehicle,
manufacturing, construction, or railway operation.

The evidence-record format protects file integrity and identities. The
signature authenticates the review record against an externally trusted key
fingerprint and reviewer identity; it cannot prove the reviewer is independent
or correctly judged the tests and demonstrations. The evaluator requires
structured CI run references but leaves their authenticity and semantics to
the independent reviewer. It does not execute journeys or query GitHub.

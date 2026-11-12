# Retained authenticated software-review profile

**[v0.6.1 is published](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.6.1)**
at commit `5cfe89488a64549b37d4a7fd3ea9e3d3a8923aea`. Start with the
[published release guide](../../releases/v0.6.1/README.md), its installation
asset and checksums. The [v0.7 roadmap](../../ROADMAP.md) now controls development.

This directory retains the stricter authenticated-review profile implemented
before publication. It is not the publication status of v0.6.1 and does not
withhold that software release. The profile's machine-readable dashboard stays
truthfully pending: no accepted independent signature or passing gate set was
invented. The published release's exact-tag CI, demonstrations and source
integrity evidence remain available in its attached software-evidence archive.

## Optional profile inspection

The retained contract is
[`campaigns/v06-software-release.toml`](../../../campaigns/v06-software-release.toml),
with a machine-readable [status record](status.json). The commands below inspect
that profile; a false result means its additional authenticated-review
conditions are unfulfilled, not that the software release is unpublished:

```sh
./osr release software readiness
./osr release software readiness --require-ready
```

The evaluator remains unchanged. Its external-attestation mode requires a clean
full checkout and an actual independently signed Ed25519 review bound to the
source commit, Git tree, contract hash and proof set. Repository identity,
reviewer identity and key fingerprint must be supplied through a trusted channel.
Passing fixture tests or another AI review do not establish that identity.

| Gate | Required evidence |
|---|---|
| SR-01 — Source and artifact integrity | Publication hashes, manifest replay and tamper rejection |
| SR-02 — Core tests | Required Python, Rust, frontend and release-lane checks on one frozen commit |
| SR-03 — Representative journeys | Editable Samawah, Baghdad comparison and candidate research demonstrations |
| SR-04 — Workbench usability | City selection/edit or comparison through calculation, same-candidate cost and export |
| SR-05 — Install and resource contract | Clean setup, disk admission, bounded outputs, warm replay and low-space refusal |
| SR-06 — Release communication | README, quickstart, release notes, maturity table, demo outputs and known limits |

## Relation to ongoing engineering

The [engineering ledger](../v06-design-closure/status.json) retains six open
engineering gates and the partial Workbench gate. Its old software-publication
control is superseded; the requirements continue into v0.7. This documentation
change closes none of those findings and changes no retained evidence.

The profile's `engineering_accepted`, `physical_accepted`,
`manufacturing_release`, `movement_authority` and `operating_release` flags
remain false. Software publication, numerical evidence and physical acceptance
are distinct states.

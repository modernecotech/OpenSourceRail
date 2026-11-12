# v0.6.1 validation

## Fast change lane

The committed selected-test list is
[`.github/release-smoke-tests.txt`](../../../.github/release-smoke-tests.txt).
The matching GitHub Actions lane sparse-checks out the selected Python tests and
their inputs, installs only pytest 9.2.0 and SciPy 1.16.3, and runs the list
with one thread per numerical library. A separate bounded journey workflow
installs Playwright and runs the Samawah browser/export contract twice. A third
small workflow tests the declared Rust control contracts. Together these are
the required Python, browser/frontend and Rust checks for the frozen candidate.
None runs native CAD/FEM/GIS or an all-city replay.

Run the same Python check locally:

```sh
mapfile -t selected < <(sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d' .github/release-smoke-tests.txt)
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  .venv/bin/python -B -m pytest -q --import-mode=importlib -p no:cacheprovider "${selected[@]}"
```

## Published release verification

[v0.6.1](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.6.1)
was published on 12 November 2026 at commit
`5cfe89488a64549b37d4a7fd3ea9e3d3a8923aea`, tree
`58ba4411d502a166b3a14000bc1e09b733b65cbd`. Both `v0.6.0` and `v0.6.1`
remain pinned to their existing commits.

| Exact-tag check | Evidence |
|---|---|
| Python release lane | [43176691666](https://github.com/modernecotech/OpenSourceRail/actions/runs/43176691666), attempt 1: 228 passed |
| Rust control contracts | [43176691677](https://github.com/modernecotech/OpenSourceRail/actions/runs/43176691677), attempt 1: passed |
| Frontend and Samawah | [43176691729](https://github.com/modernecotech/OpenSourceRail/actions/runs/43176691729), attempt 1: frontend and two complete journeys passed |

The attached software-evidence ZIP preserves the raw logs, source identities,
packet checks and refusal evidence. The journey ZIP contains complete Samawah
exports and performance records. Check both against the release's SHA256SUMS.
The records retain their original identities and execution context.

## Clean-install handover

Run this once against the published tag using a clean checkout, new Python
environment and lockfile-installed Node dependencies:

1. Download `INSTALL-v0.6.1.md`, `SHA256SUMS` and the listed release assets;
   verify the downloaded bytes using `sha256sum --check SHA256SUMS`.
2. Follow the published installation asset, including `--branch v0.6.1`, and
   check the full source commit and tree above. Record Python, Node and browser
   versions, exact setup commands, elapsed time and disk availability.
3. Use fresh output directories outside the checkout for the documented
   Samawah journey. Confirm its source commit, cold calculation, identical warm
   cache reuse, changed-input identity, fourteen cost scopes and export replay.
4. Retain command output, reports and logs against the tag. If a step fails,
   retain the exact failing command and error, then repair that defect on main;
   do not move either existing release tag or relabel old outputs as a new run.
5. Confirm the source checkout stays clean and resource admission/output
   protections remain visible. Do not fill the filesystem to test refusal.

The v0.6 handover closes when repository instructions agree with the published
release and this clean-install journey succeeds. The separate retained
readiness-browser harness is maintenance alongside v0.7: its output directory
must also be an external temporary directory.

The [authenticated-review profile](../../design-engine/v06-software-release/README.md)
is retained for optional proof verification. Its pending dashboard and signature
requirements are not a publication prerequisite for the already published
release. Do not create passing profile records or repeat release-readiness
checks merely to make that dashboard green.

The reviewed source currently reports a source-binding hold for the integrated
`docs/design-engine/current` dossier. The Workbench makes that hold visible,
omits stale global cost and portfolio cards, and serves current city geography
and Samawah calculations through their own input identities. This behavior
keeps the dossier excluded from supported v0.6 results and SR-01 evidence until
its exact provenance is resolved. SR-01 evidence is limited to the independently
verified publications and packets used by the supported journeys. Do not rerun
the broad 266-city publication path to clear this hold.

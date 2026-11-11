# v0.6.0 validation

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

## Frozen-candidate acceptance

On the exact release-candidate commit, perform and retain:

1. `git status --porcelain --untracked-files=all` is empty and the full commit,
   tree, lockfiles and required toolchain identities are recorded.
2. Source-bound shipped packet checks and tamper-rejection tests pass without
   regenerating unrelated research publications.
3. Run the Samawah browser demonstration twice from an empty external output
   directory. It checks the cold request, identical warm cache hit, changed
   input, 14 cost scopes, performance report, output-size cap and independent
   result replay.
4. Inspect the existing Baghdad and candidate source manifests and reproduce
   the documented read-only views from their pinned evidence.
5. Run the Workbench browser checks and the required Python, Rust, frontend and
   control-contract tests applicable to the advertised capabilities.
6. Exercise resource refusal under a simulated low-space condition using the
   resource-admission tests. Do not fill the host filesystem to simulate a
   low-space condition.
7. Record test, workflow run, demo manifest/evaluation, cold/warm time, CPU, RSS,
   cache and output bytes, disk admission and limitations in the external
   release bundle.
8. Have an independent reviewer inspect the exact source commit and evidence,
   sign the review record with Ed25519 and provide the public-key fingerprint
   through an independently trusted channel.
9. Verify the bundle with `--require-ready` and that fingerprint on a clean
   checkout. Keep physical, manufacturing, movement and operating flags false.

The current dashboard deliberately remains pending until those authentic
records exist. A passing local unit-test fixture cannot substitute for actual
CI receipts, three demonstrations, clean-install measurements or reviewer
signoff. Do not create a new release tag while any of these steps is missing.
The pre-existing annotated `v0.6.0` development tag is not the release
candidate; preserve it and resolve the final release tag/version name separately.

The reviewed source currently reports a source-binding hold for the integrated
`docs/design-engine/current` dossier. The Workbench makes that hold visible,
omits stale global cost and portfolio cards, and serves current city geography
and Samawah calculations through their own input identities. This behavior
does not close SR-01: retain the dossier as held until its exact provenance is
resolved. Do not rerun the broad 266-city publication path to clear this hold.

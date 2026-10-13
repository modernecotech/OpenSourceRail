# Local Processing And GitHub Storage

OpenSourceRail builds, generates cities, runs engineering studies and validates
changes on a local machine. GitHub stores committed source, compact review
artifacts and versioned release assets. Repository Actions are disabled; pushes,
pull requests, schedules and manual workflow requests cannot start jobs while
that setting remains disabled. The policy is recorded in
[local-processing.json](../.github/local-processing.json).

The workflow files remain historical, executable recipes. The local runner
uses their validation steps for the complete CI and disposable integration
profiles, without checkout, cache, artifact-upload or installation actions.
There is no self-hosted Actions runner or remote job dispatch.

## Run checks

Use the [one-command setup](../README.md#one-command-linux-setup), then:

```bash
./osr validate run --profile quick
./osr validate run --profile rust
./osr validate run --profile python
./osr validate run --profile evidence
./osr validate run --profile browser
```

Each run prints its receipt location under ignored `build/validation/`. Supply
`--output build/validation/my-fresh-run` to choose a directory; existing outputs
are refused. Inspect a profile before running it or check a receipt afterward:

```bash
./osr validate plan --profile ci
./osr validate verify build/validation/my-fresh-run
```

| Profile | Work performed locally |
|---|---|
| `quick` | Format, runner tests, README/index limits, links, file sizes, current provenance and whitespace |
| `rust` | All-feature Rust tests, documentation tests, Clippy, runtime binaries, advisory audit and city-project checks |
| `python` | All six Python test directories; requires generated test inputs |
| `evidence` | Repository health, source provenance, engineering baseline, panel/twin, assurance and operating-readiness drift checks |
| `browser` | WASM libraries, frontend acceptance and offline operations browser acceptance |
| `ci` | Complete original CI validation/generation steps, browser checks, TACS replay and bounded TLC verification |
| `kani` | Every declared safety-case Kani harness, plus three explicit release properties; failures/timeouts block success |
| `integrated-stack` | Disposable native ERPNext/FUXA/gateway/controller/Workbench, city load and outage/recovery checks |
| `example-city` | Complete city lifecycle, restart, variation, business, disposition, native engineering change and recovery |

`quick` is a development check, not a release gate. `./osr test` remains available.
City generation and engineering computation remain local through `./osr city`,
`./osr build` and the existing study commands. Commit reviewed generated changes
before validating a release candidate. A check that changes source fails its
receipt even when its individual commands finish successfully.

Install optional prerequisites for the checks you select: pinned Kani 0.67.0,
cargo-audit 0.22.2, Java/TLC, Docker Compose and native CAD/engineering tools are
needed by their respective profiles. The runner does not install them. The
`ci` profile retains the original generated-product prerequisites and exact
Baghdad test-input bootstrap. Missing tools and inputs are failures, not skips.

Run native integration profiles in a fresh checkout on a disposable local host.
They refuse existing fixture files, occupied service ports, and existing named
Compose containers or volumes before starting. Their cleanup removes their
evaluation volumes; city public evidence is copied into the receipt directory
before cleanup. Private operational deployments must use their own workspace.

## Publish source and release assets

Review local changes, commit them and push to `main` using Git normally. Keep raw
logs, solver output, caches and private data locally under `build/` or `var/`;
follow the [artifact policy](repository-artifact-policy.md) for committed outputs.
Pushing does not run remote checks while repository Actions remain disabled.

For a software release, run **all four** `ci`, `kani`, `integrated-stack` and
`example-city` profiles on the same clean candidate commit, using a different
fresh receipt directory for each. Run disposable integration profiles first in
the fresh checkout, then Kani and CI; CI's configuration-only ERP checks may
leave fixture configuration files. Follow the [release checklist](releases.md)
to package the locally validated assets, then upload those files to a GitHub
release. Packaging defaults to local evidence and starts no Actions jobs.
The explicit `--backend github` option only reads historical run evidence.

Receipts bind the commit, tree, all current nonignored source hashes, complete
planned commands, exit codes, logs and public proof/city artifacts. Verification
rejects changed source, omitted checks, failed runs and changed output bytes.
Local receipts are **unattested execution records**: their author can edit them,
and hashes do not authenticate an executor. They grant no independent safety,
physical, construction or operational approval. Raw integration logs remain
local; the release carries public city reports and original Kani proof records.

## Repository setting

GitHub's [Actions settings guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
documents the repository-level disable switch. An administrator can confirm the
setting without starting a job:

```bash
gh api repos/modernecotech/OpenSourceRail/actions/permissions
```

The `enabled` value must remain `false`. To restore this policy after a settings
change, use `gh api --method PUT repos/modernecotech/OpenSourceRail/actions/permissions -F enabled=false`.
Disabling execution preserves historical run records. Repository, release,
LFS and existing artifact storage remain subject to the account's storage terms;
this change stops new Actions compute, not every possible GitHub charge.

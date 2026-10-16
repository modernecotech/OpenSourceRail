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

When a verification step also contains the exact setup command `npm ci`, the
local adapter runs `npm ls --depth=0` to check the installed dependencies.
The exact `npx playwright install --with-deps chromium` command becomes an
installed Chromium launch, render and close check. The reviewed
`PLAYWRIGHT_BROWSERS_PATH="$HOME/.local/share/opensource-rail/toolchains/playwright"`
prefix is preserved when present. These replacements appear explicitly in each
planned command's `setup_prerequisites` metadata; every subsequent pilot and
browser test still runs. Missing dependencies or an unusable browser fail the
profile. Other inline npm, Playwright or pip installation forms are rejected
until their local setup adapter is reviewed. Named installation steps remain
prerequisites handled by the setup command, rather than profile execution.

## Run checks

Use the [one-command setup](../README.md#one-command-linux-setup), then:

```bash
./osr validate run --profile quick
./osr validate run --profile rust
./osr validate run --profile python
./osr validate run --profile evidence
./osr validate run --profile browser
./osr validate run --profile native-design
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
| `native-design` | Required installed FreeCAD → Gmsh → CalculiX acceptance for both generated part families, two meshes, independent benchmarks, invalid inputs and owned timeout cleanup; zero skips permitted |
| `ci` | Independent Rust/Python suites followed by original generation/coherence steps, browser checks, TACS replay and bounded TLC verification |
| `kani` | Every declared safety-case Kani harness, plus three explicit release properties; failures/timeouts block success |
| `integrated-stack` | Disposable native ERPNext/FUXA/gateway/controller/Workbench, city load and outage/recovery checks |
| `example-city` | Complete city lifecycle, restart, variation, business, disposition, native engineering change and recovery |

`quick` is a development check, not a release gate. `./osr test` remains available.
City generation and engineering computation remain local through `./osr city`,
`./osr build` and the existing study commands. Commit reviewed generated changes
before validating a release candidate. A check that changes source fails its
receipt even when its individual commands finish successfully.

`native-design` is the required feature-acceptance profile when changing the
generated mechanical/civil part pipeline. It checks the actual installed CAD,
mesher and solver providers and Linux PIDfd cleanup support before testing;
missing prerequisites fail clearly without installation or analytical fallback.
The profile explicitly sets `OSR_RUN_NATIVE_PARTS=1`. Ordinary broad Python runs
may leave these expensive integration tests opt-in, but explicitly requested
native tests fail when their tools are missing instead of reporting a skip.

`./osr check --scope impact --changed <files> --plan` selects `native-design`
when either native-part problem is affected through its source/schema/property
dependencies, or when its native acceptance runner/tests change. The plan lists
each profile once. Unrelated prose does not trigger native CAD/solver execution.

Use a fresh directory, for example
`./osr validate run --profile native-design --output build/validation/native-design-my-change`.
The local receipt seals `native-design/prerequisites.json`, the JUnit report,
both actual native result trees, negative-input/timeout logs and the checked
`acceptance.json`. Missing mandatory tests, skipped tests, incomplete native
reports or changed artifact bytes invalidate acceptance. This profile can gain
further native cases without changing the existing four-profile software-release
requirement. A numerical feature pass grants no physical qualification, accepted
material properties or construction authority.

The standalone `evidence` profile first runs `bootstrap_baghdad_tests.py` to
restore exact hash-bound ignored operations and solver/GIS inputs from the
bundled archive, before repository health checks. It verifies existing inputs
and refuses differing local data or archive corruption. This setup restores
recorded inputs; it does not regenerate or refresh engineering evidence.

Install optional prerequisites for the checks you select: pinned Kani 0.67.0,
cargo-audit 0.22.2, Java/TLC, Docker Compose and native CAD/engineering tools are
needed by their respective profiles. The runner does not install them. `./osr doctor --profile minimal` (or `panel`, `civil`, `browser`, `cad-bim`, `formal`, `stack`) reports prerequisites and can retain an environment receipt. `./osr check --scope impact --changed <files> --plan` selects local tiers; `./osr check --scope all` retains the full periodic profile. Independent CI/Python/evidence/browser/Kani checks continue after a failure, and the aggregate receipt still fails. The
`ci` profile retains the original generated-product prerequisites and exact
Baghdad test-input bootstrap. Missing tools and inputs are failures, not skips.

Run native integration profiles in a fresh checkout on a disposable local host.
They refuse existing fixture files, occupied service ports, and existing named
Compose containers or volumes before starting. Their cleanup removes their
evaluation volumes; city public evidence is copied into the receipt directory
before cleanup, including both native engineering-change reports and the recovery
checkpoint/result reports. Missing, malformed or linked mandatory reports fail
capture; their retained bytes are covered by the receipt's artifact hashes.
Private operational deployments must use their own workspace.

The [14 October Kani diagnostics](design-engine/kani-diagnostics.json) retain an
actual failure on the earlier clean candidate `2ebe96d1da63`. The pinned
Kani/CBMC combination exhausted the interlocking verifier's memory allowance;
larger-memory and alternate-solver attempts did not establish those properties.
This remains a release blocker. Collecting the other independent proof results
does not turn a failed profile into a passing receipt.

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

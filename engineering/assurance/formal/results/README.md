# Bounded control proof results

## Current follow-through — 19 September 2026

**Two of the four previously open obligations have passing executions.**

| Original obligation | Recorded result |
| --- | --- |
| ATP determinism — E4.1a | Passed locally and in CI on `2bf8b7717` |
| Interlocking determinism — E3.1a | Passed locally on `2bf8b7717`; repeated with the memory-capped runner |
| Odometry determinism — E4.4a | Still open; CI timed out after 1800 seconds |
| Two-train non-overlap — E1.1a and its seven paired companions | Still open; all eight local partitions exhausted their 4096 MiB address-space allowance |

The [summary](bounded-control-2026-09-19.json) and
[complete retained evidence](bounded-control-2026-09-19.tar.gz) include successes,
failures, input hashes, commands, manifests, source changes and regression logs.
No diagnostic run with omitted checks or unverified contracts is counted as a pass.

[CI run 35403962318](https://github.com/modernecotech/OpenSourceRail/actions/runs/35403962318)
on commit `2bf8b7717aea09436cbcd588fa1e084ef907e1f9` retained seven package artifacts:
**36 passes and one odometry timeout across 37 properties**. Its interlocking
runner received a shutdown signal before uploading an artifact. That interruption
is not a counterexample or a passing execution.

The subsequent local interlocking run retained all 11 declared interlocking
results: **three passes and eight memory failures**. Its Rust and GSN inputs match
the CI candidate; only the source-bound runner and workflow inputs differ because
they add recorded memory limits. These groups are recorded separately. They are
**not a successful, complete CI run on one final commit** and do not satisfy the
release gate or independent acceptance.

### Reproduce

For the CI candidate, check out `2bf8b7717`, install Kani 0.67.0 and run:

```sh
python3 tools/automation/assurance-evidence.py run \
  --timeout 1800 --output build/assurance/reproduced-candidate
```

To reproduce the memory-capped local run, extract the archive at that checkout
and apply `build/assurance/closure-capped/source.patch`, then run:

```sh
python3 tools/automation/assurance-evidence.py run \
  --package osr-interlocking --timeout 600 --memory-mib 4096 \
  --output build/assurance/reproduced-interlocking
```

Use a new output directory so historical evidence is preserved. The source patch
covers the runner/workflow changes, and each manifest binds the complete Rust,
Cargo and GSN inputs. The JSON lists the archive and member SHA-256 values.

The next unresolved work is a verified decomposition of variable-time odometry
arithmetic and two-train state replay, or a verifier configuration that completes
the full existing obligations. The isolated arithmetic and contract experiments
did not establish closure and were not adopted. Increasing time alone did not
resolve odometry. A separate non-overlap diagnostic with a 12,800 MiB
address-space allowance also timed out after 300 seconds; its complete log is
retained without counting it as a controlled pass. See the [component and partition contracts](../topology-adapters.md).

---

# Historical topology proof rehearsal

The [summary](static-topology-2026-09-18.json) records **37 passes and four
300-second timeouts** across all 41 declared Kani properties. Each of those four
properties was then rerun with a **900-second budget** and timed out again; their
original manifests, results and logs are included under `extended-budget/`. The
[archive](static-topology-2026-09-18.tar.gz) preserves the original logs,
per-package TOML results and execution manifests, plus the Rust workspace,
Clippy and 27 evidence-packaging regression-test outputs. The JSON lists the
archive SHA-256 and every archived member's SHA-256.

## Reproduce

The execution started from checkout `0a694f8cf7af9a77fcc49dee0c342553057c1297`
with the recorded Rust changes. Restore that checkout into a separate working
directory, extract the archive there and apply
`build/assurance/static-final/source.patch`. Every execution input is listed
in the summary's `source_sha256`; the patch reproduces those source bytes.
Install the reviewed Kani 0.67.0 toolchain, then run into a new output directory:

```sh
python3 tools/automation/assurance-evidence.py run \
  --timeout 300 --output build/assurance/reproduced
```

The command exits unsuccessfully if any proof fails or times out, while retaining
all completed outcomes. The extended attempts use the same command with `--solution <ID> --timeout 900`.
Runtime depends on the host and concurrent load. These runs shared a development
host with other proofs and simulations; they are not a controlled sizing benchmark. The
archive is a local, unattested rehearsal and includes failures. It cannot satisfy
the clean-commit CI release gate or independent safety acceptance.

See [topology adapters](../topology-adapters.md) for the fixture bounds, storage
contract and limitations of the comparison tests.

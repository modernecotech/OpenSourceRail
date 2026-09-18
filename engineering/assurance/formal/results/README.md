# Local topology proof rehearsal

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

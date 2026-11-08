# Actual-candidate native acceptance

The optional v2 path uses the reviewed resource supervisor and real controlled
candidate documents. The v1 legacy CI path, input semantics and overlay bytes
remain separate. A v1 HVAC kit cannot enter a supervised candidate run.

This wiring is source-tested only. No native ERP/Docker services have been run
with an actual candidate by this change. Mechanical P2 documents and coordinator
runtime authorization remain prerequisites. Software acceptance never accepts
physical equipment, manufacturing release or railway operation.

## Future execution contract

Freeze the original candidate proposal, the compiler-exported review-pack
directory, one exact discrete source part ID, all tool/source versions and the
coordinator-approved budget. Missing documents remain a hold; no USD 1 kit or
synthetic drawing substitutes for the candidate.

The reviewed supervisor starts the actual-candidate runner, for example:

```sh
.venv/bin/python tools/automation/native-v06/resource_supervisor.py \
  --owner osr-v06-<fresh twelve lowercase hex digits> \
  --private-dir /absolute/fresh/control \
  --cpu-seconds 2700 --elapsed-seconds 1800 \
  --rss-bytes 6442450944 --disk-bytes 5368709120 \
  --host-reserve-bytes 8589934592 \
  -- .venv/bin/python tools/automation/v06-platform-native.py run \
     --proposal /absolute/frozen-proposal.json.gz \
     --review-pack /absolute/controlled-review-pack \
     --component-id 'exact source part id'
```

The allocation above is a proposal, not authorization. Replace the input and
owner placeholders only after the coordinator freezes and reviews the real
inputs. The runner requires the exact `OSR_NATIVE_OWNER`,
`OSR_NATIVE_PRIVATE_DIR` and binding token supplied by that supervisor. Before
native calls or fixture writes it calls the reviewed `require_binding` API.
All host fixture output is under `/absolute/fresh/control/fixture`; a conflicting
`--output` is refused. Source, input, candidate identities, component, proposal
bytes, controlled pack, supervisor request and command digest enter an immutable
`candidate-run-binding.json`.

The disposable v2 overlay explicitly names and owner-labels
`redis-cache-data:/data`, as well as the existing site/log/database/queue volumes
and default network. Candidate Compose startup uses cached images without build
or pull. Global images/caches and unrelated services remain outside teardown.
The options and volume-target merge behavior follow Docker's
[up](https://docs.docker.com/reference/cli/docker/compose/up/),
[run](https://docs.docker.com/reference/cli/docker/compose/run/) and
[merge](https://docs.docker.com/reference/compose-file/merge/) interfaces.

## Two receipts and final verification

The runner completes the actual native ERP lifecycle and its own owned Docker
cleanup, then **stages** `fixture/evidence/result.json`. Its state remains
`awaiting-resource-supervision`. The child exits zero so the supervisor can
finish its host/Docker cleanup and produce `supervisor-result.json`.

Only after the wrapper finishes may the coordinator run this read-only gate:

```sh
.venv/bin/python tools/automation/v06-platform-native.py verify \
  --output /absolute/fresh/control/fixture/evidence \
  --proposal /absolute/frozen-proposal.json.gz \
  --review-pack /absolute/controlled-review-pack \
  --component-id 'exact source part id'
```

Verification rechecks actual lifecycle records and current sources, then requires
the completed supervisor receipt with the same owner, private binding, command,
source hash and budget. It also checks actual zero wait statuses, verified
subreaper/waitability capabilities, resource accounting, no unaccounted volumes,
and verified host/Docker cleanup. Missing, unfinished, mixed or promoted evidence
cannot produce the small `osr-v06-native-candidate-acceptance/1` receipt returned
by this gate. That receipt contains hashes of the exact checked ERP and resource
bytes. Retain both underlying receipts and the source-bound control package;
never copy private tokens, credentials, databases or raw logs into publication.

The reviewed supervisor and its sampled-limit/containment limitations are
unchanged; see [RESOURCE_SUPERVISOR.md](RESOURCE_SUPERVISOR.md). All physical,
engineering and release flags remain false after joint software acceptance.

Offline checks:

```sh
.venv/bin/python -m pytest tests/test_v06_native_runner_binding.py \
  tests/test_v06_candidate_platform_native.py tests/test_v06_platform_native.py \
  tests/test_native_resource_supervisor.py -q
```

Binding tests use labelled unit receipts and stub only the separately tested
lifecycle verifier. They prove boundary behavior, not an executed ERP campaign.

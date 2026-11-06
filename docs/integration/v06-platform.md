# Current v0.6 native business platform acceptance

The explicit runner uses real ERPNext, installed Frappe HR/HRMS, MariaDB,
Redis, background workers, gateway SQLite/outbox and FUXA. Its input is the
source-verified current export manifest and exact `retained-comfort/HVAC` BOM
occurrence. Candidate, body, evaluation and selection IDs remain distinct.
One `Nos` at USD 1 represents a synthetic software kit; it does not establish
purchased stock, manufacturing yield, a supplier quote or complete installed BOM.

```bash
python3 tools/automation/v06-platform-native.py preflight
python3 tools/automation/v06-platform-native.py run --output build/v06-platform-local
python3 tools/automation/v06-platform-native.py verify --output build/v06-platform-local/evidence
python3 -m pytest -q tests/test_v06_platform_native.py
```

`preflight` and `verify` start no services. `run` requires Docker Compose and all
five pinned runtime images, Node with the locked npm dependencies, Playwright
Chromium and at least 8 GiB free disk. It creates a fresh random
`osr-v06-<12 hex digits>` Compose project/site, loopback ports and labeled volumes.
Source mounts are read-only. Docker CPU quota support is reported by preflight.
A one-CPU quota is requested per container only when supported; otherwise CPU
limits are not enforced. BLAS/OpenMP threads are set to one, with two explicit
RQ workers. These declarations are not an OS sandbox. Cleanup removes only
that run's resources, including
its database volumes; existing pilot and operator stacks remain untouched.
Private source inputs, credentials, native state and logs remain in ignored
`build/`; only the sanitized `evidence/` directory is suitable for sharing.
Failures retain an explicit failed execution record and uncovered checks.
Success is published only after independent teardown attempts verify that no
owned containers, volumes or networks remain; cleanup errors prevent success.

The bounded chain creates an immutable engineering-to-native BOM mapping,
submitted native purchase/receipt, rejected incoming Quality Inspection,
nonconformance/rework Task and passing reinspection, native Work Order and
serial/batch manufacture, serial material issue/installation, then an observed
simulated condition. A stopped ERP frontend causes an actual durable gateway
outbox retry; gateway restart and ERP recovery must deliver that exact event.
Its native Issue drives Asset Repair, stock consumption and a replacement serial.
Readback obtains candidate IDs from the immutable native execution mapping,
selects the chronological latest submitted inspection, and checks native
manufacture and installation serial/batch bundles. The inspector is a named
in-process fixture user subject to native ERP permissions. A latest passing
native inspection is reviewed by a separate API-authenticated
ERP user through a native Task; readback checks the actual modifier and exact
candidate/test/serial. The campaign guard refuses prior/failed tests, self review
and another candidate. Native HR coverage is installed HRMS plus creation and
readback of a Training Program. FUXA must display current valid observation and
refuse an operator's project write. The package contains no equipment commands;
a movement-authority request must be rejected and no controller work queued.

The review guard belongs to this disposable acceptance fixture. It is not a
new production handback endpoint. Business review never changes the native
physical handback-required flag or grants movement authority. This run does not
measure a part, validate HVAC performance, establish employee competence, verify
a production workforce assignment, commission a railway, or qualify a vehicle.
The current read-only engineering Workbench is not a transactional operator UI.
The campaign does not cover an installed controller or field device, real
protection, source-loss quality in FUXA, or full hiring/roster/payroll workflows.
Those remain separate work and cannot inherit these software results.

The [workflow](../../.github/workflows/v06-platform.yml) runs native acceptance
on relevant main-branch changes and manual dispatch, including production
ERP/gateway and selected-export changes. It builds the pinned native services
on a disposable runner after reserving disk space. Pull requests run the
deterministic offline input/refusal/receipt boundaries only. Native job
build budget is 90 minutes; the local runner's individual service/fixture waits
are bounded. A cached-image local run should be allowed 45 minutes and at least
6 GiB available RAM; actual elapsed time and image IDs are retained per execution.

Historical v0.4 acceptance remains at
[`205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e`](https://github.com/modernecotech/OpenSourceRail/blob/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/.github/workflows/integrated-stack.yml).
The later maglev native runner and its source-bound receipts remain separate.
This current campaign neither relabels their candidates nor inherits their
native result. No completed calculation or submitted business document supplies
physical acceptance evidence.

A local cached-image execution on 6 November 2026 completed the covered chain
in 284.834 seconds before teardown, with 21 native document readbacks. Separate
`verify` replay passed, as did all 29 offline tests. The retained private artifact
is `build/v06-platform-final-source/evidence/`, with manifest SHA-256
`9731d3c7dc473aca7b818226d6421f47fac7759f769eac5976334de0add3aeef`.
Its screenshot shows gateway status 5, condition code 0, valid quality and the
actual source timestamp. Cleanup verified zero owned containers, volumes and
networks, with no cleanup errors. The existing maglev pilot stayed running.
Docker reported unavailable CPU CFS quotas; no CPU isolation was enforced.
The final source inventory includes native image recipes, Nginx configuration,
Frappe module/patch lists and the shared device-isolated Chromium launcher.
The prior successful source epochs remain preserved with their own receipts.

Three earlier private attempts remain preserved: host CPU-quota refusal before
startup (0.253 s), a missing configured-baseline fixture prerequisite (219.528 s),
and a deliberate interruption to incorporate read-only review findings (103.402 s).
They are failed/interrupted executions and provide no completed acceptance.
No private credentials, native databases or source-bound historical receipts
were committed. The CI workflow is prepared; it has not been dispatched by this
local execution.

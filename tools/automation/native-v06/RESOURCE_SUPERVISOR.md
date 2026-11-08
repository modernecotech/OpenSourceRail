# Disposable native resource supervisor

`resource_supervisor.py` supervises a **trusted, frozen** native runner. It is
not an OS sandbox, a physical qualification tool, or a business-acceptance test.
Its final receipt must accompany the candidate-specific native ERP receipt.
Resource supervision alone cannot satisfy the ERP lifecycle or railway gates.

Read-only inspection on 8 November 2026 found rootless Docker 29.8.0, cgroup v2,
but no memory-limit or CPU-CFS-quota support. `docker stats` returned `0B / 0B`
memory. A separate read-only check found that `docker top` host PIDs match
`/proc`, have birth ticks, and yield nonzero RSS. No containers or apps were
started by those checks.

## What is measured and stopped

- One exact fresh `osr-v06-[a-f0-9]{12}` owner is supplied before launch.
  Existing resources with that owner cause a hold **without cleanup authority**.
- Containers and volumes need the exact `osr.native.owner` label and the owner's
  name prefix. A Compose default network needs the exact
  `com.docker.compose.project` label and `<owner>_default` name; a conflicting
  owner label is always refused. Both labels are included in discovery so a
  partially labelled resource cannot disappear from the audit.
- Native PID sets come from inspected running containers and `docker top`.
  Root PID, set uniqueness, `/proc` birth ticks, CPU ticks and nonzero group RSS
  are checked. Missing/inaccessible telemetry holds the run. PID births are
  retained through exits, execs and restarts. The supervisor, native child,
  Python/Node/browser descendants, event reader and probe clients are included.
  A dedicated Linux child-reaper process enables and verifies
  `PR_SET_CHILD_SUBREAPER`, parent-death signalling and PID-fd capability before
  launching the native command. Ordinary forked descendants are kernel-adopted
  there even when they exit/setsid/double-fork before the first resource sample.
  Adoption ownership does not depend on earlier observation or a process group.
  Every adopted child's birth and direct parent are checked before PID-fd
  signalling or exact-PID waiting. Native Popen status is handled by its own
  Popen handle. The worker launches no other programs; outer Docker probes and
  event-reader Popen children remain with the outer supervisor and are not
  globally reaped.
- CPU is a deliberately conservative **charge**: sampled self and reaped-child
  counters may overlap; container-exit gaps, complete Docker exec intervals,
  volume-measurement helpers and final cleanup gaps are also charged at all host
  CPUs. This is an upper screening charge, not a CPU-throughput benchmark.
  Owner-labelled Docker lifecycle events must remain live and authenticate exec
  IDs. A container that exits before any authenticated process/RSS sample holds
  the run. Short-lived startup services may therefore need a reviewed startup
  observation interval rather than pretending their memory was zero.
- Disk includes allocated private files, private temp/cache/config, named-volume
  blocks, container JSON logs and reported writable-layer bytes. Unreadable
  volumes use a read-only `du` exec in an already verified owned container;
  nothing starts a helper container. Writable host binds outside the private
  directory and unlabelled/anonymous volume mounts are refused. Writable-layer
  size is Docker's reported logical change size, not a filesystem quota.
- The Docker storage filesystem and private filesystem are recorded by device.
  Their available-space floor is checked. Positive unattributed filesystem
  growth is conservatively charged as another disk ceiling; concurrent work can
  cause a hold. Unrelated deletions can mask that growth, so this still does not
  establish a hard physical-disk upper bound.
- The existing image-ID/size inventory is captured before launch. New image
  IDs, removed IDs or changed sizes hold the run. Existing shared layers are
  reported as a cache baseline, not charged repeatedly to each container.
  **Images and shared caches are never deleted.** The reviewed runner must not
  build or pull images; its pinned images must already be present.

The default observation interval is 0.5 seconds, with a 10-second whole-probe
deadline. Disk/image probes occur at least every five seconds plus probe time.
Normal-operation detection delay can therefore reach interval + probe deadline
(10.5 seconds for CPU/RSS/elapsed, longer for disk/image refresh). Child shutdown
allows 20 seconds before the child reaper uses PID-fd SIGKILL; owned Docker
teardown has a 60-second command deadline. The adoption anchor is retained if
children have not actually died/reaped, and the outer result stays held. There
is **no finite enforced byte-overshoot bound**
for transient RSS/disk growth on this host. Blocking OS I/O, supervisor SIGKILL,
host loss or daemon failure can prevent cleanup. The coordinator must audit the
recorded owner in those cases. Never describe this as kernel resource isolation.

## Coordinator wiring required before native execution

The wrapper creates the private control directory before starting its child.
The native runner therefore needs a fresh `fixture/` subdirectory rather than
rejecting the already-created control directory. Before its first Docker write:

```python
from resource_supervisor import require_binding
owner = owned_namespace(os.environ['OSR_NATIVE_OWNER'])
control_dir = Path(os.environ['OSR_NATIVE_PRIVATE_DIR'])
require_binding(owner, control_dir)
folder = control_dir / 'fixture'  # must be fresh; create with private permissions
```

The runner's actual namespace must be that owner. Every native resource must use
the existing owner labels. Preserve its normal source checks, failure records,
candidate verification and teardown; the wrapper is an additional final gate.

Redis images declare `/data`. The existing `redis-cache` service needs an
**explicit named and owner-labelled `redis-cache-data` mount** in the disposable
override. An anonymous image-created volume is neither free storage nor safely
removable shared storage. Add all such mounts explicitly before running. The
supervisor records unaccounted mounts and refuses a cleanup-success claim; it
does not delete an ambiguously owned volume.

The wrapper provides private `TMPDIR`, `TMP`, `TEMP`, `XDG_CACHE_HOME` and
`XDG_CONFIG_HOME` to capture browser/fixture temporary writes. It does not change
`HOME`, global daemon settings or the user's shared toolchain caches. This is
trusted-code discipline, not containment of a malicious process.

## Proposed runtime allocation — not authorization

Pending actual controlled drawings, source freeze and coordinator review:

| Budget | Proposed value |
| --- | ---: |
| Conservative aggregate CPU charge | 2,700 s / 45 CPU-min |
| Elapsed time through teardown | 1,800 s / 30 min |
| Sum of sampled process RSS | 6 GiB |
| Charged owned/private disk and filesystem growth | 5 GiB |
| Minimum available space per relevant filesystem | 8 GiB |

Once the runner is wired and the real source proposal/review pack/part are fixed,
the invocation is:

```sh
.venv/bin/python tools/automation/native-v06/resource_supervisor.py \
  --owner osr-v06-<fresh twelve lowercase hex digits> \
  --private-dir /absolute/fresh/native-control-directory \
  --cpu-seconds 2700 --elapsed-seconds 1800 \
  --rss-bytes 6442450944 --disk-bytes 5368709120 \
  --host-reserve-bytes 8589934592 \
  -- .venv/bin/python tools/automation/v06-platform-native.py run \
     --proposal /absolute/frozen-proposal.json.gz \
     --review-pack /absolute/real-controlled-review-pack \
     --component-id 'exact source part id'
```

These example inputs must be resolved and reviewed; synthetic unit documents
cannot replace the real producer output.

The wrapper preserves child stdout/stderr/exit, fixed-command probe responses,
Docker events, PID/resource samples, interruption and cleanup records in its
private directory. Inspection intentionally omits `Config.Env`. Probe output is
bounded to 1 MiB per response; container teardown logs retain the last 2,000
lines. The child runner retains its own full native diagnostics. No public
evidence should include these private files wholesale.

Only a zero child exit, exact binding acknowledgement, intact telemetry/budget
checks and verified absence of owned containers/volumes/networks permit
`supervisor-result.json` to say `execution="completed"`. All physical and release
flags remain false. The coordinator must then verify the separate native ERP
receipt and retain the two source-bound records together before publication.
The separate host-process cleanup record requires a verified adoption capability,
the native command's actual wait status, exact waits for adopted children, and
an empty final kernel child-list rescan. A zombie is reaped, not accepted as
clean. A missing/crashed reaper or incomplete adoption report holds the result.
The reaper process itself is waited through its outer Popen handle. Docker
teardown alone cannot satisfy this condition.

Adoption covers ordinary Linux descendant ancestry. It does not capture a
process created by an external service broker or establish containment of
malicious code. Docker daemon workloads still use the separate label/PID
checks. Supervisor/reaper SIGKILL, kernel/host failure or deliberate ancestry
escape remains a limitation; missing cleanup evidence never becomes success.

Tests use scripted Docker responses and tiny local Python children, not native
ERP or containers:

```sh
/usr/bin/time -v .venv/bin/python -m pytest tests/test_native_resource_supervisor.py -q
```

Docker exec-event identity handling follows the primary Moby
[exec](https://github.com/moby/moby/blob/master/daemon/exec.go) and
[exit-event](https://github.com/moby/moby/blob/master/daemon/monitor.go) sources;
actual runtime telemetry remains mandatory and cannot be replaced by those
interface descriptions.

The adoption model uses the Linux
[child-subreaper](https://man7.org/linux/man-pages/man2/PR_SET_CHILD_SUBREAPER.2const.html),
[verification](https://man7.org/linux/man-pages/man2/PR_GET_CHILD_SUBREAPER.2const.html)
and [parent-death signal](https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html)
interfaces. Regression tests delay the first resource sample until after native
leader exit, including a new session and a double fork, then require the child
to be dead and reaped before accepting cleanup. Another test preserves an
unrelated Popen child's exit status and outer probe-command statuses.

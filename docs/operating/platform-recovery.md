# Coordinated platform recovery

The reusable recovery runner captures ERPNext, Redis, the gateway outbox, FUXA,
Ops Core, application files, encryption/signing keys and the example city's
Workbench context at one cold checkpoint. It restores them into new isolated
volumes and checks their consistency before removing the rehearsal containers.

## Reproduce

Use a running, populated [example city](../../deployment/example-city/README.md).
The host needs Linux `/proc`, Docker Compose, the repository Python environment,
and enough free space for the images, volume archives and restored volumes.
New checkpoints archive every container image by immutable ID before stopping
writers. Recovery loads those archived images and verifies their IDs, without
replacing mutable repository tags. The destination must support their platform
and architecture. Legacy checkpoints without an image archive still require
all captured image IDs to exist locally.

```sh
tools/automation/osr-python tools/automation/platform-recovery.py checkpoint \
  --profile deployment/recovery/example-city.json \
  --output var/recovery/example-checkpoint \
  --report build/recovery-checkpoint.json

tools/automation/osr-python tools/automation/platform-recovery.py verify \
  var/recovery/example-checkpoint

tools/automation/osr-python tools/automation/platform-recovery.py rehearse \
  var/recovery/example-checkpoint --report build/recovery-result.json
```

The checkpoint destination must be new and under `var/`. It contains credentials,
private files and keys; retain it as a protected backup, never as a public CI
artifact. Use only trusted checkpoints. Checksums detect changes but do not
provide an external signature or establish who created a backup.

Capture stops the matching host simulator and Workbench, then source containers,
and resumes them in a `finally` block. This introduces downtime. A failed capture
must not be used; check both `passed` and `source_resumed` in its report and inspect
private logs if either fails. The host process registry is refreshed on restart.

For another installation, copy the JSON profile and supply its Compose project
names, private root, Ops Core database, ERP site, cities, auxiliary context and
health URLs. Service names must be unique across projects. The current runner
supports named volumes and regular-file bind mounts; the host process discovery
expects the repository Workbench and simulator. Other writers need explicit
quiescing support before their data can share this checkpoint.

## What the rehearsal checks

- Exact checkpoint membership and checksums; import and verification of archived
  immutable container images. Rehearsals never pull a replacement image.
- Fresh destination volumes, with file bytes, paths, owners, modes and symlink
  targets matching the captured inventories before services start.
- Restored Ops Core database/evidence and verification with the original signing key.
- Native ERP record hashes, selected ledger fields, files and encrypted settings.
- Gateway alarm-to-Issue links and replay of a delivered event after simulating a
  lost reply: the original Issue is reused and checked ERP records remain unchanged.
- Restored ERP, gateway, FUXA, Workbench lifecycle and Ops Core HTTP responses,
  including the correct city scope for both cities.

The clone uses an internal Docker network with no published container ports.
Fixed-destination tunnels through `docker exec` expose only local verification
ports (default 28880–28884). All source volume identities are replaced. The
runner removes its temporary containers and volumes in `finally`; private logs,
configuration and restored host files remain under `var/recovery/` for inspection.

## Recorded result and limits

The 18 September 2026 rehearsal verified **ten volume inventories, ten signed
Ops Core records and 25 linked ERP cases**. The checked ERP snapshot included
11,571 Tasks, 26 Issues, six GL entries, ten stock-ledger entries and two files.
The lost-reply replay returned the same Issue without changing those checked
records. Restored services and both city contexts passed. Archived image import through native verification took **40.519 seconds**; initial
checkpoint integrity verification, capture and cleanup are excluded. The complete
[capture-and-resume cycle](status/rehearsals/checkpoint.json), including image
archiving before writer shutdown, took 121.868 seconds. All source services
resumed and the temporary recovery containers/volumes were removed.
The [source-bound report](status/rehearsals/recovery.json) records the checkpoint
hash, source hashes, base commit and dirty working-tree state.

This is coordinated **data recovery**, not an accepted operational cutover.
Controllers, queue workers and schedulers stay stopped in the clone. FUXA's saved
links retain the source origin; clone navigation and resuming jobs/controllers
require a reviewed origin/identity migration and a further native browser run.
Production recovery-time and recovery-point objectives, a separate-host rehearsal,
off-host backup retention, interrupted capture/process failure injection and
independent acceptance remain open. No recovery-time guarantee follows from one
local rehearsal.

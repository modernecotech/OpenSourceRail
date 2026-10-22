# Stopped progressive-controller recovery

Executed stopped reconciliation within one local domain.250m assumed stopping margin explicitly retains forward locks; no capacity or physical acceptance.

`osr-progressive-stopped-recovery/1` executes 44 actual Rust replays. Prepared/committed snapshots, two trains, omitted/duplicated trains, stale/wrong-epoch proofs, unsafe clearance, moving/off-berth reports, blocked resources, a second crash, repeated reconciliation and old commits are separate controls. Rejected reconciliation changes no resource record. Positive cases require fresh prepare/commit; the old contracts remain retired.

[Full inputs, snapshots, event transcripts and outputs](study.json.gz) · [Actual compiler, API-test and replay output](execution.json.gz) · [Source receipt](manifest.json) · [Overview](overview.svg).

Verification recompiles the pinned source and repeats every replay, comparing complete decoded output; altered, rehashed histories do not pass.

- One bounded controller domain, stationary full consists at declared berths; moving restart and controller-to-controller handover remain unimplemented.
- Synthetic identified occupancy, integrity, brake readiness and100ms observation bounds require physical detector and timing qualification.
- The caller pins the expected configuration/model/policy and must authenticate and durably commit the event history before acting. This transcript and its SHA256 do not supply installed authentication, consensus, fsync or anti-rollback storage.
- Every crash loses the transient fence/reconciliation witness; a new monotonically fenced epoch and lease/skew quarantine are required. Reconciliation retires old contracts; new prepare/commit is mandatory.
- Off-berth stranded trains, evacuation, rescue authority, degraded protection, station motor/receiver composition and full-line capacity acceptance remain open.

All engineering/physical release flags remain false. No city headway or design is promoted.

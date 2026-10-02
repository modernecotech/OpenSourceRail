# RFC 0033 — TACS runtime and committed resource control

**Status:** proposed development target; software evidence generated/unreviewed.
**Supersedes:** RFC 0032's separate authority/protection implementation.
**Deployment:** synthetic reference only; sectional-authority pilot retained.

## Responsibility and interface map

| Function | Decision owner | Physical or deployment boundary |
| --- | --- | --- |
| Shared railway identities/configuration | `osr-core::deployment` | Exact model-byte hash; frozen startup parameters; designed revision distinct from installed and approved records |
| Authoritative resource lifecycle | `osr-interlocking::resources`, `resource_log`, `DerivedState` | Only verified committed `ResourceControl` entries mutate ownership |
| Ordered authoritative decisions | Existing `osr-consensus::step` | Three static voters; independent power/network placement must be designed and assessed |
| Physical proving | Identified point/station I/O hosts | Asset-scoped occupancy, integrity, points, restrictions and qualified no-reentry proof; synthetic ports in the reference |
| Onboard movement authority | Existing `compute_self_ma_from_state` | Validated committed view, exact frozen model, bounded full train footprint and evidence age |
| Speed and emergency protection | Existing `osr-atp::atp_evaluate` | Grade-adjusted illustrative braking profile; measured braking/adhesion/latency remains open |
| Mission and station requests | Existing `osr-ato::ato_evaluate`, `station_step` | Doors, charger isolation, connector clearance and energy independently gate departure |
| Final brake request | Existing `osr-brake::brake_evaluate` | Application request to separately qualified safety-output channel; software host is not qualified output hardware |
| Authentication and message contracts | `osr-proto`, `osr-crypto`, `osr-secbus`, consensus proposal verifier | Registered issuer, asset permissions, configuration/session/sequence/time checks before state effects |
| Process execution and persistence | Thin `osr-runtime` hosts | Framed local ports, event scheduling, disk writes before outbound effects, conservative cold start |
| OCC | Service intentions and observations | No authority, ownership release or latch-clear bypass |
| ERPNext/FUXA | Existing observation/maintenance integrations | Observation only; no new railway command interface |

There is one MA computer and one ATP path. Resource contracts from the earlier
prototype move into existing crates; `osr-tacs` and its parallel MA/protection
algorithms are retired. `osr-runtime` contains orchestration and adapters.
Route selection remains intent, per `osr-onboard-routing`; agreement cannot
supersede missing permission or physical proving. Logical peer observations
may traverse common infrastructure; no direct radio or `osr-t2t` crate is added.

## Configuration and communications

`railway-model.json` schema `osr-tacs-railway/2` supplies resource IDs, existing
section IDs, conflicts, extents, asset identities, train/session/formation
parameters, station locations, static voters and role-scoped public keys.
`deployment.json` is an exact-byte-hash-bound generated startup export.
`FrozenRailway` rejects unsupported versions, invalid topology/identities,
changed startup parameters and operational activation. This source is a
**designed synthetic configuration**; `installed_state=not-installed` and
`approved_operating_profile=prototype-unapproved` are separate explicit facts.
Changes require a new bundle and restart, never live digital-twin mutation.

The reference transport uses signed `osr-runtime/1` packets, postcard encoding,
existing signed consensus proposals and explicit internal interlocking entries.
Legacy protobuf/postcard `osr-proto::Entry` remains a separate versioned format;
it must not be deserialised directly into internal entries. Float-based legacy
position inputs require checked unit conversion at an explicitly selected
adapter. The runtime path publishes integer measured speed and bounded,
non-zero uncertainty. Unsupported/malformed packets fail closed.

The envelope binds configuration hash, registered session, monotonic sequence,
original observation time and message kind. Limits: 512 KiB application payload,
768 KiB signed payload, 4 MiB framed command, 16 publications per batch, 12,000
log entries and a 256-message reference queue. One-second input freshness and
100 ms maximum configured clock error are prototype assumptions; PTP and
hardware timing must establish their operational applicability. Future-dated
packets are rejected. Send/receive counters persist across restart. Asset
permissions are separate from signature validity. All load-bearing events,
including positions, use `Safety`. The legacy simulator consensus publisher
also classifies occupancy-changing position reports as `Safety` and retains
its last committed view when quorum confirmation is unavailable. No advisory route/position can unlock track.

The published deterministic reference keys are test fixtures. Operational
provisioning, protected key storage, rotation, revocation distribution,
offline replacement and recommissioning require a controlled maintenance pack.
Changing keys or sessions changes the configuration hash; interoperability
stops until the complete bundle is reconciled. Revoked participants are rejected.
Crash-fault Raft is assumed: a signed member's committed-prefix assertion is
not a Byzantine quorum certificate. Authenticated erroneous sensors and common
software, configuration, power and clock causes remain FMEA concerns.

## Ownership and evidence freshness

Unknown → qualified clear → available → reserve/prove/lock → occupy → explicit
withdrawal → qualified no-reentry/clearance → available. Identified occupied
startup admission can bind the proved train/session when no conflicting owner
exists; it cannot transfer another owner's lock. Leases time out to
`ReleasePending`, retaining their owner. Restart increments the committed
controller epoch, retains owners as unknown and quarantines empty clearance
for the maximum prior permission plus clock error. Identified retained owners
can be reconciled without transferring protection. Blocked possessions cannot
be cleared by these recovery APIs.

An empty detector does not prove cancellation safe. Qualified release requires
bounded full rear clearance with integrity, or committed withdrawal and a proved
stop/protected approach that prevents old-permission re-entry. These are physical
interface assumptions to validate. Platform resources remain owned at arrival.
Depot/work resource is explicitly protected; rescue, coupled formations,
turnbacks, arbitrary topology and large fleets remain separate packages.

MA expiry is the minimum of the new MA window and the **original** position,
local proof and held permission deadlines. Recalculation cannot refresh evidence.
Every traversed section must have the correct active owner/configuration/epoch,
current point proof and integrity. Local full-footprint uncertainty checking
adds a restrictive gate before ATP. Recovery requires stopped, valid local
facts and a privileged local procedure, never a dashboard acknowledgement.
Civil conditions enter through asset-scoped signed restrictions/closures;
urgent protection must have an engineered path independent of alarm viewing.
Removal requires qualified inspection/handback, not an ERP status change.

## Persistence and process reference

`osr-consensus::disk::DiskJournal` has one OS-locked writer. Frames carry node,
configuration, term, vote, complete log deltas, commit index, application state
and replay fences, with length and CRC bounds. Every host persists and fsyncs
file and directory before exposing messages or actuator requests. Torn/corrupt
journals inhibit startup; repair never silently discards an accepted lock.
Storage compaction atomically replaces a full-log checkpoint after fsync.
**Logical Raft snapshotting/log truncation is not implemented.** Capacity exhaustion
inhibits further publication; offline servicing requires retained-protection
and configuration reconciliation. A power interruption during rename/fsync
requires storage/hardware qualification; SIGKILL tests are software evidence.

The default Raft batch remains one entry. The reference host uses bounded
contiguous batches of twelve; Rust handles each entry under the same checked
prefix semantics. This is outside the one-entry formal refinement and needs
independent refinement review. Quorum confirmation records fresh per-peer
responses in the current term, including empty-log heartbeats; stale historical
replication indices cannot refresh a quorum. Durable reboot restores no leader
role, quorum confirmation or volatile acknowledgements.

Run `python3 tools/automation/tacs_reference.py --output /tmp/reference.json`.
The coordinator spawns two `osr-train-agent` and six `osr-wayside-agent` processes:
three voters, point I/O and west/east station I/O. Charger requests and local
proving pass through the station process ports; their asset-scoped interlocks
can inhibit power and cannot grant movement. The depot/work resource is
committed blocked and remains blocked across expiry and controller restart. Two further `osr-safety-output`
processes independently sample the existing brake deadline/latch contract. They
trip frozen/missing requests and require stopped privileged recovery; this is
process-isolation evidence, not qualification of de-energised hardware outputs.
Processes exchange signatures
through asynchronous bounded queues; publication does not wait for commitment.
Simulation truth enters only own-train sensors and local infrastructure proving
ports, never the MA state. Real journals and process kill/restart are used.
The same frozen bundle feeds every process. The physics fixture checks its
supported extents, conflict identities, formation/braking and berth/energy
parameters before startup; unsupported bundles require a new calibrated fixture. `osr-sim`'s legacy synchronous
cluster publisher remains isolated from this reference; it is not claimed as
the deployed asynchronous path. Full integration of its scenarios/physics,
shared clocks, radio/T2G/TCN failover and direct-peer performance is future work.

Station sequence is stop/secure → exchange/charge → isolate → physical departure
proof → ready. The reference measures synthetic energy and closed-loop speed;
per-car BMS/thermal/door/PSD/traction integrations remain pending HIL. Failed
charging can hold service without erasing track ownership. Emergency departure
cannot bypass a connected charger or unlocked door. Missing application output
must trip a separately qualified deadline/output channel; the isolated reference output ports model deadlines and latches but do not
qualify that hardware function.

## Evidence and staged delivery

The shared connected-engineering compiler carries part → subassembly → controller
function → train/infrastructure → hazard → control → evidence → operating response.
Source changes stale execution hashes and propagate through configuration-bound
claims and blocked release decisions. TLC checks a bounded resource abstraction
with qualified physical proving assumptions; it is neither a Rust refinement
proof nor an unbounded liveness result. G0–G4 decisions remain blocked pending
review and measurements.

Owners/reviewers below are accountable **roles to appoint**, not fabricated named
approvals. No package is accepted merely because a generated checkbox is true.

| Package | Technical owner | Independent reviewer | Exit evidence / dependency |
| --- | --- | --- | --- |
| 1 Architecture | Control architect | Independent railway safety engineer | Reviewed responsibility map; current baseline |
| 2 Shared configuration | Configuration/lifecycle engineer | Independent configuration auditor | Identity/schema/mixed-version tests; 1 |
| 3 Resource/durability | Interlocking/consensus engineer | Independent formal/storage reviewer | Lifecycle, crash and restart evidence; 2 |
| 4 Authority/protection | ATP/localisation engineer | Independent braking engineer | Freshness/uncertainty/integrity properties; 2–3 |
| 5 Communications | Communications/security engineer | Independent security/timing reviewer | Replay/loss/restart/vendor-neutral transport tests; 2 |
| 6 Runtime | Embedded runtime engineer | Independent safety-I/O reviewer | Multi-process reference and physical power-loss tests; 3–5 |
| 7 Station | Station/energy integration engineer | Independent doors/charging reviewer | Complete station-cycle and per-car tests; 4–6 |
| 8 Twin/campaign | Simulation engineer | Independent test engineer | Reproducible raw results; starts after 2 |
| 9 FMEA/GSN | Assurance engineer | Independent hazard reviewer | Connected change impact and applicability; continuous from 1 |
| 10 HIL/hardware | Electronics integration engineer | Independent hardware assessor | Measured output/timing/fault records; 6–9 |
| 11 Closed track | Test/operations engineer | Independent field safety reviewer | Braking, integrity, recovery drills; 10 |
| 12 Profile release | Railway release authority | Independent assessor | Named gates, rollback and approved installed bundle; 9–11 |

Hardware preparation proceeds with software and assurance using existing
`t-ecu-s`, `t-ecu-a`, `t-obs`, `w-sbc`, `s-sbc` families. Each pack needs exact
module/SKU/substitutes, wiring/connectors/enclosure, power/thermal/environmental
budgets, fail-safe outputs/watchdogs, calibration, controlled firmware, fixtures,
bench records, and complete-unit replacement/recommissioning instructions.
Existing COTS and custom-board release tracks both remain valid; safety-channel
selection follows `control-electronics/safety-controller-selection.md`. This
change supplies no invented SKUs, installed serials or physical test records.

Cost comparison uses equivalent service and availability, separately counting
train controllers, static voters, non-voting sites, radios/antennas/power,
retained detection, installation, spares/calibration/maintenance, integration,
assessment, recovery/disruption and local/import content. No equipment removal
or city-model savings is authorised without replacement function and evidence.
The reference's ten processes are software roles, not a bill of materials.
Cost quantities/prices remain deployment-specific inputs; an unknown input
must keep the comparison incomplete. Track duplicate safety implementations,
configuration variants, core dependencies and physical interfaces alongside money.

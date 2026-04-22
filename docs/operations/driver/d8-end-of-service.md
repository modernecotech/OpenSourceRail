# D8 — End of service

> **Deprecated for GoA 4 deployments (RFC 0015, 2026-04-22).**
> OpenSourceRail ships as Unattended Train Operation by default
> — no driver cab, no driver role. This rule file is retained
> as the reference for legacy GoA 2 cabbed fleets. GoA 4
> deployments absorb these responsibilities into dispatcher (S),
> station-staff (T), maintenance (M), and control-centre (C)
> rulebooks plus the onboard automation stack (`osr-atp`,
> `osr-ato`, `osr-obstacle-detect`). See
> [RFC 0013 §4.1](../../rfcs/0013-operations-rulebook.md)
> for the per-section migration table.

**Scope:** return of a trainset to depot, cab powerdown,
handover to the depot shift or the CBM team.

**Cross-refs:** [`osr-cbm-onboard`](../../../crates/osr-cbm-onboard/),
[`osr-event-recorder`](../../../crates/osr-event-recorder/),
RFC 0014 §5.1 (main-heavy depot functions).

## Rules

### D8.1 — Final revenue run complete

The driver completes the last revenue run per the roster,
makes the `last train, all change at [terminal]` PA at the
penultimate station, and proceeds to the assigned depot via
the empty-run route.

**Why:** the empty-run route is the same as revenue but with
no passenger interaction; dispatcher tracks it the same way.

### D8.2 — Depot entry (mode M3)

At the depot geofence the DMI transitions to M3 automatically
(per D6.6). The driver slows to ≤ 15 km/h, follows the line-
of-sight rule, and obeys any hand signals from depot yard
staff.

**Why:** depot yard geometry is a mix of mainline speeds and
close-together stalls — line-of-sight is the tractable rule.
`osr-atp` is disabled below 15 km/h inside the depot
geofence (RFC 0007 §4 safety configuration).

### D8.3 — Park in assigned stall

The driver parks in the stall assigned by the depot staff (or
shown on the DMI if the stall was preassigned by the OCC's
CBM pipeline), applies park brake, cuts traction via
`DMI → Park`.

**Why:** a trainset in the wrong stall adds friction to the
next morning's dispatch — the CBM system's predicted
maintenance window is stall-specific.

### D8.4 — Cab powerdown

The driver powers down in reverse of D1.1: `DMI power OFF →
wait for DMI-down indicator → cab isolator OFF`.

**Why:** reversing the power-on sequence avoids a bus-fault
indicator on the overnight event recorder.

### D8.5 — Fault-flag handover

If the trainset flagged any amber/red fault during the shift,
the driver confirms the fault is written to the trainset's
persistent fault register (`DMI → Fault → Commit`) before
leaving the cab. CBM picks it up overnight.

**Why:** a fault logged in volatile event-recorder memory can
be lost on powerdown; the persistent register is where CBM
looks first.

### D8.6 — Driver logbook entry

The driver fills the logbook (paper or app) with: shift start
+ end times, km driven, incidents by category, equipment
anomalies, passenger counts (roster-declared OR CBM-reported,
whichever is available).

**Why:** the logbook is the primary legal record of the
shift. A missing entry compromises any downstream legal
review (incident dispute, fare-fraud claim, insurance).

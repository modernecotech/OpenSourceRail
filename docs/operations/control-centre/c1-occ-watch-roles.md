# C1 — OCC watch roles

**Scope:** the three on-shift roles: dispatcher, supervisor,
engineer-on-call.

**Cross-refs:** RFC 0013 §4.5 C1, [`osr-occ`](../../../crates/osr-occ/).

## Rules

### C1.1 — Dispatcher

The dispatcher owns all dispatching decisions for the shift:
route grants, timetable adherence, headway regulation,
driver radio authorisations, work-block coordination. The
dispatcher's authority ends at override approval and
incident escalation.

**Why:** the dispatcher is the operational executive — fast
decisions, clear authority. Splitting dispatching across
multiple shift personnel creates decision collisions (two
trains authorised onto the same block).

### C1.2 — Supervisor

The supervisor approves `MaintenanceOverride` extensions
beyond S5.4 defaults, handles NRSA and media liaison,
countersigns incident reports, and makes the call on
degraded-mode transitions. The supervisor does not dispatch
except as the dispatcher's relief during short breaks.

**Why:** the supervisor is the quasi-legal authority on
shift — the person accountable to the regulator, to whom
the dispatcher escalates. Keeping the supervisor clear of
dispatching prevents decision-role collisions at the moment
an incident demands both.

### C1.3 — Engineer-on-call

The engineer-on-call handles software and hardware alerts
that exceed the dispatcher's scope: consensus-cluster
degradations, `osr-routing` / `osr-interlocking` anomalies,
wayside-points drift alarms. Engineer-on-call is a 24×7
phone rotation, escalation target for the dispatcher.

**Why:** the dispatcher is not a systems engineer. Routing
a technical alert to a named on-call engineer moves the
diagnosis to the person trained for it without blocking
the dispatcher's operational duties.

### C1.4 — Role rotation

Shifts rotate on a 12-hour cadence with a 15-minute overlap
for the handover. The handover overlap is paid time and
is not compressible — a late-arriving relief does not
shorten the overlap.

**Why:** 12 hours matches the circadian pattern for
alertness (with the 8-hour extension used in some
deployments); the 15-minute overlap is the floor for the
S1/S6 and C3 handover protocols to complete without
handover shortcuts.

### C1.5 — Minimum qualification

Each role has a minimum qualification: dispatcher
(certified by the NRSA-equivalent after 6 months floor
training + exam), supervisor (3 years dispatcher experience
+ supervisor exam), engineer-on-call (software-engineer role
+ deployment-specific rotation). No role may be filled by
someone below the minimum.

**Why:** qualification is the hard floor of competence. An
under-qualified supervisor making the NRSA call is how
incidents become scandals; an under-qualified dispatcher is
how incidents happen.

### C1.6 — Fatigue policy

Dispatcher slots are capped at 10 hours; a Category I5 or I6
incident triggers a mandatory 30-minute break after the
immediate response phase, with supervisor relief. Double
shifts are prohibited.

**Why:** fatigued dispatchers miss radio calls and make
timetable errors. The 10-hour cap and post-incident break
is the compensating control — recovery time when it matters
most.

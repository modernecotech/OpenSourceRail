# C3 — Shift handover

**Scope:** written log, outstanding items, on-call list for the
incoming watch.

**Cross-refs:** S6 (dispatcher handover), RFC 0013 §4.5 C3.

## Rules

### C3.1 — Written handover log

The OCC handover log covers, for every shift: open
incidents (with category and owner), active
`MaintenanceOverride` entries, active speed restrictions,
weather overlays, fleet status (revenue / maintenance /
reserve), and any CBM red alerts. The log is created
before the handover and reviewed by both outgoing and
incoming watch.

**Why:** writing the log forces the outgoing watch to
synthesise the shift; reading it forces the incoming
watch to absorb. Verbal-only handovers lose details; the
written log is the persistent record.

### C3.2 — On-call engineer list

The on-call engineer list is updated for the incoming
shift: name, phone, escalation backup. An engineer going
off-call confirms the next engineer has accepted
handover before going off-duty.

**Why:** "I thought X was on call" is the classic
escalation failure. The explicit acceptance step closes
the gap.

### C3.3 — Overnight reduced staffing

Overnight watches run on reduced staffing: one supervisor
+ one dispatcher minimum; the engineer-on-call is phone-
available but not on-site. Overnight dispatcher scope is
limited to monitoring, alarm response, and the M2 work-
block authorisation for overnight possessions.

**Why:** overnight activity is low (no revenue service,
limited movements); full-staff daytime structure wastes
the labour. The minimum crew keeps the watch safe-walked
without over-staffing.

### C3.4 — I5/I6 full brief

Any Category I5 or I6 incident ongoing across a shift
boundary gets a full brief at handover — not summarised,
not presumed-known. The outgoing supervisor briefs the
incoming supervisor verbally for at least 15 minutes.

**Why:** the biggest incidents span many shifts and
develop over hours. A silent transfer loses the
investigator's working hypotheses; the full verbal brief
restates them for the person now responsible for acting on
them.

### C3.5 — System health dashboard

At handover, the OCC captures a screenshot of the system
health dashboard (fleet status, consensus-cluster health,
station SCADA roll-up, backhaul link state) and files it
to the shift folder. The incoming watch confirms the
screenshot reflects reality before acknowledging.

**Why:** the screenshot is a timestamped snapshot of "what
was true at handover" — useful for any later investigation
that needs to establish what the incoming watch knew at
the start of their shift.

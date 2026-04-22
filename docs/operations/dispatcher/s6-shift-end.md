# S6 — Shift end

**Scope:** end-of-shift handover, outstanding-event log, system
state summary for the incoming dispatcher.

**Cross-refs:** RFC 0013 §4.2 S6.

## Rules

### S6.1 — Write the handover log

The outgoing dispatcher writes the handover log 30 minutes
before shift end. The log covers: outstanding incidents,
active `MaintenanceOverride` entries, active speed
restrictions, degraded-mode flags, depot slot availability,
and any passenger-affecting events from the shift.

**Why:** the 30-minute margin gives time for the outgoing
dispatcher to answer questions while still on shift, rather
than leaving the incoming dispatcher to decode a hastily-
written log alone.

### S6.2 — Confirm fleet overnight status

Before close, the outgoing dispatcher confirms all revenue →
depot transitions are complete, each trainset's overnight
layup slot is known, and any trainset held out of service has
a named fault attached.

**Why:** a trainset "somewhere" overnight is a trainset that
gets missed at first service next morning. The explicit
layup assignment makes the morning roster pre-solved.

### S6.3 — Carry over open incidents

Any I2/I3/I4/I5/I6 incident still open at shift end is listed
explicitly in the handover log, with the investigation owner,
deadline, and next action. Incidents are never closed by
"shift change" — only by resolution.

**Why:** incidents closed implicitly by handover disappear from
the investigation record. The 72-hour and 2-hour regulatory
clocks run on wall-clock time, not shift time.

### S6.4 — Log off

The outgoing dispatcher logs off the OCC console only after
the incoming dispatcher countersigns the handover log (per
S1.6). Until countersignature, the outgoing dispatcher
remains accountable.

**Why:** leaving early while the incoming dispatcher is still
catching up creates a window where no qualified person is
at the console. The countersignature closes that window
explicitly.

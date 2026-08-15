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

Before close, the outgoing dispatcher assigns every healthy trainset to a
named powered passenger-station track near its first morning duty or to the
main depot, and attaches a named fault to every set held out of service.

**Why:** a trainset "somewhere" overnight is a trainset that
gets missed at first service next morning. The explicit
stabling assignment makes the morning roster pre-solved.

### S6.3 — Accept a passenger-station stabling slot

The dispatcher accepts a station slot only when the set is telemetry-healthy
and the track has at least 150 kW charging, CCTV, remote traction isolation,
protected emergency access, and a confirmed passenger-area closure plan.

**Why:** overnight station parking is cheaper and starts morning service across
the route, but only if security, electrical isolation, fire response, and
public access are controlled as deliberately as a depot road.

### S6.4 — Verify simultaneous morning release

Before handover, the dispatcher records each station-stabled set's target SoC,
scheduled self-test, first duty, and fallback set; any failed charge, security,
or self-test condition routes that set to the main depot or reserve plan.

**Why:** distributed stabling saves no time if morning dispatch discovers an
unready set only when the first trip is due.

### S6.5 — Carry over open incidents

Any I2/I3/I4/I5/I6 incident still open at shift end is listed
explicitly in the handover log, with the investigation owner,
deadline, and next action. Incidents are never closed by
"shift change" — only by resolution.

**Why:** incidents closed implicitly by handover disappear from
the investigation record. The 72-hour and 2-hour regulatory
clocks run on wall-clock time, not shift time.

### S6.6 — Log off

The outgoing dispatcher logs off the OCC console only after
the incoming dispatcher countersigns the handover log (per
S1.6). Until countersignature, the outgoing dispatcher
remains accountable.

**Why:** leaving early while the incoming dispatcher is still
catching up creates a window where no qualified person is
at the console. The countersignature closes that window
explicitly.

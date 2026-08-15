# S1 — Shift start

**Scope:** OCC dispatcher handover, login, fleet inventory,
schedule ready-check.

**Cross-refs:** [`osr-occ`](../../../crates/osr-occ/), RFC 0013 §4.2 S1.

## Rules

### S1.1 — OCC login

The incoming dispatcher logs into the OCC console with a
personal credential (not a shared shift account). The console
records the login timestamp in the shift-audit log.

**Why:** every radio authorisation, MA release, and degraded-
mode transition is attributed to a person. Shared accounts
break the chain of custody that post-incident review depends
on.

### S1.2 — Read handover log

Before accepting control, the incoming dispatcher reads the
outgoing shift's handover log in full: outstanding faults,
trainsets held out of service, planned possessions, weather
advisories, radio-coverage gaps.

**Why:** the first 30 minutes of a shift is when handover
context is dense and perishable. Skimming now costs more
later when an ongoing situation escalates and the new
dispatcher doesn't have the thread.

### S1.3 — Fleet inventory

The dispatcher confirms the fleet roster against the CBM-
backend overnight report: trainsets in revenue service, in
maintenance, in cold reserve. Discrepancies (e.g. a trainset
marked revenue that is still on a depot road) are resolved
with the depot foreman before first service.

**Why:** the schedule builder allocates trainsets to services;
if the roster is wrong, the first attempt to dispatch that
service hits a no-trainset error in the middle of peak
boarding.

### S1.4 — Schedule ready-check

The dispatcher verifies today's roster matches the
`service-hours.toml` window (first revenue service, last
revenue service, headway steps). Mismatches (e.g. a public
holiday schedule loaded on a weekday) are corrected before
first service.

**Why:** schedule mismatches in small systems are detected by
the travelling public, which is the worst failure mode. The
ready-check is the last place to catch them.

### S1.5 — Network status

The dispatcher reviews any active degraded-mode bulletins:
speed restrictions, single-track working, substations on
reduced output, stations in bypass. Each active item is
countersigned on the shift sheet.

**Why:** a degraded mode left over from the previous shift
that the new dispatcher isn't aware of is the shortest path
to a rules violation. The countersignature makes "I didn't
know" impossible.

### S1.6 — Acknowledge handover

The dispatcher countersigns the handover log, which closes
the outgoing shift and transfers accountability. The OCC console
prompts for the countersignature; until it is entered, the
outgoing dispatcher remains the accountable operator.

**Why:** there must be exactly one accountable dispatcher at
all times. A gap between "I'm logging out" and "I'm logged
in" creates a window where nobody owns the radio.
